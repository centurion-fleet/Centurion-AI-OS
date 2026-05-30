"""
CenturionOS — Fleet Health Checks
==================================
Automated health monitoring for the Centurion fleet.

Each Centurion runs a health check script (via cron or background thread)
that pings the Fleet Registry and reports its status. The Overseer (Titus)
gets alerted when Centurions go stale, throw errors, or drop offline.
"""

import json
import os
import platform
import time
from typing import Optional

from .registry import FleetRegistry, CenturionIdentity, CenturionStatus


# ── Health Check Runner ──────────────────────────────────────────────

class HealthCheckRunner:
    """
    Runs on each Centurion. Checks in with the Fleet Registry periodically.

    If the registry is local (shared filesystem), it writes directly.
    If remote, it would send via Telegram/API. For MVP: local filesystem.
    """

    def __init__(
        self,
        centurion_id: str,
        registry: Optional[FleetRegistry] = None,
    ):
        self.centurion_id = centurion_id
        self.registry = registry or FleetRegistry()
        self._gather_system_info()

    def _gather_system_info(self):
        """Collect basic system metrics."""
        import psutil
        self.hostname = platform.node()
        try:
            self.cpu_load = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory()
            self.memory_used_gb = mem.used / (1024 ** 3)
            self.memory_total_gb = mem.total / (1024 ** 3)
        except ImportError:
            self.cpu_load = 0.0
            self.memory_used_gb = 0.0
            self.memory_total_gb = 0.0

    def check_in(self, status: str = "active") -> bool:
        """Send a heartbeat to the fleet registry."""
        self._gather_system_info()
        return self.registry.update_status(
            self.centurion_id,
            status=status,
            cpu_load=self.cpu_load,
            memory_used_gb=self.memory_used_gb,
            memory_total_gb=self.memory_total_gb,
            host=self.hostname,
        ) is not None

    def report_error(self, error_msg: str) -> bool:
        """Report an error condition to the fleet."""
        self._gather_system_info()
        result = self.registry.update_status(
            self.centurion_id,
            status="error",
            last_error=error_msg[:500],
            cpu_load=self.cpu_load,
            memory_used_gb=self.memory_used_gb,
            memory_total_gb=self.memory_total_gb,
        )
        return result is not None

    def report_deploying(self) -> bool:
        """Report that this Centurion is being deployed."""
        return self.registry.update_status(
            self.centurion_id,
            status="deploying",
        ) is not None

    def report_offline(self) -> bool:
        """Report that this Centurion is going offline."""
        return self.registry.update_status(
            self.centurion_id,
            status="offline",
        ) is not None


# ── Overseer Health Monitor ─────────────────────────────────────────

class OverseerHealthMonitor:
    """
    Runs on the Overseer (Titus). Monitors the entire fleet for:
    - Stale check-ins (Centurions that haven't pinged recently)
    - Error states
    - Offline status
    - Overall fleet health score
    """

    def __init__(self, registry: Optional[FleetRegistry] = None):
        self.registry = registry or FleetRegistry()

    def check_fleet_health(self, stale_threshold_seconds: int = 300) -> dict:
        """
        Comprehensive fleet health check.
        Returns a dict with overall status and per-Centurion details.
        """
        summary = self.registry.fleet_summary()
        all_records = self.registry.list_all()
        stale = self.registry.get_stale(stale_threshold_seconds)

        per_centurion = []
        for record in all_records:
            cid = record.identity.centurion_id
            age = time.time() - record.status.last_checkin
            is_stale = age > stale_threshold_seconds
            per_centurion.append({
                "id": cid,
                "name": record.identity.name,
                "emoji": record.identity.emoji,
                "owner": record.identity.owner_name,
                "status": record.status.status,
                "last_checkin_seconds_ago": int(age),
                "is_stale": is_stale,
                "has_error": bool(record.status.last_error),
                "last_error": record.status.last_error if record.status.last_error else None,
                "host": record.status.host,
                "version": record.status.version,
                "model": record.status.model,
                "cpu_load": record.status.cpu_load,
                "memory_used_gb": record.status.memory_used_gb,
                "uptime_hours": record.status.uptime_hours,
            })

        # Overall health score (0-100)
        total = len(per_centurion) or 1
        error_count = sum(1 for c in per_centurion if c["has_error"])
        stale_count = sum(1 for c in per_centurion if c["is_stale"])
        offline_count = sum(1 for c in per_centurion if c["status"] == "offline")
        active_count = sum(1 for c in per_centurion if c["status"] == "active")

        health_score = int(
            (active_count / total) * 60 +
            (1 - error_count / total) * 20 +
            (1 - stale_count / total) * 10 +
            (1 - offline_count / total) * 10
        )

        return {
            "timestamp": time.time(),
            "health_score": health_score,
            "total_centurions": summary["total"],
            "active": summary["active"],
            "error": summary["error"],
            "stale": len(stale),
            "offline": summary["offline"],
            "needs_attention": error_count + stale_count + offline_count,
            "per_centurion": per_centurion,
        }

    def get_centurions_needing_attention(self, stale_threshold: int = 300) -> list[dict]:
        """Get only the Centurions that need attention (errors, stale, offline)."""
        health = self.check_fleet_health(stale_threshold)
        return [
            c for c in health["per_centurion"]
            if c["is_stale"] or c["has_error"] or c["status"] == "offline"
        ]


# ── CLI Helper ───────────────────────────────────────────────────────

def print_fleet_status(health: dict):
    """Pretty-print fleet health to console."""
    print(f"\n{'='*50}")
    print(f"  CENTURION FLEET STATUS")
    print(f"{'='*50}")
    print(f"  Health Score: {health['health_score']}/100")
    print(f"  Total: {health['total_centurions']}  "
          f"Active: {health['active']}  "
          f"Error: {health['error']}  "
          f"Offline: {health['offline']}  "
          f"Stale: {health['stale']}")
    print(f"  Needs Attention: {health['needs_attention']}")
    print(f"{'='*50}")

    for c in health["per_centurion"]:
        status_indicator = {
            "active": "✅",
            "error": "❌",
            "offline": "⚫",
            "deploying": "🔄",
            "inactive": "💤",
            "unknown": "❓",
        }.get(c["status"], "❓")

        age_str = f"{c['last_checkin_seconds_ago']}s ago" if c['last_checkin_seconds_ago'] < 3600 else f"{c['last_checkin_seconds_ago']/3600:.1f}h ago"

        print(f"  {status_indicator} {c['emoji']} {c['name']:12s} | "
              f"{c['owner']:20s} | {c['status']:10s} | {age_str:12s}"
              + (f" | ❗ {c['last_error'][:50]}" if c['last_error'] else ""))
    print()
