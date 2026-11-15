#!/usr/bin/env python3
"""EVAL-55: real Deribit **options vol-surface / greeks -> gamma-hedged (long-gamma
gamma-scalping) P&L net of cost** falsification on BTC and ETH.

The repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is a quantitative **options** + orderflow strategy evaluated **net of cost**. Every
options+orderflow *fusion* cell (EVAL-46..53) and EVAL-54 (delta-hedged short-vol
net-of-cost) are sealed ``NO-GO CONFIRMED (PASS)``; re-litigating fused
options+orderflow or EVAL-54 is prohibited. The unmeasured heavy rung per the charter
is **real options pricing / greeks / vol-surface -> gamma-hedged P&L net of execution
costs**. EVAL-55 is the *long-gamma* pure options-native campaign: it buys real ATM
options and delta-hedges them (gamma scalping), profiting only if realized vol exceeds
the implied vol paid -- the opposite gamma exposure to EVAL-54's short-vol book, and a
distinct strategy that requires fresh real data (Deribit option trades are ~24h-capped).

Strictly additive: it consumes only the measured capture JSON files under
``--capture-dir`` and reuses the sealed pricing/greeks engine
(``src/features/options_pricing.py``) plus the sealed statistics helpers
(``_sharpe_of_returns``, ``_dsr_of_returns``, ``_cscv_pbo``, ``_benjamini_hochberg``,
``block_bootstrap_ci``, ``permutation_test``). It never re-runs a prior EVAL and never
edits ``src/`` or the sealed EVAL-02..54 scripts/tests/artifacts.

Pre-declared protocol (identical for every underlying; no curve fitting):
  * the underlying perpetual 1m candles are resampled to a 300s grid; each real 5m
    surface snapshot is treated as an end-of-bar state (its ``spot`` is the causal
    perpetual close at that bar end);
  * **real vol surface -> greeks**: for a chosen expiry and strike (nearest-to-spot
    ATM), the option's implied vol is backed out of its *real* mark
    (``implied_volatility(mark*spot, spot, K, 0, T, type)``) and ``delta`` /
    ``gamma`` come from ``black_scholes_greeks`` at that IV -- a real surface/greeks
    signal, not a hard-coded vol;
  * **long-gamma (gamma-scalping) book** (pre-registered, fixed, no fitting): LONG ATM
    ``call`` / ``put`` / ``straddle`` at a fixed expiry, delta-hedged in the perpetual
    by holding ``hedge = -position_delta`` units of the underlying;
  * per-step (causal, decision at bar ``k`` -> outcome over ``[k, k+1]``) net-of-cost
    P&L in USD per 1-unit underlying notional:
      ``gross_k = +(dOptionUSD_k) + hedge_k * dS_k``  (long option, short hedge)
      ``cost_k  = HEDGE_FEE_BPS * |hedge_k - hedge_{k-1}| * S_k / 1e4``
                 + option half bid/ask paid at entry (first step) and exit (last step)
      ``ret_k   = (gross_k - cost_k) / S_k``;
  * gamma attribution (diagnostic, not a pass criterion): realized gamma capture
    ``0.5 * Gamma_usd_k * (dS_k)^2`` summed, compared to the option premium/decay, to
    show whether the long-gamma book's P&L is gamma-driven or premium-driven;
  * full-series (causal -> out-of-sample) plus rolling walk-forward Sharpe / max-DD;
  * stats: 1000-perm paired permutation (strategy vs flat), 1000-resample block
    bootstrap CI on Sharpe (block 2), CSCV PBO across the pre-registered grid (k=4),
    BH-FDR (alpha 0.1), DSR; seed 42.

Pre-declared GO bar (conservative; the ladder EVAL-46..54 is CLOSED so NO-GO is the
default and GO needs strong evidence): GO only if, on **both** BTC and ETH and
**at least one** grid config, net-of-cost Sharpe > 0, no kill-switch breach
(max-DD <= 0.20), permutation p < 0.05, bootstrap 95% CI lower bound > 0, and pooled
PBO < 0.5. Otherwise ``NO-GO CONFIRMED (PASS)``.

Heavy-work floor (sealed; identical to the EVAL-52/54 floor): refuses to seal a verdict
unless **every** underlying independently clears the per-underlying floor -- surface
>=100 snapshots / >=50 instruments / >=240 5m bars; options order flow >=2000 trades /
>=50 instruments / >=240 bars / >=79200 s span; the two legs overlap on >=240 common
5m bars -- and the roster has >=2 underlyings. Below floor seals a measured
``EVAL_55_BLOCKED_<UTC>`` (never a NO-GO).

Seal ``EVAL_55_PREREGISTRATION_<UTC>.{json,md}`` (before measurement) then
``EVAL_55_COMBINED_<UTC>.{json,md}`` (or ``EVAL_55_BLOCKED_<UTC>``).
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
REPORT_ID = "EVAL_55_COMBINED"
PREREG_ID = "EVAL_55_PREREGISTRATION"
BLOCKED_ID = "EVAL_55_BLOCKED"

BAR_SECONDS = 300.0
HEDGE_FEE_BPS = 5.0          # taker fee + impact on delta-hedge turnover
OPTION_SPREAD = "half real bid/ask paid at entry and exit (long options pay the ask)"
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

# Heavy-work floor (per underlying) — identical to the sealed EVAL-52/54 floor.
MIN_SNAPSHOTS = 100
MIN_BARS = 240
MIN_INSTRUMENTS = 50
MIN_TRADES = 2000
MIN_SPAN_SECONDS = 79200.0
MIN_COMMON_BARS = 240
MIN_UNDERLYINGS = 2

# Long-gamma structures (EVAL-55). Short-vol (EVAL-54) is prohibited re-litigation;
# these are the *long*-gamma books whose gamma-scalp P&L is realized-vs-implied vol.
STRUCTURES: Tuple[str, ...] = ("long_atm_call", "long_atm_put", "long_atm_straddle")
EXPIRY_CHOICES: Tuple[int, ...] = (0, 1)
REBALANCE_CHOICES: Tuple[int, ...] = (1, 2)
GRID_BAR_SECONDS: Tuple[float, ...] = (300.0,)

CODE_PATHS: Tuple[str, ...] = (
    "src/features/options_pricing.py",
    "src/analytics/integrated_options_orderflow_evaluation.py",
    "src/analytics/real_walkforward_certification.py",
    "src/analytics/strategy_evaluation.py",
    "scripts/eval48_acquire_deribit_options.py",
    "scripts/eval51_acquire_options_orderflow.py",
    "scripts/eval52_acquire_synchronized_options.py",
    "scripts/eval55_acquire_options_surface.py",
    "scripts/eval55_gamma_hedged_net_of_cost.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval55_acquire_options_surface.py "
    "scripts/eval55_gamma_hedged_net_of_cost.py "
    "tests/test_eval55_gamma_hedged_net_of_cost.py",
    "python3 -m pytest -q tests/test_eval55_gamma_hedged_net_of_cost.py",
    "python3 scripts/eval55_acquire_options_surface.py "
    "--underlying BTC --underlying ETH --days 1 --out-dir data/raw/eval55 --seal",
    "python3 scripts/eval55_gamma_hedged_net_of_cost.py --prereg-only",
    "python3 scripts/eval55_gamma_hedged_net_of_cost.py --no-write",
    "python3 scripts/eval55_gamma_hedged_net_of_cost.py",
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


def _median(vals: Sequence[float]) -> float:
    vals = sorted(float(v) for v in vals if math.isfinite(float(v)))
    if not vals:
        return 0.0
    m = len(vals) // 2
    if len(vals) % 2 == 1:
        return vals[m]
    return 0.5 * (vals[m - 1] + vals[m])


# ---------------------------------------------------------------------------
# Real surface -> greeks (Black-Scholes on real marks)
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
            price_usd, spot, strike, 0.0, t_years, option_type, seed=SEED
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


def _pick_quote(
    quotes: Sequence[Dict[str, Any]], spot: float, expiry_date: str,
    need_call: bool, need_put: bool,
) -> Optional[Dict[str, Any]]:
    """Nearest-to-spot quote(s) at ``expiry_date`` for the requested legs.

    Returns a dict ``{"call": q|None, "put": q|None}`` with a common strike when both
    legs are requested (straddle), else the single requested leg.
    """
    want_date = str(expiry_date)[:10]
    pool = []
    for q in quotes:
        try:
            if str(q.get("expiry", ""))[:10] != want_date:
                continue
            strike = float(q.get("strike") or 0.0)
            mark = float(q.get("mark") or 0.0)
        except (TypeError, ValueError):
            continue
        if strike <= 0.0 or mark <= 0.0:
            continue
        pool.append((strike, q))

    if need_call and need_put:
        calls = {s: q for s, q in pool if str(q.get("option_type")).lower() == "call"}
        puts = {s: q for s, q in pool if str(q.get("option_type")).lower() == "put"}
        common = sorted(set(calls) & set(puts))
        if not common:
            return None
        strike = min(common, key=lambda s: abs(s - spot))
        return {"call": calls[strike], "put": puts[strike]}
    if need_call:
        cand = [(s, q) for s, q in pool if str(q.get("option_type")).lower() == "call"]
        if not cand:
            return None
        return {"call": min(cand, key=lambda x: abs(x[0] - spot))[1], "put": None}
    cand = [(s, q) for s, q in pool if str(q.get("option_type")).lower() == "put"]
    if not cand:
        return None
    return {"call": None, "put": min(cand, key=lambda x: abs(x[0] - spot))[1]}


# ---------------------------------------------------------------------------
# Long-gamma (gamma-scalping) book construction (causal, net of cost)
# ---------------------------------------------------------------------------
def _gamma_scalp_series(
    capture: Dict[str, Any],
    *,
    structure: str,
    expiry_iso: str,
    rebalance: int,
) -> Dict[str, Any]:
    """Long-gamma delta-hedged gamma-scalping P&L, net of cost.

    Walks the real 5m surface snapshots in ascending time. Each snapshot is an
    end-of-bar state; the hedge set at state ``k`` (from the real IV/delta/gamma) is
    held over ``[k, k+1]`` so the P&L is strictly causal. The book is LONG the option
    (pay the ask at entry, receive the bid at exit) and delta-hedged by holding
    ``hedge = -position_delta`` units of the perpetual. Returns per-step net-of-cost
    returns on 1-unit underlying notional, a realized-gamma-capture diagnostic, and
    structural diagnostics.
    """
    snapshots = sorted(
        capture.get("surface", {}).get("snapshots", []) or [],
        key=lambda s: int(s.get("bar_ms") or 0),
    )
    need_call = structure in ("long_atm_call", "long_atm_straddle")
    need_put = structure in ("long_atm_put", "long_atm_straddle")

    states: List[Dict[str, Any]] = []
    for snap in snapshots:
        bar_ms = int(snap.get("bar_ms") or 0)
        if bar_ms <= 0:
            continue
        spot = _finite(snap.get("spot"), 0.0)
        if spot <= 0.0:
            continue
        quotes = snap.get("quotes") or []
        pick = _pick_quote(quotes, spot, expiry_iso, need_call, need_put)
        if not pick:
            continue
        state_time = datetime.fromtimestamp((bar_ms + int(BAR_SECONDS) * 1000) / 1000.0,
                                            tz=timezone.utc)
        legs: List[Dict[str, float]] = []
        ok = True
        for key in ("call", "put"):
            q = pick.get(key)
            if not q:
                continue
            g = _iv_and_greeks(
                _finite(q.get("mark"), 0.0), _finite(q.get("bid"), 0.0),
                _finite(q.get("ask"), 0.0), spot, _finite(q.get("strike"), 0.0),
                q.get("expiry"), state_time,
                str(q.get("option_type") or key).lower(),
            )
            if g is None:
                ok = False
                break
            legs.append(g)
        if not ok or not legs:
            continue
        # LONG the option: position delta = +sum(option deltas); gamma = +sum.
        position_delta = sum(l["delta"] for l in legs)   # option position delta
        position_gamma = sum(l["gamma"] for l in legs)   # option position gamma
        states.append({
            "state_time": state_time,
            "spot": spot,
            "position_delta": float(position_delta),
            "position_gamma": float(position_gamma),
            "price_usd": sum(l["price_usd"] for l in legs),
            "bid_usd": sum(l["bid_usd"] for l in legs),
            "ask_usd": sum(l["ask_usd"] for l in legs),
            "iv": _mean([l["iv"] for l in legs if math.isfinite(l["iv"])]),
        })

    n = len(states)
    if n < 2:
        return {
            "structure": structure, "expiry": expiry_iso, "rebalance": int(rebalance),
            "n_states": n, "returns": [], "error": "insufficient priced states",
        }

    rebalance = max(1, int(rebalance))
    # Long option -> short the underlying delta: hedge = -position_delta.
    hedge: List[float] = []
    h = 0.0
    for k in range(n):
        if k % rebalance == 0:
            h = -float(states[k]["position_delta"])
        hedge.append(h)

    # Long options: pay half real bid/ask at entry (ask - mark) and at exit (mark - bid).
    entry_spread = 0.5 * ((states[0]["ask_usd"] - states[0]["bid_usd"]))
    exit_spread = 0.5 * ((states[-1]["ask_usd"] - states[-1]["bid_usd"]))

    returns: List[float] = []
    gross_list: List[float] = []
    cost_list: List[float] = []
    gamma_capture_list: List[float] = []
    n_rebalances = 0
    for k in range(n - 1):
        s0 = float(states[k]["spot"])
        s1 = float(states[k + 1]["spot"])
        if s0 <= 0.0:
            returns.append(0.0)
            gross_list.append(0.0)
            cost_list.append(0.0)
            gamma_capture_list.append(0.0)
            continue
        d_spot = s1 - s0
        d_option = float(states[k + 1]["price_usd"]) - float(states[k]["price_usd"])
        # Long option + short-delta hedge.
        gross = (d_option) + hedge[k] * d_spot
        # Realized gamma capture over the step (USD, per 1 option unit): 0.5*Γ*(ΔS)^2.
        gamma_capture = 0.5 * float(states[k]["position_gamma"]) * d_spot * d_spot
        turnover = abs(hedge[k] - (hedge[k - 1] if k > 0 else 0.0))
        if turnover > 0.0:
            n_rebalances += 1
        cost = HEDGE_FEE_BPS * turnover * s0 / 1e4
        if k == 0:
            cost += entry_spread
        if k == n - 2:
            cost += exit_spread
        net = gross - cost
        returns.append(net / s0)
        gross_list.append(gross / s0)
        cost_list.append(cost / s0)
        gamma_capture_list.append(gamma_capture / s0)

    realized_gamma_capture_usd = float(sum(
        0.5 * float(states[k]["position_gamma"]) *
        (float(states[k + 1]["spot"]) - float(states[k]["spot"])) ** 2
        for k in range(n - 1)
    ))
    total_premium_usd = float(states[0]["price_usd"])

    return {
        "structure": structure,
        "expiry": expiry_iso,
        "rebalance": int(rebalance),
        "n_states": n,
        "n_returns": len(returns),
        "n_hedge_rebalances": int(n_rebalances),
        "median_iv": _finite(_median([s["iv"] for s in states if math.isfinite(s["iv"])]), 0.0),
        "entry_spread_usd": float(entry_spread),
        "exit_spread_usd": float(exit_spread),
        "total_premium_usd": total_premium_usd,
        "realized_gamma_capture_usd": realized_gamma_capture_usd,
        "gamma_capture_over_premium": (
            realized_gamma_capture_usd / total_premium_usd
            if total_premium_usd > 0.0 else 0.0
        ),
        "returns": returns,
        "gross_returns": gross_list,
        "cost_returns": cost_list,
        "gamma_capture_returns": gamma_capture_list,
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
    expiry_iso: str,
    rebalance: int,
) -> Dict[str, Any]:
    inst = capture.get("underlying", "UNKNOWN")
    series = _gamma_scalp_series(
        capture, structure=structure, expiry_iso=expiry_iso, rebalance=rebalance
    )
    rets = series["returns"]
    base = {
        "underlying": inst,
        "structure": structure,
        "expiry": expiry_iso,
        "rebalance": int(rebalance),
        "bar_seconds": BAR_SECONDS,
        "n_states": series.get("n_states", 0),
        "median_iv": series.get("median_iv", 0.0),
        "n_hedge_rebalances": series.get("n_hedge_rebalances", 0),
        "realized_gamma_capture_usd": series.get("realized_gamma_capture_usd", 0.0),
        "total_premium_usd": series.get("total_premium_usd", 0.0),
        "gamma_capture_over_premium": series.get("gamma_capture_over_premium", 0.0),
    }
    if len(rets) < MIN_RETURNS_PER_CONFIG:
        return {**base, "n_returns": len(rets), "error": "insufficient returns", "pass": False}

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


def _prod_1p(rets: Sequence[float]) -> float:
    eq = 1.0
    for r in rets:
        eq *= 1.0 + float(r)
        if eq <= 0.0:
            return -1.0
    return eq - 1.0


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

    # Common grid: 5m bar-ends with a closed surface snapshot available (bar_ms+300s
    # <= bar_end) falling inside the order-flow trade time range.
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

    checks = {
        "snapshots_ok": bool(n_snapshots >= MIN_SNAPSHOTS),
        "surface_instruments_ok": bool(surface_instruments >= MIN_INSTRUMENTS),
        "surface_bars_ok": bool(surface_bars_5m >= MIN_BARS),
        "trades_ok": bool(n_trades >= MIN_TRADES),
        "of_instruments_ok": bool(of_instruments >= MIN_INSTRUMENTS),
        "of_span_ok": bool(span >= MIN_SPAN_SECONDS),
        "of_bars_ok": bool(of_bars_5m >= MIN_BARS),
        "common_overlap_ok": bool(common >= MIN_COMMON_BARS),
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
        "checks": checks,
        "ok": bool(all(checks.values())),
    }


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
        "eval": "EVAL-55",
        "title": "Real Deribit options vol-surface / greeks gamma-hedged (long-gamma gamma-scalping) net-of-cost falsification",
        "capture_dir": str(capture_dir),
        "surface_to_greeks": (
            "per real 5m snapshot & chosen expiry/strike: IV backed out of real mark "
            "(implied_volatility(mark*spot, spot, K, 0, T, type)); delta/gamma from "
            "black_scholes_greeks at that IV (intrinsic-delta fallback if IV fails)"
        ),
        "structures": list(STRUCTURES),
        "expiry_choices": list(EXPIRY_CHOICES),
        "rebalance_choices": list(REBALANCE_CHOICES),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "cost_model": (
            "net-of-cost: hedge turnover HEDGE_FEE_BPS on |Δhedge|*S; long option pays "
            "half real bid/ask at entry (ask) and exit (bid)"
        ),
        "hedge_fee_bps": float(HEDGE_FEE_BPS),
        "option_spread": OPTION_SPREAD,
        "pnl": (
            "gross_k = +(dOptionUSD_k) + hedge_k*dS_k (long option, hedge=-position_delta); "
            "ret_k = (gross_k - cost_k)/S_k; decision at bar k -> outcome over [k,k+1] (causal)"
        ),
        "gamma_attribution": (
            "diagnostic: realized gamma capture = sum 0.5*Gamma_usd_k*(dS_k)^2 vs total "
            "premium paid; gamma_capture_over_premium reported per config (not a pass criterion)"
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
        },
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def _config_grid(capture: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Pre-registered config list for one capture: structures x expiries x rebalance."""
    expiries = _distinct_expiries(capture)
    grid: List[Dict[str, Any]] = []
    for structure in STRUCTURES:
        for exp_idx in EXPIRY_CHOICES:
            if exp_idx >= len(expiries):
                continue
            expiry_iso = expiries[exp_idx]
            for rebalance in REBALANCE_CHOICES:
                grid.append({
                    "structure": structure,
                    "expiry": expiry_iso,
                    "rebalance": int(rebalance),
                })
    return grid


