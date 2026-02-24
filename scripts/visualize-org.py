#!/usr/bin/env python3
"""
Generate an interactive HTML org chart for an AI team plugin.

Accepts a JSON config file describing agents, skills, MCPs, and teams,
then produces a self-contained HTML file with SVG connection lines.

Usage:
    # Auto-discover from a plugin directory (recommended):
    python3 visualize-org.py --plugin-dir . --output org-chart.html

    # From a JSON config:
    python3 visualize-org.py --config org.json --output org-chart.html

    # Quick mode with CLI args (flat, no connections):
    python3 visualize-org.py --name "My Org" --agents "Engineer,Designer" --output org-chart.html

JSON config format:
{
  "name": "My AI Org",
  "agents": [
    {
      "name": "Engineer",
      "model": "opus",
      "skills": ["build", "review"],
      "mcps": ["GitHub"],
      "description": "Architecture and implementation",
      "markdown": "Full markdown content shown in detail panel on click"
    }
  ],
  "skills": [
    { "name": "build", "description": "Generate implementation plans" },
    { "name": "review", "description": "Code quality review" }
  ],
  "mcps": [
    { "name": "GitHub", "description": "Code & PR management" }
  ],
  "teams": [
    { "name": "Build Sprint", "members": ["Engineer", "QA", "Designer"] }
  ],
  "lifecycle": ["discover", "spec", "design", "build", "review", "ship"]
}
"""

import argparse
import glob
import html
import json
import os
import re
import sys


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
        "agents": [{"name": a, "model": "inherit", "skills": skills, "mcps": mcps_list, "description": ""} for a in agents],
        "skills": [{"name": s, "description": ""} for s in skills],
        "mcps": [{"name": m, "description": ""} for m in mcps_list],
        "teams": teams,
        "lifecycle": skills[:7]
    }


def parse_frontmatter(content):
    """Extract YAML-like frontmatter and body from a markdown file."""
    meta = {}
    body = content
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
    if match:
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                meta[key.strip()] = val.strip()
        body = match.group(2)
    return meta, body


def shorten_description(desc, max_len=40):
    """Shorten a long description to a card-friendly label."""
    if not desc or len(desc) <= max_len:
        return desc
    # Try to extract a meaningful short phrase
    # Pattern: "X specializing in Y, Z, and W" → "Y & Z"
    spec_match = re.search(r'specializing in ([^.]+)', desc)
    if spec_match:
        parts = [p.strip() for p in re.split(r',\s*(?:and\s+)?', spec_match.group(1))]
        if len(parts) >= 2:
            return fix_name_casing(f"{parts[0].title()} & {parts[1]}")
        return fix_name_casing(parts[0].title())
    # Pattern: "X for Y, Z, and W" → "Y & Z" (skip if Y starts with article)
    for_match = re.search(r'(?:for|covering) ([^.]+)', desc)
    if for_match:
        target = for_match.group(1).strip()
        if not re.match(r'^(?:a|an|the)\s', target, re.IGNORECASE):
            parts = [p.strip() for p in re.split(r',\s*(?:and\s+)?', target)]
            if len(parts) >= 2:
                return fix_name_casing(f"{parts[0].title()} & {parts[1]}")
            return fix_name_casing(parts[0].title())
    # Fallback: first sentence, first clause, truncated
    first = desc.split('.')[0]
    # Try first comma-separated clause
    clause = first.split(',')[0]
    if len(clause) <= max_len:
        return fix_name_casing(clause)
    if len(first) <= max_len:
        return fix_name_casing(first)
    return fix_name_casing(first[:max_len - 3] + "...")


def fix_name_casing(name):
    """Fix casing for known abbreviations and compound words."""
    # Common abbreviations that should stay uppercase
    abbreviations = {"qa": "QA", "ui": "UI", "ux": "UX", "ui/ux": "UI/UX", "api": "API",
                     "ci": "CI", "cd": "CD", "pr": "PR", "prd": "PRD",
                     "cto": "CTO", "ceo": "CEO", "devops": "DevOps", "bizops": "BizOps",
                     "github": "GitHub", "devtools": "DevTools"}
    # Check if the whole name (lowered) is a known abbreviation
    if name.lower() in abbreviations:
        return abbreviations[name.lower()]
    # Check each word
    words = name.split()
    fixed = []
    for w in words:
        if w.lower() in abbreviations:
            fixed.append(abbreviations[w.lower()])
        else:
            fixed.append(w)
    return " ".join(fixed)


