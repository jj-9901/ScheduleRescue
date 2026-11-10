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
- Penalties are illustrative and depend on user cost units; changing weights can change assignments. Do not interpret them as industry-calibrated values.
- Airport closures and window-specific restrictions have a solver API representation for resources, but no airport closure UI is provided.
