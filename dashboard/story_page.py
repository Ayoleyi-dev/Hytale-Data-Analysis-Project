
from pathlib import Path
import json
import sys

import pandas as pd
import streamlit as st

DASH = Path(__file__).resolve().parent
ROOT = DASH.parent
sys.path.insert(0, str(DASH))

from ui import hero, section, note, footer

OBS = ROOT / "data" / "observed"

def read_jsonl(path):
    rows = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return pd.DataFrame(rows)

events = read_jsonl(OBS / "analytics-events.jsonl")
hb = read_jsonl(OBS / "server-heartbeats.jsonl")

if not events.empty:
    events["observed_at"] = pd.to_datetime(events["observed_at"], utc=True, errors="coerce")
if not hb.empty:
    hb["observed_at"] = pd.to_datetime(hb["observed_at"], utc=True, errors="coerce")

hero(
    "Project Story // From Simulation to Telemetry",
    "How I Built the Analytics Lab",
    "I started with synthetic player and server data so I could design the analytics system honestly. "
    "Then I built a Java collector and validated the same workflow against a real Hytale server I controlled.",
    ["Synthetic analytics", "Java collector", "Observed telemetry", "Privacy-aware"],
)

section("Why I started with synthetic data")

left, right = st.columns(2)

with left:
    with st.container(border=True):
        st.markdown("#### Phase 1 — prove the analytics design")
        st.write(
            "I did not have access to Hytale's private production analytics, so I generated reproducible synthetic data instead of "
            "pretending invented numbers were real player behaviour."
        )
        st.markdown(
            """
- player sessions
- daily active players
- D1 / D7 retention
- feature usage
- server TPS / latency scenarios
- SQL + SQLite pipeline
"""
        )

with right:
    with st.container(border=True):
        st.markdown("#### Phase 2 — prove the collection pipeline")
        st.write(
            "I compiled a Java collector against the Hytale server API, installed it on a local server, authenticated the server, "
            "joined with the matching client, played briefly and ingested the resulting JSONL telemetry."
        )
        st.markdown(
            """
- player connect / disconnect
- session reconstruction
- player concurrency
- JVM memory
- world tick duration
- data-quality validation
"""
        )

if not events.empty and not hb.empty:
    section("First validated local run", "Observed data — not synthetic")

    connects = events[events["event_type"].eq("player_connect")].sort_values("observed_at")
    disconnects = events[events["event_type"].eq("player_disconnect")].sort_values("observed_at")

    minutes = None
    if len(connects) and len(disconnects):
        minutes = (
            disconnects.iloc[0]["observed_at"] - connects.iloc[0]["observed_at"]
        ).total_seconds() / 60

    a, b, c, d = st.columns(4)
    a.metric("Lifecycle events", len(events))
    b.metric("Heartbeats", len(hb))
    c.metric(
        "Peak players online",
        int(hb["players_online"].max()) if "players_online" in hb else 0,
    )
    d.metric(
        "Completed session",
        f"{minutes:.1f} min" if minutes is not None else "—",
    )

    with st.container(border=True):
        st.markdown("#### What I noticed")
        if minutes is not None:
            st.markdown(f"- I reconstructed a full connect → disconnect session lasting **{minutes:.1f} minutes**.")
        if "players_online" in hb:
            st.markdown(
                f"- The heartbeat series captured concurrency moving from **0 → {int(hb['players_online'].max())} → 0**."
            )
        if "memory_used_mb" in hb:
            st.markdown(
                f"- JVM used memory ranged from **{int(hb['memory_used_mb'].min())} MB** "
                f"to **{int(hb['memory_used_mb'].max())} MB** during the capture."
            )

    note(
        "I use this run to validate the collector and analytics pipeline. I do not use one local session to make claims "
        "about Hytale-wide players or production infrastructure.",
        kind="gold",
    )
else:
    section("First validated local run")
    st.info(
        "The public deployment intentionally does not ship my local collector output. "
        "The repository includes screenshots from the validated local test."
    )

section("Privacy by design")

with st.container(border=True):
    st.write(
        "The collector uses an HMAC-derived pseudonymous player identifier so I can match lifecycle events without storing "
        "the player's raw identity in the analytics dataset."
    )
    st.markdown(
        """
**Intentionally excluded**
- usernames
- raw UUIDs
- IP addresses
- chat content
- authentication tokens
"""
    )

section("What I would do with authorized production data")

st.write(
    "If Hytale provided an official dataset or authorized analytics API, I would keep the same source-separation rules and extend "
    "the model toward D1/D7/D30 cohorts, new vs returning players, feature adoption, LiveOps/update impact, regional reliability, "
    "capacity planning and creator/server ecosystem analytics."
)

footer()
