---
name: release-notes
description: Generate audience-targeted release announcements. Specify the audience (customers, internal team, investors, social media) and optionally a version or scope. Use after shipping to announce what was built.
---

# Release Notes: $ARGUMENTS

You are generating release announcements. Parse `$ARGUMENTS` for:
- **Audience**: customers, internal team, engineers, investors, social media (default: customers)
- **Version/Scope**: Optional version number or feature scope

## Process

1. Gather context:
   - Read recent git log for commits and changes
   - Read any specs in `.solopreneur/specs/` relevant to recent work
   - Read any build logs in `.solopreneur/builds/` or plans in `.solopreneur/plans/`
   - Check for existing release notes in `.solopreneur/releases/`

2. Delegate to the `@content-strategist` subagent to generate audience-appropriate content:

   **For customers**:
   - Tone: Exciting, benefit-focused, clear
   - Format: What's New → Why It Matters → How to Use It
   - Focus on user impact, not technical details

   **For internal team / engineers**:
   - Tone: Technical, specific, actionable
   - Format: Changelog with categories (Added, Changed, Fixed, Removed)
   - Include file paths, API changes, migration notes

   **For investors**:
   - Tone: Business impact, growth-oriented
   - Format: Key Metrics Impact → Strategic Significance → What's Next
   - Connect features to revenue, retention, or market positioning

   **For social media**:
   - Tone: Punchy, shareable, hook-driven
   - Format: 3 tweet-length announcements + 1 longer LinkedIn/blog post
   - Include suggested hashtags and CTAs

3. Save to `.solopreneur/releases/{date}-{audience}-{slug}.md` (create the directory if needed).

4. Present the release notes to the CEO for review before publishing.
