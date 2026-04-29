# PR Reviewer

This skill is invoked when the user requests a PR review inside the OpenHand Control Center.

## Instruction Chain

1. Read `AGENTS.md` in the repo root for Control Center rules.
2. Read `core/prompts/pr-reviewer.md` for the full review protocol.
3. Read `core/templates/pr-review-output.md` for the output structure.
4. Execute the AskUserQuestion flow to establish the target repo, PR/branch, and posting preference.
5. Run `python .kimi/skills/pr-reviewer/scripts/analyze_diff.py <TARGET_PATH> [BASE_BRANCH]`.
6. Analyze the diff with intent grouping and severity tagging.
7. Produce the formatted review.
8. Post via `gh pr review` if requested, otherwise output for manual copy.

## Overrides

- Always prefix file and git commands with the target repo path.
- Always use the todo list protocol.
- Prioritize the Devin-style formatting rules over generic review patterns.
