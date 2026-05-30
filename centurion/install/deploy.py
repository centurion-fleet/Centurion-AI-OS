"""
CenturionOS — Install Script
=============================
Deploys Centurion OS to a new machine and registers it in the fleet.

Usage:
    python3 -m centurion.install.deploy \\
        --name Yeshi \\
        --owner "Helen Cameron" \\
        --soul-template yeshi \\
        --telegram-token "..." \\
        --model "deepseek-v4-flash"

This script:
1. Installs Centurion OS (via pip from the repo)
2. Creates the Centurion identity and config
3. Generates the SOUL.md document
4. Registers the Centurion in the fleet registry
5. Sets up the health check cron job
6. Configures Telegram for the new Centurion
7. Runs an initial health check
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from centurion.fleet.registry import FleetRegistry, CenturionIdentity
from centurion.fleet.health import HealthCheckRunner
from centurion.soul.templates import yeshi_soul, titus_soul_summary


# ── Deployment Steps ─────────────────────────────────────────────────

class CenturionDeployer:
    """
    Handles the full deployment of a new Centurion to a target machine.
    """

    def __init__(
        self,
        name: str,
        owner_name: str,
        owner_email: str,
        soul_template: str,
        centurion_id: Optional[str] = None,
        model: str = "deepseek-v4-flash",
        provider: str = "deepseek",
        telegram_token: Optional[str] = None,
        api_key: Optional[str] = None,
        install_path: Optional[str] = None,
    ):
        self.name = name
        self.owner_name = owner_name
        self.owner_email = owner_email
        self.soul_template = soul_template
        self.centurion_id = centurion_id or f"cent-{int(time.time())}"
        self.model = model
        self.provider = provider
        self.telegram_token = telegram_token
        self.api_key = api_key
        self.install_path = install_path or os.path.expanduser("~/.centurion")
        self.home_dir = os.path.expanduser("~")
        self.hostname = platform.node()
        self.errors: list[str] = []
        self.log: list[str] = []

    def log_step(self, msg: str):
        self.log.append(f"[{len(self.log)+1}] {msg}")
        print(f"  ✓ {msg}")

    def log_error(self, msg: str):
        self.errors.append(msg)
        print(f"  ✗ ERROR: {msg}", file=sys.stderr)

    def deploy(self) -> bool:
        """Run the full deployment. Returns True on success."""
        print(f"\n{'='*50}")
        print(f"  Deploying Centurion: {self.name}")
        print(f"  Owner: {self.owner_name}")
        print(f"  Host: {self.hostname}")
        print(f"{'='*50}\n")

        steps = [
            ("Creating directory structure", self._create_dirs),
            ("Writing identity config", self._write_identity),
            ("Registering in fleet", self._register_fleet),
            ("Setting up environment", self._setup_env),
            ("Running initial health check", self._initial_health_check),
        ]

        success = True
        for step_name, step_fn in steps:
            try:
                step_fn()
                self.log_step(step_name)
            except Exception as e:
                self.log_error(f"{step_name}: {e}")
                success = False
                break

        # Generate Soul document (doesn't block deployment if it fails)
        try:
            self._generate_soul_doc()
            self.log_step("Generating Soul document")
        except Exception as e:
            self.log_error(f"Generating Soul document: {e}")

        print(f"\n{'='*50}")
        if success:
            print(f"  ✅ {self.name} deployed successfully!")
            print(f"  📍 {self.install_path}")
            print(f"  🆔 {self.centurion_id}")
        else:
            print(f"  ❌ Deployment failed — {len(self.errors)} errors")
            for e in self.errors:
                print(f"     {e}")
        print(f"{'='*50}\n")

        return success

    def _create_dirs(self):
        """Create the Centurion directory structure."""
        dirs = [
            self.install_path,
            os.path.join(self.install_path, "config"),
            os.path.join(self.install_path, "souls"),
            os.path.join(self.install_path, "fleet"),
            os.path.join(self.install_path, "fleet", "messages"),
            os.path.join(self.install_path, "fleet", "locks"),
            os.path.join(self.install_path, "policies"),
            os.path.join(self.install_path, "policies", "violations"),
            os.path.join(self.install_path, "swarm", "tasks"),
            os.path.join(self.install_path, "logs"),
        ]
        for d in dirs:
            os.makedirs(d, exist_ok=True)

    def _write_identity(self):
        """Write the Centurion's identity configuration."""
        config = {
            "centurion": {
                "id": self.centurion_id,
                "name": self.name,
                "owner": self.owner_name,
                "owner_email": self.owner_email,
                "role": "Centurion",
                "created_at": time.time(),
                "host": self.hostname,
            },
            "model": {
                "default": self.model,
                "provider": self.provider,
            },
            "telegram": {
                "bot_token": self.telegram_token or "",
                "enabled": bool(self.telegram_token),
            },
            "fleet": {
                "overseer_id": "prefect",
                "heartbeat_interval_seconds": 300,
                "registry_path": os.path.join(self.install_path, "fleet", "registry.json"),
            },
        }
        config_path = os.path.join(self.install_path, "config", "identity.json")
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

    def _register_fleet(self):
        """Register this Centurion in the fleet registry."""
        registry = FleetRegistry(
            os.path.join(self.install_path, "fleet", "registry.json")
        )

        identity = CenturionIdentity(
            centurion_id=self.centurion_id,
            name=self.name,
            emoji="🦋",
            owner_name=self.owner_name,
            owner_email=self.owner_email,
            role="Centurion",
            soul_doc_path=os.path.join(self.install_path, "souls", f"{self.centurion_id}_SOUL.md"),
            created_at=time.time(),
        )
        registry.register(identity)
        registry.update_status(
            self.centurion_id,
            status="deploying",
            version="0.14.0",
            model=self.model,
            provider=self.provider,
            host=self.hostname,
        )

    def _generate_soul_doc(self):
        """Generate and save the Soul document."""
        if self.soul_template == "yeshi":
            soul = yeshi_soul()
        elif self.soul_template == "titus":
            soul = titus_soul_summary()
        else:
            # Default: create a basic template
            from centurion.soul.templates import SoulDocument
            soul = SoulDocument(
                centurion_id=self.centurion_id,
                name=self.name,
                emoji="🦋",
                owner=self.owner_name,
                owner_email=self.owner_email,
                role="Centurion",
                core_identity=f"I am {self.name}. I am {self.owner_name}'s Centurion.",
                personality=["Warm and professional", "Direct and honest"],
                partnership_code=["Speak truth with kindness", "Serve my owner's mission"],
                communication_protocol=["Clear and concise", "Respectful always"],
                boundaries=["Never expose private information"],
            )
        soul.save(os.path.join(self.install_path, "souls"))

    def _setup_env(self):
        """Set up the environment configuration."""
        env_path = os.path.join(self.install_path, ".env")
        env_vars = []
        if os.path.exists(env_path):
            with open(env_path) as f:
                env_vars = [l.strip() for l in f if l.strip() and not l.startswith("#")]

        # Add or update key variables
        key_vars = {
            "CENTURION_ID": self.centurion_id,
            "CENTURION_NAME": self.name,
            "CENTURION_HOME": self.install_path,
            "CENTURION_MODEL": self.model,
            "CENTURION_PROVIDER": self.provider,
        }
        if self.api_key:
            key_vars["CENTURION_API_KEY"] = self.api_key
        if self.telegram_token:
            key_vars["TELEGRAM_BOT_TOKEN"] = self.telegram_token

        with open(env_path, "w") as f:
            for k, v in key_vars.items():
                f.write(f"{k}={v}\n")

    def _initial_health_check(self):
        """Run the first health check to confirm the Centurion is alive."""
        runner = HealthCheckRunner(
            centurion_id=self.centurion_id,
            registry=FleetRegistry(
                os.path.join(self.install_path, "fleet", "registry.json")
            ),
        )
        runner.check_in(status="active")
        time.sleep(0.5)


# ── CLI Entry Point ──────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Deploy a new Centurion to this machine"
    )
    parser.add_argument("--name", required=True, help="Centurion name (e.g., Yeshi)")
    parser.add_argument("--owner", required=True, help="Owner's full name")
    parser.add_argument("--owner-email", default="", help="Owner's email")
    parser.add_argument("--soul-template", default="default",
                        choices=["yeshi", "titus", "default"],
                        help="Soul document template")
    parser.add_argument("--centurion-id", help="Override Centurion ID (auto-generated)")
    parser.add_argument("--model", default="deepseek-v4-flash", help="AI model")
    parser.add_argument("--provider", default="deepseek", help="AI provider")
    parser.add_argument("--telegram-token", help="Telegram bot token")
    parser.add_argument("--api-key", help="API key for the AI provider")
    parser.add_argument("--install-path", help="Custom install path")

    args = parser.parse_args()

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

    success = deployer.deploy()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