def run_eval55(
    *,
    capture_dir: str = "data/raw/eval55",
    write: bool = True,
    task_label: str = "EVAL-55-REAL-OPTIONS-GAMMA-HEDGED-NET-OF-COST-BTC-ETH",
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
        for cfg in _config_grid(cap):
            key = f"{inst}::{cfg['structure']}::{cfg['expiry']}::reb{cfg['rebalance']}"
            try:
                res = evaluate_config(
                    cap, structure=cfg["structure"], expiry_iso=cfg["expiry"],
                    rebalance=cfg["rebalance"],
                )
            except BaseException as exc:  # noqa: BLE001
                errors.append(f"{key}: {exc!r}")
                continue
            res["config_key"] = key
            per_config.append(res)
            if res.get("n_returns", 0) >= MIN_RETURNS_PER_CONFIG:
                series = _gamma_scalp_series(
                    cap, structure=cfg["structure"], expiry_iso=cfg["expiry"],
                    rebalance=cfg["rebalance"],
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
            "best_median_iv": _finite(best.get("median_iv"), 0.0),
            "best_gamma_capture_over_premium": _finite(best.get("gamma_capture_over_premium"), 0.0),
            "any_pass": bool(any(r.get("pass") for r in rows)),
        })

    all_pass = bool(inst_summary) and all(s["any_pass"] for s in inst_summary)
    pooled_pbo = _finite(pbo.get("overall_pbo"), 0.0)
    go = bool(floor_ok and all_pass and pooled_pbo < 0.5)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = "EVAL_55_OPTIONS_GAMMA_HEDGED" if floor_ok else "EVAL_55_BLOCKED_FLOOR"

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "real Deribit options vol-surface/greeks gamma-hedged (long-gamma gamma-scalping) "
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
            "A real Deribit options vol-surface/greeks gamma-hedged long-gamma "
            "(gamma-scalping) book is net-of-cost tradable for the underlying BTC/ETH "
            "perpetual on real, synchronized Deribit data."
        ),
        "protocol": p,
        "capture_dir": str(capture_dir),
    }


