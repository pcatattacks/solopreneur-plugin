#!/usr/bin/env python3
"""Validate Claude/Codex plugin packaging for the shared root layout."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    try:
        with path.open() as handle:
            return json.load(handle)
    except FileNotFoundError:
        fail(f"missing {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")


def require_path(path: Path) -> None:
    if not path.exists():
        fail(f"missing {path.relative_to(ROOT)}")


def main() -> int:
    for rel in [
        ".claude-plugin/plugin.json",
        ".claude-plugin/marketplace.json",
        ".codex-plugin/plugin.json",
        ".codex/INSTALL.md",
        "AGENTS.md",
        "CLAUDE.md",
        "skills",
        "agents",
        "hooks/hooks.json",
        "hooks/codex-hooks.json",
        "scripts/observer-log.sh",
        "scripts/verify-codex-install.sh",
        "evals/run-evals.sh",
        "docs/codex.md",
    ]:
        require_path(ROOT / rel)

    claude = load_json(ROOT / ".claude-plugin/plugin.json")
    codex = load_json(ROOT / ".codex-plugin/plugin.json")
    claude_marketplace = load_json(ROOT / ".claude-plugin/marketplace.json")

    if claude.get("name") != "solopreneur":
        fail(".claude-plugin/plugin.json name must be solopreneur")
    if codex.get("name") != "solopreneur":
        fail(".codex-plugin/plugin.json name must be solopreneur")
    if codex.get("skills") != "./skills/":
        fail(".codex-plugin/plugin.json must reference shared ./skills/")
    if codex.get("mcpServers") != "./.mcp.json":
        fail(".codex-plugin/plugin.json must reference shared ./.mcp.json")
    if codex.get("hooks") != "./hooks/codex-hooks.json":
        fail(".codex-plugin/plugin.json must point Codex at safe hook config")
    if claude_marketplace.get("name") != "solopreneur":
        fail(".claude-plugin/marketplace.json name must be solopreneur")
    entries = claude_marketplace.get("plugins")
    if not isinstance(entries, list) or len(entries) != 1:
        fail(".claude-plugin/marketplace.json must contain exactly one plugin entry")
    entry = entries[0]
    if entry.get("name") != "solopreneur":
        fail(".claude-plugin/marketplace.json plugin entry name must be solopreneur")
    if entry.get("source") != "./":
        fail(".claude-plugin/marketplace.json must point solopreneur at the shared repo root")
    if (ROOT / ".agents").exists():
        fail("do not keep a Codex-only .agents marketplace; use the shared Claude-style marketplace")
    if (ROOT / ".codex" / "agents").exists():
        fail("do not create duplicated native Codex agents; use shared agents/*.md role prompts")
    if (ROOT / "plugins" / "solopreneur" / "skills").exists():
        fail("do not create a duplicated plugins/solopreneur/skills tree")

    codex_hooks = load_json(ROOT / "hooks/codex-hooks.json")
    user_prompt_hooks = codex_hooks.get("hooks", {}).get("UserPromptSubmit", [])
    if not user_prompt_hooks:
        fail("hooks/codex-hooks.json must register a Codex UserPromptSubmit observer hook")
    hook_commands = [
        hook.get("command", "")
        for group in user_prompt_hooks
        for hook in group.get("hooks", [])
        if isinstance(hook, dict)
    ]
    if not any("scripts/observer-log.sh" in command for command in hook_commands):
        fail("hooks/codex-hooks.json must route Codex prompts to scripts/observer-log.sh")

    agents = ROOT / "AGENTS.md"
    if agents.is_symlink():
        if agents.readlink().as_posix() != "CLAUDE.md":
            fail("AGENTS.md symlink must point to CLAUDE.md")
    else:
        text = agents.read_text()
        if "CLAUDE.md" not in text:
            fail("AGENTS.md must point Codex to CLAUDE.md when not symlinked")

    readme = (ROOT / "README.md").read_text()
    for needle in [
        "Install in Claude Code",
        "Install in Codex",
        "Scope and Install Verification",
        "bash evals/run-evals.sh --runner codex --dry",
    ]:
        if needle not in readme:
            fail(f"README.md missing required docs: {needle}")

    handbook = (ROOT / "CLAUDE.md").read_text()
    for needle in [
        "not native Codex custom agents",
        "spawn a generic Codex subagent",
        "agents/<role>.md",
    ]:
        if needle not in handbook:
            fail(f"CLAUDE.md missing Codex role delegation bridge: {needle}")

    codex_docs = (ROOT / "docs/codex.md").read_text()
    for needle in [
        "subagent workflows are enabled by default",
        "target project's `.codex/config.toml`",
        "not native Codex custom agents",
        "spawn a generic",
    ]:
        if needle not in codex_docs:
            fail(f"docs/codex.md missing Codex role delegation docs: {needle}")

    print("OK: shared root Claude/Codex plugin packaging is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
