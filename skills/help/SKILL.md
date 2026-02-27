---
name: help
description: Get oriented with the solopreneur plugin — see your AI team, check project status, and get suggestions for what to do next. Use when you're getting started or need a refresher.
argument-hint: "optional: topic (skills, team, workflow, getting started)"
---

# Help: $ARGUMENTS

The user wants to get oriented with the solopreneur plugin. Show them their AI team, where they are in the workflow, and what to do next.

## Instructions

### 1. Route by topic (if $ARGUMENTS provided)

If the user specified a topic, jump to the relevant section:

- **"skills"** → Skip to Step 4 (skill reference table)
- **"team"** → Skip to Step 3 (show team + org chart)
- **"workflow"** or **"lifecycle"** → Explain the product lifecycle pipeline, then show the skill table
- **"getting started"** → Run full onboarding (Steps 2, 4, 5)
- **Anything else** → Treat as a question; answer it using the context below, then offer the full onboarding

If no arguments, run the full onboarding experience (Steps 2, 4, 5). Do NOT auto-generate the org chart — just mention it's available via `/solopreneur:help team`.

### 2. Detect project state and suggest next step

Check the `.solopreneur/` directory to figure out where the user is in their journey. Scan in order:

1. **No `.solopreneur/` directory at all** → Brand new! Say: "Looks like you're just getting started. Your AI team is ready to go — let's kick things off! Try `/solopreneur:discover [your idea]` to research and validate a product idea."

2. **Has `.solopreneur/discoveries/` with files but no `.solopreneur/specs/`** → Say: "You've explored some ideas. Ready to turn one into a product spec? Try `/solopreneur:spec [idea]`"

3. **Has specs but no `.solopreneur/backlog/`** → Suggest `/solopreneur:backlog [spec]`

4. **Has backlog with pending tickets but no `.solopreneur/designs/`** → Suggest `/solopreneur:design [feature]` or `/solopreneur:build` depending on whether the project has a UI component

5. **Has backlog with pending tickets** → Suggest `/solopreneur:build [ticket]` for single tickets or `/solopreneur:sprint` for parallel execution

6. **Has built tickets (check backlog YAML for `status: built` or `status: tested`)** → Suggest `/solopreneur:review`

7. **Has reviewed work** → Suggest `/solopreneur:ship`

8. **Has shipped** → Suggest `/solopreneur:release-notes [audience]`

Present the suggestion conversationally: "Here's where you left off: [context]. I'd suggest [next step] — want to do that?"

### 3. Show team + org chart (only on `/help team`)

This step ONLY runs when the user explicitly asks for "team" (e.g., `/solopreneur:help team`). It is NOT part of the default onboarding flow.

**Smart caching:** Before generating, check if a cached org chart already exists:

1. Check if `.solopreneur/org-chart.html` exists
2. If it exists, compare its last-modified timestamp against the newest file in the plugin's `agents/` and `skills/` directories (go up two directories from this SKILL.md to find the plugin root)
3. If the cache is newer than all source files → just open it: `open .solopreneur/org-chart.html`
4. If any source file is newer, or the cache doesn't exist → regenerate (see below)

**Generating the org chart:**

The `visualize-org.py` script is at `scripts/visualize-org.py` relative to this plugin's root. Go up two directories from this SKILL.md (`skills/help/SKILL.md` → `skills/help/` → `skills/` → plugin root) to find it.

```bash
mkdir -p .solopreneur && python3 <plugin-root>/scripts/visualize-org.py --plugin-dir <plugin-root> --marketing --output .solopreneur/org-chart.html && open .solopreneur/org-chart.html
```

Tell the user: "I've opened your AI team's org chart in your browser. It shows all your employees, what skills they handle, what tools they use, and how the workflow connects them. Click on any card for details."

If the `open` command fails (non-macOS), try `xdg-open` instead. If both fail, just tell the user the file path.

### 4. Show available skills

Present a compact reference:

**Product Lifecycle** (each step suggests the next):
```
/discover → /spec → /backlog → /design → /build → /review → /ship → /release-notes
```

| Skill | What it does | Example |
|-------|-------------|---------|
| `/solopreneur:discover` | Research and validate an idea | `/solopreneur:discover meal planning app for busy parents` |
| `/solopreneur:spec` | Write a product requirements doc | `/solopreneur:spec [discovery file or idea]` |
| `/solopreneur:backlog` | Break spec into prioritized tickets | `/solopreneur:backlog [spec file]` |
| `/solopreneur:design` | Create UI/UX direction + HTML mockups | `/solopreneur:design [spec or feature]` |
| `/solopreneur:build` | Plan or build a feature | `/solopreneur:build [ticket or feature]` |
| `/solopreneur:review` | Multi-perspective quality review | `/solopreneur:review recent` |
| `/solopreneur:ship` | Quality gate + deployment | `/solopreneur:ship` |
| `/solopreneur:release-notes` | Audience-targeted announcements | `/solopreneur:release-notes for twitter` |

**Team & Utility:**

| Skill | What it does | Example |
|-------|-------------|---------|
| `/solopreneur:kickoff` | Run a team meeting with multiple agents | `/solopreneur:kickoff discovery sprint on [topic]` |
| `/solopreneur:sprint` | Build multiple tickets in parallel | `/solopreneur:sprint` |
| `/solopreneur:standup` | Daily summary of recent activity | `/solopreneur:standup` |
| `/solopreneur:story` | Turn your building journey into a narrative | `/solopreneur:story blog post` |
| `/solopreneur:scaffold` | Design your own AI org from scratch | `/solopreneur:scaffold "I am a freelance designer"` |
| `/solopreneur:help` | You're here! | `/solopreneur:help skills` |

Want to see your team visually? Run `/solopreneur:help team` to open the interactive org chart.

### 5. Mention Claude Code concepts

End with: "If you want to understand how skills, agents, hooks, or MCP servers work under the hood, just ask me directly — I can look up the Claude Code documentation for you."

## Tone

- Warm and welcoming, like a coworker showing someone around the office
- Use "your team" and "your employees" language — reinforce the virtual company metaphor
- Keep it scannable — bullet points and tables over paragraphs
- Adapt to technical level: if the user seems non-technical, explain concepts in plain language
