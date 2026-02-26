#!/usr/bin/env python3
"""
Generate an interactive HTML org chart for an AI team plugin.

Produces a two-column layout: vertical workflow pipeline (left) connected
via SVG lines to agent detail cards (right).

Usage:
    # Auto-discover from a plugin directory (recommended):
    python3 visualize-org.py --plugin-dir . --output org-chart.html

    # From a JSON config:
    python3 visualize-org.py --config org.json --output org-chart.html

    # With marketing header/footer (for hosted landing page):
    python3 visualize-org.py --plugin-dir . --marketing --output docs/index.html

    # Quick mode with CLI args (flat, no connections):
    python3 visualize-org.py --name "My Org" --agents "Engineer,Designer" --output org-chart.html
"""

import argparse
import glob
import html
import json
import os
import re
import sys


def parse_frontmatter(content):
    """Extract YAML-like frontmatter and body from a markdown file.

    Supports simple key: value pairs, YAML lists (- items),
    and inline lists [a, b, c].
    """
    meta = {}
    body = content
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
    if match:
        raw_meta = match.group(1)
        body = match.group(2)

        current_key = None
        current_list = None

        for line in raw_meta.split('\n'):
            # List item: "  - value"
            list_match = re.match(r'^\s+-\s+(.+)$', line)
            if list_match and current_key:
                if current_list is None:
                    current_list = []
                current_list.append(list_match.group(1).strip())
                continue

            # Flush previous list
            if current_list is not None and current_key:
                meta[current_key] = current_list
                current_list = None

            # Key-value pair (non-indented lines with colon)
            if ':' in line and not line.startswith(' '):
                key, val = line.split(':', 1)
                key = key.strip()
                val = val.strip()
                current_key = key

                if val:
                    # Inline list: [a, b, c]
                    inline_match = re.match(r'^\[(.+)\]$', val)
                    if inline_match:
                        meta[key] = [item.strip().strip('"').strip("'")
                                     for item in inline_match.group(1).split(',')]
                    else:
                        meta[key] = val
                # else: might be followed by a YAML list

        # Flush final list
        if current_list is not None and current_key:
            meta[current_key] = current_list

    return meta, body


def shorten_description(desc, max_len=40):
    """Shorten a long description to a card-friendly label."""
    if not desc or len(desc) <= max_len:
        return desc
    spec_match = re.search(r'specializing in ([^.]+)', desc)
    if spec_match:
        parts = [p.strip() for p in re.split(r',\s*(?:and\s+)?', spec_match.group(1))]
        if len(parts) >= 2:
            return fix_name_casing(f"{parts[0].title()} & {parts[1]}")
        return fix_name_casing(parts[0].title())
    for_match = re.search(r'(?:for|covering) ([^.]+)', desc)
    if for_match:
        target = for_match.group(1).strip()
        if not re.match(r'^(?:a|an|the)\s', target, re.IGNORECASE):
            parts = [p.strip() for p in re.split(r',\s*(?:and\s+)?', target)]
            if len(parts) >= 2:
                return fix_name_casing(f"{parts[0].title()} & {parts[1]}")
            return fix_name_casing(parts[0].title())
    first = desc.split('.')[0]
    clause = first.split(',')[0]
    if len(clause) <= max_len:
        return fix_name_casing(clause)
    if len(first) <= max_len:
        return fix_name_casing(first)
    return fix_name_casing(first[:max_len - 3] + "...")


def fix_name_casing(name):
    """Fix casing for known abbreviations and compound words."""
    abbreviations = {"qa": "QA", "ui": "UI", "ux": "UX", "ui/ux": "UI/UX", "api": "API",
                     "ci": "CI", "cd": "CD", "pr": "PR", "prd": "PRD",
                     "cto": "CTO", "ceo": "CEO", "devops": "DevOps", "bizops": "BizOps",
                     "github": "GitHub", "devtools": "DevTools"}
    if name.lower() in abbreviations:
        return abbreviations[name.lower()]
    words = name.split()
    fixed = []
    for w in words:
        if w.lower() in abbreviations:
            fixed.append(abbreviations[w.lower()])
        else:
            fixed.append(w)
    return " ".join(fixed)


# Skills that are meta/orchestration and shouldn't appear on agent cards
META_SKILLS = {"sprint", "standup", "scaffold", "help", "kickoff", "story"}


def build_from_cli(args):
    """Build config dict from CLI arguments for backwards compatibility."""
    agents = [a.strip() for a in args.agents.split(",") if a.strip()] if args.agents else []
    skills = [s.strip() for s in args.skills.split(",") if s.strip()] if args.skills else []
    mcps_list = [m.strip() for m in args.mcps.split(",") if m.strip()] if args.mcps else []

    teams = []
    if args.teams:
        for t in args.teams.split(","):
            parts = t.strip().split(":")
            if len(parts) == 2:
                teams.append({
                    "name": parts[0].strip(),
                    "members": [m.strip() for m in parts[1].split("+")]
                })

    return {
        "name": args.name or "My AI Org",
        "agents": [{"name": a, "model": "inherit", "skills": skills, "knowledge_skills": [],
                     "mcps": mcps_list, "cli_tools": [], "description": ""} for a in agents],
        "skills": [{"name": s, "description": ""} for s in skills],
        "mcps": [{"name": m, "description": ""} for m in mcps_list],
        "cli_tools": [],
        "teams": teams,
        "lifecycle": skills[:7],
        "alternate_paths": []
    }


