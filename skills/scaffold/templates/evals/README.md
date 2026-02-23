# Eval Suite

Test your skills with an automated eval system. Each skill can have a `skills/[skill-name]/eval.csv` with test cases. The runner invokes each test, grades the output with an LLM judge, and reports pass/fail.

## Quick Start

```bash
# See what tests exist (no LLM calls, no cost)
bash evals/run-evals.sh --dry

# Run evals for a specific skill
bash evals/run-evals.sh [skill-name]

# Run all evals
bash evals/run-evals.sh
```

## How It Works

1. The runner discovers all `skills/*/eval.csv` files
2. For each test case, it invokes `claude --print` with the test prompt
3. An LLM judge grades the output against expected behaviors using `evals/rubric.md`
4. Results are saved to `.eval-runs/` and a summary prints to terminal
5. Exit code is non-zero if any test fails (CI-friendly)

Runs execute inside a temporary git worktree for safety — your working directory is never modified.

## CSV Format

| Column | Description |
|--------|-------------|
| `id` | Unique test ID (e.g., `explicit-basic`, `negative-unrelated`) |
| `should_trigger` | `true` for positive tests, `false` for negative |
| `prompt` | The exact prompt to send to Claude |
| `expected_behaviors` | Pipe-separated list of things to check |

Example:

```csv
id,should_trigger,prompt,expected_behaviors
explicit-topic,true,"Run /myplugin:brainstorm about sustainable fashion","Generates at least 5 ideas|Includes mix of formats|Ideas are specific to topic"
implicit-stuck,true,"I'm running out of things to write about","Triggers brainstorm workflow|Generates relevant ideas"
negative-write,false,"Write the intro paragraph for my blog post","Does NOT trigger brainstorm|Recognizes this is a writing task"
```

## Writing Good Test Cases

**Positive tests** (`should_trigger=true`):
- **Explicit**: Direct skill invocation (`Run /myplugin:skill ...`)
- **Implicit**: Natural language that should trigger the skill
- **Edge case**: Vague or ambiguous prompts that test skill boundaries

**Negative tests** (`should_trigger=false`):
- Prompts that are clearly in a different domain
- Expected behaviors should describe what the skill should NOT do

**Tips for expected_behaviors**:
- Be specific and countable: "Lists at least 3 competitors" not "Good analysis"
- Each behavior is graded independently — more behaviors = more granular scoring
- Start with 3-5 behaviors per positive test
- For negative tests: "Does NOT trigger [skill]|Recognizes this is a [other task]"

## Environment Variables

```bash
# Override models (default: sonnet for both)
EVAL_MODEL=opus JUDGE_MODEL=opus bash evals/run-evals.sh

# Use a cheaper model for invocation, better model for grading
EVAL_MODEL=haiku JUDGE_MODEL=sonnet bash evals/run-evals.sh
```

## Leveling Up: Hybrid Grading

The included runner uses LLM-as-judge for all grading. This works generically for any skill but costs one LLM call per test for grading.

As you learn what your skills produce, consider adding a **deterministic check layer** for fast, cheap signals:

- Did the skill save a file to the expected directory?
- Did the right subagent get invoked?
- Does the output contain required sections?

Deterministic checks catch obvious regressions instantly (no LLM call needed). Layer them before the rubric grader for a fast-then-thorough pipeline.

For more on this hybrid approach, see: https://developers.openai.com/blog/eval-skills/
