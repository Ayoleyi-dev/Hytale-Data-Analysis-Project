#!/usr/bin/env bash
set -euo pipefail
python src/ingest_collector.py \
  --events data/observed/analytics-events.jsonl \
  --heartbeats data/observed/server-heartbeats.jsonl \
  --output-dir data/observed/processed
