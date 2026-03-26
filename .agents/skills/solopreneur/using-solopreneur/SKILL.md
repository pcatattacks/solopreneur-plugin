---
name: using-solopreneur
description: Use when the user wants the Solopreneur system, asks for the right Solopreneur workflow, or mentions `/solopreneur` commands. Routes to the appropriate Solopreneur Codex skill and shared workflow file.
---

# Using Solopreneur in Codex

Use this as the top-level Solopreneur routing skill in Codex.

## What to do

1. Read the repository root `AGENTS.md` for repo-wide guardrails and shared conventions.
2. Determine which Solopreneur workflow best matches the user's request.
3. Use the matching Codex skill in this `.agents/skills/solopreneur/` bundle when a workflow-specific skill exists.
4. Then open and follow the shared workflow instructions in `skills/<skill>/SKILL.md`.
5. Read the relevant specialist brief in `agents/*.md` when the workflow depends on a particular role.
6. Keep Codex support additive: preserve Claude slash commands, plugin files, hooks, and settings.

## Workflow routing

- Idea validation or market research -> `solopreneur-discover`
- Product requirements / PRD writing -> `solopreneur-spec`
- Ticket breakdown / backlog creation -> `solopreneur-backlog`
- Design direction / mockups -> `solopreneur-design`
- Planning or implementation -> `solopreneur-build`
- Reviews / QA -> `solopreneur-review`
- Deployment / launch readiness -> `solopreneur-ship`
- Launch copy / announcements -> `solopreneur-release-notes`
- Team sessions -> `solopreneur-kickoff`
- Parallel ticket execution -> `solopreneur-sprint`
- Status summaries -> `solopreneur-standup`
- Storytelling / retrospectives -> `solopreneur-story`
- Setup / orientation -> `solopreneur-help`
- Building a custom org -> `solopreneur-scaffold`

## Shared rules

- Treat the root `skills/*/SKILL.md` and `agents/*.md` files as the source of truth.
- Save artifacts under `.solopreneur/`.
- Do not move or rewrite `.claude-plugin/`, `hooks/`, or `settings.json` just to suit Codex.
