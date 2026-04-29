---
name: pr-reviewer
description: |
  Perform a Devin-style PR review with intent grouping and severity tagging.
  Use when the user asks to review a pull request, check code changes,
  or perform a code review on a target repository.
---

# PR Reviewer

Follow the instructions in `core/prompts/pr-reviewer.md`.
Use `core/templates/pr-review-output.md` for formatting.
Run `.gemini/skills/pr-reviewer/scripts/analyze_diff.py` for diff analysis.
Group feedback by intent and tag with 🔴 Critical, 🟡 Warning, or ⚪ Info.
