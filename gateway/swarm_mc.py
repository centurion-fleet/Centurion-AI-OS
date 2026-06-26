"""Mission Control client for Centurion AI OS — sync, tasks, documents via CTK."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_PORTAL_API = "https://www.personal-centurion.com"


class SwarmMcClient:
    """HTTP client for portal Mission Control APIs (ctk_proj_*)."""

    def __init__(
        self,
        *,
        project_token: str,
        install_id: str,
        api_base: str | None = None,
    ) -> None:
        self.project_token = project_token.strip()
        self.install_id = install_id.strip()
        self.api_base = (api_base or os.getenv("CENTURION_PORTAL_API", DEFAULT_PORTAL_API)).rstrip("/")

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.project_token}",
            "Content-Type": "application/json",
            "X-Centurion-Install-Id": self.install_id,
        }

    def _request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.api_base}{path}"
        data = json.dumps(body).encode() if body is not None else None
        req = Request(url, data=data, headers=self._headers(), method=method)
        try:
            with urlopen(req, timeout=120) as resp:
                raw = resp.read().decode()
                return json.loads(raw) if raw else {}
        except HTTPError as err:
            detail = err.read().decode()
            raise RuntimeError(f"MC API {method} {path} failed ({err.code}): {detail}") from err
        except URLError as err:
            raise RuntimeError(f"MC API unreachable: {err}") from err

    def sync(self, project_id: str, since: str | None = None) -> dict[str, Any]:
        qs = f"?since={since}" if since else ""
        return self._request("GET", f"/api/v1/swarm/projects/{project_id}/sync{qs}")

    def complete_task(
        self,
        project_id: str,
        task_id: str,
        *,
        status: str = "done",
        result: str | None = None,
        artifact_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"status": status}
        if result is not None:
            body["result"] = result
        if artifact_ids:
            body["artifact_ids"] = artifact_ids
        return self._request(
            "PATCH",
            f"/api/v1/swarm/projects/{project_id}/tasks/{task_id}",
            body,
        )

    def create_upload_url(
        self,
        project_id: str,
        path: str,
        content_type: str = "application/octet-stream",
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/api/v1/swarm/projects/{project_id}/artifacts/upload-url",
            {"path": path, "content_type": content_type},
        )

    def register_artifact(
        self,
        project_id: str,
        *,
        path: str,
        storage_path: str,
        content_type: str = "application/octet-stream",
        size_bytes: int | None = None,
        task_id: str | None = None,
        title: str | None = None,
        published_to_program: bool = False,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "path": path,
            "storage_path": storage_path,
            "content_type": content_type,
            "published_to_program": published_to_program,
        }
        if size_bytes is not None:
            body["size_bytes"] = size_bytes
        if task_id:
            body["task_id"] = task_id
        if title:
            body["title"] = title
        return self._request("POST", f"/api/v1/swarm/projects/{project_id}/artifacts", body)

    def post_activity(
        self,
        project_id: str,
        *,
        activity_type: str,
        summary: str,
        body: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/api/v1/swarm/projects/{project_id}/activity",
            {
                "items": [
                    {
                        "activity_type": activity_type,
                        "summary": summary,
                        "body": body,
                        "metadata": metadata or {},
                    }
                ]
            },
        )

    def invite_friend(
        self,
        project_id: str,
        invited_customer_id: str,
        role: str = "operator",
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/api/v1/swarm/projects/{project_id}/invites",
            {"invited_customer_id": invited_customer_id, "role": role},
        )


def load_mc_config() -> dict[str, str]:
    """Read ~/.centurion/mc.json written by `centurion swarm connect`."""
    home = Path(os.environ.get("CENTURION_HOME", Path.home() / ".centurion"))
    path = home / "mc.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
        return {k: str(v) for k, v in data.items() if v}
    except Exception:
        return {}


def save_mc_config(project_id: str, project_token: str, install_id: str) -> None:
    home = Path(os.environ.get("CENTURION_HOME", Path.home() / ".centurion"))
    home.mkdir(parents=True, exist_ok=True)
    path = home / "mc.json"
    path.write_text(
        json.dumps(
            {
                "project_id": project_id,
                "project_token": project_token,
                "install_id": install_id,
            },
            indent=2,
        )
    )
