\
"""Load CSV demo telemetry into SQLite and create portfolio-ready analytics views."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pandas as pd


def build_database(raw_dir: Path, db_path: Path, schema_path: Path) -> None:
    required = {
        "player_sessions": raw_dir / "player_sessions.csv",
        "gameplay_events": raw_dir / "gameplay_events.csv",
        "server_metrics": raw_dir / "server_metrics.csv",
    }
    missing = [str(path) for path in required.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing raw input files. Run `python src/generate_demo_data.py` first.\n"
            + "\n".join(missing)
        )

    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema_path.read_text(encoding="utf-8"))

        for table, csv_path in required.items():
            df = pd.read_csv(csv_path)
            df.to_sql(table, conn, if_exists="append", index=False)

        conn.executescript(
            """
            DROP VIEW IF EXISTS player_first_seen;
            CREATE VIEW player_first_seen AS
            SELECT
                player_id,
                MIN(DATE(session_start)) AS first_seen_date
            FROM player_sessions
            GROUP BY player_id;

            DROP VIEW IF EXISTS daily_active_players;
            CREATE VIEW daily_active_players AS
            SELECT
                DATE(session_start) AS activity_date,
                COUNT(DISTINCT player_id) AS dau,
                COUNT(*) AS sessions,
                ROUND(AVG(duration_minutes), 2) AS avg_session_minutes
            FROM player_sessions
            GROUP BY DATE(session_start);

            DROP VIEW IF EXISTS feature_usage;
            CREATE VIEW feature_usage AS
            SELECT
                feature_category,
                COUNT(*) AS events,
                COUNT(DISTINCT player_id) AS unique_players,
                ROUND(AVG(event_value), 2) AS avg_event_value
            FROM gameplay_events
            GROUP BY feature_category;

            DROP VIEW IF EXISTS server_health_daily;
            CREATE VIEW server_health_daily AS
            SELECT
                DATE(metric_ts) AS metric_date,
                server_id,
                ROUND(AVG(tps), 2) AS avg_tps,
                ROUND(AVG(memory_used_mb), 1) AS avg_memory_mb,
                ROUND(AVG(latency_ms), 1) AS avg_latency_ms,
                MAX(players_online) AS peak_players,
                MAX(capacity) AS capacity
            FROM server_metrics
            GROUP BY DATE(metric_ts), server_id;
            """
        )
        conn.commit()

    print(f"Built SQLite database: {db_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--db", type=Path, default=Path("data/processed/hytale_analytics.db"))
    parser.add_argument("--schema", type=Path, default=Path("sql/schema.sql"))
    args = parser.parse_args()
    build_database(args.raw_dir, args.db, args.schema)


if __name__ == "__main__":
    main()
