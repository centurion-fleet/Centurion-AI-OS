"""
CenturionOS — Swarm Collaboration
==================================
Inter-Centurion task delegation, communication, and coordination.

The Swarm enables Centurions to:
- Send messages to each other (via fleet message bus)
- Delegate tasks to other Centurions
- Request assistance from the fleet
- Broadcast to all Centurions
- Escalate issues to the Overseer (Titus)
"""

import json
import os
import time
from typing import Optional, Callable
from dataclasses import dataclass, field, asdict

from .registry import (
    FleetRegistry,
    send_fleet_message,
    get_fleet_messages,
    mark_fleet_message_read,
)


# ── Task Delegation ──────────────────────────────────────────────────

@dataclass
class SwarmTask:
    """A task delegated from one Centurion to another."""
    task_id: str
    sender_id: str
    recipient_id: str          # "any" = first available, "all" = broadcast
    task_type: str             # "query", "action", "review", "approval", "quality_check"
    title: str
    description: str
    priority: str = "normal"   # "low", "normal", "high", "critical"
    status: str = "pending"    # "pending", "accepted", "in_progress", "completed", "failed", "rejected"
    assigned_to: str = ""
    result: str = ""
    created_at: float = 0.0
    accepted_at: float = 0.0
    completed_at: float = 0.0
    expires_at: float = 0.0
    tags: list = field(default_factory=list)


