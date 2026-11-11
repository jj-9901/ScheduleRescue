# Experiment interpretation

These results cover nine illustrative scenarios on one small demo dataset. They do not show that one strategy is always superior.
The winner lines compare total modeled recovery cost (recovered operating cost plus recovery penalties). Operating costs and penalties remain separate in the CSV and strategy table; a lower operating cost can coincide with higher reassignment or cancellation penalties.

## Lowest total modeled recovery cost by scenario

- **S01_none:** normal had the lowest total modeled recovery cost (6,660.00).
- **S02_F001_30m:** buffered, flexible had the lowest total modeled recovery cost (6,760.00).
- **S03_F001_60m:** normal had the lowest total modeled recovery cost (106,100.00).
- **S04_F001_120m:** normal had the lowest total modeled recovery cost (106,100.00).
- **S05_F003_cancel:** normal had the lowest total modeled recovery cost (205,600.00).
- **S06_A002_unavailable:** flexible had the lowest total modeled recovery cost (205,090.00).
- **S07_C001_unavailable:** normal had the lowest total modeled recovery cost (6,660.00).
- **S08_F001_30m_A002:** flexible had the lowest total modeled recovery cost (205,090.00).
- **S09_A002_C001:** flexible had the lowest total modeled recovery cost (205,090.00).

Use `scenario_cost_differences.csv` to compare both operating-cost and total-recovery-cost differences within each scenario. Strategy-specific initial preference scores are not included in these monetary comparisons.