# Skills that are meta/orchestration and shouldn't appear on agent cards
META_SKILLS = {"sprint", "standup", "scaffold", "explain", "kickoff"}


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
            # Skip observer agent (internal, not user-facing)
            if agent_name.lower() == "observer":
                continue
            full_desc = meta.get("description", "")
            display_name = fix_name_casing(agent_name.replace("-", " ").title())
            agents.append({
                "name": display_name,
                "model": meta.get("model", "opus"),
                "skills": [],
                "mcps": [],
                "description": shorten_description(full_desc),
                "detail_description": full_desc,
                "markdown": body.strip()
            })

    # Discover skills from skills/*/SKILL.md
    skills = []
    skill_bodies = {}  # name -> body for agent mapping
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

    # Discover MCPs from .mcp.json with selective assignment
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

    # Assign MCPs to agents based on CLAUDE.md per-bullet hints
    if mcps and claude_content:
        tool_section = re.search(r'Tool Access.*?(?=^#[^#]|\Z)', claude_content, re.DOTALL | re.MULTILINE)
        if tool_section:
            # Parse each bullet line: "- **MCP**: description mentioning Agent names"
            for line in tool_section.group(0).split('\n'):
                if not line.strip().startswith('-'):
                    continue
                line_lower = line.lower()
                # Find which MCP this bullet is about
                matched_mcp = None
                for mcp in mcps:
                    if mcp["name"].lower() in line_lower:
                        matched_mcp = mcp
                        break
                if not matched_mcp:
                    continue
                # Find which agents are mentioned on this specific line
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
                if "github" in mcp_lower and ("code" in tools or "engineer" in agent_lower or "qa" in agent_lower):
                    agent["mcps"].append(mcp["name"])
                elif "devtools" in mcp_lower and ("ui" in tools or "design" in agent_lower):
                    agent["mcps"].append(mcp["name"])
                elif "context" in mcp_lower and ("research" in agent_lower):
                    agent["mcps"].append(mcp["name"])

    # Parse lifecycle from CLAUDE.md
    lifecycle = []
    lc_match = re.search(r'(/[\w-]+:[\w-]+(?:\s*→\s*/[\w-]+:[\w-]+)+)', claude_content)
    if lc_match:
        lifecycle = [s.split(":")[-1].strip() for s in lc_match.group(1).split("→")]
    if not lifecycle:
        core_skills = ["discover", "spec", "design", "build", "review", "ship"]
        lifecycle = [s for s in core_skills if s in skill_names]

    # Build teams from CLAUDE.md or agent groupings
    teams = []
    agent_names = [a["name"] for a in agents]
    if len(agent_names) >= 3:
        # Try to create sensible groupings based on skill overlap
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

    return {
        "name": name,
        "agents": agents,
        "skills": skills,
        "mcps": mcps,
        "teams": teams,
        "lifecycle": lifecycle
    }


def e(text):
    """HTML-escape shorthand."""
    return html.escape(str(text))


