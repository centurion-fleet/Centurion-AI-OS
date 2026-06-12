"""
Changelog — Version History Tracking
====================================
Append-only log of every document version published.

Each entry records: name, version, date, author, checksum, summary.
The log is stored as a JSON array at docs/changelog.json and is
queryable by document name.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


@dataclass
class ChangelogEntry:
    """A single entry in the document changelog."""

    name: str
    version: int
    published_at: float
    published_by: str
    checksum: str
    bytes: int
    lines: int
    summary: str
    previous_checksum: Optional[str] = None


_CHANGELOG_PATH: Optional[Path] = None


def _get_path() -> Path:
    global _CHANGELOG_PATH
    if _CHANGELOG_PATH is None:
        val = os.environ.get("CENTURION_HOME", "").strip()
        home = Path(val) if val else Path.home() / ".centurion"
        _CHANGELOG_PATH = home / "docs" / "changelog.json"
    return _CHANGELOG_PATH


def _load() -> list[dict]:
    path = _get_path()
    if not path.exists():
        return []
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save(entries: list[dict]) -> None:
    path = _get_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(entries, f, indent=2)


def append(entry: ChangelogEntry) -> None:
    """Append a changelog entry and persist."""
    entries = _load()
    entries.append(asdict(entry))
    _save(entries)


def list_entries(name: Optional[str] = None, limit: int = 20) -> list[dict]:
    """
    List changelog entries, optionally filtered by document name.

    Most recent first. Capped at `limit`.
    """
    entries = _load()
    if name:
        entries = [e for e in entries if e.get("name") == name]
    entries.reverse()  # Most recent first
    return entries[:limit]


def last_version(name: str) -> Optional[int]:
    """Get the latest version number for a document."""
    entries = [e for e in _load() if e.get("name") == name]
    if not entries:
        return None
    return max(e["version"] for e in entries)


def last_checksum(name: str) -> Optional[str]:
    """Get the checksum of the most recent version."""
    entries = [e for e in _load() if e.get("name") == name]
    if not entries:
        return None
    return max(entries, key=lambda e: e["version"]).get("checksum")
