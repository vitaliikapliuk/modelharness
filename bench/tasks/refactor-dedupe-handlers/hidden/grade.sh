#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pytest test_handlers.py .bench_hidden/tests/test_dedupe.py -q
