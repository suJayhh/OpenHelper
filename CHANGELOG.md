# Changelog

## [0.1.0] — 2026-04-29

### Features
- **PR Reviewer Skill** — Devin-style PR reviews with intent grouping, severity tagging (🔴 Critical, 🟡 Warning, ⚪ Info), and `gh pr review` integration. Includes `analyze_diff.py` helper script.
- **Multilingual Documentation Generator** — Bilingual EN/ZH documentation generation with parallel block formatting and cross-language verification.
- **Changelog Generator** — Categorized changelog entries from git history with Breaking Changes, Features, Bug Fixes, Performance, Documentation, and Chores groupings.
- **CLI Adapters** — Plug-and-play skill adapters for Kimi Code, Claude Code, Gemini CLI, Qwen Code, OpenAI Codex, Aider, and PI CLI.
- **Validation Script** — `scripts/validate-skills.py` checks YAML frontmatter, core prompt references, and duplicate names across all skill files.

### Documentation
- `README.md` with quick-start guide and supported CLI table.
- `docs/installation.md` with per-CLI setup instructions.
- `AGENTS.md` with Control Center rules, cross-repository execution model, and todo list protocol.

### Repository
- Initial release of the OpenHand CLI Agent Skills Repository.
