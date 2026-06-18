"""Fleet cloud check-in helpers for ``centurion fleet checkin --cloud``."""

from __future__ import annotations

import os
import sys


def cloud_checkin_from_cli() -> int:
    """POST local fleet status to the Centurion website API."""
    from centurion_cli.cloud_client import fleet_checkin_to_cloud
    from centurion_cli.config import load_config

    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        print("Error: OPENROUTER_API_KEY not set. Run centurion setup first.")
        return 1

    config = load_config() or {}
    pending: dict[str, int] = {}
    try:
        from centurion.fleet import update as fleet_update

        status = fleet_update.get_status()
        behind = int(status.get("behind", 0) or 0)
        pending = {"security": behind, "feat": int(status.get("ahead", 0) or 0)}
    except Exception:
        pending = {}

    result = fleet_checkin_to_cloud(api_key, config=config, pending_updates=pending)
    if result.get("ok"):
        print("✅ Fleet check-in sent to Centurion cloud")
        if result.get("policy"):
            print(f"   Update policy: {result['policy']}")
        return 0

    print(f"❌ Cloud check-in failed: {result.get('error', 'unknown error')}")
    return 1
