---
name: solopreneur
description: Use the Solopreneur workspace in Codex by routing requests to the repo's existing workflows, agents, and output conventions while preserving Claude Code compatibility.
metadata:
  short-description: Run Solopreneur workflows in Codex
---

# Solopreneur for Codex

Use this skill when the user wants to run the Solopreneur workflow in Codex, or references commands like `/solopreneur:discover`, `/solopreneur:build`, or `/solopreneur:review`.

## Workflow

1. Read `AGENTS.md` for the Codex compatibility layer and repo-wide guardrails.
2. Map the user's request to the matching workflow file in `skills/<skill>/SKILL.md`.
3. Read the relevant specialist brief in `agents/*.md` when the workflow depends on a particular role.
4. Execute the workflow in Codex using natural language rather than Claude's slash-command UI.
5. Save artifacts under `.solopreneur/` using the same conventions as the Claude plugin.
6. Preserve Claude-facing files and behavior; Codex support is additive.

## Workflow routing

- Idea validation -> `skills/discover/SKILL.md`
- Spec writing -> `skills/spec/SKILL.md`
- Backlog creation -> `skills/backlog/SKILL.md`
- Design work -> `skills/design/SKILL.md`
- Planning or implementation -> `skills/build/SKILL.md`
- Reviews -> `skills/review/SKILL.md`
- Shipping -> `skills/ship/SKILL.md`
- Release messaging -> `skills/release-notes/SKILL.md`
- Team sessions -> `skills/kickoff/SKILL.md`
- Parallel ticket execution -> `skills/sprint/SKILL.md`
- Status summaries -> `skills/standup/SKILL.md`
- Storytelling -> `skills/story/SKILL.md`
- Orientation -> `skills/help/SKILL.md`
- Org scaffolding -> `skills/scaffold/SKILL.md`

## Compatibility rules

- Do not rename Claude slash commands.
- Do not move or rewrite `.claude-plugin/`, `hooks/`, or `settings.json` just to suit Codex.
- Treat `skills/*/SKILL.md` and `agents/*.md` as the shared source of truth for both Claude Code and Codex.
- If a workflow references Claude-only UI, reinterpret it in the equivalent Codex flow without changing the underlying Solopreneur files.
