# Assumptions and limitations

- All timestamps are local-naive values in one common time zone. Time-zone conversion and daylight-saving transitions are not modeled.
- A flight's departure and arrival are fixed in initial planning. User-entered external delay shifts both times by the same duration for recovery.
- An aircraft must start at its initial location and availability time. A flight's required type is matched exactly unless either side uses `ANY`.
- Consecutive aircraft flights must share an airport and satisfy the selected turnaround. Each aircraft follows one continuous chronological route through the planning horizon, with any number of connected flights; disconnected paths are prohibited so an aircraft cannot reset to its initial location mid-horizon.
- Crew must start from its declared initial airport, match the required aircraft type (or `ANY`), and have enough connection/rest time and availability. A crew member is not allowed to overlap flights because route arcs enforce chronological connections.
- Crew duty is approximated by total assigned block hours over the planning horizon. Rest is a minimum connection gap; there are no daily duty windows, pairings, deadheading, base-return, qualification expiry, or regulatory regime-specific rules.
- Each flight defaults to requiring one crew member. Required crew must be available from the supplied finite pool or the model becomes infeasible/cancels flights in recovery.
- Aircraft and crew costs are hourly block-time rates. Fuel, airport fees, passenger reaccommodation, delay compensation, maintenance, and cancellation economics are omitted.
- Flexible slack is evaluated on aircraft route connections, not crew connections. Buffered reserves aircraft turnaround time.
- Recovery has fixed flight times after external disruption; it cannot optimize added delay.
- Connection gap is next departure minus previous arrival; connection slack is the gap minus the required aircraft turnaround. A 60-minute gap with a 45-minute turnaround therefore has 15 minutes of slack.
- An externally imposed delay is the selected input duration. Operated externally delayed flights exclude flights that are cancelled. Cancelled externally delayed flights are reported separately. Recovery-added delay is zero because retiming is not a decision in this model.
- Total modeled recovery cost equals recovered operating cost plus cancellation penalties, aircraft reassignment penalties, crew reassignment penalties, and any other recovery penalties. Initial cost change is reported for context but is not added as another cost. The Flexible optimization score is separate from cash-like operating costs and recovery penalties.
- Schedule coverage counts operated, cancelled, and unexpectedly uncovered flights. Solver failures do not produce valid schedule metrics.
- Penalties are illustrative and depend on user cost units; changing weights can change assignments. Do not interpret them as industry-calibrated values.
- Airport closures and window-specific restrictions have a solver API representation for resources, but no airport closure UI is provided.
