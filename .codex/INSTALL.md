# Installing Solopreneur for Codex

Solopreneur supports Codex without duplicating plugin files. The repository root is both the marketplace root and the plugin root: Codex reads the existing Claude-style marketplace at `.claude-plugin/marketplace.json`, which points to `./`, then reads `.codex-plugin/plugin.json` and the shared `skills/` directory.

## Recommended: Plugin Marketplace

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

Project-local Codex config is only active when the project `.codex/` layer is trusted. The hook records decision-like user prompts to the same project-local `.solopreneur/observer-log.md` used by Claude Code. Solopreneur still works without this flag, but Codex will not run bundled hooks.

After this branch is merged to `main`, use the same command without the test ref:

```bash
codex plugin marketplace add pcatattacks/solopreneur-plugin
```

## Local Development Install

From any directory:

```bash
codex plugin marketplace add /absolute/path/to/solopreneur-plugin
```

For this checkout:

```bash
codex plugin marketplace add /Users/pranavdhingra/dev/solopreneur-plugin
```

This is the best path while developing the plugin because Codex reads the root plugin manifest directly.

## Native Skill Discovery Fallback

If your Codex build cannot install local plugin marketplaces yet, link the shared skills directory into Codex native skill discovery:

```bash
git clone https://github.com/pcatattacks/solopreneur-plugin.git ~/.codex/solopreneur-plugin
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s ~/.codex/solopreneur-plugin/skills "${CODEX_HOME:-$HOME/.codex}/skills/solopreneur"
```

Restart Codex after creating the link.

## Scope Notes

Codex plugin scope behavior depends on the Codex version and UI surface:

- User scope: add the marketplace from your normal Codex config and enable Solopreneur globally.
- Project scope: if your Codex build exposes project-scoped plugin config, add the marketplace while the target project is active and verify Solopreneur appears only there. For repo-scoped observer logging, add `[features].codex_hooks = true` to that repo's `.codex/config.toml` and trust the project config when Codex prompts.
- Local development: use `codex plugin marketplace add /absolute/path/to/solopreneur-plugin`.
- Fallback: symlink `skills/` into `${CODEX_HOME:-$HOME/.codex}/skills/solopreneur`.

Always verify the chosen scope by starting a fresh Codex session and asking for Solopreneur help.

## Verify

```bash
python3 scripts/validate-plugin-packaging.py
scripts/verify-codex-install.sh
bash evals/run-evals.sh --runner codex --dry
```

Then in Codex, ask:

```text
Show me what my Solopreneur team can do.
```

## Update

```bash
cd ~/.codex/solopreneur-plugin
git pull
```

If installed through a marketplace, use the Codex plugin marketplace upgrade flow for your Codex build.

## Uninstall

For the symlink fallback:

```bash
rm "${CODEX_HOME:-$HOME/.codex}/skills/solopreneur"
```

For marketplace installs, remove the marketplace or disable the plugin in Codex.
