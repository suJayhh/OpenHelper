---
name: pr-reviewer
description: |
  Perform a Devin-style PR review with intent grouping and severity tagging.
  Use when the user asks to review a pull request, check code changes,
  or perform a code review on a target repository.
parameters:
  target_path:
    type: string
    description: Absolute path to the target repository.
  pr_or_branch:
    type: string
    description: PR number or branch name to review.
  auto_post:
    type: boolean
    description: Whether to post the review via gh CLI or output for manual copy.
---

# PR Reviewer

Follow the instructions in `core/prompts/pr-reviewer.md`.
Use `core/templates/pr-review-output.md` for formatting.
Run `.kimi/skills/pr-reviewer/scripts/analyze_diff.py` for diff analysis.
Group feedback by intent and tag with 🔴 Critical, 🟡 Warning, or ⚪ Info.
