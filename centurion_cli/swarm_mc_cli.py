"""``centurion swarm connect`` — store Mission Control project token for Titus tools."""
from __future__ import annotations

import argparse
import os
import sys

from centurion_cli.colors import Colors, color
from centurion_cli.config import load_config, save_config
from gateway.swarm_mc import save_mc_config


def cmd_swarm_connect(args: argparse.Namespace) -> int:
    token = (getattr(args, "token", None) or os.getenv("CTK_PROJECT_TOKEN", "")).strip()
    install_id = (getattr(args, "install_id", None) or os.getenv("CENTURION_INSTALL_ID", "")).strip()
    project_id = (getattr(args, "project_id", None) or "").strip()

    if not token.startswith("ctk_proj_"):
        print(
            color("Provide --token ctk_proj_... from Mission Control setup or invite accept.", Colors.YELLOW),
            file=sys.stderr,
        )
        return 1
    if not install_id:
        print(color("Provide --install-id (fleet checkin install_id).", Colors.YELLOW), file=sys.stderr)
        return 1
    if not project_id:
        print(color("Provide --project-id (swarm project UUID).", Colors.YELLOW), file=sys.stderr)
        return 1

    save_mc_config(project_id, token, install_id)

    config = load_config() or {}
    platforms = config.setdefault("platforms", {})
    mc = platforms.setdefault("swarm_mc", {})
    if isinstance(mc, dict):
        mc["enabled"] = True
        mc["project_id"] = project_id
        mc["install_id"] = install_id
    save_config(config)

    os.environ["CTK_PROJECT_TOKEN"] = token
    os.environ["CENTURION_INSTALL_ID"] = install_id

    print()
    print(color("  Mission Control connected", Colors.GREEN))
    print(f"  Project:   {project_id}")
    print(f"  Install:   {install_id}")
    print(f"  Token:     {token[:22]}…")
    print()
    print("  Titus can use mission_control_* tools when the gateway is running.")
    return 0


def swarm_command(args: argparse.Namespace) -> int:
    sub = getattr(args, "swarm_action", None)
    if sub == "connect":
        return cmd_swarm_connect(args)
    print("Unknown swarm subcommand. Run `centurion swarm connect -h`.", file=sys.stderr)
    return 1


def add_parser(subparsers) -> None:
    parser = subparsers.add_parser(
        "swarm",
        help="Mission Control project token and sync configuration",
    )
    swarm_sub = parser.add_subparsers(dest="swarm_action")

    connect = swarm_sub.add_parser(
        "connect",
        help="Save ctk_proj token for Mission Control APIs",
    )
    connect.add_argument("--token", help="ctk_proj_* project token")
    connect.add_argument("--install-id", dest="install_id", help="Fleet install_id")
    connect.add_argument("--project-id", dest="project_id", help="Swarm project UUID")
    connect.set_defaults(func=swarm_command)

    parser.set_defaults(func=swarm_command)
