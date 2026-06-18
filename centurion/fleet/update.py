"""Centurion Fleet Update Manager.

Allows each Centurion to check for upstream updates, selectively
apply commits, and roll back changes. The Centurion can operate
autonomously based on policy, or flag decisions for their manager.

Architecture:
    upstream (origin/main)
         │
    git fetch upstream
         │
    check commits → apply policy
         │              │
    auto-merge      flag for manager
    (security,fix)  (feat,refactor)
"""

import logging
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Default upstream — the canonical Centurion OS repo
DEFAULT_UPSTREAM = "https://github.com/centurion-fleet/Centurion-AI-OS.git"
UPSTREAM_REMOTE = "upstream"

COMMIT_CATEGORIES = {
    "security": re.compile(r"^(security|sec|CVE|fix.*security)", re.IGNORECASE),
    "fix": re.compile(r"^(fix|bugfix|hotfix|patch)", re.IGNORECASE),
    "feat": re.compile(r"^(feat|feature|add|new)", re.IGNORECASE),
    "refactor": re.compile(r"^(refactor|refact|restructure|cleanup)", re.IGNORECASE),
    "deprecation": re.compile(r"^(deprecat|breaking|remove|drop|migrat|rename)", re.IGNORECASE),
    "docs": re.compile(r"^(docs|doc|readme|comment)", re.IGNORECASE),
    "chore": re.compile(r"^(chore|ci|build|test|style)", re.IGNORECASE),
}


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def _git(*args: str, repo: Optional[Path] = None) -> str:
    """Run a git command in the repo directory. Returns stdout."""
    cwd = repo or Path.cwd()
    cmd = ["git"] + list(args)
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
        return r.stdout.strip()
    except FileNotFoundError:
        raise RuntimeError("git is not installed on this system")
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"git {' '.join(args)} timed out after 60s")


def _ensure_upstream_remote(repo: Optional[Path] = None) -> None:
    """Ensure the 'upstream' remote exists, adding it if needed."""
    remotes = _git("remote", repo=repo)
    if UPSTREAM_REMOTE not in remotes:
        _git("remote", "add", UPSTREAM_REMOTE, DEFAULT_UPSTREAM, repo=repo)
        logger.info("Added upstream remote: %s", DEFAULT_UPSTREAM)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def check_upstream(repo: Optional[Path] = None) -> List[Dict]:
    """Check what commits are available from upstream that are not in fork.

    Returns list of commit dicts: {hash, author, date, subject, category}
    """
    repo = repo or Path.cwd()
    _ensure_upstream_remote(repo)
    _git("fetch", UPSTREAM_REMOTE, repo=repo)

    # List commits on upstream/main not reachable from HEAD
    raw = _git("log", "--oneline", f"HEAD..{UPSTREAM_REMOTE}/main", repo=repo)

    if not raw:
        return []

    commits = []
    for line in raw.split("\n"):
        if not line.strip():
            continue
        parts = line.strip().split(" ", 1)
        h = parts[0]
        subject = parts[1] if len(parts) > 1 else ""

        # Get full details
        details = _git("log", "-1", "--format=%H|%an|%ai|%s", h, repo=repo)
        if details:
            d_parts = details.split("|", 3)
            full_hash = d_parts[0] if len(d_parts) > 0 else h
            author = d_parts[1] if len(d_parts) > 1 else "unknown"
            date = d_parts[2] if len(d_parts) > 2 else ""
            full_subject = d_parts[3] if len(d_parts) > 3 else subject
        else:
            full_hash = h
            author = "unknown"
            date = ""
            full_subject = subject

        # Categorise the commit
        category = "other"
        for cat, pattern in COMMIT_CATEGORIES.items():
            if pattern.search(full_subject):
                category = cat
                break

        commits.append({
            "hash": full_hash[:12],
            "full_hash": full_hash,
            "author": author,
            "date": date,
            "subject": full_subject,
            "category": category,
        })

    return commits


