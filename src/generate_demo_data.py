\
"""Generate privacy-safe synthetic Hytale-style analytics data.

This is demo data, not data collected from Hytale or Hypixel Studios.
The event and server-health model is designed around publicly documented
Hytale server concepts such as player lifecycle events and telemetry metrics.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import argparse

import numpy as np
import pandas as pd


FEATURES = ["exploration", "building", "combat", "crafting", "modding", "social"]
FEATURE_WEIGHTS = np.array([0.28, 0.23, 0.18, 0.12, 0.11, 0.08])
DISCONNECT_REASONS = ["quit", "timeout", "server_restart", "network_error"]


@dataclass(frozen=True)
class Config:
    players: int = 600
    days: int = 60
    seed: int = 42
    servers: int = 3


def _utc_floor_day(ts: pd.Timestamp) -> pd.Timestamp:
    return pd.Timestamp(ts).floor("D")


def generate(config: Config) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(config.seed)
    end_date = _utc_floor_day(pd.Timestamp.now(tz="UTC"))
    start_date = end_date - pd.Timedelta(days=config.days - 1)

    player_ids = [f"p_{i:05d}" for i in range(1, config.players + 1)]
    first_offsets = rng.integers(0, max(2, config.days - 7), size=config.players)
    first_dates = [start_date + pd.Timedelta(days=int(x)) for x in first_offsets]

    sessions = []
    events = []
    session_counter = 1

    # Each player gets a latent engagement level so the data contains realistic
    # cohorts instead of being completely uniform random noise.
    engagement = rng.beta(2.0, 4.0, size=config.players)

    for idx, (player_id, first_date) in enumerate(zip(player_ids, first_dates)):
        max_age_days = max(1, (end_date - first_date).days + 1)
        base = engagement[idx]

        # More engaged players return on more days; return probability decays
        # with player age, producing a retention curve.
        for age in range(max_age_days):
            activity_date = first_date + pd.Timedelta(days=age)
            retention_decay = np.exp(-age / (18 + 35 * base))
            active_prob = min(0.92, 0.10 + 0.72 * base * retention_decay)

            # Ensure acquisition day has at least one session.
            active = age == 0 or rng.random() < active_prob
            if not active:
                continue

            sessions_today = 1 + int(rng.random() < (0.12 + 0.35 * base))
            for _ in range(sessions_today):
                server_id = f"orbis-{rng.integers(1, config.servers + 1)}"
                start_hour = int(np.clip(rng.normal(18, 5), 0, 23))
                start_minute = int(rng.integers(0, 60))
                start_ts = activity_date + pd.Timedelta(hours=start_hour, minutes=start_minute)

                duration_min = float(np.clip(rng.lognormal(mean=3.45 + base * 0.65, sigma=0.55), 4, 240))
                end_ts = start_ts + pd.Timedelta(minutes=duration_min)

                disconnect_reason = rng.choice(
                    DISCONNECT_REASONS,
                    p=[0.90, 0.05, 0.03, 0.02],
                )

                session_id = f"s_{session_counter:08d}"
                session_counter += 1
                sessions.append(
                    {
                        "session_id": session_id,
                        "player_id": player_id,
                        "server_id": server_id,
                        "session_start": start_ts.isoformat(),
                        "session_end": end_ts.isoformat(),
                        "duration_minutes": round(duration_min, 2),
                        "disconnect_reason": disconnect_reason,
                    }
                )

                # Event count scales with session length but is capped so this
                # repo stays lightweight enough for a portfolio clone.
                event_count = int(np.clip(rng.poisson(duration_min / 7.5), 2, 28))
                event_times = np.sort(rng.uniform(0, duration_min, event_count))
                feature_mix = FEATURE_WEIGHTS.copy()

                # Give individual players a mild preference toward one feature.
                favorite = idx % len(FEATURES)
                feature_mix[favorite] += 0.10
                feature_mix /= feature_mix.sum()

                selected = rng.choice(FEATURES, size=event_count, p=feature_mix)
                for n, (offset_min, feature) in enumerate(zip(event_times, selected), start=1):
                    event_ts = start_ts + pd.Timedelta(minutes=float(offset_min))
                    events.append(
                        {
                            "event_id": f"{session_id}_e{n:03d}",
                            "session_id": session_id,
                            "player_id": player_id,
                            "server_id": server_id,
                            "event_ts": event_ts.isoformat(),
                            "event_name": f"{feature}_activity",
                            "feature_category": feature,
                            "event_value": int(rng.integers(1, 6)),
                        }
                    )

    sessions_df = pd.DataFrame(sessions)
    events_df = pd.DataFrame(events)

    # Server health sampled every 30 minutes.
    metric_rows = []
    timestamps = pd.date_range(start_date, end_date + pd.Timedelta(days=1), freq="30min", inclusive="left")
    for server_num in range(1, config.servers + 1):
        server_id = f"orbis-{server_num}"
        capacity = 120
        for ts in timestamps:
            hour = ts.hour
            peak = np.exp(-((hour - 19) ** 2) / (2 * 4.0**2))
            players_online = int(np.clip(rng.normal(12 + 62 * peak, 8), 0, capacity))
            stress = players_online / capacity
            tps = float(np.clip(rng.normal(20.0 - 2.6 * stress**2, 0.32), 12.0, 20.0))
            latency = float(np.clip(rng.normal(48 + 95 * stress**2, 18), 12, 420))
            memory_used = float(np.clip(rng.normal(3200 + 5200 * stress, 420), 1800, 10000))
            network_in = float(np.clip(rng.normal(180 + players_online * 12, 75), 20, None))
            network_out = float(np.clip(rng.normal(240 + players_online * 16, 95), 20, None))

            metric_rows.append(
                {
                    "metric_ts": ts.isoformat(),
                    "server_id": server_id,
                    "tps": round(tps, 2),
                    "memory_used_mb": round(memory_used, 1),
                    "network_in_kbps": round(network_in, 1),
                    "network_out_kbps": round(network_out, 1),
                    "players_online": players_online,
                    "capacity": capacity,
                    "latency_ms": round(latency, 1),
                }
            )

    metrics_df = pd.DataFrame(metric_rows)
    return sessions_df, events_df, metrics_df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--players", type=int, default=600)
    parser.add_argument("--days", type=int, default=60)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--servers", type=int, default=3)
    parser.add_argument("--output", type=Path, default=Path("data/raw"))
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    cfg = Config(players=args.players, days=args.days, seed=args.seed, servers=args.servers)
    sessions, events, metrics = generate(cfg)

    sessions.to_csv(args.output / "player_sessions.csv", index=False)
    events.to_csv(args.output / "gameplay_events.csv", index=False)
    metrics.to_csv(args.output / "server_metrics.csv", index=False)

    print(f"Generated {len(sessions):,} sessions")
    print(f"Generated {len(events):,} gameplay events")
    print(f"Generated {len(metrics):,} server metric samples")
    print("IMPORTANT: all rows are synthetic demo data.")


if __name__ == "__main__":
    main()
