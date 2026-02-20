---
name: review
description: Review code, specifications, or designs for quality, bugs, security, and best practices. Use when the user wants feedback on recent work, a pull request, or any artifact.
---

# Review: $ARGUMENTS

You are conducting a quality review. Determine what type of artifact is being reviewed based on `$ARGUMENTS`:

- If it's a file path ending in code extensions (.ts, .js, .py, etc.) or "recent changes" or a PR → **Code Review**
- If it's a path to a `.solopreneur/specs/` file or mentions "spec" → **Spec Review**
- If it's a path to a `.solopreneur/designs/` file or mentions "design" → **Design Review**
- If it's a path to a `.solopreneur/plans/` file → **Plan Validation** (check completed steps against acceptance criteria)

## Code Review

Delegate in parallel:
- `@engineer`: Architecture review - code structure, patterns, maintainability, performance
- `@qa`: Bug hunting - security vulnerabilities, edge cases, error handling, test coverage

## Spec Review

Delegate in parallel:
- `@bizops`: Business viability - does this make commercial sense? Are requirements prioritized correctly?
- `@engineer`: Technical feasibility - can this be built? Are estimates realistic? Any missing requirements?

## Design Review

Delegate in parallel:
- `@designer`: Usability - is the flow intuitive? Are there accessibility issues?
- `@engineer`: Implementability - can this be built as designed? Any technical constraints?

## Plan Validation (after Cursor execution)

Read the plan file and check git diff or file state:
- For each step with acceptance criteria, delegate to `@qa` to validate
- Update the plan file with checkboxes: `- [x] Step N: ... (validated)` or `- [ ] Step N: ... (FAILED: reason)`

## Output Format

Compile all findings into a structured review:
- **Critical Issues**: Must fix before proceeding
- **Warnings**: Should fix, but not blocking
- **Suggestions**: Nice-to-have improvements
- **Positives**: Things done well (always include at least one)

End with the next step prompt:
```
-> Next: Ready to ship? Run:
   /solopreneur:ship
```
