import unittest

from src.scheduler import solve_schedule
from src.validation import prepare_data
from tests.test_schedule_rescue import data


class InputValidationTests(unittest.TestCase):
    def test_invalid_parsed_timestamps_report_column_and_id(self):
        for table, column, identifier in (
            (0, "departure", "F1"), (0, "arrival", "F1"),
            (1, "available_from", "A1"), (2, "available_from", "C1"),
        ):
            for value in ("NaT", "", "invalid timestamp"):
                with self.subTest(table=table, column=column, value=value):
                    tables = list(data())
                    tables[table].loc[0, column] = value
                    with self.assertRaisesRegex(ValueError, f"{column}.*{identifier}"):
                        prepare_data(*tables)

    def test_nonfinite_data_is_rejected_before_model_construction(self):
        for table, column, identifier in (
            (0, "priority", "F1"), (1, "cost_per_hour", "A1"),
            (2, "cost_per_hour", "C1"), (2, "max_work_hours", "C1"),
        ):
            for value in (float("inf"), float("-inf")):
                with self.subTest(table=table, column=column, value=value):
                    tables = list(data())
                    tables[table][column] = tables[table][column].astype(float)
                    tables[table].loc[0, column] = value
                    with self.assertRaisesRegex(ValueError, f"{column}.*finite.*{identifier}"):
                        solve_schedule(*tables)

    def test_nonfinite_and_negative_model_parameters_are_rejected(self):
        tables = data()
        for name in (
            "turnaround_minutes", "crew_rest_minutes", "buffer_minutes",
            "flexibility_target_minutes", "flexibility_penalty_per_minute",
            "cancellation_penalty", "aircraft_change_penalty", "crew_change_penalty",
            "time_limit",
        ):
            for value in (float("nan"), float("inf"), float("-inf"), -1):
                with self.subTest(parameter=name, value=value):
                    with self.assertRaisesRegex(ValueError, name):
                        solve_schedule(*tables, **{name: value})
        with self.assertRaisesRegex(ValueError, "time_limit"):
            solve_schedule(*tables, time_limit=0)

    def test_zero_costs_and_zero_policy_weights_remain_usable(self):
        flights, aircraft, crew = data()
        aircraft["cost_per_hour"] = 0
        crew["cost_per_hour"] = 0
        result = solve_schedule(
            flights, aircraft, crew, turnaround_minutes=0, crew_rest_minutes=0,
            buffer_minutes=0, flexibility_target_minutes=0,
            flexibility_penalty_per_minute=0, aircraft_change_penalty=0,
            crew_change_penalty=0, time_limit=None,
        )
        self.assertEqual(result["result_classification"], "optimal")
        self.assertEqual(result["components"]["scheduled_operating_cost"], 0)
        self.assertTrue(result["schedule"].status.eq("Scheduled").all())


if __name__ == "__main__":
    unittest.main()
