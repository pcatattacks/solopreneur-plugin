# Using Solopreneur with Codex

This guide is additive to the existing Claude Code plugin docs. Nothing in this file replaces the Claude plugin install flow, slash commands, hooks, or packaging.

## What stays the same

- The source-of-truth workflow files are still in `skills/*/SKILL.md`.
- The specialist briefs are still in `agents/*.md`.
- Claude plugin packaging still lives in `.claude-plugin/`.
- Claude settings still live in `settings.json`.
- Hook configuration still lives in `hooks/hooks.json`.
- Artifacts still belong under `.solopreneur/`.

## What Codex adds

Codex reads the repository's `AGENTS.md`, and this repo also provides `.codex/skills/solopreneur/SKILL.md`, which together tell Codex how to:

1. map user requests to the right Solopreneur skill file
2. consult the right specialist brief when needed
3. preserve the same output locations and git workflow
4. reinterpret Claude-only UI affordances as plain-language Codex workflows

## Prompt equivalents

Use natural language in Codex where Claude Code would use slash commands.

| Claude Code command | Codex prompt |
| --- | --- |
| `/solopreneur:help` | `Read this repo's AGENTS.md and orient me to the Solopreneur workflow.` |
| `/solopreneur:discover meal planning app` | `Run the Solopreneur discover workflow for a meal planning app.` |
| `/solopreneur:spec .solopreneur/discoveries/meal-planner.md` | `Use the Solopreneur spec workflow for .solopreneur/discoveries/meal-planner.md.` |
| `/solopreneur:backlog .solopreneur/specs/meal-planner.md` | `Use the Solopreneur backlog workflow for .solopreneur/specs/meal-planner.md.` |
| `/solopreneur:build .solopreneur/backlog/meal-planner/MVP-001.md` | `Use this repo's build workflow to plan or implement .solopreneur/backlog/meal-planner/MVP-001.md.` |
| `/solopreneur:review recent` | `Act as the Solopreneur reviewer and review the most recent changes.` |
| `/solopreneur:ship` | `Run the Solopreneur ship workflow for this project.` |
| `/solopreneur:release-notes for twitter` | `Use the Solopreneur release-notes workflow to draft a Twitter announcement.` |

## Compatibility guardrails

When working in Codex, keep these rules in mind:

- Do not rename or move Claude plugin files.
- Do not change slash-command names just to suit Codex.
- Prefer adding Codex entrypoints and docs over rewriting Claude-facing behavior.
- Keep the Codex skill entrypoint in `.codex/skills/solopreneur/SKILL.md` thin and delegate to the shared Solopreneur workflow files.
- If a workflow mentions a Claude-only surface such as plugin UI or the Claude Chrome Extension, adapt it in-place to the equivalent Codex tooling that is actually available.
