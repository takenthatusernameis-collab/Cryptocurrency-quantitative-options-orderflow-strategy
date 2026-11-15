#!/usr/bin/env python3
"""EVAL-57: real Deribit **options vol-surface / greeks -> volatility risk premium
(VRP) / realized-vs-implied vol net-of-cost P&L** falsification on BTC and ETH.

The repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is a quantitative **options** + orderflow strategy evaluated **net of cost**. Every
options+orderflow *fusion* cell (EVAL-46..53) and the options greeks ladder rungs
EVAL-54 (delta-hedged short-vol), EVAL-55 (long-gamma gamma-scalping) and EVAL-56
(term-structure calendar-spread) are sealed ``NO-GO CONFIRMED (PASS)``; re-litigating
fused options+orderflow or EVAL-54/55/56 is prohibited. The unmeasured heavy rung per
the charter is **real options pricing / greeks / vol-surface -> net-of-cost
evaluation**. EVAL-57 is the *volatility risk premium* pure options-native campaign:
it backs real IV out of Deribit option marks at a common ATM strike, compares to
realized vol of the perpetual over a pre-registered lookback, and holds a
delta-hedged straddle in the perpetual sized by the IV-realized-vol spread
(long vol when IV understates realized, short vol when IV overstates realized),
profiting net of cost only if the VRP spread predicts the realized/implied gap
well enough to cover execution costs -- distinct from EVAL-54's short-vol
delta-hedging, EVAL-55's long-gamma gamma-scalping and EVAL-56's term-structure
calendar spread, and requiring fresh real data (Deribit option trades are ~24h-capped).

Strictly additive: it consumes only the measured capture JSON files under
``--capture-dir`` and reuses the sealed pricing/greeks engine
(``src/features/options_pricing.py``) plus the sealed statistics helpers
(``_sharpe_of_returns``, ``_dsr_of_returns``, ``_cscv_pbo``, ``_benjamini_hochberg``,
``block_bootstrap_ci``, ``permutation_test``). It never re-runs a prior EVAL and never
edits ``src/`` or the sealed EVAL-02..56 scripts/tests/artifacts.

Pre-declared protocol (identical for every underlying; no curve fitting):
  * the underlying perpetual 1m candles are resampled to a 300s grid; each real 5m
    surface snapshot is treated as an end-of-bar state (its ``spot`` is the causal
    perpetual close at that bar end);
  * **real vol surface -> IV**: for the front expiry at a **common strike** nearest
    spot (quoted call+put; if none the config is invalid -- never fabricate), each
    option's implied vol is backed out of its *real* mark
    (``implied_volatility(mark*spot, spot, K, 0, T, type)``) and ``delta``/``gamma``
    come from ``black_scholes_greeks`` at that IV; series IV = mean(call IV, put IV);
  * **realized vol**: annualized std of 5m log returns of the perpetual close over a
    pre-registered lookback window, causal (decision at bar k uses realized vol over
    bars ending at k);
  * **VRP book** (pre-registered, fixed, no fitting): at each state, VRP spread =
    series_IV - realized_vol. Position: LONG ATM straddle when spread < 0 (buy vol:
    IV understates realized), SHORT ATM straddle when spread > 0 (sell vol: IV
    overstates realized), flat when spread == 0. Exposure =
    clip(|spread| / VOL_TARGET, 0, SIZE_CAP) (pre-registered constants, no fitting).
    Net position delta = side * exposure * straddle_delta_sum; delta-hedged in the
    perpetual by holding ``hedge = -net_position_delta`` units of the underlying;
  * per-step (causal, decision at bar ``k`` -> outcome over ``[k, k+1]``) net-of-cost
    P&L in USD per 1-unit underlying notional:
      ``dOption_k = side_k * exposure_k * (straddle_mark_{k+1} - straddle_mark_k) * S_k``
      ``gross_k = dOption_k + hedge_k * dS_k``
      ``cost_k  = HEDGE_FEE_BPS * |hedge_k - hedge_{k-1}| * S_k / 1e4
                 + entry spread (half, at k=0) + exit spread (half, at last step)
                 + flip spread (full, when side changes between steps)``
      ``ret_k   = (gross_k - cost_k) / S_k``;
  * full-series (causal -> out-of-sample) plus rolling walk-forward Sharpe / max-DD;
  * stats: 1000-perm paired permutation (strategy vs flat), 1000-resample block
    bootstrap CI on Sharpe (block 2), CSCV PBO across the pre-registered grid
    (k=4), BH-FDR (alpha 0.1), DSR; seed 42.

Pre-declared GO bar (conservative; the ladder EVAL-46..56 is CLOSED so NO-GO is the
default and GO needs strong evidence): GO only if, on **both** BTC and ETH and
**at least one** grid config, net-of-cost Sharpe > 0, no kill-switch breach
(max-DD <= 0.20), permutation p < 0.05, bootstrap 95% CI lower bound > 0, and pooled
PBO < 0.5. Otherwise ``NO-GO CONFIRMED (PASS)``.

Heavy-work floor (per underlying): surface >=100 snapshots / >=50 instruments /
>=240 5m bars; options order flow >=2000 trades / >=50 instruments / >=240 bars /
>=79200 s span; legs overlap on >=240 common 5m bars -- **plus** the term-structure
leg viable (>=2 distinct expiries each with a common strike nearest spot present in
>=100 snapshots). Below floor seals a measured ``EVAL_57_BLOCKED_<UTC>`` (never a
NO-GO). Refuses to seal a verdict unless every underlying independently clears the
floor and the roster has >=2 underlyings.

Seal ``EVAL_57_PREREGISTRATION_<UTC>.{json,md}`` (before measurement) then
``EVAL_57_COMBINED_<UTC>.{json,md}`` (or ``EVAL_57_BLOCKED_<UTC>``).
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
REPORT_ID = "EVAL_57_COMBINED"
PREREG_ID = "EVAL_57_PREREGISTRATION"
BLOCKED_ID = "EVAL_57_BLOCKED"

BAR_SECONDS = 300.0
HEDGE_FEE_BPS = 5.0          # taker fee + impact on delta-hedge turnover
OPTION_SPREAD = ("each of the 2 straddle legs pays half its real bid/ask at entry "
                 "and half at exit (long and short legs both charged the round-trip "
                 "spread); full spread charged when the VRP side flips between steps")
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

# VRP pre-registered constants (no fitting).
VOL_TARGET = 0.5        # exposure = clip(|IV - realized| / VOL_TARGET, 0, SIZE_CAP)
SIZE_CAP = 1.0          # max straddle exposure (1.0 = 1-unit straddle notional)
ANNUALIZATION = math.sqrt(365.25 * 24 * 12)   # 5m bars per year

# Heavy-work floor (per underlying) — identical to the sealed EVAL-52/54/55/56 floor,
# plus the term-structure viability requirement.
MIN_SNAPSHOTS = 100
MIN_BARS = 240
MIN_INSTRUMENTS = 50
MIN_TRADES = 2000
MIN_SPAN_SECONDS = 79200.0
MIN_COMMON_BARS = 240
MIN_UNDERLYINGS = 2

# VRP structures: single-expiry ATM straddle, long/short sized by VRP spread.
STRUCTURES: Tuple[str, ...] = ("vrp_straddle_delta_hedged",)
# Pre-registered lookback (5m bars) for realized vol and vol-target grid.
LOOKBACK_BARS: Tuple[int, ...] = (12, 24, 48)       # 1h / 2h / 4h
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
    "scripts/eval56_acquire_options_surface.py",
    "scripts/eval56_term_structure_calendar_net_of_cost.py",
    "scripts/eval57_acquire_options_surface.py",
    "scripts/eval57_vrp_net_of_cost.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval57_acquire_options_surface.py "
    "scripts/eval57_vrp_net_of_cost.py "
    "tests/test_eval57_vrp_net_of_cost.py",
    "python3 -m pytest -q tests/test_eval57_vrp_net_of_cost.py",
    "python3 scripts/eval57_acquire_options_surface.py "
    "--underlying BTC --underlying ETH --days 1 --out-dir data/raw/eval57 --seal",
    "python3 scripts/eval57_vrp_net_of_cost.py --prereg-only",
    "python3 scripts/eval57_vrp_net_of_cost.py --no-write --capture-dir data/raw/eval57",
    "python3 scripts/eval57_vrp_net_of_cost.py --capture-dir data/raw/eval57",
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
# Straddle quote selection (common strike, single expiry, nearest to spot)
# ---------------------------------------------------------------------------
def _pick_straddle_quotes(
    quotes: Sequence[Dict[str, Any]], spot: float, expiry: str,
) -> Optional[Dict[str, Any]]:
    """Select a **common strike** (call+put both quoted) nearest to spot in a single
    expiry.

    Returns ``{"call": q, "put": q, "strike": K, "spread_usd": total 2-leg spread}``
    or ``None`` when no valid common strike exists (never fabricates).
    """
    want = str(expiry)[:10]
    pool: Dict[float, Dict[str, List[Dict[str, Any]]]] = {}
    for q in quotes:
        exp = _expiry_date(q.get("expiry"))
        if exp != want:
            continue
        try:
            strike = float(q.get("strike") or 0.0)
            mark = float(q.get("mark") or 0.0)
        except (TypeError, ValueError):
            continue
        if strike <= 0.0 or mark <= 0.0:
            continue
        ot = str(q.get("option_type") or "").lower()
        if ot not in ("call", "put"):
            continue
        pool.setdefault(strike, {"call": [], "put": []})
        pool[strike][ot].append(q)

    common = [s for s in pool if pool[s]["call"] and pool[s]["put"]]
    if not common:
        return None
    strike = min(common, key=lambda s: abs(s - spot))
    call = min(pool[strike]["call"], key=lambda q: abs(float(q.get("strike") or 0.0) - spot))
    put = min(pool[strike]["put"], key=lambda q: abs(float(q.get("strike") or 0.0) - spot))

    def leg_spread(leg: Dict[str, Any]) -> float:
        return (_finite(leg.get("ask"), 0.0) - _finite(leg.get("bid"), 0.0)) * spot

    spread_usd = leg_spread(call) + leg_spread(put)
    return {
        "call": call, "put": put, "strike": float(strike),
        "valid": True, "spread_usd": float(spread_usd),
    }


# ---------------------------------------------------------------------------
# Realized vol of the perpetual (causal, 5m grid)
# ---------------------------------------------------------------------------
def _perp_5m_closes(
    perp_candles: Sequence[Dict[str, Any]], bar_seconds: float,
) -> List[Tuple[int, float]]:
    """Resample 1m perp candles to 5m closes at bar-end boundaries."""
    bar_ms = int(float(bar_seconds) * 1000)
    closes: Dict[int, float] = {}
    for c in perp_candles:
        ts = int(c.get("ts") or 0)
        px = _finite(c.get("close"), 0.0)
        if ts <= 0 or px <= 0:
            continue
        be = ((ts // bar_ms) + 1) * bar_ms
        closes[be] = px  # last close in the bar wins
    return sorted(closes.items())


def _realized_vol_at(
    closes: List[Tuple[int, float]], idx: int, lookback_bars: int,
) -> Optional[float]:
    """Annualized std of 5m log returns over the lookback window ending at ``idx``."""
    if idx < lookback_bars or lookback_bars < 2:
        return None
    rets: List[float] = []
    for j in range(idx - lookback_bars + 1, idx + 1):
        p0 = closes[j - 1][1]
        p1 = closes[j][1]
        if p0 > 0.0 and p1 > 0.0:
            rets.append(math.log(p1 / p0))
    if len(rets) < 2:
        return None
    m = sum(rets) / len(rets)
    var = sum((r - m) ** 2 for r in rets) / (len(rets) - 1)
    if var <= 0.0:
        return 0.0
    return math.sqrt(var) * ANNUALIZATION


# ---------------------------------------------------------------------------
# VRP straddle book construction (causal, net of cost)
# ---------------------------------------------------------------------------
def _vrp_series(
    capture: Dict[str, Any],
    *,
    expiry: str,
    lookback_bars: int,
    vol_target: float,
    size_cap: float,
    rebalance: int,
) -> Dict[str, Any]:
    """Long/short ATM straddle sized by the VRP spread, delta-hedged in the perp.

    Walks the real 5m surface snapshots in ascending time; each snapshot is an
    end-of-bar state; the hedge set at state ``k`` is held over ``[k, k+1]`` so the
    P&L is strictly causal.

    At each state: back out series IV from the real call+put marks at the common
    strike nearest spot in the front expiry; compute causal realized vol of the
    perpetual over ``lookback_bars``; VRP spread = series_IV - realized_vol.
    Position side = +1 (long straddle) when spread < 0 (buy vol), -1 (short straddle)
    when spread > 0 (sell vol), 0 (flat) when spread == 0. Exposure =
    clip(|spread| / vol_target, 0, size_cap). Net position delta =
    side * exposure * straddle_delta_sum; hedge = -net position delta in the perp.

    LONG straddle pays ask at entry / receives bid at exit; SHORT straddle receives
    bid at entry / pays ask at exit. A side flip between consecutive steps charges
    the full 2-leg spread. Hedge turnover charged at HEDGE_FEE_BPS.
    Returns per-step net-of-cost returns on 1-unit underlying notional plus
    diagnostics.
    """
    snapshots = sorted(
        capture.get("surface", {}).get("snapshots", []) or [],
        key=lambda s: int(s.get("bar_ms") or 0),
    )
    perp_closes = _perp_5m_closes(capture.get("perp_candles", []) or [], BAR_SECONDS)

    # Map bar_ms -> index in the 5m close series for realized-vol lookups.
    close_by_bar = {int(ts): px for ts, px in perp_closes}
    close_ts_sorted = [ts for ts, _ in perp_closes]

    states: List[Dict[str, Any]] = []
    for snap in snapshots:
        bar_ms = int(snap.get("bar_ms") or 0)
        if bar_ms <= 0:
            continue
        spot = _finite(snap.get("spot"), 0.0)
        if spot <= 0.0:
            continue
        quotes = snap.get("quotes") or []
        pick = _pick_straddle_quotes(quotes, spot, expiry)
        if not pick or not pick.get("valid"):
            continue
        state_time = datetime.fromtimestamp(
            (bar_ms + int(BAR_SECONDS) * 1000) // 1000, tz=timezone.utc,
        )
        legs: List[Dict[str, float]] = []
        ok = True
        for key in ("call", "put"):
            q = pick[key]
            g = _iv_and_greeks(
                _finite(q.get("mark"), 0.0), _finite(q.get("bid"), 0.0),
                _finite(q.get("ask"), 0.0), spot, _finite(q.get("strike"), 0.0),
                q.get("expiry"), state_time,
                str(q.get("option_type") or key).lower(),
            )
            if g is None:
                ok = False
                break
            legs.append({"key": key, **g})
        if not ok or not legs:
            continue
        straddle_delta = sum(l["delta"] for l in legs)
        straddle_gamma = sum(l["gamma"] for l in legs)
        straddle_mark = sum(_finite(q.get("mark"), 0.0) for q in (pick["call"], pick["put"]))
        iv = _mean([l["iv"] for l in legs if math.isfinite(l["iv"])])
        if not math.isfinite(iv) or iv <= 0.0:
            continue

        # Realized vol at this state (causal: lookback bars ending at this bar).
        # Perp closes are keyed by bar end (bar_ms + BAR_SECONDS); match on that.
        target_bar_end = bar_ms + int(BAR_SECONDS) * 1000
        try:
            idx = close_ts_sorted.index(target_bar_end)
        except ValueError:
            idx = -1
        realized = _realized_vol_at(perp_closes, idx, lookback_bars) if idx >= 0 else None
        if realized is None or not math.isfinite(realized) or realized <= 0.0:
            continue

        spread = iv - realized
        side = 1 if spread < 0.0 else (-1 if spread > 0.0 else 0)
        exposure = min(abs(spread) / vol_target, size_cap) if vol_target > 0 else 0.0
        if side == 0 or exposure <= 0.0:
            side = 0
            exposure = 0.0

        states.append({
            "state_time": state_time.isoformat(),
            "bar_ms": bar_ms,
            "spot": spot,
            "side": int(side),
            "exposure": float(exposure),
            "straddle_delta": float(straddle_delta),
            "straddle_gamma": float(straddle_gamma),
            "straddle_mark": float(straddle_mark),
            "spread_usd": float(pick.get("spread_usd", 0.0)),
            "iv": float(iv),
            "realized": float(realized),
            "vrp_spread": float(spread),
            "strike": float(pick.get("strike", spot)),
        })

    n = len(states)
    if n < 2:
        return {
            "structure": "vrp_straddle_delta_hedged",
            "expiry": expiry, "lookback_bars": int(lookback_bars),
            "vol_target": float(vol_target), "size_cap": float(size_cap),
            "rebalance": int(rebalance),
            "n_states": n, "returns": [], "error": "insufficient priced states",
            "valid": False,
        }

    rebalance = max(1, int(rebalance))
    vol_target = float(vol_target)
    size_cap = float(size_cap)

    # Causal net-of-cost walk.
    returns: List[float] = []
    gross_list: List[float] = []
    cost_list: List[float] = []
    n_rebalances = 0
    n_flips = 0
    prev_side = 0
    prev_hedge = 0.0
    prev_spread_usd = 0.0

    for k in range(n - 1):
        s0 = float(states[k]["spot"])
        s1 = float(states[k + 1]["spot"])
        if s0 <= 0.0:
            returns.append(0.0); gross_list.append(0.0); cost_list.append(0.0); continue
        d_spot = s1 - s0

        side = int(states[k]["side"])
        exposure = float(states[k]["exposure"])
        straddle_delta = float(states[k]["straddle_delta"])
        straddle_mark = float(states[k]["straddle_mark"])
        spread_usd = float(states[k]["spread_usd"])

        # Position delta = side * exposure * straddle_delta; hedge = -position delta.
        if k % rebalance == 0:
            hedge = -float(side) * exposure * straddle_delta
        else:
            hedge = prev_hedge
        if hedge != prev_hedge:
            n_rebalances += 1

        # Option mark-to-market P&L for [k, k+1]: position held constant over the step.
        next_mark = float(states[k + 1]["straddle_mark"])
        d_option = float(side) * exposure * (next_mark - straddle_mark) * s0
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
        prev_spread_usd = spread_usd

    total_premium_usd = float(states[0]["straddle_mark"]) * float(states[0]["exposure"]) if states else 0.0
    median_iv = _finite(_median([s["iv"] for s in states if math.isfinite(s["iv"])]), 0.0)
    median_realized = _finite(_median([s["realized"] for s in states if math.isfinite(s["realized"])]), 0.0)
    mean_vrp_spread = _mean([s["vrp_spread"] for s in states])

    return {
        "structure": "vrp_straddle_delta_hedged",
        "expiry": expiry, "lookback_bars": int(lookback_bars),
        "vol_target": vol_target, "size_cap": size_cap, "rebalance": int(rebalance),
        "n_states": n, "n_returns": len(returns),
        "n_hedge_rebalances": int(n_rebalances), "n_side_flips": int(n_flips),
        "median_iv": median_iv,
        "median_realized_vol": median_realized,
        "mean_vrp_spread": float(mean_vrp_spread),
        "entry_spread_usd": 0.5 * float(states[0]["spread_usd"]) * float(states[0]["exposure"]),
        "exit_spread_usd": 0.5 * float(states[-1]["spread_usd"]) * float(states[-1]["exposure"]),
        "total_premium_usd": total_premium_usd,
        "strike": float(states[0]["strike"]),
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
    lookback_bars: int,
    vol_target: float,
    size_cap: float,
    rebalance: int,
) -> Dict[str, Any]:
    inst = capture.get("underlying", "UNKNOWN")
    series = _vrp_series(
        capture, expiry=expiry, lookback_bars=lookback_bars,
        vol_target=vol_target, size_cap=size_cap, rebalance=rebalance,
    )
    rets = series.get("returns", [])
    base = {
        "underlying": inst,
        "structure": structure,
        "expiry": expiry, "lookback_bars": int(lookback_bars),
        "vol_target": float(vol_target), "size_cap": float(size_cap),
        "rebalance": int(rebalance),
        "bar_seconds": BAR_SECONDS,
        "n_states": series.get("n_states", 0),
        "median_iv": series.get("median_iv", 0.0),
        "median_realized_vol": series.get("median_realized_vol", 0.0),
        "mean_vrp_spread": series.get("mean_vrp_spread", 0.0),
        "n_hedge_rebalances": series.get("n_hedge_rebalances", 0),
        "n_side_flips": series.get("n_side_flips", 0),
        "strike": series.get("strike", 0.0),
        "entry_spread_usd": series.get("entry_spread_usd", 0.0),
        "exit_spread_usd": series.get("exit_spread_usd", 0.0),
        "total_premium_usd": series.get("total_premium_usd", 0.0),
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

    # Term-structure viability: >=2 distinct expiries each with a common strike
    # nearest spot present in >=100 snapshots.
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
        "eval": "EVAL-57",
        "title": "Real Deribit options vol-surface/greeks volatility risk premium / "
                 "realized-vs-implied vol net-of-cost falsification",
        "capture_dir": str(capture_dir),
        "surface_to_iv": (
            "per real 5m snapshot & front expiry at a common strike nearest spot: "
            "series IV = mean(call IV, put IV), each backed out of each real mark "
            "(implied_volatility(mark*spot, spot, K, 0, T, type))"
        ),
        "structures": list(STRUCTURES),
        "lookback_bars": [int(b) for b in LOOKBACK_BARS],
        "vol_target": float(VOL_TARGET),
        "size_cap": float(SIZE_CAP),
        "rebalance_choices": list(REBALANCE_CHOICES),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "cost_model": (
            "net-of-cost: hedge turnover HEDGE_FEE_BPS on |Δhedge|*S; each of the 2 "
            "straddle legs pays half its real bid/ask at entry and half at exit; "
            "full spread charged on VRP side flips"
        ),
        "hedge_fee_bps": float(HEDGE_FEE_BPS),
        "option_spread": OPTION_SPREAD,
        "pnl": (
            "dOption_k = side_k*exposure_k*(straddle_mark_{k+1}-straddle_mark_k)*S_k; "
            "gross_k = dOption_k + hedge_k*dS_k (hedge = -side*exposure*straddle_delta); "
            "ret_k = (gross_k - cost_k)/S_k; decision at bar k -> outcome over [k,k+1] (causal)"
        ),
        "vrp_rule": (
            "side = +1 (long straddle) when IV < realized (buy vol), "
            "-1 (short straddle) when IV > realized (sell vol), 0 when equal; "
            "exposure = clip(|IV - realized| / vol_target, 0, size_cap)"
        ),
        "common_strike_rule": (
            "nearest-to-spot strike quoted call+put in the front expiry; "
            "else config invalid"
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
    """Pre-registered config list: structures x front expiry x lookback x
    vol_target x size_cap x rebalance."""
    expiries = _distinct_expiries(capture)
    grid: List[Dict[str, Any]] = []
    if len(expiries) < 1:
        return grid
    front_expiry = expiries[0]
    for structure in STRUCTURES:
        for lookback in LOOKBACK_BARS:
            for vol_target in (0.5, 1.0):
                for size_cap in (0.5, 1.0):
                    for rebalance in REBALANCE_CHOICES:
                        grid.append({
                            "structure": structure,
                            "expiry": front_expiry,
                            "lookback_bars": int(lookback),
                            "vol_target": float(vol_target),
                            "size_cap": float(size_cap),
                            "rebalance": int(rebalance),
                        })
    return grid


def run_eval57(
    *,
    capture_dir: str = "data/raw/eval57",
    write: bool = True,
    task_label: str = "EVAL-57-REAL-OPTIONS-VOL-RISK-PREMIUM-REALIZED-VS-IMPLIED-NET-OF-COST-BTC-ETH",
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
            key = (f"{inst}::{cfg['structure']}::{cfg['expiry']}::lb{cfg['lookback_bars']}"
                   f"::vt{cfg['vol_target']}::sc{cfg['size_cap']}::reb{cfg['rebalance']}")
            try:
                res = evaluate_config(
                    cap, structure=cfg["structure"], expiry=cfg["expiry"],
                    lookback_bars=cfg["lookback_bars"], vol_target=cfg["vol_target"],
                    size_cap=cfg["size_cap"], rebalance=cfg["rebalance"],
                )
            except BaseException as exc:  # noqa: BLE001
                errors.append(f"{key}: {exc!r}")
                continue
            res["config_key"] = key
            per_config.append(res)
            if res.get("n_returns", 0) >= MIN_RETURNS_PER_CONFIG:
                series = _vrp_series(
                    cap, expiry=cfg["expiry"], lookback_bars=cfg["lookback_bars"],
                    vol_target=cfg["vol_target"], size_cap=cfg["size_cap"],
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
            "best_median_realized_vol": _finite(best.get("median_realized_vol"), 0.0),
            "best_mean_vrp_spread": _finite(best.get("mean_vrp_spread"), 0.0),
            "best_strike": _finite(best.get("strike"), 0.0),
            "any_pass": bool(any(r.get("pass") for r in rows)),
        })

    all_pass = bool(inst_summary) and all(s["any_pass"] for s in inst_summary)
    pooled_pbo = _finite(pbo.get("overall_pbo"), 0.0)
    go = bool(floor_ok and all_pass and pooled_pbo < 0.5)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = "EVAL_57_OPTIONS_VRP_REALIZED_VS_IMPLIED" if floor_ok else "EVAL_57_BLOCKED_FLOOR"

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "real Deribit options vol-surface/greeks volatility risk premium / "
            "realized-vs-implied vol net-of-cost falsification"
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
            "A real Deribit options vol-surface/greeks volatility risk premium trade "
            "(long/short ATM straddle sized by the IV-realized-vol spread, "
            "delta-hedged in the perpetual) is net-of-cost tradable for the "
            "underlying BTC/ETH perpetual on real, synchronized Deribit data."
        ),
        "protocol": p,
        "capture_dir": str(capture_dir),
    }


def build_prereg(report: Dict[str, Any]) -> Dict[str, Any]:
    return _prereg_payload(report["generated_at"], report["capture_dir"], report["task"])


def build_prereg_md(p: Dict[str, Any]) -> str:
    proto = p["protocol"]
    lines = [
        f"# {p['prereg_id']} — EVAL-57 options vol-surface/greeks VRP / realized-vs-implied vol net-of-cost falsification",
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
        f"- Lookback bars (realized vol): {proto['lookback_bars']}",
        f"- Vol target: {proto['vol_target']}; size cap: {proto['size_cap']}",
        f"- Rebalance choices: {proto['rebalance_choices']}",
        f"- Bar grid (s): {proto['bar_seconds_grid']}",
        f"- Cost: {proto['cost_model']} (hedge {proto['hedge_fee_bps']} bps; {proto['option_spread']})",
        f"- PnL: {proto['pnl']}",
        f"- VRP rule: {proto['vrp_rule']}",
        f"- Common strike rule: {proto['common_strike_rule']}",
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
        f"# {r['report_id']} — Real Deribit options vol-surface/greeks VRP / realized-vs-implied vol net-of-cost falsification",
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
              "| underlying | configs | best Sharpe | best config | best median IV | best median realized | best mean VRP spread | best strike | any pass |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for s in r["per_underlying"]:
        lines.append(
            f"| {s['underlying']} | {s['n_configs']} | {s['best_sharpe']:.4f} | "
            f"{s['best_config']} | {s['best_median_iv']:.4f} | {s['best_median_realized_vol']:.4f} | "
            f"{s['best_mean_vrp_spread']:.4f} | {s['best_strike']:.2f} | {s['any_pass']} |"
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
        f"# {BLOCKED_ID} — options vol-surface/greeks VRP / realized-vs-implied vol net-of-cost (below heavy-work floor)",
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
        description="EVAL-57 real Deribit options vol-surface/greeks VRP / realized-vs-implied vol net-of-cost falsification"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval57")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--prereg-only", action="store_true",
                    help="seal EVAL_57_PREREGISTRATION from the pre-declared protocol only "
                         "(no measurement); use BEFORE the measuring run")
    ap.add_argument("--task-label",
                    default="EVAL-57-REAL-OPTIONS-VOL-RISK-PREMIUM-REALIZED-VS-IMPLIED-NET-OF-COST-BTC-ETH")
    args = ap.parse_args(argv)

    if args.prereg_only:
        generated_at = _utc_now_iso()
        prereg = _prereg_payload(generated_at, args.capture_dir, args.task_label)
        written = _seal(PREREG_ID, prereg, build_prereg_md)
        print(json.dumps({"prereg_only": True, "artifact_paths": written}, sort_keys=True))
        return 0

    write = not args.no_write
    try:
        report = run_eval57(
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
