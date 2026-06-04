"""
Fleet Update Tool — autonomous upstream update management.

Each Centurion can check for updates, apply them selectively,
and roll back if something breaks. The tool can operate fully
autonomously (for security/fix commits) or flag features for
manager review.
"""

import logging
from typing import Optional

from centurion.fleet import update as fleet_update
from tools.registry import registry, tool_error

logger = logging.getLogger(__name__)

FLEET_UPDATE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "action": {
            "type": "string",
            "enum": ["check", "fetch", "apply", "status", "auto", "rollback", "setup"],
            "description": (
                "Fleet update action to perform:\n"
                "- check: List available upstream commits (does not change anything)\n"
                "- fetch: Fetch latest commits from upstream (no merge)\n"
                "- apply: Cherry-pick a specific commit by hash\n"
                "- status: Show fork divergence from upstream\n"
                "- auto: Apply auto-merge policy (merges security/fix commits, flags others)\n"
                "- rollback: Revert the last applied commit\n"
                "- setup: Configure the upstream remote URL"
            ),
        },
        "commit": {
            "type": "string",
            "description": "Commit hash to apply (required for 'apply' action)",
        },
        "upstream_url": {
            "type": "string",
            "description": "Upstream repository URL (required for 'setup' action, defaults to CenturionAI-OS-v4)",
        },
    },
    "required": ["action"],
}


async def handle_fleet_update(args: dict, **kwargs) -> str:
    """Handle a fleet_update tool call."""
    action = args.get("action")
    commit = args.get("commit")
    upstream_url = args.get("upstream_url")

    try:
        if action == "check":
            commits = fleet_update.check_upstream()
            if not commits:
                return "✅ Up to date — no upstream commits to merge."

            lines = [f"📋 **{len(commits)} upstream commit(s) available:**\n"]
            for c in commits:
                emoji = {
                    "security": "🔒",
                    "fix": "🛠️",
                    "feat": "✨",
                    "refactor": "♻️",
                    "deprecation": "⚠️",
                    "docs": "📝",
                    "chore": "🧹",
                    "other": "📄",
                }.get(c["category"], "📄")
                date_short = c["date"][:10] if c["date"] else ""
                lines.append(
                    f"{emoji} `{c['hash']}` {c['subject'][:80]}\n"
                    f"   _{c['author']}_, {date_short}  —  *{c['category']}*"
                )

            return "\n".join(lines)

        elif action == "fetch":
            fleet_update.check_upstream()  # check_upstream does fetch
            return "✅ Fetched latest from upstream."

        elif action == "apply":
            if not commit:
                return tool_error("'apply' requires a 'commit' parameter")
            result = fleet_update.apply_commit(commit)
            if result["success"]:
                return f"✅ {result['message']}"
            else:
                return f"❌ {result['message']}"

        elif action == "status":
            status = fleet_update.get_status()
            lines = [
                "📊 **Fleet Update Status**",
                f"  • Upstream: `{status['upstream']}`",
                f"  • Branch: `{status['branch']}`",
                f"  • Behind upstream: **{status['behind']}** commits",
                f"  • Ahead of upstream: **{status['ahead']}** commits",
                f"  • Last fetch: {status['last_fetch']}",
            ]
            if status["behind"] > 0:
                lines.append(f"\n💡 Run `fleet_update check` to see available commits")
            return "\n".join(lines)

        elif action == "auto":
            result = fleet_update.apply_policy()
            parts = []
            if result["merged"]:
                merged_lines = [f"✅ Merged {len(result['merged'])} commit(s):"]
                for c in result["merged"]:
                    merged_lines.append(f"  • `{c['hash']}` {c['subject'][:70]}")
                parts.append("\n".join(merged_lines))
            if result["flagged"]:
                flagged_lines = [f"📋 Flagged {len(result['flagged'])} commit(s) for review:"]
                for c in result["flagged"]:
                    flagged_lines.append(f"  • `{c['hash']}` {c['subject'][:70]} — _{c.get('reason', 'Manual review needed')}_")
                parts.append("\n".join(flagged_lines))
            if not parts:
                return "✅ Up to date."
            return "\n\n".join(parts)

        elif action == "rollback":
            result = fleet_update.rollback()
            if result["success"]:
                return f"↩️ {result['message']}"
            else:
                return f"❌ {result['message']}"

        elif action == "setup":
            url = upstream_url or fleet_update.DEFAULT_UPSTREAM
            result = fleet_update.set_upstream(url)
            if result["success"]:
                return f"✅ {result['message']}"
            else:
                return f"❌ {result['message']}"

        else:
            return tool_error(f"Unknown action: {action}")

    except RuntimeError as e:
        return tool_error(str(e))
    except Exception as e:
        logger.exception("fleet_update failed")
        return tool_error(f"Unexpected error: {e}")


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------
registry.register(
    name="fleet_update",
    toolset="fleet",
    schema=FLEET_UPDATE_SCHEMA,
    handler=handle_fleet_update,
    emoji="🚢",
    description=(
        "Manage software updates from the upstream Centurion OS repository. "
        "Each Centurion can check for available commits, selectively apply "
        "security fixes or features, auto-merge based on policy, roll back, "
        "and configure their upstream source. Gives full control over what "
        "code updates to accept."
    ),
)
