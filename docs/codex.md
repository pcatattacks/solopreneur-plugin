# Solopreneur on Codex

Solopreneur is packaged as a root-level Codex plugin. The Codex manifest lives at `.codex-plugin/plugin.json` and points at the shared root `skills/` directory. There is no copied Codex-only skill tree.

## Install Options

### Direct Marketplace Install

Normal users do not need to clone the repository first.

```bash
codex plugin marketplace add pcatattacks/solopreneur-plugin
```

Install or enable `solopreneur` in Codex after registering the marketplace.

### Local Checkout

```bash
codex plugin marketplace add /Users/pranavdhingra/dev/solopreneur-plugin
```

Use this for development. It lets Codex read the root `.codex-plugin/plugin.json` and shared `skills/` directly.

### Native Skill Discovery Fallback

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s /Users/pranavdhingra/dev/solopreneur-plugin/skills "${CODEX_HOME:-$HOME/.codex}/skills/solopreneur"
```

Restart Codex after linking.

## Scope Verification

Use the following checks for each scope you configure:

1. Start a fresh Codex session in the intended scope.
2. Ask: `Show me what my Solopreneur team can do.`
3. Confirm Solopreneur skills appear.
4. Start a fresh Codex session outside that scope.
5. Confirm Solopreneur availability matches the intended scope.

If your Codex build does not expose separate project/local scope controls for plugins, use local marketplace registration for development and the symlink fallback for user-level native skill discovery.

## Platform Differences

- Claude Code slash commands use forms like `/solopreneur:discover`.
- Codex can invoke plugin skills through skill discovery and natural-language requests such as `Run the Solopreneur discover skill for ...`.
- Claude-specific hooks still live in `hooks/hooks.json`; Codex behavior is driven mainly through `.codex-plugin/plugin.json`, `AGENTS.md`, and discovered skills.
- Browser QA uses whatever browser tooling the runner exposes. Claude Chrome Extension instructions apply only to Claude Code.

## Evals

Dry runs do not require model calls:

```bash
bash evals/run-evals.sh --dry
bash evals/run-evals.sh --runner codex --dry
scripts/verify-codex-install.sh
```

Full Codex eval execution uses `codex exec`:

```bash
bash evals/run-evals.sh --runner codex
```

Claude remains the default runner:

```bash
bash evals/run-evals.sh --runner claude
```
