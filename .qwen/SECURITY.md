# Security Audit & Mitigation Plan: OpenHelper Qwen Skill

## 1. Security Vulnerabilities Assessment

The skill design relies on the LLM to orchestrate shell commands and parse untrusted data. This introduces several critical vulnerabilities:

### A. Advanced Prompt Injection (The Delimiter Bypass)
**Vulnerability:** Static bounding blocks around untrusted commit messages can be terminated by an attacker embedding the exact end delimiter inside a commit message, followed by a malicious system prompt.
**Severity:** High

### B. PowerShell Command Injection via Quote Escaping
**Vulnerability:** Single-quoted strings in PowerShell break if the input contains an unescaped single quote, allowing arbitrary code execution when the LLM constructs commands with dynamic repo or branch names.
**Severity:** Critical

### C. Git Configuration / Hook Execution Attacks
**Vulnerability:** `git clone` and subsequent commands execute inside the cloned directory, which may contain crafted `.git/config` entries or hooks.
**Severity:** Medium

### D. Resource Exhaustion (Context Bomb)
**Vulnerability:** A repository could contain gigabytes of binary data in shallow history, or commit messages millions of characters long, exhausting the agent's context window.
**Severity:** Low to Medium

---

## 2. Explicit Mitigation Strategies

### Mitigation 1: Strongly Typed Data Extraction (Anti-Prompt Injection)
All data extraction from the target repository must be performed by deterministic, non-LLM parsers. The parser extracts only necessary fields and returns sanitized JSON. The LLM only ever receives structured JSON, stripped of instructional keywords.

### Mitigation 2: Parameterized Command Execution (Anti-Command Injection)
Never allow the LLM to construct shell commands via string concatenation. Use a strongly-typed tool interface where arguments are passed as lists to an underlying `subprocess.Popen(..., shell=False)` equivalent. The skill mandates Python inline-templates with `subprocess.run(..., shell=False)` for all complex operations.

### Mitigation 3: Restricted Execution Sandbox
All `git` operations run with flags that disable hook execution and local configurations:
- Use `git -c core.hooksPath=nul` for all commands.
- Prohibit generic shell commands; restrict to predefined permitted API calls.

---

## 3. Executor Model Plan

To implement the mitigations above, the architecture should be refactored into an **Executor Model**. The bundled Python scripts (`analyze_repo.py`, `commit_and_pr.py`, `find_repo.py`, `version_bump.py`) should be used as the *only* interfaces to the repository.

### Architecture Overview
The Executor Model consists of a rigid Python harness (the Executor) and the LLM (the Brain). The LLM no longer has raw terminal access. Instead, it uses designated JSON-RPC tool calls provided by the Executor.

#### Phase 1: Safe Discovery & Analysis
1. **Tool:** `discover_repo(search_query: str)`
   - The LLM requests discovery. The Executor runs `find_repo.py` safely, interacting with the GitHub API, and returns a JSON list of scored candidates.
2. **Tool:** `analyze_target(repo_url: str)`
   - The LLM selects a target. The Executor runs `analyze_repo.py`. The script clones the repo in an isolated temp directory with hooks disabled, extracts commit history deterministically, and returns a sanitized JSON summary.

#### Phase 2: Generation
1. **Tool:** `generate_changelog(commit_data: dict)`
   - The LLM processes structured JSON commit data, groups them into features/fixes/chores, and outputs the final Markdown string.
   - Because the LLM is only reading sanitized JSON and outputting Markdown, prompt injection is neutralized.

#### Phase 3: Safe Contribution
1. **Tool:** `submit_pr(repo_url: str, changelog_markdown: str)`
   - The LLM hands the finished Markdown back to the Executor.
   - The Executor (running `commit_and_pr.py`) creates the branch, writes the file natively via Python I/O, commits using `subprocess` with `shell=False`, and pushes the PR using the GitHub API.

### Implementation Steps
1. **Remove Terminal Access:** Revoke the LLM's generic command capability when operating this skill.
2. **Expose Custom Tools:** Expose the 4 bundled Python scripts as specific AI Tools.
3. **Rewrite SKILL.md:** Update the prompt to instruct the agent to orchestrate these specific tools in sequence, rather than dropping down into shell.

---

## 4. Post-Mitigation Security Rules Summary

After mitigations are applied, the Security Rules section of `SKILL.md` contains these six subsections:

1. **§1 — PowerShell Command Injection Prevention**
2. **§2 — Path Validation / Directory Traversal Prevention**
3. **§3 — Prompt Injection Defense**
4. **§4 — Authorization Gate**
5. **§5 — Scope Containment**
6. **§6 — Git Execution Sandboxing**

Input budget rules are embedded inline in Phases 2 and 3 as operational constraints.

---

## 5. Residual Risk Acknowledgement

Even after all mitigations are applied, the following risks remain because the architecture still relies on an LLM constructing and executing shell commands:

| Residual Risk | Why It Persists | Long-Term Fix |
|---------------|-----------------|---------------|
| Novel prompt injection bypasses | LLMs are fundamentally vulnerable to adversarial prompting | Executor Model — route all I/O through typed Python tool APIs |
| Zero-day in git itself | Git clone can trigger vulns before hooks even run | Run git inside a container/sandbox |
| Token leakage via `gh auth status` output | Agent may echo auth tokens into context | Pipe `gh` output through a token-redacting filter |

The Executor Model remains the long-term architectural goal. The mitigations in `SKILL.md` provide meaningful defense-in-depth for the current prompt-driven design.
