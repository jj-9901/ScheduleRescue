"""Summarize experiment outcomes and compare strategies on common scenarios."""
from pathlib import Path
import sys

import pandas as pd
import plotly.express as px

ROOT = Path(__file__).resolve().parents[1]
USABLE = {"optimal", "feasible_limit"}
METRICS = ["initial_operating_cost", "recovered_operating_cost", "recovery_penalties",
          "total_modeled_recovery_cost", "cancelled_flights", "operated_delayed_flights",
          "cancelled_externally_delayed_flights", "aircraft_reassignment_count",
          "crew_reassignment_count", "unique_changed_flight_count", "initial_connection_slack",
          "recovered_connection_slack"]


def _status(series):
    return series.fillna("failed").astype(str).replace(
        {"Optimal": "optimal", "FeasibleLimit": "feasible_limit", "Infeasible": "infeasible", "Failed": "failed"})


def _outcomes(data):
    initial = _status(data.get("initial_result_classification", pd.Series("optimal", index=data.index)))
    recovery = _status(data.get("recovery_result_classification", data.get("result_classification", data.get("solver_status", pd.Series("failed", index=data.index)))))
    if "pair_outcome" in data:
        outcome = data.pair_outcome.fillna("").astype(str)
        # Validate explicitly stored category against individual solver classifications.
        expected = pd.Series(index=data.index, dtype=object)
        expected.loc[initial.eq("optimal") & recovery.eq("optimal")] = "optimal_pair"
        expected.loc[initial.isin(USABLE) & recovery.isin(USABLE) & expected.isna()] = "feasible_pair"
        expected.loc[expected.isna()] = "failed_pair"
        if outcome.tolist() != expected.tolist():
            raise ValueError("Experiment pair_outcome disagrees with initial/recovery classifications.")
    else:
        outcome = pd.Series("failed_pair", index=data.index)
        outcome.loc[initial.isin(USABLE) & recovery.isin(USABLE)] = "feasible_pair"
        outcome.loc[initial.eq("optimal") & recovery.eq("optimal")] = "optimal_pair"
    return initial, recovery, outcome


def _summary(frame):
    present = [metric for metric in METRICS if metric in frame]
    if not len(frame):
        return pd.DataFrame(columns=["strategy", "scenario_count", *present])
    return frame.groupby("strategy", as_index=False).agg(
        scenario_count=("scenario_id", "count"), **{metric: (metric, "mean") for metric in present})


