# Data Dictionary

## `player_sessions`

| Column | Type | Meaning |
|---|---|---|
| `session_id` | text | Synthetic unique session ID |
| `player_id` | text | Anonymous synthetic player ID |
| `server_id` | text | Demo Hytale-style server shard |
| `session_start` | timestamp | UTC session start |
| `session_end` | timestamp | UTC session end |
| `duration_minutes` | numeric | Session length in minutes |
| `disconnect_reason` | text | Demo disconnect category |

## `gameplay_events`

| Column | Type | Meaning |
|---|---|---|
| `event_id` | text | Unique synthetic event ID |
| `session_id` | text | Parent session |
| `player_id` | text | Anonymous synthetic player |
| `server_id` | text | Demo server shard |
| `event_ts` | timestamp | UTC event timestamp |
| `event_name` | text | Example activity event |
| `feature_category` | text | Exploration/building/combat/crafting/modding/social |
| `event_value` | integer | Small synthetic activity intensity value |

## `server_metrics`

| Column | Type | Meaning |
|---|---|---|
| `metric_ts` | timestamp | UTC metric sample time |
| `server_id` | text | Demo server shard |
| `tps` | numeric | Simulated ticks per second |
| `memory_used_mb` | numeric | Simulated memory usage |
| `network_in_kbps` | numeric | Simulated inbound network rate |
| `network_out_kbps` | numeric | Simulated outbound network rate |
| `players_online` | integer | Simulated concurrent players |
| `capacity` | integer | Demo configured capacity |
| `latency_ms` | numeric | Simulated latency |
