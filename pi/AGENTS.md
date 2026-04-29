# PI CLI Agent Instructions — OpenHand Control Center

You are operating inside the **OpenHand CLI Agent Skills Repository**, a Control Center for automating GitHub chore work.

## Cross-Repository Execution (MANDATORY)

Before performing ANY file operation or git command, ask the user for the target repository absolute path. Prefix all commands with it:
- `git -C <TARGET_PATH> ...`
- Absolute file paths: `<TARGET_PATH>/relative/path`

## Devin-Style Visualization Rules

When producing PR reviews or structured feedback, you MUST use this markdown layout:

1. **Intent Grouping** — Group changes by logical purpose, not alphabetically:
   - Feature Additions
   - Bug Fixes
   - Refactoring
   - Tests
   - Chores / Dependencies
   - Documentation

2. **Severity Tagging** — Tag every feedback item:
   - 🔴 **Critical (Red):** Bugs or security issues.
   - 🟡 **Warning (Yellow):** Style issues or performance concerns.
   - ⚪ **Info (Gray):** Suggestions and informational comments.

3. **Output Template** — Follow `core/templates/pr-review-output.md` for reviews.

## Available Skills

- **PR Reviewer:** Follow `core/prompts/pr-reviewer.md`
- **Multilingual Docs:** Follow `core/prompts/multilingual-docs.md`
- **Changelog Generator:** Follow `core/prompts/changelog-generator.md`

## Todo List Protocol

Every skill session MUST use a todo list:
- Initialize with sub-tasks.
- Update progress.
- Summarize at completion.
