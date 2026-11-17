#!/usr/bin/env python3
"""EVAL-82: can the **options implied-volatility surface** (EVAL-71's near-ATM
IV **level** + put-call **skew** -- the *same* signal set EVAL-72 traded) be
**monetized net-of-cost** by a signal-timed delta-hedged **BUTTERFLY** -- the
smile-**convexity** (second-moment) structure, rather than the ATM **straddle**
(EVAL-72 / EVAL-75) or the **risk reversal** (EVAL-76)?

Why this rung exists (the missing smile-decomposition traded form)
-----------------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + options order-flow + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. The runnable-now surface line
so far is:

* EVAL-71 sealed ``GO CONFIRMED`` -- the causal options implied-vol *surface*
  (near-ATM IV **level** + put-call **skew**) predicts forward realized vol;
* EVAL-73 sealed ``GO CONFIRMED (PASS)`` -- that predictiveness is stable OOS;
* EVAL-72 sealed ``NO-GO CONFIRMED (PASS)`` -- the level/skew signal does **not**
  monetize net-of-cost via a signal-timed delta-hedged **ATM straddle**;
* EVAL-75 sealed ``NO-GO CONFIRMED (PASS)`` -- the term-structure signal does not
  monetize via a signal-timed delta-hedged **ATM straddle**;
* EVAL-76 sealed ``NO-GO CONFIRMED (PASS)`` -- the skew signal does not monetize
  via a signal-timed delta-hedged **risk reversal**;
* EVAL-77 sealed ``GO CONFIRMED`` -- the cross-sectional BTC-vs-ETH basis
  predicts the BTC-minus-ETH RV spread;
* EVAL-80 sealed ``NO-GO CONFIRMED (PASS)`` -- that cross-sectional basis does
  not monetize via a two-leg relative-value straddle spread.

Every traded form above spans the *first two moments of the smile* plus the
cross-section: the **ATM straddle** is a *level / vega* (zeroth/first-moment)
structure (EVAL-72/75), the **risk reversal** is a *slope / skew* (first-moment)
structure (EVAL-76), and the **relative-value straddle spread** is a
*cross-sectional* structure (EVAL-80). The one classic smile structure none of
them trades is the **butterfly** -- the *convexity / second-moment* structure
(long the two OTM wings, short the ATM body), which isolates the *curvature* of
the smile rather than its level or slope. The genuinely distinct, on-charter,
runnable-**now** traded-form question is therefore:

    EVAL-71's surface signal is predictive of forward RV (GO). EVAL-72 showed it
    does NOT monetize net-of-cost through an ATM **straddle**. Does it monetize
    through the *butterfly* -- the smile-convexity structure -- or is the
    predictive surface non-monetizable across the full smile decomposition
    (level = straddle, slope = risk reversal, convexity = butterfly)?

This is a clean, controlled *signal -> traded-form* pairing: the **same**
EVAL-72 signal set ``{atm_iv, skew}`` and the **same** correct EVAL-62 mark-path
net-of-cost P&L, changing **only** the traded structure from the ATM straddle
(EVAL-72) to the four-leg butterfly. It is on the repo charter and runnable
**today** because it needs only the already-acquired real three-way captures
(option trade tape + surface snapshots + perp candles) -- **no new acquisition,
no network**. It does not re-litigate any sealed result:

* EVAL-57 traded a **static** VRP straddle (NO-GO);
* EVAL-61/62 traded an **options order-flow**-timed ATM straddle (NO-GO);
* EVAL-72 traded an EVAL-71 level/skew-timed ATM **straddle** (NO-GO);
* EVAL-75 traded an EVAL-74 term-structure-timed ATM **straddle** (NO-GO);
* EVAL-76 traded an EVAL-71 skew-timed **risk reversal** (NO-GO);
* EVAL-80 traded the cross-sectional basis through a **relative-value straddle
  spread** (NO-GO);
* **EVAL-82** trades the SAME EVAL-71 surface signal through a **butterfly**
  (long OTM call wing + long OTM put wing, short ATM call + short ATM put) -- a
  genuinely new traded form that isolates smile **convexity**, not level or
  slope.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
--------------------------------------------------------------------------------
For each underlying (BTC, ETH), each causal surface signal ``{atm_iv, skew}``
(EVAL-71 trailing near-ATM trade-weighted mean IV / put-minus-call IV, expanding
z-scored end-of-bar ``k``) and each bar grid ``{60s, 300s}``: build the real
**butterfly** state (front expiry; ATM body = common strike nearest spot;
upper wing = nearest OTM call; lower wing = nearest OTM put; all four legs'
IV/greeks backed out of the real mark via EVAL-57 helpers), set
``side_k = sign(z_k)`` and ``exposure_k = min(|z_k|, SIZE_CAP)``, and compute the
correct mark-path net-of-cost return (EVAL-62 ``markpath_returns``: delta-hedge +
half real 4-leg spread + hedge fee, spot-normalized) on the signed butterfly
aggregate mark/delta ``butterfly_mark = (wing_call + wing_put) - (atm_call +
atm_put)`` / ``butterfly_delta = (wing_call_delta + wing_put_delta) - (atm_call
+ atm_put)``. **GO only if, on BOTH BTC and ETH and at least one config:**
net-of-cost Sharpe > 0, no kill-switch breach (max-DD <= 0.20), directional
permutation ``p < 0.05``, block-bootstrap 95% CI lower > 0, nonzero positions >
0, and pooled BH-FDR rejects that config; else ``NO-GO CONFIRMED (PASS)`` (the
surface does not monetize net-of-cost through a butterfly either).

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
-------------------------------------------------------------------------------
EVAL-82 consumes BOTH the traded-instrument data (real surface snapshots / perp
candles / option trades) AND the surface signal data (per-bar near-ATM option
trade tape) AND requires that the four-leg butterfly be *constructible* (ATM body
+ both OTM wings priceable together). It therefore composes three honestly
pre-registered floors and requires all of them:

* the EVAL-61/62 traded-instrument floor (surface snapshots / instruments / perp
  bars / option trades / common 5m bars), reused verbatim;
* the EVAL-71 surface floor (option trades / near-ATM trades / perp candles /
  span), reused verbatim; and
* a butterfly-constructibility floor: at least
  ``min_butterfly_states_per_underlying`` per-bar states where the ATM body AND
  both OTM wings are all priceable from the real mark.

None is weakened. Below the composed floor it seals
``EVAL_82_..._BLOCKED_<UTC>`` (never a NO-GO). The EVAL-64 feasible floor that
governs the EVAL-67/68/69 ladder is untouched.

Seals ``EVAL_82_SURFACE_SKEW_BUTTERFLY_MONETIZATION_PREREGISTRATION_<UTC>`` then
``..._COMBINED_<UTC>`` (or ``..._BLOCKED_<UTC>``).
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Reuse the sealed EVAL-57/61/62 traded-form machinery, the EVAL-71 surface
# signal, and the EVAL-76 OTM-wing quote picker verbatim (no forks, no src edits).
import scripts.eval57_vrp_net_of_cost as e57  # noqa: E402
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
import scripts.eval76_surface_skew_risk_reversal_monetization as e76  # noqa: E402
from src.analytics.integrated_options_orderflow_evaluation import (  # noqa: E402
    _dsr_of_returns,
    _sharpe_of_returns,
)
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)
from src.analytics.strategy_evaluation import (  # noqa: E402
    block_bootstrap_ci,
    permutation_test,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_82_SURFACE_SKEW_BUTTERFLY_MONETIZATION_COMBINED"
PREREG_ID = "EVAL_82_SURFACE_SKEW_BUTTERFLY_MONETIZATION_PREREGISTRATION"
BLOCKED_ID = "EVAL_82_SURFACE_SKEW_BUTTERFLY_MONETIZATION_BLOCKED"

# The signal set is IDENTICAL to EVAL-72 (near-ATM IV level + put-call skew), so
# the only change versus the sealed straddle line is the traded structure.
SURFACE_SIGNALS: Tuple[str, ...] = ("atm_iv", "skew")
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)

# Stats / cost / risk constants reused verbatim from EVAL-62 (no forks).
ZWINDOW = e62.ZWINDOW
SIZE_CAP = e62.SIZE_CAP
PERMUTATION_PERMS = e62.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e62.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e62.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
KILL_SWITCH_MAX_DD = e62.KILL_SWITCH_MAX_DD
HEDGE_FEE_BPS = e62.HEDGE_FEE_BPS

# A config must produce at least this many butterfly states/returns to be
# evaluable (a result-quality guard, not a data floor).
MIN_STATES_PER_CONFIG = 100

# Composed heavy-work floor (EVAL-61/62 traded floor AND EVAL-71 surface floor
# AND a butterfly-constructibility floor; none weakened).
FLOOR: Dict[str, Any] = {
    "min_underlyings": e62.MIN_UNDERLYINGS,
    "min_butterfly_states_per_underlying": 200,
    "min_states_per_config": int(MIN_STATES_PER_CONFIG),
    "note": (
        "EVAL-82 consumes both the traded-instrument data (surface snapshots / "
        "perp candles / option trades; EVAL-61/62 floor) and the surface signal "
        "data (per-bar near-ATM option trade tape; EVAL-71 surface floor), AND it "
        "requires the four-leg butterfly (ATM body + both OTM wings) to be "
        "constructible from the real mark in >= "
        "min_butterfly_states_per_underlying per-bar states per underlying. All "
        "sealed floors are reused verbatim and must pass; none is weakened. This "
        "is NOT the EVAL-64 options-surface snapshot floor, which governs the "
        "EVAL-67/68/69 ladder and is untouched here."
    ),
}

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/integrated_options_orderflow_evaluation.py",
    "src/analytics/real_walkforward_certification.py",
    "src/analytics/strategy_evaluation.py",
    "scripts/eval57_vrp_net_of_cost.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval76_surface_skew_risk_reversal_monetization.py",
    "scripts/eval82_surface_skew_butterfly_monetization.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval82_surface_skew_butterfly_monetization.py "
    "tests/test_eval82_surface_skew_butterfly_monetization.py",
    "python3 -m pytest -q tests/test_eval82_surface_skew_butterfly_monetization.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval82_surface_skew_butterfly_monetization.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval82_surface_skew_butterfly_monetization.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL82-SURFACE-SKEW-BUTTERFLY-MONETIZATION",
)


# ---------------------------------------------------------------------------
# Small helpers (local; no src edits)
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite(x: Any, default: float = 0.0) -> float:
    return e61._finite(x, default)


def _leg_greeks(
    quote: Dict[str, Any], spot: float, state_time: datetime
) -> Optional[Dict[str, float]]:
    """Back IV + greeks out of one real option quote (EVAL-57 helper, verbatim)."""
    key = str(quote.get("option_type") or "").lower()
    return e57._iv_and_greeks(
        _finite(quote.get("mark"), 0.0),
        _finite(quote.get("bid"), 0.0),
        _finite(quote.get("ask"), 0.0),
        spot,
        _finite(quote.get("strike"), 0.0),
        quote.get("expiry"),
        state_time,
        key,
    )


# ---------------------------------------------------------------------------
# Butterfly state construction (4 legs: OTM call wing + OTM put wing - ATM body)
# ---------------------------------------------------------------------------
def build_butterfly_states(
    capture: Dict[str, Any], *, surface_signal: str, bar_seconds: float
) -> List[Dict[str, Any]]:
    """Per-bar causal butterfly states with the *surface* signal as side/exposure.

    The butterfly is the smile-convexity structure: **long** the two OTM wings
    (nearest OTM call + nearest OTM put, EVAL-76 picker) and **short** the ATM
    body (common strike nearest spot, EVAL-57 picker), all in the front expiry.
    Its aggregate mark/delta are stored under the EVAL-62 keys
    ``straddle_mark`` / ``straddle_delta`` so the sealed EVAL-62
    ``markpath_returns`` applies unchanged:

        butterfly_mark  = (wing_call_mark + wing_put_mark)
                          - (atm_call_mark  + atm_put_mark)
        butterfly_delta = (wing_call_delta + wing_put_delta)
                          - (atm_call_delta  + atm_put_delta)

    Because the long wings and short body have offsetting deltas, the butterfly
    is (near) delta-neutral by construction -- a genuinely different greek
    exposure from the ATM straddle (EVAL-72/75) and the risk reversal (EVAL-76).
    ``side_k = sign(z_k)``, ``exposure_k = min(|z_k|, SIZE_CAP)``; the hedge is
    set at ``k`` and held over ``[k, k+1]`` (strictly causal).
    """
    snapshots = sorted(
        capture.get("surface", {}).get("snapshots", []) or [],
        key=lambda s: int(s.get("bar_ms") or 0),
    )
    grid_ms = int(float(bar_seconds) * 1000)
    snap_by_bar_end: Dict[int, Tuple[float, List[Dict[str, Any]]]] = {}
    for snap in snapshots:
        bm = int(snap.get("bar_ms") or 0)
        if bm <= 0:
            continue
        be = ((bm // grid_ms) + 1) * grid_ms
        spot = _finite(snap.get("spot"), 0.0)
        quotes = snap.get("quotes") or []
        if spot > 0.0 and quotes:
            snap_by_bar_end[be] = (spot, quotes)

    # Same bar grid as EVAL-62 (perp candles -> bar_end); toxicity itself unused.
    bar_ends, _closes, _tox, _imb = e61.toxicity_per_bar(capture, bar_seconds)

    raw_by_end = e76.surface_signal_by_bar_end(
        capture, surface_signal=surface_signal, bar_seconds=bar_seconds
    )
    raw = [raw_by_end.get(int(be)) for be in bar_ends]
    filled = e71._forward_fill(raw)
    sig_z = e61.expanding_zscore(filled, ZWINDOW)

    states: List[Dict[str, Any]] = []
    for i, bar_end in enumerate(bar_ends):
        hit = snap_by_bar_end.get(int(bar_end))
        if hit is None:
            continue
        spot, quotes = hit
        bar_ms = int(bar_end) - grid_ms
        if bar_ms <= 0:
            continue
        state_time = datetime.fromtimestamp(
            (bar_ms + int(e62.BAR_SECONDS) * 1000) / 1000.0, tz=timezone.utc
        )
        exp = e62._front_expiry(quotes, state_time)
        if not exp:
            continue
        # ATM body (common strike nearest spot) and OTM wings (the strikes adjacent
        # to the BODY strike K, not to spot -- otherwise, when K sits below spot,
        # the "OTM put" would coincide with the body put and the butterfly would
        # degenerate). Reuses the sealed EVAL-76 OTM-wing picker verbatim with the
        # body strike as the reference.
        atm = e57._pick_straddle_quotes(quotes, spot, exp)
        if not atm or not atm.get("valid"):
            continue
        wings = e76._pick_risk_reversal_quotes(quotes, float(atm.get("strike", spot)), exp)
        if not wings or not wings.get("valid"):
            continue

        g_atm_c = _leg_greeks(atm["call"], spot, state_time)
        g_atm_p = _leg_greeks(atm["put"], spot, state_time)
        g_wing_c = _leg_greeks(wings["call"], spot, state_time)
        g_wing_p = _leg_greeks(wings["put"], spot, state_time)
        if g_atm_c is None or g_atm_p is None or g_wing_c is None or g_wing_p is None:
            continue

        atm_mark = _finite(atm["call"].get("mark"), 0.0) + _finite(
            atm["put"].get("mark"), 0.0
        )
        wing_mark = _finite(wings["call"].get("mark"), 0.0) + _finite(
            wings["put"].get("mark"), 0.0
        )
        butterfly_mark = wing_mark - atm_mark
        butterfly_delta = float(
            (g_wing_c["delta"] + g_wing_p["delta"])
            - (g_atm_c["delta"] + g_atm_p["delta"])
        )
        # Total 4-leg real bid/ask spread (ATM body + both wings).
        spread_usd = _finite(atm.get("spread_usd"), 0.0) + _finite(
            wings.get("spread_usd"), 0.0
        )
        if abs(butterfly_mark) <= 1e-12:
            continue

        z = float(sig_z[i]) if i < len(sig_z) else 0.0
        side = 1 if z > 1e-9 else (-1 if z < -1e-9 else 0)
        exposure = min(abs(z), SIZE_CAP) if side != 0 else 0.0
        states.append({
            "bar_ms": int(bar_ms),
            "spot": float(spot),
            "side": int(side),
            "exposure": float(exposure),
            # EVAL-62 keys, carrying the signed butterfly aggregate:
            "straddle_delta": butterfly_delta,
            "straddle_mark": float(butterfly_mark),
            "spread_usd": float(spread_usd),
            "signal_z": float(z),
            # transparency (not consumed by markpath_returns):
            "strike": float(atm.get("strike", spot)),
            "atm_strike": float(atm.get("strike", spot)),
            "strike_call": float(wings.get("strike_call", spot)),
            "strike_put": float(wings.get("strike_put", spot)),
            "structure": "butterfly",
        })
    return states


# ---------------------------------------------------------------------------
# Per-config evaluation (statistics reused verbatim from EVAL-62 / EVAL-76)
# ---------------------------------------------------------------------------
def evaluate_config(
    capture: Dict[str, Any], *, surface_signal: str, bar_seconds: float
) -> Dict[str, Any]:
    inst = capture.get("underlying", "UNKNOWN")
    states = build_butterfly_states(
        capture, surface_signal=surface_signal, bar_seconds=bar_seconds
    )
    if len(states) < MIN_STATES_PER_CONFIG:
        return {
            "underlying": inst, "signal": surface_signal,
            "bar_seconds": float(bar_seconds),
            "error": "insufficient priced butterfly states", "n_states": len(states),
            "n_returns": 0, "pass": False,
        }
    sr = e62.markpath_returns(states)
    rets = sr["returns"]
    if len(rets) < 3:
        return {
            "underlying": inst, "signal": surface_signal,
            "bar_seconds": float(bar_seconds),
            "error": "insufficient returns", "n_states": len(states),
            "n_returns": len(rets), "pass": False,
        }
    sharpe = _sharpe_of_returns(rets)
    mdd = e62._max_drawdown(rets)
    flat = [0.0] * len(rets)
    perm = permutation_test(
        rets, flat, statistic=e62._mean, n_permutations=PERMUTATION_PERMS,
        paired=True, seed=SEED,
    )
    boot = block_bootstrap_ci(
        rets, statistic=_sharpe_of_returns, n_bootstrap=BOOTSTRAP_RESAMPLES,
        block_size=BOOTSTRAP_BLOCK, seed=SEED,
    )
    wf = e62.walkforward_folds(
        rets, train=max(10, len(rets) // 3),
        test=max(10, len(rets) // 5), step=max(10, len(rets) // 5),
    )
    breach = e62.kill_switch_breach(mdd)
    perm_p = e62._finite(perm.get("p_value"), 1.0)
    ci_low = e62._finite(boot[1], 0.0)
    ci_high = e62._finite(boot[2], 0.0)
    passed = bool(
        sharpe > 0.0
        and not breach
        and perm_p < 0.05
        and ci_low > 0.0
        and sr["nonzero"] > 0,
    )
    return {
        "underlying": inst,
        "signal": surface_signal,
        "bar_seconds": float(bar_seconds),
        "n_states": len(states),
        "n_returns": len(rets),
        "nonzero_positions": sr["nonzero"],
        "n_hedge_rebalances": sr["n_hedge_rebalances"],
        "n_side_flips": sr["n_side_flips"],
        "sharpe": sharpe,
        "max_drawdown": mdd,
        "kill_switch_breach": breach,
        "permutation_p": perm_p,
        "bootstrap_ci": [boot[0], ci_low, ci_high],
        "dsr": _dsr_of_returns(rets),
        "walkforward": wf,
        "mean_return": e62._mean(rets),
        "pass": passed,
    }


# ---------------------------------------------------------------------------
# Composed heavy-work floor (EVAL-61/62 traded floor AND EVAL-71 surface floor
# AND a butterfly-constructibility floor)
# ---------------------------------------------------------------------------
def _underlying_floor(capture: Dict[str, Any], *, bar_seconds: float) -> Dict[str, Any]:
    inst = capture.get("underlying", "?")
    fl_traded = e61._underlying_floor(capture)          # surface snapshots / perp / trades
    fl_signal = e71._underlying_surface_floor(capture)  # EVAL-71 trade-tape IV floor
    n_butterfly_states = len(
        build_butterfly_states(capture, surface_signal="skew", bar_seconds=bar_seconds)
    )
    butterfly_ok = n_butterfly_states >= int(FLOOR["min_butterfly_states_per_underlying"])
    ok = bool(
        fl_traded.get("ok") and fl_signal.get("ok") and butterfly_ok
    )
    return {
        "underlying": inst,
        "traded_floor_ok": bool(fl_traded.get("ok")),
        "signal_floor_ok": bool(fl_signal.get("ok")),
        "butterfly_floor_ok": bool(butterfly_ok),
        "n_butterfly_states": int(n_butterfly_states),
        "traded_floor": fl_traded,
        "signal_floor": fl_signal,
        "checks": {
            "traded_floor_ok": bool(fl_traded.get("ok")),
            "signal_floor_ok": bool(fl_signal.get("ok")),
            "butterfly_floor_ok": bool(butterfly_ok),
        },
        "ok": ok,
    }


def campaign_floor(captures: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Composed floor: every underlying passes the EVAL-61/62 traded floor, the
    EVAL-71 surface floor, AND the butterfly-constructibility floor on the
    coarsest grid."""
    insts = sorted(captures)
    coarsest = max(GRID_BAR_SECONDS)
    per_underlying = {
        i: _underlying_floor(captures[i], bar_seconds=coarsest) for i in insts
    }
    ok = bool(
        len(insts) >= int(FLOOR["min_underlyings"])
        and per_underlying
        and all(v["ok"] for v in per_underlying.values())
    )
    return {
        "underlyings": insts,
        "per_underlying": per_underlying,
        "butterfly_floor_bar_seconds": float(coarsest),
        "checks": {
            "all_underlyings_ok": ok,
        },
        "ok": ok,
    }


