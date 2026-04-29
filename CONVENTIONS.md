# Aider Conventions — OpenHand Control Center

This repository is a **Control Center** for AI CLI agent skills. When working here, follow these conventions.

## Cross-Repository Execution

This repo contains skills and prompts, NOT the target codebase. Before doing any work:
1. Ask the user: "What is the absolute path to the target repository you want me to work on?"
2. Prefix ALL file operations and git commands with that path.
   - Use `git -C <TARGET_PATH> ...`
   - Use absolute paths like `<TARGET_PATH>/src/foo.py`

## Skills Overview

Three core skills are available:

1. **PR Reviewer** — `core/prompts/pr-reviewer.md`
   - Devin-style reviews with intent grouping and severity tagging.
   - Run `python .kimi/skills/pr-reviewer/scripts/analyze_diff.py <TARGET_PATH>` first.

2. **Multilingual Docs** — `core/prompts/multilingual-docs.md`
   - Bilingual EN/ZH documentation generation.
   - Use `core/templates/doc-section-en-zh.md` for formatting.

3. **Changelog Generator** — `core/prompts/changelog-generator.md`
   - Categorized changelog entries from git history.

## Severity Tags

When producing review output:
- 🔴 **Critical:** Bugs, security issues, broken builds.
- 🟡 **Warning:** Performance, style, maintainability.
- ⚪ **Info:** Suggestions, praise, questions.

## Todo List Protocol

Always maintain a todo list:
- Initialize at the start of a skill session.
- Update progress as items complete.
- Summarize completed vs. pending at the end.
