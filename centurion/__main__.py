"""
CenturionOS — CLI Entry Points
================================
Command-line interface for fleet management and deployment.

Usage:
    python3 -m centurion fleet status      # Show fleet health
    python3 -m centurion fleet list        # List all Centurions
    python3 -m centurion deploy --name ...  # Deploy new Centurion
    python3 -m centurion doc read <name>   # Read latest version of a document
    python3 -m centurion doc publish <name> --file <path>  # Publish new version
    python3 -m centurion doc status <name> # Check current version info
    python3 -m centurion doc history <name> # View version history
    python3 -m centurion doc list          # List all tracked documents
    python3 -m centurion doc verify <name> # Verify @latest pointer integrity
"""

import argparse
import os
import sys
import json


def fleet_status(args):
    """Show fleet health status."""
    from centurion.fleet.registry import FleetRegistry
    from centurion.fleet.overseer import OverseerCommandCenter, format_fleet_report

    registry = FleetRegistry(
        getattr(args, 'registry', None) or 
        os.path.join(os.environ.get("CENTURION_HOME", "~/.centurion"), "fleet", "registry.json")
    )
    overseer = OverseerCommandCenter(registry)
    report = format_fleet_report(overseer)
    print(report)


def fleet_list(args):
    """List all Centurions in the fleet."""
    from centurion.fleet.registry import FleetRegistry

    registry = FleetRegistry(
        getattr(args, 'registry', None) or 
        os.path.join(os.environ.get("CENTURION_HOME", "~/.centurion"), "fleet", "registry.json")
    )
    records = registry.list_all()

    print(f"\n{'='*60}")
    print(f"  Centurion Fleet — {len(records)} registered")
    print(f"{'='*60}")

    for r in records:
        i = r.identity
        s = r.status
        age = f"{int(s.last_checkin)}" if s.last_checkin else "never"
        print(f"  {i.emoji} {i.name:12s} | {i.owner_name:20s} | "
              f"{i.role:12s} | {s.status:10s} | {s.model:20s}")

    print()


def fleet_centurion(args):
    """Show details for a specific Centurion."""
    from centurion.fleet.overseer import OverseerCommandCenter

    registry_path = getattr(args, 'registry', None) or os.path.join(
        os.environ.get("CENTURION_HOME", "~/.centurion"), "fleet", "registry.json"
    )
    from centurion.fleet.registry import FleetRegistry
    registry = FleetRegistry(registry_path)
    overseer = OverseerCommandCenter(registry)

    detail = overseer.centurion_detail(args.centurion_id)
    if "error" in detail:
        print(f"Error: {detail['error']}")
        return

    print(f"\n{'='*50}")
    print(f"  {detail['identity']['emoji']} {detail['identity']['name']}")
    print(f"  {detail['identity']['id']}")
    print(f"{'='*50}")
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


def checkin(args):
    """Send a health check heartbeat from this Centurion."""
    from centurion.fleet.health import HealthCheckRunner
    from centurion.fleet.registry import FleetRegistry

    centurion_id = args.centurion_id or os.environ.get("CENTURION_ID", "")
    if not centurion_id:
        print("Error: No CENTURION_ID set. Provide --id or set CENTURION_ID env var.")
        sys.exit(1)

    registry = FleetRegistry(
        os.path.join(os.environ.get("CENTURION_HOME", "~/.centurion"), "fleet", "registry.json")
    )
    runner = HealthCheckRunner(centurion_id, registry)
    status = args.status or "active"

    if runner.check_in(status=status):
        print(f"✅ {centurion_id} checked in as '{status}'")
    else:
        print(f"❌ {centurion_id} not found in registry")
        sys.exit(1)


def policies(args):
    """List and manage fleet policies."""
    from centurion.policies.engine import PolicyStore

    store = PolicyStore()
    
    if args.action == "list":
        for cat in store.list_categories():
            policies = store.get_policies_by_category(cat)
            print(f"\n  [{cat.upper()}]")
            for p in policies:
                print(f"    {p.policy_id:12s} | {p.title:35s} | v{p.version:5s} | {p.enforce_level:10s}")
        print()

    elif args.action == "seed":
        count = store.seed_default_policies()
        print(f"Seeded {count} default policies")

    elif args.action == "violations":
        violations = store.get_violations(
            centurion_id=args.centurion_id,
            unresolved_only=args.unresolved,
        )
        print(f"\n  {'='*50}")
        print(f"  Policy Violations ({len(violations)})")
        print(f"  {'='*50}")
        for v in violations:
            print(f"  [{v.severity}] {v.centurion_id} violated {v.policy_id}")
            print(f"       {v.detail[:100]}")
        print()

    else:
        print(f"Unknown action: {args.action}")


