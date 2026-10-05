from pathlib import Path
import json
import pandas as pd
import streamlit as st

PROJECT = Path(__file__).resolve().parents[1]
OBS = PROJECT / "data" / "observed"

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

st.title("How I Built This Hytale Analytics Project")
st.caption("I built this in two stages: synthetic analytics first, then a real local Hytale server collector.")

st.header("Phase 1 — I started with synthetic data")
st.write(
    "I did not have access to Hytale's private production analytics. Instead of presenting made-up values as real player behaviour, "
    "I generated a reproducible synthetic dataset so I could design and test the analytics workflow: sessions, DAU, retention, "
    "feature usage, server operations, SQL, validation and dashboarding."
)
st.info("The synthetic side answers: Can I design the analytics system and reason about player/server metrics at useful scale?")

st.header("Phase 2 — I validated it with a real Hytale server")
st.write(
    "I built a Java collector against Hytale's public Server API, compiled it against the server JAR, installed it on a local server, "
    "authenticated the server, joined from the matching Hytale client, played briefly, left, and ingested the JSONL output."
)
st.success("The observed side answers: Can I collect genuine Hytale server observations safely and turn them into analysis?")

if not events.empty and not hb.empty:
    connects = events[events["event_type"].eq("player_connect")].sort_values("observed_at")
    disconnects = events[events["event_type"].eq("player_disconnect")].sort_values("observed_at")
    minutes = None
    if len(connects) and len(disconnects):
        minutes = (disconnects.iloc[0]["observed_at"] - connects.iloc[0]["observed_at"]).total_seconds() / 60
    a, b, c, d = st.columns(4)
    a.metric("Observed lifecycle events", len(events))
    b.metric("Heartbeat samples", len(hb))
    c.metric("Peak players online", int(hb["players_online"].max()) if "players_online" in hb else 0)
    d.metric("First completed session", f"{minutes:.1f} min" if minutes is not None else "—")
    st.subheader("What I noticed in the first validated run")
    if minutes is not None:
        st.markdown(f"- I captured a complete connect → disconnect session lasting about **{minutes:.1f} minutes**.")
    if "players_online" in hb:
        st.markdown(f"- The heartbeat data captured concurrency moving from 0 to **{int(hb['players_online'].max())}** and back to 0.")
    if "memory_used_mb" in hb:
        st.markdown(f"- JVM used memory ranged from **{int(hb['memory_used_mb'].min())} MB** to **{int(hb['memory_used_mb'].max())} MB**.")
    st.warning("I treat this as one short local test, not as evidence about Hytale's overall player base or production performance.")

st.header("Privacy and provenance")
st.write(
    "I pseudonymize player identifiers with an HMAC-derived alias so sessions can be matched without keeping usernames or raw UUIDs. "
    "The analytics dataset also excludes IP addresses, chat content and authentication tokens."
)

st.header("If I had official Hytale production data")
st.write(
    "I would extend this same pipeline to D1/D7/D30 retention, feature adoption, LiveOps/update impact, region/server reliability, "
    "capacity planning and creator/server ecosystem analytics."
)

st.markdown("---")
st.caption("Independent portfolio project. Synthetic results are simulations; observed results are scoped to the local server that generated them.")
