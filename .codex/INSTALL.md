# Installing Solopreneur for Codex

Solopreneur supports Codex without duplicating plugin files. The repository root is the plugin root: Codex reads `.codex-plugin/plugin.json`, and the skills come from the same `skills/` directory used by Claude Code.

## Recommended: Plugin Marketplace

Normal users do not need to clone the repository first.

```bash
codex plugin marketplace add pcatattacks/solopreneur-plugin
```

Then open Codex, install or enable the `solopreneur` plugin from the marketplace UI, and restart Codex if prompted.

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
- Project scope: if your Codex build exposes project-scoped plugin config, add the marketplace while the target project is active and verify Solopreneur appears only there.
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
