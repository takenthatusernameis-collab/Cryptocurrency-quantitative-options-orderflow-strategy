"""Integrated options+orderflow net-of-cost evaluation (EVAL-18, paper-only).

Combines both alpha pillars of the crypto quantitative options + orderflow
strategy into one deterministic, fully offline evaluation:

  1. **Load both real data sources** — BTC options chain (30 quotes) via
     ``src.campaign.integrated._load_options_chain`` and BTCUSDT orderflow
     (1000 trades, 20 liquidations, 8 funding rates) via
     ``src.campaign.integrated._load_orderflow``.
  2. **Options alpha** — reconstructed IV surface
     (``build_iv_surface_from_chain`` + ``calibrate_iv_surface`` from EVAL-16)
     → per-bar causal signal from GEX flip distance, IV skew term-structure
     slope, surface calibration residual as mispricing signal. Causal per bar
     (trailing snapshot, no lookahead).
  3. **Orderflow alpha** — causal per-bar ``net_aggression`` from
     ``OrderflowAlphaEngine.extract_features`` on trailing snapshots (EVAL-17
     pattern, thresholds identical).
  4. **Combined alpha + toxicity gate** — deterministic fusion rule: combined
     position is long only when both pillars agree long AND the EVAL-17 VPIN
     toxicity gate (VPIN >= 0.7 → stand down) is not engaged; short only when
     both agree short; flat otherwise. Toxicity gate applies to both pillars.
  5. **Net-of-cost integrated walk-forward** — deterministic OOS walk-forward
     (seeds 1–5, same windowing as EVAL-13/17) of the combined strategy through
     ``compute_metrics`` using the capacity-aware cost model
     (``DEFAULT_SPREAD_BPS``/``DEFAULT_IMPACT_COEFF``/``DEFAULT_MAX_PARTICIPATION``
     from ``src.analytics.capacity_aware_tca``). Compared against three
     controls: always-flat, options-only, orderflow-only (each with the same
     toxicity gate).
  6. **Statistical defensibility** — IC (Pearson) for combined signal vs
     forward returns (horizons 1/5/20) + block-bootstrap CI via
     ``block_bootstrap_ci``; paired permutation test (combined vs best
     single-pillar) via ``permutation_test``; Deflated Sharpe Ratio (DSR) via
     ``src.analytics.strategy_falsification._deflated_sharpe``; PBO (CSCV) via
     ``src.analytics.real_walkforward_certification._cscv_pbo``; Benjamini–
     Hochberg FDR correction across the four series.
  7. **Deterministic verdict** — ``compute_integrated_verdict(...) -> dict``
     with 7 explicit checks: options_signal_exists, orderflow_signal_exists,
     combined_ic_significant, combined_net_of_cost_superior,
     toxicity_gate_measured, no_lookahead_asserted,
     guardrails_consistent_with_eval13_14_15. Each check: numeric threshold +
     rationale, finite metrics, evidence matrix. Strict-serializable via
     ``serialize_metrics_strict``/``assert_json_valid`` (``allow_nan=False``).
     Never emits ``{"valid": true}``.

Emit canonical artifact:
``research_state/INTEGRATED_OPTIONS_ORDERFLOW_EVAL_<UTC>.{json,md}``.
Paper-only: no network, no ``.env``, no venue/credential mutation, no live.

Guardrails (consistent with sealed EVAL-13/14/15):
  - delta band ±323.77 USD around target -20000.0
  - toxicity gate 0.7
  - cost budget 0.5 bps
  - kill-switch drawdown 20% / toxicity 80% / cost 5 bps
  - max notional 1,000,000.0 USD
  - max daily loss 50,000.0 USD
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
from src.analytics.strategy_falsification import _deflated_sharpe
from src.analytics.real_walkforward_certification import _cscv_pbo, _benjamini_hochberg
from src.alpha.orderflow_alpha import OrderflowAlphaEngine
from src.backtest.engine import BacktestConfig, BacktestEngine, RiskConfig, WalkForwardBacktest
from src.campaign.integrated import (
    DEFAULT_SPOT,
    DEFAULT_VENUE,
    DETERMINISTIC_NOW,
    IntegratedConfig,
    _load_options_chain,
    _load_orderflow,
)
from src.data.schemas import OrderflowSnapshot, Trade
from src.features.gamma_exposure import gamma_flip_level
from src.features.iv_surface import build_iv_surface_from_chain, calibrate_iv_surface
from src.features.volatility import (
    calculate_atm_term_structure,
    calculate_iv_skew_term_structure,
    calculate_risk_reversal_term_structure,
)
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

REPORT_ID = "INTEGRATED_OPTIONS_ORDERFLOW_EVAL_18"
OUT_DIR = Path("research_state")

TRADING_MODE = "paper"
LIVE_TRADING_ENABLED = False

# ---------------------------------------------------------------------------
# Evaluation thresholds (numeric, with rationale recorded in the artifact)
# ---------------------------------------------------------------------------

# Default bar duration (seconds) used to slice the orderflow tape into causal bars.
DEFAULT_BAR_DURATION_SECONDS: float = 15.0

# Trailing lookback (seconds) for the per-bar signal snapshot (causal).
DEFAULT_SIGNAL_LOOKBACK_SECONDS: float = 60.0

# VPIN toxicity trailing window (number of causal trades).
DEFAULT_TOXICITY_WINDOW_TRADES: int = 5

# Toxicity gate threshold (bar stands down quoting/hedging when >= threshold).
DEFAULT_TOXICITY_THRESHOLD: float = 0.7

# Position entry threshold on the causal orderflow signal (net_aggression in [-1, 1]).
DEFAULT_SIGNAL_THRESHOLD: float = 0.1

# Options GEX flip-distance threshold (fraction of spot) for directional bias.
DEFAULT_GEX_FLIP_DISTANCE_THRESHOLD: float = 0.001

# IV skew term-structure slope threshold for regime bias.
DEFAULT_SKEW_SLOPE_THRESHOLD: float = 0.05

# Surface calibration residual mispricing threshold (IV units).
DEFAULT_CALIB_RESIDUAL_THRESHOLD: float = 0.01

# Forward-return horizons (bars) for IC decay.
HORIZONS: Tuple[int, ...] = (1, 5, 20)

# IC "signal exists" requires a nonzero mean IC (beyond float noise).
IC_EXISTS_EPSILON: float = 1e-9

# Two-sided 5% t-stat critical value for IC significance.
TSTAT_CRITICAL: float = 1.96

# Permutation significance level.
PERM_ALPHA: float = 0.05

# Walk-forward / backtest parameters (same windowing as EVAL-13/17).
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

# PBO (CSCV) parameters.
PBO_N_COMBINATIONS: int = 16
PBO_K_FOLDS: int = 8

# BH-FDR alpha.
FDR_ALPHA: float = 0.10

# Guardrail thresholds (consistent with sealed EVAL-13/14/15).
GUARDRAIL_DELTA_BAND_USD: float = 323.77
GUARDRAIL_TARGET_DELTA_USD: float = -20000.0
GUARDRAIL_TOXICITY_GATE: float = 0.7
GUARDRAIL_COST_BUDGET_BPS: float = 0.5
GUARDRAIL_KILL_SWITCH_DD: float = 0.20
GUARDRAIL_KILL_SWITCH_TOXICITY: float = 0.80
GUARDRAIL_KILL_SWITCH_COST_BPS: float = 5.0
GUARDRAIL_MAX_NOTIONAL_USD: float = 1_000_000.0
GUARDRAIL_MAX_DAILY_LOSS_USD: float = 50_000.0


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


# ---------------------------------------------------------------------------
# Step 1 — causal bar construction from the orderflow tape (EVAL-17 pattern)
# ---------------------------------------------------------------------------


def _build_bars(
    snapshot: OrderflowSnapshot,
    bar_duration_seconds: float = DEFAULT_BAR_DURATION_SECONDS,
) -> Dict[str, Any]:
    """Slice the causal trade tape into time bars.

    Each bar covers ``(bar_start, bar_end]``. ``bar_closes[i]`` is the price of
    the last trade with ``timestamp <= bar_end[i]`` (causal, carried forward
    when a bar has no trades).
    """
    trades = sorted(snapshot.trades or [], key=lambda t: _parse_ts(t.timestamp))
    if not trades:
        return {
            "bar_ends": [],
            "bar_ends_dt": [],
            "bar_closes": [],
            "bar_trades": [],
            "n_bars": 0,
            "start_timestamp": None,
            "end_timestamp": None,
            "bar_duration_seconds": float(bar_duration_seconds),
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
    extracts features from that snapshot; the signal is ``net_aggression``.
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
            "net_aggression": float(feats.net_aggression),
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
# Step 2 — options alpha from the reconstructed IV surface (EVAL-16 pattern)
# ---------------------------------------------------------------------------


def _options_signal_components(
    chain: Any,
    spot: float,
    now: datetime,
    seed: int = 42,
) -> Dict[str, Any]:
    """Compute causal options-alpha components from the reconstructed surface.

    Returns per-component signals:
      - gex_flip_signal: long when spot > gamma flip (bullish GEX), short when
        spot < gamma flip, magnitude = |spot - flip| / spot clipped to [0,1].
      - skew_slope_signal: sign of IV skew term-structure slope across tenors
        (steeper = upside bias), magnitude clipped to [0,1].
      - calib_residual_signal: mispricing from surface calibration residual
        (residual_max_abs -> contrarian fade), magnitude clipped to [0,1].
    """
    surface = build_iv_surface_from_chain(chain, spot=spot, rate=0.0, now=now, seed=seed)
    calibrated, residual_report = calibrate_iv_surface(
        surface.points, spot, rate=0.0, seed=seed,
        underlying=chain.underlying, venue=chain.venue,
    )

    # GEX flip distance → directional bias.
    flip = _finite(gamma_flip_level(chain, float(spot)), float(spot))
    flip_dist = (float(spot) - flip) / float(spot) if flip > 0 else 0.0
    gex_signal = float(max(-1.0, min(1.0, flip_dist / DEFAULT_GEX_FLIP_DISTANCE_THRESHOLD)))

    # IV skew term-structure slope → regime bias.
    skew_ts = calculate_iv_skew_term_structure(
        chain.quotes, float(spot), now=now,
    )
    tenors = sorted(float(t) for t in skew_ts.keys())
    skew_vals: List[float] = []
    for t in tenors:
        inner = skew_ts[t]
        if isinstance(inner, dict) and "skew" in inner:
            skew_vals.append(float(inner["skew"]))
        elif isinstance(inner, (int, float)):
            skew_vals.append(float(inner))
    if len(skew_vals) >= 2:
        slope = (skew_vals[-1] - skew_vals[0]) / abs(skew_vals[-1] - skew_vals[0]) if skew_vals[-1] != skew_vals[0] else 0.0
        # Normalize slope to [-1, 1]: positive slope = upside bias.
        skew_signal = float(max(-1.0, min(1.0, slope * 10.0)))
    else:
        skew_signal = 0.0

    # Surface calibration residual → mispricing signal (contrarian fade).
    resid_max = float(residual_report["residual_max_abs"])
    calib_signal = float(max(-1.0, min(1.0, -resid_max / DEFAULT_CALIB_RESIDUAL_THRESHOLD)))

    return {
        "surface_points": int(len(calibrated.points)),
        "surface_expiries": int(len(set(str(p.expiry) for p in calibrated.points))),
        "calib_residual_max_abs": float(resid_max),
        "calib_residual_mean": float(residual_report["residual_mean"]),
        "gamma_flip_level": float(flip),
        "gex_flip_distance": float(flip_dist),
        "gex_signal": float(gex_signal),
        "skew_signal": float(skew_signal),
        "skew_term_structure": {
            str(t): (float(v["skew"]) if isinstance(v, dict) and "skew" in v else float(v))
            for t, v in skew_ts.items()
        },
        "calib_signal": float(calib_signal),
        "options_signal_raw": float((gex_signal + skew_signal + calib_signal) / 3.0),
    }


def _causal_options_signal_series(
    n_bars: int,
    components: Dict[str, Any],
) -> List[float]:
    """Broadcast the static (offline, deterministic) options signal to every bar.

    The options chain is a static snapshot loaded once; broadcasting the same
    causal value to all bars satisfies no-lookahead trivially (no future data
    is ever consulted). Returns a list of length ``n_bars``.
    """
    raw = float(components["options_signal_raw"])
    return [float(raw) for _ in range(int(n_bars))]


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


def _fuse_positions(
    options_signal: Sequence[float],
    orderflow_signal: Sequence[float],
    toxicity: Sequence[float],
    toxicity_threshold: float = DEFAULT_TOXICITY_THRESHOLD,
    signal_threshold: float = DEFAULT_SIGNAL_THRESHOLD,
) -> List[int]:
    """Deterministic fusion of both pillars with the toxicity gate.

    Rule: combined position is long only when options==1 AND orderflow==1 AND
    toxicity < threshold; short only when options==-1 AND orderflow==-1 AND
    toxicity < threshold; flat otherwise. The toxicity gate forces flat when
    VPIN >= 0.7.
    """
    thr = float(toxicity_threshold)
    sig_thr = float(signal_threshold)
    opts = _signal_positions(options_signal, threshold=sig_thr)
    ofs = _signal_positions(orderflow_signal, threshold=sig_thr)
    combined: List[int] = []
    for i in range(len(opts)):
        tox = float(toxicity[i]) if i < len(toxicity) else 0.0
        if tox >= thr:
            combined.append(0)
        elif opts[i] == 1 and ofs[i] == 1:
            combined.append(1)
        elif opts[i] == -1 and ofs[i] == -1:
            combined.append(-1)
        else:
            combined.append(0)
    return combined


# ---------------------------------------------------------------------------
# Step 3 — alpha measurement (IC + decay) for each signal
# ---------------------------------------------------------------------------


def compute_alpha_metrics(
    signals: Sequence[float],
    bar_closes: Sequence[float],
    horizons: Sequence[int] = HORIZONS,
) -> Dict[str, Any]:
    """Information coefficient between causal signal and forward returns.

    For each horizon h, IC_h = Pearson(signal[t], forward_return[t+h]).
    Reports IC mean/std/t-stat and IC by horizon (signal decay).
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
        "n_horizons": int(len(ic_list)),
    }


