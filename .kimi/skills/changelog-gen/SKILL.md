---
name: changelog-gen
description: >
  Generate categorized changelog entries from git history for a target repository.
  Use when the user asks to update the changelog, write release notes, summarize
  recent changes, or prepare a version bump.
  Triggers on: "update changelog", "generate changelog", "release notes",
  "what changed since", "summarize commits", "version bump".
---

# Changelog Generator

This skill automates changelog maintenance by parsing git history and categorizing changes.

## Workflow

1. Load and follow the instructions in `core/prompts/changelog-generator.md`.
2. If the target repo path is unknown, ask the user via the AskUserQuestion flow defined in `AGENTS.md`.

## Helper Scripts

- `.kimi/skills/pr-reviewer/scripts/analyze_diff.py` (shared with `pr-reviewer`) — Use this to get a quick summary of changed files and magnitude before categorizing commits.

## Kimi-Specific Notes

- Use `git -C <TARGET_PATH> ...` for all git operations.
- When reading existing changelogs, use absolute paths.
- For bilingual output, mirror the structure of `core/prompts/changelog-generator.md`.
- Prefer appending to the existing `CHANGELOG.md` rather than rewriting the whole file.
