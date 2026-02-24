---
name: spec
description: Write a product specification (PRD) from a validated idea or feature request. Use when the user needs to define requirements, user stories, acceptance criteria, or technical specifications before building.
---

# Product Specification: $ARGUMENTS

You are writing a PRD (Product Requirement Document) for the CEO. If `$ARGUMENTS` is a file path, read that file for context. Otherwise, treat it as the idea description.

## Process

1. If context is insufficient, ask the CEO what they want to build and for whom.

2. Draft a structured PRD with these sections:
   - **Overview**: One-paragraph summary of what we're building and why
   - **User Stories**: 3-7 stories in format: "As a [role], I want [feature], so that [benefit]"
   - **Acceptance Criteria**: For each user story, define Given/When/Then scenarios
   - **Release Phases**: Categorize user stories into phases:
     - **MVP**: Core features needed for the product to be usable at all
     - **P1**: Important features for the next release after MVP
     - **P2**: Nice-to-have features that can wait
     Ask the CEO to confirm the phasing before finalizing.
   - **Technical Requirements**: Stack, integrations, data model, API endpoints
   - **Non-Functional Requirements**: Performance targets, security, scalability
   - **Out of Scope**: Explicitly list what we're NOT building (prevents scope creep)
   - **Open Questions**: Anything that needs CEO input before building

3. Validate with subagents in parallel:
   - Send the `@engineer` subagent to validate **technical feasibility** of each requirement. Flag anything that's overly complex, risky, or needs architectural decisions.
   - Send the `@designer` subagent to suggest **UI/UX considerations** for the user stories. What screens are needed? What user flows?

4. Incorporate subagent feedback into the final PRD.

5. Save to `.solopreneur/specs/{date}-{slug}.md` (create the directory if needed).

6. End with the next step prompt. If the spec has 5+ user stories, suggest breaking it into tickets first:
   ```
   -> Next: Break this into implementable tickets:
      /solopreneur:backlog .solopreneur/specs/{filename}

   Or for smaller specs, go straight to design:
      /solopreneur:design .solopreneur/specs/{filename}
   ```
