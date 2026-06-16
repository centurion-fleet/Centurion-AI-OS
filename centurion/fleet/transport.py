"""
CenturionOS — Fleet Network Transport
=======================================
HTTP-based network transport for inter-Centurion messaging.

Extends the file-based fleet registry/swarm with a network layer
so Centurions can communicate across machines on the internet.

Architecture:
    Each Centurion runs a small HTTP server (via the gateway's
    API server) that exposes fleet endpoints. Messages are sent
    as JSON POST requests to the recipient's endpoint.

    ┌──────────┐   POST /fleet/message   ┌──────────┐
    │ Titus    │ ──────────────────────► │ Eve      │
    │ (Ships)  │                         │ (Steve's)│
    │          │ ◄────────────────────── │          │
    └──────────┘   POST /fleet/message   └──────────┘

    If the recipient is unreachable, the message is queued
    in the local outbox for retry.

Usage:
    from centurion.fleet.transport import FleetTransport
    transport = FleetTransport(centurion_id="prefect", auth_token="...")
    transport.send_message(recipient_id="cent-002", subject="Hi", body="Hello Eve!")
"""

import json
import logging
import os
import time
import asyncio
from dataclasses import dataclass, field, asdict, fields
from typing import Optional, Callable

from .peers import FleetPeers, get_fleet_queue_dir, FleetPeer

logger = logging.getLogger(__name__)

# Default HTTP timeout for fleet messages (seconds)
DEFAULT_REQUEST_TIMEOUT = 10.0

# Retry settings for offline peer queue
MAX_RETRY_ATTEMPTS = 5
RETRY_BACKOFF_SECONDS = [30, 120, 300, 600, 1800]  # 30s, 2m, 5m, 10m, 30m


@dataclass
class OutboundMessage:
    """A message queued for delivery to a fleet peer."""
    message_id: str
    sender_id: str
    recipient_id: str
    subject: str
    body: str
    priority: str
    created_at: float
    retry_count: int = 0
    last_attempt: float = 0.0
    delivered: bool = False


@dataclass
class FleetMessageEnvelope:
    """
    The network-level envelope for fleet communication.
    Wraps the message content with routing and auth metadata.
    """
    message_id: str
    sender_id: str
    sender_name: str
    recipient_id: str
    subject: str
    body: str
    priority: str
    timestamp: float
    signature: str = ""  # Future: HMAC signature for verification


