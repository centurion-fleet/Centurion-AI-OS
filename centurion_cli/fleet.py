"""CLI for Centurion fleet management — ``centurion fleet …`` subcommand."""

from __future__ import annotations

import argparse
import os
import sys


def _registry_path(args: argparse.Namespace) -> str:
    return getattr(args, "registry", None) or os.path.join(
        os.environ.get("CENTURION_HOME", os.path.expanduser("~/.centurion")),
        "fleet",
        "registry.json",
    )


def fleet_status(args: argparse.Namespace) -> None:
    from centurion.fleet.overseer import OverseerCommandCenter, format_fleet_report
    from centurion.fleet.registry import FleetRegistry

    registry = FleetRegistry(_registry_path(args))
    overseer = OverseerCommandCenter(registry)
    print(format_fleet_report(overseer))


def fleet_list(args: argparse.Namespace) -> None:
    from centurion.fleet.registry import FleetRegistry

    registry = FleetRegistry(_registry_path(args))
    records = registry.list_all()

    print(f"\n{'=' * 60}")
    print(f"  Centurion Fleet — {len(records)} registered")
    print(f"{'=' * 60}")

    for r in records:
        i = r.identity
        s = r.status
        print(
            f"  {i.emoji} {i.name:12s} | {i.owner_name:20s} | "
            f"{i.role:12s} | {s.status:10s} | {s.model:20s}"
        )
    print()


def fleet_show(args: argparse.Namespace) -> None:
    from centurion.fleet.overseer import OverseerCommandCenter
    from centurion.fleet.registry import FleetRegistry

    registry = FleetRegistry(_registry_path(args))
    overseer = OverseerCommandCenter(registry)
    detail = overseer.centurion_detail(args.centurion_id)
    if "error" in detail:
        print(f"Error: {detail['error']}")
        return

    print(f"\n{'=' * 50}")
    print(f"  {detail['identity']['emoji']} {detail['identity']['name']}")
    print(f"  {detail['identity']['id']}")
    print(f"{'=' * 50}")
    print(f"  Owner:  {detail['identity']['owner']}")
    print(f"  Role:   {detail['identity']['role']}")
    print(f"  Status: {detail['status']['status']}")
    print(f"  Host:   {detail['status']['host']}")
    print(f"  Model:  {detail['status']['model']}")
    print(f"  Memory: {detail['status']['memory']}")
    print(f"  Uptime: {detail['status']['uptime_hours']:.1f}h")

    if detail.get("unresolved_violations"):
        print(f"\n  ⚠ {detail['unresolved_violations']} unresolved violations")
        for v in detail["violations"][:5]:
            print(f"     [{v['severity']}] {v['policy_id']}: {v['detail'][:80]}")

    if detail.get("capabilities"):
        print(f"\n  Capabilities: {', '.join(detail['capabilities'])}")
    print()


def fleet_checkin(args: argparse.Namespace) -> None:
    from centurion.fleet.health import HealthCheckRunner
    from centurion.fleet.registry import FleetRegistry

    centurion_id = args.centurion_id or os.environ.get("CENTURION_ID", "")
    if not centurion_id:
        print("Error: No CENTURION_ID set. Provide --id or set CENTURION_ID env var.")
        sys.exit(1)

    registry = FleetRegistry(
        os.path.join(
            os.environ.get("CENTURION_HOME", os.path.expanduser("~/.centurion")),
            "fleet",
            "registry.json",
        )
    )
    runner = HealthCheckRunner(centurion_id, registry)
    status = args.status or "active"

    if runner.check_in(status=status):
        print(f"✅ {centurion_id} checked in as '{status}'")
    else:
        print(f"❌ {centurion_id} not found in registry")
        sys.exit(1)

    if getattr(args, "cloud", False):
        from centurion_cli.fleet_cloud import cloud_checkin_from_cli

        sys.exit(cloud_checkin_from_cli())


def fleet_policies(args: argparse.Namespace) -> None:
    from centurion.policies.engine import PolicyStore

    store = PolicyStore()

    if args.action == "list":
        for cat in store.list_categories():
            policies = store.get_policies_by_category(cat)
            print(f"\n  [{cat.upper()}]")
            for p in policies:
                print(
                    f"    {p.policy_id:12s} | {p.title:35s} | "
                    f"v{p.version:5s} | {p.enforce_level:10s}"
                )
        print()
    elif args.action == "seed":
        count = store.seed_default_policies()
        print(f"Seeded {count} default policies")
    elif args.action == "violations":
        violations = store.get_violations(
            centurion_id=args.centurion_id,
            unresolved_only=args.unresolved,
        )
        print(f"\n  {'=' * 50}")
        print(f"  Policy Violations ({len(violations)})")
        print(f"  {'=' * 50}")
        for v in violations:
            print(f"  [{v.severity}] {v.centurion_id} violated {v.policy_id}")
            print(f"       {v.detail[:100]}")
        print()
    else:
        print(f"Unknown action: {args.action}")
        sys.exit(1)


