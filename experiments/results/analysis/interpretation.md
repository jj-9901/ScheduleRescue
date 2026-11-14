# Experiment interpretation

Input rows: 27. Optimal pairs: 27. Feasible pairs: 0. Failed pairs: 0.
Primary cross-strategy comparisons use 9 scenarios where every strategy produced usable initial and recovery schedules. The strategies receive the same scenario disruptions and common recovery settings.
Strategy-specific averages in `strategy_specific_averages.csv` use each strategy's own successful subset and are supplementary; compare them cautiously because the scenario subsets can differ.
These illustrative results do not show that one strategy is universally superior. Cost differences compare modeled operating cost and recovery penalties.

## Lowest total modeled recovery cost on the common set

- **S01_none:** normal had the lowest total modeled recovery cost (6,660.00).
- **S02_F001_30m:** buffered, flexible had the lowest total modeled recovery cost (6,760.00).
- **S03_F001_60m:** buffered, flexible had the lowest total modeled recovery cost (106,150.00).
- **S04_F001_120m:** buffered, flexible had the lowest total modeled recovery cost (106,150.00).
- **S05_F003_cancel:** normal had the lowest total modeled recovery cost (205,500.00).
- **S06_A002_unavailable:** flexible had the lowest total modeled recovery cost (204,990.00).
- **S07_C001_unavailable:** normal had the lowest total modeled recovery cost (6,660.00).
- **S08_F001_30m_A002:** flexible had the lowest total modeled recovery cost (204,990.00).
- **S09_A002_C001:** flexible had the lowest total modeled recovery cost (204,990.00).

See `scenario_cost_differences.csv` for within-scenario deltas. Strategy preference scores are not monetary recovery costs.
