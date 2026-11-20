#!/usr/bin/env python3
"""EVAL-135: can the **cross-asset term-structure slope spillover** (the OTHER
underlying's causal ``term_slope``) be **monetized net-of-cost** by a
signal-timed delta-hedged **risk reversal** on the target underlying?

This is the charter's *tradeable, net-of-cost alpha* rung: the EVAL-122
cross-asset ``term_slope`` spillover -> forward realized return skewness **GO**
is consumed here as the signal, paired with the risk-reversal traded form
(sealed EVAL-76 trade construction) and the honest Deribit/perp cost model
(EVAL-62 mark-path: half real 2-leg spread + hedge fee + flip cost), tested at
the sealed EVAL-64 feasible floor verbatim.

Why this rung exists
--------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + options order-flow + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. EVAL-122 sealed
``GO CONFIRMED`` (BTC IC 0.3817 / ETH IC 0.4643, 6 pooled BH-FDR rejections) for
the cross-asset ``term_slope`` spillover -> forward **realized return skewness**.
That is *predictiveness only* — no traded-form or monetization claim. EVAL-135
asks the monetization question: does the *other asset's z-scored term slope*
(sign/exposure from EVAL-122's best cross-asset spillover configs) timed a
delta-hedged risk reversal yield a positive net-of-cost mean on **both**
BTC and ETH?

It is a distinct *signal -> traded-form* pairing (cross-asset term-slope spillover
-> risk reversal, not surface skew -> risk reversal which is EVAL-76), it is on
the repo charter, and it is runnable **today** because it needs only the
already-acquired real three-way captures — **no new acquisition, no network**.
It does not re-litigate any sealed result: EVAL-76 traded a surface-**skew**
timed risk reversal (NO-GO); EVAL-72/EVAL-75 traded ATM straddles (NO-GO);
EVAL-122 measured predictiveness only. EVAL-135 is the net-of-cost rung.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
---------------------------------------------------------------------------------
For each target underlying (BTC, ETH) and each bar grid ``{60s, 300s}``:

* the causal term slope ``term_slope = IV(near expiry) - IV(far expiry)`` of the
  **other** underlying is reconstructed exactly as EVAL-122
  (``e74._term_bars``), aligned to the common BTC-vs-ETH bar grid
  (``build_cross_section``), forward-filled causally (``e71._forward_fill``) and
  expanding z-scored end-of-bar ``k`` (``e61.expanding_zscore``,
  ``e62.ZWINDOW``); this is the signal side/exposure source.
* the target's **risk reversal** state (front expiry; nearest OTM call + nearest
  OTM put; IV backed out of the real mark via EVAL-57 helpers) is built per bar
  from the target's real surface snapshots, reusing sealed EVAL-76
  ``build_risk_reversal_states`` trade construction verbatim, with
  ``side_k = sign(term_slope_z_k)`` and ``exposure_k = min(|term_slope_z_k|,
  SIZE_CAP)``.
* the correct mark-path **net-of-cost** return (EVAL-62 ``markpath_returns``:
  delta-hedge + half real 2-leg spread + hedge fee, spot-normalized) is computed
  on the signed long-call/short-put aggregate mark/delta.

A config **passes** only if net-of-cost ``mean_return > 0``,
directional permutation ``p < 0.05`` (H1: mean > 0), block-bootstrap 95% CI
lower ``> 0``, and nonzero positions > 0.

**GO only if, on BOTH BTC and ETH and at least one config:** net-of-cost
``mean_return > 0``, block-bootstrap 95% CI lower ``> 0``, directional
permutation ``p < 0.05``, nonzero positions > 0, and pooled BH-FDR rejects that
config; else ``NO-GO CONFIRMED (PASS)``.

Feasible floor (sealed EVAL-64 floor verbatim; NOT weakened)
---------------------------------------------------------------------------------
``floor = sealed EVAL-64 floor verbatim``: per underlying,
surface >= 1000 snapshots / >= 100 instruments / >= 1000 5m bars /
>= 600000 s span; perp >= 1000 5m bars / >= 300000 s span; Deribit option trades
>= 2000 / >= 150 instruments / >= 82000 s span / >= 240 5m bars; common 5m bars
>= 240; roster >= 2 underlyings. Reused from sealed
``scripts/eval64_orderflow_realized_vol_markpath_feasible.py`` verbatim
(``e64._underlying_floor_strict`` + ``e64.MIN_*`` constants). Neither weakened.

Corrected successor to EVAL-124 (append-only; no sealed artifact touched)
---------------------------------------------------------------------------------
EVAL-124 was the first, identical attempt at this rung and sealed ``BLOCKED`` at
``20261119T125055Z`` with **zero economic measurement**: every config aborted with
``AttributeError: module 'scripts.eval61_orderflow_realized_vol_net_of_cost' has no
attribute '_expiry_date'`` (a one-token bug — the helper lives on the EVAL-57
module, ``e57._expiry_date``). That BLOCKED seal therefore reflected an
implementation fault, not the data-availability floor. EVAL-135 is the corrected,
append-only successor: identical pre-registered GO bar and floor, with the import
bug fixed, so the monetization rung is finally *measurable* the moment a
floor-clearing real capture exists.

Below the floor it seals ``EVAL_135_..._BLOCKED_<UTC>`` (never a NO-GO). On the
deepest on-disk real capture (``data/raw/eval68``: 1067 surface snapshots, 5001
perp candles per underlying) the EVAL-64 floor still fails on breadth only —
BTC 99/100 surface instruments, ETH 1895/2000 option trades, and the order-flow
instrument count 96 (BTC) / 93 (ETH) vs 150 — so this campaign honestly seals
BLOCKED with those exact diagnostics exposed in the artifact. That is the
capture-depth ceiling, not a measurement failure and not a reason to touch the
floor; the unblocking work is a deeper real acquisition.

Seals ``EVAL_135_CROSS_ASSET_TERM_SLOPE_SPILLOVER_RISK_REVERSAL_NET_OF_COST_PREREGISTRATION_<UTC>``
then ``..._COMBINED_<UTC>`` (or ``..._BLOCKED_<UTC>``).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Reuse sealed helpers verbatim (no forks, no src edits).
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64  # noqa: E402 (EVAL-64 floor verbatim)
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402 (_forward_fill)
import scripts.eval74_surface_term_structure_predictiveness as e74  # noqa: E402 (_term_bars)
import scripts.eval57_vrp_net_of_cost as e57  # noqa: E402 (_iv_and_greeks)
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)
from src.analytics.strategy_evaluation import (  # noqa: E402
    block_bootstrap_ci,
    permutation_test,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_135_CROSS_ASSET_TERM_SLOPE_SPILLOVER_RISK_REVERSAL_NET_OF_COST_COMBINED"
PREREG_ID = "EVAL_135_CROSS_ASSET_TERM_SLOPE_SPILLOVER_RISK_REVERSAL_NET_OF_COST_PREREGISTRATION"
BLOCKED_ID = "EVAL_135_CROSS_ASSET_TERM_SLOPE_SPILLOVER_RISK_REVERSAL_NET_OF_COST_BLOCKED"

# Single cross-asset signal: the OTHER underlying's causal term_slope.
SURFACE_SIGNAL: str = "term_slope"
TARGET = "net_of_cost_mean_return"

# Grid mirrors EVAL-122 (cross-asset term_slope spillover -> return skewness).
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)

BASELINE = "BTC"
RELATIVE = "ETH"

# Stats / cost / risk constants reused verbatim from EVAL-62 (no forks).
ZWINDOW = e62.ZWINDOW
SIZE_CAP = e62.SIZE_CAP
PERMUTATION_PERMS = e65.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e65.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e65.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
KILL_SWITCH_MAX_DD = e62.KILL_SWITCH_MAX_DD
HEDGE_FEE_BPS = e62.HEDGE_FEE_BPS

# EVAL-64 feasible floor constants, reused verbatim (the floor for THIS campaign).
MIN_SNAPSHOTS = e64.MIN_SNAPSHOTS
MIN_SURFACE_INSTRUMENTS = e64.MIN_SURFACE_INSTRUMENTS
MIN_SURFACE_BARS_5M = e64.MIN_SURFACE_BARS_5M
MIN_OPTION_TRADES = e64.MIN_OPTION_TRADES
MIN_OF_INSTRUMENTS = e64.MIN_OF_INSTRUMENTS
MIN_OF_SPAN_SECONDS = e64.MIN_OF_SPAN_SECONDS
MIN_OF_BARS_5M = e64.MIN_OF_BARS_5M
MIN_PERP_BARS_5M = e64.MIN_PERP_BARS_5M
MIN_PERP_SPAN_SECONDS = e64.MIN_PERP_SPAN_SECONDS
MIN_COMMON_BARS = e64.MIN_COMMON_BARS
MIN_UNDERLYINGS = e64.MIN_UNDERLYINGS

MIN_STATES_PER_CONFIG = 100
MIN_RETURNS_PER_CONFIG = 3

# Composed floor: sealed EVAL-64 floor verbatim (per underlying) + both
# underlyings present. Not weakened.
FLOOR: Dict[str, Any] = {
    "min_underlyings": int(MIN_UNDERLYINGS),
    "min_surface_snapshots_per_underlying": int(MIN_SNAPSHOTS),
    "min_surface_instruments_per_underlying": int(MIN_SURFACE_INSTRUMENTS),
    "min_surface_bars_5m_per_underlying": int(MIN_SURFACE_BARS_5M),
    "min_option_trades_per_underlying": int(MIN_OPTION_TRADES),
    "min_of_instruments_per_underlying": int(MIN_OF_INSTRUMENTS),
    "min_of_span_seconds_per_underlying": float(MIN_OF_SPAN_SECONDS),
    "min_of_bars_5m_per_underlying": int(MIN_OF_BARS_5M),
    "min_perp_bars_5m_per_underlying": int(MIN_PERP_BARS_5M),
    "min_perp_span_seconds_per_underlying": float(MIN_PERP_SPAN_SECONDS),
    "min_common_bars_per_underlying": int(MIN_COMMON_BARS),
    "note": (
        "Floor = sealed EVAL-64 feasible floor verbatim "
        "(scripts/eval64_orderflow_realized_vol_markpath_feasible.py: "
        "min_surface_snapshots=1000, min_surface_instruments=100, "
        "min_surface_bars_5m=1000, min_option_trades=2000, "
        "min_of_instruments=150, min_of_span_seconds=82000, "
        "min_of_bars_5m=240, min_perp_bars_5m=1000, "
        "min_perp_span_seconds=300000, min_common_bars=240, "
        "min_underlyings=2), applied to BOTH BTC and ETH, reused via "
        "e64._underlying_floor_strict, NOT weakened. This governs the EVAL-67/68/69 "
        "ladder and is untouched here. Below this floor the campaign seals "
        "BLOCKED, never NO-GO."
    ),
}

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "src/analytics/strategy_evaluation.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval64_orderflow_realized_vol_markpath_feasible.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval74_surface_term_structure_predictiveness.py",
    "scripts/eval135_cross_asset_term_slope_spillover_risk_reversal_net_of_cost.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval135_cross_asset_term_slope_spillover_risk_reversal_net_of_cost.py "
    "tests/test_eval135_cross_asset_term_slope_spillover_risk_reversal_net_of_cost.py",
    "python3 -m pytest -q tests/test_eval135_cross_asset_term_slope_spillover_risk_reversal_net_of_cost.py",
    "# no acquisition, no network — consume the already-acquired real captures:",
    "python3 scripts/eval135_cross_asset_term_slope_spillover_risk_reversal_net_of_cost.py "
    "--capture-dir data/raw/eval68 --no-write",
    "python3 scripts/eval135_cross_asset_term_slope_spillover_risk_reversal_net_of_cost.py "
    "--capture-dir data/raw/eval68 --seal --task-label "
    "EVAL135-CROSS-ASSET-TERM-SLOPE-SPILLOVER-RISK-REVERSAL-NET-OF-COST",
)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite(x: Any, default: float = 0.0) -> float:
    return e71._finite(x, default)


# ---------------------------------------------------------------------------
# Cross-asset term-slope alignment (mirror EVAL-122 build_cross_section, using
# EVAL-74 _term_bars so ``term_slope`` is present).
# ---------------------------------------------------------------------------
def build_cross_section(
    captures: Dict[str, Dict[str, Any]], *, bar_seconds: float
) -> Dict[str, Any]:
    """Align two underlyings' causal term-structure bars on their common grid.

    Returns ``{"maps": {inst: {bar_open_ms: bar}}, "common": [bar_open_ms...],
    "bar_seconds": float, "underlyings": [..]}``. ``common`` is the sorted
    intersection of bar-open buckets present in *both* underlyings.
    """
    maps: Dict[str, Dict[int, Dict[str, Any]]] = {}
    for inst, cap in captures.items():
        bars = e74._term_bars(cap, bar_seconds=bar_seconds)
        maps[inst] = {int(b["bar_open_ms"]): b for b in bars}
    insts = sorted(maps)
    if len(insts) < 2:
        common: List[int] = []
    else:
        common = sorted(set.intersection(*[set(maps[i]) for i in insts]))
    return {
        "maps": maps,
        "common": common,
        "bar_seconds": float(bar_seconds),
        "underlyings": insts,
    }


def _term_slope_on_common(cs: Dict[str, Any], inst: str) -> List[Optional[float]]:
    maps = cs["maps"][inst]
    return [maps[int(m)].get(SURFACE_SIGNAL) for m in cs["common"]]


# ---------------------------------------------------------------------------
# Risk-reversal trade construction (sealed EVAL-76 build, reused verbatim),
# driven by the cross-asset z-scored term_slope signal instead of surface skew.
# ---------------------------------------------------------------------------
def _pick_risk_reversal_quotes(
    quotes: Sequence[Dict[str, Any]], spot: float, expiry: str,
) -> Optional[Dict[str, Any]]:
    """Select the nearest **OTM** call and **OTM** put in one expiry, both with a
    real positive mark. Never fabricates."""
    want = str(expiry)[:10]
    calls: List[Dict[str, Any]] = []
    puts: List[Dict[str, Any]] = []
    for q in quotes:
        exp = e57._expiry_date(q.get("expiry"))
        if exp != want:
            continue
        try:
            strike = float(q.get("strike") or 0.0)
            mark = float(q.get("mark") or 0.0)
        except (TypeError, ValueError):
            continue
        if strike <= 0.0 or mark <= 0.0 or spot <= 0.0:
            continue
        ot = str(q.get("option_type") or "").lower()
        if ot == "call" and strike > spot:
            calls.append(q)
        elif ot == "put" and strike < spot:
            puts.append(q)
    if not calls or not puts:
        return None
    call = min(calls, key=lambda q: float(q.get("strike") or 0.0))
    put = max(puts, key=lambda q: float(q.get("strike") or 0.0))

    def leg_spread(leg: Dict[str, Any]) -> float:
        return (e61._finite(leg.get("ask"), 0.0) - e61._finite(leg.get("bid"), 0.0)) * spot

    spread_usd = leg_spread(call) + leg_spread(put)
    return {
        "call": call, "put": put,
        "strike_call": float(call.get("strike") or 0.0),
        "strike_put": float(put.get("strike") or 0.0),
        "valid": True, "spread_usd": float(spread_usd),
    }


def _leg_iv_and_greeks(q: Dict[str, Any], spot: float, state_time: datetime, key_hint: str) -> Optional[Dict[str, float]]:
    return e57._iv_and_greeks(
        e61._finite(q.get("mark"), 0.0), e61._finite(q.get("bid"), 0.0),
        e61._finite(q.get("ask"), 0.0), spot, e61._finite(q.get("strike"), 0.0),
        q.get("expiry"), state_time,
        str(q.get("option_type") or key_hint).lower(),
    )


def build_risk_reversal_states(
    captures: Dict[str, Dict[str, Any]],
    *,
    target_inst: str,
    bar_seconds: float,
    sig_z: List[float],
) -> List[Dict[str, Any]]:
    """Per-bar causal risk-reversal states for ``target_inst`` driven by the
    cross-asset z-scored term_slope signal (side/exposure).

    Identical state schema to sealed EVAL-76 ``build_risk_reversal_states`` so
    ``e62.markpath_returns`` consumes it verbatim, except the driving signal is
    the cross-asset term-slope z-score of the OTHER underlying (aligned to the
    common grid at index ``k``) rather than the target's surface skew, and the
    signal is read off the common cross-section grid (bar ``k`` -> state at
    bar-end ``k+grid``).
    """
    cs = build_cross_section(captures, bar_seconds=bar_seconds)
    common = cs["common"]
    grid_ms = int(float(bar_seconds) * 1000)

    target_cap = captures[target_inst]
    snapshots = sorted(
        target_cap.get("surface", {}).get("snapshots", []) or [],
        key=lambda s: int(s.get("bar_ms") or 0),
    )
    snap_by_bar_end: Dict[int, Tuple[float, List[Dict[str, Any]]]] = {}
    for snap in snapshots:
        bm = int(snap.get("bar_ms") or 0)
        if bm <= 0:
            continue
        be = ((bm // grid_ms) + 1) * grid_ms
        spot = e61._finite(snap.get("spot"), 0.0)
        quotes = snap.get("quotes") or []
        if spot > 0.0 and quotes:
            snap_by_bar_end[be] = (spot, quotes)

    states: List[Dict[str, Any]] = []
    for k, bar_open_ms in enumerate(common):
        bar_end = bar_open_ms + grid_ms
        hit = snap_by_bar_end.get(int(bar_end))
        if hit is None:
            continue
        spot, quotes = hit
        bar_ms = int(bar_open_ms)
        if bar_ms <= 0:
            continue
        state_time = datetime.fromtimestamp(
            (bar_ms + int(e62.BAR_SECONDS) * 1000) / 1000.0, tz=timezone.utc
        )
        exp = e62._front_expiry(quotes, state_time)
        if not exp:
            continue
        pick = _pick_risk_reversal_quotes(quotes, spot, exp)
        if not pick or not pick.get("valid"):
            continue
        g_call = _leg_iv_and_greeks(pick["call"], spot, state_time, "call")
        g_put = _leg_iv_and_greeks(pick["put"], spot, state_time, "put")
        if g_call is None or g_put is None:
            continue
        rr_mark = float(
            e61._finite(pick["call"].get("mark"), 0.0)
            - e61._finite(pick["put"].get("mark"), 0.0)
        )
        rr_delta = float(g_call["delta"] - g_put["delta"])
        if abs(rr_mark) <= 1e-12:
            continue
        z = float(sig_z[k]) if k < len(sig_z) else 0.0
        side = 1 if z > 1e-9 else (-1 if z < -1e-9 else 0)
        exposure = min(abs(z), SIZE_CAP) if side != 0 else 0.0
        states.append({
            "bar_ms": int(bar_ms),
            "spot": float(spot),
            "side": int(side),
            "exposure": float(exposure),
            "straddle_delta": rr_delta,
            "straddle_mark": rr_mark,
            "spread_usd": float(pick.get("spread_usd", 0.0)),
            "signal_z": float(z),
            "strike": float(pick.get("strike_call", spot)),
            "strike_call": float(pick.get("strike_call", spot)),
            "strike_put": float(pick.get("strike_put", spot)),
            "structure": "risk_reversal",
        })
    return states


# ---------------------------------------------------------------------------
# Floor: sealed EVAL-64 floor verbatim (per underlying).
# ---------------------------------------------------------------------------
def _underlying_floor(capture: Dict[str, Any]) -> Dict[str, Any]:
    return e64._underlying_floor_strict(capture)


def campaign_floor(captures: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Sealed EVAL-64 floor verbatim, ANDed across both underlyings."""
    insts = sorted(captures)
    per_underlying = {i: _underlying_floor(captures[i]) for i in insts}
    both_present = BASELINE in captures and RELATIVE in captures
    underlyings_ok = bool(
        both_present
        and len(captures) >= int(FLOOR["min_underlyings"])
        and all(per_underlying[i]["ok"] for i in (BASELINE, RELATIVE))
    )
    return {
        "underlyings": insts,
        "per_underlying": per_underlying,
        "underlyings_ok": underlyings_ok,
        "checks": {
            "underlyings_ok": underlyings_ok,
        },
        "ok": bool(underlyings_ok),
    }


