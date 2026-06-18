"""Centurion cloud API client — subscription validation and fleet check-in."""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

_CACHE_TTL_SECONDS = 24 * 60 * 60
_CACHE_FILENAME = "cloud_validation_cache.json"


@dataclass
class ValidationResult:
    valid: bool
    plan: Optional[str] = None
    credits_remaining_usd: Optional[float] = None
    subscription_status: Optional[str] = None
    key_expires_at: Optional[str] = None
    error: Optional[str] = None


def _cache_path() -> Path:
    from centurion_constants import get_centurion_home

    return get_centurion_home() / _CACHE_FILENAME


def _read_cache(api_key: str) -> Optional[ValidationResult]:
    path = _cache_path()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("key_hash") != _key_fingerprint(api_key):
            return None
        if time.time() - float(data.get("cached_at", 0)) > _CACHE_TTL_SECONDS:
            return None
        return ValidationResult(
            valid=bool(data.get("valid")),
            plan=data.get("plan"),
            credits_remaining_usd=data.get("credits_remaining_usd"),
            subscription_status=data.get("subscription_status"),
            key_expires_at=data.get("key_expires_at"),
            error=data.get("error"),
        )
    except Exception:
        return None


def _write_cache(api_key: str, result: ValidationResult) -> None:
    path = _cache_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "key_hash": _key_fingerprint(api_key),
                    "cached_at": time.time(),
                    "valid": result.valid,
                    "plan": result.plan,
                    "credits_remaining_usd": result.credits_remaining_usd,
                    "subscription_status": result.subscription_status,
                    "key_expires_at": result.key_expires_at,
                    "error": result.error,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    except Exception as exc:
        logger.debug("Could not write cloud validation cache: %s", exc)


def _key_fingerprint(api_key: str) -> str:
    import hashlib

    return hashlib.sha256(api_key.strip().encode()).hexdigest()


def get_fleet_api_base(config: Optional[Dict[str, Any]] = None) -> str:
    if config is None:
        from centurion_cli.config import load_config

        config = load_config() or {}
    billing = config.get("billing") if isinstance(config.get("billing"), dict) else {}
    fleet_url = (billing or {}).get("fleet_api_url") or (billing or {}).get("portal_url") or ""
    fleet_url = str(fleet_url).rstrip("/")
    if fleet_url.endswith("/api/v1"):
        return fleet_url
    if fleet_url:
        return f"{fleet_url}/api/v1"
    return "https://www.personal-centurion.com/api/v1"


def _post_json(url: str, payload: Dict[str, Any], timeout: float = 15.0) -> Dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def validate_subscription_key(
    api_key: str,
    *,
    config: Optional[Dict[str, Any]] = None,
    use_cache: bool = True,
) -> ValidationResult:
    """Validate a Centurion-issued OpenRouter key against the website API."""
    trimmed = (api_key or "").strip()
    if not trimmed:
        return ValidationResult(valid=False, error="Empty API key")

    if use_cache:
        cached = _read_cache(trimmed)
        if cached is not None:
            return cached

    base = get_fleet_api_base(config)
    url = f"{base}/keys/validate"
    try:
        data = _post_json(url, {"api_key": trimmed})
    except HTTPError as exc:
        try:
            detail = json.loads(exc.read().decode("utf-8"))
        except Exception:
            detail = {"error": str(exc)}
        result = ValidationResult(valid=False, error=detail.get("error") or str(exc))
        _write_cache(trimmed, result)
        return result
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        logger.debug("Cloud validation unavailable: %s", exc)
        return ValidationResult(valid=False, error=f"Cloud API unavailable: {exc}")

    result = ValidationResult(
        valid=bool(data.get("valid")),
        plan=data.get("plan"),
        credits_remaining_usd=data.get("credits_remaining_usd"),
        subscription_status=data.get("subscription_status"),
        key_expires_at=data.get("key_expires_at"),
        error=data.get("error"),
    )
    _write_cache(trimmed, result)
    return result


def get_install_id() -> str:
    """Stable install ID persisted under CENTURION_HOME."""
    from centurion_constants import get_centurion_home

    path = get_centurion_home() / "install_id"
    if path.exists():
        existing = path.read_text(encoding="utf-8").strip()
        if existing:
            return existing
    install_id = str(uuid.uuid4())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(install_id, encoding="utf-8")
    return install_id


def fleet_checkin_to_cloud(
    api_key: str,
    *,
    config: Optional[Dict[str, Any]] = None,
    install_id: Optional[str] = None,
    version: Optional[str] = None,
    hostname: Optional[str] = None,
    provider: Optional[str] = None,
    pending_updates: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    """POST fleet health to the website cloud API."""
    import socket

    from centurion_cli import __version__ as centurion_version

    base = get_fleet_api_base(config)
    url = f"{base}/fleet/checkin"

    if config is None:
        from centurion_cli.config import load_config

        config = load_config() or {}

    model_cfg = config.get("model") if isinstance(config.get("model"), dict) else {}
    payload = {
        "api_key": api_key.strip(),
        "install_id": install_id or get_install_id(),
        "version": version or centurion_version,
        "hostname": hostname or socket.gethostname(),
        "provider": provider or model_cfg.get("provider"),
        "pending_updates": pending_updates or {},
    }

    try:
        return _post_json(url, payload)
    except Exception as exc:
        logger.debug("Fleet cloud check-in failed: %s", exc)
        return {"ok": False, "error": str(exc)}


def check_subscription_on_startup(config: Optional[Dict[str, Any]] = None) -> None:
    """Lightweight non-blocking subscription re-validation on CLI/gateway startup."""
    from centurion_cli.billing import is_billing_enabled

    if config is None:
        from centurion_cli.config import load_config

        config = load_config() or {}

    if not is_billing_enabled(config):
        return

    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        return

    result = validate_subscription_key(api_key, config=config, use_cache=True)
    if result.valid:
        return

    billing = config.get("billing") if isinstance(config.get("billing"), dict) else {}
    portal = billing.get("portal_url") or "https://www.personal-centurion.com"
    msg = result.error or "subscription inactive"
    logger.warning(
        "Centurion subscription validation failed (%s). Manage billing at %s/account/billing",
        msg,
        str(portal).rstrip("/"),
    )


def apply_openrouter_key_to_config(api_key: str, config: dict) -> None:
    """Write OpenRouter key to .env and set model provider defaults."""
    from centurion_cli.config import save_env_value

    save_env_value("OPENROUTER_API_KEY", api_key.strip())
    model_cfg = config.get("model")
    if not isinstance(model_cfg, dict):
        model_cfg = {}
        config["model"] = model_cfg
    model_cfg["provider"] = "openrouter"
    model_cfg.setdefault("base_url", "https://openrouter.ai/api/v1")