def build_prereg(report: Dict[str, Any]) -> Dict[str, Any]:
    return _prereg_payload(report["generated_at"], report["capture_dir"], report["task"])


def build_prereg_md(p: Dict[str, Any]) -> str:
    proto = p["protocol"]
    lines = [
        f"# {p['prereg_id']} — EVAL-55 options vol-surface/greeks gamma-hedged net-of-cost falsification",
        "",
        f"- Generated: `{p['generated_at']}`",
        f"- Task: `{p['task']}`",
        f"- Hypothesis: {p['hypothesis']}",
        f"- Capture dir: `{p['capture_dir']}`",
        "",
        "## Pre-declared protocol",
        "",
        f"- Surface -> greeks: {proto['surface_to_greeks']}",
        f"- Structures: {proto['structures']}",
        f"- Expiry choices: {proto['expiry_choices']}",
        f"- Rebalance choices: {proto['rebalance_choices']}",
        f"- Bar grid (s): {proto['bar_seconds_grid']}",
        f"- Cost: {proto['cost_model']} (hedge {proto['hedge_fee_bps']} bps; option {proto['option_spread']})",
        f"- PnL: {proto['pnl']}",
        f"- Gamma attribution: {proto['gamma_attribution']}",
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
        "",
    ]
    return "\n".join(lines) + "\n"


