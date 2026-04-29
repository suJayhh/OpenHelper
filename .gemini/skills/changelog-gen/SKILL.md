---
name: changelog-gen
description: |
  Generate categorized changelog entries from git history.
  Use when the user asks to update changelog, write release notes,
  or summarize recent commits for a version bump.
parameters:
  target_path:
    type: string
    description: Absolute path to the target repository.
  version_range:
    type: string
    description: Tag, date range, or 'since last tag'.
  output_mode:
    type: string
    description: append or standalone.
  bilingual:
    type: boolean
    description: Whether to produce EN/ZH output.
---

# Changelog Generator

Follow the instructions in `core/prompts/changelog-generator.md`.
Collect commits with `git -C <target_path> log`.
Categorize into Breaking Changes, Features, Bug Fixes, Performance, Documentation, Chores.
