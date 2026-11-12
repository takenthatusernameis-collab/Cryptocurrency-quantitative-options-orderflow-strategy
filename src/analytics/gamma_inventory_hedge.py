"""Gamma/inventory-aware hedge sizing + orderflow-toxicity gating (EVAL-09).

Risk-efficiency layer for the crypto options + orderflow net-of-cost evaluation.
After delta is netted across venues (EVAL-08), the remaining capital-efficiency
and risk levers are **gamma/inventory** (how much of the book's convexity to
hedge, and how inventory skews quoting) and **orderflow toxicity** (whether
incoming flow is informed — toxic flow must widen spreads or stand down, benign
flow should be absorbed). These are the last two layers before the final
net-of-cost GO/NO-GO (EVAL-10).

Model (documented, deterministic, no network / no venue API / no credentials):

    for each symbol and each OOS bar:
        net_delta_usd   = position_qty * price * option_delta      (from EVAL-07
                                                      static greeks snapshot)
        delta_gap       = net_delta_usd - target_delta_usd         (target ~ 0)
        capacity_cap    = sum over venues of max_participation * venue_liquidity
        hedge_notional  = min(abs(delta_gap), capacity_cap)
        side            = opposite of sign(delta_gap)              (hedge toward 0)
        hedge_cost_usd  = hedge_notional * realized_cost_bps / 1e4

    toxicity_score      = VPIN-style bucketed signed-volume imbalance over the
                          causal trailing orderflow (trades <= bar timestamp only
                          — no lookahead), in [0, 1].
        if toxicity_score >= threshold (default 0.7):
            toxic_gate_active = True; quoting/hedge is skipped (orders_skipped++)
        else:
            quote normally (orders_quoted++)

Net-of-cost OOS runs the EVAL-06/07/08 signal series through the gamma/inventory
hedge and the toxicity gate inside the walk-forward OOS and reports net return /
Sharpe / max-DD per seed and aggregate, WITH hedge+gate vs WITHOUT. Reuses
``src.analytics.strategy_evaluation.compute_metrics`` and
``src.backtest.engine``; bootstrap/permutation logic is NOT duplicated
(EVAL-06 owns it).

Strict-serializable via ``serialize_metrics_strict`` / ``assert_json_valid``.
Never emits ``{"valid": True}``.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from src.analytics.capacity_aware_tca import (
    CapacityAwareSizer,
    DEFAULT_IMPACT_COEFF,
    DEFAULT_MAX_PARTICIPATION,
    DEFAULT_SPREAD_BPS,
    INITIAL_CAPITAL,
    _build_signal_series_capacity,
    _static_context_capacity,
)
from src.analytics.cross_venue_netting import (
    VENUES,
    _leg_liquidity,
)
from src.analytics.strategy_evaluation import compute_metrics
from src.backtest.engine import BacktestConfig, BacktestEngine, RiskConfig, WalkForwardBacktest
from src.campaign.integrated import (
    DEFAULT_SPOT,
    DEFAULT_SYMBOLS,
    DETERMINISTIC_NOW,
    IntegratedConfig,
    _generate_price_paths,
    _load_orderflow,
    _stable_seed,
)
from src.data.schemas import OrderflowSnapshot, Trade
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

# ---------------------------------------------------------------------------
# Hedge + toxicity parameters
# ---------------------------------------------------------------------------

DEFAULT_TOXICITY_THRESHOLD: float = 0.7
DEFAULT_TARGET_DELTA_USD: float = 0.0          # bring net delta to flat
DEFAULT_TOXICITY_WINDOW_TRADES: int = 5        # trailing causal trades for toxicity
DEFAULT_HEDGE_COST_BPS: float = 1.0            # one-way hedge cost (bps)
DEFAULT_COST_BUDGET_BPS: float = 2.0           # per-window cost budget, bps of NAV
DELTA_TOL: float = 1e-6

DEFAULT_SPREAD_BPS_HEDGE: float = DEFAULT_SPREAD_BPS
DEFAULT_IMPACT_COEFF_HEDGE: float = DEFAULT_IMPACT_COEFF
DEFAULT_MAX_PARTICIPATION_HEDGE: float = DEFAULT_MAX_PARTICIPATION


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _finite(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if math.isfinite(v) else default


def _sharpe_of_returns(rets: Sequence[float], periods_per_year: float = 252.0) -> float:
    vals = [float(r) for r in rets if math.isfinite(float(r))]
    if len(vals) < 2:
        return 0.0
    mean = sum(vals) / len(vals)
    std = math.sqrt(sum((r - mean) ** 2 for r in vals) / len(vals))
    if std <= 0.0 or not math.isfinite(std):
        return 0.0
    sr = mean / std * math.sqrt(periods_per_year)
    return sr if math.isfinite(sr) else 0.0


def _max_drawdown(equity: Sequence[float]) -> float:
    mdd = 0.0
    peak = equity[0] if equity else 0.0
    for v in equity:
        if v > peak:
            peak = v
        dd = (peak - v) / peak if peak > 0 else 0.0
        if dd > mdd:
            mdd = dd
    return float(mdd)


def _path_regime(index: int, n_points: int) -> str:
    block_len = max(1, n_points // 4)
    bi = min(index // block_len, 3)
    return ("trend", "range", "high_vol_chop", "thin")[bi]


def _realized_vol(prices: Sequence[float], i: int, lookback: int = 20) -> float:
    """Trailing realized vol (causal, no lookahead). 0.0 when undefined."""
    if i < 2:
        return 0.0
    rets: List[float] = []
    for j in range(max(1, i - lookback), i + 1):
        p0 = _finite(prices[j - 1], 0.0)
        p1 = _finite(prices[j], 0.0)
        if p0 > 0.0 and p1 > 0.0:
            rets.append(math.log(p1 / p0))
    if len(rets) < 2:
        return 0.0
    m = sum(rets) / len(rets)
    var = sum((r - m) ** 2 for r in rets) / len(rets)
    return math.sqrt(max(var, 0.0))


# ---------------------------------------------------------------------------
# Orderflow toxicity (causal, VPIN-style bucketed signed-volume imbalance)
# ---------------------------------------------------------------------------


def toxicity_score(
    trades: Sequence[Trade],
    bar_timestamp: datetime,
    window_trades: int = DEFAULT_TOXICITY_WINDOW_TRADES,
) -> float:
    """Deterministic toxicity score in [0, 1] from causal orderflow.

    Only trades with ``timestamp <= bar_timestamp`` are used (no lookahead). The
    score is the signed-volume imbalance ``|buy - sell| / (buy + sell)`` over the
    trailing ``window_trades`` causal trades (VPIN-style volume-synchronized
    window), so short-term flow spikes push the score toward 1.0 while balanced
    flow keeps it near 0. Zero trades -> 0.0.
    """
    causal = [t for t in trades if t.timestamp <= bar_timestamp]
    if not causal:
        return 0.0
    causal = sorted(causal, key=lambda t: t.timestamp)
    w = max(1, int(window_trades))
    win = causal[-w:] if len(causal) >= w else causal
    buy_vol = sum(float(t.size) for t in win if str(t.side).lower() == "buy")
    sell_vol = sum(float(t.size) for t in win if str(t.side).lower() == "sell")
    total = buy_vol + sell_vol
    if total <= 0.0:
        return 0.0
    score = abs(buy_vol - sell_vol) / total
    return float(min(1.0, max(0.0, score)))


# ---------------------------------------------------------------------------
# Dataclasses (strict-serializable report schema)
# ---------------------------------------------------------------------------


@dataclass
class HedgeLeg:
    """One leg of the delta hedge."""

    symbol: str = ""
    venue: str = ""
    instrument: str = ""
    signed_contracts: float = 0.0
    delta_usd: float = 0.0
    gamma_usd: float = 0.0
    vega_usd: float = 0.0
    theta_usd: float = 0.0
    notional_usd: float = 0.0


@dataclass
class InventorySnapshot:
    """Per-bar inventory + hedge + toxicity accounting."""

    bar_index: int = 0
    timestamp: str = ""
    net_delta_usd: float = 0.0
    net_gamma_usd: float = 0.0
    net_vega_usd: float = 0.0
    inventory_skew: float = 0.0
    target_delta_usd: float = 0.0
    hedge_notional_usd: float = 0.0
    hedge_cost_usd: float = 0.0
    toxicity_score: float = 0.0
    toxic_gate_active: bool = False
    orders_quoted: int = 0
    orders_skipped: int = 0
    regime: str = ""


@dataclass
class SeedHedgeResult:
    """One seed's gamma/inventory hedge + toxicity-gate outcome."""

    seed: int = 0
    snapshots: List[InventorySnapshot] = field(default_factory=list)
    mean_abs_delta_usd: float = 0.0
    mean_inventory_skew: float = 0.0
    mean_hedge_cost_usd: float = 0.0
    mean_toxicity_score: float = 0.0
    toxic_gate_active_fraction: float = 0.0
    oos_return_with_hedge: float = 0.0
    oos_sharpe_with_hedge: float = 0.0
    oos_max_drawdown_with_hedge: float = 0.0
    oos_return_without_hedge: float = 0.0
    oos_sharpe_without_hedge: float = 0.0
    oos_max_drawdown_without_hedge: float = 0.0
    num_hedges: int = 0
    num_bars: int = 0
    num_skipped_due_to_toxicity: int = 0


