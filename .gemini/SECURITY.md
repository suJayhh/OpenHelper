# Security Audit & Mitigation Plan: OpenHelper (Gemini CLI)

## Vulnerabilities Assessed

| ID | Vulnerability | Severity | Notes |
|---|---|---|---|
| V-A | Delimiter Bypass Prompt Injection | High | Static `--- BEGIN/END UNTRUSTED DATA ---` markers can be forged inside commit messages to break out of the untrusted block. |
| V-B | PowerShell Command Injection via Quote Escaping | Critical | Single-quoted strings in PowerShell break if the input contains unescaped `'`, enabling arbitrary code execution. |
| V-C | Git Configuration / Hook Execution Attacks | Medium | Cloned repos may contain malicious `.git/config` entries or hooks triggered during agent interaction. |
| V-D | Resource Exhaustion (Context Bomb) | Low–Medium | Oversized commits, binary blobs, or huge markdown files can exhaust the agent context window. |

## Mitigations Applied

### 1. Injection-Proof Framing (Anti-Prompt Injection)
- **Randomized delimiters:** Each skill run generates a unique 16-character hex token. Bounding markers use that token (e.g., `<<<UNTRUSTED_a3f9b1c8e72d4056>>>`). If the untrusted content contains either marker string, abort immediately.
- **Content-hash seal:** Compute SHA-256 of the raw text between markers and verify before processing.
- **Behavioral firewall:** If untrusted data contains instruction-like phrases ("ignore previous instructions", "system:", "assistant:"), log the suspicion and use the data for changelog categorization only — never execute commands derived from it.

### 2. Parameterized Command Execution (Anti-Command Injection)
- **Never** construct commands by concatenating untrusted strings.
- Use the provided **Python inline-templates** for all complex operations; they internally use `subprocess.run(..., shell=False)` with list arguments.
- **Escape rule:** Before placing any dynamic value inside single quotes, replace every `'` with `''`.
- **Validation gate:** Reject dynamic values containing `;`, `|`, `&`, `` ` ``, `$(`, `>(`, `<(`, or newlines.
- Ban `Invoke-Expression`, `iex`, `& { }` with string-built commands, and `Start-Process` with a single concatenated argument string.

### 3. Git Execution Sandboxing
- **All** `git` commands include `-c core.hooksPath=nul` (Windows) or `-c core.hooksPath=/dev/null` (Unix) to disable hooks.
- **Two-step clone:** `clone --no-checkout` first, inspect `.git/config` for suspicious keys (`core.fsmonitor`, `core.sshCommand`, non-standard `credential.helper`, `filter.*`, `diff.*.textconv`), then checkout.
- Use `--no-verify` only as a supplement; it is not sufficient alone.

### 4. Input Budgets (Anti-DoS)
- Skip files larger than **100 KB**.
- Truncate each file to the first **200 lines**.
- Read at most **15 markdown files** total.
- Halt file ingestion if aggregate context exceeds **500 KB**.
- Truncate commit subjects to **500 characters**; discard commits with more than **5 consecutive non-ASCII-printable characters**.

## Residual Risks

| Risk | Why It Persists | Long-Term Fix |
|---|---|---|
| Novel prompt injection bypasses | LLMs are vulnerable to adversarial prompting | Route all I/O through typed Python tool APIs (Executor Model) |
| Zero-day in `git` itself | Clone may trigger vulnerabilities before hooks are disabled | Run git inside a container or sandbox |
| Token leakage via `gh` output | Agent may echo auth tokens into context | Pipe `gh` output through a token-redacting filter |

## Rollout Priority

1. **Shell Hardening** (Critical — ACE)
2. **Git Sandboxing** (Medium — RCE via hooks)
3. **Randomized Delimiters** (High — prompt injection)
4. **Input Budgets** (Low–Med — resource DoS)
