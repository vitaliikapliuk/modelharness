#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pytest test_app.py .bench_hidden/tests/test_structure.py -q
