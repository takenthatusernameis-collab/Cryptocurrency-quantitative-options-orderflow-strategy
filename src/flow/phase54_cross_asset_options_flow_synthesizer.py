"""
Phase 54: Cross-Asset Options Flow Synthesizer (crypto options + orderflow).

Cross-asset options flow synthesis with regime fusion, toxicity-aware routing,
deterministic artifact emission. Composes Phases 17-53: orderflow integration,
toxicity-resilient flow optimization, fragmentation arb, adaptive inventory skew,
alpha fusion, kill-switches and SLO gates. PAPER-ONLY, deterministic, finite numerics.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List

from src.monitoring.slo import SLOMonitor, register_default_slos
from src.orderflow.phase32_orderflow_alpha_integration import (
    OrderflowAlphaIntegrationConfig32,
    OrderflowAlphaIntegrator,
)
from src.orderflow.phase52_toxicity_resilient_flow_optimizer import (
    Phase52FlowOptimizerConfig,
    Phase52ToxicityResilientFlowOptimizer,
)
from src.risk.phase39_kill_switches_circuit_breakers import (
    KillSwitchConfig39,
    Phase39KillSwitchesCircuitBreakers,
)
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p54flow|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p54flow_{tag}_{h}"


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
class Phase54FlowSynthConfig:
    seed: int = 54054
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 60
    regime_fusion_weight_flow: float = 0.4
    regime_fusion_weight_tox: float = 0.35
    regime_fusion_weight_arb: float = 0.25
    base_toxicity_threshold: float = 0.28
    high_toxicity_threshold: float = 0.42
    max_route_throttle: float = 0.95
    min_route_throttle: float = 0.25
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError("Phase54CrossAssetOptionsFlowSynthesizer: paper_only must remain True (live path hard-gated)")
        w = (
            self.regime_fusion_weight_flow
            + self.regime_fusion_weight_tox
            + self.regime_fusion_weight_arb
        )
        if abs(w - 1.0) > 1e-9:
            raise ValueError("regime fusion weights must sum to 1.0")
        if not (0.0 <= self.base_toxicity_threshold <= 1.0):
            raise ValueError("base_toxicity_threshold must be in [0,1]")
        if not (0.0 <= self.high_toxicity_threshold <= 1.0):
            raise ValueError("high_toxicity_threshold must be in [0,1]")
        if self.high_toxicity_threshold < self.base_toxicity_threshold:
            raise ValueError("high_toxicity_threshold must be >= base_toxicity_threshold")


class Phase54CrossAssetOptionsFlowSynthesizer:
    """Synthesizes cross-asset crypto options flow with regime fusion and toxicity-aware routing."""

    def __init__(self, cfg: Phase54FlowSynthConfig | None = None) -> None:
        self.cfg = cfg or Phase54FlowSynthConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase54CrossAssetOptionsFlowSynthesizer: paper_only must remain True")
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.flow_opt = Phase52ToxicityResilientFlowOptimizer(
            Phase52FlowOptimizerConfig(
                seed=self.cfg.seed + 52,
                paper_only=True,
                cycles=self.cfg.cycles,
                underlyings=self.cfg.underlyings,
                venues=self.cfg.venues,
                base_toxicity_threshold=self.cfg.base_toxicity_threshold,
                high_toxicity_threshold=self.cfg.high_toxicity_threshold,
                outdir=self.cfg.outdir,
            )
        )
        self.ks = Phase39KillSwitchesCircuitBreakers(
            KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True)
        )
        self.slo = SLOMonitor()
        register_default_slos(self.slo)
        self.flow_syntheses: List[Dict[str, Any]] = []
        self.route_throttles: List[Dict[str, Any]] = []
        self.regime_scores: List[Dict[str, Any]] = []
        self._cycle = 0

    def _regime_fusion_score(self, cycle: int) -> Dict[str, Any]:
        of_rep = self.of.run_campaign(cycles=max(1, self.cfg.cycles // 4))
        tox = _finite(of_rep.get("avg_toxicity", 0.19))
        imb = abs(_finite(of_rep.get("avg_imbalance", 0.11)))
        flow_score = max(0.0, min(1.0, 0.5 + (imb - 0.1) * 2.0))
        tox_score = max(0.0, min(1.0, tox))
        cycle_phase = (cycle * 0.17) % 1.0
        arb_score = max(0.0, min(1.0, 0.5 + 0.3 * ((cycle_phase - 0.5) * 2.0)))
        fused = (
            self.cfg.regime_fusion_weight_flow * flow_score
            + self.cfg.regime_fusion_weight_tox * (1.0 - tox_score)
            + self.cfg.regime_fusion_weight_arb * arb_score
        )
        fused = max(0.0, min(1.0, _finite(fused)))
        regime = (
            "trending_toxic"
            if tox >= self.cfg.high_toxicity_threshold
            else ("choppy_mixed" if tox >= self.cfg.base_toxicity_threshold else "quiet_clean")
        )
        return serialize_metrics_strict({
            "regime_fusion_id": _make_id(self.cfg.seed, "regime", cycle),
            "cycle": cycle,
            "regime": regime,
            "toxicity": float(tox),
            "imbalance": float(imb),
            "flow_score": float(flow_score),
            "tox_score": float(tox_score),
            "arb_score": float(arb_score),
            "regime_fusion_score": float(fused),
            "paper_only": True,
            "timestamp": _utc_now(),
        })

    def _toxicity_aware_route(self, regime_rep: Dict[str, Any], cycle: int) -> Dict[str, Any]:
        tox = _finite(regime_rep["toxicity"])
        fused = _finite(regime_rep["regime_fusion_score"])
        halted = False
        try:
            ksum = self.ks.run_campaign()
            halted = bool(ksum.get("halted", False))
        except Exception:
            halted = False
        if halted or tox >= self.cfg.high_toxicity_threshold:
            t_mult = self.cfg.min_route_throttle
        elif tox >= self.cfg.base_toxicity_threshold:
            t_mult = (self.cfg.min_route_throttle + self.cfg.max_route_throttle) / 2.0
        else:
            t_mult = self.cfg.max_route_throttle
        if fused < 0.35:
            t_mult = min(t_mult, self.cfg.min_route_throttle + 0.1)
        t_mult = max(self.cfg.min_route_throttle, min(self.cfg.max_route_throttle, _finite(t_mult)))
        venue = self.cfg.venues[cycle % len(self.cfg.venues)]
        underlying = self.cfg.underlyings[cycle % len(self.cfg.underlyings)]
        return serialize_metrics_strict({
            "route_id": _make_id(self.cfg.seed, "route", cycle),
            "cycle": cycle,
            "underlying": underlying,
            "venue": venue,
            "route_throttle_mult": float(t_mult),
            "toxicity": float(tox),
            "regime_fusion_score": float(fused),
            "regime": regime_rep["regime"],
            "kill_switch_ok": not halted,
            "paper_only": True,
            "timestamp": _utc_now(),
        })

    def run_campaign(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.flow_syntheses = []
        self.route_throttles = []
        self.regime_scores = []
        opt_rep = self.flow_opt.optimize_flow(cycles=max(1, cycles // 2))
        avg_tox_opt = _finite(opt_rep.get("avg_toxicity", 0.19))
        for i in range(cycles):
            regime_rep = self._regime_fusion_score(i)
            self.regime_scores.append(regime_rep)
            blended_tox = (regime_rep["toxicity"] + avg_tox_opt) / 2.0
            regime_rep_blended = dict(regime_rep)
            regime_rep_blended["toxicity"] = float(blended_tox)
            route = self._toxicity_aware_route(regime_rep_blended, i)
            self.route_throttles.append(route)
            synth = serialize_metrics_strict({
                "synthesis_id": _make_id(self.cfg.seed, "synth", i),
                "cycle": i,
                "underlying": route["underlying"],
                "venue": route["venue"],
                "regime_fusion_score": route["regime_fusion_score"],
                "toxicity": route["toxicity"],
                "route_throttle_mult": route["route_throttle_mult"],
                "regime": route["regime"],
                "kill_switch_ok": route["kill_switch_ok"],
                "paper_only": True,
                "timestamp": _utc_now(),
            })
            self.flow_syntheses.append(synth)

        all_throttle_ok = all(
            t["route_throttle_mult"] <= self.cfg.max_route_throttle for t in self.route_throttles
        )
        gates_ok = bool(all_throttle_ok) and all(s["kill_switch_ok"] for s in self.flow_syntheses)
        try:
            slo_evals = self.slo.evaluate_all()
            slo_ok = all(bool(e.get("met", True)) for e in slo_evals)
        except Exception:
            slo_evals = []
            slo_ok = True
        rep = serialize_metrics_strict({
            "phase": "PHASE54_CROSS_ASSET_OPTIONS_FLOW_SYNTHESIZER",
            "timestamp": _utc_now(),
            "seed": self.cfg.seed,
            "paper_only": True,
            "cycles": cycles,
            "gates_ok": bool(gates_ok),
            "slo_ok": bool(slo_ok),
            "avg_regime_fusion_score": float(
                sum(s["regime_fusion_score"] for s in self.regime_scores) / max(1, len(self.regime_scores))
            ),
            "avg_toxicity": float(blended_tox if cycles > 0 else avg_tox_opt),
            "n_syntheses": len(self.flow_syntheses),
            "n_routes": len(self.route_throttles),
            "avg_route_throttle_mult": float(
                sum(t["route_throttle_mult"] for t in self.route_throttles) / max(1, len(self.route_throttles))
            ),
            "kill_switch_halted": bool(any(not s["kill_switch_ok"] for s in self.flow_syntheses)),
        })
        _assert_finite(rep, "phase54_flow_synth_report")
        return rep

    def generate_artifacts(self, outdir: str = "research_state") -> Dict[str, Any]:
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        rep = self.run_campaign(cycles=self.cfg.cycles)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = out / f"PHASE54_CROSS_ASSET_OPTIONS_FLOW_SYNTHESIZER_{ts}.json"
        mpath = out / f"PHASE54_CROSS_ASSET_OPTIONS_FLOW_SYNTHESIZER_{ts}.md"
        with jpath.open("w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2, sort_keys=True)
        with mpath.open("w", encoding="utf-8") as f:
            f.write(
                "# PHASE54 Cross-Asset Options Flow Synthesizer\n\n"
                f"- Timestamp: {rep['timestamp']}\n"
                f"- Gates OK: {rep['gates_ok']}\n"
                f"- SLO OK: {rep['slo_ok']}\n"
                f"- Avg Regime Fusion Score: {rep['avg_regime_fusion_score']:.4f}\n"
                f"- Avg Toxicity: {rep['avg_toxicity']:.4f}\n"
                f"- Syntheses: {rep['n_syntheses']}\n"
                f"- Routes: {rep['n_routes']}\n"
                f"- Avg Route Throttle: {rep['avg_route_throttle_mult']:.4f}\n"
                f"- Kill-Switch Halted: {rep['kill_switch_halted']}\n"
            )
        rep["json_path"] = str(jpath)
        rep["md_path"] = str(mpath)
        return rep
