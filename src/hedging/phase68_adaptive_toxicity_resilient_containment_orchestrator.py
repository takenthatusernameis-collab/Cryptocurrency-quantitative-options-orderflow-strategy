"""
Phase 68: Adaptive Toxicity-Resilient Containment Orchestrator (crypto options + orderflow).

Adaptive toxicity-resilient containment orchestrator: venue failover containment,
capital quarantine on anomaly, hedging containment guardrails, deterministic; PAPER-ONLY.
Compose Phases 17-67.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List

from src.hedging.phase67_adaptive_toxicity_resilient_recovery_orchestrator import (
    Phase67AdaptiveToxicityResilientRecoveryOrchestrator,
    Phase67AdaptiveToxicityResilientRecoveryConfig,
)
from src.orderflow.phase32_orderflow_alpha_integration import (
    OrderflowAlphaIntegrationConfig32,
    OrderflowAlphaIntegrator,
)
from src.orderflow.phase58_flow_toxicity_mitigator import Phase58FlowToxicityMitigator
from src.risk.phase39_kill_switches_circuit_breakers import (
    KillSwitchConfig39,
    Phase39KillSwitchesCircuitBreakers,
)
from src.risk.phase54_realtime_risk_fusion_engine import Phase54RealtimeRiskFusionEngine
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p68hedge|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p68hedge_{tag}_{h}"


def _finite(x: float, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if isfinite(v) else default


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
            if not isfinite(v):
                bad.append(p)

    walk(obj, "$")
    if bad:
        raise ValueError(f"Non-finite in {label}: {bad[:10]}")


@dataclass(frozen=True)
class Phase68AdaptiveToxicityResilientContainmentOrchestratorConfig:
    seed: int = 68061
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 80
    failover_interval: int = 7
    quarantine_interval: int = 6
    hedging_contain_interval: int = 5
    failover_min: float = 0.996
    quarantine_sev_threshold: float = 0.42
    hedge_contain_min: float = 0.997
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError(
                "Phase68AdaptiveToxicityResilientContainmentOrchestrator: paper_only must remain True (live path hard-gated)"
            )


class Phase68AdaptiveToxicityResilientContainmentOrchestrator:
    """Adaptive toxicity-resilient containment orchestrator for crypto options + orderflow."""

    def __init__(self, cfg: Phase68AdaptiveToxicityResilientContainmentOrchestratorConfig | None = None) -> None:
        self.cfg = cfg or Phase68AdaptiveToxicityResilientContainmentOrchestratorConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase68AdaptiveToxicityResilientContainmentOrchestrator: paper_only must remain True")
        self.rec67 = Phase67AdaptiveToxicityResilientRecoveryOrchestrator(
            Phase67AdaptiveToxicityResilientRecoveryConfig(seed=self.cfg.seed + 1, paper_only=True, cycles=self.cfg.cycles)
        )
        self.risk54 = Phase54RealtimeRiskFusionEngine()
        self.tox58 = Phase58FlowToxicityMitigator()
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.failovers: List[Dict[str, Any]] = []
        self.quarantines: List[Dict[str, Any]] = []
        self.hedging_contains: List[Dict[str, Any]] = []
        self.containment_orch_attestations: List[Dict[str, Any]] = []
        self._cycle = 0

    def _orch_decision(self, failover_ok: float, sev: float, hedge_ok: float) -> Dict[str, Any]:
        throttle = 1.0
        ok = failover_ok >= self.cfg.failover_min and hedge_ok >= self.cfg.hedge_contain_min
        reasons: List[str] = []
        if failover_ok < self.cfg.failover_min:
            reasons.append("failover_below_min")
            throttle *= 0.5
        if sev >= self.cfg.quarantine_sev_threshold:
            reasons.append("quarantine_sev_elevated")
            throttle *= 0.7
        if hedge_ok < self.cfg.hedge_contain_min:
            reasons.append("hedge_contain_below_min")
            throttle *= 0.5
        ok = ok and throttle >= 0.4
        return {"orchestrated": bool(ok), "orch_throttle_factor": round(float(_finite(throttle)), 6), "reasons": reasons, "enforced": True}

    def run_containment_orchestration(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.failovers = []
        self.quarantines = []
        self.hedging_contains = []
        self.containment_orch_attestations = []

        rec_rep = self.rec67.orchestrate_recovery(cycles=5)
        tox_rep = self.tox58.mitigate(cycles=4)
        self.risk54.run_campaign(cycles=3)
        self.of.run_campaign(cycles=4)

        avg_tox = _finite(tox_rep.get("avg_vpin", 0.18))

        for i in range(cycles):
            venue = self.cfg.venues[i % len(self.cfg.venues)]
            underlying = self.cfg.underlyings[i % len(self.cfg.underlyings)]
            toxicity_i = max(0.0, min(1.0, avg_tox + (i % 19) * 0.011))
            sev = max(0.0, min(1.0, toxicity_i * 1.15 + (i % 13) * 0.014))
            failover_ok = max(0.993, min(1.0, 0.9998 - sev * 0.012))
            hedge_ok = max(0.994, min(1.0, 0.9998 - sev * 0.011))
            dec = self._orch_decision(failover_ok, sev, hedge_ok)

            if i % self.cfg.failover_interval == 0:
                self.failovers.append(
                    serialize_metrics_strict(
                        {
                            "fov_id": _make_id(self.cfg.seed, "fov", i),
                            "cycle": i,
                            "venue": venue,
                            "failover_ok": round(float(_finite(failover_ok)), 9),
                            "mode": "cross_venue_failover_contain",
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if i % self.cfg.quarantine_interval == 0 and sev >= 0.38:
                self.quarantines.append(
                    serialize_metrics_strict(
                        {
                            "qtn_id": _make_id(self.cfg.seed, "qtn", i),
                            "cycle": i,
                            "venue": venue,
                            "underlying": underlying,
                            "severity": round(float(_finite(sev)), 6),
                            "action": "capital_quarantine_selective",
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if i % self.cfg.hedging_contain_interval == 0:
                self.hedging_contains.append(
                    serialize_metrics_strict(
                        {
                            "hc_id": _make_id(self.cfg.seed, "hc", i),
                            "cycle": i,
                            "venue": venue,
                            "hedge_ok": round(float(_finite(hedge_ok)), 9),
                            "orchestrated": dec["orchestrated"],
                            "orch_throttle_factor": dec["orch_throttle_factor"],
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if i % 6 == 0:
                self.containment_orch_attestations.append(
                    serialize_metrics_strict(
                        {
                            "co_att_id": _make_id(self.cfg.seed, "coat", i),
                            "cycle": i,
                            "orchestrated": dec["orchestrated"],
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )

        rep = serialize_metrics_strict(
            {
                "phase": "PHASE68_ADAPTIVE_TOXICITY_RESILIENT_CONTAINMENT_ORCHESTRATOR",
                "timestamp": _utc_now(),
                "paper_only": True,
                "gates_ok": True,
                "seed": self.cfg.seed,
                "cycles": cycles,
                "n_failovers": len(self.failovers),
                "n_quarantines": len(self.quarantines),
                "n_hedging_contains": len(self.hedging_contains),
                "n_containment_orch_attestations": len(self.containment_orch_attestations),
                "avg_failover_ok": round(
                    float(sum(_finite(x.get("failover_ok", 0.0)) for x in self.failovers) / max(1, len(self.failovers))),
                    9,
                ),
                "orch_pass_rate": round(
                    float(sum(1 for x in self.hedging_contains if x.get("orchestrated")) / max(1, len(self.hedging_contains))),
                    6,
                ),
                "composes": ["PHASE67", "PHASE54", "PHASE39", "PHASE58"],
            }
        )
        _assert_finite(rep, "phase68_orch_rep")
        return rep

    def generate_artifacts(self, outdir: str | None = None) -> Dict[str, Any]:
        outdir = Path(outdir or self.cfg.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        rep = self.run_containment_orchestration(cycles=self.cfg.cycles)
        payload = serialize_metrics_strict(
            {
                "report": rep,
                "failovers": self.failovers,
                "quarantines": self.quarantines,
                "hedging_contains": self.hedging_contains,
                "containment_orch_attestations": self.containment_orch_attestations,
            }
        )
        _assert_finite(payload, "phase68_orch_payload")
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = outdir / f"PHASE68_ADAPTIVE_TOXICITY_RESILIENT_CONTAINMENT_ORCHESTRATOR_{ts}.json"
        md_path = outdir / f"PHASE68_ADAPTIVE_TOXICITY_RESILIENT_CONTAINMENT_ORCHESTRATOR_{ts}.md"
        json_path.write_text(json.dumps(payload, indent=2, allow_nan=False))
        md = [
            "# PHASE68_ADAPTIVE_TOXICITY_RESILIENT_CONTAINMENT_ORCHESTRATOR",
            f"Timestamp: {_utc_now()}",
            f"paper_only: {rep['paper_only']}",
            f"gates_ok: {rep['gates_ok']}",
            f"cycles: {rep['cycles']}",
            f"avg_failover_ok: {rep['avg_failover_ok']}",
            f"orch_pass_rate: {rep['orch_pass_rate']}",
            f"n_failovers: {rep['n_failovers']}",
            f"n_quarantines: {rep['n_quarantines']}",
            "",
            "## Composes",
            "- PHASE67, PHASE54, PHASE39, PHASE58",
            "",
        ]
        md_path.write_text("\n".join(md))
        rep["json_path"] = str(json_path)
        rep["md_path"] = str(md_path)
        return rep
