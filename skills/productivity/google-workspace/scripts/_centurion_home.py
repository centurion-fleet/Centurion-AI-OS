"""Resolve CENTURION_HOME for standalone skill scripts.

Skill scripts may run outside the Centurion process (e.g. system Python,
nix env, CI) where ``centurion_constants`` is not importable.  This module
provides the same ``get_centurion_home()`` and ``display_centurion_home()``
contracts as ``centurion_constants`` without requiring it on ``sys.path``.

When ``centurion_constants`` IS available it is used directly so that any
future enhancements (profile resolution, Docker detection, etc.) are
picked up automatically.  The fallback path replicates the core logic
from ``centurion_constants.py`` using only the stdlib.

All scripts under ``google-workspace/scripts/`` should import from here
instead of duplicating the ``CENTURION_HOME = Path(os.getenv(...))`` pattern.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from centurion_constants import display_centurion_home as display_centurion_home
    from centurion_constants import get_centurion_home as get_centurion_home
except (ModuleNotFoundError, ImportError):

    def get_centurion_home() -> Path:
        """Return the Centurion home directory (default: ~/.centurion).

        Mirrors ``centurion_constants.get_centurion_home()``."""
        val = os.environ.get("CENTURION_HOME", "").strip()
        return Path(val) if val else Path.home() / ".centurion"

    def display_centurion_home() -> str:
        """Return a user-friendly ``~/``-shortened display string.

        Mirrors ``centurion_constants.display_centurion_home()``."""
        home = get_centurion_home()
        try:
            return "~/" + str(home.relative_to(Path.home()))
        except ValueError:
            return str(home)
