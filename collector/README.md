# Hytale Analytics Collector — Phase 2

This Java server plugin is the bridge from the portfolio's synthetic demo data
into **observed data from a Hytale server I control**.

It records only a deliberately small analytics surface:

- player connect
- player disconnect + disconnect reason
- pseudonymous player ID
- world name when available
- 60-second server heartbeat
- connected player count
- loaded world count
- JVM memory usage
- per-world configured TPS
- per-world average historical tick duration when the current API exposes it

It intentionally does **not** collect:

- usernames
- raw player UUIDs
- IP addresses
- chat messages
- authentication/session tokens
- private Hytale production telemetry

## Why this is legitimate

The collector is built against public Hytale Server API concepts. The current
API exposes `PlayerConnectEvent`, `PlayerDisconnectEvent`, `PlayerRef#getUuid`,
`Universe#getPlayerCount`, `Universe#getWorlds`, `World#getPlayerCount`,
`World#getTps`, and historic tick-length metrics. The plugin writes its own
local event log; it does not access Hypixel Studios' telemetry backend.

## Requirements

Hytale's official server manual currently specifies **Java 25** for dedicated
servers.

The build scripts compile against the `HytaleServer.jar` from the Hytale server
installation you already have. This avoids pinning the portfolio to an old API
artifact version while Hytale is changing quickly in Early Access.

## Windows build

From this `collector` directory:

```bat
set HYTALE_SERVER_JAR=C:\full\path\to\HytaleServer.jar
set HYTALE_ANALYTICS_SERVER_ID=my-test-server
build_plugin.bat
```

Output:

```text
build\HytaleAnalyticsCollector-0.2.0.jar
```

Copy that JAR into the Hytale server's `mods/` directory and start the server.
The official server manual recommends using `--disable-sentry` during active
plugin development so development crashes are not submitted.

## Output

The plugin writes inside its Hytale plugin data directory:

```text
analytics-secret.key
analytics/
├── analytics-events.jsonl
└── server-heartbeats.jsonl
```

Keep `analytics-secret.key` private. It makes pseudonymous player IDs stable
inside this dataset. Deleting the key deliberately breaks continuity with old
player IDs.

## Event example

```json
{"schema_version":1,"observed_at":"2026-10-05T12:00:00Z","source":"hytale_server_plugin","server_id":"my-test-server","event_type":"player_connect","player_id":"p_...","world_name":"default","disconnect_reason":null}
```

## Heartbeat example

```json
{"schema_version":1,"observed_at":"2026-10-05T12:01:00Z","source":"hytale_server_plugin","server_id":"my-test-server","event_type":"server_heartbeat","players_online":1,"world_count":1,"memory_used_mb":2100,"memory_max_mb":8192,"worlds":[{"world_name":"default","players_online":1,"configured_tps":20,"average_tick_ms":8.4}]}
```

## Important interpretation note

`configured_tps` is the world's configured/target TPS returned by the public
API. It is **not** labeled as measured TPS. `average_tick_ms` is kept as the
performance observation instead of inventing a measured TPS value.
