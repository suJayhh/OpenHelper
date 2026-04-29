# OpenHand CLI Agent Skills Repository: Development Plan

## 1. Executive Summary
This project aims to develop a "plug-and-play" CLI Agent Skills repository from scratch to automate GitHub chore work. The repository will provide a unified set of skills compatible with major AI CLI tools (Qwen Code, Gemini CLI, Claude Code, Codex, Kimi Code, Aider, and PI). 

Our two primary goals are:
1.  **Speed up contributor review** (via automated, high-signal PR reviews).
2.  **Enhance documentation** for future contributors (via multilingual support).

We will develop this repository as a **"Control Center"**. Users will run their CLI agent directly inside this repository, which will load all the pre-configured skills. The agent will then ask the user for a target repository path and execute the requested chore work (documentation, PR review) cross-directory on that target repository.

---

## 2. General Skill Architecture (The Core Engine)
Before individualizing for each CLI, we define the core behaviors that every skill implementation must support.

### 2.1 The "AskUserQuestion" Interactivity Module
All agent implementations must begin with an interactive diagnostic phase. Because the CLI is running in the OpenHand skills repository, it must first establish the target:
- *"What is the absolute path to the target repository you want me to work on?"*
- *"Which chore would you like me to perform today? (e.g., PR Review, Update Docs, Refactor)"*
- *"Would you like to commit or share your changes yourself, or should I automatically commit/comment on your behalf?"*

### 2.2 Cross-Repository Execution Model
Since the agent is launched within the skills repository, all file operations, diff analysis, and git commands must target the absolute path provided by the user. The skill prompts will explicitly instruct the agent to append the target path to all file exploration and `git` / `gh` commands.

### 2.3 The To-Do List Protocol
Every skill must support a `todo` command or behavior.
- **Initialization:** Upon starting a skill, the agent generates a checklist of required sub-tasks.
- **Execution:** The agent updates the user on its progress through the checklist.
- **Completion:** The agent provides a summary of completed tasks vs. pending items.

---

## 3. Skill Implementation Plans

### 3.1 Skill 1: Dev Chores - PR Reviewer (Devin AI Visualization Style)
This skill automates PR reviews and pushes comments to GitHub like a bot, but organizes the output for maximum human readability.

**Features:**
-   **Context-Aware Analysis:** Indexes the current branch changes against the main branch.
-   **Devin-Style Visualization Practices:**
    -   *Intent Grouping:* Groups diffs by logical intent (e.g., "Feature additions", "Bug fixes", "Refactoring") rather than alphabetically.
    -   *Severity Tagging:* Uses GitHub markdown blocks (Alerts) to categorize feedback:
        -   🔴 **Critical (Red):** Bugs or security issues.
        -   🟡 **Warning (Yellow):** Style issues or performance concerns.
        -   ⚪ **Info (Gray):** Suggestions and informational comments.
-   **Action:** Uses GitHub CLI (`gh pr review`) or API to push the formatted markdown as a single, beautifully formatted PR comment.

### 3.2 Skill 2: Multilingual Documentation Generator
This skill analyzes code changes and automatically writes or updates documentation in both English and Mandarin Chinese.

**Features:**
-   **Dual-Language Output:** Standardizes the output to generate parallel blocks for `EN` and `ZH`.
-   **Markdown Standardization:** Uses standard templates for `README.md`, `CONTRIBUTING.md`, and inline code documentation.
-   **Verification:** Cross-checks that both languages convey the exact same technical meaning.

### 3.3 Skill 3: Automated Changelog Generator
This skill automates the process of parsing repository history to generate an accurate, categorized changelog.

**Features:**
-   **Commit Identification:** Uses `git log` and other `git` commands to identify and extract all commits since the last release or within a specific timeframe.
-   **Categorization & Summarization:** Analyzes commit messages to intelligently categorize changes (e.g., Features, Bug Fixes, Breaking Changes).
-   **Output Generation:** Automatically creates or appends to a `CHANGELOG.md` file following standard formatting conventions.

---

## 4. CLI Agent Individualization (The Adapter Layer)

To ensure this repository is plug-and-play, we will map the General Core Skills into the specific directory structures and formats required by each of the 7 CLIs.

### 4.1 Claude Code
-   **Path:** `.claude/skills/dev-chores/SKILL.md`
-   **Implementation:** Use standard Claude tool use prompts. Leverage `$ARGUMENTS` for dynamic input to handle the "AskUserQuestion" flow.

### 4.2 Gemini CLI
-   **Path:** `.gemini/skills/dev-chores/SKILL.md`
-   **Implementation:** Define the skill using the Agent Skill Schema. Use Gemini's parameter injection to handle the interactive questionnaire.

### 4.3 Qwen Code
-   **Path:** `.qwen/commands/dev-chores.md` (or project root depending on latest Qwen spec)
-   **Implementation:** Use Markdown with YAML frontmatter containing the description. Inject shell commands `!{...}` to execute the GitHub CLI operations for PR comments.

### 4.4 OpenAI Codex
-   **Path:** `AGENTS.md` and `.agents/skills/`
-   **Implementation:** Build an instruction chain. Use an override file for the dev-chores sub-directory to ensure the Codex agent prioritizes the PR review formatting rules.

### 4.5 Kimi Code
-   **Path:** `~/.kimi/skills/` or project-specific `.kimi/skills/`
-   **Implementation:** Create custom markdown definitions. Utilize the `--agent-file` flag routing to trigger the Dev Chores routines specifically.

### 4.6 Aider
-   **Path:** `CONVENTIONS.md` or a custom `instructions.txt`
-   **Implementation:** Since Aider uses `.aider.conf.yml` mostly for system config, we will create a structured `PR_REVIEW_INSTRUCTIONS.md` and instruct users to run Aider with `/read PR_REVIEW_INSTRUCTIONS.md` or alias it in their shell.

### 4.7 PI CLI
-   **Path:** `AGENTS.md` / `append-system`
-   **Implementation:** Use directory-scoped `AGENTS.md` files. Append the Devin-style visualization rules to the system prompt to ensure the PI agent outputs the required markdown layout.

---

## 5. Development Roadmap

*   **Phase 1: The Core Prompts**
    *   Draft the system prompts for the PR Reviewer (Devin style).
    *   Draft the system prompts for the Multilingual Doc Generator.
    *   Draft the system prompts for the Automated Changelog Generator.
*   **Phase 2: CLI Adapters**
    *   Create the `.claude`, `.gemini`, `.qwen`, and `.kimi` directories.
    *   Package the core prompts into the specific markdown/TOML/YAML formats required by each.
*   **Phase 3: Interactivity & Testing**
    *   Integrate the `AskUserQuestion` and To-Do list loops.
    *   Test the PR comment push via GitHub CLI integration across all agents.
*   **Phase 4: Open Source Release**
    *   Write the installation guide. "Clone this repo, open your terminal inside it, run your preferred CLI, and point it at the open-source repo you want to help."