def fleet_deploy(args: argparse.Namespace) -> None:
    from centurion.install.deploy import CenturionDeployer

    deployer = CenturionDeployer(
        name=args.name,
        owner_name=args.owner,
        owner_email=args.owner_email,
        soul_template=args.soul_template,
        centurion_id=args.centurion_id,
        model=args.model,
        provider=args.provider,
        telegram_token=args.telegram_token,
        api_key=args.api_key,
        install_path=args.install_path,
    )
    deployer.deploy()


def _add_fleet_subcommands(
    parser: argparse.ArgumentParser,
    *,
    registry_help: str = "Path to fleet registry",
) -> None:
    parser.add_argument("--registry", help=registry_help)

    sub = parser.add_subparsers(dest="fleet_command")

    p_status = sub.add_parser("status", help="Show fleet health")
    p_status.set_defaults(func=fleet_status)

    p_list = sub.add_parser("list", help="List all Centurions")
    p_list.set_defaults(func=fleet_list)

    p_show = sub.add_parser("show", help="Show Centurion details")
    p_show.add_argument("centurion_id", help="Centurion ID (e.g., prefect, cent-004)")
    p_show.set_defaults(func=fleet_show)

    p_ci = sub.add_parser("checkin", help="Send health check heartbeat")
    p_ci.add_argument("--id", dest="centurion_id", help="Centurion ID (default: $CENTURION_ID)")
    p_ci.add_argument("--status", default="active", help="Status to report")
    p_ci.add_argument(
        "--cloud",
        action="store_true",
        help="Also POST check-in to Centurion cloud portal (requires OPENROUTER_API_KEY)",
    )
    p_ci.set_defaults(func=fleet_checkin)

    p_pol = sub.add_parser("policies", help="Manage fleet policies")
    p_pol.add_argument("action", choices=["list", "seed", "violations"])
    p_pol.add_argument("--centurion-id", help="Filter violations by Centurion")
    p_pol.add_argument(
        "--unresolved",
        action="store_true",
        default=True,
        help="Show only unresolved violations",
    )
    p_pol.set_defaults(func=fleet_policies)

    p_dep = sub.add_parser("deploy", help="Deploy a new Centurion")
    p_dep.add_argument("--name", required=True, help="Centurion name")
    p_dep.add_argument("--owner", required=True, help="Owner name")
    p_dep.add_argument("--owner-email", default="", help="Owner email")
    p_dep.add_argument(
        "--soul-template",
        default="default",
        choices=["yeshi", "titus", "default"],
    )
    p_dep.add_argument("--centurion-id", help="Override Centurion ID")
    p_dep.add_argument("--model", default="deepseek-v4-flash")
    p_dep.add_argument("--provider", default="deepseek")
    p_dep.add_argument("--telegram-token", help="Telegram bot token")
    p_dep.add_argument("--api-key", help="API key")
    p_dep.add_argument("--install-path", help="Custom install path")
    p_dep.set_defaults(func=fleet_deploy)


def build_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    """Register ``centurion fleet`` on the main CLI argparse tree."""
    fleet_parser = subparsers.add_parser(
        "fleet",
        help="Fleet registry, health, policies, and deployment",
        description="Manage the Centurion fleet (registry, check-ins, policies, deploy)",
    )
    _add_fleet_subcommands(fleet_parser)
    return fleet_parser


def fleet_command(args: argparse.Namespace) -> int:
    """Dispatch ``centurion fleet <subcommand>``."""
    func = getattr(args, "func", None)
    if func is None:
        print("Usage: centurion fleet <status|list|show|checkin|policies|deploy>")
        return 1
    func(args)
    return 0


def run_module_main(argv: list[str] | None = None) -> None:
    """Entry for ``python -m centurion`` — accepts legacy top-level fleet verbs."""
    argv = list(argv if argv is not None else sys.argv[1:])
    if argv and argv[0] == "fleet":
        argv = argv[1:]
    elif argv and argv[0] == "centurion" and len(argv) > 1:
        # legacy: python -m centurion centurion <id> -> show <id>
        argv = ["show", argv[1], *argv[2:]]

    parser = argparse.ArgumentParser(description="Centurion OS — Fleet Management")
    _add_fleet_subcommands(parser)
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    args.func(args)
