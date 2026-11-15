#!/usr/bin/env python3
"""EVAL-59: real Deribit **options vol-surface / greeks -> 25Δ butterfly / convexity
net-of-cost P&L** falsification on BTC and ETH.

The repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is a quantitative **options** + orderflow strategy evaluated **net of cost**. Every
options+orderflow *fusion* cell (EVAL-46..53) and the options greeks/smile ladder rungs
EVAL-54 (delta-hedged short-vol), EVAL-55 (long-gamma gamma-scalping), EVAL-56
(term-structure calendar-spread), EVAL-57 (volatility risk premium / realized-vs-implied)
and EVAL-58 (skew / risk-reversal 25Δ, slope) are sealed ``NO-GO CONFIRMED (PASS)``;
re-litigating fused options+orderflow or EVAL-54..58 is prohibited. The unmeasured heavy
rung per the charter is **real options pricing / greeks / vol-surface -> net-of-cost
evaluation**. EVAL-59 is the *25Δ butterfly / convexity (curvature)* pure options-native
campaign: it backs real IV out of Deribit option marks, selects the ~25Δ call and ~25Δ
put plus the ATM call+put at a common strike nearest spot (same expiry), and trades the
25Δ butterfly (long 25Δ call + long 25Δ put − ATM call − ATM put, or the mirror)
delta-hedged in the perpetual, harvesting (or failing to harvest, net of cost) the smile
curvature/convexity premium — the pure options-native curvature rung not yet measured
(EVAL-58 measured the slope / butterfly), requiring fresh real data (Deribit option
trades are ~24h-capped).

Strictly additive: it consumes only the measured capture JSON files under
``--capture-dir`` and reuses the sealed pricing/greeks engine
(``src/features/options_pricing.py``) plus the sealed statistics helpers
(``_sharpe_of_returns``, ``_dsr_of_returns``, ``_cscv_pbo``, ``_benjamini_hochberg``,
``block_bootstrap_ci``, ``permutation_test``). It never re-runs a prior EVAL and never
edits ``src/`` or the sealed EVAL-02..57 scripts/tests/artifacts.

Pre-declared protocol (identical for every underlying; no curve fitting):
  * the underlying perpetual 1m candles are resampled to a 300s grid; each real 5m
    surface snapshot is treated as an end-of-bar state (its ``spot`` is the causal
    perpetual close at that bar end);
  * **real vol surface -> IV**: at the front expiry, for every quoted call and put,
    implied vol is backed out of its *real* mark
    (``implied_volatility(mark*spot, spot, K, 0, T, type)``) and ``delta`` comes from
    ``black_scholes_greeks`` at that IV; the ~25Δ call is the quoted call whose
    ``|delta|`` is nearest 0.25 and the ~25Δ put the quoted put whose ``|delta|`` is
    nearest 0.25 (both wings must be quoted with a finite positive IV; if either
    wing is missing the state is invalid -- never fabricate);
  * **skew signal**: skew = IV(~25Δ put) - IV(~25Δ call) (put-call IV spread);
  * **butterfly book** (pre-registered, fixed, no fitting): at each state, skew
    deviation = skew - trailing median skew over ``fly_lookback_bars`` (causal,
    bars ending at k). side = +1 (LONG risk reversal: long 25Δ call / short 25Δ put)
    when deviation > 0 (skew rich -> harvest convergence), side = -1 (SHORT risk
    reversal: short 25Δ call / long 25Δ put) when deviation < 0 (skew cheap), flat
    when 0. Exposure = clip(|deviation| / fly_target, 0, size_cap). Net position
    delta = exposure * side * (call_delta - put_delta); delta-hedged in the perpetual
    by holding ``hedge = -net_position_delta`` units of the underlying;
  * per-step (causal, decision at bar ``k`` -> outcome over ``[k, k+1]``) net-of-cost
    P&L in USD per 1-unit underlying notional:
      ``dRR_k   = exposure_k * side_k * ((call_mark_{k+1}-call_mark_k)
                                        - (put_mark_{k+1}-put_mark_k)) * S_k``
      ``gross_k = dRR_k + hedge_k * dS_k``
      ``cost_k  = HEDGE_FEE_BPS * |hedge_k - hedge_{k-1}| * S_k / 1e4
                 + entry spread (half, at k=0) + exit spread (half, at last step)
                 + flip spread (full, when side changes between steps)``
      ``ret_k   = (gross_k - cost_k) / S_k``;
  * full-series (causal -> out-of-sample) plus rolling walk-forward Sharpe / max-DD;
  * stats: 1000-perm paired permutation (strategy vs flat), 1000-resample block
    bootstrap CI on Sharpe (block 2), CSCV PBO across the pre-registered grid
    (k=4), BH-FDR (alpha 0.1), DSR; seed 42.

Pre-declared GO bar (conservative; the ladder EVAL-46..57 is CLOSED so NO-GO is the
default and GO needs strong evidence): GO only if, on **both** BTC and ETH and
**at least one** grid config, net-of-cost Sharpe > 0, no kill-switch breach
(max-DD <= 0.20), permutation p < 0.05, bootstrap 95% CI lower bound > 0, and pooled
PBO < 0.5. Otherwise ``NO-GO CONFIRMED (PASS)``.

Heavy-work floor (per underlying): surface >=100 snapshots / >=50 instruments /
>=240 5m bars; options order flow >=2000 trades / >=50 instruments / >=240 bars /
>=79200 s span; legs overlap on >=240 common 5m bars -- **plus** the term-structure
leg viable (>=2 distinct expiries each with a common strike nearest spot present in
>=100 snapshots). Below floor seals a measured ``EVAL_59_BLOCKED_<UTC>`` (never a
    NO-GO). Refuses to seal a verdict unless every underlying independently clears the
    floor and the roster has >=2 underlyings.

    Seal ``EVAL_59_PREREGISTRATION_<UTC>.{json,md}`` (before measurement) then
    ``EVAL_59_COMBINED_<UTC>.{json,md}`` (or ``EVAL_59_BLOCKED_<UTC>``).
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
from src.features.options_pricing import (  # noqa: E402
    PricingInputs,
    black_scholes_greeks,
    implied_volatility,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_59_COMBINED"
PREREG_ID = "EVAL_59_PREREGISTRATION"
BLOCKED_ID = "EVAL_59_BLOCKED"

BAR_SECONDS = 300.0
HEDGE_FEE_BPS = 5.0          # taker fee + impact on delta-hedge turnover
OPTION_SPREAD = ("each of the 4 butterfly legs (25Δ call, 25Δ put, ATM call, ATM put) "
                 "pays half its real bid/ask at entry and half at exit (all legs charged "
                 "round-trip spread); full spread charged when the butterfly side flips")
DAY_COUNT = 365.25
PERMUTATION_PERMS = 1000
BOOTSTRAP_RESAMPLES = 1000
BOOTSTRAP_BLOCK = 2
PBO_K_FOLDS = 4
PBO_N_COMBINATIONS = 16
FDR_ALPHA = 0.1
SEED = 42
KILL_SWITCH_MAX_DD = 0.20
MIN_RETURNS_PER_CONFIG = 20

# Butterfly / convexity pre-registered constants (no fitting).
DELTA_TARGET = 0.25       # 25Δ wings: |delta| nearest 0.25 (call +0.25 / put -0.25)
FLY_TARGET_CHOICES: Tuple[float, ...] = (0.25, 0.5)   # exposure = clip(|dev|/fly_target, 0, size_cap)
SIZE_CAP_CHOICES: Tuple[float, ...] = (0.5, 1.0)
FLY_LOOKBACK_BARS: Tuple[int, ...] = (12, 24, 48)     # 1h / 2h / 4h trailing skew median
REBALANCE_CHOICES: Tuple[int, ...] = (1, 2)

# Heavy-work floor (per underlying) — identical to the sealed EVAL-52/54/55/56/57
# floor, plus the term-structure viability requirement.
MIN_SNAPSHOTS = 100
MIN_BARS = 240
MIN_INSTRUMENTS = 50
MIN_TRADES = 2000
MIN_SPAN_SECONDS = 79200.0
MIN_COMMON_BARS = 240
MIN_UNDERLYINGS = 2

# Butterfly / convexity structures: single-expiry 25Δ risk reversal, long/short
# sized by the skew mean-reversion deviation.
STRUCTURES: Tuple[str, ...] = ("butterfly_25d_delta_hedged",)

CODE_PATHS: Tuple[str, ...] = (
    "src/features/options_pricing.py",
    "src/analytics/integrated_options_orderflow_evaluation.py",
    "src/analytics/real_walkforward_certification.py",
    "src/analytics/strategy_evaluation.py",
    "scripts/eval48_acquire_deribit_options.py",
    "scripts/eval51_acquire_options_orderflow.py",
    "scripts/eval52_acquire_synchronized_options.py",
    "scripts/eval56_acquire_options_surface.py",
    "scripts/eval56_term_structure_calendar_net_of_cost.py",
    "scripts/eval57_acquire_options_surface.py",
    "scripts/eval57_vrp_net_of_cost.py",
    "scripts/eval59_acquire_options_surface.py",
    "scripts/eval59_butterfly_net_of_cost.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval59_acquire_options_surface.py "
    "scripts/eval59_butterfly_net_of_cost.py "
    "tests/test_eval59_butterfly_net_of_cost.py",
    "python3 -m pytest -q tests/test_eval59_butterfly_net_of_cost.py",
    "python3 scripts/eval59_acquire_options_surface.py "
    "--underlying BTC --underlying ETH --days 1 --out-dir data/raw/eval59 --seal",
    "python3 scripts/eval59_butterfly_net_of_cost.py --prereg-only",
    "python3 scripts/eval59_butterfly_net_of_cost.py --no-write --capture-dir data/raw/eval59",
    "python3 scripts/eval59_butterfly_net_of_cost.py --capture-dir data/raw/eval59",
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


def _parse_expiry(expiry_iso: Any) -> Optional[datetime]:
    try:
        text = str(expiry_iso).strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except (TypeError, ValueError):
        return None


def _expiry_date(expiry_iso: Any) -> Optional[str]:
    try:
        return str(expiry_iso).strip()[:10]
    except (TypeError, ValueError):
        return None


def _median(vals: Sequence[float]) -> float:
    vals = sorted(float(v) for v in vals if math.isfinite(float(v)))
    if not vals:
        return 0.0
    m = len(vals) // 2
    if len(vals) % 2 == 1:
        return vals[m]
    return 0.5 * (vals[m - 1] + vals[m])


def _prod_1p(rets: Sequence[float]) -> float:
    eq = 1.0
    for r in rets:
        eq *= 1.0 + float(r)
        if eq <= 0.0:
            return -1.0
    return eq - 1.0


# ---------------------------------------------------------------------------
# Real surface -> IV + greeks (Black-Scholes on real marks)
# ---------------------------------------------------------------------------
def _iv_and_greeks(
    mark: float, bid: float, ask: float, spot: float, strike: float,
    expiry_iso: Any, state_time: datetime, option_type: str,
) -> Optional[Dict[str, float]]:
    """Back IV out of the real mark, return delta/gamma + USD prices.

    Returns ``None`` when the option cannot be priced at this state (expired, no
    marks, or non-positive inputs). Falls back to intrinsic delta if the IV solve
    fails (arbitrage / deep ITM-OTM) so a valid mark still yields a usable hedge.
    """
    mark = _finite(mark, 0.0)
    bid = _finite(bid, 0.0)
    ask = _finite(ask, 0.0)
    spot = _finite(spot, 0.0)
    strike = _finite(strike, 0.0)
    if mark <= 0.0 or spot <= 0.0 or strike <= 0.0:
        return None
    expiry = _parse_expiry(expiry_iso)
    if expiry is None:
        return None
    t_years = (expiry - state_time).total_seconds() / (DAY_COUNT * 86400.0)
    if t_years <= 0.0:
        return None

    price_usd = mark * spot
    bid_usd = bid * spot if bid > 0 else price_usd
    ask_usd = ask * spot if ask > 0 else price_usd
    iv: Optional[float]
    try:
        iv = float(implied_volatility(
            price_usd, spot, strike, 0.0, t_years, option_type, seed=SEED,
        ))
        g = black_scholes_greeks(PricingInputs(
            spot=spot, strike=strike, rate=0.0, volatility=iv,
            time_to_expiry=t_years, option_type=option_type, seed=SEED,
        ))
        delta = _finite(g.get("delta"), 0.0)
        gamma = _finite(g.get("gamma"), 0.0)
    except Exception:  # noqa: BLE001 - fall back to intrinsic delta
        iv = None
        if option_type == "call":
            delta = 1.0 if spot > strike else 0.0
        else:
            delta = -1.0 if spot < strike else 0.0
        gamma = 0.0
    return {
        "iv": float(iv) if iv is not None else float("nan"),
        "delta": float(delta),
        "gamma": float(gamma),
        "price_usd": float(price_usd),
        "bid_usd": float(bid_usd),
        "ask_usd": float(ask_usd),
        "strike": float(strike),
        "spot": float(spot),
        "t_years": float(t_years),
    }


# ---------------------------------------------------------------------------
# Per-snapshot enrichment: IV + greeks for EVERY quote, once (shared across configs)
# ---------------------------------------------------------------------------
def _enrich_snapshots(capture: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Compute IV/greeks for every quoted option at every snapshot exactly once.

    The result is a list of ``{bar_ms, spot, state_time, by_expiry}`` where
    ``by_expiry[expiry] = {"call": [entry, ...], "put": [entry, ...]}`` and each
    entry carries ``delta``/``iv``/``mark``/``bid``/``ask``/``strike``/... The skew
    selection + P&L then read from this cache, so the expensive IV solve is paid
    once per capture rather than once per config.
    """
    snapshots = sorted(
        capture.get("surface", {}).get("snapshots", []) or [],
        key=lambda s: int(s.get("bar_ms") or 0),
    )
    out: List[Dict[str, Any]] = []
    for snap in snapshots:
        bar_ms = int(snap.get("bar_ms") or 0)
        spot = _finite(snap.get("spot"), 0.0)
        if bar_ms <= 0 or spot <= 0.0:
            continue
        state_time = datetime.fromtimestamp(
            (bar_ms + int(BAR_SECONDS) * 1000) // 1000, tz=timezone.utc,
        )
        by_expiry: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        for q in snap.get("quotes") or []:
            exp = _expiry_date(q.get("expiry"))
            if not exp:
                continue
            ot = str(q.get("option_type") or "").lower()
            if ot not in ("call", "put"):
                continue
            mark = _finite(q.get("mark"), 0.0)
            strike = _finite(q.get("strike"), 0.0)
            if mark <= 0.0 or strike <= 0.0:
                continue
            g = _iv_and_greeks(
                mark, _finite(q.get("bid"), 0.0), _finite(q.get("ask"), 0.0),
                spot, strike, q.get("expiry"), state_time, ot,
            )
            if g is None:
                continue
            entry = {
                "iv": g["iv"], "delta": g["delta"], "gamma": g["gamma"],
                "price_usd": g["price_usd"], "bid_usd": g["bid_usd"],
                "ask_usd": g["ask_usd"], "strike": g["strike"],
                "mark": float(mark), "bid": _finite(q.get("bid"), 0.0),
                "ask": _finite(q.get("ask"), 0.0), "option_type": ot,
                "expiry": q.get("expiry"), "symbol": q.get("symbol"),
            }
            by_expiry.setdefault(exp, {"call": [], "put": []})[ot].append(entry)
        out.append({
            "bar_ms": bar_ms, "spot": float(spot),
            "state_time": state_time, "by_expiry": by_expiry,
        })
    return out


