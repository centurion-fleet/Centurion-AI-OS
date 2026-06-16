"""Tests for gateway.slash_handlers helpers."""

from __future__ import annotations

from gateway.slash_handlers import (
    coerce_gateway_timestamp,
    resolve_slash_command,
    telegramize_command_mentions,
)


def test_resolve_slash_command_canonicalizes_alias():
    cmd_def, canonical = resolve_slash_command("/bg")
    assert canonical == "background"
    assert cmd_def is not None
    assert cmd_def.name == "background"


def test_telegramize_command_mentions_sanitizes_invalid_names():
    from gateway.config import Platform

    text = "Try /ModelPicker and /help"
    out = telegramize_command_mentions(text, Platform.TELEGRAM)
    assert "/modelpicker" in out.lower()
    assert "/help" in out


def test_coerce_gateway_timestamp_accepts_epoch_seconds():
    assert coerce_gateway_timestamp(1_700_000_000) == 1_700_000_000.0
