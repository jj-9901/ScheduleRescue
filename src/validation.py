"""Input normalization and validation for Schedule Rescue datasets."""
from __future__ import annotations

import pandas as pd

FLIGHT_COLUMNS = ["flight_id", "origin", "destination", "departure", "arrival"]
AIRCRAFT_COLUMNS = ["aircraft_id", "initial_location", "available_from", "cost_per_hour"]
CREW_COLUMNS = ["crew_id", "initial_location", "available_from", "eligible_aircraft_types", "max_work_hours", "cost_per_hour"]


def _required(df: pd.DataFrame, cols: list[str], label: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"{label} is missing required column(s): {', '.join(missing)}")
    if df.empty:
        raise ValueError(f"{label} must contain at least one record.")
    if df[cols].isna().any().any():
        bad = [c for c in cols if df[c].isna().any()]
        raise ValueError(f"{label} has missing values in: {', '.join(bad)}")


def prepare_data(flights: pd.DataFrame, aircraft: pd.DataFrame, crew: pd.DataFrame | None = None):
    """Return normalized copies, rejecting malformed or incompatible records."""
    f, a = flights.copy(), aircraft.copy()
    _required(f, FLIGHT_COLUMNS, "Flights")
    _required(a, AIRCRAFT_COLUMNS, "Aircraft")
    for col in ("flight_id", "origin", "destination"):
        f[col] = f[col].astype(str).str.strip().str.upper()
        if (f[col] == "").any():
            raise ValueError(f"Flights column {col} cannot be blank.")
    for col in ("aircraft_id", "initial_location"):
        a[col] = a[col].astype(str).str.strip().str.upper()
        if (a[col] == "").any():
            raise ValueError(f"Aircraft column {col} cannot be blank.")
    for df, key, label in ((f, "flight_id", "Flight"), (a, "aircraft_id", "Aircraft")):
        if df[key].duplicated().any():
            duplicates = df.loc[df[key].duplicated(False), key].tolist()
            raise ValueError(f"{label} IDs must be unique; duplicates: {duplicates}")
    f["departure"] = pd.to_datetime(f["departure"], errors="raise")
    f["arrival"] = pd.to_datetime(f["arrival"], errors="raise")
    a["available_from"] = pd.to_datetime(a["available_from"], errors="raise")
    if "aircraft_type_required" not in f: f["aircraft_type_required"] = "ANY"
    if "required_crew_count" not in f: f["required_crew_count"] = 1
    if "priority" not in f: f["priority"] = 1
    if "aircraft_type" not in a: a["aircraft_type"] = "ANY"
    f["aircraft_type_required"] = f["aircraft_type_required"].fillna("ANY").astype(str).str.strip().str.upper()
    f["required_crew_count"] = pd.to_numeric(f["required_crew_count"], errors="raise").fillna(1).astype(int)
    f["priority"] = pd.to_numeric(f["priority"], errors="raise").fillna(1).astype(float)
    a["aircraft_type"] = a["aircraft_type"].fillna("ANY").astype(str).str.strip().str.upper()
    a["cost_per_hour"] = pd.to_numeric(a["cost_per_hour"], errors="raise")
    if (f["arrival"] <= f["departure"]).any():
        raise ValueError("Every flight arrival must be later than departure.")
    if (f["required_crew_count"] < 1).any() or (f["priority"] <= 0).any():
        raise ValueError("Required crew count and priority must be positive.")
    if (a["cost_per_hour"] < 0).any():
        raise ValueError("Aircraft cost_per_hour cannot be negative.")
    if crew is None:
        c = pd.DataFrame(columns=CREW_COLUMNS)
    else:
        c = crew.copy()
        if "cost_per_hour" not in c.columns:
            c["cost_per_hour"] = 0.0
        _required(c, CREW_COLUMNS, "Crew")
        c["crew_id"] = c["crew_id"].astype(str).str.strip().str.upper()
        c["initial_location"] = c["initial_location"].astype(str).str.strip().str.upper()
        c["available_from"] = pd.to_datetime(c["available_from"], errors="raise")
        c["max_work_hours"] = pd.to_numeric(c["max_work_hours"], errors="raise")
        c["cost_per_hour"] = pd.to_numeric(c["cost_per_hour"], errors="raise")
        c["eligible_aircraft_types"] = c["eligible_aircraft_types"].fillna("").astype(str).str.upper()
        if c["crew_id"].duplicated().any():
            raise ValueError("Crew IDs must be unique.")
        if (c[["crew_id", "initial_location"]].eq("").any().any() or (c["max_work_hours"] <= 0).any() or (c["cost_per_hour"] < 0).any()):
            raise ValueError("Crew IDs and locations must be present; max_work_hours must be positive and costs nonnegative.")
    known_airports = set(f["origin"]) | set(f["destination"])
    locations = set(a["initial_location"])
    if not c.empty:
        locations |= set(c["initial_location"])
    unknown = locations - known_airports
    if unknown:
        raise ValueError(f"Initial location(s) do not appear in any flight: {sorted(unknown)}")
    types = set(a["aircraft_type"])
    for req in f["aircraft_type_required"]:
        if req != "ANY" and req not in types:
            raise ValueError(f"No aircraft has required type {req!r}.")
    if not c.empty:
        for req, count in zip(f["aircraft_type_required"], f["required_crew_count"]):
            if req != "ANY":
                eligible = c["eligible_aircraft_types"].str.split(";").map(lambda xs: req in [x.strip() for x in xs] or "ANY" in [x.strip() for x in xs])
                if int(eligible.sum()) < count:
                    raise ValueError(f"Not enough crew qualified for aircraft type {req!r} (required {count}).")
    return f.sort_values(["departure", "arrival"]).reset_index(drop=True), a.reset_index(drop=True), c.reset_index(drop=True)
