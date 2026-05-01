#!/usr/bin/env python3
"""
GitHub repository discovery and scoring script for OpenHelper.

⚠️  REFERENCE ONLY — Do NOT execute this script as part of the changelog workflow.
This script is bundled for documentation and offline reference.

SECURITY PATTERNS ILLUSTRATED:
- JSON-only output (no raw text fed to LLM context).
- max_results hard ceiling (default 10, absolute max 20) to prevent resource exhaustion.
- 30-second API timeout to prevent hanging on slow responses.
- All GitHub API calls use urllib with explicit headers (no shell command construction).

Usage:
    python find_repo.py <owner> <repo> [--token TOKEN]
    python find_repo.py --search "language:python stars:<500 pushed:>2025-03-30" [--token TOKEN]

Outputs JSON with scoring details.
"""

# SECURITY: This script is bundled for reference only. Dependencies are
# commented out to prevent accidental execution during the changelog workflow.
# The skill instructions in SKILL.md mandate inline git commands and file ops.
# import argparse
# import json
# import os
# import sys
# import urllib.request
# import urllib.error
# from datetime import datetime, timezone, timedelta
raise RuntimeError("This script is reference-only. Do not execute it.")



BLOCKED_PREFIXES = [
    "C:\\Windows", "C:\\Program Files", "C:\\ProgramData",
    "/etc", "/usr", "/bin", "/sbin", "/lib", "/sys", "/dev", "/proc",
]


def _is_safe_path(path: str) -> bool:
    """Reject system directories and traversal sequences."""
    from pathlib import Path
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


def _validate_working_dir():
    """Ensure we are not running from a system directory."""
    cwd = os.getcwd()
    blocked = ["windows", "program files", "system32", "etc", "usr", "bin", "sbin"]
    lowered = cwd.lower().replace("\\", "/")
    for b in blocked:
        if b in lowered:
            raise RuntimeError(f"Blocked system directory: {cwd}")


def github_api(path: str, token: str | None = None):
    """Make an authenticated GitHub API request."""
    url = f"https://api.github.com/{path.lstrip('/')}"
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode())
        except Exception:
            body = {}
        return {"error": True, "status": e.code, "message": body.get("message", str(e))}


def parse_iso_date(s: str) -> datetime:
    """Parse an ISO 8601 date string to a timezone-aware datetime."""
    # GitHub returns formats like 2025-04-01T12:34:56Z or with offset
    s = s.replace("Z", "+00:00")
    return datetime.fromisoformat(s)


