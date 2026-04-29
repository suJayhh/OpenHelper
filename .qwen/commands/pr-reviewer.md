---
name: pr-reviewer
description: Perform a Devin-style PR review on a target repository.
---

# PR Reviewer

## Pre-flight

Ask the user:
1. Target repository absolute path.
2. PR number or branch name.
3. Auto-post via `gh` or manual output.

## Execution

Load `core/prompts/pr-reviewer.md` and follow its instructions.
Run the diff analyzer:

!{python .kimi/skills/pr-reviewer/scripts/analyze_diff.py {{target_path}} {{base_branch}}}

Analyze the diff, group by intent, tag severity (🔴 Critical, 🟡 Warning, ⚪ Info).
Format output using `core/templates/pr-review-output.md`.

## Posting

If auto-post is enabled:
!{gh pr review {{pr_number}} --repo {{owner/repo}} --comment --body-file {{review_file}}}
