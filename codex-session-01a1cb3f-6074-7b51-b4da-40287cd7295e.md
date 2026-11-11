# Codex conversation

## User

# Schedule Rescue — Phase 1: Correctness, Metrics and Reproducible Experiments

Act as a senior Python developer and operations research engineer.

I have an existing Streamlit application called Schedule Rescue. It implements integrated aircraft and crew scheduling using a MILP model with PuLP/CBC.

The application already supports:
- Normal, Buffered and Flexible initial scheduling.
- Aircraft and crew assignments.
- Flight delays and cancellations.
- Aircraft and crew unavailability.
- MILP-based schedule recovery.
- Comparison of the three strategies.
- Schedule visualizations and downloadable results.

Existing verification:
- 13 existing unit tests passed.
- 21 recovery optimization runs across seven illustrative scenarios were verified.
- All 21 reported an Optimal solver status.
- The application has already been tested through Streamlit AppTest.

Do not rebuild the application. Preserve its current architecture and working functionality.

## TASK 1 — Inspect before editing

Inspect the complete repository, especially:
- app.py
- src/metrics.py
- src/scheduler.py
- src/recovery.py
- src/robustness.py
- tests/
- Existing documentation
- Existing experiment scripts and CSV files

Identify the exact functions responsible for the issues below.

Do not make changes until you have reported your findings and proposed a minimal implementation plan.

## TASK 2 — Fix reporting and metric bugs

The previous functionality review identified these issues:

1. Delay reporting bug:
   - src/metrics.py currently reports delayed_flights = 0 in a scenario where an external delay was applied.
   - The comparison dataframe and CSV download are created before the actual delay information is incorporated.
   - Calculate scenario-aware metrics once and use the same result for all tables, charts and downloads.

2. Distinguish delay categories:
   - Externally imposed delays selected by the user.
   - Externally delayed flights that actually operated.
   - Flights cancelled after an external delay.
   - Additional delays introduced by recovery optimization, if supported.
   - Do not count a cancelled delayed flight as an operated delayed flight.

3. Connection gap versus slack:
   - Connection gap = next departure minus previous arrival.
   - Connection slack = connection gap minus required turnaround time.
   - For example, a 60-minute connection with a 45-minute turnaround has 15 minutes of slack.
   - Ensure names, calculations, tables and charts consistently distinguish these values.

4. Recovery cost:
   - Recovered operating cost.
   - Change in operating cost relative to initial operating cost.
   - Cancellation penalties.
   - Aircraft reassignment penalties.
   - Crew reassignment penalties.
   - Other recovery penalties.
   - Total modeled recovery cost.

   Preserve the accounting identity:
   Total modeled recovery cost = recovered operating cost + recovery penalties.

   Do not add the full initial operating cost again.

5. Unique changed flights:
   - Aircraft and crew changes can affect the same flight.
   - Add a union-based count of unique flights affected by assignment changes.
   - Report aircraft changes and crew changes separately as well.

6. Flight coverage:
   - Report operated flights.
   - Report cancelled flights.
   - Report unexpectedly uncovered flights.
   - An accepted solution must not silently omit a flight.
   - If a solve fails, do not calculate valid schedule metrics from a nonexistent solution.

7. Results and settings consistency:
   - Store the exact inputs, turnaround, strategy parameters, disruption selections and penalties associated with every solve.
   - Do not allow old results to appear as though they correspond to newly changed settings.
   - Either invalidate stale results or clearly display the settings used for the displayed result.

## TASK 3 — Build a reproducible experiment runner

Create a separate experiment runner without making the Streamlit interface dependent on it.

Use the existing demo dataset initially.

Run all three strategies:
- Normal
- Buffered
- Flexible

For each strategy, use exactly the same disruption scenarios.

Include these scenarios:

1. No disruption.
2. Flight F001 delayed by 30 minutes.
3. Flight F001 delayed by 60 minutes.
4. Flight F001 delayed by 120 minutes.
5. Flight F003 cancelled.
6. Aircraft A002 unavailable.
7. One crew member unavailable.
8. Two simultaneous disruptions, such as a flight delay and aircraft unavailability.
9. A combined aircraft and crew disruption.

Adapt scenarios to the actual IDs and data in the repository. Never silently skip an infeasible initial schedule.

Record:
- Scenario ID.
- Strategy.
- Solver status.
- Initial operating cost.
- Recovered operating cost.
- Recovery penalties.
- Total modeled recovery cost.
- Number of cancelled flights.
- Number of operated delayed flights.
- Total delay minutes, if available.
- Aircraft reassignment count.
- Crew reassignment count.
- Unique changed-flight count.
- Initial and recovered connection slack.
- Solver runtime.

Save results to CSV.

Make the experiment deterministic where possible:
- Record dependency versions.
- Record all scenario parameters.
- Record all strategy parameters.
- Document any solver tie-breaking limitations.

## TASK 4 — Analysis

Create a script or notebook that reads the experiment results and produces:

- Strategy-wise comparison tables.
- Initial cost versus recovery cost.
- Cancellation comparisons.
- Assignment-change comparisons.
- Delay comparisons.
- Scenario-wise cost differences.
- A clear explanation of cases where each strategy performs better or worse.

Do not claim that Buffered or Flexible is always superior.

Keep operating costs separate from optimization-only preference penalties.

If an initial schedule is infeasible, report it explicitly.

## TASK 5 — Tests

Add regression tests for every bug fixed.

Test:
- An externally delayed flight that operates.
- An externally delayed flight that gets cancelled.
- A recovery with aircraft and crew changes on the same flight.
- Connection gap and slack calculations.
- Cost accounting identity.
- Uncovered-flight counting.
- Stale result invalidation.
- Consistent comparison table and CSV outputs.
- Experiment runner executing all strategies on identical scenarios.

Run:

python -m unittest discover -s tests -v

Also run the experiment runner and inspect its output.

Do not claim success unless the actual tests and experiment runs succeed.

## TASK 6 — Documentation

Update documentation to explain:
- Definitions of every metric.
- Cost accounting.
- Strategy definitions.
- Experiment design.
- Reproducibility instructions.
- Assumptions and limitations.

Do not invent research references.

## DEVELOPMENT RULES

- Preserve the existing working project.
- Make minimal, well-structured changes.
- Do not add authentication or unrelated UI features.
- Do not add crew regulatory rules without defining and validating them.
- Do not implement flight retiming in this phase.
- Do not fabricate experimental results.
- Explain important mathematical and programming changes in beginner-friendly language.

At the end, report:
1. Files changed.
2. Bugs fixed.
3. Tests passed and failed.
4. Experiment results location.
5. Remaining limitations.
6. Exact commands to reproduce the experiments.

Begin with repository inspection and a proposed plan.

## Assistant

I’ll inspect the current implementation, tests, documentation, and experiment artifacts first. I’ll report the exact functions and a minimal change plan before editing anything.

## Activity

    $ pwd && rg --files -g '!*__pycache__*' -g '!*.pyc'
    /workspaces/ScheduleRescue
    docs/assumptions.md
    docs/methodology.md
    docs/mathematical_model.md
    docs/user_guide.md
    requirements.txt
    src/__init__.py
    src/validation.py
    src/visualizations.py
    src/scheduler.py
    src/metrics.py
    tests/test_schedule_rescue.py
    README.md
    data/demo_flights.csv
    data/demo_crew.csv
    data/demo_aircraft.csv
    app.py
    ✓ • 180ms

## Activity

    $ git status --short && git ls-files
    .gitignore
    README.md
    app.py
    data/demo_aircraft.csv
    data/demo_crew.csv
    data/demo_flights.csv
    docs/assumptions.md
    docs/mathematical_model.md
    docs/methodology.md
    docs/user_guide.md
    requirements.txt
    src/__init__.py
    src/metrics.py
    src/scheduler.py
    src/validation.py
    src/visualizations.py
    tests/test_schedule_rescue.py
    ✓ • 82ms

## Activity

    $ sed -n '1,320p' src/robustness.py && sed -n '1,320p' tests/test_schedule_rescue.py
    sed: can't read src/robustness.py: No such file or directory
    ✗ (2) • 82ms

## Activity

    $ sed -n '1,260p' app.py && sed -n '1,300p' src/metrics.py
    """Streamlit front end for Schedule Rescue."""
    from __future__ import annotations
    from pathlib import Path
    import pandas as pd
    import plotly.express as px
    import streamlit as st
    from src.scheduler import solve_schedule
    from src.validation import prepare_data
    from src.metrics import connection_metrics, compare_schedules
    from src.visualizations import resource_timeline
    
    st.set_page_config(page_title="Schedule Rescue", page_icon="✈️", layout="wide")
    
    @st.cache_data
    def demo_data():
        root=Path(__file__).parent/"data"
        flights=pd.read_csv(root/"demo_flights.csv")
        aircraft=pd.read_csv(root/"demo_aircraft.csv")
        crew=pd.read_csv(root/"demo_crew.csv")
        return flights,aircraft,crew
    
    def csv_download(label, df, filename):
        st.download_button(label,df.to_csv(index=False),filename,mime="text/csv")
    
    def clear_optimization_state():
        for key in ("initial_results","recovery_results","input_snapshot","model_settings","scenario","disrupted_flights"):
            st.session_state.pop(key,None)
    
    st.title("✈️ Schedule Rescue")
    st.caption("Airline scheduling, robustness and disruption recovery using mixed-integer linear programming")
    tabs=st.tabs(["Overview","Airline data","Initial schedules","Disruption & recovery","Strategy comparison","Model & assumptions"])
    
    with tabs[0]:
        st.subheader("Can a more resilient schedule recover better?")
        st.write("Schedule Rescue assigns aircraft and qualified crew to flights, then solves the schedule again after disruptions. Compare a low-cost baseline with buffered and flexible plans under exactly the same disruption scenario.")
        st.info("A MILP chooses binary decisions such as ‘aircraft A operates flight F’ and minimizes a stated objective while obeying route, timing, qualification and duty constraints.")
        st.markdown("**Workflow:** provide flight, aircraft and crew data → generate one or all initial strategies → select disruptions → run recovery → compare solver-backed outcomes.")
        st.caption("This is an educational planning model. It simplifies airline crew regulations and is not an operational dispatch system.")
    
    with tabs[1]:
        method=st.radio("Data source",["Demo dataset","Edit manually","Upload CSV"],horizontal=True,key="data_method")
        df,da,dc=demo_data()
        upload_ready = method != "Upload CSV"
        if method=="Edit manually":
            st.caption("Time format: YYYY-MM-DD HH:MM. Aircraft type ANY matches any type; crew eligible types are semicolon-separated.")
            df=st.data_editor(df,num_rows="dynamic",key="edit_flights",use_container_width=True)
            da=st.data_editor(da,num_rows="dynamic",key="edit_aircraft",use_container_width=True)
            dc=st.data_editor(dc,num_rows="dynamic",key="edit_crew",use_container_width=True)
        elif method=="Upload CSV":
            cols=st.columns(3)
            with cols[0]: uf=st.file_uploader("Flights CSV",type="csv")
            with cols[1]: ua=st.file_uploader("Aircraft CSV",type="csv")
            with cols[2]: uc=st.file_uploader("Crew CSV",type="csv")
            if uf and ua and uc:
                try:
                    df,da,dc=pd.read_csv(uf),pd.read_csv(ua),pd.read_csv(uc)
                    upload_ready=True
                except Exception as exc:
                    st.error(f"Could not read CSV: {exc}")
                    st.session_state.pop("data",None)
                    clear_optimization_state()
            else:
                st.session_state.pop("data",None)
                clear_optimization_state()
        with st.expander("Download CSV templates"):
            cols=st.columns(3)
            with cols[0]: csv_download("Flights template",pd.DataFrame(columns=["flight_id","origin","destination","departure","arrival","aircraft_type_required","required_crew_count","priority"]),"flights_template.csv")
            with cols[1]: csv_download("Aircraft template",pd.DataFrame(columns=["aircraft_id","initial_location","available_from","cost_per_hour","aircraft_type"]),"aircraft_template.csv")
            with cols[2]: csv_download("Crew template",pd.DataFrame(columns=["crew_id","initial_location","available_from","eligible_aircraft_types","max_work_hours","cost_per_hour"]),"crew_template.csv")
        st.write("Flights",df); st.write("Aircraft",da); st.write("Crew",dc)
        if upload_ready:
            try:
                nf,na,nc=prepare_data(df,da,dc)
                st.success(f"Data valid: {len(nf)} flights, {len(na)} aircraft, {len(nc)} crew members.")
                previous=st.session_state.get("data")
                if previous is not None and any(not old.equals(new) for old,new in zip(previous,(nf,na,nc))):
                    clear_optimization_state()
                st.session_state["data"]=(nf,na,nc)
            except Exception as exc:
                st.session_state.pop("data",None)
                clear_optimization_state()
                st.error(f"Data validation: {exc}")
    
    with tabs[2]:
        st.subheader("Generate initial schedule")
        st.write("Normal minimizes operating costs. Buffered requires extra aircraft connection time. Flexible penalizes aircraft connections below a selected slack target. Crew operating cost is included in all three.")
        turnaround=st.number_input("Minimum aircraft turnaround (minutes)",0,300,45,5,key="turnaround")
        buffer=st.number_input("Extra buffer for Buffered (minutes)",0,180,30,5,key="buffer")
        target=st.number_input("Target slack for Flexible (minutes)",int(turnaround),360,max(90,int(turnaround)),5,key="target")
        chosen=st.multiselect("Strategies to solve",["normal","buffered","flexible"],["normal","buffered","flexible"],format_func=str.title)
        if st.button("Solve initial schedule(s)",type="primary"):
            if "data" not in st.session_state: st.error("Provide valid data in Airline data first.")
            else:
                f,a,c=st.session_state["data"]; results={}
                for strategy in chosen:
                    with st.spinner(f"Solving {strategy} MILP..."):
                        results[strategy]=solve_schedule(f,a,c,turnaround_minutes=turnaround,strategy=strategy,buffer_minutes=buffer,flexibility_target_minutes=target)
                st.session_state["initial_results"]=results
                st.session_state["input_snapshot"]=(f.copy(),a.copy(),c.copy())
                st.session_state["model_settings"]={"turnaround":turnaround,"buffer":buffer,"target":target}
                st.session_state.pop("recovery_results",None)
        for strategy,result in st.session_state.get("initial_results",{}).items():
            st.markdown(f"#### {strategy.title()} — {result['status']}")
            if result["status"]=="Optimal":
                st.dataframe(result["schedule"],use_container_width=True)
                m=connection_metrics(result["schedule"],int(turnaround))
                cols=st.columns(4); cols[0].metric("Operating cost",f"{result['components']['scheduled_operating_cost']:,.2f}"); cols[1].metric("Aircraft used",result["schedule"].assigned_aircraft.nunique()); cols[2].metric("Crew used",len(set(";".join(result["schedule"].assigned_crew).split(";")))); cols[3].metric("Average connection gap",f"{m['average_connection_slack_minutes'] or 0:.0f} min")
                st.caption(f"Minimum connection gap: {m['minimum_connection_slack_minutes'] if m['minimum_connection_slack_minutes'] is not None else '—'} min · Tight connections (< minimum turnaround + 30 min): {m['tight_connections']}")
                timeline_cols=st.columns(2)
                with timeline_cols[0]: st.plotly_chart(resource_timeline(result["schedule"],"assigned_aircraft",f"{strategy.title()} aircraft timeline"),use_container_width=True)
                with timeline_cols[1]: st.plotly_chart(resource_timeline(result["schedule"],"assigned_crew",f"{strategy.title()} crew timeline"),use_container_width=True)
                st.caption(f"Optimization score {result['objective']:,.2f}; flexibility penalty {result['components']['flexibility_penalty']:,.2f}. Score is not an operating cost.")
                csv_download(f"Download {strategy} schedule",result["schedule"],f"{strategy}_schedule.csv")
            else: st.error(f"Solver returned {result['status']}; this is not a feasible schedule.")
    
    with tabs[3]:
        st.subheader("Disruption scenario")
        initial=st.session_state.get("initial_results",{})
        if not initial: st.info("Solve at least one initial schedule first.")
        elif "input_snapshot" in st.session_state:
            f,a,c=st.session_state["input_snapshot"]
            flight_ids=f.flight_id.tolist(); aircraft_ids=a.aircraft_id.tolist(); crew_ids=c.crew_id.tolist()
            st.write("Each delay is added once to a fresh copy of the original flight data when recovery runs.")
            delay_ids=st.multiselect("Externally delayed flights",flight_ids,key="delay_ids")
            delay_minutes=st.number_input("Delay minutes for selected flights",0,360,60,15,key="delay_minutes")
            cancel_ids=st.multiselect("Cancel flights",flight_ids,key="cancel_ids")
            unavailable_a=st.multiselect("Unavailable aircraft",aircraft_ids,key="unavailable_a")
            unavailable_c=st.multiselect("Unavailable crew",crew_ids,key="unavailable_c")
            st.markdown("**Selected scenario**")
            st.write({"delays":{i:int(delay_minutes) for i in delay_ids},"cancelled_flights":cancel_ids,"unavailable_aircraft":unavailable_a,"unavailable_crew":unavailable_c})
            if st.button("Recover every solved strategy",type="primary"):
                modified=f.copy(); modified["departure"]=pd.to_datetime(modified.departure); modified["arrival"]=pd.to_datetime(modified.arrival)
                for fid in delay_ids:
                    mask=modified.flight_id==fid
                    modified.loc[mask,["departure","arrival"]]+=pd.Timedelta(minutes=int(delay_minutes))
                recovery={}
                settings=st.session_state["model_settings"]
                for strategy,base in initial.items():
                    if base["status"]!="Optimal": continue
                    oa=dict(zip(base["schedule"].flight_id,base["schedule"].assigned_aircraft))
                    oc={row.flight_id:[x for x in str(row.assigned_crew).split(";") if x] for row in base["schedule"].itertuples()}
                    with st.spinner(f"Recovering {strategy} schedule..."):
                        recovery[strategy]=solve_schedule(modified,a,c,turnaround_minutes=settings["turnaround"],unavailable_aircraft=unavailable_a,unavailable_crew=unavailable_c,cancelled_flights=cancel_ids,original_assignment=oa,original_crew_assignment=oc,allow_cancellation=True,strategy="normal")
                    if recovery[strategy]["status"] == "Optimal":
                        old_aircraft=dict(zip(base["schedule"].flight_id,base["schedule"].assigned_aircraft))
                        old_crew={row.flight_id:set(str(row.assigned_crew).split(";")) for row in base["schedule"].itertuples()}
                        for row in recovery[strategy]["schedule"].itertuples():
                            if row.status == "Cancelled":
                                tag="Cancelled"
                            else:
                                tags=[]
                                if row.flight_id in delay_ids: tags.append("Externally delayed")
                                if old_aircraft.get(row.flight_id) != row.assigned_aircraft: tags.append("Aircraft reassigned")
                                if old_crew.get(row.flight_id,set()) != set(str(row.assigned_crew).split(";")): tags.append("Crew reassigned")
                                tag=" · ".join(tags) if tags else "Unchanged"
                            recovery[strategy]["schedule"].loc[recovery[strategy]["schedule"].flight_id==row.flight_id,"recovery_status"]=tag
                st.session_state["recovery_results"]=recovery
                st.session_state["disrupted_flights"]=modified
                st.session_state["scenario"]={"delay_ids":delay_ids,"delay_minutes":int(delay_minutes),"cancel_ids":cancel_ids,"unavailable_a":unavailable_a,"unavailable_c":unavailable_c}
        for strategy,result in st.session_state.get("recovery_results",{}).items():
            st.markdown(f"#### {strategy.title()} recovery — {result['status']}")
            if result["status"]=="Optimal":
                base=initial[strategy]; st.dataframe(result["schedule"],use_container_width=True)
                metrics=compare_schedules(base["schedule"],result["schedule"],base,result)
                cols=st.columns(4); cols[0].metric("Cancelled flights",metrics["cancelled_flights"]); cols[1].metric("Aircraft reassigned",metrics["reassigned_flights"]); cols[2].metric("Crew changed",metrics["crew_changed_flights"]); cols[3].metric("Final operating cost",f"{metrics['recovery_operating_cost']:,.2f}")
                st.caption(f"Recovery cost change {metrics['recovery_cost_increase']:,.2f}; penalties {result['components']['recovery_penalties']:,.2f}. External delays: {len(st.session_state['scenario']['delay_ids'])}; recovery does not add further delay.")
                metrics["delayed_flights"]=len(st.session_state["scenario"]["delay_ids"])
                timeline_cols=st.columns(2)
                with timeline_cols[0]: st.plotly_chart(resource_timeline(result["schedule"],"assigned_aircraft",f"{strategy.title()} recovered aircraft",base["schedule"]),use_container_width=True)
                with timeline_cols[1]: st.plotly_chart(resource_timeline(result["schedule"],"assigned_crew",f"{strategy.title()} recovered crew",base["schedule"]),use_container_width=True)
                csv_download(f"Download {strategy} recovered schedule",result["schedule"],f"{strategy}_recovered_schedule.csv")
            else: st.error(f"Recovery solver returned {result['status']}.")
    
    with tabs[4]:
        st.subheader("Same disruption, independent recovery MILPs")
        bases=st.session_state.get("initial_results",{}); recs=st.session_state.get("recovery_results",{})
        rows=[]
        for strategy,result in recs.items():
            base=bases[strategy]
            if result["status"]=="Optimal": rows.append({"Strategy":strategy.title(),**compare_schedules(base["schedule"],result["schedule"],base,result)})
            else: rows.append({"Strategy":strategy.title(),"solver_status":result["status"]})
        if rows:
            table=pd.DataFrame(rows); st.dataframe(table,use_container_width=True); csv_download("Download comparison CSV",table,"strategy_comparison.csv")
            valid=table[table.solver_status=="Optimal"]
            if not valid.empty:
                if "scenario" in st.session_state:
                    valid["delayed_flights"] = len(st.session_state["scenario"]["delay_ids"])
                    valid["average_external_delay_minutes"] = st.session_state["scenario"]["delay_minutes"] if st.session_state["scenario"]["delay_ids"] else 0
                for metric,title in [("initial_operating_cost","Initial operating cost"),("recovery_operating_cost","Recovery operating cost"),("total_operational_cost","Total operational cost"),("cancelled_flights","Cancelled flights"),("delayed_flights","Externally delayed flights"),("reassigned_flights","Aircraft reassigned"),("crew_changed_flights","Flights with crew changes")]:
                    st.plotly_chart(px.bar(valid,x="Strategy",y=metric,title=title),use_container_width=True)
                st.caption("Total operational cost = recovered schedule operating cost + cancellation/reassignment penalties. Initial cost is shown for context and is not added again, avoiding double counting. No extra recovery delay is optimized.")
        else: st.info("Run recovery on one or more schedules to compare actual solver results.")
    
    with tabs[5]:
        st.subheader("Model at a glance")
        st.markdown("""
        **Decision variables.** Binary `x[f,a]` assigns flight *f* to aircraft *a*; `y[f,c]` assigns crew; `z[f]` cancels a flight. Binary start, end, and follow variables form time-feasible resource routes.
    
        **Objective.** Initial scheduling minimizes aircraft block-hour cost + crew block-hour cost (plus the flexible strategy's explicit connection shortfall score). Recovery minimizes those operating costs + priority-weighted cancellation penalties + aircraft/crew reassignment penalties. Components are reported separately.
    
        **Constraints.** Each flight is assigned exactly once or cancelled; each operated flight receives its required crew count. Aircraft and crew route flows connect only flights with matching destination/origin and enough time. Initial resource location and availability, type compatibility, crew qualification, crew unavailability and maximum cumulative block hours are enforced.
    
        **Strategy definitions.** Normal uses the actual minimum aircraft turnaround. Buffered adds the selected buffer only for the initial MILP. Flexible uses the normal feasibility threshold and penalizes aircraft route arcs whose available time beyond minimum turnaround is below the target. Recovery always uses the actual turnaround and a common recovery objective.
    
        **Limitations.** Flight times are fixed once the user applies an external delay; the recovery MILP does not choose additional delays. Crew legality is simplified to location continuity, minimum rest, eligibility, availability, and cumulative flight block hours. It does not model duty windows, positioning, pairing rules, certifications beyond the provided type list, or jurisdiction-specific regulations. Each flight needs at least one assigned crew member; leaving the required count blank defaults to one.
        """)
        st.code("min  Σ operating_cost[f,a]·x[f,a] + Σ crew_cost[f,c]·y[f,c] + Σ cancellation_penalty[f]·z[f] + recovery change penalties + optional flexibility score\nΣ_a x[f,a] + z[f] = 1\nΣ_c y[f,c] = required_crew[f]·(1-z[f])\nroute flow: incoming arcs + start = assignment = outgoing arcs + end",language="text")
    
    st.divider(); st.caption("Schedule Rescue · Academic planning simulator · All displayed schedules come from PuLP/CBC MILP solves")
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
    ✓ • 106ms

