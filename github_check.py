#!/usr/bin/env python3
"""
Check GitHub for recent commits.

Usage:
    python github_check.py                    # Last 10 commits
    python github_check.py <since_sha>        # Commits since SHA
"""

import json
import sys
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Try multiple .env locations
for env_path in [Path(".env"), Path.home() / ".marketing-bot" / ".env"]:
    if env_path.exists():
        load_dotenv(env_path)
        break
else:
    load_dotenv()  # fall back to environment variables

REPO = os.getenv("GITHUB_REPO", "tianzhicdev/alittlebitofmoney")
TOKEN = os.getenv("GITHUB_TOKEN")


def get_commits(since_sha=None, limit=10):
    url = f"https://api.github.com/repos/{REPO}/commits"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"
    
    params = {"per_page": limit}
    
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        all_commits = resp.json()
    except requests.RequestException as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
    
    # Format commits
    commits = []
    for c in all_commits:
        sha = c["sha"]
        
        # Stop if we've reached the since_sha
        if since_sha and sha == since_sha:
            break
        
        commits.append({
            "sha": sha,
            "message": c["commit"]["message"].split("\n")[0],  # First line only
            "full_message": c["commit"]["message"],
            "date": c["commit"]["author"]["date"],
            "author": c["commit"]["author"]["name"],
        })
    
    # Get files changed for each commit (separate API calls, limited to first 5)
    for commit in commits[:5]:
        try:
            detail_url = f"https://api.github.com/repos/{REPO}/commits/{commit['sha']}"
            detail_resp = requests.get(detail_url, headers=headers, timeout=15)
            detail_resp.raise_for_status()
            detail = detail_resp.json()
            commit["files_changed"] = [f["filename"] for f in detail.get("files", [])]
        except requests.RequestException:
            commit["files_changed"] = []
    
    return commits


def main():
    since_sha = sys.argv[1] if len(sys.argv) > 1 else None
    commits = get_commits(since_sha)
    
    output = {
        "repo": REPO,
        "since_sha": since_sha,
        "commit_count": len(commits),
        "commits": commits
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
