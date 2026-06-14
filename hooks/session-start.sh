#!/usr/bin/env bash
# SessionStart hook: stdout is appended to Claude's context at session start.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cat "${DIR}/../core/modelharness-core.md"