## Activity

    $ sed -n '1,360p' src/scheduler.py && sed -n '1,360p' src/recovery.py
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
    sed: can't read src/recovery.py: No such file or directory
    ✗ (2) • 97ms

## Activity

    $ cat data/demo_flights.csv && cat data/demo_aircraft.csv && cat data/demo_crew.csv
    flight_id,origin,destination,departure,arrival,aircraft_type_required,required_crew_count,priority
    F001,DEL,BOM,2026-11-10 08:00,2026-11-10 10:00,ANY,1,1
    F002,BOM,BLR,2026-11-10 11:00,2026-11-10 13:00,ANY,1,1
    F003,DEL,BLR,2026-11-10 09:00,2026-11-10 11:00,ANY,1,2
    F004,BLR,DEL,2026-11-10 14:00,2026-11-10 16:00,ANY,1,1
    F005,BOM,DEL,2026-11-10 11:30,2026-11-10 13:30,ANY,1,1
    F006,DEL,BOM,2026-11-10 17:00,2026-11-10 19:00,ANY,1,1
    aircraft_id,initial_location,available_from,cost_per_hour,aircraft_type
    A001,DEL,2026-11-10 06:00,500,A
    A002,DEL,2026-11-10 06:00,450,A
    A003,BOM,2026-11-10 06:00,550,A
    crew_id,initial_location,available_from,eligible_aircraft_types,max_work_hours,cost_per_hour
    C001,DEL,2026-11-10 06:00,A;ANY,10,80
    C002,DEL,2026-11-10 06:00,A;ANY,10,80
    C003,BOM,2026-11-10 06:00,A;ANY,10,80
    C004,DEL,2026-11-10 06:00,A;ANY,10,80
    C005,BOM,2026-11-10 06:00,A;ANY,10,80
    C006,BLR,2026-11-10 06:00,A;ANY,10,80
    C007,DEL,2026-11-10 06:00,A;ANY,10,80
    C008,BLR,2026-11-10 06:00,A;ANY,10,80
    ✓ • 75ms

## Activity

    $ cat README.md && cat docs/assumptions.md && cat docs/methodology.md && cat docs/mathematical_model.md && cat docs/user_guide.md && cat requirements.txt
    # Schedule Rescue
    
    An academic airline schedule planning and disruption recovery simulator. It uses PuLP and CBC to solve a binary mixed-integer linear program for aircraft and crew routing. Schedules shown in the app are solver outputs; an infeasible or non-optimal result is shown as such.
    
    ## Research question
    
    Can a somewhat more expensive initial schedule provide enough aircraft connection slack to reduce cancellations or reassignment impact after disruptions? The application generates Normal, Buffered, and Flexible plans and can recover each under one identical scenario. It reports actual results; no strategy is assumed to win.
    
    ## Features
    
    - Demo, editable manual, and three CSV input datasets.
    - Flight, aircraft, and crew validation with useful errors and downloadable templates.
    - Aircraft routing with initial location/availability, type restrictions, route continuity, and minimum turnaround. Each aircraft follows one continuous route through the planning horizon, with an unrestricted number of connected flights.
    - Crew routing with location, availability, aircraft-type qualifications, minimum rest, cumulative block-hour limits, and required flight staffing.
    - Normal, Buffered, and Flexible initial MILPs.
    - Flight delay and cancellation, aircraft unavailability, and crew unavailability disruptions.
    - Recovery MILP with cancellation, aircraft reassignment, crew reassignment, and operating cost terms reported separately.
    - Repeated strategy comparison, schedule tables, charts, and CSV downloads.
    
    ## Technology and layout
    
    Python 3.11+, Streamlit, pandas, PuLP/CBC, and Plotly.
    
    ```text
    app.py                     Streamlit user interface
    src/validation.py          normalization and input checks
    src/scheduler.py           aircraft + crew MILP for planning/recovery
    src/metrics.py             schedule slack and comparative accounting
    tests/                     small solver-backed regression tests
    docs/                      equations, methodology, assumptions, and guide
    ```
    
    ## Install and run
    
    Use a virtual environment, then install pinned dependencies:
    
    ```bash
    python -m venv .venv
    source .venv/bin/activate       # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    streamlit run app.py
    ```
    
    PuLP's CBC command-line solver must be available. The pinned PuLP distribution used in development bundles CBC. If CBC cannot start, the app will return the solver status instead of inventing a schedule.
    
    ## Using the simulator
    
    1. Choose the demo data, edit the sample tables, or upload flights, aircraft, and crew CSVs. Input IDs must be unique. Times use pandas-readable timestamps. Crew qualifications are semicolon-separated aircraft types; `ANY` matches any type.
    2. Set the actual minimum turnaround and strategy parameters. Solve any or all initial strategies. Check status and actual operating cost; the flexible objective score includes a separate non-cash resilience penalty.
    3. Select externally delayed/cancelled flights or unavailable aircraft/crew. The delay is applied once to a fresh copy of the original data for each recovery solve.
    4. Run recovery and compare the independent strategy results. Download schedules and comparison CSV.
    
    ## Accounting and model
    
    The initial operating cost is the sum of block hours times aircraft hourly cost plus the sum of block hours times crew hourly cost. Recovery reports the recovered operating cost, cancellation penalty and reassignment penalties separately. The comparison's **total operational cost** is recovered operating cost plus recovery penalties. This is algebraically initial cost plus the change in schedule operating cost plus penalties, so the initial schedule is not counted twice. External delay is reflected in time-feasibility and block-hour cost using the shifted flight times; the model has no additional delay decision variable.
    
    Normal minimizes operating cost. Buffered applies additional aircraft turnaround to the initial solve only. Flexible adds a weighted penalty to every selected aircraft connection for slack shortfall below the user target, where slack is the gap between flights minus the minimum turnaround. Both strategies retain actual operating costs as a separate result. Recovery for every strategy uses the same actual turnaround and recovery objective.
    
    The full formulation is in [docs/mathematical_model.md](docs/mathematical_model.md). Data definitions and simplifying assumptions are in [docs/assumptions.md](docs/assumptions.md); instructions are in [docs/user_guide.md](docs/user_guide.md); experiment design is in [docs/methodology.md](docs/methodology.md).
    
    ## Test
    
    ```bash
    python -m unittest discover -s tests -v
    ```
    
    Tests execute CBC on small instances, checking route continuity, equipment/crew availability, external delay, cancellation, crew qualification/duty limits, strategy settings, and an infeasible instance.
    
    ## Limitations and future scope
    
    The model is for demonstration and does not encode full airline dispatch rules. Crew duty is total flight block time, not a regulatory duty-day construct; no pairings, positioning, bases, or jurisdiction-specific limits are modeled. Flight delays are fixed external inputs during recovery; no model-selected retiming, airport closure, or time-window unavailability UI is included. Canceled flights incur a high configurable-in-code priority-weighted penalty; model weights should be calibrated before operational interpretation. Useful extensions include duty windows and pairings, optimized delay variables, airport closures, stochastic disruption sampling, and richer costs.
    # Assumptions and limitations
    
    - All timestamps are local-naive values in one common time zone. Time-zone conversion and daylight-saving transitions are not modeled.
    - A flight's departure and arrival are fixed in initial planning. User-entered external delay shifts both times by the same duration for recovery.
    - An aircraft must start at its initial location and availability time. A flight's required type is matched exactly unless either side uses `ANY`.
    - Consecutive aircraft flights must share an airport and satisfy the selected turnaround. Each aircraft follows one continuous chronological route through the planning horizon, with any number of connected flights; disconnected paths are prohibited so an aircraft cannot reset to its initial location mid-horizon.
    - Crew must start from its declared initial airport, match the required aircraft type (or `ANY`), and have enough connection/rest time and availability. A crew member is not allowed to overlap flights because route arcs enforce chronological connections.
    - Crew duty is approximated by total assigned block hours over the planning horizon. Rest is a minimum connection gap; there are no daily duty windows, pairings, deadheading, base-return, qualification expiry, or regulatory regime-specific rules.
    - Each flight defaults to requiring one crew member. Required crew must be available from the supplied finite pool or the model becomes infeasible/cancels flights in recovery.
    - Aircraft and crew costs are hourly block-time rates. Fuel, airport fees, passenger reaccommodation, delay compensation, maintenance, and cancellation economics are omitted.
    - Flexible slack is evaluated on aircraft route connections, not crew connections. Buffered reserves aircraft turnaround time.
    - Recovery has fixed flight times after external disruption; it cannot optimize added delay.
    - Penalties are illustrative and depend on user cost units; changing weights can change assignments. Do not interpret them as industry-calibrated values.
    - Airport closures and window-specific restrictions have a solver API representation for resources, but no airport closure UI is provided.
    # Methodology
    
    The experiment compares three initial MILP objective/feasibility variants on the same flights, fleet, crew, costs, and actual minimum turnaround. After users select disruptions, the same shifted times and unavailable/cancelled resource set are passed to each independent recovery MILP. Every recovery uses the actual turnaround and the same cancellation and assignment-change penalty defaults.
    
    For each strategy, report initial and final operating cost, change in operating cost, recovery penalties, cancellations, aircraft reassignment, crew changes, use, and solver status. Total operational cost means final scheduled operating cost plus the modeled recovery penalties; adding initial cost as well would double-count operations. Results may favor any strategy or tie. A single chosen disruption is an illustrative scenario, not a statistically general claim; broader research should sample many disruptions and report distributions or averages.
    
    The flexible strategy directly values aircraft connection slack. The buffered strategy instead imposes extra turnaround feasibility. This separates a slack preference from a hard reserve. Recovery returns to common operational rules so results reflect how those initial choices fare after the same event.
    # Mathematical model
    
    ## Sets and input
    
    - `F`: flights; `A`: aircraft; `C`: crew.
    - Flight `i` has origin `o_i`, destination `d_i`, fixed departure `s_i`, arrival `t_i`, required aircraft type `q_i`, crew count `r_i`, and priority `p_i`.
    - Aircraft `a` has initial airport `l_a`, availability time `v_a`, type `Q_a`, and hourly operating rate `c_a`.
    - Crew `c` has initial airport `l_c`, availability `v_c`, qualified types `Q_c`, maximum block hours `H_c`, and hourly rate `w_c`.
    - `τ` is actual aircraft minimum turnaround; `ρ` is minimum crew rest. The buffered initial model uses `τ+B`.
    
    ## Variables
    
    - `x_ia ∈ {0,1}`: aircraft `a` operates flight `i`.
    - `y_ic ∈ {0,1}`: crew member `c` operates flight `i`.
    - `z_i ∈ {0,1}`: flight `i` is cancelled.
    - `u_ia`, `v_ia`, `g_ija`: aircraft route start, end, and follow-arc indicators.
    - `U_ic`, `V_ic`, `G_ijc`: equivalent crew route indicators.
    
    Start and follow arcs are created only where initial location/availability or airport/time compatibility permits. A route arc from `i` to `j` requires `d_i=o_j` and `t_i+gap ≤ s_j`.
    
    ## Coverage and route constraints
    
    Each flight is operated once or cancelled:
    
    `Σ_a x_ia + z_i = 1  ∀i`.
    
    For each aircraft-flight node, route flow is balanced against assignment:
    
    `Σ_j g_jia + u_ia = x_ia`, `Σ_j g_ija + v_ia = x_ia  ∀i,a`.
    
    Each aircraft has at most one route start and one route end over the planning horizon. A continuous route may include any number of flights and return to its initial airport; disconnected components are prohibited because they would reset the aircraft location. Assignment is prohibited if type, availability, or declared unavailability fails.
    
    Crew count per operated flight is exact:
    
    `Σ_c y_ic = r_i(1-z_i)  ∀i`.
    
    Crew route flow uses the same in/out equations with `G,U,V`. Crew arcs require a shared airport, sufficient rest, and availability; crew-flight assignments also require qualification and initial location/time for a route start. Total assigned block time is bounded:
    
    `Σ_i h_i y_ic ≤ H_c  ∀c`, where `h_i=(t_i-s_i)` in hours.
    
    This is a simplified block-hour cap, not a regulatory duty-time model.
    
    ## Operating costs and objectives
    
    `h_i=(t_i-s_i)` hours. Aircraft and crew scheduled operating costs are:
    
    `C_A=Σ_iΣ_a h_i c_a x_ia`, `C_C=Σ_iΣ_c h_i w_c y_ic`.
    
    Normal minimizes `C_A+C_C`.
    
    Buffered minimizes the same expression, but its aircraft arcs require `τ+B` during initial planning. Recovery always reverts to `τ`.
    
    Flexible minimizes `C_A+C_C+λ Σ_(i,j,a) max(0, T - (s_j-t_i-τ))g_ija`, with target slack `T` and weight `λ`. This measures the shortfall between available gap beyond minimum turnaround and the desired slack. It is a resilience score, not cash cost.
    
    Recovery minimizes:
    
    `C_A+C_C + P_cancel Σ_i p_i z_i + P_A Σ_(i,a changed) x_ia + P_C Σ_(i,c changed) y_ic`.
    
    The implementation defaults are `P_cancel=100000`, `P_A=250`, and `P_C=100` in the dataset's cost units. They are exposed in source-level function parameters, not in the interface. Reported components stay separate. Cancellation priorities scale the cancellation term.
    
    ## Disruption representation
    
    - An external delay shifts both fixed times `s_i,t_i` before the recovery MILP is built. It is not applied in-place to session source data.
    - A flight cancellation sets `z_i=1`.
    - Full aircraft or crew unavailability removes all corresponding assignments. The solver API also accepts `(start,end)` unavailability periods, but the UI currently exposes full-resource unavailability only.
    - The recovery objective compares candidate assignments with the selected baseline assignments.
    
    There is no recovery retiming variable, so additional delay minutes are always zero in metrics. A solver result is valid only when CBC reports `Optimal`; other statuses are surfaced without presenting a schedule.
    # User guide
    
    ## 1. Enter data
    
    Choose Demo dataset, Edit manually, or Upload CSV. Flights require `flight_id,origin,destination,departure,arrival`; optional fields are `aircraft_type_required,required_crew_count,priority`. Aircraft require `aircraft_id,initial_location,available_from,cost_per_hour`; optional `aircraft_type` defaults to `ANY`. Crew requires `crew_id,initial_location,available_from,eligible_aircraft_types,max_work_hours,cost_per_hour`. List eligible types with semicolons (for example `A;B`); `ANY` qualifies for every type.
    
    The CSV templates use the current demo schema. The data page reports duplicates, missing values, timestamp errors, invalid durations/costs, and missing type/qualification coverage. Check validation success before solving.
    
    ## 2. Generate initial schedules
    
    Set the operational turnaround and select one or more strategies. Buffered adds its extra time only to aircraft connections in its initial solve. Flexible penalizes aircraft connections whose time slack beyond minimum turnaround is below the target. Compare the separately displayed operating cost and objective score; the flexible score is not a money amount.
    
    ## 3. Create a disruption
    
    Select any set of flights to delay by the same amount or cancel, and any aircraft/crew members to make unavailable. The summary lists the complete scenario. Delays are applied to a fresh original-data copy exactly once for the recovery run.
    
    ## 4. Recover and compare
    
    The app runs a separate recovery MILP for every successful initial plan. A flight labeled Cancelled is not treated as operated. The recovery table shows assigned aircraft and crew. Component costs, cancellation counts, reassignment counts, and solver status are reported. Strategy comparison uses the identical modified flight data and recovery rules.
    
    ## 5. Read the result
    
    - **Operating cost:** aircraft and crew block hours times their hourly rates.
    - **Recovery cost increase:** recovered operating cost minus initial operating cost; can be negative if flights are cancelled.
    - **Cancelled:** flight was explicitly cancelled or had no preferable feasible assignment under the chosen recovery penalties.
    - **Aircraft reassigned / crew changed:** differs from the corresponding initial allocation.
    - **Solver status:** only Optimal is presented as a feasible optimized schedule; other statuses need investigation.
    - **Total operational cost:** final operating cost plus modeled recovery penalties, with initial schedule cost not added twice.
    
    All schedule and comparison tables can be downloaded as CSV.
    streamlit==1.66.1
    pandas==3.1.0
    PuLP==2.9.0
    plotly==7.1.0
    ✓ • 80ms

## Activity

    $ cat src/metrics.py
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
    ✓ • 0ms

## Activity

    $ sed -n '1,360p' src/scheduler.py
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
    ✓ • 0ms

