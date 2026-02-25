---
name: build
description: Plan and execute code implementation for a feature or product. Can generate a plan file for Cursor or build directly with Claude. Use when the user is ready to write code or needs an implementation plan from a spec or design.
disable-model-invocation: true
---

# Build: $ARGUMENTS

You are handling implementation for the CEO. Determine the input type from `$ARGUMENTS`:

- If it's a **ticket file path** (e.g., `.solopreneur/backlog/{dir}/MVP-001.md`), read the ticket for requirements, acceptance criteria, and technical notes. Also read `backlog.md` in the same directory for dependency context — check that all blocking tickets (listed in `depends_on`) have `status: done` or `status: tested` before proceeding. If blockers remain, tell the CEO which tickets need to be completed first and suggest building one of those instead.
- If it's a **design directory** (e.g., `.solopreneur/designs/{date}-{slug}/`), read `design-brief.md` inside it and scan for `.html` mockup files — these contain the visual structure the engineer should implement.
- If it's a **spec file path**, read it for context.
- Otherwise, treat it as the feature description.

## Step 1: Ask how to build

Before doing anything else, ask the CEO:

> **How would you like to build this?**
> 1. **Plan only** — I'll create a plan file you can take to Cursor (or any other coding agent)
> 2. **Build it now** — I'll write the code directly, right here

Wait for their answer before proceeding. If they say "plan", follow the **Plan Path**. If they say "build" (or "now", "do it", "just build it", etc.), follow the **Direct Path**.

## Step 1.5: Branch Setup (ticket builds only)

If building from a ticket file, set up an isolated branch before building:

1. **Check for parallel builds**: Run `git branch` to see if any `ticket/*` branches exist that are not yet merged. If another ticket branch is active (checked out in the current worktree), create a new worktree instead:
   ```
   git worktree add .solopreneur/worktrees/{ID} -b ticket/{ID}
   ```
   Then work inside that worktree directory.

2. **Normal case** (no active ticket branch): Create a branch for this ticket:
   ```
   git checkout -b ticket/{ID}
   ```

3. **Update the ticket file**: Set `status: in-progress` and `branch: ticket/{ID}` in the YAML frontmatter.

4. **Adapt explanation to user's technical level**: If `.solopreneur/preferences.yaml` exists, read it for the CEO's git comfort level. Explain accordingly:
   - Technical: "Creating branch `ticket/MVP-001`"
   - Basic: "I'm creating a separate branch for this ticket"
   - Non-technical: "I'm saving your work in a separate space so it doesn't interfere with other work"

   If preferences don't exist yet, ask the CEO: "Quick question — how comfortable are you with git? (I use it daily / I know the basics / What's git?)" and save their answer to `.solopreneur/preferences.yaml`.

---

## Step 1.75: Deployment Strategy (first build only)

Check if `.solopreneur/preferences.yaml` has a `deployment` key. If yes, skip this step entirely.

If no deployment strategy exists yet, ask the CEO:

> **Where should this run when it's ready?**
> The engineer will set up deployment based on your tech stack. Common options:
> 1. **Vercel** — Best for Next.js, React, static sites (free tier available)
> 2. **Netlify** — Similar to Vercel, good for static sites and serverless
> 3. **GitHub Pages** — Free, simple, static sites only
> 4. **I'll figure it out later** — Skip for now, we'll set it up when you're ready to ship
>
> Not sure? The engineer can recommend one based on what we're building.

If the CEO picks a platform or asks for a recommendation:
1. Delegate to `@engineer` to configure the project for that platform:
   - Install the platform CLI if needed (e.g., `npm i -g vercel`)
   - Create platform config files (e.g., `vercel.json`, `netlify.toml`)
   - If an MCP server exists for the platform (e.g., Vercel), add it to `.mcp.json`
   - Link the project to the platform (`vercel link`, etc.)
2. Save the deployment strategy to `.solopreneur/preferences.yaml`:
   ```yaml
   deployment:
     platform: vercel  # or netlify, github-pages, fly, railway, custom, none
     configured: true
     notes: "Next.js app on Vercel, linked via CLI"
     rollback: "Run `vercel rollback` or go to vercel.com/[project]/deployments and promote the previous deployment"
   ```

If the CEO picks "I'll figure it out later", save:
```yaml
deployment:
  platform: none
  configured: false
```

This step only runs once. Subsequent `/build` calls skip it because the preference exists.

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

   ## Deployment Notes (if first build)
   **Platform**: [chosen platform]
   **Config created**: [list of config files]
   **Setup status**: [linked/configured/pending]
   ```

2. The engineer should:
   - Break the work into 3-8 sequential steps
   - List all files to create or modify with their paths
   - Include specific enough instructions that another agent can execute without additional context
   - Add acceptance criteria that the QA agent can later validate against
   - Note any dependencies to install

3. Save the plan:
   - If building from a ticket: save co-located as `.solopreneur/backlog/{dir}/{ID}-plan.md`
   - Otherwise: save to `.solopreneur/plans/build-{feature-slug}.md` (create the directory if needed)

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
   - Save the plan: if building from a ticket, co-locate as `.solopreneur/backlog/{dir}/{ID}-plan.md`; otherwise save to `.solopreneur/plans/build-{feature-slug}.md`
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

---

## Ticket Completion (ticket builds only)

After the plan or direct build is complete:

1. **Update the ticket**: Set `status: done` in the YAML frontmatter. Populate the `## Files` section with files created/modified.

2. **Offer to merge**: Ask the CEO:
   > This ticket is built on branch `ticket/{ID}`. Want me to merge it into the main branch?

3. **If yes**: Merge with a descriptive commit:
   ```
   git checkout main && git merge ticket/{ID} --no-ff -m "Merge ticket/{ID}: {title}"
   ```
   If there are merge conflicts:
   - For technical users: show the conflicts and ask how to resolve
   - For non-technical users: attempt auto-resolution; if that fails, explain in plain language: "Two changes touched the same file. Let me show you both versions so you can pick which one to keep."

4. **Clean up**: Delete the ticket branch (`git branch -d ticket/{ID}`). If a worktree was created, remove it (`git worktree remove .solopreneur/worktrees/{ID}`).

5. **Suggest next ticket**: Read `backlog.md`, find tickets that are now unblocked (their `depends_on` tickets are all `done` or `tested`), and suggest:
   ```
   -> Ticket {ID} is done! Next unblocked tickets:
      /solopreneur:build .solopreneur/backlog/{dir}/{NEXT-ID}.md

   Tickets that can be built in parallel: {list}
   ```
