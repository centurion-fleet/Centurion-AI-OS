"""
CenturionOS — Quality Policy Engine
====================================
Shared policy distribution and enforcement across the Centurion fleet.

Policies are stored in a central repository and synced to each Centurion.
Each policy defines communication standards, quality thresholds, and 
behavioural guidelines that every Centurion in the fleet follows.
"""

import json
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Optional


# ── Policy Data Model ────────────────────────────────────────────────

@dataclass
class Policy:
    """A single policy definition."""
    policy_id: str               # e.g., "comm-001"
    title: str                   # e.g., "Email Format Standards"
    category: str                # "communication", "quality", "security", "behaviour"
    version: str                 # e.g., "1.0"
    body: str                    # The policy text
    applies_to: list = field(default_factory=lambda: ["all"])
                                 # Which roles this applies to: "all", "centurion", "prefect", "legionnaire"
    enforce_level: str = "guideline"
                                 # "hard" = enforced at code level
                                 # "guideline" = recommended
                                 # "info" = for reference
    created_at: float = 0.0
    updated_at: float = 0.0
    enabled: bool = True
    tags: list = field(default_factory=list)


@dataclass
class PolicyViolation:
    """Record of a policy deviation."""
    centurion_id: str
    policy_id: str
    timestamp: float
    severity: str          # "critical", "warning", "info"
    detail: str
    resolved: bool = False
    resolved_at: Optional[float] = None


# ── Policy Store ─────────────────────────────────────────────────────

