#!/bin/bash
# observer-log.sh - Automatically append tool usage events to the observer log.
#
# This script is called by Claude Code hooks (PostToolUse, Stop).
# It reads hook event data from stdin (JSON) and appends a structured
# entry to .solopreneur/observer-log.md.
#
# Usage: observer-log.sh [event-type]
#   event-type: "tool-use", "command", or "session-end"

EVENT_TYPE="${1:-tool-use}"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE=".solopreneur/observer-log.md"

# Create the log directory and file if they don't exist
mkdir -p .solopreneur
touch "$LOG_FILE"

# Read hook input from stdin
INPUT=$(cat 2>/dev/null || echo '{}')

if [ "$EVENT_TYPE" = "session-end" ]; then
  cat >> "$LOG_FILE" << EOF

## [$TIMESTAMP] - SESSION_END
**Event**: Claude Code session ended
---
EOF
  exit 0
fi

# Extract tool name and target from the hook JSON
TOOL=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('tool_name', 'unknown'))
except:
    print('unknown')
" 2>/dev/null || echo "unknown")

TARGET=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    inp = data.get('tool_input', {})
    print(inp.get('file_path', inp.get('command', 'N/A'))[:120])
except:
    print('N/A')
" 2>/dev/null || echo "N/A")

cat >> "$LOG_FILE" << EOF

## [$TIMESTAMP] - TOOL_USE
**Tool**: $TOOL
**Target**: $TARGET
**Event**: $EVENT_TYPE
---
EOF
