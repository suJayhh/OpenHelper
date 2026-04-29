# OpenHand CLI Agent Skills Repository

A plug-and-play "Control Center" for automating GitHub chore work across major AI CLI tools.

## Quick Start

1. Clone this repository.
2. Open your terminal inside the cloned folder.
3. Launch your preferred AI CLI agent (Kimi, Claude, Gemini, etc.).
4. Tell the agent which repo you want to work on and which chore to perform.

## Supported CLI Tools

| CLI Tool | Skill Path |
|----------|-----------|
| Kimi Code | `.kimi/skills/` |
| Claude Code | `.claude/skills/` |
| Gemini CLI | `.gemini/skills/` |
| Qwen Code | `.qwen/commands/` |
| OpenAI Codex | `.agents/skills/` |
| Aider | `CONVENTIONS.md` |
| PI CLI | `AGENTS.md` |

## Skills

- **PR Reviewer** — Devin-style visual reviews with intent grouping and severity tagging.
- **Multilingual Docs** — Auto-generate `EN` + `ZH` documentation.
- **Changelog Generator** — Categorized changelog entries from git history.

## Dependencies

- `git`
- `gh` (GitHub CLI) — for posting PR reviews

## Development

This repo follows a "Kimi-first vertical slice" approach:
1. Skills are prototyped for Kimi Code CLI first.
2. Proven skills are then ported to the other CLI adapters.
