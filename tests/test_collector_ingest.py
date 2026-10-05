from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.ingest_collector import (
    build_sessions,
    flatten_heartbeats,
    load_events,
    load_heartbeats,
    validate_observed_data,
)

FIXTURES = ROOT / "tests" / "fixtures" / "collector"


def test_build_sessions_from_observed_events():
    events = load_events(FIXTURES / "analytics-events.jsonl")
    sessions, quality = build_sessions(events)
    assert len(sessions) == 2
    assert quality["unmatched_connects"] == 0
    assert quality["unmatched_disconnects"] == 0
    assert sorted(sessions["duration_minutes"].tolist()) == [42.0, 65.0]


def test_flatten_heartbeats_keeps_observed_tick_metric():
    heartbeats = load_heartbeats(FIXTURES / "server-heartbeats.jsonl")
    metrics = flatten_heartbeats(heartbeats)
    assert len(metrics) == 2
    assert metrics["configured_tps"].tolist() == [20, 20]
    assert metrics["average_tick_ms"].tolist() == [8.4, 9.1]


def test_observed_data_quality_passes_fixture():
    events = load_events(FIXTURES / "analytics-events.jsonl")
    heartbeats = load_heartbeats(FIXTURES / "server-heartbeats.jsonl")
    sessions, quality = build_sessions(events)
    checks = validate_observed_data(events, heartbeats, sessions, quality)
    assert (checks["status"] == "PASS").all()
