"""Slash-command helpers extracted from gateway/run.py for maintainability."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Optional

from centurion_cli.commands import CommandDef, resolve_command

TELEGRAM_COMMAND_MENTION_RE = re.compile(r"(?<![\w:/])/([A-Za-z0-9][A-Za-z0-9_-]*)")


def telegramize_command_mentions(text: str, platform: Any) -> str:
    """Rewrite slash-command mentions to Telegram-valid command names."""
    platform_value = getattr(platform, "value", platform)
    if platform_value != "telegram":
        return text

    from centurion_cli.commands import _sanitize_telegram_name

    def _replace(match: re.Match[str]) -> str:
        sanitized = _sanitize_telegram_name(match.group(1))
        return f"/{sanitized}" if sanitized else match.group(0)

    return TELEGRAM_COMMAND_MENTION_RE.sub(_replace, text)


def coerce_gateway_timestamp(value: Any) -> Optional[float]:
    """Best-effort conversion of stored gateway timestamps to epoch seconds."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.timestamp()
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value) / 1000.0 if float(value) > 10_000_000_000 else float(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            numeric = float(text)
            return numeric / 1000.0 if numeric > 10_000_000_000 else numeric
        except ValueError:
            pass
        try:
            if text.endswith("Z"):
                text = text[:-1] + "+00:00"
            return datetime.fromisoformat(text).timestamp()
        except ValueError:
            return None
    return None


def resolve_slash_command(command: str | None) -> tuple[CommandDef | None, str | None]:
    """Resolve a slash command string to (CommandDef, canonical_name)."""
    if not command:
        return None, None
    cmd_def = resolve_command(command)
    canonical = cmd_def.name if cmd_def else command
    return cmd_def, canonical
