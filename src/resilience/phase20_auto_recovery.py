"""Phase 20 AutoRecovery: circuit-breaker escalation, restart/retry policies, safe-mode transitions."""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from src.telemetry.serialization import serialize_metrics_strict


_BASE_DAY = datetime(2026, 11, 1, tzinfo=timezone.utc)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _det_ts(seed: int) -> str:
    return (_BASE_DAY + timedelta(seconds=int(seed))).isoformat().replace("+00:00", "Z")


@dataclass
class Phase20RecoveryConfig:
    max_retries: int = 3
    backoff_base_ms: int = 100
    escalation_threshold: int = 2
    safe_mode_on_escalation: bool = True
    paper_only: bool = True


class Phase20AutoRecovery:
    def __init__(self, config: Optional[Phase20RecoveryConfig] = None, seed: int = 42):
        self.config = config or Phase20RecoveryConfig()
        if self.config.paper_only is False:
            raise ValueError("Phase20AutoRecovery: paper_only must remain True by default")
        self.config.paper_only = True
        self.seed = int(seed)
        self.failure_counts: Dict[str, int] = {}
        self.escalations: List[Dict[str, Any]] = []
        self.safe_mode = False

    def handle_failure(self, component: str, error: str) -> Dict[str, Any]:
        c = str(component)
        self.failure_counts[c] = self.failure_counts.get(c, 0) + 1
        cnt = self.failure_counts[c]
        action = "retry"
        if cnt >= self.config.max_retries:
            action = "restart"
        if cnt >= self.config.escalation_threshold:
            action = "escalate"
            self.escalations.append({
                "component": c,
                "error": error,
                "count": cnt,
                "timestamp": _utc_now(),
                "action": action,
            })
            if self.config.safe_mode_on_escalation:
                self.safe_mode = True
        res = {
            "timestamp": _utc_now(),
            "component": c,
            "failure_count": cnt,
            "action": action,
            "backoff_ms": self.config.backoff_base_ms * (2 ** min(cnt - 1, 4)),
            "safe_mode": bool(self.safe_mode),
            "paper_only": True,
        }
        return serialize_metrics_strict(res)

    def recover(self) -> Dict[str, Any]:
        # Deterministic recovery
        recovered = []
        for comp, cnt in list(self.failure_counts.items()):
            if cnt > 0 and cnt < self.config.escalation_threshold:
                recovered.append(comp)
                self.failure_counts[comp] = 0
        if self.safe_mode and not self.escalations:
            self.safe_mode = False
        return {
            "timestamp": _utc_now(),
            "recovered_components": recovered,
            "recovered_count": len(recovered),
            "safe_mode": bool(self.safe_mode),
            "escalations_count": len(self.escalations),
            "paper_only": True,
        }

    def generate_report(self) -> Dict[str, Any]:
        rec = self.recover()
        rep = {
            "report": "PHASE20_AUTO_RECOVERY_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "config": asdict(self.config),
            "failure_counts": dict(self.failure_counts),
            "escalations": self.escalations,
            "recovery": rec,
            "safe_mode": bool(self.safe_mode),
            "paper_only": True,
        }
        return serialize_metrics_strict(rep)
