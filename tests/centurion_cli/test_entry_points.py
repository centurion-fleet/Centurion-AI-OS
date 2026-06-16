"""Smoke tests for centurion CLI entry points."""

from __future__ import annotations

import subprocess
import sys

import pytest
from importlib.metadata import entry_points


def test_console_script_entry_point():
    eps = entry_points(group="console_scripts")
    centurion = next((ep for ep in eps if ep.name == "centurion"), None)
    assert centurion is not None
    assert centurion.value == "centurion_cli.main:main"


@pytest.mark.parametrize(
    "args",
    [
        ["--help"],
        ["fleet", "status"],
    ],
)
def test_centurion_cli_subprocess_smoke(args: list[str]):
    result = subprocess.run(
        [sys.executable, "-m", "centurion_cli.main", *args],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr or result.stdout
