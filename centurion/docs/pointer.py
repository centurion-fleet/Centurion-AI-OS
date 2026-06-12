"""
PointerFile — @latest Resolution and Version Tracking
======================================================
Resolves and manages the @latest pointer for any tracked document.

A pointer file is a small JSON document (or symlink) that maps
a logical document name to its current physical path. Every
Centurion reads documents through this indirection, ensuring
all instances always see the current version.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class DocumentVersion:
    """Metadata for a single version of a tracked document."""

    name: str
    version: int
    path: str
    checksum: str
    bytes: int
    lines: int
    published_at: float
    published_by: str = "unknown"
    summary: str = ""


# ── Path conventions ─────────────────────────────────────────────

DOCS_DIR = "docs"
ARCHIVE_DIR = "docs/archive"
LATEST_DIR = "docs/latest"
POINTER_EXT = ".pointer.json"


def _centurion_home() -> Path:
    """Resolve CENTURION_HOME or default to ~/.centurion."""
    val = os.environ.get("CENTURION_HOME", "").strip()
    return Path(val) if val else Path.home() / ".centurion"


def _docs_root() -> Path:
    """Return the root docs directory under CENTURION_HOME."""
    return _centurion_home() / DOCS_DIR


def _pointer_path(name: str) -> Path:
    """Return the path to the pointer file for a document name."""
    return _docs_root() / LATEST_DIR / f"{name}{POINTER_EXT}"


def _versioned_path(name: str, version: int) -> Path:
    """Return the path for a specific version of a document."""
    return _docs_root() / f"v{version}" / f"{name}.md"


def _archive_path(name: str, version: int) -> Path:
    """Return the archive path for an old version."""
    ts = time.strftime("%Y%m%d-%H%M%S")
    return _docs_root() / ARCHIVE_DIR / f"{name}-v{version}-{ts}.md"


def _canonical_path(name: str, version: int) -> Path:
    """Return the in-place canonical path (the one @latest aliases)."""
    return _docs_root() / f"{name}@latest.md"


# ── Checksum ─────────────────────────────────────────────────────

def file_checksum(path: Path) -> str:
    """SHA-256 hex digest of file contents."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def count_lines(path: Path) -> int:
    """Count lines in a text file."""
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)


# ── Pointer operations ────────────────────────────────────────────

def read_pointer(name: str) -> Optional[DocumentVersion]:
    """
    Read the @latest pointer for a document.

    Returns None if the document has never been published.
    """
    p = _pointer_path(name)
    if not p.exists():
        return None
    try:
        with open(p, "r") as f:
            data = json.load(f)
        return DocumentVersion(**data)
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


def write_pointer(version: DocumentVersion) -> None:
    """Write (or update) the @latest pointer for a document."""
    p = _pointer_path(version.name)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump({
            "name": version.name,
            "version": version.version,
            "path": version.path,
            "checksum": version.checksum,
            "bytes": version.bytes,
            "lines": version.lines,
            "published_at": version.published_at,
            "published_by": version.published_by,
            "summary": version.summary,
        }, f, indent=2)


def resolve_latest(name: str) -> Optional[Path]:
    """
    Resolve a document name to its @latest file path.

    The Centurion always uses this before reading any tracked doc.
    Returns None if no version has been published.
    """
    pointer = read_pointer(name)
    if pointer is None:
        return None
    p = Path(pointer.path)
    if p.exists():
        return p
    # Fallback: try canonical path
    cp = _canonical_path(name, pointer.version)
    if cp.exists():
        return cp
    return None


def resolve_header(path: Path) -> dict:
    """
    Read the metadata header embedded in a @latest file.

    The first lines of the file contain YAML-like metadata:
    ---
    name: centurion-business-plan
    version: 3
    published: 2026-06-12T09:08:00Z
    checksum: abc123...
    ---
    Returns empty dict if no header is found.
    """
    meta: dict = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines(20)  # Read only header area
        if lines and lines[0].strip() == "---":
            for line in lines[1:]:
                line = line.strip()
                if line == "---":
                    break
                if ":" in line:
                    k, _, v = line.partition(":")
                    meta[k.strip()] = v.strip()
    except (OSError, UnicodeDecodeError):
        pass
    return meta
