"""Plotly timelines derived from solver schedule tables."""
import pandas as pd
import plotly.express as px


def resource_timeline(schedule: pd.DataFrame, resource: str, title: str,
                      initial_schedule: pd.DataFrame | None = None):
    """Build a Gantt-style view for aircraft or crew assignments."""
    if schedule.empty:
        return px.scatter(title=f"{title}: no schedule")
    data=schedule[schedule.status != "Cancelled"].copy()
    if resource == "assigned_crew":
        data["resource"] = data[resource].fillna("").astype(str).str.split(";")
        data=data.explode("resource")
        data=data[data.resource != ""]
    else:
        data=data.rename(columns={resource:"resource"})
        data=data.dropna(subset=["resource"])
    if initial_schedule is not None:
        old=initial_schedule.set_index("flight_id")[resource].to_dict()
        def changed(row):
            before=old.get(row.flight_id)
            if resource == "assigned_crew":
                return "Reassigned" if row.resource not in str(before).split(";") else "Operated"
            return "Reassigned" if before != row.resource else "Operated"
        data["assignment change"] = data.apply(changed,axis=1)
    else:
        data["assignment change"]="Initial"
    fig=px.timeline(data,x_start="departure",x_end="arrival",y="resource",color="assignment change",
                    hover_name="flight_id",hover_data=["origin","destination"],title=title)
    fig.update_yaxes(autorange="reversed",title="")
    fig.update_layout(xaxis_title="Time",legend_title="")
    return fig
