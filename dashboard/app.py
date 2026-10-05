
from __future__ import annotations

import sqlite3
from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

DASH = Path(__file__).resolve().parent
ROOT = DASH.parent

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(DASH))

from src.metrics import overview, query_df, retention
from ui import hero, section, note, footer, style_plot

DB_PATH = ROOT / "data" / "processed" / "hytale_analytics.db"

hero(
    "Synthetic Analytics // Scale Test",
    "Player & Server Intelligence",
    "I generated this reproducible simulation to design the analytics workflow at useful scale "
    "without presenting invented values as real Hytale player behaviour.",
    ["Player analytics", "Retention", "Feature usage", "Server operations", "Reproducible simulation"],
)

if not DB_PATH.exists():
    st.error("The synthetic SQLite database is not available in this environment.")
    st.code(
        "python src/generate_demo_data.py\n"
        "python src/build_database.py\n"
        "python -m streamlit run dashboard/Portfolio_Story.py"
    )
    st.stop()

conn = sqlite3.connect(DB_PATH)
kpi = overview(conn)

max_date = query_df(
    conn,
    "SELECT MAX(DATE(session_start)) AS max_date FROM player_sessions"
).iloc[0, 0]

min_date = query_df(
    conn,
    "SELECT MIN(DATE(session_start)) AS min_date FROM player_sessions"
).iloc[0, 0]

st.sidebar.markdown("### Synthetic dataset")
st.sidebar.write(f"**{min_date} → {max_date}**")
st.sidebar.caption("All player identifiers here are anonymous synthetic IDs.")

section("Executive snapshot", "Simulation results")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Players", f"{kpi['players']:,}")
c2.metric("Sessions", f"{kpi['sessions']:,}")
c3.metric("Avg session", f"{kpi['avg_session_minutes']:.1f} min")
c4.metric("D1 retention", f"{retention(conn, 1):.1f}%")
c5.metric("D7 retention", f"{retention(conn, 7):.1f}%")

note(
    "These KPIs come from my synthetic scenario. They demonstrate the analytics logic; "
    "they are not official Hytale statistics.",
    kind="gold",
)

section("Player engagement")

daily = query_df(
    conn,
    """
    SELECT activity_date, dau, sessions, avg_session_minutes
    FROM daily_active_players
    ORDER BY activity_date
    """,
)
daily["activity_date"] = pd.to_datetime(daily["activity_date"])

fig_dau = px.line(
    daily,
    x="activity_date",
    y="dau",
    markers=True,
    title="Daily Active Players",
    labels={"activity_date": "Date", "dau": "DAU"},
    color_discrete_sequence=["#72D7D8"],
)
style_plot(fig_dau)
st.plotly_chart(fig_dau, width="stretch")

left, right = st.columns(2)

features = query_df(
    conn,
    """
    SELECT feature_category, events, unique_players
    FROM feature_usage
    ORDER BY events DESC
    """,
)

fig_features = px.bar(
    features,
    x="feature_category",
    y="events",
    title="Feature Usage",
    labels={"feature_category": "Feature", "events": "Events"},
    color_discrete_sequence=["#E6B85C"],
)
style_plot(fig_features)
left.plotly_chart(fig_features, width="stretch")

duration = query_df(
    conn,
    "SELECT duration_minutes FROM player_sessions",
)

fig_duration = px.histogram(
    duration,
    x="duration_minutes",
    nbins=35,
    title="Session Duration Distribution",
    labels={"duration_minutes": "Minutes"},
    color_discrete_sequence=["#72D7D8"],
)
style_plot(fig_duration)
right.plotly_chart(fig_duration, width="stretch")

section("Retention", "Daily acquisition cohorts")