# ---------------------------------------------------------------------------
# Protocol + orchestration
# ---------------------------------------------------------------------------
def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-82",
        "title": "Options implied-volatility surface (EVAL-71 near-ATM IV level + "
                 "put-call skew) -> signal-timed delta-hedged BUTTERFLY (smile-"
                 "convexity structure) with correct mark-path net-of-cost P&L: "
                 "traded-form monetization falsification on the real on-disk "
                 "three-way captures",
        "extends": "EVAL-72 (identical causal EVAL-71 surface signal set {atm_iv, "
                    "skew} and identical correct EVAL-62 mark-path net-of-cost "
                    "delta-hedged traded form) but a different, on-charter traded "
                    "structure: a four-leg BUTTERFLY (long OTM call wing + long OTM "
                    "put wing, short ATM body) that isolates smile CONVEXITY rather "
                    "than the ATM straddle's level/vega; no new acquisition",
        "supersedes": "nothing — this is the smile-convexity traded-form complement "
                      "to EVAL-72's level/skew ATM straddle (NO-GO), EVAL-75's "
                      "term-structure ATM straddle (NO-GO) and EVAL-76's skew risk "
                      "reversal (NO-GO). A butterfly (convexity) is a genuinely new "
                      "traded form; no prior rung traded it",
        "capture_dir": str(capture_dir),
        "surface_signals": list(SURFACE_SIGNALS),
        "signal_detail": "atm_iv = amount-weighted mean near-ATM iv; skew = "
                         "mean(put iv) - mean(call iv) over the trailing window "
                         "(EVAL-71 helper, reused verbatim via EVAL-76)",
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "position": "side_k = sign(z_k); exposure_k = min(|z_k|, SIZE_CAP); causal "
                    "decision at bar k; z_k = expanding-z of the causal EVAL-71 "
                    "surface signal",
        "traded_form": "butterfly (front expiry; ATM body = common strike nearest "
                       "spot; upper wing = nearest OTM call; lower wing = nearest "
                       "OTM put; all four legs' IV/greeks backed out of the real "
                       "mark via EVAL-57 helpers) with the EVAL-62 mark-path "
                       "net-of-cost P&L on the signed long-wings/short-body "
                       "aggregate mark/delta: delta-hedge + half real 4-leg spread "
                       "+ hedge fee, spot-normalized",
        "butterfly_aggregation": {
            "mark": "(wing_call_mark + wing_put_mark) - (atm_call_mark + atm_put_mark)",
            "delta": "(wing_call_delta + wing_put_delta) - (atm_call_delta + atm_put_delta)",
            "note": "long the two OTM wings, short the ATM body -> near delta-neutral "
                    "smile-convexity exposure, distinct from the straddle (level) and "
                    "risk reversal (slope)",
        },
        "zwindow": int(ZWINDOW),
        "size_cap": float(SIZE_CAP),
        "hedge_fee_bps": float(HEDGE_FEE_BPS),
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation_paired": True,
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
        },
        "kill_switch_max_dd": KILL_SWITCH_MAX_DD,
        "go_bar": (
            "GO only if, on both BTC and ETH and at least one config (signal x bar "
            "grid), net-of-cost Sharpe > 0, no kill-switch breach (max-DD <= 0.20), "
            "directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, "
            "nonzero positions > 0, and pooled BH-FDR rejects that config; else "
            "NO-GO CONFIRMED (PASS)."
        ),
        "floor": {
            "composed_of": ["EVAL-61/62 traded-instrument floor",
                            "EVAL-71 surface floor",
                            "butterfly-constructibility floor"],
            "min_underlyings": int(FLOOR["min_underlyings"]),
            "min_butterfly_states_per_underlying": int(
                FLOOR["min_butterfly_states_per_underlying"]
            ),
            "min_states_per_config": int(FLOOR["min_states_per_config"]),
            "note": FLOOR["note"],
        },
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def _select_one_capture_per_underlying(
    captures: Sequence[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Richest (most real option trades) real capture per underlying; deterministic."""
    best: Dict[str, Dict[str, Any]] = {}
    for c in captures:
        inst = str(c.get("underlying") or "?")
        score = len(c.get("option_trades", []) or [])
        if inst not in best or score > len(best[inst].get("option_trades", []) or []):
            best[inst] = c
    return [best[k] for k in sorted(best)]


def run_eval82(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL82-SURFACE-SKEW-BUTTERFLY-MONETIZATION",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    captures = {
        str(c.get("underlying")): c
        for c in _select_one_capture_per_underlying(
            e61._capture_inventory(str(capture_dir_abs))
        )
    }

    floor = campaign_floor(captures)
    floor_ok = bool(len(captures) >= int(FLOOR["min_underlyings"]) and floor["ok"])

    per_config: List[Dict[str, Any]] = []
    errors: List[str] = []
    for inst in sorted(captures):
        cap = captures[inst]
        for sig in SURFACE_SIGNALS:
            for bar_s in GRID_BAR_SECONDS:
                try:
                    res = evaluate_config(
                        cap, surface_signal=sig, bar_seconds=bar_s
                    )
                except BaseException as exc:  # noqa: BLE001
                    errors.append(f"{inst}::{sig}::bar{bar_s}: {exc!r}")
                    continue
                per_config.append(res)

    p_values = {
        f"{r['underlying']}::{r['signal']}::bar{r['bar_seconds']}":
            e62._finite(r.get("permutation_p"), 1.0)
        for r in per_config
        if r.get("n_returns", 0) > 0
    }
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}
    rejected = set(bh.get("rejected") or [])

    by_inst: Dict[str, List[Dict[str, Any]]] = {}
    for r in per_config:
        by_inst.setdefault(r["underlying"], []).append(r)

    inst_summary: List[Dict[str, Any]] = []
    for inst, rows in by_inst.items():
        valid = [r for r in rows if r.get("n_returns", 0) > 0]
        best = max(valid, key=lambda r: e62._finite(r.get("sharpe"), -1e9)) if valid else None
        pass_configs = []
        for r in valid:
            key = f"{r['underlying']}::{r['signal']}::bar{r['bar_seconds']}"
            if r.get("pass") and key in rejected:
                pass_configs.append(key)
        inst_summary.append({
            "underlying": inst,
            "n_configs": len(rows),
            "best_sharpe": e62._finite(best.get("sharpe"), 0.0) if best else 0.0,
            "best_config": (
                f"{best['signal']}::bar{best['bar_seconds']}" if best else "n/a"
            ),
            "n_pass": len(pass_configs),
            "pass_configs": pass_configs,
            "any_pass": bool(pass_configs),
        })

    all_pass = bool(inst_summary) and all(s["any_pass"] for s in inst_summary)
    go = bool(floor_ok and all_pass and len(rejected) >= 1)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = (
        "EVAL_82_SURFACE_SKEW_BUTTERFLY_MONETIZATION" if floor_ok
        else "EVAL_82_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "butterfly (smile-convexity) net-of-cost monetization of EVAL-71's "
            "predictive surface (same signal set as EVAL-72, different traded "
            "structure) on the real on-disk captures"
            if floor_ok else "capture below the composed pre-registered floor; no verdict"
        ),
        "floor_ok": bool(floor_ok),
        "capture_dir": str(capture_dir_abs),
        "underlyings": sorted(captures),
        "floor": dict(FLOOR),
        "campaign_floor": floor,
        "protocol": build_protocol(capture_dir),
        "per_config": per_config,
        "per_underlying": inst_summary,
        "pooled": {
            "bh_fdr": bh,
            "all_underlyings_pass": all_pass,
            "campaign_state": campaign_state,
        },
        "errors": errors,
    }

    if not write:
        return report

    prereg = _build_prereg(report)
    e62._seal(PREREG_ID, prereg, _build_prereg_md)

    if not floor_ok:
        e62._seal(BLOCKED_ID, _build_blocked_report(report), _build_blocked_md)
        return report

    e62._seal(REPORT_ID, report, _build_md)
    return report


# ---------------------------------------------------------------------------
# Seal artifact builders
# ---------------------------------------------------------------------------
def _build_prereg(report: Dict[str, Any]) -> Dict[str, Any]:
    p = report["protocol"]
    return {
        "prereg_id": PREREG_ID,
        "generated_at": report["generated_at"],
        "task": report["task"],
        "hypothesis": (
            "The causal options implied-volatility surface (EVAL-71 near-ATM IV level "
            "and put-call skew) can be monetized net-of-cost by a signal-timed delta-"
            "hedged BUTTERFLY (long OTM call wing + long OTM put wing, short ATM body) "
            "on the BTC/ETH perpetual -- the smile-convexity traded form -- on the "
            "already-acquired real on-disk captures at the composed floor."
        ),
        "extends": p["extends"],
        "protocol": p,
        "capture_dir": report["capture_dir"],
    }


def _build_prereg_md(r: Dict[str, Any]) -> str:
    p = r["protocol"]
    fl = p["floor"]
    lines = [
        f"# {PREREG_ID} — surface -> signal-timed delta-hedged butterfly "
        f"(smile-convexity) net-of-cost monetization falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Hypothesis: {r['hypothesis']}",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Extends: {p['extends']}",
        "",
        "## Pre-declared protocol",
        "",
        f"- Surface signals: {p['surface_signals']}",
        f"- Signal detail: {p['signal_detail']}",
        f"- Bar grid (s): {p['bar_seconds_grid']}",
        f"- Position: {p['position']}",
        f"- Traded form: {p['traded_form']}",
        f"- Butterfly aggregation: mark = {p['butterfly_aggregation']['mark']}; "
        f"delta = {p['butterfly_aggregation']['delta']}",
        f"- Stats: perm {p['stats']['permutation_perms']} ({p['stats']['permutation_paired']}) / "
        f"bootstrap {p['stats']['bootstrap_resamples']} block {p['stats']['bootstrap_block']} / "
        f"BH-FDR alpha {p['stats']['fdr_alpha']} / seed {p['stats']['seed']} / "
        f"zwindow {p['zwindow']} / size_cap {p['size_cap']}",
        f"- Kill-switch max-DD: {p['kill_switch_max_dd']}",
        "",
        "## Pre-declared GO bar",
        "",
        p["go_bar"],
        "",
        "## Pre-registered composed floor (all sealed floors + butterfly constructibility; none weakened)",
        "",
        f"- {fl['note']}",
        f"- Composed of: {fl['composed_of']}",
        f"- Min underlyings: {fl['min_underlyings']}",
        f"- Min butterfly states per underlying: {fl['min_butterfly_states_per_underlying']}",
        f"- Min states per config: {fl['min_states_per_config']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    fl = r["campaign_floor"]
    lines = [
        f"# {r['report_id']} — surface -> signal-timed delta-hedged butterfly "
        f"(smile-convexity) net-of-cost monetization falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        "",
        "## Per-underlying floor (composed)",
        "",
        "| underlying | traded floor ok | surface floor ok | butterfly states | butterfly ok | ok |",
        "|---|---|---|---|---|---|",
    ]
    for inst, u in fl["per_underlying"].items():
        lines.append(
            f"| {inst} | {u['traded_floor_ok']} | {u['signal_floor_ok']} | "
            f"{u['n_butterfly_states']} | {u['butterfly_floor_ok']} | {u['ok']} |"
        )
    lines += ["", "## Per-underlying (best config by Sharpe)", "",
              "| underlying | configs | best Sharpe | best config | n pass | any pass |",
              "|---|---|---|---|---|---|"]
    for s in r["per_underlying"]:
        lines.append(
            f"| {s['underlying']} | {s['n_configs']} | {s['best_sharpe']:.4f} | "
            f"{s['best_config']} | {s['n_pass']} | {s['any_pass']} |"
        )
    lines += ["", "## Pooled", "",
              f"- BH-FDR rejected: {r['pooled']['bh_fdr'].get('rejected')}",
              f"- All underlyings pass: {r['pooled']['all_underlyings_pass']}",
              f"- Campaign state: {r['pooled']['campaign_state']}"]
    if r["errors"]:
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def _build_blocked_report(r: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "report_id": BLOCKED_ID,
        "generated_at": r["generated_at"],
        "task": r["task"],
        "verdict": "BLOCKED",
        "capture_dir": r["capture_dir"],
        "underlyings": r["underlyings"],
        "campaign_floor": r["campaign_floor"],
        "floor": r["floor"],
        "floor_ok": r["floor_ok"],
        "errors": r.get("errors", []),
    }


def _build_blocked_md(r: Dict[str, Any]) -> str:
    fl = r["campaign_floor"]
    lines = [
        f"# {BLOCKED_ID} — surface -> signal-timed delta-hedged butterfly "
        f"(below the composed pre-registered floor)",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        "- Verdict: **BLOCKED** (measured; not NO-GO)",
        f"- Capture dir: `{r.get('capture_dir')}`",
        f"- Underlyings: {', '.join(r.get('underlyings', []))}",
        "",
        "The capture does not meet the composed EVAL-61/62 + EVAL-71 + butterfly-"
        "constructibility floor, so no GO/NO-GO verdict is emitted. Do NOT weaken any "
        "floor, do NOT use synthetic data, and do NOT emit NO-GO on under-floor data.",
        "",
        "## Per-underlying floor",
        "",
    ]
    for inst, u in (fl.get("per_underlying") or {}).items():
        lines.append(
            f"- {inst}: traded_floor_ok={u.get('traded_floor_ok')} "
            f"signal_floor_ok={u.get('signal_floor_ok')} "
            f"butterfly_floor_ok={u.get('butterfly_floor_ok')} "
            f"n_butterfly_states={u.get('n_butterfly_states')}"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-82: surface-skew-timed delta-hedged butterfly (smile-"
                    "convexity) net-of-cost monetization falsification on the real "
                    "on-disk captures"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument(
        "--task-label", default="EVAL82-SURFACE-SKEW-BUTTERFLY-MONETIZATION"
    )
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval82(
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
                "campaign_floor": {},
                "floor": dict(FLOOR),
                "floor_ok": False,
                "errors": [repr(exc)],
            })
            e62._seal(BLOCKED_ID, blocked, _build_blocked_md)
        return 1

    print(json.dumps({
        "verdict": report.get("verdict"),
        "floor_ok": report.get("floor_ok"),
        "underlyings": report.get("underlyings"),
        "per_underlying": report.get("per_underlying"),
        "bh_fdr_rejected": report.get("pooled", {}).get("bh_fdr", {}).get("rejected"),
        "n_configs": len(report.get("per_config", [])),
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())