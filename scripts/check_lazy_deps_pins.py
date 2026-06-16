#!/usr/bin/env python3
"""Ensure tools/lazy_deps.py pins match pyproject.toml optional extras."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
LAZY_DEPS = ROOT / "tools" / "lazy_deps.py"

_PKG_RE = re.compile(r"^([a-zA-Z0-9_.-]+)==([0-9.]+)")


def _parse_pyproject_extras() -> dict[str, str]:
    text = PYPROJECT.read_text(encoding="utf-8")
    pins: dict[str, str] = {}
    in_optional = False
    for line in text.splitlines():
        if line.strip() == "[project.optional-dependencies]":
            in_optional = True
            continue
        if in_optional and line.startswith("["):
            break
        if not in_optional:
            continue
        for match in re.finditer(r'"([a-zA-Z0-9_.-]+)==([0-9.]+)"', line):
            name, ver = match.group(1), match.group(2)
            pins[name] = ver
    return pins


def _parse_lazy_deps() -> dict[str, str]:
  text = LAZY_DEPS.read_text(encoding="utf-8")
  pins: dict[str, str] = {}
  for match in re.finditer(r'"([a-zA-Z0-9_.-]+)==([0-9.]+)"', text):
      name, ver = match.group(1), match.group(2)
      pins[name] = ver
  return pins


def main() -> int:
    py_pins = _parse_pyproject_extras()
    lazy_pins = _parse_lazy_deps()
    mismatches: list[str] = []
    for pkg, lazy_ver in lazy_pins.items():
        if pkg not in py_pins:
            continue
        if py_pins[pkg] != lazy_ver:
            mismatches.append(
                f"{pkg}: pyproject=={py_pins[pkg]} lazy_deps=={lazy_ver}"
            )
    if mismatches:
        print("lazy_deps pin drift detected:", file=sys.stderr)
        for line in mismatches:
            print(f"  - {line}", file=sys.stderr)
        return 1
    print(f"OK: {len(lazy_pins)} lazy_deps pins checked against optional extras")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
