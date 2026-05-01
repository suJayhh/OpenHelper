# Security Posture — OpenHelper (Claude Code)

This document summarizes the threat model, key vulnerabilities, and mitigations for the OpenHelper skill.

## Threat Model

OpenHelper clones untrusted public GitHub repositories, ingests commit messages and file contents into the agent context, and performs git operations (clone, commit, push, PR). The primary risks are:

- **Prompt injection** via malicious commit messages or file contents.
- **Command injection** via untrusted repository names, paths, or file names.
- **Remote code execution** via malicious git hooks, config filters, or repository structures.
- **Denial of service** via resource exhaustion (large files, binary blobs, long commit messages).

## Key Vulnerabilities & Mitigations

| ID | Vulnerability | Severity | Mitigation |
|---|---|---|---|
| V-A | **Delimiter Bypass Prompt Injection** — Static `--- BEGIN/END UNTRUSTED DATA ---` markers can be embedded in commit messages to break out of the trusted boundary. | High | Replaced with **per-invocation randomized 16-character hex delimiters** plus a **SHA-256 content-hash seal**. Abort if markers appear inside content or the hash mismatches. |
| V-B | **PowerShell Command Injection** — Single-quoted strings break if the repo name contains an unescaped `'`, enabling arbitrary code execution. | Critical | Mandate `'` → `''` escaping. Prohibit string interpolation and `Invoke-Expression` / `iex`. Use Python templates with `subprocess.run(..., shell=False)` and list arguments only. Validate dangerous characters (`;`, `\|`, `&`, `` ` ``, `$(`, etc.) before execution. |
| V-C | **Git Hook / Config Execution** — Cloning and operating inside a malicious repo can trigger hooks, filter drivers, or fsmonitor. | Medium | Sandbox **every** git command with `-c core.hooksPath=nul -c core.fsmonitor= -c core.sshCommand=nul -c protocol.file.allow=never`. Use a **two-step clone** (`--no-checkout` → inspect `.git/config` → checkout). Reject repos with suspicious config keys. |
| V-D | **Resource Exhaustion** — Gigabyte-scale repos, million-character commit messages, or huge markdown files can crash the agent or exhaust tokens. | Low–Med | Enforce **input budgets**: skip files >100 KB, truncate to 200 lines, max 15 markdown files, 500 KB total context cap. Truncate commit subjects to 500 chars. Reduce clone depth to 50. |

## Security Rules Summary

The skill enforces six mandatory security rules:

1. **PowerShell Command Injection Prevention** — Escaped single quotes, no interpolation, no `Invoke-Expression`, validation gate.
2. **Path Validation / Directory Traversal Prevention** — Regex allowlisting, absolute paths, no `..`, home/workspace containment.
3. **Prompt Injection Defense** — Randomized delimiters, SHA-256 seals, behavioral firewall, banned static markers.
4. **Authorization Gate** — Exact file path + 20-line preview + explicit user confirmation before commit/PR.
5. **Scope Containment** — File ops confined to `TARGET_PATH`, exact `git add`, staged-file verification, pressure test.
6. **Git Execution Sandboxing** — Hook-disabling overrides on every command, two-step clone with `.git/config` inspection.

## Residual Risks

| Risk | Why It Persists | Long-Term Fix |
|---|---|---|
| Novel prompt injection bypasses | LLMs are fundamentally vulnerable to adversarial prompting | Executor Model — route all I/O through typed Python tool APIs |
| Zero-day in git itself | Git clone can trigger vulns before hooks run | Run git inside a container or Windows Sandbox |
| Token leakage via `gh auth status` | Agent may echo auth tokens into context | Pipe `gh` output through a token-redacting filter |

## Architecture Note

The current design uses **Python inline-templates** as the primary defense: the agent writes a rigid template file, edits only the `SAFE_` variable assignments at the top, and executes it. The templates use `subprocess.run(..., shell=False)` with list arguments, eliminating shell injection. All untrusted data is sanitized to JSON before entering the agent context.
