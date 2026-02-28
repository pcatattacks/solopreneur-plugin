---
name: scaffold
description: Design and scaffold your own AI org structure with custom agents, skills, teams, hooks, and MCP servers. Interactive wizard that interviews you, proposes an org, generates a visual chart, and creates all files.
argument-hint: "optional: prior context to skip"
disable-model-invocation: true
---

# Scaffold Your AI Org: $ARGUMENTS

You are helping the user design and build their own AI team. This is an interactive process. Adapt your language to the user's technical level (assessed in Step 1).

## Step 1: Discovery Interview

If `$ARGUMENTS` provides context, use it to skip already-answered questions. Otherwise, ask these questions conversationally (not all at once - ask 1-2 at a time and respond to their answers):

**About them:**
1. **What do you do?** (e.g., "I'm a freelance web developer" or "I run a content agency")
2. **How technical are you?** (e.g., "I code daily" / "I can use a terminal but don't code" / "I'm not technical at all")
   - Use their answer to calibrate ALL subsequent communication. For non-technical users: avoid jargon, explain every concept, use real-world analogies. For developers: be concise and technical.

**About their work:**
3. **What takes up most of your time?** (e.g., "Client proposals, code review, invoicing")
4. **What would your dream AI team look like?** (e.g., "A sales person, a designer, and a code reviewer")
5. **What tools do you use daily?** (e.g., "GitHub, Figma, Slack, Notion, Stripe")
6. **Do you have any MCP servers you'd like to connect?** MCP servers let your AI team interact with external tools (databases, calendars, APIs). If the user knows of specific MCP servers, include them. If not, skip — they can add them later. Do NOT generate fake MCP endpoint URLs for tools that don't have known servers.

**About sharing:**
7. **Is this just for you, or do you want to distribute it on the marketplace?**
   - **Personal use (or sharing via git)**: We'll create a project with `.claude/` structure — simpler, no plugin packaging. Others can still use it by cloning the repo.
   - **Marketplace distribution**: We'll create a full plugin with `.claude-plugin/plugin.json` and `marketplace.json` for the Anthropic marketplace.

**About their setup:**
8. **What Claude plan are you on?** (Pro, Max, Team, or API)
   - Use this to calibrate model guidance in Step 5. Don't set explicit models on agents — all agents inherit from the session model, giving users runtime control via `/model`.

Check the examples in `skills/scaffold/examples/` for reference architectures that might match the user's profile.

## Step 2: Propose Org Structure

Based on their answers, propose an org structure. Adapt the format to their technical level:

**For technical users**, use the detailed format:
```markdown
# Your AI Org: [User's Business]

## Employees (Agents)
1. **[Name]** - [What they do, 1 sentence]
   - Skills: /[skill1], /[skill2]
   - Tools: [MCP1], [MCP2]

## SOPs (Skills)
1. `/[skill]` - [What it does]

## Automation (Hooks)
- After questions: Decisions are logged automatically for future reference

## Team Meetings (Agent Teams)
Invoke with `/kickoff [team-name] [topic]`:
1. **[Team Name]**: [Agent 1] + [Agent 2] + [Agent 3] - [When to use]

## Workflow
[skill 1] → [skill 2] → [skill 3] → ...
```

**For non-technical users**, use plain language:
```markdown
# Your AI Team: [User's Business]

Think of this as your virtual company. Here's who works for you:

## Your Employees
1. **[Name]** - Like having a [real-world role] on your team. They handle [tasks].
2. ...

## What They Can Do For You
- Say "/[skill]" and [Employee] will [what happens in plain terms]
- ...

## They Work Together Too
Say "/kickoff [team name]" to start a team meeting:
- **[Team Name]**: When you need [outcome], these employees team up: [names]

## They'll Automatically...
- Keep a log of your decisions (so you can write about your journey later)
- [Other automated behaviors]
```

Ask the user to review and adjust before proceeding.

## Step 3: Generate Visual Org Chart

Create a JSON config file for the org chart, then run the visualization script.

```python
# Write the config to a JSON file inside the project
config = {
    "name": "[Org Name]",
    "agents": [
        {"name": "...", "skills": [...], "mcps": [...], "description": "..."}
    ],
    "skills": [{"name": "...", "description": "..."}],
    "mcps": [{"name": "...", "description": "..."}],
    "teams": [{"name": "...", "members": [...]}],
    "lifecycle": [...]
}
```

Save the config JSON inside the project directory (not /tmp/). For personal use: `[name]/.claude/org-chart.json`. For marketplace: `[name]/org-chart.json`.

The `visualize-org.py` script is in this plugin's `scripts/` directory — go up two directories from this SKILL.md (`skills/scaffold/SKILL.md` → plugin root) to find it. Run:

```bash
python3 <plugin-root>/scripts/visualize-org.py --config <project>/org-chart.json --output <project>/org-chart.html && open <project>/org-chart.html
```

Where `<project>` is the user's project directory (for personal use, save the HTML next to the config: `[name]/.claude/org-chart.html` or `[name]/org-chart.html` for marketplace).

Tell the user: "This chart shows your entire AI team — who they are, what they can do, and how the workflow connects them. Click on any card for details."

## Step 3.5: Consult Claude Code Best Practices

Before generating any files, delegate to the `claude-code-guide` subagent for authoritative guidance:

> "I'm building a Claude Code project with custom agents and skills for a [user's domain] workflow. I need:
>
> 1. **Complete frontmatter specs**: All supported YAML frontmatter fields for custom agents (agents/*.md) and custom skills (skills/*/SKILL.md). For each field: name, type, required/optional, default value, and when to use it.
>
> 2. **Agent design best practices**: How should agent markdown bodies be structured? What makes an effective agent description for routing? How should tools be scoped? What should go in the agent body vs what should be in skills?
>
> 3. **Skill design best practices**: How should skills be structured for maintainability? When to use `context: fork` vs running in main context? When to use `disable-model-invocation`? How to structure workflow steps and agent delegation? How to write effective next-step prompts?
>
> 4. **Plugin architecture patterns**: What are proven patterns for multi-agent setups? Common anti-patterns to avoid? How should agents and skills compose together? When to use the `skills` field on agents vs inline instructions?
>
> 5. **Example configurations**: 2-3 example agent and skill files showing best practices for different use cases.
>
> Provide specific, actionable guidance I can apply when generating files."

Use the response as the authoritative reference for all file generation in Step 4. This ensures:
- Generated files use the latest correct format (even if Claude Code adds new fields)
- Architecture follows proven patterns (not just valid syntax)
- Users get an optimally structured org without needing to understand the underlying platform

## Step 4: Generate Files

On user approval, create the file structure. What you generate depends on their sharing preference:

### For personal use (`.claude/` project structure):

This structure is auto-discovered by Claude Code — no `--plugin-dir` flag needed. Skills show as `/skill-name` (no namespace). Others can use it by cloning the repo.

```
[name]/
├── CLAUDE.md
├── .claude/
│   ├── agents/[agent].md
│   ├── skills/[skill]/SKILL.md
│   └── settings.json
├── .mcp.json
├── scripts/observer-log.sh
├── evals/
│   ├── run-evals.sh
│   ├── rubric.md
│   └── README.md
└── .gitignore
```

1. **`[name]/CLAUDE.md`** — Company handbook tailored to their workflow (see CLAUDE.md sections below)
2. **`[name]/.claude/agents/[agent].md`** — One file per agent (see agent guidance below)
3. **`[name]/.claude/skills/[skill]/SKILL.md`** — One skill per workflow (see skill guidance below)
4. **`[name]/.claude/settings.json`** — Settings with hooks included inline:
   ```json
   {
     "env": {
       "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
     },
     "hooks": {
       "PostToolUse": [{
         "matcher": "AskUserQuestion",
         "hooks": [{"type": "command", "command": "bash scripts/observer-log.sh"}]
       }]
     }
   }
   ```
5. **`[name]/.mcp.json`** — MCP servers the user specified. Only include servers the user explicitly provided or that you can verify exist. Do NOT generate fake MCP endpoint URLs. If no MCP servers were requested, create a minimal `.mcp.json` with `{"mcpServers": {}}` and a comment that servers can be added later.
6. **`[name]/scripts/observer-log.sh`** — Copy from `scripts/observer-log.sh` in the plugin root (go up two directories from this SKILL.md). Update the `LOG_FILE` and `ARCHIVE_DIR` paths to match the user's output directory (e.g., `.pm/observer-log.md` instead of `.solopreneur/observer-log.md`).
7. **`[name]/evals/run-evals.sh`** — Copy from `skills/scaffold/templates/evals/run-evals.sh` (same plugin root; make executable with `chmod +x`)
8. **`[name]/evals/rubric.md`** — Copy from `skills/scaffold/templates/evals/rubric.md` (same plugin root)
9. **`[name]/evals/README.md`** — Copy from `skills/scaffold/templates/evals/README.md` (same plugin root)
10. **`[name]/.claude/skills/[skill]/eval.csv`** — Generate eval CSVs for ALL lifecycle skills (see eval guidance below)
11. **`[name]/.gitignore`** — See gitignore template below

### For marketplace distribution (plugin structure):

Same content as above, but with a different directory layout:

