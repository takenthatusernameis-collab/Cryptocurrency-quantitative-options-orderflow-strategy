#!/usr/bin/env python3
"""EVAL-185: surface-line traded-form ROBUSTNESS GRID — is the EVAL-184 surface
NO-GO a monetization/horizon artifact or a robust economic result?

Why this exists
---------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``) is
**crypto options surface + options order-flow -> tradeable, net-of-cost alpha on
REAL public data**. All predictiveness rungs EVAL-02..183 are sealed. The traded-form
line is resolved and BOTH signal families monetize to NO-GO net-of-cost:

* EVAL-69  (order-flow toxicity -> realized vol, traded-form):  NO-GO CONFIRMED (PASS)
* EVAL-184 (surface skew/atm_iv/term_slope -> var/CVaR, traded-form): NO-GO CONFIRMED (PASS)
            (COMBINED_20261122T081750Z; 0 BH-FDR rejections across 12 configs)

Before declaring the surface NO-GO robust, we must bound whether it is an artifact of
a single cost/horizon choice rather than a robust economic fact. This campaign re-runs
the EVAL-184 surface-line traded-form (signal-timed delta-hedged ATM straddle, EVAL-62
mark-path net-of-cost P&L) under a **PRE-REGISTERED cost x horizon grid** on the SAME
floor-compliant disjoint capture (``data/raw/eval84cap``, read-only):

    3 signals {skew, atm_iv, term_slope}
  x 5 horizons {60, 120, 240, 300, 360} seconds
  x 3 cost haircuts {0.5x, 1x, 2x} applied to BOTH the hedge fee and real bid/ask spread
  = 45 pooled configurations.

Reuse: the EVAL-184 runner machinery verbatim (e71/e74/e62 surface + mark-path helpers)
and the EVAL-64 feasible floor verbatim (never weakened). The only additions over
EVAL-184 are the extra bar horizons and the cost-haircut loop, which scales both the
EVAL-62 ``hedge_fee_bps`` and each state's ``spread_usd`` by the same haircut. States
are built once per (signal, bar, underlying) and reused across the three haircuts
(mark-path state geometry is cost-invariant).

Pre-registered verdict bar (pooled BH-FDR across the FULL 45-config grid, both-asset):
* **GO** iff >= 1 grid config yields a pooled BH-FDR rejection AND net-of-cost Sharpe>0
  AND block-bootstrap 95% CI lower>0 AND nonzero positions>0 AND pooled returns>=790
  AND the EVAL-64 floor is met on BOTH underlyings AND both capture windows are disjoint,
  **and** that pass holds under >= 2 of 3 cost scenarios (robust to cost) at the same
  signal/horizon. (A config is cost-robust if it passes at >= 2 haircuts.)
* else **NO-GO CONFIRMED (PASS)** when floor+disjoint+power but not monetizable
  (the surface NO-GO is robust to monetization/horizon), **INCONCLUSIVE (UNDERPOWERED)**
  when floor+disjoint but pooled returns < 790, or **BLOCKED** (measured, never NO-GO)
  when the floor/disjointness fails.

Acquisition is intentionally NOT performed here; the gate refuses to seal until a
floor-compliant disjoint capture exists at ``data/raw/eval84cap`` and this runner's
``--no-write`` dry-run is green.

Seals ``EVAL_185_SURFACE_TRADED_ROBUSTNESS_GRID_PREREGISTRATION_<UTC>`` then
``..._COMBINED_<UTC>`` (or ``..._BLOCKED_<UTC>``). IDs match the gate's globs.
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

# Reuse the sealed EVAL-184 runner verbatim (surface signals + straddle + mark-path
# + floor + disjointness). No forks, no src edits.
import scripts.eval57_vrp_net_of_cost as e57  # noqa: E402,F401
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402,F401
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64  # noqa: E402
import scripts.eval67_btc_oflow_tox_rv_oos as e67  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
import scripts.eval74_surface_term_structure_predictiveness as e74  # noqa: E402
import scripts.eval184_surface_traded_netofcost_oos as e184  # noqa: E402
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
# Artifact IDs must match the gate's pre-registered globs.
REPORT_ID = "EVAL_185_SURFACE_TRADED_ROBUSTNESS_GRID_COMBINED"
PREREG_ID = "EVAL_185_SURFACE_TRADED_ROBUSTNESS_GRID_PREREGISTRATION"
BLOCKED_ID = "EVAL_185_SURFACE_TRADED_ROBUSTNESS_GRID_BLOCKED"
PREREG_GLOB = PREREG_ID + "_*"
COMBINED_GLOB = REPORT_ID + "_*"
BLOCKED_GLOB = BLOCKED_ID + "_*"

DEFAULT_CAPTURE_DIR = "data/raw/eval84cap"
DEFAULT_TASK_LABEL = "EVAL185-SURFACE-TRADED-ROBUSTNESS-GRID"

# Disjointness: both underlyings must be disjoint from the sealed EVAL-64/65
# three-way window; identical to EVAL-184 (same disjoint capture).
SEALED_WINDOW_START = e184.SEALED_WINDOW_START
SEALED_WINDOW_END = e184.SEALED_WINDOW_END
EARLIEST_DISJOINT_CAPTURE_END = e184.EARLIEST_DISJOINT_CAPTURE_END

# Surface-line GO cells: signal -> builder -> target (from EVAL-177/168/169).
SURFACE_SIGNALS: Tuple[str, ...] = e184.SURFACE_SIGNALS
SIGNAL_BUILDER: Dict[str, str] = dict(e184.SIGNAL_BUILDER)
SIGNAL_TARGET: Dict[str, str] = dict(e184.SIGNAL_TARGET)

# Exact pre-registered robustness grid (must equal eval185_phaseb_gate.py).
# Horizons: EVAL-184 bases {60, 300}s plus one 60s bar on each side where positive;
# 60-60=0 is omitted, so {60,120,240,300,360}.
HORIZON_GRID_SECONDS: Tuple[float, ...] = (60.0, 120.0, 240.0, 300.0, 360.0)
COST_HAIRCUTS: Tuple[float, ...] = (0.5, 1.0, 2.0)
GRID_CONFIG_COUNT = (
    len(SURFACE_SIGNALS) * len(HORIZON_GRID_SECONDS) * len(COST_HAIRCUTS)
)
SIGNAL_WINDOW_SECONDS: float = e184.SIGNAL_WINDOW_SECONDS

# Stats / cost / risk / size reused verbatim from EVAL-184 (== EVAL-62).
ZWINDOW = e184.ZWINDOW
SIZE_CAP = e184.SIZE_CAP
PERMUTATION_PERMS = e184.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e184.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e184.BOOTSTRAP_BLOCK
FDR_ALPHA = e184.FDR_ALPHA
SEED = e184.SEED
KILL_SWITCH_MAX_DD = e184.KILL_SWITCH_MAX_DD
HEDGE_FEE_BPS = e184.HEDGE_FEE_BPS

MIN_STATES_PER_CONFIG = e184.MIN_STATES_PER_CONFIG
MIN_POOLED_RETURNS = e184.MIN_POOLED_RETURNS
# Robustness: a pass must hold under at least this many of the cost haircuts.
MIN_COST_SCENARIOS_PASS = 2

UNDERLYINGS: Tuple[str, ...] = e184.UNDERLYINGS
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
    "scripts/eval185_surface_traded_robustness_oos.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval185_surface_traded_robustness_oos.py "
    "tests/test_eval185_surface_traded_robustness_oos.py",
    "python3 -m pytest -q tests/test_eval185_surface_traded_robustness_oos.py",
    "# the EVAL-184 floor-compliant disjoint capture is already on disk (gitignored):",
    "#   data/raw/eval84cap/three_way_BTC_*.json + three_way_ETH_*.json",
    "# dry-run (green = runner works):",
    "python3 scripts/eval185_surface_traded_robustness_oos.py "
    "--capture-dir data/raw/eval84cap --no-write",
    "# seal (gate refuses until runner is green):",
    "python3 scripts/eval185_surface_traded_robustness_oos.py "
    "--capture-dir data/raw/eval84cap --seal --task-label "
    "EVAL185-SURFACE-TRADED-ROBUSTNESS-GRID",
    "python3 scripts/eval185_phaseb_gate.py --execute  # require SEALED(0)",
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
        mdd = max(mdd, (peak - eq) / peak if peak > 0 else 0.0)
    return mdd


def kill_switch_breach(max_drawdown: float) -> bool:
    return float(max_drawdown) > KILL_SWITCH_MAX_DD


def scale_states_cost(
    states: Sequence[Dict[str, Any]], *, cost_haircut: float
) -> List[Dict[str, Any]]:
    """Return shallow state copies with ``spread_usd`` scaled by ``cost_haircut``.

    The hedge-fee haircut is applied separately by passing a scaled
    ``hedge_fee_bps`` to ``e62.markpath_returns``; the spread haircut is applied
    here to each state's real bid/ask spread (which ``markpath_returns`` reads).
    """
    c = float(cost_haircut)
    out: List[Dict[str, Any]] = []
    for s in states:
        d = dict(s)
        d["spread_usd"] = float(s.get("spread_usd", 0.0)) * c
        out.append(d)
    return out


# ---------------------------------------------------------------------------
# Per-config evaluation (surface states reused from EVAL-184; cost scaled)
# ---------------------------------------------------------------------------
def evaluate_config_cost(
    states: Sequence[Dict[str, Any]],
    *,
    underlying: str,
    surface_signal: str,
    bar_seconds: float,
    cost_haircut: float,
) -> Dict[str, Any]:
    """Evaluate one (signal, bar, cost haircut) cell given pre-built states."""
    inst = underlying
    if len(states) < MIN_STATES_PER_CONFIG:
        return {
            "underlying": inst, "signal": surface_signal,
            "bar_seconds": float(bar_seconds),
            "cost_haircut": float(cost_haircut),
            "error": "insufficient priced states", "n_states": len(states),
            "n_returns": 0, "pass": False,
        }
    scaled = scale_states_cost(states, cost_haircut=cost_haircut)
    hedge_fee_bps = HEDGE_FEE_BPS * float(cost_haircut)
    sr = e62.markpath_returns(scaled, hedge_fee_bps=hedge_fee_bps)
    rets = sr["returns"]
    if len(rets) < 3:
        return {
            "underlying": inst, "signal": surface_signal,
            "bar_seconds": float(bar_seconds),
            "cost_haircut": float(cost_haircut),
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
        "signal": surface_signal,
        "bar_seconds": float(bar_seconds),
        "cost_haircut": float(cost_haircut),
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
        "eval": "EVAL-185",
        "title": "Surface-line traded-form ROBUSTNESS GRID: is the EVAL-184 surface "
                 "NO-GO a monetization/horizon artifact or robust? Re-runs the "
                 "EVAL-177/168/169 surface GO monetization (skew/atm_iv/term_slope -> "
                 "forward variance/CVaR) under a pre-registered cost x horizon grid on "
                 "the same floor-compliant disjoint capture (data/raw/eval84cap), pooled "
                 "across BTC+ETH",
        "extends": "EVAL-184 (identical surface signals, EVAL-62 mark-path net-of-cost "
                    "P&L, EVAL-64 feasible floor, and EVAL-67 disjointness reused "
                    "verbatim) with a pre-registered cost x horizon grid: 3 signals x "
                    "horizons {60,120,240,300,360}s x cost haircuts {0.5x,1x,2x} = 45 "
                    "pooled configs",
        "supersedes": "nothing — EVAL-184 sealed NO-GO CONFIRMED (PASS) for the surface "
                      "line at bases {60,300}s x cost 1x; EVAL-185 bounds whether that "
                      "NO-GO is a monetization/horizon artifact.",
        "capture_dir": str(capture_dir),
        "surface_signals": list(SURFACE_SIGNALS),
        "signal_target": SIGNAL_TARGET,
        "signal_builder": SIGNAL_BUILDER,
        "horizon_grid_seconds": [float(b) for b in HORIZON_GRID_SECONDS],
        "cost_haircuts": [float(c) for c in COST_HAIRCUTS],
        "grid_config_count": int(GRID_CONFIG_COUNT),
        "signal_window_seconds": float(SIGNAL_WINDOW_SECONDS),
        "position": "side_k = sign(z_k); exposure_k = min(|z_k|, SIZE_CAP); causal "
                    "decision at bar k; z_k = expanding-z of the causal surface signal",
        "traded_form": "ATM straddle (front expiry, common strike nearest spot, IV "
                       "backed out of the real mark via EVAL-57 helpers) with the "
                       "EVAL-62 mark-path net-of-cost P&L: delta-hedge + half real "
                       "2-leg spread + hedge fee, spot-normalized; cost haircut scales "
                       "BOTH the hedge fee and each state's real bid/ask spread",
        "zwindow": int(ZWINDOW),
        "size_cap": float(SIZE_CAP),
        "hedge_fee_bps": float(HEDGE_FEE_BPS),
        "min_cost_scenarios_pass": int(MIN_COST_SCENARIOS_PASS),
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
            "GO only if >=1 grid config yields a pooled BH-FDR rejection (across the "
            "FULL 45-config grid) AND net-of-cost Sharpe > 0 AND no kill-switch breach "
            "(max-DD <= 0.20) AND directional permutation p < 0.05 AND block-bootstrap "
            "95% CI lower > 0 AND nonzero positions > 0 AND pooled returns >= 790 "
            "(power), AND the same (signal, horizon) passes at >= 2 of 3 cost haircuts "
            "(robust to cost), AND the EVAL-64 floor is met on BOTH underlyings AND both "
            "capture windows are disjoint from the sealed window; else NO-GO CONFIRMED "
            "(PASS) when floor+disjoint+power but not monetizable (the surface NO-GO is "
            "robust to monetization/horizon), INCONCLUSIVE (UNDERPOWERED) when "
            "floor+disjoint but pooled returns < 790, or BLOCKED when floor/disjoint "
            "fails."
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


def _grid_key(signal: str, bar_seconds: float, cost_haircut: float) -> str:
    return f"{signal}::bar{bar_seconds:g}::cost{cost_haircut:g}"


def run_eval185(
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

    # Build surface states ONCE per (signal, bar, underlying); the mark-path state
    # geometry is cost-invariant, so the three haircuts reuse the same states and only
    # the hedge fee + spread_usd are scaled. This keeps the 45-config grid tractable.
    states_by_key: Dict[Tuple[str, float, str], List[Dict[str, Any]]] = {}
    errors: List[str] = []
    if captures and not missing:
        for cap in captures:
            inst = str(cap.get("underlying", "?"))
            for sig in SURFACE_SIGNALS:
                for bar_s in HORIZON_GRID_SECONDS:
                    try:
                        states_by_key[(sig, float(bar_s), inst)] = (
                            e184.build_surface_states(
                                cap, surface_signal=sig, bar_seconds=float(bar_s)
                            )
                        )
                    except BaseException as exc:  # noqa: BLE001
                        errors.append(
                            f"{inst}::{sig}::bar{bar_s}: {exc!r}"
                        )
                        states_by_key[(sig, float(bar_s), inst)] = []

    # Per-config cells: one per (signal, bar, cost haircut) per underlying.
    per_config: List[Dict[str, Any]] = []
    for cap in captures:
        inst = str(cap.get("underlying", "?"))
        for sig in SURFACE_SIGNALS:
            for bar_s in HORIZON_GRID_SECONDS:
                states = states_by_key.get((sig, float(bar_s), inst), [])
                for c in COST_HAIRCUTS:
                    try:
                        res = evaluate_config_cost(
                            states, underlying=inst, surface_signal=sig,
                            bar_seconds=float(bar_s), cost_haircut=float(c),
                        )
                    except BaseException as exc:  # noqa: BLE001
                        errors.append(
                            f"{inst}::{sig}::bar{bar_s}::cost{c}: {exc!r}"
                        )
                        continue
                    per_config.append(res)

    # Pooled returns per grid config: concatenate BTC+ETH net-of-cost returns for
    # each (signal, bar, cost haircut) across underlyings.
    pooled_returns: Dict[str, List[float]] = {}
    for sig in SURFACE_SIGNALS:
        for bar_s in HORIZON_GRID_SECONDS:
            for c in COST_HAIRCUTS:
                key = _grid_key(sig, float(bar_s), float(c))
                rets: List[float] = []
                for cap in captures:
                    inst = str(cap.get("underlying", "?"))
                    states = states_by_key.get((sig, float(bar_s), inst), [])
                    if len(states) < MIN_STATES_PER_CONFIG:
                        continue
                    scaled = scale_states_cost(states, cost_haircut=float(c))
                    sr = e62.markpath_returns(
                        scaled, hedge_fee_bps=HEDGE_FEE_BPS * float(c)
                    )
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
        p_values[key] = _finite(perm.get("p_value"), 1.0)
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}
    rejected = set(bh.get("rejected") or [])

    # Per-config pooled evaluation (Sharpe / max-DD / bootstrap / nonzero / power).
    cfg_stats: Dict[str, Dict[str, Any]] = {}
    max_pooled_returns = 0
    for key, rets in pooled_returns.items():
        n = len(rets)
        max_pooled_returns = max(max_pooled_returns, n)
        if n < 8:
            cfg_stats[key] = {"n": n, "pass": False, "sharpe": 0.0, "ci_low": 0.0}
            continue
        sharpe = _sharpe_of_returns(rets)
        mdd = _max_drawdown(rets)
        boot = block_bootstrap_ci(
            rets, statistic=_sharpe_of_returns, n_bootstrap=BOOTSTRAP_RESAMPLES,
            block_size=BOOTSTRAP_BLOCK, seed=SEED,
        )
        breach = kill_switch_breach(mdd)
        perm_p = p_values[key]
        ci_low = _finite(boot[1], 0.0)
        ci_high = _finite(boot[2], 0.0)
        sig = key.split("::")[0]
        bar_s = float(key.split("::bar")[1].split("::cost")[0])
        nonzero = sum(
            1 for cap in captures
            for s in states_by_key.get((sig, bar_s, str(cap.get("underlying", "?"))), [])
            if abs(float(s.get("signal_z", 0.0))) > 1e-9
        )
        passed = bool(
            sharpe > 0.0 and not breach and perm_p < 0.05 and ci_low > 0.0
            and nonzero > 0 and n >= MIN_POOLED_RETURNS
        )
        cfg_stats[key] = {
            "n": n, "sharpe": sharpe, "max_drawdown": mdd, "breach": breach,
            "perm_p": perm_p, "ci_low": ci_low, "ci_high": ci_high,
            "nonzero": nonzero, "pass": passed,
        }

    # Cost-robustness aggregation: a (signal, horizon) passes at a cost scenario if
    # its grid config passes AND is BH-FDR rejected. A (signal,horizon) is
    # cost-robust if it passes at >= MIN_COST_SCENARIOS_PASS cost haircuts.
    pass_configs: List[str] = []
    cost_robust_pairs: List[str] = []
    for sig in SURFACE_SIGNALS:
        for bar_s in HORIZON_GRID_SECONDS:
            passing_haircuts: List[float] = []
            for c in COST_HAIRCUTS:
                key = _grid_key(sig, float(bar_s), float(c))
                st = cfg_stats.get(key, {})
                if st.get("pass") and key in rejected:
                    pass_configs.append(key)
                    passing_haircuts.append(float(c))
            if len(passing_haircuts) >= MIN_COST_SCENARIOS_PASS:
                cost_robust_pairs.append(
                    f"{sig}::bar{bar_s:g}::passes_at_cost={sorted(passing_haircuts)}"
                )

    power_adequate = bool(max_pooled_returns >= MIN_POOLED_RETURNS)
    go = bool(
        floor_and_disjoint_ok
        and pass_configs
        and cost_robust_pairs
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
        "EVAL_185_SURFACE_TRADED_ROBUSTNESS_GRID"
        if floor_and_disjoint_ok
        else "EVAL_185_BLOCKED_FLOOR_OR_DISJOINTNESS"
    )

    protocol = build_protocol(capture_dir)
    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict,
        "verdict_detail": (
            "surface-line traded-form robustness grid (disjoint real BTC+ETH window at "
            "data/raw/eval84cap) over 3 signals x 5 horizons x 3 cost haircuts = 45 "
            "pooled configs; bounds whether the EVAL-184 surface NO-GO is a "
            "monetization/horizon artifact. Pooled BH-FDR across the FULL grid; GO "
            "requires a cost-robust (>=2/3 haircuts) config that also clears Sharpe/"
            "max-DD/permutation/bootstrap/power, with EVAL-62 mark-path net-of-cost P&L "
            "+ EVAL-64 feasible floor reused verbatim"
            if floor_and_disjoint_ok
            else "capture below the pre-registered EVAL-64 feasible floor and/or missing "
                 "an underlying and/or overlapping the sealed window; no GO/NO-GO verdict"
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
            "the robustness grid consumes the same disjoint forward capture as EVAL-184, "
            "at/after 2026-11-20T00:00:00Z."
        ),
        "per_underlying_floor": per_underlying_floor,
        "disjointness": disjointness,
        "protocol": protocol,
        "per_config": per_config,
        "config_stats": cfg_stats,
        "pooled": {
            "bh_fdr": bh,
            "pass_configs": pass_configs,
            "cost_robust_pairs": cost_robust_pairs,
            "min_cost_scenarios_pass": MIN_COST_SCENARIOS_PASS,
            "max_pooled_returns": max_pooled_returns,
            "power_adequate": power_adequate,
            "min_pooled_returns": MIN_POOLED_RETURNS,
            "grid_config_count": GRID_CONFIG_COUNT,
            "campaign_state": campaign_state,
        },
        "errors": errors,
    }

    if not write:
        return report

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
            "The EVAL-184 surface-line NO-GO is NOT a monetization/horizon artifact: "
            "no signal/horizon config in the pre-registered 3x5x3 cost x horizon grid "
            "yields a pooled BH-FDR rejection with net-of-cost Sharpe>0 + bootstrap CI "
            "lower>0 + nonzero positions + >=790 pooled returns at >=2 of 3 cost "
            "haircuts (cost-robust), at the sealed EVAL-64 floor on both underlyings. If "
            "such a config exists, the surface line is monetizable and EVAL-184's NO-GO "
            "was horizon/cost-specific (GO CONFIRMED)."
        ),
        "extends": p["extends"],
        "disjointness_rule": report["disjointness_rule"],
        "data_availability": {
            "note": "consumes the SAME freshly acquired disjoint BTC+ETH three-way "
                    "capture at data/raw/eval84cap as EVAL-184 (read-only); public "
                    "read-only; no synthetic data",
            "sealed_window": [SEALED_WINDOW_START, SEALED_WINDOW_END],
            "earliest_disjoint_capture_end": EARLIEST_DISJOINT_CAPTURE_END,
        },
        "protocol": p,
        "capture_dir": report["capture_dir"],
    }


def _build_prereg_md(r: Dict[str, Any]) -> str:
    p = r["protocol"]
    lines = [
        f"# {PREREG_ID} — surface-line traded-form ROBUSTNESS GRID (is the EVAL-184 "
        f"surface NO-GO a monetization/horizon artifact?)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Hypothesis: {r['hypothesis']}",
        f"- Capture dir: `{r['capture_dir']}` (same disjoint forward capture as EVAL-184)",
        f"- Extends: {p['extends']}",
        f"- Disjoint from: [{SEALED_WINDOW_START}, {SEALED_WINDOW_END}]",
        "",
        "## Pre-declared protocol",
        "",
        f"- Underlyings: {p['floor']['min_underlyings']} (BTC+ETH)",
        f"- Surface signals: {p['surface_signals']}",
        f"- Signal targets: {p['signal_target']}",
        f"- Signal builders: {p['signal_builder']}",
        f"- Horizon grid (s): {p['horizon_grid_seconds']}",
        f"- Cost haircuts: {p['cost_haircuts']}",
        f"- Grid config count: {p['grid_config_count']}",
        f"- Signal window (s): {p['signal_window_seconds']}",
        f"- Target: signal-timed delta-hedged ATM straddle mark-path net-of-cost P&L, "
        f"pooled across BTC+ETH; cost haircut scales BOTH hedge fee and real spread",
        f"- Statistic: {p['stats']}",
        f"- Power adequacy: pooled returns >= {p['min_pooled_returns']}",
        f"- Cost-robustness: a (signal,horizon) passes at >= "
        f"{p['min_cost_scenarios_pass']} of 3 cost haircuts",
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
        f"# {r['report_id']} — surface-line traded-form ROBUSTNESS GRID (is the "
        f"EVAL-184 surface NO-GO a monetization/horizon artifact?)",
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
        f"- Grid: {r['pooled']['grid_config_count']} configs "
        f"({r['protocol']['surface_signals']} x "
        f"{r['protocol']['horizon_grid_seconds']} x {r['protocol']['cost_haircuts']})",
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
    lines += ["", "## Pooled per-config (signal x horizon x cost haircut)",
              "| signal | bar_s | cost | pooled n | power ok | Sharpe | max-DD | perm_p | CI95 | BH-rej | pass |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    cs = r.get("config_stats", {})
    for key in sorted(cs):
        sig, rest = key.split("::", 1)
        bar_s, cost = rest.split("::")
        bar_s = bar_s.replace("bar", "")
        cost = cost.replace("cost", "")
        st = cs[key]
        ci_low = st.get("ci_low", 0.0)
        ci_high = st.get("ci_high", 0.0)
        rej = "yes" if key in set(r["pooled"]["bh_fdr"].get("rejected") or []) else "no"
        lines.append(
            f"| {sig} | {bar_s} | {cost} | {st.get('n')} | "
            f"{st.get('n', 0) >= MIN_POOLED_RETURNS} | "
            f"{_finite(st.get('sharpe'), 0.0):.4f} | "
            f"{_finite(st.get('max_drawdown'), 0.0):.4f} | "
            f"{_finite(st.get('perm_p'), 1.0):.4f} | "
            f"[{_finite(ci_low, 0.0):.4f}, {_finite(ci_high, 0.0):.4f}] | {rej} | {st.get('pass')} |"
        )
    lines += ["", "## Pooled",
              f"- BH-FDR rejected configs: {r['pooled']['bh_fdr'].get('rejected')}",
              f"- Pass configs: {r['pooled']['pass_configs']}",
              f"- Cost-robust (signal,horizon) pairs: {r['pooled']['cost_robust_pairs']}",
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
        f"# {BLOCKED_ID} — surface-line traded-form ROBUSTNESS GRID "
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
            "the robustness grid consumes the same disjoint forward capture as EVAL-184, "
            "at/after 2026-11-20T00:00:00Z."
        ),
    }
    return _build_prereg(report)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-185: surface-line traded-form ROBUSTNESS GRID (is the "
                    "EVAL-184 surface NO-GO a monetization/horizon artifact?)"
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
        report = run_eval185(
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
        "grid_config_count": report.get("pooled", {}).get("grid_config_count"),
        "max_pooled_returns": report.get("pooled", {}).get("max_pooled_returns"),
        "power_adequate": report.get("pooled", {}).get("power_adequate"),
        "bh_fdr_rejected": report.get("pooled", {}).get("bh_fdr", {}).get("rejected"),
        "pass_configs": report.get("pooled", {}).get("pass_configs"),
        "cost_robust_pairs": report.get("pooled", {}).get("cost_robust_pairs"),
        "n_configs": len(report.get("per_config", [])),
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())