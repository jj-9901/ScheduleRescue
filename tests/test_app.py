from pathlib import Path
import unittest
from unittest.mock import patch

import plotly.express as px
import streamlit as st
from streamlit.testing.v1 import AppTest

from src.scheduler import solve_schedule


APP = Path(__file__).resolve().parents[1] / "app.py"


class AppResultTests(unittest.TestCase):
    def setUp(self):
        st.cache_data.clear()

    def tearDown(self):
        st.cache_data.clear()

    def click(self, app, label):
        next(button for button in app.button if button.label == label).click().run()
        self.assertFalse(app.exception, [item.message for item in app.exception])

    def test_initial_construction_error_is_reported_and_retry_succeeds(self):
        with patch("src.scheduler.solve_schedule", side_effect=ValueError("controlled initial error")):
            app = AppTest.from_file(str(APP), default_timeout=60).run()
            self.click(app, "Solve initial schedule(s)")
            self.assertEqual(len(app.session_state["initial_results"]), 3)
            self.assertTrue(all(row["result_classification"] == "failed"
                                for row in app.session_state["initial_results"].values()))
            self.assertTrue(any("controlled initial error" in item.value for item in app.error))
        self.click(app, "Solve initial schedule(s)")
        self.assertTrue(all(row["result_classification"] == "optimal"
                            for row in app.session_state["initial_results"].values()))

    def test_recovery_construction_error_is_reported_without_metrics(self):
        def solve(*args, **kwargs):
            if kwargs.get("allow_cancellation"):
                raise ValueError("controlled recovery error")
            return solve_schedule(*args, **kwargs)

        with patch("src.scheduler.solve_schedule", side_effect=solve):
            app = AppTest.from_file(str(APP), default_timeout=60).run()
            self.click(app, "Solve initial schedule(s)")
            self.click(app, "Recover every solved strategy")
            comparison = app.session_state["comparison_results"]
            self.assertEqual(len(comparison), 3)
            self.assertTrue(all("total_modeled_recovery_cost" not in row for row in comparison.values()))
            self.assertTrue(any("controlled recovery error" in item.value for item in app.error))

    def check_charts(self, mixed):
        recovery_count = 0

        def solve(*args, **kwargs):
            nonlocal recovery_count
            if kwargs.get("allow_cancellation"):
                recovery_count += 1
                if mixed and recovery_count == 3:
                    raise ValueError("controlled failed recovery")
            result = solve_schedule(*args, **kwargs)
            if not mixed or (not kwargs.get("allow_cancellation") and kwargs["strategy"] == "buffered"):
                result.update(status="FeasibleLimit", result_classification="feasible_limit",
                              solver_termination_reason="Controlled feasible-incumbent fixture")
            return result

        with patch("src.scheduler.solve_schedule", side_effect=solve), patch("plotly.express.bar", wraps=px.bar) as bar:
            app = AppTest.from_file(str(APP), default_timeout=60).run()
            self.click(app, "Solve initial schedule(s)")
            bar.reset_mock()
            self.click(app, "Recover every solved strategy")
            self.assertEqual(bar.call_count, 8)
            for call in bar.call_args_list:
                plotted = call.args[0]
                self.assertEqual(set(plotted.Strategy), {"Normal", "Buffered"} if mixed
                                 else {"Normal", "Buffered", "Flexible"})
                self.assertEqual(set(plotted["Solution status"]),
                                 {"Proven optimal", "Feasible; optimality not proven"} if mixed
                                 else {"Feasible; optimality not proven"})
                self.assertEqual(call.kwargs["color"], "Solution status")
            self.assertTrue(any("Chart legends identify" in item.value for item in app.warning))

    def test_all_feasible_pairs_appear_in_comparison_charts(self):
        self.check_charts(mixed=False)

    def test_mixed_pairs_are_labeled_and_failed_pairs_are_excluded(self):
        self.check_charts(mixed=True)


if __name__ == "__main__":
    unittest.main()
