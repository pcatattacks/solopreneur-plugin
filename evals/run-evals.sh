#!/bin/bash
# run-evals.sh - Run eval suite for Solopreneur plugin skills.
#
# Discovers skills/*/eval.csv files, invokes each test case via Claude Code CLI
# inside a sandboxed git worktree, grades outputs with an LLM rubric, and prints
# a summary table.
#
# Usage:
#   bash evals/run-evals.sh                  # Run all evals
#   bash evals/run-evals.sh discover         # Run evals for discover skill only
#   bash evals/run-evals.sh --dry            # Dry run (show test cases without executing)
#   bash evals/run-evals.sh discover --dry   # Dry run for one skill
#   bash evals/run-evals.sh --eval-model haiku --judge-model haiku  # Fast mode
#   bash evals/run-evals.sh --parallel       # Run skills in parallel (default: 5 concurrent)
#   bash evals/run-evals.sh --parallel 10    # Parallel with custom concurrency
#
# Flags:
#   --dry                Dry run (show test cases without executing)
#   --eval-model MODEL   Model for skill invocation (default: sonnet, env: EVAL_MODEL)
#   --judge-model MODEL  Model for rubric grading (default: sonnet, env: JUDGE_MODEL)
#   --parallel [N]       Run skills in parallel (default N=5, max concurrency)
#
# Environment variables (CLI flags take precedence):
#   EVAL_TIMEOUT Seconds per skill invocation (default: 900 = 15 min; 0 = no timeout)
#   JUDGE_TIMEOUT Seconds per judge call (default: 120 = 2 min; 0 = no timeout)
#
# Safety: Actual runs execute inside a temporary git worktree with
# --dangerously-skip-permissions so skills can write files and spawn subagents.
# The worktree is cleaned up automatically when the run finishes.

set -euo pipefail

PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EVAL_RUNS_BASE="$PLUGIN_DIR/.eval-runs"
RUBRIC_FILE="$SCRIPT_DIR/rubric.md"

EVAL_MODEL="${EVAL_MODEL:-sonnet}"
JUDGE_MODEL="${JUDGE_MODEL:-sonnet}"
EVAL_TIMEOUT="${EVAL_TIMEOUT:-900}"
JUDGE_TIMEOUT="${JUDGE_TIMEOUT:-120}"

# Check dependencies
for cmd in python3 git; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "Required command not found: $cmd" >&2
    exit 1
  fi
done
if ! command -v claude &>/dev/null; then
  echo "Claude CLI not found. Install: https://docs.anthropic.com/en/docs/claude-code" >&2
  exit 1
fi

# Detect timeout command (macOS: gtimeout from coreutils, Linux: timeout)
TIMEOUT_CMD=""
if [ "$EVAL_TIMEOUT" -gt 0 ] 2>/dev/null || [ "$JUDGE_TIMEOUT" -gt 0 ] 2>/dev/null; then
  if command -v timeout &>/dev/null; then
    TIMEOUT_CMD="timeout"
  elif command -v gtimeout &>/dev/null; then
    TIMEOUT_CMD="gtimeout"
  fi
fi

# Parse arguments
SKILL_FILTER="all"
DRY_RUN=false
PARALLEL=false
MAX_PARALLEL=5
while [ $# -gt 0 ]; do
  case "$1" in
    --dry) DRY_RUN=true ;;
    --eval-model) EVAL_MODEL="$2"; shift ;;
    --judge-model) JUDGE_MODEL="$2"; shift ;;
    --parallel)
      PARALLEL=true
      if [[ "${2:-}" =~ ^[0-9]+$ ]]; then
        [ "$2" -gt 0 ] && MAX_PARALLEL="$2"
        shift
      fi
      ;;
    *) SKILL_FILTER="$1" ;;
  esac
  shift
done

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
DIM='\033[2m'
NC='\033[0m'

# ─────────────────────────────────────────────────────────────────────────────
# Shared functions (used by both child and parent/sequential modes)
# ─────────────────────────────────────────────────────────────────────────────

