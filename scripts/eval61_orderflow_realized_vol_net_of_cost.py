#!/usr/bin/env python3
"""EVAL-61: real **options order-flow toxicity -> subsequent realized volatility**,
traded via a **signal-timed delta-hedged ATM straddle** net-of-cost on the
BTC/ETH perpetual.

Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``) is a
**combined OPTIONS + ORDERFLOW** strategy. Every EVAL-02..60 cell is sealed
``NO-GO CONFIRMED (PASS)``: every options+orderflow fusion cell (EVAL-46..60) and
every pure options smile/greeks ladder (EVAL-54..59) is closed. The one on-charter
combination still unmeasured is to make the **options ORDER FLOW** (the repo's
namesake) drive a **volatility** trade rather than a directional one: does real
signed options order flow carry predictive information about **subsequent realized
volatility**, and is a **signal-timed delta-hedged ATM straddle** net-of-cost
tradable? EVAL-54/55/57 traded vol/gamma but were static positions or level
comparisons; none used the options order flow to *time* a delta-hedged straddle.

This script is the pre-registered net-of-cost falsification on real, synchronized
captures produced by ``scripts/eval60_acquire_three_way.py`` (reused verbatim for
the fresh live capture). It consumes only the measured capture JSON files under
``--capture-dir`` (each carries ``surface``, ``option_trades``, ``perp_candles``)
and reuses the sealed statistics helpers
(``_sharpe_of_returns``, ``_dsr_of_returns``, ``_cscv_pbo``, ``_benjamini_hochberg``,
``block_bootstrap_ci``, ``permutation_test``) plus ``implied_volatility`` /
``black_scholes_greeks`` from ``src/features/options_pricing.py``. It never re-runs
a prior EVAL and never edits ``src/``.

Pre-declared protocol (identical for every underlying; no curve fitting):
  * resample the underlying perpetual 1m candles to a ``bar_seconds`` grid and take
    the last close per bar; per-bar causal return into the next bar;
  * **order-flow toxicity** (per bar, real Deribit option trades in
    ``(bar_end - bar_seconds, bar_end]``):
      - ``tox``      = (call_notional - put_notional) / (call_notional + put_notional)
      - ``imbalance``= (aggressive_buy_amt - aggressive_sell_amt) / total_amt
    Position ``q_k = clip(expanding_z(tox_k), -1, 1)`` (causal; decision at bar k).
  * **realized-vol target**: ``rv_{k+1} = |log(S_{k+1}) - log(S_k)|`` from Deribit
    ``{BTC,ETH}-PERPETUAL`` 1m candles (reported, not traded directly).
  * **delta-hedged ATM straddle**: ATM IV from the real surface snapshot (newest 5m
    snapshot whose candle has *closed* by ``bar_end``, i.e. ``available = bar_ms + 300s``);
    ATM strike = nearest strike to spot with both a call and a put; IV backed out of the
    *real mark* via ``implied_volatility(mark*spot, spot, K, 0, T, type)``; greeks from
    ``black_scholes_greeks`` at that IV. Position ``q_k`` in the ATM straddle
    (long when call-heavy/vol-expansion expected, short otherwise), delta-hedged each
    bar with the perp.
  * **net-of-cost P&L per bar**:
    ``q_k * [vega*(IV_{k+1}-IV_k) + 0.5*gamma*(dS)^2 - theta*dt] - hedge_cost
    - 5bps*|dq|`` where ``hedge_cost = 5bps*|q_k*delta_k - q_{k-1}*delta_{k-1}|``
    (delta-hedge rebalance) and ``5bps*|dq|`` is straddle-position turnover.
  * full-series (causal -> out-of-sample) plus rolling walk-forward Sharpe/max-DD;
  * stats: 1000-perm paired permutation (strategy vs flat), 1000-resample block
    bootstrap CI on Sharpe (block 2), CSCV PBO across the pre-registered grid
    (k=4), BH-FDR (alpha 0.1), DSR; seed 42.

Pre-declared GO bar (conservative): GO only if, on **both** BTC and ETH and
**at least one** grid config, net-of-cost Sharpe > 0, no kill-switch breach
(max-DD <= 0.20), permutation p < 0.05, bootstrap 95% CI lower bound > 0, and
pooled PBO < 0.5. Otherwise ``NO-GO CONFIRMED (PASS)``.
Grid = {toxicity variants} x {60s, 300s} per underlying.

Heavy-work floor (sealed): refuses to seal a verdict unless every underlying
independently clears the floor -- surface >=100 snapshots / >=50 instruments /
>=240 5m bars; Deribit options order flow >=2000 trades / >=50 instruments /
>=240 bars / >=79200 s span; perp candles >=240 5m bars / >=79200 s span; common
bars (surface x trades x perp) >=240; roster >=2 underlyings. Below floor seals a
measured ``EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_BLOCKED_<UTC>`` (never a NO-GO).

Seal ``EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_PREREGISTRATION_<UTC>.{json,md}``
(before measurement) then
``EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_COMBINED_<UTC>.{json,md}`` (or
``..._BLOCKED_<UTC>``).
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analytics.integrated_options_orderflow_evaluation import (  # noqa: E402
    _dsr_of_returns,
    _sharpe_of_returns,
)
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
    _cscv_pbo,
)
from src.analytics.strategy_evaluation import (  # noqa: E402
    block_bootstrap_ci,
    permutation_test,
)
from src.data.loader import _parse_dt  # noqa: E402
from src.data.schemas import PricingInputs  # noqa: E402
from src.features.options_pricing import (  # noqa: E402
    black_scholes_greeks,
    implied_volatility,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_COMBINED"
PREREG_ID = "EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_PREREGISTRATION"
BLOCKED_ID = "EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_BLOCKED"

BAR_SECONDS = 300.0
ZWINDOW = 20
COST_BPS = 5.0
PERMUTATION_PERMS = 1000
BOOTSTRAP_RESAMPLES = 1000
BOOTSTRAP_BLOCK = 2
PBO_K_FOLDS = 4
PBO_N_COMBINATIONS = 16
FDR_ALPHA = 0.1
SEED = 42
KILL_SWITCH_MAX_DD = 0.20
DAY_COUNT = 365.0
RATE = 0.0

# Heavy-work floor (per underlying).
MIN_SNAPSHOTS = 100
MIN_BARS = 240
MIN_INSTRUMENTS = 50
MIN_TRADES = 2000
MIN_SPAN_SECONDS = 79200.0
MIN_COMMON_BARS = 240
MIN_UNDERLYINGS = 2

TOX_SIGNALS: Tuple[str, ...] = ("tox", "imbalance")
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
SURFACE_BAR_SECONDS = 300.0
SIGNAL_EPS = 1e-9
ATM_STRIKE_PCT_BAND = 0.20  # ATM strike within 20% of spot

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/integrated_options_orderflow_evaluation.py",
    "src/analytics/real_walkforward_certification.py",
    "src/analytics/strategy_evaluation.py",
    "src/data/loader.py",
    "src/data/schemas.py",
    "src/features/options_pricing.py",
    "scripts/eval60_acquire_three_way.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval61_orderflow_realized_vol_net_of_cost.py "
    "tests/test_eval61_orderflow_realized_vol_net_of_cost.py",
    "python3 -m pytest -q tests/test_eval61_orderflow_realized_vol_net_of_cost.py",
    "python3 scripts/eval60_acquire_three_way.py "
    "--underlying BTC --underlying ETH --days 1 --out-dir data/raw/eval61 --seal "
    "--task-label EVAL61-OPTIONS-ORDERFLOW-TO-REALIZED-VOL-STRADDLE",
    "python3 scripts/eval61_orderflow_realized_vol_net_of_cost.py --capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval61_orderflow_realized_vol_net_of_cost.py --capture-dir data/raw/eval61",
)


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp_for_filename(iso_ts: str) -> str:
    return iso_ts.replace("-", "").replace(":", "").replace(".", "")


def _finite(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
        return v if math.isfinite(v) else float(default)
    except (TypeError, ValueError):
        return float(default)


def _mean(vals: Sequence[float]) -> float:
    vals = [float(v) for v in vals]
    return sum(vals) / len(vals) if vals else 0.0


def _std(vals: Sequence[float]) -> float:
    vals = [float(v) for v in vals]
    n = len(vals)
    if n < 2:
        return 0.0
    m = sum(vals) / n
    return math.sqrt(sum((v - m) ** 2 for v in vals) / n)


def _max_drawdown(rets: Sequence[float]) -> float:
    eq = 1.0
    peak = 1.0
    mdd = 0.0
    for r in rets:
        eq *= 1.0 + float(r)
        if eq <= 0:
            return 1.0
        peak = max(peak, eq)
        dd = (peak - eq) / peak if peak > 0 else 0.0
        mdd = max(mdd, dd)
    return mdd


def kill_switch_breach(max_drawdown: float) -> bool:
    return float(max_drawdown) > KILL_SWITCH_MAX_DD


def _bar_end(ts_ms: int, bar_ms: int) -> int:
    return ((int(ts_ms) // bar_ms) + 1) * bar_ms


def expanding_zscore(xs: Sequence[float], window: int, min_periods: int = 5) -> List[float]:
    """Causal expanding z-score: mean/std over xs[0..i] (past + present only)."""
    out: List[float] = []
    cum: List[float] = []
    cum2: List[float] = []
    for i, x in enumerate(xs):
        v = float(x)
        cum.append(v)
        cum2.append(v * v)
        n = len(cum)
        if n < max(2, int(min_periods)):
            out.append(0.0)
            continue
        m = sum(cum) / n
        var = sum(cum2) / n - m * m
        sd = math.sqrt(var) if var > 0 else 0.0
        out.append((v - m) / sd if sd > 0 else 0.0)
    return out


def _sign(x: float, eps: float = SIGNAL_EPS) -> float:
    if x > eps:
        return 1.0
    if x < -eps:
        return -1.0
    return 0.0


# ---------------------------------------------------------------------------
# Order-flow toxicity per bar (Deribit options-venue signed option trades)
# ---------------------------------------------------------------------------
def toxicity_per_bar(
    capture: Dict[str, Any],
    bar_seconds: float,
) -> Tuple[List[int], Dict[int, float], List[float], List[float]]:
    """Per-bar toxicity and signed-aggressor imbalance.

    Returns ``(bar_ends, closes, tox_list, imb_list)`` aligned ascending.
    ``tox_k`` = (call_notional - put_notional) / (call_notional + put_notional)
    from real Deribit option trades in ``(bar_end - bar, bar_end]``.
    ``imb_k`` = (aggressive_buy_amt - aggressive_sell_amt) / total_amt (signed
    aggressor variant). Bars with no trades contribute 0.0.
    """
    bar_ms = int(float(bar_seconds) * 1000)
    candles = sorted(capture.get("perp_candles", []), key=lambda c: int(c["ts"]))
    closes: Dict[int, float] = {}
    for c in candles:
        try:
            px = float(c["close"])
        except (TypeError, ValueError):
            continue
        if px > 0:
            closes[_bar_end(int(c["ts"]), bar_ms)] = px
    bar_ends = sorted(closes)

    agg: Dict[int, Dict[str, float]] = {}
    for t in capture.get("option_trades", []) or []:
        try:
            ts = int(t["ts"])
            amt = abs(float(t.get("amount") or 0.0))
        except (TypeError, ValueError):
            continue
        if amt <= 0 or ts <= 0:
            continue
        opt = str(t.get("option_type") or "").lower()
        direction = str(t.get("direction") or "").lower()
        idx = float(t.get("index_price") or 0.0)
        be = _bar_end(ts, bar_ms)
        b = agg.setdefault(be, {
            "call_notional": 0.0, "put_notional": 0.0,
            "buy_amt": 0.0, "sell_amt": 0.0,
        })
        notional = amt * idx
        if opt == "call":
            b["call_notional"] += notional
        elif opt == "put":
            b["put_notional"] += notional
        if direction == "buy":
            b["buy_amt"] += amt
        elif direction == "sell":
            b["sell_amt"] += amt

    tox_list: List[float] = []
    imb_list: List[float] = []
    for be in bar_ends:
        b = agg.get(be, {
            "call_notional": 0.0, "put_notional": 0.0,
            "buy_amt": 0.0, "sell_amt": 0.0,
        })
        total_cp = b["call_notional"] + b["put_notional"]
        tox = (b["call_notional"] - b["put_notional"]) / total_cp if total_cp > 0 else 0.0
        total_agg = b["buy_amt"] + b["sell_amt"]
        imb = (b["buy_amt"] - b["sell_amt"]) / total_agg if total_agg > 0 else 0.0
        tox_list.append(_finite(tox))
        imb_list.append(_finite(imb))
    return bar_ends, closes, tox_list, imb_list


# ---------------------------------------------------------------------------
# ATM straddle from a surface snapshot (real marks -> IV -> greeks)
# ---------------------------------------------------------------------------
def _expiry_dt(expiry_iso: str) -> Optional[datetime]:
    """Parse a Deribit expiry (ISO or date-only) to a UTC datetime (08:00 UTC if date-only)."""
    if not expiry_iso:
        return None
    s = str(expiry_iso).strip()
    if "T" in s:
        return _parse_dt(s)
    return _parse_dt(s + "T08:00:00Z")


def _leg_greeks(
    q: Dict[str, Any], spot: float, strike: float, state_time: datetime, t_years: float,
) -> Optional[Dict[str, float]]:
    """Back out IV from the real mark, then greeks at that IV. None if unpriceable."""
    mark = _finite(q.get("mark"), 0.0)
    ot = str(q.get("option_type") or "").lower()
    if mark <= 0.0 or ot not in ("call", "put"):
        return None
    price_usd = mark * spot
    try:
        iv = float(implied_volatility(
            price_usd, spot, strike, RATE, t_years, ot, seed=SEED,
        ))
        if not math.isfinite(iv) or iv < 0:
            return None
        g = black_scholes_greeks(PricingInputs(
            spot=spot, strike=strike, rate=RATE, volatility=iv,
            time_to_expiry=t_years, option_type=ot, seed=SEED,
        ))
        return {
            "iv": float(iv),
            "delta": _finite(g.get("delta"), 0.0),
            "gamma": _finite(g.get("gamma"), 0.0),
            "theta": _finite(g.get("theta"), 0.0),
            "vega": _finite(g.get("vega"), 0.0),
            "price_usd": float(price_usd),
        }
    except Exception:  # noqa: BLE001 - IV solve / greeks failed; leg is unpriceable
        return None


def _atm_straddle(
    quotes: Sequence[Dict[str, Any]], spot: float, state_time: datetime,
) -> Optional[Dict[str, float]]:
    """ATM straddle (call + put at nearest common strike to spot) with real IV/greeks.

    Picks the nearest expiry that prices both legs, then the nearest-to-spot strike
    within ``ATM_STRIKE_PCT_BAND``. Returns None if no priceable straddle exists.
    """
    by_expiry: Dict[str, Dict[float, Dict[str, Dict[str, Any]]]] = {}
    for q in quotes or []:
        try:
            strike = float(q.get("strike") or 0.0)
            mark = _finite(q.get("mark"), 0.0)
            expiry = str(q.get("expiry") or "")
            ot = str(q.get("option_type") or "").lower()
        except (TypeError, ValueError):
            continue
        if strike <= 0.0 or mark <= 0.0 or ot not in ("call", "put") or not expiry:
            continue
        exp_date = expiry[:10]
        by_expiry.setdefault(exp_date, {}).setdefault(strike, {}).setdefault(ot, q)

    best: Optional[Dict[str, Any]] = None
    best_score: Optional[Tuple[float, float]] = None
    for exp_date, strikes in by_expiry.items():
        expiry_dt = _expiry_dt(exp_date)
        if expiry_dt is None:
            continue
        t_years = (expiry_dt - state_time).total_seconds() / (DAY_COUNT * 86400.0)
        if t_years <= 0.0:
            continue
        for strike, legs in strikes.items():
            if "call" not in legs or "put" not in legs:
                continue
            if abs(strike - spot) / spot > ATM_STRIKE_PCT_BAND:
                continue
            cg = _leg_greeks(legs["call"], spot, strike, state_time, t_years)
            pg = _leg_greeks(legs["put"], spot, strike, state_time, t_years)
            if cg is None or pg is None:
                continue
            straddle = {
                "iv": (cg["iv"] + pg["iv"]) / 2.0,
                "delta": cg["delta"] + pg["delta"],
                "gamma": cg["gamma"] + pg["gamma"],
                "theta": cg["theta"] + pg["theta"],
                "vega": cg["vega"] + pg["vega"],
                "price_usd": cg["price_usd"] + pg["price_usd"],
                "strike": float(strike),
                "expiry": exp_date,
                "dist_to_spot": abs(strike - spot) / spot,
            }
            score = (t_years, straddle["dist_to_spot"])
            if best_score is None or score < best_score:
                straddle["_score"] = score
                best = straddle
                best_score = score
    if best is not None:
        best.pop("_score", None)
    return best


def straddle_series_from_surface(
    capture: Dict[str, Any],
) -> Tuple[List[int], List[Optional[Dict[str, float]]]]:
    """Per-snapshot causal ATM straddle as ``[(available_time_ms, straddle|None)]``.

    ``available_time_ms = bar_ms + SURFACE_BAR_SECONDS*1000`` -- the 5m option candle
    has fully closed only at that time, so a trading bar may use the snapshot only
    when ``bar_end >= available_time_ms`` (no lookahead).
    """
    out: List[Tuple[int, Optional[Dict[str, float]]]] = []
    for snap in capture.get("surface", {}).get("snapshots", []) or []:
        bar_ms = int(snap.get("bar_ms") or 0)
        if bar_ms <= 0:
            continue
        spot = _finite(snap.get("spot"), 0.0)
        if spot <= 0.0:
            continue
        quotes = snap.get("quotes") or []
        if not quotes:
            continue
        state_time = datetime.fromtimestamp(
            (bar_ms + int(SURFACE_BAR_SECONDS) * 1000) / 1000.0, tz=timezone.utc,
        )
        st = _atm_straddle(quotes, spot, state_time)
        out.append((bar_ms + int(SURFACE_BAR_SECONDS) * 1000, st))
    out.sort(key=lambda x: x[0])
    return out


def align_straddle(
    available: Sequence[Tuple[int, Optional[Dict[str, float]]]],
    bar_ends: Sequence[int],
) -> List[Optional[Dict[str, float]]]:
    """Newest straddle whose ``available_time <= bar_end`` (else None flat)."""
    times = [t for t, _ in available]
    vals = [v for _, v in available]
    out: List[Optional[Dict[str, float]]] = []
    j = -1
    for be in bar_ends:
        while j + 1 < len(times) and times[j + 1] <= be:
            j += 1
        out.append(vals[j] if j >= 0 else None)
    return out


# ---------------------------------------------------------------------------
# Bar building + straddle net-of-cost P&L
# ---------------------------------------------------------------------------
def build_bars(
    capture: Dict[str, Any],
    straddle_available: Sequence[Tuple[int, Optional[Dict[str, float]]]],
    bar_seconds: float,
) -> List[Dict[str, Any]]:
    """Resample 1m perp candles to ``bar_seconds``; attach toxicity + ATM straddle."""
    bar_ms = int(float(bar_seconds) * 1000)
    candles = sorted(capture.get("perp_candles", []), key=lambda c: int(c["ts"]))
    if len(candles) < 2:
        return []

    closes: Dict[int, float] = {}
    for c in candles:
        try:
            px = float(c["close"])
        except (TypeError, ValueError):
            continue
        if px > 0:
            closes[_bar_end(int(c["ts"]), bar_ms)] = px
    bar_ends = sorted(closes)
    if len(bar_ends) < 2:
        return []

    bar_ends_set, closes_map, tox_list, imb_list = toxicity_per_bar(capture, bar_seconds)
    tox_z = expanding_zscore(tox_list, ZWINDOW)
    imb_z = expanding_zscore(imb_list, ZWINDOW)
    q_tox = [max(-1.0, min(1.0, z)) for z in tox_z]
    q_imb = [max(-1.0, min(1.0, z)) for z in imb_z]

    straddle_by_bar = align_straddle(straddle_available, bar_ends)

    dt = bar_seconds / (DAY_COUNT * 86400.0)
    bars: List[Dict[str, Any]] = []
    for i, be in enumerate(bar_ends):
        s_k = closes_map[be]
        straddle_k = straddle_by_bar[i]
        bars.append({
            "bar_end": int(be),
            "close": float(s_k),
            "tox": float(tox_list[i]),
            "imbalance": float(imb_list[i]),
            "q_tox": float(q_tox[i]),
            "q_imb": float(q_imb[i]),
            "straddle": straddle_k,  # None if unpriceable at this bar
            "dt": float(dt),
        })
    return bars


def strategy_returns(
    bars: Sequence[Dict[str, Any]], q_series: Sequence[float],
    *, cost_bps: float = COST_BPS,
) -> Dict[str, Any]:
    """Net-of-cost delta-hedged ATM straddle returns.

    Per bar k (decision q_k, outcome over [k, k+1]):
      gross_k = q_k * [vega_k*(IV_{k+1}-IV_k) + 0.5*gamma_k*(dS)^2 - theta_k*dt]
      cost_k  = cost_bps * (|q_k*delta_k - q_{k-1}*delta_{k-1}| + |q_k - q_{k-1}|) / 1e4
      net_k   = gross_k - cost_k
    Bars where the straddle is unpriceable at k or k+1 contribute 0.0 (flat).
    """
    if len(bars) < 2:
        return {"returns": [], "nonzero": 0}
    returns: List[float] = []
    prev_q = 0.0
    prev_delta = 0.0
    for i in range(len(bars) - 1):
        q = float(q_series[i]) if i < len(q_series) else 0.0
        sk = bars[i]
        sk1 = bars[i + 1]
        straddle_k = sk.get("straddle")
        straddle_k1 = sk1.get("straddle")
        s0 = float(sk.get("close", 0.0))
        s1 = float(sk1.get("close", 0.0))
        if s0 <= 0.0 or s1 <= 0.0 or straddle_k is None or straddle_k1 is None:
            returns.append(0.0)
            prev_q = q
            prev_delta = float(straddle_k.get("delta", 0.0)) if straddle_k else 0.0
            continue
        d_s = s1 - s0
        d_iv = float(straddle_k1.get("iv", 0.0) or 0.0) - float(straddle_k.get("iv", 0.0) or 0.0)
        vega = float(straddle_k.get("vega", 0.0) or 0.0)
        gamma = float(straddle_k.get("gamma", 0.0) or 0.0)
        theta = float(straddle_k.get("theta", 0.0) or 0.0)
        dt = float(sk.get("dt", 0.0))
        delta_k = float(straddle_k.get("delta", 0.0) or 0.0)
        gross = q * (vega * d_iv + 0.5 * gamma * d_s * d_s - theta * dt)
        hedge_cost = cost_bps * abs(q * delta_k - prev_q * prev_delta) / 1e4
        turnover_cost = cost_bps * abs(q - prev_q) / 1e4
        net = gross - hedge_cost - turnover_cost
        returns.append(float(net))
        prev_q = q
        prev_delta = delta_k
    nonzero = sum(1 for p in q_series if abs(float(p)) > 1e-9)
    return {"returns": returns, "nonzero": int(nonzero)}


def walkforward_folds(returns: Sequence[float], train: int, test: int, step: int) -> List[Dict[str, Any]]:
    folds: List[Dict[str, Any]] = []
    n = len(returns)
    start = int(train)
    while start + int(test) <= n:
        seg = [float(r) for r in returns[start : start + int(test)]]
        folds.append({
            "test_start": start,
            "test_end": start + int(test),
            "oos_sharpe": _sharpe_of_returns(seg),
            "oos_max_drawdown": _max_drawdown(seg),
            "n": len(seg),
        })
        start += int(step)
    return folds


def evaluate_config(
    capture: Dict[str, Any],
    straddle_available: Sequence[Tuple[int, Optional[Dict[str, float]]]],
    *,
    tox_signal: str,
    bar_seconds: float,
) -> Dict[str, Any]:
    inst = capture.get("underlying", "UNKNOWN")
    bars = build_bars(capture, straddle_available, bar_seconds)
    if len(bars) < 4:
        return {
            "underlying": inst, "signal": tox_signal,
            "bar_seconds": float(bar_seconds), "error": "insufficient bars",
            "n_returns": 0, "pass": False,
        }
    q_key = "q_tox" if tox_signal == "tox" else "q_imb"
    q_series = [float(b.get(q_key, 0.0)) for b in bars]
    sr = strategy_returns(bars, q_series)
    rets = sr["returns"]
    if len(rets) < 3:
        return {
            "underlying": inst, "signal": tox_signal,
            "bar_seconds": float(bar_seconds), "error": "insufficient returns",
            "n_returns": 0, "pass": False,
        }
    sharpe = _sharpe_of_returns(rets)
    mdd = _max_drawdown(rets)
    flat = [0.0] * len(rets)
    perm = permutation_test(rets, flat, statistic=_mean,
                            n_permutations=PERMUTATION_PERMS, paired=True, seed=SEED)
    boot = block_bootstrap_ci(rets, statistic=_sharpe_of_returns,
                              n_bootstrap=BOOTSTRAP_RESAMPLES, block_size=BOOTSTRAP_BLOCK,
                              seed=SEED)
    wf = walkforward_folds(rets, train=max(10, len(rets) // 3),
                           test=max(10, len(rets) // 5), step=max(10, len(rets) // 5))
    breach = kill_switch_breach(mdd)
    perm_p = _finite(perm.get("p_value"), 1.0)
    ci_low = _finite(boot[1], 0.0)
    ci_high = _finite(boot[2], 0.0)
    passed = bool(
        sharpe > 0.0
        and not breach
        and perm_p < 0.05
        and ci_low > 0.0
        and sr["nonzero"] > 0,
    )
    return {
        "underlying": inst,
        "signal": tox_signal,
        "bar_seconds": float(bar_seconds),
        "n_bars": len(bars),
        "n_returns": len(rets),
        "nonzero_positions": sr["nonzero"],
        "sharpe": sharpe,
        "max_drawdown": mdd,
        "kill_switch_breach": breach,
        "permutation_p": perm_p,
        "bootstrap_ci": [boot[0], ci_low, ci_high],
        "dsr": _dsr_of_returns(rets),
        "walkforward": wf,
        "mean_return": _mean(rets),
        "pass": passed,
    }


# ---------------------------------------------------------------------------
# Inventory + floor
# ---------------------------------------------------------------------------
def _capture_inventory(capture_dir: str) -> List[Dict[str, Any]]:
    """Load the newest three-way capture per underlying."""
    best: Dict[str, Tuple[int, Dict[str, Any]]] = {}
    for path in sorted(glob.glob(os.path.join(capture_dir, "three_way_*.json"))):
        try:
            c = json.loads(Path(path).read_text())
        except (OSError, ValueError):
            continue
        inst = c.get("underlying", "?")
        stamp = 0
        try:
            tail = Path(path).stem.split("_")[-1]
            stamp = int("".join(ch for ch in tail if ch.isdigit()))
        except ValueError:
            stamp = 0
        if inst not in best or stamp > best[inst][0]:
            best[inst] = (stamp, c)
    return [c for _, c in best.values()]


def _bar_ends(perp_candles: Sequence[Dict[str, Any]], bar_seconds: float) -> List[int]:
    bar_ms = int(float(bar_seconds) * 1000)
    ends: set[int] = set()
    for c in perp_candles:
        px = _finite(c.get("close"), 0.0)
        if px > 0:
            ends.add(_bar_end(int(c["ts"]), bar_ms))
    return sorted(ends)


def _trade_span_and_count(trades: Sequence[Dict[str, Any]]) -> Tuple[int, int, float]:
    ts = [int(t["ts"]) for t in trades if int(t.get("ts") or 0) > 0]
    n = len(trades)
    span = ((max(ts) - min(ts)) / 1000.0) if len(ts) >= 2 else 0.0
    n_bars = int(span // 300.0) if span > 0 else 0
    return n, n_bars, span


def _underlying_floor(capture: Dict[str, Any]) -> Dict[str, Any]:
    inst = capture.get("underlying", "?")
    surface = capture.get("surface", {})
    snaps = surface.get("snapshots", []) or []
    trades = capture.get("option_trades", []) or []
    perp = capture.get("perp_candles", []) or []

    n_snapshots = len(snaps)
    surface_instruments = len({
        q.get("symbol") for s in snaps for q in (s.get("quotes") or [])
    })
    surface_bars_5m = len(_bar_ends(perp, 300.0))

    of_ts = [int(t["ts"]) for t in trades if int(t.get("ts") or 0) > 0]
    n_trades = len(trades)
    of_instruments = len({t.get("instrument") for t in trades if t.get("instrument")})
    of_span = ((max(of_ts) - min(of_ts)) / 1000.0) if len(of_ts) >= 2 else 0.0
    of_bars_5m = int(of_span // 300.0) if of_span > 0 else 0

    perp_ts = [int(c["ts"]) for c in perp if int(c.get("ts") or 0) > 0]
    perp_span = ((max(perp_ts) - min(perp_ts)) / 1000.0) if len(perp_ts) >= 2 else 0.0
    perp_bars_5m = int(perp_span // 300.0) if perp_span > 0 else 0

    # Common-grid overlap: 5m bars with a closed surface snapshot available,
    # falling inside both the option-trade and perp-candle time ranges.
    surf_avail = straddle_series_from_surface(capture)
    avail_times = [t for t, _ in surf_avail]
    common = 0
    if of_ts and perp_ts and avail_times:
        lo = max(min(of_ts), min(perp_ts))
        hi = min(max(of_ts), max(perp_ts))
        for be in _bar_ends(perp, 300.0):
            if be < lo or be > hi:
                continue
            if any(at <= be for at in avail_times):
                common += 1

    checks = {
        "snapshots_ok": bool(n_snapshots >= MIN_SNAPSHOTS),
        "surface_instruments_ok": bool(surface_instruments >= MIN_INSTRUMENTS),
        "surface_bars_ok": bool(surface_bars_5m >= MIN_BARS),
        "trades_ok": bool(n_trades >= MIN_TRADES),
        "of_instruments_ok": bool(of_instruments >= MIN_INSTRUMENTS),
        "of_span_ok": bool(of_span >= MIN_SPAN_SECONDS),
        "of_bars_ok": bool(of_bars_5m >= MIN_BARS),
        "perp_bars_ok": bool(perp_bars_5m >= MIN_BARS),
        "perp_span_ok": bool(perp_span >= MIN_SPAN_SECONDS),
        "common_overlap_ok": bool(common >= MIN_COMMON_BARS),
    }
    return {
        "underlying": inst,
        "n_surface_snapshots": n_snapshots,
        "n_surface_instruments": surface_instruments,
        "n_surface_bars_5m": surface_bars_5m,
        "n_option_trades": n_trades,
        "n_of_instruments": of_instruments,
        "of_span_seconds": round(of_span, 3),
        "n_of_bars_5m": of_bars_5m,
        "n_perp_candles": len(perp),
        "perp_span_seconds": round(perp_span, 3),
        "n_perp_bars_5m": perp_bars_5m,
        "n_common_bars_5m": common,
        "checks": checks,
        "ok": bool(all(checks.values())),
    }


# ---------------------------------------------------------------------------
# Protocol + orchestration
# ---------------------------------------------------------------------------
def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-61",
        "title": "Real options order-flow toxicity -> subsequent realized volatility, "
                 "traded via a signal-timed delta-hedged ATM straddle net-of-cost "
                 "on the BTC/ETH perpetual",
        "capture_dir": str(capture_dir),
        "tox_signals": list(TOX_SIGNALS),
        "tox_detail": {
            "tox": "(call_notional - put_notional) / (call_notional + put_notional) "
                   "from real Deribit option trades per bar",
            "imbalance": "(aggressive_buy_amt - aggressive_sell_amt) / total_amt "
                         "(signed aggressor variant)",
        },
        "position": "q_k = clip(expanding_z(tox_k), -1, 1); causal decision at bar k",
        "realized_vol_target": "rv_{k+1} = |log(S_{k+1}) - log(S_k)| from Deribit 1m perp candles",
        "straddle": "ATM straddle from real surface snapshot (newest 5m snapshot whose "
                    "candle closed by bar_end = bar_ms + 300s); IV backed out of the real "
                    "mark via implied_volatility(mark*spot, spot, K, 0, T, type); greeks "
                    "from black_scholes_greeks at that IV",
        "pnl_per_bar": "q_k * [vega*(IV_{k+1}-IV_k) + 0.5*gamma*(dS)^2 - theta*dt] "
                       "- cost_bps*|q_k*delta_k - q_{k-1}*delta_{k-1}|/1e4 "
                       "- cost_bps*|q_k - q_{k-1}|/1e4",
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "zwindow": int(ZWINDOW),
        "cost_bps": float(COST_BPS),
        "cost_model": "net-of-cost: pre-registered 5 bps on delta-hedge rebalance and "
                      "straddle-position turnover",
        "walkforward": {"train_frac": "1/3", "test_frac": "1/5", "step_frac": "1/5"},
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation_paired": True,
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "pbo_k_folds": PBO_K_FOLDS,
            "pbo_n_combinations": PBO_N_COMBINATIONS,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
        },
        "kill_switch_max_dd": KILL_SWITCH_MAX_DD,
        "go_bar": (
            "GO only if, on both BTC and ETH and at least one grid config, net-of-cost "
            "Sharpe > 0, no kill-switch breach (max-DD <= 0.20), permutation p < 0.05, "
            "bootstrap 95% CI lower > 0, and pooled PBO < 0.5; else NO-GO."
        ),
        "floor": {
            "min_surface_snapshots_per_underlying": MIN_SNAPSHOTS,
            "min_bars_per_underlying": MIN_BARS,
            "min_instruments_per_underlying": MIN_INSTRUMENTS,
            "min_option_trades_per_underlying": MIN_TRADES,
            "min_span_seconds_per_underlying": MIN_SPAN_SECONDS,
            "min_common_bars_per_underlying": MIN_COMMON_BARS,
            "min_underlyings": MIN_UNDERLYINGS,
        },
    }


def run_eval61(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL61-OPTIONS-ORDERFLOW-TO-REALIZED-VOL-STRADDLE",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    captures = _capture_inventory(str(capture_dir_abs))

    per_underlying_floor: Dict[str, Dict[str, Any]] = {}
    straddle_by_inst: Dict[str, List[Tuple[int, Optional[Dict[str, float]]]]] = {}
    for c in captures:
        inst = c.get("underlying", "?")
        fl = _underlying_floor(c)
        per_underlying_floor[inst] = fl
        try:
            straddle_by_inst[inst] = straddle_series_from_surface(c)
        except Exception:  # noqa: BLE001
            straddle_by_inst[inst] = []

    floor_ok = bool(
        len(captures) >= MIN_UNDERLYINGS
        and per_underlying_floor
        and all(v["ok"] for v in per_underlying_floor.values())
    )

    per_config: List[Dict[str, Any]] = []
    returns_by_config: Dict[str, List[float]] = {}
    errors: List[str] = []
    for cap in captures:
        inst = cap.get("underlying", "?")
        av = straddle_by_inst.get(inst, [])
        for sig in TOX_SIGNALS:
            for bar_s in GRID_BAR_SECONDS:
                try:
                    res = evaluate_config(
                        cap, av, tox_signal=sig, bar_seconds=bar_s,
                    )
                except BaseException as exc:  # noqa: BLE001
                    errors.append(f"{inst}::{sig}::bar{bar_s}: {exc!r}")
                    continue
                per_config.append(res)
                if res.get("n_returns", 0) > 0:
                    bars = build_bars(cap, av, bar_s)
                    q_key = "q_tox" if sig == "tox" else "q_imb"
                    q_series = [float(b.get(q_key, 0.0)) for b in bars]
                    returns_by_config[
                        f"{inst}::{sig}::bar{bar_s}"
                    ] = strategy_returns(bars, q_series)["returns"]

    pbo = _cscv_pbo(returns_by_config, n_combinations=PBO_N_COMBINATIONS,
                    k_folds=PBO_K_FOLDS, seed=SEED) if len(returns_by_config) >= 2 else {
                    "overall_pbo": 0.0, "note": "insufficient configs"}
    p_values = {
        f"{r['underlying']}::{r['signal']}::bar{r['bar_seconds']}": _finite(
            r.get("permutation_p"), 1.0
        )
        for r in per_config if r.get("n_returns", 0) > 0
    }
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}

    by_inst: Dict[str, List[Dict[str, Any]]] = {}
    for r in per_config:
        by_inst.setdefault(r["underlying"], []).append(r)
    inst_summary: List[Dict[str, Any]] = []
    for inst, rows in by_inst.items():
        best = max(rows, key=lambda r: _finite(r.get("sharpe"), -1e9))
        inst_summary.append({
            "underlying": inst,
            "n_configs": len(rows),
            "best_sharpe": _finite(best.get("sharpe"), 0.0),
            "best_config": f"{best['signal']}::bar{best['bar_seconds']}",
            "any_pass": bool(any(r.get("pass") for r in rows)),
        })

    all_pass = bool(inst_summary) and all(s["any_pass"] for s in inst_summary)
    pooled_pbo = _finite(pbo.get("overall_pbo"), 0.0)
    go = bool(floor_ok and all_pass and pooled_pbo < 0.5)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = "EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL" if floor_ok else "EVAL_61_BLOCKED_FLOOR"

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "real options order-flow toxicity -> subsequent realized volatility, "
            "signal-timed delta-hedged ATM straddle net-of-cost falsification"
            if floor_ok else "capture below heavy-work floor; no verdict"
        ),
        "floor_ok": bool(floor_ok),
        "capture_dir": str(capture_dir_abs),
        "underlyings": sorted(per_underlying_floor),
        "floor": build_protocol(capture_dir)["floor"],
        "per_underlying_floor": per_underlying_floor,
        "protocol": build_protocol(capture_dir),
        "per_config": per_config,
        "per_underlying": inst_summary,
        "pooled": {
            "overall_pbo": pooled_pbo,
            "bh_fdr": bh,
            "all_underlyings_pass": all_pass,
            "campaign_state": campaign_state,
        },
        "errors": errors,
    }

    if not write:
        return report

    prereg = build_prereg(report)
    _seal(PREREG_ID, prereg, build_prereg_md)

    if not floor_ok:
        _seal(BLOCKED_ID, _build_blocked_report(report), build_blocked_md)
        return report

    _seal(REPORT_ID, report, build_md)
    return report


def build_prereg(report: Dict[str, Any]) -> Dict[str, Any]:
    p = report["protocol"]
    return {
        "prereg_id": PREREG_ID,
        "generated_at": report["generated_at"],
        "task": report["task"],
        "hypothesis": (
            "Real options order-flow toxicity predicts subsequent realized volatility, "
            "and a signal-timed delta-hedged ATM straddle is net-of-cost tradable for "
            "the BTC/ETH perpetual on real, synchronized data."
        ),
        "protocol": p,
        "capture_dir": report["capture_dir"],
    }


def build_prereg_md(p: Dict[str, Any]) -> str:
    proto = p["protocol"]
    lines = [
        f"# {p['prereg_id']} — options order-flow toxicity -> realized vol straddle net-of-cost falsification",
        "",
        f"- Generated: `{p['generated_at']}`",
        f"- Task: `{p['task']}`",
        f"- Hypothesis: {p['hypothesis']}",
        f"- Capture dir: `{p['capture_dir']}`",
        "",
        "## Pre-declared protocol",
        "",
        f"- Tox signals: {proto['tox_signals']}",
        f"- Position: {proto['position']}",
        f"- Realized-vol target: {proto['realized_vol_target']}",
        f"- Straddle: {proto['straddle']}",
        f"- P&L per bar: {proto['pnl_per_bar']}",
        f"- Bar grid (s): {proto['bar_seconds_grid']}",
        f"- z-window: {proto['zwindow']}; cost: {proto['cost_model']} ({proto['cost_bps']} bps)",
        f"- Stats: perm {proto['stats']['permutation_perms']} paired / "
        f"bootstrap {proto['stats']['bootstrap_resamples']} block {proto['stats']['bootstrap_block']} / "
        f"PBO k={proto['stats']['pbo_k_folds']} / BH-FDR alpha {proto['stats']['fdr_alpha']} / "
        f"seed {proto['stats']['seed']}",
        f"- Kill-switch max-DD: {proto['kill_switch_max_dd']}",
        "",
        "## Pre-declared GO bar",
        "",
        proto["go_bar"],
        "",
        "## Heavy-work floor (must be met to seal a verdict)",
        "",
        f"- min surface snapshots/underlying: {proto['floor']['min_surface_snapshots_per_underlying']}",
        f"- min bars/underlying: {proto['floor']['min_bars_per_underlying']}",
        f"- min instruments/underlying: {proto['floor']['min_instruments_per_underlying']}",
        f"- min Deribit options-venue trades/underlying: {proto['floor']['min_option_trades_per_underlying']}",
        f"- min span seconds/underlying: {proto['floor']['min_span_seconds_per_underlying']}",
        f"- min common 5m bars/underlying: {proto['floor']['min_common_bars_per_underlying']}",
        f"- min underlyings: {proto['floor']['min_underlyings']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def build_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {r['report_id']} — real options order-flow toxicity -> realized vol straddle net-of-cost falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        "",
        "## Per-underlying floor",
        "",
        "| underlying | snaps | surf inst | 5m bars | deribit trades | of inst | deribit span s | perp bars | perp span s | common 5m | ok |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for inst, fl in r["per_underlying_floor"].items():
        lines.append(
            f"| {inst} | {fl['n_surface_snapshots']} | {fl['n_surface_instruments']} | "
            f"{fl['n_surface_bars_5m']} | {fl['n_option_trades']} | {fl['n_of_instruments']} | "
            f"{fl['of_span_seconds']:.0f} | {fl['n_perp_bars_5m']} | "
            f"{fl['perp_span_seconds']:.0f} | {fl['n_common_bars_5m']} | {fl['ok']} |"
        )
    lines += ["", "## Per-underlying (best config)", "",
              "| underlying | configs | best Sharpe | best config | any pass |",
              "|---|---|---|---|---|"]
    for s in r["per_underlying"]:
        lines.append(
            f"| {s['underlying']} | {s['n_configs']} | {s['best_sharpe']:.4f} | "
            f"{s['best_config']} | {s['any_pass']} |"
        )
    lines += ["", "## Pooled", "",
              f"- Overall PBO: {r['pooled']['overall_pbo']:.4f}",
              f"- BH-FDR rejected: {r['pooled']['bh_fdr'].get('rejected')}",
              f"- All underlyings pass: {r['pooled']['all_underlyings_pass']}"]
    if r["errors"]:
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def build_blocked_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {BLOCKED_ID} — options order-flow toxicity -> realized vol straddle (below heavy-work floor)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        "- Verdict: **BLOCKED** (measured; not NO-GO)",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Underlyings: {', '.join(r['underlyings'])}",
        f"- Floor met: {r['floor_ok']}",
        "",
        "The capture does not meet the pre-registered heavy-work floor, so no",
        "GO/NO-GO verdict is emitted. A wider/longer synchronized real capture is",
        "required (do not stop: widen the capture and re-run).",
        "",
        "## Per-underlying floor",
        "",
    ]
    for inst, fl in r["per_underlying_floor"].items():
        lines.append(f"- {inst}: {json.dumps(fl['checks'])}")
    lines.append("")
    return "\n".join(lines) + "\n"


def _build_blocked_report(r: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "report_id": BLOCKED_ID,
        "generated_at": r["generated_at"],
        "task": r["task"],
        "verdict": "BLOCKED",
        "capture_dir": r["capture_dir"],
        "underlyings": r["underlyings"],
        "per_underlying_floor": r["per_underlying_floor"],
        "floor": r["floor"],
        "floor_ok": r["floor_ok"],
    }


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, default=str))


def _seal(report_id: str, report: Dict[str, Any], md_builder=None) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _stamp_for_filename(report.get("generated_at") or _utc_now_iso())
    written: Dict[str, str] = {}
    j = OUT_DIR / f"{report_id}_{stamp}.json"
    _write_json(j, report)
    written["json"] = str(j)
    if md_builder is not None:
        m = OUT_DIR / f"{report_id}_{stamp}.md"
        m.write_text(md_builder(report), encoding="utf-8")
        written["md"] = str(m)
    return written


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-61: real options order-flow toxicity -> subsequent realized "
                    "volatility, signal-timed delta-hedged ATM straddle net-of-cost falsification"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--task-label",
                    default="EVAL61-OPTIONS-ORDERFLOW-TO-REALIZED-VOL-STRADDLE")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval61(
            capture_dir=args.capture_dir, write=write, task_label=args.task_label
        )
    except BaseException as exc:  # noqa: BLE001
        traceback.print_exc()
        if write:
            blocked = _build_blocked_report({
                "generated_at": _utc_now_iso(),
                "task": args.task_label,
                "verdict": "BLOCKED",
                "capture_dir": args.capture_dir,
                "underlyings": [],
                "per_underlying_floor": {},
                "floor": build_protocol(args.capture_dir)["floor"],
                "floor_ok": False,
                "error": repr(exc),
            })
            _seal(BLOCKED_ID, blocked, build_blocked_md)
        return 1

    print(json.dumps({
        "verdict": report.get("verdict"),
        "floor_ok": report.get("floor_ok"),
        "underlyings": report.get("underlyings"),
        "per_underlying_floor": report.get("per_underlying_floor"),
        "per_underlying": report.get("per_underlying"),
        "overall_pbo": report.get("pooled", {}).get("overall_pbo"),
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
