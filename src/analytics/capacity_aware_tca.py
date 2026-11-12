"""Capacity/liquidity-aware transaction cost analysis (TCA) for the crypto options + orderflow strategy.

Implements EVAL-07: a participation-rate cost model with per-venue capacity constraints,
a per-window cost budget, turnover accounting, and net-of-cost out-of-sample walk-forward
evaluation that reuses the EVAL-06 time-varying signal series and walk-forward engine.

Cost model (documented formula, monotone-increasing in participation rate):

    participation_rate  = order_notional_usd / available_venue_liquidity_usd
    realized_cost_bps   = spread_bps + impact_coeff * sqrt(participation_rate)
    cost_usd            = order_notional_usd * realized_cost_bps / 1e4

The square-root impact law is monotone-increasing in participation rate with a linear
spread component. Per-venue capacity is enforced by a max participation rate (default 20%
of observed bar liquidity): orders that would exceed capacity are clamped down to the cap
(never silently filled beyond capacity) and flagged as capacity_limited. A per-window cost
budget (bps of NAV) scales target notionals down so realized cost stays within budget;
utilization = realized_cost_bps / budget_bps is reported per window.

Net-of-cost OOS runs the EVAL-06 signal series through this capacity-aware sizer inside the
walk-forward OOS (WalkForwardBacktest) and reports net return / Sharpe / max-DD per seed and
aggregate versus the EVAL-06 flat-cost baseline. Reuses src.analytics.strategy_evaluation
metrics helpers and src.backtest.engine; bootstrap/permutation logic is NOT duplicated
(EVAL-06 already covers statistical falsification).

Strict-serializable via serialize_metrics_strict / assert_json_valid. Never emits
{"valid": True}.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from src.analytics.strategy_evaluation import compute_metrics
from src.backtest.engine import BacktestConfig, BacktestEngine, RiskConfig, WalkForwardBacktest
from src.campaign.integrated import (
    DEFAULT_SYMBOLS,
    DEFAULT_SPOT,
    DETERMINISTIC_NOW,
    IntegratedConfig,
    _features_for_symbol,
    _generate_price_paths,
    _load_options_chain,
    _load_orderflow,
    _time_varying_signal_series,
)
from src.backtest.engine import (
    BacktestConfig,
    BacktestEngine,
    RegimeShiftConfig,
    RiskConfig,
    WalkForwardBacktest,
    detect_regime_from_window,
)
from src.data.schemas import PricingInputs
from src.features.iv_surface import build_iv_surface_from_chain
from src.features.options_pricing import black_scholes_greeks
from src.signals.composite import CompositeSignalGenerator
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

# ---------------------------------------------------------------------------
# Cost model parameters
# ---------------------------------------------------------------------------

COST_GRID_BPS: Tuple[int, ...] = (0, 1, 5, 10)  # flat-cost baseline levels (one-way bps)
DEFAULT_SPREAD_BPS: float = 0.5          # one-way spread, bps
DEFAULT_IMPACT_COEFF: float = 10.0       # bps per sqrt(participation rate)
DEFAULT_MAX_PARTICIPATION: float = 0.20  # max 20% of bar liquidity per order
DEFAULT_COST_BUDGET_BPS: float = 2.0     # per-window cost budget, bps of NAV
INITIAL_CAPITAL: float = 100000.0
DEFAULT_VENUE: str = "synthetic"
MAX_WINDOWS_SAFETY: int = 1000


class InsufficientCapacity(Exception):
    """Raised deterministically when an order cannot be filled within venue capacity.

    The sizer clamps to the capacity cap by default and never silently fills beyond
    capacity. This exception is raised only when ``raise_on_breach=True`` or no
    positive fill fits within capacity.
    """


@dataclass
class SizingResult:
    """Outcome of sizing one order under capacity + budget constraints."""
    qty: float = 0.0
    notional_usd: float = 0.0
    participation_rate: float = 0.0
    realized_cost_bps: float = 0.0
    cost_usd: float = 0.0
    utilization: float = 0.0  # realized_cost_bps / window budget bps, [0, 1]
    capacity_limited: bool = False
    budget_limited: bool = False
    reason: str = "ok"


@dataclass
class WindowTCA:
    """Per-window TCA accounting."""
    window_index: int = 0
    test_start: int = 0
    test_end: int = 0
    gross_return: float = 0.0
    net_return: float = 0.0  # gross minus cost drag
    cost_bps: float = 0.0    # realized cost, bps of window-start NAV
    cost_usd: float = 0.0
    turnover: float = 0.0    # gross traded notional / window-start NAV
    cost_drag: float = 0.0   # cost_usd / window-start NAV
    budget_utilization: float = 0.0
    num_trades: int = 0
    capacity_limited_orders: int = 0
    budget_limited_orders: int = 0


class CapacityAwareSizer:
    """Participation-rate cost model with capacity constraints and cost budget.

    Formula (documented above):
        participation_rate = order_notional / available_venue_liquidity
        realized_cost_bps  = spread_bps + impact_coeff * sqrt(participation_rate)
        cost_usd           = order_notional * realized_cost_bps / 1e4

    ``realized_cost_bps`` is monotone-increasing in ``participation_rate``.
    """

    def __init__(
        self,
        spread_bps: float = DEFAULT_SPREAD_BPS,
        impact_coeff: float = DEFAULT_IMPACT_COEFF,
        max_participation: float = DEFAULT_MAX_PARTICIPATION,
        cost_budget_bps: float = DEFAULT_COST_BUDGET_BPS,
        seed: int = 42,
        raise_on_breach: bool = False,
    ) -> None:
        if not math.isfinite(spread_bps) or spread_bps < 0:
            raise ValueError("spread_bps must be finite and >= 0")
        if not math.isfinite(impact_coeff) or impact_coeff < 0:
            raise ValueError("impact_coeff must be finite and >= 0")
        if not 0.0 < max_participation <= 1.0:
            raise ValueError("max_participation must be in (0, 1]")
        if not math.isfinite(cost_budget_bps) or cost_budget_bps <= 0:
            raise ValueError("cost_budget_bps must be finite and > 0")
        self.spread_bps = float(spread_bps)
        self.impact_coeff = float(impact_coeff)
        self.max_participation = float(max_participation)
        self.cost_budget_bps = float(cost_budget_bps)
        self.seed = int(seed)
        self.raise_on_breach = bool(raise_on_breach)
        self._base_liquidity: Dict[str, float] = {}
        self._rng = np.random.default_rng(int(seed))

    def _base_liquidity_for(self, symbol: str) -> float:
        """Deterministic base venue liquidity (USD per bar) per symbol."""
        if symbol not in self._base_liquidity:
            draw = float(self._rng.standard_normal())
            liq = 5_000_000.0 * (1.0 + 0.25 * draw)
            self._base_liquidity[symbol] = max(liq, 500_000.0)
        return float(self._base_liquidity[symbol])

    def realized_cost_bps(self, participation_rate: float) -> float:
        """Monotone-increasing realized cost in bps for a participation rate."""
        pr = max(0.0, min(1.0, float(participation_rate)))
        return self.spread_bps + self.impact_coeff * math.sqrt(pr)

    def size(
        self,
        symbol: str,
        target_notional_usd: float,
        price: float,
        bar_index: int,
        realized_vol: float,
        window_budget_remaining_bps: float,
        nav: float,
    ) -> SizingResult:
        """Size one order under capacity + budget constraints.

        The returned qty never exceeds the capacity cap (max_participation * liquidity)
        and never implies cost beyond the window budget (scaled down to fit). Never
        silently over-fills capacity.
        """
        res = SizingResult(reason="ok")
        nav = float(nav) if math.isfinite(nav) and nav > 0 else INITIAL_CAPITAL
        target_notional_usd = (
            float(target_notional_usd) if math.isfinite(target_notional_usd) else 0.0
        )
        price = float(price) if math.isfinite(price) and price > 0 else 0.0
        if target_notional_usd <= 0.0 or price <= 0.0:
            return res

        liquidity = VenueLiquidity(
            symbol, DEFAULT_VENUE, self._base_liquidity_for(symbol), 1.0
        ).liquidity_usd(bar_index, realized_vol)

        # Capacity cap on notional: max_participation * bar liquidity.
        cap_notional = self.max_participation * liquidity
        qty_target = target_notional_usd / price
        qty_cap = cap_notional / price
        qty = min(qty_target, qty_cap)
        capacity_limited = qty < qty_target - 1e-9
        res.capacity_limited = capacity_limited

        notional = qty * price
        pr = notional / liquidity if liquidity > 0 else 0.0
        pr = max(0.0, min(1.0, pr))
        cost_bps = self.realized_cost_bps(pr)
        cost_usd = notional * cost_bps / 1e4

        # Per-window cost budget: scale down so cost_usd <= remaining budget.
        budget_usd = (
            min(window_budget_remaining_bps, self.cost_budget_bps) * nav / 1e4
        )
        budget_usd = max(budget_usd, 0.0)
        budget_limited = False
        if cost_usd > budget_usd + 1e-9 and cost_usd > 0:
            scale = budget_usd / cost_usd
            scale = max(0.0, min(1.0, scale))
            qty *= scale
            notional = qty * price
            pr = notional / liquidity if liquidity > 0 else 0.0
            pr = max(0.0, min(1.0, pr))
            cost_bps = self.realized_cost_bps(pr)
            cost_usd = notional * cost_bps / 1e4
            budget_limited = True
            res.budget_limited = True

        res.capacity_limited = capacity_limited or budget_limited
        if not math.isfinite(qty) or qty <= 0 or notional <= 0:
            return res

        res.qty = float(qty)
        res.notional_usd = float(notional)
        res.participation_rate = float(pr)
        res.realized_cost_bps = float(cost_bps)
        res.cost_usd = float(cost_usd)
        res.utilization = (
            float(min(cost_bps / max(self.cost_budget_bps, 1e-9), 1.0))
            if self.cost_budget_bps > 0
            else 0.0
        )
        res.reason = "ok"
        return res


class VenueLiquidity:
    """Deterministic per-venue, per-symbol observed bar liquidity (USD)."""

    def __init__(self, symbol: str, venue: str, base_liquidity_usd: float, vol_scale: float) -> None:
        self.symbol = symbol
        self.venue = venue
        self.base_liquidity_usd = float(base_liquidity_usd)
        self.vol_scale = float(vol_scale)

    def liquidity_usd(self, bar_index: int, realized_vol: float) -> float:
        """Deterministic liquidity for a bar (trailing-only, no lookahead)."""
        liq = self.base_liquidity_usd * max(self.vol_scale, 1e-6)
        liq *= 1.0 + 0.1 * math.sin(0.017 * float(bar_index))  # bounded, deterministic
        liq *= max(0.5, min(2.0, 1.0 + float(realized_vol)))  # vol-adj, bounded
        if not math.isfinite(liq) or liq <= 0:
            return self.base_liquidity_usd
        return float(liq)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _finite(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if math.isfinite(v) else default


def _sharpe_of_returns(rets: List[float], periods_per_year: float = 252.0) -> float:
    vals = [float(r) for r in rets if math.isfinite(float(r))]
    if len(vals) < 2:
        return 0.0
    mean = sum(vals) / len(vals)
    std = math.sqrt(sum((r - mean) ** 2 for r in vals) / len(vals))
    if std <= 0.0 or not math.isfinite(std):
        return 0.0
    sr = mean / std * math.sqrt(periods_per_year)
    return sr if math.isfinite(sr) else 0.0


def _path_regime(index: int, n_points: int) -> str:
    block_len = max(1, n_points // 4)
    bi = min(index // block_len, 3)
    return ("trend", "range", "high_vol_chop", "thin")[bi]


def _window_regime(test_start: int, test_end: int, n_points: int) -> str:
    mid = (test_start + test_end) // 2
    return _path_regime(mid, n_points)


def _vol_regime(prices: List[float], start: int, end: int) -> str:
    seg = [float(p) for p in prices[max(0, start):end] if _finite(p) > 0]
    return detect_regime_from_window(seg)


def _build_signal_series_capacity(
    sym: str,
    prices: List[float],
    static_features: Dict[str, Any],
    static_context: Dict[str, Any],
    seed: int,
) -> Tuple[List[int], List[Dict[str, Any]]]:
    """Build the EVAL-06 time-varying signal series for one symbol (reused verbatim)."""
    signal_gen = CompositeSignalGenerator()
    signal_gen.reset_regime_state()
    series, diagnostics = _time_varying_signal_series(
        signal_gen,
        sym,
        list(prices),
        static_features,
        static_context["chain"],
        static_context["iv_surface"],
        static_context["greeks_summary"],
    )
    return series, diagnostics


def _static_context_capacity(
    sym: str, spot: float, now: datetime, seed: int
) -> Dict[str, Any]:
    chain = _load_options_chain(sym, spot, now, DEFAULT_VENUE)
    of = _load_orderflow(sym, DEFAULT_VENUE)
    try:
        iv_surface = build_iv_surface_from_chain(chain, spot=spot, rate=0.0, now=now, seed=seed)
    except Exception:
        iv_surface = None
    greeks_summary: Optional[Dict[str, Any]] = None
    if chain.quotes:
        atm = min(chain.quotes, key=lambda q: abs(float(q.contract.strike) - spot))
        try:
            texp = max((atm.contract.expiry - now).total_seconds() / 86400.0 / 365.0, 1e-6)
            g = black_scholes_greeks(
                PricingInputs(
                    spot=spot,
                    strike=float(atm.contract.strike),
                    rate=0.0,
                    volatility=_finite(getattr(atm, "mark_iv", None), 0.8),
                    time_to_expiry=texp,
                    option_type=atm.contract.option_type,
                    seed=seed,
                )
            )
            greeks_summary = {
                "delta": g["delta"],
                "gamma": g["gamma"],
                "vega": g["vega"],
                "theta": g["theta"],
                "rho": g["rho"],
            }
        except Exception:
            greeks_summary = None
    features = _features_for_symbol(sym, spot, chain, of, iv_surface, greeks_summary, CompositeSignalGenerator())
    return {"chain": chain, "iv_surface": iv_surface, "greeks_summary": greeks_summary, "features": features}


def _run_capacity_aware_walkforward(
    symbol: str,
    prices: List[float],
    signals: List[int],
    timestamps: List[datetime],
    sizer: CapacityAwareSizer,
    cfg: IntegratedConfig,
    n_points: int,
    seed: int,
) -> Dict[str, Any]:
    """Run OOS walk-forward for one symbol with capacity-aware sizing.

    Mirrors the EVAL-06 engine windowing (train/test, purge/embargo) but sizes every
    order through ``CapacityAwareSizer`` and tracks per-window cost, turnover and
    budget utilization. Net return = gross return - cost drag (cost_usd / window NAV).
    """
    wfb = WalkForwardBacktest(
        purge=cfg.purge,
        embargo=cfg.embargo,
        config=BacktestConfig(
            initial_capital=INITIAL_CAPITAL,
            fee_rate=0.0,
            slippage_bps=0.0,
            slippage_seed=seed,
            risk_free_rate=0.0,
        ),
        risk_config=RiskConfig(),
    )
    wfres = wfb.run_walk_forward(
        price_series={symbol: list(prices)},
        signals={symbol: list(signals)},
        timestamps=list(timestamps),
        train_window=cfg.train_window,
        test_window=cfg.test_window,
        step_size=cfg.step_size,
        rolling=True,
        anchored=False,
        min_train_size=40,
        purge=cfg.purge,
        embargo=cfg.embargo,
    )

    windows: List[Dict[str, Any]] = []
    all_cost_usd = 0.0
    all_notional = 0.0
    all_trades = 0
    total_capacity_limited = 0
    total_budget_limited = 0
    regime_buckets: Dict[str, List[float]] = {}

    for w in wfres.windows:
        # Re-simulate the window with capacity-aware sizing to capture cost/turnover.
        oos_engine = BacktestEngine(
            BacktestConfig(
                initial_capital=INITIAL_CAPITAL,
                fee_rate=0.0,
                slippage_bps=0.0,
                slippage_seed=seed,
                risk_free_rate=0.0,
            ),
            RiskConfig(),
        )
        nav_at_start = INITIAL_CAPITAL
        window_cost_usd = 0.0
        window_notional = 0.0
        window_trades = 0
        window_cap_limited = 0
        window_budget_limited = 0
        budget_remaining_bps = sizer.cost_budget_bps

        start = w.test_start
        end = w.test_end
        if end <= start:
            continue
        end = min(end, len(prices))
        start = max(0, start)
        if start >= end:
            continue

        prev_equity = INITIAL_CAPITAL
        for i in range(start, end):
            px = _finite(prices[i], 0.0)
            if px <= 0.0:
                continue
            ts = timestamps[i] if i < len(timestamps) else DETERMINISTIC_NOW
            sig = signals[i] if i < len(signals) else 0
            if not math.isfinite(sig):
                sig = 0
            current_prices = {symbol: px}
            realized_vol = 0.0
            if i >= 2:
                rets = []
                for j in range(max(1, i - 20), i + 1):
                    p0 = _finite(prices[j - 1], 0.0)
                    p1 = _finite(prices[j], 0.0)
                    if p0 > 0.0 and p1 > 0.0:
                        rets.append(math.log(p1 / p0))
                if len(rets) >= 2:
                    m = sum(rets) / len(rets)
                    realized_vol = math.sqrt(max(sum((r - m) ** 2 for r in rets) / len(rets), 0.0))

            if sig == 1 and symbol not in oos_engine.positions:
                # Target notional: signal strength converted via max_position_pct of NAV.
                nav = oos_engine.get_equity(current_prices)
                if nav <= 0:
                    nav = INITIAL_CAPITAL
                target_notional = abs(1.0) * cfg.max_position_pct * nav  # full-strength entry
                result = sizer.size(
                    symbol, target_notional, px, i, realized_vol, budget_remaining_bps, nav,
                )
                if result.qty > 0:
                    try:
                        oos_engine.execute_trade(symbol, result.qty, px, "buy", ts)
                    except Exception:
                        pass
                    window_cost_usd += result.cost_usd
                    window_notional += result.notional_usd
                    window_trades += 1
                    budget_remaining_bps -= result.realized_cost_bps * (
                        result.notional_usd / max(nav, 1.0)
                    )
                    if result.capacity_limited:
                        window_cap_limited += 1
                    if result.budget_limited:
                        window_budget_limited += 1
            elif sig == -1:
                if symbol in oos_engine.positions and oos_engine.positions[symbol].side == "long":
                    pos = oos_engine.positions[symbol]
                    nav = oos_engine.get_equity(current_prices)
                    if nav <= 0:
                        nav = INITIAL_CAPITAL
                    result = sizer.size(
                        symbol,
                        pos.quantity * px,
                        px,
                        i,
                        realized_vol,
                        budget_remaining_bps,
                        nav,
                    )
                    if result.qty > 0:
                        try:
                            oos_engine.execute_trade(symbol, min(result.qty, pos.quantity), px, "sell", ts)
                        except Exception:
                            pass
                        window_cost_usd += result.cost_usd
                        window_notional += result.notional_usd
                        window_trades += 1
                        budget_remaining_bps -= result.realized_cost_bps * (
                            result.notional_usd / max(nav, 1.0)
                        )
                        if result.capacity_limited:
                            window_cap_limited += 1
                        if result.budget_limited:
                            window_budget_limited += 1

            oos_engine.update_equity_curve(current_prices)

        equity_curve = [float(e) for e in oos_engine.equity_curve if math.isfinite(float(e))]
        if len(equity_curve) < 2:
            gross_ret = 0.0
        else:
            gross_ret = (equity_curve[-1] - equity_curve[0]) / equity_curve[0]
        cost_drag = window_cost_usd / max(nav_at_start, 1.0)
        turnover = window_notional / max(nav_at_start, 1.0)
        net_ret = gross_ret - cost_drag
        regime = _window_regime(w.test_start, w.test_end, n_points)
        regime_buckets.setdefault(regime, []).append(net_ret)

        windows.append(
            {
                "window_index": len(windows),
                "train_start": w.train_start,
                "train_end": w.train_end,
                "test_start": w.test_start,
                "test_end": w.test_end,
                "gross_return": float(gross_ret),
                "net_return": float(net_ret),
                "cost_bps": float(window_cost_usd / max(nav_at_start, 1.0) * 1e4),
                "cost_usd": float(window_cost_usd),
                "turnover": float(turnover),
                "cost_drag": float(cost_drag),
                "budget_utilization": float(
                    min((sizer.cost_budget_bps - max(budget_remaining_bps, 0.0)) / max(sizer.cost_budget_bps, 1e-9), 1.0)
                ),
                "num_trades": int(window_trades),
                "capacity_limited_orders": int(window_cap_limited),
                "budget_limited_orders": int(window_budget_limited),
                "regime": regime,
                "vol_regime": _vol_regime(prices, w.test_start, w.test_end),
            }
        )

        all_cost_usd += window_cost_usd
        all_notional += window_notional
        all_trades += window_trades
        total_capacity_limited += window_cap_limited
        total_budget_limited += window_budget_limited

    net_returns = [win["net_return"] for win in windows]
    equity = [INITIAL_CAPITAL]
    for r in net_returns:
        equity.append(equity[-1] * (1.0 + r))
    total_return = (equity[-1] / equity[0] - 1.0) if equity[0] > 0 else 0.0
    sharpe = _sharpe_of_returns(net_returns)
    mdd = 0.0
    peak = equity[0]
    for v in equity:
        if v > peak:
            peak = v
        dd = (peak - v) / peak if peak > 0 else 0.0
        if dd > mdd:
            mdd = dd

    total_turnover = all_notional / max(INITIAL_CAPITAL * max(len(windows), 1), 1.0)
    avg_cost_bps = (all_cost_usd / max(INITIAL_CAPITAL, 1.0)) * 1e4 / max(len(windows), 1)

    regime_perf = {}
    for regime, rs in regime_buckets.items():
        regime_perf[regime] = {
            "num_windows": len(rs),
            "mean_return": float(sum(rs) / len(rs)) if rs else 0.0,
            "sharpe": float(_sharpe_of_returns(rs)),
            "trade_count": 0,
        }

    result: Dict[str, Any] = {
        "symbol": symbol,
        "spread_bps": sizer.spread_bps,
        "impact_coeff": sizer.impact_coeff,
        "max_participation": sizer.max_participation,
        "cost_budget_bps": sizer.cost_budget_bps,
        "seed": int(seed),
        "num_windows": len(windows),
        "oos_trade_count": int(all_trades),
        "oos_return": float(total_return),
        "oos_sharpe": float(sharpe),
        "oos_max_drawdown": float(mdd),
        "total_cost_usd": float(all_cost_usd),
        "total_traded_notional": float(all_notional),
        "avg_cost_bps": float(avg_cost_bps),
        "avg_turnover": float(total_turnover),
        "capacity_limited_orders": int(total_capacity_limited),
        "budget_limited_orders": int(total_budget_limited),
        "purge": cfg.purge,
        "embargo": cfg.embargo,
        "train_window": cfg.train_window,
        "test_window": cfg.test_window,
        "step_size": cfg.step_size,
        "per_window": windows,
        "oos_equity_curve": [float(v) for v in equity],
        "regime_performance": regime_perf,
        "regime_coverage": {k: len(v) for k, v in regime_buckets.items()},
    }
    assert_json_valid(result)
    return result


def _evaluate_seed_capacity(
    seed: int,
    n_points: int,
    train_window: int,
    test_window: int,
    step_size: int,
    purge: int,
    embargo: int,
    spread_bps: float,
    impact_coeff: float,
    max_participation: float,
    cost_budget_bps: float,
) -> Dict[str, Any]:
    """Evaluate one seed across BTC/ETH/SOL under capacity-aware TCA + flat baseline."""
    cfg = IntegratedConfig(
        seed=seed,
        n_points=n_points,
        train_window=train_window,
        test_window=test_window,
        step_size=step_size,
        purge=purge,
        embargo=embargo,
    )
    now = cfg.fixed_now or DETERMINISTIC_NOW
    price_series, timestamps = _generate_price_paths(cfg)
    per_symbol: Dict[str, Dict[str, Any]] = {}
    static_contexts: Dict[str, Dict[str, Any]] = {}
    for sym in cfg.symbols:
        spot = float(cfg.spot_prices.get(sym, DEFAULT_SPOT[sym]))
        static_contexts[sym] = _static_context_capacity(sym, spot, now, seed)
    signals: Dict[str, List[int]] = {}
    for sym in cfg.symbols:
        series, _diag = _build_signal_series_capacity(
            sym, price_series[sym], static_contexts[sym]["features"], static_contexts[sym], seed
        )
        signals[sym] = series

    # Capacity-aware run per symbol.
    sizer = CapacityAwareSizer(
        spread_bps=spread_bps,
        impact_coeff=impact_coeff,
        max_participation=max_participation,
        cost_budget_bps=cost_budget_bps,
        seed=seed,
    )
    cap_by_sym: Dict[str, Dict[str, Any]] = {}
    for sym in cfg.symbols:
        cap_by_sym[sym] = _run_capacity_aware_walkforward(
            sym,
            price_series[sym],
            signals[sym],
            timestamps,
            sizer,
            cfg,
            n_points,
            seed,
        )

    # Flat-cost baseline run per symbol (fixed bps, no capacity model).
    baseline_by_sym: Dict[str, Dict[str, Any]] = {}
    for bps in COST_GRID_BPS:
        baseline_by_sym[str(bps)] = {}
        for sym in cfg.symbols:
            base = _run_capacity_aware_walkforward(
                sym,
                price_series[sym],
                signals[sym],
                timestamps,
                CapacityAwareSizer(
                    spread_bps=float(bps),
                    impact_coeff=0.0,
                    max_participation=1.0,  # no effective capacity cap at baseline
                    cost_budget_bps=max(float(bps) * 10.0, 1.0),  # non-binding budget (>0)
                    seed=seed,
                ),
                cfg,
                n_points,
                seed,
            )
            baseline_by_sym[str(bps)][sym] = base

    # Portfolio (equal weight) per cost level: average per-window net returns.
    def portfolio_from(sym_results: Dict[str, Dict[str, Any]], n_windows_override: Optional[int] = None) -> Dict[str, Any]:
        n_windows = 0
        trades = 0
        windows_per_sym: Dict[str, List[float]] = {}
        for sym in cfg.symbols:
            res = sym_results[sym]
            windows_per_sym[sym] = [win["net_return"] for win in res["per_window"]]
            n_windows = max(n_windows, res["num_windows"])
            trades += res["oos_trade_count"]
        port_returns: List[float] = []
        nw = n_windows_override if n_windows_override is not None else n_windows
        for i in range(nw):
            vals = [windows_per_sym[s][i] for s in cfg.symbols if i < len(windows_per_sym[s])]
            if vals:
                port_returns.append(sum(vals) / len(vals))
        equity = [INITIAL_CAPITAL]
        for r in port_returns:
            equity.append(equity[-1] * (1.0 + r))
        total_return = (equity[-1] / equity[0] - 1.0) if equity[0] > 0 else 0.0
        sharpe = _sharpe_of_returns(port_returns)
        mdd = 0.0
        peak = equity[0]
        for v in equity:
            if v > peak:
                peak = v
            dd = (peak - v) / peak if peak > 0 else 0.0
            if dd > mdd:
                mdd = dd
        return {
            "num_windows": int(nw),
            "oos_trade_count": int(trades),
            "oos_return": float(total_return),
            "oos_sharpe": float(sharpe),
            "oos_max_drawdown": float(mdd),
            "per_window_returns": port_returns,
            "oos_equity_curve": [float(v) for v in equity],
        }

    portfolio_capacity = portfolio_from(cap_by_sym)
    portfolio_capacity["avg_turnover"] = float(
        sum(cap_by_sym[s]["avg_turnover"] for s in cfg.symbols) / len(cfg.symbols)
    )
    portfolio_capacity["avg_cost_bps"] = float(
        sum(cap_by_sym[s]["avg_cost_bps"] for s in cfg.symbols) / len(cfg.symbols)
    )
    portfolio_by_bps: Dict[str, Dict[str, Any]] = {}
    for bps in COST_GRID_BPS:
        key = str(bps)
        portfolio_by_bps[key] = portfolio_from(baseline_by_sym[key])

    capacity_net = portfolio_capacity
    baseline_net = portfolio_by_bps["0"]

    return {
        "seed": int(seed),
        "symbols": {sym: cap_by_sym[sym] for sym in cfg.symbols},
        "symbols_baseline": {sym: baseline_by_sym["1"][sym] for sym in cfg.symbols},
        "cost_grid": {
            k: {kk: vv for kk, vv in v.items() if kk not in ("per_window", "per_window_returns", "oos_equity_curve")}
            for k, v in portfolio_by_bps.items()
        },
        "capacity": {k: v for k, v in capacity_net.items() if k not in ("per_window", "per_window_returns", "oos_equity_curve")},
        "baseline": {k: v for k, v in baseline_net.items() if k not in ("per_window", "per_window_returns", "oos_equity_curve")},
        "spread_bps": spread_bps,
        "impact_coeff": impact_coeff,
        "max_participation": max_participation,
        "cost_budget_bps": cost_budget_bps,
        "total_capacity_limited_orders": sum(cap_by_sym[s]["capacity_limited_orders"] for s in cfg.symbols),
        "total_budget_limited_orders": sum(cap_by_sym[s]["budget_limited_orders"] for s in cfg.symbols),
    }


def evaluate_capacity_aware_tca(
    seeds: Optional[List[int]] = None,
    n_points: int = 500,
    train_window: int = 120,
    test_window: int = 40,
    step_size: int = 40,
    purge: int = 10,
    embargo: int = 5,
    spread_bps: float = DEFAULT_SPREAD_BPS,
    impact_coeff: float = DEFAULT_IMPACT_COEFF,
    max_participation: float = DEFAULT_MAX_PARTICIPATION,
    cost_budget_bps: float = DEFAULT_COST_BUDGET_BPS,
) -> Dict[str, Any]:
    """Run capacity-aware TCA OOS evaluation across seeds; strict-serializable report."""
    if seeds is None:
        seeds = [1, 2, 3, 4, 5]
    seeds = [int(s) for s in seeds]

    per_seed: List[Dict[str, Any]] = []
    for seed in seeds:
        per_seed.append(
            _evaluate_seed_capacity(
                seed,
                n_points,
                train_window,
                test_window,
                step_size,
                purge,
                embargo,
                spread_bps,
                impact_coeff,
                max_participation,
                cost_budget_bps,
            )
        )

    capacity_sharpes = [float(r["capacity"]["oos_sharpe"]) for r in per_seed]
    capacity_returns = [float(r["capacity"]["oos_return"]) for r in per_seed]
    baseline_sharpes = [float(r["baseline"]["oos_sharpe"]) for r in per_seed]
    baseline_returns = [float(r["baseline"]["oos_return"]) for r in per_seed]

    cost_grid_agg: Dict[str, Dict[str, Any]] = {}
    for bps in COST_GRID_BPS:
        key = str(bps)
        sh = [r["cost_grid"][key]["oos_sharpe"] for r in per_seed]
        rt = [r["cost_grid"][key]["oos_return"] for r in per_seed]
        cost_grid_agg[key] = {
            "bps": float(bps),
            "mean_net_sharpe": float(sum(sh) / len(sh)) if sh else 0.0,
            "mean_net_return": float(sum(rt) / len(rt)) if rt else 0.0,
        }

    aggregate = {
        "seeds": [int(s) for s in seeds],
        "num_seeds": int(len(seeds)),
        "mean_capacity_net_sharpe": float(sum(capacity_sharpes) / len(capacity_sharpes)) if capacity_sharpes else 0.0,
        "mean_capacity_net_return": float(sum(capacity_returns) / len(capacity_returns)) if capacity_returns else 0.0,
        "mean_baseline_net_sharpe": float(sum(baseline_sharpes) / len(baseline_sharpes)) if baseline_sharpes else 0.0,
        "mean_baseline_net_return": float(sum(baseline_returns) / len(baseline_returns)) if baseline_returns else 0.0,
        "capacity_vs_baseline_sharpe": float(
            (sum(capacity_sharpes) / len(capacity_sharpes)) - (sum(baseline_sharpes) / len(baseline_sharpes))
        ) if capacity_sharpes else 0.0,
        "capacity_vs_baseline_return": float(
            (sum(capacity_returns) / len(capacity_returns)) - (sum(baseline_returns) / len(baseline_returns))
        ) if capacity_returns else 0.0,
        "cost_grid": cost_grid_agg,
        "spread_bps": float(spread_bps),
        "impact_coeff": float(impact_coeff),
        "max_participation": float(max_participation),
        "cost_budget_bps": float(cost_budget_bps),
        "total_capacity_limited_orders": int(sum(r["total_capacity_limited_orders"] for r in per_seed)),
        "total_budget_limited_orders": int(sum(r["total_budget_limited_orders"] for r in per_seed)),
    }

    report: Dict[str, Any] = {
        "report_id": "CAPACITY_AWARE_TCA_EVAL_07",
        "generated_at": _utc_now_iso(),
        "config": {
            "seeds": [int(s) for s in seeds],
            "n_points": int(n_points),
            "train_window": int(train_window),
            "test_window": int(test_window),
            "step_size": int(step_size),
            "purge": int(purge),
            "embargo": int(embargo),
            "spread_bps": float(spread_bps),
            "impact_coeff": float(impact_coeff),
            "max_participation": float(max_participation),
            "cost_budget_bps": float(cost_budget_bps),
            "symbols": list(DEFAULT_SYMBOLS),
            "initial_capital": INITIAL_CAPITAL,
            "cost_grid_bps": [int(b) for b in COST_GRID_BPS],
        },
        "per_seed": per_seed,
        "aggregate": aggregate,
        "never_valid_true": True,
    }
    assert_json_valid(report)
    return serialize_metrics_strict(report)


def _write_markdown(report: Dict[str, Any]) -> str:
    agg = report["aggregate"]
    cfg = report["config"]
    lines: List[str] = []
    lines.append("# CAPACITY-AWARE TCA REPORT — EVAL-07")
    lines.append("")
    lines.append(f"- Report ID: {report['report_id']}")
    lines.append(f"- Generated at: {report['generated_at']}")
    lines.append(f"- Symbols: {', '.join(cfg['symbols'])}")
    lines.append(f"- Seeds: {cfg['seeds']}")
    lines.append(f"- Spread: {cfg['spread_bps']} bps | Impact coeff: {cfg['impact_coeff']} bps/sqrt(pr)")
    lines.append(f"- Max participation: {cfg['max_participation']} | Cost budget: {cfg['cost_budget_bps']} bps/window")
    lines.append("")
    lines.append("## AGGREGATE (capacity-aware vs flat-cost baseline)")
    lines.append("")
    for k in (
        "num_seeds",
        "mean_capacity_net_sharpe",
        "mean_capacity_net_return",
        "mean_baseline_net_sharpe",
        "mean_baseline_net_return",
        "capacity_vs_baseline_sharpe",
        "capacity_vs_baseline_return",
        "total_capacity_limited_orders",
        "total_budget_limited_orders",
    ):
        lines.append(f"- {k}: {agg[k]}")
    lines.append("")
    lines.append("## Cost grid (mean net Sharpe / net return across seeds, flat baseline)")
    lines.append("")
    for key in sorted(report["aggregate"]["cost_grid"], key=lambda k: float(report["aggregate"]["cost_grid"][k]["bps"])):
        v = report["aggregate"]["cost_grid"][key]
        lines.append(f"- {v['bps']} bps: net_sharpe={v['mean_net_sharpe']:.6f}, net_return={v['mean_net_return']:.6f}")
    lines.append("")
    lines.append("## Per-seed summary (capacity-aware)")
    lines.append("")
    for r in report["per_seed"]:
        cap = r["capacity"]
        base = r["baseline"]
        lines.append(
            f"- seed {r['seed']}: capacity net_sharpe={cap['oos_sharpe']:.6f}, net_return={cap['oos_return']:.6f}, "
            f"max_dd={cap['oos_max_drawdown']:.6f}, trades={cap['oos_trade_count']}, windows={cap['num_windows']} | "
            f"baseline net_sharpe={base['oos_sharpe']:.6f}, net_return={base['oos_return']:.6f}"
        )
    lines.append("")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Capacity/liquidity-aware TCA net-of-cost OOS evaluation (EVAL-07)"
    )
    parser.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3, 4, 5])
    parser.add_argument("--n-points", type=int, default=500)
    parser.add_argument("--train-window", type=int, default=120)
    parser.add_argument("--test-window", type=int, default=40)
    parser.add_argument("--step-size", type=int, default=40)
    parser.add_argument("--purge", type=int, default=10)
    parser.add_argument("--embargo", type=int, default=5)
    parser.add_argument("--spread-bps", type=float, default=DEFAULT_SPREAD_BPS)
    parser.add_argument("--impact-coeff", type=float, default=DEFAULT_IMPACT_COEFF)
    parser.add_argument("--max-participation", type=float, default=DEFAULT_MAX_PARTICIPATION)
    parser.add_argument("--cost-budget-bps", type=float, default=DEFAULT_COST_BUDGET_BPS)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--timestamp", type=str, default=_utc_now_iso())
    args = parser.parse_args(argv)

    ts = args.timestamp.replace(":", "").replace("-", "").replace("T", "").replace("Z", "").split(".")[0]
    stamp = f"{ts[:8]}T{ts[8:14]}Z" if len(ts) >= 14 else ts

    report = evaluate_capacity_aware_tca(
        seeds=args.seeds,
        n_points=args.n_points,
        train_window=args.train_window,
        test_window=args.test_window,
        step_size=args.step_size,
        purge=args.purge,
        embargo=args.embargo,
        spread_bps=args.spread_bps,
        impact_coeff=args.impact_coeff,
        max_participation=args.max_participation,
        cost_budget_bps=args.cost_budget_bps,
    )

    print(
        json.dumps(
            {
                "report_id": report["report_id"],
                "num_seeds": report["aggregate"]["num_seeds"],
                "mean_capacity_net_sharpe": report["aggregate"]["mean_capacity_net_sharpe"],
                "mean_capacity_net_return": report["aggregate"]["mean_capacity_net_return"],
                "mean_baseline_net_sharpe": report["aggregate"]["mean_baseline_net_sharpe"],
                "mean_baseline_net_return": report["aggregate"]["mean_baseline_net_return"],
                "capacity_vs_baseline_sharpe": report["aggregate"]["capacity_vs_baseline_sharpe"],
                "capacity_vs_baseline_return": report["aggregate"]["capacity_vs_baseline_return"],
                "total_capacity_limited_orders": report["aggregate"]["total_capacity_limited_orders"],
                "total_budget_limited_orders": report["aggregate"]["total_budget_limited_orders"],
                "cost_grid": report["aggregate"]["cost_grid"],
            },
            indent=2,
        )
    )

    if args.write:
        RESEARCH_STATE = Path("research_state")
        RESEARCH_STATE.mkdir(parents=True, exist_ok=True)
        stem = f"CAPACITY_AWARE_TCA_{stamp}"
        json_path = RESEARCH_STATE / f"{stem}.json"
        md_path = RESEARCH_STATE / f"{stem}.md"
        json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        md_path.write_text(_write_markdown(report) + "\n", encoding="utf-8")
        print(f"Wrote {json_path}")
        print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
