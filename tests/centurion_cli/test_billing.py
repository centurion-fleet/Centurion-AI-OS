"""Tests for Centurion billing gate (Phase 0 — BYOK until portal is live)."""

from centurion_cli.billing import is_billing_enabled
from centurion_cli.models import CANONICAL_PROVIDERS, get_picker_providers


def test_billing_disabled_by_default():
    assert is_billing_enabled({"billing": {"enabled": False}}) is False
    assert is_billing_enabled({}) is False
    assert is_billing_enabled({"billing": {}}) is False


def test_billing_enabled_when_config_true():
    assert is_billing_enabled({"billing": {"enabled": True}}) is True
    assert is_billing_enabled({"billing": {"enabled": "true"}}) is True


def test_picker_hides_nous_when_billing_disabled():
    slugs = [p.slug for p in get_picker_providers(billing_enabled=False)]
    assert "nous" not in slugs
    assert slugs[0] == "openrouter"
    assert "lmstudio" in slugs[:3]


def test_picker_includes_nous_when_billing_enabled():
    slugs = [p.slug for p in get_picker_providers(billing_enabled=True)]
    assert "nous" in slugs


def test_openrouter_first_in_canonical_list():
    assert CANONICAL_PROVIDERS[0].slug == "openrouter"
    assert CANONICAL_PROVIDERS[1].slug == "lmstudio"
