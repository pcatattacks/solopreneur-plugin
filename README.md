# Solopreneur - Your Virtual AI Team

A Claude Code plugin that treats your solopreneur workflow as a virtual company. AI agents act as specialized employees, skills are standard operating procedures, agent teams run parallel meetings, and evals are performance reviews.

## Quick Start

### Install in Claude Code (IDE extension)
1. Open Claude Code in your IDE (Cursor, VS Code)
2. Type `/plugins` → go to **Marketplaces** tab
3. Add: `pcatattacks/solopreneur-plugin`
4. Switch to **Plugins** tab → install **solopreneur**

### Install from marketplace (coming soon)
```
/plugin install solopreneur
```

### Or clone and use from source
```bash
git clone https://github.com/pcatattacks/solopreneur-plugin.git
cd solopreneur-plugin
claude --plugin-dir .
```

## MCP Server Setup

This plugin includes two MCP servers (`.mcp.json`) that work out of the box:

| Server | What it does | Setup needed |
|--------|-------------|-------------|
| **Context7** | Up-to-date library docs for your agents | None — works automatically |
| **Chrome DevTools** | Inspect live web pages | None — needs a Chromium browser open |

For GitHub features (creating repos, PRs, issues), the plugin uses the `gh` CLI. Claude will walk you through setting it up if needed — just say "share this on GitHub" or "push my work."

## Your AI Team

| Employee | Role | Model |
|----------|------|-------|
| Engineer | Architecture, implementation, debugging, code review | inherit |
| Designer | UI/UX, HTML mockups, user flows, accessibility | inherit |
| BizOps | Market analysis, pricing, go-to-market, unit economics | inherit |
| QA | Testing, bug hunting, security review, edge cases | sonnet |
| Researcher | Competitive analysis, market research, trends | sonnet |
| Content Strategist | Copywriting, tutorials, launch communications | inherit |
| Observer | Background logging for tutorial generation | haiku |

## Skills (SOPs)

### Product Lifecycle
```
/solopreneur:discover  ->  /solopreneur:spec  ->  /solopreneur:backlog  ->  /solopreneur:design  ->  /solopreneur:build  ->  /solopreneur:review  ->  /solopreneur:ship  ->  /solopreneur:release-notes
```

Each skill suggests the next step when it completes.

| Skill | What it does |
|-------|-------------|
| `/solopreneur:discover [idea]` | Research and validate a product idea |
| `/solopreneur:spec [idea or file]` | Write a product requirement document |
| `/solopreneur:backlog [spec or feature]` | Break a spec into prioritized tickets |
| `/solopreneur:design [spec or feature]` | Create UI/UX direction and HTML mockups |
| `/solopreneur:build [spec or feature]` | Generate a Cursor-ready implementation plan |
| `/solopreneur:review [file or "recent"]` | Multi-perspective quality review |
| `/solopreneur:ship` | Deployment checklist and launch prep |
| `/solopreneur:release-notes [audience]` | Audience-targeted announcements |

### Team & Utility
| Skill | What it does |
|-------|-------------|
| `/solopreneur:kickoff [task]` | Launch an agent team for parallel work |
| `/solopreneur:standup` | Generate a daily standup from recent activity |
| `/solopreneur:explain [concept]` | Learn how any Claude Code concept works |
| `/solopreneur:scaffold [role]` | Design and build your own AI org plugin |
| `/solopreneur:write-tutorial` | Turn the observer log into a blog post |

## Claude + Cursor Workflow

This plugin follows a **"Claude thinks, Cursor executes"** pattern:

1. Run `/solopreneur:build` in Claude Code - it generates a step-by-step plan
2. Open the plan file in Cursor Composer
3. Tell Cursor: "Execute this plan step by step"
4. Return to Claude Code - QA validates against acceptance criteria

Plan files are saved to `.solopreneur/plans/` in a format optimized for Cursor Composer.

## Running Evals (Developer Only)

Test your skill prompts with the eval framework. Eval CSVs live alongside each skill (`skills/*/eval.csv`).

```bash
# Dry run - see test cases without executing
bash evals/run-evals.sh --dry

# Run all evals
bash evals/run-evals.sh

# Run evals for a specific skill
bash evals/run-evals.sh discover
```

Override models via env vars: `EVAL_MODEL=opus JUDGE_MODEL=opus bash evals/run-evals.sh`

## Building Your Own AI Org

```bash
/solopreneur:scaffold "I am a [describe what you do]"
```

This interactive wizard will:
1. Interview you about your work and time sinks
2. Propose an org structure with agents, skills, and teams
3. Generate an interactive HTML org chart
4. Create a complete plugin directory you can customize

## File Structure

```
solopreneur/
├── .claude-plugin/plugin.json    # Plugin identity
├── CLAUDE.md                     # Company handbook (shared context)
├── agents/                       # Employee definitions (7 agents)
├── skills/                       # SOPs (12 skills)
├── hooks/hooks.json              # Automated observer logging
├── scripts/                      # Helper scripts
├── evals/                        # Eval runner + rubric grader
└── .solopreneur/                     # Runtime outputs (created during use)
```
