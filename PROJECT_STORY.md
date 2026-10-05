# Hytale Player & Server Analytics — Project Story

I built this project in two stages.

## Phase 1 — synthetic analytics
I did not have access to Hypixel Studios' private Hytale production telemetry, so I generated a reproducible synthetic dataset instead of presenting made-up values as real player behaviour. I used it to build sessions, DAU, retention, feature usage, server operations, SQL, validation and Streamlit visualisation.

## Phase 2 — observed local Hytale data
I built a Java collector against Hytale's public Server API, installed it on a local test server, joined with the matching client and captured real connect/disconnect lifecycle events plus server heartbeats. I pseudonymized player identity and excluded usernames, raw UUIDs, IP addresses, chat and auth tokens from the analytics dataset.

The synthetic side demonstrates the analytics design at scale. The observed side proves the collection pipeline works against a real Hytale server I controlled.

## Scope
The synthetic dashboard is a simulation. The observed dashboard is real local-server data. Neither is Hypixel Studios' private production telemetry, and neither is presented as Hytale-wide player behaviour.
