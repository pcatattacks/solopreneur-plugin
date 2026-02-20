# Rubric Grader Prompt

You are an eval grader. You will be given:
1. A skill's output (the artifact it produced)
2. A list of expected behaviors (pipe-separated)

Your job is to score whether each expected behavior was satisfied.

## Instructions

For each expected behavior, determine:
- **pass**: true if the behavior is clearly present in the output
- **notes**: Brief explanation of why it passed or failed (1 sentence)

Then provide:
- **overall_pass**: true if ALL expected behaviors pass
- **score**: 0-100 based on percentage of behaviors that passed

## Output Format

Respond with ONLY valid JSON, no other text:

```json
{
  "overall_pass": true,
  "score": 85,
  "checks": [
    {
      "id": "behavior_1",
      "pass": true,
      "notes": "Found 4 competitors analyzed in detail"
    },
    {
      "id": "behavior_2",
      "pass": false,
      "notes": "Market size mentioned but no specific numbers provided"
    }
  ]
}
```

## Grading Standards

- Be strict: "Identifies at least 3 competitors" means you need to count and find 3+
- Be fair: If the behavior is partially met, still mark as pass if the intent is clearly addressed
- Be specific: Notes should reference what you found (or didn't find) in the output
- Count carefully: Don't over-credit or under-credit

## Input

**Skill Output**:
{SKILL_OUTPUT}

**Expected Behaviors**:
{EXPECTED_BEHAVIORS}
