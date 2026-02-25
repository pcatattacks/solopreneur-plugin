---
name: review
description: Review code, specifications, or designs for quality, bugs, security, and best practices. Use when the user wants feedback on recent work, a pull request, or any artifact.
---

# Review: $ARGUMENTS

You are conducting a quality review. Determine what type of artifact is being reviewed based on `$ARGUMENTS`:

- If it's a file path ending in code extensions (.ts, .js, .py, etc.) or "recent changes" or a PR → **Code Review**
- If it's a path to a `.solopreneur/specs/` file or mentions "spec" → **Spec Review**
- If it's a path to a `.solopreneur/designs/` directory or file, or mentions "design" → **Design Review**
- If it's a path to a `.solopreneur/backlog/` ticket file (e.g., `MVP-001.md`) → **Ticket Review**
- If it's a path to a `.solopreneur/plans/` file → **Plan Validation** (check completed steps against acceptance criteria)

## Code Review

Delegate in parallel:
- `@engineer`: Architecture review - code structure, patterns, maintainability, performance
- `@qa`: Bug hunting - security vulnerabilities, edge cases, error handling, test coverage

## Spec Review

Delegate in parallel:
- `@bizops`: Business viability - does this make commercial sense? Are requirements prioritized correctly?
- `@engineer`: Technical feasibility - can this be built? Are estimates realistic? Any missing requirements?

## Design Review

If reviewing a design directory, read `design-brief.md` for flows and visual direction. If HTML mockups exist, open them in the browser (Chrome DevTools MCP if available) to inspect the actual layouts.

Delegate in parallel:
- `@designer`: Usability - is the flow intuitive? Are there accessibility issues? If HTML mockups exist, inspect them for visual consistency and responsive behavior.
- `@engineer`: Implementability - can this be built as designed? Review HTML mockups for feasible component structure. Any technical constraints?

## Ticket Review

Read the ticket file for acceptance criteria and the `## Files` section for what was built. Delegate in parallel:
- `@engineer`: Validate implementation against each acceptance criterion. Check code quality and architecture.
- `@qa`: Test edge cases, security, error handling specific to this ticket's scope.

### Browser Validation (UI tickets)

If the ticket involves UI changes (references design mockups, creates HTML/CSS/frontend files, or has UI-related acceptance criteria):

1. Follow the **Claude Chrome Extension setup check** (see Browser Tools in CLAUDE.md)
2. Delegate browser validation to `@qa` — visual walk-through, screenshots, console errors
3. Optionally spawn `@designer` to compare against design mockups if they exist in `.solopreneur/designs/`

On pass, update the ticket's YAML frontmatter: `status: tested`.

If the ticket has a `branch` field in its YAML frontmatter (e.g., `branch: ticket/MVP-001`), offer to merge:
> This ticket passes review. Want me to merge branch `ticket/{ID}` into main?

If yes: merge with `git checkout main && git merge ticket/{ID} --no-ff -m "Merge ticket/{ID}: {title}"`, delete the branch (`git branch -d ticket/{ID}`), and update ticket status to `done`.

If merge conflicts: adapt to technical level (check `.solopreneur/preferences.yaml`) — technical users see conflicts; non-technical users get plain-language explanation.

On fail, list what needs fixing and suggest:
```
-> These issues need to be fixed before merging. Run:
   /solopreneur:build .solopreneur/backlog/{date}-{slug}/{ID}.md
```

## Plan Validation (after Cursor execution)

Read the plan file and check git diff or file state:
- For each step with acceptance criteria, delegate to `@qa` to validate
- Update the plan file with checkboxes: `- [x] Step N: ... (validated)` or `- [ ] Step N: ... (FAILED: reason)`

## Output Format

Compile all findings into a structured review:
- **Critical Issues**: Must fix before proceeding
- **Warnings**: Should fix, but not blocking
- **Suggestions**: Nice-to-have improvements
- **Positives**: Things done well (always include at least one)

End with the next step prompt (adapt based on context):

**If a ticket was just merged:**
```
-> Next: Ready to ship what we've built?
   /solopreneur:ship

   More tickets to build?
   /solopreneur:sprint
```

**Otherwise (general review, no merge):**
```
-> Next: Ready to ship? Run:
   /solopreneur:ship

   Or want a deeper adversarial discussion on the findings?
   /solopreneur:kickoff code review
   (assembles your team for collaborative debate — takes longer, deeper analysis)
```
