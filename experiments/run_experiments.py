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

def _pair_outcome(initial_classification, recovery_classification):
    """Return the mutually exclusive outcome of the initial/recovery solve pair."""
    usable = {"optimal", "feasible_limit"}
    if initial_classification not in usable:
        return "failed_pair", f"Initial solve was {initial_classification}; recovery was not attempted."
    if recovery_classification not in usable:
        return "failed_pair", f"Recovery solve was {recovery_classification}."
    if initial_classification == recovery_classification == "optimal":
        return "optimal_pair", "Both initial and recovery solves were proven optimal."
    if initial_classification == "feasible_limit" and recovery_classification == "feasible_limit":
        return "feasible_pair", "Both solves produced feasible schedules; optimality was not proven for either."
    limited = "initial" if initial_classification == "feasible_limit" else "recovery"
    return "feasible_pair", f"Both solves produced usable schedules; {limited} solve optimality was not proven."


def _classification(result):
    return result.get("result_classification", "optimal" if result.get("status") == "Optimal" else "failed")


def _pair_detail(initial_classification, recovery_classification):
    if initial_classification not in {"optimal", "feasible_limit"}:
        return f"initial_{initial_classification}"
    if recovery_classification not in {"optimal", "feasible_limit"}:
        return f"recovery_{recovery_classification}"
    return f"initial_{initial_classification}_recovery_{recovery_classification}"


