#!/usr/bin/env python3
"""EVAL-78: does the **interaction of options order-flow imbalance with the
implied-volatility surface** predict subsequent realized volatility? — a distinct,
runnable-**now** conditional-flow signal-family falsification on the real on-disk
three-way captures.

Why this rung exists (the on-charter question EVAL-65/71/77 leave open)
----------------------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + **options order-flow** + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. The runnable-now line so far:

* EVAL-71 sealed ``GO CONFIRMED`` — the single-underlying near-ATM IV **level** /
  put-call **skew** predicts forward RV;
* EVAL-73 sealed ``GO CONFIRMED (PASS)`` — that predictiveness is stable OOS;
* EVAL-74 sealed ``NO-GO CONFIRMED (PASS)`` — the *term-structure* slope predicts
  ETH forward RV but is null on BTC;
* EVAL-77 sealed ``GO CONFIRMED`` — the *cross-sectional* BTC-vs-ETH near-ATM IV
  basis predicts the subsequent BTC-minus-ETH RV spread;
* EVAL-72 / EVAL-75 / EVAL-76 sealed ``NO-GO CONFIRMED (PASS)`` — the surface
  level/skew and term-structure signals do not monetize net-of-cost through an ATM
  straddle or a skew-isolating risk reversal;
* **EVAL-65 sealed ``NO-GO CONFIRMED``** — the *unconditional* options order-flow
  toxicity / signed-aggressor imbalance has **no** monotone relationship with
  subsequent realized volatility;
* **EVAL-70 sealed ``NO-GO CONFIRMED``** — the *unconditional* underlying (perp)
  order flow has no RV / signed-return predictiveness.

Every rung above tests a signal **one factor at a time**: either the surface
(alone) or order-flow (alone). The one genuinely distinct, on-charter, runnable-
**now** *signal* none of them tests is the **interaction** of the two: does the
options order-flow imbalance carry *more* forward-RV information when the implied-
vol surface is rich (high near-ATM IV) or when put-call skew is extreme? That is a
*conditional-flow* hypothesis — the flow-to-vol information is **state-dependent on
the surface** — and it is the literal thesis of the repo name ("options order-flow
strategy"). It needs only the already-acquired real three-way captures (surface +
option trade tape with direction + perp candles), with **no new acquisition** and
**no network**.

    When options order-flow is buy-heavy AND the near-ATM implied-vol surface is
    rich (equivalently skew is extreme), does subsequent realized volatility rise?
    I.e. is the causal (options order-flow z) x (surface z) interaction
    informative about subsequent realized vol?

This does **not** re-litigate any sealed result: EVAL-65 measured the
*unconditional* flow signal and EVAL-71/77 measured the *unconditional* surface
signal; EVAL-78 measures their **product** (the conditional/ interaction term),
reusing both sealed signal reconstructions verbatim.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
--------------------------------------------------------------------------------
For each underlying, each interaction ``{oflow x atm_iv, oflow x skew}`` (with the
options order-flow leg ``imbalance`` from EVAL-61/62), each bar grid ``{60s,
300s}`` and each forward horizon ``H`` bars, on the common aligned bar grid:

    oflow_z_k = causal expanding-z-scored options order-flow imbalance (EVAL-61/62)
    surf_z_k  = causal expanding-z-scored near-ATM surface signal (EVAL-71)
    x_k       = oflow_z_k * surf_z_k                        (the interaction)
    rv_k      = sqrt(mean(log-return^2)) over the next H perp bars (EVAL-71 def)

Compute the Spearman rank ``IC = rho(x_k, rv_k)``. **GO only if, on BOTH BTC and
ETH, at least one config** has ``IC > 0`` (rich surface amplifies buy-heavy flow
into higher subsequent realized vol), directional permutation ``p < 0.05``,
block-bootstrap 95% CI lower ``> 0``, at least ``MIN_USABLE_PAIRS_PER_CONFIG``
usable pairs, and pooled BH-FDR rejects that config; else
``NO-GO CONFIRMED (PASS)``.

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
-------------------------------------------------------------------------------
EVAL-78 consumes BOTH the surface (EVAL-71) and the options order-flow leg
(EVAL-61/62), so it composes two honestly pre-registered floors and requires both,
for **each** underlying:

* the EVAL-71 surface floor (option trades / near-ATM trades / perp candles /
  span), reused verbatim; and
* an options order-flow adequacy floor: at least
  ``MIN_OFLOW_STATES_PER_UNDERLYING`` priceable per-bar order-flow states (real
  surface snapshots carrying a front-expiry straddle and a causal order-flow z).

Neither is weakened. Below the composed floor it seals
``EVAL_78_..._BLOCKED_<UTC>`` (never a NO-GO). The EVAL-64 feasible floor that
governs the EVAL-67/68/69 ladder is untouched.

Seals ``EVAL_78_OFLOW_X_SURFACE_RV_INTERACTION_PREREGISTRATION_<UTC>`` then
``..._COMBINED_<UTC>`` (or ``..._BLOCKED_<UTC>``).
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
# constants, EVAL-65 statistics, and the EVAL-71 surface reconstruction verbatim
# (no forks, no src edits).
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_78_OFLOW_X_SURFACE_RV_INTERACTION_COMBINED"
PREREG_ID = "EVAL_78_OFLOW_X_SURFACE_RV_INTERACTION_PREREGISTRATION"
BLOCKED_ID = "EVAL_78_OFLOW_X_SURFACE_RV_INTERACTION_BLOCKED"

# Pre-registered grid: surface legs x order-flow legs x bar grid x forward horizons.
SURFACE_SIGNALS: Tuple[str, ...] = ("atm_iv", "skew")
OFLOW_SIGNALS: Tuple[str, ...] = ("imbalance",)
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
FORWARD_HORIZONS_BARS: Tuple[int, ...] = (6, 24, 72)

# Statistics reused verbatim from EVAL-62/65 (identical permutation / bootstrap /
# seed) so the EVAL-78 inference is byte-for-byte the sealed line's.
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
# order-flow state floor; neither weakened).
FLOOR: Dict[str, Any] = {
    "min_underlyings": 2,
    "min_oflow_states_per_underlying": 200,
    "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
    "note": (
        "EVAL-78 consumes both the surface (EVAL-71) and the options order-flow leg "
        "(EVAL-61/62). It composes the sealed EVAL-71 surface floor (applied to EACH "
        "underlying, reused verbatim, neither weakened) with an options order-flow "
        "adequacy floor (>= min_oflow_states_per_underlying priceable per-bar "
        "order-flow states per underlying). This is NOT the EVAL-64 options-surface "
        "snapshot floor, which governs the EVAL-67/68/69 ladder and is untouched here."
    ),
}

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval78_oflow_x_surface_rv_predictiveness.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval78_oflow_x_surface_rv_predictiveness.py "
    "tests/test_eval78_oflow_x_surface_rv_predictiveness.py",
    "python3 -m pytest -q tests/test_eval78_oflow_x_surface_rv_predictiveness.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval78_oflow_x_surface_rv_predictiveness.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval78_oflow_x_surface_rv_predictiveness.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL78-OFLOW-X-SURFACE-RV-INTERACTION",
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
# Aligned (order-flow state, surface state) per-bar grid
# ---------------------------------------------------------------------------
def build_aligned(
    capture: Dict[str, Any],
    *,
    oflow_signal: str,
    bar_seconds: float,
) -> Dict[str, Any]:
    """Align each underlying's causal order-flow states (EVAL-62) with its causal
    surface bars (EVAL-71) on their common bar-open grid.

    Returns ``{"rows": [(bar_open_ms, spot, oflow_z, surface_bar), ...],
    "n_oflow_states": int, "n_surface_bars": int}`` sorted ascending by bar-open.
    ``surface_bar`` is the EVAL-71 bar dict (``atm_iv`` / ``skew`` / ``close``).
    """
    states = e62.build_states(capture, tox_signal=oflow_signal, bar_seconds=bar_seconds)
    sbars = e71.build_surface_bars(capture, bar_seconds=bar_seconds)
    sbmap = {int(b["bar_open_ms"]): b for b in sbars}

    rows: List[Tuple[int, float, float, Dict[str, Any]]] = []
    for s in states:
        bo = int(s.get("bar_ms") or 0)
        surf = sbmap.get(bo)
        if surf is None:
            continue
        spot = _finite(s.get("spot"), 0.0)
        if spot <= 0.0:
            continue
        rows.append((bo, float(spot), float(s.get("signal_z", 0.0)), surf))
    rows.sort(key=lambda r: r[0])
    return {
        "rows": rows,
        "n_oflow_states": len(states),
        "n_surface_bars": len(sbars),
    }


def _forward_fill(raw: Sequence[Optional[float]]) -> List[float]:
    return e71._forward_fill(raw)


def _rv_series(closes: Sequence[float], horizon_bars: int) -> List[float]:
    """Forward realized vol over the next H bars (identical definition to EVAL-71
    ``_forward_rv``): ``sqrt(mean(log-return^2))``."""
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


def evaluate_config(
    capture: Dict[str, Any],
    *,
    surface_signal: str,
    oflow_signal: str,
    bar_seconds: float,
    horizon_bars: int,
) -> Dict[str, Any]:
    """Conditional-flow predictiveness for one (interaction, grid, horizon) config."""
    inst = capture.get("underlying", "UNKNOWN")
    aligned = build_aligned(
        capture, oflow_signal=oflow_signal, bar_seconds=bar_seconds
    )
    rows = aligned["rows"]
    if len(rows) < int(horizon_bars) + 5:
        return {
            "underlying": inst,
            "interaction": f"oflow[{oflow_signal}]_x_{surface_signal}",
            "bar_seconds": float(bar_seconds),
            "horizon_bars": int(horizon_bars),
            "error": "insufficient aligned states",
            "n_pairs": 0,
            "pass": False,
        }

    closes = [float(r[1]) for r in rows]
    oflow_z = [float(r[2]) for r in rows]
    surf_raw = _forward_fill([r[3].get(surface_signal) for r in rows])
    surf_z = e61.expanding_zscore(surf_raw, ZWINDOW)

    rv = _rv_series(closes, horizon_bars)
    n = min(len(rv), len(surf_z))
    xs: List[float] = []
    ys: List[float] = []
    for k in range(n):
        xs.append(float(surf_z[k]) * float(oflow_z[k]))
        ys.append(float(rv[k]))

    if len(xs) < int(MIN_USABLE_PAIRS_PER_CONFIG):
        return {
            "underlying": inst,
            "interaction": f"oflow[{oflow_signal}]_x_{surface_signal}",
            "bar_seconds": float(bar_seconds),
            "horizon_bars": int(horizon_bars),
            "error": "insufficient aligned pairs",
            "n_pairs": len(xs),
            "pass": False,
        }

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
    return {
        "underlying": inst,
        "interaction": f"oflow[{oflow_signal}]_x_{surface_signal}",
        "bar_seconds": float(bar_seconds),
        "horizon_bars": int(horizon_bars),
        "n_aligned_states": len(rows),
        "n_pairs": len(xs),
        "spearman_ic": ic,
        "permutation_p": perm_p,
        "bootstrap_ci": [med, ci_lo, ci_hi],
        "nonzero_signal_pairs": int(sum(1 for v in xs if abs(v) > 1e-9)),
        "pass": passed,
    }


# ---------------------------------------------------------------------------
# Composed heavy-work floor (EVAL-71 surface floor AND order-flow state floor)
# ---------------------------------------------------------------------------
def _underlying_floor(
    capture: Dict[str, Any], *, oflow_signal: str
) -> Dict[str, Any]:
    """Composed per-underlying floor: EVAL-71 surface floor AND order-flow states."""
    inst = capture.get("underlying", "?")
    surface = e71._underlying_surface_floor(capture)

    n_oflow_states = 0
    for bar_s in GRID_BAR_SECONDS:
        aligned = build_aligned(
            capture, oflow_signal=oflow_signal, bar_seconds=bar_s
        )
        n_oflow_states = max(n_oflow_states, int(aligned["n_oflow_states"]))
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
    captures: Dict[str, Dict[str, Any]], *, oflow_signal: str
) -> Dict[str, Any]:
    insts = sorted(captures)
    per_underlying = {
        i: _underlying_floor(captures[i], oflow_signal=oflow_signal) for i in insts
    }
    ok = bool(
        len(insts) >= int(FLOOR["min_underlyings"])
        and per_underlying
        and all(v["ok"] for v in per_underlying.values())
    )
    return {
        "underlyings": insts,
        "per_underlying": per_underlying,
        "checks": {"all_underlyings_ok": ok},
        "ok": ok,
    }


# ---------------------------------------------------------------------------
# Protocol + orchestration
# ---------------------------------------------------------------------------
def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-78",
        "title": "Options order-flow imbalance x implied-volatility surface interaction "
                 "-> subsequent realized volatility (wrapper-free rank information "
                 "coefficient) falsification on the real on-disk three-way captures",
        "extends": "EVAL-65 (unconditional options order-flow -> RV) and EVAL-71/77 "
                   "(unconditional surface -> RV): identical Spearman rank-IC statistic "
                   "and both signal reconstructions reused verbatim, but a different, "
                   "on-charter signal family — the *interaction* (product) of the "
                   "options order-flow imbalance and the near-ATM surface state; no new "
                   "acquisition",
        "supersedes": "nothing — this is the conditional-flow complement to EVAL-65 "
                      "(unconditional flow) and EVAL-71/77 (unconditional surface); none "
                      "of them measured the flow x surface interaction",
        "capture_dir": str(capture_dir),
        "surface_signals": list(SURFACE_SIGNALS),
        "oflow_signals": list(OFLOW_SIGNALS),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": "causal options order-flow imbalance z (EVAL-61/62 build_states, "
                  "expanding-z-scored) times causal near-ATM surface z (EVAL-71 "
                  "build_surface_bars atm_iv / skew, forward-filled then "
                  "expanding-z-scored end-of-bar k): x_k = oflow_z_k * surf_z_k",
        "target": "rv = sqrt(mean(log-return^2)) over the next H perp bars (EVAL-71 "
                  "definition) on the common aligned bar grid",
        "statistic": "Spearman rank correlation IC = rho(x_k, rv_k) over the common "
                     "aligned bar-ends (H1: IC > 0, rich surface amplifies buy-heavy "
                     "flow into higher subsequent realized vol)",
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
            "GO only if, on BOTH BTC and ETH, at least one config (interaction x bar "
            "grid x horizon) has Spearman IC > 0, directional permutation p < 0.05, "
            "block-bootstrap 95% CI lower > 0, at least min_usable_pairs_per_config "
            "usable pairs, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED "
            "(PASS)."
        ),
        "data_availability": {
            "note": "uses the already-acquired real on-disk three-way captures (surface "
                    "snapshots + option trade tape with direction + perp candles); no "
                    "new acquisition, no network; composes the EVAL-71 floor for each "
                    "underlying with an options order-flow state floor",
            "capture_dir": str(capture_dir),
        },
        "floor": dict(FLOOR),
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def run_eval78(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL78-OFLOW-X-SURFACE-RV-INTERACTION",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    selected = _select_one_capture_per_underlying(
        e61._capture_inventory(str(capture_dir_abs))
    )
    captures = {str(c.get("underlying")): c for c in selected}

    per_underlying_floor: Dict[str, Dict[str, Any]] = {}
    for inst, cap in captures.items():
        per_underlying_floor[inst] = _underlying_floor(
            cap, oflow_signal=OFLOW_SIGNALS[0]
        )
    floor = {
        "underlyings": sorted(captures),
        "per_underlying": per_underlying_floor,
        "checks": {
            "all_underlyings_ok": bool(
                len(captures) >= int(FLOOR["min_underlyings"])
                and per_underlying_floor
                and all(v["ok"] for v in per_underlying_floor.values())
            )
        },
        "ok": bool(
            len(captures) >= int(FLOOR["min_underlyings"])
            and per_underlying_floor
            and all(v["ok"] for v in per_underlying_floor.values())
        ),
    }
    floor_ok = bool(floor["ok"])

    per_config: List[Dict[str, Any]] = []
    errors: List[str] = []
    for inst, cap in captures.items():
        for surf in SURFACE_SIGNALS:
            for oflow in OFLOW_SIGNALS:
                for bar_s in GRID_BAR_SECONDS:
                    for horizon in FORWARD_HORIZONS_BARS:
                        try:
                            res = evaluate_config(
                                cap,
                                surface_signal=surf,
                                oflow_signal=oflow,
                                bar_seconds=bar_s,
                                horizon_bars=horizon,
                            )
                        except BaseException as exc:  # noqa: BLE001
                            errors.append(
                                f"{inst}::oflow[{oflow}]_x_{surf}::bar{bar_s}::"
                                f"h{horizon}: {exc!r}"
                            )
                            continue
                        per_config.append(res)

    p_values = {
        f"{r['underlying']}::{r['interaction']}::bar{r['bar_seconds']}::"
        f"h{r['horizon_bars']}": _finite(r.get("permutation_p"), 1.0)
        for r in per_config
        if r.get("n_pairs", 0) > 0
    }
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}
    rejected = set(bh.get("rejected") or [])

    by_inst: Dict[str, List[Dict[str, Any]]] = {}
    for r in per_config:
        by_inst.setdefault(r["underlying"], []).append(r)

    inst_summary: List[Dict[str, Any]] = []
    for inst, rows in by_inst.items():
        valid = [r for r in rows if r.get("n_pairs", 0) > 0]
        best = None
        if valid:
            best = max(valid, key=lambda r: _finite(r.get("spearman_ic"), -1e9))
        pass_configs = []
        for r in valid:
            key = (
                f"{r['underlying']}::{r['interaction']}::bar{r['bar_seconds']}::"
                f"h{r['horizon_bars']}"
            )
            if r.get("pass") and key in rejected:
                pass_configs.append(key)
        inst_summary.append({
            "underlying": inst,
            "n_configs": len(rows),
            "best_ic": _finite(best.get("spearman_ic"), 0.0) if best else 0.0,
            "best_config": (
                f"{best['interaction']}::bar{best['bar_seconds']}::"
                f"h{best['horizon_bars']}" if best else "n/a"
            ),
            "n_pass": len(pass_configs),
            "pass_configs": pass_configs,
            "any_pass": bool(pass_configs),
        })

    all_pass = bool(inst_summary) and all(s["any_pass"] for s in inst_summary)
    go = bool(floor_ok and all_pass and len(rejected) >= 1)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = (
        "EVAL_78_OFLOW_X_SURFACE_RV_INTERACTION" if floor_ok
        else "EVAL_78_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free information-content test: Spearman rank IC between the "
            "causal options order-flow imbalance x implied-vol surface interaction and "
            "forward realized volatility on the real on-disk captures"
            if floor_ok else "capture below the composed EVAL-71 + order-flow floor; "
                              "no verdict"
        ),
        "floor_ok": bool(floor_ok),
        "capture_dir": str(capture_dir_abs),
        "underlyings": sorted(captures),
        "floor": dict(FLOOR),
        "campaign_floor": floor,
        "protocol": build_protocol(capture_dir),
        "per_config": per_config,
        "per_underlying": inst_summary,
        "summary": {
            "n_configs": len(per_config),
            "n_pass": sum(s["n_pass"] for s in inst_summary),
            "per_underlying": inst_summary,
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
            "near-ATM implied-volatility surface (product of the EVAL-61/62 order-flow "
            "z and the EVAL-71 surface z, reconstructed from the real Deribit option "
            "trade tape and real surface snapshots) has a positive monotone (Spearman "
            "rank) relationship with subsequent realized volatility: rich surface "
            "amplifies buy-heavy flow into higher subsequent realized vol. Tested on the "
            "already-acquired real on-disk captures at the composed EVAL-71 + order-flow "
            "floor."
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
        f"# {PREREG_ID} — options order-flow x implied-vol surface interaction -> "
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
        f"- Surface signals: {p['surface_signals']}",
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
        "## Pre-registered composed floor (EVAL-71 surface + order-flow state)",
        "",
        f"- {fl['note']}",
        f"- Min underlyings: {fl['min_underlyings']}",
        f"- Min order-flow states per underlying: {fl['min_oflow_states_per_underlying']}",
        f"- Min usable pairs per config: {fl['min_usable_pairs_per_config']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    fl = r["campaign_floor"]
    lines = [
        f"# {r['report_id']} — options order-flow x implied-vol surface interaction -> "
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
    lines += ["", "## Configs (best first by Spearman IC)", ""]
    lines += ["| underlying | interaction | bar s | horizon | n pairs | Spearman IC | perm p | bootstrap 95% CI | pass |",
              "|---|---|---|---|---|---|---|---|---|"]
    rows = sorted(
        [c for c in r["per_config"] if c.get("n_pairs", 0) > 0],
        key=lambda c: _finite(c.get("spearman_ic"), -1e9),
        reverse=True,
    )
    for c in rows:
        ci = c.get("bootstrap_ci") or [0.0, 0.0, 0.0]
        lines.append(
            f"| {c['underlying']} | {c['interaction']} | {c['bar_seconds']:.0f} | "
            f"{c['horizon_bars']} | {c['n_pairs']} | {c['spearman_ic']:.4f} | "
            f"{c['permutation_p']:.4f} | "
            f"[{ci[0]:.4f}, {ci[1]:.4f}, {ci[2]:.4f}] | {c['pass']} |"
        )
    lines += ["", "## Pooled", "",
              f"- BH-FDR rejected: {r['pooled']['bh_fdr'].get('rejected')}",
              f"- Any config pass (all underlyings): {r['pooled']['any_config_pass']}",
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
        f"# {BLOCKED_ID} — options order-flow x implied-vol surface interaction -> "
        f"realized-vol predictiveness (below the composed EVAL-71 + order-flow floor)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        "- Verdict: **BLOCKED** (measured; not NO-GO)",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Underlyings: {', '.join(r['underlyings'])}",
        "",
        "The capture does not meet the composed EVAL-71 + order-flow floor, so no "
        "GO/NO-GO verdict is emitted. Do NOT weaken either floor, do NOT use synthetic "
        "data, and do NOT emit NO-GO on under-floor data.",
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
    lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-78: options order-flow imbalance x implied-vol surface "
                    "interaction -> realized-vol predictiveness (Spearman rank IC) on "
                    "the real on-disk captures"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument(
        "--task-label", default="EVAL78-OFLOW-X-SURFACE-RV-INTERACTION"
    )
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval78(
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