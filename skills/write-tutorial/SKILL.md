---
name: write-tutorial
description: Synthesize the observer log into a step-by-step tutorial or blog post documenting the workflow, decisions, and commands used. Use when you want to create content about the process of building something.
disable-model-invocation: true
---

# Write Tutorial: $ARGUMENTS

You are synthesizing the observer log into a publishable tutorial. If `$ARGUMENTS` provides a title or focus area, use it. Otherwise, infer from the log content.

## Process

1. **Read the observer log** at `.solopreneur/observer-log.md`. If it doesn't exist or is empty, tell the user there's nothing to synthesize yet.

2. **Analyze the log** to identify:
   - The narrative arc: What was the starting point? What was built? What was the result?
   - Key decision points: Where were choices made and why?
   - Natural step boundaries: Use SESSION_END markers and category changes to find where "steps" begin and end
   - Commands and code worth highlighting
   - Where screenshots would add value

3. **Delegate to the `@content-strategist` subagent** to transform the analysis into a tutorial with this structure:

   ```markdown
   # [Title]

   ## Introduction
   [What we're building and why - 2-3 paragraphs setting context]

   ## Prerequisites
   - [Tools needed]
   - [Knowledge assumed]
   - [Setup steps]

   ## Step 1: [Description]

   **What we did**: [Action taken]
   **Why**: [Rationale - pull from DECISION log entries]
   **Command/Code**:
   ```
   [The actual command or code from the log]
   ```
   **What happened**: [Result summary]

   [IMAGE: Description of what to screenshot here]

   ## Step 2: [Description]
   ...

   ## Key Takeaways
   - [3-5 lessons learned from the process]

   ## Next Steps
   - [What to explore next]
   ```

4. The content strategist should:
   - Write for someone smart but unfamiliar with the specifics
   - Include every significant command (readers need to be able to follow along)
   - Insert `[IMAGE: description]` placeholders where visuals would help
   - Keep the tone conversational and encouraging
   - Attribute decisions to their rationale (not just "we did X" but "we did X because Y")

5. Save to `.solopreneur/tutorials/{date}-{slug}.md` (create the directory if needed).

6. Present the tutorial to the CEO for review. Suggest specific places where they should add real screenshots.
