-- 1) Daily active players and engagement
SELECT
    DATE(session_start) AS activity_date,
    COUNT(DISTINCT player_id) AS daily_active_players,
    COUNT(*) AS sessions,
    ROUND(AVG(duration_minutes), 2) AS avg_session_minutes
FROM player_sessions
GROUP BY DATE(session_start)
ORDER BY activity_date;

-- 2) D1 and D7 retention
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
ORDER BY cohort_date;

-- 3) Most-used player features
SELECT
    feature_category,
    COUNT(*) AS events,
    COUNT(DISTINCT player_id) AS unique_players,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS event_share_pct
FROM gameplay_events
GROUP BY feature_category
ORDER BY events DESC;

-- 4) Server health by server
SELECT
    server_id,
    ROUND(AVG(tps), 2) AS avg_tps,
    ROUND(AVG(latency_ms), 1) AS avg_latency_ms,
    ROUND(AVG(memory_used_mb), 0) AS avg_memory_mb,
    MAX(players_online) AS peak_players,
    MAX(capacity) AS capacity
FROM server_metrics
GROUP BY server_id
ORDER BY server_id;

-- 5) Flag potentially degraded server samples
SELECT
    metric_ts,
    server_id,
    tps,
    latency_ms,
    players_online,
    capacity
FROM server_metrics
WHERE tps < 18.0 OR latency_ms > 180
ORDER BY metric_ts DESC;
