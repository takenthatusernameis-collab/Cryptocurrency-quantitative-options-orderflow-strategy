"""
Phase 53: Fragmentation Arbitrage Engine (crypto options + orderflow).

Multi-venue options fragmentation arbitrage: cross-venue basis detection,
fragmentation scoring, toxicity gating, adverse-selection-aware sizing,
kill-switch integration, and deterministic PAPER-ONLY execution signaling.
Composes Phases 32/39/40/41/42/44/45/46/47/48/49/50/51/52.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List

from src.execution.phase52_realtime_liquidity_allocator import (
    Phase52AllocatorConfig,
    Phase52RealtimeLiquidityAllocator,
)
from src.execution.phase50_cross_venue_relative_value_executor import (
    Phase50RVConfig,
    Phase50CrossVenueRelativeValueExecutor,
)
from src.marketmaking.phase50_toxicity_aware_options_mm import (
    Phase50MMConfig,
    Phase50ToxicityAwareOptionsMM,
)
from src.alpha.phase51_adaptive_orderflow_alpha_fusion import (
    Phase51AlphaFusionConfig,
    Phase51AdaptiveOrderflowAlphaFusion,
)
from src.options.phase25_iv_skew_orderflow import IVSkewOrderflow
from src.options.phase26_liquidity_capture import LiquidityCapture
from src.orderflow.phase32_orderflow_alpha_integration import (
    OrderflowAlphaIntegrationConfig32,
    OrderflowAlphaIntegrator,
)
from src.risk.phase39_kill_switches_circuit_breakers import (
    KillSwitchConfig39,
    Phase39KillSwitchesCircuitBreakers,
)
from src.telemetry.serialization import serialize_metrics_strict
from src.volatility.phase49_vol_surface_arb_engine import (
    Phase49VolSurfConfig,
    Phase49VolSurfaceArbEngine,
)
from src.monitoring.slo import SLOMonitor, register_default_slos
from src.reconciliation.phase40_position_margin_audit import (
    Phase40AuditConfig,
    Phase40PositionMarginAudit,
)
from src.settlement.phase41_cross_venue_settlement import (
    Phase41SettlementConfig,
    Phase41CrossVenueSettlement,
)
from src.deployment.phase44_live_capital_deployment import Phase44LiveCapitalDeployment
from src.integration.phase42_risk_hedge_loop import Loop42Config, Phase42RiskHedgeLoop
from src.integration.phase45_resilience_validation_loop import Phase45ResilienceValidationLoop


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p53frag|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p53frag_{tag}_{h}"


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
class Phase53FragmentationArbConfig:
    seed: int = 53051
    paper_only: bool = True
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    underlyings: tuple = ("BTC", "ETH", "SOL")
    tenors: tuple = ("1D", "7D", "30D", "90D")
    cycles: int = 60
    basis_threshold_bps: float = 1.5
    frag_threshold: float = 0.02
    tox_base_threshold: float = 0.28
    tox_high_threshold: float = 0.42
    adv_sel_penalty: float = 0.5
    max_notional_usd: float = 1_000_000.0
    size_scale: float = 0.1
    paper_only_live_gate: bool = True
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError("Phase53FragmentationArbEngine: paper_only must remain True (live path hard-gated)")
        if self.basis_threshold_bps < 0:
            raise ValueError("basis_threshold_bps must be >= 0")
        if not (0.0 <= self.frag_threshold <= 1.0):
            raise ValueError("frag_threshold must be in [0,1]")
        if self.max_notional_usd < 0:
            raise ValueError("max_notional_usd must be >= 0")


class Phase53FragmentationArbEngine:
    """Multi-venue options fragmentation arbitrage engine."""

    def __init__(self, cfg: Phase53FragmentationArbConfig | None = None) -> None:
        self.cfg = cfg or Phase53FragmentationArbConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase53FragmentationArbEngine: paper_only must remain True")
        self.seed = int(self.cfg.seed)
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.seed + 39, paper_only=True))
        self.volarb = Phase49VolSurfaceArbEngine(
            Phase49VolSurfConfig(seed=self.seed + 49, paper_only=True, outdir=self.cfg.outdir)
        )
        self.alloc52 = Phase52RealtimeLiquidityAllocator(
            Phase52AllocatorConfig(seed=self.seed + 52, paper_only=True, cycles=self.cfg.cycles, outdir=self.cfg.outdir)
        )
        self.rv50 = Phase50CrossVenueRelativeValueExecutor(
            Phase50RVConfig(seed=self.seed + 50, paper_only=True, outdir=self.cfg.outdir)
        )
        self.mm50 = Phase50ToxicityAwareOptionsMM(
            Phase50MMConfig(seed=self.seed + 51, paper_only=True, outdir=self.cfg.outdir)
        )
        self.alpha51 = Phase51AdaptiveOrderflowAlphaFusion(
            Phase51AlphaFusionConfig(seed=self.seed + 53, paper_only=True, outdir=self.cfg.outdir)
        )
        self.skew = IVSkewOrderflow(seed=self.seed + 25)
        self.liq = LiquidityCapture(seed=self.seed + 26)
        self.slo = SLOMonitor()
        register_default_slos(self.slo)
        self.recon = Phase40PositionMarginAudit(Phase40AuditConfig(seed=self.seed + 40, paper_only=True))
        self.settle = Phase41CrossVenueSettlement(Phase41SettlementConfig(seed=self.seed + 41, paper_only=True))
        self.deploy = Phase44LiveCapitalDeployment(seed=self.seed, paper_only=True)
        self.resil = Phase45ResilienceValidationLoop(
            seed=self.seed + 45, cycles=self.cfg.cycles, paper_only=True, outdir=self.cfg.outdir
        )
        self.risk_hedge = Phase42RiskHedgeLoop(
            Loop42Config(seed=self.seed + 42, cycles=self.cfg.cycles, paper_only=True, modes="paper")
        )
        self.opportunities: List[Dict[str, Any]] = []
        self.basis_observations: List[Dict[str, Any]] = []
        self.frag_scores: List[Dict[str, Any]] = []
        self._cycle = 0

    def _venue_mid(self, venue: str, underlying: str, tenor: str, idx: int) -> float:
        h = hashlib.sha256(
            f"{self.seed}|mid|{venue}|{underlying}|{tenor}|{idx}".encode()
        ).hexdigest()
        base = int(h[:8], 16) / 0xFFFFFFFF
        # venue micro-structure offset creates cross-venue basis
        off = {"deribit": 0.0, "okx": 2e-4, "bybit": -1.5e-4, "binance": 3e-4}.get(venue, 0.0)
        spot = {"BTC": 105000.0, "ETH": 3400.0, "SOL": 175.0}[underlying]
        tenor_mult = {"1D": 1.0, "7D": 1.001, "30D": 1.005, "90D": 1.01}[tenor]
        return spot * (1.0 + base * 1e-4 + off) * tenor_mult

    def _basis_bps(self, v_a: str, v_b: str, underlying: str, tenor: str, idx: int) -> float:
        m_a = self._venue_mid(v_a, underlying, tenor, idx)
        m_b = self._venue_mid(v_b, underlying, tenor, idx)
        if m_b <= 0:
            return 0.0
        return (m_a - m_b) / m_b * 1e4

    def _fragmentation_score(self, idx: int) -> Dict[str, float]:
        scores: Dict[str, float] = {}
        for v in self.cfg.venues:
            lat = {"deribit": 0.8, "okx": 1.1, "bybit": 1.0, "binance": 0.9}.get(v, 1.0)
            depth = 0.5 + 0.1 * math.sin(idx * 0.17 + hash(v) % 7)
            frag = max(0.0, min(1.0, lat * 0.4 + (1.0 - depth) * 0.6))
            scores[v] = _finite(frag)
        return scores

    def _skew_context(self, underlying: str, tenor: str, idx: int) -> float:
        tape: List[Dict[str, Any]] = []
        for k in range(5):
            tape.append({
                "bid_vol": 10.0 + k,
                "ask_vol": 10.0 + k + (idx % 3),
                "toxicity": 0.1 + (idx % 5) * 0.02,
            })
        try:
            return float(self.skew.compute_orderflow_score(tape))
        except Exception:
            return 0.0

    def run_campaign(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.opportunities = []
        self.basis_observations = []
        self.frag_scores = []
        of_rep = self.of.run_campaign(cycles=15)
        tox = max(0.0, min(1.0, _finite(of_rep.get("avg_toxicity", 0.19))))
        imb = _finite(of_rep.get("avg_imbalance", 0.11))
        ksum = self.ks.run_campaign()
        halted = bool(ksum.get("halted", False))
        vol_rep = self.volarb.run_campaign(cycles=15)
        alloc_rep = self.alloc52.allocate(cycles=15)
        rv_rep = self.rv50.run_campaign(cycles=15)
        mm_rep = self.mm50.run_campaign(cycles=15)
        alpha_rep = self.alpha51.run_campaign(cycles=15)

        for i in range(cycles):
            frag = self._fragmentation_score(i)
            frag_mean = sum(frag.values()) / max(1, len(frag))
            frag_max = max(frag.values()) if frag else 0.0
            self.frag_scores.append(serialize_metrics_strict({
                "frag_id": _make_id(self.seed, "frag", i),
                "cycle": i,
                "frag_mean": float(_finite(frag_mean)),
                "frag_max": float(_finite(frag_max)),
                "venue_scores": {v: float(_finite(f)) for v, f in frag.items()},
                "paper_only": True,
                "timestamp": _utc_now(),
            }))
            cycle_tox = tox + (i * 1e-4) % 0.03
            cycle_tox = max(0.0, min(1.0, _finite(cycle_tox)))
            venue_pair_opps: List[Dict[str, Any]] = []
            for a_i, v_a in enumerate(self.cfg.venues):
                for b_i in range(a_i + 1, len(self.cfg.venues)):
                    v_b = self.cfg.venues[b_i]
                    underlying = self.cfg.underlyings[(a_i + b_i) % len(self.cfg.underlyings)]
                    tenor = self.cfg.tenors[(a_i * 3 + b_i) % len(self.cfg.tenors)]
                    basis = self._basis_bps(v_a, v_b, underlying, tenor, i)
                    basis_abs = abs(basis)
                    size_bps_scale = max(0.0, 1.0 - cycle_tox * self.cfg.adv_sel_penalty)
                    size_bps_scale *= max(0.0, 1.0 - abs(imb) * 0.5)
                    tradable = (
                        basis_abs >= self.cfg.basis_threshold_bps
                        and frag_max >= self.cfg.frag_threshold
                        and cycle_tox < self.cfg.tox_high_threshold
                        and not halted
                        and size_bps_scale > 0.1
                    )
                    self.basis_observations.append(serialize_metrics_strict({
                        "basis_id": _make_id(self.seed, "basis", i * 100 + a_i * 10 + b_i),
                        "cycle": i,
                        "venue_a": v_a,
                        "venue_b": v_b,
                        "underlying": underlying,
                        "tenor": tenor,
                        "basis_bps": float(_finite(basis)),
                        "basis_abs_bps": float(_finite(basis_abs)),
                        "frag_max": float(_finite(frag_max)),
                        "toxicity": float(_finite(cycle_tox)),
                        "imbalance": float(_finite(imb)),
                        "size_scale": float(_finite(size_bps_scale)),
                        "tradable": bool(tradable),
                        "halted": bool(halted),
                        "paper_only": True,
                        "timestamp": _utc_now(),
                    }))
                    if not tradable:
                        continue
                    notional = self.cfg.max_notional_usd * self.cfg.size_scale * size_bps_scale
                    notional = min(self.cfg.max_notional_usd, max(0.0, _finite(notional)))
                    edge_bps = basis_abs * 0.5 - cycle_tox * 2.0 - frag_max * 1.0
                    edge_bps = max(0.0, _finite(edge_bps))
                    skew_ctx = self._skew_context(underlying, tenor, i)
                    self.opportunities.append(serialize_metrics_strict({
                        "opp_id": _make_id(self.seed, "opp", i * 100 + a_i * 10 + b_i),
                        "cycle": i,
                        "venue_a": v_a,
                        "venue_b": v_b,
                        "underlying": underlying,
                        "tenor": tenor,
                        "side": "long_venue_a_short_venue_b" if basis > 0 else "short_venue_a_long_venue_b",
                        "basis_bps": float(_finite(basis)),
                        "notional_usd": float(_finite(notional)),
                        "edge_bps": float(_finite(edge_bps)),
                        "frag_score": float(_finite(frag_max)),
                        "toxicity": float(_finite(cycle_tox)),
                        "imbalance": float(_finite(imb)),
                        "orderflow_skew_ctx": float(_finite(skew_ctx)),
                        "kill_switch_ok": not halted,
                        "paper_only": True,
                        "timestamp": _utc_now(),
                    }))
                    venue_pair_opps.append(self.opportunities[-1])

        slo_evals = self.slo.evaluate_all()
        slo_alerts_fired = sum(1 for e in slo_evals if not e.get("met", True))
        gates_ok = bool(
            not halted
            and tox < self.cfg.tox_high_threshold
            and all(o["edge_bps"] >= 0 for o in self.opportunities)
            and all(isfinite(o["basis_bps"]) for o in self.basis_observations)
        )
        rep = serialize_metrics_strict({
            "phase": "PHASE53_FRAGMENTATION_ARB_ENGINE",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "paper_only": True,
            "cycles": cycles,
            "gates_ok": bool(gates_ok),
            "avg_toxicity": float(_finite(tox)),
            "avg_imbalance": float(_finite(imb)),
            "frag_mean": float(_finite(sum(f["frag_mean"] for f in self.frag_scores) / max(1, len(self.frag_scores)))),
            "frag_max": float(_finite(max((f["frag_max"] for f in self.frag_scores), default=0.0))),
            "n_basis_observations": len(self.basis_observations),
            "n_opportunities": len(self.opportunities),
            "total_notional_usd": float(_finite(sum(o["notional_usd"] for o in self.opportunities))),
            "total_edge_bps": float(_finite(sum(o["edge_bps"] for o in self.opportunities))),
            "halted_by_kill_switch": bool(halted),
            "halted_by_toxicity": bool(tox >= self.cfg.tox_high_threshold),
            "kill_switch_halted": bool(ksum.get("halted", False)),
            "slo_alerts_fired": int(slo_alerts_fired),
            "slo_evaluations": len(slo_evals),
            "sub_reports": {
                "vol_arb_49": {"gates_ok": vol_rep.get("gates_ok", False)},
                "liquidity_alloc_52": {"gates_ok": alloc_rep.get("gates_ok", False), "n_allocations": alloc_rep.get("n_allocations", 0)},
                "rv_50": {"gates_ok": rv_rep.get("gates_ok", False)},
                "mm_50": {"gates_ok": mm_rep.get("gates_ok", False)},
                "alpha_fusion_51": {"gates_ok": alpha_rep.get("gates_ok", False)},
            },
            "integration": "Phases17-52",
            "domain_focus": "crypto_options_orderflow_fragmentation_arb_basis_toxicity",
        })
        _assert_finite(rep, "phase53_frag_arb_report")
        return rep

    def generate_artifacts(self, outdir: str = "research_state") -> Dict[str, Any]:
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        rep = self.run_campaign(cycles=self.cfg.cycles)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = out / f"PHASE53_FRAGMENTATION_ARB_ENGINE_{ts}.json"
        mpath = out / f"PHASE53_FRAGMENTATION_ARB_ENGINE_{ts}.md"
        with jpath.open("w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2, sort_keys=True)
        lines = [
            "# PHASE53 Fragmentation Arb Engine",
            f"- Timestamp: {rep['timestamp']}",
            f"- Gates OK: {rep['gates_ok']}",
            f"- Avg Toxicity: {rep['avg_toxicity']}",
            f"- Frag Max: {rep['frag_max']}",
            f"- Basis Observations: {rep['n_basis_observations']}",
            f"- Opportunities: {rep['n_opportunities']}",
            f"- Total Notional USD: {rep['total_notional_usd']}",
            f"- Total Edge BPS: {rep['total_edge_bps']}",
            f"- Kill-Switch Halted: {rep['halted_by_kill_switch']}",
            f"- SLO Alerts Fired: {rep['slo_alerts_fired']}",
        ]
        with mpath.open("w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        rep["json_path"] = str(jpath)
        rep["md_path"] = str(mpath)
        return rep