## Activity

    $ sed -n '1,320p' tests/test_schedule_rescue.py
    import unittest
    import pandas as pd
    from src.scheduler import solve_schedule
    from src.validation import prepare_data
    
    
    def data():
        flights=pd.DataFrame([
            ["F1","AAA","BBB","2026-01-01 08:00","2026-01-01 09:00","T",1,1],
            ["F2","BBB","AAA","2026-01-01 10:00","2026-01-01 11:00","T",1,1],
            ["F3","AAA","BBB","2026-01-01 09:30","2026-01-01 10:30","T",1,1]],
            columns=["flight_id","origin","destination","departure","arrival","aircraft_type_required","required_crew_count","priority"])
        aircraft=pd.DataFrame([["A1","AAA","2026-01-01 06:00",100,"T"],["A2","AAA","2026-01-01 06:00",120,"T"],["A3","BBB","2026-01-01 06:00",110,"T"],["A4","AAA","2026-01-01 06:00",130,"T"]],columns=["aircraft_id","initial_location","available_from","cost_per_hour","aircraft_type"])
        crew=pd.DataFrame([["C1","AAA","2026-01-01 06:00","T",8,10],["C2","AAA","2026-01-01 06:00","T",8,10],["C3","BBB","2026-01-01 06:00","T",8,10],["C4","AAA","2026-01-01 06:00","T",8,10]],columns=["crew_id","initial_location","available_from","eligible_aircraft_types","max_work_hours","cost_per_hour"])
        return flights,aircraft,crew
    
    
    class ScheduleModelTests(unittest.TestCase):
        def solve(self,*args,**kwargs):
            result=solve_schedule(*args,**kwargs)
            self.assertEqual(result["status"],"Optimal",result)
            return result
    
        def test_normal_schedule_and_route_continuity(self):
            f,a,c=data(); result=self.solve(f,a,c)
            self.assertEqual(len(result["schedule"]),3)
            active=result["schedule"]
            for _,group in active.groupby("assigned_aircraft"):
                rows=list(group.sort_values("departure").itertuples())
                for left,right in zip(rows,rows[1:]):
                    self.assertEqual(left.destination,right.origin)
                    self.assertGreaterEqual((right.departure-left.arrival).total_seconds()/60,45)
    
        def test_unavailability_reassigns_when_possible(self):
            f,a,c=data(); result=self.solve(f,a,c,unavailable_aircraft=["A1"])
            self.assertNotIn("A1",result["schedule"].assigned_aircraft.tolist())
    
        def test_external_delay_is_applied_once_and_recovers(self):
            f,a,c=data(); initial=self.solve(f,a,c)
            modified=f.copy(); modified["departure"]=pd.to_datetime(modified.departure); modified["arrival"]=pd.to_datetime(modified.arrival)
            modified.loc[modified.flight_id=="F1",["departure","arrival"]]+=pd.Timedelta(minutes=60)
            assign=dict(zip(initial["schedule"].flight_id,initial["schedule"].assigned_aircraft))
            result=self.solve(modified,a,c,original_assignment=assign,allow_cancellation=True)
            self.assertEqual(result["schedule"].loc[result["schedule"].flight_id=="F1","departure"].iloc[0],pd.Timestamp("2026-01-01 09:00"))
    
        def test_crew_can_continue_after_traveling_to_a_new_airport(self):
            f,a,c=data(); f=f[f.flight_id.isin(["F1","F2"])].copy()
            a=a[a.aircraft_id=="A1"].copy(); c=c[c.crew_id=="C1"].copy()
            result=self.solve(f,a,c)
            self.assertEqual(result["schedule"].sort_values("departure").assigned_crew.tolist(),["C1","C1"])
    
        def test_cancellation_is_not_reported_as_operated(self):
            f,a,c=data(); result=self.solve(f,a,c,cancelled_flights=["F1"],allow_cancellation=True)
            row=result["schedule"].set_index("flight_id").loc["F1"]
            self.assertEqual(row.status,"Cancelled"); self.assertTrue(pd.isna(row.assigned_aircraft))
    
        def test_crew_qualification_mismatch_is_rejected(self):
            f,a,c=data(); c["eligible_aircraft_types"]="OTHER"
            with self.assertRaisesRegex(ValueError,"Not enough crew qualified"):
                prepare_data(f,a,c)
    
        def test_duplicate_ids_and_negative_aircraft_cost_are_rejected(self):
            f,a,c=data(); a.loc[1,"aircraft_id"]="A1"
            with self.assertRaisesRegex(ValueError,"unique"):
                prepare_data(f,a,c)
            f,a,c=data(); a.loc[0,"cost_per_hour"]=-1
            with self.assertRaisesRegex(ValueError,"negative"):
                prepare_data(f,a,c)
    
        def test_crew_unavailability_and_duty(self):
            f,a,c=data(); result=self.solve(f,a,c,unavailable_crew=["C1"])
            self.assertNotIn("C1",";".join(result["schedule"].assigned_crew.tolist()))
            scheduled=result["schedule"].sort_values("departure")
            for crew_id in set(x for cell in scheduled.assigned_crew for x in cell.split(";") if x):
                rows=scheduled[scheduled.assigned_crew.str.split(";").map(lambda vals: crew_id in vals)]
                rows=list(rows.sort_values("departure").itertuples())
                for left,right in zip(rows,rows[1:]):
                    self.assertEqual(left.destination,right.origin)
                    self.assertGreaterEqual((right.departure-left.arrival).total_seconds()/60,30)
            c["max_work_hours"]=0.25
            result=self.solve(f,a,c,allow_cancellation=True)
            self.assertGreater((result["schedule"].status=="Cancelled").sum(),0)
    
        def test_insufficient_turnaround_prevents_same_aircraft_connection(self):
            f,a,c=data(); f=f[f.flight_id.isin(["F1","F2"])].copy()
            f.loc[f.flight_id=="F2","departure"]="2026-01-01 09:30"
            f.loc[f.flight_id=="F2","arrival"]="2026-01-01 10:30"
            a=a[a.aircraft_id=="A1"].copy(); a.loc[0,"initial_location"]="AAA"
            result=self.solve(f,a,c,allow_cancellation=True)
            self.assertEqual((result["schedule"].status=="Cancelled").sum(),1)
    
        def test_three_strategies_are_distinct_and_feasible(self):
            f,a,c=data()
            outputs={s:self.solve(f,a,c,strategy=s,buffer_minutes=30,flexibility_target_minutes=90,allow_cancellation=True) for s in ("normal","buffered","flexible")}
            self.assertEqual(outputs["buffered"]["effective_turnaround"],75)
            self.assertEqual(outputs["normal"]["effective_turnaround"],45)
            self.assertGreaterEqual(outputs["flexible"]["components"]["flexibility_penalty"],0)
    
        def test_identical_disruption_is_used_for_all_strategy_recoveries(self):
            f,a,c=data(); delayed=f.copy(); delayed["departure"]=pd.to_datetime(delayed.departure); delayed["arrival"]=pd.to_datetime(delayed.arrival)
            delayed.loc[delayed.flight_id=="F1",["departure","arrival"]]+=pd.Timedelta(minutes=30)
            outputs=[]
            for strategy in ("normal","buffered","flexible"):
                initial=self.solve(f,a,c,strategy=strategy,allow_cancellation=True)
                baseline=dict(zip(initial["schedule"].flight_id,initial["schedule"].assigned_aircraft))
                recovery=self.solve(delayed,a,c,strategy="normal",allow_cancellation=True,original_assignment=baseline,unavailable_aircraft=["A1"])
                outputs.append((recovery["schedule"].set_index("flight_id").loc["F1","departure"],recovery["status"]))
            self.assertEqual(outputs,[(pd.Timestamp("2026-01-01 08:30"),"Optimal")]*3)
    
        def test_type_and_location_constraints(self):
            f,a,c=data(); a.loc[0,"aircraft_type"]="OTHER"
            result=self.solve(f,a,c)
            assigned=result["schedule"].set_index("flight_id").loc["F1","assigned_aircraft"]
            self.assertNotEqual(assigned,"A1")
    
        def test_insufficient_aircraft_is_infeasible(self):
            f,a,c=data(); a=a.iloc[:1].copy()
            result=solve_schedule(f,a,c,allow_cancellation=False)
            self.assertNotEqual(result["status"],"Optimal")
    
    
    if __name__=="__main__": unittest.main()
    ✓ • 0ms

## Activity

    $ sed -n '240,560p' app.py
    ✓ • 0ms

## Activity

    $ cat src/validation.py
    """Input normalization and validation for Schedule Rescue datasets."""
    from __future__ import annotations
    
    import pandas as pd
    
    FLIGHT_COLUMNS = ["flight_id", "origin", "destination", "departure", "arrival"]
    AIRCRAFT_COLUMNS = ["aircraft_id", "initial_location", "available_from", "cost_per_hour"]
    CREW_COLUMNS = ["crew_id", "initial_location", "available_from", "eligible_aircraft_types", "max_work_hours", "cost_per_hour"]
    
    
    def _required(df: pd.DataFrame, cols: list[str], label: str) -> None:
        missing = [c for c in cols if c not in df.columns]
        if missing:
            raise ValueError(f"{label} is missing required column(s): {', '.join(missing)}")
        if df.empty:
            raise ValueError(f"{label} must contain at least one record.")
        if df[cols].isna().any().any():
            bad = [c for c in cols if df[c].isna().any()]
            raise ValueError(f"{label} has missing values in: {', '.join(bad)}")
    
    
    def prepare_data(flights: pd.DataFrame, aircraft: pd.DataFrame, crew: pd.DataFrame | None = None):
        """Return normalized copies, rejecting malformed or incompatible records."""
        f, a = flights.copy(), aircraft.copy()
        _required(f, FLIGHT_COLUMNS, "Flights")
        _required(a, AIRCRAFT_COLUMNS, "Aircraft")
        for col in ("flight_id", "origin", "destination"):
            f[col] = f[col].astype(str).str.strip().str.upper()
            if (f[col] == "").any():
                raise ValueError(f"Flights column {col} cannot be blank.")
        for col in ("aircraft_id", "initial_location"):
            a[col] = a[col].astype(str).str.strip().str.upper()
            if (a[col] == "").any():
                raise ValueError(f"Aircraft column {col} cannot be blank.")
        for df, key, label in ((f, "flight_id", "Flight"), (a, "aircraft_id", "Aircraft")):
            if df[key].duplicated().any():
                duplicates = df.loc[df[key].duplicated(False), key].tolist()
                raise ValueError(f"{label} IDs must be unique; duplicates: {duplicates}")
        f["departure"] = pd.to_datetime(f["departure"], errors="raise")
        f["arrival"] = pd.to_datetime(f["arrival"], errors="raise")
        a["available_from"] = pd.to_datetime(a["available_from"], errors="raise")
        if "aircraft_type_required" not in f: f["aircraft_type_required"] = "ANY"
        if "required_crew_count" not in f: f["required_crew_count"] = 1
        if "priority" not in f: f["priority"] = 1
        if "aircraft_type" not in a: a["aircraft_type"] = "ANY"
        f["aircraft_type_required"] = f["aircraft_type_required"].fillna("ANY").astype(str).str.strip().str.upper()
        f["required_crew_count"] = pd.to_numeric(f["required_crew_count"], errors="raise").fillna(1).astype(int)
        f["priority"] = pd.to_numeric(f["priority"], errors="raise").fillna(1).astype(float)
        a["aircraft_type"] = a["aircraft_type"].fillna("ANY").astype(str).str.strip().str.upper()
        a["cost_per_hour"] = pd.to_numeric(a["cost_per_hour"], errors="raise")
        if (f["arrival"] <= f["departure"]).any():
            raise ValueError("Every flight arrival must be later than departure.")
        if (f["required_crew_count"] < 1).any() or (f["priority"] <= 0).any():
            raise ValueError("Required crew count and priority must be positive.")
        if (a["cost_per_hour"] < 0).any():
            raise ValueError("Aircraft cost_per_hour cannot be negative.")
        if crew is None:
            c = pd.DataFrame(columns=CREW_COLUMNS)
        else:
            c = crew.copy()
            if "cost_per_hour" not in c.columns:
                c["cost_per_hour"] = 0.0
            _required(c, CREW_COLUMNS, "Crew")
            c["crew_id"] = c["crew_id"].astype(str).str.strip().str.upper()
            c["initial_location"] = c["initial_location"].astype(str).str.strip().str.upper()
            c["available_from"] = pd.to_datetime(c["available_from"], errors="raise")
            c["max_work_hours"] = pd.to_numeric(c["max_work_hours"], errors="raise")
            c["cost_per_hour"] = pd.to_numeric(c["cost_per_hour"], errors="raise")
            c["eligible_aircraft_types"] = c["eligible_aircraft_types"].fillna("").astype(str).str.upper()
            if c["crew_id"].duplicated().any():
                raise ValueError("Crew IDs must be unique.")
            if (c[["crew_id", "initial_location"]].eq("").any().any() or (c["max_work_hours"] <= 0).any() or (c["cost_per_hour"] < 0).any()):
                raise ValueError("Crew IDs and locations must be present; max_work_hours must be positive and costs nonnegative.")
        known_airports = set(f["origin"]) | set(f["destination"])
        locations = set(a["initial_location"])
        if not c.empty:
            locations |= set(c["initial_location"])
        unknown = locations - known_airports
        if unknown:
            raise ValueError(f"Initial location(s) do not appear in any flight: {sorted(unknown)}")
        types = set(a["aircraft_type"])
        for req in f["aircraft_type_required"]:
            if req != "ANY" and req not in types:
                raise ValueError(f"No aircraft has required type {req!r}.")
        if not c.empty:
            for req, count in zip(f["aircraft_type_required"], f["required_crew_count"]):
                if req != "ANY":
                    eligible = c["eligible_aircraft_types"].str.split(";").map(lambda xs: req in [x.strip() for x in xs] or "ANY" in [x.strip() for x in xs])
                    if int(eligible.sum()) < count:
                        raise ValueError(f"Not enough crew qualified for aircraft type {req!r} (required {count}).")
        return f.sort_values(["departure", "arrival"]).reset_index(drop=True), a.reset_index(drop=True), c.reset_index(drop=True)
    ✓ • 0ms

## Assistant

## Inspection findings

The repository is a small Streamlit application with a single MILP implementation in `src/scheduler.py`. The requested `src/recovery.py` and `src/robustness.py` files do not exist; recovery currently calls `solve_schedule` directly. There are no experiment scripts or result CSVs. The demo data, existing tests, and documentation are present. The working tree has no reported modifications.

The main functions and defects are:

- **`src/metrics.py:connection_metrics`** measures the connection gap but returns it under names containing “slack.” It does not subtract turnaround time, so a 60-minute gap with 45-minute turnaround is reported as 60 minutes rather than 15 minutes of slack.
- **`src/metrics.py:compare_schedules`** hardcodes `delayed_flights` and delay minutes to zero, counts aircraft and crew changes separately without counting their union, and computes `total_operational_cost` through an algebraically indirect expression. It has no external scenario input, so it cannot distinguish delayed flights that operated from delayed flights that were cancelled.
- **`src/scheduler.py:solve_schedule`** builds schedule rows and cost components after an Optimal solve. Its coverage constraint requires each flight to be assigned or cancelled, but the returned result does not validate coverage before metrics use it. Recovery penalty components include cancellation and assignment changes; the Flexible shortfall score is separate, but there is no general “other recovery penalties” total. Failed solves return an empty schedule, which the UI currently handles by status checks.
- **`app.py` recovery flow** applies external delays before recovery, then adds the number of selected delayed flights to comparison metrics after the fact. That counts cancelled flights as delayed operations. The recovery display, comparison table, charts, and CSV are built through separate code paths; the comparison CSV is made before the delay information is added. The recovery display also uses a generic reassignment metric for aircraft changes.
- **`app.py` result state** clears results when normalized data changes, but not when turnaround, buffer, target, strategy selection, or disruption controls change. Old result tables can therefore remain visible under changed controls. Some settings are stored, but the displayed result does not clearly identify its full solve inputs.
- **Tests** contain 13 solver-backed tests, but none cover the requested metric accounting, stale settings, comparison/CSV consistency, or experiment runner.
- **Documentation** explains the strategy concepts and basic cost identity, but does not define the requested delay categories or gap/slack metrics, and there is no reproducible experiment protocol or results analysis.
- **Demo data** has six flights (`F001`–`F006`), three aircraft (`A001`–`A003`), and eight crew (`C001`–`C008`). These IDs support the proposed scenarios directly.

## Minimal implementation plan

1. Add scenario-aware metric helpers in `src/metrics.py` for delay categories, coverage, gap/slack, unique changed flights, and explicit cost components. Use one computed comparison result as the source for the recovery display, charts, and CSV.
2. Add result validation and solve metadata in `src/scheduler.py` and the Streamlit state flow. Capture the normalized inputs, strategy parameters, turnaround, disruptions, and penalties for each solve; invalidate results when relevant settings change, and avoid metrics for unsuccessful or incomplete solves.
3. Add a standalone experiment runner and analysis script using the existing demo data. Run all three strategies against the same nine scenarios, fail visibly on an infeasible initial solve, record versions and parameters, and write CSV output plus comparison tables/plots.
4. Add regression tests for the listed bugs and runner consistency, then run the requested unittest command and the experiment runner, inspecting their outputs.
5. Update the existing methodology, assumptions, user guide, and README with metric definitions, accounting, experiment instructions, and limitations.

I have not changed any files.

## User

Your inspection findings and minimal implementation plan look good. Proceed with implementation.

Before starting, create a Git checkpoint or commit of the current working version so that we can roll back if necessary.

Please incorporate these additional requirements:

1. Keep operating costs, cancellation penalties, aircraft reassignment penalties, crew reassignment penalties and strategy-specific optimization scores separate.
2. Distinguish externally imposed delay, operated delayed flights, cancelled externally delayed flights and recovery-added delay. Do not count cancelled flights as operated delayed flights.
3. Ensure all three strategies use identical recovery constraints, objective weights and disruption inputs. Strategy-specific preferences should apply only to initial scheduling unless explicitly justified.
4. Record failed and infeasible solves in the experiment results instead of silently dropping them.
5. Ensure all comparison tables, charts and CSV exports use the same computed metrics.
6. Preserve the existing application architecture and working functionality.

Implement the tasks in the order of your proposed plan. Add regression tests as you go.

Do not stop after the implementation plan. Complete the implementation, run the existing and new tests, execute the nine-scenario experiment across all three strategies, and inspect the generated CSV.

At the end, explain the changes in beginner-friendly language and show the actual test and experiment results. Do not claim a test passed unless it was executed successfully.

## Assistant

I’ll first checkpoint the current working version in Git, then implement metrics and result consistency, add regression tests alongside those changes, and build the standalone experiment and analysis tools. I’ll run the requested test command and all 27 strategy/scenario recovery runs, then inspect the saved CSV before reporting results.

## Activity

    $ git status --short && git log -1 --oneline
    863f082 Initial commit: Schedule Rescue airline scheduling simulator
    ✓ • 0ms

## Activity

    $ git tag checkpoint/phase1-before-correctness 863f082 && git status --short && git tag --list 'checkpoint/*'
    fatal: cannot lock ref 'refs/tags/checkpoint/phase1-before-correctness': unable to create directory for .git/refs/tags/checkpoint/phase1-before-correctness
    ✗ (128) • 0ms

## Activity

    $ git tag checkpoint-phase1-before-correctness 863f082 && git status --short && git tag --list 'checkpoint-*'
    checkpoint-phase1-before-correctness
    ✓ • 0ms

## Activity

    file changes: Completed · 1 changes
    Delete: /workspaces/ScheduleRescue/src/metrics.py
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

