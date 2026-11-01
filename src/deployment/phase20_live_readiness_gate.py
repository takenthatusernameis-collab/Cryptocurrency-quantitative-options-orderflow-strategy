"""Phase 20 LiveReadinessGate: final go/no-go across capital/connectivity/risk/compliance/drift,
approval state machine, hard block unless all satisfied. Crypto options + orderflow."""
from __future__ import annotations

import math
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from src.telemetry.serialization import serialize_metrics_strict


_BASE_DAY = datetime(2026, 11, 1, tzinfo=timezone.utc)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _det_ts(seed: int) -> str:
    return (_BASE_DAY + timedelta(seconds=int(seed))).isoformat().replace("+00:00", "Z")


def _git_sha() -> Optional[str]:
    sha = os.environ.get("GIT_SHA")
    if sha:
        return str(sha)
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd="/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
        )
        if r.returncode == 0:
            return r.stdout.decode().strip()
    except Exception:
        pass
    return None


@dataclass(frozen=True)
class Phase20GateCheck:
    name: str
    passed: bool
    required: bool
    reason: str
    severity: str


@dataclass(frozen=True)
class Phase20GateDecision:
    allowed: bool
    live_allowed: bool
    paper_only: bool
    checks: Tuple[Phase20GateCheck, ...]
    blocked_reasons: Tuple[str, ...]
    approval_state: str
    timestamp: str


class Phase20LiveReadinessGate:
    def __init__(self, paper_only: bool = True, seed: int = 42):
        if not paper_only:
            raise ValueError("Phase20LiveReadinessGate: paper_only must remain True unless explicitly overridden with all hard gates satisfied and audited")
        self.paper_only = True
        self.seed = int(seed)
        self.approval_state = "PENDING"
        self.audit_log: List[Dict[str, Any]] = []
        self._log("init", {"paper_only": True})

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit_log.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def grant_approval(self) -> None:
        self.approval_state = "APPROVED"
        self._log("grant_approval", {"state": self.approval_state})

    def revoke_approval(self) -> None:
        self.approval_state = "REVOKED"
        self._log("revoke_approval", {"state": self.approval_state})

    def evaluate(self, state: Optional[Dict[str, Any]] = None) -> Phase20GateDecision:
        state = state or {}
        checks: List[Phase20GateCheck] = []
        blocked: List[str] = []

        checks.append(Phase20GateCheck("paper_only_enforced", True, True, "paper_only remains True", "info"))

        capital_ok = state.get("capital_allocated_valid") is True
        checks.append(Phase20GateCheck("capital_allocation_valid", capital_ok, True, "capital allocation valid" if capital_ok else "capital allocation invalid", "block" if not capital_ok else "info"))
        if not capital_ok:
            blocked.append("capital_allocation_valid")

        conn_ok = state.get("connectivity_ok") is True
        checks.append(Phase20GateCheck("connectivity_ok", conn_ok, True, "connectivity verified" if conn_ok else "connectivity not verified", "block" if not conn_ok else "info"))
        if not conn_ok:
            blocked.append("connectivity_ok")

        risk_ok = state.get("risk_limits_ok") is True
        checks.append(Phase20GateCheck("risk_limits_ok", risk_ok, True, "risk limits ok" if risk_ok else "risk limits breached", "block" if not risk_ok else "info"))
        if not risk_ok:
            blocked.append("risk_limits_ok")

        compliance_ok = state.get("compliance_ok") is True
        checks.append(Phase20GateCheck("compliance_ok", compliance_ok, True, "compliance verified" if compliance_ok else "compliance not verified", "block" if not compliance_ok else "info"))
        if not compliance_ok:
            blocked.append("compliance_ok")

        drift_ok = state.get("drift_within_bounds") is True
        checks.append(Phase20GateCheck("drift_within_bounds", drift_ok, True, "drift within bounds" if drift_ok else "drift out of bounds", "block" if not drift_ok else "info"))
        if not drift_ok:
            blocked.append("drift_within_bounds")

        recon_ok = state.get("recon_clean") is True
        checks.append(Phase20GateCheck("reconciliation_clean", recon_ok, True, "reconciliation clean" if recon_ok else "reconciliation discrepancies", "block" if not recon_ok else "info"))
        if not recon_ok:
            blocked.append("reconciliation_clean")

        recovery_ok = state.get("auto_recovery_ready") is True
        checks.append(Phase20GateCheck("auto_recovery_ready", recovery_ok, True, "auto-recovery ready" if recovery_ok else "auto-recovery not ready", "block" if not recovery_ok else "info"))
        if not recovery_ok:
            blocked.append("auto_recovery_ready")

        equity = float(state.get("equity", 150000.0))
        dd = float(state.get("drawdown_pct", 0.01))
        if equity < 100000.0:
            checks.append(Phase20GateCheck("min_equity", False, True, f"equity {equity} < 100000", "block"))
            blocked.append("min_equity")
        else:
            checks.append(Phase20GateCheck("min_equity", True, True, f"equity {equity} >= 100000", "info"))
        if dd > 0.08:
            checks.append(Phase20GateCheck("max_drawdown", False, True, f"drawdown {dd} > 0.08", "block"))
            blocked.append("max_drawdown")
        else:
            checks.append(Phase20GateCheck("max_drawdown", True, True, "drawdown within cap", "info"))

        live_allowed = len(blocked) == 0 and self.approval_state == "APPROVED"
        allowed = True
        decision = Phase20GateDecision(
            allowed=allowed,
            live_allowed=bool(live_allowed and not self.paper_only),
            paper_only=True,
            checks=tuple(checks),
            blocked_reasons=tuple(blocked),
            approval_state=self.approval_state,
            timestamp=_utc_now(),
        )
        self._log("evaluate", {"live_allowed": decision.live_allowed, "blocked": list(blocked)})
        return decision

    def generate_report(self, decision: Phase20GateDecision) -> Dict[str, Any]:
        rep = {
            "report": "PHASE20_LIVE_READINESS_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "git_sha": _git_sha(),
            "paper_only": True,
            "decision": {
                "allowed": bool(decision.allowed),
                "live_allowed": bool(decision.live_allowed),
                "approval_state": decision.approval_state,
                "blocked_reasons": list(decision.blocked_reasons),
                "timestamp": decision.timestamp,
            },
            "checks": [{"name": c.name, "passed": c.passed, "required": c.required, "reason": c.reason, "severity": c.severity} for c in decision.checks],
            "audit_log": self.audit_log,
        }
        return serialize_metrics_strict(rep)
