#!/usr/bin/env python3
"""EVAL-80: can the **cross-sectional options implied-volatility basis**
(EVAL-77's newly-GO BTC-vs-ETH relative near-ATM IV / skew signal) be
**monetized net-of-cost** by a signal-timed **cross-sectional relative-value
delta-hedged ATM straddle spread** — long the relatively-cheap-vol underlying's
straddle and short the relatively-rich-vol underlying's straddle?

Why this rung exists (the traded-form capstone EVAL-77 leaves open)
------------------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + options order-flow + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. The runnable-now surface line
so far is:

* EVAL-71 sealed ``GO CONFIRMED`` — the *single-underlying* options implied-vol
  surface (near-ATM IV **level** + put-call **skew**) predicts forward RV;
* EVAL-73 sealed ``GO CONFIRMED (PASS)`` — that predictiveness is stable OOS;
* EVAL-74 sealed ``NO-GO CONFIRMED (PASS)`` — the term-structure slope predicts
  ETH forward RV but is null on BTC;
* EVAL-77 sealed ``GO CONFIRMED`` — the **cross-sectional** BTC-vs-ETH relative
  near-ATM IV / skew basis predicts the subsequent BTC-minus-ETH realized-vol
  spread (relative-value mean reversion; first cross-sectional GO);
* EVAL-72 / EVAL-75 / EVAL-76 sealed ``NO-GO CONFIRMED (PASS)`` — the
  *single-underlying* level/skew, term-structure and skew signals do **not**
  monetize net-of-cost through a single-underlying ATM straddle (EVAL-72/75) or a
  skew-isolating risk reversal (EVAL-76);
* EVAL-78 / EVAL-79 sealed ``NO-GO CONFIRMED (PASS)`` — options order-flow, and
  order-flow x surface / cross-sectional basis, add no portable forward-RV
  predictiveness.

Every traded form above is **single-underlying** (EVAL-72/75/76) or a
*predictiveness* measurement (EVAL-77). The one genuinely distinct, on-charter,
runnable-**now** traded-form question none of them answers is:

    EVAL-77's cross-sectional basis is the *only* GO signal that is
    cross-sectional. Does it **monetize net-of-cost** through the traded form
    that actually expresses a cross-sectional relative-vol view — a
    **relative-value ATM straddle spread** (long the relatively-cheap-vol
    underlying's delta-hedged ATM straddle, short the relatively-rich-vol
    underlying's), rather than the single-underlying straddle/risk-reversal of
    EVAL-72/75/76?

This is a distinct *signal -> traded-form* pairing (cross-sectional basis ->
two-leg relative-value straddle spread), it is on the repo charter, and it is
runnable **today** because it needs only the already-acquired real three-way
captures (both underlyings' option trade tapes + surface snapshots + perp
candles) — **no new acquisition, no network**. It does not re-litigate any sealed
result:

* EVAL-57 traded a **static** VRP straddle (NO-GO);
* EVAL-61/62 traded an **options order-flow**-timed ATM straddle (NO-GO);
* EVAL-72 traded an EVAL-71 level/skew-timed single-underlying ATM **straddle**
  (NO-GO);
* EVAL-75 traded an EVAL-74 term-structure-timed single-underlying ATM
  **straddle** (NO-GO);
* EVAL-76 traded an EVAL-71 skew-timed single-underlying **risk reversal**
  (NO-GO);
* EVAL-77 **measured** the cross-sectional basis -> RV-spread predictiveness
  (GO) but traded nothing;
* **EVAL-80** trades the cross-sectional basis through a **two-leg
  relative-value straddle spread** (long one underlying's straddle, short the
  other's) — a genuinely new traded form, not a single-underlying structure.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
--------------------------------------------------------------------------------
For each causal cross-sectional basis signal ``{atm_iv, skew}`` and each bar grid
``{60s, 300s}``, on the common aligned bar-ends where BOTH underlyings carry a
priced ATM straddle:

    rel_k   = signal[ETH](k) - signal[BTC](k)          (relative richness)
    rel_z_k = expanding-z(rel_k)                        (causal, end-of-bar k)
    side_k  = sign(rel_z_k);  exposure_k = min(|rel_z_k|, SIZE_CAP)

Build the BTC leg with ``side`` and the ETH leg with ``-side`` (long the
relatively-cheap-vol underlying, short the relatively-rich-vol underlying),
each an ATM straddle priced from the real mark and delta-hedged with the sealed
EVAL-62 ``markpath_returns`` net-of-cost P&L (delta-hedge + half real 2-leg
spread + hedge fee, spot-normalized). The relative-value return is the
equal-notional sum of the two spot-normalized leg returns
``ret_rel_k = ret_BTC_k + ret_ETH_k``. **GO only if at least one config** has
net-of-cost Sharpe > 0, no kill-switch breach (max-DD <= 0.20), directional
permutation ``p < 0.05``, block-bootstrap 95% CI lower > 0, nonzero positions >
0, and pooled BH-FDR rejects that config; else ``NO-GO CONFIRMED (PASS)`` (the
cross-sectional basis does not monetize net-of-cost through a relative-value
straddle spread).

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
-------------------------------------------------------------------------------
EVAL-80 consumes BOTH underlyings' traded-instrument data AND both underlyings'
surface trade tape AND their cross-sectional alignment, so it composes three
honestly pre-registered floors and requires all of them:

* the EVAL-61/62 traded-instrument floor (surface snapshots / instruments / perp
  bars / option trades / common 5m bars), reused verbatim for **each**
  underlying; and
* the EVAL-71 trade-tape IV floor (option trades / near-ATM trades / perp
  candles / span), reused verbatim for **each** underlying; and
* a cross-sectional alignment floor: at least
  ``min_aligned_common_straddle_bars`` bar-ends where **both** underlyings carry a
  priced ATM straddle on the coarsest grid.

None is weakened. Below the composed floor it seals
``EVAL_80_..._BLOCKED_<UTC>`` (never a NO-GO). The EVAL-64 feasible floor that
governs the EVAL-67/68/69 ladder is untouched.

Seals ``EVAL_80_CROSS_SECTIONAL_RELATIVE_VALUE_STRADDLE_MONETIZATION_PREREGISTRATION_<UTC>``
then ``..._COMBINED_<UTC>`` (or ``..._BLOCKED_<UTC>``).
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
# signal, and the EVAL-77 cross-section verbatim (no forks, no src edits).
import scripts.eval57_vrp_net_of_cost as e57  # noqa: E402
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
import scripts.eval77_cross_sectional_surface_basis_rv_predictiveness as e77  # noqa: E402
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
REPORT_ID = "EVAL_80_CROSS_SECTIONAL_RELATIVE_VALUE_STRADDLE_MONETIZATION_COMBINED"
PREREG_ID = "EVAL_80_CROSS_SECTIONAL_RELATIVE_VALUE_STRADDLE_MONETIZATION_PREREGISTRATION"
BLOCKED_ID = "EVAL_80_CROSS_SECTIONAL_RELATIVE_VALUE_STRADDLE_MONETIZATION_BLOCKED"

# The cross-section is BTC-vs-ETH (identical to EVAL-77): ``BASELINE`` is the
# subtracted leg, so ``rel = signal[RELATIVE] - signal[BASELINE]``. ``side > 0``
# means RELATIVE (ETH) vol is rich -> long BASELINE (BTC) vol, short RELATIVE.
BASELINE = "BTC"
RELATIVE = "ETH"

# Pre-registered grid: cross-sectional basis signals x bar grid.
BASIS_SIGNALS: Tuple[str, ...] = ("atm_iv", "skew")
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
SIGNAL_WINDOW_SECONDS: float = e71.SIGNAL_WINDOW_SECONDS

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

# A config must produce at least this many aligned common straddle states to be
# evaluable (a result-quality guard, not a data floor).
MIN_STATES_PER_CONFIG = 100

# Composed heavy-work floor (both EVAL-61/62 and EVAL-71 floors AND alignment).
FLOOR: Dict[str, Any] = {
    "min_underlyings": e62.MIN_UNDERLYINGS,
    "min_aligned_common_straddle_bars": 200,
    "min_states_per_config": int(MIN_STATES_PER_CONFIG),
    "note": (
        "EVAL-80 consumes both underlyings' traded-instrument data (surface "
        "snapshots / perp candles / option trades; EVAL-61/62 floor), both "
        "underlyings' near-ATM trade-tape IV (EVAL-71 surface floor), and their "
        "cross-sectional alignment. All sealed floors are reused verbatim for "
        "each underlying and BOTH must pass, plus >= min_aligned_common_straddle_bars "
        "bar-ends where both underlyings carry a priced ATM straddle on the coarsest "
        "grid; none is weakened. This is NOT the EVAL-64 options-surface snapshot "
        "floor, which governs the EVAL-67/68/69 ladder and is untouched here."
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
    "scripts/eval77_cross_sectional_surface_basis_rv_predictiveness.py",
    "scripts/eval80_cross_sectional_relative_value_straddle_monetization.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval80_cross_sectional_relative_value_straddle_monetization.py "
    "tests/test_eval80_cross_sectional_relative_value_straddle_monetization.py",
    "python3 -m pytest -q tests/test_eval80_cross_sectional_relative_value_straddle_monetization.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval80_cross_sectional_relative_value_straddle_monetization.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval80_cross_sectional_relative_value_straddle_monetization.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL80-CROSS-SECTIONAL-RV-STRADDLE-MONETIZATION",
)


# ---------------------------------------------------------------------------
# Small helpers (local; no src edits)
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite(x: Any, default: float = 0.0) -> float:
    return e71._finite(x, default)


def _select_one_capture_per_underlying(
    captures: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Richest (most real option trades) real capture per underlying; deterministic."""
    best: Dict[str, Dict[str, Any]] = {}
    for c in captures:
        inst = str(c.get("underlying") or "?")
        score = len(c.get("option_trades", []) or [])
        if inst not in best or score > len(best[inst].get("option_trades", []) or []):
            best[inst] = c
    return [best[k] for k in sorted(best)]


