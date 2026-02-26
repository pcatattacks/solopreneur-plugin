---
name: story
description: Synthesize your project journey into a publishable narrative — tutorial, case study, blog post, or launch story. Pulls from git history, artifacts, and your decision log. Use when you want to write about how you built something.
disable-model-invocation: true
---

# Story: $ARGUMENTS

You are synthesizing the CEO's project journey into a publishable narrative.

## Format Selection

If `$ARGUMENTS` specifies a format, use it:
- **tutorial** — Step-by-step guide someone can follow to reproduce the work
- **case study** — Before/after transformation with metrics and outcomes
- **blog post** — Narrative about the journey, emphasizing pivots and decisions
- **launch story** — Product announcement framed as the founder's story

If no format is specified, infer from the content:
- Heavy on technical steps with clear sequence → **tutorial**
- Clear before/after with measurable outcomes → **case study**
- Interesting pivots, rejected ideas, or lessons learned → **blog post**
- Product is ready to ship or just shipped → **launch story**

If `$ARGUMENTS` provides a title, topic, or focus area, use it to narrow scope.

## Source Material

Gather material from three sources (in order of storytelling value):

### 1. Decision Log (CEO's voice — most valuable)
Read `.solopreneur/observer-log.md`. These entries capture the CEO's actual decisions — what they chose, what options they rejected, and why. This is the raw material that makes a story authentic. If the log is sparse or empty, that's fine — the other sources compensate.

### 2. Git History (timeline + milestones)
```bash
git log --oneline --stat
```
Commit messages show what was accomplished and when. The `--stat` output shows scope (which files, how much changed). Use this to build the narrative timeline and identify milestones.

### 3. Artifacts (substance)
Read files from `.solopreneur/` directories:
- `discoveries/` — What ideas were explored, what was validated
- `specs/` — What was planned, what requirements were set
- `designs/` — What the UX looks like, what design decisions were made
- `plans/` — Implementation plans and what was built
- `releases/` — What was shipped

These provide the concrete details that give the story substance.

## Process

1. **Gather sources** — Read the decision log, run git log, scan `.solopreneur/` for artifacts. Note what's available and what's sparse.

2. **Identify the arc** — Every project has a story: starting point → challenges → decisions → outcome. Map the material to this arc. The CEO's decisions (from the observer log) are the most compelling parts.

3. **Select format** — Choose based on `$ARGUMENTS` or infer from content (see above). Tell the CEO which format you're using and why.

4. **Delegate to `@content-strategist`** with the gathered material and the format-specific template below.

5. **Save** to `.solopreneur/stories/{date}-{slug}.md` (create the directory if needed).

6. **Present** to the CEO for review. Note where they should add real screenshots or personal anecdotes.

## Format Templates

Pass the appropriate template to `@content-strategist`:

### Tutorial
```markdown
# [Title]

## What We're Building
[Context — what and why, 2-3 paragraphs]

## Prerequisites
- [Tools, knowledge, setup]

## Step N: [Description]
**What we did**: [Action]
**Why**: [Rationale — pull from decision log entries]
**Code/Commands**:
...
**Result**: [What happened]

[IMAGE: description of what to screenshot]

## Key Takeaways
- [3-5 lessons from the process]
```

### Case Study
```markdown
# [Title]

## The Problem
[Starting situation — what wasn't working]

## The Approach
[Strategy chosen and alternatives considered]

## What We Built
[Solution overview with key decisions]

## Results
[Outcomes, metrics if available, before/after]

## Lessons Learned
- [What worked, what didn't, what we'd do differently]
```

### Blog Post
```markdown
# [Title]

[Hook — the most interesting moment, decision, or surprise]

## How It Started
[Origin — the idea, the motivation]

## The Journey
[Narrative of key decisions, pivots, and surprises. Use the CEO's actual words from the decision log where possible.]

## What I Learned
[Reflections and takeaways]

## What's Next
[Where the project goes from here]
```

### Launch Story
```markdown
# [Title]

## Why I Built This
[Personal motivation — what problem the CEO wanted to solve]

## How It Works
[Product overview — clear, benefit-focused]

## The Building Process
[Brief journey highlights — most interesting decisions or challenges]

## Try It
[CTA — how to use it, where to find it]
```

## Content Strategist Guidance

Tell the `@content-strategist`:
- Write in the CEO's voice (first person)
- Decision log entries are gold — weave the CEO's actual choices and reasoning into the narrative
- Git history provides the timeline, but don't list every commit — pick milestones
- Insert `[IMAGE: description]` placeholders where visuals would help
- Keep tone conversational and authentic — this is a founder telling their story, not a technical manual
