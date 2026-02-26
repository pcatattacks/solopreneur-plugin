---
name: conventions
user-invocable: false
description: Shared conventions for the solopreneur workflow. Preloaded into agents via the skills frontmatter field.
---

# Solopreneur Conventions

These conventions are the single source of truth for shared formats across the solopreneur workflow.

## Ticket Schema

Tickets are YAML-frontmatter markdown files in `.solopreneur/backlog/{project}/`:

```yaml
---
id: MVP-001
title: Short descriptive title
priority: MVP | P1 | P2
type: eng | design | eng+design
status: pending | in-progress | built | tested | done
depends_on: []
blocks: []
design_ref: .solopreneur/designs/{dir}/{screen}.html
branch: ticket/{ID}
worktree: /path/to/worktree
---

## Description
What this ticket implements and why.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Technical Notes
Stack choices, approach, risks.

## Files
(Populated during build)
```

### Status Transitions

```
pending       → in-progress   (build starts)
in-progress   → built         (build completes)
built         → tested        (QA passes in review)
tested        → done          (merged to main in review)
```

### Where Transitions Happen

Skills contain the operational instructions for the orchestrator. If the state machine changes, update these locations:

- `pending → in-progress`: build/SKILL.md (line 43), sprint delegates to build
- `in-progress → built`: build/SKILL.md (line 150), sprint/SKILL.md (line 99)
- `built → tested`: review/SKILL.md (line 51)
- `tested → done`: review/SKILL.md (lines 58, 99)

## Review Severity Format

When producing review findings, rate every issue:

- **Critical**: Breaks functionality, security vulnerability, data loss risk. Must fix before proceeding.
- **Warning**: Incorrect behavior in edge cases, missing validation. Should fix, not blocking.
- **Suggestion**: Code quality improvement, better patterns available. Nice-to-have.
- **Positive**: Things done well. Always include at least one.

## Plan File Format

Implementation plans use this structure:

```markdown
# Plan: [Feature Name]

## Context
[What we're building and why. Reference source spec/design if applicable.]
**Branch**: `ticket/{ID}` (if ticket build)

## Step N: [Short description]
**Files**: `path/to/file.ext` (create|modify)
**Do**: [Clear, specific instructions for what to write]
**Acceptance**: [Concrete criteria to verify this step is done]
```
