#!/bin/bash
# run-evals.sh - Run eval suite for your plugin's skills.
#
# Discovers skills/*/eval.csv files, invokes each test case via Claude Code CLI
# inside a sandboxed git worktree, grades outputs with an LLM rubric, and prints
# a summary table.
#
# Usage:
#   bash evals/run-evals.sh                  # Run all evals
#   bash evals/run-evals.sh [skill-name]     # Run evals for one skill
#   bash evals/run-evals.sh --dry            # Dry run (show test cases)
#   bash evals/run-evals.sh [skill] --dry    # Dry run for one skill
#   bash evals/run-evals.sh --eval-model haiku --judge-model haiku  # Fast mode
#
# Flags:
#   --dry                Dry run (show test cases without executing)
#   --eval-model MODEL   Model for skill invocation (default: sonnet, env: EVAL_MODEL)
#   --judge-model MODEL  Model for rubric grading (default: sonnet, env: JUDGE_MODEL)
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
EVAL_RUNS_DIR="$PLUGIN_DIR/.eval-runs"
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
while [ $# -gt 0 ]; do
  case "$1" in
    --dry) DRY_RUN=true ;;
    --eval-model) EVAL_MODEL="$2"; shift ;;
    --judge-model) JUDGE_MODEL="$2"; shift ;;
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

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Eval Runner${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${DIM}  eval model: $EVAL_MODEL | judge model: $JUDGE_MODEL${NC}"
echo ""

# Find eval CSVs - check both plugin-style (skills/) and project-style (.claude/skills/)
if [ "$SKILL_FILTER" = "all" ]; then
  CSV_FILES=""
  for search_dir in "$PLUGIN_DIR/skills" "$PLUGIN_DIR/.claude/skills"; do
    if [ -d "$search_dir" ]; then
      CSV_FILES="$CSV_FILES $(find "$search_dir" -name "eval.csv" 2>/dev/null)"
    fi
  done
  CSV_FILES=$(echo "$CSV_FILES" | tr ' ' '\n' | sort | grep -v '^$')
else
  if [ -f "$PLUGIN_DIR/skills/${SKILL_FILTER}/eval.csv" ]; then
    CSV_FILES="$PLUGIN_DIR/skills/${SKILL_FILTER}/eval.csv"
  elif [ -f "$PLUGIN_DIR/.claude/skills/${SKILL_FILTER}/eval.csv" ]; then
    CSV_FILES="$PLUGIN_DIR/.claude/skills/${SKILL_FILTER}/eval.csv"
  else
    echo -e "${RED}No eval file found for: $SKILL_FILTER${NC}"
    exit 1
  fi
fi

if [ -z "$CSV_FILES" ]; then
  echo -e "${RED}No eval.csv files found in skills/ or .claude/skills/${NC}"
  exit 1
fi

# Check rubric exists (only needed for actual runs)
if [ "$DRY_RUN" = false ] && [ ! -f "$RUBRIC_FILE" ]; then
  echo -e "${RED}Rubric not found: $RUBRIC_FILE${NC}"
  exit 1
fi

# --- Worktree setup (only for actual runs) ---
WORKTREE_DIR=""
WORKTREE_BRANCH=""
RUN_DIR="$PLUGIN_DIR"  # Where claude is invoked from (worktree during real runs)

setup_worktree() {
  # Clean up stale eval branches from previous crashed runs
  git -C "$PLUGIN_DIR" branch --list 'eval-sandbox-*' 2>/dev/null | tr -d ' ' | while read -r branch; do
    [ -z "$branch" ] && continue
    git -C "$PLUGIN_DIR" worktree remove --force "$branch" 2>/dev/null || true
    git -C "$PLUGIN_DIR" branch -q -D "$branch" 2>/dev/null || true
  done

  WORKTREE_BRANCH="eval-sandbox-$$"
  WORKTREE_DIR=$(mktemp -d "${TMPDIR:-/tmp}/eval-sandbox.XXXXXX")

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

if [ "$DRY_RUN" = false ]; then
  setup_worktree
  trap cleanup_worktree EXIT
  mkdir -p "$EVAL_RUNS_DIR"
fi

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

# Grade a test case using the rubric (works for both positive and negative tests)
grade_with_rubric() {
  local skill_name=$1
  local expected=$2
  local output=$3
  local output_file=$4

  RUBRIC_PROMPT=$(python3 -c "
import sys
template = open(sys.argv[1]).read()
result = template.replace('{SKILL_NAME}', sys.argv[2])
result = result.replace('{EXPECTED_BEHAVIORS}', sys.argv[3])
result = result.replace('{SKILL_OUTPUT}', '<see below>')
print(result)
" "$RUBRIC_FILE" "$skill_name" "$expected")
  FULL_JUDGE_PROMPT=$(printf "%s\n\n--- SKILL OUTPUT ---\n%s" "$RUBRIC_PROMPT" "$output")

  if [ -n "$TIMEOUT_CMD" ] && [ "$JUDGE_TIMEOUT" -gt 0 ] 2>/dev/null; then
    JUDGE_RESPONSE=$(echo "$FULL_JUDGE_PROMPT" | $TIMEOUT_CMD "$JUDGE_TIMEOUT" claude --print --model "$JUDGE_MODEL" 2>/dev/null || echo '{"overall_pass": false, "score": 0, "checks": []}')
  else
    JUDGE_RESPONSE=$(echo "$FULL_JUDGE_PROMPT" | claude --print --model "$JUDGE_MODEL" 2>/dev/null || echo '{"overall_pass": false, "score": 0, "checks": []}')
  fi

  # Extract JSON from judge response (may have markdown fences)
  echo "$JUDGE_RESPONSE" | python3 -c "
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
" 2>/dev/null || echo '{"overall_pass": false, "score": 0, "checks": []}'
}

# Summary accumulators
TOTAL_PASS=0
TOTAL_FAIL=0
TOTAL_TESTS=0
SUMMARY_LINES=""

for CSV_FILE in $CSV_FILES; do
  # Extract skill name from path: skills/<name>/eval.csv
  SKILL_NAME=$(basename "$(dirname "$CSV_FILE")")

  echo -e "${YELLOW}Skill: ${SKILL_NAME}${NC}"
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

    if [ "$SHOULD_TRIGGER" = "true" ]; then
      TEST_TYPE="positive"
    else
      TEST_TYPE="negative"
    fi

    # --- Dry run ---
    if [ "$DRY_RUN" = true ]; then
      echo -e "  ${BLUE}[DRY]${NC} ${DIM}${TEST_TYPE}${NC} $ID"
      echo -e "        Prompt: $PROMPT"
      echo -e "        Expected: $EXPECTED"
      echo ""
      continue
    fi

    # --- Actual run ---
    echo -e "  Running: ${BLUE}$ID${NC} ${DIM}(${TEST_TYPE})${NC}"
    echo -e "    Prompt: ${DIM}$PROMPT${NC}"

    # Create output directory for this skill
    SKILL_RUN_DIR="$EVAL_RUNS_DIR/$SKILL_NAME"
    mkdir -p "$SKILL_RUN_DIR"
    OUTPUT_FILE="$SKILL_RUN_DIR/${ID}.md"

    # Invoke skill inside the sandboxed worktree (max-turns prevents runaway execution)
    # Append eval-mode system prompt to skip interactive questions
    EVAL_MODE_ARGS=()
    if [ -f "$SCRIPT_DIR/eval-mode.txt" ]; then
      EVAL_MODE_ARGS=(--append-system-prompt-file "$SCRIPT_DIR/eval-mode.txt")
    fi
    SKILL_EXIT=0
    if [ -n "$TIMEOUT_CMD" ] && [ "$EVAL_TIMEOUT" -gt 0 ] 2>/dev/null; then
      echo "$PROMPT" | $TIMEOUT_CMD "$EVAL_TIMEOUT" claude --print --plugin-dir "$RUN_DIR" --model "$EVAL_MODEL" --max-turns 25 --dangerously-skip-permissions "${EVAL_MODE_ARGS[@]}" > "$OUTPUT_FILE" 2>&1 || SKILL_EXIT=$?
    else
      echo "$PROMPT" | claude --print --plugin-dir "$RUN_DIR" --model "$EVAL_MODEL" --max-turns 25 --dangerously-skip-permissions "${EVAL_MODE_ARGS[@]}" > "$OUTPUT_FILE" 2>&1 || SKILL_EXIT=$?
    fi
    if [ "$SKILL_EXIT" -eq 124 ]; then
      echo -e "    ${YELLOW}TIMEOUT${NC} after ${EVAL_TIMEOUT}s"
    fi
    OUTPUT=$(cat "$OUTPUT_FILE")

    # Grade with rubric (same path for positive and negative tests)
    JUDGE_JSON=$(grade_with_rubric "$SKILL_NAME" "$EXPECTED" "$OUTPUT" "$OUTPUT_FILE")

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
      TOTAL_PASS=$((TOTAL_PASS + 1))
      SUMMARY_LINES="${SUMMARY_LINES}${SKILL_NAME}|${ID}|${TEST_TYPE}|${GREEN}PASS${NC}|${SCORE}|${NOTES}\n"
    else
      echo -e "    ${RED}FAIL${NC} (score: $SCORE) — $NOTES"
      TOTAL_FAIL=$((TOTAL_FAIL + 1))
      SUMMARY_LINES="${SUMMARY_LINES}${SKILL_NAME}|${ID}|${TEST_TYPE}|${RED}FAIL${NC}|${SCORE}|${NOTES}\n"
    fi

    echo ""
  done

  echo ""
done

# --- Summary ---
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ "$DRY_RUN" = true ]; then
  echo -e "${YELLOW}Dry run complete.${NC} Found $TOTAL_TESTS test cases across $(echo "$CSV_FILES" | wc -l | tr -d ' ') skill(s)."
  echo "Remove --dry to execute evals."
else
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
  echo -e "  Artifacts saved to: ${DIM}$EVAL_RUNS_DIR/${NC}"
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Exit non-zero if any test failed (CI-friendly)
if [ "$DRY_RUN" = false ] && [ "$TOTAL_FAIL" -gt 0 ]; then
  exit 1
fi
