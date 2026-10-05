PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS gameplay_events;
DROP TABLE IF EXISTS player_sessions;
DROP TABLE IF EXISTS server_metrics;

CREATE TABLE player_sessions (
    session_id TEXT PRIMARY KEY,
    player_id TEXT NOT NULL,
    server_id TEXT NOT NULL,
    session_start TEXT NOT NULL,
    session_end TEXT NOT NULL,
    duration_minutes REAL NOT NULL CHECK (duration_minutes >= 0),
    disconnect_reason TEXT NOT NULL
);

CREATE TABLE gameplay_events (
    event_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    player_id TEXT NOT NULL,
    server_id TEXT NOT NULL,
    event_ts TEXT NOT NULL,
    event_name TEXT NOT NULL,
    feature_category TEXT NOT NULL,
    event_value INTEGER,
    FOREIGN KEY (session_id) REFERENCES player_sessions(session_id)
);

CREATE TABLE server_metrics (
    metric_ts TEXT NOT NULL,
    server_id TEXT NOT NULL,
    tps REAL NOT NULL,
    memory_used_mb REAL NOT NULL,
    network_in_kbps REAL NOT NULL,
    network_out_kbps REAL NOT NULL,
    players_online INTEGER NOT NULL,
    capacity INTEGER NOT NULL,
    latency_ms REAL NOT NULL,
    PRIMARY KEY (metric_ts, server_id)
);

CREATE INDEX idx_sessions_player ON player_sessions(player_id);
CREATE INDEX idx_sessions_start ON player_sessions(session_start);
CREATE INDEX idx_events_player ON gameplay_events(player_id);
CREATE INDEX idx_events_ts ON gameplay_events(event_ts);
CREATE INDEX idx_metrics_ts ON server_metrics(metric_ts);
