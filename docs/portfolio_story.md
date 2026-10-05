# Portfolio Story

## Business question

How can a sandbox game's product and server teams understand player engagement,
retention and technical health without mixing raw operational data directly into
ad-hoc analysis?

## What this project demonstrates

- Python data generation and ingestion
- SQL schema design and reusable views
- Player/session analytics
- D1 and D7 retention analysis
- Product feature adoption analysis
- Server-performance analytics
- A lightweight BI dashboard
- Clear privacy and data-provenance labeling
- A migration path from synthetic data to a real server-side event collector

## Interview talking points

1. **Why synthetic data?**  
   Hytale's public docs expose relevant server concepts, but private production
   telemetry is not publicly available. I therefore modeled the pipeline without
   pretending to possess proprietary data.

2. **Why sessions + events + server metrics?**  
   They separate three analytical grains: player visits, product interactions,
   and infrastructure observations.

3. **Why SQLite for the demo?**  
   It keeps the project reproducible for reviewers. The model can later move to
   PostgreSQL, BigQuery or another warehouse with minimal conceptual change.

4. **What would scale change?**  
   Batch CSV ingestion would become streaming/batched ingestion, event IDs would
   support idempotency, raw data would land in object storage, and transformed
   models would be built incrementally.

5. **What would I never collect by default?**  
   Chat text, IP addresses, auth tokens or unnecessary personal data.