class FleetTransport:
    """
    Network transport for fleet communication.
    
    Handles:
    - Sending messages to fleet peers via HTTP
    - Receiving messages (via callback registered by the API server)
    - Offline message queueing with retry
    - Health check-ins (heartbeats)
    - Peer discovery
    """

    def __init__(
        self,
        centurion_id: str,
        centurion_name: str = "",
        auth_token: str = "",
        peers: Optional[FleetPeers] = None,
        on_message: Optional[Callable] = None,
    ):
        self.centurion_id = centurion_id
        self.centurion_name = centurion_name
        self.auth_token = auth_token
        self.peers = peers or FleetPeers()
        self.on_message = on_message  # Callback(message_envelope) when message received
        self._outbox_dir = get_fleet_queue_dir()

    # ── Sending ──────────────────────────────────────────────────────

    def send_message(
        self,
        recipient_id: str,
        subject: str,
        body: str,
        priority: str = "normal",
    ) -> bool:
        """
        Send a message to another Centurion.
        Returns True if sent successfully, False if queued for retry.
        """
        message_id = f"fleet_{int(time.time())}_{self.centurion_id}_{recipient_id}"
        
        envelope = FleetMessageEnvelope(
            message_id=message_id,
            sender_id=self.centurion_id,
            sender_name=self.centurion_name,
            recipient_id=recipient_id,
            subject=subject,
            body=body,
            priority=priority,
            timestamp=time.time(),
        )

        peer = self.peers.get(recipient_id)
        if not peer or not peer.address:
            logger.warning(
                f"No address known for Centurion '{recipient_id}'. "
                f"Queuing message '{message_id}' for retry."
            )
            self._queue_for_retry(envelope)
            return False

        try:
            return self._http_send(peer, envelope)
        except Exception as e:
            logger.error(f"Failed to send to {peer.name} ({peer.address}): {e}")
            self._queue_for_retry(envelope)
            return False

    def _http_send(self, peer: FleetPeer, envelope: FleetMessageEnvelope) -> bool:
        """Send an HTTP POST with the message envelope."""
        try:
            import urllib.request
            import urllib.error

            url = f"{peer.address.rstrip('/')}/fleet/message"
            payload = asdict(envelope)
            payload_json = json.dumps(payload).encode("utf-8")

            req = urllib.request.Request(
                url,
                data=payload_json,
                headers={
                    "Content-Type": "application/json",
                    "X-Centurion-ID": self.centurion_id,
                    "X-Centurion-Auth": self.auth_token,
                },
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=DEFAULT_REQUEST_TIMEOUT) as resp:
                if resp.status == 200:
                    # Update peer status
                    self.peers.update_status(
                        peer.centurion_id,
                        status="online",
                        last_seen=time.time(),
                    )
                    logger.info(f"Message {envelope.message_id} delivered to {peer.name}")
                    return True
                else:
                    logger.warning(
                        f"Peer {peer.name} returned HTTP {resp.status}"
                    )
                    return False

        except (urllib.error.URLError, urllib.error.HTTPError,
                ConnectionRefusedError, TimeoutError, OSError) as e:
            # Mark peer offline, will be retried
            self.peers.update_status(peer.centurion_id, status="offline")
            raise

    # ── Receiving ────────────────────────────────────────────────────

    def receive_message(self, envelope: FleetMessageEnvelope) -> dict:
        """
        Process an incoming fleet message.
        Called by the API server endpoint.
        Returns a response dict.
        """
        logger.info(
            f"Fleet message from {envelope.sender_name} ({envelope.sender_id}): "
            f"[{envelope.priority}] {envelope.subject}"
        )

        # Update sender's peer status
        self.peers.update_status(
            envelope.sender_id,
            status="online",
            last_seen=time.time(),
        )

        # Fire callback if registered
        if self.on_message:
            try:
                self.on_message(envelope)
            except Exception as e:
                logger.error(f"Message callback error: {e}")

        return {
            "status": "delivered",
            "message_id": envelope.message_id,
            "recipient": self.centurion_id,
            "timestamp": time.time(),
        }

    # ── Offline Queue ────────────────────────────────────────────────

    def _queue_for_retry(self, envelope: FleetMessageEnvelope):
        """Queue an undelivered message for later retry."""
        os.makedirs(self._outbox_dir, exist_ok=True)
        path = os.path.join(self._outbox_dir, f"{envelope.message_id}.json")
        with open(path, "w") as f:
            json.dump(asdict(envelope), f, indent=2)
        logger.info(f"Message {envelope.message_id} queued for retry")

    def process_outbox(self) -> int:
        """
        Attempt to deliver all queued messages.
        Returns the number of messages still pending after this attempt.
        """
        if not os.path.exists(self._outbox_dir):
            return 0

        pending = 0
        now = time.time()

        for fname in os.listdir(self._outbox_dir):
            if not fname.endswith(".json"):
                continue

            fpath = os.path.join(self._outbox_dir, fname)
            try:
                with open(fpath) as f:
                    data = json.load(f)

                # Check retry count
                retry_count = data.get("retry_count", 0)
                last_attempt = data.get("last_attempt", 0)

                # Apply backoff: skip if too soon for next retry
                if retry_count < len(RETRY_BACKOFF_SECONDS):
                    next_retry = last_attempt + RETRY_BACKOFF_SECONDS[retry_count]
                    if now < next_retry:
                        pending += 1
                        continue

                # Attempt delivery
                envelope_keys = {f.name for f in fields(FleetMessageEnvelope)}
                envelope = FleetMessageEnvelope(
                    **{k: v for k, v in data.items() if k in envelope_keys}
                )
                peer = self.peers.get(envelope.recipient_id)

                if peer and peer.address:
                    try:
                        self._http_send(peer, envelope)
                        os.remove(fpath)  # Success — remove from queue
                        continue
                    except Exception:
                        pass

                # Delivery failed — update retry count
                data["retry_count"] = retry_count + 1
                data["last_attempt"] = now

                if data["retry_count"] >= MAX_RETRY_ATTEMPTS:
                    logger.warning(
                        f"Message {envelope.message_id} failed after "
                        f"{MAX_RETRY_ATTEMPTS} attempts. Discarding."
                    )
                    os.remove(fpath)
                else:
                    with open(fpath, "w") as f:
                        json.dump(data, f, indent=2)
                    pending += 1

            except (json.JSONDecodeError, KeyError, OSError) as e:
                logger.error(f"Outbox processing error for {fname}: {e}")
                pending += 1

        return pending

    # ── Health / Check-in ────────────────────────────────────────────

    def send_heartbeat(self, peer_id: str, version: str = "") -> bool:
        """
        Send a health check-in to a fleet peer.
        Lightweight — confirms this Centurion is alive and reachable.
        """
        return self.send_message(
            recipient_id=peer_id,
            subject="[HEARTBEAT]",
            body=json.dumps({
                "type": "heartbeat",
                "version": version or "0.3.0",
                "timestamp": time.time(),
            }),
            priority="low",
        )

    def broadcast_heartbeat(self, version: str = ""):
        """Send heartbeat to all known peers."""
        for peer in self.peers.list_all():
            if peer.address:
                try:
                    self.send_heartbeat(peer.centurion_id, version)
                except Exception:
                    pass

    # ── Peer Discovery ───────────────────────────────────────────────

    def discover_peers(self, peer_list: list[dict]):
        """
        Register or update multiple peers at once.
        Expects list of dicts with keys: centurion_id, name, address,
        optionally auth_token, telegram_handle.
        """
        for pdata in peer_list:
            peer = FleetPeer(**{k: v for k, v in pdata.items()
                                 if k in asdict(FleetPeer("", "", ""))})
            self.peers.register(peer)
