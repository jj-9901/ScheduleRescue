import unittest
import pandas as pd
from io import StringIO
from unittest.mock import patch
import pulp
from src.scheduler import solve_schedule, _classify_solver_result, _cbc_metadata, _schedule_passes_coverage
from src.validation import prepare_data
from src.metrics import compare_schedules, connection_metrics, settings_match
from pathlib import Path
from tempfile import TemporaryDirectory


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

    def test_connection_gap_and_slack_are_distinct(self):
        schedule=pd.DataFrame([
            {"flight_id":"X","origin":"AAA","destination":"BBB","departure":pd.Timestamp("2026-01-01 08:00"),"arrival":pd.Timestamp("2026-01-01 09:00"),"assigned_aircraft":"CHECK","assigned_crew":"C1","status":"Scheduled"},
            {"flight_id":"Y","origin":"BBB","destination":"CCC","departure":pd.Timestamp("2026-01-01 10:00"),"arrival":pd.Timestamp("2026-01-01 11:00"),"assigned_aircraft":"CHECK","assigned_crew":"C1","status":"Scheduled"}])
        metrics=connection_metrics(schedule,45)
        self.assertEqual(metrics["average_connection_gap_minutes"],60)
        self.assertEqual(metrics["average_connection_slack_minutes"],15)

    def test_external_delay_categories_and_cancelled_delay(self):
        f,a,c=data(); initial=self.solve(f,a,c)
        base=initial["schedule"].copy()
        recovered=base.copy()
        recovered.loc[recovered.flight_id=="F1","status"]="Cancelled"
        recovered.loc[recovered.flight_id=="F1","assigned_aircraft"]=None
        recovered.loc[recovered.flight_id=="F1","assigned_crew"]=""
        result={"status":"Optimal","components":initial["components"]}
        metrics=compare_schedules(base,recovered,initial,result,externally_imposed_delays={"F1":30,"F2":30})
        self.assertEqual(metrics["externally_imposed_delay_flights"],2)
        self.assertEqual(metrics["operated_externally_delayed_flights"],1)
        self.assertEqual(metrics["cancelled_externally_delayed_flights"],1)
        self.assertEqual(metrics["recovery_added_delay_minutes"],0)

    def test_cost_identity_unique_changes_and_uncovered_flights(self):
        f,a,c=data(); initial=self.solve(f,a,c)
        recovered=initial["schedule"].copy()
        recovered.loc[recovered.flight_id=="F1","assigned_aircraft"]="A-NEW"
        recovered.loc[recovered.flight_id=="F1","assigned_crew"]="C-NEW"
        comps={"scheduled_operating_cost":70,"cancellation_penalty":3,
               "aircraft_reassignment_penalty":5,"crew_reassignment_penalty":7,
               "other_recovery_penalties":2}
        solved={"status":"Optimal","components":comps}
        metrics=compare_schedules(initial["schedule"],recovered,initial,solved)
        self.assertEqual(metrics["aircraft_changed_flights"],1)
        self.assertEqual(metrics["crew_changed_flights"],1)
        self.assertEqual(metrics["unique_changed_flights"],1)
        self.assertEqual(metrics["recovery_penalties"],17)
        self.assertEqual(metrics["total_modeled_recovery_cost"],87)
        partial=recovered[recovered.flight_id!="F1"]
        incomplete=compare_schedules(initial["schedule"],partial,initial,solved,expected_flight_ids=["F1","F2","F3"])
        self.assertEqual(incomplete["unexpectedly_uncovered_flights"],1)

    def test_stale_result_settings_are_rejected(self):
        used={"turnaround":45,"buffer":30,"target":90,"strategies":["normal"]}
        self.assertTrue(settings_match(used,dict(used)))
        self.assertFalse(settings_match(used,{**used,"turnaround":60}))

    def test_failed_solve_cannot_produce_schedule_metrics(self):
        with self.assertRaisesRegex(ValueError,"failed solve"):
            compare_schedules(pd.DataFrame(),pd.DataFrame(),{}, {"status":"Infeasible"})

    def test_comparison_metrics_round_trip_to_csv(self):
        f,a,c=data(); initial=self.solve(f,a,c)
        metrics=compare_schedules(initial["schedule"],initial["schedule"],initial,initial)
        table=pd.DataFrame([{"Strategy":"Normal",**metrics}])
        restored=pd.read_csv(pd.io.common.StringIO(table.to_csv(index=False)))
        self.assertEqual(list(table.columns),list(restored.columns))
        self.assertEqual(table.iloc[0]["total_modeled_recovery_cost"],restored.iloc[0]["total_modeled_recovery_cost"])

    def test_experiment_runner_uses_all_strategies_for_same_scenarios(self):
        from experiments.run_experiments import SCENARIOS, STRATEGIES, run_experiments
        with TemporaryDirectory() as tmp:
            result,path=run_experiments(Path(tmp)/"out.csv")
            self.assertEqual(len(result),len(SCENARIOS)*len(STRATEGIES))
            self.assertEqual(set(result.strategy),set(STRATEGIES))
            for scenario_id,group in result.groupby("scenario_id"):
                self.assertEqual(set(group.strategy),set(STRATEGIES),scenario_id)
            self.assertTrue(Path(path).exists())

    def test_solver_result_classification_uses_solution_status(self):
        class Model:
            status = pulp.LpStatusOptimal
            sol_status = pulp.LpSolutionOptimal
        self.assertEqual(_classify_solver_result(Model()), "optimal")
        Model.sol_status = pulp.LpSolutionIntegerFeasible
        self.assertEqual(_classify_solver_result(Model()), "feasible_limit")
        Model.status = pulp.LpStatusInfeasible
        Model.sol_status = pulp.LpSolutionInfeasible
        self.assertEqual(_classify_solver_result(Model()), "infeasible")
        Model.status = pulp.LpStatusNotSolved
        Model.sol_status = pulp.LpSolutionNoSolutionFound
        self.assertEqual(_classify_solver_result(Model()), "failed")

    def test_feasible_incumbent_must_pass_independent_coverage_checks(self):
        f,a,c=data(); normalized,_,_=prepare_data(f,a,c)
        flight_data=normalized.set_index("flight_id").to_dict("index")
        schedule=pd.DataFrame([{"flight_id":"F1","assigned_aircraft":"A1","assigned_crew":"C1","status":"Scheduled"}])
        self.assertFalse(_schedule_passes_coverage(schedule, normalized.flight_id.tolist(), flight_data))
        schedule=pd.DataFrame([{"flight_id":fid,"assigned_aircraft":"A1","assigned_crew":"","status":"Scheduled"} for fid in normalized.flight_id])
        self.assertFalse(_schedule_passes_coverage(schedule, normalized.flight_id.tolist(), flight_data))

    def test_cbc_stopped_incumbent_parser_and_metadata(self):
        # This reproduces PuLP 2.9.0 CBC's broad Optimal + IntegerFeasible mapping.
        class Model:
            status = pulp.LpStatusOptimal
            sol_status = pulp.LpSolutionIntegerFeasible
        self.assertEqual(_classify_solver_result(Model()), "feasible_limit")
        reason, bound, gap = _cbc_metadata("Result - Stopped on time limit\nLower bound: 12.5\nGap: 0.25\n")
        self.assertEqual(reason, "Stopped on time limit")
        self.assertEqual(bound, 12.5)
        self.assertEqual(gap, 0.25)

    def test_proven_optimal_and_infeasible_solve_classifications(self):
        f,a,c=data()
        result=solve_schedule(f,a,c)
        self.assertEqual(result["result_classification"], "optimal")
        self.assertEqual(result["pulp_solution_status"], "Optimal Solution Found")
        impossible=solve_schedule(f,a.iloc[:1].copy(),c)
        self.assertEqual(impossible["result_classification"], "infeasible")
        self.assertTrue(impossible["schedule"].empty)

    def test_failed_solve_has_no_schedule(self):
        f,a,c=data()
        with patch("src.scheduler.pulp.PULP_CBC_CMD.actualSolve", side_effect=pulp.PulpSolverError("controlled solver failure")):
            result=solve_schedule(f,a,c)
        self.assertEqual(result["result_classification"], "failed")
        self.assertIn("controlled solver failure", result["solver_termination_reason"])
        self.assertTrue(result["schedule"].empty)

    def test_fractional_required_crew_count_is_rejected_before_cast(self):
        f,a,c=data(); f["required_crew_count"]=f.required_crew_count.astype(object); f.loc[0,"required_crew_count"]=1.8
        with self.assertRaisesRegex(ValueError, r"F1.*required_crew_count"):
            prepare_data(f,a,c)

    def test_required_crew_count_acceptance_and_rejections(self):
        f,a,c=data()
        for value in (1,2,1.0,2.0,"1.0","2.0"):
            with self.subTest(value=value):
                candidate=f.copy(); candidate["required_crew_count"]=value
                normalized,_,_=prepare_data(candidate,a,c)
                self.assertEqual(set(normalized.required_crew_count),{int(float(value))})
        for value in (1.8,0,-1,float("nan"),"NaN",float("inf"),float("-inf"),"abc"):
            with self.subTest(value=value):
                candidate=f.copy(); candidate["required_crew_count"]=value
                with self.assertRaisesRegex(ValueError, "required_crew_count"):
                    prepare_data(candidate,a,c)
        candidate=f.copy(); candidate["required_crew_count"]=""
        normalized,_,_=prepare_data(candidate,a,c)
        self.assertEqual(set(normalized.required_crew_count),{1})
        candidate=f.copy(); candidate["required_crew_count"]=None
        normalized,_,_=prepare_data(candidate,a,c)
        self.assertEqual(set(normalized.required_crew_count),{1})

    def test_csv_like_float_crew_counts_are_validated_without_truncation(self):
        f,a,c=data(); f["required_crew_count"]=pd.Series([1.0,2.0,1.0],dtype="float64")
        normalized,_,_=prepare_data(f,a,c)
        self.assertEqual(normalized.set_index("flight_id").required_crew_count.to_dict(),{"F1":1,"F2":2,"F3":1})
        f.loc[0,"required_crew_count"]=1.8
        with self.assertRaisesRegex(ValueError,"F1"):
            prepare_data(f,a,c)

    def test_csv_parser_preserves_blank_vs_nan_crew_count_values(self):
        flights,aircraft,crew=data()
        csv_text="flight_id,origin,destination,departure,arrival,aircraft_type_required,required_crew_count,priority\nX,AAA,BBB,2026-01-01 08:00,2026-01-01 09:00,T,2.0,1\n"
        parsed=pd.read_csv(StringIO(csv_text))
        raw=pd.read_csv(StringIO(csv_text),usecols=["required_crew_count"],converters={"required_crew_count":str},keep_default_na=False)
        parsed["required_crew_count"]=raw.required_crew_count.values
        normalized,_,_=prepare_data(parsed,aircraft.iloc[:1],crew.iloc[:2])
        self.assertEqual(int(normalized.required_crew_count.iloc[0]),2)
        csv_text=csv_text.replace(",2.0,",",1.8,")
        parsed=pd.read_csv(StringIO(csv_text))
        raw=pd.read_csv(StringIO(csv_text),usecols=["required_crew_count"],converters={"required_crew_count":str},keep_default_na=False)
        parsed["required_crew_count"]=raw.required_crew_count.values
        with self.assertRaisesRegex(ValueError,"required_crew_count"):
            prepare_data(parsed,aircraft.iloc[:1],crew.iloc[:2])
        csv_text=csv_text.replace(",1.8,",",,")
        parsed=pd.read_csv(StringIO(csv_text))
        raw=pd.read_csv(StringIO(csv_text),usecols=["required_crew_count"],converters={"required_crew_count":str},keep_default_na=False)
        parsed["required_crew_count"]=raw.required_crew_count.values
        normalized,_,_=prepare_data(parsed,aircraft.iloc[:1],crew.iloc[:2])
        self.assertEqual(int(normalized.required_crew_count.iloc[0]),1)

    def test_sanitization_colliding_ids_solve_and_preserve_original_ids(self):
        flights=pd.DataFrame([
            ["f-1","AAA","BBB","2026-01-01 08:00","2026-01-01 09:00","T",1,1],
            ["f_1","AAA","CCC","2026-01-01 08:00","2026-01-01 09:00","T",1,1]],
            columns=["flight_id","origin","destination","departure","arrival","aircraft_type_required","required_crew_count","priority"])
        aircraft=pd.DataFrame([
            ["a-1","AAA","2026-01-01 06:00",100,"T"],
            ["a_1","AAA","2026-01-01 06:00",100,"T"]],
            columns=["aircraft_id","initial_location","available_from","cost_per_hour","aircraft_type"])
        crew=pd.DataFrame([
            ["c-1","AAA","2026-01-01 06:00","T",8,10],
            ["c_1","AAA","2026-01-01 06:00","T",8,10]],
            columns=["crew_id","initial_location","available_from","eligible_aircraft_types","max_work_hours","cost_per_hour"])
        result=solve_schedule(flights,aircraft,crew)
        self.assertEqual(result["result_classification"],"optimal",result)
        schedule=result["schedule"]
        self.assertEqual(set(schedule.flight_id),{"f-1","f_1"})
        self.assertEqual(set(schedule.assigned_aircraft),{"a-1","a_1"})
        self.assertEqual(set(schedule.assigned_crew),{"c-1","c_1"})
        self.assertTrue(schedule.assigned_aircraft.is_unique)
        self.assertTrue(schedule.assigned_crew.is_unique)
        self.assertTrue(set(schedule.assigned_aircraft).issubset({"a-1","a_1"}))
        self.assertTrue(set(schedule.assigned_crew).issubset({"c-1","c_1"}))


if __name__=="__main__": unittest.main()
