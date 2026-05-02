# Solopreneur - Your Virtual AI Company

[![Mentioned in awesome-claude-code-workflows](https://awesome.re/mentioned-badge.svg)](https://github.com/ithiria894/awesome-claude-code-workflows)

You're a solopreneur. You have ideas, ambition, and not enough hours in the day. Solopreneur gives your coding agent a structured virtual company: an engineer, designer, QA lead, researcher, business analyst, and content strategist working from shared workflows and decision memory.

Solopreneur works as a Claude Code plugin and as a Codex plugin. Both platforms use the same root `skills/`, `agents/`, `hooks/`, and `scripts/` directories; there is no duplicated Codex-only skill tree. The Codex marketplace catalog at `.agents/plugins/marketplace.json` points back to the repository root.

## What Makes This Different

**Specialists beat generalists.** A QA agent whose entire job is finding bugs will find more bugs than asking a general assistant to also check for errors. Each role has a dedicated methodology and toolset.

**You don't need to know what to do next.** Every skill suggests the next step when it finishes. Discover an idea, write a spec, create a backlog, design, build, review, ship, and turn the journey into a story.

**Two build modes.** Generate a step-by-step plan for any coding agent, or have the current agent runner build directly. You choose per feature.

**Your decisions are remembered.** Every choice you make, what you rejected, and why can be captured in a decision journal. Later, turn that journal into a publishable blog post, tutorial, or case study.

**Parallel execution.** Sprint mode builds multiple features simultaneously, each in an isolated branch or worktree, with integrated QA review.

**Design your own.** Run the scaffold skill and design your own AI org from scratch: custom roles, custom workflows, and custom onboarding.

## Quick Start

### Install in Claude Code

In Claude Code, run:

```text
/plugin marketplace add pcatattacks/solopreneur-plugin
/plugin install solopreneur@solopreneur
```

Claude Code will ask you to choose a scope such as user, project, or local.

To use from a local checkout:

```bash
git clone https://github.com/pcatattacks/solopreneur-plugin.git
cd solopreneur-plugin
claude --plugin-dir .
```

Start with:

```text
/solopreneur:help
```

### Install in Codex

Codex reads the root `.codex-plugin/plugin.json` and the shared `skills/` directory.
Normal users do not need to clone the repository first:

```bash
codex plugin marketplace add pcatattacks/solopreneur-plugin
```

Then enable or install `solopreneur` from Codex. For local development:

```bash
git clone https://github.com/pcatattacks/solopreneur-plugin.git
codex plugin marketplace add /absolute/path/to/solopreneur-plugin
```

If your Codex build does not support local plugin marketplaces, use native skill discovery:

```bash
git clone https://github.com/pcatattacks/solopreneur-plugin.git ~/.codex/solopreneur-plugin
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s ~/.codex/solopreneur-plugin/skills "${CODEX_HOME:-$HOME/.codex}/skills/solopreneur"
```

Restart Codex, then ask:

```text
Show me what my Solopreneur team can do.
```

See [docs/codex.md](docs/codex.md) for scope verification, troubleshooting, and eval details.

### Scope and Install Verification

For each scope you use, verify from a fresh session:

1. Start Codex or Claude Code in the intended scope.
2. Ask for Solopreneur help.
3. Confirm Solopreneur skills are available.
4. Start a session outside that scope and confirm availability matches what you intended.

Codex scope behavior depends on the Codex version and UI surface. If your Codex build does not expose separate project/local plugin scope controls, use local marketplace registration for development and the `${CODEX_HOME:-$HOME/.codex}/skills/solopreneur` symlink for user-level native skill discovery.

## How It Works

### Product Lifecycle

Solopreneur follows a structured pipeline from idea to shipped product:

```text
discover -> spec -> backlog -> design -> build -> review -> ship -> release-notes
```

1. **Discover** -- Research and validate an idea.
2. **Spec** -- Turn the idea into a product requirements document.
3. **Backlog** -- Break the spec into prioritized, dependency-tracked tickets.
4. **Design** -- Create user flows and interactive HTML mockups with DaisyUI + Tailwind.
5. **Build** -- Pick plan-only mode or direct implementation.
6. **Review** -- Engineer, QA, and designer perspectives check the work.
7. **Ship** -- Run a quality gate, deployment setup, and launch checklist.
8. **Release Notes** -- Generate audience-targeted announcements.

You can skip steps, jump ahead, or start wherever makes sense.

### Build Modes

**Plan only:** the engineering role creates a detailed implementation plan saved under `.solopreneur/plans/`. You can take that plan to Cursor, Windsurf, Cline, Aider, Codex, Claude Code, or another coding agent.

**Build directly:** the engineering role creates the plan for reference, then the current agent runner writes the code, installs dependencies when appropriate, creates files, and reports progress.

## Your AI Team

| Employee | Role |
|----------|------|
| **Engineer** | Architecture, implementation, debugging, code review |
| **Designer** | UI/UX, HTML mockups, user flows, design systems, accessibility |
| **BizOps** | Market analysis, pricing strategy, go-to-market, unit economics |
| **QA** | Testing, bug hunting, security review, edge case analysis |
| **Researcher** | Competitive analysis, market research, trend identification |
| **Content Strategist** | Copywriting, tutorials, launch communications, documentation |

Agent runners differ in how they expose named subagents. When named agents are unavailable, use the role descriptions in `agents/*.md` as delegation prompts.

## Skills Reference

Claude Code examples use slash commands. In Codex, invoke the same skills by name or natural language, for example: "Run the Solopreneur discover skill for a meal planning app."

| Skill | What it does | Claude Code example |
|-------|-------------|---------------------|
| `discover` | Research and validate a product idea | `/solopreneur:discover meal planning app for busy parents` |
| `spec` | Write a product requirements document | `/solopreneur:spec .solopreneur/discoveries/meal-planner.md` |
| `backlog` | Break a spec into prioritized tickets | `/solopreneur:backlog .solopreneur/specs/meal-planner.md` |
| `design` | Create UI/UX direction and HTML mockups | `/solopreneur:design meal planner dashboard` |
| `build` | Plan or build a feature | `/solopreneur:build .solopreneur/backlog/meal-planner/MVP-001.md` |
| `review` | Multi-perspective quality review | `/solopreneur:review recent` |
| `ship` | Quality gate, pre-launch checklist, deployment | `/solopreneur:ship` |
| `release-notes` | Audience-targeted release announcements | `/solopreneur:release-notes for twitter` |
| `kickoff` | Run a collaborative team meeting | `/solopreneur:kickoff discovery sprint on AI tutoring app` |
| `sprint` | Build multiple backlog tickets in parallel | `/solopreneur:sprint` |
| `standup` | Generate a daily standup summary | `/solopreneur:standup` |
| `story` | Turn your building journey into a narrative | `/solopreneur:story blog post` |
| `scaffold` | Design your own AI org from scratch | `/solopreneur:scaffold "I am a freelance designer"` |
| `help` | See your team and find what to do next | `/solopreneur:help skills` |

## The Observer

The observer logs decisions: what you chose, what you rejected, and why. It does not log code changes. Git handles the "what"; the observer captures the human reasoning.

Runtime files live under:

```text
.solopreneur/
  observer-log.md
  observer-archives/
```

Claude Code can use the included hook to capture structured questions automatically. Other agent runners should append manual observer entries when the user explains a decision, rejects an approach, or pivots direction.

## MCP and Browser Tools

The root `.mcp.json` includes:

| Server | What it does |
|--------|-------------|
| **Context7** | Current library and framework documentation |
| **Chrome DevTools** | DOM inspection, screenshots, and layout debugging in an isolated browser profile |

Some runners expose additional browser integrations. Claude Code users can optionally use the Claude Chrome Extension for authenticated browser QA. Codex users should use the browser tools available in their Codex environment.

## GitHub Integration

For creating repos, managing PRs, and pushing code, Solopreneur uses the `gh` CLI when available. The agent should walk non-technical users through setup and explain checkpoints in plain language.

## Build Your Own AI Org

```text
/solopreneur:scaffold "I am a [describe what you do]"
```

The scaffold wizard interviews you, proposes an org structure, generates an interactive HTML org chart, and creates plugin files ready to use or share.

## Running Evals

Eval CSVs live alongside each skill in `skills/*/eval.csv`.

```bash
# Dry run -- see test cases without executing
bash evals/run-evals.sh --dry

# Run all Claude-runner evals
bash evals/run-evals.sh

# Run evals for one skill
bash evals/run-evals.sh discover

# Codex dry run
bash evals/run-evals.sh --runner codex --dry

# Codex full run
bash evals/run-evals.sh --runner codex

# Parallel Claude-runner evals
bash evals/run-evals.sh --parallel
```

Override models via environment variables or CLI flags:

```bash
EVAL_MODEL=opus JUDGE_MODEL=opus bash evals/run-evals.sh
bash evals/run-evals.sh --eval-model haiku --judge-model haiku
```

## Packaging Checks

```bash
python3 scripts/validate-plugin-packaging.py
scripts/verify-codex-install.sh
bash evals/run-evals.sh --dry
bash evals/run-evals.sh --runner codex --dry
```

## File Structure

```text
solopreneur-plugin/
├── .claude-plugin/                # Claude Code plugin metadata
├── .codex-plugin/                 # Codex plugin metadata
├── .codex/INSTALL.md              # Codex install guide
├── AGENTS.md -> CLAUDE.md         # Codex entrypoint shares the same handbook
├── CLAUDE.md                      # Shared agent handbook
├── agents/                        # Employee definitions
├── skills/                        # Workflows and SOPs
├── hooks/                         # Hook config for runners that support it
├── scripts/                       # Helper and validation scripts
├── evals/                         # Eval runner and rubric grader
├── docs/                          # Website and platform docs
├── .mcp.json                      # MCP server config
└── .solopreneur/                  # Runtime outputs, created during use
```

## License

MIT
