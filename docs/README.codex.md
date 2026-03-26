# Solopreneur for Codex

Guide for using the Solopreneur workflow in OpenAI Codex using Codex's native skill discovery.

## Quick Install

Tell Codex:

```
Fetch and follow instructions from https://raw.githubusercontent.com/pcatattacks/solopreneur-plugin/refs/heads/main/.codex/INSTALL.md
```

## Manual Installation

### Prerequisites

- OpenAI Codex CLI
- Git

### Steps

1. Clone the repo:

   ```bash
   git clone https://github.com/pcatattacks/solopreneur-plugin.git ~/.codex/solopreneur-plugin
   ```

2. Symlink the checked-in Codex skill bundle into the user skill folder Codex scans:

   ```bash
   mkdir -p ~/.agents/skills
   ln -s ~/.codex/solopreneur-plugin/.agents/skills/solopreneur ~/.agents/skills/solopreneur
   ```

3. Restart Codex.

## How this differs from the Claude plugin

The Solopreneur lifecycle itself does **not** change in Codex. The same shared workflow files still drive the work:

- `skills/*/SKILL.md` for workflow behavior
- `agents/*.md` for specialist briefs
- `.solopreneur/` for generated artifacts

What changes in Codex is the outer shell:

1. **Installation** uses clone + symlink (or `.codex/INSTALL.md`) instead of Claude marketplace/plugin installation.
2. **Invocation** uses the auto-discovered `using-solopreneur` skill (or natural-language prompts) instead of slash commands like `/solopreneur:build`.
3. **Routing** happens through `.agents/skills/solopreneur/using-solopreneur/SKILL.md` into shared root workflows, with `AGENTS.md` as repo-level guardrails.

If you already know the Claude plugin workflow, think of Codex as a different launcher around the same Solopreneur system.

## How it works

- Codex automatically discovers skills from `~/.agents/skills/`.
- This repository ships a single Codex-native entrypoint at `.agents/skills/solopreneur/using-solopreneur/`.
- That skill routes into the existing shared workflow files in `skills/*/SKILL.md` and the role briefs in `agents/*.md`.
- The repository root `AGENTS.md` remains the shared repo-wide guardrail file for Codex.

## Local repository usage

If you are already inside this repository and launch `codex` from the repo root, Codex can also discover the checked-in `.agents/skills/` directory directly.

## Included Codex skills

- `using-solopreneur`

## Usage examples

After installation, Codex can activate Solopreneur skills automatically or by name. Examples:

- `Use using-solopreneur and help me figure out the right workflow for a new SaaS idea.`
- `Use using-solopreneur for an AI meal planner idea and route me to the right Solopreneur workflow.`
- `Use using-solopreneur for .solopreneur/backlog/meal-planner/MVP-001.md.`
- `Use using-solopreneur to review the most recent changes.`

## Design choices

These choices are intentional and should be preserved unless there is a clear reason to change them:

1. **Single Codex entry skill** (`using-solopreneur`) rather than many wrappers.
2. **Shared workflow source of truth** in root `skills/*/SKILL.md` and `agents/*.md`.
3. **No forced AGENTS re-read** from the routing skill, to avoid duplicate global context loading.
4. **Additive compatibility**: Codex changes must not alter Claude plugin behavior.

## Compatibility guarantees

- Claude plugin packaging stays in `.claude-plugin/`.
- Claude hooks stay in `hooks/hooks.json`.
- Claude settings stay in `settings.json`.
- Shared workflow content stays in `skills/*/SKILL.md`.
- Shared role briefs stay in `agents/*.md`.

Codex support is additive rather than a replacement for Claude Code.
