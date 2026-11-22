#!/usr/bin/env python3
"""EVAL-184: surface-line traded-form net-of-cost OOS verdict (the EVAL-69 analogue
for EVAL-177/168/169) on a fresh, floor-compliant, disjoint forward capture.

Why this exists
---------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``) is
**crypto options surface + options order-flow -> tradeable, net-of-cost alpha on
REAL public data**. All predictiveness rungs EVAL-02..183 are sealed. The order-flow
line is predictive but NOT tradeable net-of-cost (EVAL-69 `NO-GO CONFIRMED (PASS)`).
The surviving tradeable alpha is exclusively on the **surface** line:

* EVAL-177: cross-asset skew -> forward variance        (GO CONFIRMED)
* EVAL-168: cross-asset atm_iv  -> forward CVaR         (GO CONFIRMED)
* EVAL-169: cross-asset term_slope -> forward CVaR      (GO CONFIRMED)

This campaign is the **traded-form net-of-cost monetization** of those surface GOs,
measured out-of-sample on a fresh disjoint forward capture (``data/raw/eval84cap``,
acquired by ``scripts/eval60_acquire_three_way.py``). It is the EVAL-69 analogue for
the surface line: each surface signal times a delta-hedged ATM straddle whose P&L is
the correct EVAL-62/EVAL-64 mark-path net-of-cost P&L, pooled across BTC+ETH with
pooled BH-FDR, the EVAL-64 feasible floor verbatim, and disjointness verbatim.

GO requires, on BOTH BTC and ETH and at least one grid config: net-of-cost Sharpe >
0, no kill-switch breach (max-DD <= 0.20), directional permutation p < 0.05,
block-bootstrap 95% CI lower > 0, nonzero positions > 0, pooled returns >= 790
(power), pooled BH-FDR rejects that config, the EVAL-64 floor met on BOTH
underlyings, and both capture windows disjoint from the sealed window.

Else: ``NO-GO CONFIRMED (PASS)`` when floor+disjoint+power but not monetizable,
``INCONCLUSIVE (UNDERPOWERED)`` when floor+disjoint but pooled returns < 790, or
``BLOCKED`` (measured, never NO-GO) when the floor/disjointness fails.

Acquisition is intentionally NOT performed here; the gate refuses to seal until a
floor-compliant disjoint capture exists at ``data/raw/eval84cap``.

Seals ``EVAL_184_SURFACE_TRADED_NETFCOST_OOS_PREREGISTRATION_<UTC>`` then
``..._COMBINED_<UTC>`` (or ``..._BLOCKED_<UTC>``). IDs match the gate's globs.
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

# Reuse the sealed EVAL-62/64 traded-form machinery + EVAL-67 disjointness +
# EVAL-71 surface bars + EVAL-74 term-structure bars verbatim (no forks, no src edits).
import scripts.eval57_vrp_net_of_cost as e57  # noqa: E402
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64  # noqa: E402
import scripts.eval67_btc_oflow_tox_rv_oos as e67  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
import scripts.eval74_surface_term_structure_predictiveness as e74  # noqa: E402
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
# Artifact IDs must match the gate's pre-registered globs (NETFCOST per gate).
REPORT_ID = "EVAL_184_SURFACE_TRADED_NETFCOST_OOS_COMBINED"
PREREG_ID = "EVAL_184_SURFACE_TRADED_NETFCOST_OOS_PREREGISTRATION"
BLOCKED_ID = "EVAL_184_SURFACE_TRADED_NETFCOST_OOS_BLOCKED"
PREREG_GLOB = PREREG_ID + "_*"
COMBINED_GLOB = REPORT_ID + "_*"
BLOCKED_GLOB = BLOCKED_ID + "_*"

DEFAULT_CAPTURE_DIR = "data/raw/eval84cap"
DEFAULT_TASK_LABEL = "EVAL184-SURFACE-TRADED-NETOFCOST-OOS"

# Disjointness: both underlyings must be disjoint from the sealed EVAL-64/65
# three-way window; earliest floor-compliant forward end is 2026-11-19T18:08:16Z.
SEALED_WINDOW_START = "2026-11-09T06:48:16Z"
SEALED_WINDOW_END = "2026-11-16T06:48:16Z"
EARLIEST_DISJOINT_CAPTURE_END = "2026-11-19T18:08:16Z"

# Surface-line GO cells: signal -> builder -> target (from EVAL-177/168/169).
SURFACE_SIGNALS: Tuple[str, ...] = ("skew", "atm_iv", "term_slope")
SIGNAL_BUILDER: Dict[str, str] = {
    "skew": "e71.build_surface_bars",
    "atm_iv": "e71.build_surface_bars",
    "term_slope": "e74._term_bars",
}
SIGNAL_TARGET: Dict[str, str] = {
    "skew": "forward_variance",
    "atm_iv": "forward_cvar",
    "term_slope": "forward_cvar",
}
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
SIGNAL_WINDOW_SECONDS: float = e71.SIGNAL_WINDOW_SECONDS

# Stats / cost / risk / size reused verbatim from EVAL-62 (no forks).
ZWINDOW = e62.ZWINDOW
SIZE_CAP = e62.SIZE_CAP
PERMUTATION_PERMS = e62.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e62.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e62.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
KILL_SWITCH_MAX_DD = e62.KILL_SWITCH_MAX_DD
HEDGE_FEE_BPS = e62.HEDGE_FEE_BPS

# A config must produce at least this many priced states to be evaluable (result
# quality guard, not a data floor).
MIN_STATES_PER_CONFIG = 100
# Power adequacy (pre-registered; mirrors EVAL-68/EVAL-69 pooled-return threshold).
MIN_POOLED_RETURNS = 790

UNDERLYINGS: Tuple[str, ...] = ("BTC", "ETH")
MIN_UNDERLYINGS = len(UNDERLYINGS)

# EVAL-64 feasible floor reused VERBATIM (never weakened).
_underlying_floor_strict = e64._underlying_floor_strict

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/integrated_options_orderflow_evaluation.py",
    "src/analytics/real_walkforward_certification.py",
    "src/analytics/strategy_evaluation.py",
    "scripts/eval57_vrp_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval64_orderflow_realized_vol_markpath_feasible.py",
    "scripts/eval67_btc_oflow_tox_rv_oos.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval74_surface_term_structure_predictiveness.py",
    "scripts/eval184_surface_traded_netofcost_oos.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval184_surface_traded_netofcost_oos.py "
    "tests/test_eval184_surface_traded_netofcost_oos.py",
    "python3 -m pytest -q tests/test_eval184_surface_traded_netofcost_oos.py",
    "# heavy work: acquire the floor-compliant disjoint capture first (~1h):",
    "python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH "
    "--days 3.7 --end <at/after 2026-11-19T18:08:16Z> --max-per-expiry 30 "
    "--out-dir data/raw/eval84cap --seal",
    "# then verify the EVAL-64 floor, dry-run green, and seal:",
    "python3 scripts/eval184_surface_traded_netofcost_oos.py "
    "--capture-dir data/raw/eval84cap --no-write",
    "python3 scripts/eval184_surface_traded_netofcost_oos.py "
    "--capture-dir data/raw/eval84cap --seal --task-label "
    "EVAL184-SURFACE-TRADED-NETOFCOST-OOS",
    "python3 scripts/eval184_phaseb_gate.py --execute  # require SEALED(0)",
)


# ---------------------------------------------------------------------------
# Small helpers (local; no src edits)
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp_for_filename(iso_ts: str) -> str:
    return iso_ts.replace("-", "").replace(":", "").replace(".", "")


def _finite(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
        return v if __import__("math").isfinite(v) else float(default)
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
        mdd = max(mdd, (peak - eq) / peak if peak > 0 else 0.0)
    return mdd


def kill_switch_breach(max_drawdown: float) -> bool:
    return float(max_drawdown) > KILL_SWITCH_MAX_DD


# ---------------------------------------------------------------------------
# Surface signal -> causal bar-end signal (EVAL-71 / EVAL-74 builders)
# ---------------------------------------------------------------------------
def surface_signal_by_bar_end(
    capture: Dict[str, Any], *, surface_signal: str, bar_seconds: float
) -> Dict[int, Optional[float]]:
    """Causal per-bar surface signal mapped to the EVAL-62 bar-end grid.

    ``skew``/``atm_iv`` come from EVAL-71 ``build_surface_bars`` (trailing near-ATM
    trade-tape IV surface); ``term_slope`` comes from EVAL-74 ``_term_bars``
    (near-minus-far ATM IV slope). Returns ``{bar_end_ms: raw_signal_or_None}``.
    """
    if surface_signal == "term_slope":
        bars = e74._term_bars(
            capture, bar_seconds=bar_seconds,
            signal_window_seconds=SIGNAL_WINDOW_SECONDS,
        )
    else:
        bars = e71.build_surface_bars(
            capture, bar_seconds=bar_seconds,
            signal_window_seconds=SIGNAL_WINDOW_SECONDS,
        )
    grid_ms = int(float(bar_seconds) * 1000)
    out: Dict[int, Optional[float]] = {}
    for b in bars:
        end_ms = int(b["bar_open_ms"]) + grid_ms
        out[end_ms] = b.get(surface_signal)
    return out


def build_surface_states(
    capture: Dict[str, Any], *, surface_signal: str, bar_seconds: float
) -> List[Dict[str, Any]]:
    """Per-bar causal straddle states driven by a *surface* signal.

    Identical state schema and straddle construction to EVAL-62 ``build_states`` /
    EVAL-72 ``build_skew_states`` (front expiry, common strike nearest spot, IV
    backed out of the real mark), except the driving signal is the causal surface
    signal (skew / atm_iv / term_slope) rather than options order-flow toxicity.
    ``side_k = sign(z_k)``, ``exposure_k = min(|z_k|, SIZE_CAP)``; state is
    end-of-bar and the hedge is set at ``k`` held over ``[k, k+1]`` (strictly causal).
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
        spot = e61._finite(snap.get("spot"), 0.0)
        quotes = snap.get("quotes") or []
        if spot > 0.0 and quotes:
            snap_by_bar_end[be] = (spot, quotes)

    # Same bar grid as EVAL-62 (perp candles -> bar_end); used only for grid alignment.
    bar_ends, _closes, _tox, _imb = e61.toxicity_per_bar(capture, bar_seconds)

    raw_by_end = surface_signal_by_bar_end(
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
        pick = e57._pick_straddle_quotes(quotes, spot, exp)
        if not pick or not pick.get("valid"):
            continue
        legs: List[Dict[str, float]] = []
        ok = True
        for key in ("call", "put"):
            q = pick[key]
            g = e57._iv_and_greeks(
                e61._finite(q.get("mark"), 0.0), e61._finite(q.get("bid"), 0.0),
                e61._finite(q.get("ask"), 0.0), spot, e61._finite(q.get("strike"), 0.0),
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
        straddle_mark = sum(
            e61._finite(q.get("mark"), 0.0) for q in (pick["call"], pick["put"])
        )
        if straddle_mark <= 0.0:
            continue
        z = float(sig_z[i]) if i < len(sig_z) else 0.0
        side = 1 if z > 1e-9 else (-1 if z < -1e-9 else 0)
        exposure = min(abs(z), SIZE_CAP) if side != 0 else 0.0
        states.append({
            "bar_ms": int(bar_ms),
            "spot": float(spot),
            "side": int(side),
            "exposure": float(exposure),
            "straddle_delta": float(straddle_delta),
            "straddle_mark": float(straddle_mark),
            "spread_usd": float(pick.get("spread_usd", 0.0)),
            "signal_z": float(z),
            "strike": float(pick.get("strike", spot)),
        })
    return states


# ---------------------------------------------------------------------------
# Per-config evaluation (statistics reused verbatim from EVAL-62)
# ---------------------------------------------------------------------------
def evaluate_config(
    capture: Dict[str, Any], *, surface_signal: str, bar_seconds: float
) -> Dict[str, Any]:
    inst = capture.get("underlying", "UNKNOWN")
    states = build_surface_states(
        capture, surface_signal=surface_signal, bar_seconds=bar_seconds
    )
    if len(states) < MIN_STATES_PER_CONFIG:
        return {
            "underlying": inst, "signal": surface_signal,
            "bar_seconds": float(bar_seconds),
            "error": "insufficient priced states", "n_states": len(states),
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
    mdd = _max_drawdown(rets)
    flat = [0.0] * len(rets)
    perm = permutation_test(
        rets, flat, statistic=_mean, n_permutations=PERMUTATION_PERMS,
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
    breach = kill_switch_breach(mdd)
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
        "mean_return": _mean(rets),
        "pass": passed,
    }


# ---------------------------------------------------------------------------
# Floor: EVAL-64 feasible floor verbatim (never weakened)
# ---------------------------------------------------------------------------
def _underlying_floor(capture: Dict[str, Any]) -> Dict[str, Any]:
    fl = _underlying_floor_strict(capture)
    return {
        "underlying": fl["underlying"],
        "n_surface_snapshots": fl["n_surface_snapshots"],
        "n_surface_instruments": fl["n_surface_instruments"],
        "n_surface_bars_5m": fl["n_surface_bars_5m"],
        "n_option_trades": fl["n_option_trades"],
        "n_of_instruments": fl["n_of_instruments"],
        "of_span_seconds": fl["of_span_seconds"],
        "n_of_bars_5m": fl["n_of_bars_5m"],
        "n_perp_candles": fl["n_perp_candles"],
        "perp_span_seconds": fl["perp_span_seconds"],
        "n_perp_bars_5m": fl["n_perp_bars_5m"],
        "n_common_bars_5m": fl["n_common_bars_5m"],
        "checks": fl["checks"],
        "ok": bool(fl["ok"]),
    }


# ---------------------------------------------------------------------------
# Protocol + orchestration
# ---------------------------------------------------------------------------
def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-184",
        "title": "Surface-line traded-form net-of-cost OOS monetization of the "
                 "EVAL-177/168/169 surface GOs (skew/atm_iv/term_slope -> forward "
                 "variance/CVaR) via signal-timed delta-hedged ATM straddle with "
                 "correct mark-path net-of-cost P&L, pooled across BTC+ETH",
        "extends": "EVAL-69 (identical pooled traded-form + BH-FDR + EVAL-64 floor "
                   "reused verbatim) with a surface signal source instead of the "
                   "order-flow toxicity; fresh disjoint forward capture at "
                   "data/raw/eval84cap",
        "supersedes": "nothing — disjoint forward OOS traded-form test of the "
                      "surface line; EVAL-69 sealed NO-GO CONFIRMED (PASS) for the "
                      "order-flow line only.",
        "capture_dir": str(capture_dir),
        "surface_signals": list(SURFACE_SIGNALS),
        "signal_target": SIGNAL_TARGET,
        "signal_builder": SIGNAL_BUILDER,
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "signal_window_seconds": float(SIGNAL_WINDOW_SECONDS),
        "position": "side_k = sign(z_k); exposure_k = min(|z_k|, SIZE_CAP); causal "
                    "decision at bar k; z_k = expanding-z of the causal surface signal",
        "traded_form": "ATM straddle (front expiry, common strike nearest spot, IV "
                       "backed out of the real mark via EVAL-57 helpers) with the "
                       "EVAL-62 mark-path net-of-cost P&L: delta-hedge + half real "
                       "2-leg spread + hedge fee, spot-normalized",
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
        "min_pooled_returns": MIN_POOLED_RETURNS,
        "go_bar": (
            "GO only if, on both BTC and ETH and at least one grid config, net-of-cost "
            "Sharpe > 0, no kill-switch breach (max-DD <= 0.20), directional "
            "permutation p < 0.05, block-bootstrap 95% CI lower > 0, nonzero "
            "positions > 0, pooled returns >= 790 (power), pooled BH-FDR rejects "
            "that config, the EVAL-64 floor is met on BOTH underlyings, and both "
            "capture windows are disjoint from the sealed window; else NO-GO CONFIRMED "
            "(PASS) when floor+disjoint+power but not monetizable, INCONCLUSIVE "
            "(UNDERPOWERED) when floor+disjoint but pooled returns < 790, or BLOCKED "
            "when floor/disjoint fails."
        ),
        "floor": {
            "source": "EVAL-64 feasible floor reused verbatim (never weakened)",
            "min_underlyings": int(MIN_UNDERLYINGS),
            "checks": [
                "snapshots_ok", "surface_instruments_ok", "surface_bars_ok",
                "trades_ok", "of_instruments_ok", "of_span_ok", "of_bars_ok",
                "perp_bars_ok", "perp_span_ok", "common_overlap_ok",
            ],
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


def run_eval184(
    *,
    capture_dir: str = DEFAULT_CAPTURE_DIR,
    write: bool = True,
    task_label: str = DEFAULT_TASK_LABEL,
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    captures = _select_one_capture_per_underlying(
        e61._capture_inventory(str(capture_dir_abs))
    )
    # Pooled panel: keep only the two crypto underlyings.
    captures = [c for c in captures if str(c.get("underlying", "")).upper() in UNDERLYINGS]

    per_underlying_floor: Dict[str, Dict[str, Any]] = {}
    disjointness: Dict[str, Dict[str, Any]] = {}
    for c in captures:
        inst = str(c.get("underlying", "?"))
        per_underlying_floor[inst] = _underlying_floor(c)
        disjointness[inst] = e67.check_disjointness(c)

    present = {str(c.get("underlying", "")).upper() for c in captures}
    missing = [u for u in UNDERLYINGS if u not in present]
    floor_ok = bool(
        len(captures) >= MIN_UNDERLYINGS
        and not missing
        and per_underlying_floor
        and all(v["ok"] for v in per_underlying_floor.values())
    )
    disjoint_ok = bool(
        len(captures) >= MIN_UNDERLYINGS
        and not missing
        and disjointness
        and all(v["ok"] for v in disjointness.values())
    )
    floor_and_disjoint_ok = bool(floor_ok and disjoint_ok)

    per_config: List[Dict[str, Any]] = []
    errors: List[str] = []
    if captures and not missing:
        for cap in captures:
            for sig in SURFACE_SIGNALS:
                for bar_s in GRID_BAR_SECONDS:
                    try:
                        res = evaluate_config(
                            cap, surface_signal=sig, bar_seconds=bar_s
                        )
                    except BaseException as exc:  # noqa: BLE001
                        errors.append(
                            f"{cap.get('underlying','?')}::{sig}::bar{bar_s}: {exc!r}"
                        )
                        continue
                    per_config.append(res)

    # Rebuild pooled returns properly: concatenate BTC+ETH net-of-cost returns
    # per config (signal::bar_seconds) across underlyings.
    pooled_returns: Dict[str, List[float]] = {}
    if captures and not missing:
        for sig in SURFACE_SIGNALS:
            for bar_s in GRID_BAR_SECONDS:
                key = f"{sig}::bar{bar_s}"
                rets: List[float] = []
                for cap in captures:
                    states = build_surface_states(
                        cap, surface_signal=sig, bar_seconds=bar_s
                    )
                    sr = e62.markpath_returns(states)
                    rets.extend([float(x) for x in sr["returns"]])
                pooled_returns[key] = rets

    p_values: Dict[str, float] = {}
    for key, rets in pooled_returns.items():
        if len(rets) < 8:
            p_values[key] = 1.0
            continue
        flat = [0.0] * len(rets)
        perm = permutation_test(
            rets, flat, statistic=_mean, n_permutations=PERMUTATION_PERMS,
            paired=True, seed=SEED,
        )
        p_values[key] = e62._finite(perm.get("p_value"), 1.0)
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}
    rejected = set(bh.get("rejected") or [])

    pass_configs: List[str] = []
    max_pooled_returns = 0
    for key, rets in pooled_returns.items():
        n = len(rets)
        max_pooled_returns = max(max_pooled_returns, n)
        if n < 8:
            continue
        sharpe = _sharpe_of_returns(rets)
        mdd = _max_drawdown(rets)
        flat = [0.0] * n
        boot = block_bootstrap_ci(
            rets, statistic=_sharpe_of_returns, n_bootstrap=BOOTSTRAP_RESAMPLES,
            block_size=BOOTSTRAP_BLOCK, seed=SEED,
        )
        breach = kill_switch_breach(mdd)
        perm_p = p_values[key]
        ci_low = e62._finite(boot[1], 0.0)
        ci_high = e62._finite(boot[2], 0.0)
        nonzero = sum(
            1 for cap in captures
            for s in build_surface_states(
                cap,
                surface_signal=key.split("::")[0],
                bar_seconds=float(key.split("::bar")[1]),
            )
            if abs(float(s.get("signal_z", 0.0))) > 1e-9
        )
        passed = bool(
            sharpe > 0.0 and not breach and perm_p < 0.05 and ci_low > 0.0
            and nonzero > 0 and n >= MIN_POOLED_RETURNS
        )
        if passed and key in rejected:
            pass_configs.append(key)

    power_adequate = bool(max_pooled_returns >= MIN_POOLED_RETURNS)
    go = bool(
        floor_and_disjoint_ok
        and pass_configs
        and len(rejected) >= 1
        and power_adequate
    )

    if not floor_and_disjoint_ok:
        verdict = "BLOCKED"
    elif go:
        verdict = "GO CONFIRMED"
    elif not power_adequate:
        verdict = "INCONCLUSIVE (UNDERPOWERED)"
    else:
        verdict = "NO-GO CONFIRMED (PASS)"

    campaign_state = (
        "EVAL_184_SURFACE_TRADED_NETFCOST_OOS"
        if floor_and_disjoint_ok
        else "EVAL_184_BLOCKED_FLOOR_OR_DISJOINTNESS"
    )

    protocol = build_protocol(capture_dir)
    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict,
        "verdict_detail": (
            "surface-line traded-form net-of-cost OOS (disjoint real BTC+ETH window "
            "at data/raw/eval84cap) of the EVAL-177/168/169 surface GOs; pooled "
            "sample Sharpe / max-DD / permutation / bootstrap on the mark-path "
            "net-of-cost P&L with EVAL-62 signal/P&L + EVAL-64 feasible floor reused"
            if floor_and_disjoint_ok
            else "capture below the pre-registered EVAL-64 feasible floor and/or "
                 "missing an underlying and/or overlapping the sealed window; no "
                 "GO/NO-GO verdict"
        ),
        "floor_ok": bool(floor_ok),
        "disjointness_ok": bool(disjoint_ok),
        "floor_and_disjoint_ok": floor_and_disjoint_ok,
        "missing_underlyings": missing,
        "capture_dir": str(capture_dir_abs),
        "underlyings": sorted(present),
        "floor": protocol["floor"],
        "disjointness_rule": (
            "A capture is usable only if [window_start, window_end] does not overlap "
            f"[{SEALED_WINDOW_START}, {SEALED_WINDOW_END}] (sealed EVAL-64/65 window); "
            "the surface-line traded-form must consume a forward capture disjoint "
            "from it, at/after 2026-11-20T00:00:00Z."
        ),
        "per_underlying_floor": per_underlying_floor,
        "disjointness": disjointness,
        "protocol": protocol,
        "per_config": per_config,
        "pooled": {
            "bh_fdr": bh,
            "pass_configs": pass_configs,
            "max_pooled_returns": max_pooled_returns,
            "power_adequate": power_adequate,
            "min_pooled_returns": MIN_POOLED_RETURNS,
            "campaign_state": campaign_state,
        },
        "errors": errors,
    }

    if not write:
        return report

    # Prereg is written once (design precedes capture); do not duplicate on re-seal.
    if not list(OUT_DIR.glob(PREREG_GLOB)):
        e62._seal(PREREG_ID, _build_prereg(report), _build_prereg_md)

    if not floor_and_disjoint_ok:
        e62._seal(BLOCKED_ID, _build_blocked_report(report), _build_blocked_md)
        return report

    e62._seal(REPORT_ID, report, _build_md)
    return report


# ---------------------------------------------------------------------------
# Artifact builders
# ---------------------------------------------------------------------------
def _build_prereg(report: Dict[str, Any]) -> Dict[str, Any]:
    p = report["protocol"]
    return {
        "prereg_id": PREREG_ID,
        "generated_at": report["generated_at"],
        "task": report["task"],
        "hypothesis": (
            "Pooled across BTC and ETH, the surface-line signals (skew -> forward "
            "variance, atm_iv/term_slope -> forward CVaR) are monetizable "
            "net-of-cost out-of-sample on a fresh disjoint real forward window "
            "(data/raw/eval84cap): pooled Sharpe > 0, no kill-switch breach "
            "(max-DD <= 0.20), directional permutation p < 0.05, block-bootstrap "
            "95% CI lower > 0, >=790 pooled returns (power), and BH-FDR rejects, at "
            "the sealed EVAL-64 floor on both underlyings."
        ),
        "extends": p["extends"],
        "disjointness_rule": report["disjointness_rule"],
        "data_availability": {
            "note": "consumes the freshly acquired disjoint BTC+ETH three-way "
                    "capture at data/raw/eval84cap; public read-only; no synthetic data",
            "sealed_window": [SEALED_WINDOW_START, SEALED_WINDOW_END],
            "earliest_disjoint_capture_end": EARLIEST_DISJOINT_CAPTURE_END,
        },
        "protocol": p,
        "capture_dir": report["capture_dir"],
    }


def _build_prereg_md(r: Dict[str, Any]) -> str:
    p = r["protocol"]
    lines = [
        f"# {PREREG_ID} — surface-line traded-form net-of-cost OOS monetization of "
        f"the EVAL-177/168/169 surface GOs (pooled-sample Sharpe)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Hypothesis: {r['hypothesis']}",
        f"- Capture dir: `{r['capture_dir']}` (fresh disjoint forward capture)",
        f"- Extends: {p['extends']}",
        f"- Disjoint from: [{SEALED_WINDOW_START}, {SEALED_WINDOW_END}]",
        "",
        "## Pre-declared protocol",
        "",
        f"- Underlyings: {p['floor']['min_underlyings']} (BTC+ETH)",
        f"- Surface signals: {p['surface_signals']}",
        f"- Signal targets: {p['signal_target']}",
        f"- Signal builders: {p['signal_builder']}",
        f"- Bar grid (s): {p['bar_seconds_grid']}",
        f"- Signal window (s): {p['signal_window_seconds']}",
        f"- Target: signal-timed delta-hedged ATM straddle mark-path net-of-cost P&L, "
        f"pooled across BTC+ETH",
        f"- Statistic: {p['stats']}",
        f"- Power adequacy: pooled returns >= {p['min_pooled_returns']}",
        "",
        "## Pre-declared disjointness + capture-window rule",
        "",
        r["disjointness_rule"],
        "",
        "## Pre-declared GO bar",
        "",
        p["go_bar"],
        "",
        "## Pre-registered feasible floor (reused verbatim from sealed EVAL-64)",
        "",
        f"- min underlyings (BTC+ETH): {p['floor']['min_underlyings']}",
        f"- Floor checks: {', '.join(p['floor']['checks'])}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {r['report_id']} — surface-line traded-form net-of-cost OOS monetization "
        f"of the EVAL-177/168/169 surface GOs",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        f"- Disjointness OK: {r.get('disjointness_ok')}",
        f"- Missing underlyings: {r.get('missing_underlyings')}",
        f"- Max pooled returns: {r['pooled']['max_pooled_returns']} "
        f"(>= {r['pooled']['min_pooled_returns']} required; power adequate: "
        f"{r['pooled']['power_adequate']})",
        "",
        "## Disjointness (sealed window 2026-11-09T06:48:16Z..2026-11-16T06:48:16Z)",
        "",
        "| underlying | disjoint | overlap s | capture window | span s |",
        "|---|---|---|---|---|",
    ]
    for inst, dj in (r.get("disjointness") or {}).items():
        lines.append(
            f"| {inst} | {dj.get('ok')} | {dj.get('overlap_seconds')} | "
            f"{dj.get('capture_window')} | {dj.get('capture_span_seconds')} |"
        )
    lines += [
        "",
        "## Per-underlying EVAL-64 floor",
        "",
        "| underlying | snaps | surf inst | 5m bars | deribit trades | of inst | of span s | perp bars | perp span s | common 5m | ok |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for inst, fl in r["per_underlying_floor"].items():
        lines.append(
            f"| {inst} | {fl['n_surface_snapshots']} | {fl['n_surface_instruments']} | "
            f"{fl['n_surface_bars_5m']} | {fl['n_option_trades']} | "
            f"{fl['n_of_instruments']} | {fl['of_span_seconds']:.0f} | "
            f"{fl['n_of_bars_5m']} | {fl['n_perp_bars_5m']} | "
            f"{fl['perp_span_seconds']:.0f} | {fl['n_common_bars_5m']} | {fl['ok']} |"
        )
    lines += ["", "## Pooled per-config", "",
              "| signal | bar_s | underlyings | pooled n | power ok | Sharpe | max-DD | perm_p | CI95 | pass |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for c in r.get("per_config", []):
        ci = c.get("bootstrap_ci") or [float("nan")] * 3
        lines.append(
            f"| {c.get('signal')} | {c.get('bar_seconds')} | "
            f"{c.get('underlying')} | {c.get('n_returns')} | "
            f"{c.get('n_returns') >= MIN_POOLED_RETURNS} | "
            f"{e62._finite(c.get('sharpe'), 0.0):.4f} | "
            f"{e62._finite(c.get('max_drawdown'), 0.0):.4f} | "
            f"{e62._finite(c.get('permutation_p'), 1.0):.4f} | "
            f"[{e62._finite(ci[1], 0.0):.4f}, {e62._finite(ci[2], 0.0):.4f}] | {c.get('pass')} |"
        )
    lines += ["", "## Pooled", "",
              f"- BH-FDR rejected: {r['pooled']['bh_fdr'].get('rejected')}",
              f"- Pass configs: {r['pooled']['pass_configs']}",
              f"- Power adequate: {r['pooled']['power_adequate']}",
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
        "missing_underlyings": r.get("missing_underlyings", []),
        "per_underlying_floor": r["per_underlying_floor"],
        "floor": r["floor"],
        "floor_ok": r["floor_ok"],
        "disjointness_ok": r.get("disjointness_ok", False),
        "disjointness": r.get("disjointness", {}),
        "errors": r.get("errors", []),
    }


def _build_blocked_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {BLOCKED_ID} — surface-line traded-form net-of-cost OOS "
        f"(below the pre-registered EVAL-64 feasible floor and/or missing an "
        f"underlying and/or overlapping the sealed window)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        "- Verdict: **BLOCKED** (measured; not NO-GO)",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Underlyings: {', '.join(r['underlyings'])}",
        f"- Missing underlyings: {r.get('missing_underlyings', [])}",
        f"- Floor met: {r['floor_ok']}",
        f"- Disjointness met: {r.get('disjointness_ok', False)}",
        "",
        "The capture does not meet the pre-registered EVAL-64 feasible floor (never "
        "weakened), is missing a required underlying, and/or overlaps the sealed "
        "EVAL-64/65 window (2026-11-09T06:48:16Z..2026-11-16T06:48:16Z), so no "
        "GO/NO-GO verdict is emitted. Do NOT weaken the floor, do NOT use synthetic "
        "data, and do NOT emit NO-GO on under-floor or non-disjoint data.",
        "",
        "## Disjointness",
        "",
    ]
    for inst, dj in (r.get("disjointness") or {}).items():
        lines.append(f"- {inst}: {json.dumps(dj)}")
    lines += ["", "## Per-underlying floor", ""]
    for inst, fl in r["per_underlying_floor"].items():
        lines.append(f"- {inst}: {json.dumps(fl['checks'])}")
    lines.append("")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Prereg-only emission (design artifact; no capture required)
# ---------------------------------------------------------------------------
def build_prereg_document(
    *, task_label: str = DEFAULT_TASK_LABEL, capture_dir: str = DEFAULT_CAPTURE_DIR
) -> Dict[str, Any]:
    protocol = build_protocol(capture_dir)
    report = {
        "generated_at": _utc_now_iso(),
        "task": task_label,
        "protocol": protocol,
        "capture_dir": str(capture_dir),
        "disjointness_rule": (
            "A capture is usable only if [window_start, window_end] does not overlap "
            f"[{SEALED_WINDOW_START}, {SEALED_WINDOW_END}] (sealed EVAL-64/65 window); "
            "the surface-line traded-form must consume a forward capture disjoint "
            "from it, at/after 2026-11-20T00:00:00Z."
        ),
    }
    return _build_prereg(report)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-184: surface-line traded-form net-of-cost OOS verdict "
                    "(the EVAL-69 analogue for the EVAL-177/168/169 surface GOs)"
    )
    ap.add_argument("--capture-dir", default=DEFAULT_CAPTURE_DIR)
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined/blocked (default)")
    ap.add_argument("--task-label", default=DEFAULT_TASK_LABEL)
    ap.add_argument(
        "--emit-prereg",
        action="store_true",
        help="write only the pre-registration (design; no capture needed) and exit",
    )
    args = ap.parse_args(argv)

    if args.emit_prereg:
        prereg = build_prereg_document(task_label=args.task_label, capture_dir=args.capture_dir)
        written = e62._seal(PREREG_ID, prereg, _build_prereg_md)
        print(json.dumps({"prereg_id": PREREG_ID, "written": written}, indent=2, default=str))
        return 0

    write = not args.no_write
    try:
        report = run_eval184(
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
                "missing_underlyings": list(UNDERLYINGS),
                "per_underlying_floor": {},
                "floor": build_protocol(args.capture_dir)["floor"],
                "floor_ok": False,
                "disjointness_ok": False,
                "disjointness": {},
                "errors": [repr(exc)],
            })
            e62._seal(BLOCKED_ID, blocked, _build_blocked_md)
        return 1

    print(json.dumps({
        "verdict": report.get("verdict"),
        "floor_ok": report.get("floor_ok"),
        "disjointness_ok": report.get("disjointness_ok"),
        "missing_underlyings": report.get("missing_underlyings"),
        "underlyings": report.get("underlyings"),
        "max_pooled_returns": report.get("pooled", {}).get("max_pooled_returns"),
        "power_adequate": report.get("pooled", {}).get("power_adequate"),
        "bh_fdr_rejected": report.get("pooled", {}).get("bh_fdr", {}).get("rejected"),
        "pass_configs": report.get("pooled", {}).get("pass_configs"),
        "n_configs": len(report.get("per_config", [])),
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
