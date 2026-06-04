#!/usr/bin/env python3
"""Fleet health check — reports status of all Centurion branches and their divergence from develop."""

import subprocess, json, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
CENTURIONS = ["titus", "eve", "adam"]

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    return r.stdout.strip(), r.returncode

def main():
    print("🦅 Centurion Fleet Health Check")
    print("=" * 50)

    # Fetch latest
    run(["git", "fetch", "--all", "--quiet"])

    # Get develop latest
    dev_hash, _ = run(["git", "rev-parse", "origin/develop"])

    for name in CENTURIONS:
        hash_, rc = run(["git", "rev-parse", f"origin/{name}"])
        if rc != 0:
            print(f"\n❌ {name} — branch not found on origin")
            continue

        ahead_behind_str, _ = run(["git", "rev-list", "--left-right", "--count", f"{name}...origin/develop"])
        if ahead_behind_str:
            parts = ahead_behind_str.split()
            behind = parts[-1] if len(parts) == 2 else "0"
        else:
            behind = "0"

        status = "✅" if behind == "0" else "⚠️"
        behind_msg = f"behind develop by {behind} commits" if behind != "0" else "up to date with develop"

        print(f"\n{status} {name}")
        print(f"   {behind_msg}")

    print("\n" + "=" * 50)
    print("Fleet health check complete.")

if __name__ == "__main__":
    main()
