"""Tests for gateway.session_lifecycle helpers."""

from __future__ import annotations

from gateway.session_lifecycle import running_agent_age, should_evict_stale_running_agent


class _IdleAgent:
    def get_activity_summary(self):
        return {"seconds_since_activity": 9999, "last_activity_desc": "idle"}


def test_should_evict_when_idle_beyond_timeout():
    should_evict, idle, _detail = should_evict_stale_running_agent(
        stale_age=100.0,
        raw_stale_timeout=60.0,
        agent=_IdleAgent(),
    )
    assert should_evict is True
    assert idle == 9999


def test_should_not_evict_when_recently_active():
    class _ActiveAgent:
        def get_activity_summary(self):
            return {"seconds_since_activity": 5}

    should_evict, _, _ = should_evict_stale_running_agent(
        stale_age=100.0,
        raw_stale_timeout=60.0,
        agent=_ActiveAgent(),
    )
    assert should_evict is False


def test_running_agent_age_non_negative():
    import time

    age = running_agent_age(time.time() - 30)
    assert 29 <= age <= 31
