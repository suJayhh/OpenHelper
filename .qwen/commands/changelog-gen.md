---
name: changelog-gen
description: Generate categorized changelog entries from git history.
---

# Changelog Generator

## Pre-flight

Ask the user:
1. Target repository absolute path.
2. Version tag or range (e.g., `v1.2.0`, `since last tag`).
3. Append to CHANGELOG.md or standalone output.
4. Bilingual output (yes/no).

## Execution

Load `core/prompts/changelog-generator.md` and follow its instructions.

!{git -C {{target_path}} describe --tags --abbrev=0}
!{git -C {{target_path}} log {{base}}..HEAD --oneline --no-merges}

Categorize and format the changelog entry.
