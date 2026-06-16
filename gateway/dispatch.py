"""Running-agent slash-command dispatch helpers for gateway/run.py."""

from __future__ import annotations

from centurion_cli.commands import (
    ACTIVE_SESSION_BYPASS_COMMANDS,
    CommandDef,
    should_bypass_active_session,
)

# Commands that mutate session state inline while an agent is running.
RUNNING_AGENT_INLINE_COMMANDS: frozenset[str] = frozenset(
    {"yolo", "verbose", "footer"}
)

# Commands handled before the running-agent catch-all busy response.
RUNNING_AGENT_PRIORITY_COMMANDS: frozenset[str] = frozenset(
    {"status", "restart", "stop", "new", "queue", "q", "steer"}
)


def is_active_session_bypass_command(command_name: str | None) -> bool:
    """True when *command_name* must bypass the adapter active-session queue."""
    return should_bypass_active_session(command_name)


def is_dedicated_running_agent_handler(command_name: str | None) -> bool:
    """True when gateway/run.py has an explicit Level-2 handler for *command_name*."""
    return bool(command_name and command_name in ACTIVE_SESSION_BYPASS_COMMANDS)


def classify_running_agent_command(
    cmd_def: CommandDef | None,
) -> str | None:
    """Map a resolved slash command to a running-agent dispatch bucket.

    Returns one of: ``inline``, ``priority``, ``dedicated``, ``catch_all``,
    or ``None`` when *cmd_def* is unset.
    """
    if cmd_def is None:
        return None
    name = cmd_def.name
    if name in RUNNING_AGENT_INLINE_COMMANDS:
        return "inline"
    if name in RUNNING_AGENT_PRIORITY_COMMANDS:
        return "priority"
    if name in ACTIVE_SESSION_BYPASS_COMMANDS:
        return "dedicated"
    return "catch_all"
