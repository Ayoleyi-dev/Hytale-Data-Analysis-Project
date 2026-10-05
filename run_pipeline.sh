#!/usr/bin/env bash
set -euo pipefail
python src/generate_demo_data.py
python src/build_database.py
echo
echo "Pipeline complete."
echo "Run: streamlit run dashboard/app.py"
