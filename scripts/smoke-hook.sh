#!/usr/bin/env bash
# Verifies the SessionStart hook emits the behavioral core on stdout.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
out="$("$ROOT/hooks/session-start.sh")"
echo "$out" | grep -q "modelharness — Behavioral Core" || { echo "FAIL: core header missing"; exit 1; }
echo "$out" | grep -q "Grounded progress" || { echo "FAIL: pattern 1 missing"; exit 1; }
python3 -c "import json,sys; json.load(open('$ROOT/.claude-plugin/plugin.json')); json.load(open('$ROOT/hooks/hooks.json')); json.load(open('$ROOT/.claude-plugin/marketplace.json'))" \
  || { echo "FAIL: invalid JSON"; exit 1; }
echo "PASS"
