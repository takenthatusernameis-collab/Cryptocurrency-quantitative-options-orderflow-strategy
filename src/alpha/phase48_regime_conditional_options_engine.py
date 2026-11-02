"""
Phase 48: Regime-Conditional Options Strategies & Orderflow Signal Fusion Engine.

Crypto options + orderflow focused. Regime-conditional options strategy selection
(vol surface, skew, term structure), orderflow signal fusion, alpha scoring,
capital allocation. Composes Phases 17-47. PAPER-ONLY hard gate by default;
live paths hard-gated + tested. Deterministic: fixed seeds, injectable data,
no real network calls, finite numerics, allow_nan=False serialization.
"""
from __future__ import annotations

import hashlib
import json
import math
import threading
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional, Tuple

from src.alpha.orderflow_alpha import OrderflowAlphaEngine
from src.alpha.signal_fusion import SignalFusion
from src.errors import RiskLimitError, get_logger
from src.execution.phase47_cross_venue_arbitrage_engine import (
    Phase47Config,
    Phase47CrossVenueArbitrageEngine,
)
from src.orderflow.phase32_orderflow_alpha_integration import (
    OrderflowAlphaIntegrationConfig32,
    OrderflowAlphaIntegrator,
)
from src.risk.phase39_kill_switches_circuit_breakers import (
    Phase39KillSwitchesCircuitBreakers,
    KillSwitchConfig39,
)
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p48|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p48_{tag}_{h}"


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


class MarketRegime(str, Enum):
    LOW_VOL = "low_vol"
    NORMAL = "normal"
    HIGH_VOL = "high_vol"
    CRISIS = "crisis"
    TRENDING = "trending"


class OptionStrategyType(str, Enum):
    CALENDAR_SPREAD = "calendar_spread"
    VERTICAL_SPREAD = "vertical_spread"
    IRON_CONDOR = "iron_condor"
    STRADDLE = "straddle"
    STRANGLE = "strangle"
    RATIO_SPREAD = "ratio_spread"
    BUTTERFLY = "butterfly"
    COVERED_CALL = "covered_call"
    PROTECTIVE_PUT = "protective_put"
    VOL_ARB = "vol_arb"


class OrderflowSignalType(str, Enum):
    CUMULATIVE_DELTA = "cumulative_delta"
    IMBALANCE = "imbalance"
    VPIN = "vpin"
    ABSORPTION = "absorption"
    SWEEP = "sweep"
    LIQUIDITY_VACUUM = "liquidity_vacuum"
    AGGRESSION = "aggression"


@dataclass(frozen=True)
class Phase48Config:
    seed: int = 48048
    paper_only: bool = True
    underlyings: Tuple[str, ...] = ("BTC", "ETH", "SOL")
    venues: Tuple[str, ...] = ("deribit", "okx", "bybit", "binance")
    expiries: Tuple[str, ...] = ("1D", "7D", "30D", "90D")
    cycles: int = 60
    min_alpha_score: float = 0.25
    min_fused_score: float = 0.30
    max_allocation_pct: float = 0.15
    total_capital_usd: float = 2000000.0
    orderflow_weight: float = 0.45
    regime_weight: float = 0.25
    vol_surface_weight: float = 0.30
    toxicity_threshold: float = 0.35
    max_positions: int = 25
    enable_cross_venue_arb_fusion: bool = True
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise RiskLimitError("paper_only must be bool", context={"paper_only": self.paper_only})
        if not self.paper_only:
            raise RiskLimitError("Phase48RegimeConditionalOptionsEngine: paper_only must remain True (live path hard-gated)")
        if not self.underlyings:
            raise RiskLimitError("underlyings must be non-empty")
        if not (0.0 <= self.min_alpha_score <= 1.0):
            raise RiskLimitError("min_alpha_score must be in [0,1]")
        if not (0.0 <= self.orderflow_weight <= 1.0):
            raise RiskLimitError("orderflow_weight must be in [0,1]")
        if self.cycles < 1:
            raise RiskLimitError("cycles must be >= 1")
        if abs(self.orderflow_weight + self.regime_weight + self.vol_surface_weight - 1.0) > 1e-9:
            raise RiskLimitError("fusion weights must sum to 1.0")