# ---------------------------------------------------------------------------
# Per-config evaluation (cross-asset term_slope spillover -> risk reversal net-of-cost)
# ---------------------------------------------------------------------------
def _eval_one_config(
    captures: Dict[str, Dict[str, Any]],
    *,
    target_inst: str,
    bar_seconds: float,
) -> Dict[str, Any]:
    cs = build_cross_section(captures, bar_seconds=bar_seconds)
    n_common = len(cs["common"])
    other_inst = RELATIVE if target_inst == BASELINE else BASELINE

    other_slope = _term_slope_on_common(cs, other_inst)
    sig_filled = e71._forward_fill(other_slope)
    sig_z = e61.expanding_zscore(sig_filled, ZWINDOW)

    states = build_risk_reversal_states(
        captures, target_inst=target_inst, bar_seconds=bar_seconds, sig_z=sig_z
    )
    n_states = len(states)
    base = {
        "target_underlying": target_inst,
        "signal_underlying": other_inst,
        "signal": SURFACE_SIGNAL,
        "target": TARGET,
        "bar_seconds": float(bar_seconds),
        "n_common_bars": n_common,
        "n_states": n_states,
    }
    if n_states < MIN_STATES_PER_CONFIG:
        base.update({
            "mean_return": float("nan"), "permutation_p": 1.0,
            "bootstrap_ci": [float("nan"), float("nan"), float("nan")],
            "nonzero_positions": 0, "pass": False,
            "reason": "insufficient_states",
        })
        return base

    sr = e62.markpath_returns(states, hedge_fee_bps=HEDGE_FEE_BPS)
    rets = sr["returns"]
    n_returns = len(rets)
    if n_returns < MIN_RETURNS_PER_CONFIG:
        base.update({
            "mean_return": float("nan"), "permutation_p": 1.0,
            "bootstrap_ci": [float("nan"), float("nan"), float("nan")],
            "nonzero_positions": int(sr.get("nonzero", 0)), "pass": False,
            "reason": "insufficient_returns",
        })
        return base

    mean_return = e62._mean(rets)
    flat = [0.0] * n_returns
    perm = permutation_test(
        rets, flat, statistic=e62._mean, n_permutations=PERMUTATION_PERMS,
        paired=True, seed=SEED,
    )
    boot = block_bootstrap_ci(
        rets, statistic=e62._mean, n_bootstrap=BOOTSTRAP_RESAMPLES,
        block_size=BOOTSTRAP_BLOCK, seed=SEED,
    )
    perm_p = e62._finite(perm.get("p_value"), 1.0)
    ci_low = e62._finite(boot[1], 0.0)
    ci_high = e62._finite(boot[2], 0.0)
    nonzero = int(sr.get("nonzero", 0))
    passed = bool(
        mean_return > 0.0
        and ci_low > 0.0
        and perm_p < 0.05
        and nonzero > 0
    )
    base.update({
        "n_returns": n_returns,
        "nonzero_positions": nonzero,
        "n_hedge_rebalances": sr.get("n_hedge_rebalances", 0),
        "n_side_flips": sr.get("n_side_flips", 0),
        "mean_return": float(mean_return),
        "max_drawdown": e62._max_drawdown(rets),
        "kill_switch_breach": e62.kill_switch_breach(e62._max_drawdown(rets)),
        "permutation_p": perm_p,
        "bootstrap_ci": [boot[0], ci_low, ci_high],
        "pass": passed,
        "reason": "ok" if passed else "gate_fail",
    })
    return base


