"""
Centurion Portal platform adapter.

Connects the gateway to the portal realtime broker (Fly) so owner chat uses
the same Titus agent loop as Telegram. Telegram remains optional via config.

Protocol: see Centurion-website-v3-3 docs/platform-portal-protocol.md
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import aiohttp

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    aiohttp = None  # type: ignore[assignment]

from gateway.config import Platform, PlatformConfig
from gateway.platforms.base import (
    BasePlatformAdapter,
    MessageEvent,
    MessageType,
    SendResult,
)
from gateway.session import SessionSource

logger = logging.getLogger(__name__)

DEFAULT_WS = "wss://centurion-realtime.fly.dev/agent/ws"
HEARTBEAT_SEC = 30
_BACKOFF_STEPS = [5, 10, 30, 60]


def check_portal_requirements() -> bool:
    """Portal adapter needs aiohttp and a centurion_key_* API key."""
    if not AIOHTTP_AVAILABLE:
        return False
    key = os.getenv("CENTURION_AGENT_API_KEY", "").strip()
    if key.startswith("centurion_key_"):
        return True
    return False


def _format_history_context(history: List[Dict[str, Any]]) -> str:
    lines: List[str] = []
    for msg in history[-12:]:
        role = str(msg.get("role", "")).strip().lower()
        text = str(msg.get("content", "")).strip()
        if not text or role not in {"user", "assistant"}:
            continue
        label = "User" if role == "user" else "Assistant"
        lines.append(f"{label}: {text}")
    if not lines:
        return ""
    return "Recent portal conversation:\n" + "\n".join(lines)


class PortalPlatformAdapter(BasePlatformAdapter):
    """WebSocket client to the portal realtime gateway."""

    MAX_MESSAGE_LENGTH = 32_000

    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform.PORTAL)
        extra = config.extra or {}
        self._api_key = (
            (config.api_key or config.token or os.getenv("CENTURION_AGENT_API_KEY", "")).strip()
        )
        ws_base = str(extra.get("ws_url") or os.getenv("CENTURION_PORTAL_WS_URL", DEFAULT_WS)).rstrip("/")
        self._ws_url = ws_base
        self._primary_channel = str(extra.get("primary_channel") or "portal")

        self._session: Optional["aiohttp.ClientSession"] = None
        self._ws: Optional["aiohttp.ClientWebSocketResponse"] = None
        self._listen_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None

        self._centurion_id: str = ""
        self._customer_id: str = ""
        self._settings_version: int = 0
        self._portal_router_enabled: bool = True

        # conversation_id -> reply_to message_id for outbound responses
        self._reply_targets: Dict[str, str] = {}
        self._stream_buffers: Dict[str, str] = {}

    def _ws_connect_url(self) -> str:
        return f"{self._ws_url}?api_key={self._api_key}"

    async def connect(self) -> bool:
        if not AIOHTTP_AVAILABLE:
            logger.warning("[%s] aiohttp not installed", self.name)
            return False
        if not self._api_key.startswith("centurion_key_"):
            logger.warning("[%s] CENTURION_AGENT_API_KEY must be centurion_key_*", self.name)
            return False

        try:
            ok = await self._open_ws()
            if not ok:
                return False
            self._listen_task = asyncio.create_task(self._listen_loop())
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            self._running = True
            logger.info("[%s] Connected to portal realtime (%s)", self.name, self._ws_url)
            return True
        except Exception as exc:
            logger.error("[%s] connect failed: %s", self.name, exc)
            return False

    async def _open_ws(self) -> bool:
        await self._cleanup_ws()
        self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120))
        self._ws = await self._session.ws_connect(self._ws_connect_url(), heartbeat=30, timeout=60)
        return True

    async def _cleanup_ws(self) -> None:
        if self._ws and not self._ws.closed:
            await self._ws.close()
        self._ws = None
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None

    async def disconnect(self) -> None:
        self._running = False
        for task in (self._heartbeat_task, self._listen_task):
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        self._heartbeat_task = None
        self._listen_task = None
        await self._cleanup_ws()
        logger.info("[%s] Disconnected", self.name)

    async def _heartbeat_loop(self) -> None:
        while self._running:
            await asyncio.sleep(HEARTBEAT_SEC)
            if self._ws and not self._ws.closed:
                try:
                    await self._ws.send_json({"type": "heartbeat"})
                except Exception:
                    logger.debug("[%s] heartbeat failed", self.name, exc_info=True)

    async def _listen_loop(self) -> None:
        backoff_idx = 0
        while self._running:
            try:
                await self._read_messages()
            except asyncio.CancelledError:
                return
            except Exception as exc:
                logger.warning("[%s] websocket error: %s", self.name, exc)

            if not self._running:
                return

            delay = _BACKOFF_STEPS[min(backoff_idx, len(_BACKOFF_STEPS) - 1)]
            logger.info("[%s] reconnecting in %ss", self.name, delay)
            await asyncio.sleep(delay)
            backoff_idx += 1
            try:
                if await self._open_ws():
                    backoff_idx = 0
            except Exception as exc:
                logger.warning("[%s] reconnect failed: %s", self.name, exc)

    async def _read_messages(self) -> None:
        if self._ws is None or self._ws.closed:
            return
        async for ws_msg in self._ws:
            if ws_msg.type == aiohttp.WSMsgType.TEXT:
                try:
                    data = json.loads(ws_msg.data)
                except json.JSONDecodeError:
                    continue
                await self._handle_inbound(data)
            elif ws_msg.type in {aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR}:
                break

    async def _handle_inbound(self, data: Dict[str, Any]) -> None:
        msg_type = data.get("type")

        if msg_type == "connected":
            self._centurion_id = str(data.get("centurion_id") or "")
            self._customer_id = str(data.get("customer_id") or "")
            logger.info("[%s] registered centurion %s", self.name, self._centurion_id)
            return

        if msg_type == "platform_config":
            await self._apply_platform_config(data.get("config") or {})
            return

        if msg_type == "user_message":
            asyncio.create_task(self._on_user_message(data))
            return

        if msg_type in {"pong", "queue_flush_complete"}:
            return

        logger.debug("[%s] inbound %s", self.name, msg_type)

    async def _apply_platform_config(self, config: Dict[str, Any]) -> None:
        self._settings_version = int(config.get("settings_version") or 0)
        self._portal_router_enabled = bool(config.get("portal_router_enabled", True))
        self.config.extra["portal_platform_config"] = dict(config)
        logger.info(
            "[%s] applied platform_config v%s (router=%s)",
            self.name,
            self._settings_version,
            self._portal_router_enabled,
        )
        if self._ws and not self._ws.closed:
            await self._ws.send_json(
                {
                    "type": "platform_config_ack",
                    "settings_version": self._settings_version,
                }
            )

    async def _on_user_message(self, data: Dict[str, Any]) -> None:
        content = str(data.get("content") or "").strip()
        if not content:
            return

        conversation_id = str(data.get("conversation_id") or "")
        message_id = str(data.get("message_id") or "")
        if conversation_id and message_id:
            self._reply_targets[conversation_id] = message_id

        history = data.get("history")
        channel_context = None
        if isinstance(history, list) and history:
            channel_context = _format_history_context(history)

        source = self.build_source(
            chat_id=conversation_id or "portal",
            chat_name="Portal Chat",
            chat_type="dm",
            user_id=self._customer_id or "owner",
            user_name="Owner",
        )

        event = MessageEvent(
            text=content,
            message_type=MessageType.TEXT,
            source=source,
            raw_message=data,
            message_id=message_id or None,
            channel_context=channel_context,
            timestamp=datetime.now(),
        )
        await self.handle_message(event)

    async def _send_ws(self, payload: Dict[str, Any]) -> bool:
        if not self._ws or self._ws.closed:
            logger.warning("[%s] cannot send — websocket closed", self.name)
            return False
        try:
            await self._ws.send_json(payload)
            return True
        except Exception as exc:
            logger.error("[%s] send failed: %s", self.name, exc)
            return False

    async def send(
        self,
        chat_id: str,
        content: str,
        reply_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SendResult:
        reply_to_id = reply_to or self._reply_targets.get(chat_id)
        payload = {
            "type": "response",
            "conversation_id": chat_id,
            "reply_to_message_id": reply_to_id,
            "content": content,
        }
        if metadata and metadata.get("model"):
            payload["model"] = metadata["model"]
        ok = await self._send_ws(payload)
        return SendResult(
            success=ok,
            message_id=str(uuid.uuid4()) if ok else None,
            error=None if ok else "websocket send failed",
        )

    async def edit_message(
        self,
        chat_id: str,
        message_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        *,
        finalize: bool = False,
    ) -> SendResult:
        """Stream tokens to the portal via response_token / response_done."""
        del message_id  # portal streams per conversation, not per message id
        buf = self._stream_buffers.setdefault(chat_id, "")
        if content:
            delta = content[len(buf) :] if content.startswith(buf) else content
            buf = content
            self._stream_buffers[chat_id] = buf
            if delta:
                await self._send_ws(
                    {
                        "type": "response_token",
                        "conversation_id": chat_id,
                        "content": delta,
                    }
                )

        if finalize:
            reply_to_id = self._reply_targets.get(chat_id)
            model = (metadata or {}).get("model")
            done: Dict[str, Any] = {
                "type": "response_done",
                "conversation_id": chat_id,
                "reply_to_message_id": reply_to_id,
            }
            if model:
                done["model"] = model
            ok = await self._send_ws(done)
            self._stream_buffers.pop(chat_id, None)
            return SendResult(success=ok, message_id=str(uuid.uuid4()) if ok else None)

        return SendResult(success=True, message_id=str(uuid.uuid4()))

    async def send_proactive(
        self,
        content: str,
        *,
        conversation_id: Optional[str] = None,
        model: Optional[str] = None,
    ) -> SendResult:
        """Titus-initiated message to the owner (persisted by the gateway)."""
        payload: Dict[str, Any] = {
            "type": "proactive_message",
            "content": content,
        }
        if conversation_id:
            payload["conversation_id"] = conversation_id
        if model:
            payload["model"] = model
        ok = await self._send_ws(payload)
        return SendResult(success=ok, message_id=str(uuid.uuid4()) if ok else None)

    @property
    def portal_router_enabled(self) -> bool:
        return self._portal_router_enabled

    @property
    def centurion_id(self) -> str:
        return self._centurion_id