def build_from_plugin(plugin_dir):
    """Auto-discover agents, skills, and MCPs from a plugin directory."""
    plugin_dir = os.path.abspath(plugin_dir)

    # Read plugin name from plugin.json
    name = "My AI Org"
    plugin_json = os.path.join(plugin_dir, ".claude-plugin", "plugin.json")
    if os.path.isfile(plugin_json):
        with open(plugin_json) as f:
            pj = json.load(f)
            name = pj.get("name", name).replace("-", " ").title()

    # Read CLAUDE.md for lifecycle and team hints
    claude_content = ""
    claude_md = os.path.join(plugin_dir, "CLAUDE.md")
    if os.path.isfile(claude_md):
        with open(claude_md) as f:
            claude_content = f.read()

    # Discover agents from agents/*.md
    agents = []
    agent_dir = os.path.join(plugin_dir, "agents")
    if os.path.isdir(agent_dir):
        for path in sorted(glob.glob(os.path.join(agent_dir, "*.md"))):
            with open(path) as f:
                content = f.read()
            meta, body = parse_frontmatter(content)
            agent_name = meta.get("name", os.path.splitext(os.path.basename(path))[0])
            if agent_name.lower() == "observer":
                continue
            full_desc = meta.get("description", "")
            display_name = fix_name_casing(agent_name.replace("-", " ").title())

            # Parse knowledge skills from frontmatter 'skills' field
            raw_skills = meta.get("skills", [])
            if isinstance(raw_skills, str):
                raw_skills = [s.strip() for s in raw_skills.split(",") if s.strip()]

            agents.append({
                "name": display_name,
                "model": meta.get("model", "inherit"),
                "skills": [],  # operational — computed below via @agent scanning
                "knowledge_skills": raw_skills,
                "mcps": [],
                "cli_tools": [],
                "description": shorten_description(full_desc),
                "detail_description": full_desc,
                "markdown": body.strip()
            })

    # Discover skills from skills/*/SKILL.md
    skills = []
    skill_bodies = {}
    skills_dir = os.path.join(plugin_dir, "skills")
    if os.path.isdir(skills_dir):
        for skill_dir_path in sorted(glob.glob(os.path.join(skills_dir, "*"))):
            skill_md = os.path.join(skill_dir_path, "SKILL.md")
            if not os.path.isfile(skill_md):
                continue
            with open(skill_md) as f:
                content = f.read()
            meta, body = parse_frontmatter(content)
            skill_name = meta.get("name", os.path.basename(skill_dir_path))
            full_desc = meta.get("description", "")
            skills.append({
                "name": skill_name,
                "description": shorten_description(full_desc),
                "detail_description": full_desc,
                "markdown": body.strip()
            })
            skill_bodies[skill_name] = body

    # Map skills to agents using dual-direction parsing
    skill_names = {s["name"] for s in skills}
    agent_name_lower = {a["name"].lower().replace(" ", "-"): a for a in agents}
    agent_name_lower.update({a["name"].lower().replace(" ", ""): a for a in agents})
    agent_name_lower.update({a["name"].lower(): a for a in agents})

    # Forward: scan skill bodies for @agent references (skip meta-skills)
    for skill_name, body in skill_bodies.items():
        if skill_name in META_SKILLS:
            continue
        for ref in re.findall(r'@(\w[\w-]*)', body):
            ref_lower = ref.lower()
            if ref_lower in agent_name_lower:
                agent = agent_name_lower[ref_lower]
                if skill_name not in agent["skills"]:
                    agent["skills"].append(skill_name)

    # Reverse: scan agent "When Delegated To" sections for /skill references
    for agent in agents:
        agent_body = agent.get("markdown", "")
        delegated_section = re.search(r'When Delegated To.*?$', agent_body, re.DOTALL | re.MULTILINE)
        if delegated_section:
            section_text = delegated_section.group(0)
            for sn in skill_names:
                if sn in META_SKILLS:
                    continue
                if f"/{sn}" in section_text or f"`{sn}`" in section_text:
                    if sn not in agent["skills"]:
                        agent["skills"].append(sn)

    # Discover MCPs from .mcp.json
    mcps = []
    mcp_json = os.path.join(plugin_dir, ".mcp.json")
    if os.path.isfile(mcp_json):
        with open(mcp_json) as f:
            mcp_data = json.load(f)
        for server_name, server_cfg in mcp_data.get("mcpServers", {}).items():
            display_name = fix_name_casing(server_name.replace("-", " ").title())
            cmd = server_cfg.get("command", "")
            mcp_args = server_cfg.get("args", [])
            desc = f"Command: {cmd} {' '.join(mcp_args[:2])}" if cmd else ""
            mcps.append({"name": display_name, "description": "", "detail_description": desc})

    # Discover CLI tools from CLAUDE.md
    cli_tools = []
    if claude_content:
        cli_section = re.search(r'### CLI Tools\n(.*?)(?=\n###|\n##|\Z)', claude_content, re.DOTALL)
        if cli_section:
            for line in cli_section.group(1).split('\n'):
                if not line.strip().startswith('-'):
                    continue
                tool_match = re.search(r'\*\*([^*]+?)(?:\s*\([^)]*\))?\*\*', line)
                if tool_match:
                    raw_name = tool_match.group(1).strip()
                    display_name = fix_name_casing(raw_name)
                    desc_match = re.search(r'\*\*:\s*(.+)', line)
                    desc = desc_match.group(1).strip() if desc_match else ""
                    cli_tools.append({"name": display_name, "description": desc})

    # Assign MCPs to agents based on CLAUDE.md per-bullet hints
    if mcps and claude_content:
        tool_section = re.search(r'Tool Access.*?(?=^#[^#]|\Z)', claude_content, re.DOTALL | re.MULTILINE)
        if tool_section:
            for line in tool_section.group(0).split('\n'):
                if not line.strip().startswith('-'):
                    continue
                line_lower = line.lower()
                matched_mcp = None
                for mcp in mcps:
                    if mcp["name"].lower() in line_lower:
                        matched_mcp = mcp
                        break
                if not matched_mcp:
                    continue
                for agent in agents:
                    if agent["name"].lower() in line_lower:
                        if matched_mcp["name"] not in agent["mcps"]:
                            agent["mcps"].append(matched_mcp["name"])

    # Fallback: role-based heuristics for agents with no MCPs assigned
    for agent in agents:
        if not agent["mcps"] and mcps:
            agent_lower = agent["name"].lower()
            tools = agent.get("detail_description", "").lower()
            for mcp in mcps:
                mcp_lower = mcp["name"].lower()
                if "devtools" in mcp_lower and ("ui" in tools or "design" in agent_lower):
                    agent["mcps"].append(mcp["name"])
                elif "context" in mcp_lower and ("research" in agent_lower):
                    agent["mcps"].append(mcp["name"])

    # Assign CLI tools to agents (heuristic: code-related roles get gh)
    for agent in agents:
        agent_lower = agent["name"].lower()
        for tool in cli_tools:
            tool_lower = tool["name"].lower()
            if "github" in tool_lower and agent_lower in ("engineer", "qa"):
                agent["cli_tools"].append(tool["name"])

    # Parse lifecycle from CLAUDE.md
    lifecycle = []
    lc_match = re.search(r'(/[\w-]+:[\w-]+(?:\s*→\s*/[\w-]+:[\w-]+)+)', claude_content)
    if lc_match:
        lifecycle = [s.split(":")[-1].strip() for s in lc_match.group(1).split("→")]
    if not lifecycle:
        core_skills = ["discover", "spec", "design", "build", "review", "ship"]
        lifecycle = [s for s in core_skills if s in skill_names]

    # Build teams — first try parsing named teams from CLAUDE.md, fall back to skill heuristics
    teams = []
    agent_names_set = {a["name"].lower() for a in agents}
    agent_display = {a["name"].lower(): a["name"] for a in agents}
    # Parse "**Team Name**: @agent + @agent + @agent" patterns from CLAUDE.md
    team_pattern = re.findall(
        r'\*\*([^*]+)\*\*:\s*(@[\w-]+(?:\s*\+\s*@[\w-]+)*)',
        claude_content
    )
    for team_name, members_str in team_pattern:
        member_refs = re.findall(r'@([\w-]+)', members_str)
        resolved = []
        for ref in member_refs:
            ref_lower = ref.lower().replace("-", " ")
            if ref_lower in agent_display:
                resolved.append(agent_display[ref_lower])
            elif ref.lower().replace("-", " ") in agent_names_set:
                resolved.append(fix_name_casing(ref.replace("-", " ").title()))
        if resolved:
            teams.append({"name": team_name.strip(), "members": resolved})
    # Fallback: build from agent skills if no teams found in CLAUDE.md
    if not teams:
        agent_names = [a["name"] for a in agents]
        if len(agent_names) >= 3:
            discovery_agents = [a["name"] for a in agents
                               if any(s in a["skills"] for s in ["discover"])]
            build_agents = [a["name"] for a in agents
                           if any(s in a["skills"] for s in ["build", "design", "review"])]
            ship_agents = [a["name"] for a in agents
                          if any(s in a["skills"] for s in ["ship", "release-notes"])]
            if discovery_agents:
                teams.append({"name": "Discovery Sprint", "members": discovery_agents})
            if build_agents:
                teams.append({"name": "Build & QA", "members": build_agents})
            if ship_agents:
                teams.append({"name": "Ship & Launch", "members": ship_agents})

    # Build alternate paths from meta-skills that exist
    alternate_paths = []
    meta_skill_names = {s["name"] for s in skills} & META_SKILLS
    if "sprint" in meta_skill_names:
        alternate_paths.append({
            "name": "sprint",
            "description": "Batch-execute multiple tickets in parallel",
            "replaces": ["build"]
        })
    if "kickoff" in meta_skill_names:
        alternate_paths.append({
            "name": "kickoff",
            "description": "Team meeting \u2014 use at any point",
            "type": "anytime"
        })
    if "standup" in meta_skill_names:
        alternate_paths.append({
            "name": "standup",
            "description": "Daily summary",
            "type": "anytime"
        })

    # Build utility skills list (meta-skills with their agent mappings)
    utility_skills = []
    for sk in skills:
        if sk["name"] not in META_SKILLS:
            continue
        # Scan skill body for @agent references
        sk_agents = []
        body = skill_bodies.get(sk["name"], "")
        for ref in re.findall(r'@(\w[\w-]*)', body):
            ref_lower = ref.lower()
            if ref_lower in agent_name_lower:
                agent = agent_name_lower[ref_lower]
                if agent["name"] not in sk_agents:
                    sk_agents.append(agent["name"])
        utility_skills.append({
            "name": sk["name"],
            "description": sk.get("description", ""),
            "agents": sk_agents
        })

    return {
        "name": name,
        "agents": agents,
        "skills": skills,
        "mcps": mcps,
        "cli_tools": cli_tools,
        "teams": teams,
        "lifecycle": lifecycle,
        "alternate_paths": alternate_paths,
        "utility_skills": utility_skills
    }


def e(text):
    """HTML-escape shorthand."""
    return html.escape(str(text))


AGENT_COLORS = [
    '#3b82f6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4', '#8b5cf6',
    '#f97316', '#14b8a6', '#a855f7', '#ef4444',
]

