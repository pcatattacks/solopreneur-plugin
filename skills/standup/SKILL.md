---
name: standup
description: Generate a daily standup summary showing what was done, what is planned, and any blockers. Use when the user wants a status update or progress report.
---

# Daily Standup

Generate a standup summary by gathering information from multiple sources.

## Process

1. **Gather activity data**:
   - Check `git log --oneline -20` for recent commits
   - Read `.solopreneur/observer-log.md` if it exists (recent entries)
   - Scan `.solopreneur/` subdirectories for recently created/modified files:
     - `.solopreneur/discoveries/` - discovery briefs
     - `.solopreneur/specs/` - product specs
     - `.solopreneur/designs/` - design docs
     - `.solopreneur/plans/` - build plans (check for completion checkboxes)
     - `.solopreneur/builds/` - build logs
     - `.solopreneur/releases/` - release notes

2. **Check plan progress**:
   - Read any plan files in `.solopreneur/plans/`
   - Count completed (`[x]`) vs pending (`[ ]`) steps
   - Identify any blocked or failed steps

3. **Generate standup** in this format:

   ```markdown
   # Standup - [Date]

   ## Done
   - [Completed items with brief descriptions]

   ## In Progress
   - [Items currently being worked on, with % completion if from plans]

   ## Up Next
   - [Suggested next steps based on lifecycle flow]

   ## Blockers
   - [Any issues, failed steps, or decisions needed from the CEO]

   ## Team Activity
   - [Which agents were invoked and what they produced]
   ```

4. Save to `.solopreneur/standups/{date}.md` (create the directory if needed).
