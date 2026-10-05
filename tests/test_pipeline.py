\
from pathlib import Path
import sqlite3
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.generate_demo_data import Config, generate


def test_generated_sessions_have_positive_duration():
    sessions, events, metrics = generate(Config(players=30, days=12, seed=1, servers=2))
    assert not sessions.empty
    assert (sessions["duration_minutes"] > 0).all()


def test_all_events_reference_existing_sessions():
    sessions, events, metrics = generate(Config(players=30, days=12, seed=2, servers=2))
    assert set(events["session_id"]).issubset(set(sessions["session_id"]))


def test_server_metrics_stay_within_capacity():
    sessions, events, metrics = generate(Config(players=30, days=12, seed=3, servers=2))
    assert (metrics["players_online"] <= metrics["capacity"]).all()
    assert (metrics["players_online"] >= 0).all()