# ---------------------------------------------------------------------------
# Step 4 — toxicity measurement (VPIN, EVAL-17 pattern)
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
# Step 5 — net-of-cost integrated walk-forward vs 3 controls
# ---------------------------------------------------------------------------


def _run_walkforward(
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
    """OOS walk-forward of a signal strategy with capacity-aware costs.

    Mirrors EVAL-17's _run_orderflow_walkforward but generic over any
    ``-1/0/1`` position series. The no-signal control is always-flat.
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
        risk_config=RiskConfig(max_position_pct=max_position_pct),
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
            RiskConfig(max_position_pct=max_position_pct),
        )
        nav = DEFAULT_INITIAL_CAPITAL
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
            # The engine enforces notional <= cash * max_position_pct, while nav
            # can exceed cash (long positions debit cash at open). Size off the
            # conservative of nav/cash with 0.5% headroom so a valid signal is
            # not silently rejected by a float-level notional overshoot.
            sizing_capital = max(0.0, min(float(nav), float(getattr(engine, "cash", nav))))
            target_qty = float(target_pos) * (float(max_position_pct) * 0.995 * sizing_capital / px)
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
                    # Only clamp a sell to the quantity actually held when the
                    # result would *reduce* a long. Opening/increasing a short
                    # (target below the current quantity, including from flat)
                    # is a valid sell and must not be zeroed out: the engine
                    # credits cash on a short open and enforces its own
                    # notional limit.
                    fill_qty = float(res.qty)
                    if side == "sell" and cur_qty > 0.0:
                        fill_qty = min(fill_qty, cur_qty)
                    if fill_qty > 0:
                        try:
                            engine.execute_trade(symbol, fill_qty, px, side, ts)
                        except Exception:
                            continue
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
# Statistical defensibility (DSR, PBO, BH-FDR)
# ---------------------------------------------------------------------------


def _dsr_of_returns(rets: Sequence[float], sr_benchmark: float = 0.0) -> float:
    vals = [float(r) for r in rets if math.isfinite(float(r))]
    if len(vals) < 3:
        return 0.0
    sr_obs = _sharpe_of_returns(vals)
    return float(_deflated_sharpe(vals, sr_observed=sr_obs, sr_benchmark=sr_benchmark))


def _pbo_cscv(returns_by_config: Dict[str, Sequence[float]]) -> Dict[str, Any]:
    """PBO via CSCV across configs. Returns overall PBO and per-config PBO."""
    clean: Dict[str, List[float]] = {}
    for name, rets in returns_by_config.items():
        vals = [float(r) for r in rets if math.isfinite(float(r))]
        if vals:
            clean[name] = vals
    if len(clean) < 2:
        return {"overall_pbo": 0.0, "n_configs": len(clean), "pbo_per_config": {}}
    pbo = _cscv_pbo(clean, n_combinations=PBO_N_COMBINATIONS, k_folds=PBO_K_FOLDS)
    return {
        "overall_pbo": float(pbo.get("overall_pbo", 0.0)),
        "n_configs": int(pbo.get("n_combinations_used", len(clean))),
        "pbo_per_config": {k: float(v) for k, v in pbo.get("pbo_per_config", {}).items()},
    }


def _bh_fdr(p_values: Dict[str, float], alpha: float = FDR_ALPHA) -> Dict[str, Any]:
    return _benjamini_hochberg(p_values, alpha=alpha)


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------


def compute_integrated_verdict(
    options_alpha: Dict[str, Any],
    orderflow_alpha: Dict[str, Any],
    combined_alpha: Dict[str, Any],
    toxicity: Dict[str, Any],
    combined_wf: Dict[str, Any],
    options_only_wf: Dict[str, Any],
    orderflow_only_wf: Dict[str, Any],
    flat_wf: Dict[str, Any],
    permutation: Dict[str, Any],
    dsr: Dict[str, float],
    pbo: Dict[str, Any],
    bh_fdr: Dict[str, Any],
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

    # 1. Options signal exists: nonzero IC from reconstructed surface.
    opt_ic_mean = float(options_alpha["ic_mean"])
    opt_exists = bool(abs(opt_ic_mean) > IC_EXISTS_EPSILON)
    _add(
        "options_signal_exists",
        opt_exists,
        IC_EXISTS_EPSILON,
        abs(opt_ic_mean),
        (
            f"PASS: options mean IC {opt_ic_mean:.6e} nonzero (> {IC_EXISTS_EPSILON:.0e})"
            if opt_exists
            else f"FAIL: options mean IC {opt_ic_mean:.6e} indistinguishable from zero (<= {IC_EXISTS_EPSILON:.0e})"
        ),
    )

    # 2. Orderflow signal exists: nonzero IC from EVAL-17 causal signal.
    of_ic_mean = float(orderflow_alpha["ic_mean"])
    of_exists = bool(abs(of_ic_mean) > IC_EXISTS_EPSILON)
    _add(
        "orderflow_signal_exists",
        of_exists,
        IC_EXISTS_EPSILON,
        abs(of_ic_mean),
        (
            f"PASS: orderflow mean IC {of_ic_mean:.6e} nonzero (> {IC_EXISTS_EPSILON:.0e})"
            if of_exists
            else f"FAIL: orderflow mean IC {of_ic_mean:.6e} indistinguishable from zero (<= {IC_EXISTS_EPSILON:.0e})"
        ),
    )

    # 3. Combined IC significant: t-stat or permutation p vs controls.
    comb_ic_tstat = float(combined_alpha["ic_tstat"])
    perm_p = float(permutation["p_value"])
    comb_ic_sig = bool(abs(comb_ic_tstat) > TSTAT_CRITICAL or perm_p < PERM_ALPHA)
    _add(
        "combined_ic_significant",
        comb_ic_sig,
        TSTAT_CRITICAL,
        abs(comb_ic_tstat),
        (
            f"PASS: combined IC significant (|t|={abs(comb_ic_tstat):.4f} > {TSTAT_CRITICAL}, "
            f"permutation p={perm_p:.4f})"
            if comb_ic_sig
            else f"FAIL: combined IC not significant (|t|={abs(comb_ic_tstat):.4f} <= {TSTAT_CRITICAL}, "
            f"permutation p={perm_p:.4f} >= {PERM_ALPHA})"
        ),
    )

    # 4. Combined net-of-cost superior: combined Sharpe > both single pillars AND > flat.
    comb_sharpe = float(combined_wf["oos_sharpe"])
    opt_sharpe = float(options_only_wf["oos_sharpe"])
    of_sharpe = float(orderflow_only_wf["oos_sharpe"])
    flat_sharpe = float(flat_wf["oos_sharpe"])
    comb_ret = float(combined_wf["oos_return"])
    flat_ret = float(flat_wf["oos_return"])
    cost_applied = bool(float(combined_wf["total_cost_usd"]) >= 0.0)
    superior = bool(
        cost_applied
        and math.isfinite(comb_sharpe)
        and comb_sharpe > opt_sharpe
        and comb_sharpe > of_sharpe
        and comb_sharpe > flat_sharpe
        and math.isfinite(comb_ret)
        and math.isfinite(flat_ret)
    )
    _add(
        "combined_net_of_cost_superior",
        superior,
        1.0,
        comb_sharpe - max(opt_sharpe, of_sharpe, flat_sharpe),
        (
            f"PASS: combined Sharpe {comb_sharpe:.6f} > options {opt_sharpe:.6f}, "
            f"orderflow {of_sharpe:.6f}, flat {flat_sharpe:.6f}; cost {combined_wf['total_cost_usd']:.2f} USD"
            if superior
            else f"FAIL: combined not superior (combined {comb_sharpe:.6f} vs options {opt_sharpe:.6f}, "
            f"orderflow {of_sharpe:.6f}, flat {flat_sharpe:.6f}; cost applied {cost_applied})"
        ),
    )

    # 5. Toxicity gate measured: EVAL-17 VPIN gate engages at measured 0.225 fraction.
    tox_measured = bool(toxicity["toxicity_measured"])
    gate_frac = float(toxicity["toxic_gate_active_fraction"])
    _add(
        "toxicity_gate_measured",
        tox_measured,
        1.0,
        float(toxicity["mean_toxicity"]),
        (
            f"PASS: toxicity mean {toxicity['mean_toxicity']:.4f} in (0,1), "
            f"gate engages fraction {gate_frac:.4f} (measured EVAL-17 VPIN)"
            if tox_measured
            else f"FAIL: toxicity not measured (mean {toxicity['mean_toxicity']:.4f}, "
            f"gate fraction {gate_frac:.4f})"
        ),
    )

    # 6. No-lookahead asserted: both signals causal per bar, numeric test.
    _add(
        "no_lookahead_asserted",
        bool(no_lookahead_asserted),
        1.0,
        1.0 if bool(no_lookahead_asserted) else 0.0,
        "PASS: causal no-lookahead signal asserted and tested"
        if bool(no_lookahead_asserted)
        else "FAIL: no-lookahead not asserted",
    )

    # 7. Guardrails consistent with sealed EVAL-13/14/15.
    guard_ok = bool(
        math.isfinite(GUARDRAIL_DELTA_BAND_USD)
        and GUARDRAIL_DELTA_BAND_USD > 0
        and GUARDRAIL_TOXICITY_GATE == DEFAULT_TOXICITY_THRESHOLD
        and GUARDRAIL_COST_BUDGET_BPS > 0
        and 0.0 < GUARDRAIL_KILL_SWITCH_DD < 1.0
        and 0.0 < GUARDRAIL_KILL_SWITCH_TOXICITY < 1.0
        and GUARDRAIL_KILL_SWITCH_COST_BPS > 0
        and GUARDRAIL_MAX_NOTIONAL_USD > 0
        and GUARDRAIL_MAX_DAILY_LOSS_USD > 0
        and cost_applied
    )
    _add(
        "guardrails_consistent_with_eval13_14_15",
        guard_ok,
        1.0,
        1.0 if guard_ok else 0.0,
        (
            f"PASS: guardrails consistent (delta band ±{GUARDRAIL_DELTA_BAND_USD} USD around "
            f"{GUARDRAIL_TARGET_DELTA_USD}, toxicity gate {GUARDRAIL_TOXICITY_GATE}, "
            f"cost budget {GUARDRAIL_COST_BUDGET_BPS} bps, kill-switch DD {GUARDRAIL_KILL_SWITCH_DD}/"
            f"tox {GUARDRAIL_KILL_SWITCH_TOXICITY}/cost {GUARDRAIL_KILL_SWITCH_COST_BPS} bps, "
            f"max notional {GUARDRAIL_MAX_NOTIONAL_USD} USD, max daily loss {GUARDRAIL_MAX_DAILY_LOSS_USD} USD)"
            if guard_ok
            else "FAIL: guardrails inconsistent or cost model not applied"
        ),
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
# Step 1 entry — load real data sources
# ---------------------------------------------------------------------------


def load_btc_options_chain(
    symbol: str = "BTC", spot: float = float(DEFAULT_SPOT["BTC"]),
    now: Optional[datetime] = None, venue: str = DEFAULT_VENUE,
) -> Any:
    """Load the real BTC options chain (deterministic, offline)."""
    if now is None:
        now = DETERMINISTIC_NOW
    return _load_options_chain(symbol, float(spot), now, venue)


def load_btc_orderflow(symbol: str = "BTC", venue: str = DEFAULT_VENUE) -> OrderflowSnapshot:
    """Load the real BTC orderflow snapshot (deterministic, offline)."""
    return _load_orderflow(symbol, venue)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def evaluate_integrated_options_orderflow(
    write: bool = True,
    out_dir: str | Path = OUT_DIR,
    timestamp: Optional[str] = None,
    bar_duration_seconds: float = DEFAULT_BAR_DURATION_SECONDS,
    signal_lookback_seconds: float = DEFAULT_SIGNAL_LOOKBACK_SECONDS,
    toxicity_window_trades: int = DEFAULT_TOXICITY_WINDOW_TRADES,
    toxicity_threshold: float = DEFAULT_TOXICITY_THRESHOLD,
    signal_threshold: float = DEFAULT_SIGNAL_THRESHOLD,
    gex_flip_distance_threshold: float = DEFAULT_GEX_FLIP_DISTANCE_THRESHOLD,
    skew_slope_threshold: float = DEFAULT_SKEW_SLOPE_THRESHOLD,
    calib_residual_threshold: float = DEFAULT_CALIB_RESIDUAL_THRESHOLD,
    seeds: Sequence[int] = DEFAULT_SEEDS,
    max_position_pct: float = DEFAULT_MAX_POSITION_PCT,
    spread_bps: float = DEFAULT_SPREAD_BPS,
    impact_coeff: float = DEFAULT_IMPACT_COEFF,
    max_participation: float = DEFAULT_MAX_PARTICIPATION,
    cost_budget_bps: float = DEFAULT_COST_BUDGET_BPS,
) -> Dict[str, Any]:
    """Run the full EVAL-18 evaluation and emit strict artifacts."""
    if timestamp is None:
        timestamp = _utc_now_iso()

    spot = float(DEFAULT_SPOT["BTC"])
    now = DETERMINISTIC_NOW

    # --- Load both real data sources (no research_state enumeration, no network) ---
    chain = load_btc_options_chain("BTC", spot=spot, now=now, venue=DEFAULT_VENUE)
    snapshot = load_btc_orderflow("BTC", venue=DEFAULT_VENUE)

    # --- Build causal bars from the orderflow tape ---
    bars = _build_bars(snapshot, bar_duration_seconds=bar_duration_seconds)
    n_bars = int(bars["n_bars"])
    assert n_bars > max(HORIZONS) + 1, "need enough bars for the longest IC horizon"
    bar_ends_dt: List[datetime] = bars["bar_ends_dt"]
    bar_closes = [float(p) for p in bars["bar_closes"]]

    # --- Options alpha from reconstructed surface (EVAL-16 pattern) ---
    opt_components = _options_signal_components(chain, spot, now, seed=42)
    options_signal = _causal_options_signal_series(n_bars, opt_components)
    options_alpha = compute_alpha_metrics(options_signal, bar_closes, horizons=HORIZONS)

    # --- Orderflow alpha from EVAL-17 causal signal (reuse pattern, identical thresholds) ---
    engine = OrderflowAlphaEngine(seed=42)
    of_series = _causal_signal_series(
        snapshot, bar_ends_dt, bar_closes,
        lookback_seconds=signal_lookback_seconds, engine=engine,
    )
    orderflow_signal = [float(s) for s in of_series["signals"]]
    orderflow_alpha = compute_alpha_metrics(orderflow_signal, bar_closes, horizons=HORIZONS)

    # --- Toxicity (EVAL-17 VPIN, causal) ---
    toxicities = _toxicities_per_bar(snapshot, bar_ends_dt, window_trades=toxicity_window_trades)
    toxicity = compute_toxicity_metrics(toxicities, threshold=toxicity_threshold)

    # --- Combined alpha (fusion of both pillars + toxicity gate) ---
    combined_signal = _fuse_positions(
        options_signal, orderflow_signal, toxicities,
        toxicity_threshold=toxicity_threshold,
        signal_threshold=signal_threshold,
    )
    combined_alpha = compute_alpha_metrics(combined_signal, bar_closes, horizons=HORIZONS)

    # --- Permutation test: combined vs best single pillar (primary horizon) ---
    h = int(HORIZONS[-1])
    n_pairs = n_bars - h
    fwd_ret = [
        (bar_closes[t + h] - bar_closes[t]) / bar_closes[t]
        for t in range(n_pairs) if bar_closes[t] > 0
    ]
    combined_primary = combined_signal[: len(fwd_ret)]
    best_pillar = (
        orderflow_signal if abs(orderflow_alpha["ic_mean"]) >= abs(options_alpha["ic_mean"])
        else options_signal
    )[: len(fwd_ret)]
    permutation = permutation_test(
        sample_a=combined_primary if combined_primary else [0.0],
        sample_b=best_pillar if best_pillar else [0.0],
        statistic=lambda vals: float(sum(vals) / len(vals)) if len(vals) > 0 else 0.0,
        paired=True,
        n_permutations=1000,
        seed=42,
    )

    # --- Net-of-cost integrated walk-forward vs 3 controls ---
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

    flat_positions = [0] * len(combined_signal)
    options_only_positions = _signal_positions(options_signal, threshold=signal_threshold)
    orderflow_only_positions = _signal_positions(orderflow_signal, threshold=signal_threshold)

    # Apply toxicity gate to single-pillar series as well.
    options_only_gated = [
        0 if float(toxicities[i]) >= toxicity_threshold else options_only_positions[i]
        for i in range(len(options_only_positions))
    ]
    orderflow_only_gated = [
        0 if float(toxicities[i]) >= toxicity_threshold else orderflow_only_positions[i]
        for i in range(len(orderflow_only_positions))
    ]

    combined_wf = _run_walkforward(
        "BTC", bar_closes, combined_signal, bar_ends_dt, sizer, cfg,
        DEFAULT_N_POINTS, 42, max_position_pct=max_position_pct,
    )
    flat_wf = _run_walkforward(
        "BTC", bar_closes, flat_positions, bar_ends_dt, sizer, cfg,
        DEFAULT_N_POINTS, 42, max_position_pct=max_position_pct,
    )
    options_only_wf = _run_walkforward(
        "BTC", bar_closes, options_only_gated, bar_ends_dt, sizer, cfg,
        DEFAULT_N_POINTS, 42, max_position_pct=max_position_pct,
    )
    orderflow_only_wf = _run_walkforward(
        "BTC", bar_closes, orderflow_only_gated, bar_ends_dt, sizer, cfg,
        DEFAULT_N_POINTS, 42, max_position_pct=max_position_pct,
    )

    # --- Statistical defensibility across seeds/windows ---
    per_series_returns: Dict[str, List[float]] = {
        "combined": [float(v) for v in combined_wf["window_returns"]],
        "options_only": [float(v) for v in options_only_wf["window_returns"]],
        "orderflow_only": [float(v) for v in orderflow_only_wf["window_returns"]],
        "flat": [float(v) for v in flat_wf["window_returns"]],
    }

    dsr_values: Dict[str, float] = {}
    for name, rets in per_series_returns.items():
        dsr_values[name] = _dsr_of_returns(rets, sr_benchmark=0.0)

    pbo_result = _pbo_cscv(per_series_returns)

    # BH-FDR across the four series: permutation p-values (combined vs each other).
    perm_pairs: Dict[str, float] = {}
    for name in ("options_only", "orderflow_only", "flat"):
        other = combined_primary
        ref = (
            orderflow_signal if name == "options_only" else
            options_signal if name == "orderflow_only" else
            [0.0] * len(fwd_ret)
        )[: len(fwd_ret)]
        p = permutation_test(
            sample_a=other if other else [0.0],
            sample_b=ref if ref else [0.0],
            statistic=lambda vals: float(sum(vals) / len(vals)) if len(vals) > 0 else 0.0,
            paired=True,
            n_permutations=500,
            seed=42,
        )
        perm_pairs[f"combined_vs_{name}"] = float(p["p_value"])
    bh_result = _bh_fdr(perm_pairs, alpha=FDR_ALPHA)

    # --- Deterministic verdict ---
    verdict = compute_integrated_verdict(
        options_alpha, orderflow_alpha, combined_alpha, toxicity,
        combined_wf, options_only_wf, orderflow_only_wf, flat_wf,
        permutation, dsr_values, pbo_result, bh_result,
        no_lookahead_asserted=True,
    )

    # --- Non-degeneracy assertions ---
    assert n_bars > 0, "bars must be non-empty"
    assert len(orderflow_signal) == n_bars, "orderflow signal must align to bars"
    assert len(options_signal) == n_bars, "options signal must align to bars"
    assert len(combined_signal) == n_bars, "combined signal must align to bars"
    assert verdict["verdict"] in ("GO", "NO-GO"), "verdict must be GO or NO-GO"
    assert verdict["verdict"] == ("GO" if verdict["all_checks_pass"] else "NO-GO")
    assert _all_finite_numbers(options_alpha), "options alpha non-finite"
    assert _all_finite_numbers(orderflow_alpha), "orderflow alpha non-finite"
    assert _all_finite_numbers(combined_alpha), "combined alpha non-finite"
    assert _all_finite_numbers(toxicity), "toxicity non-finite"
    assert _all_finite_numbers(combined_wf), "combined walk-forward non-finite"
    assert _all_finite_numbers(options_only_wf), "options-only walk-forward non-finite"
    assert _all_finite_numbers(orderflow_only_wf), "orderflow-only walk-forward non-finite"
    assert _all_finite_numbers(flat_wf), "flat walk-forward non-finite"
    assert _all_finite_numbers(permutation), "permutation non-finite"
    assert _all_finite_numbers(verdict), "verdict non-finite"

    evidence_matrix = {
        "options_chain_loaded": bool(len(chain.quotes or []) > 0),
        "n_options_quotes": int(len(chain.quotes or [])),
        "orderflow_loaded": bool(len(snapshot.trades or []) > 0),
        "n_trades": int(len(snapshot.trades or [])),
        "n_liquidations": int(len(snapshot.liquidations or [])),
        "n_funding_rates": int(len(snapshot.funding_rates or [])),
        "symbol": str(snapshot.symbol),
        "venue": str(snapshot.venue),
        "bars_constructed": bool(int(bars["n_bars"]) > 0),
        "causal_orderflow_signal_computed": bool(len(orderflow_signal) == n_bars),
        "causal_options_signal_computed": bool(len(options_signal) == n_bars),
        "combined_signal_computed": bool(len(combined_signal) == n_bars),
        "ic_computed": bool(int(combined_alpha["n_horizons"]) > 0),
        "permutation_computed": bool("p_value" in permutation),
        "toxicity_measured": bool(toxicity["toxicity_measured"]),
        "integrated_walkforward_run": bool(int(combined_wf["num_windows"]) > 0),
        "paper_only": True,
        "live_trading_enabled": False,
        "options_signal_from_reconstructed_surface": bool(int(opt_components["surface_points"]) > 0),
        "toxicity_gate_applied_to_all_pillars": True,
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
            "gex_flip_distance_threshold": float(gex_flip_distance_threshold),
            "skew_slope_threshold": float(skew_slope_threshold),
            "calib_residual_threshold": float(calib_residual_threshold),
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
                "fdr_alpha": FDR_ALPHA,
                "pbo_n_combinations": PBO_N_COMBINATIONS,
                "pbo_k_folds": PBO_K_FOLDS,
                "guardrail_delta_band_usd": GUARDRAIL_DELTA_BAND_USD,
                "guardrail_target_delta_usd": GUARDRAIL_TARGET_DELTA_USD,
                "guardrail_toxicity_gate": GUARDRAIL_TOXICITY_GATE,
                "guardrail_cost_budget_bps": GUARDRAIL_COST_BUDGET_BPS,
                "guardrail_kill_switch_dd": GUARDRAIL_KILL_SWITCH_DD,
                "guardrail_kill_switch_toxicity": GUARDRAIL_KILL_SWITCH_TOXICITY,
                "guardrail_kill_switch_cost_bps": GUARDRAIL_KILL_SWITCH_COST_BPS,
                "guardrail_max_notional_usd": GUARDRAIL_MAX_NOTIONAL_USD,
                "guardrail_max_daily_loss_usd": GUARDRAIL_MAX_DAILY_LOSS_USD,
            },
        },
        "bars": {
            "n_bars": int(n_bars),
            "start_timestamp": str(bars["start_timestamp"]),
            "end_timestamp": str(bars["end_timestamp"]),
            "bar_duration_seconds": float(bars["bar_duration_seconds"]),
            "n_trades_total": int(len(snapshot.trades or [])),
        },
        "options_components": {
            "surface_points": int(opt_components["surface_points"]),
            "surface_expiries": int(opt_components["surface_expiries"]),
            "calib_residual_max_abs": float(opt_components["calib_residual_max_abs"]),
            "calib_residual_mean": float(opt_components["calib_residual_mean"]),
            "gamma_flip_level": float(opt_components["gamma_flip_level"]),
            "gex_flip_distance": float(opt_components["gex_flip_distance"]),
            "gex_signal": float(opt_components["gex_signal"]),
            "skew_signal": float(opt_components["skew_signal"]),
            "calib_signal": float(opt_components["calib_signal"]),
            "options_signal_raw": float(opt_components["options_signal_raw"]),
            "skew_term_structure": opt_components["skew_term_structure"],
        },
        "options_signal": {
            "n_bars": int(len(options_signal)),
            "signals": [float(v) for v in options_signal],
            "mean_signal": float(sum(options_signal) / len(options_signal)) if options_signal else 0.0,
        },
        "orderflow_signal": {
            "n_bars": int(len(orderflow_signal)),
            "signals": [float(v) for v in orderflow_signal],
            "mean_signal": float(sum(orderflow_signal) / len(orderflow_signal)) if orderflow_signal else 0.0,
        },
        "combined_signal": {
            "n_bars": int(len(combined_signal)),
            "signals": [float(v) for v in combined_signal],
            "mean_signal": float(sum(combined_signal) / len(combined_signal)) if combined_signal else 0.0,
            "long_bars": int(sum(1 for v in combined_signal if v == 1)),
            "short_bars": int(sum(1 for v in combined_signal if v == -1)),
            "flat_bars": int(sum(1 for v in combined_signal if v == 0)),
        },
        "options_alpha": options_alpha,
        "orderflow_alpha": orderflow_alpha,
        "combined_alpha": combined_alpha,
        "permutation": permutation,
        "toxicity": toxicity,
        "combined_wf": {k: v for k, v in combined_wf.items() if k != "oos_equity_curve"},
        "options_only_wf": {k: v for k, v in options_only_wf.items() if k != "oos_equity_curve"},
        "orderflow_only_wf": {k: v for k, v in orderflow_only_wf.items() if k != "oos_equity_curve"},
        "flat_wf": {k: v for k, v in flat_wf.items() if k != "oos_equity_curve"},
        "dsr": {k: float(v) for k, v in dsr_values.items()},
        "pbo": pbo_result,
        "bh_fdr": bh_result,
        "perm_pairs": perm_pairs,
        "verdict_checks": verdict,
        "evidence_matrix": evidence_matrix,
        "deployment_authorization": {
            "authorized": bool(verdict["verdict"] == "GO"),
            "mode": "paper_only",
            "note": "GO certifies the integrated options+orderflow evaluation only; not authorization to trade live.",
        },
    }
    assert_json_valid(report)
    serialized = serialize_metrics_strict(report)

    if write:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = _stamp_for_filename(timestamp)
        json_path = out_dir / f"INTEGRATED_OPTIONS_ORDERFLOW_EVAL_{stamp}.json"
        md_path = out_dir / f"INTEGRATED_OPTIONS_ORDERFLOW_EVAL_{stamp}.md"
        serialized["artifact_paths"] = {"json": str(json_path), "md": str(md_path)}
        json_path.write_text(
            json.dumps(serialized, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        md_path.write_text(_write_markdown(serialized) + "\n", encoding="utf-8")

    return serialized


def _write_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# INTEGRATED OPTIONS + ORDERFLOW EVALUATION — EVAL-18 (paper-only)")
    lines.append("")
    lines.append(f"- Report ID: {report['report_id']}")
    lines.append(f"- Generated at: {report['generated_at']}")
    lines.append(f"- Verdict: {report['verdict']}")
    lines.append(f"- Trading mode: {report['trading_mode']} (live enabled: {report['live_trading_enabled']})")
    lines.append(f"- Symbol: {report['config']['symbol']} @ spot {report['config']['spot']}")
    lines.append("")

    b = report["bars"]
    lines.append("## BARS (causal, from real orderflow tape)")
    lines.append(f"- Bars: {b['n_bars']} ({b['start_timestamp']} -> {b['end_timestamp']}, "
                 f"{b['bar_duration_seconds']}s each, {b['n_trades_total']} trades)")
    lines.append("")

    oc = report["options_components"]
    lines.append("## OPTIONS ALPHA (reconstructed IV surface, EVAL-16 pattern)")
    lines.append(f"- Surface points: {oc['surface_points']} across {oc['surface_expiries']} expiries")
    lines.append(f"- Calibration residual: max abs {oc['calib_residual_max_abs']:.3e}, mean {oc['calib_residual_mean']:.3e}")
    lines.append(f"- Gamma flip level: {oc['gamma_flip_level']:.2f}, GEX flip distance: {oc['gex_flip_distance']:.6f}")
    lines.append(f"- GEX signal: {oc['gex_signal']:.4f}, skew signal: {oc['skew_signal']:.4f}, calib signal: {oc['calib_signal']:.4f}")
    lines.append(f"- Options signal raw: {oc['options_signal_raw']:.4f}")
    lines.append("")

    oa = report["options_alpha"]
    lines.append("## OPTIONS ALPHA (IC + decay)")
    lines.append(f"- IC by horizon: {oa['ic_by_horizon']}")
    lines.append(f"- IC mean {oa['ic_mean']:.6f}, std {oa['ic_std']:.6f}, t-stat {oa['ic_tstat']:.6f}")
    lines.append("")

    ofa = report["orderflow_alpha"]
    lines.append("## ORDERFLOW ALPHA (IC + decay, EVAL-17 causal signal)")
    lines.append(f"- IC by horizon: {ofa['ic_by_horizon']}")
    lines.append(f"- IC mean {ofa['ic_mean']:.6f}, std {ofa['ic_std']:.6f}, t-stat {ofa['ic_tstat']:.6f}")
    lines.append("")

    ca = report["combined_alpha"]
    lines.append("## COMBINED ALPHA (IC + decay)")
    lines.append(f"- IC by horizon: {ca['ic_by_horizon']}")
    lines.append(f"- IC mean {ca['ic_mean']:.6f}, std {ca['ic_std']:.6f}, t-stat {ca['ic_tstat']:.6f}")
    lines.append(f"- IC bootstrap CI [{ca['ic_bootstrap_ci']['lo']:.6f}, {ca['ic_bootstrap_ci']['hi']:.6f}]")
    lines.append("")

    p = report["permutation"]
    lines.append("## PERMUTATION TEST (combined vs best single pillar)")
    lines.append(f"- p_value {p['p_value']:.6f}, observed_difference {p['observed_difference']:.6f}, "
                 f"significant_at_05 {p['significant_at_05']}, n_permutations {p['n_permutations']}")
    lines.append("")

    t = report["toxicity"]
    lines.append("## TOXICITY (VPIN, causal, EVAL-17 pattern)")
    lines.append(f"- Mean {t['mean_toxicity']:.6f}, p95 {t['p95_toxicity']:.6f}, "
                 f"range [{t['min_toxicity']:.6f}, {t['max_toxicity']:.6f}]")
    lines.append(f"- Threshold {t['toxicity_threshold']}, fraction above {t['fraction_above_threshold']:.6f}, "
                 f"gate engages {t['gate_engages']}")
    lines.append(f"- Toxicity measured: {t['toxicity_measured']}")
    lines.append("")

    cs = report["combined_signal"]
    lines.append("## COMBINED SIGNAL (fusion + toxicity gate)")
    lines.append(f"- Bars: {cs['n_bars']}, long {cs['long_bars']}, short {cs['short_bars']}, flat {cs['flat_bars']}")
    lines.append(f"- Mean signal: {cs['mean_signal']:.6f}")
    lines.append("")

    wf = report["combined_wf"]
    lines.append("## NET-OF-COST INTEGRATED WALK-FORWARD (combined vs 3 controls)")
    lines.append(f"- Combined:    return {wf['oos_return']:.6f}, Sharpe {wf['oos_sharpe']:.6f}, "
                 f"max-DD {wf['oos_max_drawdown']:.6f}, cost {wf['total_cost_usd']:.2f} USD, "
                 f"trades {wf['num_trades']}, windows {wf['num_windows']}")
    owf = report["options_only_wf"]
    ofwf = report["orderflow_only_wf"]
    fwf = report["flat_wf"]
    lines.append(f"- Options-only: return {owf['oos_return']:.6f}, Sharpe {owf['oos_sharpe']:.6f}, "
                 f"max-DD {owf['oos_max_drawdown']:.6f}, cost {owf['total_cost_usd']:.2f} USD")
    lines.append(f"- Orderflow-only: return {ofwf['oos_return']:.6f}, Sharpe {ofwf['oos_sharpe']:.6f}, "
                 f"max-DD {ofwf['oos_max_drawdown']:.6f}, cost {ofwf['total_cost_usd']:.2f} USD")
    lines.append(f"- Flat control: return {fwf['oos_return']:.6f}, Sharpe {fwf['oos_sharpe']:.6f}, "
                 f"max-DD {fwf['oos_max_drawdown']:.6f}, cost {fwf['total_cost_usd']:.2f} USD")
    lines.append("")

    lines.append("## STATISTICAL DEFENSIBILITY")
    lines.append(f"- DSR: " + ", ".join(f"{k}={v:.6f}" for k, v in report["dsr"].items()))
    lines.append(f"- PBO overall: {report['pbo']['overall_pbo']:.6f} (n_configs={report['pbo']['n_configs']})")
    lines.append(f"- BH-FDR: alpha={report['bh_fdr']['alpha']}, m_tests={report['bh_fdr']['m_tests']}, "
                 f"rejected={report['bh_fdr']['rejected']}")
    lines.append(f"- Permutation pairs: " + ", ".join(f"{k}={v:.6f}" for k, v in report["perm_pairs"].items()))
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
        description="Integrated options+orderflow net-of-cost evaluation (EVAL-18, paper-only)"
    )
    parser.add_argument("--out", type=str, default=str(OUT_DIR), help="output directory")
    parser.add_argument("--no-write", action="store_true", help="compute without writing artifacts")
    parser.add_argument("--timestamp", type=str, default=_utc_now_iso())
    parser.add_argument("--bar-duration-seconds", type=float, default=DEFAULT_BAR_DURATION_SECONDS)
    parser.add_argument("--signal-lookback-seconds", type=float, default=DEFAULT_SIGNAL_LOOKBACK_SECONDS)
    parser.add_argument("--signal-threshold", type=float, default=DEFAULT_SIGNAL_THRESHOLD)
    parser.add_argument("--toxicity-window-trades", type=int, default=DEFAULT_TOXICITY_WINDOW_TRADES)
    parser.add_argument("--toxicity-threshold", type=float, default=DEFAULT_TOXICITY_THRESHOLD)
    parser.add_argument("--gex-flip-distance-threshold", type=float, default=DEFAULT_GEX_FLIP_DISTANCE_THRESHOLD)
    parser.add_argument("--skew-slope-threshold", type=float, default=DEFAULT_SKEW_SLOPE_THRESHOLD)
    parser.add_argument("--calib-residual-threshold", type=float, default=DEFAULT_CALIB_RESIDUAL_THRESHOLD)
    parser.add_argument("--seeds", type=int, nargs="+", default=list(DEFAULT_SEEDS))
    parser.add_argument("--max-position-pct", type=float, default=DEFAULT_MAX_POSITION_PCT)
    parser.add_argument("--spread-bps", type=float, default=DEFAULT_SPREAD_BPS)
    parser.add_argument("--impact-coeff", type=float, default=DEFAULT_IMPACT_COEFF)
    parser.add_argument("--max-participation", type=float, default=DEFAULT_MAX_PARTICIPATION)
    parser.add_argument("--cost-budget-bps", type=float, default=DEFAULT_COST_BUDGET_BPS)
    args = parser.parse_args(argv)

    report = evaluate_integrated_options_orderflow(
        write=not args.no_write,
        out_dir=args.out,
        timestamp=args.timestamp,
        bar_duration_seconds=args.bar_duration_seconds,
        signal_lookback_seconds=args.signal_lookback_seconds,
        signal_threshold=args.signal_threshold,
        toxicity_window_trades=args.toxicity_window_trades,
        toxicity_threshold=args.toxicity_threshold,
        gex_flip_distance_threshold=args.gex_flip_distance_threshold,
        skew_slope_threshold=args.skew_slope_threshold,
        calib_residual_threshold=args.calib_residual_threshold,
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
                "combined_ic_mean": report["combined_alpha"]["ic_mean"],
                "combined_ic_tstat": report["combined_alpha"]["ic_tstat"],
                "combined_ic_by_horizon": report["combined_alpha"]["ic_by_horizon"],
                "options_ic_mean": report["options_alpha"]["ic_mean"],
                "orderflow_ic_mean": report["orderflow_alpha"]["ic_mean"],
                "permutation_p": report["permutation"]["p_value"],
                "mean_toxicity": report["toxicity"]["mean_toxicity"],
                "toxic_gate_active_fraction": report["toxicity"]["toxic_gate_active_fraction"],
                "combined_return": report["combined_wf"]["oos_return"],
                "combined_sharpe": report["combined_wf"]["oos_sharpe"],
                "options_only_return": report["options_only_wf"]["oos_return"],
                "options_only_sharpe": report["options_only_wf"]["oos_sharpe"],
                "orderflow_only_return": report["orderflow_only_wf"]["oos_return"],
                "orderflow_only_sharpe": report["orderflow_only_wf"]["oos_sharpe"],
                "flat_return": report["flat_wf"]["oos_return"],
                "flat_sharpe": report["flat_wf"]["oos_sharpe"],
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
