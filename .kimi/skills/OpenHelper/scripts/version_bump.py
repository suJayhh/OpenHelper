#!/usr/bin/env python3
"""
Infer versions for commits based on a deterministic delta scheme.

⚠️  REFERENCE ONLY — Do NOT execute this script as part of the changelog workflow.
The skill instructions in SKILL.md mandate inline git commands and file operations.
This script is bundled for documentation and offline reference.

Usage:
    python version_bump.py --repo <repo_path> [--base-version VERSION] [--output FILE]

Outputs JSON mapping each commit to an inferred version and category.
"""

# SECURITY: This script is bundled for reference only. Dependencies are
# commented out to prevent accidental execution during the changelog workflow.
# The skill instructions in SKILL.md mandate inline git commands and file ops.
# import argparse
# import json
# import os
# import re
# import subprocess
# from dataclasses import dataclass, asdict
# from pathlib import Path
raise RuntimeError("This script is reference-only. Do not execute it.")

# --- Everything below is dead reference code. It is preserved for documentation
# --- but will never execute because the RuntimeError above aborts import.

# BLOCKED_PREFIXES = [
#     "C:\\Windows", "C:\\Program Files", "C:\\ProgramData",
#     "/etc", "/usr", "/bin", "/sbin", "/lib", "/sys", "/dev", "/proc",
# ]
#
#
# def _is_safe_path(path: str) -> bool:
#     """Reject system directories and traversal sequences."""
#     p = Path(path).resolve()
#     parts = [part.lower() for part in p.parts]
#     if ".." in parts:
#         return False
#     for blocked in BLOCKED_PREFIXES:
#         bpath = Path(blocked).resolve()
#         try:
#             p.relative_to(bpath)
#             return False
#         except ValueError:
#             pass
#     return True
#
#
# def _validate_git_repo(repo_path: str) -> None:
#     """Ensure the path contains a .git directory."""
#     git_dir = Path(repo_path) / ".git"
#     if not git_dir.is_dir():
#         raise RuntimeError(f"Not a git repository: {repo_path}")
#
#
# @dataclass
# class Commit:
#     sha: str
#     short_sha: str
#     date: str
#     message: str
#     category: str
#     inferred_version: str
#     is_tagged: bool = False
#
#
# def run_git(repo_path: str, *args: str) -> str:
#     if not _is_safe_path(repo_path):
#         raise RuntimeError(f"Unsafe repo path rejected: {repo_path}")
#     _validate_git_repo(repo_path)
#     result = subprocess.run(
#         ["git", "-C", repo_path] + list(args),
#         capture_output=True, text=True, encoding="utf-8", errors="ignore"
#     )
#     if result.returncode != 0:
#         raise RuntimeError(f"git failed: {result.stderr}")
#     return result.stdout.strip()
#
#
# def get_tags(repo_path: str) -> dict[str, str]:
#     """Map commit SHAs to their tags."""
#     tags = {}
#     try:
#         output = run_git(repo_path, "for-each-ref", "refs/tags", "--format=%(refname:short)|%(objectname)")
#         for line in output.splitlines():
#             if "|" in line:
#                 tag, sha = line.split("|", 1)
#                 tags[sha.strip()] = tag.strip()
#     except RuntimeError:
#         pass
#     return tags
#
#
# def classify_commit(message: str) -> str:
#     """Classify a commit message into feat/fix/chore/other."""
#     msg_lower = message.lower()
#     if any(msg_lower.startswith(p) for p in ["feat:", "feature:", "add:", "implement:", "new:"]):
#         return "feat"
#     if any(msg_lower.startswith(p) for p in ["fix:", "bugfix:", "patch:", "hotfix:", "bug:"]):
#         return "fix"
#     if any(msg_lower.startswith(p) for p in ["chore:", "docs:", "style:", "refactor:", "test:", "ci:", "build:", "perf:"]):
#         return "chore"
#     # Fallback heuristics
#     if any(w in msg_lower for w in ["add", "implement", "introduce", "support"]):
#         return "feat"
#     if any(w in msg_lower for w in ["fix", "bug", "patch", "resolve", "correct"]):
#         return "fix"
#     return "chore"
#
#
# def parse_version(version_str: str) -> tuple[int, int, int]:
#     """Parse a version string like v1.2.3 or 1.2.3 into (major, minor, patch)."""
#     version_str = version_str.lstrip("vV")
#     parts = version_str.split(".")
#     major = int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else 0
#     minor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
#     patch = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
#     return major, minor, patch
#
#
# def format_version(major: int, minor: int, patch: int, chore_count: int = 0) -> str:
#     """Format version components into a string."""
#     if chore_count > 0:
#         return f"v{major}.{minor}.{patch}.{chore_count}"
#     return f"v{major}.{minor}.{patch}"
#
#
# def infer_versions_forward(commits: list[Commit], base_version: str) -> list[Commit]:
#     """
#     Traverse commits FORWARD (oldest to newest) and assign inferred versions.
#
#     Rules:
#     - Feature: +0.1 to minor
#     - Fix: +0.01 to patch
#     - Chore: append decimal with consecutive count
#     """
#     major, minor, patch = parse_version(base_version)
#     # Start one step BEFORE base so the first commit doesn't equal base
#     # This ensures all inferred versions are clearly synthetic
#     minor = max(0, minor - 1)
#
#     result = []
#     chore_counter = 0
#
#     for commit in commits:
#         if commit.is_tagged:
#             # Reset to tagged version
#             major_t, minor_t, patch_t = parse_version(commit.inferred_version)
#             major, minor, patch = major_t, minor_t, patch_t
#             chore_counter = 0
#             result.append(commit)
#             continue
#
#         if commit.category == "feat":
#             minor += 1
#             patch = 0
#             chore_counter = 0
#             commit.inferred_version = format_version(major, minor, patch)
#         elif commit.category == "fix":
#             patch += 1
#             chore_counter = 0
#             commit.inferred_version = format_version(major, minor, patch)
#         else:  # chore
#             chore_counter += 1
#             commit.inferred_version = format_version(major, minor, patch, chore_counter)
#
#         result.append(commit)
#
#     return result
#
#
# def get_commits(repo_path: str, limit: int = 50) -> list[Commit]:
#     """Get commits from the repository (oldest first) using null-safe format."""
#     log_format = "%H%x00%h%x00%ci%x00%s"
#     output = run_git(repo_path, "log", f"--format={log_format}", f"-n", str(limit))
#     tags = get_tags(repo_path)
#
#     commits = []
#     for line in output.split("\x00"):
#         parts = line.split("\x00")
#         if len(parts) < 4:
#             continue
#         sha, short_sha, date, message = parts[0], parts[1], parts[2], parts[3]
#         category = classify_commit(message)
#         is_tagged = sha in tags
#         version = tags.get(sha, "")
#         commits.append(Commit(
#             sha=sha,
#             short_sha=short_sha,
#             date=date,
#             message=message,
#             category=category,
#             inferred_version=version,
#             is_tagged=is_tagged,
#         ))
#
#     # Git log returns newest first; reverse to oldest first
#     commits.reverse()
#     return commits
#
#
# def main():
#     parser = argparse.ArgumentParser(description="Infer versions for commits.")
#     parser.add_argument("--repo", required=True, help="Path to the git repository")
#     parser.add_argument("--base-version", default="v1.0.0", help="Base version to start from")
#     parser.add_argument("--limit", type=int, default=50, help="Number of commits to analyze")
#     parser.add_argument("--output", help="Path to write commit_versions.json")
#     args = parser.parse_args()
#
#     commits = get_commits(args.repo, limit=args.limit)
#     commits = infer_versions_forward(commits, args.base_version)
#
#     result = {
#         "base_version": args.base_version,
#         "commits": [asdict(c) for c in commits],
#     }
#
#     if args.output:
#         with open(args.output, "w", encoding="utf-8") as f:
#             json.dump(result, f, indent=2)
#
#     print(json.dumps(result, indent=2))
#
#
# if __name__ == "__main__":
#     main()
