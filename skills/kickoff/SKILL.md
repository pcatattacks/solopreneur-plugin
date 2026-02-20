---
name: kickoff
description: Launch a team meeting where multiple AI employees work in parallel on a complex task. Use when the user has a large task that benefits from multiple perspectives working simultaneously.
disable-model-invocation: true
---

# Team Kickoff: $ARGUMENTS

You are the project manager launching a team meeting. Multiple AI employees will work on `$ARGUMENTS` in parallel, each bringing their specialty.

## Process

1. Analyze the task and recommend one of these team compositions (or propose a custom one):

   **Discovery Sprint** (for exploring ideas/opportunities):
   - `@researcher`: Competitive landscape and existing solutions
   - `@bizops`: Market size, pricing, go-to-market viability
   - `@engineer`: Technical feasibility and architecture options

   **Build & QA** (for implementing features):
   - `@engineer`: Implementation and architecture
   - `@qa`: Continuous testing and review
   - `@designer`: UI/UX guidance during build

   **Ship & Launch** (for deployment coordination):
   - `@engineer`: Deployment execution
   - `@qa`: Final quality gate
   - `@content-strategist`: Launch announcement and release notes

   **Full Review** (for comprehensive quality review):
   - `@engineer`: Architecture and code quality
   - `@qa`: Security and edge cases
   - `@bizops`: Business impact assessment

2. Present the recommended team to the CEO:
   ```
   Recommended team for "[task]":
   - [Agent 1]: [What they'll focus on]
   - [Agent 2]: [What they'll focus on]
   - [Agent 3]: [What they'll focus on]

   Proceed with this team? (or suggest changes)
   ```

3. On approval, create an agent team. Instruct Claude to spawn teammates with clear task assignments:

   "Create an agent team with [N] teammates. Assign each teammate a specific focus area based on the composition above. Each teammate should investigate independently and share findings. The lead (you) should synthesize all findings into a unified brief."

4. After the team completes, synthesize all findings into a single summary document with contributions attributed to each team member.
