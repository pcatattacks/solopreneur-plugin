---
name: scaffold
description: Design and scaffold your own AI org structure with custom agents, skills, teams, hooks, and MCP servers. Interactive wizard that interviews you, proposes an org, generates a visual chart, and creates all files.
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

**About sharing:**
6. **Is this just for you, or do you want to share it with others?**
   - **Personal use only**: We'll create a project setup (CLAUDE.md + agents + skills) without plugin packaging. Simpler, no marketplace config needed.
   - **Share with team/community**: We'll create a full plugin with `plugin.json` and `marketplace.json` so others can install it.

Check the examples in `skills/scaffold/examples/` for reference architectures that might match the user's profile.

## Step 2: Propose Org Structure

Based on their answers, propose an org structure. Adapt the format to their technical level:

**For technical users**, use the detailed format:
```markdown
# Your AI Org: [User's Business]

## Employees (Agents)
1. **[Name]** (model: [opus/sonnet/haiku]) - [What they do, 1 sentence]
   - Skills: /[name]:[skill1], /[name]:[skill2]
   - Tools: [MCP1], [MCP2]

## SOPs (Skills)
1. `/[plugin-name]:[skill]` - [What it does]

## Automation (Hooks)
- After file changes: [what happens automatically]
- After commands: [what happens automatically]

## Team Meetings (Agent Teams)
Invoke with `/[name]:kickoff [team-name] [topic]`:
1. **[Team Name]**: [Agent 1] + [Agent 2] + [Agent 3] - [When to use]

## Product Lifecycle
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
- Say "/[name]:[skill]" and [Employee] will [what happens in plain terms]
- ...

## They Work Together Too
Say "/[name]:kickoff [team name]" to start a team meeting:
- **[Team Name]**: When you need [outcome], these employees team up: [names]

## They'll Automatically...
- Keep a log of your decisions (so you can write about your journey later)
- [Other automated behaviors]
```

Ask the user to review and adjust before proceeding.

## Step 3: Generate Visual Org Chart

Create a JSON config file for the org chart, then run the visualization script:

```python
# Write the config to a temp file
config = {
    "name": "[Org Name]",
    "agents": [
        {"name": "...", "model": "...", "skills": [...], "mcps": [...], "description": "..."}
    ],
    "skills": [{"name": "...", "description": "..."}],
    "mcps": [{"name": "...", "description": "..."}],
    "teams": [{"name": "...", "members": [...]}],
    "lifecycle": [...]
}
```

```bash
python3 scripts/visualize-org.py --config [config-file].json --output [plugin-name]-org-chart.html
```

Tell the user to open the HTML file in their browser. Explain: "This chart shows your entire AI team - who they are, what they can do, and what tools they use. Hover over an employee to see their connections. Hover over a team to see who's in it."

## Step 4: Generate Files

On user approval, create the file structure. What you generate depends on their sharing preference:

### For personal use (no plugin packaging):
1. **`[name]/CLAUDE.md`** - Company handbook tailored to their workflow
2. **`[name]/agents/[agent].md`** - One file per agent with YAML frontmatter (name, description, tools, model) and role-specific system prompt
3. **`[name]/skills/[skill]/SKILL.md`** - One skill per SOP with YAML frontmatter and process instructions. Always generate a `skills/kickoff/SKILL.md` that reads team definitions from the org's CLAUDE.md. Use the solopreneur plugin's kickoff as a reference pattern — it works generically with any team definitions. If the org has a ship/deploy skill, it should read deployment config from `.solopreneur/preferences.yaml`, support first-time deployment setup, and pattern after the solopreneur plugin's ship skill.
4. **`[name]/.mcp.json`** - MCP servers based on their daily tools
5. **`[name]/settings.json`** - Enable agent teams
6. **`[name]/hooks/hooks.json`** - Automated behaviors (at minimum: decision and session boundary logging)
7. **`[name]/scripts/observer-log.sh`** - Copy from this plugin's `scripts/` for automated logging
8. **`[name]/evals/run-evals.sh`** - Copy from this plugin's `skills/scaffold/templates/evals/run-evals.sh` (make executable with `chmod +x`)
9. **`[name]/evals/rubric.md`** - Copy from this plugin's `skills/scaffold/templates/evals/rubric.md`
10. **`[name]/evals/README.md`** - Copy from this plugin's `skills/scaffold/templates/evals/README.md`
11. **`[name]/skills/[top-skill]/eval.csv`** - Generate starter eval CSV (see eval guidance below)

