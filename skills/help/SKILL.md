---
name: help
description: Get oriented with the solopreneur plugin — see your AI team, check project status, and get suggestions for what to do next. Use when you're getting started or need a refresher.
argument-hint: "optional: topic (skills, team, workflow, evals, getting started)"
---

# Help: $ARGUMENTS

The user wants to get oriented with the solopreneur plugin. Show them their AI team, where they are in the workflow, and what to do next. Adapt examples to the current runner: Claude Code can use `/solopreneur:<skill>` slash commands; Codex and other runners can invoke skills by name or natural language.

## Instructions

### 1. Route by topic (if $ARGUMENTS provided)

If the user specified a topic, jump to the relevant section:

- **"skills"** → Skip to Step 4 (skill reference table)
- **"team"** → Skip to Step 3 (show team + org chart)
- **"workflow"** or **"lifecycle"** → Explain the product lifecycle pipeline, then show the skill table
- **"evals"** or **"testing"** → Skip to Step 6 (eval system guide)
- **"getting started"** → Run full onboarding (Steps 2, 4, 5)
- **Anything else** → Treat as a question; answer it using the context below, then offer the full onboarding

If no arguments, run the full onboarding experience (Steps 2, 4, 5). Do NOT auto-generate the org chart — just mention it's available via the help/team skill.

### 2. Detect project state and suggest next step

Check the `.solopreneur/` directory to figure out where the user is in their journey. Scan in order:

1. **No `.solopreneur/` directory at all** → Brand new! Say: "Looks like you're just getting started. Your AI team is ready to go — let's kick things off. Run the discover skill for your idea to research and validate it."

2. **Has `.solopreneur/discoveries/` with files but no `.solopreneur/specs/`** → Say: "You've explored some ideas. Ready to turn one into a product spec? Run the spec skill on one of the discovery files."

3. **Has specs but no `.solopreneur/backlog/`** → Suggest the backlog skill with the spec path

4. **Has backlog with pending tickets but no `.solopreneur/designs/`** → Suggest the design skill or build skill depending on whether the project has a UI component

5. **Has backlog with pending tickets** → Suggest the build skill for single tickets or sprint skill for parallel execution

6. **Has built tickets (check backlog YAML for `status: built` or `status: tested`)** → Suggest the review skill

7. **Has reviewed work** → Suggest the ship skill

8. **Has shipped** → Suggest the release-notes skill

Present the suggestion conversationally: "Here's where you left off: [context]. I'd suggest [next step] — want to do that?"

### 3. Show team + org chart (only on help/team requests)

This step ONLY runs when the user explicitly asks for "team" (for example, `/solopreneur:help team` in Claude Code or "show my Solopreneur team" in Codex). It is NOT part of the default onboarding flow.

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

| Skill | What it does | Claude Code example |
|-------|-------------|---------------------|
| `discover` | Research and validate an idea | `/solopreneur:discover meal planning app for busy parents` |
| `spec` | Write a product requirements doc | `/solopreneur:spec [discovery file or idea]` |
| `backlog` | Break spec into prioritized tickets | `/solopreneur:backlog [spec file]` |
| `design` | Create UI/UX direction + HTML mockups | `/solopreneur:design [spec or feature]` |
| `build` | Plan or build a feature | `/solopreneur:build [ticket or feature]` |
| `review` | Multi-perspective quality review | `/solopreneur:review recent` |
| `ship` | Quality gate + deployment | `/solopreneur:ship` |
| `release-notes` | Audience-targeted announcements | `/solopreneur:release-notes for twitter` |

**Team & Utility:**

| Skill | What it does | Claude Code example |
|-------|-------------|---------------------|
| `kickoff` | Run a team meeting with multiple agents | `/solopreneur:kickoff discovery sprint on [topic]` |
| `sprint` | Build multiple tickets in parallel | `/solopreneur:sprint` |
| `standup` | Daily summary of recent activity | `/solopreneur:standup` |
| `story` | Turn your building journey into a narrative | `/solopreneur:story blog post` |
| `scaffold` | Design your own AI org from scratch | `/solopreneur:scaffold "I am a freelance designer"` |
| `help` | You're here! | `/solopreneur:help skills` |

Want to see your team visually? Run the help/team skill to open the interactive org chart.

### 5. Mention platform concepts

End with: "If you want to understand how skills, agents, hooks, MCP servers, or Codex/Claude Code plugin installs work under the hood, ask me directly."

### 6. Eval system guide (only on `/help evals` or `/help testing`)

This step ONLY runs when the user explicitly asks for "evals" or "testing". It is NOT part of the default onboarding flow.

Present the eval system as a way to systematically improve skills:

**What evals are:**

Your plugin includes an automated testing system. Each skill has test cases that check whether it produces the right output. An LLM judge grades each test against specific expected behaviors.

**Quick commands:**

```bash
# See what tests exist (no cost — just shows test cases)
bash evals/run-evals.sh --dry

# Codex dry run
bash evals/run-evals.sh --runner codex --dry

# Run evals for a specific skill
bash evals/run-evals.sh [skill-name]

# Run all evals
bash evals/run-evals.sh

# Run all skills in parallel (faster for full suite)
bash evals/run-evals.sh --parallel

# Use a stronger model for more thorough testing
EVAL_MODEL=opus bash evals/run-evals.sh [skill-name]
```

**The improvement loop:**

1. Run evals for a skill: `bash evals/run-evals.sh [skill]`
2. Read the judge feedback in `.eval-runs/[skill]/[test-id].judge.json`
3. Refine the skill's SKILL.md based on what failed
4. Re-run evals to verify the fix

**Adding new test cases:**

Each skill's `eval.csv` defines its tests. The format is:

```csv
id,should_trigger,prompt,expected_behaviors
```

- **Positive tests** (`should_trigger=true`): Check the skill produces the right output
- **Negative tests** (`should_trigger=false`): Check the skill doesn't falsely trigger
- **Expected behaviors**: Pipe-separated, specific and countable (e.g., "Identifies at least 3 competitors")

See `evals/README.md` for detailed guidance on writing good test cases.

## Tone

- Warm and welcoming, like a coworker showing someone around the office
- Use "your team" and "your employees" language — reinforce the virtual company metaphor
- Keep it scannable — bullet points and tables over paragraphs
- Adapt to technical level: if the user seems non-technical, explain concepts in plain language
