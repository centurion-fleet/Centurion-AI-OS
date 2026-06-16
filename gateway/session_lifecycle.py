"""Session lifecycle helpers extracted from gateway/run.py."""

from __future__ import annotations

import time
from typing import Any, Optional


def should_evict_stale_running_agent(
    *,
    stale_age: float,
    raw_stale_timeout: float,
    agent: Any,
    stale_idle: float | None = None,
) -> tuple[bool, float, str]:
    """Return whether a leaked ``_running_agents`` entry should be evicted.

    Mirrors the staleness logic in ``GatewayRunner._handle_message`` so it can
    be unit-tested without spinning up the full gateway.

    Returns ``(should_evict, stale_idle, detail_suffix)``.
    """
    detail = ""
    idle = stale_idle if stale_idle is not None else float("inf")
    if agent and hasattr(agent, "get_activity_summary"):
        try:
            summary = agent.get_activity_summary()
            idle = summary.get("seconds_since_activity", float("inf"))
            detail = (
                f" | last_activity={summary.get('last_activity_desc', 'unknown')} "
                f"({idle:.0f}s ago) "
                f"| iteration={summary.get('api_call_count', 0)}/{summary.get('max_iterations', 0)}"
            )
        except Exception:
            pass

    wall_ttl = max(raw_stale_timeout * 10, 7200) if raw_stale_timeout > 0 else float("inf")
    should_evict = (
        agent is not None
        and (
            (raw_stale_timeout > 0 and idle >= raw_stale_timeout)
            or stale_age > wall_ttl
        )
    )
    return should_evict, idle, detail


def running_agent_age(stale_ts: float) -> float:
    """Seconds since the running-agent timestamp was recorded."""
    if not stale_ts:
        return 0.0
    return max(0.0, time.time() - stale_ts)
