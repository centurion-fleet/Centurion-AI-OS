"""Centurion subscription billing gate.

Until ``portal.personal-centurion.com`` is live, billing stays disabled and
Nous/Centurion Portal OAuth is blocked. Users configure bring-your-own-key
providers via ``centurion setup`` / ``centurion model`` instead.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

DEFAULT_CENTURION_PORTAL_URL = "https://portal.personal-centurion.com"
DEFAULT_CENTURION_INFERENCE_URL = "https://inference-api.personal-centurion.com/v1"
DEFAULT_CENTURION_CLIENT_ID = "centurion-cli"


def is_billing_enabled(config: Optional[Dict[str, Any]] = None) -> bool:
    """Return True when Centurion subscription billing is enabled."""
    if config is None:
        from centurion_cli.config import load_config

        config = load_config() or {}
    billing = config.get("billing")
    if not isinstance(billing, dict):
        return False
    from utils import is_truthy_value

    return is_truthy_value(billing.get("enabled"), default=False)


def billing_unavailable_message() -> str:
    """User-facing message when subscription billing is not yet available."""
    return (
        "Centurion subscription billing is not available yet.\n"
        "  Configure a provider with your own API key instead:\n"
        "    centurion setup\n"
        "    centurion model\n"
        f"  Subscription portal (coming soon): {DEFAULT_CENTURION_PORTAL_URL}"
    )
