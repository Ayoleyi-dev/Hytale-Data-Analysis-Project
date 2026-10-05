
from pathlib import Path
import sys

import streamlit as st

PAGE = Path(__file__).resolve()
DASH = PAGE.parents[1]
ROOT = PAGE.parents[2]
sys.path.insert(0, str(DASH))

from ui import hero, section, note, footer

OBS = ROOT / "data" / "observed"

def count_lines(path):
    if not path.exists():
        return 0

    return sum(
        1
        for x in path.read_text(encoding="utf-8").splitlines()
        if x.strip()
    )

events = count_lines(OBS / "analytics-events.jsonl")
heartbeats = count_lines(OBS / "server-heartbeats.jsonl")

hero(
    "Trust Layer // Provenance",
    "What Every Number Actually Represents",
    "I keep simulated, locally observed and unavailable production data explicitly separated so the project never implies more scope than the source supports.",
    ["Synthetic", "Observed local", "Production unavailable", "Privacy boundary"],
)

section("Current data sources")

c1, c2, c3 = st.columns(3)

with c1:
    with st.container(border=True):
        st.markdown("#### Synthetic demo")
        st.caption("AVAILABLE")
        st.write(
            "Reproducible simulated player, session and server data I generated to test analytics logic at useful scale."
        )

with c2:
    with st.container(border=True):
        st.markdown("#### Local Hytale collector")
        st.caption("OBSERVED LOCAL DATA")
        if events or heartbeats:
            st.write(
                f"This environment currently has **{events} lifecycle events** and **{heartbeats} server heartbeats** loaded."
            )
        else:
            st.write(
                "The public deployment intentionally excludes my local collector output. "
                "Validated screenshots remain in the repository."
            )

with c3:
    with st.container(border=True):
        st.markdown("#### Hypixel Studios production telemetry")
        st.caption("NOT AVAILABLE")
        st.write(
            "I do not have private production access and I do not present local or synthetic data as Hytale-wide KPIs."
        )

section("Why I used both synthetic and observed data")

st.write(
    "Synthetic data let me prove the analytics design at scale. "
    "The local collector then proved that I could capture genuine Hytale events, reconstruct sessions and validate server observations "
    "from a system I controlled."
)

section("Collector privacy boundary")

left, right = st.columns(2)

with left:
    with st.container(border=True):
        st.markdown("#### What I keep")
        st.markdown(
            """
- pseudonymous player ID
- connect / disconnect lifecycle
- world name
- player counts
- JVM memory
- limited performance observations
"""
        )

with right:
    with st.container(border=True):
        st.markdown("#### What I intentionally exclude")
        st.markdown(
            """
- usernames
- raw UUIDs
- IP addresses
- chat content
- authentication tokens
- private Hypixel telemetry
"""
        )

section("Interpretation rule")

note(
    "Synthetic results are simulations. Observed results are scoped to the server that generated them. "
    "Neither should be described as Hytale-wide player behaviour without an official dataset or authorized production-data source.",
    kind="gold",
)

footer()
