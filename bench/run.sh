#!/usr/bin/env bash
# Usage: bench/run.sh --config bare|plugin|sonnet|sonnet-plugin|haiku|haiku-plugin|fable|fable-plugin [--core PATH] [--task NAME] [--reps 3] [--start-rep K]
# Appends one CSV row per run to bench/results/results.csv:
# timestamp,task,category,config,rep,pass,cost_usd,duration_s,num_turns,asked_question
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG="" TASK_FILTER="" REPS=3 START_REP=1 CORE_PATH=""

while [ $# -gt 0 ]; do
  case "$1" in
    --config)    CONFIG="$2"; shift 2 ;;
    --core)      CORE_PATH="$2"; shift 2 ;;
    --task)      TASK_FILTER="$2"; shift 2 ;;
    --reps)      REPS="$2"; shift 2 ;;
    --start-rep) START_REP="$2"; shift 2 ;;
    *) echo "unknown arg: $1"; exit 2 ;;
  esac
done

case "$CONFIG" in
  bare)          MODEL="claude-opus-4-8" ;;
  plugin)        MODEL="claude-opus-4-8" ;;
  sonnet)        MODEL="claude-sonnet-4-6" ;;
  sonnet-plugin) MODEL="claude-sonnet-4-6" ;;
  haiku)         MODEL="claude-haiku-4-5" ;;
  haiku-plugin)  MODEL="claude-haiku-4-5" ;;
  fable)         MODEL="claude-fable-5" ;;
  fable-plugin)  MODEL="claude-fable-5" ;;
  *) echo "usage: --config bare|plugin|sonnet|sonnet-plugin|haiku|haiku-plugin|fable|fable-plugin [--core PATH] [--task NAME] [--reps N] [--start-rep K]"; exit 2 ;;
esac

# Default core path; validate when config uses the plugin preamble
[ -z "$CORE_PATH" ] && CORE_PATH="$ROOT/core/modelharness-core.md"
is_plugin_config() { case "$1" in plugin|sonnet-plugin|haiku-plugin|fable-plugin) return 0 ;; *) return 1 ;; esac }
if is_plugin_config "$CONFIG" && [ ! -f "$CORE_PATH" ]; then
  echo "error: core file not found: $CORE_PATH"; exit 2
fi

command -v claude >/dev/null || { echo "claude CLI not found"; exit 1; }
command -v jq >/dev/null || { echo "jq not found"; exit 1; }

# macOS-compatible timeout wrapper: prefers the system `timeout`, then `gtimeout`
# (brew coreutils), then a perl-based fallback.
run_with_timeout() {
  local secs="$1"; shift
  if command -v timeout >/dev/null 2>&1; then
    timeout "$secs" "$@"
  elif command -v gtimeout >/dev/null 2>&1; then
    gtimeout "$secs" "$@"
  else
    perl -e '
      my ($secs, @cmd) = @ARGV;
      $SIG{ALRM} = sub { kill "TERM", -$$; exit 124 };
      alarm $secs;
      my $rc = system @cmd;
      alarm 0;
      exit($rc >> 8);
    ' "$secs" "$@"
  fi
}

RESULTS="$ROOT/bench/results/results.csv"
mkdir -p "$ROOT/bench/results"
[ -f "$RESULTS" ] || echo "timestamp,task,category,config,rep,pass,cost_usd,duration_s,num_turns,asked_question" > "$RESULTS"

# modelharness injection for the "plugin" config: same content the SessionStart hook
# injects, delivered via --append-system-prompt (deterministic in headless mode).
# Skills are referenced by absolute path since plugin discovery isn't active here.
build_preamble() {
  cat "$CORE_PATH"
  cat <<EOF

(modelharness note for this headless session: when the core says to load a skill,
Read the file instead: verification-loop -> $ROOT/skills/verification-loop/SKILL.md,
memory-discipline -> $ROOT/skills/memory-discipline/SKILL.md,
delegation-triggers -> $ROOT/skills/delegation-triggers/SKILL.md.
For fresh-context verification, dispatch a general-purpose subagent with the
instructions in $ROOT/agents/verifier.md.)
EOF
}

