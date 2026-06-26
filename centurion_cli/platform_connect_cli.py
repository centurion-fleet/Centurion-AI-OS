"""``centurion platform connect`` — bind Centurion AI OS to the portal chat broker."""
from __future__ import annotations

import argparse
import os
import sys

from centurion_cli.colors import Colors, color
from centurion_cli.config import load_config, save_config


DEFAULT_WS = "wss://centurion-realtime.fly.dev/agent/ws"


def _ensure_portal_platform(config: dict, api_key: str, ws_url: str) -> None:
    platforms = config.setdefault("platforms", {})
    if not isinstance(platforms, dict):
        platforms = {}
        config["platforms"] = platforms
    portal = platforms.setdefault("portal", {})
    if not isinstance(portal, dict):
        portal = {}
        platforms["portal"] = portal
    portal["enabled"] = True
    portal["api_key"] = api_key
    extra = portal.setdefault("extra", {})
    if not isinstance(extra, dict):
        extra = {}
        portal["extra"] = extra
    extra["ws_url"] = ws_url
    extra["primary_channel"] = "portal"


def cmd_platform_connect(args: argparse.Namespace) -> int:
    api_key = (getattr(args, "key", None) or os.getenv("CENTURION_AGENT_API_KEY", "")).strip()
    if not api_key.startswith("centurion_key_"):
        print(
            color(
                "Provide --key centurion_key_... from Account → My Centurions on the portal.",
                Colors.YELLOW,
            ),
            file=sys.stderr,
        )
        return 1

    ws_url = (getattr(args, "ws_url", None) or os.getenv("CENTURION_PORTAL_WS_URL", DEFAULT_WS)).rstrip("/")
    config = load_config() or {}
    _ensure_portal_platform(config, api_key, ws_url)
    save_config(config)

    os.environ["CENTURION_AGENT_API_KEY"] = api_key
    os.environ["CENTURION_PORTAL_WS_URL"] = ws_url

    print()
    print(color("  Portal chat connected (config saved)", Colors.GREEN))
    print(f"  WebSocket: {ws_url}")
    print(f"  API key:   {api_key[:18]}…")
    print()
    print("  Restart the gateway so Titus receives portal messages:")
    print(color("    centurion gateway restart", Colors.CYAN))
    print()
    print("  Optional fleet bind:")
    print(color("    centurion fleet checkin --cloud", Colors.CYAN))
    print()
    print("  Telegram stays available when enabled in config — portal is primary.")
    return 0


def platform_connect_command(args: argparse.Namespace) -> int:
    sub = getattr(args, "platform_action", None)
    if sub == "connect":
        return cmd_platform_connect(args)
    print("Unknown platform subcommand. Run `centurion platform connect -h`.", file=sys.stderr)
    return 1


def add_parser(subparsers) -> None:
    parser = subparsers.add_parser(
        "platform",
        help="Connect Centurion AI OS to the portal realtime chat broker",
    )
    plat_sub = parser.add_subparsers(dest="platform_action")

    connect = plat_sub.add_parser(
        "connect",
        help="Save portal API key and enable the portal platform adapter",
    )
    connect.add_argument(
        "--key",
        help="centurion_key_* from Account → My Centurions (or CENTURION_AGENT_API_KEY)",
    )
    connect.add_argument(
        "--ws-url",
        dest="ws_url",
        default=None,
        help=f"Realtime gateway URL (default: {DEFAULT_WS})",
    )
    connect.set_defaults(func=platform_connect_command)

    parser.set_defaults(func=platform_connect_command)
