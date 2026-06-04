"""
CenturionOS — Fleet
====================
Inter-Centurion fleet management, messaging, and coordination.

Modules:
- registry      — Fleet identity registration and status tracking
- peers         — Network-level peer registry for cross-machine communication
- swarm         — Task delegation, messaging, and coordination
- transport     — HTTP-based network transport for fleet messaging
- health        — Automated health monitoring and check-ins
- overseer      — Fleet Overseer (Titus) command center dashboard
"""

from .registry import FleetRegistry, CenturionIdentity, CenturionStatus, CenturionRecord
from .peers import FleetPeers, FleetPeer
from .swarm import SwarmCoordinator, SwarmTask
from .transport import FleetTransport, FleetMessageEnvelope
from .health import HealthCheckRunner, OverseerHealthMonitor
from .overseer import OverseerCommandCenter, format_fleet_report

__all__ = [
    "FleetRegistry", "CenturionIdentity", "CenturionStatus", "CenturionRecord",
    "FleetPeers", "FleetPeer",
    "SwarmCoordinator", "SwarmTask",
    "FleetTransport", "FleetMessageEnvelope",
    "HealthCheckRunner", "OverseerHealthMonitor",
    "OverseerCommandCenter", "format_fleet_report",
]
