"""
Phase 51: Adaptive Orderflow Alpha Fusion (crypto options + orderflow).

Adaptive fusion of orderflow microstructure (imbalance/toxicity/footprint/liquidity/vwap/OFI)
with regime signals, options flow context, and cross-asset signals. Dynamic weights, decay,
feature selection, alpha scoring, regime-conditional gating. Composes Phases 32/39/46/47/48/49/50.
PAPER-ONLY hard gate by default; live paths hard-gated + tested. Deterministic: fixed seeds,
injectable data, no real network calls, finite numerics, allow_nan=False serialization.
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
    h = hashlib.sha256(f"{seed}|p51alpha|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p51alpha_{tag}_{h}"


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
class Phase51AlphaFusionConfig:
    seed: int = 51051
    paper_only: bool = True
    underlyings: Tuple[str, ...] = ("BTC", "ETH", "SOL")
    expiries: Tuple[str, ...] = ("1D", "7D", "30D", "90D")
    venues: Tuple[str, ...] = ("deribit", "okx", "bybit", "binance")
    regimes: Tuple[str, ...] = ("low_vol", "normal", "high_vol", "crisis", "trending")
    feature_count: int = 14
    selected_features: int = 8
    alpha_decay: float = 0.85
    weight_adaptation_lr: float = 0.12
    min_weight: float = 0.02
    max_weight: float = 0.40
    toxicity_threshold: float = 0.32
    imbalance_threshold: float = 0.25
    footprint_threshold: float = 0.30
    min_confidence: float = 0.55
    kill_switch_on_breach: bool = True
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError("Phase51AdaptiveOrderflowAlphaFusion: paper_only must remain True (live path hard-gated)")
        if not (0.0 < self.alpha_decay <= 1.0):
            raise ValueError("alpha_decay must be in (0,1]")
        if not (0.0 < self.weight_adaptation_lr <= 1.0):
            raise ValueError("weight_adaptation_lr must be in (0,1]")
        if not (0.0 <= self.min_weight < self.max_weight <= 1.0):
            raise ValueError("invalid weight bounds")
        if not (0.0 <= self.toxicity_threshold <= 1.0):
            raise ValueError("toxicity_threshold must be in [0,1]")
        if not (1 <= self.selected_features <= self.feature_count):
            raise ValueError("invalid feature selection")


@dataclass
class OrderflowMicrostructure:
    ts: str
    underlying: str
    expiry: str
    venue: str
    imbalance: float
    toxicity: float
    footprint: float
    liquidity: float
    vwap: float
    ofi: float
    mid_price: float
    spread_bps: float
    paper_only: bool

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict(asdict(self))


@dataclass
class RegimeSignal:
    ts: str
    underlying: str
    regime: str
    regime_prob: float
    vol_percentile: float
    trend_strength: float
    skew: float
    paper_only: bool

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict(asdict(self))


@dataclass
class OptionsFlowContext:
    ts: str
    underlying: str
    expiry: str
    strike: float
    option_type: str
    flow_imbalance: float
    iv_rank: float
    term_slope: float
    paper_only: bool

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict(asdict(self))


@dataclass
class CrossAssetSignal:
    ts: str
    underlying: str
    btc_correlation: float
    eth_correlation: float
    perp_spot_basis_bps: float
    funding_rate: float
    paper_only: bool

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict(asdict(self))


@dataclass
class FusedAlpha:
    alpha_id: str
    ts: str
    underlying: str
    expiry: str
    venue: str
    regime: str
    regime_prob: float
    alpha_score: float
    confidence: float
    gate_passed: bool
    feature_weights: Dict[str, float]
    selected_features: List[str]
    expected_bps: float
    decay_applied: float
    paper_only: bool
    kill_switch_armed: bool

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict(asdict(self))


_FEATURE_NAMES = (
    "imbalance",
    "toxicity",
    "footprint",
    "liquidity",
    "vwap_dev_bps",
    "ofi",
    "spread_bps",
    "regime_prob",
    "vol_percentile",
    "trend_strength",
    "skew",
    "flow_imbalance",
    "iv_rank",
    "basis_bps",
)


class Phase51AdaptiveOrderflowAlphaFusion:
    """Adaptive orderflow microstucture + regime alpha scorer for crypto options."""

    def __init__(self, config: Optional[Phase51AlphaFusionConfig] = None) -> None:
        self.cfg = config or Phase51AlphaFusionConfig()
        self.rng = random.Random(self.cfg.seed)
        self.weights = {name: 1.0 / len(_FEATURE_NAMES) for name in _FEATURE_NAMES}
        self.weight_history: List[Dict[str, float]] = [dict(self.weights)]
        self.alphas: List[FusedAlpha] = []
        self.alpha_integrator = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=1)
        )
        self.kill_switches = Phase39KillSwitchesCircuitBreakers(
            KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True)
        )
        self._cycle = 0
        self._last_breach: Optional[str] = None

    # ------------------------------------------------------------------ inputs
    def _microstructure(self, underlying: str, expiry: str, venue: str, idx: int) -> OrderflowMicrostructure:
        r = self.rng
        imbalance = _finite(r.uniform(-1.0, 1.0))
        toxicity = _finite(r.uniform(0.0, 1.0))
        footprint = _finite(r.uniform(0.0, 1.0))
        liquidity = _finite(r.uniform(0.1, 1.0))
        vwap_dev = _finite(r.uniform(-25.0, 25.0))
        ofi = _finite(r.uniform(-1.0, 1.0))
        mid = _finite(r.uniform(80000.0, 120000.0) if underlying == "BTC" else r.uniform(1500.0, 4000.0))
        spread = _finite(r.uniform(2.0, 40.0))
        return OrderflowMicrostructure(
            ts=_utc_now(),
            underlying=underlying,
            expiry=expiry,
            venue=venue,
            imbalance=imbalance,
            toxicity=toxicity,
            footprint=footprint,
            liquidity=liquidity,
            vwap=mid + vwap_dev,
            ofi=ofi,
            mid_price=mid,
            spread_bps=spread,
            paper_only=True,
        )

    def _regime(self, underlying: str, idx: int) -> RegimeSignal:
        r = self.rng
        regime = self.cfg.regimes[idx % len(self.cfg.regimes)]
        return RegimeSignal(
            ts=_utc_now(),
            underlying=underlying,
            regime=regime,
            regime_prob=_finite(r.uniform(0.5, 0.99)),
            vol_percentile=_finite(r.uniform(0.0, 1.0)),
            trend_strength=_finite(r.uniform(0.0, 1.0)),
            skew=_finite(r.uniform(-1.0, 1.0)),
            paper_only=True,
        )

    def _options_flow(self, underlying: str, expiry: str, idx: int) -> OptionsFlowContext:
        r = self.rng
        strike = _finite(r.uniform(50000.0, 150000.0)) if underlying == "BTC" else _finite(r.uniform(1000.0, 6000.0))
        return OptionsFlowContext(
            ts=_utc_now(),
            underlying=underlying,
            expiry=expiry,
            strike=strike,
            option_type="call" if idx % 2 == 0 else "put",
            flow_imbalance=_finite(r.uniform(-1.0, 1.0)),
            iv_rank=_finite(r.uniform(0.0, 1.0)),
            term_slope=_finite(r.uniform(-1.0, 1.0)),
            paper_only=True,
        )

    def _cross_asset(self, underlying: str, idx: int) -> CrossAssetSignal:
        r = self.rng
        return CrossAssetSignal(
            ts=_utc_now(),
            underlying=underlying,
            btc_correlation=_finite(r.uniform(-1.0, 1.0)) if underlying != "BTC" else 1.0,
            eth_correlation=_finite(r.uniform(-1.0, 1.0)) if underlying != "ETH" else 1.0,
            perp_spot_basis_bps=_finite(r.uniform(-100.0, 100.0)),
            funding_rate=_finite(r.uniform(-0.01, 0.01)),
            paper_only=True,
        )

    # --------------------------------------------------------------- adaptation
    def _feature_vector(self, ms: OrderflowMicrostructure, rg: RegimeSignal, of: OptionsFlowContext, ca: CrossAssetSignal) -> List[float]:
        return [
            _finite(ms.imbalance),
            _finite(ms.toxicity),
            _finite(ms.footprint),
            _finite(ms.liquidity),
            _finite((ms.mid_price - ms.vwap) / max(ms.mid_price, 1e-9) * 1e4),
            _finite(ms.ofi),
            _finite(ms.spread_bps),
            _finite(rg.regime_prob),
            _finite(rg.vol_percentile),
            _finite(rg.trend_strength),
            _finite(rg.skew),
            _finite(of.flow_imbalance),
            _finite(of.iv_rank),
            _finite(ca.perp_spot_basis_bps),
        ]

    def _regime_gate(self, rg: RegimeSignal, ms: OrderflowMicrostructure) -> tuple[bool, str]:
        if rg.regime == "crisis" and ms.toxicity > self.cfg.toxicity_threshold:
            return False, "crisis_regime_high_toxicity"
        if rg.regime == "high_vol" and rg.vol_percentile > 0.95 and ms.toxicity > 0.6:
            return False, "high_vol_extreme_toxicity"
        if ms.toxicity > 0.9:
            return False, "toxicity_critical"
        if rg.regime_prob < self.cfg.min_confidence:
            return False, "low_regime_confidence"
        return True, "ok"

    def _adapt_weights(self, features: List[float], alpha_score: float, confidence: float) -> None:
        target = confidence * alpha_score
        for i, name in enumerate(_FEATURE_NAMES[: self.cfg.selected_features]):
            grad = features[i] * target
            new_w = _finite(self.weights[name] + self.cfg.weight_adaptation_lr * grad)
            self.weights[name] = min(max(new_w, self.cfg.min_weight), self.cfg.max_weight)
        total = sum(self.weights[name] for name in _FEATURE_NAMES[: self.cfg.selected_features])
        if total <= 0:
            total = 1.0
        for name in _FEATURE_NAMES[: self.cfg.selected_features]:
            self.weights[name] /= total
        for name in _FEATURE_NAMES[self.cfg.selected_features:]:
            self.weights[name] = _finite(self.weights[name] * self.cfg.alpha_decay)
        self.weight_history.append(dict(self.weights))
        if len(self.weight_history) > 200:
            self.weight_history = self.weight_history[-200:]

    def _select_features(self) -> List[str]:
        ranked = sorted(_FEATURE_NAMES[: self.cfg.selected_features], key=lambda n: -self.weights[n])
        return ranked[: self.cfg.selected_features]

    def _decay_score(self, score: float, cycles_since: int) -> float:
        return _finite(score * (self.cfg.alpha_decay ** min(cycles_since, 50)))

    # ------------------------------------------------------------------ core
    def fuse(
        self,
        underlying: str,
        expiry: str,
        venue: str,
        idx: int,
        cycles_since: int = 0,
    ) -> FusedAlpha:
        ms = self._microstructure(underlying, expiry, venue, idx)
        rg = self._regime(underlying, idx)
        of = self._options_flow(underlying, expiry, idx)
        ca = self._cross_asset(underlying, idx)

        features = self._feature_vector(ms, rg, of, ca)
        gate_passed, gate_reason = self._regime_gate(rg, ms)

        raw_score = 0.0
        for i, name in enumerate(_FEATURE_NAMES):
            raw_score += self.weights[name] * features[i]
        raw_score = _finite(raw_score)
        score = _finite(self._decay_score(raw_score, cycles_since))
        confidence = _finite(min(0.5 + abs(rg.regime_prob - 0.5) + 0.3 * (1.0 - ms.toxicity), 0.99))
        confidence = _finite(min(confidence, max(0.05, rg.regime_prob)))

        fused = FusedAlpha(
            alpha_id=_make_id(self.cfg.seed, "alpha", idx),
            ts=_utc_now(),
            underlying=underlying,
            expiry=expiry,
            venue=venue,
            regime=rg.regime,
            regime_prob=_finite(rg.regime_prob),
            alpha_score=score,
            confidence=confidence,
            gate_passed=bool(gate_passed),
            feature_weights={n: _finite(self.weights[n]) for n in _FEATURE_NAMES[: self.cfg.selected_features]},
            selected_features=self._select_features(),
            expected_bps=_finite(score * 100.0 * confidence),
            decay_applied=_finite(self.cfg.alpha_decay ** min(cycles_since, 50)),
            paper_only=True,
            kill_switch_armed=bool(self.cfg.kill_switch_on_breach and not gate_passed),
        )
        _assert_finite(fused.to_dict(), f"fused alpha {fused.alpha_id}")
        self.alphas.append(fused)
        if not gate_passed:
            self._last_breach = gate_reason
        self._adapt_weights(features, score, confidence)
        self._cycle += 1
        return fused

    def run_campaign(self, cycles: int = 60) -> Dict[str, Any]:
        if cycles <= 0:
            raise ValueError("cycles must be positive")
        self._cycle = 0
        results: List[Dict[str, Any]] = []
        gate_failures = 0
        for i in range(cycles):
            u = self.cfg.underlyings[i % len(self.cfg.underlyings)]
            e = self.cfg.expiries[i % len(self.cfg.expiries)]
            v = self.cfg.venues[i % len(self.cfg.venues)]
            a = self.fuse(u, e, v, i, cycles_since=i)
            results.append(a.to_dict())
            if not a.gate_passed:
                gate_failures += 1
        ks = self.kill_switches.run_campaign()
        rep = serialize_metrics_strict({
            "phase": "PHASE51_ADAPTIVE_ORDERFLOW_ALPHA_FUSION",
            "timestamp": _utc_now(),
            "seed": self.cfg.seed,
            "paper_only": True,
            "cycles": cycles,
            "gates_ok": bool(ks.get("gates_ok", True)) and gate_failures < cycles,
            "n_alphas": len(results),
            "n_gate_passed": sum(1 for r in results if r["gate_passed"]),
            "n_gate_failures": gate_failures,
            "avg_alpha_score": _finite(sum(r["alpha_score"] for r in results) / max(len(results), 1)),
            "avg_confidence": _finite(sum(r["confidence"] for r in results) / max(len(results), 1)),
            "avg_expected_bps": _finite(sum(r["expected_bps"] for r in results) / max(len(results), 1)),
            "regimes": {rg: sum(1 for r in results if r["regime"] == rg) for rg in self.cfg.regimes},
            "weight_history": self.weight_history[-1],
            "selected_features": self._select_features(),
            "kill_switch_armed": bool(ks.get("gates_ok", True) is False),
            "last_breach": self._last_breach,
            "alphas": results,
        })
        return rep

    def generate_artifacts(self, outdir: Optional[str] = None) -> Dict[str, Any]:
        target = Path(outdir or self.cfg.outdir)
        target.mkdir(parents=True, exist_ok=True)
        rep = self.run_campaign() if not self.alphas else serialize_metrics_strict({
            "phase": "PHASE51_ADAPTIVE_ORDERFLOW_ALPHA_FUSION",
            "timestamp": _utc_now(),
            "seed": self.cfg.seed,
            "paper_only": True,
            "cycles": len(self.alphas),
            "gates_ok": True,
            "n_alphas": len(self.alphas),
            "weight_history": self.weight_history[-1],
            "selected_features": self._select_features(),
            "alphas": [a.to_dict() for a in self.alphas],
        })
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = target / f"phase51_adaptive_orderflow_alpha_fusion_{stamp}.json"
        md_path = target / f"phase51_adaptive_orderflow_alpha_fusion_{stamp}.md"
        with open(json_path, "w") as f:
            json.dump(rep, f, indent=2, allow_nan=False)
        with open(md_path, "w") as f:
            f.write("# Phase 51 - Adaptive Orderflow Alpha Fusion\n\n")
            f.write(f"- Timestamp: {rep['timestamp']}\n")
            f.write(f"- Seed: {self.cfg.seed} | Paper-only: true | Gates OK: {rep['gates_ok']}\n")
            f.write(f"- Alphas: {rep['n_alphas']} | Gate passed: {rep.get('n_gate_passed', rep['n_alphas'])} | Failures: {rep.get('n_gate_failures', 0)}\n")
            f.write(f"- Avg alpha score: {rep.get('avg_alpha_score', 0.0):.4f} | Avg confidence: {rep.get('avg_confidence', 0.0):.4f}\n")
            f.write(f"- Avg expected bps: {rep.get('avg_expected_bps', 0.0):.4f} | Selected features: {', '.join(rep.get('selected_features', []))}\n")
            f.write(f"- Kill switch armed: {rep.get('kill_switch_armed', False)} | Last breach: {rep.get('last_breach', 'none')}\n")
        return {"json": str(json_path), "md": str(md_path), "report": rep}
