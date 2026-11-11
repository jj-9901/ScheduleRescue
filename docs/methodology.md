# Methodology

The experiment compares three initial MILP objective/feasibility variants on the same flights, fleet, crew, costs, and actual minimum turnaround. After users select disruptions, the same shifted times and unavailable/cancelled resource set are passed to each independent recovery MILP. Every recovery uses the actual turnaround and the same cancellation and assignment-change penalty defaults.

For each strategy, report initial and final operating cost, change in operating cost, recovery penalties, cancellations, aircraft reassignment, crew changes, use, and solver status. Total operational cost means final scheduled operating cost plus the modeled recovery penalties; adding initial cost as well would double-count operations. Results may favor any strategy or tie. A single chosen disruption is an illustrative scenario, not a statistically general claim; broader research should sample many disruptions and report distributions or averages.

The flexible strategy directly values aircraft connection slack. The buffered strategy instead imposes extra turnaround feasibility. This separates a slack preference from a hard reserve. Recovery returns to common operational rules so results reflect how those initial choices fare after the same event.

## Demo experiment protocol

`python experiments/run_experiments.py` executes nine fixed scenarios against Normal, Buffered, and Flexible initial schedules using `data/demo_*.csv`. Every strategy receives the same disrupted flight times, cancellation selection, unavailable resources, actual recovery turnaround, cancellation penalty, and reassignment weights. Initial Buffered and Flexible settings affect only their initial MILPs; every recovery MILP uses the Normal recovery formulation. Scenarios cover no disruption, F001 delayed 30/60/120 minutes, F003 cancellation, A002 unavailable, C001 unavailable, a delay plus aircraft disruption, and combined aircraft and crew unavailability.

Each scenario/strategy pair is kept in the output, including an explicit initial infeasibility, recovery infeasibility, or solver error. An infeasible initial plan is not silently substituted or dropped. The result CSV includes parameters, solver statuses/runtime, dependency/platform versions, cost components, coverage and assignment metrics, and average initial/recovered connection slack. `python experiments/analyze_results.py` produces strategy-level means and per-scenario operating cost differences, plus chart HTML files. The analysis is descriptive: it has nine illustrative cases from one small demo dataset, not a statistical sample supporting a universal strategy ranking.

PuLP and CBC can return different assignments when multiple solutions have equal objective value. Dependency and platform versions are recorded; exact tie-breaking and timing may vary. Runtime is measured around the solver call. Strategy optimization scores are not included in operating costs or recovery penalty totals.

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
| Connection gap / slack | Next departure minus prior arrival; slack equals gap minus actual turnaround. Connection averages are over compatible consecutive flights assigned to the same aircraft. |
| Solver runtime | Wall-clock seconds around the solver invocation; it excludes preparation and report generation. |
| Strategy optimization score | Flexible's initial-schedule slack-shortfall score. It is a preference term, not an operating or recovery cost. |
