"""
Phase 61: Adaptive Regime-Switching Hedge Orchestrator (crypto options + orderflow).

Adaptive regime-switching hedge orchestrator: switches among delta/vol/vega
hedge strategies by regime (normal/elevated/high_toxicity/vol_shock),
latency-aware, regime-conditional, deterministic. PAPER-ONLY. Composes Phases 59, 60.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List

from src.hedging.phase59_adaptive_cross_asset_hedge_fusion import Phase59AdaptiveCrossAssetHedgeFusion
from src.hedging.phase60_toxicity_resilient_hedge_fusion import (
    Phase60ToxicityResilientHedgeFusion,
    Phase60ToxicityResilientHedgeConfig,
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
    h = hashlib.sha256(f"{seed}|p61regime|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p61regime_{tag}_{h}"


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
class Phase61AdaptiveRegimeSwitchingHedgeConfig:
    seed: int = 61061
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 80
    regime_high_toxicity: float = 0.38
    regime_vol_shock: float = 0.04
    regime_elevated_toxicity: float = 0.24
    regime_elevated_vol_shock: float = 0.02
    max_delta_notional_usd: float = 6_000_000.0
    max_vega_notional_usd: float = 4_000_000.0
    max_gamma_notional_usd: float = 2_500_000.0
    hedge_ratio_min: float = 0.1
    hedge_ratio_max: float = 1.5
    latency_ms_cap: float = 120.0
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError("Phase61AdaptiveRegimeSwitchingHedge: paper_only must remain True (live path hard-gated)")
        if self.max_delta_notional_usd <= 0 or self.max_vega_notional_usd <= 0 or self.max_gamma_notional_usd <= 0:
            raise ValueError("hedge notionals must be > 0")


class Phase61AdaptiveRegimeSwitchingHedgeOrchestrator:
    """Adaptive regime-switching hedge orchestrator for crypto options + orderflow."""

    def __init__(self, cfg: Phase61AdaptiveRegimeSwitchingHedgeConfig | None = None) -> None:
        self.cfg = cfg or Phase61AdaptiveRegimeSwitchingHedgeConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase61AdaptiveRegimeSwitchingHedgeOrchestrator: paper_only must remain True")
        self.hedge60 = Phase60ToxicityResilientHedgeFusion(Phase60ToxicityResilientHedgeConfig(seed=self.cfg.seed + 1, paper_only=True))
        self.hedge59 = Phase59AdaptiveCrossAssetHedgeFusion()
        self.risk54 = Phase54RealtimeRiskFusionEngine()
        self.tox58 = Phase58FlowToxicityMitigator()
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.hedges: List[Dict[str, Any]] = []
        self.switches: List[Dict[str, Any]] = []
        self.regimes: List[Dict[str, Any]] = []
        self.limit_clips: List[Dict[str, Any]] = []
        self._prev_regime: str = "normal"
        self._cycle = 0

    def _regime(self, toxicity: float, vol_shock: float) -> str:
        if toxicity >= self.cfg.regime_high_toxicity or vol_shock >= self.cfg.regime_vol_shock:
            return "high_toxicity"
        if toxicity >= self.cfg.regime_elevated_toxicity or vol_shock >= self.cfg.regime_elevated_vol_shock:
            return "elevated"
        return "normal"

    def _hedge_strategy(self, regime: str, toxicity: float) -> str:
        if regime == "high_toxicity":
            return "vol_vega_dominant"
        if regime == "elevated":
            return "delta_vol_balanced"
        return "delta_dominant"

    def _hedge_ratio(self, regime: str, strategy: str, toxicity: float) -> float:
        base = {"normal": 1.0, "elevated": 1.15, "high_toxicity": 1.35}[regime]
        strat_mult = {"delta_dominant": 1.0, "delta_vol_balanced": 1.1, "vol_vega_dominant": 1.25}[strategy]
        ratio = base * strat_mult * (1.0 + min(0.3, toxicity * 0.4))
        return float(max(self.cfg.hedge_ratio_min, min(self.cfg.hedge_ratio_max, ratio)))

    def run_orchestration(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.hedges = []
        self.switches = []
        self.regimes = []
        self.limit_clips = []

        risk_rep = self.risk54.run_campaign(cycles=4)
        tox_rep = self.tox58.mitigate(cycles=4)
        of_rep = self.of.run_campaign(cycles=3)
        ks_rep = self.ks.run_campaign()
        hedge60_rep = self.hedge60.run_hedge_fusion(cycles=4)
        hedge59_rep = self.hedge59.run_hedge_fusion(cycles=4)

        halted = bool(ks_rep.get("halted", False))
        avg_tox = _finite(tox_rep.get("avg_vpin", 0.18))
        vol_shock = 0.015 + avg_tox * 0.05

        for i in range(cycles):
            underlying = self.cfg.underlyings[i % len(self.cfg.underlyings)]
            venue = self.cfg.venues[i % len(self.cfg.venues)]
            toxicity_i = max(0.0, min(1.0, avg_tox + (i % 13) * 0.018))
            vol_shock_i = min(0.06, vol_shock + (i % 7) * 0.005)
            regime = self._regime(toxicity_i, vol_shock_i)
            strategy = self._hedge_strategy(regime, toxicity_i)
            ratio = self._hedge_ratio(regime, strategy, toxicity_i)

            regime_switched = regime != self._prev_regime
            if regime_switched:
                self.switches.append(serialize_metrics_strict({
                    "switch_id": _make_id(self.cfg.seed, "sw", i),
                    "cycle": i,
                    "from_regime": self._prev_regime,
                    "to_regime": regime,
                    "from_strategy": self._hedge_strategy(self._prev_regime, toxicity_i),
                    "to_strategy": strategy,
                    "toxicity": float(_finite(toxicity_i)),
                    "vol_shock": float(_finite(vol_shock_i)),
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))
                self._prev_regime = regime

            delta_notional = 1_500_000.0 * (1.0 + (i % 17) * 0.08)
            vega_notional = 900_000.0 * (1.0 + (i % 11) * 0.1)
            gamma_notional = 500_000.0 * (1.0 + (i % 9) * 0.12)
            mult = ratio if not halted else 0.0
            delta_target = delta_notional * mult
            vega_target = vega_notional * mult
            gamma_target = gamma_notional * mult

            delta_clip = min(delta_target, self.cfg.max_delta_notional_usd)
            vega_clip = min(vega_target, self.cfg.max_vega_notional_usd)
            gamma_clip = min(gamma_target, self.cfg.max_gamma_notional_usd)

            if halted:
                self.limit_clips.append(serialize_metrics_strict({
                    "clip_id": _make_id(self.cfg.seed, "halt", i),
                    "cycle": i,
                    "underlying": underlying,
                    "venue": venue,
                    "action": "halt_all_hedges",
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))
            if delta_clip < delta_target and mult > 0:
                self.limit_clips.append(serialize_metrics_strict({
                    "clip_id": _make_id(self.cfg.seed, "delta", i),
                    "cycle": i,
                    "underlying": underlying,
                    "venue": venue,
                    "action": "clip_delta_notional",
                    "requested": float(_finite(delta_target)),
                    "applied": float(_finite(delta_clip)),
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))
            if vega_clip < vega_target and mult > 0:
                self.limit_clips.append(serialize_metrics_strict({
                    "clip_id": _make_id(self.cfg.seed, "vega", i),
                    "cycle": i,
                    "underlying": underlying,
                    "venue": venue,
                    "action": "clip_vega_notional",
                    "requested": float(_finite(vega_target)),
                    "applied": float(_finite(vega_clip)),
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))
            if gamma_clip < gamma_target and mult > 0:
                self.limit_clips.append(serialize_metrics_strict({
                    "clip_id": _make_id(self.cfg.seed, "gamma", i),
                    "cycle": i,
                    "underlying": underlying,
                    "venue": venue,
                    "action": "clip_gamma_notional",
                    "requested": float(_finite(gamma_target)),
                    "applied": float(_finite(gamma_clip)),
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))

            self.hedges.append(serialize_metrics_strict({
                "hedge_id": _make_id(self.cfg.seed, "hedge", i),
                "cycle": i,
                "underlying": underlying,
                "venue": venue,
                "regime": regime,
                "strategy": strategy,
                "toxicity": float(_finite(toxicity_i)),
                "vol_shock": float(_finite(vol_shock_i)),
                "hedge_ratio": float(_finite(ratio)),
                "delta_notional_usd": float(_finite(delta_clip)),
                "vega_notional_usd": float(_finite(vega_clip)),
                "gamma_notional_usd": float(_finite(gamma_clip)),
                "paper_only": True,
                "timestamp": _utc_now(),
            }))
            self.regimes.append(serialize_metrics_strict({
                "regime_id": _make_id(self.cfg.seed, "regime", i),
                "cycle": i,
                "underlying": underlying,
                "regime": regime,
                "strategy": strategy,
                "toxicity": float(_finite(toxicity_i)),
                "vol_shock": float(_finite(vol_shock_i)),
                "hedge_ratio": float(_finite(ratio)),
                "paper_only": True,
                "timestamp": _utc_now(),
            }))

        n_hedges = len(self.hedges)
        n_switches = len(self.switches)
        gates_ok = bool(
            (not halted)
            and all(
                self.cfg.hedge_ratio_min <= h["hedge_ratio"] <= self.cfg.hedge_ratio_max
                and h["delta_notional_usd"] <= self.cfg.max_delta_notional_usd
                and h["vega_notional_usd"] <= self.cfg.max_vega_notional_usd
                and h["gamma_notional_usd"] <= self.cfg.max_gamma_notional_usd
                for h in self.hedges
            )
        )
        rep = serialize_metrics_strict({
            "phase": "PHASE61_ADAPTIVE_REGIME_SWITCHING_HEDGE_ORCHESTRATOR",
            "timestamp": _utc_now(),
            "seed": self.cfg.seed,
            "paper_only": True,
            "cycles": cycles,
            "gates_ok": bool(gates_ok),
            "halted": bool(halted),
            "avg_toxicity": float(_finite(avg_tox)),
            "avg_vol_shock": float(_finite(vol_shock)),
            "n_hedges": int(n_hedges),
            "n_switches": int(n_switches),
            "n_limit_clips": len(self.limit_clips),
            "n_regime_high": sum(1 for r in self.regimes if r["regime"] == "high_toxicity"),
            "n_regime_elevated": sum(1 for r in self.regimes if r["regime"] == "elevated"),
            "n_regime_normal": sum(1 for r in self.regimes if r["regime"] == "normal"),
            "strategy_vol_vega": sum(1 for h in self.hedges if h["strategy"] == "vol_vega_dominant"),
            "strategy_delta_vol": sum(1 for h in self.hedges if h["strategy"] == "delta_vol_balanced"),
            "strategy_delta": sum(1 for h in self.hedges if h["strategy"] == "delta_dominant"),
            "hedge60_ok": bool(hedge60_rep.get("gates_ok", False)),
            "hedge59_ok": bool(hedge59_rep.get("gates_ok", False)),
            "risk54_ok": bool(risk_rep.get("gates_ok", False)),
            "tox58_ok": bool(tox_rep.get("gates_ok", False)),
            "composed_phases": "17-60",
        })
        _assert_finite(rep, "phase61_regime_switching_hedge_report")
        return rep

    def generate_artifacts(self, outdir: str = "research_state") -> Dict[str, Any]:
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        rep = self.run_orchestration(cycles=self.cfg.cycles)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = out / f"PHASE61_ADAPTIVE_REGIME_SWITCHING_HEDGE_{ts}.json"
        mpath = out / f"PHASE61_ADAPTIVE_REGIME_SWITCHING_HEDGE_{ts}.md"
        with jpath.open("w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2, sort_keys=True)
        with mpath.open("w", encoding="utf-8") as f:
            f.write(
                f"# PHASE61 Adaptive Regime-Switching Hedge Orchestrator\n\n"
                f"- Timestamp: {rep['timestamp']}\n"
                f"- Gates OK: {rep['gates_ok']}\n"
                f"- Paper Only: {rep['paper_only']}\n"
                f"- Cycles: {rep['cycles']}\n"
                f"- Halted: {rep['halted']}\n"
                f"- Hedges: {rep['n_hedges']} | Switches: {rep['n_switches']} | Limit Clips: {rep['n_limit_clips']}\n"
                f"- Regime High: {rep['n_regime_high']} | Elevated: {rep['n_regime_elevated']} | Normal: {rep['n_regime_normal']}\n"
                f"- Strategy Vol/Vega: {rep['strategy_vol_vega']} | Delta/Vol: {rep['strategy_delta_vol']} | Delta: {rep['strategy_delta']}\n"
                f"- Avg Toxicity: {rep['avg_toxicity']:.4f} | Avg Vol Shock: {rep['avg_vol_shock']:.5f}\n"
                f"- Composed: {rep['composed_phases']}\n"
            )
        rep["json_path"] = str(jpath)
        rep["md_path"] = str(mpath)
        return rep