```
[name]/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── CLAUDE.md
├── agents/[agent].md          ← at root, not in .claude/
├── skills/[skill]/SKILL.md    ← at root, not in .claude/
├── hooks/hooks.json           ← separate file, not in settings
├── settings.json
├── .mcp.json
├── scripts/observer-log.sh
├── evals/
└── .gitignore
```

Key differences from personal use:
- Agents and skills are at the plugin root (not in `.claude/`)
- Hooks go in `hooks/hooks.json` (not inline in settings.json), using `${CLAUDE_PLUGIN_ROOT}` for script paths:
  ```json
  {"hooks": {"PostToolUse": [{"matcher": "AskUserQuestion", "hooks": [{"type": "command", "command": "bash \"${CLAUDE_PLUGIN_ROOT}/scripts/observer-log.sh\""}]}]}}
  ```
- Add `.claude-plugin/plugin.json` with name, description, version
- Add `.claude-plugin/marketplace.json` for distribution
- Skills are namespaced: `/[plugin-name]:[skill]`

### Agent generation guidance

Use the frontmatter fields from the claude-code-guide specs (Step 3.5). Every agent needs:
- `name` (required): lowercase-with-hyphens identifier
- `description` (required): when Claude should delegate to this agent — be specific, this is Claude's "API docs" for routing
- `color`: assign a color from `purple`, `cyan`, `green`, `orange`, `blue`, `red`. Cycle through the set if there are more agents than colors. This helps users visually identify which agent is running.
- `tools`: restrict to what the agent actually needs (principle of least privilege)
- Do NOT set `model` on agents — let them inherit from the session. This gives users runtime control via `/model`. Only set `model: haiku` for agents that do simple, high-volume tasks (log formatting, simple lookups).
- For agents that benefit from cross-session memory (engineers, analysts, anyone who builds on prior work), add `memory: project`
- Use the `skills` field to share reference material that multiple agents need

The markdown body is the agent's system prompt. Include:
- Role identity (1-2 sentences: who they are, what they specialize in)
- Working methodology (detailed phases, checklists, quality standards — NOT thin)
- Output format (if the agent produces structured output)
- Output location (where to save artifacts)

**Agent bodies should be rich**, not thin. Include detailed methodology: checklists, workflow steps, quality standards, output formats. Official examples all have substantial bodies. Thin agents with just a role description are the anti-pattern.

### Skill generation guidance

Use the frontmatter fields from the claude-code-guide specs (Step 3.5). Common fields:
- `name`: display name (defaults to directory name if omitted)
- `description`: when to use this skill — Claude uses this to decide auto-invocation
- `argument-hint`: brief hint shown in autocomplete (e.g., `"[idea or topic]"`)
- `disable-model-invocation: true`: for skills that should only run when explicitly called (kickoff, help)
- `user-invocable: false`: for internal reference skills that agents load but users don't invoke
- `allowed-tools`: restrict tool access when the skill shouldn't write files or run commands

The markdown body defines the workflow. Structure as:
- Input parsing (what `$ARGUMENTS` expects)
- Process steps (what to do, in order)
- Agent delegation (which agents to spawn and what they handle)
- Output format (what artifacts to produce)
- Next step prompt (suggest the next skill in the workflow)

**Always generate these utility skills:**

1. **`skills/kickoff/SKILL.md`** — Reads team definitions from the org's CLAUDE.md. Use the solopreneur plugin's kickoff as a reference pattern (go up two directories from this SKILL.md to find `skills/kickoff/SKILL.md`) — it works generically with any team definitions.

2. **`skills/help/SKILL.md`** — Onboarding and orientation. Should:
   - Detect project state (check output directories) and suggest next step
   - Show available skills in a table
   - On `/help team`: generate and cache the org chart visualization to `[output-dir]/org-chart.html`. Use smart caching — check if the cached file exists and is newer than all agent/skill files before regenerating.
   - Reference the `visualize-org.py` script using the "go up two directories from SKILL.md" pattern
   - On `/help evals` or `/help testing`: explain the eval system and how to use it to improve skills. Include:
     - What evals are (automated tests that check skill output against expected behaviors)
     - Commands: `bash evals/run-evals.sh --dry` (see tests), `bash evals/run-evals.sh [skill]` (run), `EVAL_MODEL=opus` (stronger model)
     - The improvement loop: run eval → read judge feedback → refine skill → re-run
     - How to add test cases to `eval.csv` files
     - Adapt language to user's technical level: non-technical users get "think of evals as a checklist that automatically tests your AI team"; technical users get the command reference

If the org has a ship/deploy skill, it should read deployment config from preferences, support first-time deployment setup, and pattern after the solopreneur plugin's ship skill.

### CLAUDE.md sections

In the generated CLAUDE.md, include:

