#!/bin/bash
# run-evals.sh - Run eval suite for Solopreneur plugin skills.
#
# This script:
# 1. Reads CSV test cases for a specified skill (or all skills)
# 2. For each test case, invokes the skill with the test prompt
# 3. Runs the deterministic grader on the output
# 4. Prints a summary table
#
# Usage:
#   ./evals/run-evals.sh                  # Run all evals
#   ./evals/run-evals.sh discover         # Run evals for discover skill only
#   ./evals/run-evals.sh discover --dry   # Dry run (show test cases without executing)
#
# Prerequisites:
#   - Claude Code CLI installed
#   - Plugin loaded (run from plugin root directory)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_FILTER="${1:-all}"
DRY_RUN="${2:-}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Solopreneur Eval Runner${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

TOTAL_PASS=0
TOTAL_FAIL=0
TOTAL_SKIP=0

# Find CSV files to process
if [ "$SKILL_FILTER" = "all" ]; then
  CSV_FILES=$(find "$SCRIPT_DIR/prompts" -name "*.csv" 2>/dev/null)
else
  CSV_FILES="$SCRIPT_DIR/prompts/${SKILL_FILTER}.csv"
fi

if [ -z "$CSV_FILES" ]; then
  echo -e "${RED}No eval files found for: $SKILL_FILTER${NC}"
  exit 1
fi

for CSV_FILE in $CSV_FILES; do
  SKILL_NAME=$(basename "$CSV_FILE" .csv)
  echo -e "${YELLOW}Skill: /solopreneur:${SKILL_NAME}${NC}"
  echo "─────────────────────────────────────"

  # Skip header line, read each test case
  tail -n +2 "$CSV_FILE" | while IFS=, read -r id should_trigger prompt expected_behaviors; do
    # Strip quotes from fields
    id=$(echo "$id" | tr -d '"')
    should_trigger=$(echo "$should_trigger" | tr -d '"')
    prompt=$(echo "$prompt" | tr -d '"')
    expected_behaviors=$(echo "$expected_behaviors" | tr -d '"')

    if [ "$DRY_RUN" = "--dry" ]; then
      echo -e "  ${BLUE}[DRY]${NC} $id: $prompt"
      echo "        Expected: $expected_behaviors"
      echo ""
      continue
    fi

    echo -e "  Running: ${BLUE}$id${NC}"
    echo "    Prompt: $prompt"

    if [ "$should_trigger" = "true" ]; then
      # TODO: Replace with actual Claude Code CLI invocation
      # claude --plugin-dir . --json --print "$prompt" 2>/dev/null
      echo -e "    ${YELLOW}[MANUAL]${NC} Run this prompt and check expected behaviors:"
      echo "    Expected: $expected_behaviors"
    else
      echo -e "    ${YELLOW}[NEGATIVE]${NC} Skill should NOT trigger for this prompt"
      echo "    Verify: Skill does not activate"
    fi
    echo ""
  done

  echo ""
done

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ "$DRY_RUN" = "--dry" ]; then
  echo -e "${YELLOW}Dry run complete. No skills were actually invoked.${NC}"
  echo "Remove --dry flag to execute evals."
else
  echo -e "${YELLOW}Manual eval run complete.${NC}"
  echo ""
  echo "To run deterministic checks on outputs:"
  echo "  bash evals/graders/deterministic.sh discover .solopreneur/discoveries/"
  echo "  bash evals/graders/deterministic.sh spec .solopreneur/specs/"
  echo ""
  echo "Tip: After running evals, add failing cases as new CSV rows"
  echo "to grow your test coverage over time."
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