PHASE_DEFS = [
    {"label": "Discovery", "color": "#06b6d4"},
    {"label": "Planning", "color": "#ec4899"},
    {"label": "Execution", "color": "#3b82f6"},
    {"label": "Launch", "color": "#10b981"},
]

# Icons for utility / value-prop skills
VP_ICONS = {
    "sprint": "\u26a1",
    "observer": "\U0001f9e0",
    "story": "\U0001f4d6",
    "scaffold": "\U0001f3d7\ufe0f",
    "standup": "\U0001f4cb",
    "help": "\u2753",
    "kickoff": "\U0001f91d",
}

# Default VP descriptions when the config doesn't supply one
VP_DEFAULTS = {
    "sprint": "Execute a batch of tickets in parallel — one Engineer per ticket, then QA and Designer review simultaneously.",
    "story": "Turn your decision log into a publishable narrative — tutorial, case study, blog post, or launch story.",
    "scaffold": "Design and build your own custom AI org — define your own agents, skills, and workflows from scratch.",
    "standup": "Generate a daily summary from git history, observer log, and project artifacts.",
    "help": "Get oriented — see your team, check project status, and find what to do next.",
    "kickoff": "Collaborative agent team meetings — pre-configured or ad-hoc.",
}

# Preferred display order for known agents and VP cards.
# Agents/skills not in the list sort alphabetically at the end.
PREFERRED_AGENT_ORDER = [
    "engineer", "designer", "bizops", "qa", "researcher", "content strategist",
]
PREFERRED_VP_ORDER = [
    "sprint", "observer", "story", "scaffold", "standup", "help",
]


def _order_key(names_list):
    """Return a sort-key function for preferred ordering."""
    index = {n: i for i, n in enumerate(names_list)}
    sentinel = len(names_list)
    return lambda item: (index.get(item, sentinel), item)


def assign_agent_colors(agents):
    """Assign colors from palette to agents. Returns dict of name -> color."""
    color_map = {}
    # Well-known default colors for common agent names
    known = {
        'engineer': '#3b82f6', 'designer': '#ec4899', 'bizops': '#f59e0b',
        'qa': '#10b981', 'researcher': '#06b6d4', 'content strategist': '#8b5cf6',
        'content': '#8b5cf6',
    }
    used_colors = set()
    for agent in agents:
        name_lower = agent.get("name", "").lower()
        if name_lower in known:
            color_map[agent["name"]] = known[name_lower]
            used_colors.add(known[name_lower])
    # Assign remaining from palette
    palette_idx = 0
    for agent in agents:
        if agent["name"] not in color_map:
            while palette_idx < len(AGENT_COLORS) and AGENT_COLORS[palette_idx] in used_colors:
                palette_idx += 1
            color_map[agent["name"]] = AGENT_COLORS[palette_idx % len(AGENT_COLORS)]
            used_colors.add(color_map[agent["name"]])
            palette_idx += 1
    return color_map


def build_lifecycle_data(lifecycle, agents, skills, alternate_paths, color_map):
    """Build lifecycle steps with agent roles and phase grouping.

    Returns a list of step dicts with phase indices assigned.
    """
    skill_desc = {s["name"]: s.get("description", "") for s in skills}

    # Build agent -> skills mapping and agent lookup
    agent_by_name = {}
    agent_skills_map = {}  # skill_name -> list of agent names
    for agent in agents:
        agent_by_name[agent["name"]] = agent
        for sk in agent.get("skills", []):
            agent_skills_map.setdefault(sk, [])
            if agent["name"] not in agent_skills_map[sk]:
                agent_skills_map[sk].append(agent["name"])

    # Assign phases: distribute lifecycle steps across 4 phases
    n = len(lifecycle)
    if n == 8:
        phase_assignment = [0, 0, 1, 1, 2, 2, 3, 3]
    elif n <= 4:
        phase_assignment = list(range(n))
    else:
        phase_assignment = []
        per_phase = n / 4
        for i in range(n):
            phase_assignment.append(min(3, int(i / per_phase)))

    steps = []
    for i, skill_name in enumerate(lifecycle):
        phase_idx = phase_assignment[i] if i < len(phase_assignment) else 3
        involved_agents = agent_skills_map.get(skill_name, [])
        agent_roles = []
        for aname in involved_agents:
            agent = agent_by_name.get(aname)
            if not agent:
                continue
            # Use description as fallback role text
            role = agent.get("description", "")
            agent_roles.append({
                "id": aname.lower().replace(" ", "-"),
                "name": aname,
                "color": color_map.get(aname, "#94a3b8"),
                "role": role,
            })
        steps.append({
            "skill": skill_name,
            "desc": skill_desc.get(skill_name, ""),
            "phase": phase_idx,
            "agents": agent_roles,
        })

    # Find sprint alternate path
    sprint_alt = None
    for ap in alternate_paths:
        if ap.get("name") == "sprint":
            sprint_alt = ap
            break

    return steps, sprint_alt