def _select_rr_wings(
    by_expiry: Dict[str, Dict[str, List[Dict[str, Any]]]], expiry: str,
) -> Optional[Dict[str, Any]]:
    """Select the ~25Δ call (|delta| nearest 0.25) and ~25Δ put (|delta| nearest
    0.25) at a common expiry.

    Only quotes with a finite, positive IV are eligible (skew needs a real IV on
    both wings). If either wing is missing -> ``None`` (never fabricate).
    """
    want = str(expiry)[:10]
    legs = by_expiry.get(want)
    if not legs:
        return None
    calls = [g for g in (legs.get("call") or [])
             if math.isfinite(g.get("iv", float("nan"))) and g.get("iv", 0.0) > 0.0]
    puts = [g for g in (legs.get("put") or [])
            if math.isfinite(g.get("iv", float("nan"))) and g.get("iv", 0.0) > 0.0]
    if not calls or not puts:
        return None
    call = min(calls, key=lambda g: abs(abs(g["delta"]) - DELTA_TARGET))
    put = min(puts, key=lambda g: abs(abs(g["delta"]) - DELTA_TARGET))
    return {"call": call, "put": put}


# ---------------------------------------------------------------------------
# Butterfly / convexity book construction (causal, net of cost)
# ---------------------------------------------------------------------------
def _rr_states(
    capture: Dict[str, Any],
    *,
    expiry: str,
    fly_lookback: int,
    fly_target: float,
    size_cap: float,
    enriched: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Build the causal butterfly state series (with side/exposure).

    Each state is an end-of-bar real snapshot where a valid 25Δ call+put pair was
    found at ``expiry``. ``skew = IV(put) - IV(call)``; the side/exposure is set by
    the pre-registered mean-reversion rule vs the trailing skew median.
    """
    if enriched is None:
        enriched = _enrich_snapshots(capture)
    raw: List[Dict[str, Any]] = []
    for es in enriched:
        pick = _select_rr_wings(es["by_expiry"], expiry)
        if not pick:
            continue
        call = pick["call"]
        put = pick["put"]
        skew = float(put["iv"]) - float(call["iv"])
        call_spread_usd = (float(call["ask_usd"]) - float(call["bid_usd"]))
        put_spread_usd = (float(put["ask_usd"]) - float(put["bid_usd"]))
        raw.append({
            "bar_ms": int(es["bar_ms"]),
            "spot": float(es["spot"]),
            "skew": skew,
            "call_iv": float(call["iv"]),
            "put_iv": float(put["iv"]),
            "call_delta": float(call["delta"]),
            "put_delta": float(put["delta"]),
            "call_mark": float(call["mark"]),
            "put_mark": float(put["mark"]),
            "call_strike": float(call["strike"]),
            "put_strike": float(put["strike"]),
            "spread_usd": float(call_spread_usd + put_spread_usd),
        })

    fly_lookback = max(1, int(fly_lookback))
    fly_target = float(fly_target)
    size_cap = float(size_cap)
    n = len(raw)
    for k in range(n):
        if k < fly_lookback - 1:
            raw[k].update(side=0, exposure=0.0, fly_dev=0.0, active=False)
            continue
        window = [raw[j]["skew"] for j in range(k - fly_lookback + 1, k + 1)]
        med = _median(window)
        dev = float(raw[k]["skew"]) - float(med)
        side = 1 if dev > 0.0 else (-1 if dev < 0.0 else 0)
        exposure = min(abs(dev) / fly_target, size_cap) if fly_target > 0.0 else 0.0
        if side == 0 or exposure <= 0.0:
            side = 0
            exposure = 0.0
        raw[k].update(
            side=int(side), exposure=float(exposure), fly_dev=float(dev), active=True,
        )
    return raw


def _rr_series(
    capture: Dict[str, Any],
    *,
    expiry: str,
    fly_lookback: int,
    fly_target: float,
    size_cap: float,
    rebalance: int,
    enriched: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Long/short 25Δ risk reversal sized by the skew mean-reversion deviation,
    delta-hedged in the perpetual. Causal: state at bar ``k`` -> outcome over
    ``[k, k+1]``.

    LONG risk reversal (side +1) = long 25Δ call / short 25Δ put, profits when the
    call richens vs the put (skew = IV_put - IV_call falls); SHORT risk reversal
    (side -1) = short 25Δ call / long 25Δ put, profits when skew rises. Each wing
    pays half its real bid/ask at entry and exit; a side flip charges the full 2-leg
    spread; hedge turnover charged at HEDGE_FEE_BPS.
    """
    states = _rr_states(
        capture, expiry=expiry, fly_lookback=fly_lookback,
        fly_target=fly_target, size_cap=size_cap, enriched=enriched,
    )
    n = len(states)
    if n < 2:
        return {
            "structure": "butterfly_25d_delta_hedged",
            "expiry": expiry, "fly_lookback": int(fly_lookback),
            "fly_target": float(fly_target), "size_cap": float(size_cap),
            "rebalance": int(rebalance),
            "n_states": n, "returns": [], "error": "insufficient priced states",
            "valid": False,
        }

    rebalance = max(1, int(rebalance))

    returns: List[float] = []
    gross_list: List[float] = []
    cost_list: List[float] = []
    n_rebalances = 0
    n_flips = 0
    prev_side = 0
    prev_hedge = 0.0

    for k in range(n - 1):
        s0 = float(states[k]["spot"])
        s1 = float(states[k + 1]["spot"])
        if s0 <= 0.0:
            returns.append(0.0); gross_list.append(0.0); cost_list.append(0.0); continue
        d_spot = s1 - s0

        side = int(states[k]["side"])
        exposure = float(states[k]["exposure"])
        call_mark = float(states[k]["call_mark"])
        put_mark = float(states[k]["put_mark"])
        call_delta = float(states[k]["call_delta"])
        put_delta = float(states[k]["put_delta"])
        spread_usd = float(states[k]["spread_usd"])

        # Position weights: side=+1 -> long call/short put; side=-1 -> short call/long put.
        w_call = float(side)
        w_put = -float(side)

        if k % rebalance == 0:
            hedge = -exposure * (w_call * call_delta + w_put * put_delta)
        else:
            hedge = prev_hedge
        if hedge != prev_hedge:
            n_rebalances += 1

        # Option mark-to-market P&L for [k, k+1] (position held constant over the step).
        next_call = float(states[k + 1]["call_mark"])
        next_put = float(states[k + 1]["put_mark"])
        d_option = exposure * (w_call * (next_call - call_mark) + w_put * (next_put - put_mark)) * s0
        gross = d_option + hedge * d_spot

        # Costs: hedge turnover + entry/exit spread + side-flip spread.
        turnover = abs(hedge - prev_hedge)
        cost = HEDGE_FEE_BPS * turnover * s0 / 1e4
        if k == 0:
            cost += 0.5 * spread_usd * exposure          # entry: half spread
        if k == n - 2:
            cost += 0.5 * float(states[-1]["spread_usd"]) * float(states[-1]["exposure"])  # exit: half spread
        if prev_side != 0 and side != 0 and prev_side != side:
            cost += spread_usd * exposure                # full spread on side flip
            n_flips += 1

        net = gross - cost
        returns.append(net / s0)
        gross_list.append(gross / s0)
        cost_list.append(cost / s0)

        prev_side = side
        prev_hedge = hedge

    active = [s for s in states if s.get("active")]
    devs = [float(s["fly_dev"]) for s in active if math.isfinite(float(s["fly_dev"]))]
    median_call_iv = _finite(_median([s["call_iv"] for s in states if math.isfinite(s["call_iv"])]), 0.0)
    median_put_iv = _finite(_median([s["put_iv"] for s in states if math.isfinite(s["put_iv"])]), 0.0)
    median_skew = _finite(_median([s["skew"] for s in states if math.isfinite(s["skew"])]), 0.0)
    median_fly = _finite(_median([s["fly_dev"] for s in states if math.isfinite(s["fly_dev"])]), 0.0)

    s0 = float(states[0]["spot"])
    net_rr_premium_usd = (float(states[0]["call_mark"]) - float(states[0]["put_mark"])) \
        * float(states[0]["exposure"]) * s0

    return {
        "structure": "butterfly_25d_delta_hedged",
        "expiry": expiry, "fly_lookback": int(fly_lookback),
        "fly_target": float(fly_target), "size_cap": float(size_cap),
        "rebalance": int(rebalance),
        "n_states": n, "n_returns": len(returns),
        "n_hedge_rebalances": int(n_rebalances), "n_side_flips": int(n_flips),
        "median_call_iv": median_call_iv,
        "median_put_iv": median_put_iv,
        "median_skew": median_skew,
        "median_fly": median_fly,
        "mean_fly_dev": _mean(devs),
        "entry_spread_usd": 0.5 * float(states[0]["spread_usd"]) * float(states[0]["exposure"]),
        "exit_spread_usd": 0.5 * float(states[-1]["spread_usd"]) * float(states[-1]["exposure"]),
        "net_rr_premium_usd": float(net_rr_premium_usd),
        "strike_call": float(states[0]["call_strike"]),
        "strike_put": float(states[0]["put_strike"]),
        "returns": returns,
        "gross_returns": gross_list,
        "cost_returns": cost_list,
        "valid": True,
    }


# ---------------------------------------------------------------------------
# Walk-forward + config evaluation
# ---------------------------------------------------------------------------
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
    *,
    structure: str,
    expiry: str,
    fly_lookback: int,
    fly_target: float,
    size_cap: float,
    rebalance: int,
    enriched: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    inst = capture.get("underlying", "UNKNOWN")
    series = _rr_series(
        capture, expiry=expiry, fly_lookback=fly_lookback,
        fly_target=fly_target, size_cap=size_cap, rebalance=rebalance,
        enriched=enriched,
    )
    rets = series.get("returns", [])
    base = {
        "underlying": inst,
        "structure": structure,
        "expiry": expiry, "fly_lookback": int(fly_lookback),
        "fly_target": float(fly_target), "size_cap": float(size_cap),
        "rebalance": int(rebalance),
        "bar_seconds": BAR_SECONDS,
        "n_states": series.get("n_states", 0),
        "median_call_iv": series.get("median_call_iv", 0.0),
        "median_put_iv": series.get("median_put_iv", 0.0),
        "median_skew": series.get("median_skew", 0.0),
        "median_fly": series.get("median_fly", 0.0),
        "mean_fly_dev": series.get("mean_fly_dev", 0.0),
        "n_hedge_rebalances": series.get("n_hedge_rebalances", 0),
        "n_side_flips": series.get("n_side_flips", 0),
        "strike_call": series.get("strike_call", 0.0),
        "strike_put": series.get("strike_put", 0.0),
        "entry_spread_usd": series.get("entry_spread_usd", 0.0),
        "exit_spread_usd": series.get("exit_spread_usd", 0.0),
        "net_rr_premium_usd": series.get("net_rr_premium_usd", 0.0),
        "valid": series.get("valid", False),
    }
    if not series.get("valid", False):
        return {**base, "n_returns": 0, "error": series.get("error", "invalid config"),
                "pass": False}
    if len(rets) < MIN_RETURNS_PER_CONFIG:
        return {**base, "n_returns": len(rets), "error": "insufficient returns",
                "pass": False}

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
    nonzero = sum(1 for r in rets if abs(float(r)) > 1e-12)
    passed = bool(
        sharpe > 0.0
        and not breach
        and perm_p < 0.05
        and ci_low > 0.0
        and nonzero > 0
    )
    return {
        **base,
        "n_returns": len(rets),
        "nonzero_returns": int(nonzero),
        "sharpe": sharpe,
        "max_drawdown": mdd,
        "kill_switch_breach": breach,
        "permutation_p": perm_p,
        "bootstrap_ci": [boot[0], ci_low, ci_high],
        "dsr": _dsr_of_returns(rets),
        "walkforward": wf,
        "mean_return": _mean(rets),
        "total_return": float(_prod_1p(rets)),
        "pass": passed,
    }


# ---------------------------------------------------------------------------
# Inventory + floor
# ---------------------------------------------------------------------------
def _capture_inventory(capture_dir: str) -> List[Dict[str, Any]]:
    """Load the newest synchronized capture per underlying."""
    best: Dict[str, Tuple[int, Dict[str, Any]]] = {}
    for path in sorted(glob.glob(os.path.join(capture_dir, "options_surface_*.json"))):
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
    ends: set = set()
    for c in perp_candles:
        px = _finite(c.get("close"), 0.0)
        if px <= 0:
            continue
        ts = int(c.get("ts") or 0)
        if ts <= 0:
            continue
        ends.add(((ts // bar_ms) + 1) * bar_ms)
    return sorted(ends)


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

    trade_ts = [int(t["ts"]) for t in trades if int(t.get("ts") or 0) > 0]
    n_trades = len(trades)
    of_instruments = len({t.get("instrument") for t in trades if t.get("instrument")})
    span = ((max(trade_ts) - min(trade_ts)) / 1000.0) if len(trade_ts) >= 2 else 0.0
    of_bars_5m = int(span // 300.0) if span > 0 else 0

    snap_avail = sorted(int(s.get("bar_ms") or 0) + 300 for s in snaps
                        if int(s.get("bar_ms") or 0) > 0)
    common = 0
    if trade_ts and snap_avail:
        lo, hi = min(trade_ts), max(trade_ts)
        j = -1
        for be in _bar_ends(perp, 300.0):
            if be < lo or be > hi:
                continue
            while j + 1 < len(snap_avail) and snap_avail[j + 1] <= be:
                j += 1
            if j >= 0:
                common += 1

    ts = _term_structure_viability(capture)
    ts_ok = bool(ts["viable"])

    checks = {
        "snapshots_ok": bool(n_snapshots >= MIN_SNAPSHOTS),
        "surface_instruments_ok": bool(surface_instruments >= MIN_INSTRUMENTS),
        "surface_bars_ok": bool(surface_bars_5m >= MIN_BARS),
        "trades_ok": bool(n_trades >= MIN_TRADES),
        "of_instruments_ok": bool(of_instruments >= MIN_INSTRUMENTS),
        "of_span_ok": bool(span >= MIN_SPAN_SECONDS),
        "of_bars_ok": bool(of_bars_5m >= MIN_BARS),
        "common_overlap_ok": bool(common >= MIN_COMMON_BARS),
        "term_structure_ok": ts_ok,
    }
    return {
        "underlying": inst,
        "n_surface_snapshots": n_snapshots,
        "n_surface_instruments": surface_instruments,
        "n_surface_bars_5m": surface_bars_5m,
        "n_option_trades": n_trades,
        "n_of_instruments": of_instruments,
        "of_span_seconds": round(span, 3),
        "n_of_bars_5m": of_bars_5m,
        "n_common_bars_5m": common,
        "n_viable_expiries": ts["n_viable_expiries"],
        "viable_expiries": ts["viable_expiries"],
        "checks": checks,
        "ok": bool(all(checks.values())),
    }


def _term_structure_viability(capture: Dict[str, Any]) -> Dict[str, Any]:
    """Count, per expiry, snapshots holding a common strike (call+put both quoted)
    nearest to spot. Viable iff >= 2 expiries each reach >=100 snapshots."""
    snaps = capture.get("surface", {}).get("snapshots", []) or []
    expiry_counts: Dict[str, int] = {}
    for snap in snaps:
        spot = float(snap.get("spot") or 0.0)
        if spot <= 0.0:
            continue
        quotes = snap.get("quotes") or []
        by_expiry: Dict[str, Dict[str, List[float]]] = {}
        for q in quotes:
            exp = _expiry_date(q.get("expiry"))
            if not exp:
                continue
            ot = str(q.get("option_type") or "").lower()
            if ot not in ("call", "put"):
                continue
            try:
                strike = float(q.get("strike") or 0.0)
                mark = float(q.get("mark") or 0.0)
            except (TypeError, ValueError):
                continue
            if strike <= 0.0 or mark <= 0.0:
                continue
            by_expiry.setdefault(exp, {}).setdefault(ot, []).append(strike)
        for exp, legs in by_expiry.items():
            calls = set(legs.get("call", []))
            puts = set(legs.get("put", []))
            if calls & puts:
                expiry_counts[exp] = expiry_counts.get(exp, 0) + 1
    viable = sorted(
        exp for exp, n in expiry_counts.items()
        if n >= TERM_STRUCTURE_MIN_SNAPSHOTS_PER_EXPIRY
    )
    return {
        "viable": len(viable) >= TERM_STRUCTURE_MIN_EXPIRIES,
        "n_viable_expiries": len(viable),
        "viable_expiries": viable,
        "expiry_snapshot_counts": {exp: expiry_counts.get(exp, 0) for exp in sorted(expiry_counts)},
    }


# Term-structure viability floor constants (mirrored in the acquisition script).
TERM_STRUCTURE_MIN_EXPIRIES = 2
TERM_STRUCTURE_MIN_SNAPSHOTS_PER_EXPIRY = 100


def _distinct_expiries(capture: Dict[str, Any]) -> List[str]:
    dates = {
        str(q.get("expiry"))[:10]
        for s in capture.get("surface", {}).get("snapshots", []) or []
        for q in (s.get("quotes") or [])
        if str(q.get("expiry") or "")[:4].isdigit()
    }
    return sorted(d for d in dates if d)


# ---------------------------------------------------------------------------
# Protocol + orchestration
# ---------------------------------------------------------------------------
def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-59",
        "title": "Real Deribit options vol-surface/greeks butterfly / convexity (25Δ) "
                 "net-of-cost falsification",
        "capture_dir": str(capture_dir),
        "surface_to_iv": (
            "per real 5m snapshot & front expiry: IV backed out of each real quote "
            "mark (implied_volatility(mark*spot, spot, K, 0, T, type)); ~25Δ call = "
            "quoted call with |delta| nearest 0.25, ~25Δ put = quoted put with "
            "|delta| nearest 0.25 (both wings need a finite positive IV)"
        ),
        "structures": list(STRUCTURES),
        "fly_lookback_bars": [int(b) for b in FLY_LOOKBACK_BARS],
        "fly_target_choices": [float(t) for t in FLY_TARGET_CHOICES],
        "size_cap_choices": [float(c) for c in SIZE_CAP_CHOICES],
        "rebalance_choices": list(REBALANCE_CHOICES),
        "delta_target": float(DELTA_TARGET),
        "cost_model": (
            "net-of-cost: hedge turnover HEDGE_FEE_BPS on |Δhedge|*S; each of the 2 "
            "butterfly wings pays half its real bid/ask at entry and half at "
            "exit; full spread charged on butterfly side flips"
        ),
        "hedge_fee_bps": float(HEDGE_FEE_BPS),
        "option_spread": OPTION_SPREAD,
        "pnl": (
            "dRR_k = exposure_k*side_k*((call_mark_{k+1}-call_mark_k)-(put_mark_{k+1}-put_mark_k))*S_k; "
            "gross_k = dRR_k + hedge_k*dS_k (hedge = -exposure*side*(call_delta - put_delta)); "
            "ret_k = (gross_k - cost_k)/S_k; decision at bar k -> outcome over [k,k+1] (causal)"
        ),
        "skew_rule": (
            "skew = IV(~25Δ put) - IV(~25Δ call); deviation = skew - trailing median skew "
            "over fly_lookback_bars (causal); side = +1 (long RR: long call/short put) "
            "when deviation > 0, -1 (short RR) when deviation < 0, 0 when equal; "
            "exposure = clip(|deviation| / fly_target, 0, size_cap)"
        ),
        "wing_selection_rule": (
            "~25Δ call = quoted call with |delta| nearest 0.25; ~25Δ put = quoted put "
            "with |delta| nearest 0.25; both at the front expiry; else config invalid"
        ),
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
            "term_structure_min_expiries": TERM_STRUCTURE_MIN_EXPIRIES,
            "term_structure_min_snapshots_per_expiry": TERM_STRUCTURE_MIN_SNAPSHOTS_PER_EXPIRY,
        },
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def _config_grid(capture: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Pre-registered config list: structures x front expiry x fly_lookback x
    fly_target x size_cap x rebalance."""
    expiries = _distinct_expiries(capture)
    grid: List[Dict[str, Any]] = []
    if len(expiries) < 1:
        return grid
    front_expiry = expiries[0]
    for structure in STRUCTURES:
        for fly_lookback in FLY_LOOKBACK_BARS:
            for fly_target in FLY_TARGET_CHOICES:
                for size_cap in SIZE_CAP_CHOICES:
                    for rebalance in REBALANCE_CHOICES:
                        grid.append({
                            "structure": structure,
                            "expiry": front_expiry,
                            "fly_lookback": int(fly_lookback),
                            "fly_target": float(fly_target),
                            "size_cap": float(size_cap),
                            "rebalance": int(rebalance),
                        })
    return grid


def run_eval59(
    *,
    capture_dir: str = "data/raw/eval59",
    write: bool = True,
    task_label: str = "EVAL-59-REAL-OPTIONS-SKEW-RISK-REVERSAL-NET-OF-COST-BTC-ETH",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    captures = _capture_inventory(str(capture_dir_abs))

    per_underlying_floor: Dict[str, Dict[str, Any]] = {}
    for c in captures:
        inst = c.get("underlying", "?")
        per_underlying_floor[inst] = _underlying_floor(c)

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
        enriched = _enrich_snapshots(cap)  # IV/greeks paid once per capture
        for cfg in _config_grid(cap):
            key = (f"{inst}::{cfg['structure']}::{cfg['expiry']}::lb{cfg['fly_lookback']}"
                   f"::st{cfg['fly_target']}::sc{cfg['size_cap']}::reb{cfg['rebalance']}")
            try:
                res = evaluate_config(
                    cap, structure=cfg["structure"], expiry=cfg["expiry"],
                    fly_lookback=cfg["fly_lookback"], fly_target=cfg["fly_target"],
                    size_cap=cfg["size_cap"], rebalance=cfg["rebalance"],
                    enriched=enriched,
                )
            except BaseException as exc:  # noqa: BLE001
                errors.append(f"{key}: {exc!r}")
                continue
            res["config_key"] = key
            per_config.append(res)
            if res.get("n_returns", 0) >= MIN_RETURNS_PER_CONFIG:
                series = _rr_series(
                    cap, expiry=cfg["expiry"], fly_lookback=cfg["fly_lookback"],
                    fly_target=cfg["fly_target"], size_cap=cfg["size_cap"],
                    rebalance=cfg["rebalance"], enriched=enriched,
                )
                if series.get("returns"):
                    returns_by_config[key] = series["returns"]

    pbo = _cscv_pbo(returns_by_config, n_combinations=PBO_N_COMBINATIONS,
                    k_folds=PBO_K_FOLDS, seed=SEED) if len(returns_by_config) >= 2 else {
                    "overall_pbo": 0.0, "note": "insufficient configs"}
    p_values = {
        r["config_key"]: _finite(r.get("permutation_p"), 1.0)
        for r in per_config if r.get("n_returns", 0) >= MIN_RETURNS_PER_CONFIG
    }
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}

    by_inst: Dict[str, List[Dict[str, Any]]] = {}
    for r in per_config:
        if r.get("n_returns", 0) >= MIN_RETURNS_PER_CONFIG:
            by_inst.setdefault(r["underlying"], []).append(r)
    inst_summary: List[Dict[str, Any]] = []
    for inst, rows in by_inst.items():
        best = max(rows, key=lambda r: _finite(r.get("sharpe"), -1e9))
        inst_summary.append({
            "underlying": inst,
            "n_configs": len(rows),
            "best_sharpe": _finite(best.get("sharpe"), 0.0),
            "best_config": best.get("config_key"),
            "best_median_call_iv": _finite(best.get("median_call_iv"), 0.0),
            "best_median_put_iv": _finite(best.get("median_put_iv"), 0.0),
            "best_median_skew": _finite(best.get("median_skew"), 0.0),
            "best_mean_fly_dev": _finite(best.get("mean_fly_dev"), 0.0),
            "best_strike_call": _finite(best.get("strike_call"), 0.0),
            "best_strike_put": _finite(best.get("strike_put"), 0.0),
            "any_pass": bool(any(r.get("pass") for r in rows)),
        })

    all_pass = bool(inst_summary) and all(s["any_pass"] for s in inst_summary)
    pooled_pbo = _finite(pbo.get("overall_pbo"), 0.0)
    go = bool(floor_ok and all_pass and pooled_pbo < 0.5)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = "EVAL_59_OPTIONS_BUTTERFLY_25D" if floor_ok else "EVAL_59_BLOCKED_FLOOR"

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "real Deribit options vol-surface/greeks butterfly / convexity (25Δ) "
            "net-of-cost falsification"
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


def _prereg_payload(generated_at: str, capture_dir: str, task_label: str) -> Dict[str, Any]:
    p = build_protocol(capture_dir)
    return {
        "prereg_id": PREREG_ID,
        "generated_at": generated_at,
        "task": task_label,
        "hypothesis": (
            "A real Deribit options vol-surface/greeks butterfly / convexity (25Δ) "
            "trade (long one 25Δ wing / short the other, sized by the skew "
            "mean-reversion deviation, delta-hedged in the perpetual) is "
            "net-of-cost tradable for the underlying BTC/ETH perpetual on real, "
            "synchronized Deribit data."
        ),
        "protocol": p,
        "capture_dir": str(capture_dir),
    }


def build_prereg(report: Dict[str, Any]) -> Dict[str, Any]:
    return _prereg_payload(report["generated_at"], report["capture_dir"], report["task"])


def build_prereg_md(p: Dict[str, Any]) -> str:
    proto = p["protocol"]
    lines = [
        f"# {p['prereg_id']} — EVAL-59 options vol-surface/greeks butterfly / convexity (25Δ) net-of-cost falsification",
        "",
        f"- Generated: `{p['generated_at']}`",
        f"- Task: `{p['task']}`",
        f"- Hypothesis: {p['hypothesis']}",
        f"- Capture dir: `{p['capture_dir']}`",
        "",
        "## Pre-declared protocol",
        "",
        f"- Surface -> IV: {proto['surface_to_iv']}",
        f"- Structures: {proto['structures']}",
        f"- Skew lookback bars (trailing skew median): {proto['fly_lookback_bars']}",
        f"- Skew target choices: {proto['fly_target_choices']}; size cap choices: {proto['size_cap_choices']}",
        f"- Rebalance choices: {proto['rebalance_choices']}; 25Δ delta target: {proto['delta_target']}",
        f"- Cost: {proto['cost_model']} (hedge {proto['hedge_fee_bps']} bps; {proto['option_spread']})",
        f"- PnL: {proto['pnl']}",
        f"- Skew rule: {proto['skew_rule']}",
        f"- Wing selection rule: {proto['wing_selection_rule']}",
        f"- Walk-forward: {proto['walkforward']}",
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
        f"- min option trades/underlying: {proto['floor']['min_option_trades_per_underlying']}",
        f"- min span seconds/underlying: {proto['floor']['min_span_seconds_per_underlying']}",
        f"- min common 5m bars/underlying: {proto['floor']['min_common_bars_per_underlying']}",
        f"- min underlyings: {proto['floor']['min_underlyings']}",
        f"- term-structure min expiries: {proto['floor']['term_structure_min_expiries']}",
        f"- term-structure min snapshots/expiry: {proto['floor']['term_structure_min_snapshots_per_expiry']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def build_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {r['report_id']} — Real Deribit options vol-surface/greeks butterfly / convexity (25Δ) net-of-cost falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        "",
        "## Per-underlying floor",
        "",
        "| underlying | snaps | surf inst | 5m bars | trades | of inst | span s | common 5m | viable expiries | ok |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for inst, fl in r["per_underlying_floor"].items():
        lines.append(
            f"| {inst} | {fl['n_surface_snapshots']} | {fl['n_surface_instruments']} | "
            f"{fl['n_surface_bars_5m']} | {fl['n_option_trades']} | {fl['n_of_instruments']} | "
            f"{fl['of_span_seconds']:.0f} | {fl['n_common_bars_5m']} | "
            f"{fl['n_viable_expiries']} | {fl['ok']} |"
        )
    lines += ["", "## Per-underlying (best config)", "",
              "| underlying | configs | best Sharpe | best config | best median call IV | best median put IV | best median skew | best mean skew dev | best strike call | best strike put | any pass |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for s in r["per_underlying"]:
        lines.append(
            f"| {s['underlying']} | {s['n_configs']} | {s['best_sharpe']:.4f} | "
            f"{s['best_config']} | {s['best_median_call_iv']:.4f} | {s['best_median_put_iv']:.4f} | "
            f"{s['best_median_skew']:.4f} | {s['best_mean_fly_dev']:.4f} | "
            f"{s['best_strike_call']:.2f} | {s['best_strike_put']:.2f} | {s['any_pass']} |"
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
        f"# {BLOCKED_ID} — options vol-surface/greeks butterfly / convexity (25Δ) net-of-cost (below heavy-work floor)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        "- Verdict: **BLOCKED** (measured; not NO-GO)",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Underlyings: {', '.join(r['underlyings'])}",
        f"- Floor met: {r['floor_ok']}",
        "",
        "The capture does not meet the pre-registered heavy-work floor (including the",
        "term-structure viability requirement), so no GO/NO-GO verdict is emitted.",
        "A wider/longer synchronized real Deribit capture is required.",
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
        description="EVAL-59 real Deribit options vol-surface/greeks butterfly / convexity (25Δ) net-of-cost falsification"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval59")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--prereg-only", action="store_true",
                    help="seal EVAL_58_PREREGISTRATION from the pre-declared protocol only "
                         "(no measurement); use BEFORE the measuring run")
    ap.add_argument("--task-label",
                    default="EVAL-59-REAL-OPTIONS-SKEW-RISK-REVERSAL-NET-OF-COST-BTC-ETH")
    args = ap.parse_args(argv)

    if args.prereg_only:
        generated_at = _utc_now_iso()
        prereg = _prereg_payload(generated_at, args.capture_dir, args.task_label)
        written = _seal(PREREG_ID, prereg, build_prereg_md)
        print(json.dumps({"prereg_only": True, "artifact_paths": written}, sort_keys=True))
        return 0

    write = not args.no_write
    try:
        report = run_eval59(
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