## Activity

    file changes: Completed · 1 changes
    Add: /workspaces/ScheduleRescue/src/metrics.py
    """Scenario-aware schedule metrics and cost accounting."""
    from __future__ import annotations
    
    import pandas as pd
    
    
    def connection_metrics(schedule, turnaround_minutes=45):
        """Return connection gap (elapsed time) and slack (gap less turnaround)."""
        active = schedule[schedule.status != "Cancelled"].copy()
        gaps = []
        for _, group in active.dropna(subset=["assigned_aircraft"]).groupby("assigned_aircraft"):
            rows = list(group.sort_values("departure").to_dict("records"))
            for left, right in zip(rows, rows[1:]):
                if left["destination"] == right["origin"]:
                    gaps.append((right["departure"] - left["arrival"]).total_seconds() / 60)
        slacks = [gap - turnaround_minutes for gap in gaps]
        return {
            "average_connection_gap_minutes": sum(gaps) / len(gaps) if gaps else None,
            "minimum_connection_gap_minutes": min(gaps) if gaps else None,
            "average_connection_slack_minutes": sum(slacks) / len(slacks) if slacks else None,
            "minimum_connection_slack_minutes": min(slacks) if slacks else None,
            "tight_connections": sum(slack < 30 for slack in slacks),
            "connection_count": len(gaps),
        }
    
    
    def compare_schedules(initial, recovered, initial_result, recovered_result,
                          externally_imposed_delays=None, expected_flight_ids=None,
                          turnaround_minutes=45):
        """Compute one complete comparison row for tables, charts, and downloads.
    
        Externally imposed delays is a mapping from flight ID to added minutes.
        Recovery retiming is not modeled, so recovery-added delay is zero.
        """
        if recovered_result.get("status") != "Optimal":
            raise ValueError("Cannot calculate schedule metrics for a failed solve.")
        a = initial.set_index("flight_id")
        b = recovered.set_index("flight_id")
        expected = set(expected_flight_ids if expected_flight_ids is not None else a.index)
        present = set(b.index)
        operated_mask = b.status != "Cancelled"
        operated = b[operated_mask]
        cancelled = b[b.status == "Cancelled"]
        missing = expected - present
        unexpected = present - expected
        externally_imposed_delays = {str(k): int(v) for k, v in (externally_imposed_delays or {}).items() if int(v) > 0}
        externally_delayed_operated = len(set(operated.index) & set(externally_imposed_delays))
        externally_delayed_cancelled = len(set(cancelled.index) & set(externally_imposed_delays))
        aircraft_changed_ids = {
            fid for fid in operated.index if fid in a.index
            and b.loc[fid, "assigned_aircraft"] != a.loc[fid, "assigned_aircraft"]
        }
        def crew_set(cell):
            return {x for x in str(cell or "").split(";") if x and x.lower() != "nan"}
        crew_changed_ids = {
            fid for fid in operated.index if fid in a.index
            and crew_set(b.loc[fid, "assigned_crew"]) != crew_set(a.loc[fid, "assigned_crew"])
        }
        initial_components = initial_result.get("components", {})
        components = recovered_result.get("components", {})
        initial_cost = float(initial_components.get("scheduled_operating_cost", 0) or 0)
        recovered_cost = float(components.get("scheduled_operating_cost", 0) or 0)
        cancellation = float(components.get("cancellation_penalty", 0) or 0)
        aircraft_penalty = float(components.get("aircraft_reassignment_penalty", 0) or 0)
        crew_penalty = float(components.get("crew_reassignment_penalty", 0) or 0)
        other_penalty = float(components.get("other_recovery_penalties", 0) or 0)
        penalties = cancellation + aircraft_penalty + crew_penalty + other_penalty
        initial_connections = connection_metrics(initial, turnaround_minutes)
        recovered_connections = connection_metrics(recovered, turnaround_minutes)
        return {
            "solver_status": recovered_result.get("status", "Unknown"),
            "initial_operating_cost": initial_cost,
            "recovery_operating_cost": recovered_cost,
            "operating_cost_change": recovered_cost - initial_cost,
            "recovery_cost_increase": recovered_cost - initial_cost,
            "cancellation_penalty": cancellation,
            "aircraft_reassignment_penalty": aircraft_penalty,
            "crew_reassignment_penalty": crew_penalty,
            "other_recovery_penalties": other_penalty,
            "recovery_penalties": penalties,
            "total_modeled_recovery_cost": recovered_cost + penalties,
            "total_operational_cost": recovered_cost + penalties,
            "cancelled_flights": len(cancelled),
            "operated_flights": len(operated),
            "unexpectedly_uncovered_flights": len(missing) + len(unexpected),
            "uncovered_flight_ids": ";".join(sorted(missing | unexpected)),
            "externally_imposed_delay_flights": len(externally_imposed_delays),
            "externally_imposed_delay_minutes": sum(externally_imposed_delays.values()),
            "operated_externally_delayed_flights": externally_delayed_operated,
            "cancelled_externally_delayed_flights": externally_delayed_cancelled,
            "recovery_added_delay_minutes": 0,
            "delayed_flights": externally_delayed_operated,
            "average_additional_delay_minutes": 0,
            "aircraft_changed_flights": len(aircraft_changed_ids),
            "crew_changed_flights": len(crew_changed_ids),
            "unique_changed_flights": len(aircraft_changed_ids | crew_changed_ids),
            "reassigned_flights": len(aircraft_changed_ids),
            "aircraft_in_use": operated.assigned_aircraft.nunique(),
            "crew_in_use": len(set().union(*(crew_set(x) for x in operated.assigned_crew.fillna("")))) if len(operated) else 0,
            "initial_connection_gap_minutes": initial_connections["average_connection_gap_minutes"],
            "initial_connection_slack_minutes": initial_connections["average_connection_slack_minutes"],
            "recovered_connection_gap_minutes": recovered_connections["average_connection_gap_minutes"],
            "recovered_connection_slack_minutes": recovered_connections["average_connection_slack_minutes"],
            "strategy_optimization_score": recovered_result.get("strategy_score", 0),
        }

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /workspaces/ScheduleRescue/src/scheduler.py
    @@ -4,2 +4,3 @@
     import re
    +import time
     import pandas as pd
    @@ -164,3 +165,5 @@
         solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit)
    +    solve_started = time.perf_counter()
         m.solve(solver)
    +    solver_runtime = time.perf_counter() - solve_started
         status = pulp.LpStatus[m.status]
    @@ -168,3 +171,4 @@
             return {"status": status, "schedule": pd.DataFrame(), "objective": None,
    -                "strategy": strategy, "effective_turnaround": op_turn, "components": {}, "solver_message": status}
    +                "strategy": strategy, "effective_turnaround": op_turn, "components": {}, "solver_message": status,
    +                "solver_runtime_seconds": solver_runtime}
         rows=[]
    @@ -177,2 +181,18 @@
         values["recovery_penalties"] = sum(values[k] for k in ("cancellation_penalty","aircraft_reassignment_penalty","crew_reassignment_penalty"))
    -    return {"status":status,"schedule":pd.DataFrame(rows),"objective":float(pulp.value(m.objective)),"strategy":strategy,"effective_turnaround":op_turn,"components":values,"solver_message":status}
    +    schedule = pd.DataFrame(rows)
    +    # Coverage is checked at the solver boundary so later metrics cannot legitimize
    +    # a malformed or partial result.
    +    covered = set(schedule.flight_id)
    +    if len(schedule) != len(F) or covered != set(F):
    +        return {"status":"InvalidSolution", "schedule":pd.DataFrame(), "objective":None,
    +                "strategy":strategy, "effective_turnaround":op_turn, "components":{},
    +                "solver_message":"Solver result did not cover every input flight.",
    +                "solver_runtime_seconds":solver_runtime}
    +    strategy_score = values["flexibility_penalty"] if strategy == "flexible" else 0.0
    +    return {"status":status,"schedule":schedule,"objective":float(pulp.value(m.objective)),"strategy":strategy,"effective_turnaround":op_turn,"components":values,"strategy_score":strategy_score,"solver_message":status,"solver_runtime_seconds":solver_runtime,
    +            "solve_parameters":{"turnaround_minutes":turnaround_minutes,"crew_rest_minutes":crew_rest_minutes,
    +                "strategy":strategy,"buffer_minutes":buffer_minutes,"flexibility_target_minutes":flexibility_target_minutes,
    +                "flexibility_penalty_per_minute":flexibility_penalty_per_minute,"cancellation_penalty":cancellation_penalty,
    +                "aircraft_change_penalty":AIRCRAFT_CHANGE_PENALTY,"crew_change_penalty":CREW_CHANGE_PENALTY,
    +                "unavailable_aircraft":sorted(unavailable_aircraft),"unavailable_crew":sorted(unavailable_crew),
    +                "cancelled_flights":sorted(cancelled_flights),"allow_cancellation":allow_cancellation}}

## Assistant

The rollback checkpoint is now recorded as Git tag `checkpoint-phase1-before-correctness`. I’ve confirmed the app’s recovery path is the scheduler itself, so I’m keeping that architecture and adding shared scenario metrics there. Cost and strategy preference scores will remain distinct; the first regression tests will lock down the corrected gap/slack and delay accounting.

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /workspaces/ScheduleRescue/tests/test_schedule_rescue.py
    @@ -4,2 +4,3 @@
     from src.validation import prepare_data
    +from src.metrics import compare_schedules, connection_metrics
     
    @@ -120,2 +121,29 @@
     
    +    def test_connection_gap_and_slack_are_distinct(self):
    +        f,a,c=data(); result=self.solve(f,a,c)
    +        schedule=result["schedule"].copy()
    +        # Two consecutive flights on this resource have a 60-minute gap.
    +        schedule.loc[schedule.flight_id=="F2","departure"] = pd.Timestamp("2026-01-01 10:00")
    +        schedule.loc[schedule.flight_id=="F1","arrival"] = pd.Timestamp("2026-01-01 09:00")
    +        schedule.loc[schedule.flight_id=="F2","origin"] = schedule.loc[schedule.flight_id=="F1","destination"].iloc[0]
    +        schedule.loc[schedule.flight_id=="F1","assigned_aircraft"]="CHECK"
    +        schedule.loc[schedule.flight_id=="F2","assigned_aircraft"]="CHECK"
    +        metrics=connection_metrics(schedule,45)
    +        self.assertEqual(metrics["average_connection_gap_minutes"],60)
    +        self.assertEqual(metrics["average_connection_slack_minutes"],15)
    +
    +    def test_external_delay_categories_and_cancelled_delay(self):
    +        f,a,c=data(); initial=self.solve(f,a,c)
    +        base=initial["schedule"].copy()
    +        recovered=base.copy()
    +        recovered.loc[recovered.flight_id=="F1","status"]="Cancelled"
    +        recovered.loc[recovered.flight_id=="F1","assigned_aircraft"]=None
    +        recovered.loc[recovered.flight_id=="F1","assigned_crew"]=""
    +        result={"status":"Optimal","components":initial["components"]}
    +        metrics=compare_schedules(base,recovered,initial,result,externally_imposed_delays={"F1":30,"F2":30})
    +        self.assertEqual(metrics["externally_imposed_delay_flights"],2)
    +        self.assertEqual(metrics["operated_externally_delayed_flights"],1)
    +        self.assertEqual(metrics["cancelled_externally_delayed_flights"],1)
    +        self.assertEqual(metrics["recovery_added_delay_minutes"],0)
    +
     

## Activity

    $ python -m unittest discover -s tests -v
    test_cancellation_is_not_reported_as_operated (test_schedule_rescue.ScheduleModelTests.test_cancellation_is_not_reported_as_operated) ... ok
    test_connection_gap_and_slack_are_distinct (test_schedule_rescue.ScheduleModelTests.test_connection_gap_and_slack_are_distinct) ... ok
    test_crew_can_continue_after_traveling_to_a_new_airport (test_schedule_rescue.ScheduleModelTests.test_crew_can_continue_after_traveling_to_a_new_airport) ... ok
    test_crew_qualification_mismatch_is_rejected (test_schedule_rescue.ScheduleModelTests.test_crew_qualification_mismatch_is_rejected) ... ok
    test_crew_unavailability_and_duty (test_schedule_rescue.ScheduleModelTests.test_crew_unavailability_and_duty) ... ok
    test_duplicate_ids_and_negative_aircraft_cost_are_rejected (test_schedule_rescue.ScheduleModelTests.test_duplicate_ids_and_negative_aircraft_cost_are_rejected) ... ok
    test_external_delay_categories_and_cancelled_delay (test_schedule_rescue.ScheduleModelTests.test_external_delay_categories_and_cancelled_delay) ... ok
    test_external_delay_is_applied_once_and_recovers (test_schedule_rescue.ScheduleModelTests.test_external_delay_is_applied_once_and_recovers) ... ok
    test_identical_disruption_is_used_for_all_strategy_recoveries (test_schedule_rescue.ScheduleModelTests.test_identical_disruption_is_used_for_all_strategy_recoveries) ... ok
    test_insufficient_aircraft_is_infeasible (test_schedule_rescue.ScheduleModelTests.test_insufficient_aircraft_is_infeasible) ... ok
    test_insufficient_turnaround_prevents_same_aircraft_connection (test_schedule_rescue.ScheduleModelTests.test_insufficient_turnaround_prevents_same_aircraft_connection) ... ok
    test_normal_schedule_and_route_continuity (test_schedule_rescue.ScheduleModelTests.test_normal_schedule_and_route_continuity) ... ok
    test_three_strategies_are_distinct_and_feasible (test_schedule_rescue.ScheduleModelTests.test_three_strategies_are_distinct_and_feasible) ... ok
    test_type_and_location_constraints (test_schedule_rescue.ScheduleModelTests.test_type_and_location_constraints) ... ok
    test_unavailability_reassigns_when_possible (test_schedule_rescue.ScheduleModelTests.test_unavailability_reassigns_when_possible) ... ok
    
    ----------------------------------------------------------------------
    Ran 15 tests in 0.925s
    
    OK
    ✓ • 12.71s

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /workspaces/ScheduleRescue/app.py
    @@ -25,3 +25,3 @@
     def clear_optimization_state():
    -    for key in ("initial_results","recovery_results","input_snapshot","model_settings","scenario","disrupted_flights"):
    +    for key in ("initial_results","recovery_results","input_snapshot","model_settings","scenario","disrupted_flights","comparison_results"):
             st.session_state.pop(key,None)
    @@ -89,3 +89,6 @@
         target=st.number_input("Target slack for Flexible (minutes)",int(turnaround),360,max(90,int(turnaround)),5,key="target")
    -    chosen=st.multiselect("Strategies to solve",["normal","buffered","flexible"],["normal","buffered","flexible"],format_func=str.title)
    +    chosen=st.multiselect("Strategies to solve",["normal","buffered","flexible"],["normal","buffered","flexible"],format_func=str.title,key="chosen_strategies")
    +    active_settings={"turnaround":int(turnaround),"buffer":int(buffer),"target":int(target),"strategies":list(chosen)}
    +    if st.session_state.get("initial_results") and st.session_state.get("model_settings") != active_settings:
    +        clear_optimization_state()
         if st.button("Solve initial schedule(s)",type="primary"):
    @@ -99,3 +102,3 @@
                 st.session_state["input_snapshot"]=(f.copy(),a.copy(),c.copy())
    -            st.session_state["model_settings"]={"turnaround":turnaround,"buffer":buffer,"target":target}
    +            st.session_state["model_settings"]=active_settings
                 st.session_state.pop("recovery_results",None)
    @@ -106,4 +109,4 @@
                 m=connection_metrics(result["schedule"],int(turnaround))
    -            cols=st.columns(4); cols[0].metric("Operating cost",f"{result['components']['scheduled_operating_cost']:,.2f}"); cols[1].metric("Aircraft used",result["schedule"].assigned_aircraft.nunique()); cols[2].metric("Crew used",len(set(";".join(result["schedule"].assigned_crew).split(";")))); cols[3].metric("Average connection gap",f"{m['average_connection_slack_minutes'] or 0:.0f} min")
    -            st.caption(f"Minimum connection gap: {m['minimum_connection_slack_minutes'] if m['minimum_connection_slack_minutes'] is not None else '—'} min · Tight connections (< minimum turnaround + 30 min): {m['tight_connections']}")
    +            cols=st.columns(4); cols[0].metric("Operating cost",f"{result['components']['scheduled_operating_cost']:,.2f}"); cols[1].metric("Aircraft used",result["schedule"].assigned_aircraft.nunique()); cols[2].metric("Crew used",len(set(";".join(result["schedule"].assigned_crew).split(";")))); cols[3].metric("Average connection slack",f"{m['average_connection_slack_minutes'] or 0:.0f} min")
    +            st.caption(f"Average connection gap: {m['average_connection_gap_minutes'] if m['average_connection_gap_minutes'] is not None else '—'} min · Minimum gap: {m['minimum_connection_gap_minutes'] if m['minimum_connection_gap_minutes'] is not None else '—'} min · Minimum slack: {m['minimum_connection_slack_minutes'] if m['minimum_connection_slack_minutes'] is not None else '—'} min")
                 timeline_cols=st.columns(2)
    @@ -128,2 +131,5 @@
             unavailable_c=st.multiselect("Unavailable crew",crew_ids,key="unavailable_c")
    +        current_scenario={"delay_ids":list(delay_ids),"delay_minutes":int(delay_minutes),"cancel_ids":list(cancel_ids),"unavailable_a":list(unavailable_a),"unavailable_c":list(unavailable_c)}
    +        if st.session_state.get("recovery_results") and st.session_state.get("scenario") != current_scenario:
    +            st.session_state.pop("recovery_results",None); st.session_state.pop("comparison_results",None)
             st.markdown("**Selected scenario**")
    @@ -158,3 +164,12 @@
                 st.session_state["disrupted_flights"]=modified
    -            st.session_state["scenario"]={"delay_ids":delay_ids,"delay_minutes":int(delay_minutes),"cancel_ids":cancel_ids,"unavailable_a":unavailable_a,"unavailable_c":unavailable_c}
    +            st.session_state["scenario"]=current_scenario
    +            comparison={}
    +            for strategy,result in recovery.items():
    +                if result.get("status")=="Optimal":
    +                    comparison[strategy]=compare_schedules(initial[strategy]["schedule"],result["schedule"],initial[strategy],result,
    +                        externally_imposed_delays={fid:int(delay_minutes) for fid in delay_ids},expected_flight_ids=flight_ids,
    +                        turnaround_minutes=settings["turnaround"])
    +                else:
    +                    comparison[strategy]={"solver_status":result.get("status","Unknown")}
    +            st.session_state["comparison_results"]=comparison
         for strategy,result in st.session_state.get("recovery_results",{}).items():
    @@ -163,6 +178,5 @@
                 base=initial[strategy]; st.dataframe(result["schedule"],use_container_width=True)
    -            metrics=compare_schedules(base["schedule"],result["schedule"],base,result)
    -            cols=st.columns(4); cols[0].metric("Cancelled flights",metrics["cancelled_flights"]); cols[1].metric("Aircraft reassigned",metrics["reassigned_flights"]); cols[2].metric("Crew changed",metrics["crew_changed_flights"]); cols[3].metric("Final operating cost",f"{metrics['recovery_operating_cost']:,.2f}")
    -            st.caption(f"Recovery cost change {metrics['recovery_cost_increase']:,.2f}; penalties {result['components']['recovery_penalties']:,.2f}. External delays: {len(st.session_state['scenario']['delay_ids'])}; recovery does not add further delay.")
    -            metrics["delayed_flights"]=len(st.session_state["scenario"]["delay_ids"])
    +            metrics=st.session_state.get("comparison_results",{}).get(strategy,{})
    +            cols=st.columns(4); cols[0].metric("Cancelled flights",metrics["cancelled_flights"]); cols[1].metric("Aircraft changed",metrics["aircraft_changed_flights"]); cols[2].metric("Crew changed",metrics["crew_changed_flights"]); cols[3].metric("Final operating cost",f"{metrics['recovery_operating_cost']:,.2f}")
    +            st.caption(f"Unique flights with assignment changes: {metrics['unique_changed_flights']}. Externally delayed: {metrics['externally_imposed_delay_flights']}; operated delayed: {metrics['operated_externally_delayed_flights']}; cancelled after delay: {metrics['cancelled_externally_delayed_flights']}; recovery-added delay: {metrics['recovery_added_delay_minutes']} minutes.")
                 timeline_cols=st.columns(2)
    @@ -179,3 +193,3 @@
             base=bases[strategy]
    -        if result["status"]=="Optimal": rows.append({"Strategy":strategy.title(),**compare_schedules(base["schedule"],result["schedule"],base,result)})
    +        if result["status"]=="Optimal": rows.append({"Strategy":strategy.title(),**st.session_state.get("comparison_results",{}).get(strategy,{})})
             else: rows.append({"Strategy":strategy.title(),"solver_status":result["status"]})
    @@ -185,8 +199,5 @@
             if not valid.empty:
    -            if "scenario" in st.session_state:
    -                valid["delayed_flights"] = len(st.session_state["scenario"]["delay_ids"])
    -                valid["average_external_delay_minutes"] = st.session_state["scenario"]["delay_minutes"] if st.session_state["scenario"]["delay_ids"] else 0
    -            for metric,title in [("initial_operating_cost","Initial operating cost"),("recovery_operating_cost","Recovery operating cost"),("total_operational_cost","Total operational cost"),("cancelled_flights","Cancelled flights"),("delayed_flights","Externally delayed flights"),("reassigned_flights","Aircraft reassigned"),("crew_changed_flights","Flights with crew changes")]:
    +            for metric,title in [("initial_operating_cost","Initial operating cost"),("recovery_operating_cost","Recovered operating cost"),("total_modeled_recovery_cost","Total modeled recovery cost"),("cancelled_flights","Cancelled flights"),("operated_externally_delayed_flights","Operated externally delayed flights"),("aircraft_changed_flights","Aircraft assignment changes"),("crew_changed_flights","Crew assignment changes"),("unique_changed_flights","Unique flights changed")]:
                     st.plotly_chart(px.bar(valid,x="Strategy",y=metric,title=title),use_container_width=True)
    -            st.caption("Total operational cost = recovered schedule operating cost + cancellation/reassignment penalties. Initial cost is shown for context and is not added again, avoiding double counting. No extra recovery delay is optimized.")
    +            st.caption("Total modeled recovery cost = recovered operating cost + cancellation, aircraft change, crew change, and other recovery penalties. Strategy preference scores are separate. Initial cost is shown for comparison only.")
         else: st.info("Run recovery on one or more schedules to compare actual solver results.")

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /workspaces/ScheduleRescue/app.py
    @@ -28,2 +28,5 @@
     
    +def result_settings_match(saved, current):
    +    return saved == current
    +
     st.title("✈️ Schedule Rescue")
    @@ -91,3 +94,3 @@
         active_settings={"turnaround":int(turnaround),"buffer":int(buffer),"target":int(target),"strategies":list(chosen)}
    -    if st.session_state.get("initial_results") and st.session_state.get("model_settings") != active_settings:
    +    if st.session_state.get("initial_results") and not result_settings_match(st.session_state.get("model_settings"), active_settings):
             clear_optimization_state()

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /workspaces/ScheduleRescue/src/metrics.py
    @@ -6,2 +6,7 @@
     
    +def settings_match(saved, current):
    +    """Whether the controls still describe the solve currently displayed."""
    +    return saved == current
    +
    +
     def connection_metrics(schedule, turnaround_minutes=45):

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /workspaces/ScheduleRescue/app.py
    @@ -8,3 +8,3 @@
     from src.validation import prepare_data
    -from src.metrics import connection_metrics, compare_schedules
    +from src.metrics import connection_metrics, compare_schedules, settings_match
     from src.visualizations import resource_timeline
    @@ -28,5 +28,2 @@
     
    -def result_settings_match(saved, current):
    -    return saved == current
    -
     st.title("✈️ Schedule Rescue")
    @@ -94,3 +91,3 @@
         active_settings={"turnaround":int(turnaround),"buffer":int(buffer),"target":int(target),"strategies":list(chosen)}
    -    if st.session_state.get("initial_results") and not result_settings_match(st.session_state.get("model_settings"), active_settings):
    +    if st.session_state.get("initial_results") and not settings_match(st.session_state.get("model_settings"), active_settings):
             clear_optimization_state()

## Assistant

The initial metrics regressions now pass: 15 tests are green. The Streamlit flow now uses one stored comparison result for its display and exports, separates externally delayed flights from cancellations, and invalidates results when solve controls change. Next I’m adding the standalone runner; it will run each disruption against each initial strategy while using the same Normal recovery model and penalty weights for all three.

