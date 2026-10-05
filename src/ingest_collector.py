"""Utilities for turning Hytale collector JSONL into analysis-ready tables.

Observed collector data is kept separate from the synthetic demo dataset.
No missing session boundaries are fabricated: an unmatched connect or disconnect
is reported as a data-quality issue instead of being guessed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict, deque
from pathlib import Path

import pandas as pd

EXPECTED_SOURCE = "hytale_server_plugin"
EVENT_COLUMNS = [
    "schema_version",
    "observed_at",
    "source",
    "server_id",
    "event_type",
    "player_id",
    "world_name",
    "disconnect_reason",
]
HEARTBEAT_COLUMNS = [
    "schema_version",
    "observed_at",
    "source",
    "server_id",
    "event_type",
    "players_online",
    "world_count",
    "memory_used_mb",
    "memory_max_mb",
    "worlds",
]


def _read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                value = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in {path} line {line_number}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"Expected JSON object in {path} line {line_number}")
            rows.append(value)
    return rows


def load_events(path: Path) -> pd.DataFrame:
    rows = _read_jsonl(path)
    df = pd.DataFrame(rows)
    for column in EVENT_COLUMNS:
        if column not in df.columns:
            df[column] = None
    if df.empty:
        return df[EVENT_COLUMNS]

    invalid_sources = sorted(set(df.loc[df["source"] != EXPECTED_SOURCE, "source"].dropna()))
    if invalid_sources:
        raise ValueError(f"Unexpected collector source values: {invalid_sources}")

    invalid_types = sorted(
        set(df.loc[~df["event_type"].isin(["player_connect", "player_disconnect"]), "event_type"].dropna())
    )
    if invalid_types:
        raise ValueError(f"Unexpected player event types: {invalid_types}")

    df["observed_at"] = pd.to_datetime(df["observed_at"], utc=True, errors="raise")
    df["schema_version"] = pd.to_numeric(df["schema_version"], errors="raise").astype(int)
    df = df.sort_values("observed_at").reset_index(drop=True)
    return df[EVENT_COLUMNS]


def load_heartbeats(path: Path) -> pd.DataFrame:
    rows = _read_jsonl(path)
    df = pd.DataFrame(rows)
    for column in HEARTBEAT_COLUMNS:
        if column not in df.columns:
            df[column] = None
    if df.empty:
        return df[HEARTBEAT_COLUMNS]

    if not (df["source"] == EXPECTED_SOURCE).all():
        raise ValueError("Heartbeat file contains a non-Hytale collector source")
    if not (df["event_type"] == "server_heartbeat").all():
        raise ValueError("Heartbeat file contains a non-heartbeat event")

    df["observed_at"] = pd.to_datetime(df["observed_at"], utc=True, errors="raise")
    for column in ["players_online", "world_count", "memory_used_mb", "memory_max_mb"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df = df.sort_values("observed_at").reset_index(drop=True)
    return df[HEARTBEAT_COLUMNS]


def build_sessions(events: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    session_rows: list[dict] = []
    opens: dict[tuple[str, str], deque[dict]] = defaultdict(deque)
    unmatched_disconnects = 0

    for row in events.to_dict("records"):
        server_id = str(row["server_id"])
        player_id = str(row["player_id"])
        key = (server_id, player_id)
        if row["event_type"] == "player_connect":
            opens[key].append(row)
            continue

        if row["event_type"] == "player_disconnect":
            if not opens[key]:
                unmatched_disconnects += 1
                continue
            start = opens[key].popleft()
            started_at = pd.Timestamp(start["observed_at"])
            ended_at = pd.Timestamp(row["observed_at"])
            if ended_at < started_at:
                unmatched_disconnects += 1
                continue
            duration_minutes = (ended_at - started_at).total_seconds() / 60.0
            stable = f"{server_id}|{player_id}|{started_at.isoformat()}|{ended_at.isoformat()}"
            session_id = "obs_" + hashlib.sha256(stable.encode("utf-8")).hexdigest()[:20]
            session_rows.append(
                {
                    "session_id": session_id,
                    "player_id": player_id,
                    "server_id": server_id,
                    "session_start": started_at,
                    "session_end": ended_at,
                    "duration_minutes": round(duration_minutes, 3),
                    "world_name": start.get("world_name") or row.get("world_name"),
                    "disconnect_reason": row.get("disconnect_reason"),
                    "data_source": "observed_hytale_server",
                }
            )

    unmatched_connects = sum(len(queue) for queue in opens.values())
    sessions = pd.DataFrame(
        session_rows,
        columns=[
            "session_id",
            "player_id",
            "server_id",
            "session_start",
            "session_end",
            "duration_minutes",
            "world_name",
            "disconnect_reason",
            "data_source",
        ],
    )
    quality = {
        "unmatched_connects": int(unmatched_connects),
        "unmatched_disconnects": int(unmatched_disconnects),
        "completed_sessions": int(len(sessions)),
    }
    return sessions, quality


def flatten_heartbeats(heartbeats: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for hb in heartbeats.to_dict("records"):
        worlds = hb.get("worlds") or []
        if not isinstance(worlds, list):
            worlds = []
        if not worlds:
            rows.append(
                {
                    "metric_ts": hb["observed_at"],
                    "server_id": hb["server_id"],
                    "world_name": None,
                    "server_players_online": hb["players_online"],
                    "world_players_online": None,
                    "world_count": hb["world_count"],
                    "memory_used_mb": hb["memory_used_mb"],
                    "memory_max_mb": hb["memory_max_mb"],
                    "configured_tps": None,
                    "average_tick_ms": None,
                    "data_source": "observed_hytale_server",
                }
            )
            continue
        for world in worlds:
            rows.append(
                {
                    "metric_ts": hb["observed_at"],
                    "server_id": hb["server_id"],
                    "world_name": world.get("world_name"),
                    "server_players_online": hb["players_online"],
                    "world_players_online": world.get("players_online"),
                    "world_count": hb["world_count"],
                    "memory_used_mb": hb["memory_used_mb"],
                    "memory_max_mb": hb["memory_max_mb"],
                    "configured_tps": world.get("configured_tps"),
                    "average_tick_ms": world.get("average_tick_ms"),
                    "data_source": "observed_hytale_server",
                }
            )
    return pd.DataFrame(rows)


def validate_observed_data(
    events: pd.DataFrame,
    heartbeats: pd.DataFrame,
    sessions: pd.DataFrame,
    quality: dict[str, int],
) -> pd.DataFrame:
    checks: list[dict] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "status": "PASS" if passed else "WARN", "detail": detail})

    add("Collector event source", events.empty or (events["source"] == EXPECTED_SOURCE).all(), "All events identify the expected collector source.")
    add("Player IDs pseudonymized", events.empty or events["player_id"].astype(str).str.match(r"^p_[0-9a-f]{32}$").all(), "Player IDs should be HMAC-derived aliases, never raw UUIDs.")
    add("Completed session duration", sessions.empty or (sessions["duration_minutes"] >= 0).all(), "No completed session has a negative duration.")
    add("Unmatched connects", quality["unmatched_connects"] == 0, f"{quality['unmatched_connects']} connect event(s) are still open and are not converted into sessions.")
    add("Unmatched disconnects", quality["unmatched_disconnects"] == 0, f"{quality['unmatched_disconnects']} disconnect event(s) had no matching earlier connect.")
    add("Heartbeat player counts", heartbeats.empty or (heartbeats["players_online"].fillna(0) >= 0).all(), "Heartbeat player counts are non-negative.")
    add("Memory bounds", heartbeats.empty or (heartbeats["memory_used_mb"].fillna(0) <= heartbeats["memory_max_mb"].fillna(float("inf"))).all(), "Observed JVM used memory does not exceed reported max memory.")

    return pd.DataFrame(checks)


def export_observed(events_path: Path, heartbeats_path: Path, output_dir: Path) -> dict[str, int]:
    events = load_events(events_path)
    heartbeats = load_heartbeats(heartbeats_path)
    sessions, quality = build_sessions(events)
    metrics = flatten_heartbeats(heartbeats)
    checks = validate_observed_data(events, heartbeats, sessions, quality)

    output_dir.mkdir(parents=True, exist_ok=True)
    events.to_csv(output_dir / "collector_events.csv", index=False)
    sessions.to_csv(output_dir / "observed_sessions.csv", index=False)
    metrics.to_csv(output_dir / "observed_server_metrics.csv", index=False)
    checks.to_csv(output_dir / "observed_data_quality.csv", index=False)

    return {
        "events": len(events),
        "heartbeats": len(heartbeats),
        "sessions": len(sessions),
        **quality,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Hytale Analytics Collector JSONL")
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--heartbeats", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("data/observed/processed"))
    args = parser.parse_args()

    result = export_observed(args.events, args.heartbeats, args.output_dir)
    print("Observed Hytale collector ingestion complete")
    for key, value in result.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
