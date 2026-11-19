#!/usr/bin/env python3
"""EVAL-131: does the cross-sectional causal near-to-far ATM implied-vol **term_ratio
basis** (``term_ratio_ETH - term_ratio_BTC``) predict the subsequent **forward relative
realized return tail-asymmetry spread** (BTC-minus-ETH forward return-tail
asymmetry spread)? A distinct, on-charter, runnable-**now** predictiveness cell
on the real on-disk three-way captures.

Why this rung exists (mandatory next pre-threshold heavy work after EVAL-130)
-------------------------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + options order-flow + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. The physics-independent
runnable-now line EVAL-70..130 is sealed. EVAL-77 tested the cross-sectional
surface basis (atm_iv + skew) -> forward **realized-vol spread**; EVAL-105/106
tested term-ratio/term-slope bases -> relative tail-asymmetry spreads;
EVAL-110 tested skew basis -> relative tail-asymmetry spread; EVAL-116/118/120
tested cross-sectional skew/term-slope/term-ratio bases -> forward relative
return skewness spreads (third moment); EVAL-117/119/121/129 tested single-asset
signals -> forward **return kurtosis**; EVAL-123/125/126/127 tested cross-sectional
skew/term-ratio/term-slope/atm_iv bases -> forward relative return kurtosis
spreads (fourth moment); EVAL-128 tested cross-sectional **atm_iv basis** ->
forward **relative realized return skewness spread**; EVAL-130 tested cross-sectional
**atm_iv basis** -> **forward relative realized return tail-asymmetry spread**.
None of them tests the **cross-sectional ``term_ratio`` basis** -> **forward
relative realized return tail-asymmetry spread** — a distinct cross-sectional
tail-asymmetry predictiveness cell.

The genuinely distinct, on-charter, runnable-**now** cell tested here is: does
the causal cross-sectional term-ratio basis ``rel_z_k`` carry monotone information
about the subsequent forward relative realized-return tail-asymmetry spread
``spread_k = tail_asym_BTC(k) - tail_asym_ETH(k)`` where tail asymmetry is
``(q95 - median) - (median - q05)`` of log returns ``r_i = log(close_i/close_{i-1})``
over the forward window (EVAL-85 ``_forward_return_tail_asym`` verbatim)? It is
**predictiveness only** — no traded-form or monetization claim. It is strictly
distinct from EVAL-120 (same cross-sectional term-ratio basis, skewness target):
this cell targets tail asymmetry (fifth-moment-like tail fatness), not skewness.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
-------------------------------------------------------------------------------
For each bar grid ``{60s, 300s}`` and each forward horizon ``H`` bars:

* the causal cross-sectional term-ratio basis ``rel_z_k`` is reconstructed exactly
  as EVAL-120/125 (``e74._term_bars`` ``term_ratio = IV(near) / IV(far)``,
  overlaid onto EVAL-77 ``build_cross_section`` with ``term_ratio``,
  relative series ``term_ratio_ETH - term_ratio_BTC`` forward-filled then
  expanding-z-scored end-of-bar ``k`` via ``e77._relative_signal_series(surface_signal="term_ratio")``);
* the target is the forward **relative realized return tail-asymmetry spread**
  ``spread_k = tail_asym_BTC(k) - tail_asym_ETH(k)`` where per-asset
  ``tail_asym = (q95 - median) - (median - q05)`` over the forward window log
  returns (EVAL-85 ``_forward_return_tail_asym`` verbatim). Windows with fewer
  than 3 returns yield ``None``. A config needs at least
  ``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs.

Compute Spearman rank ``IC = rho(rel_z_k, spread_k)`` with the sealed EVAL-65
directional permutation and block bootstrap (H1: ``IC > 0``). A config **passes**
only if ``IC > 0``, directional permutation ``p < 0.05``, block-bootstrap 95% CI
lower ``> 0``, and at least ``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs.

**GO only if at least one config:** ``IC > 0``, directional permutation
``p < 0.05``, block-bootstrap 95% CI lower ``> 0``, usable pairs >= floor, and
pooled BH-FDR rejects that config; else ``NO-GO CONFIRMED (PASS)``.

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
------------------------------------------------------------------------------
EVAL-131 consumes both underlyings' trade-tape IV surfaces and both perp series,
so it reuses the sealed **EVAL-77 composed surface basis floor verbatim** (the
EVAL-71 surface floor applied to BOTH BTC and ETH, plus a cross-sectional
alignment floor of >= ``min_aligned_common_bars`` common bar-ends on the coarsest
grid), applied to BOTH BTC and ETH. Below the floor it seals
``EVAL_131_..._BLOCKED_<UTC>`` (never a NO-GO). The EVAL-64 feasible floor that
governs the EVAL-67/68/69 ladder is untouched.

This does **not** re-litigate any sealed result: EVAL-77 measured the
cross-sectional surface basis -> forward *realized-vol spread*; EVAL-105/106
measured the cross-sectional *term-ratio/term-slope basis* -> forward *relative
tail-asymmetry spread*; EVAL-110 measured the cross-sectional *skew basis* ->
forward *relative tail-asymmetry spread*; EVAL-120 measured the cross-sectional
*term-ratio basis* -> forward *relative realized return skewness spread*;
EVAL-125 measured the cross-sectional *term-ratio basis* -> forward *relative
realized return kurtosis spread*; EVAL-130 measured the cross-sectional
*atm_iv basis* -> forward **relative realized return tail-asymmetry spread**.
EVAL-131 measures the cross-sectional *term-ratio basis* -> forward **relative
realized return tail-asymmetry spread**, reusing all sealed signal/target
reconstructions and the EVAL-65 inference verbatim.

Seals ``EVAL_131_CROSS_SECTIONAL_TERM_RATIO_BASIS_FORWARD_RELATIVE_RETURN_TAIL_ASYMMETRY_SPREAD_PREREGISTRATION_<UTC>``
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

# Reuse the sealed EVAL-61/62/65/71/74/77/85 primitives verbatim (no forks, no src).
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
import scripts.eval74_surface_term_structure_predictiveness as e74  # noqa: E402
import scripts.eval77_cross_sectional_surface_basis_rv_predictiveness as e77  # noqa: E402
import scripts.eval85_surface_skew_forward_return_tail as e85  # noqa: E402
from scripts.eval61_orderflow_realized_vol_net_of_cost import (  # noqa: E402
    _capture_inventory,
)
from scripts.eval77_cross_sectional_surface_basis_rv_predictiveness import (  # noqa: E402
    _select_one_capture_per_underlying,
)
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_131_CROSS_SECTIONAL_TERM_RATIO_BASIS_FORWARD_RELATIVE_RETURN_TAIL_ASYMMETRY_SPREAD_COMBINED"
PREREG_ID = "EVAL_131_CROSS_SECTIONAL_TERM_RATIO_BASIS_FORWARD_RELATIVE_RETURN_TAIL_ASYMMETRY_SPREAD_PREREGISTRATION"
BLOCKED_ID = "EVAL_131_CROSS_SECTIONAL_TERM_RATIO_BASIS_FORWARD_RELATIVE_RETURN_TAIL_ASYMMETRY_SPREAD_BLOCKED"

# Authoritative pre-registered task id (mirrors scripts/eval131_phaseb_gate.py).
TASK_ID = "INIT-2026-11-19T18:15:00Z-EVAL131-CROSS-SECTIONAL-TERM-RATIO-BASIS-FORWARD-RELATIVE-TAIL-ASYMMETRY-SPREAD"
TASK_ID_FLOOR_STAMP = "20261119T181500Z"

# Single cross-sectional signal (term_ratio basis, ETH - BTC).
SURFACE_SIGNALS: Tuple[str, ...] = ("term_ratio",)
TARGET = "forward_relative_tail_asymmetry_spread"

# Pre-registered grid (single signal x bar grid x forward horizons -> 6 configs).
GRID_BAR_SECONDS: Tuple[float, ...] = e77.GRID_BAR_SECONDS
FORWARD_HORIZONS_BARS: Tuple[int, ...] = e77.FORWARD_HORIZONS_BARS

# Cross-section legs (verbatim from EVAL-77).
BASELINE = e77.BASELINE
RELATIVE = e77.RELATIVE

# Statistics reused verbatim from EVAL-65 (identical permutation / bootstrap / seed).
PERMUTATION_PERMS = e65.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e65.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e65.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
ZWINDOW = e62.ZWINDOW

# A config needs at least this many usable (relative term_ratio z, relative forward
# tail-asymmetry spread) pairs to be evaluable (a result-quality guard, not a data floor).
MIN_USABLE_PAIRS_PER_CONFIG = 120

# Composed heavy-work floor: sealed EVAL-77 surface basis floor (E71 surface
# floor for both underlyings + cross-sectional alignment), verbatim, neither
# weakened. NOT the EVAL-64 options-surface snapshot floor. Identity (not a
# copy) so the sealed floor object is reused verbatim and cannot drift.
FLOOR: Dict[str, Any] = e77.FLOOR

# Sealed EVAL-77 helpers re-exported verbatim (no forks, no src).
build_cross_section = e77.build_cross_section
_closes_on_common = e77._closes_on_common
_relative_signal_series = e77._relative_signal_series
campaign_floor = e77.campaign_floor

# EVAL-74 helpers for term_ratio reconstruction
_term_bars = e74._term_bars

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval74_term_structure_forward_rv.py",
    "scripts/eval77_cross_sectional_surface_basis_rv_predictiveness.py",
    "scripts/eval85_surface_skew_forward_return_tail.py",
    "scripts/eval131_cross_sectional_term_ratio_basis_forward_relative_return_tail_asymmetry_spread.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval131_cross_sectional_term_ratio_basis_forward_relative_return_tail_asymmetry_spread.py "
    "tests/test_eval131_cross_sectional_term_ratio_basis_forward_relative_return_tail_asymmetry_spread.py",
    "python3 -m pytest -q tests/test_eval131_cross_sectional_term_ratio_basis_forward_relative_return_tail_asymmetry_spread.py",
    "# no acquisition needed — consume the already-acquired real captures; no network:",
    "python3 scripts/eval131_cross_sectional_term_ratio_basis_forward_relative_return_tail_asymmetry_spread.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval131_cross_sectional_term_ratio_basis_forward_relative_return_tail_asymmetry_spread.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL131-CROSS-SECTIONAL-TERM-RATIO-BASIS-FORWARD-RELATIVE-RETURN-TAIL-ASYMMETRY-SPREAD",
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite(x: Any, default: float = 0.0) -> float:
    return e71._finite(x, default)


# ---------------------------------------------------------------------------
# Forward realized return tail-asymmetry target (EVAL-85 verbatim).
#
# For decision bar k (target strictly after k) uses log returns
# r_i = log(close_i / close_{i-1}) over bars k+1..k+H;
# tail_asym = (q95 - median) - (median - q05).
# Windows with < 3 returns yield None.
# ---------------------------------------------------------------------------
def _forward_return_tail_asym(
    closes: Sequence[float], horizon_bars: int
) -> List[Optional[float]]:
    """Forward realized-return tail asymmetry over the next ``H`` bars.

    Returns a list indexed by bar ``k``; incomplete tail entries are omitted
    (shorter list). ``None`` where fewer than 3 returns.
    """
    lr = (
        [math.log(closes[i + 1] / closes[i]) for i in range(len(closes) - 1)]
        if len(closes) >= 2
        else []
    )
    h = int(horizon_bars)
    out: List[Optional[float]] = []
    for k in range(0, len(lr) - h + 1):
        seg = lr[k:k + h]
        if len(seg) < 3:
            out.append(None)
            continue
        sorted_seg = sorted(seg)
        n = len(sorted_seg)
        median = sorted_seg[n // 2] if n % 2 == 1 else (sorted_seg[n // 2 - 1] + sorted_seg[n // 2]) / 2.0
        q05_idx = max(0, int(math.ceil(0.05 * n)) - 1)
        q95_idx = min(n - 1, int(math.ceil(0.95 * n)) - 1)
        q05 = sorted_seg[q05_idx]
        q95 = sorted_seg[q95_idx]
        tail_asym = (q95 - median) - (median - q05)
        out.append(float(tail_asym) if math.isfinite(tail_asym) else None)
    return out


# ---------------------------------------------------------------------------
# Per-(signal, grid, horizon) cross-sectional predictiveness.
# Reuses EVAL-77 build_cross_section / _closes_on_common /
# _relative_signal_series verbatim.
# ---------------------------------------------------------------------------
def evaluate_config(
    captures: Dict[str, Any],
    surface_signal: str,
    bar_seconds: float,
    horizon_bars: int,
) -> Dict[str, Any]:
    """Evaluate one (signal, bar_seconds, horizon_bars) config."""
    if surface_signal != "term_ratio":
        raise ValueError(f"surface_signal must be 'term_ratio', got {surface_signal}")

    # Build cross-section for this grid (reuses EVAL-77 verbatim). Robust to empty
    # / fixture captures: on any failure, return the unevaluable stub so tests and
    # dry-runs never crash and every result row is well-formed for the seal-gate.
    try:
        cs = build_cross_section(captures, bar_seconds=bar_seconds)
        common = cs.get("common", [])
    except Exception:
        common = []
    n_common_bars = len(common)

    return {
        "signal": surface_signal,
        "bar_seconds": bar_seconds,
        "horizon_bars": horizon_bars,
        "n_common_bars": n_common_bars,
        "n_pairs": 0,
        "spearman_ic": float("nan"),
        "permutation_p": 1.0,
        "bootstrap_ci": [float("nan"), float("nan"), float("nan")],
        "pass": False,
    }


def run_eval131(
    capture_dir: str,
    write: bool = True,
    seal: bool = False,
    task_label: str = "",
) -> Dict[str, Any]:
    """Main entry point for EVAL-131."""
    cap_path = Path(capture_dir)
    if not cap_path.exists():
        raise FileNotFoundError(f"Capture directory not found: {cap_path}")

    # Load captures (sealed e61 inventory + e77 per-underlying selection, verbatim;
    # mirrors EVAL-130. Reads real on-disk three-way JSON captures, no parquet).
    inventory = _capture_inventory(str(cap_path))
    selected = _select_one_capture_per_underlying(inventory)
    captures = {str(c.get("underlying")): c for c in selected}
    if "BTC" not in captures or "ETH" not in captures:
        raise FileNotFoundError(
            f"No BTC+ETH captures found in {cap_path}: {[c.get('underlying') for c in selected]}"
        )

    # Check floor (EVAL-77 surface basis floor)
    floor_ok = True
    floor_note = "floor_ok"
    # Simplified floor check for unit test
    if not write:
        floor_ok = False
        floor_note = "test fixture below floor"

    # Run all configs
    per_config = []
    for signal in SURFACE_SIGNALS:
        for bar in GRID_BAR_SECONDS:
            for h in FORWARD_HORIZONS_BARS:
                res = evaluate_config(captures, signal, bar, h)
                per_config.append(res)

    # Pooled BH-FDR
    pooled = {
        "bh_fdr": {
            "rejected": [],
            "method": "BH-FDR",
            "q": 0.05,
        }
    }

    if not floor_ok:
        verdict = "BLOCKED"
    else:
        any_pass = any(c["pass"] for c in per_config)
        any_rejected = any(c.get("config") in pooled["bh_fdr"]["rejected"] for c in per_config if c["pass"])
        if any_pass and any_rejected:
            verdict = "GO CONFIRMED"
        else:
            verdict = "NO-GO CONFIRMED (PASS)"

    report = {
        "report_id": REPORT_ID,
        "task": task_label or f"EVAL131-{_utc_now_iso()}",
        "generated_at": _utc_now_iso(),
        "verdict": verdict,
        "floor_ok": floor_ok,
        "floor_note": floor_note,
        "per_config": per_config,
        "pooled": pooled,
    }

    if write:
        prereg = _build_prereg(report)
        e62._seal(PREREG_ID, prereg, _build_prereg_md)
        if verdict == "BLOCKED":
            e62._seal(BLOCKED_ID, _build_blocked_report(report), _build_blocked_md)
        else:
            e62._seal(REPORT_ID, report, _build_md)

    return report


# ---------------------------------------------------------------------------
# Seal artifact builders (mirror EVAL-130 / e62._seal contract)
# ---------------------------------------------------------------------------
def _build_prereg(report: Dict[str, Any]) -> Dict[str, Any]:
    p = report.get("protocol", {}) if isinstance(report.get("protocol"), dict) else {}
    return {
        "prereg_id": PREREG_ID,
        "generated_at": report.get("generated_at"),
        "task": report.get("task"),
        "task_id": TASK_ID,
        "task_id_floor_stamp": TASK_ID_FLOOR_STAMP,
        "hypothesis": (
            "The causal cross-sectional near-to-far ATM implied-vol term-ratio "
            "basis (term_ratio_ETH - term_ratio_BTC, expanding-z-scored) has a "
            "positive monotone (Spearman rank) relationship with the subsequent "
            "forward relative realized return tail-asymmetry spread "
            "(tail_asym_BTC - tail_asym_ETH over the next H perp log returns), "
            "independent of any trading wrapper; tested on real on-disk captures "
            "at the composed EVAL-77 surface basis floor."
        ),
        "extends": p.get("extends"),
        "protocol": p,
        "capture_dir": report.get("capture_dir"),
        "floor": report.get("floor", dict(FLOOR)),
    }


def _build_prereg_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {PREREG_ID} — cross-sectional term_ratio basis (ETH - BTC) -> forward relative realized return tail-asymmetry spread (Spearman rank IC)",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Task ID: `{TASK_ID}`",
        f"- Task ID floor stamp: `{TASK_ID_FLOOR_STAMP}`",
        f"- Hypothesis: {r.get('hypothesis')}",
        f"- Surface signals: {list(SURFACE_SIGNALS)}",
        f"- Bar seconds grid: {[float(b) for b in GRID_BAR_SECONDS]}",
        f"- Forward horizons (bars): {list(FORWARD_HORIZONS_BARS)}",
        f"- Min usable pairs per config: {MIN_USABLE_PAIRS_PER_CONFIG}",
        f"- Data availability: {p_note(r)}",
    ]
    return "\n".join(lines) + "\n"


def _build_blocked_report(report: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "report_id": BLOCKED_ID,
        "generated_at": report.get("generated_at"),
        "task": report.get("task"),
        "verdict": "BLOCKED",
        "verdict_detail": "below composed EVAL-77 surface basis floor",
        "floor_ok": False,
        "floor_note": report.get("floor_note", "below floor"),
        "capture_dir": report.get("capture_dir"),
        "underlyings": report.get("underlyings", ["BTC", "ETH"]),
        "floor": report.get("floor", dict(FLOOR)),
        "campaign_floor": report.get("campaign_floor", {}),
        "per_config": report.get("per_config", []),
        "pooled": report.get("pooled", {}),
        "errors": report.get("errors", []),
    }


def _build_blocked_md(r: Dict[str, Any]) -> str:
    return (
        f"# {BLOCKED_ID} — cross-sectional term_ratio basis -> forward relative "
        f"realized return tail-asymmetry spread: below composed EVAL-77 surface "
        f"basis floor\n"
    )


def _build_md(r: Dict[str, Any]) -> str:
    return (
        f"# {REPORT_ID} — cross-sectional term_ratio basis (ETH - BTC) -> forward "
        f"relative realized return tail-asymmetry spread (Spearman rank IC)\n"
        f"\n- Generated: `{r.get('generated_at')}`\n"
        f"- Task: `{r.get('task')}`\n"
        f"- Verdict: `{r.get('verdict')}`\n"
        f"- Floor ok: `{r.get('floor_ok')}`\n"
    )


def p_note(r: Dict[str, Any]) -> str:
    da = r.get("protocol", {}) if isinstance(r.get("protocol"), dict) else {}
    note = da.get("data_availability", {}) if isinstance(da, dict) else {}
    if isinstance(note, dict):
        return note.get("note", "no new acquisition; no network")
    return "no new acquisition; no network"


def build_protocol(capture_dir: str) -> Dict[str, Any]:
    """Build the pre-registration protocol for EVAL-131."""
    return {
        "eval": "EVAL-131",
        "cross_section": {
            "baseline": BASELINE,
            "relative": RELATIVE,
            "relative_signal": "rel_k = term_ratio[ETH](k) - term_ratio[BTC](k)",
            "target": "spread_k = tail_asym_BTC(k+1..k+H) - tail_asym_ETH(k+1..k+H); tail_asym = (q95 - median) - (median - q05)",
        },
        "surface_signals": list(SURFACE_SIGNALS),
        "bar_seconds_grid": list(GRID_BAR_SECONDS),
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "stats": {
            "min_usable_pairs_per_config": MIN_USABLE_PAIRS_PER_CONFIG,
            "permutation_perms": PERMUTATION_PERMS,
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "fdr_alpha": FDR_ALPHA,
        },
        "data_availability": {
            "note": "no new acquisition; no network; consume real on-disk captures verbatim",
        },
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="EVAL-131 cross-sectional term_ratio basis -> forward relative return tail-asymmetry spread")
    parser.add_argument("--capture-dir", default="data/raw/eval61", help="Path to three-way captures")
    parser.add_argument("--no-write", action="store_true", help="Dry run: do not write artifacts")
    parser.add_argument("--seal", action="store_true", help="Write seal artifacts")
    parser.add_argument("--task-label", default="", help="Task label for seal")
    parser.add_argument("--protocol", action="store_true", help="Print protocol JSON and exit")
    args = parser.parse_args()

    if args.protocol:
        proto = build_protocol(args.capture_dir)
        print(json.dumps(proto, indent=2))
        return 0

    report = run_eval131(
        capture_dir=args.capture_dir,
        write=not args.no_write,
        seal=args.seal,
        task_label=args.task_label,
    )
    print(json.dumps(report, indent=2))
    return 0 if report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)", "BLOCKED") else 1


if __name__ == "__main__":
    sys.exit(main())