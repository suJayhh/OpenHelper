---
name: pr-reviewer
description: >
  Perform a high-signal, Devin-style PR review on a target repository.
  Use when the user asks to review a pull request, review code changes,
  analyze a PR, or perform dev chores related to PR review.
  Triggers on phrases like: "review this PR", "PR review", "check my pull request",
  "code review", or "review changes".
---

# PR Reviewer

This skill automates PR reviews with intent grouping and severity tagging.

## Workflow

1. Load and follow the instructions in `core/prompts/pr-reviewer.md`.
2. Use `core/templates/pr-review-output.md` as the output structure.
3. If the target repo path is unknown, ask the user via the AskUserQuestion flow defined in `AGENTS.md`.

## Helper Scripts

- `scripts/analyze_diff.py` — Run this script against the target repo to get a deterministic JSON summary of changed files and line counts. Example:
  ```bash
  python .kimi/skills/pr-reviewer/scripts/analyze_diff.py <TARGET_PATH> [BASE_BRANCH]
  ```
  The script outputs grouped file information that you can use to plan your review before reading individual files.

## Kimi-Specific Notes

- Use `git -C <TARGET_PATH> ...` for all git operations.
- When reading files, use the absolute path `<TARGET_PATH>/relative/path`.
- Before posting via `gh`, confirm the PR number and repo slug with the user.
- Always present a todo list at the start of the review session and update it as you progress.