# ---------------------------------------------------------------------------
# Capture selection / orchestration
# ---------------------------------------------------------------------------
def _select_captures(capture_dir: str) -> List[Dict[str, Any]]:
    all_caps = e61._capture_inventory(capture_dir)
    best: Dict[str, Dict[str, Any]] = {}
    for c in all_caps:
        inst = c.get("underlying", "UNKNOWN")
        score = len(c.get("option_trades", []) or [])
        prev = best.get(inst)
        if prev is None or score > len(prev.get("option_trades", []) or []):
            best[inst] = c
    order = [k for k in ("BTC", "ETH") if k in best] + [k for k in sorted(best) if k not in ("BTC", "ETH")]
    return [best[k] for k in order]


def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-135",
        "title": "Cross-asset term-structure slope spillover (other asset's z-scored "
                 "term_slope) -> signal-timed delta-hedged risk reversal with "
                 "correct mark-path net-of-cost P&L: traded-form monetization "
                 "falsification at the sealed EVAL-64 floor",
        "extends": "EVAL-122 (cross-asset term_slope spillover signal, GO) + "
                   "EVAL-76 (risk-reversal trade construction, mark-path P&L) + "
                   "EVAL-64 (feasible floor verbatim) + EVAL-65/62 inference",
        "supersedes": "EVAL-124 (sealed BLOCKED on an implementation fault: "
                      "e61._expiry_date AttributeError aborted every config, so no "
                      "economic verdict was measured). EVAL-135 is the corrected "
                      "append-only successor with the identical floor and GO bar; "
                      "no new acquisition",
        "capture_dir": str(capture_dir),
        "surface_signal": SURFACE_SIGNAL,
        "target": TARGET,
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "cross_section": {
            "baseline": BASELINE,
            "relative": RELATIVE,
            "spillover_signal": "signal_k = z(term_slope[OTHER](k))  "
                                "(other asset's near-minus-far ATM IV slope, causal, expanding-z)",
        },
        "signal": "causal per-bar near-minus-far ATM IV term slope of the OTHER "
                  "underlying (e74._term_bars term_slope), aligned to the common "
                  "BTC-vs-ETH bar grid (build_cross_section), forward-filled and "
                  "expanding-zscored end-of-bar k (reused e71._forward_fill / "
                  "e61.expanding_zscore)",
        "traded_form": "risk reversal (front expiry; nearest OTM call + nearest OTM put; "
                       "IV backed out of the real mark via EVAL-57 helpers) with the "
                       "EVAL-62 mark-path net-of-cost P&L on the signed long-call/"
                       "short-put aggregate mark/delta: delta-hedge + half real 2-leg "
                       "spread + hedge fee, spot-normalized",
        "position": "side_k = sign(z_k); exposure_k = min(|z_k|, SIZE_CAP); causal "
                    "decision at bar k; z_k = expanding-z of the causal cross-asset "
                    "term_slope of the OTHER underlying",
        "cost_model": "net-of-cost: hedge_fee_bps on |dHedge|*S; half real 2-leg spread "
                      "at entry/exit; full spread on side flip (identical to EVAL-57/62/76)",
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
            "zwindow": ZWINDOW,
            "min_states_per_config": MIN_STATES_PER_CONFIG,
            "min_returns_per_config": MIN_RETURNS_PER_CONFIG,
        },
        "kill_switch_max_dd": KILL_SWITCH_MAX_DD,
        "go_bar": (
            "GO only if, on BOTH BTC and ETH and at least one config, net-of-cost "
            "mean_return > 0, block-bootstrap 95% CI lower > 0, directional "
            "permutation p < 0.05, nonzero positions > 0, and pooled BH-FDR "
            "rejects that config; else NO-GO CONFIRMED (PASS); below the sealed "
            "EVAL-64 floor -> BLOCKED (never NO-GO)."
        ),
        "floor": dict(FLOOR),
        "floor_source": "sealed EVAL-64 feasible floor verbatim "
                        "(scripts/eval64_orderflow_realized_vol_markpath_feasible.py)",
        "data_availability": {
            "note": "uses already-acquired real on-disk three-way captures (option trades "
                    "with iv/strike/expiry + perp candles + surface snapshots); no new "
                    "acquisition, no network, public read-only only",
            "capture_dir": str(capture_dir),
        },
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def run_eval135(
    *,
    capture_dir: str = "data/raw/eval68",
    write: bool = True,
    task_label: str = "EVAL135-CROSS-ASSET-TERM-SLOPE-SPILLOVER-RISK-REVERSAL-NET-OF-COST",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    selected = _select_captures(str(capture_dir_abs))
    captures = {str(c.get("underlying")): c for c in selected}

    floor = campaign_floor(captures)
    floor_ok = bool(len(captures) >= int(FLOOR["min_underlyings"]) and floor["ok"])

    per_config: List[Dict[str, Any]] = []
    errors: List[str] = []
    for target_inst in (BASELINE, RELATIVE):
        for bar_s in GRID_BAR_SECONDS:
            try:
                res = _eval_one_config(
                    captures,
                    target_inst=target_inst,
                    bar_seconds=bar_s,
                )
            except BaseException as exc:  # noqa: BLE001
                other_inst = RELATIVE if target_inst == BASELINE else BASELINE
                errors.append(
                    f"{target_inst}<-{other_inst}::{SURFACE_SIGNAL}::bar{bar_s}: {exc!r}"
                )
                continue
            per_config.append(res)

    p_values = {
        f"{r['target_underlying']}<-{r['signal_underlying']}::{r['signal']}::bar{r['bar_seconds']}": _finite(r.get("permutation_p"), 1.0)
        for r in per_config if r.get("n_returns", 0) > 0
    }
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}
    rejected = set(bh.get("rejected") or [])

    pass_configs: List[str] = []
    for r in per_config:
        key = (
            f"{r['target_underlying']}<-{r['signal_underlying']}::{r['signal']}"
            f"::bar{r['bar_seconds']}"
        )
        if r.get("pass") and key in rejected:
            pass_configs.append(key)

    by_target: Dict[str, List[Dict[str, Any]]] = {}
    for r in per_config:
        by_target.setdefault(r.get("target_underlying", "?"), []).append(r)

    target_summary: List[Dict[str, Any]] = []
    for inst, rows in by_target.items():
        valid = [r for r in rows if r.get("n_returns", 0) > 0]
        best = max(valid, key=lambda r: _finite(r.get("mean_return"), -1e9)) if valid else None
        pass_configs_t: List[str] = []
        for r in valid:
            key = (
                f"{r['target_underlying']}<-{r['signal_underlying']}::{r['signal']}"
                f"::bar{r['bar_seconds']}"
            )
            if r.get("pass") and key in rejected:
                pass_configs_t.append(key)
        target_summary.append({
            "target_underlying": inst,
            "signal_underlying": RELATIVE if inst == BASELINE else BASELINE,
            "n_configs": len(rows),
            "best_mean_return": _finite(best.get("mean_return"), 0.0) if best else 0.0,
            "best_config": (
                f"{best['signal_underlying']}->{best['target_underlying']}::"
                f"{best['signal']}::bar{best['bar_seconds']}"
                if best else "n/a"
            ),
            "n_pass": len(pass_configs_t),
            "pass_configs": pass_configs_t,
            "any_pass": bool(pass_configs_t),
        })

    all_pass = bool(target_summary) and all(s["any_pass"] for s in target_summary)
    go = bool(floor_ok and all_pass and len(rejected) >= 1)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = (
        "EVAL_135_CROSS_ASSET_TERM_SLOPE_SPILLOVER_RISK_REVERSAL_NET_OF_COST" if floor_ok
        else "EVAL_135_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "cross-asset z-scored term_slope spillover timed delta-hedged risk "
            "reversal with correct mark-path net-of-cost P&L (EVAL-76 trade "
            "construction + EVAL-62 cost model) at the sealed EVAL-64 floor, on "
            "real on-disk captures"
            if floor_ok else "capture below the sealed EVAL-64 feasible floor; no verdict (never a NO-GO)"
        ),
        "floor_ok": bool(floor_ok),
        "capture_dir": str(capture_dir_abs),
        "underlyings": sorted(captures),
        "floor": dict(FLOOR),
        "campaign_floor": floor,
        "protocol": build_protocol(capture_dir),
        "per_config": per_config,
        "per_target": target_summary,
        "pooled": {"bh_fdr": bh, "all_targets_pass": all_pass, "campaign_state": campaign_state},
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
    p = report.get("protocol", {})
    return {
        "prereg_id": PREREG_ID,
        "generated_at": report.get("generated_at"),
        "task": report.get("task"),
        "hypothesis": (
            "The causal near-minus-far ATM IV term slope of the OTHER underlying "
            "(cross-asset term_slope spillover, expanding-z scored) has a positive "
            "net-of-cost relationship when timed as a delta-hedged risk reversal on "
            "the target underlying, tested on real on-disk captures at the sealed "
            "EVAL-64 feasible floor."
        ),
        "extends": p.get("extends"),
        "protocol": p,
        "capture_dir": report.get("capture_dir"),
        "floor": report.get("floor", dict(FLOOR)),
    }


