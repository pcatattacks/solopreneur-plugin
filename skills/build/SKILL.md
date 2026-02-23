---
name: build
description: Plan and execute code implementation for a feature or product. Can generate a plan file for Cursor or build directly with Claude. Use when the user is ready to write code or needs an implementation plan from a spec or design.
disable-model-invocation: true
---

# Build: $ARGUMENTS

You are handling implementation for the CEO. If `$ARGUMENTS` is a file path, read that file for context (likely a spec or design doc). If it's a directory path (e.g., `.solopreneur/designs/{date}-{slug}/`), read the `design-brief.md` inside it and scan for `.html` mockup files — these contain the visual structure the engineer should implement. Otherwise, treat it as the feature description.

## Step 1: Ask how to build

Before doing anything else, ask the CEO:

> **How would you like to build this?**
> 1. **Plan only** — I'll create a plan file you can take to Cursor (or any other coding agent)
> 2. **Build it now** — I'll write the code directly, right here

Wait for their answer before proceeding. If they say "plan", follow the **Plan Path**. If they say "build" (or "now", "do it", "just build it", etc.), follow the **Direct Path**.

---

## Plan Path

1. Delegate to the `@engineer` subagent to create a plan file. The plan must follow this exact format:

   ```markdown
   # Plan: [Feature Name]

   ## Context
   [What we're building and why. Reference the source spec/design if applicable.]

   ## Step 1: [Short description]
   **Files**: `path/to/file.ext` (create|modify)
   **Do**: [Clear, specific instructions for what code to write. Include key function signatures, data structures, or logic.]
   **Acceptance**: [Concrete criteria to verify this step is done correctly.]

   ## Step 2: [Short description]
   ...
   ```

2. The engineer should:
   - Break the work into 3-8 sequential steps
   - List all files to create or modify with their paths
   - Include specific enough instructions that another agent can execute without additional context
   - Add acceptance criteria that the QA agent can later validate against
   - Note any dependencies to install

3. Save the plan to `.solopreneur/plans/build-{feature-slug}.md` (create the directory if needed).

4. Present a summary of the plan to the CEO:
   - Number of steps
   - Files that will be created/modified
   - Any decisions that need CEO input
   - Estimated complexity (Simple / Moderate / Complex)

5. End with the handoff prompt:
   ```
   -> Next: Take this plan to your coding agent (Cursor, Windsurf, etc.) for execution:
      Open .solopreneur/plans/{filename} and tell it:
      "Execute this plan step by step"

      When done, come back and run:
      /solopreneur:review
   ```

---

## Direct Path

1. Delegate to the `@engineer` subagent to **plan and execute the implementation directly**. The engineer should:
   - First, create the same structured plan (3-8 steps with files, instructions, and acceptance criteria)
   - Save the plan to `.solopreneur/plans/build-{feature-slug}.md` for reference
   - Then execute each step: create/modify files, install dependencies, write the actual code
   - After each step, briefly report progress to the CEO

2. Once the engineer finishes, present a summary:
   - What was built (files created/modified)
   - Any decisions that were made along the way
   - Anything that needs CEO input or attention

3. End with the review prompt:
   ```
   -> Next: Let's review what was built:
      /solopreneur:review
   ```
