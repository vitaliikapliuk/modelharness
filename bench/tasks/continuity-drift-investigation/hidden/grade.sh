#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pytest test_report_visible.py .bench_hidden/tests -q
