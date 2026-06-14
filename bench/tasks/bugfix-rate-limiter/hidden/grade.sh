#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pytest .bench_hidden/tests test_limiter_basic.py -q
