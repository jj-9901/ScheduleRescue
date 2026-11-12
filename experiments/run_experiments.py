"""Run the fixed demo experiment matrix and save one row per scenario/strategy."""
from __future__ import annotations

import json
import platform
import subprocess
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
    cbc = pulp.PULP_CBC_CMD().available()
    try:
        cbc_version = subprocess.run([cbc, "-version"], capture_output=True, text=True,
                                      timeout=3, check=False).stdout.strip().splitlines()[:2]
    except (OSError, subprocess.TimeoutExpired):
        cbc_version = ["unavailable"]
    return {"python": platform.python_version(), "pandas": pd.__version__,
            "pulp": pulp.__version__, "available_solvers": pulp.listSolvers(onlyAvailable=True),
            "cbc_version": cbc_version, "platform": platform.platform()}


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
                   "initial_result_classification": initial.get("result_classification", "failed"),
                   "initial_solver_termination_reason": initial.get("solver_termination_reason", ""),
                   "initial_best_bound": initial.get("best_bound"),
                   "initial_optimality_gap": initial.get("optimality_gap"),
                   "initial_solver_runtime_seconds": initial.get("solver_runtime_seconds"),
                   "solver_status": "not_run_initial", "result_classification": "not_run_initial",
                   "recovery_result_classification": "not_run_initial",
                   "solver_termination_reason": "", "best_bound": None, "optimality_gap": None,
                   "solver_runtime_seconds": None,
                   "initial_operating_cost": None, "recovered_operating_cost": None,
                   "recovery_penalties": None, "cancellation_penalty": None,
                   "aircraft_reassignment_penalty": None, "crew_reassignment_penalty": None,
                   "strategy_optimization_score": None, "cancelled_flights": None,
                   "operated_delayed_flights": None, "cancelled_externally_delayed_flights": None,
                   "externally_imposed_delay_flights": len(scenario["delays"]),
                   "externally_imposed_delay_minutes": sum(scenario["delays"].values()),
                   "recovery_added_delay_minutes": 0,
                   "total_delay_minutes": sum(scenario["delays"].values()),
                   "total_modeled_recovery_cost": None,
                   "aircraft_reassignment_count": None, "crew_reassignment_count": None,
                   "unique_changed_flight_count": None, "initial_connection_slack": None,
                   "recovered_connection_slack": None, "initial_error": initial.get("solver_message", ""),
                   "recovery_error": ""}
            if initial.get("result_classification", "optimal" if initial.get("status") == "Optimal" else "failed") not in {"optimal", "feasible_limit"}:
                row["solver_status"] = "not_run_initial"
                row["result_classification"] = "not_run_initial"
                row["solver_termination_reason"] = initial.get("solver_termination_reason", initial.get("solver_message", ""))
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
            recovery_classification = recovered.get("result_classification", "optimal" if recovered.get("status") == "Optimal" else "failed")
            row["recovery_result_classification"] = recovery_classification
            initial_classification = initial.get("result_classification", "optimal" if initial.get("status") == "Optimal" else "failed")
            row["result_classification"] = (
                "feasible_limit" if "feasible_limit" in {initial_classification, recovery_classification}
                else recovery_classification)
            row["solver_status"] = row["result_classification"]
            row["solver_termination_reason"] = recovered.get("solver_termination_reason", recovered.get("solver_message", ""))
            row["best_bound"] = recovered.get("best_bound")
            row["optimality_gap"] = recovered.get("optimality_gap")
            row["solver_runtime_seconds"] = recovered.get("solver_runtime_seconds")
            row["recovery_error"] = recovered.get("solver_message", "")
            if row["result_classification"] in {"optimal", "feasible_limit"}:
                metrics = compare_schedules(initial["schedule"], recovered["schedule"], initial, recovered,
                    externally_imposed_delays=scenario["delays"], expected_flight_ids=flights.flight_id,
                    turnaround_minutes=RECOVERY_PARAMETERS["turnaround_minutes"])
                row.update({"initial_operating_cost": metrics["initial_operating_cost"],
                    "recovered_operating_cost": metrics["recovery_operating_cost"],
                    "recovery_penalties": metrics["recovery_penalties"],
                    "total_modeled_recovery_cost": metrics["total_modeled_recovery_cost"],
                    "cancellation_penalty": metrics["cancellation_penalty"],
                    "aircraft_reassignment_penalty": metrics["aircraft_reassignment_penalty"],
                    "crew_reassignment_penalty": metrics["crew_reassignment_penalty"],
                    "strategy_optimization_score": initial.get("strategy_score", 0),
                    "cancelled_flights": metrics["cancelled_flights"],
                    "operated_delayed_flights": metrics["operated_externally_delayed_flights"],
                    "cancelled_externally_delayed_flights": metrics["cancelled_externally_delayed_flights"],
                    "aircraft_reassignment_count": metrics["aircraft_changed_flights"],
                    "crew_reassignment_count": metrics["crew_changed_flights"],
                    "unique_changed_flight_count": metrics["unique_changed_flights"],
                    "initial_connection_slack": connection_metrics(initial["schedule"], 45)["average_connection_slack_minutes"],
                    "recovered_connection_slack": connection_metrics(recovered["schedule"], 45)["average_connection_slack_minutes"]})
                row["solver_status"] = row["result_classification"]
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
