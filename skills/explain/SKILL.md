---
name: explain
description: Explain how any Claude Code concept works in beginner-friendly language, with examples from this plugin. Use when you want to understand skills, agents, teams, MCP, hooks, plugins, evals, or the Claude+Cursor workflow.
argument-hint: concept name (skills, agents, hooks, etc.)
---

# Explain: $ARGUMENTS

The user wants to understand a Claude Code concept. Explain it clearly for someone who may not be technical.

## Instructions

1. Identify which concept(s) the user is asking about from `$ARGUMENTS`. Map to one or more of these topics:

   - **CLAUDE.md / Context Management**: How Claude reads project context
   - **Skills**: Reusable workflows invoked with `/skill-name`
   - **Subagents / Agents**: Specialized AI "employees" with focused roles
   - **Agent Teams**: Multiple agents working in parallel
   - **MCP Servers**: External tool access (GitHub, Figma, etc.)
   - **Hooks**: Automated actions triggered by events
   - **Plugins**: Packaged collections of agents, skills, and config
   - **Plugin Registries / Marketplaces**: How to share and install plugins
   - **Evals**: Testing and measuring skill/agent quality
   - **Plan Files**: Cursor-ready implementation plans
   - **Claude + Cursor Workflow**: Using Claude for planning, Cursor for execution

2. For each concept, provide:

   **What it is** (1-2 sentences, no jargon):
   > Plain English explanation of the concept

   **Why it matters**:
   > What problem does this solve? Why would you use it?

   **How it works in this plugin**:
   > Point to the specific file(s) in the Solopreneur plugin that demonstrate this concept. Read and quote relevant sections.

   **Real-world analogy**:
   > Compare to something in a real company (e.g., "Skills are like SOPs - standard procedures your team follows")

   **Try it yourself**:
   > Give a concrete command the user can run right now to see it in action

3. Keep explanations conversational and encouraging. Assume the reader is smart but new to these tools.

4. If the user asks about something not in the list above, do your best to explain it or suggest where to find documentation.