def analyze(path=None):
    source = Path(path) if path else ROOT / "experiments/results/experiment_results.csv"
    data = pd.read_csv(source)
    output = source.parent / "analysis"
    output.mkdir(parents=True, exist_ok=True)
    initial, recovery, outcome = _outcomes(data)
    data = data.copy()
    data["analysis_outcome"] = outcome
    category_counts = outcome.value_counts().reindex(["optimal_pair", "feasible_pair", "failed_pair"], fill_value=0)
    if int(category_counts.sum()) != len(data):
        raise ValueError(f"Outcome category totals ({int(category_counts.sum())}) do not equal input rows ({len(data)}).")
    category_summary = pd.DataFrame([{"outcome": name, "count": int(category_counts[name])} for name in category_counts.index])
    category_summary.to_csv(output / "outcome_counts.csv", index=False)
    for category in category_counts.index:
        data[outcome == category].drop(columns=["analysis_outcome"]).to_csv(output / f"{category}.csv", index=False)
    # Keep the legacy failed export path, with the required pair-level reason.
    failed = data[outcome == "failed_pair"].copy()
    if "pair_failure_reason" not in failed:
        failed["pair_failure_reason"] = "A solve did not produce a usable schedule."
    failed.to_csv(output / "failed_solves.csv", index=False)
    optimal = data[outcome == "optimal_pair"].copy()
    feasible = data[outcome == "feasible_pair"].copy()
    usable = data[outcome.isin(["optimal_pair", "feasible_pair"])].copy()

    strategies = sorted(data.strategy.dropna().unique()) if "strategy" in data else []
    strategy_counts = []
    for strategy in strategies:
        subset = data[data.strategy == strategy]
        strategy_counts.append({"strategy": strategy,
            "success_count": int(subset.analysis_outcome.isin(["optimal_pair", "feasible_pair"]).sum()),
            "failure_count": int(subset.analysis_outcome.eq("failed_pair").sum()),
            "optimal_pair_count": int(subset.analysis_outcome.eq("optimal_pair").sum()),
            "feasible_pair_count": int(subset.analysis_outcome.eq("feasible_pair").sum())})
    pd.DataFrame(strategy_counts).to_csv(output / "strategy_success_counts.csv", index=False)

    if strategies and "scenario_id" in usable:
        counts = usable.groupby("scenario_id").strategy.nunique()
        common_ids = sorted(counts[counts == len(strategies)].index)
        common = usable[usable.scenario_id.isin(common_ids)]
        # Guard against duplicate/missing strategy rows for a scenario.
        expected_pairs = len(common_ids) * len(strategies)
        if len(common) != expected_pairs:
            raise ValueError("Common comparison set has duplicate strategy/scenario rows.")
    else:
        common_ids, common = [], usable.iloc[0:0]
    common_summary = _summary(common)
    common_summary.insert(1, "common_scenario_count", len(common_ids))
    common_summary.to_csv(output / "strategy_comparison.csv", index=False)
    specific = _summary(usable)
    specific.to_csv(output / "strategy_specific_averages.csv", index=False)
    common.to_csv(output / "common_successful_scenario_metrics.csv", index=False)
    usable.to_csv(output / "successful_scenario_metrics.csv", index=False)

    if common_ids:
        operating = common.pivot(index="scenario_id", columns="strategy", values="recovered_operating_cost")
        total = common.pivot(index="scenario_id", columns="strategy", values="total_modeled_recovery_cost")
        differences = pd.DataFrame(index=operating.index)
        for strategy in operating.columns:
            differences[f"{strategy}_operating_cost_delta"] = operating[strategy] - operating.min(axis=1)
            differences[f"{strategy}_total_recovery_cost_delta"] = total[strategy] - total.min(axis=1)
        differences.to_csv(output / "scenario_cost_differences.csv")
        long = common.melt(id_vars=["scenario_id", "strategy"], var_name="metric", value_name="value")
        charts = [("initial_vs_recovered_cost.html", ["initial_operating_cost", "recovered_operating_cost"], "Operating costs on common successful scenarios"),
            ("cancellations.html", ["cancelled_flights"], "Cancelled flights on common successful scenarios"),
            ("assignment_changes.html", ["aircraft_reassignment_count", "crew_reassignment_count", "unique_changed_flight_count"], "Assignment changes on common successful scenarios"),
            ("delay_comparison.html", ["externally_imposed_delay_flights", "externally_imposed_delay_minutes", "operated_delayed_flights", "cancelled_externally_delayed_flights", "recovery_added_delay_minutes"], "Delay metrics on common successful scenarios")]
        for filename, metrics, title in charts:
            chart_frame = long[long.metric.isin(metrics)]
            if not chart_frame.empty:
                px.bar(chart_frame, x="scenario_id", y="value", color="strategy", barmode="group", facet_col="metric", title=title).write_html(output / filename, include_plotlyjs="cdn")
        winners = []
        for scenario_id, group in common.groupby("scenario_id"):
            best = group.total_modeled_recovery_cost.min()
            names = ", ".join(group.loc[group.total_modeled_recovery_cost == best, "strategy"].tolist())
            winners.append(f"- **{scenario_id}:** {names} had the lowest total modeled recovery cost ({best:,.2f}).")
        differences_text = differences.to_string()
    else:
        differences = pd.DataFrame()
        differences.to_csv(output / "scenario_cost_differences.csv")
        winners = ["No common successful scenarios are available; no cross-strategy averages or cost comparisons were calculated."]
        differences_text = "No common successful scenarios."
    explanation = ["# Experiment interpretation", "",
        f"Input rows: {len(data)}. Optimal pairs: {int(category_counts.optimal_pair)}. Feasible pairs: {int(category_counts.feasible_pair)}. Failed pairs: {int(category_counts.failed_pair)}.",
        f"Primary cross-strategy comparisons use {len(common_ids)} scenarios where every strategy produced usable initial and recovery schedules. The strategies receive the same scenario disruptions and common recovery settings.",
        "Strategy-specific averages in `strategy_specific_averages.csv` use each strategy's own successful subset and are supplementary; compare them cautiously because the scenario subsets can differ.",
        "These illustrative results do not show that one strategy is universally superior. Cost differences compare modeled operating cost and recovery penalties.", "",
        "## Lowest total modeled recovery cost on the common set", "", *winners,
        "", "See `scenario_cost_differences.csv` for within-scenario deltas. Strategy preference scores are not monetary recovery costs."]
    (output / "interpretation.md").write_text("\n".join(explanation) + "\n", encoding="utf-8")
    print(f"Analyzed {len(data)} rows: {int(category_counts.optimal_pair)} optimal pairs, {int(category_counts.feasible_pair)} feasible pairs, {int(category_counts.failed_pair)} failed pairs.")
    print(f"Per-strategy success/failure counts: {output / 'strategy_success_counts.csv'}")
    print(f"Common successful scenario count: {len(common_ids)}")
    if common_ids:
        print("Cross-strategy averages on the common set:")
        print(common_summary.to_string(index=False))
    else:
        print("No common comparison set is available; no cross-strategy averages generated.")
    print("Strategy-specific supplementary averages:")
    print(specific.to_string(index=False))
    print(f"Analysis files: {output}")
    return common_summary, differences


if __name__ == "__main__":
    analyze(sys.argv[1] if len(sys.argv) > 1 else None)
