---
name: backlog
description: Break a spec or feature into prioritized, dependency-tracked tickets for implementation. Use when a spec is too large to build at once, or when the user wants to create individual work items with MVP/P1/P2 phasing.
argument-hint: spec file path
---

# Backlog: $ARGUMENTS

You are creating a prioritized backlog for the CEO. Determine the mode based on `$ARGUMENTS`:

- If it's a file path to a spec (`.solopreneur/specs/...`) or design directory (`.solopreneur/designs/...`), read it for context → **Full Breakdown** mode
- Otherwise, treat it as a task description → **Single Ticket** mode

---

## Full Breakdown Mode

### Step 1: Read Context

Read the spec file (and design directory if referenced). Understand:
- What's being built and for whom
- All user stories and acceptance criteria
- Technical requirements and constraints
- Release phases if the spec includes them (MVP/P1/P2)

### Step 2: Break Down with Agents

Delegate to subagents in parallel:
- `@engineer`: Break requirements into implementable tickets. For each ticket: title, description, acceptance criteria, technical notes, complexity estimate (S/M/L), and dependencies on other tickets. Flag technical risks.
- `@designer`: Identify which tickets need design work (type: `eng+design` or `design`). Flag UX dependencies between tickets (e.g., "dashboard needs auth to be built first for the logged-in state").

### Step 3: Propose Backlog to CEO

Present the ticket breakdown to the CEO for approval:
- MVP/P1/P2 grouping (use spec's release phases if available, otherwise propose phasing)
- Dependency graph showing which tickets block others
- Parallel groups — tickets with no shared dependencies that can be built simultaneously
- Total ticket count and complexity distribution
- Ask: "Does this breakdown look right? Want to adjust the phasing or split/merge any tickets?"

Wait for CEO approval before creating files.

### Step 4: Create Ticket Files

On CEO approval, create the backlog directory and files:

**Directory**: `.solopreneur/backlog/{date}-{slug}/`

**backlog.md** — The board view with all tickets, statuses, dependency graph, and parallel groups. Format:

```markdown
# Backlog: {Feature Name}

## Source
Spec: `.solopreneur/specs/{spec-file}`
Design: `.solopreneur/designs/{design-dir}/` (if exists)

## MVP
| ID | Title | Status | Depends On | Type | Size |
|----|-------|--------|------------|------|------|
| MVP-001 | ... | pending | — | eng | M |

## P1
| ID | Title | Status | Depends On | Type | Size |
|----|-------|--------|------------|------|------|

## P2
| ID | Title | Status | Depends On | Type | Size |
|----|-------|--------|------------|------|------|

## Dependency Graph
(ASCII diagram showing ticket dependencies)

## Parallel Groups
(List tickets that can be built simultaneously)
```

**{ID}.md** — One file per ticket with YAML frontmatter and markdown body:

```markdown
---
id: MVP-001
title: Short descriptive title
priority: MVP
type: eng
status: pending
depends_on: []
blocks: [MVP-002]
design_ref:
branch:
---

## Description
What this ticket implements and why.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Technical Notes
(From @engineer: stack choices, approach, risks)

## Files
(Populated during build)
```

### Step 5: Next Step

Suggest the appropriate next action based on the backlog:

- If MVP tickets need design work (type includes `design`):
  ```
  -> Next: Design the MVP screens:
     /solopreneur:design .solopreneur/backlog/{dir}/backlog.md
  ```
- If MVP tickets are ready to build (all `eng` type, or designs already exist):
  ```
  -> Next: Start building the first ticket:
     /solopreneur:build .solopreneur/backlog/{dir}/MVP-001.md

  Tickets that can be built in parallel: MVP-001, MVP-003
  ```

---

## Single Ticket Mode

If `$ARGUMENTS` doesn't reference a spec or design file, treat it as a standalone task:

1. Check if an existing backlog directory exists in `.solopreneur/backlog/`. If so, add the ticket to that backlog (with the next available ID). If not, create a new backlog directory.

2. Create a single ticket file with:
   - A clear title derived from the description
   - Acceptance criteria (ask the CEO if unclear)
   - Priority: default to MVP unless specified
   - Type: infer from the task (eng, design, eng+design)

3. Update backlog.md to include the new ticket.

4. Suggest building it:
   ```
   -> Next: Build this ticket:
      /solopreneur:build .solopreneur/backlog/{dir}/{ID}.md
   ```