def _validated_parameters(parameters, supported, label):
    unsupported = set(parameters) - set(supported)
    if unsupported:
        raise ValueError(f"Unsupported {label} experiment configuration: {sorted(unsupported)}")
    return dict(parameters)


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
    initial_parameters = _validated_parameters(INITIAL_PARAMETERS,
        {"turnaround_minutes", "crew_rest_minutes", "buffer_minutes", "flexibility_target_minutes", "flexibility_penalty_per_minute"}, "initial")
    recovery_parameters = _validated_parameters(RECOVERY_PARAMETERS,
        {"turnaround_minutes", "crew_rest_minutes", "cancellation_penalty", "aircraft_change_penalty", "crew_change_penalty", "recovery_strategy"}, "recovery")
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
    operating_cost_weights = {
        "aircraft": dict(zip(aircraft.aircraft_id, aircraft.cost_per_hour)),
        "crew": dict(zip(crew.crew_id, crew.cost_per_hour)),
    }
    for strategy in STRATEGIES:
        try:
            initial = solve_schedule(flights, aircraft, crew, strategy=strategy,
                                     **initial_parameters)
        except Exception as exc:
            initial = {"status": "Error", "result_classification": "failed", "solver_message": str(exc), "solver_termination_reason": str(exc), "schedule": pd.DataFrame(), "components": {}}
        for scenario in SCENARIOS:
            row = {"scenario_id": scenario["scenario_id"], "strategy": strategy,
                   "scenario_parameters": json.dumps(scenario, sort_keys=True),
                   "initial_parameters": json.dumps({**initial_parameters, "strategy": strategy}, sort_keys=True),
                   "recovery_parameters": json.dumps(recovery_parameters, sort_keys=True),
                   "initial_solve_parameters": json.dumps(initial.get("solve_parameters", {
                       **initial_parameters, "strategy": strategy, "operating_cost_weights": operating_cost_weights,
                       "time_limit": 30}), sort_keys=True),
                   "recovery_solve_parameters": "",
                   "dependency_versions": json.dumps(_versions(), sort_keys=True),
                   "initial_solver_status": initial.get("status", "Unknown"),
                   "initial_result_classification": initial.get("result_classification", "failed"),
                   "initial_solver_termination_reason": initial.get("solver_termination_reason", ""),
                   "initial_best_bound": initial.get("best_bound"),
                   "initial_optimality_gap": initial.get("optimality_gap"),
                   "initial_solver_runtime_seconds": initial.get("solver_runtime_seconds"),
                   "solver_status": "not_run_initial", "result_classification": "not_run_initial",
                   "recovery_result_classification": "not_run_initial",
                   "pair_outcome": "", "pair_status_detail": "", "pair_failure_reason": "",
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
            initial_classification = _classification(initial)
            row["initial_result_classification"] = initial_classification
            if initial_classification not in {"optimal", "feasible_limit"}:
                row["solver_status"] = "not_run_initial"
                row["result_classification"] = "not_run_initial"
                row["pair_outcome"], row["pair_failure_reason"] = _pair_outcome(initial_classification, "not_run_initial")
                row["pair_status_detail"] = _pair_detail(initial_classification, "not_run_initial")
                row["solver_termination_reason"] = initial.get("solver_termination_reason", initial.get("solver_message", ""))
                row["recovery_error"] = "Recovery not attempted because initial solve produced no usable schedule."
                rows.append(row)
                continue
            disrupted = _apply_delays(flights, scenario["delays"])
            assignment = dict(zip(initial["schedule"].flight_id, initial["schedule"].assigned_aircraft))
            crew_assignment = {r.flight_id: [x for x in str(r.assigned_crew).split(";") if x]
                               for r in initial["schedule"].itertuples()}
            recovery_call_parameters = {}
            try:
                recovery_call_parameters = dict(
                    turnaround_minutes=recovery_parameters["turnaround_minutes"],
                    crew_rest_minutes=recovery_parameters["crew_rest_minutes"],
                    unavailable_aircraft=scenario["aircraft"], unavailable_crew=scenario["crew"],
                    cancelled_flights=scenario["cancel"], original_assignment=assignment,
                    original_crew_assignment=crew_assignment, allow_cancellation=True,
                    strategy=recovery_parameters["recovery_strategy"],
                    cancellation_penalty=recovery_parameters["cancellation_penalty"],
                    aircraft_change_penalty=recovery_parameters["aircraft_change_penalty"],
                    crew_change_penalty=recovery_parameters["crew_change_penalty"])
                row["recovery_solve_parameters"] = json.dumps(recovery_call_parameters, sort_keys=True)
                recovered = solve_schedule(disrupted, aircraft, crew, **recovery_call_parameters)
                row["recovery_solve_parameters"] = json.dumps(recovered.get("solve_parameters", {
                    **recovery_call_parameters, "operating_cost_weights": operating_cost_weights,
                    "time_limit": 30}), sort_keys=True)
            except Exception as exc:
                recovered = {"status": "Error", "result_classification": "failed", "solver_message": str(exc), "solver_termination_reason": str(exc), "schedule": pd.DataFrame(), "components": {}}
            if not recovered.get("solve_parameters"):
                row["recovery_solve_parameters"] = json.dumps({
                    **recovery_call_parameters, "operating_cost_weights": operating_cost_weights,
                    "time_limit": 30}, sort_keys=True)
            row["solver_status"] = recovered.get("status", "Unknown")
            recovery_classification = _classification(recovered)
            row["recovery_result_classification"] = recovery_classification
            row["result_classification"] = recovery_classification
            row["pair_outcome"], row["pair_failure_reason"] = _pair_outcome(initial_classification, recovery_classification)
            row["pair_status_detail"] = _pair_detail(initial_classification, recovery_classification)
            row["solver_termination_reason"] = recovered.get("solver_termination_reason", recovered.get("solver_message", ""))
            row["best_bound"] = recovered.get("best_bound")
            row["optimality_gap"] = recovered.get("optimality_gap")
            row["solver_runtime_seconds"] = recovered.get("solver_runtime_seconds")
            row["recovery_error"] = recovered.get("solver_message", "")
            if row["pair_outcome"] in {"optimal_pair", "feasible_pair"}:
                metrics = compare_schedules(initial["schedule"], recovered["schedule"], initial, recovered,
                    externally_imposed_delays=scenario["delays"], expected_flight_ids=flights.flight_id,
                    turnaround_minutes=recovery_parameters["turnaround_minutes"])
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
            else:
                row["solver_status"] = recovery_classification
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