def generate_html(config):
    """Generate a self-contained HTML org chart with SVG connections."""
    name = config.get("name", "My AI Org")
    agents = config.get("agents", [])
    skills = config.get("skills", [])
    mcps = config.get("mcps", [])
    teams = config.get("teams", [])
    lifecycle = config.get("lifecycle", [])

    # Build lookup maps
    skill_names = {s["name"] for s in skills}
    mcp_names = {m["name"] for m in mcps}

    # Build agent-to-skill and agent-to-mcp connection data for JS
    connections = []
    for agent in agents:
        for sk in agent.get("skills", []):
            connections.append({"from": f"agent-{agent['name']}", "to": f"skill-{sk}", "type": "solid"})
        for mc in agent.get("mcps", []):
            connections.append({"from": f"agent-{agent['name']}", "to": f"mcp-{mc}", "type": "dotted"})

    # CEO-to-agent connections
    for agent in agents:
        connections.append({"from": "ceo-node", "to": f"agent-{agent['name']}", "type": "solid"})

    connections_json = json.dumps(connections)

    # Build detail content map for click-to-view panels
    detail_data = {}
    for agent in agents:
        key = f"agent-{agent['name']}"
        detail_data[key] = {
            "type": "agent",
            "name": agent["name"],
            "model": agent.get("model", "inherit"),
            "skills": agent.get("skills", []),
            "mcps": agent.get("mcps", []),
            "description": agent.get("detail_description", "") or agent.get("description", ""),
            "markdown": agent.get("markdown", "")
        }
    for sk in skills:
        key = f"skill-{sk['name']}"
        used_by = [a["name"] for a in agents if sk["name"] in a.get("skills", [])]
        detail_data[key] = {
            "type": "skill",
            "name": f"/{sk['name']}",
            "usedBy": used_by,
            "description": sk.get("detail_description", "") or sk.get("description", ""),
            "markdown": sk.get("markdown", "")
        }
    for mc in mcps:
        key = f"mcp-{mc['name']}"
        used_by = [a["name"] for a in agents if mc["name"] in a.get("mcps", [])]
        detail_data[key] = {
            "type": "mcp",
            "name": mc["name"],
            "usedBy": used_by,
            "description": mc.get("detail_description", "") or mc.get("description", ""),
            "markdown": mc.get("markdown", "")
        }
    for i, tm in enumerate(teams):
        key = f"team-{i}"
        detail_data[key] = {
            "type": "team",
            "name": tm["name"],
            "members": tm.get("members", []),
            "description": tm.get("description", "")
        }
    detail_json = json.dumps(detail_data)

    # Build team membership lookup for highlight
    team_data = json.dumps(teams)

    # --- Agent cards ---
    agent_cards = ""
    for agent in agents:
        model_badge = agent.get("model", "inherit")
        model_color = {"opus": "#c084fc", "sonnet": "#818cf8", "haiku": "#38bdf8", "inherit": "#64748b"}.get(model_badge, "#64748b")
        skill_tags = "".join(
            f'<span class="tag tag-skill">/{e(s)}</span>' for s in agent.get("skills", [])
        )
        mcp_tags = "".join(
            f'<span class="tag tag-mcp">{e(m)}</span>' for m in agent.get("mcps", [])
        )
        desc = agent.get("description", "")
        agent_cards += f"""
            <div class="agent-card" id="agent-{e(agent['name'])}" data-name="{e(agent['name'])}">
                <div class="agent-header">
                    <span class="agent-icon">&#x1f464;</span>
                    <span class="agent-name">{e(agent['name'])}</span>
                    <span class="model-badge" style="background:{model_color}">{e(model_badge)}</span>
                </div>
                {'<div class="agent-desc">' + e(desc) + '</div>' if desc else ''}
                <div class="agent-connections">
                    {('<div class="conn-group"><span class="conn-label">Skills</span>' + skill_tags + '</div>') if skill_tags else ''}
                    {('<div class="conn-group"><span class="conn-label">Tools</span>' + mcp_tags + '</div>') if mcp_tags else ''}
                </div>
            </div>"""

    # --- Skill cards ---
    skill_cards = ""
    for sk in skills:
        desc = sk.get("description", "")
        # Find which agents use this skill
        used_by = [a["name"] for a in agents if sk["name"] in a.get("skills", [])]
        used_by_html = ", ".join(used_by) if used_by else "unassigned"
        skill_cards += f"""
            <div class="skill-card" id="skill-{e(sk['name'])}" data-name="{e(sk['name'])}">
                <div class="card-icon">&#x26A1;</div>
                <div class="card-name">/{e(sk['name'])}</div>
                {'<div class="card-desc">' + e(desc) + '</div>' if desc else ''}
                <div class="card-meta">Used by: {e(used_by_html)}</div>
            </div>"""

    # --- MCP cards ---
    mcp_cards = ""
    for mc in mcps:
        desc = mc.get("description", "")
        used_by = [a["name"] for a in agents if mc["name"] in a.get("mcps", [])]
        used_by_html = ", ".join(used_by) if used_by else "available to all"
        mcp_cards += f"""
            <div class="mcp-card" id="mcp-{e(mc['name'])}" data-name="{e(mc['name'])}">
                <div class="card-icon">&#x1F50C;</div>
                <div class="card-name">{e(mc['name'])}</div>
                {'<div class="card-desc">' + e(desc) + '</div>' if desc else ''}
                <div class="card-meta">Used by: {e(used_by_html)}</div>
            </div>"""

    # --- Team cards ---
    team_cards = ""
    for i, tm in enumerate(teams):
        members_html = "".join(f'<span class="team-member">{e(m)}</span>' for m in tm.get("members", []))
        team_cards += f"""
            <div class="team-card" id="team-{i}" data-members='{json.dumps(tm.get("members", []))}'>
                <div class="team-name">&#x1F91D; {e(tm['name'])}</div>
                <div class="team-members">{members_html}</div>
            </div>"""

    # --- Lifecycle ---
    lifecycle_html = ""
    if lifecycle:
        steps = []
        for i, step in enumerate(lifecycle):
            steps.append(f'<span class="lc-step">/{e(step)}</span>')
            if i < len(lifecycle) - 1:
                steps.append('<span class="lc-arrow">&#x2192;</span>')
        lifecycle_html = f"""
        <div class="section">
            <div class="section-title">Product Lifecycle</div>
            <div class="lifecycle">{''.join(steps)}</div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(name)} - AI Org Chart</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0f172a; color: #e2e8f0; min-height: 100vh;
    overflow-x: hidden;
  }}

  /* SVG overlay for connection lines */
  #connections {{
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none; z-index: 0;
  }}

  .page {{ position: relative; max-width: 1200px; margin: 0 auto; padding: 0 24px; }}

  /* Header */
  .header {{ text-align: center; padding: 36px 20px 12px; }}
  .header h1 {{
    font-size: 2rem;
    background: linear-gradient(135deg, #818cf8, #c084fc);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
  }}
  .header p {{ color: #94a3b8; font-size: 0.95rem; }}

  /* CEO node */
  .ceo-row {{ display: flex; justify-content: center; padding: 20px 0 8px; }}
  .ceo-node {{
    padding: 14px 32px; border-radius: 14px; text-align: center;
    background: linear-gradient(135deg, #fbbf24, #f59e0b);
    color: #1e293b; font-weight: 700; font-size: 1.05rem;
    box-shadow: 0 4px 16px rgba(251,191,36,0.25);
    position: relative; z-index: 1;
  }}

  /* Section */
  .section {{ padding: 16px 0; }}
  .section-title {{
    font-size: 0.8rem; color: #94a3b8; text-transform: uppercase;
    letter-spacing: 2px; margin-bottom: 14px; padding-left: 10px;
    border-left: 3px solid #818cf8;
  }}

  /* Agent cards */
  .agent-row {{
    display: flex; flex-wrap: wrap; gap: 16px; justify-content: center;
    position: relative; z-index: 1;
  }}
  .agent-card {{
    background: #1e293b; border: 1px solid #3b82f6; border-radius: 12px;
    padding: 16px; width: 220px; transition: all 0.2s; cursor: default;
    position: relative; z-index: 1;
  }}
  .agent-card:hover, .agent-card.highlight {{
    border-color: #60a5fa; box-shadow: 0 0 20px rgba(59,130,246,0.25);
    transform: translateY(-2px);
  }}
  .agent-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }}
  .agent-icon {{ font-size: 1.3rem; }}
  .agent-name {{ font-weight: 600; font-size: 1rem; flex: 1; }}
  .model-badge {{
    font-size: 0.65rem; padding: 2px 8px; border-radius: 8px;
    color: #fff; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;
  }}
  .agent-desc {{ font-size: 0.8rem; color: #94a3b8; margin-bottom: 8px; line-height: 1.4; }}
  .agent-connections {{ display: flex; flex-direction: column; gap: 6px; }}
  .conn-group {{ display: flex; flex-wrap: wrap; align-items: center; gap: 4px; }}
  .conn-label {{
    font-size: 0.65rem; color: #64748b; text-transform: uppercase;
    letter-spacing: 1px; width: 42px; flex-shrink: 0;
  }}
  .tag {{
    font-size: 0.7rem; padding: 2px 7px; border-radius: 6px; font-weight: 500;
  }}
  .tag-skill {{ background: rgba(139,92,246,0.2); color: #a78bfa; border: 1px solid rgba(139,92,246,0.3); }}
  .tag-mcp {{ background: rgba(16,185,129,0.15); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.25); }}

  /* Skill / MCP cards */
  .card-row {{
    display: flex; flex-wrap: wrap; gap: 12px; justify-content: center;
    position: relative; z-index: 1;
  }}
  .skill-card, .mcp-card {{
    border-radius: 10px; padding: 12px 16px; width: 170px;
    text-align: center; transition: all 0.2s; cursor: default;
    position: relative; z-index: 1;
  }}
  .skill-card {{
    background: rgba(139,92,246,0.08); border: 1px solid rgba(139,92,246,0.25);
  }}
  .skill-card:hover, .skill-card.highlight {{
    border-color: #8b5cf6; box-shadow: 0 0 16px rgba(139,92,246,0.2);
  }}
  .mcp-card {{
    background: rgba(16,185,129,0.06); border: 1px solid rgba(16,185,129,0.2);
  }}
  .mcp-card:hover, .mcp-card.highlight {{
    border-color: #10b981; box-shadow: 0 0 16px rgba(16,185,129,0.2);
  }}
  .card-icon {{ font-size: 1.2rem; margin-bottom: 4px; }}
  .card-name {{ font-weight: 600; font-size: 0.9rem; }}
  .card-desc {{ font-size: 0.75rem; color: #94a3b8; margin-top: 4px; line-height: 1.3; }}
  .card-meta {{ font-size: 0.65rem; color: #475569; margin-top: 6px; font-style: italic; }}

  /* Team cards */
  .team-row {{ display: flex; flex-wrap: wrap; gap: 14px; justify-content: center; }}
  .team-card {{
    background: transparent; border: 2px dashed #475569; border-radius: 12px;
    padding: 14px 18px; min-width: 200px; cursor: pointer;
    transition: all 0.2s; position: relative; z-index: 1;
  }}
  .team-card:hover {{ border-color: #818cf8; }}
  .team-card.active {{ border-color: #818cf8; background: rgba(129,140,248,0.05); }}
  .team-name {{ font-weight: 600; font-size: 0.95rem; margin-bottom: 6px; }}
  .team-members {{ display: flex; flex-wrap: wrap; gap: 4px; }}
  .team-member {{
    font-size: 0.75rem; padding: 3px 8px; border-radius: 6px;
    background: rgba(129,140,248,0.12); color: #a5b4fc; border: 1px solid rgba(129,140,248,0.2);
  }}

  /* Lifecycle */
  .lifecycle {{
    display: flex; align-items: center; flex-wrap: wrap; gap: 6px;
    justify-content: center;
  }}
  .lc-step {{
    background: #1e293b; border: 1px solid #475569; padding: 6px 14px;
    border-radius: 8px; font-family: monospace; font-size: 0.85rem; color: #e2e8f0;
  }}
  .lc-arrow {{ color: #818cf8; font-size: 1.1rem; font-weight: 700; }}

  /* Legend */
  .legend {{
    display: flex; gap: 20px; justify-content: center; padding: 12px 0 4px;
    flex-wrap: wrap;
  }}
  .legend-item {{ display: flex; align-items: center; gap: 6px; font-size: 0.8rem; color: #94a3b8; }}
  .legend-line {{
    width: 32px; height: 0; border-top: 2px solid; display: inline-block;
  }}
  .legend-line.solid {{ border-color: #475569; }}
  .legend-line.dotted {{ border-color: #475569; border-top-style: dashed; }}

  .footer {{ text-align: center; padding: 32px; color: #334155; font-size: 0.8rem; }}

  /* Fade non-highlighted on team hover */
  .page.filtering .agent-card:not(.highlight),
  .page.filtering .skill-card:not(.highlight),
  .page.filtering .mcp-card:not(.highlight) {{
    opacity: 0.2; transform: scale(0.97);
  }}

  /* Detail panel (slide-in from right) */
  .detail-overlay {{
    position: fixed; top: 0; right: 0; width: 420px; max-width: 90vw; height: 100vh;
    background: #1e293b; border-left: 2px solid #334155; z-index: 100;
    transform: translateX(100%); transition: transform 0.25s ease;
    display: flex; flex-direction: column; box-shadow: -8px 0 32px rgba(0,0,0,0.4);
  }}
  .detail-overlay.open {{ transform: translateX(0); }}
  .detail-header {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 20px; border-bottom: 1px solid #334155; flex-shrink: 0;
  }}
  .detail-header h2 {{ font-size: 1.1rem; color: #e2e8f0; margin: 0; }}
  .detail-close {{
    background: none; border: none; color: #94a3b8; font-size: 1.4rem;
    cursor: pointer; padding: 4px 8px; border-radius: 6px;
  }}
  .detail-close:hover {{ background: #334155; color: #e2e8f0; }}
  .detail-type {{
    font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px;
    padding: 2px 8px; border-radius: 6px; margin-right: 10px; font-weight: 600;
  }}
  .detail-type.agent {{ background: rgba(59,130,246,0.2); color: #60a5fa; }}
  .detail-type.skill {{ background: rgba(139,92,246,0.2); color: #a78bfa; }}
  .detail-type.mcp {{ background: rgba(16,185,129,0.15); color: #6ee7b7; }}
  .detail-type.team {{ background: rgba(129,140,248,0.12); color: #a5b4fc; }}
  .detail-body {{
    padding: 20px; overflow-y: auto; flex: 1;
    font-size: 0.85rem; line-height: 1.7; color: #cbd5e1;
  }}
  .detail-body pre {{
    background: #0f172a; border: 1px solid #334155; border-radius: 8px;
    padding: 12px; overflow-x: auto; font-size: 0.8rem; margin: 8px 0;
  }}
  .detail-body code {{ color: #a78bfa; }}
  .detail-body h1, .detail-body h2, .detail-body h3 {{
    color: #e2e8f0; margin: 16px 0 8px; }}
  .detail-body h1 {{ font-size: 1.1rem; }}
  .detail-body h2 {{ font-size: 1rem; }}
  .detail-body h3 {{ font-size: 0.9rem; }}
  .detail-body ul, .detail-body ol {{ padding-left: 20px; margin: 6px 0; }}
  .detail-body li {{ margin: 4px 0; }}
  .detail-body strong {{ color: #e2e8f0; }}
  .detail-body .detail-meta {{
    background: #0f172a; border-radius: 8px; padding: 12px; margin-bottom: 16px;
    font-size: 0.8rem;
  }}
  .detail-body .detail-meta span {{ display: block; margin: 4px 0; }}
  .detail-body .detail-meta .meta-label {{ color: #64748b; text-transform: uppercase;
    font-size: 0.65rem; letter-spacing: 1px; }}
  .detail-scrim {{
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.3); z-index: 99; display: none;
  }}
  .detail-scrim.open {{ display: block; }}
</style>
</head>
<body>
<div class="page" id="page">
  <svg id="connections"></svg>

  <div class="header">
    <h1>{e(name)}</h1>
    <p>AI Org Chart</p>
  </div>

  <div class="legend">
    <div class="legend-item"><span class="legend-line solid"></span> Direct relationship</div>
    <div class="legend-item"><span class="legend-line dotted"></span> Optional tool access</div>
    <div class="legend-item"><span class="model-badge" style="background:#64748b;font-size:0.65rem;padding:2px 6px;border-radius:6px;color:#fff">model</span> AI model used</div>
  </div>

  <div class="ceo-row">
    <div class="ceo-node" id="ceo-node">&#x1F451; CEO (You)</div>
  </div>

  <div class="section">
    <div class="section-title">Employees (Agents)</div>
    <div class="agent-row">{agent_cards if agent_cards else '<p style="color:#64748b;text-align:center;width:100%">No agents defined</p>'}
    </div>
  </div>

  <div class="section">
    <div class="section-title">SOPs (Skills)</div>
    <div class="card-row">{skill_cards if skill_cards else '<p style="color:#64748b;text-align:center;width:100%">No skills defined</p>'}
    </div>
  </div>

  <div class="section">
    <div class="section-title">Tools (MCP Servers)</div>
    <div class="card-row">{mcp_cards if mcp_cards else '<p style="color:#64748b;text-align:center;width:100%">No MCP servers configured</p>'}
    </div>
  </div>

  {lifecycle_html}

  <div class="section">
    <div class="section-title">Agent Teams</div>
    <div class="team-row">{team_cards if team_cards else '<p style="color:#64748b;text-align:center;width:100%">No teams defined</p>'}
    </div>
  </div>

  <div class="footer">Generated by Solopreneur Scaffold &middot; Claude Code Plugin</div>
</div>

<div class="detail-scrim" id="detail-scrim"></div>
<div class="detail-overlay" id="detail-panel">
  <div class="detail-header">
    <div style="display:flex;align-items:center">
      <span class="detail-type" id="detail-type-badge"></span>
      <h2 id="detail-title"></h2>
    </div>
    <button class="detail-close" id="detail-close">&times;</button>
  </div>
  <div class="detail-body" id="detail-body"></div>
</div>

<script>
const CONNECTIONS = {connections_json};
const TEAMS = {team_data};
const DETAIL_DATA = {detail_json};

function getCenter(el) {{
  const r = el.getBoundingClientRect();
  const pr = document.getElementById('page').getBoundingClientRect();
  return {{
    x: r.left - pr.left + r.width / 2,
    y: r.top - pr.top + r.height / 2
  }};
}}

function getEdge(el, targetCenter) {{
  const r = el.getBoundingClientRect();
  const pr = document.getElementById('page').getBoundingClientRect();
  const cx = r.left - pr.left + r.width / 2;
  const cy = r.top - pr.top + r.height / 2;
  // Return bottom-center if target is below, top-center if above
  if (targetCenter.y > cy) {{
    return {{ x: cx, y: r.top - pr.top + r.height }};
  }} else {{
    return {{ x: cx, y: r.top - pr.top }};
  }}
}}

function drawConnections() {{
  const svg = document.getElementById('connections');
  const page = document.getElementById('page');
  svg.setAttribute('width', page.scrollWidth);
  svg.setAttribute('height', page.scrollHeight);
  svg.innerHTML = '';

  CONNECTIONS.forEach(conn => {{
    const fromEl = document.getElementById(conn.from);
    const toEl = document.getElementById(conn.to);
    if (!fromEl || !toEl) return;

    const toCenter = getCenter(toEl);
    const fromPt = getEdge(fromEl, toCenter);
    const fromCenter = getCenter(fromEl);
    const toPt = getEdge(toEl, fromCenter);

    // Curved path
    const midY = (fromPt.y + toPt.y) / 2;
    const d = `M${{fromPt.x}},${{fromPt.y}} C${{fromPt.x}},${{midY}} ${{toPt.x}},${{midY}} ${{toPt.x}},${{toPt.y}}`;

    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', d);
    path.setAttribute('fill', 'none');
    path.setAttribute('data-from', conn.from);
    path.setAttribute('data-to', conn.to);

    if (conn.type === 'dotted') {{
      path.setAttribute('stroke', 'rgba(16,185,129,0.25)');
      path.setAttribute('stroke-width', '1.5');
      path.setAttribute('stroke-dasharray', '6,4');
    }} else if (conn.from === 'ceo-node') {{
      path.setAttribute('stroke', 'rgba(251,191,36,0.2)');
      path.setAttribute('stroke-width', '1.5');
    }} else {{
      path.setAttribute('stroke', 'rgba(139,92,246,0.25)');
      path.setAttribute('stroke-width', '1.5');
    }}

    svg.appendChild(path);
  }});
}}

// Highlight connections on agent hover
document.querySelectorAll('.agent-card').forEach(card => {{
  card.addEventListener('mouseenter', () => {{
    const id = card.id;
    document.querySelectorAll('#connections path').forEach(p => {{
      if (p.getAttribute('data-from') === id || p.getAttribute('data-to') === id) {{
        p.setAttribute('stroke-opacity', '1');
        p.setAttribute('stroke-width', '2.5');
        if (p.getAttribute('stroke-dasharray')) {{
          p.setAttribute('stroke', 'rgba(16,185,129,0.7)');
        }} else if (p.getAttribute('data-from') === 'ceo-node') {{
          p.setAttribute('stroke', 'rgba(251,191,36,0.6)');
        }} else {{
          p.setAttribute('stroke', 'rgba(139,92,246,0.7)');
        }}
        // Highlight connected nodes
        const targetId = p.getAttribute('data-from') === id ? p.getAttribute('data-to') : p.getAttribute('data-from');
        const target = document.getElementById(targetId);
        if (target) target.classList.add('highlight');
      }}
    }});
  }});
  card.addEventListener('mouseleave', () => {{
    drawConnections(); // Reset
    document.querySelectorAll('.highlight').forEach(el => el.classList.remove('highlight'));
  }});
}});

// Team hover: highlight members
document.querySelectorAll('.team-card').forEach(card => {{
  card.addEventListener('mouseenter', () => {{
    const members = JSON.parse(card.getAttribute('data-members'));
    card.classList.add('active');
    document.getElementById('page').classList.add('filtering');
    members.forEach(m => {{
      const agentEl = document.getElementById('agent-' + m);
      if (agentEl) agentEl.classList.add('highlight');
      // Also highlight their skills/mcps
      CONNECTIONS.filter(c => c.from === 'agent-' + m).forEach(c => {{
        const el = document.getElementById(c.to);
        if (el) el.classList.add('highlight');
      }});
    }});
  }});
  card.addEventListener('mouseleave', () => {{
    card.classList.remove('active');
    document.getElementById('page').classList.remove('filtering');
    document.querySelectorAll('.highlight').forEach(el => el.classList.remove('highlight'));
  }});
}});

// Draw on load and resize
window.addEventListener('load', drawConnections);
window.addEventListener('resize', drawConnections);

// --- Detail panel click-to-view ---
const panel = document.getElementById('detail-panel');
const scrim = document.getElementById('detail-scrim');
const detailTitle = document.getElementById('detail-title');
const detailBadge = document.getElementById('detail-type-badge');
const detailBody = document.getElementById('detail-body');
const detailClose = document.getElementById('detail-close');

function mdToHtml(text) {{
  // Minimal markdown-to-HTML for descriptions
  if (!text) return '';
  let s = text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/^\\d+\\. (.+)$/gm, '<li>$1</li>');
  // Wrap consecutive <li> in <ul>
  s = s.replace(/((?:<li>.*<\\/li>\\n?)+)/g, '<ul>$1</ul>');
  // Paragraphs
  s = s.replace(/\\n\\n/g, '</p><p>');
  return '<p>' + s + '</p>';
}}

function openDetail(id) {{
  const data = DETAIL_DATA[id];
  if (!data) return;
  detailTitle.textContent = data.name;
  detailBadge.textContent = data.type;
  detailBadge.className = 'detail-type ' + data.type;
  let html = '';
  if (data.type === 'agent') {{
    html += '<div class="detail-meta">';
    html += '<span><span class="meta-label">Model</span> ' + (data.model || 'inherit') + '</span>';
    if (data.skills.length) html += '<span><span class="meta-label">Skills</span> ' + data.skills.map(s => '/' + s).join(', ') + '</span>';
    if (data.mcps.length) html += '<span><span class="meta-label">Tools</span> ' + data.mcps.join(', ') + '</span>';
    html += '</div>';
  }} else if (data.type === 'skill' || data.type === 'mcp') {{
    if (data.usedBy && data.usedBy.length) {{
      html += '<div class="detail-meta"><span><span class="meta-label">Used by</span> ' + data.usedBy.join(', ') + '</span></div>';
    }}
  }} else if (data.type === 'team') {{
    if (data.members && data.members.length) {{
      html += '<div class="detail-meta"><span><span class="meta-label">Members</span> ' + data.members.join(', ') + '</span></div>';
    }}
  }}
  if (data.description) {{
    html += '<p style="color:#94a3b8;font-style:italic;margin-bottom:12px">' + data.description.replace(/</g,'&lt;') + '</p>';
  }}
  if (data.markdown) {{
    html += mdToHtml(data.markdown);
  }}
  if (!data.description && !data.markdown) {{
    html += '<p style="color:#475569">No detailed description available. Add a "markdown" field to the JSON config for this element.</p>';
  }}
  detailBody.innerHTML = html;
  panel.classList.add('open');
  scrim.classList.add('open');
}}

function closeDetail() {{
  panel.classList.remove('open');
  scrim.classList.remove('open');
}}

detailClose.addEventListener('click', closeDetail);
scrim.addEventListener('click', closeDetail);
document.addEventListener('keydown', (ev) => {{ if (ev.key === 'Escape') closeDetail(); }});

// Make all cards clickable
document.querySelectorAll('.agent-card, .skill-card, .mcp-card, .team-card').forEach(card => {{
  card.style.cursor = 'pointer';
  card.addEventListener('click', (ev) => {{
    ev.stopPropagation();
    openDetail(card.id);
  }});
}});
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
    parser.add_argument("--output", default="org-chart.html", help="Output file path")

    args = parser.parse_args()

    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    elif args.plugin_dir:
        config = build_from_plugin(args.plugin_dir)
    else:
        config = build_from_cli(args)

    html_content = generate_html(config)

    with open(args.output, "w") as f:
        f.write(html_content)

    print(f"Org chart generated: {args.output}")
    print(f"Open in your browser: open {args.output}")


if __name__ == "__main__":
    main()