**Communication Style:**
```
## Communication Style
The user's technical level is: [beginner/intermediate/advanced]
- [beginner]: Explain everything in plain language. Avoid jargon. Use analogies. Always explain what a command does before running it.
- [intermediate]: Can use a terminal and understands basic concepts. Explain technical decisions but not basic operations.
- [advanced]: Be concise and technical. Skip explanations of standard tools and patterns.

All agents inherit your session model. Use `/model` to switch between sonnet, opus, and haiku.
```

**Team Meetings:** Define named teams using the `**Team Name**: @agent1 + @agent2 + @agent3` format in CLAUDE.md. This format is parsed by the org chart visualization script.

**Version Control:**
```
## Version Control
You (Claude) manage all git operations for the user. They should never need to use git directly.
- Automatically create commits after significant milestones with clear, descriptive messages
- Explain what you're saving and why in plain language: "I'm saving a checkpoint of your work so we can go back to this point if needed"
- If the user wants to share, handle GitHub repository creation and pushing
- Always explain what you're doing with git before doing it
```

**Observer Protocol:** Include the observer format (same as the solopreneur plugin's CLAUDE.md — captures WHY decisions were made for future storytelling).

### Eval CSV generation

Generate a starter `eval.csv` for EVERY lifecycle skill (not utility skills like help/kickoff). Each eval gets 3-4 test cases: 2 positive + 1 edge case + 1 negative.

Each positive test should have 3-5 specific, countable expected_behaviors (pipe-separated). Negative tests should describe what the skill should NOT do.

Example for a hypothetical `/content:brainstorm` skill:

```csv
id,should_trigger,prompt,expected_behaviors
explicit-topic,true,"Run /content:brainstorm about sustainable fashion","Generates at least 5 content ideas|Includes mix of formats (blog, video, social)|Ideas are specific to sustainable fashion"
implicit-stuck,true,"I'm running out of things to write about for my cooking blog","Triggers brainstorm workflow|Generates ideas relevant to cooking|Suggests content gaps or trends"
edge-broad,true,"Brainstorm content ideas","Asks clarifying questions about niche or audience|Does not generate generic ideas without context"
negative-write,false,"Write the introduction paragraph for my blog post about coffee","Does NOT trigger brainstorm|Recognizes this is a writing task"
```

### .gitignore template

```
.eval-runs/
[output-dir]/observer-archives/
.DS_Store
__pycache__/
*.pyc
```

Where `[output-dir]` is the org's output directory (e.g., `.pm/`, `.agency/`). Do NOT gitignore `.claude/` — it contains the org's agents and skills.

### Hooks explanation

Explain to the user: "Hooks automatically capture your decisions when your AI team asks you questions. This builds a decision journal you can reference later — useful for writing about your process or understanding why you made certain choices."

### Initialize git repository

After generating all files, initialize a git repo and create an initial commit so that version control and evals work immediately:

```bash
cd [name]
git init
git add -A
git commit -m "Initial scaffold: [org name] AI team"
```

If the project is already inside a git repo, skip this step. Explain to the user: "I've set up version control so I can save checkpoints of your work and the eval system has a safe sandbox to run in."

## Step 5: Test & Next Steps

Tell the user (adapted to their technical level):

**For personal use:**

*Technical users:*
```
Your setup is ready! Start using it:
  cd [name] && claude

Try your first skill:
  /[first-skill] [example input]

Your agents inherit whatever model you're running. Use /model to switch:
  /model sonnet   — balanced (great default)
  /model opus     — deep reasoning
  /model haiku    — fast and cheap

See your eval test cases:
  bash evals/run-evals.sh [skill] --dry

Run the full eval (invokes your skill and grades the output):
  bash evals/run-evals.sh [skill]
```

*Non-technical users:*
```
Your AI team is ready! Here's how to use it:

1. Open your terminal and navigate to the [name] folder
2. Type "claude" and press Enter — your team is loaded automatically
3. Try talking to your team:
   /[first-skill] [example in their domain]

Your team will handle everything from there. If you ever want to understand
how something works, just ask:
   /help [topic]
```

**For marketplace distribution:**

*In addition to the above:*
```
To test your plugin:
  cd [name] && claude --plugin-dir .

To share your AI team:
1. I'll create a GitHub repository for you (just confirm and I'll handle it)
2. Others can install it from the marketplace

Want me to set up the GitHub repository now?
```

**For all users:**

Also mention:
- "Want to refine your skills? Check the official Anthropic marketplace for the skill-creator plugin — it can test, evaluate, and improve your skills. Browse available plugins with `/plugin`."
- "If you ever need to explain your setup to a developer or document how it works technically, just ask me and I'll generate detailed documentation for you."
- "Run `/help team` to see a visual org chart of your AI team anytime."
