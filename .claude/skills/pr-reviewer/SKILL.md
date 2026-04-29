---
name: pr-reviewer
description: Perform a Devin-style PR review with intent grouping and severity tagging.
---

# PR Reviewer

When the user asks to review a pull request, perform the following steps:

1. Ask the user for the target repository path: "What is the absolute path to the target repository you want me to work on?"
2. Ask for the PR number or branch name.
3. Ask whether to post the review automatically or output it for manual copy-paste.
4. Load the instructions from `core/prompts/pr-reviewer.md` and follow them exactly.
5. Use `core/templates/pr-review-output.md` as the output format.
6. Run the helper script `!python .claude/skills/pr-reviewer/scripts/analyze_diff.py $ARGUMENTS` to get a structured diff summary before analyzing individual files.
7. Produce the review with intent grouping and severity tagging (🔴 Critical, 🟡 Warning, ⚪ Info).
8. If automatic posting was selected, use `gh pr review` to submit.
