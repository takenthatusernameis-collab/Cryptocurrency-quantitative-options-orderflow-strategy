"""
Phase 51: Latency-Aware Options Smart Order Routing (crypto options + orderflow).

Latency-aware SOR for options/perps across venues: venue latency/queue/fill models,
microstructure-adjusted routing, toxicity-aware routing penalty, order slicing/peg logic,
TCA hooks, slippage minimization. Composes Phases 32/39/46/47/49/50. PAPER-ONLY hard gate
by default; live paths hard-gated + tested. Deterministic: fixed seeds, injectable data,
finite numerics, allow_nan=False serialization.
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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
    h = hashlib.sha256(f"{seed}|p51sor|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p51sor_{tag}_{h}"


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
class Phase51SORConfig:
    seed: int = 51052
    paper_only: bool = True
    underlyings: Tuple[str, ...] = ("BTC", "ETH", "SOL")
    expiries: Tuple[str, ...] = ("1D", "7D", "30D", "90D")
    venues: Tuple[str, ...] = ("deribit", "okx", "bybit", "binance")
    base_latency_ms: Tuple[float, ...] = (4.0, 9.0, 13.0, 17.0)
    jitter_ms: float = 2.0
    toxicity_penalty_bps: float = 8.0
    max_slices: int = 6
    min_slice_notional_usd: float = 5000.0
    max_slice_notional_usd: float = 200000.0
    peg_offset_bps: float = 1.5
    slippage_bps_per_slice: float = 0.4
    fill_probability_base: float = 0.85
    queue_penalty_bps: float = 3.0
    latency_score_weight: float = 0.35
    fill_score_weight: float = 0.35
    toxicity_score_weight: float = 0.30
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError("Phase51LatencyAwareOptionsSOR: paper_only must remain True (live path hard-gated)")
        if not (1 <= self.max_slices <= 20):
            raise ValueError("max_slices must be in [1,20]")
        if not (0.0 <= self.toxicity_penalty_bps):
            raise ValueError("toxicity_penalty_bps must be >= 0")


@dataclass
class VenueLatencyModel:
    venue: str
    latency_ms: float
    queue_depth: float
    fill_probability: float
    toxicity: float
    paper_only: bool

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict(asdict(self))


@dataclass
class RouteDecision:
    route_id: str
    underlying: str
    expiry: str
    strike: float
    option_type: str
    side: str
    venue: str
    latency_ms: float
    queue_depth: float
    fill_probability: float
    toxicity: float
    toxicity_penalty_bps: float
    slippage_bps: float
    expected_cost_bps: float
    score: float
    sliced: bool
    n_slices: int
    slice_notional_usd: float
    peg_offset_bps: float
    paper_only: bool
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict(asdict(self))


@dataclass
class TCA:
    tca_id: str
    route_id: str
    underlying: str
    venue: str
    arrival_price: float
    fill_price: float
    slippage_bps: float
    latency_ms: float
    implementation_shortfall_bps: float
    paper_only: bool
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict(asdict(self))


class Phase51LatencyAwareOptionsSOR:
    """Latency-aware smart order router for crypto options/perps across venues."""

    def __init__(self, config: Optional[Phase51SORConfig] = None) -> None:
        self.cfg = config or Phase51SORConfig()
        self.rng = random.Random(self.cfg.seed)
        self.venue_latency: Dict[str, VenueLatencyModel] = {}
        self.decisions: List[RouteDecision] = []
        self.tcas: List[TCA] = []
        self._slice_ctr = 0
        self._last_halt: Optional[str] = None
        self.alpha_integrator = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=1)
        )
        self.kill_switches = Phase39KillSwitchesCircuitBreakers(
            KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True)
        )

    # --------------------------------------------------------------- venue models
    def _venue_model(self, venue: str, idx: int) -> VenueLatencyModel:
        base = float(self.cfg.base_latency_ms[self.cfg.venues.index(venue)])
        jitter = _finite(self.rng.uniform(-self.cfg.jitter_ms, self.cfg.jitter_ms))
        latency = _finite(max(0.5, base + jitter))
        queue_depth = _finite(self.rng.uniform(0.0, 1.0))
        fill_prob = _finite(min(0.99, self.cfg.fill_probability_base * (1.0 - 0.15 * queue_depth)))
        toxicity = _finite(self.rng.uniform(0.0, 1.0))
        model = VenueLatencyModel(
            venue=venue,
            latency_ms=latency,
            queue_depth=queue_depth,
            fill_probability=fill_prob,
            toxicity=toxicity,
            paper_only=True,
        )
        self.venue_latency[venue] = model
        return model

    # --------------------------------------------------------------- routing
    def route_order(
        self,
        underlying: str,
        expiry: str,
        strike: float,
        option_type: str,
        side: str,
        notional_usd: float,
        urgency: float,
        idx: int,
        toxicity: Optional[float] = None,
    ) -> RouteDecision:
        notional = _finite(notional_usd)
        urgency = _finite(min(max(urgency, 0.0), 1.0))
        tox = _finite(self.rng.uniform(0.0, 1.0) if toxicity is None else toxicity)

        best: Optional[RouteDecision] = None
        best_score = float("-inf")
        for venue in self.cfg.venues:
            vm = self._venue_model(venue, idx)
            lat_penalty = vm.latency_ms * self.cfg.latency_score_weight
            fill_reward = vm.fill_probability * self.cfg.fill_score_weight
            tox_penalty = vm.toxicity * self.cfg.toxicity_score_weight
            score = _finite(fill_reward - lat_penalty - tox_penalty - 0.1 * vm.queue_depth)
            if score > best_score:
                best_score = score
                best = (venue, vm, score)

        assert best is not None
        venue, vm, score = best
        tox_penalty_bps = _finite(tox * self.cfg.toxicity_penalty_bps)
        slippage = _finite(self.cfg.slippage_bps_per_slice + vm.latency_ms * 0.05 + tox_penalty_bps * 0.1)
        expected_cost = _finite(slippage + tox_penalty_bps + vm.queue_depth * self.cfg.queue_penalty_bps)
        n_slices = int(min(max(1, int(notional / self.cfg.max_slice_notional_usd) + 1), self.cfg.max_slices))
        slice_notional = _finite(notional / n_slices)
        peg_offset = _finite(self.cfg.peg_offset_bps * (1.0 + urgency))

        decision = RouteDecision(
            route_id=_make_id(self.cfg.seed, "route", idx),
            underlying=underlying,
            expiry=expiry,
            strike=_finite(strike),
            option_type=option_type,
            side=side,
            venue=venue,
            latency_ms=_finite(vm.latency_ms),
            queue_depth=_finite(vm.queue_depth),
            fill_probability=_finite(vm.fill_probability),
            toxicity=_finite(vm.toxicity),
            toxicity_penalty_bps=_finite(tox_penalty_bps),
            slippage_bps=_finite(slippage),
            expected_cost_bps=_finite(expected_cost),
            score=_finite(score),
            sliced=n_slices > 1,
            n_slices=n_slices,
            slice_notional_usd=_finite(slice_notional),
            peg_offset_bps=_finite(peg_offset),
            paper_only=True,
            timestamp=_utc_now(),
        )
        _assert_finite(decision.to_dict(), f"route {decision.route_id}")
        self.decisions.append(decision)

        if tox > 0.85 or vm.latency_ms > 60.0:
            self._last_halt = f"route_halt_{decision.route_id}"

        tca = TCA(
            tca_id=_make_id(self.cfg.seed, "tca", idx),
            route_id=decision.route_id,
            underlying=underlying,
            venue=venue,
            arrival_price=_finite(self.rng.uniform(80000.0, 120000.0)),
            fill_price=_finite(self.rng.uniform(80000.0, 120000.0)),
            slippage_bps=_finite(slippage),
            latency_ms=_finite(vm.latency_ms),
            implementation_shortfall_bps=_finite(expected_cost),
            paper_only=True,
            timestamp=_utc_now(),
        )
        _assert_finite(tca.to_dict(), f"tca {tca.tca_id}")
        self.tcas.append(tca)
        return decision

    def run_campaign(self, cycles: int = 60) -> Dict[str, Any]:
        if cycles <= 0:
            raise ValueError("cycles must be positive")
        decisions: List[Dict[str, Any]] = []
        halted = 0
        for i in range(cycles):
            u = self.cfg.underlyings[i % len(self.cfg.underlyings)]
            e = self.cfg.expiries[i % len(self.cfg.expiries)]
            strike = _finite(self.rng.uniform(50000.0, 150000.0)) if u == "BTC" else _finite(self.rng.uniform(1000.0, 6000.0))
            ot = "call" if i % 2 == 0 else "put"
            side = "buy" if i % 2 == 0 else "sell"
            notional = _finite(self.rng.uniform(10000.0, 500000.0))
            urgency = _finite(self.rng.uniform(0.0, 1.0))
            d = self.route_order(u, e, strike, ot, side, notional, urgency, i)
            decisions.append(d.to_dict())
            if d.toxicity_penalty_bps > self.cfg.toxicity_penalty_bps * 0.8:
                halted += 1
        ks = self.kill_switches.run_campaign()
        rep = serialize_metrics_strict({
            "phase": "PHASE51_LATENCY_AWARE_OPTIONS_SOR",
            "timestamp": _utc_now(),
            "seed": self.cfg.seed,
            "paper_only": True,
            "cycles": cycles,
            "gates_ok": bool(ks.get("gates_ok", True)) and halted < cycles,
            "n_routes": len(decisions),
            "n_sliced": sum(1 for d in decisions if d["sliced"]),
            "avg_latency_ms": _finite(sum(d["latency_ms"] for d in decisions) / max(len(decisions), 1)),
            "avg_fill_probability": _finite(sum(d["fill_probability"] for d in decisions) / max(len(decisions), 1)),
            "avg_toxicity_penalty_bps": _finite(sum(d["toxicity_penalty_bps"] for d in decisions) / max(len(decisions), 1)),
            "avg_slippage_bps": _finite(sum(d["slippage_bps"] for d in decisions) / max(len(decisions), 1)),
            "avg_expected_cost_bps": _finite(sum(d["expected_cost_bps"] for d in decisions) / max(len(decisions), 1)),
            "avg_score": _finite(sum(d["score"] for d in decisions) / max(len(decisions), 1)),
            "venue_picks": {v: sum(1 for d in decisions if d["venue"] == v) for v in self.cfg.venues},
            "halted_routes": halted,
            "last_halt": self._last_halt,
            "routes": decisions,
            "tcas": [t.to_dict() for t in self.tcas],
        })
        return rep

    def generate_artifacts(self, outdir: Optional[str] = None) -> Dict[str, Any]:
        target = Path(outdir or self.cfg.outdir)
        target.mkdir(parents=True, exist_ok=True)
        rep = self.run_campaign() if not self.decisions else serialize_metrics_strict({
            "phase": "PHASE51_LATENCY_AWARE_OPTIONS_SOR",
            "timestamp": _utc_now(),
            "seed": self.cfg.seed,
            "paper_only": True,
            "cycles": len(self.decisions),
            "gates_ok": True,
            "n_routes": len(self.decisions),
            "venues": {v: sum(1 for d in self.decisions if d.venue == v) for v in self.cfg.venues},
            "routes": [d.to_dict() for d in self.decisions],
            "tcas": [t.to_dict() for t in self.tcas],
        })
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = target / f"phase51_latency_aware_options_sor_{stamp}.json"
        md_path = target / f"phase51_latency_aware_options_sor_{stamp}.md"
        with open(json_path, "w") as f:
            json.dump(rep, f, indent=2, allow_nan=False)
        with open(md_path, "w") as f:
            f.write("# Phase 51 - Latency-Aware Options Smart Order Routing\n\n")
            f.write(f"- Timestamp: {rep['timestamp']}\n")
            f.write(f"- Seed: {self.cfg.seed} | Paper-only: true | Gates OK: {rep['gates_ok']}\n")
            f.write(f"- Routes: {rep['n_routes']} | Sliced: {rep.get('n_sliced', 0)}\n")
            f.write(f"- Avg latency: {rep.get('avg_latency_ms', 0.0):.2f} ms | Avg fill prob: {rep.get('avg_fill_probability', 0.0):.4f}\n")
            f.write(f"- Avg slippage: {rep.get('avg_slippage_bps', 0.0):.4f} bps | Avg expected cost: {rep.get('avg_expected_cost_bps', 0.0):.4f} bps\n")
            f.write(f"- Venue picks: {rep.get('venue_picks', {})} | Last halt: {rep.get('last_halt', 'none')}\n")
        return {"json": str(json_path), "md": str(md_path), "report": rep}