# ---------------------------------------------------------------------------
# Per-underlying causal ATM straddle states (EVAL-62-correct, no signal)
# ---------------------------------------------------------------------------
def build_atm_straddle_states(
    capture: Dict[str, Any], *, bar_seconds: float
) -> Dict[int, Dict[str, Any]]:
    """Per-bar causal ATM straddle instrument states, keyed by ``bar_ms`` (bar open).

    Identical straddle construction to the sealed EVAL-62 ``build_states`` /
    EVAL-72 ``build_skew_states`` (front expiry, common strike nearest spot, IV
    backed out of the real mark via EVAL-57 helpers) except it carries **no**
    side/exposure (the cross-sectional relative-value side is applied by the
    caller once the two underlyings are aligned). Returns
    ``{bar_ms: {spot, straddle_delta, straddle_mark, spread_usd, strike}}``.
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

    out: Dict[int, Dict[str, Any]] = {}
    for bar_end in bar_ends:
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
        pick = e57._pick_straddle_quotes(quotes, spot, exp)
        if not pick or not pick.get("valid"):
            continue
        legs: List[Dict[str, float]] = []
        ok = True
        for key in ("call", "put"):
            q = pick[key]
            g = e57._iv_and_greeks(
                _finite(q.get("mark"), 0.0), _finite(q.get("bid"), 0.0),
                _finite(q.get("ask"), 0.0), spot, _finite(q.get("strike"), 0.0),
                q.get("expiry"), state_time,
                str(q.get("option_type") or key).lower(),
            )
            if g is None:
                ok = False
                break
            legs.append({"key": key, **g})
        if not ok or len(legs) != 2:
            continue
        straddle_delta = float(sum(l["delta"] for l in legs))
        straddle_mark = float(
            _finite(pick["call"].get("mark"), 0.0) + _finite(pick["put"].get("mark"), 0.0)
        )
        if straddle_mark <= 0.0:
            continue
        out[int(bar_ms)] = {
            "spot": float(spot),
            "straddle_delta": straddle_delta,
            "straddle_mark": straddle_mark,
            "spread_usd": float(pick.get("spread_usd", 0.0)),
            "strike": float(pick.get("strike", spot)),
        }
    return out


# ---------------------------------------------------------------------------
# Cross-sectional relative-value leg construction
# ---------------------------------------------------------------------------
def cross_section_relative_z(
    captures: Dict[str, Dict[str, Any]], *, surface_signal: str, bar_seconds: float
) -> Tuple[Dict[str, Any], Dict[int, float]]:
    """Reuse EVAL-77's cross-section + relative signal verbatim.

    Returns ``(cs, rel_z_by_bar)`` where ``cs`` is EVAL-77's ``build_cross_section``
    result and ``rel_z_by_bar`` maps each common bar-open to the causal
    expanding-z of the ``signal[ETH] - signal[BTC]`` relative basis.
    """
    cs = e77.build_cross_section(captures, bar_seconds=bar_seconds)
    rel = e77._relative_signal_series(cs, surface_signal=surface_signal)
    rel_by_bar = {int(b): float(rel[i]) for i, b in enumerate(cs["common"])}
    return cs, rel_by_bar


def build_relative_value_legs(
    captures: Dict[str, Dict[str, Any]], *, surface_signal: str, bar_seconds: float
) -> Dict[str, Any]:
    """Align both underlyings' ATM straddle states on their common bar grid and
    attach the cross-sectional relative-value side/exposure.

    ``side_k = sign(rel_z_k)`` on the BASELINE (BTC) leg and ``-side_k`` on the
    RELATIVE (ETH) leg, so ``side > 0`` (ETH rich) is long BTC vol / short ETH vol.
    ``exposure_k = min(|rel_z_k|, SIZE_CAP)``. The two per-leg state lists are
    aligned 1:1 on the common trade bars so the sealed EVAL-62
    ``markpath_returns`` can be applied to each leg and summed by the caller.
    """
    states = {
        BASELINE: build_atm_straddle_states(captures[BASELINE], bar_seconds=bar_seconds),
        RELATIVE: build_atm_straddle_states(captures[RELATIVE], bar_seconds=bar_seconds),
    }
    cs, rel_by_bar = cross_section_relative_z(
        captures, surface_signal=surface_signal, bar_seconds=bar_seconds
    )
    common_trade = [
        int(b)
        for b in cs["common"]
        if int(b) in states[BASELINE]
        and int(b) in states[RELATIVE]
        and int(b) in rel_by_bar
    ]

    btc_leg: List[Dict[str, Any]] = []
    eth_leg: List[Dict[str, Any]] = []
    for b in common_trade:
        z = float(rel_by_bar[b])
        side = 1 if z > 1e-9 else (-1 if z < -1e-9 else 0)
        exposure = min(abs(z), SIZE_CAP) if side != 0 else 0.0
        sb = states[BASELINE][b]
        se = states[RELATIVE][b]
        btc_leg.append({
            "bar_ms": int(b),
            "spot": float(sb["spot"]),
            "side": int(side),
            "exposure": float(exposure),
            "straddle_delta": float(sb["straddle_delta"]),
            "straddle_mark": float(sb["straddle_mark"]),
            "spread_usd": float(sb["spread_usd"]),
            "signal_z": float(z),
            "strike": float(sb.get("strike", sb["spot"])),
        })
        eth_leg.append({
            "bar_ms": int(b),
            "spot": float(se["spot"]),
            "side": int(-side),
            "exposure": float(exposure),
            "straddle_delta": float(se["straddle_delta"]),
            "straddle_mark": float(se["straddle_mark"]),
            "spread_usd": float(se["spread_usd"]),
            "signal_z": float(z),
            "strike": float(se.get("strike", se["spot"])),
        })
    return {
        "common_trade_bars": common_trade,
        "btc_leg": btc_leg,
        "eth_leg": eth_leg,
        "cs": cs,
        "surface_signal": surface_signal,
        "bar_seconds": float(bar_seconds),
    }


# ---------------------------------------------------------------------------
# Per-config evaluation (relative-value mark-path net-of-cost; EVAL-62 stats)
# ---------------------------------------------------------------------------
def evaluate_config(
    captures: Dict[str, Dict[str, Any]], *, basis_signal: str, bar_seconds: float
) -> Dict[str, Any]:
    legs = build_relative_value_legs(
        captures, surface_signal=basis_signal, bar_seconds=bar_seconds
    )
    n_states = len(legs["btc_leg"])
    if n_states < int(MIN_STATES_PER_CONFIG):
        return {
            "basis_signal": basis_signal,
            "bar_seconds": float(bar_seconds),
            "error": "insufficient aligned common straddle states",
            "n_states": n_states,
            "n_returns": 0,
            "pass": False,
        }

    rb = e62.markpath_returns(legs["btc_leg"])
    re = e62.markpath_returns(legs["eth_leg"])
    n = min(len(rb["returns"]), len(re["returns"]))
    ret_rel = [float(rb["returns"][k]) + float(re["returns"][k]) for k in range(n)]
    if len(ret_rel) < 3:
        return {
            "basis_signal": basis_signal,
            "bar_seconds": float(bar_seconds),
            "error": "insufficient relative-value returns",
            "n_states": n_states,
            "n_returns": len(ret_rel),
            "pass": False,
        }

    sharpe = _sharpe_of_returns(ret_rel)
    mdd = e62._max_drawdown(ret_rel)
    flat = [0.0] * len(ret_rel)
    perm = permutation_test(
        ret_rel, flat, statistic=e62._mean, n_permutations=PERMUTATION_PERMS,
        paired=True, seed=SEED,
    )
    boot = block_bootstrap_ci(
        ret_rel, statistic=_sharpe_of_returns, n_bootstrap=BOOTSTRAP_RESAMPLES,
        block_size=BOOTSTRAP_BLOCK, seed=SEED,
    )
    wf = e62.walkforward_folds(
        ret_rel, train=max(10, len(ret_rel) // 3),
        test=max(10, len(ret_rel) // 5), step=max(10, len(ret_rel) // 5),
    )
    breach = e62.kill_switch_breach(mdd)
    perm_p = e62._finite(perm.get("p_value"), 1.0)
    ci_low = e62._finite(boot[1], 0.0)
    ci_high = e62._finite(boot[2], 0.0)
    nonzero = int(sum(1 for s in legs["btc_leg"] if abs(float(s.get("signal_z", 0.0))) > 1e-9))
    passed = bool(
        sharpe > 0.0
        and not breach
        and perm_p < 0.05
        and ci_low > 0.0
        and nonzero > 0,
    )
    return {
        "basis_signal": basis_signal,
        "bar_seconds": float(bar_seconds),
        "n_states": n_states,
        "n_returns": len(ret_rel),
        "nonzero_positions": nonzero,
        "n_hedge_rebalances_btc": rb.get("n_hedge_rebalances"),
        "n_hedge_rebalances_eth": re.get("n_hedge_rebalances"),
        "n_side_flips_btc": rb.get("n_side_flips"),
        "n_side_flips_eth": re.get("n_side_flips"),
        "sharpe": float(sharpe),
        "max_drawdown": float(mdd),
        "kill_switch_breach": bool(breach),
        "permutation_p": float(perm_p),
        "bootstrap_ci": [float(boot[0]), float(ci_low), float(ci_high)],
        "dsr": _dsr_of_returns(ret_rel),
        "walkforward": wf,
        "mean_return": e62._mean(ret_rel),
        "pass": bool(passed),
    }


# ---------------------------------------------------------------------------
# Composed heavy-work floor (EVAL-61/62 traded floor AND EVAL-71 surface floor
# AND cross-sectional straddle alignment)
# ---------------------------------------------------------------------------
def _underlying_floor(capture: Dict[str, Any]) -> Dict[str, Any]:
    inst = capture.get("underlying", "?")
    fl_traded = e61._underlying_floor(capture)          # surface snapshots / perp / trades
    fl_signal = e71._underlying_surface_floor(capture)  # EVAL-71 trade-tape IV floor
    ok = bool(fl_traded.get("ok") and fl_signal.get("ok"))
    return {
        "underlying": inst,
        "traded_floor_ok": bool(fl_traded.get("ok")),
        "signal_floor_ok": bool(fl_signal.get("ok")),
        "traded_floor": fl_traded,
        "signal_floor": fl_signal,
        "checks": {
            "traded_floor_ok": bool(fl_traded.get("ok")),
            "signal_floor_ok": bool(fl_signal.get("ok")),
        },
        "ok": ok,
    }


def _common_straddle_bars(captures: Dict[str, Dict[str, Any]], *, bar_seconds: float) -> int:
    b = set(build_atm_straddle_states(captures[BASELINE], bar_seconds=bar_seconds))
    r = set(build_atm_straddle_states(captures[RELATIVE], bar_seconds=bar_seconds))
    return len(b & r)


def campaign_floor(captures: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Composed floor: both underlyings pass EVAL-61/62 AND EVAL-71, and the
    cross-sectional straddle alignment floor holds on the coarsest grid."""
    insts = sorted(captures)
    per_underlying = {i: _underlying_floor(captures[i]) for i in insts if i in (BASELINE, RELATIVE)}
    both_present = BASELINE in captures and RELATIVE in captures
    underlyings_ok = bool(
        both_present
        and all(per_underlying[i]["ok"] for i in (BASELINE, RELATIVE) if i in per_underlying)
    )

    aligned_by_grid: Dict[str, int] = {}
    if both_present:
        for bar_s in GRID_BAR_SECONDS:
            aligned_by_grid[str(bar_s)] = _common_straddle_bars(
                {BASELINE: captures[BASELINE], RELATIVE: captures[RELATIVE]},
                bar_seconds=bar_s,
            )
    coarsest = max(GRID_BAR_SECONDS)
    aligned_binding = int(aligned_by_grid.get(str(coarsest), 0))
    aligned_ok = aligned_binding >= int(FLOOR["min_aligned_common_straddle_bars"])
    return {
        "underlyings": insts,
        "per_underlying": per_underlying,
        "underlyings_ok": underlyings_ok,
        "aligned_common_straddle_bars_by_grid": aligned_by_grid,
        "aligned_common_straddle_bars_binding": aligned_binding,
        "aligned_ok": aligned_ok,
        "checks": {
            "underlyings_ok": underlyings_ok,
            "aligned_ok": aligned_ok,
        },
        "ok": bool(underlyings_ok and aligned_ok),
    }


