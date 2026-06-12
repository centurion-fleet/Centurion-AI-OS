"""
CenturionOS — Document Versioning System (@latest Pointer)
===========================================================
Authoritative document management for the Centurion fleet.

Every document lives at a stable path with a `@latest` alias.
No Centurion ever refers to a bare filename — they always
resolve through the @latest pointer, ensuring every instance
reads the current version regardless of when it last woke.

Modules:
- manager   — DocumentManager: read, publish, archive, status
- pointer   — PointerFile: @latest resolution and version tracking
- changelog — Version history logging
"""

from .manager import DocumentManager
from .pointer import DocumentVersion
from .changelog import ChangelogEntry, append as changelog_append, list_entries, last_version, last_checksum

__all__ = [
    "DocumentManager",
    "DocumentVersion",
    "ChangelogEntry",
    "changelog_append",
    "list_entries",
    "last_version",
    "last_checksum",
]
