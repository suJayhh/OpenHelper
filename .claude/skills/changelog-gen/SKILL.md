---
name: changelog-gen
description: Generate categorized changelog entries from git history.
---

# Changelog Generator

When the user asks to update the changelog or summarize changes, perform the following steps:

1. Ask the user for the target repository path: "What is the absolute path to the target repository you want me to work on?"
2. Ask for the version tag or date range to changelog.
3. Ask whether to append to existing CHANGELOG.md or output standalone.
4. Ask whether to produce bilingual output.
5. Load the instructions from `core/prompts/changelog-generator.md` and follow them exactly.
6. Use `git -C <TARGET_PATH> log` and `git -C <TARGET_PATH> diff` to collect commits and file stats.
7. Categorize entries into: Breaking Changes, Features, Bug Fixes, Performance, Refactoring, Documentation, Chores.
8. Write the formatted entry to the target repo's CHANGELOG.md.