def generate_html(config, marketing=False):
    """Generate a self-contained HTML org chart matching the dark-theme design."""
    name = config.get("name", "My AI Org")
    agents = config.get("agents", [])
    skills = config.get("skills", [])
    teams = config.get("teams", [])
    lifecycle = config.get("lifecycle", [])
    alternate_paths = config.get("alternate_paths", [])
    utility_skills = config.get("utility_skills", [])

    # -- Build data structures --
    color_map = assign_agent_colors(agents)
    lifecycle_steps, sprint_alt = build_lifecycle_data(
        lifecycle, agents, skills, alternate_paths, color_map
    )

    # Build JS-consumable agent list
    agent_data = []
    for agent in agents:
        tools = list(agent.get("mcps", []))
        for ct in agent.get("cli_tools", []):
            tools.append(f"{ct} CLI")
        agent_data.append({
            "id": agent["name"].lower().replace(" ", "-"),
            "name": agent["name"],
            "color": color_map.get(agent["name"], "#94a3b8"),
            "model": agent.get("model") or "inherit",
            "desc": agent.get("description", ""),
            "tools": tools,
            "skills": agent.get("skills", []),
            "knowledge_skills": agent.get("knowledge_skills", []),
            "mcps": agent.get("mcps", []),
            "cli_tools": agent.get("cli_tools", []),
            "detail_description": agent.get("detail_description", "") or agent.get("description", ""),
        })

    # Sort agents by preferred display order
    agent_key = _order_key(PREFERRED_AGENT_ORDER)
    agent_data.sort(key=lambda a: agent_key(a["id"].replace("-", " ")))

    # Build VP cards from utility_skills or alternate_paths
    vp_cards = []
    # Always include decision memory (observer) — it's not a skill but a feature
    vp_cards.append({
        "icon": VP_ICONS.get("observer", "\U0001f9e0"),
        "skill": "observer",
        "name": "Decision memory",
        "desc": "Every choice you make is logged with your reasoning. Not what changed (git handles that) — but WHY you chose it.",
        "agents": ["orchestrator"],
    })
    if utility_skills:
        for us in utility_skills:
            sk_name = us["name"]
            if sk_name == "kickoff":
                continue  # kickoff is shown in teams section
            agent_ids = []
            for aname in us.get("agents", []):
                agent_ids.append(aname.lower().replace(" ", "-"))
            if not agent_ids:
                agent_ids = ["orchestrator"]
            vp_cards.append({
                "icon": VP_ICONS.get(sk_name, "\u2699\ufe0f"),
                "skill": sk_name,
                "name": f"/{sk_name}",
                "desc": us.get("description", "") or VP_DEFAULTS.get(sk_name, ""),
                "agents": agent_ids,
            })
    else:
        # Fallback: build from alternate_paths for non-plugin configs
        for ap in alternate_paths:
            sk_name = ap["name"]
            if sk_name == "sprint" or sk_name == "kickoff":
                continue
            vp_cards.append({
                "icon": VP_ICONS.get(sk_name, "\u2699\ufe0f"),
                "skill": sk_name,
                "name": f"/{sk_name}",
                "desc": ap.get("description", "") or VP_DEFAULTS.get(sk_name, ""),
                "agents": ["orchestrator"],
            })
        # Add well-known utility skills that might be in skills list
        skill_names_set = {s["name"] for s in skills}
        for sk_name in ["story", "scaffold", "help"]:
            if sk_name in skill_names_set and not any(v["skill"] == sk_name for v in vp_cards):
                sk_obj = next((s for s in skills if s["name"] == sk_name), None)
                vp_cards.append({
                    "icon": VP_ICONS.get(sk_name, "\u2699\ufe0f"),
                    "skill": sk_name,
                    "name": f"/{sk_name}",
                    "desc": sk_obj.get("description", "") if sk_obj else VP_DEFAULTS.get(sk_name, ""),
                    "agents": ["orchestrator"],
                })

    # Sort VP cards by preferred display order
    vp_key = _order_key(PREFERRED_VP_ORDER)
    vp_cards.sort(key=lambda v: vp_key(v["skill"]))

    # Build team data
    team_data = []
    for tm in teams:
        members = []
        for mname in tm.get("members", []):
            members.append({
                "id": mname.lower().replace(" ", "-"),
                "name": mname,
                "color": color_map.get(mname, "#94a3b8"),
            })
        team_data.append({
            "name": tm["name"],
            "purpose": tm.get("description", ""),
            "members": members,
        })

    # Build detail data for the panel
    detail_data = {}
    for agent in agents:
        key = f"agent-{agent['name'].lower().replace(' ', '-')}"
        detail_data[key] = {
            "type": "agent",
            "name": agent["name"],
            "model": agent.get("model") or "inherit",
            "desc": agent.get("detail_description", "") or agent.get("description", ""),
            "tools": list(agent.get("mcps", [])) + [f"{t} (CLI)" for t in agent.get("cli_tools", [])],
            "skills": agent.get("skills", []),
            "color": color_map.get(agent["name"], "#94a3b8"),
        }
    for sk in skills:
        key = f"skill-{sk['name']}"
        used_by = [a["name"] for a in agents if sk["name"] in a.get("skills", [])]
        # Find which phase this skill belongs to
        phase_name = ""
        for step in lifecycle_steps:
            if step["skill"] == sk["name"]:
                phase_name = PHASE_DEFS[step["phase"]]["label"] if step["phase"] < len(PHASE_DEFS) else ""
                break
        detail_data[key] = {
            "type": "skill",
            "name": f"/{sk['name']}",
            "desc": sk.get("detail_description", "") or sk.get("description", ""),
            "usedBy": used_by,
            "phase": phase_name,
        }
    for i, tm in enumerate(teams):
        key = f"team-{i}"
        detail_data[key] = {
            "type": "team",
            "name": tm["name"],
            "members": tm.get("members", []),
            "desc": tm.get("description", ""),
        }

    # Serialize all data to JSON, escaping </ for script safety
    def safe_json(obj):
        return json.dumps(obj, ensure_ascii=False).replace('</', r'<\/')

    agents_json = safe_json(agent_data)
    lifecycle_json = safe_json(lifecycle_steps)
    phases_json = safe_json(PHASE_DEFS)
    vp_json = safe_json(vp_cards)
    teams_json = safe_json(team_data)
    detail_json = safe_json(detail_data)
    sprint_json = safe_json(sprint_alt)
    color_map_json = safe_json(color_map)

    escaped_name = e(name)

    # -- Hero / header section --
    if marketing:
        hero_html = f"""
  <div class="hero">
    <div class="pill reveal">Claude Code Plugin</div>
    <h1 class="hero-title reveal">{escaped_name}</h1>
    <p class="hero-tagline reveal">Your Virtual AI Company</p>
    <p class="hero-desc reveal">A Claude Code plugin that gives you a full AI team &mdash; specialized agents, guided workflows, and decision memory. Ship products faster as a team of one.</p>
    <div class="install-steps reveal">
      <div class="install-step">
        <span class="install-num">1</span>
        <code id="cmd1">/plugin marketplace add pcatattacks/solopreneur-plugin</code>
        <button class="copy-btn" onclick="copyCmd('cmd1',this)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg></button>
      </div>
      <div class="install-step">
        <span class="install-num">2</span>
        <code id="cmd2">/plugin install solopreneur@solopreneur</code>
        <button class="copy-btn" onclick="copyCmd('cmd2',this)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg></button>
      </div>
      <div class="install-step">
        <span class="install-num">3</span>
        <code id="cmd3">/solopreneur:help</code>
        <button class="copy-btn" onclick="copyCmd('cmd3',this)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg></button>
      </div>
    </div>
    <div class="hero-link-wrap reveal">
      <a class="hero-link" href="https://github.com/pcatattacks/solopreneur-plugin" target="_blank" rel="noopener">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
        View on GitHub
      </a>
    </div>
  </div>"""
        footer_html = """
  <div class="footer">
    <div class="footer-name reveal">Built by <strong>Pranav Dhingra</strong></div>
    <div class="footer-links reveal">
      <a href="https://pranavdhingra.com" target="_blank" rel="noopener">Portfolio</a>
      <a href="https://linkedin.com/in/pranav-dhingra" target="_blank" rel="noopener">LinkedIn</a>
      <a href="https://github.com/pcatattacks" target="_blank" rel="noopener">GitHub</a>
    </div>
  </div>"""
    else:
        hero_html = f"""
  <div class="hero hero-simple">
    <h1 class="hero-title reveal">{escaped_name}</h1>
    <p class="hero-tagline reveal">AI Org Chart</p>
  </div>"""
        footer_html = """
  <div class="footer">
    <div class="footer-name reveal">Built with the <a href="https://github.com/pcatattacks/solopreneur-plugin" target="_blank" rel="noopener" style="color:var(--text-secondary);text-decoration:none">Solopreneur plugin</a> for Claude Code</div>
  </div>"""

    # Build the mini-dots for the HiW flow from actual agent data
    hiw_dots = ""
    for agent in agents[:8]:
        c = color_map.get(agent["name"], "#94a3b8")
        hiw_dots += f'<span class="mini-dot" style="background:{c}"></span>'
    if not hiw_dots:
        hiw_dots = '<span class="mini-dot" style="background:#3b82f6"></span>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escaped_name} &mdash; AI Org Chart</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}

  :root {{
    --bg: #0a0e1a;
    --surface: #111627;
    --card: #161c30;
    --card-hover: #1c2340;
    --border: #232a44;
    --border-light: #2d365a;
    --text: #e8ecf4;
    --text-secondary: #a0aac0;
    --text-dim: #6b7694;
    --orchestrator: #94a3b8;
    --accent-purple: #c084fc;
    --font-display: 'Instrument Serif', Georgia, serif;
    --font-body: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-mono: 'JetBrains Mono', 'SF Mono', Consolas, monospace;
    --ease: cubic-bezier(0.4, 0, 0.2, 1);
    --chip-w: 130px;
  }}

  html {{ scroll-behavior: smooth }}
  body {{
    font-family: var(--font-body);
    background: var(--bg);
    color: var(--text);
    line-height: 1.65;
    font-size: 15px;
    -webkit-font-smoothing: antialiased;
    overflow-x: hidden;
  }}

  ::-webkit-scrollbar {{ width: 5px }}
  ::-webkit-scrollbar-track {{ background: var(--bg) }}
  ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px }}

  .page {{ max-width: 760px; margin: 0 auto; padding: 0 28px 64px }}

  /* ── Animations ── */
  .reveal {{
    opacity: 0; transform: translateY(14px);
    transition: opacity 0.5s var(--ease), transform 0.5s var(--ease);
  }}
  .reveal.visible {{ opacity: 1; transform: translateY(0) }}

  /* ── Dimming ── */
  .page.filtering .dimmable {{ opacity: 0.1; transition: opacity 0.25s var(--ease) }}
  .page.filtering .dimmable.hl {{ opacity: 1 }}

  /* ════ HERO ════ */
  .hero {{ padding: 64px 0 44px; position: relative }}
  .hero::after {{
    content: ''; position: absolute; bottom: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
  }}
  .hero-simple {{ padding: 48px 0 36px }}
  .pill {{
    display: inline-block;
    font-family: var(--font-mono);
    font-size: 0.72rem; font-weight: 500;
    letter-spacing: 0.08em; text-transform: uppercase;
    padding: 5px 14px; border-radius: 100px;
    border: 1px solid var(--border);
    color: var(--text-dim); margin-bottom: 16px;
  }}
  .hero-title {{
    font-family: var(--font-display);
    font-size: clamp(3rem, 7vw, 4.2rem);
    font-weight: 400; line-height: 1.08;
    background: linear-gradient(135deg, #a78bfa 0%, #818cf8 40%, #6366f1 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin-bottom: 6px;
  }}
  .hero-tagline {{
    font-size: 1.15rem; color: var(--text-secondary);
    font-weight: 400; margin-bottom: 16px;
  }}
  .hero-desc {{
    font-size: 0.95rem; color: var(--text-dim);
    margin-bottom: 28px; line-height: 1.7;
  }}

  /* Install steps */
  .install-steps {{ display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px }}
  .install-step {{
    display: flex; align-items: center; gap: 10px;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 8px; padding: 9px 12px 9px 14px;
  }}
  .install-num {{
    font-family: var(--font-mono);
    font-size: 0.65rem; font-weight: 600;
    color: var(--text-dim); width: 14px; flex-shrink: 0;
  }}
  .install-step code {{
    font-family: var(--font-mono);
    font-size: 0.82rem; color: var(--text);
    flex: 1; white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis;
  }}
  .copy-btn {{
    background: transparent; border: 1px solid var(--border);
    border-radius: 5px; color: var(--text-dim);
    cursor: pointer; padding: 4px 8px;
    display: flex; align-items: center;
    transition: all 0.2s var(--ease); flex-shrink: 0;
  }}
  .copy-btn:hover {{ border-color: var(--text-secondary); color: var(--text-secondary) }}
  .copy-btn.copied {{ border-color: #10b981; color: #10b981 }}
  .copy-btn svg {{ width: 13px; height: 13px }}

  .hero-link-wrap {{ text-align: center }}
  .hero-link {{
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 0.82rem; color: var(--text-dim);
    text-decoration: none; transition: color 0.2s;
  }}
  .hero-link:hover {{ color: var(--text-secondary) }}
  .hero-link svg {{ width: 15px; height: 15px; opacity: 0.6 }}

  /* ════ SECTIONS ════ */
  .section {{ padding: 48px 0 0 }}
  .section-eyebrow {{
    font-family: var(--font-mono);
    font-size: 0.7rem; font-weight: 500;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: var(--text-dim); margin-bottom: 6px;
  }}
  .section-heading {{
    font-family: var(--font-display);
    font-size: 1.55rem; font-weight: 400;
    color: var(--text); margin-bottom: 6px;
    line-height: 1.25;
  }}
  .section-desc {{
    font-size: 0.92rem; color: var(--text-dim);
    margin-bottom: 24px; line-height: 1.65;
  }}

  /* ════ HOW IT WORKS ════ */
  .hiw-flow {{
    display: flex; align-items: center; justify-content: center;
    gap: 14px; padding: 4px 0; flex-wrap: wrap;
  }}
  .hiw-node {{
    text-align: center; padding: 10px 16px;
    border-radius: 10px; font-size: 0.82rem; font-weight: 500;
  }}
  .hiw-you {{
    background: linear-gradient(135deg, rgba(167,139,250,0.08), rgba(99,102,241,0.08));
    border: 1px solid rgba(167,139,250,0.2); color: #a78bfa;
  }}
  .hiw-claude {{
    background: rgba(148,163,184,0.06);
    border: 1px solid rgba(148,163,184,0.15); color: var(--orchestrator);
  }}
  .hiw-node .hiw-label {{
    font-size: 0.62rem; color: var(--text-dim);
    display: block; margin-bottom: 1px;
    font-family: var(--font-mono); letter-spacing: 0.06em; text-transform: uppercase;
  }}
  .hiw-agents-node {{
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border);
    display: flex; gap: 5px; padding: 10px 14px;
    border-radius: 10px;
  }}
  .hiw-agents-node .mini-dot {{ width: 9px; height: 9px; border-radius: 50% }}
  .hiw-arrow {{ color: var(--text-dim); font-family: var(--font-mono); font-size: 0.85rem }}

  /* ════ AGENT CARDS ════ */
  .agent-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px }}
  @media (max-width: 600px) {{ .agent-grid {{ grid-template-columns: repeat(2, 1fr) }} }}

  .agent-card {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 14px 16px;
    cursor: pointer; transition: all 0.25s var(--ease);
    position: relative; overflow: hidden;
  }}
  .agent-card::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: var(--agent-color); opacity: 0.6;
  }}
  .agent-card:hover {{
    border-color: var(--agent-color); background: var(--card-hover);
    transform: translateY(-2px); box-shadow: 0 6px 24px rgba(0,0,0,0.3);
  }}
  .agent-top {{ display: flex; align-items: center; gap: 8px; margin-bottom: 5px }}
  .agent-dot {{ width: 8px; height: 8px; border-radius: 50%; background: var(--agent-color); flex-shrink: 0 }}
  .agent-name {{ font-weight: 600; font-size: 0.88rem; flex: 1 }}
  .agent-role {{ font-size: 0.8rem; color: var(--text-dim); line-height: 1.4 }}
  .panel-model-badge {{
    font-family: var(--font-mono);
    font-size: 0.68rem; font-weight: 600;
    letter-spacing: 0.03em; text-transform: uppercase;
    padding: 2px 7px; border-radius: 4px;
    display: inline-block;
  }}
  .panel-model-explicit {{ background: rgba(129,140,248,0.12); color: #818cf8 }}
  .panel-model-inherit {{ background: rgba(148,163,184,0.08); color: var(--text-dim) }}

  /* ════ WORKFLOW ════ */
  .workflow {{ position: relative; padding-left: 32px }}
  .workflow::before {{
    content: ''; position: absolute;
    left: 10px; top: 0; bottom: 0; width: 2px;
    background: linear-gradient(180deg, #06b6d4 0%, #ec4899 35%, #3b82f6 55%, #10b981 80%, #8b5cf6 100%);
    opacity: 0.2; border-radius: 2px;
  }}

  .phase-label {{
    position: relative;
    font-family: var(--font-mono);
    font-size: 0.65rem; font-weight: 600;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--phase-color, var(--text-dim));
    padding: 20px 0 10px;
    display: flex; align-items: center; gap: 10px;
  }}
  .phase-label::before {{
    content: ''; position: absolute;
    left: -22px; top: 50%; transform: translateY(30%);
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--phase-color, var(--text-dim)); opacity: 0.4;
  }}
  .phase-label::after {{
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, var(--phase-color, var(--border)), transparent);
    opacity: 0.2;
  }}

  .step-card {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 16px 20px;
    margin-bottom: 8px; cursor: pointer;
    transition: all 0.25s var(--ease); position: relative;
  }}
  .step-card:hover {{
    border-color: var(--border-light); background: var(--card-hover);
    transform: translateX(3px);
  }}
  .step-card::before {{
    content: ''; position: absolute;
    left: -26px; top: 20px;
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--border-light); transition: background 0.2s;
  }}
  .step-card:hover::before {{ background: var(--text-secondary) }}

  .step-header {{ display: flex; align-items: baseline; gap: 10px; margin-bottom: 2px }}
  .step-skill {{ font-family: var(--font-mono); font-size: 0.9rem; font-weight: 600; color: var(--text) }}
  .step-desc {{ font-size: 0.82rem; color: var(--text-dim) }}

  .step-agents {{ margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border) }}
  .step-agent-row {{
    display: flex; align-items: baseline; gap: 10px;
    padding: 3px 0; font-size: 0.8rem;
  }}
  .step-agent-chip {{
    display: inline-flex; align-items: center; gap: 5px;
    width: var(--chip-w); flex-shrink: 0;
    font-family: var(--font-mono); font-size: 0.72rem; font-weight: 500;
    color: var(--agent-color);
  }}
  .step-agent-chip .cdot {{ width: 5px; height: 5px; border-radius: 50%; background: var(--agent-color) }}
  .step-agent-role {{ color: var(--text-secondary); font-size: 0.82rem; line-height: 1.4 }}

  /* Sprint branch */
  .sprint-branch {{
    background: var(--surface); border: 2px dashed var(--border);
    border-radius: 12px; padding: 18px 20px;
    margin: 12px 0; position: relative;
  }}
  .sprint-branch::before {{
    content: ''; position: absolute;
    left: -26px; top: 24px;
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--border-light);
  }}
  .sprint-or {{
    font-family: var(--font-mono);
    font-size: 0.68rem; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: var(--text-dim);
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 10px;
  }}
  .sprint-or::before, .sprint-or::after {{
    content: ''; flex: 1; height: 1px;
    background: var(--border);
  }}
  .sprint-header {{
    font-family: var(--font-mono); font-size: 0.9rem; font-weight: 600;
    color: var(--text); margin-bottom: 2px;
  }}
  .sprint-desc {{ font-size: 0.82rem; color: var(--text-dim); margin-bottom: 10px; line-height: 1.5 }}

  /* ════ VALUE PROP CARDS ════ */
  .vp-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px }}
  @media (max-width: 540px) {{ .vp-grid {{ grid-template-columns: 1fr }} }}

  .vp-card {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 18px 20px;
    cursor: pointer; transition: all 0.25s var(--ease);
  }}
  .vp-card:hover {{ border-color: var(--border-light); background: var(--card-hover) }}
  .vp-icon {{ font-size: 1.3rem; margin-bottom: 8px }}
  .vp-name {{
    font-family: var(--font-mono); font-size: 0.85rem; font-weight: 600;
    color: var(--text); margin-bottom: 4px;
  }}
  .vp-desc {{ font-size: 0.82rem; color: var(--text-dim); line-height: 1.5 }}
  .vp-agents {{ display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px }}
  .vp-chip {{
    display: inline-flex; align-items: center; gap: 4px;
    font-family: var(--font-mono); font-size: 0.62rem; font-weight: 500;
    padding: 2px 7px; border-radius: 4px;
    background: rgba(255,255,255,0.03); color: var(--chip-color, var(--text-dim));
  }}
  .vp-chip .cdot {{ width: 4px; height: 4px; border-radius: 50%; background: var(--chip-color, var(--text-dim)) }}

  /* ════ TEAMS ════ */
  .team-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px }}
  @media (max-width: 600px) {{ .team-grid {{ grid-template-columns: 1fr }} }}

  .team-card {{
    background: transparent; border: 1px dashed var(--border);
    border-radius: 10px; padding: 16px 18px;
    cursor: pointer; transition: all 0.25s var(--ease);
  }}
  .team-card:hover {{ border-color: var(--border-light); border-style: solid; background: var(--card) }}
  .team-name {{ font-weight: 600; font-size: 0.88rem; margin-bottom: 4px }}
  .team-purpose {{ font-size: 0.78rem; color: var(--text-dim); margin-bottom: 10px; line-height: 1.45 }}
  .team-members {{ display: flex; flex-wrap: wrap; gap: 4px }}
  .team-member {{
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.7rem; font-weight: 500;
    padding: 2px 8px 2px 6px; border-radius: 5px;
    background: rgba(255,255,255,0.03); color: var(--member-color);
  }}
  .team-member .cdot {{ width: 5px; height: 5px; border-radius: 50%; background: var(--member-color) }}

  /* ════ FOOTER ════ */
  .footer {{
    text-align: center; padding: 48px 0 0; position: relative;
  }}
  .footer::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
  }}
  .footer-name {{ font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 8px }}
  .footer-links {{ display: flex; gap: 20px; justify-content: center; font-size: 0.82rem; flex-wrap: wrap }}
  .footer-links a {{ color: var(--text-dim); text-decoration: none; transition: color 0.2s }}
  .footer-links a:hover {{ color: var(--text-secondary) }}

  /* ════ DETAIL PANEL ════ */
  .panel-scrim {{
    position: fixed; inset: 0; background: rgba(0,0,0,0.5);
    opacity: 0; pointer-events: none; transition: opacity 0.25s var(--ease); z-index: 100;
  }}
  .panel-scrim.open {{ opacity: 1; pointer-events: auto }}
  .panel {{
    position: fixed; top: 0; right: 0;
    width: min(420px, 90vw); height: 100vh;
    background: var(--surface); border-left: 1px solid var(--border);
    transform: translateX(100%); transition: transform 0.3s var(--ease);
    z-index: 101; display: flex; flex-direction: column;
    box-shadow: -8px 0 40px rgba(0,0,0,0.4);
  }}
  .panel.open {{ transform: translateX(0) }}
  .panel-header {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 18px 20px; border-bottom: 1px solid var(--border); flex-shrink: 0;
  }}
  .panel-header-left {{ display: flex; align-items: center; gap: 10px }}
  .panel-type-badge {{
    font-family: var(--font-mono); font-size: 0.62rem; font-weight: 600;
    letter-spacing: 0.06em; text-transform: uppercase; padding: 3px 8px; border-radius: 4px;
  }}
  .panel-type-agent {{ background: rgba(59,130,246,0.12); color: #60a5fa }}
  .panel-type-skill {{ background: rgba(139,92,246,0.12); color: #a78bfa }}
  .panel-type-team {{ background: rgba(129,140,248,0.12); color: #a5b4fc }}
  .panel-title-text {{ font-weight: 600; font-size: 1.05rem }}
  .panel-close {{
    background: none; border: 1px solid var(--border); border-radius: 6px;
    color: var(--text-dim); cursor: pointer; width: 28px; height: 28px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; transition: all 0.15s;
  }}
  .panel-close:hover {{ border-color: var(--text-secondary); color: var(--text) }}
  .panel-body {{
    padding: 20px; overflow-y: auto; flex: 1;
    font-size: 0.88rem; line-height: 1.7; color: var(--text-secondary);
  }}
  .panel-meta {{
    background: var(--bg); border-radius: 8px; padding: 12px 14px; margin-bottom: 16px;
  }}
  .panel-meta-row {{ display: flex; gap: 8px; margin: 4px 0; font-size: 0.82rem; align-items: baseline }}
  .panel-meta-label {{
    font-family: var(--font-mono); font-size: 0.62rem; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--text-dim); width: 54px; flex-shrink: 0;
  }}
  .panel-section-title {{
    font-family: var(--font-mono); font-size: 0.68rem; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: var(--text-dim); margin: 16px 0 8px;
  }}
  .panel-skill-item {{ padding: 6px 0; border-bottom: 1px solid var(--border); font-size: 0.84rem }}
  .panel-skill-item:last-child {{ border-bottom: none }}
  .panel-skill-name {{ font-family: var(--font-mono); font-weight: 600; color: var(--text); font-size: 0.82rem }}
  .panel-skill-role {{ color: var(--text-dim); font-size: 0.8rem }}
</style>
</head>
<body>
<div class="page" id="page">

  {hero_html}

  <!-- How it works -->
  <div class="section">
    <div class="section-eyebrow reveal">How it works</div>
    <div class="section-heading reveal">You lead. Claude orchestrates. Agents execute.</div>
    <div class="section-desc reveal">You're the CEO. Claude coordinates your AI team through a guided workflow &mdash; delegating to specialized agents, then reporting back.</div>
    <div class="hiw-flow reveal">
      <div class="hiw-node hiw-you"><span class="hiw-label">You</span>CEO</div>
      <span class="hiw-arrow">&rarr;</span>
      <div class="hiw-node hiw-claude"><span class="hiw-label">Claude</span>Orchestrator</div>
      <span class="hiw-arrow">&rarr;</span>
      <div class="hiw-agents-node">
        {hiw_dots}
      </div>
    </div>
  </div>

  <!-- Your AI team -->
  <div class="section" id="team-section">
    <div class="section-eyebrow reveal">Your AI team</div>
    <div class="section-heading reveal">{len(agents)} specialized agent{"s" if len(agents) != 1 else ""}</div>
    <div class="section-desc reveal">Each agent brings deep expertise. Hover to see where they contribute across the workflow.</div>
    <div class="agent-grid" id="agent-grid"></div>
  </div>

  <!-- The workflow -->
  <div class="section" id="workflow-section">
    <div class="section-eyebrow reveal">The workflow</div>
    <div class="section-heading reveal">Idea to launch in {len(lifecycle)} steps</div>
    <div class="section-desc reveal">A guided lifecycle from research through release. Each step knows who to call and what they should do.</div>
    <div class="workflow" id="workflow"></div>
  </div>

  <!-- Beyond the lifecycle -->
  <div class="section" id="beyond-section">
    <div class="section-eyebrow reveal">Beyond the lifecycle</div>
    <div class="section-heading reveal">What makes {escaped_name} different</div>
    <div class="section-desc reveal">The lifecycle gets your product built. These capabilities make the whole experience smarter.</div>
    <div class="vp-grid" id="vp-grid"></div>
  </div>

  <!-- Agent teams -->
  <div class="section" id="teams-section">
    <div class="section-eyebrow reveal">Agent teams</div>
    <div class="section-heading reveal">Collaborative meetings</div>
    <div class="section-desc reveal">Pre-configured teams for common workflows via <code style="font-family:var(--font-mono);color:#a78bfa">/kickoff</code>. You can also assemble ad-hoc teams by naming any agents.</div>
    <div class="team-grid" id="team-grid"></div>
  </div>

  {footer_html}
</div>

<!-- Detail panel -->
<div class="panel-scrim" id="panelScrim"></div>
<div class="panel" id="panel">
  <div class="panel-header">
    <div class="panel-header-left">
      <span class="panel-type-badge" id="panelBadge"></span>
      <span class="panel-title-text" id="panelTitle"></span>
    </div>
    <button class="panel-close" id="panelClose">&times;</button>
  </div>
  <div class="panel-body" id="panelBody"></div>
</div>

<script>
// ════════════════════════
// DATA (injected from Python)
// ════════════════════════
const AGENTS = {agents_json};
const LIFECYCLE = {lifecycle_json};
const PHASES = {phases_json};
const VP_CARDS = {vp_json};
const TEAMS = {teams_json};
const DETAIL_DATA = {detail_json};
const SPRINT = {sprint_json};
const COLOR_MAP = {color_map_json};

const AM = {{}};
AGENTS.forEach(a => AM[a.id] = a);

// ════════════════════════
// RENDER
// ════════════════════════

// Agents
const agentGrid = document.getElementById('agent-grid');
AGENTS.forEach(a => {{
  const d = document.createElement('div');
  d.className = 'agent-card dimmable reveal';
  d.dataset.agent = a.id;
  d.style.setProperty('--agent-color', a.color);
  d.innerHTML = '<div class="agent-top"><span class="agent-dot"></span><span class="agent-name">' + a.name + '</span></div><div class="agent-role">' + a.desc + '</div>';
  d.addEventListener('click', () => openAgentPanel(a.id));
  d.addEventListener('mouseenter', () => hlAgent(a.id));
  d.addEventListener('mouseleave', clearHl);
  agentGrid.appendChild(d);
}});

// Workflow
const wf = document.getElementById('workflow');
let curPhase = -1;
LIFECYCLE.forEach((step, i) => {{
  if (step.phase !== curPhase) {{
    curPhase = step.phase;
    const ph = document.createElement('div');
    ph.className = 'phase-label reveal';
    const phDef = PHASES[step.phase] || {{ label: 'Phase ' + step.phase, color: '#94a3b8' }};
    ph.style.setProperty('--phase-color', phDef.color);
    ph.textContent = phDef.label;
    wf.appendChild(ph);
  }}
  const card = document.createElement('div');
  card.className = 'step-card dimmable reveal';
  card.dataset.skill = step.skill;
  step.agents.forEach(sa => card.setAttribute('data-agent-' + sa.id, '1'));

  const agHtml = step.agents.map(sa => {{
    return '<div class="step-agent-row"><span class="step-agent-chip" style="--agent-color:' + sa.color + '"><span class="cdot"></span>' + sa.name + '</span><span class="step-agent-role">' + sa.role + '</span></div>';
  }}).join('');

  card.innerHTML = '<div class="step-header"><span class="step-skill">/' + step.skill + '</span><span class="step-desc">' + step.desc + '</span></div>' + (agHtml ? '<div class="step-agents">' + agHtml + '</div>' : '');
  card.addEventListener('click', () => openSkillPanel(step.skill));
  card.addEventListener('mouseenter', () => hlSkill(step.skill));
  card.addEventListener('mouseleave', clearHl);
  wf.appendChild(card);

  // Sprint branch after /build
  if (step.skill === 'build' && SPRINT) {{
    const branch = document.createElement('div');
    branch.className = 'sprint-branch dimmable reveal';
    branch.dataset.skill = 'sprint';
    // Figure out sprint agents from data
    const sprintAgentIds = ['engineer','qa','designer'].filter(id => AM[id]);
    sprintAgentIds.forEach(id => branch.setAttribute('data-agent-' + id, '1'));

    let sprintAgentHtml = '';
    sprintAgentIds.forEach(id => {{
      const ag = AM[id];
      if (ag) {{
        sprintAgentHtml += '<div class="step-agent-row"><span class="step-agent-chip" style="--agent-color:' + ag.color + '"><span class="cdot"></span>' + ag.name + '</span><span class="step-agent-role">' + ag.desc + '</span></div>';
      }}
    }});

    branch.innerHTML = '<div class="sprint-or">or batch-execute with</div>' +
      '<div class="sprint-header">/sprint</div>' +
      '<div class="sprint-desc">' + (SPRINT.description || 'Batch-execute multiple tickets in parallel') + '</div>' +
      (sprintAgentHtml ? '<div class="step-agents" style="border:0;padding:0;margin:0">' + sprintAgentHtml + '</div>' : '');
    branch.style.cursor = 'pointer';
    branch.addEventListener('click', () => openVpPanel('sprint'));
    branch.addEventListener('mouseenter', () => hlSkill('sprint'));
    branch.addEventListener('mouseleave', clearHl);
    wf.appendChild(branch);
  }}
}});

// Value prop cards
const vpGrid = document.getElementById('vp-grid');
VP_CARDS.forEach(vp => {{
  const d = document.createElement('div');
  d.className = 'vp-card reveal';
  d.dataset.skill = vp.skill;

  const chips = vp.agents.map(id => {{
    if (id === 'orchestrator') return '<span class="vp-chip" style="--chip-color:var(--orchestrator)"><span class="cdot"></span>Orchestrator</span>';
    const ag = AM[id];
    if (!ag) {{
      // Try matching by name
      const found = AGENTS.find(a => a.name.toLowerCase().replace(/\\s+/g,'-') === id || a.name.toLowerCase() === id);
      if (found) return '<span class="vp-chip" style="--chip-color:' + found.color + '"><span class="cdot"></span>' + found.name + '</span>';
      return '<span class="vp-chip" style="--chip-color:var(--orchestrator)"><span class="cdot"></span>' + id + '</span>';
    }}
    return '<span class="vp-chip" style="--chip-color:' + ag.color + '"><span class="cdot"></span>' + ag.name + '</span>';
  }}).join('');

  d.innerHTML = '<div class="vp-icon">' + vp.icon + '</div><div class="vp-name">' + vp.name + '</div><div class="vp-desc">' + vp.desc + '</div><div class="vp-agents">' + chips + '</div>';
  d.addEventListener('click', () => openVpPanel(vp.skill));
  vpGrid.appendChild(d);
}});

// Teams
const teamGrid = document.getElementById('team-grid');
TEAMS.forEach((t, i) => {{
  const d = document.createElement('div');
  d.className = 'team-card dimmable reveal';
  d.dataset.team = i;
  t.members.forEach(m => d.setAttribute('data-agent-' + m.id, '1'));
  const mHtml = t.members.map(m => {{
    return '<span class="team-member" style="--member-color:' + m.color + '"><span class="cdot"></span>' + m.name + '</span>';
  }}).join('');
  d.innerHTML = '<div class="team-name">' + t.name + '</div><div class="team-purpose">' + (t.purpose || '') + '</div><div class="team-members">' + mHtml + '</div>';
  d.addEventListener('click', () => openTeamPanel(i));
  d.addEventListener('mouseenter', () => hlTeam(i));
  d.addEventListener('mouseleave', clearHl);
  teamGrid.appendChild(d);
}});

// ════════════════════════
// HIGHLIGHTING
// ════════════════════════
function hlAgent(id) {{
  document.getElementById('page').classList.add('filtering');
  document.querySelectorAll('[data-agent="' + id + '"]').forEach(el => el.classList.add('hl'));
  document.querySelectorAll('[data-agent-' + id + ']').forEach(el => el.classList.add('hl'));
}}
function hlSkill(sk) {{
  document.getElementById('page').classList.add('filtering');
  document.querySelectorAll('[data-skill="' + sk + '"]').forEach(el => el.classList.add('hl'));
  const step = LIFECYCLE.find(s => s.skill === sk);
  if (step) step.agents.forEach(sa => document.querySelectorAll('[data-agent="' + sa.id + '"]').forEach(el => el.classList.add('hl')));
  if (sk === 'sprint') {{
    ['engineer','qa','designer'].forEach(id => document.querySelectorAll('[data-agent="' + id + '"]').forEach(el => el.classList.add('hl')));
  }}
}}
function hlTeam(idx) {{
  document.getElementById('page').classList.add('filtering');
  document.querySelectorAll('[data-team="' + idx + '"]').forEach(el => el.classList.add('hl'));
  TEAMS[idx].members.forEach(m => {{
    document.querySelectorAll('[data-agent="' + m.id + '"]').forEach(el => el.classList.add('hl'));
    document.querySelectorAll('[data-agent-' + m.id + ']').forEach(el => el.classList.add('hl'));
  }});
}}
function clearHl() {{
  document.getElementById('page').classList.remove('filtering');
  document.querySelectorAll('.hl').forEach(el => el.classList.remove('hl'));
}}

// ════════════════════════
// DETAIL PANEL
// ════════════════════════
const panel = document.getElementById('panel');
const panelScrim = document.getElementById('panelScrim');
const panelBadge = document.getElementById('panelBadge');
const panelTitle = document.getElementById('panelTitle');
const panelBody = document.getElementById('panelBody');

function openPanel(type, title, html) {{
  panelBadge.textContent = type;
  panelBadge.className = 'panel-type-badge panel-type-' + type;
  panelTitle.textContent = title;
  panelBody.innerHTML = html;
  panel.classList.add('open');
  panelScrim.classList.add('open');
}}
function closePanel() {{ panel.classList.remove('open'); panelScrim.classList.remove('open') }}
document.getElementById('panelClose').addEventListener('click', closePanel);
panelScrim.addEventListener('click', closePanel);
document.addEventListener('keydown', ev => {{ if (ev.key === 'Escape') closePanel() }});

function openAgentPanel(id) {{
  const a = AM[id]; if (!a) return;
  const dd = DETAIL_DATA['agent-' + id];
  const lSkills = LIFECYCLE.filter(s => s.agents.some(sa => sa.id === id));
  const aTeams = TEAMS.filter(t => t.members.some(m => m.id === id));
  const modelVal = a.model || 'inherit';
  const modelHtml = (modelVal && modelVal !== 'inherit' && modelVal !== 'null')
    ? '<span class="panel-model-badge panel-model-explicit">Claude ' + modelVal.charAt(0).toUpperCase() + modelVal.slice(1) + '</span>'
    : '<span class="panel-model-badge panel-model-inherit">Inherits from conversation</span>';
  let h = '<div class="panel-meta">' +
    '<div class="panel-meta-row"><span class="panel-meta-label">Model</span>' + modelHtml + '</div>' +
    '<div class="panel-meta-row"><span class="panel-meta-label">Role</span>' + (dd ? dd.desc : a.desc) + '</div>';
  if (a.tools && a.tools.length) h += '<div class="panel-meta-row"><span class="panel-meta-label">Tools</span>' + a.tools.join(', ') + '</div>';
  if (aTeams.length) h += '<div class="panel-meta-row"><span class="panel-meta-label">Teams</span>' + aTeams.map(t=>t.name).join(', ') + '</div>';
  h += '</div>';
  if (lSkills.length) {{
    h += '<div class="panel-section-title">Lifecycle roles</div>';
    lSkills.forEach(s => {{
      const r = s.agents.find(sa => sa.id === id);
      h += '<div class="panel-skill-item"><span class="panel-skill-name">/' + s.skill + '</span><div class="panel-skill-role">' + (r ? r.role : '') + '</div></div>';
    }});
  }}
  openPanel('agent', a.name, h);
}}

function openSkillPanel(sk) {{
  const step = LIFECYCLE.find(s => s.skill === sk); if (!step) return;
  const phDef = PHASES[step.phase] || {{ label: '', color: '#94a3b8' }};
  let h = '<div class="panel-meta"><div class="panel-meta-row"><span class="panel-meta-label">Phase</span>' + phDef.label + '</div><div class="panel-meta-row"><span class="panel-meta-label">Purpose</span>' + step.desc + '</div></div>';
  if (step.agents.length) {{
    h += '<div class="panel-section-title">Agents involved</div>';
    step.agents.forEach(sa => {{
      h += '<div class="panel-skill-item"><span class="panel-skill-name" style="color:' + sa.color + '">' + sa.name + '</span><div class="panel-skill-role">' + sa.role + '</div></div>';
    }});
  }}
  openPanel('skill', '/' + sk, h);
}}

function openVpPanel(sk) {{
  const vp = VP_CARDS.find(v => v.skill === sk); if (!vp) return;
  const agentNames = vp.agents.map(id => {{
    if (id === 'orchestrator') return 'Orchestrator (Claude)';
    const ag = AM[id];
    return ag ? ag.name : id;
  }});
  let h = '<div class="panel-meta"><div class="panel-meta-row"><span class="panel-meta-label">Type</span>Utility Skill</div><div class="panel-meta-row"><span class="panel-meta-label">Purpose</span>' + vp.desc + '</div><div class="panel-meta-row"><span class="panel-meta-label">Agents</span>' + agentNames.join(', ') + '</div></div>';
  openPanel('skill', vp.name, h);
}}

function openTeamPanel(idx) {{
  const t = TEAMS[idx]; if (!t) return;
  let h = '<div class="panel-meta"><div class="panel-meta-row"><span class="panel-meta-label">Purpose</span>' + (t.purpose || '') + '</div><div class="panel-meta-row"><span class="panel-meta-label">Invoke</span><code style="font-family:var(--font-mono);font-size:0.82rem;color:#a78bfa">/kickoff ' + t.name.toLowerCase() + '</code></div></div>';
  h += '<div class="panel-section-title">Members</div>';
  t.members.forEach(m => {{
    h += '<div class="panel-skill-item"><span class="panel-skill-name" style="color:' + m.color + '">' + m.name + '</span><div class="panel-skill-role">' + (AM[m.id] ? AM[m.id].desc : '') + '</div></div>';
  }});
  openPanel('team', t.name, h);
}}

// ════════════════════════
// COPY
// ════════════════════════
function copyCmd(id, btn) {{
  navigator.clipboard.writeText(document.getElementById(id).textContent).then(() => {{
    btn.classList.add('copied');
    btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>';
    setTimeout(() => {{ btn.classList.remove('copied'); btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>'; }}, 2000);
  }});
}}

// ════════════════════════
// ANIMATIONS
// ════════════════════════
const obs = new IntersectionObserver(entries => {{
  entries.forEach(entry => {{
    if (entry.isIntersecting) {{
      const parent = entry.target.parentElement;
      const siblings = Array.from(parent.querySelectorAll(':scope > .reveal'));
      const idx = siblings.indexOf(entry.target);
      setTimeout(() => entry.target.classList.add('visible'), Math.max(0, idx) * 50);
      obs.unobserve(entry.target);
    }}
  }});
}}, {{ threshold: 0.05, rootMargin: '0px 0px -10px 0px' }});
document.querySelectorAll('.reveal').forEach(el => obs.observe(el));
setTimeout(() => document.querySelectorAll('.reveal:not(.visible)').forEach(el => el.classList.add('visible')), 2000);
</script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Generate an AI org chart HTML file")
    parser.add_argument("--config", help="JSON config file path")
    parser.add_argument("--plugin-dir", help="Auto-discover from a plugin directory (reads agents/, skills/, .mcp.json)")
    parser.add_argument("--name", default="My AI Org", help="Org name (CLI mode)")
    parser.add_argument("--agents", default="", help="Comma-separated agents (CLI mode)")
    parser.add_argument("--skills", default="", help="Comma-separated skills (CLI mode)")
    parser.add_argument("--teams", default="", help="Teams as Name:A+B,Name2:C+D (CLI mode)")
    parser.add_argument("--mcps", default="", help="Comma-separated MCPs (CLI mode)")
    parser.add_argument("--marketing", action="store_true", help="Add marketing header/footer for hosted landing page")
    parser.add_argument("--output", default="org-chart.html", help="Output file path")

    args = parser.parse_args()

    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    elif args.plugin_dir:
        config = build_from_plugin(args.plugin_dir)
    else:
        config = build_from_cli(args)

    html_content = generate_html(config, marketing=args.marketing)

    with open(args.output, "w") as f:
        f.write(html_content)

    print(f"Org chart generated: {args.output}")
    print(f"Open in your browser: open {args.output}")


if __name__ == "__main__":
    main()
