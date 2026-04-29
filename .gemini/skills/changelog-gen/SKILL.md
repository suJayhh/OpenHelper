---
name: changelog-gen
description: |
  Generate categorized changelog entries from git history.
  Use when the user asks to update changelog, write release notes,
  or summarize recent commits for a version bump.
---

# Changelog Generator

Follow the instructions in `core/prompts/changelog-generator.md`.
Collect commits with `git -C <target_path> log`.
Categorize into Breaking Changes, Features, Bug Fixes, Performance, Documentation, Chores.
