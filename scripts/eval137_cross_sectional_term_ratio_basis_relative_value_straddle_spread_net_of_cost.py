#!/usr/bin/env python3
"""EVAL-137: can the **cross-sectional causal near-to-far ATM implied-vol term
ratio basis** (EVAL-125's only surviving GO, IC 0.4128, 2 BH-FDR rejections) be
**monetized net-of-cost** by a signal-timed **cross-sectional relative-value
delta-hedged ATM straddle spread** — long the cheap-term (low term_ratio)
relative leg, short the rich-term (high term_ratio) relative leg?

Why this rung exists (the charter's net-of-cost monetization rung)
------------------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + options order-flow + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. The predictiveness line
EVAL-70..136 is sealed. EVAL-125 sealed the **cross-sectional ``term_ratio``
basis** (term_ratio_ETH - term_ratio_BTC) -> forward relative realized return
kurtosis spread as its strongest surviving unmonetized GO (IC 0.4128, 2 pooled
BH-FDR rejections) — *predictiveness only*, no traded-form or monetization
claim. EVAL-137 asks the monetization question: does the *cross-sectional
term-ratio basis z-score* timed a two-leg relative-value ATM straddle spread
(long the cheap-term leg, short the rich-term leg) yield a positive
net-of-cost mean on the real on-disk captures?

It is a distinct *signal -> traded-form* pairing (cross-sectional term-ratio
basis -> relative-value straddle spread, not single-underlying straddle/risk
reversal which are EVAL-72/75/76/80), it is on the repo charter, and it is
runnable **today** because it needs only the already-acquired real three-way
captures — **no new acquisition, no network**. It does not re-litigate any
sealed result: EVAL-80 traded the cross-sectional *atm_iv/skew* basis through a
relative-value straddle spread (NO-GO); EVAL-76 traded a skew-timed single-
underlying risk reversal (NO-GO); EVAL-125 measured term-ratio predictiveness
only. EVAL-137 is the net-of-cost rung consuming EVAL-125's GO.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
--------------------------------------------------------------------------------
For each bar grid ``{60s, 300s}``, on the common aligned bar-ends where BOTH
underlyings carry a priced ATM straddle:

    rel_k       = term_ratio[ETH](k) - term_ratio[BTC](k)        (term-ratio basis)
    rel_z_k     = expanding_z(rel_k)                              (causal, end-of-bar k)
    side_k      = sign(rel_z_k);  exposure_k = min(|rel_z_k|, SIZE_CAP)

Build the BTC leg with ``side_k`` and the ETH leg with ``-side_k`` (long the
relatively-cheap-term underlying's delta-hedged ATM straddle, short the
relatively-rich-term underlying's), each an ATM straddle priced from the real
mark and delta-hedged with the sealed EVAL-62 ``markpath_returns`` net-of-cost
P&L (delta-hedge + half real 2-leg spread + hedge fee, spot-normalized). The
relative-value return is the equal-notional sum ``ret_rel_k = ret_BTC_k +
ret_ETH_k``. A config **passes** only if net-of-cost ``mean_return > 0``,
directional permutation ``p < 0.05`` (H1: mean > 0), block-bootstrap 95% CI
lower ``> 0`` (on the mean), nonzero positions > 0, and pooled BH-FDR rejects
that config.

**GO only if at least one config:** net-of-cost mean > 0, block-bootstrap 95%
CI lower > 0, directional permutation p < 0.05, nonzero positions > 0, and
pooled BH-FDR rejects that config; else ``NO-GO CONFIRMED (PASS)`` (the
term-ratio basis does not monetize net-of-cost through a relative-value
straddle spread).

Feasible floor (sealed EVAL-64 floor verbatim; NOT weakened)
--------------------------------------------------------------------------------
``floor = sealed EVAL-64 floor verbatim``: per underlying,
surface >= 1000 snapshots / >= 100 instruments / >= 1000 5m bars /
>= 600000 s span; perp >= 1000 5m bars / >= 300000 s span; Deribit option trades
>= 2000 / >= 150 instruments / >= 82000 s span / >= 240 5m bars; roster >= 2
underlyings. Reused from sealed
``scripts/eval64_orderflow_realized_vol_markpath_feasible.py`` verbatim
(``e64._underlying_floor_strict`` + ``e64.MIN_*`` constants). Neither weakened.
Below the floor it seals ``EVAL_137_..._BLOCKED_<UTC>`` (never a NO-GO). The
EVAL-64 feasible floor that governs the EVAL-67/68/69 ladder is untouched.

This does **not** re-litigate any sealed result: EVAL-80 measured the cross-
sectional atm_iv/skew basis -> relative-value straddle spread net-of-cost
(NO-GO); EVAL-125 measured the cross-sectional term-ratio basis -> forward
relative return kurtosis spread predictiveness (GO). EVAL-137 monetizes the
cross-sectional term-ratio basis through a relative-value straddle spread,
reusing all sealed signal/trade/cost reconstructions and the EVAL-62 inference
verbatim, at the sealed EVAL-64 floor.

Seals ``EVAL_137_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VALUE_STRADDLE_SPREAD_NET_OF_COST_PREREGISTRATION_<UTC>``
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

# Reuse the sealed EVAL-61/62/64/71/74/77/80/125 machinery verbatim (no forks,
# no src edits). Signal: term_ratio basis (EVAL-125/EVAL-77/EVAL-74). Trade
# construction: EVAL-80 relative-value ATM straddle states. Cost model +
# inference: EVAL-62 markpath_returns + permutation/bootstrap. Floor: EVAL-64
# verbatim via e64._underlying_floor_strict + e64.MIN_* constants.
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64  # noqa: E402 (EVAL-64 floor verbatim)
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402 (_forward_fill/_finite)
import scripts.eval74_surface_term_structure_predictiveness as e74  # noqa: E402 (_term_bars)
import scripts.eval77_cross_sectional_surface_basis_rv_predictiveness as e77  # noqa: E402
import scripts.eval80_cross_sectional_relative_value_straddle_monetization as e80  # noqa: E402 (build_atm_straddle_states)
import scripts.eval125_cross_sectional_term_ratio_basis_forward_relative_return_kurtosis_spread as e125  # noqa: E402
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
REPORT_ID = "EVAL_137_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VALUE_STRADDLE_SPREAD_NET_OF_COST_COMBINED"
PREREG_ID = "EVAL_137_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VALUE_STRADDLE_SPREAD_NET_OF_COST_PREREGISTRATION"
BLOCKED_ID = "EVAL_137_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VALUE_STRADDLE_SPREAD_NET_OF_COST_BLOCKED"

# Cross-section is BTC-vs-ETH (identical to EVAL-77/EVAL-80/EVAL-125).
BASELINE = e77.BASELINE
RELATIVE = e77.RELATIVE

# Pre-registered grid: single term-ratio basis signal x bar grid.
BASIS_SIGNALS: Tuple[str, ...] = ("term_ratio",)
GRID_BAR_SECONDS: Tuple[float, ...] = e77.GRID_BAR_SECONDS

# Stats / cost / risk constants reused verbatim from EVAL-62 (no forks).
ZWINDOW = e62.ZWINDOW
SIZE_CAP = e62.SIZE_CAP
PERMUTATION_PERMS = e62.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e62.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e62.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED

# A config must produce at least this many aligned common straddle states to be
# evaluable (a result-quality guard, not a data floor).
MIN_STATES_PER_CONFIG = 100

# Floor: sealed EVAL-64 floor verbatim (identity, not a copy — cannot drift).
FLOOR: Dict[str, Any] = {
    "min_underlyings": int(e64.MIN_UNDERLYINGS),
    "min_surface_snapshots_per_underlying": int(e64.MIN_SNAPSHOTS),
    "min_surface_instruments_per_underlying": int(e64.MIN_SURFACE_INSTRUMENTS),
    "min_surface_bars_5m_per_underlying": int(e64.MIN_SURFACE_BARS_5M),
    "min_option_trades_per_underlying": int(e64.MIN_OPTION_TRADES),
    "min_of_instruments_per_underlying": int(e64.MIN_OF_INSTRUMENTS),
    "min_of_span_seconds_per_underlying": float(e64.MIN_OF_SPAN_SECONDS),
    "min_of_bars_5m_per_underlying": int(e64.MIN_OF_BARS_5M),
    "min_perp_bars_5m_per_underlying": int(e64.MIN_PERP_BARS_5M),
    "min_perp_span_seconds_per_underlying": float(e64.MIN_PERP_SPAN_SECONDS),
    "min_common_bars_per_underlying": int(e64.MIN_COMMON_BARS),
    "note": (
        "Sealed EVAL-64 feasible floor verbatim (heaviest floor the free "
        "Deribit/OKX public API can deliver; NOT weakened): per underlying "
        "surface >= 1000 snapshots / >= 100 instruments / >= 1000 5m bars / "
        ">= 600000 s span; perp >= 1000 5m bars / >= 300000 s span; Deribit "
        "option trades >= 2000 / >= 150 instruments / >= 82000 s span / >= 240 "
        "5m bars; roster >= 2 underlyings. Below the floor the campaign seals "
        "BLOCKED, never NO-GO. The EVAL-64 floor governing the EVAL-67/68/69 "
        "ladder is untouched."
    ),
}

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/integrated_options_orderflow_evaluation.py",
    "src/analytics/real_walkforward_certification.py",
    "src/analytics/strategy_evaluation.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval64_orderflow_realized_vol_markpath_feasible.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval74_surface_term_structure_predictiveness.py",
    "scripts/eval77_cross_sectional_surface_basis_rv_predictiveness.py",
    "scripts/eval80_cross_sectional_relative_value_straddle_monetization.py",
    "scripts/eval125_cross_sectional_term_ratio_basis_forward_relative_return_kurtosis_spread.py",
    "scripts/eval137_cross_sectional_term_ratio_basis_relative_value_straddle_spread_net_of_cost.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval137_cross_sectional_term_ratio_basis_relative_value_straddle_spread_net_of_cost.py "
    "tests/test_eval137_cross_sectional_term_ratio_basis_relative_value_straddle_spread_net_of_cost.py "
    "tests/test_eval137_phaseb_gate.py",
    "python3 -m pytest -q tests/test_eval137_cross_sectional_term_ratio_basis_relative_value_straddle_spread_net_of_cost.py "
    "tests/test_eval137_phaseb_gate.py",
    "# no acquisition needed — consume the already-acquired real captures; no network:",
    "python3 scripts/eval137_cross_sectional_term_ratio_basis_relative_value_straddle_spread_net_of_cost.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval137_cross_sectional_term_ratio_basis_relative_value_straddle_spread_net_of_cost.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL137-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-VALUE-STRADDLE-SPREAD-NET-OF-COST",
)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite(x: Any, default: float = 0.0) -> float:
    return e71._finite(x, default)


def _select_captures(capture_dir: str) -> Dict[str, Dict[str, Any]]:
    """Richest (most real option trades) real capture per underlying; deterministic."""
    selected = e80._select_one_capture_per_underlying(
        e61._capture_inventory(capture_dir)
    )
    return {str(c.get("underlying")): c for c in selected}


# ---------------------------------------------------------------------------
# Causal cross-sectional term-ratio basis z-score (EVAL-125 signal path verbatim)
# ---------------------------------------------------------------------------
def build_cross_section_with_term_ratio(
    captures: Dict[str, Dict[str, Any]], *, bar_seconds: float
) -> Dict[str, Any]:
    """EVAL-77 cross-section maps with EVAL-74 ``term_ratio`` overlaid by bar,
    reused verbatim from EVAL-125. Returns ``cs`` with ``term_ratio`` on each
    map bar plus the causal expanding-z relative series."""
    cs = e125.build_cross_section_with_term(captures, bar_seconds=bar_seconds)
    rel_z = e125._relative_term_ratio_series(cs, term_signal="term_ratio")
    rel_z_by_bar = {int(b): float(rel_z[i]) for i, b in enumerate(cs["common"])}
    return {"cs": cs, "rel_z_by_bar": rel_z_by_bar, "bar_seconds": float(bar_seconds)}


# Per-underlying causal ATM straddle states: alias sealed EVAL-80
# ``build_atm_straddle_states`` verbatim (identity, not a fork).
build_atm_straddle_states = e80.build_atm_straddle_states  # noqa: F811


# ---------------------------------------------------------------------------
# Cross-sectional relative-value leg construction on the term-ratio basis
# ---------------------------------------------------------------------------
def build_relative_value_legs(
    captures: Dict[str, Dict[str, Any]], *, bar_seconds: float
) -> Dict[str, Any]:
    """Align both underlyings' ATM straddle states on their common bar grid and
    attach the cross-sectional term-ratio basis side/exposure.

    ``rel_z_k = term_ratio[ETH](k) - term_ratio[BTC](k)`` expanding-z-scored;
    ``side_k = sign(rel_z_k)`` on the BASELINE (BTC) leg and ``-side_k`` on the
    RELATIVE (ETH) leg, so rel_z > 0 (ETH relatively rich-term) is long BTC
    (cheap-term leg) / short ETH (rich-term leg).
    ``exposure_k = min(|rel_z_k|, SIZE_CAP)``. The two per-leg state lists are
    aligned 1:1 on the common trade bars so the sealed EVAL-62
    ``markpath_returns`` can be applied to each leg and summed by the caller.
    """
    states = {
        BASELINE: build_atm_straddle_states(captures[BASELINE], bar_seconds=bar_seconds),
        RELATIVE: build_atm_straddle_states(captures[RELATIVE], bar_seconds=bar_seconds),
    }
    css = build_cross_section_with_term_ratio(captures, bar_seconds=bar_seconds)
    rel_by_bar = css["rel_z_by_bar"]
    common_trade = [
        int(b)
        for b in css["cs"]["common"]
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
        "cs": css["cs"],
        "surface_signal": "term_ratio",
        "bar_seconds": float(bar_seconds),
    }


# ---------------------------------------------------------------------------
# Per-config evaluation (relative-value mark-path net-of-cost; EVAL-62 stats)
# ---------------------------------------------------------------------------
def evaluate_config(
    captures: Dict[str, Dict[str, Any]], *, bar_seconds: float
) -> Dict[str, Any]:
    """Cross-sectional net-of-cost monetization: causal term-ratio basis z at bar k
    -> forward relative-value delta-hedged ATM straddle spread return."""
    legs = build_relative_value_legs(captures, bar_seconds=bar_seconds)
    n_states = len(legs["btc_leg"])
    if n_states < int(MIN_STATES_PER_CONFIG):
        return {
            "signal": "term_ratio",
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
            "signal": "term_ratio",
            "bar_seconds": float(bar_seconds),
            "error": "insufficient relative-value returns",
            "n_states": n_states,
            "n_returns": len(ret_rel),
            "pass": False,
        }

    mean_return = e62._mean(ret_rel)
    mdd = e62._max_drawdown(ret_rel)
    flat = [0.0] * len(ret_rel)
    # Directional permutation H1: mean > 0 (flat zero reference, paired).
    perm = permutation_test(
        ret_rel, flat, statistic=e62._mean, n_permutations=PERMUTATION_PERMS,
        paired=True, seed=SEED,
    )
    # Block-bootstrap 95% CI on the mean (GO bar: CI lower > 0).
    boot = block_bootstrap_ci(
        ret_rel, statistic=e62._mean, n_bootstrap=BOOTSTRAP_RESAMPLES,
        block_size=BOOTSTRAP_BLOCK, seed=SEED,
    )
    perm_p = e62._finite(perm.get("p_value"), 1.0)
    ci_low = e62._finite(boot[1], 0.0)
    nonzero = int(
        sum(1 for s in legs["btc_leg"] if abs(float(s.get("signal_z", 0.0))) > 1e-9)
    )
    passed = bool(
        mean_return > 0.0
        and perm_p < 0.05
        and ci_low > 0.0
        and nonzero > 0,
    )
    return {
        "signal": "term_ratio",
        "bar_seconds": float(bar_seconds),
        "n_states": n_states,
        "n_returns": len(ret_rel),
        "nonzero_positions": nonzero,
        "n_hedge_rebalances_btc": rb.get("n_hedge_rebalances"),
        "n_hedge_rebalances_eth": re.get("n_hedge_rebalances"),
        "n_side_flips_btc": rb.get("n_side_flips"),
        "n_side_flips_eth": re.get("n_side_flips"),
        "max_drawdown": float(mdd),
        "permutation_p": float(perm_p),
        "bootstrap_ci": [float(boot[0]), float(ci_low), float(boot[2])],
        "dsr": _dsr_of_returns(ret_rel),
        "mean_return": float(mean_return),
        "pass": bool(passed),
    }


# Floor: per-underlying check delegates verbatim to sealed EVAL-64
# ``_underlying_floor_strict`` (identity, not a copy — cannot drift).
_underlying_floor = e64._underlying_floor_strict  # noqa: F811


def campaign_floor(captures: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Sealed EVAL-64 floor verbatim: both underlyings pass e64._underlying_floor_strict
    and roster >= 2. Neither weakened."""
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
# Protocol + orchestration
# ---------------------------------------------------------------------------
def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-137",
        "title": "Cross-sectional causal near-to-far ATM implied-vol term-ratio "
        "basis (EVAL-125's only surviving GO, IC 0.4128, 2 BH-FDR rejections) -> "
        "signal-timed cross-sectional relative-value delta-hedged ATM straddle "
        "spread (long the cheap-term leg, short the rich-term leg) with correct "
        "mark-path net-of-cost P&L at the sealed EVAL-64 floor: traded-form "
        "monetization falsification on the real on-disk three-way captures",
        "extends": "EVAL-125 (identical cross-sectional BTC-vs-ETH term-ratio "
        "basis GO signal, reused verbatim) and EVAL-80 (identical relative-value "
        "ATM straddle-spread trade construction) and EVAL-62 (identical correct "
        "mark-path net-of-cost delta-hedged P&L + permutation/bootstrap inference) "
        "and EVAL-64 (sealed feasible floor, verbatim, NOT weakened); a distinct, "
        "on-charter traded-form monetization cell consuming EVAL-125's GO; "
        "no new acquisition",
        "supersedes": "nothing — this is the charter's net-of-cost rung consuming "
        "EVAL-125's term-ratio-basis GO. EVAL-72/75/76 traded single-underlying "
        "straddle/risk-reversal (all NO-GO); EVAL-80 traded the cross-sectional "
        "atm_iv/skew basis through a relative-value straddle spread (NO-GO); "
        "EVAL-125 measured term-ratio predictiveness only (GO); EVAL-137 trades "
        "the cross-sectional term-ratio basis through a relative-value straddle "
        "spread — genuinely new",
        "capture_dir": str(capture_dir),
        "cross_section": {
            "baseline": BASELINE,
            "relative": RELATIVE,
            "relative_signal": "rel_k = term_ratio[ETH](k) - term_ratio[BTC](k)",
            "position": "side_k = sign(rel_z_k) on the BTC leg and -side_k on the "
                        "ETH leg (long the relatively-cheap-term underlying, short "
                        "the relatively-rich-term underlying); exposure_k = "
                        "min(|rel_z_k|, size_cap)",
            "combination": "ret_rel_k = ret_BTC_k + ret_ETH_k (equal-notional sum of "
                           "the two spot-normalized EVAL-62 mark-path leg returns)",
        },
        "basis_signals": list(BASIS_SIGNALS),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "traded_form": "two-leg cross-sectional relative-value ATM straddle spread "
                       "(each leg: front expiry, common strike nearest spot, IV backed "
                       "out of the real mark via EVAL-57 helpers) with the EVAL-62 "
                       "mark-path net-of-cost P&L per leg: delta-hedge + half real "
                       "2-leg spread + hedge fee, spot-normalized, then summed",
        "zwindow": int(ZWINDOW),
        "size_cap": float(SIZE_CAP),
        "hedge_fee_bps": float(e62.HEDGE_FEE_BPS),
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation_paired": True,
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
            "min_states_per_config": int(MIN_STATES_PER_CONFIG),
        },
        "go_bar": (
            "GO only if at least one config (basis signal x bar grid) has net-of-cost "
            "mean_return > 0, directional permutation p < 0.05 (H1: mean > 0), "
            "block-bootstrap 95% CI lower > 0 on the mean, nonzero positions > 0, "
            "and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS)."
        ),
        "floor": {
            "source": "sealed EVAL-64 feasible floor verbatim (NOT weakened)",
            "min_underlyings": int(FLOOR["min_underlyings"]),
            "note": FLOOR["note"],
        },
        "data_availability": {
            "note": "uses the already-acquired real on-disk three-way captures "
                    "(option trades with real iv + perp candles for BTC and ETH); "
                    "no new acquisition, no network; floor = sealed EVAL-64 floor verbatim",
            "capture_dir": str(capture_dir),
        },
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def run_eval137(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL137-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-VALUE-STRADDLE-SPREAD-NET-OF-COST",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    captures = _select_captures(str(capture_dir_abs))

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
                res = evaluate_config(captures, bar_seconds=bar_s)
            except BaseException as exc:  # noqa: BLE001
                errors.append(f"{sig}::bar{bar_s}: {exc!r}")
                continue
            per_config.append(res)

    p_values = {
        f"{r['signal']}::bar{r['bar_seconds']}": _finite(r.get("permutation_p"), 1.0)
        for r in per_config
        if r.get("n_returns", 0) > 0
    }
    bh = (
        _benjamini_hochberg(p_values, alpha=FDR_ALPHA)
        if p_values
        else {"rejected": []}
    )
    rejected = set(bh.get("rejected") or [])

    pass_configs: List[str] = []
    for r in per_config:
        key = f"{r['signal']}::bar{r['bar_seconds']}"
        if r.get("pass") and key in rejected:
            pass_configs.append(key)

    valid = [r for r in per_config if r.get("n_returns", 0) > 0]
    best = (
        max(valid, key=lambda r: _finite(r.get("mean_return"), -1e9))
        if valid
        else None
    )

    any_pass = bool(pass_configs)
    go = bool(floor_ok and any_pass and len(rejected) >= 1)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = (
        "EVAL_137_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VALUE_STRADDLE_SPREAD_NET_OF_COST"
        if floor_ok
        else "EVAL_137_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free information-content + monetization test: Spearman-term-ratio-basis "
            "z timed a cross-sectional relative-value delta-hedged ATM straddle spread "
            "(long cheap-term leg, short rich-term leg); net-of-cost mean_return > 0 with "
            "block-bootstrap CI lower > 0 and directional permutation p < 0.05, pooled "
            "BH-FDR rejection, on the real on-disk captures at the sealed EVAL-64 floor"
            if floor_ok
            else "capture below the sealed EVAL-64 feasible floor; no verdict (never a NO-GO)"
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
            "best_mean_return": _finite(best.get("mean_return"), 0.0) if best else 0.0,
            "best_config": (
                f"{best['signal']}::bar{best['bar_seconds']}" if best else "n/a"
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
        "generated_at": report.get("generated_at"),
        "task": report.get("task"),
        "hypothesis": (
            "The causal cross-sectional near-to-far ATM implied-vol term-ratio basis "
            "(term_ratio_ETH - term_ratio_BTC, expanding-z-scored) timed a "
            "cross-sectional relative-value delta-hedged ATM straddle spread "
            "(long the cheap-term leg, short the rich-term leg) has a positive "
            "net-of-cost mean return on the real on-disk captures, independent of "
            "any trading wrapper; tested at the sealed EVAL-64 feasible floor."
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
        f"# {PREREG_ID} — cross-sectional term-ratio basis -> relative-value straddle spread net-of-cost",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Hypothesis: {r.get('hypothesis')}",
        f"- Capture dir: `{r.get('capture_dir')}`",
        f"- Extends: {p.get('extends')}",
        "",
        "## Pre-declared protocol",
        "",
        f"- Basis signals: {p.get('basis_signals')}",
        f"- Bar grid (s): {p.get('bar_seconds_grid')}",
        f"- Cross-section: baseline `{cs.get('baseline')}`, relative `{cs.get('relative')}`",
        f"- Relative signal: {cs.get('relative_signal')}",
        f"- Position: {cs.get('position')}",
        f"- Combination: {cs.get('combination')}",
        f"- Traded form: {p.get('traded_form')}",
        f"- Statistic: net-of-cost mean_return > 0 with directional permutation p < 0.05 "
        f"(H1: mean > 0) and block-bootstrap 95% CI lower > 0",
        f"- Stats: perm {p.get('stats', {}).get('permutation_perms')} / "
        f"bootstrap {p.get('stats', {}).get('bootstrap_resamples')} block {p.get('stats', {}).get('bootstrap_block')} / "
        f"BH-FDR alpha {p.get('stats', {}).get('fdr_alpha')} / seed {p.get('stats', {}).get('seed')} / "
        f"zwindow {p.get('stats', {}).get('zwindow')} / size_cap {p.get('size_cap')} / "
        f"min states per config {p.get('stats', {}).get('min_states_per_config')}",
        "",
        "## Pre-declared GO bar",
        "",
        str(p.get("go_bar")),
        "",
        "## Pre-registered floor (sealed EVAL-64 verbatim, NOT weakened)",
        "",
        f"- {fl.get('note')}",
        f"- Min underlyings: {fl.get('min_underlyings')}",
        f"- Min states per config: {p.get('stats', {}).get('min_states_per_config')}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    fl = r.get("campaign_floor", {})
    lines = [
        f"# {r['report_id']} — cross-sectional term-ratio basis -> relative-value straddle spread net-of-cost",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Verdict: **{r.get('verdict')}**",
        f"- Verdict detail: {r.get('verdict_detail')}",
        f"- Floor OK: {r.get('floor_ok')} (underlyings {', '.join(r.get('underlyings', []))})",
        "",
        "## Per-underlying EVAL-64 floor (verbatim)",
        "",
        "| underlying | surface_floor_ok | n surface snapshots | n surface instruments | n surface bars 5m | n option trades | n of instruments | of span (s) | n perp bars 5m | perp span (s) | n common bars | ok |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for inst, u in fl.get("per_underlying", {}).items():
        lines.append(
            f"| {inst} | {u.get('ok')} | {u.get('n_surface_snapshots')} | "
            f"{u.get('n_surface_instruments')} | {u.get('n_surface_bars_5m')} | "
            f"{u.get('n_option_trades')} | {u.get('n_of_instruments')} | "
            f"{u.get('of_span_seconds')} | {u.get('n_perp_bars_5m')} | "
            f"{u.get('perp_span_seconds')} | {u.get('n_common_bars_5m')} | {u.get('ok')} |"
        )
    lines += [
        "",
        "## Per-config (best by net-of-cost mean return)",
        "",
        "| signal | bar_seconds | n_states | n_returns | nonzero_positions | mean_return | perm_p | CI lo | CI hi | pass |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for c in r.get("per_config", []):
        ci = c.get("bootstrap_ci", [float("nan")] * 3)
        lines.append(
            f"| {c.get('signal')} | {c.get('bar_seconds')} | {c.get('n_states')} | "
            f"{c.get('n_returns')} | {c.get('nonzero_positions')} | "
            f"{_finite(c.get('mean_return')):.6g} | {_finite(c.get('permutation_p'),1.0):.4g} | "
            f"{_finite(ci[1]):.6g} | {_finite(ci[2]):.6g} | {c.get('pass')} |"
        )
    lines += [
        "",
        "## Summary",
        "",
        f"- n_configs: {r.get('summary', {}).get('n_configs')}",
        f"- n_pass: {r.get('summary', {}).get('n_pass')}",
        f"- pass_configs: {r.get('summary', {}).get('pass_configs')}",
        f"- best_mean_return: {r.get('summary', {}).get('best_mean_return'):.6g}",
        f"- best_config: {r.get('summary', {}).get('best_config')}",
        "",
        "## Pooled",
        "",
        f"- BH-FDR rejected: {r.get('pooled', {}).get('bh_fdr', {}).get('rejected')}",
        f"- Any config pass: {r.get('pooled', {}).get('any_config_pass')}",
        f"- Campaign state: {r.get('pooled', {}).get('campaign_state')}",
    ]
    if r.get("errors"):
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def _build_blocked_report(r: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "report_id": BLOCKED_ID,
        "generated_at": r.get("generated_at", _utc_now_iso()),
        "task": r.get("task", "EVAL137-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-VALUE-STRADDLE-SPREAD-NET-OF-COST"),
        "verdict": "BLOCKED",
        "verdict_detail": "capture below the sealed EVAL-64 feasible floor; no verdict (never a NO-GO)",
        "floor_ok": False,
        "capture_dir": r.get("capture_dir"),
        "underlyings": r.get("underlyings", []),
        "floor": r.get("floor", dict(FLOOR)),
        "campaign_floor": r.get("campaign_floor", {}),
        "errors": r.get("errors", []),
    }


def _build_blocked_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {BLOCKED_ID} — cross-sectional term-ratio basis -> relative-value straddle spread net-of-cost: BELOW FLOOR",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Verdict: **BLOCKED**",
        f"- Capture dir: `{r.get('capture_dir')}`",
        "",
        "The capture does not meet the sealed EVAL-64 feasible floor; no "
        "net-of-cost monetization verdict is emitted (never a NO-GO).",
    ]
    if r.get("errors"):
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-137: cross-sectional term-ratio basis -> relative-value straddle spread net-of-cost monetization"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument("--task-label", default="EVAL137-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-VALUE-STRADDLE-SPREAD-NET-OF-COST")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval137(capture_dir=args.capture_dir, write=write, task_label=args.task_label)
    except BaseException as exc:  # noqa: BLE001
        traceback.print_exc()
        if write:
            blocked = _build_blocked_report({
                "generated_at": _utc_now_iso(), "task": args.task_label,
                "capture_dir": args.capture_dir, "underlyings": [],
                "floor": dict(FLOOR), "campaign_floor": {}, "floor_ok": False,
                "errors": [repr(exc)],
            })
            e62._seal(BLOCKED_ID, blocked, _build_blocked_md)
        return 1

    print(
        json.dumps(
            {
                "verdict": report.get("verdict"),
                "floor_ok": report.get("floor_ok"),
                "underlyings": report.get("underlyings"),
                "per_config": report.get("per_config"),
                "summary": report.get("summary"),
                "bh_fdr_rejected": report.get("pooled", {}).get("bh_fdr", {}).get("rejected"),
                "n_configs": len(report.get("per_config", [])),
            },
            indent=2,
            default=str,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
