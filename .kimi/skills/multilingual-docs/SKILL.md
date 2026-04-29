---
name: multilingual-docs
description: >
  Generate or update bilingual (English + Mandarin Chinese) documentation
  for a target repository. Use when the user asks to write docs, update
  documentation, translate README, create CONTRIBUTING guides, or produce
  dual-language technical documentation.
  Triggers on: "write docs", "update documentation", "translate to Chinese",
  "bilingual docs", "generate README", "document this repo".
---

# Multilingual Documentation Generator

This skill produces and maintains bilingual EN/ZH documentation for open-source projects.

## Workflow

1. Load and follow the instructions in `core/prompts/multilingual-docs.md`.
2. Use `core/templates/doc-section-en-zh.md` as the default section format.
3. If the target repo path is unknown, ask the user via the AskUserQuestion flow defined in `AGENTS.md`.

## Kimi-Specific Notes

- Use `git -C <TARGET_PATH> ...` to inspect recent changes when updating docs.
- When reading existing docs, load them with absolute paths.
- Before writing large files, offer a preview unless the user explicitly requested direct writes.
- For inline code documentation, read the source files and add docstrings/comments in both languages only if the project already uses bilingual comments; otherwise, use English for code comments and bilingual for markdown docs.
