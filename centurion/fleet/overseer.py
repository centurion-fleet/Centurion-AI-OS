"""
CenturionOS — Fleet Overseer Command Center
============================================
The Overseer (Titus) dashboard for monitoring and managing the fleet.

Provides:
- Fleet status overview
- Health scores per Centurion
- Policy compliance tracking
- Active task monitoring
- Alert management
"""

from typing import Optional

from .registry import FleetRegistry
from .health import OverseerHealthMonitor
from .swarm import SwarmCoordinator
from ..policies.engine import PolicyStore


class OverseerCommandCenter:
    """
    Central command dashboard for the Fleet Overseer.
    Aggregates data from fleet registry, health monitor, policy store,
    and swarm coordinator into a single view.
    """

    def __init__(
        self,
        registry: Optional[FleetRegistry] = None,
        health_monitor: Optional[OverseerHealthMonitor] = None,
        policy_store: Optional[PolicyStore] = None,
        swarm: Optional[SwarmCoordinator] = None,
    ):
        self.registry = registry or FleetRegistry()
        self.health = health_monitor or OverseerHealthMonitor(self.registry)
        self.policies = policy_store or PolicyStore()
        self.swarm = swarm or SwarmCoordinator(
            centurion_id="prefect",
            capabilities=["oversight", "quality_check", "escalation"],
            registry=self.registry,
        )

    def full_status(self) -> dict:
        """Complete fleet snapshot — the big picture."""
        fleet_health = self.health.check_fleet_health()
        policies = self.policies.list_categories()
        violations = self.policies.get_violations(unresolved_only=True)
        pending_tasks = self.swarm.get_pending_tasks()

        return {
            "fleet_health": fleet_health,
            "policy_categories": policies,
            "unresolved_violations": len(violations),
            "pending_tasks": len(pending_tasks),
            "timestamp": fleet_health["timestamp"],
        }

    def centurion_detail(self, centurion_id: str) -> dict:
        """Detailed view of a single Centurion."""
        record = self.registry.get(centurion_id)
        if not record:
            return {"error": f"Centurion '{centurion_id}' not found"}

        violations = self.policies.get_violations(
            centurion_id=centurion_id, unresolved_only=True
        )

        return {
            "identity": {
                "name": record.identity.name,
                "emoji": record.identity.emoji,
                "owner": record.identity.owner_name,
                "role": record.identity.role,
                "id": record.identity.centurion_id,
            },
            "status": {
                "status": record.status.status,
                "last_checkin": record.status.last_checkin,
                "version": record.status.version,
                "model": record.status.model,
                "host": record.status.host,
                "uptime_hours": record.status.uptime_hours,
                "cpu_load": record.status.cpu_load,
                "memory": f"{record.status.memory_used_gb:.1f}/{record.status.memory_total_gb:.1f} GB",
                "last_error": record.status.last_error,
            },
            "capabilities": record.capabilities,
            "tags": record.tags,
            "unresolved_violations": len(violations),
            "violations": [
                {"policy_id": v.policy_id, "severity": v.severity, "detail": v.detail}
                for v in violations[:10]
            ],
        }


def format_fleet_report(cmd: OverseerCommandCenter) -> str:
    """Generate a human-readable fleet report string."""
    status = cmd.full_status()
    fh = status["fleet_health"]

    lines = []
    lines.append("=" * 55)
    lines.append("  🦅 CENTURION FLEET — OVERSEER REPORT")
    lines.append("=" * 55)
    lines.append(f"  Health: {fh['health_score']}/100")
    lines.append(f"  Total: {fh['total_centurions']}  "
                 f"Active: {fh['active']}  "
                 f"Error: {fh['error']}  "
                 f"Offline: {fh['offline']}")
    lines.append(f"  Needs Attention: {fh['needs_attention']}")
    lines.append(f"  Policy Violations: {status['unresolved_violations']}")
    lines.append(f"  Pending Tasks: {status['pending_tasks']}")
    lines.append("-" * 55)

    for c in fh["per_centurion"]:
        icon = {"active": "✅", "error": "❌", "offline": "⚫",
                "deploying": "🔄", "inactive": "💤"}.get(c["status"], "❓")

        age = c["last_checkin_seconds_ago"]
        age_str = f"{age}s" if age < 60 else f"{age//60}m {age%60}s"

        error_note = f" ❗ {c['last_error'][:60]}" if c["last_error"] else ""
        lines.append(
            f"  {icon} {c['emoji']} {c['name']:12s} | "
            f"{c['owner']:18s} | {c['status']:10s} | "
            f"{age_str:>8s}{error_note}"
        )

    if status["unresolved_violations"] > 0:
        lines.append("-" * 55)
        lines.append(f"  ⚠ {status['unresolved_violations']} unresolved policy violations")

    if status["pending_tasks"] > 0:
        lines.append(f"  📋 {status['pending_tasks']} pending swarm tasks")

    lines.append("=" * 55)
    return "\n".join(lines)
