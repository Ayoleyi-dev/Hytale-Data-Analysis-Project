\
"""Reusable SQL metrics for the dashboard and tests."""

from __future__ import annotations

import sqlite3
import pandas as pd


def scalar(conn: sqlite3.Connection, query: str, params: tuple = ()):
    row = conn.execute(query, params).fetchone()
    return row[0] if row else None


def overview(conn: sqlite3.Connection) -> dict:
    return {
        "players": scalar(conn, "SELECT COUNT(DISTINCT player_id) FROM player_sessions"),
        "sessions": scalar(conn, "SELECT COUNT(*) FROM player_sessions"),
        "avg_session_minutes": scalar(conn, "SELECT ROUND(AVG(duration_minutes), 1) FROM player_sessions"),
        "events": scalar(conn, "SELECT COUNT(*) FROM gameplay_events"),
        "avg_tps": scalar(conn, "SELECT ROUND(AVG(tps), 2) FROM server_metrics"),
    }


def retention(conn: sqlite3.Connection, day_n: int) -> float:
    query = """
    WITH first_seen AS (
        SELECT player_id, MIN(DATE(session_start)) AS cohort_date
        FROM player_sessions
        GROUP BY player_id
    ),
    returned AS (
        SELECT DISTINCT
            s.player_id
        FROM player_sessions s
        JOIN first_seen f ON f.player_id = s.player_id
        WHERE DATE(s.session_start) = DATE(f.cohort_date, ?)
    )
    SELECT
        100.0 * COUNT(*) / NULLIF((SELECT COUNT(*) FROM first_seen), 0)
    FROM returned;
    """
    modifier = f"+{int(day_n)} day"
    value = scalar(conn, query, (modifier,))
    return round(float(value or 0.0), 1)


def query_df(conn: sqlite3.Connection, query: str, params: tuple = ()) -> pd.DataFrame:
    return pd.read_sql_query(query, conn, params=params)