def get_status(repo: Optional[Path] = None) -> Dict:
    """Return the current divergence status between fork and upstream."""
    repo = repo or Path.cwd()
    _ensure_upstream_remote(repo)
    _git("fetch", UPSTREAM_REMOTE, repo=repo)

    behind = _git("rev-list", "--count", f"HEAD..{UPSTREAM_REMOTE}/main", repo=repo)
    ahead = _git("rev-list", "--count", f"{UPSTREAM_REMOTE}/main..HEAD", repo=repo)

    return {
        "behind": int(behind),
        "ahead": int(ahead),
        "upstream": DEFAULT_UPSTREAM,
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD", repo=repo),
        "last_fetch": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


def apply_commit(hash: str, repo: Optional[Path] = None) -> Dict:
    """Cherry-pick a single commit from upstream into the fork.

    Returns: {success: bool, message: str, commit: str}
    """
    repo = repo or Path.cwd()
    _ensure_upstream_remote(repo)

    # Verify the commit exists in upstream
    try:
        _git("fetch", UPSTREAM_REMOTE, repo=repo)
        _git("log", "-1", "--format=%H", hash, repo=repo)
    except RuntimeError as e:
        return {"success": False, "message": f"Commit {hash[:12]} not found: {e}", "commit": hash}

    try:
        _git("cherry-pick", hash, repo=repo)
        short = _git("log", "-1", "--format=%h", "HEAD", repo=repo)
        subject = _git("log", "-1", "--format=%s", "HEAD", repo=repo)
        return {
            "success": True,
            "message": f"Applied {short}: {subject}",
            "commit": short,
        }
    except RuntimeError as e:
        # Abort the cherry-pick if it failed
        try:
            _git("cherry-pick", "--abort", repo=repo)
        except RuntimeError:
            pass
        return {"success": False, "message": f"Cherry-pick failed: {e}", "commit": hash}


def apply_policy(repo: Optional[Path] = None) -> Dict:
    """Apply auto-merge policy: merge security and fix commits automatically.

    Returns summary of what was merged and what was flagged.
    """
    repo = repo or Path.cwd()
    commits = check_upstream(repo)

    if not commits:
        return {"merged": [], "flagged": [], "message": "Already up to date"}

    merged = []
    flagged = []

    for c in commits:
        if c["category"] in ("security", "fix"):
            result = apply_commit(c["full_hash"], repo)
            if result["success"]:
                merged.append(c)
            else:
                flagged.append({**c, "reason": result["message"]})
        else:
            flagged.append({**c, "reason": "Requires manager review"})

    parts = []
    if merged:
        parts.append(f"Merged {len(merged)} commit(s) automatically")
    if flagged:
        parts.append(f"Flagged {len(flagged)} commit(s) for review")

    return {
        "merged": merged,
        "flagged": flagged,
        "message": " — ".join(parts) if parts else "Nothing to do",
    }


def rollback(repo: Optional[Path] = None) -> Dict:
    """Revert the last applied commit."""
    repo = repo or Path.cwd()
    try:
        last = _git("log", "-1", "--format=%h|%s", "HEAD", repo=repo)
        if not last:
            return {"success": False, "message": "No commits to roll back"}
        parts = last.split("|", 1)
        h, subject = parts[0], parts[1] if len(parts) > 1 else ""

        _git("revert", "--no-edit", "HEAD", repo=repo)
        return {
            "success": True,
            "message": f"Reverted {h}: {subject}",
            "commit": h,
        }
    except RuntimeError as e:
        return {"success": False, "message": f"Rollback failed: {e}"}


def set_upstream(url: str, repo: Optional[Path] = None) -> Dict:
    """Set or change the upstream remote URL."""
    repo = repo or Path.cwd()
    remotes = _git("remote", repo=repo)
    if UPSTREAM_REMOTE in remotes:
        _git("remote", "set-url", UPSTREAM_REMOTE, url, repo=repo)
    else:
        _git("remote", "add", UPSTREAM_REMOTE, url, repo=repo)
    return {"success": True, "message": f"Upstream set to {url}"}
