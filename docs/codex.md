# Solopreneur on Codex

Solopreneur is packaged as a root-level Codex plugin. Codex reads the existing Claude-style marketplace at `.claude-plugin/marketplace.json`, whose `solopreneur` entry points to `./`, so the Codex manifest at `.codex-plugin/plugin.json` and the shared root `skills/` directory are used directly. There is no copied Codex-only skill tree.

## Install Options

### Direct Marketplace Install

Normal users do not need to clone the repository first.

For this branch, add the marketplace with the test ref:

```bash
codex plugin marketplace add pcatattacks/solopreneur-plugin --ref codex-plugin-compat
```

Then install the plugin in Codex:

1. Open Codex and run `/plugins`.
2. Select the `Solopreneur` marketplace tab.
3. Install or enable the `solopreneur` plugin.
4. Restart Codex if prompted, then start a fresh session.

Codex subagent workflows are enabled by default in current Codex releases. No feature flag is required for Solopreneur role delegation.

To enable the observer hook for every Codex project, turn on Codex hooks in `${CODEX_HOME:-$HOME/.codex}/config.toml`:

```toml
[features]
codex_hooks = true
```

For project/repo scope only, put the same flag in the target project's `.codex/config.toml`:

```toml
[features]
codex_hooks = true
```

Project-local Codex config is only active when the project `.codex/` layer is trusted. `codex_hooks` lets Codex run the bundled `UserPromptSubmit` hook and record decision-like prompts to `.solopreneur/observer-log.md`.

After this branch is merged to `main`, use the same command without the test ref:

```bash
codex plugin marketplace add pcatattacks/solopreneur-plugin
```

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

## Role Delegation Test Scenarios

Use these after installing Solopreneur in Codex:

1. **Explicit ad-hoc team**: ask `Run Solopreneur kickoff code review with @engineer @qa on this auth flow`. Expected: Codex reads `agents/engineer.md` and `agents/qa.md`, uses generic subagents, and returns distinct engineering and QA perspectives.
2. **Implicit team inference**: ask `Get the team together to debug this failing checkout flow`. Expected: Codex routes to kickoff, infers the Build & QA team, and uses the matching role files rather than inventing new roles.
3. **Single specialist**: ask `Run Solopreneur kickoff just with @researcher on market trends for AI invoicing`. Expected: Codex uses only `agents/researcher.md` and returns a focused research output.
4. **Lifecycle delegation**: ask `Run Solopreneur spec for a habit tracker with social accountability`. Expected: the spec workflow delegates technical feasibility to the engineer role and user-flow review to the designer role.
5. **Fallback behavior**: explicitly ask Codex not to spawn subagents. Expected: Solopreneur still works, but role work is simulated or briefed in-session instead of spawning Codex subagents.
6. **No duplication check**: confirm the installed plugin uses `agents/*.md` and does not require `.codex/agents/*.toml`.

## Platform Differences

- Claude Code slash commands use forms like `/solopreneur:discover`.
- Codex can invoke plugin skills through skill discovery and natural-language requests such as `Run the Solopreneur discover skill for ...`.
- Codex can read Claude-style marketplace files, so Solopreneur uses the existing `.claude-plugin/marketplace.json` for both Claude Code compatibility and Codex marketplace discovery.
- `agents/*.md` files are shared role prompt files, not native Codex custom agents. When a Solopreneur workflow mentions `@engineer`, `@qa`, `@designer`, `@bizops`, `@researcher`, or `@content-strategist`, Codex should read `agents/<role>.md` and spawn a generic `worker` or `explorer` subagent with that role brief plus the specific task.
- Claude Code hooks still live in `hooks/hooks.json`. Codex loads `hooks/codex-hooks.json` through `.codex-plugin/plugin.json`; when `[features].codex_hooks = true`, Codex records decision-like user prompts through `UserPromptSubmit` into the shared `.solopreneur/observer-log.md`.
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

Omit model flags to use the Codex CLI default. If you override models, pass exact Codex model ids accepted by `codex exec --model`; Claude aliases such as `haiku`, `sonnet`, and `opus` are rejected in Codex runner mode.

Claude remains the default runner:

```bash
bash evals/run-evals.sh --runner claude
```