@dataclass
class RegimeSignal:
    regime_id: str
    cycle: int
    timestamp: str
    regime: str
    confidence: float
    volatility_regime: float
    trend_regime: float
    liquidity_regime: float
    skew_regime: float
    term_structure_regime: float
    paper_only: bool

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "regime_id": self.regime_id,
            "cycle": int(self.cycle),
            "timestamp": self.timestamp,
            "regime": self.regime,
            "confidence": float(_finite(self.confidence)),
            "volatility_regime": float(_finite(self.volatility_regime)),
            "trend_regime": float(_finite(self.trend_regime)),
            "liquidity_regime": float(_finite(self.liquidity_regime)),
            "skew_regime": float(_finite(self.skew_regime)),
            "term_structure_regime": float(_finite(self.term_structure_regime)),
            "paper_only": bool(self.paper_only),
        })


@dataclass
class OrderflowFusionSignal:
    fusion_id: str
    cycle: int
    timestamp: str
    symbol: str
    venue: str
    cumulative_delta: float
    imbalance: float
    vpin_lite: float
    absorption_score: float
    sweep_score: float
    liquidity_vacuum_score: float
    aggression_score: float
    orderflow_score: float
    toxicity_score: float
    decay_factor: float
    paper_only: bool

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "fusion_id": self.fusion_id,
            "cycle": int(self.cycle),
            "timestamp": self.timestamp,
            "symbol": self.symbol,
            "venue": self.venue,
            "cumulative_delta": float(_finite(self.cumulative_delta)),
            "imbalance": float(_finite(self.imbalance)),
            "vpin_lite": float(_finite(self.vpin_lite)),
            "absorption_score": float(_finite(self.absorption_score)),
            "sweep_score": float(_finite(self.sweep_score)),
            "liquidity_vacuum_score": float(_finite(self.liquidity_vacuum_score)),
            "aggression_score": float(_finite(self.aggression_score)),
            "orderflow_score": float(_finite(self.orderflow_score)),
            "toxicity_score": float(_finite(self.toxicity_score)),
            "decay_factor": float(_finite(self.decay_factor)),
            "paper_only": bool(self.paper_only),
        })


@dataclass
class RegimeConditionalAlpha:
    alpha_id: str
    cycle: int
    timestamp: str
    symbol: str
    underlying: str
    expiry: str
    strike: float
    option_type: str
    strategy_type: str
    regime: str
    orderflow_score: float
    vol_surface_score: float
    regime_score: float
    fused_score: float
    alpha_score: float
    notional_usd: float
    allocation_pct: float
    expected_edge_bps: float
    confidence: float
    delta_est: float
    vega_est: float
    gamma_est: float
    theta_est: float
    risk_flags: List[str]
    rationale: str
    paper_only: bool

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "alpha_id": self.alpha_id,
            "cycle": int(self.cycle),
            "timestamp": self.timestamp,
            "symbol": self.symbol,
            "underlying": self.underlying,
            "expiry": self.expiry,
            "strike": float(_finite(self.strike)),
            "option_type": self.option_type,
            "strategy_type": self.strategy_type,
            "regime": self.regime,
            "orderflow_score": float(_finite(self.orderflow_score)),
            "vol_surface_score": float(_finite(self.vol_surface_score)),
            "regime_score": float(_finite(self.regime_score)),
            "fused_score": float(_finite(self.fused_score)),
            "alpha_score": float(_finite(self.alpha_score)),
            "notional_usd": float(_finite(self.notional_usd)),
            "allocation_pct": float(_finite(self.allocation_pct)),
            "expected_edge_bps": float(_finite(self.expected_edge_bps)),
            "confidence": float(_finite(self.confidence)),
            "delta_est": float(_finite(self.delta_est)),
            "vega_est": float(_finite(self.vega_est)),
            "gamma_est": float(_finite(self.gamma_est)),
            "theta_est": float(_finite(self.theta_est)),
            "risk_flags": list(self.risk_flags),
            "rationale": self.rationale,
            "paper_only": bool(self.paper_only),
        })


