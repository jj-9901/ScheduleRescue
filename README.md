# Schedule Rescue

An academic airline schedule planning and disruption recovery simulator. It uses PuLP and CBC to solve a binary mixed-integer linear program for aircraft and crew routing. Schedules shown in the app are solver outputs; an infeasible or non-optimal result is shown as such.

## Research question

Can a somewhat more expensive initial schedule provide enough aircraft connection slack to reduce cancellations or reassignment impact after disruptions? The application generates Normal, Buffered, and Flexible plans and can recover each under one identical scenario. It reports actual results; no strategy is assumed to win.

## Features

- Demo, editable manual, and three CSV input datasets.
- Flight, aircraft, and crew validation with useful errors and downloadable templates.
- Aircraft routing with initial location/availability, type restrictions, route continuity, and minimum turnaround. Each aircraft follows one continuous route through the planning horizon, with an unrestricted number of connected flights.
- Crew routing with location, availability, aircraft-type qualifications, minimum rest, cumulative block-hour limits, and required flight staffing.
- Normal, Buffered, and Flexible initial MILPs.
- Flight delay and cancellation, aircraft unavailability, and crew unavailability disruptions.
- Recovery MILP with cancellation, aircraft reassignment, crew reassignment, and operating cost terms reported separately.
- Repeated strategy comparison, schedule tables, charts, and CSV downloads.

## Technology and layout

Python 3.11+, Streamlit, pandas, PuLP/CBC, and Plotly.

```text
app.py                     Streamlit user interface
src/validation.py          normalization and input checks
src/scheduler.py           aircraft + crew MILP for planning/recovery
src/metrics.py             schedule slack and comparative accounting
tests/                     small solver-backed regression tests
docs/                      equations, methodology, assumptions, and guide
```

## Install and run

Use a virtual environment, then install pinned dependencies:

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

PuLP's CBC command-line solver must be available. The pinned PuLP distribution used in development bundles CBC. If CBC cannot start, the app will return the solver status instead of inventing a schedule.

## Using the simulator

1. Choose the demo data, edit the sample tables, or upload flights, aircraft, and crew CSVs. Input IDs must be unique. Times use pandas-readable timestamps. Crew qualifications are semicolon-separated aircraft types; `ANY` matches any type.
2. Set the actual minimum turnaround and strategy parameters. Solve any or all initial strategies. Check status and actual operating cost; the flexible objective score includes a separate non-cash resilience penalty.
3. Select externally delayed/cancelled flights or unavailable aircraft/crew. The delay is applied once to a fresh copy of the original data for each recovery solve.
4. Run recovery and compare the independent strategy results. Download schedules and comparison CSV.

## Accounting and model

The initial operating cost is the sum of block hours times aircraft hourly cost plus the sum of block hours times crew hourly cost. Recovery reports the recovered operating cost, cancellation penalty and reassignment penalties separately. The comparison's **total operational cost** is recovered operating cost plus recovery penalties. This is algebraically initial cost plus the change in schedule operating cost plus penalties, so the initial schedule is not counted twice. External delay is reflected in time-feasibility and block-hour cost using the shifted flight times; the model has no additional delay decision variable.

Normal minimizes operating cost. Buffered applies additional aircraft turnaround to the initial solve only. Flexible adds a weighted penalty to every selected aircraft connection for slack shortfall below the user target, where slack is the gap between flights minus the minimum turnaround. Both strategies retain actual operating costs as a separate result. Recovery for every strategy uses the same actual turnaround and recovery objective.

The full formulation is in [docs/mathematical_model.md](docs/mathematical_model.md). Data definitions and simplifying assumptions are in [docs/assumptions.md](docs/assumptions.md); instructions are in [docs/user_guide.md](docs/user_guide.md); experiment design is in [docs/methodology.md](docs/methodology.md).

## Test

```bash
python -m unittest discover -s tests -v
```

Tests execute CBC on small instances, checking route continuity, equipment/crew availability, external delay, cancellation, crew qualification/duty limits, strategy settings, and an infeasible instance.

## Limitations and future scope

The model is for demonstration and does not encode full airline dispatch rules. Crew duty is total flight block time, not a regulatory duty-day construct; no pairings, positioning, bases, or jurisdiction-specific limits are modeled. Flight delays are fixed external inputs during recovery; no model-selected retiming, airport closure, or time-window unavailability UI is included. Canceled flights incur a high configurable-in-code priority-weighted penalty; model weights should be calibrated before operational interpretation. Useful extensions include duty windows and pairings, optimized delay variables, airport closures, stochastic disruption sampling, and richer costs.
