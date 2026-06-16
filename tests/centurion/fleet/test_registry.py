"""Tests for centurion.fleet.registry."""

from __future__ import annotations

import json
import time

import pytest

from centurion.fleet.registry import CenturionIdentity, FleetRegistry


@pytest.fixture
def registry_path(tmp_path, monkeypatch):
    fleet_dir = tmp_path / ".centurion" / "fleet"
    fleet_dir.mkdir(parents=True)
    path = fleet_dir / "registry.json"
    monkeypatch.setenv("CENTURION_HOME", str(tmp_path / ".centurion"))
    return str(path)


def _identity(cid: str = "cent-001", name: str = "Titus") -> CenturionIdentity:
    return CenturionIdentity(
        centurion_id=cid,
        name=name,
        emoji="🦅",
        owner_name="Test Owner",
        owner_email="owner@example.com",
        role="Centurion",
        soul_doc_path="/tmp/SOUL.md",
        created_at=time.time(),
    )


def test_register_and_list(registry_path):
    reg = FleetRegistry(registry_path)
    reg.register(_identity())
    records = reg.list_all()
    assert len(records) == 1
    assert records[0].identity.name == "Titus"


def test_check_in_updates_status(registry_path):
    reg = FleetRegistry(registry_path)
    reg.register(_identity())
    assert reg.check_in("cent-001", status="active") is True
    record = reg.get("cent-001")
    assert record is not None
    assert record.status.status == "active"
    assert record.status.last_checkin > 0


def test_registry_persists_to_disk(registry_path):
    reg = FleetRegistry(registry_path)
    reg.register(_identity("cent-002", "Yeshi"))
    reloaded = FleetRegistry(registry_path)
    assert reloaded.get("cent-002") is not None
    assert reloaded.get("cent-002").identity.name == "Yeshi"
    data = json.loads(open(registry_path, encoding="utf-8").read())
    assert "cent-002" in data


def test_get_stale_marks_old_checkins(registry_path):
    reg = FleetRegistry(registry_path)
    reg.register(_identity())
    record = reg.get("cent-001")
    record.status.last_checkin = time.time() - 600
    reg._save()
    stale = reg.get_stale(max_age_seconds=300)
    assert len(stale) == 1
