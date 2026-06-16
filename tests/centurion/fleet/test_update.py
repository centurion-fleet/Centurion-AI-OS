"""Tests for centurion.fleet.update policy helpers."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from centurion.fleet import update as fleet_update


def test_apply_policy_merges_security_and_flags_others(tmp_path):
    commits = [
        {
            "hash": "abc123",
            "full_hash": "abc123deadbeef",
            "author": "bot",
            "date": "2026-01-01",
            "subject": "fix: patch crash",
            "category": "fix",
        },
        {
            "hash": "def456",
            "full_hash": "def456deadbeef",
            "author": "bot",
            "date": "2026-01-02",
            "subject": "feat: new dashboard",
            "category": "feat",
        },
    ]

    with patch.object(fleet_update, "check_upstream", return_value=commits), patch.object(
        fleet_update,
        "apply_commit",
        side_effect=lambda h, repo=None: {
            "success": True,
            "message": f"Applied {h[:6]}",
            "commit": h[:6],
        },
    ):
        result = fleet_update.apply_policy(repo=tmp_path)

    assert len(result["merged"]) == 1
    assert result["merged"][0]["category"] == "fix"
    assert len(result["flagged"]) == 1
    assert result["flagged"][0]["category"] == "feat"


def test_apply_policy_up_to_date(tmp_path):
    with patch.object(fleet_update, "check_upstream", return_value=[]):
        result = fleet_update.apply_policy(repo=tmp_path)
    assert result["merged"] == []
    assert result["flagged"] == []
    assert "up to date" in result["message"].lower()


@pytest.mark.parametrize(
    "subject,expected",
    [
        ("security: rotate token", "security"),
        ("fix: null pointer", "fix"),
        ("feat: add widget", "feat"),
        ("random subject", "other"),
    ],
)
def test_commit_category_patterns(subject, expected):
    for cat, pattern in fleet_update.COMMIT_CATEGORIES.items():
        if pattern.search(subject):
            assert cat == expected
            return
    assert expected == "other"
