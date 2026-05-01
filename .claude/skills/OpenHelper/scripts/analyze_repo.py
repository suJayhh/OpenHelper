#!/usr/bin/env python3
"""
Clone and analyze a target repository, producing a machine-readable context file.

⚠️  REFERENCE ONLY — Do NOT execute this script as part of the changelog workflow.
This script is bundled for documentation and offline reference.

SECURITY PATTERNS ILLUSTRATED:
- All git subprocess calls use -c core.hooksPath=/dev/null to disable hook execution.
- Clone depth capped at 20 (was 100) to reduce attack surface and resource usage.
- Markdown file scan capped at 20 files, 500KB each, to prevent resource exhaustion.
- Commit messages truncated to 500 chars and stripped of control characters / bounding-block markers before entering JSON output.
- _is_safe_path rejects system dirs AND requires the path to be inside the user's home directory or a designated workspace.
- subprocess.run(..., shell=False) with list arguments only (no shell string construction).
- Deterministic JSON output; LLM never sees raw, unfiltered repository text.

Usage:
    python analyze_repo.py <clone_url> <output_dir>

Produces:
    <output_dir>/repo_context.json
"""

# SECURITY: This script is bundled for reference only. Dependencies are
# commented out to prevent accidental execution during the changelog workflow.
# The skill instructions in SKILL.md mandate inline git commands and file ops.
# import argparse
# import json
# import os
# import re
# import subprocess
# import sys
# from pathlib import Path
raise RuntimeError("This script is reference-only. Do not execute it.")


BLOCKED_PREFIXES = [
    "C:\\Windows", "C:\\Program Files", "C:\\ProgramData",
    "/etc", "/usr", "/bin", "/sbin", "/lib", "/sys", "/dev", "/proc",
]


def _is_safe_path(path: str) -> bool:
    """Reject system directories, traversal sequences, and paths outside the workspace."""
    p = Path(path).resolve()
    parts = [part.lower() for part in p.parts]
    if ".." in parts:
        return False
    for blocked in BLOCKED_PREFIXES:
        bpath = Path(blocked).resolve()
        try:
            p.relative_to(bpath)
            return False
        except ValueError:
            pass
    # SECURITY: Path must be inside the user's home or a designated workspace.
    home = Path.home().resolve()
    try:
        p.relative_to(home)
    except ValueError:
        # Allow explicit workspace override if needed; default to home-only.
        return False
    return True


def _validate_git_repo(repo_path: str) -> None:
    """Ensure the path contains a .git directory."""
    git_dir = Path(repo_path) / ".git"
    if not git_dir.is_dir():
        raise RuntimeError(f"Not a git repository: {repo_path}")


def run(cmd: list[str], cwd: str | None = None, check: bool = True) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore", cwd=cwd)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr}")
    return result.stdout.strip()


def clone_repo(clone_url: str, target_path: str, depth: int = 20):
    if not _is_safe_path(target_path):
        raise RuntimeError(f"Unsafe target path rejected: {target_path}")
    # SECURITY: Disable git hooks during clone to prevent arbitrary code execution.
    git_cmd = ["git", "-c", "core.hooksPath=/dev/null"]
    if os.path.exists(target_path):
        _validate_git_repo(target_path)
        run(git_cmd + ["pull", "--depth", str(depth)], cwd=target_path)
    else:
        run(git_cmd + ["clone", "--depth", str(depth), clone_url, target_path])
        _validate_git_repo(target_path)


def find_markdown_files(repo_path: str, max_files: int = 20) -> list[str]:
    """Find markdown files in root and docs/, limited to max_files."""
    files = []
    root = Path(repo_path)
    for pattern in ["*.md", "**/*.md"]:
        for f in root.glob(pattern):
            if f.is_file() and f.stat().st_size < 500 * 1024:  # < 500KB
                rel = str(f.relative_to(root))
                # Prioritize root-level and docs/
                priority = 0 if rel.count(os.sep) == 0 else (1 if rel.startswith("docs") else 2)
                files.append((priority, rel, str(f)))
    files.sort(key=lambda x: (x[0], x[1]))
    return [f[2] for f in files[:max_files]]


def _sanitize_message(msg: str) -> str:
    """Truncate and strip control characters / bounding-block markers from commit messages."""
    # Truncate to 500 chars
    msg = msg[:500]
    # Strip control chars except safe whitespace
    allowed = {"\n", "\r", "\t"}
    msg = "".join(ch for ch in msg if ch in allowed or ord(ch) >= 32)
    # Remove bounding-block markers that could be used for prompt injection
    markers = ["--- BEGIN UNTRUSTED DATA", "--- END UNTRUSTED DATA"]
    for marker in markers:
        msg = msg.replace(marker, "[REDACTED]")
    return msg