### For sharing (full plugin):
All of the above, plus:
12. **`[name]/.claude-plugin/plugin.json`** - Plugin manifest with name, description, version
13. **`[name]/.claude-plugin/marketplace.json`** - Registry manifest for distribution

### Hooks configuration
Always include a `hooks/hooks.json` that:
- Captures CEO decisions (PostToolUse on AskUserQuestion) to an observer log

Explain to the user: "Hooks automatically capture your decisions when your AI team asks you questions. This builds a decision journal you can use to write about your building journey later."

### CLAUDE.md communication level
In the generated CLAUDE.md, include a section like:
```
## Communication Style
The CEO's technical level is: [beginner/intermediate/advanced]
- [beginner]: Explain everything in plain language. Avoid jargon. Use analogies. Always explain what a command does before running it. When showing file paths, explain what they mean.
- [intermediate]: Can use a terminal and understands basic concepts. Explain technical decisions but not basic operations.
- [advanced]: Be concise and technical. Skip explanations of standard tools and patterns.
```

### Git management section
In the generated CLAUDE.md, include:
```
## Version Control
You (Claude) manage all git operations for the CEO. They should never need to use git directly.
- Automatically create commits after significant milestones with clear, descriptive messages
- Explain what you're saving and why in plain language: "I'm saving a checkpoint of your work so we can go back to this point if needed"
- If the user wants to share their plugin, handle GitHub repository creation and pushing
- Always explain what you're doing with git before doing it
```

### Eval CSV generation

Generate a starter `skills/[top-skill]/eval.csv` with 4 test cases: 3 positive + 1 negative. Use the user's top skill (the one most central to their workflow).

Each positive test should have 3-5 specific, countable expected_behaviors (pipe-separated). Negative tests should describe what the skill should NOT do.

Example for a hypothetical `/content:brainstorm` skill:

```csv
id,should_trigger,prompt,expected_behaviors
explicit-topic,true,"Run /content:brainstorm about sustainable fashion","Generates at least 5 content ideas|Includes mix of formats (blog, video, social)|Ideas are specific to sustainable fashion"
implicit-stuck,true,"I'm running out of things to write about for my cooking blog","Triggers brainstorm workflow|Generates ideas relevant to cooking|Suggests content gaps or trends"
edge-broad,true,"Brainstorm content ideas","Asks clarifying questions about niche or audience|Does not generate generic ideas without context"
negative-write,false,"Write the introduction paragraph for my blog post about coffee","Does NOT trigger brainstorm|Recognizes this is a writing task"
```

Also add `.eval-runs/` to the generated `.gitignore` (eval artifacts are ephemeral).

## Step 5: Test & Next Steps

Tell the user (adapted to their technical level):

**For technical users:**
```
Your setup is ready! Test it with:
  claude --plugin-dir ./[name]

Try your first skill:
  /[name]:[first-skill] [example input]

See your eval test cases:
  bash evals/run-evals.sh [skill] --dry

Run the full eval (invokes your skill and grades the output):
  bash evals/run-evals.sh [skill]
```

**For non-technical users:**
```
Your AI team is ready! Here's how to use it:

1. Open your terminal and navigate to the [name] folder
2. Start Claude Code with your team loaded:
   claude --plugin-dir ./[name]
3. Try talking to your team:
   /[name]:[first-skill] [example in their domain]

Your team will handle everything from there. If you ever want to understand
how something works, just ask:
   /[name]:explain [concept]
```

If they chose to share, also explain:
```
To share your AI team with others:
1. I'll create a GitHub repository for you (just confirm and I'll handle it)
2. Others can then install it with one command

Want me to set up the GitHub repository now?
```

Let them know they can always generate detailed technical documentation later if they need to hand things off to a human developer:
"If you ever need to explain your setup to a developer or document how it works technically, just ask me and I'll generate detailed documentation for you."
