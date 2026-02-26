---
name: review
description: Review code, specifications, or designs for quality, bugs, security, and best practices. Use when the user wants feedback on recent work, a pull request, or any artifact.
---

# Review: $ARGUMENTS

You are conducting a quality review. Determine what type of artifact is being reviewed based on `$ARGUMENTS`:

- If it's a file path ending in code extensions (.ts, .js, .py, etc.) or a PR → **Code Review**
- If it's a path to a `.solopreneur/specs/` file or mentions "spec" → **Spec Review**
- If it's a path to a `.solopreneur/designs/` directory or file, or mentions "design" → **Design Review**
- If it's a path to a `.solopreneur/backlog/` ticket file (e.g., `MVP-001.md`) → **Ticket Review**
- If `$ARGUMENTS` mentions "sprint" or "batch" → **Sprint Review** (scans all backlog directories for `status: built` tickets)
- If it's a path to a `.solopreneur/plans/` file → **Plan Validation** (check completed steps against acceptance criteria)

## Code Review

Delegate in parallel:
- `@engineer`: Architecture review — code structure, patterns, maintainability, performance. Rate every finding using severity format (Critical/Warning/Suggestion/Positive).
- `@qa`: Bug hunting — security vulnerabilities, edge cases, error handling, test coverage. Rate every finding using severity format.

## Spec Review

Delegate in parallel:
- `@bizops`: Business viability — does this make commercial sense? Are requirements prioritized correctly? Provide a go/no-go per requirement.
- `@engineer`: Technical feasibility — can this be built as specified? Flag complexity risks, estimate effort, note missing requirements. Rate each requirement: feasible / complex / risky.

## Design Review

If reviewing a design directory, read `design-brief.md` for flows and visual direction. If HTML mockups exist, open them in the browser (Chrome DevTools MCP if available) to inspect the actual layouts.

Delegate in parallel:
- `@designer`: Usability review — is the flow intuitive? Accessibility issues? If HTML mockups exist, inspect for visual consistency and responsive behavior. Rate findings using severity format.
- `@engineer`: Implementability — can this be built as designed? Flag any technical constraints. Rate findings using severity format.

## Ticket Review

Read the ticket file for acceptance criteria and the `## Files` section for what was built. Delegate in parallel:
- `@engineer`: Validate implementation against each acceptance criterion. Check code quality and architecture. Rate findings using severity format.
- `@qa`: Test edge cases, security, error handling specific to this ticket's scope. Rate findings using severity format.

### Browser Validation (UI tickets)

If the ticket involves UI changes (references design mockups, creates HTML/CSS/frontend files, or has UI-related acceptance criteria):

1. Follow the **Claude Chrome Extension setup check** (see Browser Tools in CLAUDE.md)
2. Delegate browser validation to `@qa` — visual walk-through, screenshots, console errors
3. Optionally spawn `@designer` to compare against design mockups if they exist in `.solopreneur/designs/`

On pass, update the ticket's YAML frontmatter: `status: tested`.

If the ticket has a `branch` field in its YAML frontmatter, offer to merge:
> This ticket passes review. Want me to merge branch `{branch}` into main?

If yes:
1. Merge: `git checkout main && git merge {branch} --no-ff -m "Merge ticket/{ID}: {title}"`
2. Update ticket status to `done`.
3. Delete the branch: `git branch -d {branch}`
4. If the ticket has a `worktree` field, clean it up: `git worktree remove {worktree}`
5. If merge conflicts: adapt to technical level (check `.solopreneur/preferences.yaml`) — technical users see conflicts; non-technical users get plain-language explanation.

On fail, list what needs fixing and suggest:
```
-> These issues need to be fixed before merging. Run:
   /solopreneur:build .solopreneur/backlog/{date}-{slug}/{ID}.md
```

## Sprint Review

Scan all `.solopreneur/backlog/` directories for tickets with `status: built` that have a `branch` field in their YAML frontmatter.

If no built tickets found, report that and suggest:
```
No tickets ready for review. Build first:
/solopreneur:sprint
```

### Phase 1 — Parallel Code Review

For each built ticket, spawn **background** review agents in parallel:
- `@engineer`: Validate implementation against acceptance criteria, check architecture and code quality. Rate findings using severity format.
- `@qa`: Test edge cases, security, error handling for this ticket. Rate findings using severity format.

This means 2 agents per ticket (up to 6 agents for 3 tickets), all running simultaneously.

### Phase 2 — Sequential CEO Review

As review results come in, present a consolidated report grouped by ticket using the standard Output Format (Critical / Warnings / Suggestions / Positives).

For **UI tickets**: run Browser Validation at this point (sequential — browser is shared state). Follow the Claude Chrome Extension setup check. Optionally spawn `@designer` to compare against design mockups if they exist.

The CEO reviews the product, flow, and findings with their own eyes.

### Phase 3 — Merge Decisions

For each ticket, based on the CEO's decision:

- **Pass**: Merge the ticket's branch to main (same merge logic as Ticket Review). Clean up the worktree if present: `git worktree remove {worktree}`. Update status to `done`.
- **Fail**: List issues and suggest fixes. **Keep the worktree alive** so the CEO can fix in parallel:
  ```
  -> Ticket {ID} needs fixes. The code is in its worktree — run:
     /solopreneur:build .solopreneur/backlog/{dir}/{ID}.md
  ```

After all merge decisions:
```
-> Next: Ready to ship?
   /solopreneur:ship

   More tickets to build?
   /solopreneur:sprint
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

**If ticket(s) were just merged:**
```
-> Next: Ready to ship what we've built?
   /solopreneur:ship

   More tickets to build?
   /solopreneur:sprint
```

**If review failed (no merge):**
```
-> These issues need fixing first. Then re-review:
   /solopreneur:build .solopreneur/backlog/{dir}/{ID}.md
```

**Otherwise (general review, no ticket merge):**
```
-> Next: Ready to ship? Run:
   /solopreneur:ship

   Or want a deeper adversarial discussion on the findings?
   /solopreneur:kickoff code review
   (assembles your team for collaborative debate — takes longer, deeper analysis)
```