# ---------------------------------------------------------------------------
# Protocol + orchestration
# ---------------------------------------------------------------------------
def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-80",
        "title": "Cross-sectional options implied-volatility basis (EVAL-77 "
                 "BTC-vs-ETH relative near-ATM IV / skew) -> signal-timed "
                 "cross-sectional relative-value delta-hedged ATM straddle spread "
                 "(long the relatively-cheap-vol underlying, short the "
                 "relatively-rich-vol underlying) with correct mark-path "
                 "net-of-cost P&L: traded-form monetization falsification on the "
                 "real on-disk three-way captures",
        "extends": "EVAL-77 (identical cross-sectional BTC-vs-ETH relative near-ATM "
                    "IV / skew basis and Spearman-rank-IC predictiveness GO) and "
                    "EVAL-62/EVAL-72/EVAL-75/EVAL-76 (identical correct mark-path "
                    "net-of-cost delta-hedged traded form) but a different, on-charter "
                    "traded structure: a two-leg cross-sectional relative-value ATM "
                    "straddle spread rather than a single-underlying straddle or "
                    "risk reversal; no new acquisition",
        "supersedes": "nothing — this is the traded-form monetization capstone of "
                      "EVAL-77's cross-sectional predictiveness GO. EVAL-57 traded a "
                      "static VRP straddle (NO-GO), EVAL-61/62 an order-flow-timed "
                      "ATM straddle (NO-GO), EVAL-72 a level/skew-timed single-"
                      "underlying ATM straddle (NO-GO), EVAL-75 a term-structure-"
                      "timed single-underlying ATM straddle (NO-GO), EVAL-76 a "
                      "skew-timed single-underlying risk reversal (NO-GO), and "
                      "EVAL-77 measured the cross-sectional basis -> RV-spread "
                      "predictiveness (GO) without trading; a two-leg relative-value "
                      "straddle spread is genuinely new",
        "capture_dir": str(capture_dir),
        "cross_section": {
            "baseline": BASELINE,
            "relative": RELATIVE,
            "relative_signal": "rel_k = signal[ETH](k) - signal[BTC](k)",
            "position": "side_k = sign(rel_z_k) on the BTC leg and -side_k on the ETH "
                        "leg (long the relatively-cheap-vol underlying, short the "
                        "relatively-rich-vol underlying); exposure_k = min(|rel_z_k|, "
                        "size_cap)",
            "combination": "ret_rel_k = ret_BTC_k + ret_ETH_k (equal-notional sum of "
                           "the two spot-normalized EVAL-62 mark-path leg returns)",
        },
        "basis_signals": list(BASIS_SIGNALS),
        "signal_window_seconds": float(SIGNAL_WINDOW_SECONDS),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "traded_form": "two-leg cross-sectional relative-value ATM straddle spread "
                       "(each leg: front expiry, common strike nearest spot, IV backed "
                       "out of the real mark via EVAL-57 helpers) with the EVAL-62 "
                       "mark-path net-of-cost P&L per leg: delta-hedge + half real "
                       "2-leg spread + hedge fee, spot-normalized, then summed",
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
            "min_states_per_config": int(MIN_STATES_PER_CONFIG),
        },
        "kill_switch_max_dd": KILL_SWITCH_MAX_DD,
        "go_bar": (
            "GO only if at least one config (basis signal x bar grid) has net-of-cost "
            "Sharpe > 0, no kill-switch breach (max-DD <= 0.20), directional "
            "permutation p < 0.05, block-bootstrap 95% CI lower > 0, nonzero positions "
            "> 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS)."
        ),
        "floor": {
            "composed_of": ["EVAL-61/62 traded-instrument floor",
                            "EVAL-71 surface floor",
                            "cross-sectional straddle alignment floor"],
            "min_underlyings": int(FLOOR["min_underlyings"]),
            "min_aligned_common_straddle_bars": int(FLOOR["min_aligned_common_straddle_bars"]),
            "note": FLOOR["note"],
        },
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def run_eval80(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL80-CROSS-SECTIONAL-RV-STRADDLE-MONETIZATION",
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
    floor_ok = bool(
        BASELINE in captures
        and RELATIVE in captures
        and len(captures) >= int(FLOOR["min_underlyings"])
        and floor["ok"]
    )

    per_config: List[Dict[str, Any]] = []
    errors: List[str] = []
    for sig in BASIS_SIGNALS:
        for bar_s in GRID_BAR_SECONDS:
            try:
                res = evaluate_config(
                    captures, basis_signal=sig, bar_seconds=bar_s
                )
            except BaseException as exc:  # noqa: BLE001
                errors.append(f"{sig}::bar{bar_s}: {exc!r}")
                continue
            per_config.append(res)

    p_values = {
        f"{r['basis_signal']}::bar{r['bar_seconds']}":
            _finite(r.get("permutation_p"), 1.0)
        for r in per_config
        if r.get("n_returns", 0) > 0
    }
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}
    rejected = set(bh.get("rejected") or [])

    pass_configs: List[str] = []
    for r in per_config:
        key = f"{r['basis_signal']}::bar{r['bar_seconds']}"
        if r.get("pass") and key in rejected:
            pass_configs.append(key)

    valid = [r for r in per_config if r.get("n_returns", 0) > 0]
    best = (
        max(valid, key=lambda r: _finite(r.get("sharpe"), -1e9))
        if valid else None
    )

    any_pass = bool(pass_configs)
    go = bool(floor_ok and any_pass and len(rejected) >= 1)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = (
        "EVAL_80_CROSS_SECTIONAL_RELATIVE_VALUE_STRADDLE_MONETIZATION" if floor_ok
        else "EVAL_80_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "cross-sectional relative-value delta-hedged ATM straddle spread with "
            "correct mark-path net-of-cost P&L (traded-form monetization of EVAL-77's "
            "cross-sectional predictive basis) on the real on-disk captures"
            if floor_ok else "capture below the composed pre-registered floor; no verdict"
        ),
        "floor_ok": bool(floor_ok),
        "capture_dir": str(capture_dir_abs),
        "underlyings": sorted(captures),
        "floor": dict(FLOOR),
        "campaign_floor": floor,
        "protocol": build_protocol(capture_dir),
        "per_config": per_config,
        "summary": {
            "n_configs": len(per_config),
            "n_pass": len(pass_configs),
            "pass_configs": pass_configs,
            "best_sharpe": _finite(best.get("sharpe"), 0.0) if best else 0.0,
            "best_config": (
                f"{best['basis_signal']}::bar{best['bar_seconds']}" if best else "n/a"
            ),
        },
        "pooled": {
            "bh_fdr": bh,
            "any_config_pass": any_pass,
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
            "The causal cross-sectional options implied-volatility basis (EVAL-77 "
            "BTC-vs-ETH relative near-ATM IV / put-call skew, from the real Deribit "
            "option trade tapes) can be monetized net-of-cost by a signal-timed "
            "cross-sectional relative-value delta-hedged ATM straddle spread (long the "
            "relatively-cheap-vol underlying's straddle, short the relatively-rich-vol "
            "underlying's) on the BTC/ETH perpetual, on the already-acquired real "
            "on-disk captures at the composed floor."
        ),
        "extends": p["extends"],
        "protocol": p,
        "capture_dir": report["capture_dir"],
    }


