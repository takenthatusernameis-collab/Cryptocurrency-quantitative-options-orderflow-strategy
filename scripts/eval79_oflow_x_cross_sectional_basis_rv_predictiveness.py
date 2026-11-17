#!/usr/bin/env python3
"""EVAL-79: does the **causal options order-flow imbalance, conditioned on the
cross-sectional implied-volatility basis**, predict subsequent realized vol? — a
distinct, runnable-**now** conditional-flow signal-family falsification on the
real on-disk three-way captures.

Why this rung exists (the on-charter question EVAL-65/68/77 leave open)
-----------------------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + **options order-flow** + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. The runnable-now line so far:

* EVAL-65 sealed ``NO-GO CONFIRMED`` — the *unconditional* options order-flow
  toxicity / signed-aggressor imbalance has no monotone RV relationship;
* EVAL-70 sealed ``NO-GO CONFIRMED`` — the *unconditional* underlying (perp)
  order flow has no RV / signed-return predictiveness;
* EVAL-71 / EVAL-73 sealed ``GO CONFIRMED`` — the single-underlying surface
  (near-ATM IV level + skew) predicts forward RV, stable OOS;
* EVAL-74 sealed ``NO-GO CONFIRMED (PASS)`` — the term-structure slope predicts
  ETH forward RV but is null on BTC;
* EVAL-77 sealed ``GO CONFIRMED`` — the *cross-sectional* BTC-vs-ETH near-ATM IV
  basis predicts the subsequent BTC-minus-ETH RV spread;
* EVAL-78 sealed ``NO-GO CONFIRMED (PASS)`` — the options order-flow imbalance x
  single-underlying surface interaction (atm_iv / skew per underlying) adds no
  portable forward-RV predictiveness;
* EVAL-72 / EVAL-75 / EVAL-76 sealed ``NO-GO CONFIRMED (PASS)`` — no surface /
  term-structure signal monetizes net-of-cost via an ATM straddle or risk
  reversal.

Every flow rung above tests order-flow **unconditionally** (EVAL-65) or interacted
with a **single-underlying** surface state (EVAL-78). None tests whether the
options order-flow imbalance carries forward-RV information that is
**state-dependent on the cross-sectional BTC-vs-ETH IV basis** (EVAL-77's GO
signal). That is the genuinely distinct, on-charter, runnable-**now** signal none
of them covers: does buy-heavy options flow predict higher subsequent realized vol
*specifically when* ETH is IV-rich relative to BTC (equivalently BTC is IV-cheap)?
It needs only the already-acquired real three-way captures (per-bar near-ATM
option-trade IV for BTC and ETH + option trade tape with direction + perp
candles), **no new acquisition** and **no network**.

    When options order-flow is buy-heavy AND the cross-sectional near-ATM IV
    basis is extreme (ETH rich vs BTC), does subsequent realized volatility rise?
    I.e. is the causal (options order-flow z) x (cross-sectional basis z)
    interaction informative about subsequent realized vol?

This does **not** re-litigate any sealed result: EVAL-65 measured unconditional
flow, EVAL-77 measured the unconditional cross-sectional basis, and EVAL-78
measured flow x single-underlying surface. EVAL-79 measures flow x
cross-sectional basis, reusing all sealed signal reconstructions verbatim.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
--------------------------------------------------------------------------------
For each underlying, each surface leg ``{atm_iv, skew}`` of the cross-sectional
basis ``rel_k = signal[ETH](k) - signal[BTC](k)``, each bar grid ``{60s, 300s}``
and each forward horizon ``H`` bars, on the common aligned bar grid:

    oflow_z_k   = causal expanding-z-scored options order-flow imbalance (EVAL-61/62)
    basis_z_k   = causal expanding-z-scored cross-sectional IV basis (EVAL-77 build)
    x_k         = oflow_z_k * basis_z_k                       (the interaction)
    rv_k        = sqrt(mean(log-return^2)) over the next H perp bars (EVAL-71 def)

Compute the Spearman rank ``IC = rho(x_k, rv_k)``. **GO only if, on BOTH BTC and
ETH, at least one config** has ``IC > 0`` (basis-conditioned buy-heavy flow
amplifies into higher subsequent realized vol), directional permutation
``p < 0.05``, block-bootstrap 95% CI lower ``> 0``, at least
``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs, and pooled BH-FDR rejects that
config; else ``NO-GO CONFIRMED (PASS)``.

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
--------------------------------------------------------------------------------
EVAL-79 consumes both underlyings' trade-tape IV surfaces (cross-sectional basis)
and both options order-flow tapes, so it composes three honestly pre-registered
floors and requires all, for **each** underlying:

* the EVAL-71 surface floor (option trades / near-ATM trades / perp candles /
  span), reused verbatim; and
* an options order-flow adequacy floor: at least
  ``MIN_OFLOW_STATES_PER_UNDERLYING`` priceable per-bar order-flow states
  (real surface snapshots carrying a front-expiry straddle and a causal
  order-flow z); and
* a cross-sectional alignment floor: at least
  ``MIN_ALIGNED_COMMON_BARS`` bar-ends where both underlyings carry a causal
  near-ATM IV on the coarsest grid.

None is weakened. Below the composed floor it seals
``EVAL_79_..._BLOCKED_<UTC>`` (never a NO-GO). The EVAL-64 feasible floor that
governs the EVAL-67/68/69 ladder is untouched.

Seals ``EVAL_79_OFLOW_X_CROSS_SECTIONAL_BASIS_RV_PREDICTIVENESS_PREREGISTRATION_<UTC>``
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

# Reuse the sealed EVAL-61 measurement helpers, EVAL-62 order-flow states +
# constants, EVAL-65 statistics, the EVAL-71 surface reconstruction, and the
# EVAL-77 cross-sectional basis builder verbatim (no forks, no src edits).
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
import scripts.eval77_cross_sectional_surface_basis_rv_predictiveness as e77  # noqa: E402
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_79_OFLOW_X_CROSS_SECTIONAL_BASIS_RV_PREDICTIVENESS_COMBINED"
PREREG_ID = "EVAL_79_OFLOW_X_CROSS_SECTIONAL_BASIS_RV_PREDICTIVENESS_PREREGISTRATION"
BLOCKED_ID = "EVAL_79_OFLOW_X_CROSS_SECTIONAL_BASIS_RV_PREDICTIVENESS_BLOCKED"

# Pre-registered grid: cross-sectional basis legs x order-flow leg x bar grid x
# forward horizons.
BASIS_SIGNALS: Tuple[str, ...] = ("atm_iv", "skew")
OFLOW_SIGNALS: Tuple[str, ...] = ("imbalance",)
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
FORWARD_HORIZONS_BARS: Tuple[int, ...] = (6, 24, 72)

# Statistics reused verbatim from EVAL-62/65 (identical permutation / bootstrap /
# seed) so the EVAL-79 inference is byte-for-byte the sealed line's.
PERMUTATION_PERMS = e65.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e65.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e65.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
ZWINDOW = e62.ZWINDOW

# A config needs at least this many usable (interaction, rv) pairs to be evaluable
# (a result-quality guard, not a data floor).
MIN_USABLE_PAIRS_PER_CONFIG = 120

# Composed heavy-work floor (EVAL-71 surface floor for each underlying AND an
# order-flow state floor AND a cross-sectional alignment floor; none weakened).
FLOOR: Dict[str, Any] = {
    "min_underlyings": 2,
    "min_oflow_states_per_underlying": 200,
    "min_aligned_common_bars": 200,
    "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
    "note": (
        "EVAL-79 consumes both underlyings' trade-tape IV surfaces (cross-sectional "
        "basis) and both options order-flow tapes. It composes the sealed EVAL-71 "
        "surface floor (applied to EACH underlying, reused verbatim, neither "
        "weakened) with an options order-flow adequacy floor (>= "
        "min_oflow_states_per_underlying priceable per-bar order-flow states per "
        "underlying) and a cross-sectional alignment floor (>= "
        "min_aligned_common_bars common bar-ends on the coarsest grid). This is NOT "
        "the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/"
        "69 ladder and is untouched here."
    ),
}

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval77_cross_sectional_surface_basis_rv_predictiveness.py",
    "scripts/eval79_oflow_x_cross_sectional_basis_rv_predictiveness.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval79_oflow_x_cross_sectional_basis_rv_predictiveness.py "
    "tests/test_eval79_oflow_x_cross_sectional_basis_rv_predictiveness.py",
    "python3 -m pytest -q tests/test_eval79_oflow_x_cross_sectional_basis_rv_predictiveness.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval79_oflow_x_cross_sectional_basis_rv_predictiveness.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval79_oflow_x_cross_sectional_basis_rv_predictiveness.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL79-OFLOW-X-CROSS-SECTIONAL-BASIS-RV-PREDICTIVENESS",
)


# ---------------------------------------------------------------------------
# Small helpers (local; no src edits)
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite(x: Any, default: float = 0.0) -> float:
    return e71._finite(x, default)


def _rv_series(closes: Sequence[float], horizon_bars: int) -> List[float]:
    """Forward realized vol over the next H bars (identical definition to
    EVAL-71/EVAL-77/EVAL-78 ``_rv_series``): ``sqrt(mean(log-return^2))``."""
    lr = (
        [math.log(closes[i + 1] / closes[i]) for i in range(len(closes) - 1)]
        if len(closes) >= 2
        else []
    )
    h = int(horizon_bars)
    rv: List[float] = []
    for k in range(0, len(lr) - h + 1):
        seg = lr[k:k + h]
        rv.append(math.sqrt(sum(r * r for r in seg) / float(h)))
    return rv


# ---------------------------------------------------------------------------
# Per-underlying (order-flow state, cross-sectional basis, forward RV) grid
# ---------------------------------------------------------------------------
def _aligned_rows(
    capture: Dict[str, Any],
    inst: str,
    cs: Dict[str, Any],
    basis_z: Sequence[float],
    *,
    bar_seconds: float,
) -> List[Tuple[int, float, float, float]]:
    """Align one underlying's causal order-flow states (EVAL-62) with the
    cross-sectional basis z (EVAL-77) on the common bar grid.

    Returns ``[(bar_open_ms, spot, oflow_z, basis_z), ...]`` sorted ascending by
    bar-open; one row per common bar-end where the underlying carries a causal,
    priceable order-flow state.
    """
    states = e62.build_states(capture, tox_signal="imbalance", bar_seconds=bar_seconds)
    state_map: Dict[int, float] = {}
    for s in states:
        bm = int(s.get("bar_ms") or 0)
        state_map[bm] = float(s.get("signal_z", 0.0))
    smap = cs["maps"][inst]
    common = cs["common"]
    rows: List[Tuple[int, float, float, float]] = []
    for i, m in enumerate(common):
        if m not in state_map:
            continue
        bar = smap.get(m)
        if bar is None:
            continue
        spot = _finite(bar.get("close"), 0.0)
        if spot <= 0.0:
            continue
        rows.append((m, spot, state_map[m], float(basis_z[i])))
    rows.sort(key=lambda r: r[0])
    return rows


def evaluate_config(
    captures: Dict[str, Dict[str, Any]],
    *,
    basis_signal: str,
    bar_seconds: float,
    horizon_bars: int,
) -> Dict[str, Any]:
    """Basis-conditioned order-flow predictiveness for one config (pooled across
    underlyings for the statistic, reported per underlying)."""
    cs = e77.build_cross_section(captures, bar_seconds=bar_seconds)
    common = cs["common"]
    n_common = len(common)
    if n_common < int(horizon_bars) + 5:
        return {
            "basis_signal": basis_signal,
            "bar_seconds": float(bar_seconds),
            "horizon_bars": int(horizon_bars),
            "error": "insufficient common surface bars",
            "n_common_bars": n_common,
            "n_pairs": 0,
            "pass": False,
        }

    basis_z = e77._relative_signal_series(cs, surface_signal=basis_signal)

    per_inst: Dict[str, Dict[str, Any]] = {}
    xs_all: List[float] = []
    ys_all: List[float] = []
    for inst in sorted(captures):
        rows = _aligned_rows(
            captures[inst], inst, cs, basis_z, bar_seconds=bar_seconds
        )
        closes = e77._closes_on_common(cs, inst)
        rv = _rv_series(closes, horizon_bars)
        n = min(len(rv), len(rows))
        xs: List[float] = []
        ys: List[float] = []
        for k in range(n):
            xs.append(float(rows[k][2]) * float(rows[k][3]))
            ys.append(float(rv[k]))
        if len(xs) < int(MIN_USABLE_PAIRS_PER_CONFIG):
            per_inst[inst] = {
                "underlying": inst,
                "error": "insufficient aligned pairs",
                "n_pairs": len(xs),
                "pass": False,
            }
            continue
        ic, perm_p = e65._perm_p_ic(xs, ys, PERMUTATION_PERMS, SEED)
        med, ci_lo, ci_hi = e65._boot_ci_ic(
            xs, ys, BOOTSTRAP_RESAMPLES, BOOTSTRAP_BLOCK, SEED
        )
        passed = bool(
            ic > 0.0
            and perm_p < 0.05
            and ci_lo > 0.0
            and len(xs) >= int(MIN_USABLE_PAIRS_PER_CONFIG)
        )
        per_inst[inst] = {
            "underlying": inst,
            "n_pairs": len(xs),
            "spearman_ic": ic,
            "permutation_p": perm_p,
            "bootstrap_ci": [med, ci_lo, ci_hi],
            "nonzero_signal_pairs": int(sum(1 for v in xs if abs(v) > 1e-9)),
            "pass": passed,
        }
        xs_all.extend(xs)
        ys_all.extend(ys)

    if len(xs_all) < int(MIN_USABLE_PAIRS_PER_CONFIG):
        return {
            "basis_signal": basis_signal,
            "bar_seconds": float(bar_seconds),
            "horizon_bars": int(horizon_bars),
            "error": "insufficient pooled aligned pairs",
            "n_common_bars": n_common,
            "n_pairs": len(xs_all),
            "pass": False,
            "per_inst": per_inst,
        }

    ic, perm_p = e65._perm_p_ic(xs_all, ys_all, PERMUTATION_PERMS, SEED)
    med, ci_lo, ci_hi = e65._boot_ci_ic(
        xs_all, ys_all, BOOTSTRAP_RESAMPLES, BOOTSTRAP_BLOCK, SEED
    )
    passed = bool(
        ic > 0.0
        and perm_p < 0.05
        and ci_lo > 0.0
        and len(xs_all) >= int(MIN_USABLE_PAIRS_PER_CONFIG)
    )
    return {
        "basis_signal": basis_signal,
        "bar_seconds": float(bar_seconds),
        "horizon_bars": int(horizon_bars),
        "n_common_bars": n_common,
        "n_pairs": len(xs_all),
        "spearman_ic": ic,
        "permutation_p": perm_p,
        "bootstrap_ci": [med, ci_lo, ci_hi],
        "nonzero_signal_pairs": int(sum(1 for v in xs_all if abs(v) > 1e-9)),
        "pass": passed,
        "per_inst": per_inst,
    }


# ---------------------------------------------------------------------------
# Composed heavy-work floor (EVAL-71 surface floor AND order-flow state floor
# AND cross-sectional alignment floor)
# ---------------------------------------------------------------------------
def _underlying_floor(
    capture: Dict[str, Any], *, inst: str, captures: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """Composed per-underlying floor: EVAL-71 surface floor AND order-flow
    states (max over the two bar grids)."""
    surface = e71._underlying_surface_floor(capture)

    n_oflow_states = 0
    for bar_s in GRID_BAR_SECONDS:
        states = e62.build_states(
            capture, tox_signal="imbalance", bar_seconds=bar_s
        )
        n_oflow_states = max(n_oflow_states, len(states))
    oflow_ok = n_oflow_states >= int(FLOOR["min_oflow_states_per_underlying"])

    return {
        "underlying": inst,
        "surface_floor_ok": bool(surface.get("ok")),
        "surface_floor": surface,
        "n_oflow_states": n_oflow_states,
        "oflow_ok": oflow_ok,
        "checks": {
            "surface_floor_ok": bool(surface.get("ok")),
            "oflow_ok": oflow_ok,
        },
        "ok": bool(surface.get("ok") and oflow_ok),
    }


def campaign_floor(
    captures: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    insts = sorted(captures)
    per_underlying = {
        i: _underlying_floor(captures[i], inst=i, captures=captures) for i in insts
    }
    ok = bool(
        len(insts) >= int(FLOOR["min_underlyings"])
        and per_underlying
        and all(v["ok"] for v in per_underlying.values())
    )
    # Cross-sectional alignment floor on the coarsest grid (both underlyings
    # carry a causal near-ATM IV at the same bar-end).
    coarsest = max(GRID_BAR_SECONDS)
    if len(insts) >= 2:
        cs = e77.build_cross_section(captures, bar_seconds=coarsest)
        aligned_binding = len(cs["common"])
    else:
        aligned_binding = 0
    aligned_ok = aligned_binding >= int(FLOOR["min_aligned_common_bars"])
    return {
        "underlyings": insts,
        "per_underlying": per_underlying,
        "aligned_common_bars_coarsest": aligned_binding,
        "aligned_ok": aligned_ok,
        "checks": {
            "all_underlyings_ok": ok,
            "aligned_ok": aligned_ok,
        },
        "ok": bool(ok and aligned_ok),
    }


# ---------------------------------------------------------------------------
# Protocol + orchestration
# ---------------------------------------------------------------------------
def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-79",
        "title": "Options order-flow imbalance x cross-sectional implied-vol "
                 "basis -> subsequent realized volatility (wrapper-free rank "
                 "information coefficient) falsification on the real on-disk "
                 "three-way captures",
        "extends": "EVAL-65 (unconditional options order-flow -> RV), EVAL-77 "
                   "(unconditional cross-sectional IV basis -> RV spread) and "
                   "EVAL-78 (order-flow x single-underlying surface -> RV): the "
                   "same Spearman rank-IC statistic and all sealed signal "
                   "reconstructions reused verbatim, but a distinct, on-charter "
                   "signal family — the *interaction* of the options order-flow "
                   "imbalance and the cross-sectional BTC-vs-ETH near-ATM IV "
                   "basis; no new acquisition",
        "supersedes": "nothing — this is the cross-sectional-basis-conditioned "
                      "flow complement to EVAL-65 (unconditional flow), EVAL-77 "
                      "(unconditional cross-sectional basis) and EVAL-78 (flow x "
                      "single-underlying surface); none measured flow conditioned "
                      "on the cross-sectional basis",
        "capture_dir": str(capture_dir),
        "basis_signals": list(BASIS_SIGNALS),
        "oflow_signals": list(OFLOW_SIGNALS),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": "causal options order-flow imbalance z (EVAL-61/62 build_states, "
                  "expanding-z-scored) times causal cross-sectional near-ATM IV "
                  "basis z (EVAL-77 rel = signal[ETH] - signal[BTC], "
                  "forward-filled then expanding-z-scored end-of-bar k): "
                  "x_k = oflow_z_k * basis_z_k",
        "target": "rv = sqrt(mean(log-return^2)) over the next H perp bars "
                  "(EVAL-71 definition), per underlying, on the common aligned "
                  "bar grid",
        "statistic": "Spearman rank correlation IC = rho(x_k, rv_k) over the "
                     "common aligned bar-ends (H1: IC > 0, basis-conditioned "
                     "buy-heavy flow amplifies into higher subsequent realized vol)",
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation": "directional (H1: IC>0), shuffle the realized-vol series",
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
            "zwindow": ZWINDOW,
            "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
        },
        "go_bar": (
            "GO only if, on BOTH BTC and ETH, at least one config (basis leg x bar "
            "grid x horizon) has Spearman IC > 0, directional permutation p < 0.05, "
            "block-bootstrap 95% CI lower > 0, at least min_usable_pairs_per_config "
            "usable pairs, and pooled BH-FDR rejects that config; else NO-GO "
            "CONFIRMED (PASS)."
        ),
        "data_availability": {
            "note": "uses the already-acquired real on-disk three-way captures "
                    "(surface snapshots + option trade tape with direction + perp "
                    "candles); no new acquisition, no network; composes the EVAL-71 "
                    "floor for each underlying with an order-flow state floor and a "
                    "cross-sectional alignment floor",
            "capture_dir": str(capture_dir),
        },
        "floor": dict(FLOOR),
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def run_eval79(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL79-OFLOW-X-CROSS-SECTIONAL-BASIS-RV-PREDICTIVENESS",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    selected = e77._select_one_capture_per_underlying(
        e61._capture_inventory(str(capture_dir_abs))
    )
    captures = {str(c.get("underlying")): c for c in selected}

    floor = campaign_floor(captures)
    floor_ok = bool(floor["ok"])

    per_config: List[Dict[str, Any]] = []
    errors: List[str] = []
    for basis in BASIS_SIGNALS:
        for bar_s in GRID_BAR_SECONDS:
            for horizon in FORWARD_HORIZONS_BARS:
                try:
                    res = evaluate_config(
                        captures,
                        basis_signal=basis,
                        bar_seconds=bar_s,
                        horizon_bars=horizon,
                    )
                except BaseException as exc:  # noqa: BLE001
                    errors.append(
                        f"basis[{basis}]::bar{bar_s}::h{horizon}: {exc!r}"
                    )
                    continue
                per_config.append(res)

    p_values = {
        f"basis[{r['basis_signal']}]::bar{r['bar_seconds']}::"
        f"h{r['horizon_bars']}": _finite(r.get("permutation_p"), 1.0)
        for r in per_config
        if r.get("n_pairs", 0) > 0
    }
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}
    rejected = set(bh.get("rejected") or [])

    by_config: Dict[str, List[Dict[str, Any]]] = {}
    for r in per_config:
        key = (
            f"basis[{r['basis_signal']}]::bar{r['bar_seconds']}::"
            f"h{r['horizon_bars']}"
        )
        by_config.setdefault(key, []).append(r)

    config_summary: List[Dict[str, Any]] = []
    for key, rows in by_config.items():
        valid = [r for r in rows if r.get("n_pairs", 0) > 0]
        best = None
        if valid:
            best = max(valid, key=lambda r: _finite(r.get("spearman_ic"), -1e9))
        pass_configs = []
        for r in valid:
            if r.get("pass") and key in rejected:
                pass_configs.append(key)
        insts_ok = all(
            r.get("per_inst", {}).get(inst, {}).get("pass", False)
            for r in valid
            for inst in sorted(captures)
        )
        config_summary.append({
            "config": key,
            "n_underlyings": len(valid),
            "best_ic": _finite(best.get("spearman_ic"), 0.0) if best else 0.0,
            "best_config": (key if best else "n/a"),
            "n_pass": len(pass_configs),
            "pass_configs": pass_configs,
            "both_underlyings_pass": bool(insts_ok),
        })

    all_pass = bool(config_summary) and all(s["both_underlyings_pass"] for s in config_summary)
    go = bool(floor_ok and all_pass and len(rejected) >= 1)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = (
        "EVAL_79_OFLOW_X_CROSS_SECTIONAL_BASIS_RV_PREDICTIVENESS" if floor_ok
        else "EVAL_79_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free information-content test: Spearman rank IC between the "
            "causal options order-flow imbalance x cross-sectional implied-vol "
            "basis interaction and forward realized volatility on the real "
            "on-disk captures"
            if floor_ok else "capture below the composed EVAL-71 + order-flow + "
                             "cross-sectional floor; no verdict"
        ),
        "floor_ok": bool(floor_ok),
        "capture_dir": str(capture_dir_abs),
        "underlyings": sorted(captures),
        "floor": dict(FLOOR),
        "campaign_floor": floor,
        "protocol": build_protocol(capture_dir),
        "per_config": per_config,
        "config_summary": config_summary,
        "summary": {
            "n_configs": len(per_config),
            "n_pass": sum(s["n_pass"] for s in config_summary),
            "config_summary": config_summary,
        },
        "pooled": {
            "bh_fdr": bh,
            "any_config_pass": all_pass,
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
            "The causal interaction of the options order-flow imbalance with the "
            "cross-sectional near-ATM implied-volatility basis (product of the "
            "EVAL-61/62 order-flow z and the EVAL-77 cross-sectional basis z, "
            "reconstructed from the real Deribit option trade tape and real surface "
            "snapshots) has a positive monotone (Spearman rank) relationship with "
            "subsequent realized volatility: basis-conditioned buy-heavy flow "
            "amplifies into higher subsequent realized vol. Tested on the "
            "already-acquired real on-disk captures at the composed EVAL-71 + "
            "order-flow + cross-sectional floor."
        ),
        "extends": p["extends"],
        "data_availability": p["data_availability"],
        "protocol": p,
        "capture_dir": report["capture_dir"],
    }


def _build_prereg_md(r: Dict[str, Any]) -> str:
    p = r["protocol"]
    fl = p["floor"]
    lines = [
        f"# {PREREG_ID} — options order-flow x cross-sectional IV basis -> "
        f"realized-vol predictiveness (wrapper-free Spearman rank IC)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Hypothesis: {r['hypothesis']}",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Extends: {p['extends']}",
        "",
        "## Pre-declared protocol",
        "",
        f"- Cross-sectional basis signals: {p['basis_signals']}",
        f"- Order-flow signals: {p['oflow_signals']}",
        f"- Bar grid (s): {p['bar_seconds_grid']}",
        f"- Forward horizons (bars): {p['forward_horizons_bars']}",
        f"- Signal: {p['signal']}",
        f"- Target detail: {p['target']}",
        f"- Statistic: {p['statistic']}",
        f"- Stats: perm {p['stats']['permutation_perms']} ({p['stats']['permutation']}) / "
        f"bootstrap {p['stats']['bootstrap_resamples']} block {p['stats']['bootstrap_block']} / "
        f"BH-FDR alpha {p['stats']['fdr_alpha']} / seed {p['stats']['seed']} / "
        f"zwindow {p['stats']['zwindow']} / "
        f"min usable pairs {p['stats']['min_usable_pairs_per_config']}",
        "",
        "## Pre-declared GO bar",
        "",
        p["go_bar"],
        "",
        "## Pre-registered composed floor (EVAL-71 surface + order-flow state + "
        "cross-sectional alignment)",
        "",
        f"- {fl['note']}",
        f"- Min underlyings: {fl['min_underlyings']}",
        f"- Min order-flow states per underlying: {fl['min_oflow_states_per_underlying']}",
        f"- Min aligned common bars (coarsest grid): {fl['min_aligned_common_bars']}",
        f"- Min usable pairs per config: {fl['min_usable_pairs_per_config']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    fl = r["campaign_floor"]
    lines = [
        f"# {r['report_id']} — options order-flow x cross-sectional IV basis -> "
        f"realized-vol predictiveness (wrapper-free rank IC) falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        "",
        "## Per-underlying composed floor",
        "",
        "| underlying | surface floor ok | n option trades | n oflow states | oflow ok | ok |",
        "|---|---|---|---|---|---|",
    ]
    for inst, u in fl["per_underlying"].items():
        s = u["surface_floor"]
        lines.append(
            f"| {inst} | {u['surface_floor_ok']} | {s.get('n_option_trades')} | "
            f"{u.get('n_oflow_states')} | {u.get('oflow_ok')} | {u['ok']} |"
        )
    lines += ["", "## Cross-sectional alignment", "",
              f"- Aligned common bars on coarsest grid ({max(GRID_BAR_SECONDS):.0f}s): "
              f"{fl['aligned_common_bars_coarsest']} (floor >= {FLOOR['min_aligned_common_bars']})",
              f"- Aligned ok: {fl['aligned_ok']}",
              "", "## Configs (best first by pooled Spearman IC)", ""]
    lines += ["| basis signal | bar s | horizon | n pairs | Spearman IC | perm p | bootstrap 95% CI | pass |",
              "|---|---|---|---|---|---|---|---|"]
    rows = sorted(
        [c for c in r["per_config"] if c.get("n_pairs", 0) > 0],
        key=lambda c: _finite(c.get("spearman_ic"), -1e9),
        reverse=True,
    )
    for c in rows:
        ci = c.get("bootstrap_ci") or [0.0, 0.0, 0.0]
        lines.append(
            f"| {c['basis_signal']} | {c['bar_seconds']:.0f} | "
            f"{c['horizon_bars']} | {c['n_pairs']} | {c['spearman_ic']:.4f} | "
            f"{c['permutation_p']:.4f} | "
            f"[{ci[0]:.4f}, {ci[1]:.4f}, {ci[2]:.4f}] | {c['pass']} |"
        )
    lines += ["", "## Pooled", "",
              f"- BH-FDR rejected: {r['pooled']['bh_fdr'].get('rejected')}",
              f"- Any config pass (both underlyings): {r['pooled']['any_config_pass']}",
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
        f"# {BLOCKED_ID} — options order-flow x cross-sectional IV basis -> "
        f"realized-vol predictiveness (below the composed EVAL-71 + order-flow + "
        f"cross-sectional floor)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        "- Verdict: **BLOCKED** (measured; not NO-GO)",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Underlyings: {', '.join(r['underlyings'])}",
        "",
        "The capture does not meet the composed EVAL-71 + order-flow + "
        "cross-sectional floor, so no GO/NO-GO verdict is emitted. Do NOT weaken "
        "any floor, do NOT use synthetic data, and do NOT emit NO-GO on "
        "under-floor data.",
        "",
        "## Per-underlying composed floor",
        "",
    ]
    for inst, u in fl["per_underlying"].items():
        lines.append(
            f"- {inst}: surface_floor_ok={u.get('surface_floor_ok')} "
            f"n_oflow_states={u.get('n_oflow_states')} oflow_ok={u.get('oflow_ok')} "
            f"checks={json.dumps(u.get('checks'))}"
        )
    lines.append(
        f"- aligned_common_bars_coarsest={fl.get('aligned_common_bars_coarsest')} "
        f"aligned_ok={fl.get('aligned_ok')}"
    )
    lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-79: options order-flow imbalance x cross-sectional "
                    "implied-vol basis -> realized-vol predictiveness (Spearman "
                    "rank IC) on the real on-disk captures"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument(
        "--task-label", default="EVAL79-OFLOW-X-CROSS-SECTIONAL-BASIS-RV-PREDICTIVENESS"
    )
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval79(
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
        "bh_fdr_rejected": report.get("pooled", {}).get("bh_fdr", {}).get("rejected"),
        "n_configs": len(report.get("per_config", [])),
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
