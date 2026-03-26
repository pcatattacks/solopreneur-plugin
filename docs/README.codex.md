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

## How it works

- Codex automatically discovers skills from `~/.agents/skills/`.
- This repository ships a Codex-native skill bundle in `.agents/skills/solopreneur/`.
- Each Codex skill is a thin wrapper that points back to the existing shared workflow files in `skills/*/SKILL.md` and the role briefs in `agents/*.md`.
- The repository root `AGENTS.md` remains the shared repo-wide guardrail file for Codex.

## Local repository usage

If you are already inside this repository and launch `codex` from the repo root, Codex can also discover the checked-in `.agents/skills/` directory directly.

## Included Codex skills

- `using-solopreneur`
- `solopreneur-help`
- `solopreneur-discover`
- `solopreneur-spec`
- `solopreneur-backlog`
- `solopreneur-design`
- `solopreneur-build`
- `solopreneur-review`
- `solopreneur-ship`
- `solopreneur-release-notes`
- `solopreneur-kickoff`
- `solopreneur-sprint`
- `solopreneur-standup`
- `solopreneur-story`
- `solopreneur-scaffold`

## Usage examples

After installation, Codex can activate Solopreneur skills automatically or by name. Examples:

- `Use using-solopreneur and help me figure out the right workflow for a new SaaS idea.`
- `Use solopreneur-discover for an AI meal planner idea.`
- `Use solopreneur-build for .solopreneur/backlog/meal-planner/MVP-001.md.`
- `Use solopreneur-review on the most recent changes.`

## Compatibility guarantees

- Claude plugin packaging stays in `.claude-plugin/`.
- Claude hooks stay in `hooks/hooks.json`.
- Claude settings stay in `settings.json`.
- Shared workflow content stays in `skills/*/SKILL.md`.
- Shared role briefs stay in `agents/*.md`.

Codex support is additive rather than a replacement for Claude Code.
