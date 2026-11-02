"""
Phase 59: Autonomous Execution Hardening Loop (crypto options + orderflow).

Autonomous execution hardening: venue failover, circuit breakers, post-trade
validation, auto-contain/rollback, artifacts, composes Phases 17-58.
PAPER-ONLY enforced.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List

from src.execution.phase58_adaptive_options_smart_order_router import Phase58AdaptiveOptionsSmartOrderRouter
from src.hedging.phase59_adaptive_cross_asset_hedge_fusion import Phase59AdaptiveCrossAssetHedgeFusion
from src.integration.phase58_autonomous_risk_containment_loop import Phase58AutonomousRiskContainmentLoop
from src.liquidity.phase59_fragmentation_toxicity_arb_engine import Phase59FragmentationToxicityArbEngine
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
from src.risk.phase57_production_circuit_breakers import Phase57ProductionCircuitBreakers
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p59harden|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p59harden_{tag}_{h}"


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
class Phase59AutonomousExecutionHardeningConfig:
    seed: int = 59061
    paper_only: bool = True
    cycles: int = 80
    venue_failover_enabled: bool = True
    posttrade_validation_enabled: bool = True
    auto_contain_on_breach: bool = True
    auto_rollback_on_severe: bool = True
    drawdown_halt_pct: float = 0.05
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError("Phase59AutonomousExecutionHardeningLoop: paper_only must remain True (live path hard-gated)")


class Phase59AutonomousExecutionHardeningLoop:
    """Autonomous execution hardening loop composing Phases 17-58."""

    def __init__(self, cfg: Phase59AutonomousExecutionHardeningConfig | None = None) -> None:
        self.cfg = cfg or Phase59AutonomousExecutionHardeningConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase59AutonomousExecutionHardeningLoop: paper_only must remain True")
        self.arc58 = Phase58AutonomousRiskContainmentLoop()
        self.arb59 = Phase59FragmentationToxicityArbEngine()
        self.hedge59 = Phase59AdaptiveCrossAssetHedgeFusion()
        self.risk54 = Phase54RealtimeRiskFusionEngine()
        self.cb57 = Phase57ProductionCircuitBreakers()
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.tox58 = Phase58FlowToxicityMitigator()
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.sor58 = Phase58AdaptiveOptionsSmartOrderRouter()
        self.failovers: List[Dict[str, Any]] = []
        self.posttrade_validations: List[Dict[str, Any]] = []
        self.containments: List[Dict[str, Any]] = []
        self.rollbacks: List[Dict[str, Any]] = []
        self.venue_states: Dict[str, str] = {v: "active" for v in ("deribit", "okx", "bybit", "binance")}
        self._cycle = 0

    def run_hardening(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.failovers = []
        self.posttrade_validations = []
        self.containments = []
        self.rollbacks = []
        arc_rep = self.arc58.run_containment(cycles=40)
        arb_rep = self.arb59.run_arb(cycles=40)
        hedge_rep = self.hedge59.run_hedge_fusion(cycles=40)
        risk_rep = self.risk54.run_campaign(cycles=40)
        cb_rep = self.cb57.evaluate(metrics={
            "drawdown_pct": _finite(risk_rep.get("max_drawdown_pct", 0.02)) if "max_drawdown_pct" in risk_rep else 0.02,
            "latency_ms_p99": _finite(hedge_rep.get("avg_latency_ms", 20.0)),
            "toxicity": _finite(arb_rep.get("avg_toxicity", 0.18)),
            "risk_breach": float(len(risk_rep.get("breaches", []))) / 100.0,
        })
        of_rep = self.of.run_campaign(cycles=30)
        tox_rep = self.tox58.mitigate(cycles=40)
        sor_rep = self.sor58.route_adaptive(cycles=40)
        ks_rep = self.ks.run_campaign()
        halted = bool(ks_rep.get("halted", False)) or bool(cb_rep.get("halted", False)) or bool(arc_rep.get("halted", False))
        cb_breaches = cb_rep.get("breaches", [])
        active_venues = [v for v, s in self.venue_states.items() if s == "active"]

        for i in range(cycles):
            venue = active_venues[i % max(1, len(active_venues))] if active_venues else "deribit"
            underlying = ("BTC", "ETH", "SOL")[i % 3]
            dd_pct = 0.02 + (i % 9) * 0.006
            risk_breach_i = bool(cb_breaches) or halted or dd_pct >= self.cfg.drawdown_halt_pct
            latency_ms = 6.0 + (i % 6) * 4.0 + _finite(arb_rep.get("avg_toxicity", 0.18)) * 8.0

            if self.cfg.venue_failover_enabled and (risk_breach_i or i % 11 == 5) and len(active_venues) > 1:
                failed = venue
                self.venue_states[failed] = "failover"
                active_venues = [v for v, s in self.venue_states.items() if s == "active"] or [failed]
                self.failovers.append(serialize_metrics_strict({
                    "fo_id": _make_id(self.cfg.seed, "fo", i),
                    "cycle": i,
                    "failed_venue": failed,
                    "fallback_venue": active_venues[0] if active_venues else "deribit",
                    "reason": "risk_breach_or_scheduled_drill",
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))
                self.venue_states[failed] = "active"

            if self.cfg.posttrade_validation_enabled and i % 3 == 0:
                fill_rate = max(0.5, min(1.0, 0.97 - _finite(arb_rep.get("avg_toxicity", 0.18)) * 0.4 - latency_ms / 500.0))
                passed = fill_rate >= 0.7 and not halted
                self.posttrade_validations.append(serialize_metrics_strict({
                    "val_id": _make_id(self.cfg.seed, "val", i),
                    "cycle": i,
                    "venue": venue,
                    "underlying": underlying,
                    "fill_rate": float(_finite(fill_rate)),
                    "latency_ms": float(_finite(latency_ms)),
                    "passed": bool(passed),
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))

            if risk_breach_i and self.cfg.auto_contain_on_breach:
                self.containments.append(serialize_metrics_strict({
                    "contain_id": _make_id(self.cfg.seed, "contain", i),
                    "cycle": i,
                    "venue": venue,
                    "underlying": underlying,
                    "action": "auto_contain",
                    "trigger": "risk_breach_or_halt",
                    "severity": "critical" if halted else "high",
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))
            if risk_breach_i and self.cfg.auto_rollback_on_severe and dd_pct >= self.cfg.drawdown_halt_pct:
                self.rollbacks.append(serialize_metrics_strict({
                    "rb_id": _make_id(self.cfg.seed, "rb", i),
                    "cycle": i,
                    "venue": venue,
                    "underlying": underlying,
                    "action": "auto_rollback",
                    "trigger": "severe_drawdown",
                    "drawdown_pct": float(_finite(dd_pct)),
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))

        pass_rate = sum(1 for v in self.posttrade_validations if v["passed"]) / max(1, len(self.posttrade_validations))
        gates_ok = bool(pass_rate >= 0.75 and not halted and arb_rep.get("gates_ok", False) and hedge_rep.get("gates_ok", False))
        rep = serialize_metrics_strict({
            "phase": "PHASE59_AUTONOMOUS_EXECUTION_HARDENING_LOOP",
            "timestamp": _utc_now(),
            "seed": self.cfg.seed,
            "paper_only": True,
            "cycles": cycles,
            "gates_ok": bool(gates_ok),
            "halted": bool(halted),
            "n_failovers": len(self.failovers),
            "n_posttrade_validations": len(self.posttrade_validations),
            "posttrade_pass_rate": float(_finite(pass_rate)),
            "n_containments": len(self.containments),
            "n_rollbacks": len(self.rollbacks),
            "cb_breaches": len(cb_breaches),
            "arc58_ok": bool(arc_rep.get("gates_ok", False)),
            "arb59_ok": bool(arb_rep.get("gates_ok", False)),
            "hedge59_ok": bool(hedge_rep.get("gates_ok", False)),
            "risk54_ok": bool(risk_rep.get("gates_ok", False)),
            "cb57_ok": bool(cb_rep.get("gates_ok", False)),
            "composed_phases": "17-58",
        })
        _assert_finite(rep, "phase59_hardening_report")
        return rep

    def generate_artifacts(self, outdir: str = "research_state") -> Dict[str, Any]:
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        rep = self.run_hardening(cycles=self.cfg.cycles)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = out / f"PHASE59_AUTONOMOUS_EXECUTION_HARDENING_{ts}.json"
        mpath = out / f"PHASE59_AUTONOMOUS_EXECUTION_HARDENING_{ts}.md"
        with jpath.open("w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2, sort_keys=True)
        with mpath.open("w", encoding="utf-8") as f:
            f.write(
                f"# PHASE59 Autonomous Execution Hardening Loop\n\n"
                f"- Timestamp: {rep['timestamp']}\n"
                f"- Gates OK: {rep['gates_ok']}\n"
                f"- Halted: {rep['halted']}\n"
                f"- Failovers: {rep['n_failovers']} | Posttrade Validations: {rep['n_posttrade_validations']}\n"
                f"- Posttrade Pass Rate: {rep['posttrade_pass_rate']:.4f}\n"
                f"- Containments: {rep['n_containments']} | Rollbacks: {rep['n_rollbacks']} | CB Breaches: {rep['cb_breaches']}\n"
                f"- Composed: {rep['composed_phases']}\n"
            )
        rep["json_path"] = str(jpath)
        rep["md_path"] = str(mpath)
        return rep


# Compatibility: ensure Phase57 circuit breakers expose run_campaign/run_monitor aliases
try:
    from src.risk.phase57_production_circuit_breakers import Phase57ProductionCircuitBreakers as _CB57
    if not hasattr(_CB57, "run_campaign"):
        def _cb_run_campaign(self, cycles: int = 30, **kwargs):
            rep = self.evaluate()
            return {
                "phase": rep.get("phase"),
                "paper_only": rep.get("paper_only", True),
                "halted": bool(rep.get("halted", False)),
                "gates_ok": not bool(rep.get("halted", False)),
                "cycles": cycles,
                "breaches": rep.get("breaches", []),
            }
        _CB57.run_campaign = _cb_run_campaign  # type: ignore
    if not hasattr(_CB57, "run_monitor"):
        _CB57.run_monitor = _CB57.run_campaign  # type: ignore
except Exception:
    pass
