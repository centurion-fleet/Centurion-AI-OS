"""
DocumentManager — Authoritative Document Reading and Publishing
================================================================
The single entry point for all document operations in Centurion OS.

Every Centurion MUST use DocumentManager to read or write tracked
documents. Direct file access bypasses the @latest indirection and
can cause version confusion across the fleet.

Usage:
    dm = DocumentManager()
    
    # Read the latest version (what every Centurion should do)
    content, meta = dm.read("centurion-business-plan")
    
    # Publish a new version (archives old, creates new @latest)
    dm.publish("centurion-business-plan", content, 
               published_by="Titus", summary="Updated pricing to £7,495")
    
    # Check what version is current
    status = dm.status("centurion-business-plan")
    
    # List all versions ever published
    history = dm.history("centurion-business-plan")
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Optional, Tuple

from .pointer import (
    DocumentVersion,
    _docs_root,
    _canonical_path,
    _archive_path,
    _pointer_path,
    read_pointer,
    write_pointer,
    resolve_latest,
    resolve_header,
    file_checksum,
    count_lines,
    LATEST_DIR,
    ARCHIVE_DIR,
    DOCS_DIR,
)
from .changelog import ChangelogEntry, append as changelog_append


class DocumentError(Exception):
    """Raised on document operations that cannot complete."""


class DocumentManager:
    """
    Document lifecycle manager with @latest pointer indirection.

    All document reads go through the pointer system so that every
    Centurion instance always sees the current version, regardless
    of when it last woke.
    """

    def __init__(self, docs_root: Optional[Path] = None):
        self._root = docs_root or _docs_root()
        self._ensure_dirs()

    # ── Public API ────────────────────────────────────────────────

    def read(self, name: str) -> Tuple[str, DocumentVersion]:
        """
        Read the current @latest version of a document.

        Returns (content, metadata).
        Raises DocumentError if the document has never been published.
        """
        pointer = read_pointer(name)
        if pointer is None:
            raise DocumentError(
                f"Document '{name}' has never been published. "
                f"Use publish() to create the first version."
            )

        path = resolve_latest(name)
        if path is None:
            raise DocumentError(
                f"Document '{name}' pointer exists but file not found at: "
                f"{pointer.path}"
            )

        content = path.read_text(encoding="utf-8")
        return content, pointer

    def publish(
        self,
        name: str,
        content: str,
        published_by: str = "centurion",
        summary: str = "",
    ) -> DocumentVersion:
        """
        Publish a new version of a document.

        - Archives the current version (if any) to docs/archive/
        - Writes the new content to docs/{name}@latest.md
        - Updates the @latest pointer
        - Logs the change in changelog.json

        Returns the metadata for the newly published version.
        """
        # Determine version number
        current = read_pointer(name)
        new_version = (current.version + 1) if current else 1

        # Archive old version if it exists
        if current:
            old_canonical = _canonical_path(name, current.version)
            if old_canonical.exists():
                archive_dest = _archive_path(name, current.version)
                archive_dest.parent.mkdir(parents=True, exist_ok=True)
                old_canonical.rename(archive_dest)

        # Write new content
        canonical = _canonical_path(name, new_version)
        canonical.parent.mkdir(parents=True, exist_ok=True)

        # Add metadata header to the file
        header = self._build_header(name, new_version, published_by)
        full_content = header + content
        canonical.write_text(full_content, encoding="utf-8")

        # Compute metadata
        checksum = file_checksum(canonical)
        lines = count_lines(canonical)
        byte_count = canonical.stat().st_size
        now = time.time()

        # Create pointer
        version = DocumentVersion(
            name=name,
            version=new_version,
            path=str(canonical),
            checksum=checksum,
            bytes=byte_count,
            lines=lines,
            published_at=now,
            published_by=published_by,
            summary=summary,
        )
        write_pointer(version)

        # Log changelog
        entry = ChangelogEntry(
            name=name,
            version=new_version,
            published_at=now,
            published_by=published_by,
            checksum=checksum,
            bytes=byte_count,
            lines=lines,
            summary=summary,
            previous_checksum=current.checksum if current else None,
        )
        changelog_append(entry)

        return version

    def status(self, name: str) -> Optional[dict]:
        """
        Get the current version status for a document.

        Returns dict with version info, or None if never published.
        """
        pointer = read_pointer(name)
        if pointer is None:
            return None

        path = resolve_latest(name)
        exists = path.exists() if path else False

        return {
            "name": pointer.name,
            "version": pointer.version,
            "path": pointer.path,
            "exists_on_disk": exists,
            "checksum": pointer.checksum,
            "bytes": pointer.bytes,
            "lines": pointer.lines,
            "published_at": pointer.published_at,
            "published_by": pointer.published_by,
            "summary": pointer.summary,
        }

    def history(self, name: str, limit: int = 20) -> list[dict]:
        """
        List the publication history for a document.

        Most recent first. Limited to `limit` entries.
        """
        from .changelog import list_entries
        return list_entries(name=name, limit=limit)

    def list_documents(self) -> list[str]:
        """
        List all documents that have ever been published.

        Scans the pointer directory.
        """
        pointer_dir = self._root / LATEST_DIR
        if not pointer_dir.exists():
            return []
        names = []
        for f in sorted(pointer_dir.iterdir()):
            if f.suffix == ".json":
                names.append(f.stem)
        return names

    def verify(self, name: str) -> dict:
        """
        Verify that the @latest pointer matches the actual file.

        Returns a dict with verification results.
        """
        pointer = read_pointer(name)
        if pointer is None:
            return {"status": "never_published", "name": name}

        path = resolve_latest(name)
        if path is None:
            return {"status": "missing_file", "name": name, "expected_path": pointer.path}

        actual_checksum = file_checksum(path)
        matches = actual_checksum == pointer.checksum

        return {
            "status": "verified" if matches else "checksum_mismatch",
            "name": name,
            "version": pointer.version,
            "expected_checksum": pointer.checksum,
            "actual_checksum": actual_checksum,
            "matches": matches,
            "path": str(path),
        }

    def get_header(self, name: str) -> dict:
        """
        Read the embedded metadata header from the @latest file.

        Returns empty dict if no header or file doesn't exist.
        """
        path = resolve_latest(name)
        if path is None:
            return {}
        return resolve_header(path)

    # ── Internal ──────────────────────────────────────────────────

    def _ensure_dirs(self) -> None:
        """Create required directory structure if it doesn't exist."""
        for sub in [DOCS_DIR, ARCHIVE_DIR, LATEST_DIR, f"{DOCS_DIR}/v1"]:
            (self._root / sub).mkdir(parents=True, exist_ok=True)

    def _build_header(self, name: str, version: int, author: str) -> str:
        """Build the YAML-style metadata header for embedding in the file."""
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        return (
            "---\n"
            f"name: {name}\n"
            f"version: {version}\n"
            f"published: {now}\n"
            f"published_by: {author}\n"
            f"---\n\n"
        )
