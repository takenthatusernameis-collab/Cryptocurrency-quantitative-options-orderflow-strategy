#!/usr/bin/env python3
"""EVAL-83: does one crypto's **options implied-volatility surface** carry causal
information about the **other crypto's subsequent realized volatility**? — a
cross-asset, lead-lag *spillover* predictiveness falsification, runnable **now** on
the real on-disk three-way captures.

Why this rung exists (the one on-charter cell EVAL-71/73/77 leave open)
-----------------------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + **options order-flow** + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. The runnable-now predictiveness
line has measured these surface x target cells:

* EVAL-71 sealed ``GO CONFIRMED`` — the *own-asset* surface (near-ATM IV level /
  put-call skew) predicts the *same* underlying's forward realized volatility on
  BOTH BTC and ETH; EVAL-73 confirmed it is stable across a disjoint OOS split.
* EVAL-77 sealed ``GO CONFIRMED`` — the *contemporaneous cross-sectional basis*
  (BTC-minus-ETH relative near-ATM IV / skew) predicts the *subsequent BTC-minus-ETH
  RV spread*.
* EVAL-74 (term structure), EVAL-70/78/79/81 (order-flow) sealed NO-GO.

The one genuinely distinct, on-charter, runnable-**now** cell none of them covers
is a **cross-asset lead-lag** question:

    Does the causal options *surface* of one crypto at bar ``k`` carry monotone
    information about the *subsequent* forward realized volatility of the OTHER
    crypto over bars ``k+1..k+H`` — i.e. does BTC's option-implied vol lead ETH's
    realized vol (and vice versa)?

This is **not** EVAL-71 (that is *own-asset*: surface -> same-asset RV) and **not**
EVAL-77 (that is *contemporaneous cross-sectional basis* -> *contemporaneous* RV
*spread*). EVAL-83 is *temporal cross-asset*: leader surface at ``k`` -> target
forward RV strictly after ``k``. It is the sharpest remaining expression of the
repo's *cross-sectional crypto options* thesis, and it is runnable **today** on the
already-acquired real on-disk captures (surface trade tape + perp candles for both
underlyings), with **no new acquisition** and **no network**.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
--------------------------------------------------------------------------------
For each **ordered** pair ``(leader, target)`` with ``leader != target`` (so
``BTC->ETH`` and ``ETH->BTC``), each leader surface signal ``{atm_iv, skew}``,
each bar grid ``{60s, 300s}`` and each forward horizon ``H`` bars, on the common
bar timestamps of the two underlyings:

    x_k        = causal, expanding-z-scored leader surface signal at bar k
                 (EVAL-71 ``build_surface_bars`` reconstruction, reused verbatim)
    y_k        = target forward realized volatility over the target's bars k+1..k+H
                 (EVAL-71 ``_forward_rv``, reused verbatim)
    c_k        = target's OWN causal surface signal z at bar k (control)

Compute the raw cross-asset Spearman rank ``spillover_ic = rho(x_k, y_k)`` with the
sealed EVAL-65 directional permutation and block bootstrap, and a *partial*
Spearman ``partial_ic = rho(x_k, y_k | c_k)`` (residualizing both ``x`` and ``y`` on
the target's own surface ``c``) as an incremental-over-own-surface control. A
config **passes** only if ``spillover_ic > 0``, directional permutation ``p < 0.05``,
block-bootstrap 95% CI lower ``> 0``, ``partial_ic > 0`` (the spillover is not
merely the target's own surface re-expressed), and at least
``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs.

**GO only if, for EACH target underlying, at least one incoming-spillover config
(from the other asset) passes AND pooled BH-FDR rejects that config; else ``NO-GO
CONFIRMED (PASS)``.** The per-direction detail is reported so a one-directional
spillover (e.g. BTC->ETH but not ETH->BTC) is visible even when the symmetric GO
bar is not met.

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
--------------------------------------------------------------------------------
EVAL-83 consumes each underlying's causal surface series (which needs the real
option trade tape for the IV surface and the real perp candles for forward RV) and
requires a minimum overlap between the two underlyings' bar grids. It therefore
composes two honestly pre-registered floors, requiring both:

* the sealed EVAL-71 surface floor for **each** underlying (option trades / near-ATM
  trades / perp candles / span), reused verbatim and not weakened; and
* a cross-asset common-bar floor: at least ``min_common_bars_per_pair`` common bar
  timestamps between each ordered pair on the coarser (300 s) grid.

Below the composed floor it seals ``EVAL_83_..._BLOCKED_<UTC>`` (never a NO-GO).
The EVAL-64 feasible floor that governs the EVAL-67/68/69 ladder is untouched.

This does **not** re-litigate any sealed result: EVAL-71/73 measured *own-asset*
surface -> own-asset RV; EVAL-77 measured *contemporaneous* cross-sectional basis
-> RV spread. EVAL-83 measures the *temporal cross-asset* leader surface -> target
forward RV, reusing all sealed signal reconstructions and the sealed EVAL-65
inference verbatim.

Seals ``EVAL_83_CROSS_ASSET_SURFACE_SPILLOVER_RV_PREDICTIVENESS_PREREGISTRATION_<UTC>``
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

# Reuse the sealed EVAL-61/62/65/71 measurement + inference helpers verbatim
# (no forks, no src edits).
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_83_CROSS_ASSET_SURFACE_SPILLOVER_RV_PREDICTIVENESS_COMBINED"
PREREG_ID = "EVAL_83_CROSS_ASSET_SURFACE_SPILLOVER_RV_PREDICTIVENESS_PREREGISTRATION"
BLOCKED_ID = "EVAL_83_CROSS_ASSET_SURFACE_SPILLOVER_RV_PREDICTIVENESS_BLOCKED"

# Pre-registered grid: leader surface signal x bar grid x forward horizon. The
# target is always the TARGET underlying's forward realized volatility.
SURFACE_SIGNALS: Tuple[str, ...] = ("atm_iv", "skew")
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
FORWARD_HORIZONS_BARS: Tuple[int, ...] = (6, 24, 72)
TARGET = "forward_rv"

# Map a surface signal name to its per-bar z-series key built by
# ``_asset_surface_series`` (both are expanding-z-scored causal signals).
SIGNAL_Z_KEY: Dict[str, str] = {"atm_iv": "atm_iv_z", "skew": "skew_z"}

# Trailing window / near-ATM band reused verbatim from the sealed EVAL-71 surface.
SIGNAL_WINDOW_SECONDS: float = e71.SIGNAL_WINDOW_SECONDS
ATM_BAND: float = e71.ATM_BAND

# Statistics reused verbatim from EVAL-65 (identical permutation / bootstrap / seed)
# for the raw cross-asset spillover IC.
PERMUTATION_PERMS = e65.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e65.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e65.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
ZWINDOW = e62.ZWINDOW

# A config needs at least this many usable (leader signal, target forward RV) pairs
# to be evaluable (a result-quality guard, not a data floor).
MIN_USABLE_PAIRS_PER_CONFIG = 100

# Composed heavy-work floor (EVAL-71 surface floor for each underlying AND a
# cross-asset common-bar floor; none weakened).
FLOOR: Dict[str, Any] = {
    "min_underlyings": 2,
    "min_common_bars_per_pair": 150,
    "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
    "note": (
        "EVAL-83 consumes each underlying's causal options-surface series (real "
        "option trade tape for the IV surface, real perp candles for forward RV) and "
        "requires cross-asset overlap. It composes the sealed EVAL-71 surface floor "
        "(applied to EACH underlying, reused verbatim, neither weakened) with a "
        "cross-asset common-bar floor (>= min_common_bars_per_pair common bar "
        "timestamps between each ordered pair on the coarser 300 s grid). This is NOT "
        "the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/69 "
        "ladder and is untouched here."
    ),
}

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval83_cross_asset_surface_spillover_rv_predictiveness.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval83_cross_asset_surface_spillover_rv_predictiveness.py "
    "tests/test_eval83_cross_asset_surface_spillover_rv_predictiveness.py",
    "python3 -m pytest -q tests/test_eval83_cross_asset_surface_spillover_rv_predictiveness.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval83_cross_asset_surface_spillover_rv_predictiveness.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval83_cross_asset_surface_spillover_rv_predictiveness.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL83-CROSS-ASSET-SURFACE-SPILLOVER-RV-PREDICTIVENESS",
)


# ---------------------------------------------------------------------------
# Small helpers (local; no src edits)
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite(x: Any, default: float = 0.0) -> float:
    return e71._finite(x, default)


def _residualize(ranked: Sequence[float], rc: Sequence[float]) -> List[float]:
    """Residuals of ``ranked`` after an OLS regression on ``rc`` (with intercept).

    Used to build the partial-Spearman control: residualizing both the leader
    signal and the target forward RV on the target's own surface ranks removes the
    own-surface component, leaving the incremental cross-asset co-movement.
    """
    n = len(ranked)
    if n < 3:
        return [0.0] * n
    mc = sum(rc) / n
    mr = sum(ranked) / n
    scc = sum((v - mc) ** 2 for v in rc)
    if scc <= 0.0:
        return [0.0] * n
    b = sum((rc[i] - mc) * (ranked[i] - mr) for i in range(n)) / scc
    a = mr - b * mc
    return [ranked[i] - (a + b * rc[i]) for i in range(n)]


def _partial_spearman(x: Sequence[float], y: Sequence[float], c: Sequence[float]) -> float:
    """Partial Spearman ``rho(x, y | c)``: Pearson correlation of the rank residuals
    of ``x`` and ``y`` after regressing each on the rank of the control ``c``.

    Returns ``0.0`` for degenerate inputs (e.g. ``x == c`` leaves no residual
    variance in ``x``, so the partial correlation is ``0`` — the correct limit).
    """
    if len(x) != len(y) or len(x) != len(c) or len(x) < 4:
        return 0.0
    rx = e65._rankdata(x)
    ry = e65._rankdata(y)
    rc = e65._rankdata(c)
    ex = _residualize(rx, rc)
    ey = _residualize(ry, rc)
    return e65._pearson(ex, ey)


# ---------------------------------------------------------------------------
# Per-asset causal surface z-series + forward RV, keyed by bar-open timestamp
# ---------------------------------------------------------------------------
def _asset_surface_series(
    capture: Dict[str, Any],
    *,
    bar_seconds: float,
    horizon_bars: int,
    signal_window_seconds: float = SIGNAL_WINDOW_SECONDS,
    atm_band: float = ATM_BAND,
) -> Dict[int, Dict[str, Any]]:
    """Causal per-bar surface signal z-series and target forward RV for one asset.

    Returns ``{bar_open_ms: {"atm_iv_z", "skew_z", "fwd_rv"}}`` where:

    * ``atm_iv_z`` / ``skew_z`` are the EVAL-71 surface signals (near-ATM IV level
      / put-minus-call skew) forward-filled then expanding-z-scored (EVAL-61
      ``expanding_zscore``), reusing EVAL-71 ``build_surface_bars`` verbatim;
    * ``fwd_rv`` is the forward realized volatility over the *next* ``H`` perp bars
      (EVAL-71 ``_forward_rv``), or ``None`` for bars without a full forward window.
    """
    bars = e71.build_surface_bars(
        capture,
        bar_seconds=bar_seconds,
        signal_window_seconds=signal_window_seconds,
        atm_band=atm_band,
    )
    fwd = e71._forward_rv(bars, horizon_bars)

    atm_filled = e71._forward_fill([b.get("atm_iv") for b in bars])
    skew_filled = e71._forward_fill([b.get("skew") for b in bars])
    atm_z = e61.expanding_zscore(atm_filled, ZWINDOW)
    skew_z = e61.expanding_zscore(skew_filled, ZWINDOW)

    out: Dict[int, Dict[str, Any]] = {}
    n_fwd = len(fwd)
    for k, b in enumerate(bars):
        out[int(b["bar_open_ms"])] = {
            "atm_iv_z": float(atm_z[k]) if k < len(atm_z) else 0.0,
            "skew_z": float(skew_z[k]) if k < len(skew_z) else 0.0,
            "fwd_rv": float(fwd[k]) if k < n_fwd else None,
        }
    return out


# ---------------------------------------------------------------------------
# Per-(ordered pair, signal, grid, horizon) spillover predictiveness
# ---------------------------------------------------------------------------
def evaluate_spillover(
    leader_capture: Dict[str, Any],
    target_capture: Dict[str, Any],
    *,
    surface_signal: str,
    bar_seconds: float,
    horizon_bars: int,
) -> Dict[str, Any]:
    """Cross-asset lead-lag spillover: leader surface z at bar k -> target forward
    RV over bars k+1..k+H, on the common bar timestamps of the two underlyings."""
    leader = str(leader_capture.get("underlying", "LEADER"))
    target = str(target_capture.get("underlying", "TARGET"))
    zkey = SIGNAL_Z_KEY[surface_signal]

    leader_series = _asset_surface_series(
        leader_capture, bar_seconds=bar_seconds, horizon_bars=horizon_bars
    )
    target_series = _asset_surface_series(
        target_capture, bar_seconds=bar_seconds, horizon_bars=horizon_bars
    )
    common = sorted(set(leader_series) & set(target_series))

    xs: List[float] = []
    ys: List[float] = []
    cs: List[float] = []
    for t in common:
        y = target_series[t].get("fwd_rv")
        if y is None:
            continue
        xs.append(float(leader_series[t].get(zkey, 0.0)))
        ys.append(float(y))
        cs.append(float(target_series[t].get(zkey, 0.0)))

    base = {
        "leader": leader,
        "target": target,
        "signal": surface_signal,
        "target_type": TARGET,
        "bar_seconds": float(bar_seconds),
        "horizon_bars": int(horizon_bars),
        "n_common_bars": len(common),
        "n_pairs": len(xs),
    }

    if len(xs) < 8:
        return {
            **base,
            "error": "insufficient aligned cross-asset pairs",
            "pass": False,
        }

    ic, perm_p = e65._perm_p_ic(xs, ys, PERMUTATION_PERMS, SEED)
    med, ci_lo, ci_hi = e65._boot_ci_ic(xs, ys, BOOTSTRAP_RESAMPLES, BOOTSTRAP_BLOCK, SEED)
    own_ic = e65._spearman(cs, ys)
    partial_ic = _partial_spearman(xs, ys, cs)

    passed = bool(
        len(xs) >= int(MIN_USABLE_PAIRS_PER_CONFIG)
        and ic > 0.0
        and perm_p < 0.05
        and ci_lo > 0.0
        and partial_ic > 0.0
    )
    return {
        **base,
        "n_nonzero_signal_pairs": int(sum(1 for v in xs if abs(v) > 1e-9)),
        "spillover_ic": ic,
        "permutation_p": perm_p,
        "bootstrap_ci": [med, ci_lo, ci_hi],
        "own_ic": own_ic,
        "partial_spillover_ic": partial_ic,
        "pass": passed,
    }


# ---------------------------------------------------------------------------
# Composed heavy-work floor (EVAL-71 surface floor AND cross-asset common-bar floor)
# ---------------------------------------------------------------------------
def _ordered_pairs(insts: Sequence[str]) -> List[Tuple[str, str]]:
    return [(a, b) for a in insts for b in insts if a != b]


def _common_bar_count(
    cap_a: Dict[str, Any], cap_b: Dict[str, Any], *, bar_seconds: float
) -> int:
    a = _asset_surface_series(cap_a, bar_seconds=bar_seconds, horizon_bars=1)
    b = _asset_surface_series(cap_b, bar_seconds=bar_seconds, horizon_bars=1)
    return len(set(a) & set(b))


def campaign_floor(captures: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    insts = sorted(captures)
    per_underlying = {i: e71._underlying_surface_floor(captures[i]) for i in insts}

    coarser = max(GRID_BAR_SECONDS)
    per_pair: Dict[str, Dict[str, Any]] = {}
    for a, b in _ordered_pairs(insts):
        try:
            n_common = _common_bar_count(captures[a], captures[b], bar_seconds=coarser)
            err = None
        except BaseException as exc:  # noqa: BLE001
            n_common = 0
            err = repr(exc)
        ok = n_common >= int(FLOOR["min_common_bars_per_pair"]) and err is None
        per_pair[f"{a}->{b}"] = {
            "leader": a,
            "target": b,
            "bar_seconds": float(coarser),
            "n_common_bars": n_common,
            "min_common_bars": int(FLOOR["min_common_bars_per_pair"]),
            "ok": bool(ok),
            **({"error": err} if err else {}),
        }

    ok = bool(
        len(insts) >= int(FLOOR["min_underlyings"])
        and per_underlying
        and all(v.get("ok") for v in per_underlying.values())
        and per_pair
        and all(v["ok"] for v in per_pair.values())
    )
    return {
        "underlyings": insts,
        "per_underlying": per_underlying,
        "per_pair": per_pair,
        "checks": {
            "all_underlyings_ok": all(v.get("ok") for v in per_underlying.values()) if per_underlying else False,
            "all_pairs_overlap_ok": all(v["ok"] for v in per_pair.values()) if per_pair else False,
        },
        "ok": ok,
    }


# ---------------------------------------------------------------------------
# Protocol + orchestration
# ---------------------------------------------------------------------------
def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-83",
        "title": "Cross-asset options implied-volatility surface lead-lag spillover -> "
                 "subsequent forward realized volatility: wrapper-free rank "
                 "information coefficient (predictiveness) falsification on the real "
                 "on-disk three-way captures",
        "extends": "EVAL-71/73 (own-asset surface -> own-asset forward RV) and EVAL-77 "
                   "(contemporaneous cross-sectional basis -> RV spread): the same "
                   "Spearman rank-IC statistic and all sealed signal reconstructions "
                   "reused verbatim, but a distinct, on-charter signal x target cell — "
                   "the *cross-asset temporal* leader surface vs the *target* forward "
                   "RV; no new acquisition",
        "supersedes": "nothing — this is the temporal cross-asset complement to "
                      "EVAL-71/73 (own-asset surface -> own RV) and EVAL-77 "
                      "(contemporaneous basis -> spread); none measured leader surface "
                      "vs the other asset's forward RV",
        "capture_dir": str(capture_dir),
        "surface_signals": list(SURFACE_SIGNALS),
        "target": TARGET,
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": "causal options-implied-vol surface (near-ATM IV level / put-call "
                  "skew) z (EVAL-71 build_surface_bars + EVAL-61 expanding_zscore, "
                  "end-of-bar k)",
        "target_detail": "target forward realized volatility = sqrt(mean(r^2)) over "
                         "the TARGET's next H perp bars (strictly after the decision "
                         "at bar k); the subsequent realized vol of the OTHER crypto",
        "statistic": "Spearman rank correlation IC = rho(leader_signal_z_k, "
                     "target_fwd_rv_k) over common bar timestamps (H1: IC > 0); plus a "
                     "partial Spearman rho(., . | target own surface z) as an "
                     "incremental-over-own-surface control",
        "go_bar": (
            "GO only if, for EACH target underlying, at least one incoming-spillover "
            "config (from the other asset; bar grid x horizon) has Spearman IC > 0, "
            "directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, "
            "partial-over-own-surface IC > 0, at least min_usable_pairs_per_config "
            "usable pairs, and pooled BH-FDR rejects that config; else NO-GO "
            "CONFIRMED (PASS). Per-direction detail is reported so a one-directional "
            "spillover is not misread as bidirectional."
        ),
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation": "directional (H1: IC>0), shuffle the target forward-RV series",
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
            "zwindow": ZWINDOW,
            "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
        },
        "data_availability": {
            "note": "uses the already-acquired real on-disk three-way captures "
                    "(surface snapshots + option trade tape with IV + perp candles) "
                    "for BOTH underlyings; no new acquisition, no network; composes "
                    "the EVAL-71 surface floor for each underlying with a cross-asset "
                    "common-bar floor",
            "capture_dir": str(capture_dir),
        },
        "floor": dict(FLOOR),
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def _select_captures(capture_dir_abs: Path) -> Dict[str, Dict[str, Any]]:
    selected = e71._select_one_capture_per_underlying(
        e61._capture_inventory(str(capture_dir_abs))
    )
    captures: Dict[str, Dict[str, Any]] = {}
    for cap in selected:
        inst = str(cap.get("underlying"))
        if inst and inst not in captures:
            captures[inst] = cap
    return captures


def run_eval83(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL83-CROSS-ASSET-SURFACE-SPILLOVER-RV-PREDICTIVENESS",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    captures = _select_captures(capture_dir_abs)

    floor = campaign_floor(captures)
    floor_ok = bool(floor["ok"])

    per_config: List[Dict[str, Any]] = []
    errors: List[str] = []
    for leader, target in _ordered_pairs(sorted(captures)):
        for sig in SURFACE_SIGNALS:
            for bar_s in GRID_BAR_SECONDS:
                for horizon in FORWARD_HORIZONS_BARS:
                    try:
                        res = evaluate_spillover(
                            captures[leader],
                            captures[target],
                            surface_signal=sig,
                            bar_seconds=bar_s,
                            horizon_bars=horizon,
                        )
                    except BaseException as exc:  # noqa: BLE001
                        errors.append(
                            f"{leader}->{target}::{sig}::{TARGET}::bar{bar_s}::"
                            f"h{horizon}: {exc!r}"
                        )
                        continue
                    per_config.append(res)

    p_values = {
        f"{r['leader']}->{r['target']}::{r['signal']}::bar{r['bar_seconds']}::"
        f"h{r['horizon_bars']}": _finite(r.get("permutation_p"), 1.0)
        for r in per_config
        if r.get("n_pairs", 0) > 0
    }
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}
    rejected = set(bh.get("rejected") or [])

    def _key(r: Dict[str, Any]) -> str:
        return (
            f"{r['leader']}->{r['target']}::{r['signal']}::"
            f"bar{r['bar_seconds']}::h{r['horizon_bars']}"
        )

    # Per-direction (ordered pair) summary.
    by_pair: Dict[str, List[Dict[str, Any]]] = {}
    for r in per_config:
        by_pair.setdefault(f"{r['leader']}->{r['target']}", []).append(r)

    pair_summary: List[Dict[str, Any]] = []
    for pair, rows in by_pair.items():
        valid = [r for r in rows if r.get("n_pairs", 0) > 0]
        best = max(valid, key=lambda r: _finite(r.get("spillover_ic"), -1e9)) if valid else None
        pass_configs = [ _key(r) for r in valid if r.get("pass") and _key(r) in rejected ]
        leader, target = pair.split("->", 1)
        pair_summary.append({
            "pair": pair,
            "leader": leader,
            "target": target,
            "n_configs": len(rows),
            "best_ic": _finite(best.get("spillover_ic"), 0.0) if best else 0.0,
            "best_partial_ic": _finite(best.get("partial_spillover_ic"), 0.0) if best else 0.0,
            "best_config": (
                f"{best['signal']}::bar{best['bar_seconds']}::h{best['horizon_bars']}"
                if best else "n/a"
            ),
            "n_pass": len(pass_configs),
            "pass_configs": pass_configs,
            "any_pass": bool(pass_configs),
        })

    # Per-target: does each target receive significant incoming spillover?
    targets = sorted({p["target"] for p in pair_summary})
    per_target: List[Dict[str, Any]] = []
    for tgt in targets:
        inc = [p for p in pair_summary if p["target"] == tgt]
        incoming = [p["leader"] for p in inc]
        any_in = any(p["any_pass"] for p in inc)
        per_target.append({
            "target": tgt,
            "incoming_leaders": incoming,
            "n_incoming_configs": sum(p["n_configs"] for p in inc),
            "any_incoming_pass": bool(any_in),
            "passing_leaders": [p["leader"] for p in inc if p["any_pass"]],
        })

    all_targets_pass = bool(per_target) and all(t["any_incoming_pass"] for t in per_target)
    any_pair_pass = any(p["any_pass"] for p in pair_summary)
    go = bool(floor_ok and all_targets_pass and len(rejected) >= 1)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = (
        "EVAL_83_CROSS_ASSET_SURFACE_SPILLOVER_RV_PREDICTIVENESS" if floor_ok
        else "EVAL_83_BLOCKED_FLOOR"
    )

    if floor_ok and not go and any_pair_pass:
        verdict_detail = (
            "one-directional cross-asset spillover detected (see per_direction) but "
            "not significant into EACH target underlying; symmetric GO bar not met"
        )
    else:
        verdict_detail = (
            "wrapper-free information-content test: Spearman rank IC between one "
            "crypto's causal options surface and the OTHER crypto's forward realized "
            "volatility on the real on-disk captures"
            if floor_ok else "capture below the composed EVAL-71 + cross-asset "
                             "common-bar floor; no verdict"
        )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": verdict_detail,
        "floor_ok": bool(floor_ok),
        "capture_dir": str(capture_dir_abs),
        "underlyings": sorted(captures),
        "floor": dict(FLOOR),
        "campaign_floor": floor,
        "protocol": build_protocol(capture_dir),
        "per_config": per_config,
        "per_direction": pair_summary,
        "per_target": per_target,
        "pooled": {
            "bh_fdr": bh,
            "all_targets_pass": all_targets_pass,
            "any_pair_pass": any_pair_pass,
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
            "The causal options implied-volatility surface of one crypto (EVAL-71 "
            "near-ATM IV level / put-call skew, expanding-z-scored) has a positive "
            "monotone (Spearman rank) relationship with the subsequent forward "
            "realized volatility of the OTHER crypto, reconstructed from the real "
            "Deribit option trade tape and real perp candles of both underlyings, "
            "beyond the target's own surface (partial-over-own-surface IC > 0). Tested "
            "on the already-acquired real on-disk captures at the composed EVAL-71 + "
            "cross-asset common-bar floor."
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
        f"# {PREREG_ID} — cross-asset options surface lead-lag spillover -> "
        f"subsequent forward realized volatility (wrapper-free Spearman rank IC)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Hypothesis: {r['hypothesis']}",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Extends: {p['extends']}",
        "",
        "## Pre-declared protocol",
        "",
        f"- Leader surface signals: {p['surface_signals']}",
        f"- Target: {p['target']} — {p['target_detail']}",
        f"- Bar grid (s): {p['bar_seconds_grid']}",
        f"- Forward horizons (bars): {p['forward_horizons_bars']}",
        f"- Signal: {p['signal']}",
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
        "## Pre-registered composed floor (EVAL-71 surface + cross-asset common-bar)",
        "",
        f"- {fl['note']}",
        f"- Min underlyings: {fl['min_underlyings']}",
        f"- Min common bars per ordered pair: {fl['min_common_bars_per_pair']}",
        f"- Min usable pairs per config: {fl['min_usable_pairs_per_config']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    fl = r["campaign_floor"]
    lines = [
        f"# {r['report_id']} — cross-asset options surface lead-lag spillover -> "
        f"subsequent forward realized volatility (wrapper-free rank IC) falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Verdict detail: {r['verdict_detail']}",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        "",
        "## Per-underlying surface floor (EVAL-71, reused verbatim)",
        "",
        "| underlying | n option trades | n near-ATM | n perp candles | span (s) | ok |",
        "|---|---|---|---|---|---|",
    ]
    for inst, u in fl["per_underlying"].items():
        lines.append(
            f"| {inst} | {u.get('n_option_trades')} | {u.get('n_near_atm_option_trades')} | "
            f"{u.get('n_perp_candles')} | {u.get('perp_span_seconds')} | {u.get('ok')} |"
        )
    lines += ["", "## Cross-asset common-bar floor (coarser grid)", "",
              "| pair | bar s | common bars | min | ok |",
              "|---|---|---|---|---|"]
    for pair, u in fl["per_pair"].items():
        lines.append(
            f"| {pair} | {u['bar_seconds']:.0f} | {u['n_common_bars']} | "
            f"{u['min_common_bars']} | {u['ok']} |"
        )
    lines += ["", "## Configs (best first by spillover IC)", "",
              "| leader->target | signal | bar s | horizon | n pairs | spillover IC | "
              "partial IC | own IC | perm p | bootstrap 95% CI | pass |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    rows = sorted(
        [c for c in r["per_config"] if c.get("n_pairs", 0) > 0],
        key=lambda c: _finite(c.get("spillover_ic"), -1e9),
        reverse=True,
    )
    for c in rows:
        ci = c.get("bootstrap_ci") or [0.0, 0.0, 0.0]
        lines.append(
            f"| {c['leader']}->{c['target']} | {c['signal']} | {c['bar_seconds']:.0f} | "
            f"{c['horizon_bars']} | {c['n_pairs']} | {c['spillover_ic']:.4f} | "
            f"{_finite(c.get('partial_spillover_ic')):.4f} | {_finite(c.get('own_ic')):.4f} | "
            f"{c['permutation_p']:.4f} | [{ci[0]:.4f}, {ci[1]:.4f}, {ci[2]:.4f}] | "
            f"{c['pass']} |"
        )
    lines += ["", "## Per-direction (ordered pair)", "",
              "| pair | n_configs | best IC | best partial IC | best config | n_pass | any_pass |",
              "|---|---|---|---|---|---|---|"]
    for s in r["per_direction"]:
        lines.append(
            f"| {s['pair']} | {s['n_configs']} | {s['best_ic']:.4f} | "
            f"{s['best_partial_ic']:.4f} | {s['best_config']} | {s['n_pass']} | "
            f"{s['any_pass']} |"
        )
    lines += ["", "## Per-target (does each target receive incoming spillover?)", "",
              "| target | incoming leaders | n incoming configs | any incoming pass | passing leaders |",
              "|---|---|---|---|---|"]
    for t in r["per_target"]:
        lines.append(
            f"| {t['target']} | {', '.join(t['incoming_leaders'])} | "
            f"{t['n_incoming_configs']} | {t['any_incoming_pass']} | "
            f"{', '.join(t['passing_leaders']) or '(none)'} |"
        )
    lines += ["", "## Pooled", "",
              f"- BH-FDR rejected: {r['pooled']['bh_fdr'].get('rejected')}",
              f"- All targets receive spillover: {r['pooled']['all_targets_pass']}",
              f"- Any direction passes: {r['pooled']['any_pair_pass']}",
              f"- Campaign state: {r['pooled']['campaign_state']}"]
    if r["errors"]:
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def _build_blocked_report(r: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "report_id": BLOCKED_ID,
        "generated_at": r.get("generated_at", _utc_now_iso()),
        "task": r.get("task", "EVAL83-CROSS-ASSET-SURFACE-SPILLOVER-RV-PREDICTIVENESS"),
        "verdict": "BLOCKED",
        "verdict_detail": (
            "capture below the composed EVAL-71 surface + cross-asset common-bar "
            "floor; no predictiveness verdict is emitted (never a NO-GO)"
        ),
        "floor_ok": False,
        "capture_dir": r.get("capture_dir"),
        "underlyings": r.get("underlyings", []),
        "floor": r.get("floor", dict(FLOOR)),
        "campaign_floor": r.get("campaign_floor", {}),
        "errors": r.get("errors", []),
    }


def _build_blocked_md(r: Dict[str, Any]) -> str:
    fl = r.get("campaign_floor") or {}
    lines = [
        f"# {BLOCKED_ID} — cross-asset options surface lead-lag spillover predictiveness: "
        f"BELOW FLOOR",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Verdict: **BLOCKED**",
        f"- Capture dir: `{r.get('capture_dir')}`",
        f"- Underlyings: {', '.join(r.get('underlyings', [])) or '(none)'}",
        "",
        "The capture is below the composed EVAL-71 surface + cross-asset common-bar "
        "floor; no predictiveness verdict is emitted (never a NO-GO).",
    ]
    per = fl.get("per_underlying") or {}
    if per:
        lines += ["", "## Per-underlying floor", "",
                  "| underlying | n option trades | ok |", "|---|---|---|"]
        for inst, u in per.items():
            lines.append(f"| {inst} | {u.get('n_option_trades')} | {u.get('ok')} |")
    per_pair = fl.get("per_pair") or {}
    if per_pair:
        lines += ["", "## Per-pair overlap floor", "",
                  "| pair | common bars | ok |", "|---|---|---|"]
        for pair, u in per_pair.items():
            lines.append(f"| {pair} | {u.get('n_common_bars')} | {u.get('ok')} |")
    if r.get("errors"):
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-83: wrapper-free cross-asset options surface lead-lag "
                    "spillover -> target forward realized volatility predictiveness "
                    "(Spearman rank IC) on the real on-disk captures"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument(
        "--task-label",
        default="EVAL83-CROSS-ASSET-SURFACE-SPILLOVER-RV-PREDICTIVENESS",
    )
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval83(
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
                "floor": dict(FLOOR),
                "campaign_floor": {},
                "errors": [repr(exc)],
            })
            e62._seal(BLOCKED_ID, blocked, _build_blocked_md)
        return 1

    print(json.dumps({
        "verdict": report.get("verdict"),
        "floor_ok": report.get("floor_ok"),
        "underlyings": report.get("underlyings"),
        "per_direction": report.get("per_direction"),
        "per_target": report.get("per_target"),
        "bh_fdr_rejected": report.get("pooled", {}).get("bh_fdr", {}).get("rejected"),
        "n_configs": len(report.get("per_config", [])),
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())