@dataclass
class GammaInventoryReport:
    """Top-level report (strict-serializable via :func:`serialize_metrics_strict`)."""

    report_id: str = ""
    generated_at: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    per_seed: List[Dict[str, Any]] = field(default_factory=list)
    aggregate: Dict[str, Any] = field(default_factory=dict)
    never_valid_true: bool = True


# ---------------------------------------------------------------------------
# Per-window walk-forward with gamma/inventory hedge + toxicity gate
# ---------------------------------------------------------------------------


def _run_hedge_walkforward(
    symbol: str,
    prices: List[float],
    signals: List[int],
    timestamps: List[datetime],
    orderflow: OrderflowSnapshot,
    static_ctx: Dict[str, Any],
    sizer: CapacityAwareSizer,
    cfg: IntegratedConfig,
    n_points: int,
    seed: int,
    with_hedge: bool,
    target_delta_usd: float = DEFAULT_TARGET_DELTA_USD,
    toxicity_threshold: float = DEFAULT_TOXICITY_THRESHOLD,
    hedge_cost_bps: float = DEFAULT_HEDGE_COST_BPS,
) -> Dict[str, Any]:
    """Run OOS walk-forward for one symbol, with or without the hedge+gate.

    Two books share the SAME window boundaries and SAME signal series:
      * without hedge — plain signal-driven execution through CapacityAwareSizer.
      * with hedge    — same execution plus a per-bar delta hedge toward
                        ``target_delta_usd`` (capped by per-venue capacity) and
                        an orderflow-toxicity gate that skips quoting when the
                        causal toxicity score exceeds the threshold.
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

    greeks = static_ctx.get("greeks_summary") or {}
    option_delta = float(_finite(greeks.get("delta"), 0.0))
    option_gamma = float(_finite(greeks.get("gamma"), 0.0))
    option_vega = float(_finite(greeks.get("vega"), 0.0))
    option_theta = float(_finite(greeks.get("theta"), 0.0))

    def _engine() -> BacktestEngine:
        return BacktestEngine(
            BacktestConfig(
                initial_capital=INITIAL_CAPITAL,
                fee_rate=0.0,
                slippage_bps=0.0,
                slippage_seed=seed,
                risk_free_rate=0.0,
            ),
            RiskConfig(),
        )

    windows: List[Dict[str, Any]] = []
    window_returns: List[float] = []
    snapshots: List[InventorySnapshot] = []
    num_windows_processed = 0
    total_cost_usd = 0.0
    total_notional = 0.0
    total_trades = 0
    total_hedges = 0
    total_skipped = 0
    base_liquidity: Dict[Tuple[str, str], float] = {}

    for w in wfres.windows:
        start = max(0, int(w.test_start))
        end = min(int(w.test_end), len(prices))
        if end <= start:
            continue
        num_windows_processed += 1
        nav_at_start = INITIAL_CAPITAL
        engine = _engine()
        window_cost_usd = 0.0
        window_notional = 0.0
        window_trades = 0
        window_hedges = 0
        window_skipped = 0
        budget_remaining_bps = sizer.cost_budget_bps

        for i in range(start, end):
            px = _finite(prices[i], 0.0)
            if px <= 0.0:
                continue
            ts = timestamps[i] if i < len(timestamps) else DETERMINISTIC_NOW
            sig = int(signals[i]) if i < len(signals) and math.isfinite(signals[i]) else 0
            cur = {symbol: px}
            rv = _realized_vol(prices, i)
            nav = engine.get_equity(cur) or INITIAL_CAPITAL

            # ---- signal-driven execution (same for both books) --------------
            if sig == 1 and symbol not in engine.positions:
                target_notional = abs(1.0) * cfg.max_position_pct * nav
                res = sizer.size(
                    symbol, target_notional, px, i, rv, budget_remaining_bps, nav,
                )
                if res.qty > 0:
                    try:
                        engine.execute_trade(symbol, res.qty, px, "buy", ts)
                    except Exception:
                        pass
                    window_cost_usd += res.cost_usd
                    window_notional += res.notional_usd
                    window_trades += 1
                    budget_remaining_bps -= res.realized_cost_bps * (
                        res.notional_usd / max(nav, 1.0)
                    )
            elif sig == -1 and symbol in engine.positions and engine.positions[symbol].side == "long":
                pos = engine.positions[symbol]
                res = sizer.size(
                    symbol, pos.quantity * px, px, i, rv, budget_remaining_bps, nav,
                )
                if res.qty > 0:
                    try:
                        engine.execute_trade(
                            symbol, min(res.qty, pos.quantity), px, "sell", ts,
                        )
                    except Exception:
                        pass
                    window_cost_usd += res.cost_usd
                    window_notional += res.notional_usd
                    window_trades += 1
                    budget_remaining_bps -= res.realized_cost_bps * (
                        res.notional_usd / max(nav, 1.0)
                    )

            # ---- gamma/inventory hedge + toxicity gate (hedge book only) --
            hedge_notional = 0.0
            hedge_cost_usd = 0.0
            toxic = False
            toxicity = 0.0
            orders_quoted = 0
            orders_skipped = 0
            if with_hedge:
                pos = engine.positions.get(symbol)
                pos_qty = float(pos.quantity) if pos is not None else 0.0
                net_delta_usd_pre = pos_qty * px * option_delta
                delta_gap = net_delta_usd_pre - float(target_delta_usd)
                toxicity = toxicity_score(orderflow.trades, ts)
                toxic = toxicity >= float(toxicity_threshold)

                if not toxic and abs(delta_gap) > DELTA_TOL:
                    capacity_cap = float(
                        sizer.max_participation
                        * sum(
                            _leg_liquidity(symbol, v, seed, base_liquidity)
                            for v in VENUES
                        )
                    )
                    target_hedge = min(abs(delta_gap), capacity_cap) if capacity_cap > 0 else 0.0
                    if target_hedge > 0.0:
                        res = sizer.size(
                            symbol, target_hedge, px, i, rv, budget_remaining_bps, nav,
                        )
                        hedge_notional = float(res.notional_usd)
                        hedge_cost_usd = float(res.cost_usd)
                        qty = hedge_notional / px if px > 0.0 else 0.0
                        side = "sell" if delta_gap > 0.0 else "buy"
                        if qty > 0.0:
                            try:
                                engine.execute_trade(symbol, qty, px, side, ts)
                            except Exception:
                                pass
                        total_hedges += 1
                        window_hedges += 1
                        orders_quoted += 1
                        window_cost_usd += hedge_cost_usd
                        window_notional += hedge_notional
                        budget_remaining_bps -= res.realized_cost_bps * (
                            res.notional_usd / max(nav, 1.0)
                        )
                else:
                    orders_skipped += 1
                    window_skipped += 1
                    total_skipped += 1

            engine.update_equity_curve(cur)

            # ---- post-hedge inventory snapshot -----------------------------
            pos2 = engine.positions.get(symbol)
            pos_qty2 = float(pos2.quantity) if pos2 is not None else 0.0
            net_delta_usd = pos_qty2 * px * option_delta
            net_gamma_usd = pos_qty2 * px * option_gamma
            net_vega_usd = pos_qty2 * px * option_vega
            inventory_skew = (
                net_gamma_usd / max(abs(net_delta_usd), 1e-9) if net_delta_usd != 0 else 0.0
            )
            snapshots.append(
                InventorySnapshot(
                    bar_index=i,
                    timestamp=ts.isoformat() if hasattr(ts, "isoformat") else str(ts),
                    net_delta_usd=float(net_delta_usd),
                    net_gamma_usd=float(net_gamma_usd),
                    net_vega_usd=float(net_vega_usd),
                    inventory_skew=float(inventory_skew),
                    target_delta_usd=float(target_delta_usd),
                    hedge_notional_usd=float(hedge_notional),
                    hedge_cost_usd=float(hedge_cost_usd),
                    toxicity_score=float(toxicity),
                    toxic_gate_active=bool(toxic),
                    orders_quoted=int(orders_quoted),
                    orders_skipped=int(orders_skipped),
                    regime=_path_regime(i, n_points),
                )
            )

        equity_curve = [float(e) for e in engine.equity_curve if math.isfinite(float(e))]
        if len(equity_curve) >= 2:
            window_ret = (equity_curve[-1] - equity_curve[0]) / equity_curve[0]
        else:
            window_ret = 0.0
        window_returns.append(float(window_ret))
        total_cost_usd += window_cost_usd
        total_notional += window_notional
        total_trades += window_trades

    # OOS metrics via compute_metrics on the chained equity curve (EVAL-06/07 helper).
    equity = [INITIAL_CAPITAL]
    for r in window_returns:
        equity.append(equity[-1] * (1.0 + r))
    try:
        metrics = compute_metrics(equity)
    except ValueError:
        metrics = {}

    abs_deltas = [abs(s.net_delta_usd) for s in snapshots]
    mean_abs_delta = float(sum(abs_deltas) / len(abs_deltas)) if abs_deltas else 0.0
    mean_skew = float(sum(s.inventory_skew for s in snapshots) / len(snapshots)) if snapshots else 0.0
    mean_cost = float(sum(s.hedge_cost_usd for s in snapshots) / len(snapshots)) if snapshots else 0.0
    mean_tox = float(sum(s.toxicity_score for s in snapshots) / len(snapshots)) if snapshots else 0.0
    tox_frac = float(
        sum(1 for s in snapshots if s.toxic_gate_active) / len(snapshots)
    ) if snapshots else 0.0

    result: Dict[str, Any] = {
        "symbol": symbol,
        "with_hedge": bool(with_hedge),
        "seed": int(seed),
        "num_windows": int(num_windows_processed),
        "num_bars": int(len(snapshots)),
        "oos_return": float(metrics.get("total_return", 0.0)),
        "oos_sharpe": float(metrics.get("sharpe", 0.0)),
        "oos_max_drawdown": float(metrics.get("max_drawdown", 0.0)),
        "oos_ann_vol": float(metrics.get("ann_vol", 0.0)),
        "total_cost_usd": float(total_cost_usd),
        "total_traded_notional": float(total_notional),
        "num_trades": int(total_trades),
        "num_hedges": int(total_hedges),
        "num_skipped_due_to_toxicity": int(total_skipped),
        "mean_abs_delta_usd": float(mean_abs_delta),
        "mean_inventory_skew": float(mean_skew),
        "mean_hedge_cost_usd": float(mean_cost),
        "mean_toxicity_score": float(mean_tox),
        "toxic_gate_active_fraction": float(tox_frac),
        "target_delta_usd": float(target_delta_usd),
        "toxicity_threshold": float(toxicity_threshold),
        "option_delta": float(option_delta),
        "option_gamma": float(option_gamma),
        "option_vega": float(option_vega),
        "option_theta": float(option_theta),
        "snapshots": [
            {
                "bar_index": s.bar_index,
                "timestamp": s.timestamp,
                "net_delta_usd": s.net_delta_usd,
                "net_gamma_usd": s.net_gamma_usd,
                "net_vega_usd": s.net_vega_usd,
                "inventory_skew": s.inventory_skew,
                "target_delta_usd": s.target_delta_usd,
                "hedge_notional_usd": s.hedge_notional_usd,
                "hedge_cost_usd": s.hedge_cost_usd,
                "toxicity_score": s.toxicity_score,
                "toxic_gate_active": s.toxic_gate_active,
                "orders_quoted": s.orders_quoted,
                "orders_skipped": s.orders_skipped,
                "regime": s.regime,
            }
            for s in snapshots
        ],
        "oos_equity_curve": [float(v) for v in equity],
    }
    assert_json_valid(result)
    return result


def _evaluate_seed_hedge(
    seed: int,
    n_points: int,
    train_window: int,
    test_window: int,
    step_size: int,
    purge: int,
    embargo: int,
    target_delta_usd: float,
    toxicity_threshold: float,
    hedge_cost_bps: float,
    spread_bps: float,
    impact_coeff: float,
    max_participation: float,
    cost_budget_bps: float,
) -> Dict[str, Any]:
    """Evaluate one seed across BTC/ETH/SOL with and without the hedge+gate."""
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

    static_contexts: Dict[str, Dict[str, Any]] = {}
    orderflows: Dict[str, OrderflowSnapshot] = {}
    signals: Dict[str, List[int]] = {}
    for sym in cfg.symbols:
        spot = float(cfg.spot_prices.get(sym, DEFAULT_SPOT[sym]))
        static_contexts[sym] = _static_context_capacity(sym, spot, now, seed)
        orderflows[sym] = _load_orderflow(sym, "synthetic")
        series, _diag = _build_signal_series_capacity(
            sym, price_series[sym], static_contexts[sym]["features"], static_contexts[sym], seed
        )
        signals[sym] = series

    sizer = CapacityAwareSizer(
        spread_bps=spread_bps,
        impact_coeff=impact_coeff,
        max_participation=max_participation,
        cost_budget_bps=cost_budget_bps,
        seed=seed,
    )

    per_symbol: Dict[str, Dict[str, Any]] = {}
    for sym in cfg.symbols:
        with_res = _run_hedge_walkforward(
            sym,
            price_series[sym],
            signals[sym],
            timestamps,
            orderflows[sym],
            static_contexts[sym],
            sizer,
            cfg,
            n_points,
            seed,
            with_hedge=True,
            target_delta_usd=target_delta_usd,
            toxicity_threshold=toxicity_threshold,
            hedge_cost_bps=hedge_cost_bps,
        )
        without_res = _run_hedge_walkforward(
            sym,
            price_series[sym],
            signals[sym],
            timestamps,
            orderflows[sym],
            static_contexts[sym],
            sizer,
            cfg,
            n_points,
            seed,
            with_hedge=False,
            target_delta_usd=target_delta_usd,
            toxicity_threshold=toxicity_threshold,
            hedge_cost_bps=hedge_cost_bps,
        )
        per_symbol[sym] = {
            "with_hedge": with_res,
            "without_hedge": without_res,
        }

    return {
        "seed": int(seed),
        "symbols": per_symbol,
        "n_points": int(n_points),
        "target_delta_usd": float(target_delta_usd),
        "toxicity_threshold": float(toxicity_threshold),
        "hedge_cost_bps": float(hedge_cost_bps),
        "spread_bps": float(spread_bps),
        "impact_coeff": float(impact_coeff),
        "max_participation": float(max_participation),
        "cost_budget_bps": float(cost_budget_bps),
    }


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def evaluate_gamma_inventory_hedge(
    seeds: Optional[List[int]] = None,
    n_points: int = 500,
    train_window: int = 120,
    test_window: int = 40,
    step_size: int = 40,
    purge: int = 10,
    embargo: int = 5,
    target_delta_usd: float = DEFAULT_TARGET_DELTA_USD,
    toxicity_threshold: float = DEFAULT_TOXICITY_THRESHOLD,
    hedge_cost_bps: float = DEFAULT_HEDGE_COST_BPS,
    spread_bps: float = DEFAULT_SPREAD_BPS_HEDGE,
    impact_coeff: float = DEFAULT_IMPACT_COEFF_HEDGE,
    max_participation: float = DEFAULT_MAX_PARTICIPATION_HEDGE,
    cost_budget_bps: float = DEFAULT_COST_BUDGET_BPS,
) -> Dict[str, Any]:
    """Run gamma/inventory hedge + toxicity-gate OOS evaluation across seeds."""
    if seeds is None:
        seeds = [1, 2, 3, 4, 5]
    seeds = [int(s) for s in seeds]

    per_seed: List[Dict[str, Any]] = []
    for seed in seeds:
        per_seed.append(
            _evaluate_seed_hedge(
                seed,
                n_points,
                train_window,
                test_window,
                step_size,
                purge,
                embargo,
                target_delta_usd,
                toxicity_threshold,
                hedge_cost_bps,
                spread_bps,
                impact_coeff,
                max_participation,
                cost_budget_bps,
            )
        )

    # Aggregate headline metrics across seeds and symbols.
    def _seed_headline(r: Dict[str, Any]) -> Dict[str, float]:
        with_rets: List[float] = []
        without_rets: List[float] = []
        with_sharpe: List[float] = []
        without_sharpe: List[float] = []
        with_mdd: List[float] = []
        without_mdd: List[float] = []
        mean_abs_d: List[float] = []
        mean_tox: List[float] = []
        tox_fracs: List[float] = []
        total_hedges = 0
        total_skipped = 0
        total_cost = 0.0
        total_notional = 0.0
        total_trades = 0
        total_bars = 0
        for sym, v in r["symbols"].items():
            wh = v["with_hedge"]
            wo = v["without_hedge"]
            with_rets.append(float(wh["oos_return"]))
            without_rets.append(float(wo["oos_return"]))
            with_sharpe.append(float(wh["oos_sharpe"]))
            without_sharpe.append(float(wo["oos_sharpe"]))
            with_mdd.append(float(wh["oos_max_drawdown"]))
            without_mdd.append(float(wo["oos_max_drawdown"]))
            mean_abs_d.append(float(wh["mean_abs_delta_usd"]))
            mean_tox.append(float(wh["mean_toxicity_score"]))
            tox_fracs.append(float(wh["toxic_gate_active_fraction"]))
            total_hedges += int(wh["num_hedges"])
            total_skipped += int(wh["num_skipped_due_to_toxicity"])
            total_cost += float(wh["total_cost_usd"])
            total_notional += float(wh["total_traded_notional"])
            total_trades += int(wh["num_trades"])
            total_bars += int(wh["num_bars"])

        def _mean(vals: List[float]) -> float:
            return float(sum(vals) / len(vals)) if vals else 0.0

        return {
            "mean_oos_return_with_hedge": _mean(with_rets),
            "mean_oos_return_without_hedge": _mean(without_rets),
            "return_delta_with_vs_without_hedge": _mean(with_rets) - _mean(without_rets),
            "mean_oos_sharpe_with_hedge": _mean(with_sharpe),
            "mean_oos_sharpe_without_hedge": _mean(without_sharpe),
            "sharpe_delta_with_vs_without_hedge": _mean(with_sharpe) - _mean(without_sharpe),
            "mean_oos_max_drawdown_with_hedge": _mean(with_mdd),
            "mean_oos_max_drawdown_without_hedge": _mean(without_mdd),
            "mean_abs_delta_usd_with_hedge": _mean(mean_abs_d),
            "mean_toxicity_score": _mean(mean_tox),
            "toxic_gate_active_fraction": _mean(tox_fracs),
            "total_hedges": int(total_hedges),
            "total_skipped_due_to_toxicity": int(total_skipped),
            "total_cost_usd": float(total_cost),
            "total_traded_notional": float(total_notional),
            "total_trades": int(total_trades),
            "total_bars": int(total_bars),
        }

    per_seed_agg: List[Dict[str, Any]] = []
    for r in per_seed:
        per_seed_agg.append(
            {
                "seed": int(r["seed"]),
                "symbols": {
                    sym: {
                        "with_hedge": {
                            k: vv
                            for k, vv in val["with_hedge"].items()
                            if k != "oos_equity_curve"
                        },
                        "without_hedge": {
                            k: vv
                            for k, vv in val["without_hedge"].items()
                            if k not in ("snapshots", "oos_equity_curve")
                        },
                    }
                    for sym, val in r["symbols"].items()
                },
                "headline": _seed_headline(r),
            }
        )

    all_with_ret = [p["headline"]["mean_oos_return_with_hedge"] for p in per_seed_agg]
    all_without_ret = [p["headline"]["mean_oos_return_without_hedge"] for p in per_seed_agg]
    all_with_sh = [p["headline"]["mean_oos_sharpe_with_hedge"] for p in per_seed_agg]
    all_without_sh = [p["headline"]["mean_oos_sharpe_without_hedge"] for p in per_seed_agg]
    all_with_mdd = [p["headline"]["mean_oos_max_drawdown_with_hedge"] for p in per_seed_agg]
    all_without_mdd = [p["headline"]["mean_oos_max_drawdown_without_hedge"] for p in per_seed_agg]
    all_tox = [p["headline"]["toxic_gate_active_fraction"] for p in per_seed_agg]
    all_abs_d = [p["headline"]["mean_abs_delta_usd_with_hedge"] for p in per_seed_agg]

    def _mean(vals: List[float]) -> float:
        return float(sum(vals) / len(vals)) if vals else 0.0

    aggregate = {
        "seeds": [int(s) for s in seeds],
        "num_seeds": int(len(seeds)),
        "mean_oos_return_with_hedge": _mean(all_with_ret),
        "mean_oos_return_without_hedge": _mean(all_without_ret),
        "return_delta_with_vs_without_hedge": float(_mean(all_with_ret) - _mean(all_without_ret)),
        "mean_oos_sharpe_with_hedge": _mean(all_with_sh),
        "mean_oos_sharpe_without_hedge": _mean(all_without_sh),
        "sharpe_delta_with_vs_without_hedge": float(_mean(all_with_sh) - _mean(all_without_sh)),
        "mean_oos_max_drawdown_with_hedge": _mean(all_with_mdd),
        "mean_oos_max_drawdown_without_hedge": _mean(all_without_mdd),
        "mean_abs_delta_usd_with_hedge": _mean(all_abs_d),
        "mean_toxicity_score": _mean([p["headline"]["mean_toxicity_score"] for p in per_seed_agg]),
        "toxic_gate_active_fraction": _mean(all_tox),
        "total_hedges": int(sum(p["headline"]["total_hedges"] for p in per_seed_agg)),
        "total_skipped_due_to_toxicity": int(
            sum(p["headline"]["total_skipped_due_to_toxicity"] for p in per_seed_agg)
        ),
        "total_cost_usd": float(sum(p["headline"]["total_cost_usd"] for p in per_seed_agg)),
        "total_traded_notional": float(
            sum(p["headline"]["total_traded_notional"] for p in per_seed_agg)
        ),
        "total_trades": int(sum(p["headline"]["total_trades"] for p in per_seed_agg)),
        "total_bars": int(sum(p["headline"]["total_bars"] for p in per_seed_agg)),
        "target_delta_usd": float(target_delta_usd),
        "toxicity_threshold": float(toxicity_threshold),
        "hedge_cost_bps": float(hedge_cost_bps),
        "spread_bps": float(spread_bps),
        "impact_coeff": float(impact_coeff),
        "max_participation": float(max_participation),
        "cost_budget_bps": float(cost_budget_bps),
    }

    report: Dict[str, Any] = {
        "report_id": "GAMMA_INVENTORY_HEDGE_EVAL_09",
        "generated_at": _utc_now_iso(),
        "config": {
            "seeds": [int(s) for s in seeds],
            "n_points": int(n_points),
            "train_window": int(train_window),
            "test_window": int(test_window),
            "step_size": int(step_size),
            "purge": int(purge),
            "embargo": int(embargo),
            "target_delta_usd": float(target_delta_usd),
            "toxicity_threshold": float(toxicity_threshold),
            "hedge_cost_bps": float(hedge_cost_bps),
            "spread_bps": float(spread_bps),
            "impact_coeff": float(impact_coeff),
            "max_participation": float(max_participation),
            "cost_budget_bps": float(cost_budget_bps),
            "symbols": list(DEFAULT_SYMBOLS),
            "venues": list(VENUES),
            "venue_count": len(VENUES),
            "initial_capital": INITIAL_CAPITAL,
        },
        "per_seed": per_seed_agg,
        "aggregate": aggregate,
        "never_valid_true": True,
    }
    assert_json_valid(report)
    return serialize_metrics_strict(report)


# ---------------------------------------------------------------------------
# Markdown + CLI
# ---------------------------------------------------------------------------


def _write_markdown(report: Dict[str, Any]) -> str:
    agg = report["aggregate"]
    cfg = report["config"]
    lines: List[str] = []
    lines.append("# GAMMA/INVENTORY HEDGE + ORDERFLOW TOXICITY GATE REPORT — EVAL-09")
    lines.append("")
    lines.append(f"- Report ID: {report['report_id']}")
    lines.append(f"- Generated at: {report['generated_at']}")
    lines.append(f"- Symbols: {', '.join(cfg['symbols'])}")
    lines.append(f"- Venues: {', '.join(cfg['venues'])}")
    lines.append(f"- Seeds: {cfg['seeds']}")
    lines.append(
        f"- Target delta: {cfg['target_delta_usd']} | Toxicity threshold: {cfg['toxicity_threshold']} | "
        f"Hedge cost: {cfg['hedge_cost_bps']} bps | Spread: {cfg['spread_bps']} bps"
    )
    lines.append(
        f"- Impact coeff: {cfg['impact_coeff']} | Max participation: {cfg['max_participation']} | "
        f"Cost budget: {cfg['cost_budget_bps']} bps/window"
    )
    lines.append("")
    lines.append("## AGGREGATE (with hedge+gate vs without)")
    lines.append("")
    for k in (
        "num_seeds",
        "mean_oos_return_with_hedge",
        "mean_oos_return_without_hedge",
        "return_delta_with_vs_without_hedge",
        "mean_oos_sharpe_with_hedge",
        "mean_oos_sharpe_without_hedge",
        "sharpe_delta_with_vs_without_hedge",
        "mean_oos_max_drawdown_with_hedge",
        "mean_oos_max_drawdown_without_hedge",
        "mean_abs_delta_usd_with_hedge",
        "mean_toxicity_score",
        "toxic_gate_active_fraction",
        "total_hedges",
        "total_skipped_due_to_toxicity",
        "total_cost_usd",
        "total_traded_notional",
        "total_trades",
        "total_bars",
    ):
        lines.append(f"- {k}: {agg[k]}")
    lines.append("")
    lines.append("## Per-seed headline (with hedge+gate vs without)")
    lines.append("")
    for p in report["per_seed"]:
        h = p["headline"]
        lines.append(
            f"- seed {p['seed']}: ret_with={h['mean_oos_return_with_hedge']:.6f}, "
            f"ret_without={h['mean_oos_return_without_hedge']:.6f}, "
            f"sharpe_with={h['mean_oos_sharpe_with_hedge']:.6f}, "
            f"sharpe_without={h['mean_oos_sharpe_without_hedge']:.6f}, "
            f"maxdd_with={h['mean_oos_max_drawdown_with_hedge']:.6f}, "
            f"maxdd_without={h['mean_oos_max_drawdown_without_hedge']:.6f}, "
            f"toxicity={h['mean_toxicity_score']:.4f}, "
            f"tox_frac={h['toxic_gate_active_fraction']:.4f}, "
            f"hedges={h['total_hedges']}, skipped={h['total_skipped_due_to_toxicity']}, "
            f"abs_delta={h['mean_abs_delta_usd_with_hedge']:.4f}"
        )
    lines.append("")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Gamma/inventory-aware hedge sizing + orderflow-toxicity gating (EVAL-09)"
    )
    parser.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3, 4, 5])
    parser.add_argument("--n-points", type=int, default=500)
    parser.add_argument("--train-window", type=int, default=120)
    parser.add_argument("--test-window", type=int, default=40)
    parser.add_argument("--step-size", type=int, default=40)
    parser.add_argument("--purge", type=int, default=10)
    parser.add_argument("--embargo", type=int, default=5)
    parser.add_argument("--target-delta-usd", type=float, default=DEFAULT_TARGET_DELTA_USD)
    parser.add_argument("--toxicity-threshold", type=float, default=DEFAULT_TOXICITY_THRESHOLD)
    parser.add_argument("--hedge-cost-bps", type=float, default=DEFAULT_HEDGE_COST_BPS)
    parser.add_argument("--spread-bps", type=float, default=DEFAULT_SPREAD_BPS_HEDGE)
    parser.add_argument("--impact-coeff", type=float, default=DEFAULT_IMPACT_COEFF_HEDGE)
    parser.add_argument("--max-participation", type=float, default=DEFAULT_MAX_PARTICIPATION_HEDGE)
    parser.add_argument("--cost-budget-bps", type=float, default=DEFAULT_COST_BUDGET_BPS)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--timestamp", type=str, default=_utc_now_iso())
    args = parser.parse_args(argv)

    ts = args.timestamp.replace(":", "").replace("-", "").replace("T", "").replace("Z", "").split(".")[0]
    stamp = f"{ts[:8]}T{ts[8:14]}Z" if len(ts) >= 14 else ts

    report = evaluate_gamma_inventory_hedge(
        seeds=args.seeds,
        n_points=args.n_points,
        train_window=args.train_window,
        test_window=args.test_window,
        step_size=args.step_size,
        purge=args.purge,
        embargo=args.embargo,
        target_delta_usd=args.target_delta_usd,
        toxicity_threshold=args.toxicity_threshold,
        hedge_cost_bps=args.hedge_cost_bps,
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
                "mean_oos_return_with_hedge": report["aggregate"]["mean_oos_return_with_hedge"],
                "mean_oos_return_without_hedge": report["aggregate"]["mean_oos_return_without_hedge"],
                "return_delta_with_vs_without_hedge": report["aggregate"][
                    "return_delta_with_vs_without_hedge"
                ],
                "mean_oos_sharpe_with_hedge": report["aggregate"]["mean_oos_sharpe_with_hedge"],
                "mean_oos_sharpe_without_hedge": report["aggregate"][
                    "mean_oos_sharpe_without_hedge"
                ],
                "sharpe_delta_with_vs_without_hedge": report["aggregate"][
                    "sharpe_delta_with_vs_without_hedge"
                ],
                "mean_oos_max_drawdown_with_hedge": report["aggregate"][
                    "mean_oos_max_drawdown_with_hedge"
                ],
                "mean_oos_max_drawdown_without_hedge": report["aggregate"][
                    "mean_oos_max_drawdown_without_hedge"
                ],
                "mean_abs_delta_usd_with_hedge": report["aggregate"][
                    "mean_abs_delta_usd_with_hedge"
                ],
                "mean_toxicity_score": report["aggregate"]["mean_toxicity_score"],
                "toxic_gate_active_fraction": report["aggregate"][
                    "toxic_gate_active_fraction"
                ],
                "total_hedges": report["aggregate"]["total_hedges"],
                "total_skipped_due_to_toxicity": report["aggregate"][
                    "total_skipped_due_to_toxicity"
                ],
                "total_cost_usd": report["aggregate"]["total_cost_usd"],
                "total_trades": report["aggregate"]["total_trades"],
            },
            indent=2,
        )
    )

    if args.write:
        research_state = Path("research_state")
        research_state.mkdir(parents=True, exist_ok=True)
        stem = f"GAMMA_INVENTORY_HEDGE_{stamp}"
        json_path = research_state / f"{stem}.json"
        md_path = research_state / f"{stem}.md"
        json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        md_path.write_text(_write_markdown(report) + "\n", encoding="utf-8")
        print(f"Wrote {json_path}")
        print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
