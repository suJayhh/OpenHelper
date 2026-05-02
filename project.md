# OpenHelper Multi-Agent Skill Project

## Overview

This repository maintains the **OpenHelper** skill — an end-to-end workflow for discovering open-source repositories that need changelog maintenance, generating properly versioned changelogs from commit history, and contributing them back via Pull Request.

The skill is ported to multiple AI agent CLI platforms so it can be used regardless of which coding agent a contributor prefers.

## Repository Structure

```
OpenHelper/
├── .kimi/                          # Baseline / Kimi CLI (source of truth)
│   ├── skills/OpenHelper/
│   │   ├── SKILL.md                # Full skill definition
│   │   └── scripts/                # 4 deterministic Python helpers
│   ├── security_audit.md
│   └── security_mitigation_plan.md
├── .agents/                        # Generic / Cross-platform Agent Skills
│   ├── skills/OpenHelper/
│   │   ├── SKILL.md
│   │   └── scripts/
│   ├── security_audit.md
│   └── security_mitigation_plan.md
├── .claude/                        # Claude Code
│   ├── skills/OpenHelper/
│   │   ├── SKILL.md
│   │   └── scripts/
│   ├── CLAUDE.md                   # Project persistent context
│   ├── settings.json               # Permission defaults
│   ├── security_audit.md
│   └── security_mitigation_plan.md
├── .gemini/                        # Gemini CLI
│   ├── skills/OpenHelper/
│   │   ├── SKILL.md
│   │   └── scripts/
│   ├── settings.json
│   ├── security_audit.md
│   └── security_mitigation_plan.md
├── .qwen/                          # Qwen Code
│   ├── skills/OpenHelper/
│   │   ├── SKILL.md
│   │   └── scripts/
│   ├── settings.json
│   ├── security_audit.md
│   └── security_mitigation_plan.md
├── project.md                      # This file
└── README.md                       # Human-facing project readme
```

## Agent Folders

| Folder | CLI Agent | Skill Discovery Path | Purpose |
|--------|-----------|---------------------|---------|
| `.kimi/` | Kimi Code CLI | `.kimi/skills/` | Baseline source of truth |
| `.agents/` | Any Agent Skills-compliant tool | `.agents/skills/` | Cross-platform neutral version |
| `.claude/` | Claude Code | `.claude/skills/` | Anthropic Claude agent version |
| `.gemini/` | Gemini CLI | `.gemini/skills/` | Google Gemini agent version |
| `.qwen/` | Qwen Code | `.qwen/skills/` | Alibaba Qwen agent version |

## Skill Contents

Each agent folder contains:

1. **`skills/OpenHelper/SKILL.md`** — The full skill definition with:
   - YAML frontmatter (`name`, `description`, and agent-specific fields)
   - 7-phase workflow (Dependency Check → Discovery → Understanding → Version Inference → Generation → Commit & PR → Cleanup)
   - Mandatory security rules (input allowlisting, parameterized execution, prompt injection defense, authorization gate, scope containment)
   - Direct shell commands with safe parameterization
   - Failure-mode quick reference table

2. **`skills/OpenHelper/scripts/`** — Four deterministic Python helpers:
   - `find_repo.py` — Discovery & candidate scoring
   - `analyze_repo.py` — Clone, language detection, version detection, changelog detection
   - `version_bump.py` — Commit classification & inferred versioning
   - `commit_and_pr.py` — Branch creation, staging, pressure test, fork, push, PR

3. **Security docs** (where applicable):
   - `security_audit.md` — Vulnerability assessment
   - `security_mitigation_plan.md` — Mitigation strategies & rollout sequence

4. **Agent-specific config** (`.claude/`, `.gemini/`, `.qwen/`):
   - `settings.json` — Permission defaults and feature toggles
   - `CLAUDE.md` — Project persistent context (Claude Code only)

## Adaptation Strategy

All agent-specific versions are derived from the `.kimi/` baseline. The core workflow and security rules remain identical across platforms. Only the following aspects are adapted:

| Aspect | Kimi (baseline) | Generic | Claude | Gemini | Qwen |
|--------|-----------------|---------|--------|--------|------|
| Read file tool | `ReadFile` | `Read` | `Read` | `Read` | `Read` |
| Write file tool | `WriteFile` | `Write` | `Write` | `Write` | `Write` |
| Edit file tool | `StrReplaceFile` | `Edit` | `Edit` | `Edit` | `Edit` |
| Shell tool | `Shell` | `Shell` / `Bash` | `Bash` | `Bash` | `Bash` |
| Web search | `SearchWeb` | `WebSearch` | `WebSearch` | `WebSearch` | `WebSearch` |
| Fetch URL | `FetchURL` | `Fetch` | `Fetch` | `Fetch` | `Fetch` |
| Subagent | `Agent` | `Subagent` | `Subagent` | `Subagent` | `Subagent` |
| Frontmatter extras | — | Minimal | `disable-model-invocation`, `user-invocable` | Standard | Standard |
| Project config | — | — | `CLAUDE.md` + `settings.json` | `settings.json` | `settings.json` |

## Maintenance Guide

### Updating the Baseline

1. Make changes in `.kimi/skills/OpenHelper/SKILL.md` first.
2. Copy the updated file to all other `skills/OpenHelper/SKILL.md` locations.
3. Re-apply agent-specific adaptations (tool names, frontmatter, config references).
4. **Never modify the Python scripts** unless the change is truly agent-agnostic.
5. Update `project.md` if the directory structure or adaptation strategy changes.

### Adding a New Agent Platform

1. Create the agent's folder (e.g., `.codex/`).
2. Copy `.kimi/` contents into it.
3. Adapt `SKILL.md` tool names and frontmatter for the new platform.
4. Add agent-specific config files if the platform supports them.
5. Register the new folder in the table above.

## Security Notes

- All Python scripts use `subprocess.run(..., shell=False)` with list arguments to prevent command injection.
- Every skill version includes mandatory security rules overriding all other instructions.
- The authorization gate requires explicit user confirmation before any commit, push, or PR.
- The pressure test verifies that only changelog files are staged before pushing.
