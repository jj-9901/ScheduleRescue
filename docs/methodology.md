# Methodology

The experiment compares three initial MILP objective/feasibility variants on the same flights, fleet, crew, costs, and actual minimum turnaround. After users select disruptions, the same shifted times and unavailable/cancelled resource set are passed to each independent recovery MILP. Every recovery uses the actual turnaround and the same cancellation and assignment-change penalty defaults.

For each strategy, report initial and final operating cost, change in operating cost, recovery penalties, cancellations, aircraft reassignment, crew changes, use, and solver status. Total operational cost means final scheduled operating cost plus the modeled recovery penalties; adding initial cost as well would double-count operations. Results may favor any strategy or tie. A single chosen disruption is an illustrative scenario, not a statistically general claim; broader research should sample many disruptions and report distributions or averages.

The flexible strategy directly values aircraft connection slack. The buffered strategy instead imposes extra turnaround feasibility. This separates a slack preference from a hard reserve. Recovery returns to common operational rules so results reflect how those initial choices fare after the same event.
