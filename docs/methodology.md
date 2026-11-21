# Methodology

The experiment compares three initial MILP objective/feasibility variants on the same flights, fleet, crew, costs, and actual minimum turnaround. After users select disruptions, the same shifted times and unavailable/cancelled resource set are passed to each independent recovery MILP. Every recovery uses the actual turnaround and the same cancellation and assignment-change penalty defaults.

For each strategy, report initial and final operating cost, change in operating cost, recovery penalties, cancellations, aircraft reassignment, crew changes, use, and solver status. Total operational cost means final scheduled operating cost plus the modeled recovery penalties; adding initial cost as well would double-count operations. Results may favor any strategy or tie. A single chosen disruption is an illustrative scenario, not a statistically general claim; broader research should sample many disruptions and report distributions or averages.

The flexible strategy directly values aircraft connection slack. The buffered strategy instead imposes extra turnaround feasibility. This separates a slack preference from a hard reserve. Recovery returns to common operational rules so results reflect how those initial choices fare after the same event.

## Demo experiment protocol

`python experiments/run_experiments.py` executes nine fixed scenarios against Normal, Buffered, and Flexible initial schedules using `data/demo_*.csv`. Every strategy receives the same disrupted flight times, cancellation selection, unavailable resources, actual recovery turnaround, cancellation penalty, and reassignment weights. Initial Buffered and Flexible settings affect only their initial MILPs; every recovery MILP uses the Normal recovery formulation. Scenarios cover no disruption, F001 delayed 30/60/120 minutes, F003 cancellation, A002 unavailable, C001 unavailable, a delay plus aircraft disruption, and combined aircraft and crew unavailability.

Each scenario/strategy pair is kept in the output, including an explicit initial infeasibility, recovery infeasibility, or solver error. A pair is optimal only when both solves are proven optimal; it is feasible when both have usable schedules but at least one is not proven optimal. Failed pairs are retained but are not scored as successful recoveries. The result CSV includes parameters, solver statuses/runtime, dependency/platform versions, cost components, coverage and assignment metrics, and average initial/recovered connection slack computed with the configured turnaround for each respective solve. `python experiments/analyze_results.py` produces strategy-level means and per-scenario operating cost differences, plus chart HTML files. Primary strategy comparisons use common successful scenarios; per-strategy success/failure counts are reported separately, and strategy-specific averages are supplementary. The analysis is descriptive: it has nine illustrative cases from one small demo dataset, not a statistical sample supporting a universal strategy ranking.

## Equal-cost optima and tie-break replicates

A MILP can have many optimal solutions. In the demo data all crew members have the same hourly rate, so many crew assignments have identical cost; aircraft routings can also tie. Without control, CBC picks one of them based on internal order, and that choice changed with the row order of the input files. Recovery charges a penalty for every change from the initial assignment, so an arbitrary initial crew choice changed the recovery penalties and could reverse the strategy ranking.

Every solve therefore has two lexicographic stages. Stage one minimizes the stated objective. Stage two adds the constraint `primary objective <= stage-one value (+ 1e-6 relative tolerance)` and minimizes `Σ w_ia x_ia + Σ w_ic y_ic`, where each weight lies in [1, 2) and is derived from a SHA-256 hash of the tie-break seed and the flight and resource IDs. Inputs are also sorted by ID before the model is built. The selected schedule is therefore still optimal for the primary objective, and identical data always produce the identical schedule.

Any single tie-break rule is still one arbitrary choice among equal-cost optima. The experiment runner therefore repeats the full scenario matrix for seeds 0 to 9. Within a seed, all three strategies and all recoveries use the same rule. The analysis treats each scenario-seed combination as one comparison case and reports, per strategy and per scenario, the mean, minimum, and maximum across seeds (`tie_break_spread_by_strategy.csv`, `tie_break_spread_by_scenario.csv`) and how often each strategy had the lowest total recovery cost (`lowest_total_cost_counts.csv`). A difference that holds for every seed is attributed to the strategy; one that changes sign across seeds is reported as dependent on the choice among equal-cost optima. The interface uses seed 0.

Dependency and platform versions are recorded; timing may vary. Runtime is measured around the solver call. Strategy optimization scores are not included in operating costs or recovery penalty totals.

## Metric definitions

| Metric | Definition |
|---|---|
| Initial operating cost | Aircraft plus crew block-hour cost in the initial schedule. |
| Recovered operating cost | Aircraft plus crew block-hour cost in the recovered schedule, using the externally shifted fixed times. |
| Operating cost change | Recovered operating cost minus initial operating cost; it can be negative. |
| Cancellation penalty | Priority-weighted configured penalty for cancelled flights. |
| Aircraft / crew reassignment penalty | Configured objective weight charged for assignment changes from the initial schedule. |
| Other recovery penalties | Any separately modeled recovery penalty not in the preceding categories; zero in the current model. |
| Total modeled recovery cost | Recovered operating cost plus all recovery penalties. It excludes initial operating cost and strategy preference scores. |
| Operated / cancelled flights | Counts by final recovery status. An explicit cancellation is in the cancelled count. |
| Unexpectedly uncovered flights | Flight IDs expected in the input but absent from the recovered schedule, or unexpected IDs present. An accepted solver output is checked for complete coverage; failed solves have no valid schedule metrics. |
| Externally imposed delay | Count of selected flights and sum of selected delay minutes. |
| Operated externally delayed / cancelled externally delayed | Counts of externally delayed flight IDs partitioned by whether they operated or were cancelled. |
| Recovery-added delay | Zero minutes because flight retiming is not modeled. |
| Aircraft changes / crew changes | Operated flights whose respective assignment differs from the initial assignment. |
| Unique changed flights | Size of the union of aircraft-changed and crew-changed flight IDs, so a flight changed in both categories is counted once. |
| Connection gap / slack | Next departure minus prior arrival; slack equals gap minus the configured turnaround used for that solve. Connection averages are over compatible consecutive flights assigned to the same aircraft. |
| Solver runtime | Wall-clock seconds around the solver invocation; it excludes preparation and report generation. |
| Strategy optimization score | Flexible's initial-schedule slack-shortfall score. It is a preference term, not an operating or recovery cost. |