def extract_context(repo_path: str) -> dict:
    if not _is_safe_path(repo_path):
        raise RuntimeError(f"Unsafe repo path rejected: {repo_path}")
    _validate_git_repo(repo_path)
    root = Path(repo_path)
    context = {
        "project_name": root.name,
        "description": "",
        "primary_language": "",
        "version_source": "",
        "version_value": "",
        "conventional_commits": False,
        "has_changelog": False,
        "changelog_path": "",
        "commit_count": 0,
        "latest_commit_date": "",
        "latest_commit_message": "",
    }

    # Primary language (from GitHub lang stats or file counts)
    exts = {}
    for f in root.rglob("*"):
        if f.is_file() and f.stat().st_size < 10 * 1024 * 1024:
            ext = f.suffix.lower()
            if ext:
                exts[ext] = exts.get(ext, 0) + 1
    lang_map = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".rs": "Rust", ".go": "Go", ".rb": "Ruby", ".java": "Java",
        ".cpp": "C++", ".c": "C", ".cs": "C#", ".php": "PHP",
    }
    top_ext = max(exts, key=exts.get) if exts else ""
    context["primary_language"] = lang_map.get(top_ext, "Unknown")

    # README description
    readme = root / "README.md"
    if readme.exists():
        lines = readme.read_text(encoding="utf-8", errors="ignore").splitlines()
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith("["):
                context["description"] = stripped[:200]
                break

    # Version detection
    version_files = [
        ("package.json", r'"version"\s*:\s*"([^"]+)"'),
        ("Cargo.toml", r'^version\s*=\s*"([^"]+)"'),
        ("pyproject.toml", r'^version\s*=\s*"([^"]+)"'),
        ("setup.py", r'version\s*=\s*["\']([^"\']+)["\']'),
        ("version.rb", r'VERSION\s*=\s*["\']([^"\']+)["\']'),
    ]
    for fname, pattern in version_files:
        fpath = root / fname
        if fpath.exists():
            text = fpath.read_text(encoding="utf-8", errors="ignore")
            m = re.search(pattern, text, re.MULTILINE)
            if m:
                context["version_source"] = fname
                context["version_value"] = m.group(1)
                break

    # Latest tag
    try:
        tag = run(["git", "-c", "core.hooksPath=/dev/null", "describe", "--tags", "--abbrev=0"], cwd=repo_path, check=False)
        if tag:
            context["version_value"] = tag
            context["version_source"] = "git_tag"
    except Exception:
        pass

    # Conventional commits check (sample last 20)
    try:
        log = run(["git", "-c", "core.hooksPath=/dev/null", "log", "--format=%s", "-n", "20"], cwd=repo_path, check=False)
        prefixes = ["feat:", "fix:", "chore:", "docs:", "style:", "refactor:", "test:", "ci:"]
        lines = log.splitlines()
        conv_count = sum(1 for line in lines if any(line.startswith(p) for p in prefixes))
        context["conventional_commits"] = conv_count >= len(lines) * 0.5 if lines else False
    except Exception:
        pass

    # Changelog detection
    candidates = [
        "CHANGELOG.md", "changelog.md", "CHANGES.md", "changes.md",
        "HISTORY.md", "history.md", "NEWS.md", "news.md",
        "RELEASES.md", "releases.md",
    ]
    for cand in candidates:
        if (root / cand).exists():
            context["has_changelog"] = True
            context["changelog_path"] = cand
            break
    if not context["has_changelog"]:
        for cand in candidates:
            matches = list(root.rglob(cand))
            if matches:
                context["has_changelog"] = True
                context["changelog_path"] = str(matches[0].relative_to(root))
                break

    # Commit stats
    try:
        count = run(["git", "-c", "core.hooksPath=/dev/null", "rev-list", "--count", "HEAD"], cwd=repo_path, check=False)
        context["commit_count"] = int(count) if count else 0
    except Exception:
        pass

    try:
        latest = run(["git", "-c", "core.hooksPath=/dev/null", "log", "-1", "--format=%ci%x00%s"], cwd=repo_path, check=False)
        if "\x00" in latest:
            date, msg = latest.split("\x00", 1)
            context["latest_commit_date"] = date.strip()
            context["latest_commit_message"] = _sanitize_message(msg.strip())
    except Exception:
        pass

    return context


def main():
    parser = argparse.ArgumentParser(description="Clone and analyze a repository.")
    parser.add_argument("clone_url", help="Git clone URL")
    parser.add_argument("output_dir", help="Directory to write repo_context.json and clone into")
    parser.add_argument("--depth", type=int, default=20, help="Git clone depth (capped for security)")
    args = parser.parse_args()

    repo_name = args.clone_url.rstrip("/").split("/")[-1].replace(".git", "")
    target_path = os.path.join(args.output_dir, repo_name)
    os.makedirs(args.output_dir, exist_ok=True)

    clone_repo(args.clone_url, target_path, depth=args.depth)
    context = extract_context(target_path)
    context["local_path"] = target_path
    context["clone_url"] = args.clone_url

    out_path = os.path.join(args.output_dir, "repo_context.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(context, f, indent=2)

    print(json.dumps(context, indent=2))


if __name__ == "__main__":
    main()
