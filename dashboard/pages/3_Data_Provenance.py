from pathlib import Path
import pandas as pd
import streamlit as st

PROJECT = Path(__file__).resolve().parents[2]
OBS = PROJECT / "data" / "observed"

def count_lines(path):
    if not path.exists():
        return 0
    return sum(1 for x in path.read_text(encoding="utf-8").splitlines() if x.strip())

events = count_lines(OBS / "analytics-events.jsonl")
heartbeats = count_lines(OBS / "server-heartbeats.jsonl")

st.title("Data Provenance & Validation")
st.caption("I keep synthetic, locally observed and unavailable production data explicitly separated.")

rows = [
    {
        "Dataset": "Synthetic demo",
        "Status": "Available",
        "Meaning": "Reproducible simulated data I generated to test analytics logic at scale.",
    },
    {
        "Dataset": "Local Hytale collector",
        "Status": f"Observed data available ({events} events, {heartbeats} heartbeats)" if events or heartbeats else "Not loaded",
        "Meaning": "Events and server-health observations captured on a Hytale server I control.",
    },
    {
        "Dataset": "Hypixel Studios production telemetry",
        "Status": "Not available to this project",
        "Meaning": "I do not have private production access and do not present local/synthetic data as Hytale-wide KPIs.",
    },
]
st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

st.header("Why I used both synthetic and observed data")
st.write(
    "Synthetic data let me prove the analytics design at scale. The local collector then proved that I could capture genuine Hytale events, "
    "reconstruct sessions and validate server observations from a system I controlled."
)

st.header("Collector privacy boundary")
st.write(
    "The analytics dataset uses pseudonymous player IDs and intentionally excludes usernames, raw UUIDs, IP addresses, chat content and authentication tokens."
)

st.header("Interpretation rule")
st.warning(
    "Synthetic results are simulations. Observed results are scoped to the server that generated them. "
    "Neither should be described as Hytale-wide player behaviour without an official dataset or authorized production-data source."
)