retention_df = query_df(
    conn,
    """
    WITH first_seen AS (
        SELECT player_id, MIN(DATE(session_start)) AS cohort_date
        FROM player_sessions
        GROUP BY player_id
    ),
    returns AS (
        SELECT
            f.player_id,
            f.cohort_date,
            MAX(CASE WHEN DATE(s.session_start) = DATE(f.cohort_date, '+1 day') THEN 1 ELSE 0 END) AS d1,
            MAX(CASE WHEN DATE(s.session_start) = DATE(f.cohort_date, '+7 day') THEN 1 ELSE 0 END) AS d7
        FROM first_seen f
        LEFT JOIN player_sessions s ON s.player_id = f.player_id
        GROUP BY f.player_id, f.cohort_date
    )
    SELECT
        cohort_date,
        COUNT(*) AS acquired_players,
        ROUND(100.0 * AVG(d1), 1) AS d1_retention_pct,
        ROUND(100.0 * AVG(d7), 1) AS d7_retention_pct
    FROM returns
    GROUP BY cohort_date
    ORDER BY cohort_date
    """,
)

retention_long = retention_df.melt(
    id_vars=["cohort_date", "acquired_players"],
    value_vars=["d1_retention_pct", "d7_retention_pct"],
    var_name="retention_window",
    value_name="retention_pct",
)

fig_retention = px.line(
    retention_long,
    x="cohort_date",
    y="retention_pct",
    color="retention_window",
    title="Retention by Acquisition Cohort",
    labels={
        "cohort_date": "Acquisition date",
        "retention_pct": "Retention %",
        "retention_window": "Window",
    },
    color_discrete_sequence=["#A4E7E2", "#66B8FF"],
)
style_plot(fig_retention, "Retention window")
st.plotly_chart(fig_retention, width="stretch")

st.caption(
    "Daily cohorts are useful for diagnosis but can be noisy when individual cohort sizes are small."
)

section("Server operations", "Synthetic infrastructure scenario")

health = query_df(
    conn,
    """
    SELECT metric_ts, server_id, tps, latency_ms, memory_used_mb,
           players_online, capacity
    FROM server_metrics
    ORDER BY metric_ts
    """,
)
health["metric_ts"] = pd.to_datetime(health["metric_ts"])

h1, h2 = st.columns(2)

fig_tps = px.line(
    health,
    x="metric_ts",
    y="tps",
    color="server_id",
    title="Server TPS",
    labels={"metric_ts": "Time", "tps": "TPS", "server_id": "Server"},
    color_discrete_sequence=["#72D7D8", "#66B8FF", "#E6B85C"],
)
style_plot(fig_tps, "Server")
h1.plotly_chart(fig_tps, width="stretch")

fig_latency = px.line(
    health,
    x="metric_ts",
    y="latency_ms",
    color="server_id",
    title="Latency",
    labels={"metric_ts": "Time", "latency_ms": "Latency (ms)", "server_id": "Server"},
    color_discrete_sequence=["#72D7D8", "#66B8FF", "#E6B85C"],
)
style_plot(fig_latency, "Server")
h2.plotly_chart(fig_latency, width="stretch")

degraded = query_df(
    conn,
    """
    SELECT metric_ts, server_id, tps, latency_ms, players_online, capacity
    FROM server_metrics
    WHERE tps < 18.0 OR latency_ms > 180
    ORDER BY metric_ts DESC
    LIMIT 100
    """,
)

with st.expander("Operational anomaly samples"):
    if degraded.empty:
        st.success("No degraded samples in the current demo dataset.")
    else:
        st.dataframe(degraded, width="stretch", hide_index=True)

section("Analyst interpretation")

st.markdown(
    """
- **Retention:** compare cohort behaviour over time and investigate whether changes align with onboarding or content changes.
- **Feature usage:** use both raw event volume and unique-player reach so repetitive mechanics do not dominate the story.
- **Operations:** inspect TPS/latency changes alongside concurrency and resource pressure.
- **Phase 2:** I also built and validated an opt-in Hytale server-side collector; that pipeline is documented separately in this project.
"""
)

conn.close()
footer()
