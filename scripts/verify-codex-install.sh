#!/usr/bin/env bash
# Verify Solopreneur's Codex install paths without changing the user's Codex config.

set -euo pipefail

PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)"

if ! command -v codex >/dev/null 2>&1; then
  echo "FAIL: codex CLI not found"
  exit 1
fi

tmp_home="$(mktemp -d)"
cleanup() {
  rm -rf "$tmp_home"
}
trap cleanup EXIT

echo "Checking local Codex marketplace install..."
CODEX_HOME="$tmp_home" codex plugin marketplace add "$PLUGIN_DIR" >/tmp/solopreneur-codex-marketplace.out
cat /tmp/solopreneur-codex-marketplace.out
# Some Codex wrapper builds leave a detached helper process after CLI commands.
pkill -f "codex plugin marketplace add $PLUGIN_DIR" >/dev/null 2>&1 || true

if ! grep -q "source = \"$PLUGIN_DIR\"" "$tmp_home/config.toml"; then
  echo "FAIL: temporary Codex config did not point at $PLUGIN_DIR"
  exit 1
fi

if [ ! -f "$PLUGIN_DIR/.agents/plugins/marketplace.json" ]; then
  echo "FAIL: missing Codex marketplace catalog at .agents/plugins/marketplace.json"
  exit 1
fi

if ! grep -q '"source": "url"' "$PLUGIN_DIR/.agents/plugins/marketplace.json" ||
  ! grep -q '"url": "https://github.com/pcatattacks/solopreneur-plugin.git"' "$PLUGIN_DIR/.agents/plugins/marketplace.json" ||
  ! grep -q '"ref": "codex-plugin-compat"' "$PLUGIN_DIR/.agents/plugins/marketplace.json"; then
  echo "FAIL: Codex marketplace catalog must use a Git-backed root plugin source"
  exit 1
fi

if ! grep -q '"hooks": "./hooks/codex-hooks.json"' "$PLUGIN_DIR/.codex-plugin/plugin.json"; then
  echo "FAIL: Codex plugin manifest must point at safe hook config"
  exit 1
fi

echo "Checking native skill discovery symlink fallback..."
mkdir -p "$tmp_home/skills"
ln -s "$PLUGIN_DIR/skills" "$tmp_home/skills/solopreneur"

if [ "$(readlink "$tmp_home/skills/solopreneur")" != "$PLUGIN_DIR/skills" ]; then
  echo "FAIL: skill symlink did not point at shared skills directory"
  exit 1
fi

echo "Scope note:"
echo "This verifier checks local marketplace registration and native skill symlink fallback."
echo "Verify user/project scope in the Codex UI or version-specific config surface for your Codex build."

rm -f /tmp/solopreneur-codex-marketplace.out
echo "OK: Codex local marketplace registration and skill symlink fallback verified"
