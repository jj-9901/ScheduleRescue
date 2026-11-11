"""Scenario-aware schedule metrics and cost accounting."""
from __future__ import annotations

import pandas as pd


def settings_match(saved, current):
    """Whether the controls still describe the solve currently displayed."""
    return saved == current


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