def deploy(args):
    """Deploy a new Centurion to this machine."""
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


# ── Document Versioning Commands ──────────────────────────────────

def doc_read(args):
    """Read the latest version of a document and print it."""
    from centurion.docs.manager import DocumentManager, DocumentError
    dm = DocumentManager()
    try:
        content, meta = dm.read(args.name)
        print(f"─── {args.name} (v{meta.version}) ───")
        print(f"Published: {meta.published_by} | {meta.lines} lines | {meta.bytes} bytes")
        print(f"Checksum: {meta.checksum[:16]}...")
        print(f"Summary: {meta.summary}")
        print("─" * 40)
        print(content)
    except DocumentError as e:
        print(f"Error: {e}")
        sys.exit(1)


def doc_publish(args):
    """Publish a new version from a file."""
    from centurion.docs.manager import DocumentManager
    dm = DocumentManager()
    file_path = args.file
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    with open(file_path, "r") as f:
        content = f.read()
    version = dm.publish(
        name=args.name,
        content=content,
        published_by=args.author,
        summary=args.summary,
    )
    print(f"✅ Published {args.name} as v{version.version}")
    print(f"   Path: {version.path}")
    print(f"   Lines: {version.lines}")
    print(f"   Checksum: {version.checksum[:16]}...")


def doc_status(args):
    """Show current version info for a document."""
    from centurion.docs.manager import DocumentManager
    dm = DocumentManager()
    status = dm.status(args.name)
    if status is None:
        print(f"Document '{args.name}' has never been published.")
        sys.exit(1)
    print(f"─── {status['name']} ───")
    print(f"  Version:       v{status['version']}")
    print(f"  Path:          {status['path']}")
    print(f"  On disk:       {'✅' if status['exists_on_disk'] else '❌'}")
    print(f"  Checksum:      {status['checksum'][:16]}...")
    print(f"  Bytes:         {status['bytes']:,}")
    print(f"  Lines:         {status['lines']:,}")
    print(f"  Published:     {status['published_at']}")
    print(f"  Published by:  {status['published_by']}")
    print(f"  Summary:       {status['summary']}")


def doc_history(args):
    """Show publication history for a document."""
    from centurion.docs.manager import DocumentManager
    dm = DocumentManager()
    entries = dm.history(args.name, limit=args.limit)
    if not entries:
        print(f"No history for '{args.name}'.")
        return
    print(f"─── {args.name} History ───")
    for e in entries:
        print(f"  v{e['version']:2d} | {e['published_at']} | {e['published_by']:15s} | {e['checksum'][:12]}...")

def doc_list(args):
    """List all tracked documents."""
    from centurion.docs.manager import DocumentManager
    dm = DocumentManager()
    docs = dm.list_documents()
    if not docs:
        print("No documents have been published yet.")
        return
    print(f"─── Tracked Documents ({len(docs)}) ───")
    for name in docs:
        st = dm.status(name)
        if st:
            v = st["version"]
            s = st["summary"][:50] if st["summary"] else "(no summary)"
            print(f"  {name:35s} | v{v:2d} | {s}")

