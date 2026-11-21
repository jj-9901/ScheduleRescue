# Experiment interpretation

Input rows: 270. Optimal pairs: 270. Feasible pairs: 0. Failed pairs: 0.
Primary cross-strategy comparisons use 90 cases (scenario and tie-break seed) where every strategy produced usable initial and recovery schedules. The strategies receive the same scenario disruptions, the same tie-break seed, and common recovery settings.
Each tie-break seed selects a different, deterministic schedule among equal-cost optima. A result that changes across seeds depends on that arbitrary choice and should not be attributed to the strategy; see `tie_break_spread_by_strategy.csv` and `tie_break_spread_by_scenario.csv`.
Strategy-specific averages in `strategy_specific_averages.csv` use each strategy's own successful subset and are supplementary; compare them cautiously because the scenario subsets can differ.
These illustrative results do not show that one strategy is universally superior. Cost differences compare modeled operating cost and recovery penalties.

## Lowest total modeled recovery cost across tie-break seeds

- **S01_none:** lowest (or tied-lowest) total modeled recovery cost in buffered 0/10, flexible 0/10, normal 10/10 seed cases.
- **S02_F001_30m:** lowest (or tied-lowest) total modeled recovery cost in buffered 10/10, flexible 10/10, normal 0/10 seed cases.
- **S03_F001_60m:** lowest (or tied-lowest) total modeled recovery cost in buffered 5/10, flexible 5/10, normal 5/10 seed cases.
- **S04_F001_120m:** lowest (or tied-lowest) total modeled recovery cost in buffered 5/10, flexible 5/10, normal 5/10 seed cases.
- **S05_F003_cancel:** lowest (or tied-lowest) total modeled recovery cost in buffered 0/10, flexible 0/10, normal 10/10 seed cases.
- **S06_A002_unavailable:** lowest (or tied-lowest) total modeled recovery cost in buffered 10/10, flexible 10/10, normal 0/10 seed cases.
- **S07_C001_unavailable:** lowest (or tied-lowest) total modeled recovery cost in buffered 0/10, flexible 0/10, normal 10/10 seed cases.
- **S08_F001_30m_A002:** lowest (or tied-lowest) total modeled recovery cost in buffered 10/10, flexible 10/10, normal 0/10 seed cases.
- **S09_A002_C001:** lowest (or tied-lowest) total modeled recovery cost in buffered 10/10, flexible 10/10, normal 0/10 seed cases.

See `scenario_cost_differences.csv` for within-scenario deltas. Strategy preference scores are not monetary recovery costs.