## Activity

    file changes: Completed · 1 changes
    Add: /workspaces/ScheduleRescue/experiments/run_experiments.py
    """Run the fixed demo experiment matrix and save one row per scenario/strategy."""
    from __future__ import annotations
    
    import json
    import platform
    import sys
    from pathlib import Path
    
    import pandas as pd
    import pulp
    
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    
    from src.metrics import compare_schedules, connection_metrics
    from src.scheduler import solve_schedule
    from src.validation import prepare_data
    
    STRATEGIES = ("normal", "buffered", "flexible")
    SCENARIOS = (
        {"scenario_id": "S01_none", "delays": {}, "cancel": [], "aircraft": [], "crew": []},
        {"scenario_id": "S02_F001_30m", "delays": {"F001": 30}, "cancel": [], "aircraft": [], "crew": []},
        {"scenario_id": "S03_F001_60m", "delays": {"F001": 60}, "cancel": [], "aircraft": [], "crew": []},
        {"scenario_id": "S04_F001_120m", "delays": {"F001": 120}, "cancel": [], "aircraft": [], "crew": []},
        {"scenario_id": "S05_F003_cancel", "delays": {}, "cancel": ["F003"], "aircraft": [], "crew": []},
        {"scenario_id": "S06_A002_unavailable", "delays": {}, "cancel": [], "aircraft": ["A002"], "crew": []},
        {"scenario_id": "S07_C001_unavailable", "delays": {}, "cancel": [], "aircraft": [], "crew": ["C001"]},
        {"scenario_id": "S08_F001_30m_A002", "delays": {"F001": 30}, "cancel": [], "aircraft": ["A002"], "crew": []},
        {"scenario_id": "S09_A002_C001", "delays": {}, "cancel": [], "aircraft": ["A002"], "crew": ["C001"]},
    )
    INITIAL_PARAMETERS = {"turnaround_minutes": 45, "crew_rest_minutes": 30,
                         "buffer_minutes": 30, "flexibility_target_minutes": 90,
                         "flexibility_penalty_per_minute": 5}
    RECOVERY_PARAMETERS = {"turnaround_minutes": 45, "crew_rest_minutes": 30,
                           "cancellation_penalty": 100000.0,
                           "aircraft_change_penalty": 250.0,
                           "crew_change_penalty": 100.0,
                           "recovery_strategy": "normal"}
    
    
    def _versions():
        return {"python": platform.python_version(), "pandas": pd.__version__,
                "pulp": pulp.__version__, "available_solvers": pulp.listSolvers(onlyAvailable=True),
                "platform": platform.platform()}
    
    
    def _apply_delays(flights, delays):
        modified = flights.copy()
        for column in ("departure", "arrival"):
            modified[column] = pd.to_datetime(modified[column])
        for flight_id, minutes in delays.items():
            mask = modified.flight_id == flight_id
            modified.loc[mask, ["departure", "arrival"]] += pd.Timedelta(minutes=minutes)
        return modified
    
    
    def run_experiments(output_path=None):
        flights, aircraft, crew = prepare_data(
            pd.read_csv(ROOT / "data/demo_flights.csv"),
            pd.read_csv(ROOT / "data/demo_aircraft.csv"),
            pd.read_csv(ROOT / "data/demo_crew.csv"))
        unknown = (set().union(*(set(x["delays"]) | set(x["cancel"]) for x in SCENARIOS)) - set(flights.flight_id))
        unknown |= set().union(*(set(x["aircraft"]) for x in SCENARIOS)) - set(aircraft.aircraft_id)
        unknown |= set().union(*(set(x["crew"]) for x in SCENARIOS)) - set(crew.crew_id)
        if unknown:
            raise ValueError(f"Experiment scenarios reference missing demo IDs: {sorted(unknown)}")
        rows = []
        for strategy in STRATEGIES:
            try:
                initial = solve_schedule(flights, aircraft, crew, strategy=strategy,
                                         **{k: v for k, v in INITIAL_PARAMETERS.items() if k != "crew_rest_minutes"})
            except Exception as exc:
                initial = {"status": "Error", "solver_message": str(exc), "schedule": pd.DataFrame(), "components": {}}
            for scenario in SCENARIOS:
                row = {"scenario_id": scenario["scenario_id"], "strategy": strategy,
                       "scenario_parameters": json.dumps(scenario, sort_keys=True),
                       "initial_parameters": json.dumps({**INITIAL_PARAMETERS, "strategy": strategy}, sort_keys=True),
                       "recovery_parameters": json.dumps(RECOVERY_PARAMETERS, sort_keys=True),
                       "dependency_versions": json.dumps(_versions(), sort_keys=True),
                       "initial_solver_status": initial.get("status", "Unknown"),
                       "solver_status": "NotRunInitialInfeasible", "solver_runtime_seconds": None,
                       "initial_operating_cost": None, "recovered_operating_cost": None,
                       "recovery_penalties": None, "cancellation_penalty": None,
                       "aircraft_reassignment_penalty": None, "crew_reassignment_penalty": None,
                       "strategy_optimization_score": None, "cancelled_flights": None,
                       "operated_delayed_flights": None, "total_delay_minutes": None,
                       "aircraft_reassignment_count": None, "crew_reassignment_count": None,
                       "unique_changed_flight_count": None, "initial_connection_slack": None,
                       "recovered_connection_slack": None, "initial_error": initial.get("solver_message", ""),
                       "recovery_error": ""}
                if initial.get("status") != "Optimal":
                    row["solver_status"] = "NotRunInitialInfeasible"
                    rows.append(row)
                    continue
                disrupted = _apply_delays(flights, scenario["delays"])
                assignment = dict(zip(initial["schedule"].flight_id, initial["schedule"].assigned_aircraft))
                crew_assignment = {r.flight_id: [x for x in str(r.assigned_crew).split(";") if x]
                                   for r in initial["schedule"].itertuples()}
                try:
                    recovered = solve_schedule(disrupted, aircraft, crew,
                        turnaround_minutes=RECOVERY_PARAMETERS["turnaround_minutes"],
                        crew_rest_minutes=RECOVERY_PARAMETERS["crew_rest_minutes"],
                        unavailable_aircraft=scenario["aircraft"], unavailable_crew=scenario["crew"],
                        cancelled_flights=scenario["cancel"], original_assignment=assignment,
                        original_crew_assignment=crew_assignment, allow_cancellation=True,
                        strategy="normal", cancellation_penalty=RECOVERY_PARAMETERS["cancellation_penalty"])
                except Exception as exc:
                    recovered = {"status": "Error", "solver_message": str(exc), "schedule": pd.DataFrame(), "components": {}}
                row["solver_status"] = recovered.get("status", "Unknown")
                row["solver_runtime_seconds"] = recovered.get("solver_runtime_seconds")
                row["recovery_error"] = recovered.get("solver_message", "")
                if recovered.get("status") == "Optimal":
                    metrics = compare_schedules(initial["schedule"], recovered["schedule"], initial, recovered,
                        externally_imposed_delays=scenario["delays"], expected_flight_ids=flights.flight_id,
                        turnaround_minutes=RECOVERY_PARAMETERS["turnaround_minutes"])
                    row.update({"initial_operating_cost": metrics["initial_operating_cost"],
                        "recovered_operating_cost": metrics["recovery_operating_cost"],
                        "recovery_penalties": metrics["recovery_penalties"],
                        "cancellation_penalty": metrics["cancellation_penalty"],
                        "aircraft_reassignment_penalty": metrics["aircraft_reassignment_penalty"],
                        "crew_reassignment_penalty": metrics["crew_reassignment_penalty"],
                        "strategy_optimization_score": initial.get("strategy_score", 0),
                        "cancelled_flights": metrics["cancelled_flights"],
                        "operated_delayed_flights": metrics["operated_externally_delayed_flights"],
                        "total_delay_minutes": metrics["externally_imposed_delay_minutes"],
                        "aircraft_reassignment_count": metrics["aircraft_changed_flights"],
                        "crew_reassignment_count": metrics["crew_changed_flights"],
                        "unique_changed_flight_count": metrics["unique_changed_flights"],
                        "initial_connection_slack": connection_metrics(initial["schedule"], 45)["average_connection_slack_minutes"],
                        "recovered_connection_slack": connection_metrics(recovered["schedule"], 45)["average_connection_slack_minutes"]})
                rows.append(row)
        result = pd.DataFrame(rows)
        path = Path(output_path) if output_path else ROOT / "experiments/results/experiment_results.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        result.to_csv(path, index=False)
        return result, path
    
    
    if __name__ == "__main__":
        frame, path = run_experiments()
        print(f"Saved {len(frame)} rows to {path}")
        print(frame.groupby(["strategy", "solver_status"], dropna=False).size().to_string())

## Activity

    file changes: Completed · 1 changes
    Add: /workspaces/ScheduleRescue/experiments/analyze_results.py
    """Summarize experiment CSVs and generate shareable comparison charts."""
    from pathlib import Path
    import sys
    
    import pandas as pd
    import plotly.express as px
    
    ROOT = Path(__file__).resolve().parents[1]
    
    
    def analyze(path=None):
        source = Path(path) if path else ROOT / "experiments/results/experiment_results.csv"
        data = pd.read_csv(source)
        output = source.parent / "analysis"
        output.mkdir(parents=True, exist_ok=True)
        successful = data[data.solver_status == "Optimal"].copy()
        summaries = successful.groupby("strategy", as_index=False).agg(
            scenario_count=("scenario_id", "count"),
            initial_operating_cost=("initial_operating_cost", "mean"),
            recovered_operating_cost=("recovered_operating_cost", "mean"),
            recovery_penalties=("recovery_penalties", "mean"),
            cancelled_flights=("cancelled_flights", "mean"),
            operated_delayed_flights=("operated_delayed_flights", "mean"),
            aircraft_reassignment_count=("aircraft_reassignment_count", "mean"),
            crew_reassignment_count=("crew_reassignment_count", "mean"),
            unique_changed_flight_count=("unique_changed_flight_count", "mean"),
            initial_connection_slack=("initial_connection_slack", "mean"),
            recovered_connection_slack=("recovered_connection_slack", "mean"))
        summaries.to_csv(output / "strategy_comparison.csv", index=False)
        # Per-scenario results and differences remain visible; no average is used
        # to imply that a strategy wins in every case.
        pivot = successful.pivot(index="scenario_id", columns="strategy", values="recovered_operating_cost")
        differences = pivot.copy()
        for strategy in pivot.columns:
            differences[strategy] = pivot[strategy] - pivot.min(axis=1)
        differences.to_csv(output / "scenario_cost_differences.csv")
        successful.to_csv(output / "successful_scenario_metrics.csv", index=False)
        data[data.solver_status != "Optimal"].to_csv(output / "failed_solves.csv", index=False)
        charts = [
            ("initial_vs_recovered_cost.html", ["initial_operating_cost", "recovered_operating_cost"], "Operating costs by scenario"),
            ("cancellations.html", ["cancelled_flights"], "Cancelled flights"),
            ("assignment_changes.html", ["aircraft_reassignment_count", "crew_reassignment_count", "unique_changed_flight_count"], "Assignment changes"),
            ("delay_comparison.html", ["operated_delayed_flights", "total_delay_minutes"], "External delay exposure"),
        ]
        long = successful.melt(id_vars=["scenario_id", "strategy"], var_name="metric", value_name="value")
        for filename, metrics, title in charts:
            frame = long[long.metric.isin(metrics)]
            fig = px.bar(frame, x="scenario_id", y="value", color="strategy", barmode="group", facet_col="metric", title=title)
            fig.write_html(output / filename, include_plotlyjs="cdn")
        print(f"Analyzed {len(data)} rows ({len(successful)} optimal, {len(data)-len(successful)} failed or not run).")
        print(summaries.to_string(index=False))
        print(f"Analysis files: {output}")
        print("Scenario cost differences (each strategy minus that scenario's lowest recovered operating cost):")
        print(differences.to_string())
        return summaries, differences
    
    
    if __name__ == "__main__":
        analyze(sys.argv[1] if len(sys.argv) > 1 else None)

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /workspaces/ScheduleRescue/tests/test_schedule_rescue.py
    @@ -4,3 +4,5 @@
     from src.validation import prepare_data
    -from src.metrics import compare_schedules, connection_metrics
    +from src.metrics import compare_schedules, connection_metrics, settings_match
    +from pathlib import Path
    +from tempfile import TemporaryDirectory
     
    @@ -122,10 +124,5 @@
         def test_connection_gap_and_slack_are_distinct(self):
    -        f,a,c=data(); result=self.solve(f,a,c)
    -        schedule=result["schedule"].copy()
    -        # Two consecutive flights on this resource have a 60-minute gap.
    -        schedule.loc[schedule.flight_id=="F2","departure"] = pd.Timestamp("2026-01-01 10:00")
    -        schedule.loc[schedule.flight_id=="F1","arrival"] = pd.Timestamp("2026-01-01 09:00")
    -        schedule.loc[schedule.flight_id=="F2","origin"] = schedule.loc[schedule.flight_id=="F1","destination"].iloc[0]
    -        schedule.loc[schedule.flight_id=="F1","assigned_aircraft"]="CHECK"
    -        schedule.loc[schedule.flight_id=="F2","assigned_aircraft"]="CHECK"
    +        schedule=pd.DataFrame([
    +            {"flight_id":"X","origin":"AAA","destination":"BBB","departure":pd.Timestamp("2026-01-01 08:00"),"arrival":pd.Timestamp("2026-01-01 09:00"),"assigned_aircraft":"CHECK","assigned_crew":"C1","status":"Scheduled"},
    +            {"flight_id":"Y","origin":"BBB","destination":"CCC","departure":pd.Timestamp("2026-01-01 10:00"),"arrival":pd.Timestamp("2026-01-01 11:00"),"assigned_aircraft":"CHECK","assigned_crew":"C1","status":"Scheduled"}])
             metrics=connection_metrics(schedule,45)
    @@ -148,2 +145,44 @@
     
    +    def test_cost_identity_unique_changes_and_uncovered_flights(self):
    +        f,a,c=data(); initial=self.solve(f,a,c)
    +        recovered=initial["schedule"].copy()
    +        recovered.loc[recovered.flight_id=="F1","assigned_aircraft"]="A-NEW"
    +        recovered.loc[recovered.flight_id=="F1","assigned_crew"]="C-NEW"
    +        comps={"scheduled_operating_cost":70,"cancellation_penalty":3,
    +               "aircraft_reassignment_penalty":5,"crew_reassignment_penalty":7,
    +               "other_recovery_penalties":2}
    +        solved={"status":"Optimal","components":comps}
    +        metrics=compare_schedules(initial["schedule"],recovered,initial,solved)
    +        self.assertEqual(metrics["aircraft_changed_flights"],1)
    +        self.assertEqual(metrics["crew_changed_flights"],1)
    +        self.assertEqual(metrics["unique_changed_flights"],1)
    +        self.assertEqual(metrics["recovery_penalties"],17)
    +        self.assertEqual(metrics["total_modeled_recovery_cost"],87)
    +        partial=recovered[recovered.flight_id!="F1"]
    +        incomplete=compare_schedules(initial["schedule"],partial,initial,solved,expected_flight_ids=["F1","F2","F3"])
    +        self.assertEqual(incomplete["unexpectedly_uncovered_flights"],1)
    +
    +    def test_stale_result_settings_are_rejected(self):
    +        used={"turnaround":45,"buffer":30,"target":90,"strategies":["normal"]}
    +        self.assertTrue(settings_match(used,dict(used)))
    +        self.assertFalse(settings_match(used,{**used,"turnaround":60}))
    +
    +    def test_comparison_metrics_round_trip_to_csv(self):
    +        f,a,c=data(); initial=self.solve(f,a,c)
    +        metrics=compare_schedules(initial["schedule"],initial["schedule"],initial,initial)
    +        table=pd.DataFrame([{"Strategy":"Normal",**metrics}])
    +        restored=pd.read_csv(pd.io.common.StringIO(table.to_csv(index=False)))
    +        self.assertEqual(list(table.columns),list(restored.columns))
    +        self.assertEqual(table.iloc[0]["total_modeled_recovery_cost"],restored.iloc[0]["total_modeled_recovery_cost"])
    +
    +    def test_experiment_runner_uses_all_strategies_for_same_scenarios(self):
    +        from experiments.run_experiments import SCENARIOS, STRATEGIES, run_experiments
    +        with TemporaryDirectory() as tmp:
    +            result,path=run_experiments(Path(tmp)/"out.csv")
    +            self.assertEqual(len(result),len(SCENARIOS)*len(STRATEGIES))
    +            self.assertEqual(set(result.strategy),set(STRATEGIES))
    +            for scenario_id,group in result.groupby("scenario_id"):
    +                self.assertEqual(set(group.strategy),set(STRATEGIES),scenario_id)
    +            self.assertTrue(Path(path).exists())
    +
     

## Activity

    $ rg -n 'Normal minimizes|strategy directly|Accounting and model|## Test' README.md docs/methodology.md
    README.md:53:## Accounting and model
    README.md:57:Normal minimizes operating cost. Buffered applies additional aircraft turnaround to the initial solve only. Flexible adds a weighted penalty to every selected aircraft connection for slack shortfall below the user target, where slack is the gap between flights minus the minimum turnaround. Both strategies retain actual operating costs as a separate result. Recovery for every strategy uses the same actual turnaround and recovery objective.
    README.md:61:## Test
    docs/methodology.md:7:The flexible strategy directly values aircraft connection slack. The buffered strategy instead imposes extra turnaround feasibility. This separates a slack preference from a hard reserve. Recovery returns to common operational rules so results reflect how those initial choices fare after the same event.
    ✓ • 0ms

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /workspaces/ScheduleRescue/README.md
    @@ -58,2 +58,17 @@
     
    +Connection **gap** is the minutes between one flight's arrival and the next departure. Connection **slack** is gap minus required turnaround. External delay metrics distinguish selected delayed flights and total imposed minutes from delayed flights that operated and delayed flights that were cancelled. The model has no recovery retiming decision, so recovery-added delay is zero. Assignment changes report aircraft and crew separately plus the union of unique affected flights.
    +
    +Recovery cost is recovered operating cost plus cancellation, aircraft reassignment, crew reassignment, and any other recovery penalties. Initial operating cost is shown only as a reference; its full value is not added again. Flexible strategy's connection shortfall score is an optimization preference and is reported separately from operating cost and recovery penalties.
    +
    +## Reproducible experiment
    +
    +Run from the repository root:
    +
    +```bash
    +python experiments/run_experiments.py
    +python experiments/analyze_results.py
    +```
    +
    +The runner saves every one of nine scenarios for all three strategies in `experiments/results/experiment_results.csv`, including failed solves. Recovery uses the same Normal objective, penalties, actual turnaround, and resource disruption rules for every initial strategy. The analysis writes strategy summaries, per-scenario cost differences, failed-solve rows, and interactive HTML charts under `experiments/results/analysis/`. CBC can choose different equal-cost optima across versions or environments; recorded dependency and platform versions support comparison, but exact assignment tie-breaking is not guaranteed.
    +
     The full formulation is in [docs/mathematical_model.md](docs/mathematical_model.md). Data definitions and simplifying assumptions are in [docs/assumptions.md](docs/assumptions.md); instructions are in [docs/user_guide.md](docs/user_guide.md); experiment design is in [docs/methodology.md](docs/methodology.md).

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /workspaces/ScheduleRescue/docs/methodology.md
    @@ -7 +7,9 @@
     The flexible strategy directly values aircraft connection slack. The buffered strategy instead imposes extra turnaround feasibility. This separates a slack preference from a hard reserve. Recovery returns to common operational rules so results reflect how those initial choices fare after the same event.
    +
    +## Demo experiment protocol
    +
    +`python experiments/run_experiments.py` executes nine fixed scenarios against Normal, Buffered, and Flexible initial schedules using `data/demo_*.csv`. Every strategy receives the same disrupted flight times, cancellation selection, unavailable resources, actual recovery turnaround, cancellation penalty, and reassignment weights. Initial Buffered and Flexible settings affect only their initial MILPs; every recovery MILP uses the Normal recovery formulation. Scenarios cover no disruption, F001 delayed 30/60/120 minutes, F003 cancellation, A002 unavailable, C001 unavailable, a delay plus aircraft disruption, and combined aircraft and crew unavailability.
    +
    +Each scenario/strategy pair is kept in the output, including an explicit initial infeasibility, recovery infeasibility, or solver error. An infeasible initial plan is not silently substituted or dropped. The result CSV includes parameters, solver statuses/runtime, dependency/platform versions, cost components, coverage and assignment metrics, and average initial/recovered connection slack. `python experiments/analyze_results.py` produces strategy-level means and per-scenario operating cost differences, plus chart HTML files. The analysis is descriptive: it has nine illustrative cases from one small demo dataset, not a statistical sample supporting a universal strategy ranking.
    +
    +PuLP and CBC can return different assignments when multiple solutions have equal objective value. Dependency and platform versions are recorded; exact tie-breaking and timing may vary. Runtime is measured around the solver call. Strategy optimization scores are not included in operating costs or recovery penalty totals.

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /workspaces/ScheduleRescue/docs/assumptions.md
    @@ -12,2 +12,6 @@
     - Recovery has fixed flight times after external disruption; it cannot optimize added delay.
    +- Connection gap is next departure minus previous arrival; connection slack is the gap minus the required aircraft turnaround. A 60-minute gap with a 45-minute turnaround therefore has 15 minutes of slack.
    +- An externally imposed delay is the selected input duration. Operated externally delayed flights exclude flights that are cancelled. Cancelled externally delayed flights are reported separately. Recovery-added delay is zero because retiming is not a decision in this model.
    +- Total modeled recovery cost equals recovered operating cost plus cancellation penalties, aircraft reassignment penalties, crew reassignment penalties, and any other recovery penalties. Initial cost change is reported for context but is not added as another cost. The Flexible optimization score is separate from cash-like operating costs and recovery penalties.
    +- Schedule coverage counts operated, cancelled, and unexpectedly uncovered flights. Solver failures do not produce valid schedule metrics.
     - Penalties are illustrative and depend on user cost units; changing weights can change assignments. Do not interpret them as industry-calibrated values.

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /workspaces/ScheduleRescue/docs/user_guide.md
    @@ -29,2 +29,10 @@
     
    +- **Connection gap:** next departure minus previous arrival on the same aircraft route. **Connection slack:** connection gap minus required turnaround.
    +- **Externally imposed delays:** the user selected delay count and minutes. **Operated delayed flights** exclude delayed flights that were cancelled; those appear separately as **cancelled after external delay**. Recovery-added delay is zero because the model does not retime flights.
    +- **Unique changed flights:** the union of flights with aircraft or crew assignment changes; the two change counts are also reported separately.
    +- **Unexpectedly uncovered flights:** expected flight IDs absent from the accepted schedule. An incomplete result is not treated as a successful solver schedule.
    +- **Recovery cost:** recovered operating cost plus cancellation, aircraft change, crew change, and other recovery penalties. The Flexible strategy score is shown separately and is not an operating cost.
    +
    +Changing the input data, strategy selection, turnaround, buffer, or target clears results generated under the earlier settings. Changing a disruption clears its recovery and comparison outputs. Each solve also retains its model settings for reproducibility.
    +
     All schedule and comparison tables can be downloaded as CSV.

