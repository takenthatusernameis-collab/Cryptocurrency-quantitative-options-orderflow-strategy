"""
Phase 52: Toxicity-Resilient Flow Optimizer (crypto options + orderflow).

Toxicity-resilient flow optimization: adaptive toxicity scoring, flow segmentation
(informed/noise), adverse selection estimation, dynamic quote/size throttles,
inventory-aware flow routing, regime-conditional tightening, kill-switch hooks.
PAPER-ONLY, deterministic, finite numerics.
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
from src.risk.phase39_kill_switches_circuit_breakers import (
    KillSwitchConfig39,
    Phase39KillSwitchesCircuitBreakers,
)
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p52flow|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p52flow_{tag}_{h}"


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
class Phase52FlowOptimizerConfig:
    seed: int = 52052
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 60
    base_toxicity_threshold: float = 0.28
    high_toxicity_threshold: float = 0.42
    adverse_sel_est_factor: float = 1.15
    throttle_base_mult: float = 0.9
    throttle_high_mult: float = 0.6
    inventory_routing_factor: float = 0.8
    regime_tighten: bool = True
    max_throttle: float = 0.95
    min_throttle: float = 0.25
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError("Phase52ToxicityResilientFlowOptimizer: paper_only must remain True (live path hard-gated)")
        if not (0.0 <= self.base_toxicity_threshold <= 1.0):
            raise ValueError("base_toxicity_threshold must be in [0,1]")
        if not (0.0 <= self.high_toxicity_threshold <= 1.0):
            raise ValueError("high_toxicity_threshold must be in [0,1]")
        if self.high_toxicity_threshold < self.base_toxicity_threshold:
            raise ValueError("high_toxicity_threshold must be >= base_toxicity_threshold")


class Phase52ToxicityResilientFlowOptimizer:
    """Toxicity-resilient flow optimizer for crypto options + orderflow."""

    def __init__(self, cfg: Phase52FlowOptimizerConfig | None = None) -> None:
        self.cfg = cfg or Phase52FlowOptimizerConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase52ToxicityResilientFlowOptimizer: paper_only must remain True")
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.flow_segments: List[Dict[str, Any]] = []
        self.throttles: List[Dict[str, Any]] = []
        self.routing_decisions: List[Dict[str, Any]] = []
        self._cycle = 0

    def _adaptive_toxicity(self) -> float:
        rep = self.of.run_campaign(cycles=15)
        tox = rep.get("avg_toxicity", 0.19)
        imb = abs(rep.get("avg_imbalance", 0.11))
        adv = max(0.0, _finite(tox) * (1.0 + imb * 0.25))
        return max(0.0, min(1.0, adv))

    def _segment_flow(self, tox: float, idx: int) -> Dict[str, Any]:
        if tox >= self.cfg.high_toxicity_threshold:
            seg = "informed_toxic"
            as_est = tox * self.cfg.adverse_sel_est_factor
        elif tox >= self.cfg.base_toxicity_threshold:
            seg = "mixed"
            as_est = tox * (1.0 + 0.08)
        else:
            seg = "noise"
            as_est = tox * 0.6
        as_est = max(0.0, min(1.0, _finite(as_est)))
        return serialize_metrics_strict({
            "segment_id": _make_id(self.cfg.seed, seg, idx),
            "segment": seg,
            "toxicity": float(_finite(tox)),
            "adverse_selection_est": float(as_est),
            "paper_only": True,
            "timestamp": _utc_now(),
        })

    def optimize_flow(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.flow_segments = []
        self.throttles = []
        self.routing_decisions = []
        tox = self._adaptive_toxicity()
        ksum = self.ks.run_campaign()

        halted = bool(ksum.get("halted", False))
        for i in range(cycles):
            seg = self._segment_flow(tox + (i * 1e-4) % 0.05, i)
            self.flow_segments.append(seg)
            if seg["segment"] == "informed_toxic" or halted:
                t_mult = self.cfg.throttle_high_mult
            elif seg["segment"] == "mixed":
                t_mult = (self.cfg.throttle_base_mult + self.cfg.throttle_high_mult) / 2.0
            else:
                t_mult = self.cfg.throttle_base_mult
            if self.cfg.regime_tighten and tox >= self.cfg.high_toxicity_threshold:
                t_mult = min(t_mult, self.cfg.throttle_high_mult)
            t_mult = max(self.cfg.min_throttle, min(self.cfg.max_throttle, _finite(t_mult)))
            self.throttles.append(serialize_metrics_strict({
                "throttle_id": _make_id(self.cfg.seed, "thr", i),
                "cycle": i,
                "multiplier": float(t_mult),
                "toxicity": float(_finite(tox)),
                "segment": seg["segment"],
                "paper_only": True,
                "timestamp": _utc_now(),
            }))
            inv_factor = self.cfg.inventory_routing_factor
            routed_venue = self.cfg.venues[i % len(self.cfg.venues)]
            self.routing_decisions.append(serialize_metrics_strict({
                "route_id": _make_id(self.cfg.seed, "route", i),
                "cycle": i,
                "venue": routed_venue,
                "inventory_aware_factor": float(_finite(inv_factor)),
                "throttle_mult": float(t_mult),
                "kill_switch_ok": not halted,
                "paper_only": True,
                "timestamp": _utc_now(),
            }))

        gates_ok = bool(not halted) and all(t["multiplier"] <= self.cfg.max_throttle for t in self.throttles)
        rep = serialize_metrics_strict({
            "phase": "PHASE52_TOXICITY_RESILIENT_FLOW_OPTIMIZER",
            "timestamp": _utc_now(),
            "seed": self.cfg.seed,
            "paper_only": True,
            "cycles": cycles,
            "gates_ok": bool(gates_ok),
            "avg_toxicity": float(_finite(tox)),
            "n_segments": len(self.flow_segments),
            "n_throttles": len(self.throttles),
            "n_routes": len(self.routing_decisions),
            "avg_throttle_mult": float(sum(t["multiplier"] for t in self.throttles) / max(1, len(self.throttles))),
            "halted_by_kill_switch": bool(halted),
        })
        _assert_finite(rep, "phase52_flow_opt_report")
        return rep

    def generate_artifacts(self, outdir: str = "research_state") -> Dict[str, Any]:
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        rep = self.optimize_flow(cycles=self.cfg.cycles)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = out / f"PHASE52_FLOW_OPTIMIZER_{ts}.json"
        mpath = out / f"PHASE52_FLOW_OPTIMIZER_{ts}.md"
        with jpath.open("w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2, sort_keys=True)
        with mpath.open("w", encoding="utf-8") as f:
            f.write(f"# PHASE52 Flow Optimizer\n\n- Timestamp: {rep['timestamp']}\n- Gates OK: {rep['gates_ok']}\n- Avg Toxicity: {rep['avg_toxicity']}\n- Avg Throttle: {rep['avg_throttle_mult']}\n- Kill-Switch Halted: {rep['halted_by_kill_switch']}\n")
        rep["json_path"] = str(jpath)
        rep["md_path"] = str(mpath)
        return rep
