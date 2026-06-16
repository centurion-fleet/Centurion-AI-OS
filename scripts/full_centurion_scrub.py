#!/usr/bin/env python3
"""Full-repo scrub: Centurion/Nous → Centurion branding."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
    "centurionai_os.egg-info", "dist", "build", ".next", "web_dist", "tui_dist",
}

def _skip_path(path: Path) -> bool:
    if any(part in SKIP_DIRS for part in path.parts):
        return True
    # Skip bundled/minified dashboard assets (rebuilt separately).
    if "dashboard" in path.parts and path.suffix == ".js" and path.stat().st_size > 200_000:
        return True
    return False

TEXT_SUFFIXES = {
    ".py", ".md", ".mdx", ".yaml", ".yml", ".json", ".toml", ".sh", ".ps1",
    ".ts", ".tsx", ".js", ".jsx", ".css", ".html", ".txt", ".ini", ".cfg",
    ".service", ".nix", ".sql", ".j2", ".env.example", ".gitignore",
    ".dockerignore", ".hadolint.yaml", ".svg", ".rb", ".cmd", ".mjs",
}

TEXT_NAMES = {
    "Dockerfile", "flake.nix", "constraints-termux.txt",
    "cli-config.yaml.example", "package-lock.json", "centurion-gateway",
}

REPLACEMENTS: list[tuple[str, str]] = [
    ("centurion-fleet/Centurion-AI-OS", "centurion-fleet/Centurion-AI-OS"),
    ("centurion-fleet/centurion-ai-os", "centurion-fleet/centurion-ai-os"),
    ("github.com/centurion-fleet/Centurion-AI-OS", "github.com/centurion-fleet/Centurion-AI-OS"),
    ("security@centurion-fleet.com", "security@centurion-fleet.com"),
    ("portal.personal-centurion.com", "portal.personal-centurion.com"),
    ("Centurion Portal", "Centurion Portal"),
    ("Centurion Fleet", "Centurion Fleet"),
    ("@centurion-fleet/ui", "@centurion-fleet/ui"),
    ("X-Centurion-Session-Id", "X-Centurion-Session-Id"),
    ("ai.centurion.gateway", "ai.centurion.gateway"),
    ("centurion-gateway", "centurion-gateway"),
    ("centurion.service", "centurion.service"),
    ("main-centurion", "main-centurion"),
    ("centurion-ai-os.nix", "centurion-ai-os.nix"),
    ("centurion-ai-os.rb", "centurion-ai-os.rb"),
    ("openclaw_to_centurion", "openclaw_to_centurion"),
    ("_centurion_home", "_centurion_home"),
    ("nous_centurion", "nous_centurion"),
    ("centurion_voice", "centurion_voice"),
    ("centurion-install-autostash", "centurion-install-autostash"),
    ("/tmp/centurion-", "/tmp/centurion-"),
    ("Centurion AI OS", "Centurion AI OS"),
    ("Centurion agent", "Centurion agent"),
    ("Centurion Gateway", "Centurion Gateway"),
    ("Centurion Chat", "Centurion Chat"),
    ("Centurion Commands", "Centurion Commands"),
    ("Centurion TUI", "Centurion TUI"),
    ("CenturionCLI", "CenturionCLI"),
    ("Centurion venv", "Centurion venv"),
    ("Centurion ", "Centurion "),
    (" Centurion", " Centurion"),
    ("_CENTURION_WEBHOOK_SAFE_TOOLS", "_CENTURION_WEBHOOK_SAFE_TOOLS"),
    ("_CENTURION_CORE_TOOLS", "_CENTURION_CORE_TOOLS"),
    ("CENTURION_INSTALL_DIR", "CENTURION_INSTALL_DIR"),
    ("CENTURION_BACKGROUND_NOTIFICATIONS", "CENTURION_BACKGROUND_NOTIFICATIONS"),
    ("CENTURION_BUNDLED_SKILLS", "CENTURION_BUNDLED_SKILLS"),
    ("CENTURION_OPTIONAL_SKILLS", "CENTURION_OPTIONAL_SKILLS"),
    ("CENTURION_MANAGED", "CENTURION_MANAGED"),
    ("CENTURION_KANBAN_BOARD", "CENTURION_KANBAN_BOARD"),
    ("CENTURION_ISOLATE_CHILD", "CENTURION_ISOLATE_CHILD"),
    ("CENTURION_PYTHON", "CENTURION_PYTHON"),
    ("CENTURION_TUI", "CENTURION_TUI"),
    ("CENTURION_HOME", "CENTURION_HOME"),
    ("CENTURION_UID", "CENTURION_UID"),
    ("CENTURION_GID", "CENTURION_GID"),
    ("CENTURION_BIN", "CENTURION_BIN"),
    ("CENTURION_CMD", "CENTURION_CMD"),
    ("metadata.centurion", "metadata.centurion"),
    ("get_centurion_home", "get_centurion_home"),
    ("display_centurion_home", "display_centurion_home"),
    ("load_centurion_dotenv", "load_centurion_dotenv"),
    ("_default_centurion_home", "_default_centurion_home"),
    ("_isolate_centurion_home", "_isolate_centurion_home"),
    ("get_centurion_command_path", "get_centurion_command_path"),
    ("current_centurion", "current_centurion"),
    ("centurion_node", "centurion_node"),
    ("centurion_meta", "centurion_meta"),
    ("centurion_bin", "centurion_bin"),
    ("centurion_cmd", "centurion_cmd"),
    ("centurion_home", "centurion_home"),
    ("isinstance(centurion,", "isinstance(centurion,"),
    ("centurion_state.py", "centurion_state.py"),
    ("centurion_logging.py", "centurion_logging.py"),
    ("centurion_constants.py", "centurion_constants.py"),
    ("centurion_bootstrap.py", "centurion_bootstrap.py"),
    ("centurion_time.py", "centurion_time.py"),
    ("centurion_cli/", "centurion_cli/"),
    ("centurion_cli.", "centurion_cli."),
    ("tests/centurion_cli", "tests/centurion_cli"),
    ("tests/centurion_state", "tests/centurion_state"),
    ("centurion-achievements", "centurion-achievements"),
    ("centurion-ink", "centurion-ink"),
    ("@centurion/ink", "@centurion/ink"),
    ("centurion-smoke-test", "centurion-smoke-test"),
    ("setup-centurion.sh", "setup-centurion.sh"),
    ("centurion-agent-skill-authoring", "centurion-agent-skill-authoring"),
    ("centurion-s6-container-supervision", "centurion-s6-container-supervision"),
    ("debugging-centurion-tui-commands", "debugging-centurion-tui-commands"),
    ("/opt/centurion/", "/opt/centurion/"),
    ("/opt/centurion", "/opt/centurion"),
    ("~/.centurion", "~/.centurion"),
    ("$HOME/.centurion", "$HOME/.centurion"),
    ("/root/.centurion", "/root/.centurion"),
    ("python -m centurion_cli", "python -m centurion_cli"),
    ("venv/bin/centurion", "venv/bin/centurion"),
    ("$link_dir/centurion", "$link_dir/centurion"),
    ("command_link_dir/centurion", "command_link_dir/centurion"),
    ("--centurion-home", "--centurion-home"),
    ("name = \"centurion-ai-os\"", "name = \"centurionai-os\""),
    ("centurion-ai-os", "centurion-ai-os"),
    ("centurion_cli", "centurion_cli"),
    ("centurion_state", "centurion_state"),
    ("`/centurion`", "`/centurion`"),
    ("`/centurion ", "`/centurion "),
    ("/centurion\n", "/centurion\n"),
    ("'centurion'", "'centurion'"),
    ('"centurion"', '"centurion"'),
    ("`centurion`", "`centurion`"),
    ("centurion dashboard", "centurion dashboard"),
    ("centurion gateway", "centurion gateway"),
    ("centurion debug share", "centurion debug share"),
    ("centurion kanban", "centurion kanban"),
    ("centurion update", "centurion update"),
    ("centurion setup", "centurion setup"),
    ("centurion doctor", "centurion doctor"),
    ("centurion model", "centurion model"),
    ("centurion tools", "centurion tools"),
    ("centurion chat", "centurion chat"),
    ("centurion config", "centurion config"),
    ("centurion skills", "centurion skills"),
    ("centurion plugins", "centurion plugins"),
    ("centurion cron", "centurion cron"),
    ("centurion memory", "centurion memory"),
    ("centurion claw", "centurion claw"),
    ("centurion whatsapp", "centurion whatsapp"),
    ("centurion pairing", "centurion pairing"),
    ("centurion bundles", "centurion bundles"),
    ("centurion status", "centurion status"),
    ("centurion logs", "centurion logs"),
    ("centurion --tui", "centurion --tui"),
    ("centurion --help", "centurion --help"),
    ("centurion --toolsets", "centurion --toolsets"),
    ("centurion version", "centurion version"),
    ("author: Centurion AI OS", "author: Centurion Fleet"),
    ("centurion\n", "centurion\n"),
    ("centurion ", "centurion "),
    (" centurion", " centurion"),
]

FRONTMATTER_HERMES = re.compile(
    r"^(metadata:\s*\n(?:[ \t]+[^\n]+\n)*?[ \t]+)centurion:(\s*\n)",
    re.MULTILINE,
)


def should_process(path: Path) -> bool:
    if path.name in TEXT_NAMES:
        return True
    return path.suffix in TEXT_SUFFIXES or path.name == "uv.lock"


def scrub_text(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    text = FRONTMATTER_HERMES.sub(r"\1centurion:\2", text)
    return text


def main() -> int:
    targets = [
        ROOT / d for d in [
            "agent", "centurion_cli", "gateway", "tools", "cron", "tui_gateway",
            "acp_adapter", "plugins", "providers", "skills", "optional-skills",
            "website", "web", "ui-tui", "docker", "scripts", "tests", "docs",
            "plans", ".plans", "packaging", "locales", ".github", "nix",
            "datagen-config-examples", "acp_registry",
        ]
    ]
    root_files = [
        "Dockerfile", "docker-compose.yml", "pyproject.toml", "uv.lock",
        "cli-config.yaml.example", ".env.example", ".gitignore", ".dockerignore",
        ".hadolint.yaml", "flake.nix", "constraints-termux.txt", "setup-centurion.sh",
        "mcp_serve.py", "run_agent.py", "model_tools.py", "toolsets.py", "cli.py",
        "batch_runner.py", "mini_swe_runner.py", "trajectory_compressor.py",
        "centurion_constants.py", "centurion_state.py", "centurion_logging.py",
        "centurion_bootstrap.py", "centurion_time.py",
    ]
    targets.extend(ROOT / f for f in root_files if (ROOT / f).exists())

    changed = 0
    for base in targets:
        paths = [base] if base.is_file() else list(base.rglob("*")) if base.is_dir() else []
        for path in paths:
            if not path.is_file() or _skip_path(path):
                continue
            if not should_process(path):
                continue
            try:
                original = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            updated = scrub_text(original)
            if updated != original:
                path.write_text(updated, encoding="utf-8")
                changed += 1
    print(f"Scrubbed {changed} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
