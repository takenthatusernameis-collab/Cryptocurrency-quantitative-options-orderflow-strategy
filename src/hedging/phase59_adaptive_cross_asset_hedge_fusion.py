"""
Phase 59: Adaptive Cross-Asset Hedge Fusion (crypto options + orderflow).

Adaptive cross-asset/options delta-vol-vega hedge fusion, latency-aware,
regime-conditional, deterministic. PAPER-ONLY, finite numerics.
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
    h = hashlib.sha256(f"{seed}|p59hedgef|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p59hedgef_{tag}_{h}"


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
class Phase59AdaptiveCrossAssetHedgeConfig:
    seed: int = 59060
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 80
    latency_fee_bps: float = 0.15
    toxicity_hedge_mult: float = 1.25
    regime_high_toxicity: float = 0.35
    max_delta_notional_usd: float = 5_000_000.0
    max_vega_notional_usd: float = 3_000_000.0
    max_gamma_notional_usd: float = 2_000_000.0
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError("Phase59AdaptiveCrossAssetHedgeFusion: paper_only must remain True (live path hard-gated)")
        if self.max_delta_notional_usd <= 0 or self.max_vega_notional_usd <= 0 or self.max_gamma_notional_usd <= 0:
            raise ValueError("hedge notionals must be > 0")


class Phase59AdaptiveCrossAssetHedgeFusion:
    """Adaptive cross-asset/options delta-vol-vega hedge fusion for crypto options + orderflow."""

    def __init__(self, cfg: Phase59AdaptiveCrossAssetHedgeConfig | None = None) -> None:
        self.cfg = cfg or Phase59AdaptiveCrossAssetHedgeConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase59AdaptiveCrossAssetHedgeFusion: paper_only must remain True")
        self.risk54 = Phase54RealtimeRiskFusionEngine()
        self.tox58 = Phase58FlowToxicityMitigator()
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.hedges: List[Dict[str, Any]] = []
        self.regimes: List[Dict[str, Any]] = []
        self.limit_clips: List[Dict[str, Any]] = []
        self._cycle = 0

    def _regime(self, toxicity: float, latency_ms: float) -> str:
        if toxicity >= self.cfg.regime_high_toxicity or latency_ms > 100.0:
            return "high_toxicity"
        if toxicity >= 0.22 or latency_ms > 50.0:
            return "elevated"
        return "normal"

    def run_hedge_fusion(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.hedges = []
        self.regimes = []
        self.limit_clips = []
        risk_rep = self.risk54.run_campaign(cycles=4)
        tox_rep = self.tox58.mitigate(cycles=4)
        of_rep = self.of.run_campaign(cycles=3)
        ks_rep = self.ks.run_campaign()
        halted = bool(ks_rep.get("halted", False))
        avg_tox = _finite(tox_rep.get("avg_vpin", 0.2))
        avg_latency = 8.0 + (avg_tox * 40.0)

        for i in range(cycles):
            underlying = self.cfg.underlyings[i % len(self.cfg.underlyings)]
            venue = self.cfg.venues[i % len(self.cfg.venues)]
            toxicity_i = max(0.0, min(1.0, avg_tox + (i % 13) * 0.02))
            latency_ms = avg_latency + (i % 5) * 6.0 + toxicity_i * 10.0
            regime = self._regime(toxicity_i, latency_ms)
            delta_notional = 1_200_000.0 * (1.0 + (i % 15) * 0.1)
            vega_notional = 700_000.0 * (1.0 + (i % 9) * 0.12)
            gamma_notional = 400_000.0 * (1.0 + (i % 7) * 0.15)
            mult = self.cfg.toxicity_hedge_mult if regime == "high_toxicity" else 1.0
            if halted:
                mult = 0.0
            delta_clip = min(delta_notional * mult, self.cfg.max_delta_notional_usd)
            vega_clip = min(vega_notional * mult, self.cfg.max_vega_notional_usd)
            gamma_clip = min(gamma_notional * mult, self.cfg.max_gamma_notional_usd)
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
            if delta_clip < delta_notional * mult and mult > 0:
                self.limit_clips.append(serialize_metrics_strict({
                    "clip_id": _make_id(self.cfg.seed, "delta", i),
                    "cycle": i,
                    "underlying": underlying,
                    "venue": venue,
                    "action": "clip_delta_notional",
                    "requested": float(_finite(delta_notional * mult)),
                    "applied": float(_finite(delta_clip)),
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))
            if vega_clip < vega_notional * mult and mult > 0:
                self.limit_clips.append(serialize_metrics_strict({
                    "clip_id": _make_id(self.cfg.seed, "vega", i),
                    "cycle": i,
                    "underlying": underlying,
                    "venue": venue,
                    "action": "clip_vega_notional",
                    "requested": float(_finite(vega_notional * mult)),
                    "applied": float(_finite(vega_clip)),
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))
            if gamma_clip < gamma_notional * mult and mult > 0:
                self.limit_clips.append(serialize_metrics_strict({
                    "clip_id": _make_id(self.cfg.seed, "gamma", i),
                    "cycle": i,
                    "underlying": underlying,
                    "venue": venue,
                    "action": "clip_gamma_notional",
                    "requested": float(_finite(gamma_notional * mult)),
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
                "latency_ms": float(_finite(latency_ms)),
                "toxicity": float(_finite(toxicity_i)),
                "delta_notional_usd": float(_finite(delta_clip)),
                "vega_notional_usd": float(_finite(vega_clip)),
                "gamma_notional_usd": float(_finite(gamma_clip)),
                "hedge_mult": float(_finite(mult)),
                "paper_only": True,
                "timestamp": _utc_now(),
            }))
            self.regimes.append(serialize_metrics_strict({
                "regime_id": _make_id(self.cfg.seed, "regime", i),
                "cycle": i,
                "underlying": underlying,
                "regime": regime,
                "toxicity": float(_finite(toxicity_i)),
                "latency_ms": float(_finite(latency_ms)),
                "paper_only": True,
                "timestamp": _utc_now(),
            }))

        n_hedges = len(self.hedges)
        gates_ok = bool((not halted) and all(
            h["delta_notional_usd"] <= self.cfg.max_delta_notional_usd
            and h["vega_notional_usd"] <= self.cfg.max_vega_notional_usd
            and h["gamma_notional_usd"] <= self.cfg.max_gamma_notional_usd
            for h in self.hedges
        ))
        rep = serialize_metrics_strict({
            "phase": "PHASE59_ADAPTIVE_CROSS_ASSET_HEDGE_FUSION",
            "timestamp": _utc_now(),
            "seed": self.cfg.seed,
            "paper_only": True,
            "cycles": cycles,
            "gates_ok": bool(gates_ok),
            "halted": bool(halted),
            "avg_toxicity": float(_finite(avg_tox)),
            "avg_latency_ms": float(_finite(avg_latency)),
            "n_hedges": int(n_hedges),
            "n_limit_clips": len(self.limit_clips),
            "n_regime_high": sum(1 for r in self.regimes if r["regime"] == "high_toxicity"),
            "risk54_ok": bool(risk_rep.get("gates_ok", False)),
            "tox58_ok": bool(tox_rep.get("gates_ok", False)),
            "composed_phases": "17-58",
        })
        _assert_finite(rep, "phase59_hedge_fusion_report")
        return rep

    def generate_artifacts(self, outdir: str = "research_state") -> Dict[str, Any]:
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        rep = self.run_hedge_fusion(cycles=self.cfg.cycles)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = out / f"PHASE59_ADAPTIVE_CROSS_ASSET_HEDGE_FUSION_{ts}.json"
        mpath = out / f"PHASE59_ADAPTIVE_CROSS_ASSET_HEDGE_FUSION_{ts}.md"
        with jpath.open("w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2, sort_keys=True)
        with mpath.open("w", encoding="utf-8") as f:
            f.write(
                f"# PHASE59 Adaptive Cross-Asset Hedge Fusion\n\n"
                f"- Timestamp: {rep['timestamp']}\n"
                f"- Gates OK: {rep['gates_ok']}\n"
                f"- Halted: {rep['halted']}\n"
                f"- Avg Toxicity: {rep['avg_toxicity']:.4f}\n"
                f"- Avg Latency (ms): {rep['avg_latency_ms']:.2f}\n"
                f"- Hedges: {rep['n_hedges']} | Limit Clips: {rep['n_limit_clips']} | High-Tox Regimes: {rep['n_regime_high']}\n"
                f"- Composed: {rep['composed_phases']}\n"
            )
        rep["json_path"] = str(jpath)
        rep["md_path"] = str(mpath)
        return rep
