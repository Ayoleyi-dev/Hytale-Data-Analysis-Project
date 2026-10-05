
from pathlib import Path
import json
from collections import defaultdict, deque
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

PAGE = Path(__file__).resolve()
DASH = PAGE.parents[1]
ROOT = PAGE.parents[2]
sys.path.insert(0, str(DASH))

from ui import hero, section, note, footer, style_plot

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

def friendly_reason(v):
    s = "" if v is None else str(v)
    low = s.lower()

    if "clientdisconnecttype=disconnect" in low:
        return "Client disconnect"
    if "timeout" in low:
        return "Timeout"
    if "kick" in low:
        return "Kicked"
    if "shutdown" in low:
        return "Server shutdown"

    return s.replace("DisconnectReason{", "").replace("}", "") or "Unknown"

def sessions_from(events):
    if events.empty:
        return pd.DataFrame()

    e = events.copy()
    e["observed_at"] = pd.to_datetime(e["observed_at"], utc=True, errors="coerce")
    e = e.dropna(subset=["observed_at"]).sort_values("observed_at")

    q = defaultdict(deque)
    rows = []

    for _, r in e.iterrows():
        pid = r.get("player_id")
        event_type = r.get("event_type")

        if event_type == "player_connect":
            q[pid].append(r)

        elif event_type == "player_disconnect" and q[pid]:
            c = q[pid].popleft()

            rows.append(
                {
                    "player_id": pid,
                    "world_name": c.get("world_name") or r.get("world_name"),
                    "start_utc": c["observed_at"],
                    "end_utc": r["observed_at"],
                    "duration_minutes": (
                        r["observed_at"] - c["observed_at"]
                    ).total_seconds() / 60,
                    "disconnect_reason": friendly_reason(r.get("disconnect_reason")),
                }
            )

    return pd.DataFrame(rows)

events = read_jsonl(OBS / "analytics-events.jsonl")
hb = read_jsonl(OBS / "server-heartbeats.jsonl")
sessions = sessions_from(events)

meta_path = OBS / "run_metadata.json"
meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}

hero(
    "Observed Telemetry // Local Validation",
    "Real Hytale Server Capture",
    "This page only uses lifecycle events and server-health measurements collected from a Hytale server I controlled. "
    "No synthetic values are substituted here.",
    ["Java collector", "JSONL telemetry", "Session reconstruction", "Server health"],
)

if events.empty and hb.empty:
    section("Public deployment mode")
    st.info(
        "My real local telemetry files are intentionally excluded from the public GitHub/Streamlit deployment."
    )

    shot = ROOT / "docs" / "screenshots" / "observed-server-health.png"

    if shot.exists():
        st.image(
            str(shot),
            caption=(
                "Validated local capture: player concurrency, JVM memory usage and world tick duration "
                "from a Hytale server I controlled."
            ),
            width="stretch",
        )

    note(
        "The screenshot documents a genuine controlled Hytale server test. It is not Hypixel Studios production telemetry.",
        kind="gold",
    )

    footer()
    st.stop()

if not events.empty:
    events["observed_at"] = pd.to_datetime(events["observed_at"], utc=True, errors="coerce")

if not hb.empty:
    hb["observed_at"] = pd.to_datetime(hb["observed_at"], utc=True, errors="coerce")

players = events["player_id"].dropna().nunique() if "player_id" in events else 0
latest = (
    int(hb.sort_values("observed_at").iloc[-1]["players_online"])
    if not hb.empty and "players_online" in hb
    else 0
)
avg = sessions["duration_minutes"].mean() if len(sessions) else 0

section("Capture summary", "Observed local telemetry")

a, b, c, d = st.columns(4)
a.metric("Observed players", int(players))
b.metric("Completed sessions", len(sessions))
c.metric("Avg completed session", f"{avg:.1f} min" if len(sessions) else "—")
d.metric("Latest online", latest)

section("What I did")

st.write(
    "I ran a local Hytale server with my Java collector installed, joined from the matching client, played briefly and left. "
    "The collector wrote lifecycle events and 60-second server heartbeats, which I then ingested into this dashboard."
)

section("What I noticed")

with st.container(border=True):
    if len(sessions):
        r = sessions.iloc[0]
        st.markdown(
            f"- The collector reconstructed a complete session lasting **{r['duration_minutes']:.1f} minutes** "
            f"in **{r['world_name']}**."
        )

    if not hb.empty and "players_online" in hb:
        st.markdown(
            f"- The observed peak was **{int(hb['players_online'].max())} player(s)** and the series returned to 0 after the session."
        )

    if not hb.empty and "memory_used_mb" in hb:
        st.markdown(
            f"- JVM used memory ranged from **{int(hb['memory_used_mb'].min())} MB** "
            f"to **{int(hb['memory_used_mb'].max())} MB**."
        )

