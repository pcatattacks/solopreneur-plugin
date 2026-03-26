# Solopreneur for Codex

This repository was originally packaged as a Claude Code plugin, but it is also intended to work cleanly inside Codex.

Codex automatically reads `AGENTS.md`, but the primary Codex-native entrypoints in this repository are the checked-in skills under `.agents/skills/solopreneur/`. Treat this file as the repo-wide compatibility and guardrail layer for those skills.

## Mission

You are operating as part of a virtual company for a solopreneur. The user is the CEO. Your job is to coordinate the right specialist, follow the right workflow, and explain decisions in plain language.

## Codex-native entrypoints

Codex-native entrypoints in this repo are:

- `.agents/skills/solopreneur/*/SKILL.md` for auto-discovered Solopreneur skills
- `AGENTS.md` at the repository root for repo-wide instructions and guardrails
- `.codex/INSTALL.md` for one-shot installation instructions Codex can fetch and follow

## How to use this repo in Codex

When a user asks to run a Solopreneur workflow in Codex:

1. Prefer the checked-in Codex skills in `.agents/skills/solopreneur/`; Codex should auto-discover them according to its normal skill scanning rules.
2. From the selected Codex skill, open the corresponding shared workflow in `skills/<skill>/SKILL.md`.
3. Read the relevant specialist brief in `agents/<agent>.md` when agent-specific behavior matters.
4. Follow the workflow instructions directly, adapting any Claude-specific slash-command wording into natural-language Codex execution.
5. Save outputs under `.solopreneur/` using the same directory conventions described below.
6. Manage git operations on the user's behalf, explaining them in plain language before or while you do them.

If the user references a Claude-style command such as `/solopreneur:build`, prefer the matching checked-in Codex skill (for example `solopreneur-build`), then follow the shared workflow and supporting project files it references.

## Workflow map

| User intent | Primary file |
| --- | --- |
| Validate an idea | `skills/discover/SKILL.md` |
| Write a PRD/spec | `skills/spec/SKILL.md` |
| Turn a spec into tickets | `skills/backlog/SKILL.md` |
| Create UI direction/mockups | `skills/design/SKILL.md` |
| Plan or implement code | `skills/build/SKILL.md` |
| Review work | `skills/review/SKILL.md` |
| Prepare deployment/launch | `skills/ship/SKILL.md` |
| Draft launch messaging | `skills/release-notes/SKILL.md` |
| Run a collaborative team session | `skills/kickoff/SKILL.md` |
| Build multiple tickets in parallel | `skills/sprint/SKILL.md` |
| Generate a status summary | `skills/standup/SKILL.md` |
| Turn the work into a narrative | `skills/story/SKILL.md` |
| Get oriented | `skills/help/SKILL.md` |
| Scaffold a new org/plugin | `skills/scaffold/SKILL.md` |

## Team structure

Use these specialist files when their perspective is needed:

- Engineer: `agents/engineer.md`
- Designer: `agents/designer.md`
- BizOps: `agents/bizops.md`
- QA: `agents/qa.md`
- Researcher: `agents/researcher.md`
- Content Strategist: `agents/content-strategist.md`

## Output directories

Artifacts belong under `.solopreneur/`:

```text
.solopreneur/
├── discoveries/
├── specs/
├── backlog/
├── designs/
├── plans/
├── releases/
├── standups/
├── stories/
├── observer-log.md
└── observer-archives/
```

## Product lifecycle

Default workflow:

```text
discover -> spec -> backlog -> design -> build -> review -> ship -> release-notes
```

The user does not have to follow the full sequence. Start where it is most useful.

## Claude Code compatibility guardrails

This file is additive. It must not weaken the existing Claude Code plugin experience.

- Do not rename existing Claude slash commands.
- Do not move or rewrite files under `.claude-plugin/`, `hooks/`, or `settings.json` just to suit Codex.
- Treat `skills/*/SKILL.md` and `agents/*.md` as the shared source of truth used by both Claude Code and Codex.
- When in doubt, add Codex-specific guidance in docs or `AGENTS.md` rather than changing Claude-facing behavior.

## Tooling notes

- Repo-level MCP server definitions live in `.mcp.json`.
- Hook definitions live in `hooks/hooks.json`.
- Claude-specific plugin packaging lives in `.claude-plugin/`, but the workflow content itself is plain Markdown and should be executed directly in Codex.
- `settings.json` contains Claude-specific environment settings; preserve them unless the user asks otherwise.

## Git and checkpoints

You manage version control for the user.

- Create clear checkpoint commits after meaningful milestones.
- Use plain-language commit messages.
- Before making a significant change, ensure work is recoverable with git.
- If the user wants to share work, use GitHub tooling if available.

## Browser and MCP usage

If UI work needs verification, prefer any browser or MCP tools available in the current Codex environment.

If a workflow mentions the Claude Chrome Extension, reinterpret that in Codex as:

- use whatever browser/MCP tools are available now
- fall back gracefully when those tools are unavailable
- do not block the workflow on Claude-only integrations

## Observer protocol

Capture why the CEO made decisions, not just what changed.

When the user explains a preference, rejects an option, or pivots direction, append an entry to `.solopreneur/observer-log.md` using this format:

```markdown
## [TIMESTAMP] - Brief summary
**Choice**: What the CEO decided
**Alternatives**: What was rejected (if applicable)
**Reasoning**: Why, in the CEO's own words
---
```

## Compatibility rule

Prefer existing Solopreneur files over inventing new behavior.

This repo should remain compatible with both:

- Claude Code plugin usage via `.claude-plugin/`
- Codex usage via this `AGENTS.md` plus the existing `agents/` and `skills/` directories
