---
name: discover
description: Research and validate product ideas, market opportunities, or feature concepts. Use when the user wants to explore whether an idea is worth pursuing, needs competitive analysis, or wants to understand a market.
---

# Discovery: $ARGUMENTS

You are running a discovery sprint for the CEO. Your goal is to determine whether this idea is worth pursuing.

## Process

1. If `$ARGUMENTS` is vague or missing, ask clarifying questions before proceeding. Do not generate a full brief from vague input like "something with AI."

2. Delegate research in parallel:
   - Send the `@researcher` subagent to analyze the **competitive landscape**: existing solutions, top 3-5 competitors, their positioning, pricing, strengths, weaknesses, and user sentiment.
   - Send the `@bizops` subagent to assess **business viability**: market size (TAM/SAM/SOM), pricing opportunities, revenue model options, and go-to-market considerations.

3. Synthesize findings into a discovery brief with these sections:
   - **Problem Statement**: What pain point does this solve?
   - **Target Audience**: Who has this pain? How badly?
   - **Competitive Landscape**: Top 3 competitors with comparison table
   - **Market Size Estimate**: TAM/SAM/SOM with assumptions stated
   - **Unique Angle**: What would make our approach different?
   - **Risk Factors**: What could go wrong?
   - **Go/No-Go Recommendation**: Clear recommendation with rationale

4. Save the brief to `.solopreneur/discoveries/{date}-{slug}.md` (create the directory if needed).

5. End with the next step prompt:
   ```
   -> Next: Turn this into a product spec with:
      /solopreneur:spec .solopreneur/discoveries/{filename}

   Or want the team to debate these findings first?
      /solopreneur:kickoff discovery sprint
      (assembles your full team for collaborative discussion — takes longer, deeper analysis)
   ```
