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

if not questions or not answers:
    exit(0)

lines = []
for q in questions:
    question_text = q.get("question", "")
    options = q.get("options", [])
    answer_text = answers.get(question_text, "")

    if not question_text or not answer_text:
        continue

    option_labels = [o.get("label", "") for o in options if o.get("label")]
    lines.append(f"\n## [{timestamp}] - {question_text}")
    if option_labels:
        lines.append(f"**Options**: {', '.join(option_labels)}")
    lines.append(f"**Choice**: {answer_text}")
    lines.append("---")

if lines:
    with open(log_file, "a") as f:
        f.write("\n".join(lines) + "\n")
PYEOF
