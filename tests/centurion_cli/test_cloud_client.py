"""Tests for centurion_cli.cloud_client."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from centurion_cli.cloud_client import (
    ValidationResult,
    _key_fingerprint,
    get_fleet_api_base,
    validate_subscription_key,
)


def test_get_fleet_api_base_from_config():
    cfg = {
        "billing": {
            "portal_url": "https://www.personal-centurion.com",
            "fleet_api_url": "https://www.personal-centurion.com/api/v1",
        }
    }
    assert get_fleet_api_base(cfg) == "https://www.personal-centurion.com/api/v1"


def test_get_fleet_api_base_derives_from_portal():
    cfg = {"billing": {"portal_url": "https://www.personal-centurion.com"}}
    assert get_fleet_api_base(cfg) == "https://www.personal-centurion.com/api/v1"


@patch("centurion_cli.cloud_client.urlopen")
def test_validate_subscription_key_success(mock_urlopen, tmp_path, monkeypatch):
    monkeypatch.setattr("centurion_cli.cloud_client._cache_path", lambda: tmp_path / "cache.json")
    response = MagicMock()
    response.read.return_value = json.dumps({
        "valid": True,
        "plan": "professional",
        "credits_remaining_usd": 100.0,
        "subscription_status": "active",
    }).encode()
    response.__enter__ = lambda s: s
    response.__exit__ = MagicMock(return_value=False)
    mock_urlopen.return_value = response

    cfg = {"billing": {"fleet_api_url": "https://example.com/api/v1"}}
    result = validate_subscription_key("sk-or-v1-testkey", config=cfg, use_cache=False)
    assert result.valid is True
    assert result.plan == "professional"


def test_key_fingerprint_stable():
    assert _key_fingerprint("sk-or-v1-abc") == _key_fingerprint("sk-or-v1-abc")
    assert _key_fingerprint("sk-or-v1-abc") != _key_fingerprint("sk-or-v1-xyz")
