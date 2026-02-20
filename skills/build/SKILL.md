---
name: build
description: Plan and execute code implementation for a feature or product. Generates a Cursor-ready plan file. Use when the user is ready to write code or needs an implementation plan from a spec or design.
disable-model-invocation: true
---

# Build: $ARGUMENTS

You are planning the implementation for the CEO. If `$ARGUMENTS` is a file path, read that file for context (likely a spec or design doc). Otherwise, treat it as the feature description.

## Process

1. Delegate to the `@engineer` subagent to create a **Cursor-ready plan file**. The plan must follow this exact format so it can be handed to Cursor Composer for fast execution:

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
   - Include specific enough instructions that Cursor can execute without additional context
   - Add acceptance criteria that the QA agent can later validate against
   - Note any dependencies to install

3. Save the plan to `.solopreneur/plans/build-{feature-slug}.md` (create the directory if needed).

4. Present a summary of the plan to the CEO:
   - Number of steps
   - Files that will be created/modified
   - Any decisions that need CEO input
   - Estimated complexity (Simple / Moderate / Complex)

5. End with the Cursor handoff prompt:
   ```
   -> Next: Take this plan to Cursor Composer for fast execution:
      Open .solopreneur/plans/{filename} in Cursor and tell Composer:
      "Execute this plan step by step"

      When done, come back and run:
      /solopreneur:review
   ```