# Parse CSV using python3 (handles quoted fields with commas)
parse_csv() {
  python3 -c "
import csv, json, sys
with open(sys.argv[1]) as f:
    reader = csv.DictReader(f)
    rows = list(reader)
print(json.dumps(rows))
" "$1"
}

# Negative-test patterns per skill (used to detect false triggers)
get_negative_patterns() {
  local skill=$1
  case "$skill" in
    discover) echo "Go/No-Go|Competitive Landscape|Market Size|Discovery Brief" ;;
    spec)     echo "User Stor|Acceptance Criteria|Technical Requirements|Out of Scope" ;;
    design)   echo "User Flow|Component|Visual Direction|design-brief|\.html|daisyui" ;;
    review)   echo "Critical|Warning|Suggestion|Positive|Severity" ;;
    backlog)  echo "Backlog|MVP|P1|P2|Depend|Acceptance Criteria|ticket" ;;
    scaffold) echo "Your AI Org|Employees.*Agents|SOPs.*Skills|org chart" ;;
    sprint)   echo "Sprint Complete|tickets built|BUILT|status: built" ;;
    *)        echo "" ;;
  esac
}

# Print the summary table and save artifacts
print_summary() {
  # Expects: TOTAL_PASS, TOTAL_FAIL, SUMMARY_LINES, EVAL_RUNS_DIR, RUN_TIMESTAMP set
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""
  printf "  %-12s %-22s %-10s %-8s %-6s %s\n" "Skill" "Test ID" "Type" "Result" "Score" "Notes"
  printf "  %-12s %-22s %-10s %-8s %-6s %s\n" "────────────" "──────────────────────" "──────────" "────────" "──────" "──────────────────────"
  echo -e "$SUMMARY_LINES" | while IFS='|' read -r skill id type result score notes; do
    [ -z "$skill" ] && continue
    printf "  %-12s %-22s %-10s %-8b %-6s %s\n" "$skill" "$id" "$type" "$result" "$score" "$notes"
  done
  echo ""
  echo -e "  Total: $((TOTAL_PASS + TOTAL_FAIL)) | ${GREEN}Pass: $TOTAL_PASS${NC} | ${RED}Fail: $TOTAL_FAIL${NC}"
  echo ""

  # Save summary to run dir and update latest symlink
  printf "%-12s %-22s %-10s %-8s %-6s %s\n" "Skill" "Test ID" "Type" "Result" "Score" "Notes" > "$EVAL_RUNS_DIR/summary.txt"
  echo -e "$SUMMARY_LINES" | sed 's/\x1b\[[0-9;]*m//g' | while IFS='|' read -r skill id type result score notes; do
    [ -z "$skill" ] && continue
    printf "%-12s %-22s %-10s %-8s %-6s %s\n" "$skill" "$id" "$type" "$result" "$score" "$notes"
  done >> "$EVAL_RUNS_DIR/summary.txt"
  echo "Total: $((TOTAL_PASS + TOTAL_FAIL)) | Pass: $TOTAL_PASS | Fail: $TOTAL_FAIL" >> "$EVAL_RUNS_DIR/summary.txt"
  ln -sfn "$RUN_TIMESTAMP" "$EVAL_RUNS_BASE/latest"

  echo -e "  Artifacts saved to: ${DIM}$EVAL_RUNS_DIR/${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Run all tests for a single skill. Populates CHILD_PASS, CHILD_FAIL, CHILD_SUMMARY.
# Expects: SKILL_NAME, CSV_FILE, RUN_DIR, EVAL_RUNS_DIR, EVAL_MODEL, JUDGE_MODEL,
#          EVAL_TIMEOUT, JUDGE_TIMEOUT, TIMEOUT_CMD, SCRIPT_DIR, RUBRIC_FILE set.
run_skill_tests() {
  CHILD_PASS=0
  CHILD_FAIL=0
  CHILD_SUMMARY=""

  ROWS=$(parse_csv "$CSV_FILE")
  ROW_COUNT=$(echo "$ROWS" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")

  for i in $(seq 0 $((ROW_COUNT - 1))); do
    ROW=$(echo "$ROWS" | python3 -c "import json,sys; r=json.load(sys.stdin)[$i]; print(json.dumps(r))")
    ID=$(echo "$ROW" | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")
    SHOULD_TRIGGER=$(echo "$ROW" | python3 -c "import json,sys; print(json.load(sys.stdin)['should_trigger'])")
    PROMPT=$(echo "$ROW" | python3 -c "import json,sys; print(json.load(sys.stdin)['prompt'])")
    EXPECTED=$(echo "$ROW" | python3 -c "import json,sys; print(json.load(sys.stdin)['expected_behaviors'])")

    if [ "$SHOULD_TRIGGER" = "true" ]; then
      TEST_TYPE="positive"
    else
      TEST_TYPE="negative"
    fi

    echo -e "  Running: ${BLUE}$ID${NC} ${DIM}(${TEST_TYPE})${NC}"
    echo -e "    Prompt: ${DIM}$PROMPT${NC}"

    # Create output directory for this skill
    SKILL_RUN_DIR="$EVAL_RUNS_DIR/$SKILL_NAME"
    mkdir -p "$SKILL_RUN_DIR"
    OUTPUT_FILE="$SKILL_RUN_DIR/${ID}.md"

    # Invoke skill inside the sandboxed worktree
    EVAL_MODE_ARGS=()
    if [ -f "$SCRIPT_DIR/eval-mode.txt" ]; then
      EVAL_MODE_ARGS=(--append-system-prompt-file "$SCRIPT_DIR/eval-mode.txt")
    fi
    SKILL_EXIT=0
    if [ -n "$TIMEOUT_CMD" ] && [ "$EVAL_TIMEOUT" -gt 0 ] 2>/dev/null; then
      echo "$PROMPT" | (cd "$RUN_DIR" && $TIMEOUT_CMD "$EVAL_TIMEOUT" claude --print --plugin-dir "$RUN_DIR" --model "$EVAL_MODEL" --max-turns 25 --dangerously-skip-permissions "${EVAL_MODE_ARGS[@]}") > "$OUTPUT_FILE" 2>&1 || SKILL_EXIT=$?
    else
      echo "$PROMPT" | (cd "$RUN_DIR" && claude --print --plugin-dir "$RUN_DIR" --model "$EVAL_MODEL" --max-turns 25 --dangerously-skip-permissions "${EVAL_MODE_ARGS[@]}") > "$OUTPUT_FILE" 2>&1 || SKILL_EXIT=$?
    fi
    if [ "$SKILL_EXIT" -eq 124 ]; then
      echo -e "    ${YELLOW}TIMEOUT${NC} after ${EVAL_TIMEOUT}s"
    fi
    OUTPUT=$(cat "$OUTPUT_FILE")

    if [ "$SHOULD_TRIGGER" = "true" ]; then
      # --- Positive test: grade with rubric ---
      RUBRIC_PROMPT=$(python3 -c "
import sys
template = open(sys.argv[1]).read()
result = template.replace('{SKILL_NAME}', sys.argv[2])
result = result.replace('{EXPECTED_BEHAVIORS}', sys.argv[3])
result = result.replace('{SKILL_OUTPUT}', '<see below>')
print(result)
" "$RUBRIC_FILE" "$SKILL_NAME" "$EXPECTED")
      FULL_JUDGE_PROMPT=$(printf "%s\n\n--- SKILL OUTPUT ---\n%s" "$RUBRIC_PROMPT" "$OUTPUT")

      if [ -n "$TIMEOUT_CMD" ] && [ "$JUDGE_TIMEOUT" -gt 0 ] 2>/dev/null; then
        JUDGE_RESPONSE=$(echo "$FULL_JUDGE_PROMPT" | $TIMEOUT_CMD "$JUDGE_TIMEOUT" claude --print --model "$JUDGE_MODEL" 2>/dev/null || echo '{"overall_pass": false, "score": 0, "checks": []}')
      else
        JUDGE_RESPONSE=$(echo "$FULL_JUDGE_PROMPT" | claude --print --model "$JUDGE_MODEL" 2>/dev/null || echo '{"overall_pass": false, "score": 0, "checks": []}')
      fi

      # Extract JSON from judge response (may have markdown fences)
      JUDGE_JSON=$(echo "$JUDGE_RESPONSE" | python3 -c "
import sys, json, re
text = sys.stdin.read()
# Try to find JSON in markdown code block
m = re.search(r'\`\`\`(?:json)?\s*(\{.*?\})\s*\`\`\`', text, re.DOTALL)
if m:
    text = m.group(1)
# Try to parse the whole thing as JSON
try:
    obj = json.loads(text.strip())
    print(json.dumps(obj))
except:
    # Last resort: find first { to last }
    start = text.find('{')
    end = text.rfind('}')
    if start >= 0 and end > start:
        try:
            obj = json.loads(text[start:end+1])
            print(json.dumps(obj))
        except:
            print(json.dumps({'overall_pass': False, 'score': 0, 'checks': []}))
    else:
        print(json.dumps({'overall_pass': False, 'score': 0, 'checks': []}))
" 2>/dev/null || echo '{"overall_pass": false, "score": 0, "checks": []}')

      PASS=$(echo "$JUDGE_JSON" | python3 -c "import json,sys; print(json.load(sys.stdin).get('overall_pass', False))")
      SCORE=$(echo "$JUDGE_JSON" | python3 -c "import json,sys; print(json.load(sys.stdin).get('score', 0))")
      NOTES=$(echo "$JUDGE_JSON" | python3 -c "
import json, sys
data = json.load(sys.stdin)
checks = data.get('checks', [])
failed = [c for c in checks if not c.get('pass', False)]
if failed:
    print('; '.join(c.get('notes','') for c in failed[:3]))
else:
    print('All checks passed')
")

      # Save judge output alongside skill output
      echo "$JUDGE_JSON" > "$SKILL_RUN_DIR/${ID}.judge.json"

      if [ "$PASS" = "True" ] || [ "$PASS" = "true" ]; then
        echo -e "    ${GREEN}PASS${NC} (score: $SCORE)"
        CHILD_PASS=$((CHILD_PASS + 1))
        CHILD_SUMMARY="${CHILD_SUMMARY}${SKILL_NAME}|${ID}|${TEST_TYPE}|${GREEN}PASS${NC}|${SCORE}|${NOTES}\n"
      else
        echo -e "    ${RED}FAIL${NC} (score: $SCORE) — $NOTES"
        CHILD_FAIL=$((CHILD_FAIL + 1))
        CHILD_SUMMARY="${CHILD_SUMMARY}${SKILL_NAME}|${ID}|${TEST_TYPE}|${RED}FAIL${NC}|${SCORE}|${NOTES}\n"
      fi

    else
      # --- Negative test: check for false trigger ---
      PATTERNS=$(get_negative_patterns "$SKILL_NAME")
      TRIGGERED=false

      if [ -n "$PATTERNS" ]; then
        IFS='|' read -ra PAT_ARRAY <<< "$PATTERNS"
        MATCHED_PATTERNS=""
        for pat in "${PAT_ARRAY[@]}"; do
          if echo "$OUTPUT" | grep -qi "$pat" 2>/dev/null; then
            TRIGGERED=true
            MATCHED_PATTERNS="${MATCHED_PATTERNS}${pat}, "
          fi
        done
      fi

      if [ "$TRIGGERED" = true ]; then
        echo -e "    ${RED}FAIL${NC} — skill falsely triggered (matched: ${MATCHED_PATTERNS%, })"
        CHILD_FAIL=$((CHILD_FAIL + 1))
        CHILD_SUMMARY="${CHILD_SUMMARY}${SKILL_NAME}|${ID}|${TEST_TYPE}|${RED}FAIL${NC}|-|False trigger: ${MATCHED_PATTERNS%, }\n"
      else
        echo -e "    ${GREEN}PASS${NC} — skill correctly did not trigger"
        CHILD_PASS=$((CHILD_PASS + 1))
        CHILD_SUMMARY="${CHILD_SUMMARY}${SKILL_NAME}|${ID}|${TEST_TYPE}|${GREEN}PASS${NC}|-|Correctly not triggered\n"
      fi
    fi

    echo ""
  done
}

# Clean up stale eval branches that don't have active worktrees
cleanup_stale_branches() {
  git -C "$PLUGIN_DIR" branch --list 'eval-sandbox-*' 2>/dev/null | tr -d ' ' | while read -r branch; do
    [ -z "$branch" ] && continue
    # Skip branches with active worktrees (may belong to another running eval)
    if git -C "$PLUGIN_DIR" worktree list --porcelain 2>/dev/null | grep -q "branch refs/heads/$branch"; then
      continue
    fi
    git -C "$PLUGIN_DIR" branch -q -D "$branch" 2>/dev/null || true
  done
}

# ─────────────────────────────────────────────────────────────────────────────
# Child mode: invoked by parallel parent to run one skill's tests
# ─────────────────────────────────────────────────────────────────────────────

if [ "${_EVAL_CHILD:-}" = "1" ]; then
  # Child receives: SKILL_FILTER (positional), _EVAL_RUNS_DIR, _EVAL_RESULTS_DIR as env vars
  if [ "$SKILL_FILTER" = "all" ]; then
    echo "Child mode requires a single skill filter" >&2
    exit 1
  fi

  CSV_FILE="$PLUGIN_DIR/skills/${SKILL_FILTER}/eval.csv"
  if [ ! -f "$CSV_FILE" ]; then
    echo "No eval file: $CSV_FILE" >&2
    exit 1
  fi
  if [ ! -f "$RUBRIC_FILE" ]; then
    echo "Rubric not found: $RUBRIC_FILE" >&2
    exit 1
  fi

  SKILL_NAME="$SKILL_FILTER"
  EVAL_RUNS_DIR="$_EVAL_RUNS_DIR"

  # Create child's own worktree (unique PID + skill name ensures no collisions)
  WORKTREE_BRANCH="eval-sandbox-$$-${SKILL_NAME}"
  WORKTREE_DIR=$(mktemp -d "${TMPDIR:-/tmp}/solopreneur-eval.XXXXXX")
  # Clean up this specific branch in case of PID reuse from a crashed run
  git -C "$PLUGIN_DIR" branch -q -D "$WORKTREE_BRANCH" 2>/dev/null || true
  git -C "$PLUGIN_DIR" worktree add -q -b "$WORKTREE_BRANCH" "$WORKTREE_DIR" HEAD
  RUN_DIR="$WORKTREE_DIR"

  child_cleanup() {
    if [ -n "$WORKTREE_DIR" ] && [ -d "$WORKTREE_DIR" ]; then
      git -C "$PLUGIN_DIR" worktree remove --force "$WORKTREE_DIR" 2>/dev/null || true
      git -C "$PLUGIN_DIR" branch -q -D "$WORKTREE_BRANCH" 2>/dev/null || true
    fi
  }
  trap child_cleanup EXIT

  # Run tests
  run_skill_tests

  # Write results atomically
  echo -e "pass=$CHILD_PASS\nfail=$CHILD_FAIL" > "$_EVAL_RESULTS_DIR/${SKILL_NAME}.result.tmp"
  mv "$_EVAL_RESULTS_DIR/${SKILL_NAME}.result.tmp" "$_EVAL_RESULTS_DIR/${SKILL_NAME}.result"
  printf "%b" "$CHILD_SUMMARY" > "$_EVAL_RESULTS_DIR/${SKILL_NAME}.summary.tmp"
  mv "$_EVAL_RESULTS_DIR/${SKILL_NAME}.summary.tmp" "$_EVAL_RESULTS_DIR/${SKILL_NAME}.summary"

  exit 0
fi

# ─────────────────────────────────────────────────────────────────────────────
# Parent mode: banner, discovery, and orchestration
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Solopreneur Eval Runner${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${DIM}  eval model: $EVAL_MODEL | judge model: $JUDGE_MODEL${NC}"
echo ""

# Find eval CSVs (always from the real plugin dir, not the worktree)
if [ "$SKILL_FILTER" = "all" ]; then
  CSV_FILES=$(find "$PLUGIN_DIR/skills" -name "eval.csv" 2>/dev/null | sort)
else
  CSV_FILES="$PLUGIN_DIR/skills/${SKILL_FILTER}/eval.csv"
  if [ ! -f "$CSV_FILES" ]; then
    echo -e "${RED}No eval file found: $CSV_FILES${NC}"
    exit 1
  fi
fi

if [ -z "$CSV_FILES" ]; then
  echo -e "${RED}No eval.csv files found in skills/*/${NC}"
  exit 1
fi

# Check rubric exists (only needed for actual runs)
if [ "$DRY_RUN" = false ] && [ ! -f "$RUBRIC_FILE" ]; then
  echo -e "${RED}Rubric not found: $RUBRIC_FILE${NC}"
  exit 1
fi

# ─────────────────────────────────────────────────────────────────────────────
# Dry run mode
# ─────────────────────────────────────────────────────────────────────────────

if [ "$DRY_RUN" = true ]; then
  TOTAL_TESTS=0
  for CSV_FILE in $CSV_FILES; do
    SKILL_NAME=$(basename "$(dirname "$CSV_FILE")")
    echo -e "${YELLOW}Skill: /solopreneur:${SKILL_NAME}${NC}"
    echo "─────────────────────────────────────"

    ROWS=$(parse_csv "$CSV_FILE")
    ROW_COUNT=$(echo "$ROWS" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")

    for i in $(seq 0 $((ROW_COUNT - 1))); do
      ROW=$(echo "$ROWS" | python3 -c "import json,sys; r=json.load(sys.stdin)[$i]; print(json.dumps(r))")
      ID=$(echo "$ROW" | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")
      SHOULD_TRIGGER=$(echo "$ROW" | python3 -c "import json,sys; print(json.load(sys.stdin)['should_trigger'])")
      PROMPT=$(echo "$ROW" | python3 -c "import json,sys; print(json.load(sys.stdin)['prompt'])")
      EXPECTED=$(echo "$ROW" | python3 -c "import json,sys; print(json.load(sys.stdin)['expected_behaviors'])")

      TOTAL_TESTS=$((TOTAL_TESTS + 1))
      TEST_TYPE="positive"
      [ "$SHOULD_TRIGGER" != "true" ] && TEST_TYPE="negative"

      echo -e "  ${BLUE}[DRY]${NC} ${DIM}${TEST_TYPE}${NC} $ID"
      echo -e "        Prompt: $PROMPT"
      echo -e "        Expected: $EXPECTED"
      echo ""
    done
    echo ""
  done

  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${YELLOW}Dry run complete.${NC} Found $TOTAL_TESTS test cases across $(echo "$CSV_FILES" | wc -l | tr -d ' ') skill(s)."
  echo "Remove --dry to execute evals."
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  exit 0
fi

# ─────────────────────────────────────────────────────────────────────────────
# Parallel mode: one child process per skill
# ─────────────────────────────────────────────────────────────────────────────

if [ "$PARALLEL" = true ] && [ "$SKILL_FILTER" = "all" ]; then
  # Clean up stale branches from previous crashed runs (safe: no children yet)
  cleanup_stale_branches

  RUN_TIMESTAMP=$(date +%Y-%m-%dT%H-%M-%S)
  EVAL_RUNS_DIR="$EVAL_RUNS_BASE/$RUN_TIMESTAMP"
  mkdir -p "$EVAL_RUNS_DIR"
  RESULTS_DIR=$(mktemp -d "${TMPDIR:-/tmp}/eval-results.XXXXXX")
  LOGS_DIR="$EVAL_RUNS_DIR/logs"
  mkdir -p "$LOGS_DIR"

  # Build skill array
  SKILL_ARRAY=()
  for csv in $CSV_FILES; do
    SKILL_ARRAY+=("$(basename "$(dirname "$csv")")")
  done
  TOTAL_SKILLS=${#SKILL_ARRAY[@]}

  echo -e "${YELLOW}Parallel mode:${NC} ${TOTAL_SKILLS} skills, max ${MAX_PARALLEL} concurrent"
  echo ""

  # Signal handler: kill all children on interrupt
  ALL_CHILD_PIDS=()
  parallel_cleanup() {
    echo -e "\n${RED}  Interrupted. Stopping child processes...${NC}"
    for pid in "${ALL_CHILD_PIDS[@]}"; do
      kill "$pid" 2>/dev/null || true
    done
    wait 2>/dev/null || true
    rm -rf "$RESULTS_DIR"
  }
  trap parallel_cleanup INT TERM

  # Batch loop (bash 3.2 compatible)
  for ((batch_start=0; batch_start<TOTAL_SKILLS; batch_start+=MAX_PARALLEL)); do
    BATCH_PIDS=()
    BATCH_SKILLS=()
    for ((j=batch_start; j<batch_start+MAX_PARALLEL && j<TOTAL_SKILLS; j++)); do
      skill="${SKILL_ARRAY[$j]}"
      BATCH_SKILLS+=("$skill")
      echo -e "  ${BLUE}Starting:${NC} $skill"

      _EVAL_CHILD=1 \
        _EVAL_RUNS_DIR="$EVAL_RUNS_DIR" \
        _EVAL_RESULTS_DIR="$RESULTS_DIR" \
        EVAL_MODEL="$EVAL_MODEL" \
        JUDGE_MODEL="$JUDGE_MODEL" \
        EVAL_TIMEOUT="$EVAL_TIMEOUT" \
        JUDGE_TIMEOUT="$JUDGE_TIMEOUT" \
        bash "$0" "$skill" \
        > "$LOGS_DIR/${skill}.log" 2>&1 &
      BATCH_PIDS+=($!)
      ALL_CHILD_PIDS+=($!)
    done

    echo -e "  ${DIM}Waiting for batch: ${BATCH_SKILLS[*]}...${NC}"
    echo ""

    for pid in "${BATCH_PIDS[@]}"; do
      wait "$pid" 2>/dev/null || true
    done

    # Report batch completions
    for skill in "${BATCH_SKILLS[@]}"; do
      if [ -f "$RESULTS_DIR/${skill}.result" ]; then
        pass=$(grep '^pass=' "$RESULTS_DIR/${skill}.result" | cut -d= -f2)
        fail=$(grep '^fail=' "$RESULTS_DIR/${skill}.result" | cut -d= -f2)
        if [ "${fail:-0}" -gt 0 ]; then
          echo -e "  ${RED}Done:${NC} $skill (${pass:-0} pass, ${fail:-0} fail)"
        else
          echo -e "  ${GREEN}Done:${NC} $skill (${pass:-0} pass, ${fail:-0} fail)"
        fi
      else
        echo -e "  ${RED}CRASH:${NC} $skill ${DIM}(check $LOGS_DIR/${skill}.log)${NC}"
      fi
    done
    echo ""
  done

  # Aggregate results
  TOTAL_PASS=0
  TOTAL_FAIL=0
  SUMMARY_LINES=""
  for skill in "${SKILL_ARRAY[@]}"; do
    result_file="$RESULTS_DIR/${skill}.result"
    summary_file="$RESULTS_DIR/${skill}.summary"
    if [ -f "$result_file" ] && grep -q '^fail=' "$result_file"; then
      pass=$(grep '^pass=' "$result_file" | cut -d= -f2)
      fail=$(grep '^fail=' "$result_file" | cut -d= -f2)
      TOTAL_PASS=$((TOTAL_PASS + ${pass:-0}))
      TOTAL_FAIL=$((TOTAL_FAIL + ${fail:-0}))
    else
      # Child crashed or produced incomplete results
      TOTAL_FAIL=$((TOTAL_FAIL + 1))
      SUMMARY_LINES="${SUMMARY_LINES}${skill}|-|crash|${RED}FAIL${NC}|-|Child process crashed (check logs/${skill}.log)\n"
    fi
    if [ -f "$summary_file" ]; then
      SUMMARY_LINES="${SUMMARY_LINES}$(cat "$summary_file")"
    fi
  done

  # Clean up temp results dir
  rm -rf "$RESULTS_DIR"

  # Print summary and exit
  echo -e "  ${DIM}Per-skill logs: $LOGS_DIR/${NC}"
  echo ""
  print_summary

  if [ "$TOTAL_FAIL" -gt 0 ]; then
    exit 1
  fi
  exit 0
fi

# ─────────────────────────────────────────────────────────────────────────────
# Sequential mode (default): single worktree, all skills in series
# ─────────────────────────────────────────────────────────────────────────────

# --- Worktree setup ---
WORKTREE_DIR=""
WORKTREE_BRANCH=""
RUN_DIR="$PLUGIN_DIR"

setup_worktree() {
  cleanup_stale_branches

  WORKTREE_BRANCH="eval-sandbox-$$"
  WORKTREE_DIR=$(mktemp -d "${TMPDIR:-/tmp}/solopreneur-eval.XXXXXX")

  echo -e "${DIM}  Setting up sandbox worktree...${NC}"
  git -C "$PLUGIN_DIR" worktree add -q -b "$WORKTREE_BRANCH" "$WORKTREE_DIR" HEAD
  RUN_DIR="$WORKTREE_DIR"

  echo -e "${DIM}  Sandbox: $WORKTREE_DIR${NC}"
  echo ""
}

cleanup_worktree() {
  if [ -n "$WORKTREE_DIR" ] && [ -d "$WORKTREE_DIR" ]; then
    echo -e "${DIM}  Cleaning up sandbox worktree...${NC}"
    git -C "$PLUGIN_DIR" worktree remove --force "$WORKTREE_DIR" 2>/dev/null || true
    git -C "$PLUGIN_DIR" branch -q -D "$WORKTREE_BRANCH" 2>/dev/null || true
  fi
}

setup_worktree
trap cleanup_worktree EXIT

RUN_TIMESTAMP=$(date +%Y-%m-%dT%H-%M-%S)
EVAL_RUNS_DIR="$EVAL_RUNS_BASE/$RUN_TIMESTAMP"
mkdir -p "$EVAL_RUNS_DIR"

# Summary accumulators
TOTAL_PASS=0
TOTAL_FAIL=0
SUMMARY_LINES=""

for CSV_FILE in $CSV_FILES; do
  SKILL_NAME=$(basename "$(dirname "$CSV_FILE")")

  echo -e "${YELLOW}Skill: /solopreneur:${SKILL_NAME}${NC}"
  echo "─────────────────────────────────────"

  run_skill_tests

  TOTAL_PASS=$((TOTAL_PASS + CHILD_PASS))
  TOTAL_FAIL=$((TOTAL_FAIL + CHILD_FAIL))
  SUMMARY_LINES="${SUMMARY_LINES}${CHILD_SUMMARY}"

  echo ""
done

# --- Summary ---
print_summary

# Exit non-zero if any test failed (CI-friendly)
if [ "$TOTAL_FAIL" -gt 0 ]; then
  exit 1
fi