def build_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {r['report_id']} — Real Deribit options vol-surface/greeks gamma-hedged net-of-cost falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        "",
        "## Per-underlying floor",
        "",
        "| underlying | snaps | surf inst | 5m bars | trades | of inst | span s | common 5m | ok |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for inst, fl in r["per_underlying_floor"].items():
        lines.append(
            f"| {inst} | {fl['n_surface_snapshots']} | {fl['n_surface_instruments']} | "
            f"{fl['n_surface_bars_5m']} | {fl['n_option_trades']} | {fl['n_of_instruments']} | "
            f"{fl['of_span_seconds']:.0f} | {fl['n_common_bars_5m']} | {fl['ok']} |"
        )
    lines += ["", "## Per-underlying (best config)", "",
              "| underlying | configs | best Sharpe | best config | best median IV | gamma capture/premium | any pass |",
              "|---|---|---|---|---|---|---|"]
    for s in r["per_underlying"]:
        lines.append(
            f"| {s['underlying']} | {s['n_configs']} | {s['best_sharpe']:.4f} | "
            f"{s['best_config']} | {s['best_median_iv']:.4f} | "
            f"{s['best_gamma_capture_over_premium']:.4f} | {s['any_pass']} |"
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
        f"# {BLOCKED_ID} — options vol-surface/greeks gamma-hedged net-of-cost (below heavy-work floor)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        "- Verdict: **BLOCKED** (measured; not NO-GO)",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Underlyings: {', '.join(r['underlyings'])}",
        f"- Floor met: {r['floor_ok']}",
        "",
        "The capture does not meet the pre-registered heavy-work floor, so no",
        "GO/NO-GO verdict is emitted. A wider/longer synchronized real Deribit",
        "capture is required.",
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
        description="EVAL-55 real Deribit options vol-surface/greeks gamma-hedged net-of-cost falsification"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval55")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--prereg-only", action="store_true",
                    help="seal EVAL_55_PREREGISTRATION from the pre-declared protocol only "
                         "(no measurement); use BEFORE the measuring run")
    ap.add_argument("--task-label",
                    default="EVAL-55-REAL-OPTIONS-GAMMA-HEDGED-NET-OF-COST-BTC-ETH")
    args = ap.parse_args(argv)

    if args.prereg_only:
        generated_at = _utc_now_iso()
        prereg = _prereg_payload(generated_at, args.capture_dir, args.task_label)
        written = _seal(PREREG_ID, prereg, build_prereg_md)
        print(json.dumps({"prereg_only": True, "artifact_paths": written}, sort_keys=True))
        return 0

    write = not args.no_write
    try:
        report = run_eval55(
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