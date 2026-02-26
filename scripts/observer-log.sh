#!/bin/bash
# observer-log.sh - Log CEO decisions to the observer log.
#
# Called by PostToolUse hook on AskUserQuestion.
# Extracts the questions asked, options presented, and the CEO's answers.
#
# Hook stdin format:
#   tool_input.questions  — array of {question, options, ...}
#   tool_input.answers    — {question_text: selected_label} (filled by permission component)

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE=".solopreneur/observer-log.md"

mkdir -p .solopreneur
touch "$LOG_FILE"

# Read hook data from stdin
INPUT=$(cat 2>/dev/null || echo '{}')

# Pass data via env var — can't pipe + heredoc at the same time (heredoc steals stdin)
INPUT="$INPUT" TIMESTAMP="$TIMESTAMP" LOG_FILE="$LOG_FILE" python3 << 'PYEOF'
import json, os

timestamp = os.environ.get("TIMESTAMP", "")
log_file = os.environ.get("LOG_FILE", ".solopreneur/observer-log.md")

try:
    data = json.loads(os.environ.get("INPUT", "{}"))
except Exception:
    exit(0)

tool_input = data.get("tool_input", {})
questions = tool_input.get("questions", [])
# Answers live in tool_input.answers (filled by the permission component)
answers = tool_input.get("answers", {}) if isinstance(tool_input, dict) else {}
# Annotations contain user's freeform notes (e.g., "Other" selections)
annotations = tool_input.get("annotations", {}) if isinstance(tool_input, dict) else {}

if not questions or not answers:
    exit(0)

lines = []
for q in questions:
    question_text = q.get("question", "")
    options = q.get("options", [])
    answer_text = answers.get(question_text, "")

    if not question_text or not answer_text:
        continue

    lines.append(f"\n## [{timestamp}] - {question_text}")
    lines.append(f"**Choice**: {answer_text}")

    # Show what alternatives were considered
    option_labels = [o.get("label", "") for o in options if o.get("label")]
    rejected = [l for l in option_labels if l != answer_text]
    if rejected:
        lines.append(f"**Alternatives**: {', '.join(rejected)}")

    # Context: option description > annotation notes > omit
    context = ""
    for o in options:
        if o.get("label", "") == answer_text:
            context = o.get("description", "")
            break
    if not context:
        q_annotations = annotations.get(question_text, {})
        context = q_annotations.get("notes", "")
    if context:
        lines.append(f"**Context**: {context}")
    lines.append("---")

if lines:
    with open(log_file, "a") as f:
        f.write("\n".join(lines) + "\n")
PYEOF

# --- Log rotation ---
# If the log exceeds 500 lines, archive older entries and keep the last 200.
if [ -f "$LOG_FILE" ]; then
  LINE_COUNT=$(wc -l < "$LOG_FILE" | tr -d ' ')
  if [ "$LINE_COUNT" -gt 500 ]; then
    ARCHIVE_DIR=".solopreneur/observer-archives"
    ARCHIVE_FILE="$ARCHIVE_DIR/$(date '+%Y-%m').md"
    mkdir -p "$ARCHIVE_DIR"
    KEEP=200
    CUT=$((LINE_COUNT - KEEP))
    head -n "$CUT" "$LOG_FILE" >> "$ARCHIVE_FILE"
    tail -n "$KEEP" "$LOG_FILE" > "$LOG_FILE.tmp"
    echo "> Older entries archived in observer-archives/" > "$LOG_FILE"
    cat "$LOG_FILE.tmp" >> "$LOG_FILE"
    rm -f "$LOG_FILE.tmp"
  fi
fi
