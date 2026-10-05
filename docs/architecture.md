# Architecture

```text
        ┌──────────────────────────────┐
        │  Demo source (Milestone 1)   │
        │ synthetic gameplay + server │
        │ telemetry CSVs              │
        └──────────────┬───────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │ Python ingestion / validation│
        │ src/build_database.py        │
        └──────────────┬───────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │ SQLite analytical model      │
        │ sessions / events / metrics  │
        │ + reusable SQL views         │
        └───────────┬───────────┬──────┘
                    │           │
                    ▼           ▼
          ┌──────────────┐  ┌───────────────┐
          │ SQL analysis │  │ Streamlit BI  │
          │ portfolio    │  │ dashboard     │
          │ queries      │  │               │
          └──────────────┘  └───────────────┘
```

## Planned Milestone 2: real Hytale server collector

The public Hytale Server API documents player lifecycle events such as
`PlayerConnectEvent` and `PlayerDisconnectEvent`, plus an `EventRegistry` for
listener registration. Hytale also documents a server `TelemetryModule` that
tracks server lifecycle data and periodic performance metrics including TPS,
memory, network and capacity.

The real collector will be kept **server-side, opt-in and privacy-conscious**.
It will emit only the fields needed for analysis and will avoid chat content,
IP addresses, authentication data or other unnecessary personal information.

Official API references:

- https://docs.hytale.com/api/com/hypixel/hytale/server/core/event/events/player/package-summary
- https://docs.hytale.com/api/com/hypixel/hytale/server/core/event/events/player/PlayerDisconnectEvent
- https://docs.hytale.com/api/com/hypixel/hytale/server/core/telemetry/TelemetryModule
- https://pre-release.docs.hytale.com/api/com/hypixel/hytale/event/EventRegistry

> API note: Hytale is in active development, so the integration layer should be
> version-pinned and re-checked against the current Server API before release.