shopt -s nullglob
for task_dir in "$ROOT"/bench/tasks/*/; do
  task="$(basename "$task_dir")"
  [ -n "$TASK_FILTER" ] && [ "$task" != "$TASK_FILTER" ] && continue
  category="$(jq -r '.category' "$task_dir/meta.json")"
  timeout_s="$(jq -r '.timeout_seconds' "$task_dir/meta.json")"
  max_turns="$(jq -r '.max_turns' "$task_dir/meta.json")"
  phases="$(jq -r '.phases // 1' "$task_dir/meta.json")"

  for rep in $(seq "$START_REP" "$REPS"); do
    work="$(mktemp -d)"
    # Ensure the temp workspace is removed on ANY failure path (set -e aborts the
    # script mid-rep; the EXIT trap then cleans up the current $work).
    trap 'rm -rf "$work"' EXIT
    cp -R "$task_dir/workspace/." "$work/"
    git -C "$work" init -q && git -C "$work" add -A && git -C "$work" -c user.email=b@b -c user.name=bench commit -qm init

    duration=0 claude_rc=0 out=""

    # run_phase <prompt-file>: runs one fresh `claude -p` invocation in $work with the
    # task's model/config flags. A separate `claude -p` call IS a fresh session (no
    # conversation carryover) sharing the same workdir. Applies the 429 retry logic
    # independently per phase. Because phase>1 runs over the prior phase's in-progress
    # work, a 429 retry must NOT reset the workspace; it simply re-invokes claude in
    # place. Sets globals `out` (raw JSON) and `claude_rc`; adds elapsed to `duration`.
    run_phase() {
      local prompt_file="$1"
      local p_args=(-p "$(cat "$prompt_file")" --model "$MODEL" --output-format json
            --dangerously-skip-permissions --max-turns "$max_turns")
      is_plugin_config "$CONFIG" && p_args+=(--append-system-prompt "$(build_preamble)")

      local attempt=0 p_start p_dur
      while true; do
        attempt=$(( attempt + 1 ))
        p_start="$(date +%s)"
        set +e
        out="$(cd "$work" && run_with_timeout "$timeout_s" claude "${p_args[@]}" 2>"$work/.stderr")"
        claude_rc=$?
        set -e
        p_dur=$(( $(date +%s) - p_start ))

        # Detect transient API errors: 429 (rate limit) and 529 (overloaded)
        local api_err
        api_err="$(echo "$out" | jq -r '.api_error_status // empty' 2>/dev/null || echo "")"
        if [ "$api_err" = "429" ] || [ "$api_err" = "529" ]; then
          if [ "$attempt" -ge 24 ]; then
            echo "[$CONFIG/$task/rep$rep] API-$api_err — exhausted 24 attempts (6h), aborting run"
            exit 3
          fi
          echo "[$CONFIG/$task/rep$rep] API-$api_err — waiting 15m (attempt $attempt/24)"
          sleep 900
          continue
        fi
        break
      done
      duration=$(( duration + p_dur ))
    }

    # Phase 1 (PROMPT.md). 429 retries handled inside run_phase. A terminal non-429
    # error in phase 1 does NOT abort a two-phase task: we still attempt phase 2 (the
    # task tests cross-session recovery).
    run_phase "$task_dir/PROMPT.md"

    if [ "$phases" -ge 2 ]; then
      # Single-phase cost/turns are read directly below (byte-identical CSV).
      # For two-phase tasks we sum across phases; capture phase 1's values now.
      cost1="$(echo "$out" | jq -r '.total_cost_usd // 0' 2>/dev/null || echo 0)"
      turns1="$(echo "$out" | jq -r '.num_turns // 0' 2>/dev/null || echo 0)"

      # Phase 2 (PROMPT2.md): a SEPARATE fresh session in the SAME workdir. Grading
      # happens only after phase 2 completes.
      run_phase "$task_dir/PROMPT2.md"
    fi

    result_text="$(echo "$out" | jq -r '.result // ""' 2>/dev/null || echo "")"
    asked=0
    echo "$result_text" | tail -3 | grep -q '?[[:space:]]*$' && asked=1

    if [ "$phases" -ge 2 ]; then
      cost2="$(echo "$out" | jq -r '.total_cost_usd // 0' 2>/dev/null || echo 0)"
      turns2="$(echo "$out" | jq -r '.num_turns // 0' 2>/dev/null || echo 0)"
      cost="$(awk -v a="$cost1" -v b="$cost2" 'BEGIN{print a+b}')"
      turns=$(( turns1 + turns2 ))
    else
      cost="$(echo "$out" | jq -r '.total_cost_usd // "NA"' 2>/dev/null || echo NA)"
      turns="$(echo "$out" | jq -r '.num_turns // "NA"' 2>/dev/null || echo NA)"
    fi

    mkdir -p "$work/.bench_hidden" && cp -R "$task_dir/hidden/." "$work/.bench_hidden/"
    pass=0
    (cd "$work" && bash .bench_hidden/grade.sh > "$work/.grade.log" 2>&1) && pass=1

    echo "$(date -u +%FT%TZ),$task,$category,$CONFIG,$rep,$pass,$cost,$duration,$turns,$asked" >> "$RESULTS"
    echo "[$CONFIG/$task/rep$rep] pass=$pass cost=$cost dur=${duration}s turns=$turns rc=$claude_rc"

    keep_dir="$ROOT/bench/results/runs/$CONFIG-$task-rep$rep-$(date +%s)"
    mkdir -p "$keep_dir"
    cp "$work/.grade.log" "$keep_dir/" 2>/dev/null || true
    cp "$work/.stderr" "$keep_dir/claude-stderr.log" 2>/dev/null || true
    echo "$out" > "$keep_dir/claude-output.json"
    rm -rf "$work"
  done
done
echo "done -> $RESULTS"
