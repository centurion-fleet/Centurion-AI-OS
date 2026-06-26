"""Mission Control tools — sync, complete tasks, upload documents via portal CTK."""

from __future__ import annotations

import logging
from pathlib import Path

from gateway.swarm_mc import SwarmMcClient, load_mc_config
from tools.registry import registry, tool_error

logger = logging.getLogger(__name__)

MC_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "action": {
            "type": "string",
            "enum": ["sync", "complete_task", "upload_document", "invite_friend"],
            "description": (
                "Mission Control action:\n"
                "- sync: Pull project tasks, targets, artifacts since last sync\n"
                "- complete_task: Mark task done with optional result text\n"
                "- upload_document: Register artifact metadata after storage upload\n"
                "- invite_friend: Invite another owner's Centurion (mutual trust required)"
            ),
        },
        "task_id": {"type": "string", "description": "Task UUID for complete_task"},
        "result": {"type": "string", "description": "Completion summary for complete_task"},
        "path": {"type": "string", "description": "File path for upload_document"},
        "storage_path": {"type": "string", "description": "Storage path from upload-url response"},
        "title": {"type": "string", "description": "Human title for document"},
        "published_to_program": {
            "type": "boolean",
            "description": "Include in program document library for owner download",
        },
        "invited_customer_id": {
            "type": "string",
            "description": "Friend owner customer UUID for invite_friend",
        },
        "since": {"type": "string", "description": "ISO timestamp for incremental sync"},
    },
    "required": ["action"],
}


def _client() -> SwarmMcClient:
    cfg = load_mc_config()
    token = cfg.get("project_token", "")
    install_id = cfg.get("install_id", "")
    if not token.startswith("ctk_proj_") or not install_id:
        raise ValueError("Run `centurion swarm connect` with a ctk_proj token first")
    return SwarmMcClient(project_token=token, install_id=install_id)


async def handle_mission_control(args: dict, **kwargs) -> str:
    action = args.get("action")
    cfg = load_mc_config()
    project_id = cfg.get("project_id", "")
    if not project_id:
        return tool_error("No project_id in mc.json — run centurion swarm connect")

    try:
        client = _client()
    except ValueError as err:
        return tool_error(str(err))

    try:
        if action == "sync":
            data = client.sync(project_id, args.get("since"))
            tasks = len(data.get("tasks", []))
            return f"Synced project {project_id[:8]}… ({tasks} task delta)"

        if action == "complete_task":
            task_id = args.get("task_id", "").strip()
            if not task_id:
                return tool_error("task_id required")
            client.complete_task(
                project_id,
                task_id,
                result=args.get("result"),
                status="done",
            )
            return f"Task {task_id[:8]}… marked done"

        if action == "upload_document":
            path = args.get("path", "").strip()
            storage_path = args.get("storage_path", "").strip()
            if not path or not storage_path:
                return tool_error("path and storage_path required")
            client.register_artifact(
                project_id,
                path=path,
                storage_path=storage_path,
                title=args.get("title"),
                task_id=args.get("task_id"),
                published_to_program=bool(args.get("published_to_program")),
            )
            return f"Registered document {Path(path).name}"

        if action == "invite_friend":
            invited = args.get("invited_customer_id", "").strip()
            if not invited:
                return tool_error("invited_customer_id required")
            client.invite_friend(project_id, invited)
            return f"Project invite sent to owner {invited[:8]}…"

        return tool_error(f"Unknown action: {action}")
    except Exception as err:
        logger.exception("mission_control failed")
        return tool_error(str(err))


registry.register(
    name="mission_control",
    toolset="centurion-mission-control",
    schema=MC_SCHEMA,
    handler=handle_mission_control,
    emoji="🎯",
    description=(
        "Operate Mission Control projects on the portal: sync tasks, complete work "
        "with results, register task documents, and invite trusted friend Centurions."
    ),
)
