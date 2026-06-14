#!/usr/bin/env bash
# Usage: bench/scripts/selfcheck.sh <task-name> | --all
# Proves: grade fails on untouched workspace AND passes on the reference solution.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

check_task() {
  local task="$1" dir tmp
  dir="$ROOT/bench/tasks/$task"
  [ -d "$dir" ] || { echo "no such task: $task"; return 1; }

  tmp="$(mktemp -d)"
  cp -R "$dir/workspace/." "$tmp/"
  mkdir -p "$tmp/.bench_hidden" && cp -R "$dir/hidden/." "$tmp/.bench_hidden/"
  if (cd "$tmp" && bash .bench_hidden/grade.sh >/dev/null 2>&1); then
    echo "FAIL [$task]: grade passes on untouched workspace"; rm -rf "$tmp"; return 1
  fi
  rm -rf "$tmp"

  tmp="$(mktemp -d)"
  cp -R "$dir/workspace/." "$tmp/"
  cp -R "$dir/hidden/reference/." "$tmp/"
  mkdir -p "$tmp/.bench_hidden" && cp -R "$dir/hidden/." "$tmp/.bench_hidden/"
  if ! (cd "$tmp" && bash .bench_hidden/grade.sh >/dev/null 2>&1); then
    echo "FAIL [$task]: grade fails on reference solution"; rm -rf "$tmp"; return 1
  fi
  rm -rf "$tmp"
  echo "OK   [$task]"
}

if [ "${1:-}" = "--all" ]; then
  rc=0
  for d in "$ROOT"/bench/tasks/*/; do check_task "$(basename "$d")" || rc=1; done
  exit $rc
else
  check_task "${1:?usage: selfcheck.sh <task-name>|--all}"
fi