class Phase48RegimeConditionalOptionsEngine:
    """Regime-conditional crypto options strategies with orderflow fusion."""

    def __init__(self, cfg: Optional[Phase48Config] = None, seed: int = 48048, paper_only: bool = True) -> None:
        if cfg is not None and not isinstance(cfg.paper_only, bool):
            raise RiskLimitError("paper_only must be bool")
        if cfg is not None and not cfg.paper_only:
            raise RiskLimitError("Phase48RegimeConditionalOptionsEngine: paper_only must remain True (live path hard-gated)")
        self.cfg = cfg or Phase48Config(seed=seed, paper_only=paper_only)
        if not self.cfg.paper_only:
            raise RiskLimitError("Phase48RegimeConditionalOptionsEngine: paper_only must remain True (live path hard-gated)")
        self.cfg = Phase48Config(
            seed=int(self.cfg.seed),
            paper_only=True,
            underlyings=tuple(self.cfg.underlyings),
            venues=tuple(self.cfg.venues),
            expiries=tuple(self.cfg.expiries),
            cycles=int(self.cfg.cycles),
            min_alpha_score=float(self.cfg.min_alpha_score),
            min_fused_score=float(self.cfg.min_fused_score),
            max_allocation_pct=float(self.cfg.max_allocation_pct),
            total_capital_usd=float(self.cfg.total_capital_usd),
            orderflow_weight=float(self.cfg.orderflow_weight),
            regime_weight=float(self.cfg.regime_weight),
            vol_surface_weight=float(self.cfg.vol_surface_weight),
            toxicity_threshold=float(self.cfg.toxicity_threshold),
            max_positions=int(self.cfg.max_positions),
            enable_cross_venue_arb_fusion=bool(self.cfg.enable_cross_venue_arb_fusion),
            outdir=str(self.cfg.outdir),
        )
        self.seed = int(self.cfg.seed)
        self.paper_only = True
        self.outdir = self.cfg.outdir
        self.lock = threading.RLock()
        self._ctr = 0
        self._regime_history: Deque[RegimeSignal] = deque(maxlen=1000)
        self._of_history: Deque[OrderflowFusionSignal] = deque(maxlen=2000)
        self._alpha_history: Deque[RegimeConditionalAlpha] = deque(maxlen=2000)
        self._cycles_run: List[Dict[str, Any]] = []
        self._halted = False
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.seed + 39, paper_only=True))
        self.of_int = OrderflowAlphaIntegrator(OrderflowAlphaIntegrationConfig32(
            seed=self.seed + 32, paper_only=True, cycles=self.cfg.cycles,
        ))
        self.arb47 = Phase47CrossVenueArbitrageEngine(Phase47Config(seed=self.seed + 47, paper_only=True, cycles=self.cfg.cycles))
        self._sym_state: Dict[str, Dict[str, float]] = {
            u: {"cum_delta": 0.0, "vpin": 0.12, "absorp": 0.25, "imb": 0.0, "sweep": 0.1, "liqvac": 0.15, "agg": 0.2}
            for u in self.cfg.underlyings
        }

    def _id(self, tag: str) -> str:
        with self.lock:
            self._ctr += 1
            return _make_id(self.seed, tag, self._ctr)

    def _regime_from_state(self, cycle: int) -> RegimeSignal:
        # Deterministic regime classification
        r = (self.seed * 131542391 + cycle * 1009) % 997
        if r < 150:
            regime = MarketRegime.CRISIS.value
            conf = 0.85
        elif r < 300:
            regime = MarketRegime.HIGH_VOL.value
            conf = 0.78
        elif r < 550:
            regime = MarketRegime.TRENDING.value
            conf = 0.72
        elif r < 800:
            regime = MarketRegime.LOW_VOL.value
            conf = 0.76
        else:
            regime = MarketRegime.NORMAL.value
            conf = 0.74
        sig = RegimeSignal(
            regime_id=self._id("reg"),
            cycle=cycle,
            timestamp=_utc_now(),
            regime=regime,
            confidence=conf,
            volatility_regime=_finite(min(1.0, max(0.0, 0.3 + (r % 200)/500.0))),
            trend_regime=_finite(min(1.0, max(0.0, 0.25 + ((r+7)%150)/400.0))),
            liquidity_regime=_finite(min(1.0, max(0.0, 0.4 + ((r+13)%100)/250.0))),
            skew_regime=_finite(min(1.0, max(0.0, 0.2 + ((r+17)%180)/600.0))),
            term_structure_regime=_finite(min(1.0, max(0.0, 0.3 + ((r+23)%160)/500.0))),
            paper_only=True,
        )
        with self.lock:
            self._regime_history.append(sig)
        return sig

    def _fuse_orderflow(self, symbol: str, venue: str, cycle: int) -> OrderflowFusionSignal:
        st = self._sym_state.get(symbol, {})
        # Evolve state deterministically
        drift = math.sin((self.seed + cycle) * 0.01) * 0.05
        st["cum_delta"] = _finite(st.get("cum_delta", 0.0) + drift * 10.0)
        st["imb"] = _finite(max(-0.8, min(0.8, st.get("imb", 0.0) + drift)))
        st["vpin"] = _finite(max(0.01, min(0.9, st.get("vpin", 0.12) + (drift * 0.1))))
        st["absorp"] = _finite(max(0.05, min(0.95, st.get("absorp", 0.25) + drift * 0.05)))
        st["sweep"] = _finite(max(0.01, min(0.8, st.get("sweep", 0.1) + drift * 0.03)))
        st["liqvac"] = _finite(max(0.01, min(0.7, st.get("liqvac", 0.15) + drift * 0.02)))
        st["agg"] = _finite(max(0.01, min(0.95, st.get("agg", 0.2) + drift * 0.04)))
        self._sym_state[symbol] = st
        of_score = _finite((abs(st["cum_delta"])/100.0)*0.25 + abs(st["imb"])*0.2 + st["sweep"]*0.2 + st["agg"]*0.2 + st["absorp"]*0.15)
        of_score = max(0.0, min(1.0, of_score))
        tox = _finite(max(0.0, min(1.0, st["vpin"] * 0.6 + st["liqvac"] * 0.4)))
        decay = _finite(max(0.3, min(1.0, 0.9 ** (cycle % 10))))
        sig = OrderflowFusionSignal(
            fusion_id=self._id("of"),
            cycle=cycle,
            timestamp=_utc_now(),
            symbol=symbol,
            venue=venue,
            cumulative_delta=float(st["cum_delta"]),
            imbalance=float(st["imb"]),
            vpin_lite=float(st["vpin"]),
            absorption_score=float(st["absorp"]),
            sweep_score=float(st["sweep"]),
            liquidity_vacuum_score=float(st["liqvac"]),
            aggression_score=float(st["agg"]),
            orderflow_score=of_score,
            toxicity_score=tox,
            decay_factor=decay,
            paper_only=True,
        )
        with self.lock:
            self._of_history.append(sig)
        return sig

    def _select_strategy(self, regime: RegimeSignal, ofsig: OrderflowFusionSignal) -> Tuple[str, float]:
        r = regime.regime
        if r == MarketRegime.CRISIS.value:
            return OptionStrategyType.PROTECTIVE_PUT.value, 0.9
        if r == MarketRegime.HIGH_VOL.value:
            if ofsig.orderflow_score > 0.6:
                return OptionStrategyType.STRADDLE.value, 0.82
            return OptionStrategyType.STRANGLE.value, 0.78
        if r == MarketRegime.TRENDING.value:
            if ofsig.cumulative_delta > 5.0:
                return OptionStrategyType.COVERED_CALL.value, 0.76
            return OptionStrategyType.VERTICAL_SPREAD.value, 0.74
        if r == MarketRegime.LOW_VOL.value:
            return OptionStrategyType.IRON_CONDOR.value, 0.8
        # NORMAL
        if ofsig.sweep_score > 0.4:
            return OptionStrategyType.RATIO_SPREAD.value, 0.72
        return OptionStrategyType.CALENDAR_SPREAD.value, 0.7
