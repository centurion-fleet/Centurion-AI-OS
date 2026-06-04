"""
CenturionOS — Fleet Peers Registry
====================================
Network-level peer registry for cross-machine Centurion communication.

Stores the addresses, auth tokens, and connection status of every
Centurion in the fleet. Used by the FleetTransport to route messages
to the right machine.
"""

import json
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Optional


def get_peers_path() -> str:
    """Return path to the fleet peers registry."""
    base = os.environ.get("CENTURION_HOME", os.path.expanduser("~/.centurion"))
    return os.path.join(base, "fleet", "peers.json")


def get_fleet_queue_dir() -> str:
    """Return path for offline message queue."""
    base = os.environ.get("CENTURION_HOME", os.path.expanduser("~/.centurion"))
    return os.path.join(base, "fleet", "outbox")


@dataclass
class FleetPeer:
    """A known Centurion in the fleet network."""
    centurion_id: str
    name: str
    address: str                 # e.g. "http://ships-ai:8642" or "https://eve.centurion.dev"
    auth_token: str = ""         # Shared secret for authenticating messages
    telegram_handle: str = ""    # Fallback communication channel
    public_key: str = ""         # Future: for message encryption
    last_seen: float = 0.0       # Unix timestamp of last successful contact
    status: str = "unknown"      # "online", "offline", "unknown"
    version: str = ""            # Last known Centurion OS version
    latency_ms: float = 0.0      # Last measured round-trip time


class FleetPeers:
    """
    Manages the list of known fleet peers.
    Thread-safe via atomic file writes.
    """

    def __init__(self, peers_path: Optional[str] = None):
        self.peers_path = peers_path or get_peers_path()
        self._ensure_dirs()
        self._peers: dict[str, FleetPeer] = {}
        self._load()

    def _ensure_dirs(self):
        os.makedirs(os.path.dirname(self.peers_path), exist_ok=True)
        os.makedirs(get_fleet_queue_dir(), exist_ok=True)

    def _load(self):
        if os.path.exists(self.peers_path):
            try:
                with open(self.peers_path) as f:
                    data = json.load(f)
                for cid, pdata in data.get("peers", {}).items():
                    self._peers[cid] = FleetPeer(**pdata)
            except (json.JSONDecodeError, KeyError, TypeError):
                self._peers = {}

    def _save(self):
        data = {"peers": {}}
        for cid, peer in self._peers.items():
            data["peers"][cid] = asdict(peer)
        tmp = self.peers_path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, self.peers_path)

    # ── CRUD ─────────────────────────────────────────────────────────

    def register(self, peer: FleetPeer) -> FleetPeer:
        """Add or update a peer."""
        self._peers[peer.centurion_id] = peer
        self._save()
        return peer

    def update_status(self, centurion_id: str, status: str,
                      last_seen: Optional[float] = None,
                      version: Optional[str] = None,
                      latency_ms: Optional[float] = None) -> Optional[FleetPeer]:
        """Update peer connection status."""
        peer = self._peers.get(centurion_id)
        if not peer:
            return None
        peer.status = status
        if last_seen is not None:
            peer.last_seen = last_seen
        if version is not None:
            peer.version = version
        if latency_ms is not None:
            peer.latency_ms = latency_ms
        self._save()
        return peer

    def get(self, centurion_id: str) -> Optional[FleetPeer]:
        return self._peers.get(centurion_id)

    def list_online(self) -> list[FleetPeer]:
        return [p for p in self._peers.values() if p.status == "online"]

    def list_all(self) -> list[FleetPeer]:
        return list(self._peers.values())

    def remove(self, centurion_id: str) -> bool:
        if centurion_id in self._peers:
            del self._peers[centurion_id]
            self._save()
            return True
        return False

    def configure_defaults(self):
        """Set up default fleet peers for Centurion fleet."""
        defaults = [
            FleetPeer(
                centurion_id="prefect",
                name="Titus",
                address="",
                telegram_handle="@Titus_Centurion_Bot",
                status="unknown",
            ),
            FleetPeer(
                centurion_id="cent-002",
                name="Eve",
                address="",
                telegram_handle="@Eve_Centurion",
                status="unknown",
            ),
            FleetPeer(
                centurion_id="cent-001",
                name="Adam",
                address="",
                telegram_handle="",
                status="unknown",
            ),
        ]
        for peer in defaults:
            if peer.centurion_id not in self._peers:
                self._peers[peer.centurion_id] = peer
        self._save()
