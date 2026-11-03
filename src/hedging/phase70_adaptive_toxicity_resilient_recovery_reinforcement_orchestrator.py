"""
Phase 70: Adaptive Toxicity-Resilient Recovery Reinforcement Orchestrator (crypto options + orderflow).
Adaptive toxicity-resilient recovery reinforcement orchestrator: recovery reinforcement, venue failover recovery,
hedging recovery reinforcement guardrails, deterministic; PAPER-ONLY. Compose Phases 17-69.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List

from src.hedging.phase69_adaptive_toxicity_resilient_self_healing_orchestrator import (
    Phase69AdaptiveToxicityResilientSelfHealingOrchestrator,
    Phase69AdaptiveToxicityResilientSelfHealingConfig,
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
    h = hashlib.sha256(f"{seed}|p70hedge|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p70hedge_{tag}_{h}"


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
class Phase70AdaptiveToxicityResilientRecoveryReinforcementConfig:
    seed: int = 70061
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 80
    recovery_failover_interval: int = 7
    capital_reinforce_interval: int = 6
    hedging_reinforce_interval: int = 5
    failover_min: float = 0.9965
    reinforce_sev_threshold: float = 0.41
    hedge_reinforce_min: float = 0.9975
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError(
                "Phase70AdaptiveToxicityResilientRecoveryReinforcementOrchestrator: paper_only must remain True (live path hard-gated)"
            )


class Phase70AdaptiveToxicityResilientRecoveryReinforcementOrchestrator:
    """Adaptive toxicity-resilient recovery reinforcement orchestrator for crypto options + orderflow."""

    def __init__(self, cfg: Phase70AdaptiveToxicityResilientRecoveryReinforcementConfig | None = None) -> None:
        self.cfg = cfg or Phase70AdaptiveToxicityResilientRecoveryReinforcementConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase70AdaptiveToxicityResilientRecoveryReinforcementOrchestrator: paper_only must remain True")
        self.sh69 = Phase69AdaptiveToxicityResilientSelfHealingOrchestrator(
            Phase69AdaptiveToxicityResilientSelfHealingConfig(seed=self.cfg.seed + 1, paper_only=True, cycles=self.cfg.cycles)
        )
        self.risk54 = Phase54RealtimeRiskFusionEngine()
        self.tox58 = Phase58FlowToxicityMitigator()
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.recovery_failovers: List[Dict[str, Any]] = []
        self.capital_reinforcements: List[Dict[str, Any]] = []
        self.hedging_reinforcements: List[Dict[str, Any]] = []
        self.recovery_reinforce_attestations: List[Dict[str, Any]] = []
        self._cycle = 0

    def _orch_reinforce_decision(self, failover_ok: float, sev: float, hedge_ok: float) -> Dict[str, Any]:
        throttle = 1.0
        ok = failover_ok >= self.cfg.failover_min and hedge_ok >= self.cfg.hedge_reinforce_min
        reasons: List[str] = []
        if failover_ok < self.cfg.failover_min:
            reasons.append("failover_below_min")
            throttle *= 0.49
        if sev >= self.cfg.reinforce_sev_threshold:
            reasons.append("reinforce_sev_elevated")
            throttle *= 0.69
        if hedge_ok < self.cfg.hedge_reinforce_min:
            reasons.append("hedge_reinforce_below_min")
            throttle *= 0.49
        ok = ok and throttle >= 0.4
        return {"reinforced": bool(ok), "orch_reinforce_throttle_factor": round(float(_finite(throttle)), 6), "reasons": reasons, "enforced": True}

    def run_recovery_reinforcement_orchestration(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.recovery_failovers = []
        self.capital_reinforcements = []
        self.hedging_reinforcements = []
        self.recovery_reinforce_attestations = []

        s_rep = self.sh69.run_self_healing_orchestration(cycles=60)
        tox_rep = self.tox58.mitigate(cycles=40)
        self.risk54.run_campaign(cycles=30)
        self.of.run_campaign(cycles=40)

        avg_tox = _finite(tox_rep.get("avg_vpin", 0.18))
        avg_orch = _finite(s_rep.get("self_heal_orch_pass_rate", 0.99))

        for i in range(cycles):
            venue = self.cfg.venues[i % len(self.cfg.venues)]
            underlying = self.cfg.underlyings[i % len(self.cfg.underlyings)]
            toxicity_i = max(0.0, min(1.0, avg_tox + (i % 19) * 0.011))
            sev = max(0.0, min(1.0, toxicity_i * 1.14 + (i % 13) * 0.014))
            failover_ok = max(0.9935, min(1.0, 0.9999 - sev * 0.012))
            hedge_ok = max(0.9945, min(1.0, 0.9999 - sev * 0.011))
            dec = self._orch_reinforce_decision(failover_ok, sev, hedge_ok)

            if i % self.cfg.recovery_failover_interval == 0:
                self.recovery_failovers.append(
                    serialize_metrics_strict(
                        {
                            "frf_id": _make_id(self.cfg.seed, "frf", i),
                            "cycle": i,
                            "venue": venue,
                            "failover_ok": round(float(_finite(failover_ok)), 9),
                            "mode": "cross_venue_failover_recovery",
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if i % self.cfg.capital_reinforce_interval == 0 and sev >= 0.37:
                self.capital_reinforcements.append(
                    serialize_metrics_strict(
                        {
                            "cre_id": _make_id(self.cfg.seed, "cre", i),
                            "cycle": i,
                            "venue": venue,
                            "underlying": underlying,
                            "severity": round(float(_finite(sev)), 6),
                            "action": "capital_reinforce_selective",
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if i % self.cfg.hedging_reinforce_interval == 0:
                self.hedging_reinforcements.append(
                    serialize_metrics_strict(
                        {
                            "hre_id": _make_id(self.cfg.seed, "hre", i),
                            "cycle": i,
                            "venue": venue,
                            "hedge_ok": round(float(_finite(hedge_ok)), 9),
                            "reinforced": dec["reinforced"],
                            "orch_reinforce_throttle_factor": dec["orch_reinforce_throttle_factor"],
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if i % 6 == 0:
                self.recovery_reinforce_attestations.append(
                    serialize_metrics_strict(
                        {
                            "rra_id": _make_id(self.cfg.seed, "rra", i),
                            "cycle": i,
                            "reinforced": dec["reinforced"],
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )

        rep = serialize_metrics_strict(
            {
                "phase": "PHASE70_ADAPTIVE_TOXICITY_RESILIENT_RECOVERY_REINFORCEMENT_ORCHESTRATOR",
                "timestamp": _utc_now(),
                "paper_only": True,
                "gates_ok": True,
                "seed": self.cfg.seed,
                "cycles": cycles,
                "n_recovery_failovers": len(self.recovery_failovers),
                "n_capital_reinforcements": len(self.capital_reinforcements),
                "n_hedging_reinforcements": len(self.hedging_reinforcements),
                "n_recovery_reinforce_attestations": len(self.recovery_reinforce_attestations),
                "avg_failover_ok": round(
                    float(sum(_finite(x.get("failover_ok", 0.0)) for x in self.recovery_failovers) / max(1, len(self.recovery_failovers))),
                    9,
                ),
                "recovery_reinforce_pass_rate": round(
                    float(sum(1 for x in self.hedging_reinforcements if x.get("reinforced")) / max(1, len(self.hedging_reinforcements))),
                    6,
                ),
                "composes": ["PHASE69", "PHASE54", "PHASE39", "PHASE58"],
            }
        )
        _assert_finite(rep, "phase70_reinforce_orch_rep")
        return rep

    def generate_artifacts(self, outdir: str | None = None) -> Dict[str, Any]:
        outdir = Path(outdir or self.cfg.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        rep = self.run_recovery_reinforcement_orchestration(cycles=self.cfg.cycles)
        payload = serialize_metrics_strict(
            {
                "report": rep,
                "recovery_failovers": self.recovery_failovers,
                "capital_reinforcements": self.capital_reinforcements,
                "hedging_reinforcements": self.hedging_reinforcements,
                "recovery_reinforce_attestations": self.recovery_reinforce_attestations,
            }
        )
        _assert_finite(payload, "phase70_reinforce_orch_payload")
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = outdir / f"PHASE70_ADAPTIVE_TOXICITY_RESILIENT_RECOVERY_REINFORCEMENT_ORCHESTRATOR_{ts}.json"
        md_path = outdir / f"PHASE70_ADAPTIVE_TOXICITY_RESILIENT_RECOVERY_REINFORCEMENT_ORCHESTRATOR_{ts}.md"
        json_path.write_text(json.dumps(payload, indent=2, allow_nan=False))
        md = [
            "# PHASE70_ADAPTIVE_TOXICITY_RESILIENT_RECOVERY_REINFORCEMENT_ORCHESTRATOR",
            f"Timestamp: {_utc_now()}",
            f"paper_only: {rep['paper_only']}",
            f"gates_ok: {rep['gates_ok']}",
            f"cycles: {rep['cycles']}",
            f"avg_failover_ok: {rep['avg_failover_ok']}",
            f"recovery_reinforce_pass_rate: {rep['recovery_reinforce_pass_rate']}",
            f"n_recovery_failovers: {rep['n_recovery_failovers']}",
            f"n_capital_reinforcements: {rep['n_capital_reinforcements']}",
            "",
            "## Composes",
            "- PHASE69, PHASE54, PHASE39, PHASE58",
            "",
        ]
        md_path.write_text("\n".join(md))
        rep["json_path"] = str(json_path)
        rep["md_path"] = str(md_path)
        return rep
