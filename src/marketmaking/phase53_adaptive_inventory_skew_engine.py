"""
Phase 53: Adaptive Inventory Skew Engine (crypto options + orderflow).

Adaptive inventory skewing for options market making: regime-aware skew,
gamma-aware sizing, orderflow-shaded skew, kill-switch/SLO integration,
PAPER-ONLY deterministic. Composes Phases 32/39/40/41/42/44/45/46/47/48/49/50/51/52.
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
from src.alpha.phase48_regime_conditional_options_engine import (
    Phase48Config,
    Phase48RegimeConditionalOptionsEngine,
)
from src.alpha.phase51_adaptive_orderflow_alpha_fusion import (
    Phase51AlphaFusionConfig,
    Phase51AdaptiveOrderflowAlphaFusion,
)
from src.hedging.phase49_orderflow_driven_delta_hedge import (
    Phase49HedgeConfig,
    Phase49OrderflowDrivenDeltaHedge,
)
from src.volatility.phase49_vol_surface_arb_engine import (
    Phase49VolSurfConfig,
    Phase49VolSurfaceArbEngine,
)
from src.orderflow.phase32_orderflow_alpha_integration import (
    OrderflowAlphaIntegrationConfig32,
    OrderflowAlphaIntegrator,
)
from src.risk.phase39_kill_switches_circuit_breakers import (
    KillSwitchConfig39,
    Phase39KillSwitchesCircuitBreakers,
)
from src.telemetry.serialization import serialize_metrics_strict
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
    h = hashlib.sha256(f"{seed}|p53skew|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p53skew_{tag}_{h}"


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
class Phase53InventorySkewConfig:
    seed: int = 53052
    paper_only: bool = True
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    underlyings: tuple = ("BTC", "ETH", "SOL")
    tenors: tuple = ("1D", "7D", "30D", "90D")
    cycles: int = 60
    base_skew_bps: float = 6.0
    gamma_skew_factor: float = 0.4
    inventory_skew_factor: float = 0.3
    orderflow_shade_factor: float = 0.5
    tox_widen_factor: float = 2.0
    max_position_usd: float = 2_000_000.0
    gamma_cap_bps: float = 25.0
    regime_tighten: bool = True
    min_spread_bps: float = 0.5
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError("Phase53AdaptiveInventorySkewEngine: paper_only must remain True (live path hard-gated)")
        if self.base_skew_bps < 0 or self.gamma_cap_bps < 0:
            raise ValueError("skew/gamma caps must be >= 0")
        if self.max_position_usd < 0:
            raise ValueError("max_position_usd must be >= 0")


class Phase53AdaptiveInventorySkewEngine:
    """Adaptive inventory skew engine for crypto options market making."""

    def __init__(self, cfg: Phase53InventorySkewConfig | None = None) -> None:
        self.cfg = cfg or Phase53InventorySkewConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase53AdaptiveInventorySkewEngine: paper_only must remain True")
        self.seed = int(self.cfg.seed)
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.seed + 39, paper_only=True))
        self.hedge49 = Phase49OrderflowDrivenDeltaHedge(
            Phase49HedgeConfig(seed=self.seed + 49, paper_only=True, outdir=self.cfg.outdir)
        )
        self.volarb49 = Phase49VolSurfaceArbEngine(
            Phase49VolSurfConfig(seed=self.seed + 50, paper_only=True, outdir=self.cfg.outdir)
        )
        self.alloc52 = Phase52RealtimeLiquidityAllocator(
            Phase52AllocatorConfig(seed=self.seed + 51, paper_only=True, cycles=self.cfg.cycles, outdir=self.cfg.outdir)
        )
        self.rv50 = Phase50CrossVenueRelativeValueExecutor(
            Phase50RVConfig(seed=self.seed + 52, paper_only=True, outdir=self.cfg.outdir)
        )
        self.mm50 = Phase50ToxicityAwareOptionsMM(
            Phase50MMConfig(seed=self.seed + 53, paper_only=True, outdir=self.cfg.outdir)
        )
        self.alpha48 = Phase48RegimeConditionalOptionsEngine(
            Phase48Config(seed=self.seed + 48, paper_only=True, cycles=self.cfg.cycles, outdir=self.cfg.outdir)
        )
        self.alpha51 = Phase51AdaptiveOrderflowAlphaFusion(
            Phase51AlphaFusionConfig(seed=self.seed + 54, paper_only=True, outdir=self.cfg.outdir)
        )
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
        self.quotes: List[Dict[str, Any]] = []
        self.skew_decisions: List[Dict[str, Any]] = []
        self.inventory_snapshots: List[Dict[str, Any]] = []
        self._cycle = 0

    def _regime(self) -> str:
        try:
            rep = self.alpha48.run_campaign(cycles=15)
            reg = str(rep.get("regime", "neutral"))
        except Exception:
            reg = "neutral"
        return reg if reg in ("bullish", "bearish", "neutral", "volatile", "choppy") else "neutral"

    def _inventory(self, underlying: str, idx: int) -> float:
        h = hashlib.sha256(f"{self.seed}|inv|{underlying}|{idx}".encode()).hexdigest()
        frac = int(h[:8], 16) / 0xFFFFFFFF
        # signed inventory in [-1, 1] drifting with cycle
        drift = math.sin(idx * 0.21 + len(underlying) * 0.5)
        return max(-1.0, min(1.0, _finite((frac - 0.5) * 2.0 + drift * 0.25)))

    def _gamma_vega_proxy(self, underlying: str, tenor: str, idx: int) -> float:
        h = hashlib.sha256(f"{self.seed}|gv|{underlying}|{tenor}|{idx}".encode()).hexdigest()
        return _finite(0.5 + (int(h[:8], 16) / 0xFFFFFFFF))

    def _orderflow_shade(self, idx: int) -> float:
        try:
            rep = self.of.run_campaign(cycles=15)
            return _finite(rep.get("avg_imbalance", 0.0))
        except Exception:
            return 0.0

    def run_campaign(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.quotes = []
        self.skew_decisions = []
        self.inventory_snapshots = []
        regime = self._regime()
        of_shade = _finite(self._orderflow_shade(0))
        of_shade = max(-1.0, min(1.0, of_shade))
        ksum = self.ks.run_campaign()
        halted = bool(ksum.get("halted", False))
        hedge_rep = self.hedge49.run_campaign(cycles=15)
        vol_rep = self.volarb49.run_campaign(cycles=15)
        alloc_rep = self.alloc52.allocate(cycles=15)
        rv_rep = self.rv50.run_campaign(cycles=15)
        mm_rep = self.mm50.run_campaign(cycles=15)
        alpha_rep = self.alpha51.run_campaign(cycles=15)

        regime_mult = {
            "bullish": 1.1, "bearish": 1.1, "neutral": 1.0,
            "volatile": 1.4, "choppy": 1.25,
        }.get(regime, 1.0)

        for i in range(cycles):
            cycle_inv: Dict[str, float] = {}
            cycle_quote: List[Dict[str, Any]] = []
            for u_i, underlying in enumerate(self.cfg.underlyings):
                inv = self._inventory(underlying, i)
                cycle_inv[underlying] = float(_finite(inv))
                inv_abs = abs(inv)
                inv_cap_ratio = min(1.0, inv_abs / 0.9)
                for v_j, venue in enumerate(self.cfg.venues):
                    for t_k, tenor in enumerate(self.cfg.tenors):
                        gv = self._gamma_vega_proxy(underlying, tenor, i)
                        gamma_adj = self.cfg.gamma_skew_factor * gv * self.cfg.gamma_cap_bps / 100.0
                        inv_adj = self.cfg.inventory_skew_factor * inv * self.cfg.base_skew_bps
                        shade_adj = self.cfg.orderflow_shade_factor * of_shade * self.cfg.base_skew_bps
                        tox_widen = self.cfg.tox_widen_factor
                        # get toxicity from orderflow integrator
                        tox = max(0.0, min(1.0, _finite(self.of.run_campaign(cycles=5).get("avg_toxicity", 0.19))))
                        widen = 1.0 + tox * tox_widen
                        skew_bps = (self.cfg.base_skew_bps + inv_adj + shade_adj + gamma_adj) * regime_mult * widen
                        skew_bps = max(self.cfg.min_spread_bps, min(self.cfg.gamma_cap_bps, _finite(skew_bps)))
                        # regime tightening reduces size in volatile/choppy
                        size_mult = 1.0
                        if self.cfg.regime_tighten and regime in ("volatile", "choppy"):
                            size_mult = 0.6
                        if halted:
                            size_mult = 0.0
                        size_mult *= max(0.1, 1.0 - inv_cap_ratio * 0.5)
                        notional = self.cfg.max_position_usd * 0.05 * size_mult / max(1, len(self.cfg.venues) * len(self.cfg.tenors))
                        notional = max(0.0, _finite(notional))
                        mid = {"BTC": 105000.0, "ETH": 3400.0, "SOL": 175.0}[underlying]
                        half = skew_bps / 2.0 / 1e4
                        bid = mid * (1.0 - half)
                        ask = mid * (1.0 + half)
                        cycle_quote.append(serialize_metrics_strict({
                            "quote_id": _make_id(self.seed, "q", i * 1000 + u_i * 100 + v_j * 10 + t_k),
                            "cycle": i,
                            "underlying": underlying,
                            "venue": venue,
                            "tenor": tenor,
                            "bid": float(_finite(bid)),
                            "ask": float(_finite(ask)),
                            "mid": float(_finite(mid)),
                            "spread_bps": float(_finite(skew_bps)),
                            "inventory": float(_finite(inv)),
                            "gamma_adj_bps": float(_finite(gamma_adj * 100.0)),
                            "shade_adj_bps": float(_finite(shade_adj)),
                            "tox_widen": float(_finite(widen)),
                            "regime": regime,
                            "size_mult": float(_finite(size_mult)),
                            "notional_usd": float(_finite(notional)),
                            "kill_switch_ok": not halted,
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }))
            self.quotes.extend(cycle_quote)
            self.skew_decisions.append(serialize_metrics_strict({
                "skew_id": _make_id(self.seed, "skew", i),
                "cycle": i,
                "regime": regime,
                "regime_mult": float(_finite(regime_mult)),
                "orderflow_shade": float(_finite(of_shade)),
                "tox_widen": float(_finite(1.0 + _finite(self.of.run_campaign(cycles=5).get("avg_toxicity", 0.19)) * self.cfg.tox_widen_factor)),
                "halted": bool(halted),
                "paper_only": True,
                "timestamp": _utc_now(),
            }))
            self.inventory_snapshots.append(serialize_metrics_strict({
                "snap_id": _make_id(self.seed, "snap", i),
                "cycle": i,
                "inventory": cycle_inv,
                "max_abs_inventory": float(_finite(max((abs(v) for v in cycle_inv.values()), default=0.0))),
                "paper_only": True,
                "timestamp": _utc_now(),
            }))

        slo_evals = self.slo.evaluate_all()
        slo_alerts_fired = sum(1 for e in slo_evals if not e.get("met", True))
        gates_ok = bool(
            not halted
            and all(q["spread_bps"] >= self.cfg.min_spread_bps for q in self.quotes)
            and all(isfinite(q["bid"]) and isfinite(q["ask"]) and q["ask"] > q["bid"] for q in self.quotes)
            and all(abs(snap["max_abs_inventory"]) <= 1.0 for snap in self.inventory_snapshots)
        )
        rep = serialize_metrics_strict({
            "phase": "PHASE53_ADAPTIVE_INVENTORY_SKEW_ENGINE",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "paper_only": True,
            "cycles": cycles,
            "gates_ok": bool(gates_ok),
            "regime": regime,
            "orderflow_shade": float(_finite(of_shade)),
            "regime_mult": float(_finite(regime_mult)),
            "halted_by_kill_switch": bool(halted),
            "n_quotes": len(self.quotes),
            "n_skew_decisions": len(self.skew_decisions),
            "n_inventory_snaps": len(self.inventory_snapshots),
            "avg_spread_bps": float(_finite(sum(q["spread_bps"] for q in self.quotes) / max(1, len(self.quotes)))),
            "max_abs_inventory": float(_finite(max((s["max_abs_inventory"] for s in self.inventory_snapshots), default=0.0))),
            "slo_alerts_fired": int(slo_alerts_fired),
            "slo_evaluations": len(slo_evals),
            "sub_reports": {
                "hedge_49": {"gates_ok": hedge_rep.get("gates_ok", False)},
                "vol_arb_49": {"gates_ok": vol_rep.get("gates_ok", False)},
                "liquidity_alloc_52": {"gates_ok": alloc_rep.get("gates_ok", False)},
                "rv_50": {"gates_ok": rv_rep.get("gates_ok", False)},
                "mm_50": {"gates_ok": mm_rep.get("gates_ok", False)},
                "alpha_48": {"gates_ok": alpha_rep.get("gates_ok", False)},
                "alpha_fusion_51": {"gates_ok": alpha_rep.get("gates_ok", False)},
            },
            "integration": "Phases17-52",
            "domain_focus": "crypto_options_orderflow_adaptive_inventory_skew_gamma",
        })
        _assert_finite(rep, "phase53_inventory_skew_report")
        return rep

    def generate_artifacts(self, outdir: str = "research_state") -> Dict[str, Any]:
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        rep = self.run_campaign(cycles=self.cfg.cycles)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = out / f"PHASE53_ADAPTIVE_INVENTORY_SKEW_ENGINE_{ts}.json"
        mpath = out / f"PHASE53_ADAPTIVE_INVENTORY_SKEW_ENGINE_{ts}.md"
        with jpath.open("w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2, sort_keys=True)
        lines = [
            "# PHASE53 Adaptive Inventory Skew Engine",
            f"- Timestamp: {rep['timestamp']}",
            f"- Gates OK: {rep['gates_ok']}",
            f"- Regime: {rep['regime']}",
            f"- Orderflow Shade: {rep['orderflow_shade']}",
            f"- Regime Mult: {rep['regime_mult']}",
            f"- Kill-Switch Halted: {rep['halted_by_kill_switch']}",
            f"- Quotes: {rep['n_quotes']}",
            f"- Avg Spread BPS: {rep['avg_spread_bps']}",
            f"- Max Abs Inventory: {rep['max_abs_inventory']}",
            f"- SLO Alerts Fired: {rep['slo_alerts_fired']}",
        ]
        with mpath.open("w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        rep["json_path"] = str(jpath)
        rep["md_path"] = str(mpath)
        return rep
