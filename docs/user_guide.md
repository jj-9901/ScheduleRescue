# User guide

## 1. Enter data

Choose Demo dataset, Edit manually, or Upload CSV. Flights require `flight_id,origin,destination,departure,arrival`; optional fields are `aircraft_type_required,required_crew_count,priority`. Aircraft require `aircraft_id,initial_location,available_from,cost_per_hour`; optional `aircraft_type` defaults to `ANY`. Crew requires `crew_id,initial_location,available_from,eligible_aircraft_types,max_work_hours,cost_per_hour`. List eligible types with semicolons (for example `A;B`); `ANY` qualifies for every type.

The CSV templates use the current demo schema. The data page reports duplicates, missing values, timestamp errors, invalid durations/costs, and missing type/qualification coverage. Check validation success before solving.

## 2. Generate initial schedules

Set the operational turnaround and select one or more strategies. Buffered adds its extra time only to aircraft connections in its initial solve. Flexible penalizes aircraft connections whose time slack beyond minimum turnaround is below the target. Compare the separately displayed operating cost and objective score; the flexible score is not a money amount.

## 3. Create a disruption

Select any set of flights to delay by the same amount or cancel, and any aircraft/crew members to make unavailable. The summary lists the complete scenario. Delays are applied to a fresh original-data copy exactly once for the recovery run.

## 4. Recover and compare

The app runs a separate recovery MILP for every successful initial plan. A flight labeled Cancelled is not treated as operated. The recovery table shows assigned aircraft and crew. Component costs, cancellation counts, reassignment counts, and solver status are reported. Strategy comparison uses the identical modified flight data and recovery rules.

## 5. Read the result

- **Operating cost:** aircraft and crew block hours times their hourly rates.
- **Recovery cost increase:** recovered operating cost minus initial operating cost; can be negative if flights are cancelled.
- **Cancelled:** flight was explicitly cancelled or had no preferable feasible assignment under the chosen recovery penalties.
- **Aircraft reassigned / crew changed:** differs from the corresponding initial allocation.
- **Solver status:** only Optimal is presented as a feasible optimized schedule; other statuses need investigation.
- **Total operational cost:** final operating cost plus modeled recovery penalties, with initial schedule cost not added twice.

All schedule and comparison tables can be downloaded as CSV.
