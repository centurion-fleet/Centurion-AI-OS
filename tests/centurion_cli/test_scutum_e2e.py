"""Scutum integration smoke tests (mocked — no live website)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from centurion_cli.cloud_client import (
    apply_openrouter_key_to_config,
    fleet_checkin_to_cloud,
    validate_subscription_key,
)


@patch("centurion_cli.cloud_client.urlopen")
def test_scutum_flow_validate_then_checkin(mock_urlopen, tmp_path, monkeypatch):
    """Subscribe path: validate key → fleet check-in POST."""
    monkeypatch.setattr("centurion_cli.cloud_client._cache_path", lambda: tmp_path / "cache.json")

    calls: list[str] = []

    def fake_urlopen(req, timeout=15.0):
        calls.append(req.full_url)
        payload = json.loads(req.data.decode())
        if req.full_url.endswith("/keys/validate"):
            body = {
                "valid": True,
                "plan": "starter",
                "credits_remaining_usd": 25.0,
                "subscription_status": "active",
            }
        else:
            assert payload.get("install_id")
            assert payload.get("api_key") == "sk-or-v1-flowtest"
            body = {"ok": True, "policy": "auto_security_fix"}
        response = MagicMock()
        response.read.return_value = json.dumps(body).encode()
        response.__enter__ = lambda s: s
        response.__exit__ = MagicMock(return_value=False)
        return response

    mock_urlopen.side_effect = fake_urlopen

    cfg = {
        "billing": {
            "enabled": True,
            "fleet_api_url": "https://www.personal-centurion.com/api/v1",
        },
        "model": {"provider": "openrouter"},
    }

    result = validate_subscription_key("sk-or-v1-flowtest", config=cfg, use_cache=False)
    assert result.valid is True

    checkin = fleet_checkin_to_cloud(
        "sk-or-v1-flowtest",
        config=cfg,
        install_id="test-install-1",
        version="0.14.0",
        hostname="test-host",
    )
    assert checkin.get("ok") is True
    assert len(calls) == 2


def test_apply_openrouter_key_sets_provider(tmp_path, monkeypatch):
    monkeypatch.setenv("CENTURION_HOME", str(tmp_path / ".centurion"))
    from centurion_constants import get_centurion_home

    get_centurion_home()  # prime after env set

    cfg: dict = {"model": {}}
    with patch("centurion_cli.config.save_env_value") as mock_save:
        apply_openrouter_key_to_config("sk-or-v1-apply", cfg)
        mock_save.assert_called_once_with("OPENROUTER_API_KEY", "sk-or-v1-apply")
    assert cfg["model"]["provider"] == "openrouter"