note(
    "This is a short local validation run. I use it to verify the collector and analytics pipeline rather than make Hytale-wide claims.",
    kind="gold",
)

section("Session view")

if len(sessions) < 5:
    if sessions.empty:
        st.info("No completed session yet.")
    else:
        show = sessions.copy()
        show["start_utc"] = show["start_utc"].dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        show["end_utc"] = show["end_utc"].dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        show["duration_minutes"] = show["duration_minutes"].round(2)

        st.dataframe(
            show,
            width="stretch",
            hide_index=True,
        )
else:
    l, r = st.columns(2)

    with l:
        fig = px.histogram(
            sessions,
            x="duration_minutes",
            title="Completed Session Duration",
            color_discrete_sequence=["#72D7D8"],
        )
        style_plot(fig)
        st.plotly_chart(fig, width="stretch")

    reasons = (
        sessions["disconnect_reason"]
        .value_counts()
        .rename_axis("reason")
        .reset_index(name="sessions")
    )

    with r:
        fig = px.bar(
            reasons,
            x="reason",
            y="sessions",
            title="Disconnect Reasons",
            color_discrete_sequence=["#E6B85C"],
        )
        style_plot(fig)
        st.plotly_chart(fig, width="stretch")

section("Observed server health")

if not hb.empty and "players_online" in hb:
    l, r = st.columns(2)

    with l:
        fig = px.line(
            hb,
            x="observed_at",
            y="players_online",
            markers=True,
            title="Concurrent Players",
            color_discrete_sequence=["#72D7D8"],
        )
        style_plot(fig)
        st.plotly_chart(fig, width="stretch")

    if "memory_used_mb" in hb:
        with r:
            fig = px.line(
                hb,
                x="observed_at",
                y="memory_used_mb",
                markers=True,
                title="JVM Memory Used (MB)",
                color_discrete_sequence=["#E6B85C"],
            )
            style_plot(fig)
            st.plotly_chart(fig, width="stretch")

world_rows = []

if not hb.empty and "worlds" in hb:
    for _, row in hb.iterrows():
        worlds = row.get("worlds")

        if isinstance(worlds, list):
            for w in worlds:
                if isinstance(w, dict):
                    world_rows.append(
                        {
                            "metric_ts": row["observed_at"],
                            "world_name": w.get("world_name"),
                            "average_tick_ms": w.get("average_tick_ms"),
                        }
                    )

world = pd.DataFrame(world_rows)

if not world.empty:
    fig = px.line(
        world,
        x="metric_ts",
        y="average_tick_ms",
        color="world_name",
        markers=True,
        title="Observed Average World Tick Duration",
        color_discrete_sequence=["#66B8FF"],
    )
    style_plot(fig, "World")
    st.plotly_chart(fig, width="stretch")

    st.caption(
        "Configured TPS is not shown as measured TPS; tick duration is the observed performance metric retained by the collector."
    )

section("Data quality")

checks = []

source_ok = events.empty or (
    "source" in events and events["source"].eq("hytale_server_plugin").all()
)
checks.append(("Collector source", "PASS" if source_ok else "REVIEW", "Expected server plugin source."))

pid_ok = events.empty or (
    "player_id" in events
    and events["player_id"].dropna().astype(str).str.startswith("p_").all()
)
checks.append(("Player IDs pseudonymized", "PASS" if pid_ok else "REVIEW", "Aliases should begin with p_."))

duration_ok = sessions.empty or (sessions["duration_minutes"] >= 0).all()
checks.append(("Completed session duration", "PASS" if duration_ok else "REVIEW", "No negative durations."))

if not hb.empty and {"memory_used_mb", "memory_max_mb"}.issubset(hb.columns):
    memory_ok = (hb["memory_used_mb"] <= hb["memory_max_mb"]).all()
    checks.append(("Memory bounds", "PASS" if memory_ok else "REVIEW", "Used memory should not exceed reported max."))

st.dataframe(
    pd.DataFrame(checks, columns=["check", "status", "detail"]),
    width="stretch",
    hide_index=True,
)

with st.expander("Raw observed lifecycle events"):
    raw = events.copy()

    if "disconnect_reason" in raw:
        raw["disconnect_reason"] = raw["disconnect_reason"].map(friendly_reason)

    st.dataframe(raw, width="stretch", hide_index=True)

section("Run provenance")

if meta:
    a, b, c = st.columns(3)
    a.metric("Hytale server", meta.get("hytale_server_version", "not recorded"))
    b.metric("Collector", f"v{meta.get('collector_version', 'unknown')}")
    c.metric("Schema", f"v{meta.get('schema_version', 'unknown')}")
    st.caption(meta.get("privacy", ""))

footer()
