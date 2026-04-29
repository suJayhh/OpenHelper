---
name: multilingual-docs
description: |
  Generate or update bilingual (EN + ZH) documentation for a target repository.
  Use when the user asks to write docs, translate README, update CONTRIBUTING,
  or produce dual-language technical documentation.
parameters:
  target_path:
    type: string
    description: Absolute path to the target repository.
  doc_scope:
    type: string
    description: Which docs to update (README, CONTRIBUTING, API, inline, all).
  write_mode:
    type: string
    description: direct or preview.
---

# Multilingual Documentation Generator

Follow the instructions in `core/prompts/multilingual-docs.md`.
Use `core/templates/doc-section-en-zh.md` for section formatting.
Inspect existing docs to match the repo's bilingual conventions.
