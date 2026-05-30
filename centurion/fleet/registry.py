"""
CenturionOS — Fleet Registry
=============================
Identity, registration, and status tracking for the Centurion fleet.

Each Centurion in the fleet has a unique identity, an owner (human), 
a Soul document, and a current status. The Fleet Registry is the 
authoritative source of truth for who is in the fleet and their state.
"""

import json
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Optional


# ── Fleet Registry Paths ─────────────────────────────────────────────

def get_fleet_home() -> str:
    """Return the fleet data directory. Respects CENTURION_HOME env var."""
    base = os.environ.get("CENTURION_HOME", os.path.expanduser("~/.centurion"))
    return os.path.join(base, "fleet")


def get_registry_path() -> str:
    return os.path.join(get_fleet_home(), "registry.json")


def get_locks_dir() -> str:
    return os.path.join(get_fleet_home(), "locks")


def get_messages_dir() -> str:
    return os.path.join(get_fleet_home(), "messages")


# ── Data Models ──────────────────────────────────────────────────────

@dataclass
class CenturionIdentity:
    """The core identity of a Centurion — set once at creation."""
    centurion_id: str           # e.g., "cent-001"
    name: str                   # e.g., "Titus", "Yeshi"
    emoji: str                  # e.g., "🦅", "🦋"
    owner_name: str             # e.g., "Adrian Barkus"
    owner_email: str            # e.g., "hello@adrianbarkus.com"
    role: str                   # "Prefect", "Centurion", "Legionnaire"
    soul_doc_path: str          # Path to SOUL.md
    created_at: float = 0.0     # Unix timestamp


@dataclass
class CenturionStatus:
    """Live status — updated on each check-in."""
    status: str = "unknown"     # "active", "inactive", "error", "deploying", "offline"
    last_checkin: float = 0.0   # Unix timestamp
    version: str = ""           # Centurion OS version
    model: str = ""             # Current AI model
    provider: str = ""          # Current provider
    uptime_hours: float = 0.0
    last_error: str = ""
    cpu_load: float = 0.0
    memory_used_gb: float = 0.0
    memory_total_gb: float = 0.0
    host: str = ""              # Machine hostname
    telegram_handle: str = ""   # @username for direct messaging


@dataclass
class CenturionRecord:
    """Complete record — identity + status + metadata."""
    identity: CenturionIdentity
    status: CenturionStatus = field(default_factory=CenturionStatus)
    capabilities: list = field(default_factory=list)
    tags: list = field(default_factory=list)
    notes: str = ""


# ── Fleet Registry ───────────────────────────────────────────────────