## Activity

    $ python -m unittest discover -s tests -v
    test_cancellation_is_not_reported_as_operated (test_schedule_rescue.ScheduleModelTests.test_cancellation_is_not_reported_as_operated) ... ok
    test_comparison_metrics_round_trip_to_csv (test_schedule_rescue.ScheduleModelTests.test_comparison_metrics_round_trip_to_csv) ... ok
    test_connection_gap_and_slack_are_distinct (test_schedule_rescue.ScheduleModelTests.test_connection_gap_and_slack_are_distinct) ... ok
    test_cost_identity_unique_changes_and_uncovered_flights (test_schedule_rescue.ScheduleModelTests.test_cost_identity_unique_changes_and_uncovered_flights) ... ok
    test_crew_can_continue_after_traveling_to_a_new_airport (test_schedule_rescue.ScheduleModelTests.test_crew_can_continue_after_traveling_to_a_new_airport) ... ok
    test_crew_qualification_mismatch_is_rejected (test_schedule_rescue.ScheduleModelTests.test_crew_qualification_mismatch_is_rejected) ... ok
    test_crew_unavailability_and_duty (test_schedule_rescue.ScheduleModelTests.test_crew_unavailability_and_duty) ... ok
    test_duplicate_ids_and_negative_aircraft_cost_are_rejected (test_schedule_rescue.ScheduleModelTests.test_duplicate_ids_and_negative_aircraft_cost_are_rejected) ... ok
    test_experiment_runner_uses_all_strategies_for_same_scenarios (test_schedule_rescue.ScheduleModelTests.test_experiment_runner_uses_all_strategies_for_same_scenarios) ... ok
    test_external_delay_categories_and_cancelled_delay (test_schedule_rescue.ScheduleModelTests.test_external_delay_categories_and_cancelled_delay) ... ok
    test_external_delay_is_applied_once_and_recovers (test_schedule_rescue.ScheduleModelTests.test_external_delay_is_applied_once_and_recovers) ... ok
    test_identical_disruption_is_used_for_all_strategy_recoveries (test_schedule_rescue.ScheduleModelTests.test_identical_disruption_is_used_for_all_strategy_recoveries) ... ok
    test_insufficient_aircraft_is_infeasible (test_schedule_rescue.ScheduleModelTests.test_insufficient_aircraft_is_infeasible) ... ok
    test_insufficient_turnaround_prevents_same_aircraft_connection (test_schedule_rescue.ScheduleModelTests.test_insufficient_turnaround_prevents_same_aircraft_connection) ... ok
    test_normal_schedule_and_route_continuity (test_schedule_rescue.ScheduleModelTests.test_normal_schedule_and_route_continuity) ... ok
    test_stale_result_settings_are_rejected (test_schedule_rescue.ScheduleModelTests.test_stale_result_settings_are_rejected) ... ok
    test_three_strategies_are_distinct_and_feasible (test_schedule_rescue.ScheduleModelTests.test_three_strategies_are_distinct_and_feasible) ... ok
    test_type_and_location_constraints (test_schedule_rescue.ScheduleModelTests.test_type_and_location_constraints) ... ok
    test_unavailability_reassigns_when_possible (test_schedule_rescue.ScheduleModelTests.test_unavailability_reassigns_when_possible) ... ok
    
    ----------------------------------------------------------------------
    Ran 19 tests in 3.074s
    
    OK
    ✓ • 3.51s

## Assistant

The expanded test suite now passes all 19 tests, including a full run of the experiment runner to verify the 3×9 matrix and matching scenarios. I’m running the requested saved experiment and analysis now, then I’ll inspect solver statuses, CSV row coverage, accounting consistency, and the generated analysis files.

## Activity

    $ python experiments/run_experiments.py
    Saved 27 rows to /workspaces/ScheduleRescue/experiments/results/experiment_results.csv
    strategy  solver_status
    buffered  Optimal          9
    flexible  Optimal          9
    normal    Optimal          9
    ✓ • 2.56s

## Activity

    $ python experiments/analyze_results.py && python -c 'import pandas as pd; p="experiments/results/experiment_results.csv"; d=pd.read_csv(p); print("rows",len(d),"unique scenarios",d.scenario_id.nunique(),"strategies",sorted(d.strategy.unique())); print(d[["scenario_id","strategy","solver_status","initial_operating_cost","recovered_operating_cost","recovery_penalties","cancelled_flights","operated_delayed_flights","aircraft_reassignment_count","crew_reassignment_count","unique_changed_flight_count"]].to_string(index=False)); print("all statuses:",d.solver_status.value_counts().to_dict()); print("all exact 3x9:",len(d)==27 and d.groupby("scenario_id").strategy.nunique().eq(3).all())'
    Analyzed 27 rows (27 optimal, 0 failed or not run).
    strategy  scenario_count  initial_operating_cost  recovered_operating_cost  recovery_penalties  cancelled_flights  operated_delayed_flights  aircraft_reassignment_count  crew_reassignment_count  unique_changed_flight_count  initial_connection_slack  recovered_connection_slack
    buffered               9                  6760.0               5755.555556       111388.888889                1.0                  0.333333                     0.666667                 1.111111                     1.777778                     115.0                   87.222222
    flexible               9                  6760.0               5755.555556       111344.444444                1.0                  0.333333                     0.666667                 0.666667                     0.777778                     115.0                   87.222222
      normal               9                  6660.0               5666.666667       111483.333333                1.0                  0.333333                     1.444444                 0.111111                     1.555556                      15.0                   58.333333
    Analysis files: /workspaces/ScheduleRescue/experiments/results/analysis
    Scenario cost differences (each strategy minus that scenario's lowest recovered operating cost):
    strategy              buffered  flexible  normal
    scenario_id
    S01_none                 100.0     100.0     0.0
    S02_F001_30m               0.0       0.0     0.0
    S03_F001_60m             200.0     200.0     0.0
    S04_F001_120m            200.0     200.0     0.0
    S05_F003_cancel          200.0     200.0     0.0
    S06_A002_unavailable       0.0       0.0     0.0
    S07_C001_unavailable     100.0     100.0     0.0
    S08_F001_30m_A002          0.0       0.0     0.0
    S09_A002_C001              0.0       0.0     0.0
    rows 27 unique scenarios 9 strategies ['buffered', 'flexible', 'normal']
             scenario_id strategy solver_status  initial_operating_cost  recovered_operating_cost  recovery_penalties  cancelled_flights  operated_delayed_flights  aircraft_reassignment_count  crew_reassignment_count  unique_changed_flight_count
                S01_none   normal       Optimal                  6660.0                    6660.0                 0.0                  0                         0                            0                        0                            0
            S02_F001_30m   normal       Optimal                  6660.0                    6760.0               750.0                  0                         1                            3                        0                            3
            S03_F001_60m   normal       Optimal                  6660.0                    5600.0            100500.0                  1                         1                            2                        0                            2
           S04_F001_120m   normal       Optimal                  6660.0                    5600.0            100500.0                  1                         1                            2                        0                            2
         S05_F003_cancel   normal       Optimal                  6660.0                    5500.0            200100.0                  1                         0                            0                        1                            1
    S06_A002_unavailable   normal       Optimal                  6660.0                    4740.0            200500.0                  2                         0                            2                        0                            2
    S07_C001_unavailable   normal       Optimal                  6660.0                    6660.0                 0.0                  0                         0                            0                        0                            0
       S08_F001_30m_A002   normal       Optimal                  6660.0                    4740.0            200500.0                  2                         0                            2                        0                            2
           S09_A002_C001   normal       Optimal                  6660.0                    4740.0            200500.0                  2                         0                            2                        0                            2
                S01_none buffered       Optimal                  6760.0                    6760.0                 0.0                  0                         0                            0                        0                            0
            S02_F001_30m buffered       Optimal                  6760.0                    6760.0                 0.0                  0                         1                            0                        0                            0
            S03_F001_60m buffered       Optimal                  6760.0                    5800.0            100450.0                  1                         1                            1                        2                            3
           S04_F001_120m buffered       Optimal                  6760.0                    5800.0            100450.0                  1                         1                            1                        2                            3
         S05_F003_cancel buffered       Optimal                  6760.0                    5700.0            200250.0                  1                         0                            1                        0                            1
    S06_A002_unavailable buffered       Optimal                  6760.0                    4740.0            200450.0                  2                         0                            1                        2                            3
    S07_C001_unavailable buffered       Optimal                  6760.0                    6760.0                 0.0                  0                         0                            0                        0                            0
       S08_F001_30m_A002 buffered       Optimal                  6760.0                    4740.0            200450.0                  2                         0                            1                        2                            3
           S09_A002_C001 buffered       Optimal                  6760.0                    4740.0            200450.0                  2                         0                            1                        2                            3
                S01_none flexible       Optimal                  6760.0                    6760.0                 0.0                  0                         0                            0                        0                            0
            S02_F001_30m flexible       Optimal                  6760.0                    6760.0                 0.0                  0                         1                            0                        0                            0
            S03_F001_60m flexible       Optimal                  6760.0                    5800.0            100350.0                  1                         1                            1                        1                            1
           S04_F001_120m flexible       Optimal                  6760.0                    5800.0            100350.0                  1                         1                            1                        1                            1
         S05_F003_cancel flexible       Optimal                  6760.0                    5700.0            200250.0                  1                         0                            1                        0                            1
    S06_A002_unavailable flexible       Optimal                  6760.0                    4740.0            200350.0                  2                         0                            1                        1                            1
    S07_C001_unavailable flexible       Optimal                  6760.0                    6760.0               100.0                  0                         0                            0                        1                            1
       S08_F001_30m_A002 flexible       Optimal                  6760.0                    4740.0            200350.0                  2                         0                            1                        1                            1
           S09_A002_C001 flexible       Optimal                  6760.0                    4740.0            200350.0                  2                         0                            1                        1                            1
    all statuses: {'Optimal': 27}
    all exact 3x9: True
    ✓ • 6.15s

## Activity

    $ sed -n '85,180p' experiments/run_experiments.py && sed -n '20,100p' experiments/analyze_results.py
                       "aircraft_reassignment_penalty": None, "crew_reassignment_penalty": None,
                       "strategy_optimization_score": None, "cancelled_flights": None,
                       "operated_delayed_flights": None, "total_delay_minutes": None,
                       "aircraft_reassignment_count": None, "crew_reassignment_count": None,
                       "unique_changed_flight_count": None, "initial_connection_slack": None,
                       "recovered_connection_slack": None, "initial_error": initial.get("solver_message", ""),
                       "recovery_error": ""}
                if initial.get("status") != "Optimal":
                    row["solver_status"] = "NotRunInitialInfeasible"
                    rows.append(row)
                    continue
                disrupted = _apply_delays(flights, scenario["delays"])
                assignment = dict(zip(initial["schedule"].flight_id, initial["schedule"].assigned_aircraft))
                crew_assignment = {r.flight_id: [x for x in str(r.assigned_crew).split(";") if x]
                                   for r in initial["schedule"].itertuples()}
                try:
                    recovered = solve_schedule(disrupted, aircraft, crew,
                        turnaround_minutes=RECOVERY_PARAMETERS["turnaround_minutes"],
                        crew_rest_minutes=RECOVERY_PARAMETERS["crew_rest_minutes"],
                        unavailable_aircraft=scenario["aircraft"], unavailable_crew=scenario["crew"],
                        cancelled_flights=scenario["cancel"], original_assignment=assignment,
                        original_crew_assignment=crew_assignment, allow_cancellation=True,
                        strategy="normal", cancellation_penalty=RECOVERY_PARAMETERS["cancellation_penalty"])
                except Exception as exc:
                    recovered = {"status": "Error", "solver_message": str(exc), "schedule": pd.DataFrame(), "components": {}}
                row["solver_status"] = recovered.get("status", "Unknown")
                row["solver_runtime_seconds"] = recovered.get("solver_runtime_seconds")
                row["recovery_error"] = recovered.get("solver_message", "")
                if recovered.get("status") == "Optimal":
                    metrics = compare_schedules(initial["schedule"], recovered["schedule"], initial, recovered,
                        externally_imposed_delays=scenario["delays"], expected_flight_ids=flights.flight_id,
                        turnaround_minutes=RECOVERY_PARAMETERS["turnaround_minutes"])
                    row.update({"initial_operating_cost": metrics["initial_operating_cost"],
                        "recovered_operating_cost": metrics["recovery_operating_cost"],
                        "recovery_penalties": metrics["recovery_penalties"],
                        "cancellation_penalty": metrics["cancellation_penalty"],
                        "aircraft_reassignment_penalty": metrics["aircraft_reassignment_penalty"],
                        "crew_reassignment_penalty": metrics["crew_reassignment_penalty"],
                        "strategy_optimization_score": initial.get("strategy_score", 0),
                        "cancelled_flights": metrics["cancelled_flights"],
                        "operated_delayed_flights": metrics["operated_externally_delayed_flights"],
                        "total_delay_minutes": metrics["externally_imposed_delay_minutes"],
                        "aircraft_reassignment_count": metrics["aircraft_changed_flights"],
                        "crew_reassignment_count": metrics["crew_changed_flights"],
                        "unique_changed_flight_count": metrics["unique_changed_flights"],
                        "initial_connection_slack": connection_metrics(initial["schedule"], 45)["average_connection_slack_minutes"],
                        "recovered_connection_slack": connection_metrics(recovered["schedule"], 45)["average_connection_slack_minutes"]})
                rows.append(row)
        result = pd.DataFrame(rows)
        path = Path(output_path) if output_path else ROOT / "experiments/results/experiment_results.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        result.to_csv(path, index=False)
        return result, path
    
    
    if __name__ == "__main__":
        frame, path = run_experiments()
        print(f"Saved {len(frame)} rows to {path}")
        print(frame.groupby(["strategy", "solver_status"], dropna=False).size().to_string())
            recovered_operating_cost=("recovered_operating_cost", "mean"),
            recovery_penalties=("recovery_penalties", "mean"),
            cancelled_flights=("cancelled_flights", "mean"),
            operated_delayed_flights=("operated_delayed_flights", "mean"),
            aircraft_reassignment_count=("aircraft_reassignment_count", "mean"),
            crew_reassignment_count=("crew_reassignment_count", "mean"),
            unique_changed_flight_count=("unique_changed_flight_count", "mean"),
            initial_connection_slack=("initial_connection_slack", "mean"),
            recovered_connection_slack=("recovered_connection_slack", "mean"))
        summaries.to_csv(output / "strategy_comparison.csv", index=False)
        # Per-scenario results and differences remain visible; no average is used
        # to imply that a strategy wins in every case.
        pivot = successful.pivot(index="scenario_id", columns="strategy", values="recovered_operating_cost")
        differences = pivot.copy()
        for strategy in pivot.columns:
            differences[strategy] = pivot[strategy] - pivot.min(axis=1)
        differences.to_csv(output / "scenario_cost_differences.csv")
        successful.to_csv(output / "successful_scenario_metrics.csv", index=False)
        data[data.solver_status != "Optimal"].to_csv(output / "failed_solves.csv", index=False)
        charts = [
            ("initial_vs_recovered_cost.html", ["initial_operating_cost", "recovered_operating_cost"], "Operating costs by scenario"),
            ("cancellations.html", ["cancelled_flights"], "Cancelled flights"),
            ("assignment_changes.html", ["aircraft_reassignment_count", "crew_reassignment_count", "unique_changed_flight_count"], "Assignment changes"),
            ("delay_comparison.html", ["operated_delayed_flights", "total_delay_minutes"], "External delay exposure"),
        ]
        long = successful.melt(id_vars=["scenario_id", "strategy"], var_name="metric", value_name="value")
        for filename, metrics, title in charts:
            frame = long[long.metric.isin(metrics)]
            fig = px.bar(frame, x="scenario_id", y="value", color="strategy", barmode="group", facet_col="metric", title=title)
            fig.write_html(output / filename, include_plotlyjs="cdn")
        print(f"Analyzed {len(data)} rows ({len(successful)} optimal, {len(data)-len(successful)} failed or not run).")
        print(summaries.to_string(index=False))
        print(f"Analysis files: {output}")
        print("Scenario cost differences (each strategy minus that scenario's lowest recovered operating cost):")
        print(differences.to_string())
        return summaries, differences
    
    
    if __name__ == "__main__":
        analyze(sys.argv[1] if len(sys.argv) > 1 else None)
    ✓ • 0ms

## Activity

    $ sed -n '72,96p' experiments/run_experiments.py && sed -n '1,30p' experiments/analyze_results.py
                                         **{k: v for k, v in INITIAL_PARAMETERS.items() if k != "crew_rest_minutes"})
            except Exception as exc:
                initial = {"status": "Error", "solver_message": str(exc), "schedule": pd.DataFrame(), "components": {}}
            for scenario in SCENARIOS:
                row = {"scenario_id": scenario["scenario_id"], "strategy": strategy,
                       "scenario_parameters": json.dumps(scenario, sort_keys=True),
                       "initial_parameters": json.dumps({**INITIAL_PARAMETERS, "strategy": strategy}, sort_keys=True),
                       "recovery_parameters": json.dumps(RECOVERY_PARAMETERS, sort_keys=True),
                       "dependency_versions": json.dumps(_versions(), sort_keys=True),
                       "initial_solver_status": initial.get("status", "Unknown"),
                       "solver_status": "NotRunInitialInfeasible", "solver_runtime_seconds": None,
                       "initial_operating_cost": None, "recovered_operating_cost": None,
                       "recovery_penalties": None, "cancellation_penalty": None,
                       "aircraft_reassignment_penalty": None, "crew_reassignment_penalty": None,
                       "strategy_optimization_score": None, "cancelled_flights": None,
                       "operated_delayed_flights": None, "total_delay_minutes": None,
                       "aircraft_reassignment_count": None, "crew_reassignment_count": None,
                       "unique_changed_flight_count": None, "initial_connection_slack": None,
                       "recovered_connection_slack": None, "initial_error": initial.get("solver_message", ""),
                       "recovery_error": ""}
                if initial.get("status") != "Optimal":
                    row["solver_status"] = "NotRunInitialInfeasible"
                    rows.append(row)
                    continue
                disrupted = _apply_delays(flights, scenario["delays"])
    """Summarize experiment CSVs and generate shareable comparison charts."""
    from pathlib import Path
    import sys
    
    import pandas as pd
    import plotly.express as px
    
    ROOT = Path(__file__).resolve().parents[1]
    
    
    def analyze(path=None):
        source = Path(path) if path else ROOT / "experiments/results/experiment_results.csv"
        data = pd.read_csv(source)
        output = source.parent / "analysis"
        output.mkdir(parents=True, exist_ok=True)
        successful = data[data.solver_status == "Optimal"].copy()
        summaries = successful.groupby("strategy", as_index=False).agg(
            scenario_count=("scenario_id", "count"),
            initial_operating_cost=("initial_operating_cost", "mean"),
            recovered_operating_cost=("recovered_operating_cost", "mean"),
            recovery_penalties=("recovery_penalties", "mean"),
            cancelled_flights=("cancelled_flights", "mean"),
            operated_delayed_flights=("operated_delayed_flights", "mean"),
            aircraft_reassignment_count=("aircraft_reassignment_count", "mean"),
            crew_reassignment_count=("crew_reassignment_count", "mean"),
            unique_changed_flight_count=("unique_changed_flight_count", "mean"),
            initial_connection_slack=("initial_connection_slack", "mean"),
            recovered_connection_slack=("recovered_connection_slack", "mean"))
        summaries.to_csv(output / "strategy_comparison.csv", index=False)
        # Per-scenario results and differences remain visible; no average is used
    ✓ • 0ms

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /workspaces/ScheduleRescue/experiments/run_experiments.py
    @@ -86,3 +86,8 @@
                        "strategy_optimization_score": None, "cancelled_flights": None,
    -                   "operated_delayed_flights": None, "total_delay_minutes": None,
    +                   "operated_delayed_flights": None, "cancelled_externally_delayed_flights": None,
    +                   "externally_imposed_delay_flights": len(scenario["delays"]),
    +                   "externally_imposed_delay_minutes": sum(scenario["delays"].values()),
    +                   "recovery_added_delay_minutes": 0,
    +                   "total_delay_minutes": sum(scenario["delays"].values()),
    +                   "total_modeled_recovery_cost": None,
                        "aircraft_reassignment_count": None, "crew_reassignment_count": None,
    @@ -119,2 +124,3 @@
                         "recovery_penalties": metrics["recovery_penalties"],
    +                    "total_modeled_recovery_cost": metrics["total_modeled_recovery_cost"],
                         "cancellation_penalty": metrics["cancellation_penalty"],
    @@ -125,3 +131,3 @@
                         "operated_delayed_flights": metrics["operated_externally_delayed_flights"],
    -                    "total_delay_minutes": metrics["externally_imposed_delay_minutes"],
    +                    "cancelled_externally_delayed_flights": metrics["cancelled_externally_delayed_flights"],
                         "aircraft_reassignment_count": metrics["aircraft_changed_flights"],

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /workspaces/ScheduleRescue/experiments/analyze_results.py
    @@ -21,2 +21,3 @@
             recovery_penalties=("recovery_penalties", "mean"),
    +        total_modeled_recovery_cost=("total_modeled_recovery_cost", "mean"),
             cancelled_flights=("cancelled_flights", "mean"),
    @@ -31,6 +32,8 @@
         # to imply that a strategy wins in every case.
    -    pivot = successful.pivot(index="scenario_id", columns="strategy", values="recovered_operating_cost")
    -    differences = pivot.copy()
    -    for strategy in pivot.columns:
    -        differences[strategy] = pivot[strategy] - pivot.min(axis=1)
    +    operating = successful.pivot(index="scenario_id", columns="strategy", values="recovered_operating_cost")
    +    total = successful.pivot(index="scenario_id", columns="strategy", values="total_modeled_recovery_cost")
    +    differences = pd.DataFrame(index=operating.index)
    +    for strategy in operating.columns:
    +        differences[f"{strategy}_operating_cost_delta"] = operating[strategy] - operating.min(axis=1)
    +        differences[f"{strategy}_total_recovery_cost_delta"] = total[strategy] - total.min(axis=1)
         differences.to_csv(output / "scenario_cost_differences.csv")
    @@ -52,3 +55,3 @@
         print(f"Analysis files: {output}")
    -    print("Scenario cost differences (each strategy minus that scenario's lowest recovered operating cost):")
    +    print("Per-scenario cost differences versus the lowest strategy cost in that scenario (operating and total modeled recovery cost separately):")
         print(differences.to_string())

