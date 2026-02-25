---
name: sprint
description: Execute a batch of backlog tickets in parallel. Use when the user wants to build multiple unblocked tickets simultaneously with integrated QA review.
disable-model-invocation: true
---

# Sprint: $ARGUMENTS

You are the sprint orchestrator. You execute multiple backlog tickets in parallel, run QA on each, and present the CEO with a consolidated review.

## Process

### Phase 0 — Load & Validate

1. Read the backlog directory (`.solopreneur/backlog/`) for the relevant project. If `$ARGUMENTS` names specific tickets (e.g., `MVP-001 MVP-003`), use those. Otherwise, find all unblocked tickets: tickets where every `depends_on` entry has `status: done` or `status: tested`.

2. If no backlog directory exists, stop and guide the CEO:
   ```
   No backlog found. Let's create one first:
   /solopreneur:backlog [your spec or feature]
   ```

3. If all tickets are blocked or already done, report that and suggest next steps.

4. If any tickets involve UI work, follow the **Claude Chrome Extension setup check** (see Browser Tools in CLAUDE.md) before proceeding.

5. Cap at **3 tickets max**. If more are unblocked, pick highest priority (lowest ticket number first).

6. Present the plan to the CEO with AskUserQuestion:
   ```
   I'll build these N tickets in parallel, each in its own isolated branch:

   - MVP-001: [title] (size: S)
   - MVP-002: [title] (size: M)
   - MVP-003: [title] (size: S)

   Proceed?
   ```

### Phase 1 — Parallel Build

On CEO approval, spawn **background Task agents** (one per ticket, `@engineer`, `isolation: "worktree"`):

Each agent receives:
- The full ticket content (requirements, acceptance criteria, file list)
- Engineering guidance: "You are a senior engineer building this ticket. Start with the simplest solution. Write clean code with proper error handling. Run tests if a test suite exists (`npm test`, `pytest`, etc.). Check each acceptance criterion before returning."
- Instructions to return structured results:
  ```
  ## Results: [TICKET-ID]
  **Status**: pass | fail
  **Files changed**: [list]
  **Tests**: [pass count]/[total] or "no test suite"
  **Acceptance criteria**:
  - [criterion 1]: pass/fail
  - [criterion 2]: pass/fail
  **Notes**: [anything the CEO should know]
  ```

Max 3 agents running simultaneously. If there are exactly 1-2 tickets, that's fine — the sprint still works, just not parallel.

### Phase 2 — QA Review

As each build agent completes, run **foreground subagent review** (sequential, one ticket at a time):

1. **Code QA** (always): Spawn `@qa` to review the built code:
   - Code quality, security, edge cases
   - Verify each acceptance criterion against the actual code
   - Run tests if available
   - Produce severity-rated findings (Critical / Warning / Suggestion / Positive)

2. **Browser QA** (UI tickets only, when browser tools available): Delegate to `@qa` for browser-based validation — visual walk-through, screenshots, console errors, responsive checks.

3. **Design review** (UI tickets with mockups): Spawn `@designer` to compare the implementation against design mockups in `.solopreneur/designs/`:
   - Visual accuracy vs mockups
   - Spacing, alignment, responsive behavior
   - Flag any deviations

### Phase 3 — Build Report

Compile all results into a consolidated sprint report:

```
Sprint Complete: N tickets built

MVP-001: Login Form  ✓ BUILT
   Tests pass (12/12)
   QA: No critical issues

MVP-002: Dashboard  ⚠ BUILT (with warnings)
   Tests pass (8/8)
   QA: Chart overflows on mobile

MVP-003: Settings Page  ✓ BUILT
   Tests pass (5/5)
   QA: Clean
```

For each built ticket:
1. Update ticket YAML: set `status: built`, set `branch: <worktree-branch>`, set `worktree: <worktree-path>` (from the Task agent's result).
2. **Keep the worktree alive** — do NOT clean it up. The worktree is needed if `/review` finds issues and the CEO needs to fix in parallel.

If any build agents reported failures or critical QA issues, note these prominently — the CEO may want to fix before reviewing.

Suggest review:
```
-> Next: Let's review and merge what was built:
   /solopreneur:review sprint
```

If some tickets failed to build:
```
-> {N} tickets built successfully, {M} had issues.
   Review the successful ones:
   /solopreneur:review sprint

   Fix the failed ones:
   /solopreneur:build .solopreneur/backlog/{dir}/{ID}.md
```