class FleetRegistry:
    """Manages the fleet registry file — thread-safe via file locking."""

    def __init__(self, registry_path: Optional[str] = None):
        self.registry_path = registry_path or get_registry_path()
        self._ensure_dirs()
        self._records: dict[str, CenturionRecord] = {}
        self._load()

    def _ensure_dirs(self):
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        os.makedirs(get_locks_dir(), exist_ok=True)
        os.makedirs(get_messages_dir(), exist_ok=True)

    def _load(self):
        """Load registry from disk."""
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path) as f:
                    data = json.load(f)
                for cid, record_data in data.items():
                    identity = CenturionIdentity(**record_data["identity"])
                    status = CenturionStatus(**record_data.get("status", {}))
                    self._records[cid] = CenturionRecord(
                        identity=identity,
                        status=status,
                        capabilities=record_data.get("capabilities", []),
                        tags=record_data.get("tags", []),
                        notes=record_data.get("notes", ""),
                    )
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Fleet registry corrupt, starting fresh: {e}")

    def _save(self):
        """Write registry to disk atomically."""
        data = {}
        for cid, record in self._records.items():
            data[cid] = {
                "identity": asdict(record.identity),
                "status": asdict(record.status),
                "capabilities": record.capabilities,
                "tags": record.tags,
                "notes": record.notes,
            }
        tmp_path = self.registry_path + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, self.registry_path)

    # ── CRUD ─────────────────────────────────────────────────────────

    def register(self, identity: CenturionIdentity) -> CenturionRecord:
        """Register a new Centurion in the fleet. Returns the record."""
        if identity.centurion_id in self._records:
            raise ValueError(
                f"Centurion '{identity.centurion_id}' already registered. "
                f"Use update() to modify."
            )
        record = CenturionRecord(identity=identity)
        record.status.status = "deploying"
        record.status.last_checkin = time.time()
        self._records[identity.centurion_id] = record
        self._save()
        return record

    def update_status(self, centurion_id: str, **status_fields) -> Optional[CenturionStatus]:
        """Update status fields for a Centurion. Triggers check-in timestamp."""
        record = self._records.get(centurion_id)
        if not record:
            return None
        for key, value in status_fields.items():
            if hasattr(record.status, key):
                setattr(record.status, key, value)
        record.status.last_checkin = time.time()
        self._save()
        return record.status

    def check_in(self, centurion_id: str, status: str = "active") -> bool:
        """Simple heartbeart check-in. Returns True if registered."""
        record = self._records.get(centurion_id)
        if not record:
            return False
        record.status.status = status
        record.status.last_checkin = time.time()
        self._save()
        return True

    def get(self, centurion_id: str) -> Optional[CenturionRecord]:
        return self._records.get(centurion_id)

    def list_all(self, status_filter: Optional[str] = None) -> list[CenturionRecord]:
        """List all Centurions, optionally filtered by status."""
        if status_filter:
            return [r for r in self._records.values() if r.status.status == status_filter]
        return list(self._records.values())

    def remove(self, centurion_id: str) -> bool:
        """Remove a Centurion from the registry (decommissioned)."""
        if centurion_id in self._records:
            del self._records[centurion_id]
            self._save()
            return True
        return False

    # ── Fleet Health ─────────────────────────────────────────────────

    def get_stale(self, max_age_seconds: int = 300) -> list[CenturionRecord]:
        """Return Centurions that haven't checked in recently."""
        now = time.time()
        return [
            r for r in self._records.values()
            if now - r.status.last_checkin > max_age_seconds
        ]

    def fleet_summary(self) -> dict:
        """Return a quick overview of the entire fleet."""
        now = time.time()
        all_records = self.list_all()
        return {
            "total": len(all_records),
            "active": len([r for r in all_records if r.status.status == "active"]),
            "inactive": len([r for r in all_records if r.status.status == "inactive"]),
            "error": len([r for r in all_records if r.status.status == "error"]),
            "offline": len([r for r in all_records if r.status.status == "offline"]),
            "deploying": len([r for r in all_records if r.status.status == "deploying"]),
            "stale": len(self.get_stale()),
            "last_updated": now,
        }


# ── Fleet Messaging (Inter-Centurion Communication) ──────────────────

FLEET_MESSAGE_DIR = get_messages_dir()


def send_fleet_message(
    sender_id: str,
    recipient_id: str,
    subject: str,
    body: str,
    priority: str = "normal",
) -> str:
    """
    Send a message from one Centurion to another via the fleet message bus.
    Returns message_id.
    """
    os.makedirs(FLEET_MESSAGE_DIR, exist_ok=True)
    msg_id = f"{int(time.time())}_{sender_id}_{recipient_id}"
    message = {
        "message_id": msg_id,
        "sender": sender_id,
        "recipient": recipient_id,
        "subject": subject,
        "body": body,
        "priority": priority,
        "timestamp": time.time(),
        "read": False,
    }
    msg_path = os.path.join(FLEET_MESSAGE_DIR, f"{msg_id}.json")
    with open(msg_path, "w") as f:
        json.dump(message, f, indent=2)
    return msg_id


def get_fleet_messages(centurion_id: str, unread_only: bool = True) -> list[dict]:
    """Get messages for a specific Centurion."""
    messages = []
    if not os.path.exists(FLEET_MESSAGE_DIR):
        return messages
    for fname in sorted(os.listdir(FLEET_MESSAGE_DIR)):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(FLEET_MESSAGE_DIR, fname)
        try:
            with open(fpath) as f:
                msg = json.load(f)
            if msg["recipient"] != "all" and msg["recipient"] != centurion_id:
                continue
            if unread_only and msg.get("read", False):
                continue
            messages.append(msg)
        except (json.JSONDecodeError, KeyError):
            continue
    return messages


def mark_fleet_message_read(message_id: str) -> bool:
    """Mark a fleet message as read."""
    fpath = os.path.join(FLEET_MESSAGE_DIR, f"{message_id}.json")
    if not os.path.exists(fpath):
        return False
    with open(fpath) as f:
        msg = json.load(f)
    msg["read"] = True
    with open(fpath, "w") as f:
        json.dump(msg, f, indent=2)
    return True
