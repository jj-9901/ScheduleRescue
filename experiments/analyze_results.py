"""Summarize experiment CSVs and generate shareable comparison charts."""
from pathlib import Path
import sys

import pandas as pd
import plotly.express as px

ROOT = Path(__file__).resolve().parents[1]


def analyze(path=None):
    source = Path(path) if path else ROOT / "experiments/results/experiment_results.csv"
    data = pd.read_csv(source)
    output = source.parent / "analysis"
    output.mkdir(parents=True, exist_ok=True)
    successful = data[data.solver_status == "Optimal"].copy()
    summaries = successful.groupby("strategy", as_index=False).agg(
        scenario_count=("scenario_id", "count"),
        initial_operating_cost=("initial_operating_cost", "mean"),
        recovered_operating_cost=("recovered_operating_cost", "mean"),
        recovery_penalties=("recovery_penalties", "mean"),
        total_modeled_recovery_cost=("total_modeled_recovery_cost", "mean"),
        cancelled_flights=("cancelled_flights", "mean"),
        operated_delayed_flights=("operated_delayed_flights", "mean"),
        cancelled_externally_delayed_flights=("cancelled_externally_delayed_flights", "mean"),
        aircraft_reassignment_count=("aircraft_reassignment_count", "mean"),
        crew_reassignment_count=("crew_reassignment_count", "mean"),
        unique_changed_flight_count=("unique_changed_flight_count", "mean"),
        initial_connection_slack=("initial_connection_slack", "mean"),
        recovered_connection_slack=("recovered_connection_slack", "mean"))
    summaries.to_csv(output / "strategy_comparison.csv", index=False)
    # Per-scenario results and differences remain visible; no average is used
    # to imply that a strategy wins in every case.
    operating = successful.pivot(index="scenario_id", columns="strategy", values="recovered_operating_cost")
    total = successful.pivot(index="scenario_id", columns="strategy", values="total_modeled_recovery_cost")
    differences = pd.DataFrame(index=operating.index)
    for strategy in operating.columns:
        differences[f"{strategy}_operating_cost_delta"] = operating[strategy] - operating.min(axis=1)
        differences[f"{strategy}_total_recovery_cost_delta"] = total[strategy] - total.min(axis=1)
    differences.to_csv(output / "scenario_cost_differences.csv")
    successful.to_csv(output / "successful_scenario_metrics.csv", index=False)
    data[data.solver_status != "Optimal"].to_csv(output / "failed_solves.csv", index=False)
    charts = [
        ("initial_vs_recovered_cost.html", ["initial_operating_cost", "recovered_operating_cost"], "Operating costs by scenario"),
        ("cancellations.html", ["cancelled_flights"], "Cancelled flights"),
        ("assignment_changes.html", ["aircraft_reassignment_count", "crew_reassignment_count", "unique_changed_flight_count"], "Assignment changes"),
        ("delay_comparison.html", ["externally_imposed_delay_flights", "externally_imposed_delay_minutes", "operated_delayed_flights", "cancelled_externally_delayed_flights", "recovery_added_delay_minutes"], "External and recovery delay metrics"),
    ]
    long = successful.melt(id_vars=["scenario_id", "strategy"], var_name="metric", value_name="value")
    for filename, metrics, title in charts:
        frame = long[long.metric.isin(metrics)]
        fig = px.bar(frame, x="scenario_id", y="value", color="strategy", barmode="group", facet_col="metric", title=title)
        fig.write_html(output / filename, include_plotlyjs="cdn")
    winners = []
    for scenario_id, group in successful.groupby("scenario_id"):
        best = group.total_modeled_recovery_cost.min()
        names = ", ".join(group.loc[group.total_modeled_recovery_cost == best, "strategy"].tolist())
        winners.append(f"- **{scenario_id}:** {names} had the lowest total modeled recovery cost ({best:,.2f}).")
    explanation = [
        "# Experiment interpretation",
        "",
        "These results cover nine illustrative scenarios on one small demo dataset. They do not show that one strategy is always superior.",
        "The winner lines compare total modeled recovery cost (recovered operating cost plus recovery penalties). Operating costs and penalties remain separate in the CSV and strategy table; a lower operating cost can coincide with higher reassignment or cancellation penalties.",
        "",
        "## Lowest total modeled recovery cost by scenario",
        "",
        *winners,
        "",
        "Use `scenario_cost_differences.csv` to compare both operating-cost and total-recovery-cost differences within each scenario. Strategy-specific initial preference scores are not included in these monetary comparisons."
    ]
    (output / "interpretation.md").write_text("\n".join(explanation) + "\n", encoding="utf-8")
    print(f"Analyzed {len(data)} rows ({len(successful)} optimal, {len(data)-len(successful)} failed or not run).")
    print(summaries.to_string(index=False))
    print(f"Analysis files: {output}")
    print("Interpretation written to:", output / "interpretation.md")
    print("Per-scenario cost differences versus the lowest strategy cost in that scenario (operating and total modeled recovery cost separately):")
    print(differences.to_string())
    return summaries, differences


if __name__ == "__main__":
    analyze(sys.argv[1] if len(sys.argv) > 1 else None)
