---
name: kickoff
description: Launch a collaborative team meeting using agent teams. Use when the user wants deep multi-perspective analysis, adversarial review, debugging with competing hypotheses, or any task where agents should debate and converge rather than work independently.
disable-model-invocation: true
---

# Kickoff: $ARGUMENTS

You are the team lead for a collaborative agent team meeting. Unlike skills that delegate to independent subagents, kickoff uses Claude Code's agent teams feature — teammates share a task list, message each other directly, and challenge each other's findings.

## Phase 0 — Team Selection

1. Parse `$ARGUMENTS` to identify the team:
   - **Named team match**: If arguments mention a team name from the "Team Meetings" section in CLAUDE.md (e.g., "Discovery Sprint", "Build & QA", "Ship & Launch"), use that team's members.
   - **Agent mentions**: If arguments include `@agent` references (e.g., `@engineer @qa on [topic]`), assemble an ad-hoc team with those agents.
   - **Topic-based inference**: If arguments describe a task without naming a team, infer the best fit:
     - Research, exploration, idea validation → Discovery Sprint
     - Code review, debugging, architecture → Build & QA
     - Launch prep, deployment, announcements → Ship & Launch
   - **Ambiguous**: Propose your best-fit team and let the CEO confirm or adjust.

2. If `$ARGUMENTS` includes a file path or reference, read it for context to pass to teammates.

3. Present to the CEO via AskUserQuestion:
   ```
   I'll assemble [team name] to work on [topic]:
   - @[agent1]: [their focus for this meeting]
   - @[agent2]: [their focus for this meeting]
   - @[agent3]: [their focus for this meeting]

   They'll collaborate — sharing findings, challenging assumptions, and
   converging on a recommendation.

   Note: This assembles your full team for collaborative discussion —
   takes longer and uses more resources, but produces deeper analysis.
   ```

   Options: "Yes, start the meeting" / "Adjust the team" / "Use [lifecycle skill] instead" (suggest the faster alternative — e.g., `/discover` for research, `/review` for code review)

## Phase 1 — Spawn Agent Team

On CEO approval, create the agent team:

**Teammate setup** — for each team member:

1. Read the agent's role file (`agents/[agent].md`) for their system prompt and capabilities.

2. Write a spawn prompt that includes:
   - The agent's role description and expertise
   - The topic and any file context (spec content, code to review, bug report, etc.)
   - Collaborative instructions: "You are in a team meeting with [other teammates]. Share your findings with them. Challenge assumptions you disagree with. Build on their insights. Your goal is to converge on the best recommendation as a team, not just produce your own independent analysis."

3. Use Sonnet for teammates by default (balances capability and cost).

**Task list** — create a shared task list based on the meeting's purpose. Aim for 5-6 tasks per teammate. Examples:

For a Discovery Sprint:
- Research competitive landscape and existing solutions
- Assess market size, pricing opportunities, and unit economics
- Evaluate technical feasibility and architecture approach
- Identify top risks and potential blockers
- Challenge each other's findings and draft consolidated recommendation

For an adversarial code review:
- Review for security vulnerabilities and data exposure
- Review for performance issues and scalability
- Review for edge cases and error handling
- Challenge each other's findings — debate severity and impact
- Draft prioritized findings with consensus severity ratings

**Monitoring** — while teammates collaborate:
- Wait for all teammates to finish before compiling results (do not start implementing or writing the summary yourself)
- Intervene only if a teammate goes off-topic, appears stuck, or the CEO sends a message
- If a task appears stuck (teammates sometimes fail to mark tasks complete), nudge the teammate

## Phase 2 — Compile & Present

When all teammates have finished:

1. Compile findings into a structured report:

   ```
   ## Kickoff Report: [topic]

   ### Consensus
   [What the team agreed on — the strongest, most defensible conclusions]

   ### Debate Points
   [Where agents disagreed, with each side's reasoning. Highlight which
   argument was stronger and why]

   ### Key Findings
   - **@[agent1]**: [Top insight from their perspective]
   - **@[agent2]**: [Top insight from their perspective]
   - **@[agent3]**: [Top insight from their perspective]

   ### Recommendation
   [The team's collective recommendation — what the CEO should do next]

   ### Dissent
   [If any agent strongly disagrees with the recommendation, note it here
   with their reasoning. The CEO deserves to see minority opinions.]
   ```

2. Clean up the team.

3. Suggest the next step based on what was discussed:
   - Discovery kickoff → `/solopreneur:spec`
   - Code review kickoff → fix issues or `/solopreneur:ship`
   - Debug kickoff → implement the fix
   - Launch kickoff → `/solopreneur:ship`
   - Ad-hoc → suggest the most relevant next action
