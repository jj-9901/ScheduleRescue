# Mathematical model

## Sets and input

- `F`: flights; `A`: aircraft; `C`: crew.
- Flight `i` has origin `o_i`, destination `d_i`, fixed departure `s_i`, arrival `t_i`, required aircraft type `q_i`, crew count `r_i`, and priority `p_i`.
- Aircraft `a` has initial airport `l_a`, availability time `v_a`, type `Q_a`, and hourly operating rate `c_a`.
- Crew `c` has initial airport `l_c`, availability `v_c`, qualified types `Q_c`, maximum block hours `H_c`, and hourly rate `w_c`.
- `τ` is actual aircraft minimum turnaround; `ρ` is minimum crew rest. The buffered initial model uses `τ+B`.

## Variables

- `x_ia ∈ {0,1}`: aircraft `a` operates flight `i`.
- `y_ic ∈ {0,1}`: crew member `c` operates flight `i`.
- `z_i ∈ {0,1}`: flight `i` is cancelled.
- `u_ia`, `v_ia`, `g_ija`: aircraft route start, end, and follow-arc indicators.
- `U_ic`, `V_ic`, `G_ijc`: equivalent crew route indicators.

Start and follow arcs are created only where initial location/availability or airport/time compatibility permits. A route arc from `i` to `j` requires `d_i=o_j` and `t_i+gap ≤ s_j`.

## Coverage and route constraints

Each flight is operated once or cancelled:

`Σ_a x_ia + z_i = 1  ∀i`.

For each aircraft-flight node, route flow is balanced against assignment:

`Σ_j g_jia + u_ia = x_ia`, `Σ_j g_ija + v_ia = x_ia  ∀i,a`.

Each aircraft has at most one route start and one route end over the planning horizon. A continuous route may include any number of flights and return to its initial airport; disconnected components are prohibited because they would reset the aircraft location. Assignment is prohibited if type, availability, or declared unavailability fails.

Crew count per operated flight is exact:

`Σ_c y_ic = r_i(1-z_i)  ∀i`.

Crew route flow uses the same in/out equations with `G,U,V`. Crew arcs require a shared airport, sufficient rest, and availability; crew-flight assignments also require qualification and initial location/time for a route start. Total assigned block time is bounded:

`Σ_i h_i y_ic ≤ H_c  ∀c`, where `h_i=(t_i-s_i)` in hours.

This is a simplified block-hour cap, not a regulatory duty-time model.

## Operating costs and objectives

`h_i=(t_i-s_i)` hours. Aircraft and crew scheduled operating costs are:

`C_A=Σ_iΣ_a h_i c_a x_ia`, `C_C=Σ_iΣ_c h_i w_c y_ic`.

Normal minimizes `C_A+C_C`.

Buffered minimizes the same expression, but its aircraft arcs require `τ+B` during initial planning. Recovery always reverts to `τ`.

Flexible minimizes `C_A+C_C+λ Σ_(i,j,a) max(0, T - (s_j-t_i-τ))g_ija`, with target slack `T` and weight `λ`. This measures the shortfall between available gap beyond minimum turnaround and the desired slack. It is a resilience score, not cash cost.

Recovery minimizes:

`C_A+C_C + P_cancel Σ_i p_i z_i + P_A Σ_(i,a changed) x_ia + P_C Σ_(i,c changed) y_ic`.

The implementation defaults are `P_cancel=100000`, `P_A=250`, and `P_C=100` in the dataset's cost units. They are exposed in source-level function parameters, not in the interface. Reported components stay separate. Cancellation priorities scale the cancellation term.

## Disruption representation

- An external delay shifts both fixed times `s_i,t_i` before the recovery MILP is built. It is not applied in-place to session source data.
- A flight cancellation sets `z_i=1`.
- Full aircraft or crew unavailability removes all corresponding assignments. The solver API also accepts `(start,end)` unavailability periods, but the UI currently exposes full-resource unavailability only.
- The recovery objective compares candidate assignments with the selected baseline assignments.

There is no recovery retiming variable, so additional delay minutes are always zero in metrics. A solver result is valid only when CBC reports `Optimal`; other statuses are surfaced without presenting a schedule.
