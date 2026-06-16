"""Tests for gateway.dispatch helpers."""

from __future__ import annotations

from centurion_cli.commands import resolve_command
from gateway.dispatch import (
    classify_running_agent_command,
    is_active_session_bypass_command,
    is_dedicated_running_agent_handler,
)


def test_classify_running_agent_command_buckets():
    help_def = resolve_command("help")
    model_def = resolve_command("model")
    yolo_def = resolve_command("yolo")

    assert classify_running_agent_command(help_def) == "dedicated"
    assert classify_running_agent_command(model_def) == "catch_all"
    assert classify_running_agent_command(yolo_def) == "inline"
    assert classify_running_agent_command(None) is None


def test_bypass_and_dedicated_helpers():
    assert is_active_session_bypass_command("stop") is True
    assert is_active_session_bypass_command("not-a-command") is False
    assert is_dedicated_running_agent_handler("status") is True
    assert is_dedicated_running_agent_handler("model") is False
