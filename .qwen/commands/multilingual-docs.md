---
description: Generate bilingual EN/ZH documentation for a target repository.
---

# Multilingual Documentation Generator

## Pre-flight

Ask the user:
1. Target repository absolute path.
2. Which docs to update (README, CONTRIBUTING, API, inline, all).
3. Direct write or preview mode.

## Execution

Load `core/prompts/multilingual-docs.md` and follow its instructions.
Use `core/templates/doc-section-en-zh.md` as the default format.

Run `git diff main...HEAD --name-only` in the target repository to focus updates on changed files when applicable.