def _build_prereg_md(r: Dict[str, Any]) -> str:
    p = r["protocol"]
    cs = p["cross_section"]
    fl = p["floor"]
    lines = [
        f"# {PREREG_ID} — cross-sectional relative-value delta-hedged ATM straddle "
        f"spread net-of-cost monetization falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Hypothesis: {r['hypothesis']}",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Extends: {p['extends']}",
        "",
        "## Pre-declared protocol",
        "",
        f"- Cross-section: baseline `{cs['baseline']}`, relative `{cs['relative']}`",
        f"- Relative signal: {cs['relative_signal']}",
        f"- Position: {cs['position']}",
        f"- Combination: {cs['combination']}",
        f"- Basis signals: {p['basis_signals']}",
        f"- Signal window (s): {p['signal_window_seconds']}",
        f"- Bar grid (s): {p['bar_seconds_grid']}",
        f"- Traded form: {p['traded_form']}",
        f"- Stats: perm {p['stats']['permutation_perms']} ({p['stats']['permutation_paired']}) / "
        f"bootstrap {p['stats']['bootstrap_resamples']} block {p['stats']['bootstrap_block']} / "
        f"BH-FDR alpha {p['stats']['fdr_alpha']} / seed {p['stats']['seed']} / "
        f"zwindow {p['zwindow']} / size_cap {p['size_cap']} / "
        f"min states per config {p['stats']['min_states_per_config']}",
        f"- Kill-switch max-DD: {p['kill_switch_max_dd']}",
        "",
        "## Pre-declared GO bar",
        "",
        p["go_bar"],
        "",
        "## Pre-registered composed floor (all sealed floors + alignment; none weakened)",
        "",
        f"- {fl['note']}",
        f"- Composed of: {fl['composed_of']}",
        f"- Min underlyings: {fl['min_underlyings']}",
        f"- Min aligned common straddle bars (coarsest grid): {fl['min_aligned_common_straddle_bars']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    fl = r["campaign_floor"]
    lines = [
        f"# {r['report_id']} — cross-sectional relative-value delta-hedged ATM "
        f"straddle spread net-of-cost monetization falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        f"- Aligned common straddle bars by grid: {fl['aligned_common_straddle_bars_by_grid']}",
        "",
        "## Per-underlying floor (composed)",
        "",
        "| underlying | traded floor ok | surface floor ok | ok |",
        "|---|---|---|---|",
    ]
    for inst, u in fl["per_underlying"].items():
        lines.append(
            f"| {inst} | {u['traded_floor_ok']} | {u['signal_floor_ok']} | {u['ok']} |"
        )
    lines += ["", "## Configs (best first by Sharpe)", "",
              "| basis signal | bar s | n states | n returns | Sharpe | max-DD | perm p | bootstrap 95% CI | pass |",
              "|---|---|---|---|---|---|---|---|---|"]
    rows = sorted(
        [c for c in r["per_config"] if c.get("n_returns", 0) > 0],
        key=lambda c: _finite(c.get("sharpe"), -1e9),
        reverse=True,
    )
    for c in rows:
        ci = c.get("bootstrap_ci") or [0.0, 0.0, 0.0]
        lines.append(
            f"| {c['basis_signal']} | {c['bar_seconds']:.0f} | {c['n_states']} | "
            f"{c['n_returns']} | {c['sharpe']:.4f} | {c['max_drawdown']:.4f} | "
            f"{c['permutation_p']:.4f} | [{ci[0]:.4f}, {ci[1]:.4f}, {ci[2]:.4f}] | "
            f"{c['pass']} |"
        )
    lines += ["", "## Pooled", "",
              f"- BH-FDR rejected: {r['pooled']['bh_fdr'].get('rejected')}",
              f"- Any config pass: {r['pooled']['any_config_pass']}",
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
        f"# {BLOCKED_ID} — cross-sectional relative-value delta-hedged ATM straddle "
        f"spread (below the composed pre-registered floor)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        "- Verdict: **BLOCKED** (measured; not NO-GO)",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Underlyings: {', '.join(r['underlyings'])}",
        f"- Underlyings floor met: {fl.get('underlyings_ok')}",
        f"- Aligned common straddle bars by grid: {fl.get('aligned_common_straddle_bars_by_grid')}",
        f"- Aligned floor met: {fl.get('aligned_ok')}",
        "",
        "The capture does not meet the composed EVAL-61/62 + EVAL-71 + cross-sectional "
        "alignment floor, so no GO/NO-GO verdict is emitted. Do NOT weaken any floor, "
        "do NOT use synthetic data, and do NOT emit NO-GO on under-floor data.",
        "",
        "## Per-underlying floor",
        "",
    ]
    for inst, u in (fl.get("per_underlying") or {}).items():
        lines.append(
            f"- {inst}: traded_floor_ok={u.get('traded_floor_ok')} "
            f"signal_floor_ok={u.get('signal_floor_ok')} checks={json.dumps(u.get('checks'))}"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-80: cross-sectional relative-value delta-hedged ATM straddle "
                    "spread net-of-cost monetization falsification on the real on-disk "
                    "captures"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument(
        "--task-label", default="EVAL80-CROSS-SECTIONAL-RV-STRADDLE-MONETIZATION"
    )
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval80(
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
        "summary": report.get("summary"),
        "aligned_common_straddle_bars": report.get("campaign_floor", {}).get(
            "aligned_common_straddle_bars_by_grid"
        ),
        "bh_fdr_rejected": report.get("pooled", {}).get("bh_fdr", {}).get("rejected"),
        "n_configs": len(report.get("per_config", [])),
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())