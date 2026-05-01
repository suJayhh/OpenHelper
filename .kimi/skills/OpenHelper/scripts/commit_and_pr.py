#!/usr/bin/env python3
"""
Commit changelog changes, fork the repo, push a branch, and open a PR.

⚠️  REFERENCE ONLY — Do NOT execute this script as part of the changelog workflow.
The skill instructions in SKILL.md mandate inline git commands and file operations.
This script is bundled for documentation and offline reference.

Usage:
    python commit_and_pr.py --repo <repo_path> --owner <upstream_owner> --repo-name <upstream_repo> \
        [--branch-name <name>] [--commit-msg <msg>] [--username <github_user>]

Environment:
    GITHUB_USERNAME - fallback if --username not provided
"""

# SECURITY: This script is bundled for reference only. Dependencies are
# commented out to prevent accidental execution during the changelog workflow.
# The skill instructions in SKILL.md mandate inline git commands and file ops.
# import argparse
# import json
# import os
# import subprocess
# import sys
# from datetime import datetime
# from pathlib import Path
raise RuntimeError("This script is reference-only. Do not execute it.")


BLOCKED_PREFIXES = [
    "C:\\Windows", "C:\\Program Files", "C:\\ProgramData",
    "/etc", "/usr", "/bin", "/sbin", "/lib", "/sys", "/dev", "/proc",
]


def _is_safe_path(path: str) -> bool:
    """Reject system directories and traversal sequences."""
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
    return True


def _validate_git_repo(repo_path: str) -> None:
    """Ensure the path contains a .git directory."""
    git_dir = Path(repo_path) / ".git"
    if not git_dir.is_dir():
        raise RuntimeError(f"Not a git repository: {repo_path}")


def run(cmd: list[str], cwd: str | None = None, check: bool = True) -> str:
    if cwd and not _is_safe_path(cwd):
        raise RuntimeError(f"Unsafe working directory rejected: {cwd}")
    if cwd:
        _validate_git_repo(cwd)
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore", cwd=cwd)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr}")
    return result.stdout.strip()


def get_github_username() -> str:
    """Get GitHub username from gh CLI."""
    try:
        return run(["gh", "api", "user", "-q", ".login"])
    except RuntimeError:
        username = os.environ.get("GITHUB_USERNAME")
        if username:
            return username
        raise RuntimeError("Could not determine GitHub username. Set GITHUB_USERNAME or run `gh auth login`.")


def ensure_branch(repo_path: str, branch_name: str) -> str:
    """Create a new branch. If name collision, append timestamp."""
    try:
        run(["git", "-C", repo_path, "checkout", "-b", branch_name], check=False)
        return branch_name
    except RuntimeError:
        # Likely branch exists
        suffix = datetime.now().strftime("%Y%m%d%H%M%S")
        new_name = f"{branch_name}-{suffix}"
        run(["git", "-C", repo_path, "checkout", "-b", new_name])
        return new_name


def fork_repo(owner: str, repo: str) -> str:
    """Fork the target repository via gh CLI. Returns fork owner."""
    try:
        result = run(["gh", "repo", "fork", f"{owner}/{repo}", "--default-branch-only", "--clone=false"])
        print(result)
    except RuntimeError as e:
        # May already be forked
        print(f"Fork may already exist: {e}")
    return get_github_username()


def push_to_fork(repo_path: str, fork_owner: str, repo: str, branch: str):
    """Add fork remote and push branch."""
    remote_url = f"https://github.com/{fork_owner}/{repo}.git"
    # Check if remote already exists
    try:
        remotes = run(["git", "-C", repo_path, "remote", "-v"])
        if "fork" not in remotes:
            run(["git", "-C", repo_path, "remote", "add", "fork", remote_url])
        else:
            run(["git", "-C", repo_path, "remote", "set-url", "fork", remote_url])
    except RuntimeError:
        run(["git", "-C", repo_path, "remote", "add", "fork", remote_url])

    run(["git", "-C", repo_path, "push", "-u", "fork", branch])


def create_pr(owner: str, repo: str, branch: str, username: str) -> str:
    """Create a PR using gh CLI. Returns PR URL."""
    title = "docs: add/update changelog"
    body = (
        "This PR adds or updates the project changelog to document recent changes.\n\n"
        "Generated with [OpenHelper](https://github.com/suJayhh/OpenHelper)."
    )
    try:
        result = run([
            "gh", "pr", "create",
            "--repo", f"{owner}/{repo}",
            "--title", title,
            "--body", body,
            "--head", f"{username}:{branch}",
        ])
        return result
    except RuntimeError as e:
        # Fallback: print manual URL
        manual_url = f"https://github.com/{owner}/{repo}/compare/main...{username}:{branch}"
        print(f"gh pr create failed: {e}")
        print(f"Manual PR URL: {manual_url}")
        return manual_url


def main():
    parser = argparse.ArgumentParser(description="Commit and open PR for changelog.")
    parser.add_argument("--repo", required=True, help="Path to local git repository")
    parser.add_argument("--owner", required=True, help="Upstream repository owner")
    parser.add_argument("--repo-name", required=True, help="Upstream repository name")
    parser.add_argument("--branch-name", default="chore/update-changelog", help="Feature branch name")
    parser.add_argument("--commit-msg", default="chore|docs: changelog", help="Commit message")
    parser.add_argument("--username", help="GitHub username (or set GITHUB_USERNAME)")
    parser.add_argument("--no-verify", action="store_true", help="Pass --no-verify to git commit")
    args = parser.parse_args()

    username = args.username or get_github_username()

    # Ensure branch
    branch = ensure_branch(args.repo, args.branch_name)
    print(f"Using branch: {branch}")

    # Stage and commit
    run(["git", "-C", args.repo, "add", "-A"])
    commit_cmd = ["git", "-C", args.repo, "commit", "-m", args.commit_msg]
    if args.no_verify:
        commit_cmd.append("--no-verify")
    try:
        run(commit_cmd)
    except RuntimeError as e:
        # Nothing to commit
        print(f"Commit failed (maybe nothing to commit?): {e}")
        sys.exit(0)

    # Fork and push
    fork_owner = fork_repo(args.owner, args.repo_name)
    push_to_fork(args.repo, fork_owner, args.repo_name, branch)

    # Create PR
    pr_result = create_pr(args.owner, args.repo_name, branch, username)
    print(f"PR result: {pr_result}")

    output = {
        "branch": branch,
        "fork_owner": fork_owner,
        "upstream": f"{args.owner}/{args.repo_name}",
        "pr_url": pr_result if pr_result.startswith("http") else None,
        "pr_cli_output": pr_result,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
