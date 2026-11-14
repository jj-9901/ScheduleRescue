import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from experiments import analyze_results, run_experiments
from tests.test_schedule_rescue import data
from src.scheduler import solve_schedule


class ExperimentPairTests(unittest.TestCase):
    def test_pair_outcome_matrix_and_failure_reasons(self):
        cases = [
            ("optimal", "optimal", "optimal_pair"),
            ("feasible_limit", "optimal", "feasible_pair"),
            ("optimal", "feasible_limit", "feasible_pair"),
            ("feasible_limit", "failed", "failed_pair"),
            ("optimal", "infeasible", "failed_pair"),
            ("failed", "not_run_initial", "failed_pair"),
        ]
        for initial, recovery, expected in cases:
            with self.subTest(initial=initial, recovery=recovery):
                outcome, reason = run_experiments._pair_outcome(initial, recovery)
                self.assertEqual(outcome, expected)
                detail = run_experiments._pair_detail(initial, recovery)
                if initial not in {"optimal", "feasible_limit"}:
                    expected_detail = f"initial_{initial}"
                elif recovery not in {"optimal", "feasible_limit"}:
                    expected_detail = f"recovery_{recovery}"
                else:
                    expected_detail = f"initial_{initial}_recovery_{recovery}"
                self.assertEqual(detail, expected_detail)
                if expected == "failed_pair":
                    self.assertTrue(reason)

    def test_pair_failure_is_recorded_and_batch_continues(self):
        fake_scenarios = (
            {"scenario_id": "bad", "delays": {}, "cancel": [], "aircraft": [], "crew": []},
            {"scenario_id": "good", "delays": {}, "cancel": [], "aircraft": [], "crew": []},
        )
        f, a, c = data()
        initial = {"status": "Optimal", "result_classification": "optimal", "schedule": solve_schedule(f, a, c)["schedule"], "components": {}, "solver_message": "ok"}
        recovery_good = solve_schedule(f, a, c, allow_cancellation=True)
        calls = []
        def mocked(*args, **kwargs):
            calls.append(kwargs)
            if kwargs.get("strategy") in {"normal", "buffered", "flexible"} and not kwargs.get("original_assignment"):
                return initial
            if kwargs.get("unavailable_aircraft") is not None and len(calls) % 2:
                return {"status": "Infeasible", "result_classification": "infeasible", "schedule": pd.DataFrame(), "solver_message": "controlled infeasible", "solver_termination_reason": "controlled infeasible"}
            return recovery_good
        with tempfile.TemporaryDirectory() as tmp, patch.object(run_experiments, "SCENARIOS", fake_scenarios), patch.object(run_experiments, "solve_schedule", side_effect=mocked):
            result, _ = run_experiments.run_experiments(Path(tmp) / "out.csv")
            stored = pd.read_csv(Path(tmp) / "out.csv")
        self.assertEqual(len(result), 6)
        self.assertTrue((result.pair_outcome == "optimal_pair").any())
        self.assertTrue((result.pair_outcome == "failed_pair").any())
        self.assertEqual(len(stored), 6)
        self.assertTrue(stored.loc[stored.pair_outcome == "failed_pair", "pair_failure_reason"].notna().all())

    def test_initial_failure_skips_recovery_but_records_each_pair(self):
        failed = {"status": "Infeasible", "result_classification": "infeasible",
                  "solver_termination_reason": "initial infeasible", "solver_message": "initial infeasible",
                  "schedule": pd.DataFrame(), "components": {}}
        with tempfile.TemporaryDirectory() as tmp, patch.object(run_experiments, "solve_schedule", return_value=failed):
            frame, _ = run_experiments.run_experiments(Path(tmp) / "out.csv")
        self.assertEqual(len(frame), len(run_experiments.SCENARIOS) * len(run_experiments.STRATEGIES))
        self.assertTrue((frame.pair_outcome == "failed_pair").all())
        self.assertTrue((frame.recovery_result_classification == "not_run_initial").all())
        self.assertTrue(frame.recovery_error.str.contains("not attempted").all())

    def test_runner_propagates_and_records_configuration(self):
        captured = []
        real = run_experiments.solve_schedule
        def record(*args, **kwargs):
            captured.append(dict(kwargs))
            return real(*args, **kwargs)
        with tempfile.TemporaryDirectory() as tmp, patch.object(run_experiments, "solve_schedule", side_effect=record):
            frame, _ = run_experiments.run_experiments(Path(tmp) / "out.csv")
        self.assertTrue(captured)
        for kw in captured:
            self.assertIn("crew_rest_minutes", kw)
            if kw.get("original_assignment"):
                self.assertEqual(kw["aircraft_change_penalty"], run_experiments.RECOVERY_PARAMETERS["aircraft_change_penalty"])
                self.assertEqual(kw["crew_change_penalty"], run_experiments.RECOVERY_PARAMETERS["crew_change_penalty"])
                self.assertEqual(kw["cancellation_penalty"], run_experiments.RECOVERY_PARAMETERS["cancellation_penalty"])
                self.assertEqual(kw["strategy"], "normal")
            else:
                self.assertNotIn("aircraft_change_penalty", kw)
        self.assertEqual(json.loads(frame.iloc[0].initial_parameters)["crew_rest_minutes"], 30)
        self.assertEqual(json.loads(frame.iloc[0].initial_solve_parameters)["strategy"], "normal")
        self.assertIn("A001", json.loads(frame.iloc[0].initial_solve_parameters)["operating_cost_weights"]["aircraft"])
        recovery_parameters = json.loads(frame.loc[frame.recovery_solve_parameters != "", "recovery_solve_parameters"].iloc[0])
        self.assertEqual(recovery_parameters["strategy"], "normal")
        self.assertEqual(recovery_parameters["aircraft_change_penalty"], run_experiments.RECOVERY_PARAMETERS["aircraft_change_penalty"])
        self.assertIn("C001", recovery_parameters["operating_cost_weights"]["crew"])

    def test_scheduler_records_and_uses_configured_penalties(self):
        f, a, c = data()
        base = solve_schedule(f, a, c, allow_cancellation=True)
        assignment = {fid: "missing" for fid in base["schedule"].flight_id}
        crew_assignment = {fid: [] for fid in base["schedule"].flight_id}
        changed = solve_schedule(f, a, c, allow_cancellation=True,
            original_assignment=assignment, original_crew_assignment=crew_assignment,
            aircraft_change_penalty=37, crew_change_penalty=19, cancellation_penalty=321)
        self.assertEqual(changed["solve_parameters"]["aircraft_change_penalty"], 37)
        self.assertEqual(changed["solve_parameters"]["crew_change_penalty"], 19)
        self.assertEqual(changed["solve_parameters"]["cancellation_penalty"], 321)
        self.assertGreater(changed["components"]["aircraft_reassignment_penalty"], 0)
        self.assertGreater(changed["components"]["crew_reassignment_penalty"], 0)

        cancelled_low = solve_schedule(f, a, c, cancelled_flights=["F1"], allow_cancellation=True, cancellation_penalty=321)
        cancelled_high = solve_schedule(f, a, c, cancelled_flights=["F1"], allow_cancellation=True, cancellation_penalty=642)
        self.assertEqual(cancelled_low["components"]["cancellation_penalty"], 321)
        self.assertEqual(cancelled_high["components"]["cancellation_penalty"], 642)

    def test_unsupported_configuration_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported initial experiment configuration"):
            run_experiments._validated_parameters({"mystery_weight": 2}, set(), "initial")


