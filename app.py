"""Streamlit front end for Schedule Rescue."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from src.scheduler import solve_schedule
from src.validation import prepare_data
from src.metrics import connection_metrics, compare_schedules, settings_match
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
    for key in ("initial_results","recovery_results","input_snapshot","model_settings","scenario","disrupted_flights","comparison_results"):
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
    chosen=st.multiselect("Strategies to solve",["normal","buffered","flexible"],["normal","buffered","flexible"],format_func=str.title,key="chosen_strategies")
    active_settings={"turnaround":int(turnaround),"buffer":int(buffer),"target":int(target),"strategies":list(chosen)}
    if st.session_state.get("initial_results") and not settings_match(st.session_state.get("model_settings"), active_settings):
        clear_optimization_state()
    if st.button("Solve initial schedule(s)",type="primary"):
        if "data" not in st.session_state: st.error("Provide valid data in Airline data first.")
        else:
            f,a,c=st.session_state["data"]; results={}
            for strategy in chosen:
                with st.spinner(f"Solving {strategy} MILP..."):
                    results[strategy]=solve_schedule(f,a,c,turnaround_minutes=turnaround,strategy=strategy,buffer_minutes=buffer,flexibility_target_minutes=target)
                results[strategy]["solve_context"]={"flights":f.copy(),"aircraft":a.copy(),"crew":c.copy(),
                    "strategy_settings":dict(active_settings),"strategy":strategy}
            st.session_state["initial_results"]=results
            st.session_state["input_snapshot"]=(f.copy(),a.copy(),c.copy())
            st.session_state["model_settings"]=active_settings
            st.session_state.pop("recovery_results",None)
    for strategy,result in st.session_state.get("initial_results",{}).items():
        st.markdown(f"#### {strategy.title()} — {result['status']}")
        if result["status"]=="Optimal":
            st.dataframe(result["schedule"],use_container_width=True)
            m=connection_metrics(result["schedule"],int(turnaround))
            cols=st.columns(4); cols[0].metric("Operating cost",f"{result['components']['scheduled_operating_cost']:,.2f}"); cols[1].metric("Aircraft used",result["schedule"].assigned_aircraft.nunique()); cols[2].metric("Crew used",len(set(";".join(result["schedule"].assigned_crew).split(";")))); cols[3].metric("Average connection slack",f"{m['average_connection_slack_minutes'] or 0:.0f} min")
            st.caption(f"Average connection gap: {m['average_connection_gap_minutes'] if m['average_connection_gap_minutes'] is not None else '—'} min · Minimum gap: {m['minimum_connection_gap_minutes'] if m['minimum_connection_gap_minutes'] is not None else '—'} min · Minimum slack: {m['minimum_connection_slack_minutes'] if m['minimum_connection_slack_minutes'] is not None else '—'} min")
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
        current_scenario={"delay_ids":list(delay_ids),"delay_minutes":int(delay_minutes),"cancel_ids":list(cancel_ids),"unavailable_a":list(unavailable_a),"unavailable_c":list(unavailable_c)}
        if st.session_state.get("recovery_results") and st.session_state.get("scenario") != current_scenario:
            st.session_state.pop("recovery_results",None); st.session_state.pop("comparison_results",None)
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
                recovery[strategy]["solve_context"]={"flights":modified.copy(),"aircraft":a.copy(),"crew":c.copy(),
                    "initial_strategy":strategy,"initial_settings":dict(settings),"disruptions":dict(current_scenario),
                    "recovery_parameters":dict(recovery[strategy].get("solve_parameters",{}))}
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
            st.session_state["scenario"]=current_scenario
            comparison={}
            for strategy,result in recovery.items():
                if result.get("status")=="Optimal":
                    comparison[strategy]=compare_schedules(initial[strategy]["schedule"],result["schedule"],initial[strategy],result,
                        externally_imposed_delays={fid:int(delay_minutes) for fid in delay_ids},expected_flight_ids=flight_ids,
                        turnaround_minutes=settings["turnaround"])
                else:
                    comparison[strategy]={"solver_status":result.get("status","Unknown")}
            st.session_state["comparison_results"]=comparison
    for strategy,result in st.session_state.get("recovery_results",{}).items():
        st.markdown(f"#### {strategy.title()} recovery — {result['status']}")
        if result["status"]=="Optimal":
            base=initial[strategy]; st.dataframe(result["schedule"],use_container_width=True)
            metrics=st.session_state.get("comparison_results",{}).get(strategy,{})
            cols=st.columns(4); cols[0].metric("Cancelled flights",metrics["cancelled_flights"]); cols[1].metric("Aircraft changed",metrics["aircraft_changed_flights"]); cols[2].metric("Crew changed",metrics["crew_changed_flights"]); cols[3].metric("Final operating cost",f"{metrics['recovery_operating_cost']:,.2f}")
            st.caption(f"Unique flights with assignment changes: {metrics['unique_changed_flights']}. Externally delayed: {metrics['externally_imposed_delay_flights']}; operated delayed: {metrics['operated_externally_delayed_flights']}; cancelled after delay: {metrics['cancelled_externally_delayed_flights']}; recovery-added delay: {metrics['recovery_added_delay_minutes']} minutes.")
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
        if result["status"]=="Optimal": rows.append({"Strategy":strategy.title(),**st.session_state.get("comparison_results",{}).get(strategy,{})})
        else: rows.append({"Strategy":strategy.title(),"solver_status":result["status"]})
    if rows:
        table=pd.DataFrame(rows); st.dataframe(table,use_container_width=True); csv_download("Download comparison CSV",table,"strategy_comparison.csv")
        valid=table[table.solver_status=="Optimal"]
        if not valid.empty:
            for metric,title in [("initial_operating_cost","Initial operating cost"),("recovery_operating_cost","Recovered operating cost"),("total_modeled_recovery_cost","Total modeled recovery cost"),("cancelled_flights","Cancelled flights"),("operated_externally_delayed_flights","Operated externally delayed flights"),("aircraft_changed_flights","Aircraft assignment changes"),("crew_changed_flights","Crew assignment changes"),("unique_changed_flights","Unique flights changed")]:
                st.plotly_chart(px.bar(valid,x="Strategy",y=metric,title=title),use_container_width=True)
            st.caption("Total modeled recovery cost = recovered operating cost + cancellation, aircraft change, crew change, and other recovery penalties. Strategy preference scores are separate. Initial cost is shown for comparison only.")
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
