# Solopreneur - Your Virtual AI Company

You're a solopreneur. You have ideas, ambition, and not enough hours in the day. What if you had a full team -- an engineer, designer, QA lead, researcher, business analyst, and content strategist -- available instantly, working in parallel, and remembering every decision you've ever made?

Solopreneur is a [Claude Code plugin](https://docs.anthropic.com/en/docs/claude-code/plugins) that turns Claude into a structured virtual company. Not a chatbot you ask questions to. A company with specialists, workflows, and institutional memory.

## What Makes This Different

**Specialists beat generalists.** A QA agent whose entire job is finding bugs will find more bugs than asking Claude to "also check for errors." Each agent has a dedicated role, methodology, and toolset -- just like a real employee.

**You don't need to know what to do next.** Every skill suggests the next step when it finishes. Discover an idea, and it suggests writing a spec. Write a spec, and it suggests creating a backlog. The workflow guides you from idea to shipped product.

**Two build modes.** Generate a step-by-step plan and hand it to any coding agent (Cursor, Windsurf, Cline, Aider, or anything else), or have Claude build it directly. You choose per feature.

**Your decisions are remembered.** Every choice you make -- what you picked, what you rejected, and why -- is captured in a decision journal. Later, turn that journal into a publishable blog post, tutorial, or case study of your building journey.

**Parallel execution.** Sprint mode builds multiple features simultaneously, each in an isolated branch, with integrated QA review when they're done.

**Design your own.** Don't like the default team? Run `/solopreneur:scaffold` and design your own AI org from scratch -- custom agents, custom workflows, custom everything.

## Quick Start

### Install the plugin

In Claude Code (CLI or IDE extension), run:

```
/plugin marketplace add pcatattacks/solopreneur-plugin
/plugin install solopreneur@solopreneur
```

The first command registers the marketplace. The second installs the plugin. You'll be asked to choose a scope (user, project, or local).

### Or clone and use from source

```bash
git clone https://github.com/pcatattacks/solopreneur-plugin.git
cd solopreneur-plugin
claude --plugin-dir .
```

### First command

```
/solopreneur:help
```

This opens an interactive org chart of your AI team and shows you where to start based on your project's current state.

## How It Works

### The Product Lifecycle

Solopreneur follows a structured pipeline from idea to shipped product. Each step feeds into the next:

```
/discover  -->  /spec  -->  /backlog  -->  /design  -->  /build  -->  /review  -->  /ship  -->  /release-notes
```

Here's what that looks like in practice:

1. **Discover** -- You have an idea. Your researcher and business analyst investigate the market, competitors, and viability.
2. **Spec** -- The idea has legs. Your team writes a product requirements document with technical feasibility checks.
3. **Backlog** -- The spec is broken into prioritized, dependency-tracked tickets with acceptance criteria.
4. **Design** -- Your designer creates user flows and interactive HTML mockups with DaisyUI + Tailwind.
5. **Build** -- Pick "plan only" (for Cursor/Windsurf/etc.) or "build directly" (Claude writes the code). Either way, a plan file is saved for reference.
6. **Review** -- Your engineer, QA, and designer review what was built from their respective angles.
7. **Ship** -- Quality gate, deployment setup, and pre-launch checklist. Your QA agent runs final checks.
8. **Release Notes** -- Audience-targeted announcements: Twitter, blog, changelog, investor update -- you name it.

You don't have to follow the pipeline linearly. Skip steps, jump ahead, or start wherever makes sense.

### Alternate Paths

- **Sprint** -- Have multiple tickets ready? Sprint mode builds them in parallel, each in an isolated branch, with QA review built in.
- **Kickoff** -- Need your agents to debate an idea? Run a team meeting where agents challenge each other's assumptions in real time.

### Two Build Modes Explained

When you run `/solopreneur:build`, you're asked how you want to proceed:

**Plan only:** Claude's engineer creates a detailed, step-by-step implementation plan. You take that plan to your preferred coding agent (Cursor, Windsurf, Cline, Aider, or any tool that can follow instructions). When the code is written, come back and Claude's QA agent validates it against the acceptance criteria.

**Build directly:** Claude's engineer creates the plan for reference, then writes the code itself -- installing dependencies, creating files, the whole thing. Progress is reported after each step.

Plan files are saved to `.solopreneur/plans/` (or co-located with tickets in `.solopreneur/backlog/`).

## Your AI Team

| Employee | Role | Model |
|----------|------|-------|
| **Engineer** | Architecture, implementation, debugging, code review | opus (inherited) |
| **Designer** | UI/UX, HTML mockups, user flows, design systems, accessibility | opus (inherited) |
| **BizOps** | Market analysis, pricing strategy, go-to-market, unit economics | opus (inherited) |
| **QA** | Testing, bug hunting, security review, edge case analysis | sonnet |
| **Researcher** | Competitive analysis, market research, trend identification | sonnet |
| **Content Strategist** | Copywriting, tutorials, launch communications, documentation | opus (inherited) |

Agents that say "opus (inherited)" use whatever model you're running Claude Code with. QA and Researcher use Sonnet for cost efficiency -- they handle high-volume, structured tasks where speed matters more than deep reasoning.

## Skills Reference

### Product Lifecycle

Each step suggests the next when it completes.

| Skill | What it does | Example |
|-------|-------------|---------|
| `/solopreneur:discover` | Research and validate a product idea | `/solopreneur:discover meal planning app for busy parents` |
| `/solopreneur:spec` | Write a product requirements document | `/solopreneur:spec .solopreneur/discoveries/meal-planner.md` |
| `/solopreneur:backlog` | Break a spec into prioritized, dependency-tracked tickets | `/solopreneur:backlog .solopreneur/specs/meal-planner.md` |
| `/solopreneur:design` | Create UI/UX direction and interactive HTML mockups | `/solopreneur:design meal planner dashboard` |
| `/solopreneur:build` | Plan for another agent or build directly with Claude | `/solopreneur:build .solopreneur/backlog/meal-planner/MVP-001.md` |
| `/solopreneur:review` | Multi-perspective quality review (engineer + QA + designer) | `/solopreneur:review recent` |
| `/solopreneur:ship` | Quality gate, pre-launch checklist, and deployment | `/solopreneur:ship` |
| `/solopreneur:release-notes` | Audience-targeted release announcements | `/solopreneur:release-notes for twitter` |

### Team & Utility

| Skill | What it does | Example |
|-------|-------------|---------|
| `/solopreneur:kickoff` | Run a collaborative team meeting with multiple agents | `/solopreneur:kickoff discovery sprint on AI tutoring app` |
| `/solopreneur:sprint` | Build multiple backlog tickets in parallel with integrated QA | `/solopreneur:sprint` |
| `/solopreneur:standup` | Generate a daily standup summary from recent activity | `/solopreneur:standup` |
| `/solopreneur:story` | Turn your building journey into a publishable narrative | `/solopreneur:story blog post` |
| `/solopreneur:scaffold` | Design and build your own AI org from scratch | `/solopreneur:scaffold "I am a freelance designer"` |
| `/solopreneur:help` | See your team, check project status, learn what to do next | `/solopreneur:help skills` |

### Pre-built Team Meetings

These are named teams you can use with `/solopreneur:kickoff`:

| Team | Members | When to use |
|------|---------|-------------|
| **Discovery Sprint** | Researcher + BizOps + Engineer | Deep exploration of a new idea, where agents challenge each other |
| **Build & QA** | Engineer + QA + Designer | Code review with competing hypotheses, implementation trade-offs |
| **Ship & Launch** | Engineer + QA + Content Strategist | Launch coordination: deployment, known issues, messaging |

You can also assemble ad-hoc teams: `/solopreneur:kickoff @engineer @designer on responsive layout approach`

## The Observer: Your Building Journal

Every product has a story. Solopreneur captures yours automatically.

### What it captures

The observer logs your *decisions* -- what you chose, what you rejected, and why. It does not log code changes (git handles that). It captures the human side of building: the reasoning, the pivots, the preferences.

Examples of what gets logged:
- "The CEO chose a flat pricing model over tiered pricing because they want to keep the landing page simple"
- "The CEO rejected the dashboard design -- too cluttered, wants a single-focus view instead"
- "Pivoted from React to vanilla JS -- the CEO wants zero build step for v1"

### How it works

**Automatic:** When your AI team asks you a question and you answer, a hook automatically logs your decision to `.solopreneur/observer-log.md`. You don't have to do anything.

**Manual:** When you explain reasoning ("I picked X because..."), reject an approach ("Let's not do Y"), or pivot direction ("Actually, let's switch to..."), your AI team adds an entry. It will briefly tell you what it's logging and why.

### Why it matters

Run `/solopreneur:story` and the content strategist synthesizes your observer log, git history, and project artifacts into a publishable narrative. Choose from:

- **Tutorial** -- Step-by-step guide others can follow
- **Case study** -- Before/after transformation with outcomes
- **Blog post** -- Your journey with pivots and lessons learned
- **Launch story** -- Product announcement framed as the founder's story

Your actual words and decisions are what make the story authentic -- not generic AI-generated content.

### Where it lives

```
.solopreneur/
  observer-log.md           # Recent entries
  observer-archives/        # Rotated monthly for older entries
```

## MCP Server Setup

This plugin includes two MCP servers (via `.mcp.json`) that work out of the box:

| Server | What it does | Setup needed |
|--------|-------------|-------------|
| **Context7** | Up-to-date library and framework documentation for your agents | None -- works automatically |
| **Chrome DevTools** | Inspect DOM, take screenshots, debug layouts in an isolated browser | None -- needs a Chromium browser open |

### Optional: Claude Chrome Extension

For visual QA, testing user flows, and working with authenticated web apps, set up the Claude Chrome Extension. Run `/chrome` inside Claude Code and it will walk you through installation.

Once connected, your QA agent can validate user flows by clicking through the app, taking screenshots, and checking for errors -- all in your real browser with your login sessions. Skills like `/sprint` and `/review` automatically detect and use it when available.

The first time a skill needs browser testing, it will ask if you want to set this up. You can say yes, skip for now (use DevTools only), or "don't ask again."

### GitHub Integration

For creating repos, managing PRs, and pushing code, the plugin uses the `gh` CLI. Claude handles all git operations for you -- just say "share this on GitHub" or "push my work" and it will walk you through setup if needed.

You don't need to know git. Claude creates checkpoints automatically after each milestone, explains what it's saving in plain language, and can undo changes if you ask.

## Build Your Own AI Org

```
/solopreneur:scaffold "I am a [describe what you do]"
```

This interactive wizard will:

1. **Interview you** about your work, time sinks, and what your dream AI team looks like
2. **Propose an org structure** with custom agents, skills, workflows, and team meetings
3. **Generate an interactive HTML org chart** so you can visualize your team
4. **Create a complete plugin directory** with all the files, ready to use or share

The scaffold adapts to your technical level -- developers get technical details, non-technical users get plain-language explanations.

You can scaffold for personal use (just the config files) or for sharing (full plugin with marketplace config so others can install it).

## Running Evals (Developer)

Test skill prompts with the built-in eval framework. Eval CSVs live alongside each skill (`skills/*/eval.csv`).

```bash
# Dry run -- see test cases without executing
bash evals/run-evals.sh --dry

# Run all evals
bash evals/run-evals.sh

# Run evals for a specific skill
bash evals/run-evals.sh discover

# Run all skills in parallel (faster for full suite)
bash evals/run-evals.sh --parallel

# Parallel + fast mode
bash evals/run-evals.sh --parallel --eval-model haiku --judge-model haiku
```

Override models via environment variables or CLI flags:

```bash
EVAL_MODEL=opus JUDGE_MODEL=opus bash evals/run-evals.sh
bash evals/run-evals.sh --eval-model haiku --judge-model haiku
```

## File Structure

```
solopreneur-plugin/
├── .claude-plugin/plugin.json    # Plugin identity and metadata
├── CLAUDE.md                     # Company handbook (shared context for all agents)
├── agents/                       # Employee definitions (6 agents)
│   ├── engineer.md
│   ├── designer.md
│   ├── bizops.md
│   ├── qa.md
│   ├── researcher.md
│   └── content-strategist.md
├── skills/                       # Workflows and SOPs (16 skills)
│   ├── discover/
│   ├── spec/
│   ├── backlog/
│   ├── design/
│   ├── build/
│   ├── review/
│   ├── ship/
│   ├── release-notes/
│   ├── kickoff/
│   ├── sprint/
│   ├── standup/
│   ├── story/
│   ├── scaffold/
│   ├── help/
│   ├── conventions/              # Shared reference (output formats, ticket schema)
│   └── design-system/            # Shared reference (DaisyUI + Tailwind specs)
├── hooks/hooks.json              # Automated decision capture
├── scripts/                      # Helper scripts (observer logging, org chart viz)
├── evals/                        # Eval runner and rubric grader
├── settings.json                 # Agent team configuration
└── .solopreneur/                 # Runtime outputs (created during use)
    ├── discoveries/              # Discovery briefs
    ├── specs/                    # Product requirement documents
    ├── backlog/                  # Prioritized tickets (per project)
    ├── designs/                  # Design direction and HTML mockups
    ├── plans/                    # Implementation plans
    ├── releases/                 # Release notes
    ├── standups/                 # Standup summaries
    ├── stories/                  # Generated narratives
    ├── observer-log.md           # Decision journal (recent entries)
    └── observer-archives/        # Rotated monthly archives
```

## License

MIT
