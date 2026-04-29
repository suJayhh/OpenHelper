#!/usr/bin/env python3
"""
analyze_diff.py

Deterministic helper to summarize git diff statistics for PR review.
Outputs JSON with changed files grouped by directory and change magnitude.
"""

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


def run_git_diff_stat(repo_path: str, base_branch: str = "main"):
    """Run git diff --stat and parse the output."""
    cmd = ["git", "-C", repo_path, "diff", f"{base_branch}...HEAD", "--stat"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Try 'master' if 'main' fails
        if base_branch == "main":
            return run_git_diff_stat(repo_path, "master")
        print(f"Error running git diff: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def parse_diff_stat(diff_stat: str):
    """Parse git diff --stat output into structured data."""
    files = []
    for line in diff_stat.splitlines():
        # Skip empty lines and the summary line (ends with "N files changed...")
        if not line.strip() or "files changed" in line:
            continue

        # Format: " path/to/file |  10 +++---"
        parts = line.split("|")
        if len(parts) != 2:
            continue

        file_path = parts[0].strip()
        change_part = parts[1].strip()

        # Parse insertions/deletions
        insertions = change_part.count("+")
        deletions = change_part.count("-")
        total = insertions + deletions

        files.append({
            "path": file_path,
            "insertions": insertions,
            "deletions": deletions,
            "total_changes": total,
        })

    return files


def group_by_directory(files):
    """Group files by their parent directory."""
    groups = defaultdict(list)
    for f in files:
        directory = str(Path(f["path"]).parent)
        if directory == ".":
            directory = "root"
        groups[directory].append(f)
    return dict(groups)


def add_magnitude_flags(files):
    """Add a magnitude flag based on total changed lines."""
    for f in files:
        total = f["total_changes"]
        if total > 200:
            f["magnitude"] = "large"
        elif total > 50:
            f["magnitude"] = "medium"
        else:
            f["magnitude"] = "small"
    return files


def main():
    parser = argparse.ArgumentParser(description="Summarize git diff for PR review.")
    parser.add_argument("repo_path", help="Absolute or relative path to the target repository")
    parser.add_argument("base_branch", nargs="?", default="main", help="Base branch to compare against (default: main)")
    args = parser.parse_args()

    diff_stat = run_git_diff_stat(args.repo_path, args.base_branch)
    files = parse_diff_stat(diff_stat)
    files = add_magnitude_flags(files)
    grouped = group_by_directory(files)

    total_insertions = sum(f["insertions"] for f in files)
    total_deletions = sum(f["deletions"] for f in files)

    output = {
        "repo_path": str(Path(args.repo_path).resolve()),
        "base_branch": args.base_branch,
        "total_files": len(files),
        "total_insertions": total_insertions,
        "total_deletions": total_deletions,
        "grouped_files": grouped,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
