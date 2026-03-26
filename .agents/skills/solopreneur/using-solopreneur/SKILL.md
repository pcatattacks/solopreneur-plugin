---
name: using-solopreneur
description: Use when the user wants the Solopreneur system, asks which Solopreneur workflow to use, or references `/solopreneur` commands. Routes the request into the shared Solopreneur workflow files.
---

# Using Solopreneur in Codex

Use this as the single Codex-native entrypoint for the Solopreneur system.

## What to do

1. Determine which Solopreneur workflow best matches the user's request.
2. Open and follow the matching shared workflow instructions in `skills/<skill>/SKILL.md`.
3. Read the relevant specialist brief in `agents/*.md` when the workflow depends on a particular role.
4. Keep Codex support additive: preserve Claude slash commands, plugin files, hooks, and settings.
5. Save artifacts under `.solopreneur/`.

## Workflow routing

- Idea validation or market research -> `skills/discover/SKILL.md`
- Product requirements / PRD writing -> `skills/spec/SKILL.md`
- Ticket breakdown / backlog creation -> `skills/backlog/SKILL.md`
- Design direction / mockups -> `skills/design/SKILL.md`
- Planning or implementation -> `skills/build/SKILL.md`
- Reviews / QA -> `skills/review/SKILL.md`
- Deployment / launch readiness -> `skills/ship/SKILL.md`
- Launch copy / announcements -> `skills/release-notes/SKILL.md`
- Team sessions -> `skills/kickoff/SKILL.md`
- Parallel ticket execution -> `skills/sprint/SKILL.md`
- Status summaries -> `skills/standup/SKILL.md`
- Storytelling / retrospectives -> `skills/story/SKILL.md`
- Setup / orientation -> `skills/help/SKILL.md`
- Building a custom org -> `skills/scaffold/SKILL.md`

## Why there is only one Codex skill

The shared Solopreneur workflow files already exist at the repo root in `skills/*/SKILL.md`. This Codex entrypoint stays intentionally thin so the Codex layer does not duplicate every workflow, drift from the shared source of truth, or create generic skill-name collisions like `build`, `review`, or `help` in Codex.

This skill intentionally does **not** force re-reading `AGENTS.md`; that file is treated as repo-level guidance rather than per-invocation workflow logic.
