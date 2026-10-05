@echo off
python src\ingest_collector.py ^
  --events data\observed\analytics-events.jsonl ^
  --heartbeats data\observed\server-heartbeats.jsonl ^
  --output-dir data\observed\processed
