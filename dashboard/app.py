\
from __future__ import annotations

import sqlite3
from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.metrics import overview, query_df, retention

DB_PATH = ROOT / "data" / "processed" / "hytale_analytics.db"

st.set_page_config(
    page_title="Hytale Player & Server Analytics",
    page_icon="ðŸ“Š",
    layout="wide",
)

st.title("Synthetic Hytale Player & Server Analytics")
st.info("Why synthetic? I needed enough reproducible data to test retention, engagement and server-operations analysis without pretending I had access to Hytale's private production telemetry. After proving the analytics logic here, I built the real local server collector shown on the Observed Server Data page.")

st.caption(
    "Portfolio demo using synthetic data. This dashboard is not affiliated with "
    "Hypixel Studios and does not contain proprietary Hytale player data."
)

if not DB_PATH.exists():
    st.error("Database not found.")
    st.code(
        "python src/generate_demo_data.py\n"
        "python src/build_database.py\n"
        "streamlit run dashboard/app.py"
    )
    st.stop()

conn = sqlite3.connect(DB_PATH)
kpi = overview(conn)

max_date = query_df(conn, "SELECT MAX(DATE(session_start)) AS max_date FROM player_sessions").iloc[0, 0]
min_date = query_df(conn, "SELECT MIN(DATE(session_start)) AS min_date FROM player_sessions").iloc[0, 0]

st.sidebar.header("Dataset")
st.sidebar.write(f"Period: **{min_date} â†’ {max_date}**")
st.sidebar.info("All player identifiers are anonymous synthetic IDs.")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Players", f"{kpi['players']:,}")
c2.metric("Sessions", f"{kpi['sessions']:,}")
c3.metric("Avg session", f"{kpi['avg_session_minutes']:.1f} min")
c4.metric("D1 retention", f"{retention(conn, 1):.1f}%")
c5.metric("D7 retention", f"{retention(conn, 7):.1f}%")

st.subheader("Player engagement")

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
)
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
)
left.plotly_chart(fig_features, width="stretch")

duration = query_df(
    conn,
    """
    SELECT duration_minutes
    FROM player_sessions
    """,
)
fig_duration = px.histogram(
    duration,
    x="duration_minutes",
    nbins=35,
    title="Session Duration Distribution",
    labels={"duration_minutes": "Minutes"},
)
right.plotly_chart(fig_duration, width="stretch")

st.subheader("Retention")

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
)
st.plotly_chart(fig_retention, width="stretch")

st.subheader("Server operations")

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
)
h1.plotly_chart(fig_tps, width="stretch")

fig_latency = px.line(
    health,
    x="metric_ts",
    y="latency_ms",
    color="server_id",
    title="Latency",
    labels={"metric_ts": "Time", "latency_ms": "Latency (ms)", "server_id": "Server"},
)
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
        st.dataframe(degraded, width="stretch")

st.subheader("Analyst interpretation")
st.markdown(
    """
- **Retention:** compare D1 and D7 curves by acquisition cohort to identify whether
  new-player stickiness changes over time.
- **Feature usage:** use unique-player reach alongside raw event volume so highly
  repetitive actions do not dominate interpretation.
- **Operations:** investigate periods where TPS drops or latency spikes, then compare
  them with player concurrency and memory/network load.
- **Next step:** replace the synthetic event source with a real opt-in server-side
  collector built against Hytale's public Server API.
"""
)

conn.close()

