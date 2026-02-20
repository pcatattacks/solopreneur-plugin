#!/bin/bash
# deterministic.sh - Layer 1 grader for skill evals.
#
# Checks concrete, binary conditions after a skill run:
# - Did output files get created in the expected directory?
# - Do output files contain expected sections/keywords?
# - Were the right number of commands executed?
#
# Usage: deterministic.sh <skill-name> <output-dir>
# Returns: JSON with pass/fail for each check
#
# Example: deterministic.sh discover .solopreneur/discoveries/

SKILL=$1
OUTPUT_DIR=$2

if [ -z "$SKILL" ] || [ -z "$OUTPUT_DIR" ]; then
  echo '{"error": "Usage: deterministic.sh <skill-name> <output-dir>"}'
  exit 1
fi

CHECKS="[]"
PASS_COUNT=0
FAIL_COUNT=0

add_check() {
  local id=$1
  local pass=$2
  local notes=$3
  if [ "$pass" = "true" ]; then
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
  CHECKS=$(echo "$CHECKS" | python3 -c "
import sys, json
checks = json.load(sys.stdin)
checks.append({'id': '$id', 'pass': $pass, 'notes': '$notes'})
json.dump(checks, sys.stdout)
")
}

# Check 1: Output directory exists
if [ -d "$OUTPUT_DIR" ]; then
  add_check "output_dir_exists" "True" "Directory $OUTPUT_DIR exists"
else
  add_check "output_dir_exists" "False" "Directory $OUTPUT_DIR not found"
fi

# Check 2: At least one output file was created
FILE_COUNT=$(find "$OUTPUT_DIR" -type f -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
if [ "$FILE_COUNT" -gt 0 ]; then
  add_check "output_file_created" "True" "Found $FILE_COUNT output file(s)"
else
  add_check "output_file_created" "False" "No .md files found in $OUTPUT_DIR"
fi

# Check 3: Skill-specific section checks
LATEST_FILE=$(find "$OUTPUT_DIR" -type f -name "*.md" -print0 2>/dev/null | xargs -0 ls -t 2>/dev/null | head -1)

if [ -n "$LATEST_FILE" ]; then
  case "$SKILL" in
    discover)
      for section in "Competitive Landscape" "Market Size" "Go/No-Go" "Risk"; do
        if grep -qi "$section" "$LATEST_FILE" 2>/dev/null; then
          add_check "section_${section// /_}" "True" "Found '$section' section"
        else
          add_check "section_${section// /_}" "False" "Missing '$section' section"
        fi
      done
      ;;
    spec)
      for section in "User Stor" "Acceptance Criteria" "Technical Requirements" "Out of Scope"; do
        if grep -qi "$section" "$LATEST_FILE" 2>/dev/null; then
          add_check "section_${section// /_}" "True" "Found '$section' section"
        else
          add_check "section_${section// /_}" "False" "Missing '$section' section"
        fi
      done
      ;;
    review)
      for section in "Critical" "Warning" "Suggestion" "Positive"; do
        if grep -qi "$section" "$LATEST_FILE" 2>/dev/null; then
          add_check "section_${section// /_}" "True" "Found '$section' section"
        else
          add_check "section_${section// /_}" "False" "Missing '$section' section"
        fi
      done
      ;;
    *)
      add_check "content_nonempty" "True" "Output file has content"
      ;;
  esac
fi

# Output results
TOTAL=$((PASS_COUNT + FAIL_COUNT))
if [ "$FAIL_COUNT" -eq 0 ]; then
  OVERALL="true"
else
  OVERALL="false"
fi

python3 -c "
import json
checks = json.loads('$CHECKS')
result = {
    'overall_pass': $OVERALL,
    'score': round($PASS_COUNT / max($TOTAL, 1) * 100),
    'passed': $PASS_COUNT,
    'failed': $FAIL_COUNT,
    'checks': checks
}
print(json.dumps(result, indent=2))
"