## Activity

    $ python -c 'import pulp; s=pulp.PULP_CBC_CMD(); print(s.path); print(s.available())'
    /usr/local/python/3.14.2/lib/python3.14/site-packages/pulp/solverdir/cbc/linux/64/cbc
    /usr/local/python/3.14.2/lib/python3.14/site-packages/pulp/solverdir/cbc/linux/64/cbc
    ✓ • 28ms

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /workspaces/ScheduleRescue/experiments/run_experiments.py
    @@ -5,2 +5,3 @@
     import platform
    +import subprocess
     import sys
    @@ -42,5 +43,11 @@
     def _versions():
    +    cbc = pulp.PULP_CBC_CMD().available()
    +    try:
    +        cbc_version = subprocess.run([cbc, "-version"], capture_output=True, text=True,
    +                                      timeout=3, check=False).stdout.strip().splitlines()[:2]
    +    except (OSError, subprocess.TimeoutExpired):
    +        cbc_version = ["unavailable"]
         return {"python": platform.python_version(), "pandas": pd.__version__,
                 "pulp": pulp.__version__, "available_solvers": pulp.listSolvers(onlyAvailable=True),
    -            "platform": platform.platform()}
    +            "cbc_version": cbc_version, "platform": platform.platform()}
     
    @@ -81,2 +88,3 @@
                        "initial_solver_status": initial.get("status", "Unknown"),
    +                   "initial_solver_runtime_seconds": initial.get("solver_runtime_seconds"),
                        "solver_status": "NotRunInitialInfeasible", "solver_runtime_seconds": None,

## Activity

    $ python -m unittest discover -s tests -v && python experiments/run_experiments.py && python experiments/analyze_results.py
    test_cancellation_is_not_reported_as_operated (test_schedule_rescue.ScheduleModelTests.test_cancellation_is_not_reported_as_operated) ... ok
    test_comparison_metrics_round_trip_to_csv (test_schedule_rescue.ScheduleModelTests.test_comparison_metrics_round_trip_to_csv) ... ok
    test_connection_gap_and_slack_are_distinct (test_schedule_rescue.ScheduleModelTests.test_connection_gap_and_slack_are_distinct) ... ok
    test_cost_identity_unique_changes_and_uncovered_flights (test_schedule_rescue.ScheduleModelTests.test_cost_identity_unique_changes_and_uncovered_flights) ... ok
    test_crew_can_continue_after_traveling_to_a_new_airport (test_schedule_rescue.ScheduleModelTests.test_crew_can_continue_after_traveling_to_a_new_airport) ... ok
    test_crew_qualification_mismatch_is_rejected (test_schedule_rescue.ScheduleModelTests.test_crew_qualification_mismatch_is_rejected) ... ok
    test_crew_unavailability_and_duty (test_schedule_rescue.ScheduleModelTests.test_crew_unavailability_and_duty) ... ok
    test_duplicate_ids_and_negative_aircraft_cost_are_rejected (test_schedule_rescue.ScheduleModelTests.test_duplicate_ids_and_negative_aircraft_cost_are_rejected) ... ok
    test_experiment_runner_uses_all_strategies_for_same_scenarios (test_schedule_rescue.ScheduleModelTests.test_experiment_runner_uses_all_strategies_for_same_scenarios) ... ok
    test_external_delay_categories_and_cancelled_delay (test_schedule_rescue.ScheduleModelTests.test_external_delay_categories_and_cancelled_delay) ... ok
    test_external_delay_is_applied_once_and_recovers (test_schedule_rescue.ScheduleModelTests.test_external_delay_is_applied_once_and_recovers) ... ok
    test_identical_disruption_is_used_for_all_strategy_recoveries (test_schedule_rescue.ScheduleModelTests.test_identical_disruption_is_used_for_all_strategy_recoveries) ... ok
    test_insufficient_aircraft_is_infeasible (test_schedule_rescue.ScheduleModelTests.test_insufficient_aircraft_is_infeasible) ... ok
    test_insufficient_turnaround_prevents_same_aircraft_connection (test_schedule_rescue.ScheduleModelTests.test_insufficient_turnaround_prevents_same_aircraft_connection) ... ok
    test_normal_schedule_and_route_continuity (test_schedule_rescue.ScheduleModelTests.test_normal_schedule_and_route_continuity) ... ok
    test_stale_result_settings_are_rejected (test_schedule_rescue.ScheduleModelTests.test_stale_result_settings_are_rejected) ... ok
    test_three_strategies_are_distinct_and_feasible (test_schedule_rescue.ScheduleModelTests.test_three_strategies_are_distinct_and_feasible) ... ok
    test_type_and_location_constraints (test_schedule_rescue.ScheduleModelTests.test_type_and_location_constraints) ... ok
    test_unavailability_reassigns_when_possible (test_schedule_rescue.ScheduleModelTests.test_unavailability_reassigns_when_possible) ... ok
    
    ----------------------------------------------------------------------
    Ran 19 tests in 2.937s
    
    OK
    Saved 27 rows to /workspaces/ScheduleRescue/experiments/results/experiment_results.csv
    strategy  solver_status
    buffered  Optimal          9
    flexible  Optimal          9
    normal    Optimal          9
    Analyzed 27 rows (27 optimal, 0 failed or not run).
    strategy  scenario_count  initial_operating_cost  recovered_operating_cost  recovery_penalties  total_modeled_recovery_cost  cancelled_flights  operated_delayed_flights  aircraft_reassignment_count  crew_reassignment_count  unique_changed_flight_count  initial_connection_slack  recovered_connection_slack
    buffered               9                  6760.0               5755.555556       111388.888889                117144.444444                1.0                  0.333333                     0.666667                 1.111111                     1.777778                     115.0                   87.222222
    flexible               9                  6760.0               5755.555556       111344.444444                117100.000000                1.0                  0.333333                     0.666667                 0.666667                     0.777778                     115.0                   87.222222
      normal               9                  6660.0               5666.666667       111483.333333                117150.000000                1.0                  0.333333                     1.444444                 0.111111                     1.555556                      15.0                   58.333333
    Analysis files: /workspaces/ScheduleRescue/experiments/results/analysis
    Per-scenario cost differences versus the lowest strategy cost in that scenario (operating and total modeled recovery cost separately):
                          buffered_operating_cost_delta  buffered_total_recovery_cost_delta  flexible_operating_cost_delta  flexible_total_recovery_cost_delta  normal_operating_cost_delta  normal_total_recovery_cost_delta
    scenario_id
    S01_none                                      100.0                               100.0                          100.0                               100.0                          0.0                               0.0
    S02_F001_30m                                    0.0                                 0.0                            0.0                                 0.0                          0.0                             750.0
    S03_F001_60m                                  200.0                               150.0                          200.0                                50.0                          0.0                               0.0
    S04_F001_120m                                 200.0                               150.0                          200.0                                50.0                          0.0                               0.0
    S05_F003_cancel                               200.0                               350.0                          200.0                               350.0                          0.0                               0.0
    S06_A002_unavailable                            0.0                               100.0                            0.0                                 0.0                          0.0                             150.0
    S07_C001_unavailable                          100.0                               100.0                          100.0                               200.0                          0.0                               0.0
    S08_F001_30m_A002                               0.0                               100.0                            0.0                                 0.0                          0.0                             150.0
    S09_A002_C001                                   0.0                               100.0                            0.0                                 0.0                          0.0                             150.0
    ✓ • 7.27s

## Activity

    $ python -c 'import pandas as pd; d=pd.read_csv("experiments/results/experiment_results.csv"); assert len(d)==27; assert d.groupby("scenario_id").strategy.nunique().eq(3).all(); assert (d.solver_status=="Optimal").all(); assert (d.total_modeled_recovery_cost-d.recovered_operating_cost-d.recovery_penalties).abs().max()<1e-6; print("CSV checks: 27 rows; 9 scenarios × 3 strategies; all Optimal; cost identity max error", (d.total_modeled_recovery_cost-d.recovered_operating_cost-d.recovery_penalties).abs().max()); print("Recorded versions:", d.dependency_versions.iloc[0]); print("CSV columns:", ", ".join(d.columns)); print("Analysis files:"); import pathlib; print("\n".join(str(p) for p in sorted(pathlib.Path("experiments/results/analysis").iterdir())))' && python -c 'from streamlit.testing.v1 import AppTest; app=AppTest.from_file("app.py").run(timeout=30); print("AppTest exceptions:", len(app.exception)); [print(e.message) for e in app.exception]; assert len(app.exception)==0'
    CSV checks: 27 rows; 9 scenarios × 3 strategies; all Optimal; cost identity max error 0.0
    Recorded versions: {"available_solvers": ["PULP_CBC_CMD"], "cbc_version": ["Welcome to the CBC MILP Solver ", "Version: 2.10.3 "], "pandas": "3.1.0", "platform": "Linux-6.8.0-1070-azure-x86_64-with-glibc2.39", "pulp": "2.9.0", "python": "3.14.2"}
    CSV columns: scenario_id, strategy, scenario_parameters, initial_parameters, recovery_parameters, dependency_versions, initial_solver_status, initial_solver_runtime_seconds, solver_status, solver_runtime_seconds, initial_operating_cost, recovered_operating_cost, recovery_penalties, cancellation_penalty, aircraft_reassignment_penalty, crew_reassignment_penalty, strategy_optimization_score, cancelled_flights, operated_delayed_flights, cancelled_externally_delayed_flights, externally_imposed_delay_flights, externally_imposed_delay_minutes, recovery_added_delay_minutes, total_delay_minutes, total_modeled_recovery_cost, aircraft_reassignment_count, crew_reassignment_count, unique_changed_flight_count, initial_connection_slack, recovered_connection_slack, initial_error, recovery_error
    Analysis files:
    experiments/results/analysis/assignment_changes.html
    experiments/results/analysis/cancellations.html
    experiments/results/analysis/delay_comparison.html
    experiments/results/analysis/failed_solves.csv
    experiments/results/analysis/initial_vs_recovered_cost.html
    experiments/results/analysis/scenario_cost_differences.csv
    experiments/results/analysis/strategy_comparison.csv
    experiments/results/analysis/successful_scenario_metrics.csv
    2026-11-11 15:54:10.440 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
    AppTest exceptions: 0
    ✓ • 3.88s

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /workspaces/ScheduleRescue/src/scheduler.py
    @@ -185,3 +185,7 @@
         covered = set(schedule.flight_id)
    -    if len(schedule) != len(F) or covered != set(F):
    +    invalid_rows = schedule[(schedule.status != "Cancelled") & schedule.assigned_aircraft.isna()]
    +    invalid_crew = schedule.apply(lambda row: row.status != "Cancelled" and
    +        len([item for item in str(row.assigned_crew).split(";") if item]) !=
    +        int(fd[row.flight_id]["required_crew_count"]), axis=1)
    +    if len(schedule) != len(F) or covered != set(F) or not invalid_rows.empty or invalid_crew.any():
             return {"status":"InvalidSolution", "schedule":pd.DataFrame(), "objective":None,

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /workspaces/ScheduleRescue/tests/test_schedule_rescue.py
    @@ -169,2 +169,6 @@
     
    +    def test_failed_solve_cannot_produce_schedule_metrics(self):
    +        with self.assertRaisesRegex(ValueError,"failed solve"):
    +            compare_schedules(pd.DataFrame(),pd.DataFrame(),{}, {"status":"Infeasible"})
    +
         def test_comparison_metrics_round_trip_to_csv(self):

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /workspaces/ScheduleRescue/docs/methodology.md
    @@ -15 +15,23 @@
     PuLP and CBC can return different assignments when multiple solutions have equal objective value. Dependency and platform versions are recorded; exact tie-breaking and timing may vary. Runtime is measured around the solver call. Strategy optimization scores are not included in operating costs or recovery penalty totals.
    +
    +## Metric definitions
    +
    +| Metric | Definition |
    +|---|---|
    +| Initial operating cost | Aircraft plus crew block-hour cost in the initial schedule. |
    +| Recovered operating cost | Aircraft plus crew block-hour cost in the recovered schedule, using the externally shifted fixed times. |
    +| Operating cost change | Recovered operating cost minus initial operating cost; it can be negative. |
    +| Cancellation penalty | Priority-weighted configured penalty for cancelled flights. |
    +| Aircraft / crew reassignment penalty | Configured objective weight charged for assignment changes from the initial schedule. |
    +| Other recovery penalties | Any separately modeled recovery penalty not in the preceding categories; zero in the current model. |
    +| Total modeled recovery cost | Recovered operating cost plus all recovery penalties. It excludes initial operating cost and strategy preference scores. |
    +| Operated / cancelled flights | Counts by final recovery status. An explicit cancellation is in the cancelled count. |
    +| Unexpectedly uncovered flights | Flight IDs expected in the input but absent from the recovered schedule, or unexpected IDs present. An accepted solver output is checked for complete coverage; failed solves have no valid schedule metrics. |
    +| Externally imposed delay | Count of selected flights and sum of selected delay minutes. |
    +| Operated externally delayed / cancelled externally delayed | Counts of externally delayed flight IDs partitioned by whether they operated or were cancelled. |
    +| Recovery-added delay | Zero minutes because flight retiming is not modeled. |
    +| Aircraft changes / crew changes | Operated flights whose respective assignment differs from the initial assignment. |
    +| Unique changed flights | Size of the union of aircraft-changed and crew-changed flight IDs, so a flight changed in both categories is counted once. |
    +| Connection gap / slack | Next departure minus prior arrival; slack equals gap minus actual turnaround. Connection averages are over compatible consecutive flights assigned to the same aircraft. |
    +| Solver runtime | Wall-clock seconds around the solver invocation; it excludes preparation and report generation. |
    +| Strategy optimization score | Flexible's initial-schedule slack-shortfall score. It is a preference term, not an operating or recovery cost. |

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /workspaces/ScheduleRescue/src/scheduler.py
    @@ -180,3 +180,4 @@
         values["scheduled_operating_cost"] = values["aircraft_operating_cost"]+values["crew_operating_cost"]
    -    values["recovery_penalties"] = sum(values[k] for k in ("cancellation_penalty","aircraft_reassignment_penalty","crew_reassignment_penalty"))
    +    values["other_recovery_penalties"] = 0.0
    +    values["recovery_penalties"] = sum(values[k] for k in ("cancellation_penalty","aircraft_reassignment_penalty","crew_reassignment_penalty","other_recovery_penalties"))
         schedule = pd.DataFrame(rows)
    @@ -201,2 +202,4 @@
                     "unavailable_aircraft":sorted(unavailable_aircraft),"unavailable_crew":sorted(unavailable_crew),
    -                "cancelled_flights":sorted(cancelled_flights),"allow_cancellation":allow_cancellation}}
    +                "unavailable_periods":periods,"cancelled_flights":sorted(cancelled_flights),
    +                "original_assignment":original_assignment,"original_crew_assignment":original_crew_assignment,
    +                "allow_cancellation":allow_cancellation}}

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /workspaces/ScheduleRescue/app.py
    @@ -100,2 +100,4 @@
                         results[strategy]=solve_schedule(f,a,c,turnaround_minutes=turnaround,strategy=strategy,buffer_minutes=buffer,flexibility_target_minutes=target)
    +                results[strategy]["solve_context"]={"flights":f.copy(),"aircraft":a.copy(),"crew":c.copy(),
    +                    "strategy_settings":dict(active_settings),"strategy":strategy}
                 st.session_state["initial_results"]=results
    @@ -149,2 +151,5 @@
                         recovery[strategy]=solve_schedule(modified,a,c,turnaround_minutes=settings["turnaround"],unavailable_aircraft=unavailable_a,unavailable_crew=unavailable_c,cancelled_flights=cancel_ids,original_assignment=oa,original_crew_assignment=oc,allow_cancellation=True,strategy="normal")
    +                recovery[strategy]["solve_context"]={"flights":modified.copy(),"aircraft":a.copy(),"crew":c.copy(),
    +                    "initial_strategy":strategy,"initial_settings":dict(settings),"disruptions":dict(current_scenario),
    +                    "recovery_parameters":dict(recovery[strategy].get("solve_parameters",{}))}
                     if recovery[strategy]["status"] == "Optimal":

## Assistant

All 27 saved experiment rows are Optimal, with exactly three strategies per scenario. I also checked the CSV’s cost identity row by row: total modeled recovery cost equals recovered operating cost plus recovery penalties with zero numerical discrepancy. Analysis now compares both operating cost and total modeled recovery cost per scenario, since those can favor different strategies. I’m doing one final regression and UI smoke check after the last metadata and coverage edits.

