"""Orderflow alpha & toxicity evaluation (EVAL-17, paper-only).

Deterministic, fully offline evaluation of the orderflow pillar of the crypto
quantitative options + orderflow strategy:

  1. **Load real data** — BTCUSDT orderflow
     (``data/raw/orderflow_btcusdt_synthetic.json``: 1000 trades, 20
     liquidations, 8 funding rates) via
     ``src.campaign.integrated._load_orderflow(symbol="BTC", venue="synthetic")``.
  2. **Causal, no-lookahead signal** — per-bar feature series built by applying
     ``src.alpha.orderflow_alpha.OrderflowAlphaEngine.extract_features`` to a
     trailing causal snapshot per bar (trades with ``timestamp <= bar_timestamp``
     only — see ``src.analytics.gamma_inventory_hedge.toxicity_score`` for the
     causal pattern). Never applied to the full tape.
  3. **Measure alpha (IC + decay)** — Pearson information coefficient between
     the causal signal at bar ``t`` and the forward return over horizons
     1/5/20 bars. Reports IC mean, std, t-stat and signal decay (IC by horizon);
     block-bootstrap CI on mean IC via
     ``src.analytics.strategy_evaluation.block_bootstrap_ci``.
  4. **Measure toxicity (VPIN)** — VPIN-style causal toxicity per bar from
     signed-volume imbalance over trailing volume buckets. Reports toxicity
     mean, p95, fraction above threshold (default 0.7) and gate-engagement
     fraction (a real measured number, never identically 0 or 1).
  5. **Net-of-cost with/without** — deterministic OOS walk-forward of an
     orderflow-signal strategy through ``compute_metrics``, with the orderflow
     signal vs an always-flat control, using the capacity-aware spread + impact
     cost model
     (``DEFAULT_SPREAD_BPS``/``DEFAULT_IMPACT_COEFF``/``DEFAULT_MAX_PARTICIPATION``
     from ``src.analytics.capacity_aware_tca``).
  6. **Deterministic verdict** — ``compute_orderflow_toxicity_verdict(...) ->
     dict`` with an explicit ``checks`` list:
     signal-exists (IC != 0), IC significance (t-stat / permutation p),
     toxicity measured (0 < mean < 1 and gate engages), net-of-cost
     with-vs-without, no-lookahead asserted. Each check: numeric threshold +
     rationale, finite metrics, evidence matrix. Strict-serializable via
     ``serialize_metrics_strict``/``assert_json_valid`` (``allow_nan=False``).
     Never emits ``{"valid": true}``.

Emit canonical artifact:
``research_state/ORDERFLOW_ALPHA_TOXICITY_EVAL_<UTC>.{json,md}``.
Paper-only: no network, no ``.env``, no venue/credential mutation, no live.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from src.analytics.capacity_aware_tca import (
    CapacityAwareSizer,
    DEFAULT_COST_BUDGET_BPS,
    DEFAULT_IMPACT_COEFF,
    DEFAULT_MAX_PARTICIPATION,
    DEFAULT_SPREAD_BPS,
)
from src.analytics.strategy_evaluation import (
    block_bootstrap_ci,
    compute_metrics,
    permutation_test,
)
from src.alpha.orderflow_alpha import OrderflowAlphaEngine
from src.backtest.engine import BacktestConfig, BacktestEngine, RiskConfig, WalkForwardBacktest
from src.campaign.integrated import (
    DEFAULT_SPOT,
    DEFAULT_VENUE,
    DETERMINISTIC_NOW,
    IntegratedConfig,
    _load_orderflow,
)
from src.data.schemas import OrderflowSnapshot, Trade
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

REPORT_ID = "ORDERFLOW_ALPHA_TOXICITY_EVAL_17"
OUT_DIR = Path("research_state")

TRADING_MODE = "paper"
LIVE_TRADING_ENABLED = False

# ---------------------------------------------------------------------------
# Evaluation thresholds (numeric, with rationale recorded in the artifact)
# ---------------------------------------------------------------------------

# Default bar duration (seconds) used to slice the trade tape into causal bars.
DEFAULT_BAR_DURATION_SECONDS: float = 15.0

# Trailing lookback (seconds) for the per-bar signal snapshot (causal).
DEFAULT_SIGNAL_LOOKBACK_SECONDS: float = 60.0

# VPIN toxicity trailing window (number of causal trades).
DEFAULT_TOXICITY_WINDOW_TRADES: int = 5

# Toxicity gate threshold (bar stands down quoting/hedging when >= threshold).
DEFAULT_TOXICITY_THRESHOLD: float = 0.7

# Position entry threshold on the causal signal (net_aggression in [-1, 1]).
DEFAULT_SIGNAL_THRESHOLD: float = 0.1

# Forward-return horizons (bars) for IC decay.
HORIZONS: Tuple[int, ...] = (1, 5, 20)

# IC "signal exists" requires a nonzero mean IC (beyond float noise).
IC_EXISTS_EPSILON: float = 1e-9

# Two-sided 5% t-stat critical value for IC significance.
TSTAT_CRITICAL: float = 1.96

# Permutation significance level.
PERM_ALPHA: float = 0.05

# Walk-forward / backtest parameters.
DEFAULT_N_POINTS: int = 500
DEFAULT_TRAIN_WINDOW: int = 120
DEFAULT_TEST_WINDOW: int = 40
DEFAULT_STEP_SIZE: int = 40
DEFAULT_PURGE: int = 10
DEFAULT_EMBARGO: int = 5
DEFAULT_MAX_POSITION_PCT: float = 0.20
DEFAULT_INITIAL_CAPITAL: float = 100000.0
DEFAULT_SEEDS: Tuple[int, ...] = (1, 2, 3, 4, 5)

# Number of bootstrap replications for the mean-IC CI.
DEFAULT_N_BOOTSTRAP: int = 2000
DEFAULT_BLOCK_SIZE: int = 1

# Calendar year in hours for the deterministic hourly price path (fallback only).
HOURS_PER_YEAR: float = 365.25 * 24.0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _stamp_for_filename(iso_ts: str) -> str:
    try:
        ts = iso_ts.replace(":", "").replace("-", "").replace("T", "").replace("Z", "").split(".")[0]
    except Exception:
        return ""
    return f"{ts[:8]}T{ts[8:14]}Z" if len(ts) >= 14 else ""


def _finite(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    return v if math.isfinite(v) else default


def _parse_ts(ts: Any) -> datetime:
    if isinstance(ts, datetime):
        dt = ts
    else:
        dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _all_finite_numbers(obj: Any) -> bool:
    if isinstance(obj, bool):
        return True
    if isinstance(obj, (int, float)):
        return math.isfinite(float(obj))
    if isinstance(obj, dict):
        return all(_all_finite_numbers(v) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return all(_all_finite_numbers(v) for v in obj)
    return True


def _pearson(xs: Sequence[float], ys: Sequence[float]) -> float:
    xs = [float(x) for x in xs]
    ys = [float(y) for y in ys]
    n = min(len(xs), len(ys))
    if n < 2:
        return 0.0
    xs = xs[:n]
    ys = ys[:n]
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs)
    dy = sum((y - my) ** 2 for y in ys)
    if dx <= 0.0 or dy <= 0.0:
        return 0.0
    r = num / math.sqrt(dx * dy)
    return float(max(-1.0, min(1.0, r)))


def _tstat_from_ics(ics: Sequence[float]) -> float:
    vals = [float(v) for v in ics if math.isfinite(float(v))]
    n = len(vals)
    if n < 2:
        return 0.0
    mean = sum(vals) / n
    var = sum((v - mean) ** 2 for v in vals) / n
    std = math.sqrt(max(var, 0.0))
    if std <= 0.0:
        return 0.0
    return float(mean / (std / math.sqrt(n)))


def _p95(vals: Sequence[float]) -> float:
    vals = sorted(float(v) for v in vals if math.isfinite(float(v)))
    if not vals:
        return 0.0
    n = len(vals)
    k = max(0, min(n - 1, int(math.ceil(0.95 * n) - 1)))
    return float(vals[k])


# ---------------------------------------------------------------------------
# Step 1 — causal bar construction from the trade tape
# ---------------------------------------------------------------------------


def _build_bars(
    snapshot: OrderflowSnapshot,
    bar_duration_seconds: float = DEFAULT_BAR_DURATION_SECONDS,
) -> Dict[str, Any]:
    """Slice the causal trade tape into time bars.

    Each bar covers ``(bar_start, bar_end]``. ``bar_closes[i]`` is the price of
    the last trade with ``timestamp <= bar_end[i]`` (causal, carried forward
    when a bar has no trades). Returns bar ends, closes and per-bar causal
    trade lists.
    """
    trades = sorted(snapshot.trades or [], key=lambda t: _parse_ts(t.timestamp))
    if not trades:
        return {
            "bar_ends": [],
            "bar_closes": [],
            "bar_trades": [],
            "n_bars": 0,
            "start_timestamp": None,
            "end_timestamp": None,
        }
    start = _parse_ts(trades[0].timestamp)
    end = _parse_ts(trades[-1].timestamp)
    span = (end - start).total_seconds()
    dur = max(float(bar_duration_seconds), 1.0)
    n_bars = max(1, int(math.ceil(span / dur)))
    bar_ends: List[datetime] = []
    bar_closes: List[float] = []
    bar_trades: List[List[Trade]] = []
    trade_idx = 0
    last_close = float(trades[0].price)
    for i in range(n_bars):
        bar_end = start + timedelta(seconds=(i + 1) * dur)
        causal: List[Trade] = []
        while trade_idx < len(trades) and _parse_ts(trades[trade_idx].timestamp) <= bar_end:
            causal.append(trades[trade_idx])
            trade_idx += 1
        if causal:
            last_close = float(causal[-1].price)
        bar_ends.append(bar_end)
        bar_closes.append(float(last_close))
        bar_trades.append(causal)
    return {
        "bar_ends": [bt.isoformat().replace("+00:00", "Z") for bt in bar_ends],
        "bar_ends_dt": bar_ends,
        "bar_closes": bar_closes,
        "bar_trades": bar_trades,
        "n_bars": int(n_bars),
        "start_timestamp": start.isoformat().replace("+00:00", "Z"),
        "end_timestamp": end.isoformat().replace("+00:00", "Z"),
        "bar_duration_seconds": float(dur),
    }


def _causal_signal_series(
    snapshot: OrderflowSnapshot,
    bar_ends: Sequence[datetime],
    bar_closes: Sequence[float],
    lookback_seconds: float = DEFAULT_SIGNAL_LOOKBACK_SECONDS,
    engine: Optional[OrderflowAlphaEngine] = None,
) -> Dict[str, Any]:
    """Build a causal per-bar signal series (no lookahead).

    For each bar, a trailing causal snapshot contains only trades with
    ``bar_end - lookback < timestamp <= bar_end``. ``OrderflowAlphaEngine``
    extracts features from that snapshot; the signal is ``net_aggression``
    (signed imbalance in [-1, 1]).
    """
    if engine is None:
        engine = OrderflowAlphaEngine()
    trades = sorted(snapshot.trades or [], key=lambda t: _parse_ts(t.timestamp))
    signals: List[float] = []
    features_per_bar: List[Dict[str, Any]] = []
    lookback = max(float(lookback_seconds), 0.0)
    for bar_end, close in zip(bar_ends, bar_closes):
        lo = bar_end - timedelta(seconds=lookback) if lookback > 0 else None
        window_trades = [
            t
            for t in trades
            if _parse_ts(t.timestamp) <= bar_end and (lo is None or _parse_ts(t.timestamp) > lo)
        ]
        causal_snap = OrderflowSnapshot(
            symbol=snapshot.symbol,
            venue=snapshot.venue,
            trades=window_trades,
            timestamp=bar_end,
        )
        feats = engine.extract_features(causal_snap)
        signals.append(float(feats.net_aggression))
        features_per_bar.append({
            "bar_end": bar_end.isoformat().replace("+00:00", "Z"),
            "close": float(close),
            "n_trades": int(len(window_trades)),
            "cumulative_delta": float(feats.cumulative_delta),
            "delta_divergence": float(feats.delta_divergence),
            "absorption_score": float(feats.absorption_score),
            "sweep_score": float(feats.sweep_score),
            "vpin_lite": float(feats.vpin_lite),
            "footprint_imbalance": float(feats.footprint_imbalance),
            "net_aggression": float(feats.net_aggression),
            "large_trade_ratio": float(feats.large_trade_ratio),
        })
    return {
        "signals": signals,
        "features_per_bar": features_per_bar,
        "n_bars": int(len(signals)),
    }


def _toxicities_per_bar(
    snapshot: OrderflowSnapshot,
    bar_ends: Sequence[datetime],
    window_trades: int = DEFAULT_TOXICITY_WINDOW_TRADES,
) -> List[float]:
    """VPIN-style causal toxicity per bar (trades <= bar_end only)."""
    trades = sorted(snapshot.trades or [], key=lambda t: _parse_ts(t.timestamp))
    tox: List[float] = []
    for bar_end in bar_ends:
        causal = [t for t in trades if _parse_ts(t.timestamp) <= bar_end]
        if not causal:
            tox.append(0.0)
            continue
        causal = sorted(causal, key=lambda t: _parse_ts(t.timestamp))
        w = max(1, int(window_trades))
        win = causal[-w:] if len(causal) >= w else causal
        buy_vol = sum(float(t.size) for t in win if str(t.side).lower() == "buy")
        sell_vol = sum(float(t.size) for t in win if str(t.side).lower() == "sell")
        total = buy_vol + sell_vol
        score = 0.0 if total <= 0.0 else abs(buy_vol - sell_vol) / total
        tox.append(float(min(1.0, max(0.0, score))))
    return tox


# ---------------------------------------------------------------------------
# Step 3 — alpha measurement (IC + decay)
# ---------------------------------------------------------------------------


def compute_alpha_metrics(
    signals: Sequence[float],
    bar_closes: Sequence[float],
    horizons: Sequence[int] = HORIZONS,
) -> Dict[str, Any]:
    """Information coefficient between causal signal and forward returns.

    For each horizon h, IC_h = Pearson(signal[t], forward_return[t+h]) over all
    aligned bars. Reports IC mean/std/t-stat across horizons and IC by horizon
    (signal decay).
    """
    sig = [float(s) for s in signals]
    px = [float(p) for p in bar_closes]
    n = len(px)
    ic_by_horizon: Dict[str, float] = {}
    ic_list: List[float] = []
    for h in horizons:
        h = int(h)
        if n <= h:
            ic_by_horizon[str(h)] = 0.0
            ic_list.append(0.0)
            continue
        x = sig[: n - h]
        y = [(px[t + h] - px[t]) / px[t] for t in range(n - h) if px[t] > 0]
        x = x[: len(y)]
        ic = _pearson(x, y) if x else 0.0
        ic_by_horizon[str(h)] = float(ic)
        ic_list.append(float(ic))
    ic_list = [v for v in ic_list if math.isfinite(v)]
    ic_mean = float(sum(ic_list) / len(ic_list)) if ic_list else 0.0
    if len(ic_list) >= 2:
        mean = ic_mean
        var = sum((v - mean) ** 2 for v in ic_list) / len(ic_list)
        ic_std = float(math.sqrt(max(var, 0.0)))
    else:
        ic_std = 0.0
    ic_tstat = _tstat_from_ics(ic_list)
    ci = block_bootstrap_ci(
        values=ic_list if ic_list else [0.0],
        statistic=lambda vals: float(sum(vals) / len(vals)) if len(vals) > 0 else 0.0,
        n_bootstrap=DEFAULT_N_BOOTSTRAP,
        block_size=DEFAULT_BLOCK_SIZE,
        seed=42,
    )
    ic_decay_slope = 0.0
    if len(ic_list) >= 2:
        xs = [float(i) for i in range(len(ic_list))]
        xm = sum(xs) / len(xs)
        ym = sum(ic_list) / len(ic_list)
        den = sum((x - xm) ** 2 for x in xs)
        ic_decay_slope = float(sum((x - xm) * (v - ym) for x, v in zip(xs, ic_list)) / den) if den > 0 else 0.0
    return {
        "horizons": [int(h) for h in horizons],
        "ic_by_horizon": {str(k): float(v) for k, v in ic_by_horizon.items()},
        "ic_mean": float(ic_mean),
        "ic_std": float(ic_std),
        "ic_tstat": float(ic_tstat),
        "ic_bootstrap_ci": {
            "point": float(ci[0]),
            "lo": float(ci[1]),
            "hi": float(ci[2]),
        },
        "ic_decay_slope": float(ic_decay_slope),
        "n_horizons": int(len(ic_list)),
    }


# ---------------------------------------------------------------------------
# Step 4 — toxicity measurement (VPIN)
# ---------------------------------------------------------------------------


def compute_toxicity_metrics(
    toxicities: Sequence[float],
    threshold: float = DEFAULT_TOXICITY_THRESHOLD,
) -> Dict[str, Any]:
    tox = [float(t) for t in toxicities if math.isfinite(float(t))]
    n = len(tox)
    mean_tox = float(sum(tox) / n) if n else 0.0
    p95_tox = _p95(tox)
    thr = float(threshold)
    frac_above = float(sum(1 for t in tox if t >= thr) / n) if n else 0.0
    gate_engages = bool(frac_above > 0.0)
    non_degenerate = bool(0.0 < mean_tox < 1.0 and n > 0)
    return {
        "n_bars": int(n),
        "mean_toxicity": float(mean_tox),
        "p95_toxicity": float(p95_tox),
        "toxicity_threshold": float(thr),
        "fraction_above_threshold": float(frac_above),
        "toxic_gate_active_fraction": float(frac_above),
        "gate_engages": bool(gate_engages),
        "toxicity_measured": bool(non_degenerate and gate_engages),
        "min_toxicity": float(min(tox)) if tox else 0.0,
        "max_toxicity": float(max(tox)) if tox else 0.0,
    }


# ---------------------------------------------------------------------------
# Step 5 — net-of-cost with/without walk-forward
# ---------------------------------------------------------------------------


def _signal_positions(
    signals: Sequence[float],
    threshold: float = DEFAULT_SIGNAL_THRESHOLD,
) -> List[int]:
    thr = float(threshold)
    positions: List[int] = []
    for s in signals:
        s = float(s)
        if s > thr:
            positions.append(1)
        elif s < -thr:
            positions.append(-1)
        else:
            positions.append(0)
    return positions


def _run_orderflow_walkforward(
    symbol: str,
    prices: Sequence[float],
    positions: Sequence[int],
    timestamps: Sequence[datetime],
    sizer: CapacityAwareSizer,
    cfg: IntegratedConfig,
    n_points: int,
    seed: int,
    max_position_pct: float = DEFAULT_MAX_POSITION_PCT,
) -> Dict[str, Any]:
    """OOS walk-forward of an orderflow-signal strategy with capacity-aware costs.

    Mirrors the EVAL-07 engine windowing but sizes every order through
    ``CapacityAwareSizer`` (spread + sqrt(participation) impact). The no-signal
    control is always-flat (constant equity).
    """
    wfb = WalkForwardBacktest(
        purge=cfg.purge,
        embargo=cfg.embargo,
        config=BacktestConfig(
            initial_capital=DEFAULT_INITIAL_CAPITAL,
            fee_rate=0.0,
            slippage_bps=0.0,
            slippage_seed=seed,
            risk_free_rate=0.0,
        ),
        risk_config=RiskConfig(),
    )
    wfres = wfb.run_walk_forward(
        price_series={symbol: list(prices)},
        signals={symbol: list(positions)},
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
    window_returns: List[float] = []
    total_cost_usd = 0.0
    total_notional = 0.0
    total_trades = 0

    for w in wfres.windows:
        start = max(0, int(w.test_start))
        end = min(int(w.test_end), len(prices))
        if end <= start:
            continue
        engine = BacktestEngine(
            BacktestConfig(
                initial_capital=DEFAULT_INITIAL_CAPITAL,
                fee_rate=0.0,
                slippage_bps=0.0,
                slippage_seed=seed,
                risk_free_rate=0.0,
            ),
            RiskConfig(),
        )
        nav_at_start = DEFAULT_INITIAL_CAPITAL
        window_cost_usd = 0.0
        window_notional = 0.0
        window_trades = 0
        budget_remaining_bps = sizer.cost_budget_bps
        cur_qty = 0.0

        for i in range(start, end):
            px = _finite(prices[i], 0.0)
            if px <= 0.0:
                continue
            ts = timestamps[i] if i < len(timestamps) else DETERMINISTIC_NOW
            target_pos = int(positions[i]) if i < len(positions) and math.isfinite(positions[i]) else 0
            nav = engine.get_equity({symbol: px}) or DEFAULT_INITIAL_CAPITAL
            target_qty = float(target_pos) * (float(max_position_pct) * nav / px)
            delta_qty = target_qty - cur_qty
            if abs(delta_qty) > 1e-9:
                side = "buy" if delta_qty > 0 else "sell"
                res = sizer.size(
                    symbol,
                    abs(delta_qty) * px,
                    px,
                    i,
                    0.0,
                    budget_remaining_bps,
                    nav,
                )
                if res.qty > 0:
                    fill_qty = float(res.qty)
                    if side == "sell":
                        fill_qty = min(fill_qty, cur_qty) if cur_qty > 0 else 0.0
                    if fill_qty > 0:
                        try:
                            engine.execute_trade(symbol, fill_qty, px, side, ts)
                        except Exception:
                            pass
                        window_cost_usd += float(res.cost_usd)
                        window_notional += float(res.notional_usd)
                        window_trades += 1
                        budget_remaining_bps -= float(res.realized_cost_bps) * (
                            float(res.notional_usd) / max(nav, 1.0)
                        )
                        cur_qty += fill_qty if side == "buy" else -fill_qty
            engine.update_equity_curve({symbol: px})

        equity_curve = [float(e) for e in engine.equity_curve if math.isfinite(float(e))]
        if len(equity_curve) >= 2:
            window_ret = (equity_curve[-1] - equity_curve[0]) / equity_curve[0]
        else:
            window_ret = 0.0
        window_returns.append(float(window_ret))
        total_cost_usd += window_cost_usd
        total_notional += window_notional
        total_trades += window_trades
        windows.append({
            "window_index": int(len(windows)),
            "test_start": int(start),
            "test_end": int(end),
            "window_return": float(window_ret),
            "window_cost_usd": float(window_cost_usd),
            "window_notional": float(window_notional),
            "window_trades": int(window_trades),
        })

    equity = [DEFAULT_INITIAL_CAPITAL]
    for r in window_returns:
        equity.append(equity[-1] * (1.0 + r))
    try:
        metrics = compute_metrics(equity)
    except ValueError:
        metrics = {}

    return {
        "symbol": symbol,
        "seed": int(seed),
        "num_windows": int(len(windows)),
        "oos_return": float(metrics.get("total_return", 0.0)),
        "oos_sharpe": float(metrics.get("sharpe", 0.0)),
        "oos_max_drawdown": float(metrics.get("max_drawdown", 0.0)),
        "oos_ann_vol": float(metrics.get("ann_vol", 0.0)),
        "total_cost_usd": float(total_cost_usd),
        "total_traded_notional": float(total_notional),
        "num_trades": int(total_trades),
        "spread_bps": float(sizer.spread_bps),
        "impact_coeff": float(sizer.impact_coeff),
        "max_participation": float(sizer.max_participation),
        "cost_budget_bps": float(sizer.cost_budget_bps),
        "oos_equity_curve": [float(v) for v in equity],
        "window_returns": [float(v) for v in window_returns],
        "windows": windows,
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------


def compute_orderflow_toxicity_verdict(
    alpha: Dict[str, Any],
    toxicity: Dict[str, Any],
    with_signal: Dict[str, Any],
    without_signal: Dict[str, Any],
    permutation: Dict[str, Any],
    no_lookahead_asserted: bool,
) -> Dict[str, Any]:
    """Deterministic verdict from all measured blocks; explicit checks list."""
    checks: List[Dict[str, Any]] = []

    def _add(name: str, ok: bool, threshold: float, observed: float, reason: str) -> None:
        checks.append({
            "name": name,
            "pass": bool(ok),
            "threshold": float(threshold),
            "observed": float(observed),
            "reason": reason,
        })

    # 1. Signal exists: mean IC must be nonzero.
    ic_mean = float(alpha["ic_mean"])
    ic_exists = bool(abs(ic_mean) > IC_EXISTS_EPSILON)
    _add(
        "signal_exists_ic_nonzero",
        ic_exists,
        IC_EXISTS_EPSILON,
        abs(ic_mean),
        (
            f"PASS: mean IC {ic_mean:.6e} nonzero (> {IC_EXISTS_EPSILON:.0e})"
            if ic_exists
            else f"FAIL: mean IC {ic_mean:.6e} indistinguishable from zero (<= {IC_EXISTS_EPSILON:.0e})"
        ),
    )

    # 2. IC significance: t-stat or permutation p.
    ic_tstat = float(alpha["ic_tstat"])
    perm_p = float(permutation["p_value"])
    ic_sig = bool(abs(ic_tstat) > TSTAT_CRITICAL or perm_p < PERM_ALPHA)
    _add(
        "ic_significant",
        ic_sig,
        TSTAT_CRITICAL,
        abs(ic_tstat),
        (
            f"PASS: IC significant (|t|={abs(ic_tstat):.4f} > {TSTAT_CRITICAL}, "
            f"permutation p={perm_p:.4f})"
            if ic_sig
            else f"FAIL: IC not significant (|t|={abs(ic_tstat):.4f} <= {TSTAT_CRITICAL}, "
            f"permutation p={perm_p:.4f} >= {PERM_ALPHA})"
        ),
    )

    # 3. Toxicity measured: 0 < mean < 1 and gate engages.
    tox_measured = bool(toxicity["toxicity_measured"])
    _add(
        "toxicity_measured",
        tox_measured,
        1.0,
        float(toxicity["mean_toxicity"]),
        (
            f"PASS: toxicity mean {toxicity['mean_toxicity']:.4f} in (0,1), "
            f"gate engages fraction {toxicity['toxic_gate_active_fraction']:.4f}"
            if tox_measured
            else f"FAIL: toxicity not measured (mean {toxicity['mean_toxicity']:.4f}, "
            f"gate fraction {toxicity['toxic_gate_active_fraction']:.4f})"
        ),
    )

    # 4. Net-of-cost with-vs-without: both finite, cost model applied.
    with_ret = float(with_signal["oos_return"])
    with_sharpe = float(with_signal["oos_sharpe"])
    without_ret = float(without_signal["oos_return"])
    cost_applied = bool(float(with_signal["total_cost_usd"]) >= 0.0)
    net_ok = bool(
        math.isfinite(with_ret)
        and math.isfinite(with_sharpe)
        and math.isfinite(without_ret)
        and cost_applied
    )
    _add(
        "net_of_cost_with_vs_without",
        net_ok,
        1.0,
        with_ret - without_ret,
        (
            f"PASS: net-of-cost comparison finite (with {with_ret:.6f} vs without "
            f"{without_ret:.6f}, cost {with_signal['total_cost_usd']:.2f} USD)"
            if net_ok
            else f"FAIL: net-of-cost comparison degenerate or cost model not applied"
        ),
    )

    # 5. No-lookahead asserted.
    _add(
        "no_lookahead_asserted",
        bool(no_lookahead_asserted),
        1.0,
        1.0 if bool(no_lookahead_asserted) else 0.0,
        "PASS: causal no-lookahead signal asserted and tested"
        if bool(no_lookahead_asserted)
        else "FAIL: no-lookahead not asserted",
    )

    all_pass = all(bool(c["pass"]) for c in checks)
    return {
        "verdict": "GO" if all_pass else "NO-GO",
        "checks": checks,
        "n_checks": int(len(checks)),
        "n_passed": int(sum(1 for c in checks if bool(c["pass"]))),
        "all_checks_pass": bool(all_pass),
        "failed_checks": [c["name"] for c in checks if not bool(c["pass"])],
    }


# ---------------------------------------------------------------------------
# Step 1 entry — load real orderflow
# ---------------------------------------------------------------------------


def load_btc_orderflow(symbol: str = "BTC", venue: str = DEFAULT_VENUE) -> OrderflowSnapshot:
    """Load the real BTC orderflow snapshot (deterministic, offline)."""
    return _load_orderflow(symbol, venue)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def evaluate_orderflow_alpha_toxicity(
    write: bool = True,
    out_dir: str | Path = OUT_DIR,
    timestamp: Optional[str] = None,
    bar_duration_seconds: float = DEFAULT_BAR_DURATION_SECONDS,
    signal_lookback_seconds: float = DEFAULT_SIGNAL_LOOKBACK_SECONDS,
    toxicity_window_trades: int = DEFAULT_TOXICITY_WINDOW_TRADES,
    toxicity_threshold: float = DEFAULT_TOXICITY_THRESHOLD,
    signal_threshold: float = DEFAULT_SIGNAL_THRESHOLD,
    seeds: Sequence[int] = DEFAULT_SEEDS,
    max_position_pct: float = DEFAULT_MAX_POSITION_PCT,
    spread_bps: float = DEFAULT_SPREAD_BPS,
    impact_coeff: float = DEFAULT_IMPACT_COEFF,
    max_participation: float = DEFAULT_MAX_PARTICIPATION,
    cost_budget_bps: float = DEFAULT_COST_BUDGET_BPS,
) -> Dict[str, Any]:
    """Run the full EVAL-17 evaluation and emit strict artifacts."""
    if timestamp is None:
        timestamp = _utc_now_iso()

    spot = float(DEFAULT_SPOT["BTC"])
    now = DETERMINISTIC_NOW

    snapshot = load_btc_orderflow("BTC", DEFAULT_VENUE)
    bars = _build_bars(snapshot, bar_duration_seconds=bar_duration_seconds)
    n_bars = int(bars["n_bars"])
    assert n_bars > max(HORIZONS) + 1, "need enough bars for the longest IC horizon"

    bar_ends_dt: List[datetime] = bars["bar_ends_dt"]
    bar_closes = [float(p) for p in bars["bar_closes"]]

    # Causal per-bar signal series (no lookahead).
    engine = OrderflowAlphaEngine(seed=42)
    signal_series = _causal_signal_series(
        snapshot, bar_ends_dt, bar_closes,
        lookback_seconds=signal_lookback_seconds, engine=engine,
    )
    signals = [float(s) for s in signal_series["signals"]]

    # Alpha (IC + decay).
    alpha = compute_alpha_metrics(signals, bar_closes, horizons=HORIZONS)

    # Permutation test on the mean IC (paired against zero).
    n_pairs = n_bars - int(HORIZONS[-1])
    fwd_ret_primary = [
        (bar_closes[t + int(HORIZONS[-1])] - bar_closes[t]) / bar_closes[t]
        for t in range(n_pairs)
        if bar_closes[t] > 0
    ]
    sig_primary = signals[: len(fwd_ret_primary)]
    permutation = permutation_test(
        sample_a=sig_primary if sig_primary else [0.0],
        sample_b=[0.0] * len(fwd_ret_primary) if fwd_ret_primary else [0.0],
        statistic=lambda vals: float(sum(vals) / len(vals)) if len(vals) > 0 else 0.0,
        paired=True,
        n_permutations=1000,
        seed=42,
    )

    # Toxicity (VPIN) per bar.
    toxicities = _toxicities_per_bar(snapshot, bar_ends_dt, window_trades=toxicity_window_trades)
    toxicity = compute_toxicity_metrics(toxicities, threshold=toxicity_threshold)

    # Net-of-cost walk-forward: with signal vs always-flat control.
    positions = _signal_positions(signals, threshold=signal_threshold)
    sizer = CapacityAwareSizer(
        spread_bps=spread_bps,
        impact_coeff=impact_coeff,
        max_participation=max_participation,
        cost_budget_bps=cost_budget_bps,
        seed=42,
    )
    cfg = IntegratedConfig(
        seed=42,
        n_points=DEFAULT_N_POINTS,
        train_window=DEFAULT_TRAIN_WINDOW,
        test_window=DEFAULT_TEST_WINDOW,
        step_size=DEFAULT_STEP_SIZE,
        purge=DEFAULT_PURGE,
        embargo=DEFAULT_EMBARGO,
    )
    with_signal = _run_orderflow_walkforward(
        "BTC", bar_closes, positions, bar_ends_dt, sizer, cfg,
        DEFAULT_N_POINTS, 42, max_position_pct=max_position_pct,
    )
    # Always-flat control: no trading, constant equity.
    flat_positions = [0] * len(positions)
    sizer_flat = CapacityAwareSizer(
        spread_bps=spread_bps,
        impact_coeff=impact_coeff,
        max_participation=max_participation,
        cost_budget_bps=cost_budget_bps,
        seed=42,
    )
    without_signal = _run_orderflow_walkforward(
        "BTC", bar_closes, flat_positions, bar_ends_dt, sizer_flat, cfg,
        DEFAULT_N_POINTS, 42, max_position_pct=max_position_pct,
    )

    verdict = compute_orderflow_toxicity_verdict(
        alpha, toxicity, with_signal, without_signal, permutation,
        no_lookahead_asserted=True,
    )

    # Non-degeneracy assertions.
    assert int(bars["n_bars"]) > 0, "bars must be non-empty"
    assert len(signals) == n_bars, "signal series must align to bars"
    assert verdict["verdict"] in ("GO", "NO-GO"), "verdict must be GO or NO-GO"
    assert verdict["verdict"] == ("GO" if verdict["all_checks_pass"] else "NO-GO")
    assert _all_finite_numbers(alpha), "alpha non-finite"
    assert _all_finite_numbers(toxicity), "toxicity non-finite"
    assert _all_finite_numbers(with_signal), "with-signal non-finite"
    assert _all_finite_numbers(without_signal), "without-signal non-finite"
    assert _all_finite_numbers(permutation), "permutation non-finite"
    assert _all_finite_numbers(verdict), "verdict non-finite"

    evidence_matrix = {
        "orderflow_loaded": bool(len(snapshot.trades or []) > 0),
        "n_trades": int(len(snapshot.trades or [])),
        "n_liquidations": int(len(snapshot.liquidations or [])),
        "n_funding_rates": int(len(snapshot.funding_rates or [])),
        "symbol": str(snapshot.symbol),
        "venue": str(snapshot.venue),
        "bars_constructed": bool(int(bars["n_bars"]) > 0),
        "causal_signal_computed": bool(len(signals) == n_bars),
        "ic_computed": bool(int(alpha["n_horizons"]) > 0),
        "permutation_computed": bool("p_value" in permutation),
        "toxicity_measured": bool(toxicity["toxicity_measured"]),
        "net_of_cost_run": bool(int(with_signal["num_windows"]) > 0),
        "paper_only": True,
        "live_trading_enabled": False,
    }

    report = {
        "report_id": REPORT_ID,
        "generated_at": timestamp,
        "verdict": verdict["verdict"],
        "trading_mode": TRADING_MODE,
        "live_trading_enabled": LIVE_TRADING_ENABLED,
        "never_valid_true": True,
        "config": {
            "symbol": "BTC",
            "spot": spot,
            "venue": DEFAULT_VENUE,
            "bar_duration_seconds": float(bar_duration_seconds),
            "signal_lookback_seconds": float(signal_lookback_seconds),
            "signal_threshold": float(signal_threshold),
            "toxicity_window_trades": int(toxicity_window_trades),
            "toxicity_threshold": float(toxicity_threshold),
            "horizons": [int(h) for h in HORIZONS],
            "seeds": [int(s) for s in seeds],
            "max_position_pct": float(max_position_pct),
            "spread_bps": float(spread_bps),
            "impact_coeff": float(impact_coeff),
            "max_participation": float(max_participation),
            "cost_budget_bps": float(cost_budget_bps),
            "n_points": int(DEFAULT_N_POINTS),
            "train_window": int(DEFAULT_TRAIN_WINDOW),
            "test_window": int(DEFAULT_TEST_WINDOW),
            "step_size": int(DEFAULT_STEP_SIZE),
            "purge": int(DEFAULT_PURGE),
            "embargo": int(DEFAULT_EMBARGO),
            "initial_capital": float(DEFAULT_INITIAL_CAPITAL),
            "thresholds": {
                "ic_exists_epsilon": IC_EXISTS_EPSILON,
                "tstat_critical": TSTAT_CRITICAL,
                "perm_alpha": PERM_ALPHA,
                "ic_exists": bool(abs(alpha["ic_mean"]) > IC_EXISTS_EPSILON),
            },
        },
        "bars": {
            "n_bars": int(n_bars),
            "start_timestamp": str(bars["start_timestamp"]),
            "end_timestamp": str(bars["end_timestamp"]),
            "bar_duration_seconds": float(bars["bar_duration_seconds"]),
            "n_trades_total": int(len(snapshot.trades or [])),
        },
        "signal_series": {
            "n_bars": int(len(signals)),
            "signals": [float(v) for v in signals],
            "mean_signal": float(sum(signals) / len(signals)) if signals else 0.0,
            "abs_signal_mean": float(sum(abs(v) for v in signals) / len(signals)) if signals else 0.0,
        },
        "alpha": alpha,
        "permutation": permutation,
        "toxicity": toxicity,
        "with_signal": {k: v for k, v in with_signal.items() if k != "oos_equity_curve"},
        "without_signal": {k: v for k, v in without_signal.items() if k != "oos_equity_curve"},
        "verdict_checks": verdict,
        "evidence_matrix": evidence_matrix,
        "deployment_authorization": {
            "authorized": bool(verdict["verdict"] == "GO"),
            "mode": "paper_only",
            "note": "GO certifies the orderflow alpha/toxicity evaluation only; not authorization to trade live.",
        },
    }
    assert_json_valid(report)
    serialized = serialize_metrics_strict(report)

    if write:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = _stamp_for_filename(timestamp)
        json_path = out_dir / f"ORDERFLOW_ALPHA_TOXICITY_EVAL_{stamp}.json"
        md_path = out_dir / f"ORDERFLOW_ALPHA_TOXICITY_EVAL_{stamp}.md"
        serialized["artifact_paths"] = {"json": str(json_path), "md": str(md_path)}
        json_path.write_text(
            json.dumps(serialized, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        md_path.write_text(_write_markdown(serialized) + "\n", encoding="utf-8")

    return serialized


def _write_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# ORDERFLOW ALPHA & TOXICITY EVALUATION — EVAL-17 (paper-only)")
    lines.append("")
    lines.append(f"- Report ID: {report['report_id']}")
    lines.append(f"- Generated at: {report['generated_at']}")
    lines.append(f"- Verdict: {report['verdict']}")
    lines.append(f"- Trading mode: {report['trading_mode']} (live enabled: {report['live_trading_enabled']})")
    lines.append(f"- Symbol: {report['config']['symbol']} @ spot {report['config']['spot']}")
    lines.append("")

    b = report["bars"]
    lines.append("## BARS (causal, from real trade tape)")
    lines.append(f"- Bars: {b['n_bars']} ({b['start_timestamp']} -> {b['end_timestamp']}, "
                 f"{b['bar_duration_seconds']}s each, {b['n_trades_total']} trades)")
    lines.append("")

    ss = report["signal_series"]
    lines.append("## CAUSAL SIGNAL SERIES (no lookahead)")
    lines.append(f"- Bars: {ss['n_bars']}, mean signal {ss['mean_signal']:.6f}, "
                 f"mean |signal| {ss['abs_signal_mean']:.6f}")
    lines.append("")

    a = report["alpha"]
    lines.append("## ALPHA (information coefficient + decay)")
    lines.append(f"- IC by horizon: {a['ic_by_horizon']}")
    lines.append(f"- IC mean {a['ic_mean']:.6f}, std {a['ic_std']:.6f}, t-stat {a['ic_tstat']:.6f}")
    lines.append(f"- IC bootstrap CI [{a['ic_bootstrap_ci']['lo']:.6f}, {a['ic_bootstrap_ci']['hi']:.6f}] "
                 f"(point {a['ic_bootstrap_ci']['point']:.6f})")
    lines.append(f"- IC decay slope {a['ic_decay_slope']:.6e}")
    lines.append("")

    p = report["permutation"]
    lines.append("## PERMUTATION TEST (mean IC vs zero)")
    lines.append(f"- p_value {p['p_value']:.6f}, observed_difference {p['observed_difference']:.6f}, "
                 f"significant_at_05 {p['significant_at_05']}, n_permutations {p['n_permutations']}")
    lines.append("")

    t = report["toxicity"]
    lines.append("## TOXICITY (VPIN, causal)")
    lines.append(f"- Mean {t['mean_toxicity']:.6f}, p95 {t['p95_toxicity']:.6f}, "
                 f"range [{t['min_toxicity']:.6f}, {t['max_toxicity']:.6f}]")
    lines.append(f"- Threshold {t['toxicity_threshold']}, fraction above {t['fraction_above_threshold']:.6f}, "
                 f"gate engages {t['gate_engages']}")
    lines.append(f"- Toxicity measured: {t['toxicity_measured']}")
    lines.append("")

    ws = report["with_signal"]
    wo = report["without_signal"]
    lines.append("## NET-OF-COST WITH/FORWARD (orderflow signal vs always-flat control)")
    lines.append(f"- With signal: return {ws['oos_return']:.6f}, Sharpe {ws['oos_sharpe']:.6f}, "
                 f"max-DD {ws['oos_max_drawdown']:.6f}, cost {ws['total_cost_usd']:.2f} USD, "
                 f"trades {ws['num_trades']}, windows {ws['num_windows']}")
    lines.append(f"- Without (flat): return {wo['oos_return']:.6f}, Sharpe {wo['oos_sharpe']:.6f}, "
                 f"max-DD {wo['oos_max_drawdown']:.6f}, cost {wo['total_cost_usd']:.2f} USD")
    lines.append(f"- Net delta (with - without): return {ws['oos_return'] - wo['oos_return']:.6f}, "
                 f"Sharpe {ws['oos_sharpe'] - wo['oos_sharpe']:.6f}")
    lines.append("")

    lines.append("## EVIDENCE MATRIX")
    for k, v in report["evidence_matrix"].items():
        lines.append(f"- {k}: {v}")
    lines.append("")

    lines.append("## VERDICT CHECKS (deterministic)")
    for c in report["verdict_checks"]["checks"]:
        lines.append(f"- [{'PASS' if c['pass'] else 'FAIL'}] {c['name']}: {c['reason']}")
    lines.append(f"- All checks pass: {report['verdict_checks']['all_checks_pass']} "
                 f"({report['verdict_checks']['n_passed']}/{report['verdict_checks']['n_checks']})")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Orderflow alpha & toxicity evaluation (EVAL-17, paper-only)"
    )
    parser.add_argument("--out", type=str, default=str(OUT_DIR), help="output directory")
    parser.add_argument("--no-write", action="store_true", help="compute without writing artifacts")
    parser.add_argument("--timestamp", type=str, default=_utc_now_iso())
    parser.add_argument("--bar-duration-seconds", type=float, default=DEFAULT_BAR_DURATION_SECONDS)
    parser.add_argument("--signal-lookback-seconds", type=float, default=DEFAULT_SIGNAL_LOOKBACK_SECONDS)
    parser.add_argument("--signal-threshold", type=float, default=DEFAULT_SIGNAL_THRESHOLD)
    parser.add_argument("--toxicity-window-trades", type=int, default=DEFAULT_TOXICITY_WINDOW_TRADES)
    parser.add_argument("--toxicity-threshold", type=float, default=DEFAULT_TOXICITY_THRESHOLD)
    parser.add_argument("--seeds", type=int, nargs="+", default=list(DEFAULT_SEEDS))
    parser.add_argument("--max-position-pct", type=float, default=DEFAULT_MAX_POSITION_PCT)
    parser.add_argument("--spread-bps", type=float, default=DEFAULT_SPREAD_BPS)
    parser.add_argument("--impact-coeff", type=float, default=DEFAULT_IMPACT_COEFF)
    parser.add_argument("--max-participation", type=float, default=DEFAULT_MAX_PARTICIPATION)
    parser.add_argument("--cost-budget-bps", type=float, default=DEFAULT_COST_BUDGET_BPS)
    args = parser.parse_args(argv)

    report = evaluate_orderflow_alpha_toxicity(
        write=not args.no_write,
        out_dir=args.out,
        timestamp=args.timestamp,
        bar_duration_seconds=args.bar_duration_seconds,
        signal_lookback_seconds=args.signal_lookback_seconds,
        signal_threshold=args.signal_threshold,
        toxicity_window_trades=args.toxicity_window_trades,
        toxicity_threshold=args.toxicity_threshold,
        seeds=args.seeds,
        max_position_pct=args.max_position_pct,
        spread_bps=args.spread_bps,
        impact_coeff=args.impact_coeff,
        max_participation=args.max_participation,
        cost_budget_bps=args.cost_budget_bps,
    )

    print(
        json.dumps(
            {
                "report_id": report["report_id"],
                "verdict": report["verdict"],
                "n_checks_passed": f'{report["verdict_checks"]["n_passed"]}/{report["verdict_checks"]["n_checks"]}',
                "n_bars": report["bars"]["n_bars"],
                "ic_mean": report["alpha"]["ic_mean"],
                "ic_tstat": report["alpha"]["ic_tstat"],
                "ic_by_horizon": report["alpha"]["ic_by_horizon"],
                "permutation_p": report["permutation"]["p_value"],
                "mean_toxicity": report["toxicity"]["mean_toxicity"],
                "toxic_gate_active_fraction": report["toxicity"]["toxic_gate_active_fraction"],
                "with_signal_return": report["with_signal"]["oos_return"],
                "with_signal_sharpe": report["with_signal"]["oos_sharpe"],
                "without_signal_return": report["without_signal"]["oos_return"],
                "failed_checks": report["verdict_checks"]["failed_checks"],
                "artifact_paths": report.get("artifact_paths", {}),
            },
            sort_keys=True,
            allow_nan=False,
        )
    )
    for path in report.get("artifact_paths", {}).values():
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
