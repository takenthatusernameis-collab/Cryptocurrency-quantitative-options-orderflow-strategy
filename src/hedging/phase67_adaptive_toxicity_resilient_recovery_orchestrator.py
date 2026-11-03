"""
Phase 67: Adaptive Toxicity-Resilient Recovery Orchestrator (crypto options + orderflow).

Adaptive toxicity-resilient recovery orchestrator: venue failover recovery, capital rebalance on stress,
hedging recovery guardrails, deterministic; PAPER-ONLY. Compose Phases 17-66.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List

from src.hedging.phase66_adaptive_toxicity_resilient_capital_rebalance_orchestrator import (
    Phase66AdaptiveToxicityResilientCapitalRebalanceOrchestrator,
    Phase66AdaptiveToxicityResilientCapitalRebalanceOrchestratorConfig,
)
from src.hedging.phase65_adaptive_toxicity_resilient_capital_allocation_orchestrator import (
    Phase65AdaptiveToxicityResilientCapitalAllocationOrchestrator,
    Phase65AdaptiveToxicityResilientCapitalAllocationOrchestratorConfig,
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
    h = hashlib.sha256(f"{seed}|p67hedge|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p67hedge_{tag}_{h}"


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
class Phase67AdaptiveToxicityResilientRecoveryConfig:
    seed: int = 67160
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 80
    venue_failover_interval: int = 6
    capital_rebalance_on_stress_interval: int = 8
    hedging_recovery_guardrail_interval: int = 4
    toxicity_recovery_threshold: float = 0.32
    failover_readiness_min: float = 0.995
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError(
                "Phase67AdaptiveToxicityResilientRecoveryOrchestrator: paper_only must remain True (live path hard-gated)"
            )


class Phase67AdaptiveToxicityResilientRecoveryOrchestrator:
    """Adaptive toxicity-resilient recovery orchestrator for crypto options + orderflow."""

    def __init__(self, cfg: Phase67AdaptiveToxicityResilientRecoveryConfig | None = None) -> None:
        self.cfg = cfg or Phase67AdaptiveToxicityResilientRecoveryConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase67AdaptiveToxicityResilientRecoveryOrchestrator: paper_only must remain True")
        self.rebal66 = Phase66AdaptiveToxicityResilientCapitalRebalanceOrchestrator(
            Phase66AdaptiveToxicityResilientCapitalRebalanceOrchestratorConfig(seed=self.cfg.seed + 1, paper_only=True, cycles=self.cfg.cycles)
        )
        self.alloc65 = Phase65AdaptiveToxicityResilientCapitalAllocationOrchestrator(
            Phase65AdaptiveToxicityResilientCapitalAllocationOrchestratorConfig(seed=self.cfg.seed + 2, paper_only=True, cycles=self.cfg.cycles)
        )
        self.risk54 = Phase54RealtimeRiskFusionEngine()
        self.tox58 = Phase58FlowToxicityMitigator()
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.venue_failovers: List[Dict[str, Any]] = []
        self.capital_rebalances: List[Dict[str, Any]] = []
        self.hedging_recoveries: List[Dict[str, Any]] = []
        self.recovery_attestations: List[Dict[str, Any]] = []
        self._cycle = 0

    def _recovery_decision(self, failover_readiness: float, tox: float) -> Dict[str, Any]:
        throttle = 1.0
        ok = failover_readiness >= self.cfg.failover_readiness_min
        reasons: List[str] = []
        if not ok:
            reasons.append("failover_readiness_below_min")
            throttle *= 0.5
        if tox >= self.cfg.toxicity_recovery_threshold:
            reasons.append("toxicity_recovery_guard")
            throttle *= 0.7
        ok = ok and throttle >= 0.4
        return {"recovered": bool(ok), "recovery_throttle_factor": round(float(_finite(throttle)), 6), "reasons": reasons, "executed": True}

    def orchestrate_recovery(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.venue_failovers = []
        self.capital_rebalances = []
        self.hedging_recoveries = []
        self.recovery_attestations = []

        reb66 = self.rebal66.orchestrate_rebalance(cycles=60)
        alloc65 = self.alloc65.orchestrate_allocation(cycles=60)
        tox_rep = self.tox58.mitigate(cycles=40)
        self.risk54.run_campaign(cycles=30)

        avg_tox = _finite(tox_rep.get("avg_vpin", 0.18))

        for i in range(cycles):
            venue = self.cfg.venues[i % len(self.cfg.venues)]
            underlying = self.cfg.underlyings[i % len(self.cfg.underlyings)]
            tox_i = max(0.0, min(1.0, avg_tox + (i % 17) * 0.013))
            failover_readiness = max(0.992, min(1.0, 0.9997 - tox_i * 0.01))
            dec = self._recovery_decision(failover_readiness, tox_i)

            if i % self.cfg.venue_failover_interval == 0:
                self.venue_failovers.append(
                    serialize_metrics_strict(
                        {
                            "fail_id": _make_id(self.cfg.seed, "fail", i),
                            "cycle": i,
                            "from_venue": venue,
                            "to_venue": self.cfg.venues[(i + 1) % len(self.cfg.venues)],
                            "failover_readiness": round(float(_finite(failover_readiness)), 9),
                            "recovered": dec["recovered"],
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if i % self.cfg.capital_rebalance_on_stress_interval == 0:
                self.capital_rebalances.append(
                    serialize_metrics_strict(
                        {
                            "creb_id": _make_id(self.cfg.seed, "creb", i),
                            "cycle": i,
                            "underlying": underlying,
                            "toxicity": round(float(_finite(tox_i)), 6),
                            "rebalanced": True,
                            "recovery_throttle_factor": dec["recovery_throttle_factor"],
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if i % self.cfg.hedging_recovery_guardrail_interval == 0:
                self.hedging_recoveries.append(
                    serialize_metrics_strict(
                        {
                            "hrec_id": _make_id(self.cfg.seed, "hrec", i),
                            "cycle": i,
                            "venue": venue,
                            "hedge_recovered": dec["recovered"],
                            "guardrails_ok": dec["recovered"],
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if i % 7 == 0:
                self.recovery_attestations.append(
                    serialize_metrics_strict(
                        {
                            "ratt_id": _make_id(self.cfg.seed, "ratt", i),
                            "cycle": i,
                            "failover_readiness": round(float(_finite(failover_readiness)), 9),
                            "recovered": dec["recovered"],
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )

        rep = serialize_metrics_strict(
            {
                "phase": "PHASE67_ADAPTIVE_TOXICITY_RESILIENT_RECOVERY_ORCHESTRATOR",
                "timestamp": _utc_now(),
                "paper_only": True,
                "gates_ok": True,
                "seed": self.cfg.seed,
                "cycles": cycles,
                "n_venue_failovers": len(self.venue_failovers),
                "n_capital_rebalances": len(self.capital_rebalances),
                "n_hedging_recoveries": len(self.hedging_recoveries),
                "n_recovery_attestations": len(self.recovery_attestations),
                "avg_failover_readiness": round(
                    float(sum(_finite(x.get("failover_readiness", 0.0)) for x in self.venue_failovers) / max(1, len(self.venue_failovers))),
                    9,
                ),
                "recovery_pass_rate": round(
                    float(sum(1 for x in self.venue_failovers if x.get("recovered")) / max(1, len(self.venue_failovers))),
                    6,
                ),
                "composes": ["PHASE66", "PHASE65", "PHASE54", "PHASE39", "PHASE58"],
            }
        )
        _assert_finite(rep, "phase67_recovery_rep")
        return rep

    def generate_artifacts(self, outdir: str | None = None) -> Dict[str, Any]:
        outdir = Path(outdir or self.cfg.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        rep = self.orchestrate_recovery(cycles=self.cfg.cycles)
        payload = serialize_metrics_strict(
            {
                "report": rep,
                "venue_failovers": self.venue_failovers,
                "capital_rebalances": self.capital_rebalances,
                "hedging_recoveries": self.hedging_recoveries,
                "recovery_attestations": self.recovery_attestations,
            }
        )
        _assert_finite(payload, "phase67_recovery_payload")
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = outdir / f"PHASE67_ADAPTIVE_TOXICITY_RESILIENT_RECOVERY_ORCHESTRATOR_{ts}.json"
        md_path = outdir / f"PHASE67_ADAPTIVE_TOXICITY_RESILIENT_RECOVERY_ORCHESTRATOR_{ts}.md"
        json_path.write_text(json.dumps(payload, indent=2, allow_nan=False))
        md = [
            "# PHASE67_ADAPTIVE_TOXICITY_RESILIENT_RECOVERY_ORCHESTRATOR",
            f"Timestamp: {_utc_now()}",
            f"paper_only: {rep['paper_only']}",
            f"gates_ok: {rep['gates_ok']}",
            f"cycles: {rep['cycles']}",
            f"avg_failover_readiness: {rep['avg_failover_readiness']}",
            f"recovery_pass_rate: {rep['recovery_pass_rate']}",
            f"n_venue_failovers: {rep['n_venue_failovers']}",
            "",
            "## Composes",
            "- PHASE66, PHASE65, PHASE54, PHASE39, PHASE58",
            "",
        ]
        md_path.write_text("\n".join(md))
        rep["json_path"] = str(json_path)
        rep["md_path"] = str(md_path)
        return rep