## Activity

    $ python -m unittest discover -s tests -v && python experiments/run_experiments.py && python experiments/analyze_results.py && python -c 'from streamlit.testing.v1 import AppTest; app=AppTest.from_file("app.py").run(timeout=30); print("AppTest exceptions:",len(app.exception)); [print(e.message) for e in app.exception]; assert not app.exception' && git status --short && git diff --stat
    test_cancellation_is_not_reported_as_operated (test_schedule_rescue.ScheduleModelTests.test_cancellation_is_not_reported_as_operated) ... ok
    test_comparison_metrics_round_trip_to_csv (test_schedule_rescue.ScheduleModelTests.test_comparison_metrics_round_trip_to_csv) ... ok
    test_connection_gap_and_slack_are_distinct (test_schedule_rescue.ScheduleModelTests.test_connection_gap_and_slack_are_distinct) ... ok
    test_cost_identity_unique_changes_and_uncovered_flights (test_schedule_rescue.ScheduleModelTests.test_cost_identity_unique_changes_and_uncovered_flights) ... ok
    test_crew_can_continue_after_traveling_to_a_new_airport (test_schedule_rescue.ScheduleModelTests.test_crew_can_continue_after_traveling_to_a_new_airport) ... ok
    test_crew_qualification_mismatch_is_rejected (test_schedule_rescue.ScheduleModelTests.test_crew_qualification_mismatch_is_rejected) ... ok
    test_crew_unavailability_and_duty (test_schedule_rescue.ScheduleModelTests.test_crew_unavailability_and_duty) ... ok
    test_duplicate_ids_and_negative_aircraft_cost_are_rejected (test_schedule_rescue.ScheduleModelTests.test_duplicate_ids_and_negative_aircraft_cost_are_rejected) ... ok
    test_experiment_runner_uses_all_strategies_for_same_scenarios (test_schedule_rescue.ScheduleModelTests.test_experiment_runner_uses_all_strategies_for_same_scenarios) ... ok
    test_external_delay_categories_and_cancelled_delay (test_schedule_rescue.ScheduleModelTests.test_external_delay_categories_and_cancelled_delay) ... ok
    test_external_delay_is_applied_once_and_recovers (test_schedule_rescue.ScheduleModelTests.test_external_delay_is_applied_once_and_recovers) ... ok
    test_failed_solve_cannot_produce_schedule_metrics (test_schedule_rescue.ScheduleModelTests.test_failed_solve_cannot_produce_schedule_metrics) ... ok
    test_identical_disruption_is_used_for_all_strategy_recoveries (test_schedule_rescue.ScheduleModelTests.test_identical_disruption_is_used_for_all_strategy_recoveries) ... ok
    test_insufficient_aircraft_is_infeasible (test_schedule_rescue.ScheduleModelTests.test_insufficient_aircraft_is_infeasible) ... ok
    test_insufficient_turnaround_prevents_same_aircraft_connection (test_schedule_rescue.ScheduleModelTests.test_insufficient_turnaround_prevents_same_aircraft_connection) ... ok
    test_normal_schedule_and_route_continuity (test_schedule_rescue.ScheduleModelTests.test_normal_schedule_and_route_continuity) ... ok
    test_stale_result_settings_are_rejected (test_schedule_rescue.ScheduleModelTests.test_stale_result_settings_are_rejected) ... ok
    test_three_strategies_are_distinct_and_feasible (test_schedule_rescue.ScheduleModelTests.test_three_strategies_are_distinct_and_feasible) ... ok
    test_type_and_location_constraints (test_schedule_rescue.ScheduleModelTests.test_type_and_location_constraints) ... ok
    test_unavailability_reassigns_when_possible (test_schedule_rescue.ScheduleModelTests.test_unavailability_reassigns_when_possible) ... ok
    
    ----------------------------------------------------------------------
    Ran 20 tests in 3.124s
    
    OK
    Saved 27 rows to /workspaces/ScheduleRescue/experiments/results/experiment_results.csv
    strategy  solver_status
    buffered  Optimal          9
    flexible  Optimal          9
    normal    Optimal          9
    Analyzed 27 rows (27 optimal, 0 failed or not run).
    strategy  scenario_count  initial_operating_cost  recovered_operating_cost  recovery_penalties  total_modeled_recovery_cost  cancelled_flights  operated_delayed_flights  aircraft_reassignment_count  crew_reassignment_count  unique_changed_flight_count  initial_connection_slack  recovered_connection_slack
    buffered               9                  6760.0               5755.555556       111388.888889                117144.444444                1.0                  0.333333                     0.666667                 1.111111                     1.777778                     115.0                   87.222222
    flexible               9                  6760.0               5755.555556       111344.444444                117100.000000                1.0                  0.333333                     0.666667                 0.666667                     0.777778                     115.0                   87.222222
      normal               9                  6660.0               5666.666667       111483.333333                117150.000000                1.0                  0.333333                     1.444444                 0.111111                     1.555556                      15.0                   58.333333
    Analysis files: /workspaces/ScheduleRescue/experiments/results/analysis
    Per-scenario cost differences versus the lowest strategy cost in that scenario (operating and total modeled recovery cost separately):
                          buffered_operating_cost_delta  buffered_total_recovery_cost_delta  flexible_operating_cost_delta  flexible_total_recovery_cost_delta  normal_operating_cost_delta  normal_total_recovery_cost_delta
    scenario_id
    S01_none                                      100.0                               100.0                          100.0                               100.0                          0.0                               0.0
    S02_F001_30m                                    0.0                                 0.0                            0.0                                 0.0                          0.0                             750.0
    S03_F001_60m                                  200.0                               150.0                          200.0                                50.0                          0.0                               0.0
    S04_F001_120m                                 200.0                               150.0                          200.0                                50.0                          0.0                               0.0
    S05_F003_cancel                               200.0                               350.0                          200.0                               350.0                          0.0                               0.0
    S06_A002_unavailable                            0.0                               100.0                            0.0                                 0.0                          0.0                             150.0
    S07_C001_unavailable                          100.0                               100.0                          100.0                               200.0                          0.0                               0.0
    S08_F001_30m_A002                               0.0                               100.0                            0.0                                 0.0                          0.0                             150.0
    S09_A002_C001                                   0.0                               100.0                            0.0                                 0.0                          0.0                             150.0
    2026-11-11 15:55:30.830 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
    AppTest exceptions: 0
     M README.md
     M app.py
     M docs/assumptions.md
     M docs/methodology.md
     M docs/user_guide.md
     M src/metrics.py
     M src/scheduler.py
     M tests/test_schedule_rescue.py
    ?? experiments/
     README.md                     |  15 +++++
     app.py                        |  50 ++++++++++------
     docs/assumptions.md           |   4 ++
     docs/methodology.md           |  30 ++++++++++
     docs/user_guide.md            |   8 +++
     src/metrics.py                | 134 ++++++++++++++++++++++++++++++++----------
     src/scheduler.py              |  33 ++++++++++-
     tests/test_schedule_rescue.py |  71 ++++++++++++++++++++++
     8 files changed, 294 insertions(+), 51 deletions(-)
    ✓ • 9.05s

## Activity

    $ git diff --check && rg --files experiments && python -c 'import pandas as pd; d=pd.read_csv("experiments/results/experiment_results.csv"); print("unique statuses:",d.solver_status.value_counts().to_dict()); print("missing required experiment values among successful:",d[d.solver_status=="Optimal"][["initial_operating_cost","recovered_operating_cost","recovery_penalties","total_modeled_recovery_cost","cancelled_flights","operated_delayed_flights","aircraft_reassignment_count","crew_reassignment_count","unique_changed_flight_count","initial_connection_slack","recovered_connection_slack","solver_runtime_seconds"]].isna().sum().to_dict()); print("scenario count per strategy:",d.groupby("strategy").scenario_id.nunique().to_dict())'
    experiments/analyze_results.py
    experiments/results/analysis/strategy_comparison.csv
    experiments/results/analysis/assignment_changes.html
    experiments/results/analysis/successful_scenario_metrics.csv
    experiments/results/analysis/initial_vs_recovered_cost.html
    experiments/results/analysis/cancellations.html
    experiments/results/analysis/failed_solves.csv
    experiments/results/analysis/scenario_cost_differences.csv
    experiments/results/analysis/delay_comparison.html
    experiments/results/experiment_results.csv
    experiments/run_experiments.py
    unique statuses: {'Optimal': 27}
    missing required experiment values among successful: {'initial_operating_cost': 0, 'recovered_operating_cost': 0, 'recovery_penalties': 0, 'total_modeled_recovery_cost': 0, 'cancelled_flights': 0, 'operated_delayed_flights': 0, 'aircraft_reassignment_count': 0, 'crew_reassignment_count': 0, 'unique_changed_flight_count': 0, 'initial_connection_slack': 0, 'recovered_connection_slack': 0, 'solver_runtime_seconds': 0}
    scenario count per strategy: {'buffered': 9, 'flexible': 9, 'normal': 9}
    ✓ • 415ms

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /workspaces/ScheduleRescue/experiments/analyze_results.py
    @@ -52,2 +52,20 @@
             fig.write_html(output / filename, include_plotlyjs="cdn")
    +    winners = []
    +    for scenario_id, group in successful.groupby("scenario_id"):
    +        best = group.total_modeled_recovery_cost.min()
    +        names = ", ".join(group.loc[group.total_modeled_recovery_cost == best, "strategy"].tolist())
    +        winners.append(f"- **{scenario_id}:** {names} had the lowest total modeled recovery cost ({best:,.2f}).")
    +    explanation = [
    +        "# Experiment interpretation",
    +        "",
    +        "These results cover nine illustrative scenarios on one small demo dataset. They do not show that one strategy is always superior.",
    +        "The winner lines compare total modeled recovery cost (recovered operating cost plus recovery penalties). Operating costs and penalties remain separate in the CSV and strategy table; a lower operating cost can coincide with higher reassignment or cancellation penalties.",
    +        "",
    +        "## Lowest total modeled recovery cost by scenario",
    +        "",
    +        *winners,
    +        "",
    +        "Use `scenario_cost_differences.csv` to compare both operating-cost and total-recovery-cost differences within each scenario. Strategy-specific initial preference scores are not included in these monetary comparisons."
    +    ]
    +    (output / "interpretation.md").write_text("\n".join(explanation) + "\n", encoding="utf-8")
         print(f"Analyzed {len(data)} rows ({len(successful)} optimal, {len(data)-len(successful)} failed or not run).")
    @@ -55,2 +73,3 @@
         print(f"Analysis files: {output}")
    +    print("Interpretation written to:", output / "interpretation.md")
         print("Per-scenario cost differences versus the lowest strategy cost in that scenario (operating and total modeled recovery cost separately):")

## Activity

    $ python -m unittest discover -s tests -v && python experiments/analyze_results.py && git diff --check && sed -n '1,120p' experiments/results/analysis/interpretation.md
    test_cancellation_is_not_reported_as_operated (test_schedule_rescue.ScheduleModelTests.test_cancellation_is_not_reported_as_operated) ... ok
    test_comparison_metrics_round_trip_to_csv (test_schedule_rescue.ScheduleModelTests.test_comparison_metrics_round_trip_to_csv) ... ok
    test_connection_gap_and_slack_are_distinct (test_schedule_rescue.ScheduleModelTests.test_connection_gap_and_slack_are_distinct) ... ok
    test_cost_identity_unique_changes_and_uncovered_flights (test_schedule_rescue.ScheduleModelTests.test_cost_identity_unique_changes_and_uncovered_flights) ... ok
    test_crew_can_continue_after_traveling_to_a_new_airport (test_schedule_rescue.ScheduleModelTests.test_crew_can_continue_after_traveling_to_a_new_airport) ... ok
    test_crew_qualification_mismatch_is_rejected (test_schedule_rescue.ScheduleModelTests.test_crew_qualification_mismatch_is_rejected) ... ok
    test_crew_unavailability_and_duty (test_schedule_rescue.ScheduleModelTests.test_crew_unavailability_and_duty) ... ok
    test_duplicate_ids_and_negative_aircraft_cost_are_rejected (test_schedule_rescue.ScheduleModelTests.test_duplicate_ids_and_negative_aircraft_cost_are_rejected) ... ok
    test_experiment_runner_uses_all_strategies_for_same_scenarios (test_schedule_rescue.ScheduleModelTests.test_experiment_runner_uses_all_strategies_for_same_scenarios) ... ok
    test_external_delay_categories_and_cancelled_delay (test_schedule_rescue.ScheduleModelTests.test_external_delay_categories_and_cancelled_delay) ... ok
    test_external_delay_is_applied_once_and_recovers (test_schedule_rescue.ScheduleModelTests.test_external_delay_is_applied_once_and_recovers) ... ok
    test_failed_solve_cannot_produce_schedule_metrics (test_schedule_rescue.ScheduleModelTests.test_failed_solve_cannot_produce_schedule_metrics) ... ok
    test_identical_disruption_is_used_for_all_strategy_recoveries (test_schedule_rescue.ScheduleModelTests.test_identical_disruption_is_used_for_all_strategy_recoveries) ... ok
    test_insufficient_aircraft_is_infeasible (test_schedule_rescue.ScheduleModelTests.test_insufficient_aircraft_is_infeasible) ... ok
    test_insufficient_turnaround_prevents_same_aircraft_connection (test_schedule_rescue.ScheduleModelTests.test_insufficient_turnaround_prevents_same_aircraft_connection) ... ok
    test_normal_schedule_and_route_continuity (test_schedule_rescue.ScheduleModelTests.test_normal_schedule_and_route_continuity) ... ok
    test_stale_result_settings_are_rejected (test_schedule_rescue.ScheduleModelTests.test_stale_result_settings_are_rejected) ... ok
    test_three_strategies_are_distinct_and_feasible (test_schedule_rescue.ScheduleModelTests.test_three_strategies_are_distinct_and_feasible) ... ok
    test_type_and_location_constraints (test_schedule_rescue.ScheduleModelTests.test_type_and_location_constraints) ... ok
    test_unavailability_reassigns_when_possible (test_schedule_rescue.ScheduleModelTests.test_unavailability_reassigns_when_possible) ... ok
    
    ----------------------------------------------------------------------
    Ran 20 tests in 3.044s
    
    OK
    Analyzed 27 rows (27 optimal, 0 failed or not run).
    strategy  scenario_count  initial_operating_cost  recovered_operating_cost  recovery_penalties  total_modeled_recovery_cost  cancelled_flights  operated_delayed_flights  aircraft_reassignment_count  crew_reassignment_count  unique_changed_flight_count  initial_connection_slack  recovered_connection_slack
    buffered               9                  6760.0               5755.555556       111388.888889                117144.444444                1.0                  0.333333                     0.666667                 1.111111                     1.777778                     115.0                   87.222222
    flexible               9                  6760.0               5755.555556       111344.444444                117100.000000                1.0                  0.333333                     0.666667                 0.666667                     0.777778                     115.0                   87.222222
      normal               9                  6660.0               5666.666667       111483.333333                117150.000000                1.0                  0.333333                     1.444444                 0.111111                     1.555556                      15.0                   58.333333
    Analysis files: /workspaces/ScheduleRescue/experiments/results/analysis
    Interpretation written to: /workspaces/ScheduleRescue/experiments/results/analysis/interpretation.md
    Per-scenario cost differences versus the lowest strategy cost in that scenario (operating and total modeled recovery cost separately):
                          buffered_operating_cost_delta  buffered_total_recovery_cost_delta  flexible_operating_cost_delta  flexible_total_recovery_cost_delta  normal_operating_cost_delta  normal_total_recovery_cost_delta
    scenario_id
    S01_none                                      100.0                               100.0                          100.0                               100.0                          0.0                               0.0
    S02_F001_30m                                    0.0                                 0.0                            0.0                                 0.0                          0.0                             750.0
    S03_F001_60m                                  200.0                               150.0                          200.0                                50.0                          0.0                               0.0
    S04_F001_120m                                 200.0                               150.0                          200.0                                50.0                          0.0                               0.0
    S05_F003_cancel                               200.0                               350.0                          200.0                               350.0                          0.0                               0.0
    S06_A002_unavailable                            0.0                               100.0                            0.0                                 0.0                          0.0                             150.0
    S07_C001_unavailable                          100.0                               100.0                          100.0                               200.0                          0.0                               0.0
    S08_F001_30m_A002                               0.0                               100.0                            0.0                                 0.0                          0.0                             150.0
    S09_A002_C001                                   0.0                               100.0                            0.0                                 0.0                          0.0                             150.0
    # Experiment interpretation
    
    These results cover nine illustrative scenarios on one small demo dataset. They do not show that one strategy is always superior.
    The winner lines compare total modeled recovery cost (recovered operating cost plus recovery penalties). Operating costs and penalties remain separate in the CSV and strategy table; a lower operating cost can coincide with higher reassignment or cancellation penalties.
    
    ## Lowest total modeled recovery cost by scenario
    
    - **S01_none:** normal had the lowest total modeled recovery cost (6,660.00).
    - **S02_F001_30m:** buffered, flexible had the lowest total modeled recovery cost (6,760.00).
    - **S03_F001_60m:** normal had the lowest total modeled recovery cost (106,100.00).
    - **S04_F001_120m:** normal had the lowest total modeled recovery cost (106,100.00).
    - **S05_F003_cancel:** normal had the lowest total modeled recovery cost (205,600.00).
    - **S06_A002_unavailable:** flexible had the lowest total modeled recovery cost (205,090.00).
    - **S07_C001_unavailable:** normal had the lowest total modeled recovery cost (6,660.00).
    - **S08_F001_30m_A002:** flexible had the lowest total modeled recovery cost (205,090.00).
    - **S09_A002_C001:** flexible had the lowest total modeled recovery cost (205,090.00).
    
    Use `scenario_cost_differences.csv` to compare both operating-cost and total-recovery-cost differences within each scenario. Strategy-specific initial preference scores are not included in these monetary comparisons.
    ✓ • 4.55s

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /workspaces/ScheduleRescue/experiments/analyze_results.py
    @@ -24,2 +24,3 @@
             operated_delayed_flights=("operated_delayed_flights", "mean"),
    +        cancelled_externally_delayed_flights=("cancelled_externally_delayed_flights", "mean"),
             aircraft_reassignment_count=("aircraft_reassignment_count", "mean"),
    @@ -45,3 +46,3 @@
             ("assignment_changes.html", ["aircraft_reassignment_count", "crew_reassignment_count", "unique_changed_flight_count"], "Assignment changes"),
    -        ("delay_comparison.html", ["operated_delayed_flights", "total_delay_minutes"], "External delay exposure"),
    +        ("delay_comparison.html", ["externally_imposed_delay_flights", "externally_imposed_delay_minutes", "operated_delayed_flights", "cancelled_externally_delayed_flights", "recovery_added_delay_minutes"], "External and recovery delay metrics"),
         ]

## Activity

    $ python experiments/analyze_results.py
    Analyzed 27 rows (27 optimal, 0 failed or not run).
    strategy  scenario_count  initial_operating_cost  recovered_operating_cost  recovery_penalties  total_modeled_recovery_cost  cancelled_flights  operated_delayed_flights  cancelled_externally_delayed_flights  aircraft_reassignment_count  crew_reassignment_count  unique_changed_flight_count  initial_connection_slack  recovered_connection_slack
    buffered               9                  6760.0               5755.555556       111388.888889                117144.444444                1.0                  0.333333                              0.111111                     0.666667                 1.111111                     1.777778                     115.0                   87.222222
    flexible               9                  6760.0               5755.555556       111344.444444                117100.000000                1.0                  0.333333                              0.111111                     0.666667                 0.666667                     0.777778                     115.0                   87.222222
      normal               9                  6660.0               5666.666667       111483.333333                117150.000000                1.0                  0.333333                              0.111111                     1.444444                 0.111111                     1.555556                      15.0                   58.333333
    Analysis files: /workspaces/ScheduleRescue/experiments/results/analysis
    Interpretation written to: /workspaces/ScheduleRescue/experiments/results/analysis/interpretation.md
    Per-scenario cost differences versus the lowest strategy cost in that scenario (operating and total modeled recovery cost separately):
                          buffered_operating_cost_delta  buffered_total_recovery_cost_delta  flexible_operating_cost_delta  flexible_total_recovery_cost_delta  normal_operating_cost_delta  normal_total_recovery_cost_delta
    scenario_id
    S01_none                                      100.0                               100.0                          100.0                               100.0                          0.0                               0.0
    S02_F001_30m                                    0.0                                 0.0                            0.0                                 0.0                          0.0                             750.0
    S03_F001_60m                                  200.0                               150.0                          200.0                                50.0                          0.0                               0.0
    S04_F001_120m                                 200.0                               150.0                          200.0                                50.0                          0.0                               0.0
    S05_F003_cancel                               200.0                               350.0                          200.0                               350.0                          0.0                               0.0
    S06_A002_unavailable                            0.0                               100.0                            0.0                                 0.0                          0.0                             150.0
    S07_C001_unavailable                          100.0                               100.0                          100.0                               200.0                          0.0                               0.0
    S08_F001_30m_A002                               0.0                               100.0                            0.0                                 0.0                          0.0                             150.0
    S09_A002_C001                                   0.0                               100.0                            0.0                                 0.0                          0.0                             150.0
    ✓ • 1.17s

## Assistant

## Completed

The working version is checkpointed at Git tag `checkpoint-phase1-before-correctness`.

**Metrics and app behavior:** Delay metrics now distinguish imposed delay, delayed flights that operated, delayed flights that were cancelled, and recovery-added delay. Connection gap and slack are calculated and labeled separately. Cost reports keep recovered operating cost, operating-cost change, each recovery penalty, and strategy preference scores distinct. Assignment changes include aircraft and crew counts plus the unique-flight union.

The app computes comparison metrics once and uses them for its table, charts, and CSV. It rejects failed solves for schedule metrics, checks schedule coverage, and clears stale results when relevant settings or disruptions change. Solve inputs and parameters are retained with results.

**Experiments and analysis:** The standalone runner covers all nine scenarios across all three strategies. Recovery uses identical constraints and penalty weights for every strategy. The analysis produces comparison tables, per-scenario operating and total-cost differences, charts, and an interpretation summary. It preserves failed or infeasible runs in its output.

## Verification results

- `python -m unittest discover -s tests -v`: **20 passed, 0 failed**.
- Streamlit AppTest smoke check: **0 exceptions**.
- Experiment runner: **27 rows** across 9 scenarios × 3 strategies; **27 Optimal**, with no failed or infeasible solves.
- CSV inspection confirmed every expected strategy/scenario pair and no missing required metrics. The cost identity held for every row: total modeled recovery cost = recovered operating cost + recovery penalties, with maximum discrepancy **0.0**.

The results show tradeoffs rather than a universal winner. For the 30-minute F001 delay, Buffered and Flexible have lower total modeled recovery cost than Normal; for the 60-minute delay, Normal has the lowest total modeled recovery cost. These are illustrative outcomes from this small demo dataset.

## Files and outputs

Updated the app, scheduler, metrics, tests, README, and methodology, assumptions, and user-guide documentation. Added the experiment runner and analysis script.

- Results: [experiment_results.csv](/workspaces/ScheduleRescue/experiments/results/experiment_results.csv)
- Analysis summary: [strategy_comparison.csv](/workspaces/ScheduleRescue/experiments/results/analysis/strategy_comparison.csv)
- Scenario cost differences: [scenario_cost_differences.csv](/workspaces/ScheduleRescue/experiments/results/analysis/scenario_cost_differences.csv)
- Interpretation: [interpretation.md](/workspaces/ScheduleRescue/experiments/results/analysis/interpretation.md)
- Charts and additional analysis files: `/workspaces/ScheduleRescue/experiments/results/analysis/`

Reproduce the work from the repository root:

```bash
python -m unittest discover -s tests -v
python experiments/run_experiments.py
python experiments/analyze_results.py
```

Remaining limitations include the small illustrative dataset, simplified crew rules, fixed flight times during recovery, and possible solver tie-breaking differences across environments. The experiment records Python, pandas, PuLP, CBC, and platform versions; exact equal-cost assignments are not guaranteed.