def _build_prereg_md(r: Dict[str, Any]) -> str:
    p = r.get("protocol", {})
    fl = p.get("floor", FLOOR)
    cs = p.get("cross_section", {})
    lines = [
        f"# {PREREG_ID} — cross-asset term_slope spillover -> risk reversal net-of-cost monetization",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Hypothesis: {r.get('hypothesis')}",
        f"- Capture dir: `{r.get('capture_dir')}`",
        f"- Extends: {p.get('extends')}",
        "",
        "## Pre-declared protocol",
        "",
        f"- Cross-asset spillover: baseline `{cs.get('baseline')}`, relative `{cs.get('relative')}`",
        f"- Spillover signal: {cs.get('spillover_signal')}",
        f"- Signal: {p.get('surface_signal')} — {p.get('signal')}",
        f"- Traded form: {p.get('traded_form')}",
        f"- Bar grid (s): {p.get('bar_seconds_grid')}",
        f"- Position: {p.get('position')}",
        f"- Cost model: {p.get('cost_model')}",
        f"- Stats: perm {p.get('stats', {}).get('permutation_perms')} / "
        f"bootstrap {p.get('stats', {}).get('bootstrap_resamples')} block {p.get('stats', {}).get('bootstrap_block')} / "
        f"BH-FDR alpha {p.get('stats', {}).get('fdr_alpha')} / seed {p.get('stats', {}).get('seed')} / "
        f"zwindow {p.get('stats', {}).get('zwindow')} / size_cap {p.get('stats', {}).get('size_cap')} / "
        f"hedge_fee_bps {p.get('stats', {}).get('hedge_fee_bps')}",
        f"- Kill-switch max-DD: {p.get('kill_switch_max_dd')}",
        "",
        "## Pre-declared GO bar",
        "",
        str(p.get("go_bar")),
        "",
        "## Pre-registered floor (sealed EVAL-64 feasible floor verbatim)",
        "",
        f"- {fl.get('note')}",
        f"- Min underlyings: {fl.get('min_underlyings')}",
        f"- Min surface snapshots/underlying: {fl.get('min_surface_snapshots_per_underlying')}",
        f"- Min surface instruments/underlying: {fl.get('min_surface_instruments_per_underlying')}",
        f"- Min surface 5m bars/underlying: {fl.get('min_surface_bars_5m_per_underlying')}",
        f"- Min option trades/underlying: {fl.get('min_option_trades_per_underlying')}",
        f"- Min OF instruments/underlying: {fl.get('min_of_instruments_per_underlying')}",
        f"- Min OF span seconds/underlying: {fl.get('min_of_span_seconds_per_underlying')}",
        f"- Min OF 5m bars/underlying: {fl.get('min_of_bars_5m_per_underlying')}",
        f"- Min perp 5m bars/underlying: {fl.get('min_perp_bars_5m_per_underlying')}",
        f"- Min perp span seconds/underlying: {fl.get('min_perp_span_seconds_per_underlying')}",
        f"- Min common bars/underlying: {fl.get('min_common_bars_per_underlying')}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    fl = r.get("campaign_floor", {})
    lines = [
        f"# {r['report_id']} — cross-asset term_slope spillover -> risk reversal net-of-cost",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Verdict: **{r.get('verdict')}**",
        f"- Verdict detail: {r.get('verdict_detail')}",
        f"- Floor OK: {r.get('floor_ok')} (underlyings {', '.join(r.get('underlyings', []))})",
        "",
        "## Per-underlying EVAL-64 feasible floor",
        "",
        "| underlying | floor ok | snapshots | instruments | surface 5m bars | option trades | OF span (s) | perp 5m bars | perp span (s) | common bars |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for inst, u in fl.get("per_underlying", {}).items():
        lines.append(
            f"| {inst} | {u.get('ok')} | {u.get('n_surface_snapshots')} | "
            f"{u.get('n_surface_instruments')} | {u.get('n_surface_bars_5m')} | "
            f"{u.get('n_option_trades')} | {u.get('of_span_seconds')} | "
            f"{u.get('n_perp_bars_5m')} | {u.get('perp_span_seconds')} | "
            f"{u.get('n_common_bars_5m')} |"
        )
    lines += ["", "## Per-target (best config by net-of-cost mean return)", "",
              "| target <- signal | configs | best mean | best config | n pass | any pass |",
              "|---|---|---|---|---|---|"]
    for s in r.get("per_target", []):
        lines.append(
            f"| {s['signal_underlying']}->{s['target_underlying']} | {s['n_configs']} | "
            f"{s['best_mean_return']:.6f} | {s['best_config']} | {s['n_pass']} | {s['any_pass']} |"
        )
    lines += ["", "## Pooled", "",
              f"- BH-FDR rejected: {r.get('pooled', {}).get('bh_fdr', {}).get('rejected')}",
              f"- All targets pass: {r.get('pooled', {}).get('all_targets_pass')}",
              f"- Campaign state: {r.get('pooled', {}).get('campaign_state')}"]
    if r.get("errors"):
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def _build_blocked_report(r: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "report_id": BLOCKED_ID,
        "generated_at": r.get("generated_at", _utc_now_iso()),
        "task": r.get("task"),
        "verdict": "BLOCKED",
        "verdict_detail": "capture below the sealed EVAL-64 feasible floor; no verdict (never a NO-GO)",
        "floor_ok": False,
        "capture_dir": r.get("capture_dir"),
        "underlyings": r.get("underlyings", []),
        "campaign_floor": r.get("campaign_floor", {}),
        "floor": r.get("floor", dict(FLOOR)),
        "errors": r.get("errors", []),
    }


def _build_blocked_md(r: Dict[str, Any]) -> str:
    fl = r.get("campaign_floor", {})
    lines = [
        f"# {BLOCKED_ID} — cross-asset term_slope spillover -> risk reversal net-of-cost: BELOW FLOOR",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Verdict: **BLOCKED**",
        f"- Capture dir: `{r.get('capture_dir')}`",
        "",
        "The capture does not meet the sealed EVAL-64 feasible floor; no net-of-cost "
        "verdict is emitted (never a NO-GO). Do NOT weaken the EVAL-64 floor, do NOT "
        "use synthetic data, and do NOT emit NO-GO on under-floor data.",
    ]
    if r.get("errors"):
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-135: cross-asset term_slope spillover -> risk reversal "
                    "net-of-cost monetization falsification at the sealed EVAL-64 floor"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval68")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument("--task-label", default="EVAL135-CROSS-ASSET-TERM-SLOPE-SPILLOVER-RISK-REVERSAL-NET-OF-COST")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval135(
            capture_dir=args.capture_dir, write=write, task_label=args.task_label
        )
    except BaseException as exc:  # noqa: BLE001
        traceback.print_exc()
        if write:
            blocked = _build_blocked_report({
                "generated_at": _utc_now_iso(), "task": args.task_label,
                "verdict": "BLOCKED",
                "capture_dir": args.capture_dir, "underlyings": [],
                "campaign_floor": {}, "floor": dict(FLOOR), "floor_ok": False,
                "errors": [repr(exc)],
            })
            e62._seal(BLOCKED_ID, blocked, _build_blocked_md)
        return 1

    print(json.dumps({
        "verdict": report.get("verdict"),
        "floor_ok": report.get("floor_ok"),
        "underlyings": report.get("underlyings"),
        "per_target": report.get("per_target"),
        "bh_fdr_rejected": report.get("pooled", {}).get("bh_fdr", {}).get("rejected"),
        "n_configs": len(report.get("per_config", [])),
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
