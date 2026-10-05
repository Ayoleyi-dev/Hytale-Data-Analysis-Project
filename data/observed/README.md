# Observed Hytale Server Data

Do not commit real collector output by default.

When testing the Phase 2 Java collector, copy its two local JSONL outputs here:

```text
analytics-events.jsonl
server-heartbeats.jsonl
```

The Streamlit page `Observed Server Data` will automatically detect them.

The collector pseudonymization secret (`analytics-secret.key`) must **never** be
copied into this repository.
