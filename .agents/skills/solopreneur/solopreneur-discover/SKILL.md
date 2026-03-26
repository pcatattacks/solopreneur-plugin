---
name: solopreneur-discover
description: Use when the user wants to validate a product idea, do market research, or mentions `/solopreneur:discover`.
---

# solopreneur-discover

This is the Codex wrapper for the shared Solopreneur `discover` workflow.

## What to do

1. Read the repository root `AGENTS.md` for repo-wide Solopreneur guardrails.
2. Open `skills/discover/SKILL.md` and follow it as the source of truth.
3. Read the relevant specialist brief in `agents/*.md` if the workflow depends on a particular role.
4. Interpret Claude-specific UI language as Codex-friendly natural language, but do not change the underlying workflow files.
5. Save outputs in `.solopreneur/discoveries/`.
6. Preserve Claude compatibility: do not rename slash commands or rewrite `.claude-plugin/`, `hooks/`, or `settings.json` for Codex.
