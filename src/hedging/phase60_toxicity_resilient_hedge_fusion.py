"""
Phase 60: Real-Time Toxicity-Resilient Hedge Fusion (crypto options + orderflow).

Real-time toxicity-resilient hedge fusion: adaptive delta-vol-vega hedge ratios
conditioned on orderflow toxicity, regime, latency and venue liquidity. PAPER-ONLY.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List

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
    h = hashlib.sha256(f"{seed}|p60toxhedge|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p60toxhedge_{tag}_{h}"


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
class Phase60ToxicityResilientHedgeConfig:
    seed: int = 60061
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 80
    toxicity_resilience_mult: float = 1.4
    regime_high_toxicity: float = 0.38
    max_delta_notional_usd: float = 6_000_000.0
    max_vega_notional_usd: float = 4_000_000.0
    max_gamma_notional_usd: float = 2_500_000.0
    hedge_ratio_min: float = 0.1
    hedge_ratio_max: float = 1.5
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError("Phase60ToxicityResilientHedge: paper_only must remain True (live path hard-gated)")
        if self.max_delta_notional_usd <= 0 or self.max_vega_notional_usd <= 0 or self.max_gamma_notional_usd <= 0:
            raise ValueError("hedge notionals must be > 0")


class Phase60ToxicityResilientHedgeFusion:
    """Real-time toxicity-resilient hedge fusion for crypto options + orderflow."""

    def __init__(self, cfg: Phase60ToxicityResilientHedgeConfig | None = None) -> None:
        self.cfg = cfg or Phase60ToxicityResilientHedgeConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase60ToxicityResilientHedgeFusion: paper_only must remain True")
        self.risk54 = Phase54RealtimeRiskFusionEngine()
        self.tox58 = Phase58FlowToxicityMitigator()
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.hedges: List[Dict[str, Any]] = []
        self.adjustments: List[Dict[str, Any]] = []
        self.regimes: List[Dict[str, Any]] = []
        self.limit_clips: List[Dict[str, Any]] = []
        self._cycle = 0

    def _regime(self, toxicity: float, vol_shock: float) -> str:
        if toxicity >= self.cfg.regime_high_toxicity or vol_shock >= 0.04:
            return "high_toxicity"
        if toxicity >= 0.24 or vol_shock >= 0.02:
            return "elevated"
        return "normal"

    def _hedge_ratio(self, regime: str, toxicity: float) -> float:
        base = {"normal": 1.0, "elevated": 1.15, "high_toxicity": 1.35}[regime]
        ratio = base * (1.0 + min(0.3, toxicity * 0.4)) * self.cfg.toxicity_resilience_mult
        return float(max(self.cfg.hedge_ratio_min, min(self.cfg.hedge_ratio_max, ratio)))

    def run_hedge_fusion(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.hedges = []
        self.adjustments = []
        self.regimes = []
        self.limit_clips = []
        risk_rep = self.risk54.run_campaign(cycles=40)
        tox_rep = self.tox58.mitigate(cycles=40)
        of_rep = self.of.run_campaign(cycles=30)
        ks_rep = self.ks.run_campaign()
        halted = bool(ks_rep.get("halted", False))
        avg_tox = _finite(tox_rep.get("avg_vpin", 0.18))
        vol_shock = 0.015 + avg_tox * 0.05

        for i in range(cycles):
            underlying = self.cfg.underlyings[i % len(self.cfg.underlyings)]
            venue = self.cfg.venues[i % len(self.cfg.venues)]
            toxicity_i = max(0.0, min(1.0, avg_tox + (i % 13) * 0.018))
            vol_shock_i = min(0.06, vol_shock + (i % 7) * 0.005)
            regime = self._regime(toxicity_i, vol_shock_i)
            ratio = self._hedge_ratio(regime, toxicity_i)
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
                "toxicity": float(_finite(toxicity_i)),
                "vol_shock": float(_finite(vol_shock_i)),
                "hedge_ratio": float(_finite(ratio)),
                "paper_only": True,
                "timestamp": _utc_now(),
            }))
            if ratio != 1.0 and not halted:
                self.adjustments.append(serialize_metrics_strict({
                    "adj_id": _make_id(self.cfg.seed, "adj", i),
                    "cycle": i,
                    "underlying": underlying,
                    "regime": regime,
                    "from_ratio": 1.0,
                    "to_ratio": float(_finite(ratio)),
                    "toxicity": float(_finite(toxicity_i)),
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))

        n_hedges = len(self.hedges)
        gates_ok = bool((not halted) and all(
            h["delta_notional_usd"] <= self.cfg.max_delta_notional_usd
            and h["vega_notional_usd"] <= self.cfg.max_vega_notional_usd
            and h["gamma_notional_usd"] <= self.cfg.max_gamma_notional_usd
            and self.cfg.hedge_ratio_min <= h["hedge_ratio"] <= self.cfg.hedge_ratio_max
            for h in self.hedges
        ))
        rep = serialize_metrics_strict({
            "phase": "PHASE60_TOXICITY_RESILIENT_HEDGE_FUSION",
            "timestamp": _utc_now(),
            "seed": self.cfg.seed,
            "paper_only": True,
            "cycles": cycles,
            "gates_ok": bool(gates_ok),
            "halted": bool(halted),
            "avg_toxicity": float(_finite(avg_tox)),
            "avg_vol_shock": float(_finite(vol_shock)),
            "n_hedges": int(n_hedges),
            "n_adjustments": len(self.adjustments),
            "n_limit_clips": len(self.limit_clips),
            "n_regime_high": sum(1 for r in self.regimes if r["regime"] == "high_toxicity"),
            "risk54_ok": bool(risk_rep.get("gates_ok", False)),
            "tox58_ok": bool(tox_rep.get("gates_ok", False)),
            "composed_phases": "17-59",
        })
        _assert_finite(rep, "phase60_tox_resilient_hedge_report")
        return rep

    def generate_artifacts(self, outdir: str = "research_state") -> Dict[str, Any]:
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        rep = self.run_hedge_fusion(cycles=self.cfg.cycles)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = out / f"PHASE60_TOXICITY_RESILIENT_HEDGE_FUSION_{ts}.json"
        mpath = out / f"PHASE60_TOXICITY_RESILIENT_HEDGE_FUSION_{ts}.md"
        with jpath.open("w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2, sort_keys=True)
        with mpath.open("w", encoding="utf-8") as f:
            f.write(
                f"# PHASE60 Toxicity-Resilient Hedge Fusion\n\n"
                f"- Timestamp: {rep['timestamp']}\n"
                f"- Gates OK: {rep['gates_ok']}\n"
                f"- Halted: {rep['halted']}\n"
                f"- Avg Toxicity: {rep['avg_toxicity']:.4f} | Avg Vol Shock: {rep['avg_vol_shock']:.5f}\n"
                f"- Hedges: {rep['n_hedges']} | Adjustments: {rep['n_adjustments']} | Limit Clips: {rep['n_limit_clips']}\n"
                f"- High-Tox Regimes: {rep['n_regime_high']}\n"
                f"- Composed: {rep['composed_phases']}\n"
            )
        rep["json_path"] = str(jpath)
        rep["md_path"] = str(mpath)
        return rep
