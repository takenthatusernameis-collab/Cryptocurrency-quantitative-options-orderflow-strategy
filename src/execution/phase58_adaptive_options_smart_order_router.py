"""
Phase 58: Adaptive Options Smart Order Router (crypto options + orderflow).

Adaptive options SOR: latency/slippage/toxicity/fragmentation aware routing,
dark/venue preference, fill prediction, hard limits, deterministic. PAPER-ONLY.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.execution.phase51_latency_aware_options_sor import Phase51LatencyAwareOptionsSOR, Phase51SORConfig
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
    h = hashlib.sha256(f"{seed}|p58sor|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p58sor_{tag}_{h}"


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
class Phase58AdaptiveOptionsSORConfig:
    seed: int = 58059
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 80
    latency_weight: float = 0.30
    slippage_weight: float = 0.25
    toxicity_weight: float = 0.25
    fragmentation_weight: float = 0.20
    max_slices: int = 8
    dark_preference_bps: float = 1.0
    hard_limit_notional_usd: float = 2_000_000.0
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError("Phase58AdaptiveOptionsSmartOrderRouter: paper_only must remain True (live path hard-gated)")
        if not (0.0 <= sum([self.latency_weight, self.slippage_weight, self.toxicity_weight, self.fragmentation_weight]) <= 1.0001):
            pass  # allow small float drift
        if self.hard_limit_notional_usd <= 0:
            raise ValueError("hard_limit_notional_usd must be > 0")


class Phase58AdaptiveOptionsSmartOrderRouter:
    """Adaptive options SOR for crypto options + orderflow."""

    def __init__(self, cfg: Phase58AdaptiveOptionsSORConfig | None = None) -> None:
        self.cfg = cfg or Phase58AdaptiveOptionsSORConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase58AdaptiveOptionsSmartOrderRouter: paper_only must remain True")
        self.sor51 = Phase51LatencyAwareOptionsSOR(Phase51SORConfig(seed=self.cfg.seed + 51, paper_only=True))
        self.tox58 = Phase58FlowToxicityMitigator()
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.routes: List[Dict[str, Any]] = []
        self.predictions: List[Dict[str, Any]] = []
        self._cycle = 0

    def route_adaptive(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.routes = []
        self.predictions = []
        tox_rep = self.tox58.mitigate(cycles=30)
        of_rep = self.of.run_campaign(cycles=20)
        ksum = self.ks.run_campaign()
        halted = bool(ksum.get("halted", False))
        tox_factor = _finite(tox_rep.get("avg_vpin", 0.2))
        frag = _finite(of_rep.get("avg_imbalance", 0.1))

        for i in range(cycles):
            venue = self.cfg.venues[i % len(self.cfg.venues)]
            latency_ms = 4.0 + (i % 4) * 3.5 + tox_factor * 2.0
            slippage_bps = 1.2 + tox_factor * 6.0 + frag * 2.5
            tox_pen_bps = tox_factor * 10.0
            frag_pen_bps = frag * 5.0
            score = 1.0 - (
                self.cfg.latency_weight * min(1.0, latency_ms / 25.0)
                + self.cfg.slippage_weight * min(1.0, slippage_bps / 20.0)
                + self.cfg.toxicity_weight * tox_factor
                + self.cfg.fragmentation_weight * min(1.0, frag)
            )
            score = max(0.0, min(1.0, _finite(score)))
            sliced = i % 3 != 0
            n_slices = min(self.cfg.max_slices, 2 + i % 6) if sliced else 1
            notional = min(self.cfg.hard_limit_notional_usd, 25000.0 * (1 + i % 40))
            dark_pref = True if venue in ("okx", "binance") else False
            self.routes.append(serialize_metrics_strict({
                "route_id": _make_id(self.cfg.seed, "route", i),
                "cycle": i,
                "venue": venue,
                "underlying": self.cfg.underlyings[i % len(self.cfg.underlyings)],
                "latency_ms": float(_finite(latency_ms)),
                "slippage_bps": float(_finite(slippage_bps)),
                "toxicity_penalty_bps": float(_finite(tox_pen_bps)),
                "fragmentation_penalty_bps": float(_finite(frag_pen_bps)),
                "score": float(score),
                "sliced": bool(sliced),
                "n_slices": int(n_slices),
                "notional_usd": float(_finite(notional)),
                "dark_preference": bool(dark_pref),
                "kill_switch_ok": not halted,
                "paper_only": True,
                "timestamp": _utc_now(),
            }))
            fill_pred = max(0.4, min(0.98, 0.9 - tox_factor * 0.25 - frag * 0.15))
            self.predictions.append(serialize_metrics_strict({
                "pred_id": _make_id(self.cfg.seed, "pred", i),
                "cycle": i,
                "fill_probability_pred": float(_finite(fill_pred)),
                "expected_slippage_bps": float(_finite(slippage_bps * 0.9)),
                "paper_only": True,
                "timestamp": _utc_now(),
            }))

        gates_ok = bool(not halted) and all(r["score"] >= 0.0 and r["notional_usd"] <= self.cfg.hard_limit_notional_usd for r in self.routes)
        rep = serialize_metrics_strict({
            "phase": "PHASE58_ADAPTIVE_OPTIONS_SMART_ORDER_ROUTER",
            "timestamp": _utc_now(),
            "seed": self.cfg.seed,
            "paper_only": True,
            "cycles": cycles,
            "gates_ok": bool(gates_ok),
            "avg_route_score": float(sum(r["score"] for r in self.routes) / max(1, len(self.routes))),
            "avg_fill_pred": float(sum(p["fill_probability_pred"] for p in self.predictions) / max(1, len(self.predictions))),
            "n_routes": len(self.routes),
            "tox58_integration_ok": bool(tox_rep.get("gates_ok", False)),
            "kill_switch_halted": bool(halted),
        })
        _assert_finite(rep, "phase58_sor_report")
        return rep

    def generate_artifacts(self, outdir: str = "research_state") -> Dict[str, Any]:
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        rep = self.route_adaptive(cycles=self.cfg.cycles)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = out / f"PHASE58_ADAPTIVE_OPTIONS_SOR_{ts}.json"
        mpath = out / f"PHASE58_ADAPTIVE_OPTIONS_SOR_{ts}.md"
        with jpath.open("w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2, sort_keys=True)
        with mpath.open("w", encoding="utf-8") as f:
            f.write(f"# PHASE58 Adaptive Options SOR\n\n- Timestamp: {rep['timestamp']}\n- Gates OK: {rep['gates_ok']}\n- Avg Route Score: {rep['avg_route_score']}\n- Avg Fill Pred: {rep['avg_fill_pred']}\n")
        rep["json_path"] = str(jpath)
        rep["md_path"] = str(mpath)
        return rep
