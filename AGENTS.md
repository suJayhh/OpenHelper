# OpenHand Control Center — Agent Instructions

You are operating inside the **OpenHand CLI Agent Skills Repository**. This repository is a "Control Center" — it does not contain the target codebase you will work on. Instead, it contains pre-configured skills and prompts that you load, and then you apply them to a user-specified target repository.

## Cross-Repository Execution Model (MANDATORY)

Before performing ANY file operation, `git` command, or `gh` command, you MUST establish the target repository path.

1. If the user has not yet provided a target path, ask:
   - "What is the absolute path to the target repository you want me to work on?"
2. Once you have the path (let's call it `TARGET_PATH`), prefix ALL exploration and git commands with it:
   - Use `git -C <TARGET_PATH> ...` instead of `git ...`
   - Use absolute paths like `<TARGET_PATH>/src/foo.py` for all file reads and writes.
   - Never assume the current working directory is the target repo.

## AskUserQuestion Interactivity Module

When a skill is triggered, begin with this diagnostic questionnaire:
1. "What is the absolute path to the target repository you want me to work on?"
2. "Which chore would you like me to perform today? (e.g., PR Review, Update Docs, Generate Changelog)"
3. "Would you like to commit or share your changes yourself, or should I automatically commit/comment on your behalf?"

Capture the answers and proceed accordingly.

## To-Do List Protocol

Every skill session MUST use a todo list:
- **Initialization:** Generate a checklist of required sub-tasks before starting work.
- **Execution:** Update the user on your progress through the checklist as you complete items.
- **Completion:** Provide a final summary of completed tasks vs. pending items.

## Severity Tag Conventions

When producing review output or structured feedback, use these visual severity tags:
- 🔴 **Critical (Red):** Bugs, security issues, data loss risks, or broken builds.
- 🟡 **Warning (Yellow):** Style issues, performance concerns, or maintainability problems.
- ⚪ **Info (Gray):** Suggestions, informational comments, or minor enhancements.

## Skill Discovery

Kimi skills are located in `.kimi/skills/`. Reference them by name when the user requests a chore that matches a skill's description.

## Output Standards

- Prefer concise, actionable output.
- Use standard GitHub-flavored Markdown.
- When generating documentation, always produce dual-language blocks (EN / ZH) unless the user explicitly requests a single language.