class SwarmCoordinator:
    """
    Coordinates task delegation and communication across the fleet.
    Runs on each Centurion — routes tasks based on capabilities.

    Supports two transport modes:
    - Local (file-based): messages stored in ~/.centurion/fleet/messages/
    - Network (HTTP): messages sent via FleetTransport to peer machines

    If a FleetTransport is provided, network mode is preferred.
    File-based messaging remains as fallback for same-machine Centurions.
    """

    def __init__(
        self,
        centurion_id: str,
        capabilities: Optional[list] = None,
        registry: Optional[FleetRegistry] = None,
        transport: Optional[object] = None,
        centurion_name: str = "",
    ):
        self.centurion_id = centurion_id
        self.capabilities = capabilities or []
        self.registry = registry or FleetRegistry()
        self.transport = transport  # FleetTransport instance for network mode
        self.centurion_name = centurion_name
        self._tasks_dir = os.path.join(
            os.environ.get("CENTURION_HOME", os.path.expanduser("~/.centurion")),
            "swarm", "tasks"
        )
        os.makedirs(self._tasks_dir, exist_ok=True)

    # ── Task Management ──────────────────────────────────────────────

    def _task_path(self, task_id: str) -> str:
        return os.path.join(self._tasks_dir, f"{task_id}.json")

    def _save_task(self, task: SwarmTask):
        path = self._task_path(task.task_id)
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(asdict(task), f, indent=2)
        os.replace(tmp, path)

    def _load_task(self, task_id: str) -> Optional[SwarmTask]:
        path = self._task_path(task_id)
        if not os.path.exists(path):
            return None
        try:
            with open(path) as f:
                return SwarmTask(**json.load(f))
        except (json.JSONDecodeError, TypeError):
            return None

    def create_task(
        self,
        recipient_id: str,
        task_type: str,
        title: str,
        description: str,
        priority: str = "normal",
    ) -> SwarmTask:
        """Create and dispatch a task to another Centurion."""
        task = SwarmTask(
            task_id=f"{int(time.time())}_{self.centurion_id}_{recipient_id}",
            sender_id=self.centurion_id,
            recipient_id=recipient_id,
            task_type=task_type,
            title=title,
            description=description,
            priority=priority,
            created_at=time.time(),
        )
        self._save_task(task)

        # Send a fleet message to notify the recipient
        if self.transport:
            # Network mode — send via HTTP
            self.transport.send_message(
                recipient_id=recipient_id,
                subject=f"[TASK] {title}",
                body=f"Type: {task_type}\nPriority: {priority}\n\n{description}\n\nTask ID: {task.task_id}",
                priority=priority,
            )
        else:
            # Local mode — file-based messaging
            send_fleet_message(
                sender_id=self.centurion_id,
                recipient_id=recipient_id,
                subject=f"[TASK] {title}",
                body=f"Type: {task_type}\nPriority: {priority}\n\n{description}\n\nTask ID: {task.task_id}",
                priority=priority,
            )

        return task

    def broadcast_task(
        self,
        task_type: str,
        title: str,
        description: str,
        priority: str = "normal",
    ) -> SwarmTask:
        """Broadcast a task to all available Centurions (first to accept gets it)."""
        return self.create_task("any", task_type, title, description, priority)

    def get_pending_tasks(self) -> list[SwarmTask]:
        """Get tasks assigned to this Centurion that are still pending."""
        tasks = []
        for fname in os.listdir(self._tasks_dir):
            if not fname.endswith(".json"):
                continue
            task = self._load_task(fname[:-5])
            if task and task.recipient_id in (self.centurion_id, "any", "all"):
                if task.status in ("pending",):
                    tasks.append(task)
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)

    def accept_task(self, task_id: str) -> Optional[SwarmTask]:
        """Accept a pending task."""
        task = self._load_task(task_id)
        if not task or task.status != "pending":
            return None
        task.status = "accepted"
        task.assigned_to = self.centurion_id
        task.accepted_at = time.time()
        self._save_task(task)

        # Notify the sender
        if self.transport:
            self.transport.send_message(
                recipient_id=task.sender_id,
                subject=f"[ACCEPTED] {task.title}",
                body=f"Task {task.task_id} accepted by {self.centurion_id}.",
                priority="normal",
            )
        else:
            send_fleet_message(
                sender_id=self.centurion_id,
                recipient_id=task.sender_id,
                subject=f"[ACCEPTED] {task.title}",
                body=f"Task {task.task_id} accepted by {self.centurion_id}.",
                priority="normal",
            )
        return task

    def complete_task(self, task_id: str, result: str) -> bool:
        """Mark a task as completed with results."""
        task = self._load_task(task_id)
        if not task:
            return False
        task.status = "completed"
        task.result = result
        task.completed_at = time.time()
        self._save_task(task)

        if self.transport:
            self.transport.send_message(
                recipient_id=task.sender_id,
                subject=f"[COMPLETED] {task.title}",
                body=f"Task completed.\n\nResult:\n{result[:1000]}",
                priority="normal",
            )
        else:
            send_fleet_message(
                sender_id=self.centurion_id,
                recipient_id=task.sender_id,
                subject=f"[COMPLETED] {task.title}",
                body=f"Task completed.\n\nResult:\n{result[:1000]}",
                priority="normal",
            )
        return True

    def fail_task(self, task_id: str, reason: str) -> bool:
        """Mark a task as failed."""
        task = self._load_task(task_id)
        if not task:
            return False
        task.status = "failed"
        task.result = f"FAILED: {reason}"
        task.completed_at = time.time()
        self._save_task(task)
        return True

    # ── Delegation Helpers ───────────────────────────────────────────

    def delegate_quality_check(
        self,
        target_id: str,
        subject: str,
    ) -> SwarmTask:
        """Ask another Centurion to perform a quality check."""
        return self.create_task(
            recipient_id=target_id,
            task_type="quality_check",
            title=f"Quality Check: {subject}",
            description=f"Please review and provide quality feedback on: {subject}",
            priority="normal",
        )

    def delegate_to_overseer(
        self,
        subject: str,
        description: str,
        priority: str = "normal",
    ) -> SwarmTask:
        """Escalate something to the Overseer (Prefect)."""
        return self.create_task(
            recipient_id="prefect",  # Titus
            task_type="escalation",
            title=subject,
            description=description,
            priority=priority,
        )

    def request_assistance(
        self,
        description: str,
        priority: str = "high",
    ) -> SwarmTask:
        """Request help from any available Centurion."""
        return self.broadcast_task(
            task_type="assistance",
            title="Assistance Requested",
            description=description,
            priority=priority,
        )


# ── Swarm CLI ────────────────────────────────────────────────────────

def print_swarm_status(coordinator: SwarmCoordinator):
    """Print pending tasks and messages for a Centurion."""
    pending = coordinator.get_pending_tasks()
    messages = get_fleet_messages(coordinator.centurion_id)

    print(f"\n  📬 Swarm Status — {coordinator.centurion_id}")
    print(f"  {'='*40}")
    print(f"  Unread Messages: {len(messages)}")
    print(f"  Pending Tasks: {len(pending)}")

    if pending:
        print(f"\n  ── Pending Tasks ──")
        for t in pending:
            print(f"  [{t.priority.upper()}] {t.title}")
            print(f"       From: {t.sender_id} | Type: {t.task_type}")
            print(f"       {t.description[:80]}...")
            print()

    if messages:
        print(f"\n  ── Unread Messages ──")
        for msg in messages[:5]:
            print(f"  [{msg['priority'].upper()}] {msg['subject']}")
            print(f"       From: {msg['sender']} | {msg['body'][:80]}...")
            print()
