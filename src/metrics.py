"""Consistent schedule and recovery accounting helpers."""
import pandas as pd


def connection_metrics(schedule, turnaround_minutes=45):
    active = schedule[schedule.status != "Cancelled"].copy()
    gaps=[]
    for _, group in active.dropna(subset=["assigned_aircraft"]).groupby("assigned_aircraft"):
        group=group.sort_values("departure")
        rows=list(group.to_dict("records"))
        for left,right in zip(rows,rows[1:]):
            if left["destination"] == right["origin"]:
                gaps.append((right["departure"]-left["arrival"]).total_seconds()/60)
    return {"average_connection_slack_minutes":sum(gaps)/len(gaps) if gaps else None,
            "minimum_connection_slack_minutes":min(gaps) if gaps else None,
            "tight_connections":sum(g < turnaround_minutes+30 for g in gaps),
            "connection_count":len(gaps)}


def compare_schedules(initial, recovered, initial_result, recovered_result):
    a=initial.set_index("flight_id"); b=recovered.set_index("flight_id")
    cancelled=int((b.status=="Cancelled").sum())
    operated=b[b.status!="Cancelled"]
    reassigned=sum(fid in a.index and b.loc[fid,"assigned_aircraft"] != a.loc[fid,"assigned_aircraft"] for fid in operated.index)
    crew_changed=sum(fid in a.index and set(str(b.loc[fid,"assigned_crew"]).split(";")) != set(str(a.loc[fid,"assigned_crew"]).split(";")) for fid in operated.index)
    unchanged=len(operated)-reassigned-0
    delay_minutes=0  # Flight times are fixed at the disruption-adjusted times in this model.
    initial_cost=initial_result.get("components",{}).get("scheduled_operating_cost",0)
    final_cost=recovered_result.get("components",{}).get("scheduled_operating_cost",0)
    penalties=recovered_result.get("components",{}).get("recovery_penalties",0)
    return {"initial_operating_cost":initial_cost,"recovery_operating_cost":final_cost,
            "recovery_cost_increase":final_cost-initial_cost,"cancellation_penalty":recovered_result.get("components",{}).get("cancellation_penalty",0),
            "total_operational_cost":initial_cost+(final_cost-initial_cost)+penalties,
            "cancelled_flights":cancelled,"reassigned_flights":int(reassigned),"crew_changed_flights":int(crew_changed),
            "unchanged_aircraft_assignments":int(unchanged),"delayed_flights":0,"average_additional_delay_minutes":delay_minutes,
            "solver_status":recovered_result.get("status","Unknown"),
            "aircraft_in_use":operated.assigned_aircraft.nunique(),
            "crew_in_use":len(set(x for cell in operated.assigned_crew.fillna("") for x in str(cell).split(";") if x))}
