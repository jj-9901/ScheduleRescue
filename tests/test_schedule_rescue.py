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