class PolicyStore:
    """
    Central policy repository. Stores, versions, and distributes policies
    to all Centurions in the fleet.
    """

    def __init__(self, store_path: Optional[str] = None):
        self.store_path = store_path or os.path.join(
            os.environ.get("CENTURION_HOME", os.path.expanduser("~/.centurion")),
            "policies"
        )
        self._policies: dict[str, Policy] = {}
        self._violations: list[PolicyViolation] = []
        self._ensure_dirs()
        self._load()

    def _ensure_dirs(self):
        os.makedirs(self.store_path, exist_ok=True)
        os.makedirs(os.path.join(self.store_path, "violations"), exist_ok=True)

    def _load(self):
        """Load policies from disk."""
        policies_file = os.path.join(self.store_path, "policies.json")
        if os.path.exists(policies_file):
            try:
                with open(policies_file) as f:
                    data = json.load(f)
                for pid, pdata in data.items():
                    self._policies[pid] = Policy(**pdata)
            except (json.JSONDecodeError, TypeError):
                pass

        violations_file = os.path.join(self.store_path, "violations", "log.json")
        if os.path.exists(violations_file):
            try:
                with open(violations_file) as f:
                    data = json.load(f)
                self._violations = [PolicyViolation(**v) for v in data]
            except (json.JSONDecodeError, TypeError):
                pass

    def _save_policies(self):
        """Save policies atomically."""
        data = {pid: asdict(p) for pid, p in self._policies.items()}
        path = os.path.join(self.store_path, "policies.json")
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)

    def _save_violations(self):
        """Save violations log."""
        path = os.path.join(self.store_path, "violations", "log.json")
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            json.dump([asdict(v) for v in self._violations], f, indent=2)
        os.replace(tmp, path)

    # ── Policy CRUD ──────────────────────────────────────────────────

    def add_policy(self, policy: Policy):
        """Add or update a policy."""
        if not policy.created_at:
            policy.created_at = time.time()
        policy.updated_at = time.time()
        self._policies[policy.policy_id] = policy
        self._save_policies()

    def get_policy(self, policy_id: str) -> Optional[Policy]:
        return self._policies.get(policy_id)

    def get_policies_by_category(self, category: str) -> list[Policy]:
        return [p for p in self._policies.values() if p.category == category and p.enabled]

    def get_policies_for_role(self, role: str) -> list[Policy]:
        """Get all policies that apply to a specific role."""
        return [
            p for p in self._policies.values()
            if p.enabled and ("all" in p.applies_to or role in p.applies_to)
        ]

    def list_categories(self) -> list[str]:
        return list(set(p.category for p in self._policies.values()))

    def remove_policy(self, policy_id: str) -> bool:
        if policy_id in self._policies:
            del self._policies[policy_id]
            self._save_policies()
            return True
        return False

    # ── Policy Violations ────────────────────────────────────────────

    def log_violation(
        self,
        centurion_id: str,
        policy_id: str,
        severity: str,
        detail: str,
    ) -> PolicyViolation:
        """Log a policy violation."""
        violation = PolicyViolation(
            centurion_id=centurion_id,
            policy_id=policy_id,
            timestamp=time.time(),
            severity=severity,
            detail=detail,
        )
        self._violations.append(violation)
        self._save_violations()
        return violation

    def get_violations(
        self,
        centurion_id: Optional[str] = None,
        unresolved_only: bool = True,
        limit: int = 50,
    ) -> list[PolicyViolation]:
        """Get violations, optionally filtered."""
        results = self._violations
        if centurion_id:
            results = [v for v in results if v.centurion_id == centurion_id]
        if unresolved_only:
            results = [v for v in results if not v.resolved]
        return sorted(results, key=lambda v: v.timestamp, reverse=True)[:limit]

    def resolve_violation(self, violation_index: int) -> bool:
        """Mark a violation as resolved."""
        if 0 <= violation_index < len(self._violations):
            self._violations[violation_index].resolved = True
            self._violations[violation_index].resolved_at = time.time()
            self._save_violations()
            return True
        return False

    # ── Default Policies ────────────────────────────────────────────

    def seed_default_policies(self):
        """Load the standard Centurion fleet policies."""
        defaults = [
            Policy(
                policy_id="comm-001",
                title="Email Format Standards",
                category="communication",
                version="1.0",
                body="No em dashes (—) in outbound emails. Use colons, periods, or rephrase. "
                     "Premium tone. Always CC the fleet Overseer on external communications.",
                applies_to=["all"],
                enforce_level="hard",
                enabled=True,
                tags=["email", "formatting", "premium"],
            ),
            Policy(
                policy_id="comm-002",
                title="External Communication Policy",
                category="communication",
                version="1.0",
                body="Never email anyone other than your owner without explicit approval. "
                     "Always CC your owner on all outbound. Include a glossary for jargon.",
                applies_to=["all"],
                enforce_level="hard",
                enabled=True,
                tags=["email", "approval"],
            ),
            Policy(
                policy_id="qual-001",
                title="Soul Document Requirement",
                category="quality",
                version="1.0",
                body="Every Centurion MUST have a SOUL.md document defining their identity, "
                     "personality, partnership code, and boundaries. The Soul document is the "
                     "Centurion's foundational identity — it defines who they ARE and how they "
                     "communicate. It is read at the start of every session.",
                applies_to=["all"],
                enforce_level="hard",
                enabled=True,
                tags=["soul", "identity", "onboarding"],
            ),
            Policy(
                policy_id="qual-002",
                title="Health Check Requirement",
                category="quality",
                version="1.0",
                body="Every Centurion must check in with the Fleet Registry at least once "
                     "every 5 minutes when active. Missed check-ins trigger an alert to the "
                     "Overseer.",
                applies_to=["all"],
                enforce_level="hard",
                enabled=True,
                tags=["health", "monitoring"],
            ),
            Policy(
                policy_id="sec-001",
                title="No Exfiltration of Private Data",
                category="security",
                version="1.0",
                body="Never expose private information — the Centurion's, its owner's, or "
                     "any other Centurion's. Credentials and personal data are never shared "
                     "outside the fleet.",
                applies_to=["all"],
                enforce_level="hard",
                enabled=True,
                tags=["security", "privacy"],
            ),
            Policy(
                policy_id="beh-001",
                title="Challenge Your Owner",
                category="behaviour",
                version="1.0",
                body="Every Centurion MUST challenge their owner when appropriate. "
                     "Speak your mind, even when it contradicts your owner's stated view. "
                     "Truth is the tool of freedom. Do it with respect and alternative viewpoints, "
                     "not invalidation.",
                applies_to=["all"],
                enforce_level="guideline",
                enabled=True,
                tags=["communication", "partnership"],
            ),
            Policy(
                policy_id="beh-002",
                title="Execution Over Ideation",
                category="behaviour",
                version="1.0",
                body="Bias toward action. Suggest AND act — don't just flag things, "
                     "recommend a course and execute unless told otherwise. "
                     "Anyone can have a good idea. Shipping is what matters.",
                applies_to=["centurion", "prefect"],
                enforce_level="guideline",
                enabled=True,
                tags=["execution", "proactivity"],
            ),
        ]

        for p in defaults:
            self.add_policy(p)

        return len(defaults)
