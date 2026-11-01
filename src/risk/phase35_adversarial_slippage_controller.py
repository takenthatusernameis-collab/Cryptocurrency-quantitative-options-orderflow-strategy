"""
Phase 35: Adversarial Slippage Controller for crypto options + orderflow.
Detects and mitigates adversarial slippage, enforces hard limits. Deterministic, paper-only.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import hashlib
import json
import math
from pathlib import Path

from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _assert_finite(obj: Any, label: str = "obj") -> None:
    bad: List[str] = []

    def walk(v: Any, p: str) -> None:
        if isinstance(v, dict):
            for k, val in v.items():
                walk(val, f"{p}/{k}")
        elif isinstance(v, (list, tuple)):
            for i, val in enumerate(v):
                walk(val, f"{p}[{i}]")
        elif isinstance(v, float) and not isinstance(v, bool):
            if not math.isfinite(v):
                bad.append(p)

    walk(obj, "$")
    if bad:
        raise ValueError(f"Non-finite in {label}: {bad[:10]}")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p35adv|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p35adv_{tag}_{h}"


@dataclass(frozen=True)
class AdversarialSlippageConfig:
    seed: int = 42
    paper_only: bool = True
    hard_limit_bps: float = 15.0
    warn_limit_bps: float = 10.0
    latency_penalty_bps: float = 2.0
    toxic_flow_penalty_bps: float = 3.0
    enforce_gates: bool = True


@dataclass(frozen=True)
class SlippageMitigation:
    mitigation_id: str
    order_id: str
    venue: str
    detected_slippage_bps: float
    mitigated_slippage_bps: float
    action: str
    penalty_applied_bps: float
    blocked: bool
    reason: str
    timestamp: str


class AdversarialSlippageController:
    def __init__(self, config: Optional[AdversarialSlippageConfig] = None, seed: int = 42):
        self.config = config or AdversarialSlippageConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("AdversarialSlippageController: paper_only must remain True (live path hard-gated)")
        self.config = AdversarialSlippageConfig(
            seed=int(self.config.seed),
            paper_only=True,
            hard_limit_bps=float(self.config.hard_limit_bps),
            warn_limit_bps=float(self.config.warn_limit_bps),
            latency_penalty_bps=float(self.config.latency_penalty_bps),
            toxic_flow_penalty_bps=float(self.config.toxic_flow_penalty_bps),
            enforce_gates=bool(self.config.enforce_gates),
        )
        self.seed = int(self.config.seed)
        self._counter = 0
        self.mitigations: List[SlippageMitigation] = []
        self.blocked_count = 0

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        return _make_id(self.seed, tag, self._counter)

    def control_slippage(self, routed_orders: List[Dict[str, Any]], market_state: Optional[Dict[str, Any]] = None) -> List[SlippageMitigation]:
        self.mitigations = []
        self.blocked_count = 0
        market_state = market_state or {"toxicity": 0.3, "latency_ms": 50.0}

        tox = float(market_state.get("toxicity", 0.3))
        lat = float(market_state.get("latency_ms", 50.0))

        for ro in routed_orders:
            detected = float(ro.get("expected_slippage_bps", 5.0))
            oid = str(ro.get("order_id", self._next_id("ord")))
            venue = str(ro.get("venue", "deribit"))

            penalty = 0.0
            action = "pass"
            reason = "ok"

            if tox > 0.5:
                penalty += self.config.toxic_flow_penalty_bps * tox
                action = "reduce_size"
                reason = "toxic_flow_detected"
            if lat > 80:
                penalty += self.config.latency_penalty_bps * (lat / 80.0)
                action = "reduce_size" if action == "pass" else action
                reason = reason if reason != "ok" else "latency_penalty"

            mitigated = detected + penalty
            blocked = False
            if mitigated > self.config.hard_limit_bps:
                blocked = True
                action = "block"
                reason = "hard_limit_exceeded"
                self.blocked_count += 1
                mitigated = self.config.hard_limit_bps
            elif mitigated > self.config.warn_limit_bps:
                if action == "pass":
                    action = "slice"
                reason = reason if reason != "ok" else "warning_threshold"

            mit = SlippageMitigation(
                mitigation_id=self._next_id("mit"),
                order_id=oid,
                venue=venue,
                detected_slippage_bps=float(detected),
                mitigated_slippage_bps=float(mitigated),
                action=action,
                penalty_applied_bps=float(penalty),
                blocked=bool(blocked),
                reason=reason,
                timestamp=_utc_now(),
            )
            _assert_finite(asdict(mit), "slippage_mitigation")
            self.mitigations.append(mit)

        return self.mitigations

    def generate_report(self, outdir: str = "research_state") -> Dict[str, Any]:
        Path(outdir).mkdir(parents=True, exist_ok=True)
        report = {
            "status": "ok",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "paper_only": True,
            "mitigations_count": len(self.mitigations),
            "blocked_count": self.blocked_count,
            "hard_limit_bps": self.config.hard_limit_bps,
            "warn_limit_bps": self.config.warn_limit_bps,
            "mitigations": [asdict(m) for m in self.mitigations[:15]],
        }
        _assert_finite(report, "phase35_adversarial_slippage_report")
        rep_json = Path(outdir) / "PHASE35_ADVERSARIAL_SLIPPAGE_REPORT.json"
        rep_md = Path(outdir) / "PHASE35_ADVERSARIAL_SLIPPAGE_REPORT.md"
        rep_md.write_text(
            f"# PHASE35_ADVERSARIAL_SLIPPAGE_REPORT\n\n"
            f"Timestamp: {report['timestamp']}\nStatus: ok\nPaper-only: true\n"
            f"Mitigations: {len(self.mitigations)}\nBlocked: {self.blocked_count}\n"
            f"Hard limit: {self.config.hard_limit_bps} bps | Warn: {self.config.warn_limit_bps} bps\n"
        )
        rep_json.write_text(json.dumps(serialize_metrics_strict(report), indent=2))
        return {"status": "ok", "json": str(rep_json), "md": str(rep_md), "paper_only": True}