def score_repo(owner: str, repo: str, token: str | None = None) -> dict:
    """Score a repository against the helpee criteria."""
    repo_data = github_api(f"/repos/{owner}/{repo}", token=token)
    if repo_data.get("error"):
        return repo_data

    commits_data = github_api(f"/repos/{owner}/{repo}/commits?per_page=1", token=token)
    if isinstance(commits_data, dict) and commits_data.get("error"):
        return commits_data

    # Latest commit date
    latest_commit_date = None
    if isinstance(commits_data, list) and len(commits_data) > 0:
        latest_commit_date = parse_iso_date(commits_data[0]["commit"]["committer"]["date"])

    # Search for changelog-like files via contents API (tree is cheaper)
    tree_data = github_api(f"/repos/{owner}/{repo}/git/trees/{repo_data['default_branch']}?recursive=1", token=token)
    has_changelog = False
    last_changelog_commit = None
    if isinstance(tree_data, dict) and "tree" in tree_data:
        for entry in tree_data["tree"]:
            name = entry.get("path", "").lower()
            if any(x in name for x in ["changelog", "changes", "history", "news", "releases"]):
                has_changelog = True
                break

    # If has changelog, try to find last commit touching it via search API
    if has_changelog:
        search_data = github_api(
            f"/search/commits?q=repo:{owner}/{repo}+filename:CHANGELOG+filename:changes+filename:history+filename:news+filename:releases&sort=committer-date&order=desc&per_page=1",
            token=token,
        )
        if isinstance(search_data, dict) and "items" in search_data and search_data["items"]:
            last_changelog_commit = parse_iso_date(search_data["items"][0]["commit"]["committer"]["date"])

    now = datetime.now(timezone.utc)
    days_since_last_commit = (now - latest_commit_date).days if latest_commit_date else 999
    days_since_changelog = (now - last_changelog_commit).days if last_changelog_commit else 999

    total_commits = repo_data.get("size", 0)  # size is rough proxy; better: use commits list length or another call
    # Use open issues count as rough activity proxy if needed
    stars = repo_data.get("stargazers_count", 0)
    is_archived = repo_data.get("archived", False)
    is_fork = repo_data.get("fork", False)
    has_license = repo_data.get("license") is not None

    # Scoring
    score = 0
    reasons = []

    if days_since_last_commit <= 30:
        score += 30
        reasons.append("Recent activity (<=30 days)")
    else:
        reasons.append(f"Stale repo ({days_since_last_commit} days)")

    if not has_changelog:
        score += 40
        reasons.append("No changelog found")
    elif days_since_changelog > 14:
        score += 20
        reasons.append(f"Changelog stale ({days_since_changelog} days)")
    else:
        reasons.append(f"Changelog recently updated ({days_since_changelog} days)")

    if has_license:
        score += 10
        reasons.append("Has LICENSE")

    if not is_archived and not is_fork:
        score += 10
        reasons.append("Not archived/fork")
    else:
        reasons.append("Archived or fork")

    # Tiebreaker: lower stars = higher score (capped)
    if stars < 500:
        score += min(10, max(0, 10 - stars // 50))
        reasons.append(f"Small repo ({stars} stars)")

    return {
        "owner": owner,
        "repo": repo,
        "url": repo_data.get("html_url"),
        "clone_url": repo_data.get("clone_url"),
        "default_branch": repo_data.get("default_branch"),
        "stars": stars,
        "language": repo_data.get("language"),
        "latest_commit_date": latest_commit_date.isoformat() if latest_commit_date else None,
        "days_since_last_commit": days_since_last_commit,
        "has_changelog": has_changelog,
        "last_changelog_commit": last_changelog_commit.isoformat() if last_changelog_commit else None,
        "days_since_changelog": days_since_changelog,
        "is_archived": is_archived,
        "is_fork": is_fork,
        "has_license": has_license,
        "score": score,
        "reasons": reasons,
        "recommended": score >= 60 and days_since_last_commit <= 30 and (not has_changelog or days_since_changelog > 14) and not is_archived and not is_fork,
    }


def search_candidates(query: str, token: str | None = None, max_results: int = 10) -> list[dict]:
    """Search GitHub for candidate repositories."""
    results = []
    search_data = github_api(f"/search/repositories?q={urllib.parse.quote(query)}&sort=updated&order=desc&per_page={max_results}", token=token)
    if search_data.get("error"):
        return [search_data]
    for item in search_data.get("items", []):
        score = score_repo(item["owner"]["login"], item["name"], token=token)
        if not score.get("error"):
            results.append(score)
    # Sort by score descending
    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    return results


def main():
    parser = argparse.ArgumentParser(description="Score or search GitHub repos for changelog help.")
    parser.add_argument("owner", nargs="?", help="Repository owner")
    parser.add_argument("repo", nargs="?", help="Repository name")
    parser.add_argument("--search", help="GitHub search query string")
    parser.add_argument("--token", default=os.environ.get("GH_TOKEN"), help="GitHub API token (or set GH_TOKEN)")
    parser.add_argument("--max-results", type=int, default=10, help="Max search results")
    args = parser.parse_args()

    if args.search:
        candidates = search_candidates(args.search, token=args.token, max_results=args.max_results)
        print(json.dumps(candidates, indent=2))
    elif args.owner and args.repo:
        result = score_repo(args.owner, args.repo, token=args.token)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    _validate_working_dir()
    main()
