"""Aircraft and crew route MILP for initial scheduling and recovery."""
from __future__ import annotations

import re
import pandas as pd
import pulp
from src.validation import prepare_data

CANCEL_PENALTY = 100_000.0
AIRCRAFT_CHANGE_PENALTY = 250.0
CREW_CHANGE_PENALTY = 100.0


def _name(value):
    return re.sub(r"[^A-Za-z0-9_]", "_", str(value))


def _compatible_type(required, provided):
    return required == "ANY" or provided == "ANY" or required == provided


def _followable(left, right, gap_minutes):
    return left["destination"] == right["origin"] and left["arrival"] + pd.Timedelta(minutes=gap_minutes) <= right["departure"]


def _overlap(left, right):
    return left["departure"] < right["arrival"] and right["departure"] < left["arrival"]


def solve_schedule(flights, aircraft, crew=None, turnaround_minutes=45,
                   crew_rest_minutes=30, unavailable_aircraft=None,
                   unavailable_crew=None, unavailable_periods=None,
                   cancelled_flights=None, original_assignment=None,
                   original_crew_assignment=None, allow_cancellation=False,
                   strategy="normal", buffer_minutes=30,
                   flexibility_target_minutes=90,
                   flexibility_penalty_per_minute=5,
                   cancellation_penalty=CANCEL_PENALTY,
                   time_limit=30):
    """Solve a time-space route assignment MILP.

    Crew duty is approximated by total block time (sum of flight durations).
    Fixed flight times mean no recovery-added delay variable is present.
    """
    f, a, c = prepare_data(flights, aircraft, crew)
    strategy = str(strategy).lower().strip()
    if strategy not in {"normal", "buffered", "flexible"}:
        raise ValueError("Strategy must be normal, buffered, or flexible.")
    if turnaround_minutes < 0 or crew_rest_minutes < 0 or buffer_minutes < 0:
        raise ValueError("Turnaround, rest, and buffer values cannot be negative.")
    cancelled_flights = set(cancelled_flights or [])
    unavailable_aircraft, unavailable_crew = set(unavailable_aircraft or []), set(unavailable_crew or [])
    original_assignment = dict(original_assignment or {})
    original_crew_assignment = dict(original_crew_assignment or {})
    periods = unavailable_periods or {}
    F, A, C = f.flight_id.tolist(), a.aircraft_id.tolist(), c.crew_id.tolist()
    fd, ad, cd = (x.set_index(k).to_dict("index") for x, k in ((f,"flight_id"),(a,"aircraft_id"),(c,"crew_id")))
    unknown = cancelled_flights - set(F)
    if unknown: raise ValueError(f"Unknown cancelled flight IDs: {sorted(unknown)}")
    if unavailable_aircraft - set(A): raise ValueError("Unknown unavailable aircraft ID.")
    if unavailable_crew - set(C): raise ValueError("Unknown unavailable crew ID.")
    for fid in F:
        if int(fd[fid]["required_crew_count"]) and not C and not allow_cancellation:
            raise ValueError("Crew data is required for flights with required_crew_count > 0.")
    op_turn = turnaround_minutes + (buffer_minutes if strategy == "buffered" else 0)
    m = pulp.LpProblem("Schedule_Rescue", pulp.LpMinimize)
    x = {(i,j): pulp.LpVariable(f"x_{_name(i)}_{_name(j)}", cat="Binary") for i in F for j in A}
    z = {i: pulp.LpVariable(f"cancel_{_name(i)}", cat="Binary") for i in F}
    # One connected, chronological route per resource; it may contain any number of flights.
    starts, ends, arcs = {}, {}, {}
    for j in A:
        for i in F:
            if (j not in unavailable_aircraft and fd[i]["origin"] == ad[j]["initial_location"]
                and fd[i]["departure"] >= ad[j]["available_from"]):
                starts[i,j] = pulp.LpVariable(f"as_{_name(i)}_{_name(j)}", cat="Binary")
            for k in F:
                if i != k and _followable(fd[i], fd[k], op_turn):
                    arcs[i,k,j] = pulp.LpVariable(f"aa_{_name(i)}_{_name(k)}_{_name(j)}", cat="Binary")
            ends[i,j] = pulp.LpVariable(f"ae_{_name(i)}_{_name(j)}", cat="Binary")
    eligible = {}
    for j in A:
        for i in F:
            ok = (_compatible_type(fd[i]["aircraft_type_required"], ad[j]["aircraft_type"])
                  and j not in unavailable_aircraft and fd[i]["departure"] >= ad[j]["available_from"])
            for start, finish in periods.get(j, []):
                ok = ok and not (fd[i]["departure"] < pd.Timestamp(finish) and fd[i]["arrival"] > pd.Timestamp(start))
            eligible[i,j] = ok
            if not ok: m += x[i,j] == 0
    for i in F:
        m += pulp.lpSum(x[i,j] for j in A) + z[i] == 1, f"cover_{_name(i)}"
        if not allow_cancellation: m += z[i] == 0
        if i in cancelled_flights: m += z[i] == 1
    for i in F:
        for j in A:
            pred = [v for (g,k,h),v in arcs.items() if k == i and h == j]
            pred += [starts[i,j]] if (i,j) in starts else []
            succ = [v for (g,k,h),v in arcs.items() if g == i and h == j] + [ends[i,j]]
            m += pulp.lpSum(pred) == x[i,j]
            m += pulp.lpSum(succ) == x[i,j]
    for j in A:
        m += pulp.lpSum(v for (i,a_id),v in starts.items() if a_id == j) <= 1
        m += pulp.lpSum(ends[i,j] for i in F) <= 1
    # Route-flow alone permits disconnected route components to overlap.
    # Exclude only simultaneous operations; non-overlapping flights may connect
    # through intermediate flights even when they cannot follow directly.
    for j in A:
        for pos, i in enumerate(F):
            for k in F[pos + 1:]:
                if _overlap(fd[i], fd[k]):
                    m += x[i,j] + x[k,j] <= 1, f"aircraft_conflict_{_name(i)}_{_name(k)}_{_name(j)}"
    # Crew routes, qualifications, location, rest, availability, and total block-time limits.
    y = {(i,j): pulp.LpVariable(f"y_{_name(i)}_{_name(j)}", cat="Binary") for i in F for j in C}
    cstarts, cends, carcs = {}, {}, {}
    for j in C:
        quals = {q.strip() for q in str(cd[j]["eligible_aircraft_types"]).split(";") if q.strip()}
        for i in F:
            req = fd[i]["aircraft_type_required"]
            crew_ok = (j not in unavailable_crew and ("ANY" in quals or req == "ANY" or req in quals))
            for start, finish in periods.get(f"crew:{j}", []):
                crew_ok = crew_ok and not (fd[i]["departure"] < pd.Timestamp(finish) and fd[i]["arrival"] > pd.Timestamp(start))
            if crew_ok and fd[i]["origin"] == cd[j]["initial_location"] and fd[i]["departure"] >= cd[j]["available_from"]:
                cstarts[i,j] = pulp.LpVariable(f"cs_{_name(i)}_{_name(j)}", cat="Binary")
            if not crew_ok: m += y[i,j] == 0
            cends[i,j] = pulp.LpVariable(f"ce_{_name(i)}_{_name(j)}", cat="Binary")
            for k in F:
                if i != k and _followable(fd[i], fd[k], crew_rest_minutes):
                    carcs[i,k,j] = pulp.LpVariable(f"ca_{_name(i)}_{_name(k)}_{_name(j)}", cat="Binary")
    for i in F:
        m += pulp.lpSum(y[i,j] for j in C) == int(fd[i]["required_crew_count"]) * (1-z[i]), f"crew_count_{_name(i)}"
        for j in C:
            quals = {q.strip() for q in str(cd[j]["eligible_aircraft_types"]).split(";") if q.strip()}
            for a_id in A:
                if "ANY" not in quals and ad[a_id]["aircraft_type"] not in quals:
                    m += y[i,j] + x[i,a_id] <= 1, f"crew_aircraft_type_{_name(i)}_{_name(j)}_{_name(a_id)}"
    for i in F:
        for j in C:
            pred = [v for (g,k,h),v in carcs.items() if k == i and h == j]
            pred += [cstarts[i,j]] if (i,j) in cstarts else []
            succ = [v for (g,k,h),v in carcs.items() if g == i and h == j] + [cends[i,j]]
            m += pulp.lpSum(pred) == y[i,j]
            m += pulp.lpSum(succ) == y[i,j]
    for j in C:
        m += pulp.lpSum(v for (i,c_id),v in cstarts.items() if c_id == j) <= 1
        m += pulp.lpSum(cends[i,j] for i in F) <= 1
        for pos, i in enumerate(F):
            for k in F[pos + 1:]:
                if _overlap(fd[i], fd[k]):
                    m += y[i,j] + y[k,j] <= 1, f"crew_conflict_{_name(i)}_{_name(k)}_{_name(j)}"
    for j in C:
        block_hours = {i: (fd[i]["arrival"]-fd[i]["departure"]).total_seconds()/3600 for i in F}
        m += pulp.lpSum(block_hours[i]*y[i,j] for i in F) <= float(cd[j]["max_work_hours"]), f"duty_{_name(j)}"
    # Objective: schedule cost, explicitly separated recovery penalties, and strategy score.
    op_cost = pulp.lpSum(((fd[i]["arrival"]-fd[i]["departure"]).total_seconds()/3600)*float(ad[j]["cost_per_hour"])*x[i,j] for i in F for j in A)
    crew_cost = pulp.lpSum(((fd[i]["arrival"]-fd[i]["departure"]).total_seconds()/3600)*float(cd[j]["cost_per_hour"])*y[i,j] for i in F for j in C)
    cancel_cost = pulp.lpSum(float(cancellation_penalty)*float(fd[i]["priority"])*z[i] for i in F)
    aircraft_change = pulp.lpSum(AIRCRAFT_CHANGE_PENALTY*x[i,j] for i in F for j in A if i in original_assignment and original_assignment[i] != j)
    crew_change = pulp.lpSum(CREW_CHANGE_PENALTY*y[i,j] for i in F for j in C if i in original_crew_assignment and j not in set(original_crew_assignment[i]))
    tight_penalty = pulp.LpAffineExpression()
    if strategy == "flexible":
        for (i,k,j),v in arcs.items():
            slack = (fd[k]["departure"]-fd[i]["arrival"]).total_seconds()/60 - turnaround_minutes
            tight_penalty += max(0, flexibility_target_minutes-slack)*flexibility_penalty_per_minute*v
    m += op_cost + crew_cost + cancel_cost + aircraft_change + crew_change + tight_penalty
    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit)
    m.solve(solver)
    status = pulp.LpStatus[m.status]
    if status != "Optimal":
        return {"status": status, "schedule": pd.DataFrame(), "objective": None,
                "strategy": strategy, "effective_turnaround": op_turn, "components": {}, "solver_message": status}
    rows=[]
    for i in F:
        ass=next((j for j in A if pulp.value(x[i,j]) > .5), None)
        crew_ids=[j for j in C if pulp.value(y[i,j]) > .5]
        rows.append({"flight_id":i,"origin":fd[i]["origin"],"destination":fd[i]["destination"],"departure":fd[i]["departure"],"arrival":fd[i]["arrival"],"assigned_aircraft":ass,"assigned_crew":";".join(crew_ids),"status":"Cancelled" if pulp.value(z[i])>.5 else "Scheduled"})
    values = {"aircraft_operating_cost":float(pulp.value(op_cost) or 0),"crew_operating_cost":float(pulp.value(crew_cost) or 0),"cancellation_penalty":float(pulp.value(cancel_cost) or 0),"aircraft_reassignment_penalty":float(pulp.value(aircraft_change) or 0),"crew_reassignment_penalty":float(pulp.value(crew_change) or 0),"flexibility_penalty":float(pulp.value(tight_penalty) or 0)}
    values["scheduled_operating_cost"] = values["aircraft_operating_cost"]+values["crew_operating_cost"]
    values["recovery_penalties"] = sum(values[k] for k in ("cancellation_penalty","aircraft_reassignment_penalty","crew_reassignment_penalty"))
    return {"status":status,"schedule":pd.DataFrame(rows),"objective":float(pulp.value(m.objective)),"strategy":strategy,"effective_turnaround":op_turn,"components":values,"solver_message":status}
