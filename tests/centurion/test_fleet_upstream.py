"""Fleet upstream URL and toolset wiring."""

from centurion.fleet import update as fleet_update
from toolsets import TOOLSETS, resolve_toolset


def test_default_upstream_points_at_centurion_fleet():
    assert fleet_update.DEFAULT_UPSTREAM == "https://github.com/centurion-fleet/Centurion-AI-OS.git"


def test_fleet_toolset_includes_fleet_update():
    assert "fleet_update" in resolve_toolset("fleet")
    assert "fleet" in TOOLSETS
