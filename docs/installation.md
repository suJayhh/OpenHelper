# Installation Guide

## Quick Start

1. Clone this repository.
2. Open your terminal inside the cloned folder.
3. Launch your preferred AI CLI agent.
4. The agent will load the skills automatically and ask for a target repository.

## Per-CLI Setup

### Kimi Code

Kimi discovers skills from `.kimi/skills/` inside this repo automatically when you run Kimi here.

```bash
cd openhand-skills
kimi
```

### Claude Code

Claude Code reads skills from `.claude/skills/`. Launch Claude inside this repo:

```bash
cd openhand-skills
claude
```

### Gemini CLI

Gemini CLI loads skills from `.gemini/skills/`. Start Gemini here:

```bash
cd openhand-skills
gemini
```

### Qwen Code

Qwen Code reads commands from `.qwen/commands/`. Run Qwen inside this repo:

```bash
cd openhand-skills
qwen
```

### OpenAI Codex

Codex uses `.agents/skills/` and `AGENTS.md`. Run Codex here:

```bash
cd openhand-skills
codex
```

### Aider

Aider reads `CONVENTIONS.md` from the repo root. Start Aider with:

```bash
cd openhand-skills
aider
```

Or manually load the instructions:

```
/read CONVENTIONS.md
```

### PI CLI

PI CLI uses directory-scoped `AGENTS.md` files. The PI-specific instructions are in `pi/AGENTS.md`. Run PI here:

```bash
cd openhand-skills
pi
```

## Dependencies

- `git` — Required for all skills.
- `gh` (GitHub CLI) — Required for the PR Reviewer skill to post comments.

Install `gh`:

```bash
# macOS
brew install gh

# Windows
winget install GitHub.cli

# Ubuntu/Debian
sudo apt install gh
```

## Verification

Run the validation script to ensure all skills are correctly configured:

```bash
python scripts/validate-skills.py
```
