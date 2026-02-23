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
#
# Environment variables:
#   EVAL_MODEL   Model for skill invocation (default: sonnet)
#   JUDGE_MODEL  Model for rubric grading (default: sonnet)
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

# Parse arguments - support both "discover --dry" and "--dry discover" and "--dry" alone
SKILL_FILTER="all"
DRY_RUN=false
for arg in "$@"; do
  if [ "$arg" = "--dry" ]; then
    DRY_RUN=true
  else
    SKILL_FILTER="$arg"
  fi
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

# --- Worktree setup (only for actual runs) ---
WORKTREE_DIR=""
WORKTREE_BRANCH=""
RUN_DIR="$PLUGIN_DIR"  # Where claude is invoked from (worktree during real runs)

setup_worktree() {
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

if [ "$DRY_RUN" = false ]; then
  setup_worktree
  trap cleanup_worktree EXIT
  mkdir -p "$EVAL_RUNS_DIR"
fi

# Negative-test patterns per skill (used to detect false triggers)
get_negative_patterns() {
  local skill=$1
  case "$skill" in
    discover) echo "Go/No-Go|Competitive Landscape|Market Size|Discovery Brief" ;;
    spec)     echo "User Stor|Acceptance Criteria|Technical Requirements|Out of Scope" ;;
    design)   echo "User Flow|Component|Visual Direction|design-brief|\.html|daisyui" ;;
    review)   echo "Critical|Warning|Suggestion|Positive|Severity" ;;
    scaffold) echo "Your AI Org|Employees.*Agents|SOPs.*Skills|org chart" ;;
    *)        echo "" ;;
  esac
}

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

# Summary accumulators
TOTAL_PASS=0
TOTAL_FAIL=0
TOTAL_TESTS=0
SUMMARY_LINES=""

for CSV_FILE in $CSV_FILES; do
  # Extract skill name from path: skills/<name>/eval.csv
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

    # Invoke skill inside the sandboxed worktree
    echo "$PROMPT" | claude --print --plugin-dir "$RUN_DIR" --model "$EVAL_MODEL" --dangerously-skip-permissions > "$OUTPUT_FILE" 2>&1 || true
    OUTPUT=$(cat "$OUTPUT_FILE")

    if [ "$SHOULD_TRIGGER" = "true" ]; then
      # --- Positive test: grade with rubric ---
      RUBRIC_TEMPLATE=$(cat "$RUBRIC_FILE")
      RUBRIC_PROMPT=$(echo "$RUBRIC_TEMPLATE" | \
        sed "s|{SKILL_NAME}|$SKILL_NAME|g" | \
        sed "s|{EXPECTED_BEHAVIORS}|$EXPECTED|g")
      # Append the skill output at the end (avoid sed issues with output content)
      RUBRIC_PROMPT=$(echo "$RUBRIC_PROMPT" | sed "s|{SKILL_OUTPUT}|<see below>|g")
      FULL_JUDGE_PROMPT=$(printf "%s\n\n--- SKILL OUTPUT ---\n%s" "$RUBRIC_PROMPT" "$OUTPUT")

      JUDGE_RESPONSE=$(echo "$FULL_JUDGE_PROMPT" | claude --print --model "$JUDGE_MODEL" 2>/dev/null || echo '{"overall_pass": false, "score": 0, "checks": []}')

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
        TOTAL_PASS=$((TOTAL_PASS + 1))
        SUMMARY_LINES="${SUMMARY_LINES}${SKILL_NAME}|${ID}|${TEST_TYPE}|${GREEN}PASS${NC}|${SCORE}|${NOTES}\n"
      else
        echo -e "    ${RED}FAIL${NC} (score: $SCORE) — $NOTES"
        TOTAL_FAIL=$((TOTAL_FAIL + 1))
        SUMMARY_LINES="${SUMMARY_LINES}${SKILL_NAME}|${ID}|${TEST_TYPE}|${RED}FAIL${NC}|${SCORE}|${NOTES}\n"
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
        TOTAL_FAIL=$((TOTAL_FAIL + 1))
        SUMMARY_LINES="${SUMMARY_LINES}${SKILL_NAME}|${ID}|${TEST_TYPE}|${RED}FAIL${NC}|-|False trigger: ${MATCHED_PATTERNS%, }\n"
      else
        echo -e "    ${GREEN}PASS${NC} — skill correctly did not trigger"
        TOTAL_PASS=$((TOTAL_PASS + 1))
        SUMMARY_LINES="${SUMMARY_LINES}${SKILL_NAME}|${ID}|${TEST_TYPE}|${GREEN}PASS${NC}|-|Correctly not triggered\n"
      fi
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