class ExperimentAnalysisTests(unittest.TestCase):
    def table(self, success):
        rows = []
        for strategy, ids in success.items():
            for scenario in ("s1", "s2", "s3"):
                ok = scenario in ids
                rows.append({"scenario_id": scenario, "strategy": strategy,
                    "initial_result_classification": "optimal",
                    "recovery_result_classification": "optimal" if ok else "infeasible",
                    "pair_outcome": "optimal_pair" if ok else "failed_pair",
                    "pair_failure_reason": "controlled failure" if not ok else "",
                    "initial_operating_cost": 1 if ok else None,
                    "recovered_operating_cost": {"normal": 10, "buffered": 20, "flexible": 30}[strategy] if ok else None,
                    "recovery_penalties": 0 if ok else None,
                    "total_modeled_recovery_cost": {"normal": 10, "buffered": 20, "flexible": 30}[strategy] if ok else None})
        return pd.DataFrame(rows)

    def test_mutually_exclusive_exports_totals_and_common_scenarios(self):
        table = self.table({"normal": {"s1", "s2"}, "buffered": {"s1", "s3"}, "flexible": {"s1"}})
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.csv"; table.to_csv(source, index=False)
            summary, differences = analyze_results.analyze(source)
            output = source.parent / "analysis"
            self.assertEqual(len(pd.read_csv(output / "optimal_pair.csv")), 5)
            self.assertEqual(len(pd.read_csv(output / "feasible_pair.csv")), 0)
            self.assertEqual(len(pd.read_csv(output / "failed_pair.csv")), 4)
            self.assertEqual(len(pd.read_csv(output / "failed_solves.csv")), 4)
            self.assertEqual(len(pd.read_csv(output / "common_successful_scenario_metrics.csv")), 3)
            self.assertEqual(set(differences.index), {"s1"})
            counts = pd.read_csv(output / "outcome_counts.csv").set_index("outcome")["count"]
            self.assertEqual(int(counts.sum()), len(table))
            self.assertTrue((pd.read_csv(output / "failed_solves.csv").pair_failure_reason == "controlled failure").all())
            self.assertEqual(set(summary.common_scenario_count), {1})

    def test_no_common_scenario_produces_no_comparison_average(self):
        table = self.table({"normal": {"s1"}, "buffered": {"s2"}, "flexible": {"s3"}})
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.csv"; table.to_csv(source, index=False)
            summary, differences = analyze_results.analyze(source)
            self.assertEqual(len(summary), 0)
            self.assertTrue(differences.empty)
            interpretation = (source.parent / "analysis" / "interpretation.md").read_text()
            self.assertIn("No common successful scenarios", interpretation)


if __name__ == "__main__":
    unittest.main()
