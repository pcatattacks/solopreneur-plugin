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
        ".agents/plugins/marketplace.json",
        ".codex/INSTALL.md",
        "AGENTS.md",
        "CLAUDE.md",
        "skills",
        "agents",
        "hooks/hooks.json",
        "scripts/observer-log.sh",
        "scripts/verify-codex-install.sh",
        "evals/run-evals.sh",
        "docs/codex.md",
    ]:
        require_path(ROOT / rel)

    claude = load_json(ROOT / ".claude-plugin/plugin.json")
    codex = load_json(ROOT / ".codex-plugin/plugin.json")
    codex_marketplace = load_json(ROOT / ".agents/plugins/marketplace.json")
    load_json(ROOT / ".claude-plugin/marketplace.json")

    if claude.get("name") != "solopreneur":
        fail(".claude-plugin/plugin.json name must be solopreneur")
    if codex.get("name") != "solopreneur":
        fail(".codex-plugin/plugin.json name must be solopreneur")
    if codex.get("skills") != "./skills/":
        fail(".codex-plugin/plugin.json must reference shared ./skills/")
    if codex.get("mcpServers") != "./.mcp.json":
        fail(".codex-plugin/plugin.json must reference shared ./.mcp.json")
    if codex_marketplace.get("name") != "solopreneur":
        fail(".agents/plugins/marketplace.json name must be solopreneur")
    entries = codex_marketplace.get("plugins")
    if not isinstance(entries, list) or len(entries) != 1:
        fail(".agents/plugins/marketplace.json must contain exactly one plugin entry")
    entry = entries[0]
    if entry.get("name") != "solopreneur":
        fail(".agents/plugins/marketplace.json plugin entry name must be solopreneur")
    source = entry.get("source", {})
    if source.get("source") != "local" or source.get("path") != ".":
        fail(".agents/plugins/marketplace.json must point solopreneur at the shared repo root")
    policy = entry.get("policy", {})
    if policy.get("installation") != "AVAILABLE" or policy.get("authentication") != "ON_INSTALL":
        fail(".agents/plugins/marketplace.json must mark solopreneur available on install")
    if (ROOT / "plugins" / "solopreneur" / "skills").exists():
        fail("do not create a duplicated plugins/solopreneur/skills tree")

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

    print("OK: shared root Claude/Codex plugin packaging is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