def doc_verify(args):
    """Verify @latest pointer integrity."""
    from centurion.docs.manager import DocumentManager
    dm = DocumentManager()
    result = dm.verify(args.name)
    status = result["status"]
    if status == "verified":
        print(f"✅ {args.name} @latest is VERIFIED (v{result['version']}, checksum matches)")
    elif status == "checksum_mismatch":
        print(f"❌ {args.name} CHECKSUM MISMATCH")
        print(f"   Expected: {result['expected_checksum'][:16]}...")
        print(f"   Actual:   {result['actual_checksum'][:16]}...")
        sys.exit(1)
    elif status == "never_published":
        print(f"⚠  {args.name} has never been published.")
    elif status == "missing_file":
        print(f"❌ {args.name} pointer exists but file is MISSING")
        print(f"   Expected at: {result.get('expected_path')}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Centurion OS — Fleet Management CLI"
    )
    subparsers = parser.add_subparsers(dest="command")

    # ── fleet status ──
    p_status = subparsers.add_parser("status", help="Show fleet health")
    p_status.add_argument("--registry", help="Path to fleet registry")
    p_status.set_defaults(func=fleet_status)

    # ── fleet list ──
    p_list = subparsers.add_parser("list", help="List all Centurions")
    p_list.add_argument("--registry", help="Path to fleet registry")
    p_list.set_defaults(func=fleet_list)

    # ── fleet centurion ──
    p_cent = subparsers.add_parser("centurion", help="Show Centurion details")
    p_cent.add_argument("centurion_id", help="Centurion ID (e.g., prefect, cent-004)")
    p_cent.add_argument("--registry", help="Path to fleet registry")
    p_cent.set_defaults(func=fleet_centurion)

    # ── checkin ──
    p_ci = subparsers.add_parser("checkin", help="Send health check heartbeat")
    p_ci.add_argument("--id", dest="centurion_id", help="Centurion ID (default: $CENTURION_ID)")
    p_ci.add_argument("--status", default="active", help="Status to report")
    p_ci.set_defaults(func=checkin)

    # ── policies ──
    p_pol = subparsers.add_parser("policies", help="Manage fleet policies")
    p_pol.add_argument("action", choices=["list", "seed", "violations"])
    p_pol.add_argument("--centurion-id", help="Filter violations by Centurion")
    p_pol.add_argument("--unresolved", action="store_true", default=True,
                       help="Show only unresolved violations")
    p_pol.set_defaults(func=policies)

    # ── deploy ──
    p_dep = subparsers.add_parser("deploy", help="Deploy a new Centurion")
    p_dep.add_argument("--name", required=True, help="Centurion name")
    p_dep.add_argument("--owner", required=True, help="Owner name")
    p_dep.add_argument("--owner-email", default="", help="Owner email")
    p_dep.add_argument("--soul-template", default="default",
                       choices=["yeshi", "titus", "default"])
    p_dep.add_argument("--centurion-id", help="Override Centurion ID")
    p_dep.add_argument("--model", default="deepseek-v4-flash")
    p_dep.add_argument("--provider", default="deepseek")
    p_dep.add_argument("--telegram-token", help="Telegram bot token")
    p_dep.add_argument("--api-key", help="API key")
    p_dep.add_argument("--install-path", help="Custom install path")
    p_dep.set_defaults(func=deploy)

    # ── doc ──
    p_doc = subparsers.add_parser("doc", help="Document version management (@latest system)")
    doc_sub = p_doc.add_subparsers(dest="doc_action")

    # doc read
    p_doc_read = doc_sub.add_parser("read", help="Read the latest version of a document")
    p_doc_read.add_argument("name", help="Document name (e.g., centurion-business-plan)")
    p_doc_read.set_defaults(func=doc_read)

    # doc publish
    p_doc_pub = doc_sub.add_parser("publish", help="Publish a new version of a document")
    p_doc_pub.add_argument("name", help="Document name")
    p_doc_pub.add_argument("--file", "-f", required=True, help="Path to the new content file")
    p_doc_pub.add_argument("--author", default="centurion", help="Who is publishing this")
    p_doc_pub.add_argument("--summary", "-m", default="", help="Summary of changes")
    p_doc_pub.set_defaults(func=doc_publish)

    # doc status
    p_doc_st = doc_sub.add_parser("status", help="Show current version info for a document")
    p_doc_st.add_argument("name", help="Document name")
    p_doc_st.set_defaults(func=doc_status)

    # doc history
    p_doc_hist = doc_sub.add_parser("history", help="Show publication history for a document")
    p_doc_hist.add_argument("name", help="Document name")
    p_doc_hist.add_argument("--limit", type=int, default=10, help="Max entries")
    p_doc_hist.set_defaults(func=doc_history)

    # doc list
    p_doc_ls = doc_sub.add_parser("list", help="List all tracked documents")
    p_doc_ls.set_defaults(func=doc_list)

    # doc verify
    p_doc_vfy = doc_sub.add_parser("verify", help="Verify @latest pointer integrity")
    p_doc_vfy.add_argument("name", help="Document name")
    p_doc_vfy.set_defaults(func=doc_verify)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
