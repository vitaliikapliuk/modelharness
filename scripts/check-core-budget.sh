#!/usr/bin/env bash
# Fails if core/modelharness-core.md exceeds the 2K-token budget (heuristic: 1 token ≈ 4 chars).
set -euo pipefail
FILE="$(cd "$(dirname "$0")" && pwd)/../core/modelharness-core.md"
MAX_CHARS=8000
chars=$(wc -c < "$FILE")
echo "core size: ${chars} chars (budget: ${MAX_CHARS} ≈ 2000 tokens)"
[ "$chars" -le "$MAX_CHARS" ] || { echo "FAIL: core exceeds token budget"; exit 1; }
echo "PASS"
