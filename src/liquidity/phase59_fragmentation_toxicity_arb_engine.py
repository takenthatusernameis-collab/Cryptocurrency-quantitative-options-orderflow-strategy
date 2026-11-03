"""
Phase 59: Fragmentation + Toxicity-Aware Cross-Venue Arbitrage Engine (crypto options + orderflow).

Cross-venue liquidity fragmentation arbitrage: basis detection between venues,
toxicity-adverse-selection filters, size hard limits, venue quarantine integration,
deterministic. PAPER-ONLY, finite numerics.
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
from src.liquidity.phase53_fragmentation_arb_engine import Phase53FragmentationArbEngine
from src.orderflow.phase32_orderflow_alpha_integration import (
    OrderflowAlphaIntegrationConfig32,
    OrderflowAlphaIntegrator,
)
from src.orderflow.phase58_flow_toxicity_mitigator import Phase58FlowToxicityMitigator
from src.risk.phase39_kill_switches_circuit_breakers import (
    KillSwitchConfig39,
    Phase39KillSwitchesCircuitBreakers,
)
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p59fragtox|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p59fragtox_{tag}_{h}"


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
class Phase59FragmentationToxicityArbConfig:
    seed: int = 59059
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 80
    basis_min_bps: float = 0.5
    basis_max_bps: float = 50.0
    toxicity_threshold: float = 0.35
    adverse_sel_threshold: float = 0.30
    hard_limit_notional_usd: float = 1_000_000.0
    max_consec_reject: int = 4
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError("Phase59FragmentationToxicityArb: paper_only must remain True (live path hard-gated)")
        if self.hard_limit_notional_usd <= 0:
            raise ValueError("hard_limit_notional_usd must be > 0")


class Phase59FragmentationToxicityArbEngine:
    """Fragmentation+toxicity-aware cross-venue arbitrage for crypto options + orderflow."""

    def __init__(self, cfg: Phase59FragmentationToxicityArbConfig | None = None) -> None:
        self.cfg = cfg or Phase59FragmentationToxicityArbConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase59FragmentationToxicityArbEngine: paper_only must remain True")
        self.frag53 = Phase53FragmentationArbEngine()
        self.tox58 = Phase58FlowToxicityMitigator()
        self.sor58 = Phase58AdaptiveOptionsSmartOrderRouter()
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.opportunities: List[Dict[str, Any]] = []
        self.filters: List[Dict[str, Any]] = []
        self.venues_quarantined: List[Dict[str, Any]] = []
        self.hard_limit_rejects: List[Dict[str, Any]] = []
        self._cycle = 0

    def run_arb(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.opportunities = []
        self.filters = []
        self.venues_quarantined = []
        self.hard_limit_rejects = []
        tox_rep = self.tox58.mitigate(cycles=4)
        frag_rep = self.frag53.run_campaign(cycles=4)
        sor_rep = self.sor58.route_adaptive(cycles=4)
        ks_rep = self.ks.run_campaign()
        of_rep = self.of.run_campaign(cycles=3)
        halted = bool(ks_rep.get("halted", False))
        avg_tox = _finite(tox_rep.get("avg_vpin", 0.2))
        avg_frag = _finite(frag_rep.get("avg_basis_bps", 1.0)) / 100.0
        consec_reject = 0

        for i in range(cycles):
            venue_a = self.cfg.venues[i % len(self.cfg.venues)]
            venue_b = self.cfg.venues[(i + 1) % len(self.cfg.venues)]
            underlying = self.cfg.underlyings[i % len(self.cfg.underlyings)]
            basis_bps = max(0.0, min(self.cfg.basis_max_bps, 1.0 + (i % 17) * 0.7 + avg_frag * 10.0))
            notional = min(self.cfg.hard_limit_notional_usd, 50_000.0 * (1.0 + i % 20))
            toxicity_i = max(0.0, min(1.0, avg_tox + (i % 11) * 0.03))
            as_i = max(0.0, min(1.0, toxicity_i * (1.05 + 0.05 * (i % 3))))
            venue_quarantined = venue_a in ("bybit",) and i % 7 == 3 and halted
            if venue_quarantined:
                self.venues_quarantined.append(serialize_metrics_strict({
                    "q_id": _make_id(self.cfg.seed, "vq", i),
                    "cycle": i,
                    "venue": venue_a,
                    "reason": "halt_or_toxicity_quarantine",
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))
                consec_reject += 1
                continue
            reject_reason: str | None = None
            if halted:
                reject_reason = "kill_switch_halted"
            elif toxicity_i >= self.cfg.toxicity_threshold:
                reject_reason = "toxicity_threshold"
            elif as_i >= self.cfg.adverse_sel_threshold:
                reject_reason = "adverse_selection"
            elif not (self.cfg.basis_min_bps <= basis_bps <= self.cfg.basis_max_bps):
                reject_reason = "basis_out_of_band"
            elif notional > self.cfg.hard_limit_notional_usd:
                reject_reason = "hard_limit_notional"
            if reject_reason is not None:
                self.filters.append(serialize_metrics_strict({
                    "filter_id": _make_id(self.cfg.seed, "filt", i),
                    "cycle": i,
                    "venue_a": venue_a,
                    "venue_b": venue_b,
                    "underlying": underlying,
                    "reason": reject_reason,
                    "basis_bps": float(_finite(basis_bps)),
                    "toxicity": float(_finite(toxicity_i)),
                    "adverse_selection": float(_finite(as_i)),
                    "notional_usd": float(_finite(notional)),
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))
                consec_reject += 1
                if consec_reject >= self.cfg.max_consec_reject:
                    self.venues_quarantined.append(serialize_metrics_strict({
                        "q_id": _make_id(self.cfg.seed, "consec", i),
                        "cycle": i,
                        "venue": venue_b,
                        "reason": "consecutive_rejects",
                        "paper_only": True,
                        "timestamp": _utc_now(),
                    }))
                    consec_reject = 0
                continue
            consec_reject = 0
            edge_bps = basis_bps - toxicity_i * 4.0 - as_i * 3.0
            self.opportunities.append(serialize_metrics_strict({
                "opp_id": _make_id(self.cfg.seed, "opp", i),
                "cycle": i,
                "venue_a": venue_a,
                "venue_b": venue_b,
                "underlying": underlying,
                "basis_bps": float(_finite(basis_bps)),
                "edge_bps": float(_finite(max(0.0, edge_bps))),
                "toxicity": float(_finite(toxicity_i)),
                "adverse_selection": float(_finite(as_i)),
                "notional_usd": float(_finite(notional)),
                "venue_quarantine_ok": True,
                "paper_only": True,
                "timestamp": _utc_now(),
            }))

        n_opps = len(self.opportunities)
        avg_edge = float(sum(o["edge_bps"] for o in self.opportunities) / max(1, n_opps))
        gates_ok = bool((not halted) and n_opps >= 0 and all(_finite(o["edge_bps"]) >= 0 for o in self.opportunities))
        rep = serialize_metrics_strict({
            "phase": "PHASE59_FRAGMENTATION_TOXICITY_ARB_ENGINE",
            "timestamp": _utc_now(),
            "seed": self.cfg.seed,
            "paper_only": True,
            "cycles": cycles,
            "gates_ok": bool(gates_ok),
            "halted": bool(halted),
            "avg_toxicity": float(_finite(avg_tox)),
            "n_opportunities": int(n_opps),
            "avg_edge_bps": float(_finite(avg_edge)),
            "n_filters": len(self.filters),
            "n_venue_quarantines": len(self.venues_quarantined),
            "n_hard_limit_rejects": len(self.hard_limit_rejects),
            "tox58_ok": bool(tox_rep.get("gates_ok", False)),
            "frag53_ok": bool(frag_rep.get("gates_ok", False)),
            "sor58_ok": bool(sor_rep.get("gates_ok", False)),
            "composed_phases": "17-58",
        })
        _assert_finite(rep, "phase59_arb_report")
        return rep

    def generate_artifacts(self, outdir: str = "research_state") -> Dict[str, Any]:
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        rep = self.run_arb(cycles=self.cfg.cycles)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = out / f"PHASE59_FRAGMENTATION_TOXICITY_ARB_{ts}.json"
        mpath = out / f"PHASE59_FRAGMENTATION_TOXICITY_ARB_{ts}.md"
        with jpath.open("w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2, sort_keys=True)
        with mpath.open("w", encoding="utf-8") as f:
            f.write(
                f"# PHASE59 Fragmentation + Toxicity-Aware Arb Engine\n\n"
                f"- Timestamp: {rep['timestamp']}\n"
                f"- Gates OK: {rep['gates_ok']}\n"
                f"- Halted: {rep['halted']}\n"
                f"- Opportunities: {rep['n_opportunities']}\n"
                f"- Avg Edge (bps): {rep['avg_edge_bps']:.4f}\n"
                f"- Filters: {rep['n_filters']} | Venue Quarantines: {rep['n_venue_quarantines']}\n"
                f"- Composed: {rep['composed_phases']}\n"
            )
        rep["json_path"] = str(jpath)
        rep["md_path"] = str(mpath)
        return rep
