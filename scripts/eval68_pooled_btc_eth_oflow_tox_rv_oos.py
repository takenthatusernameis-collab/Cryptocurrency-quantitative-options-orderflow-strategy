#!/usr/bin/env python3
"""EVAL-68: pooled BTC+ETH out-of-sample replication of the suggestive EVAL-65
options order-flow toxicity -> forward realized-vol slice, on a fresh **disjoint**
forward window, pooled across both crypto underlyings to reach power adequacy.

Why this exists
---------------
EVAL-67 is BTC-only and was recorded (pre-run) as underpowered for the EVAL-65 BTC
effect (IC 0.088, n 596 => one-sided power ~0.70, conjunction ~0.53; ~790 pairs
needed for 80% power). EVAL-65's only full-GO slice was ETH `imbalance::bar60::h72`
(IC 0.1176, p 0.001); EVAL-66's ETH replication sealed BLOCKED and was never tested
on a disjoint window. Pooling BTC + ETH on one disjoint forward window is the
natural power-adequate follow-up and the repo-priority ("crypto OPTIONS surface +
OPTIONS order-flow") core-thesis test.

This is a thin extension of EVAL-67 (no `phaseNN_*` wrappers):
- reuses sealed EVAL-62 `build_states`, EVAL-64 feasible floor verbatim, EVAL-65
  stats, and the EVAL-67 pair-extraction / per-config machinery
- the only new statistic is the POOLED rank-IC: all (signal_z, rv_forward) pairs
  from BTC and ETH are concatenated per config and a single Spearman IC /
  directional permutation p / block-bootstrap 95% CI is computed on the pooled
  sample, requiring >= 790 pooled pairs (80% power)
- GO requires the pooled statistic to clear the bar, the EVAL-64 floor on BOTH
  underlyings, disjointness on BOTH, and pooled BH-FDR rejection
- under-floor or non-disjoint on a non-empty real capture => BLOCKED (never NO-GO);
  an empty capture directory is not a BLOCKED result (--seal refuses to write until
  real three_way_BTC_*.json and three_way_ETH_*.json captures exist)

Disjointness: both underlyings must be disjoint from the sealed EVAL-64/65 three-way
window 2026-11-09T06:48:16Z..2026-11-16T06:48:16Z. Because the free Deribit perp 1m
endpoint returns only 300000 s, the earliest floor-compliant forward end is
2026-11-19T18:08:16Z; use 2026-11-20T00:00:00Z or later with --days 3.7 for margin.
EVAL-68 is gated to run only AFTER EVAL-67 has sealed (see eval68_phaseb_gate.py),
so the two campaigns never compete for the single forward acquisition window.
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

# Reuse sealed EVAL-61/62/64/65 + the EVAL-67 pair/statistic machinery verbatim.
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval67_btc_oflow_tox_rv_oos as e67  # noqa: E402
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_COMBINED"
PREREG_ID = "EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION"
BLOCKED_ID = "EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_BLOCKED"
PREREG_GLOB = PREREG_ID + "_*"

DEFAULT_CAPTURE_DIR = "data/raw/eval68"
DEFAULT_TASK_LABEL = "EVAL68-POOLED-BTC-ETH-OFLOW-TOX-RV-OOS"

# Sealed EVAL-64/65 three-way window (must not overlap, both underlyings).
# Source: research_state/POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_ACQUISITION_20261116T064816Z.json
SEALED_WINDOW_START = "2026-11-09T06:48:16Z"
SEALED_WINDOW_END = "2026-11-16T06:48:16Z"
EARLIEST_DISJOINT_CAPTURE_END = "2026-11-20T00:00:00Z"

# Configs: only the suggestive EVAL-65 slice (identical to EVAL-67).
TOX_SIGNALS: Tuple[str, ...] = e67.TOX_SIGNALS
GRID_BAR_SECONDS: Tuple[float, ...] = e67.GRID_BAR_SECONDS
FORWARD_HORIZONS_BARS: Tuple[int, ...] = e67.FORWARD_HORIZONS_BARS

# Stats (identical to EVAL-65/EVAL-67).
PERMUTATION_PERMS = e65.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e65.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e65.BOOTSTRAP_BLOCK
FDR_ALPHA = e65.FDR_ALPHA
SEED = e65.SEED

# Feasible floor reused verbatim from sealed EVAL-64.
_underlying_floor_strict = e64._underlying_floor_strict

# Pooled panel requires both crypto underlyings.
UNDERLYINGS: Tuple[str, ...] = ("BTC", "ETH")
MIN_UNDERLYINGS = len(UNDERLYINGS)
# Power adequacy (pre-registered): ~790 pairs for 80% power at the EVAL-65 effect.
MIN_POOLED_PAIRS = 790

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval60_acquire_three_way.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval64_orderflow_realized_vol_markpath_feasible.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval67_btc_oflow_tox_rv_oos.py",
    "scripts/eval68_pooled_btc_eth_oflow_tox_rv_oos.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval68_pooled_btc_eth_oflow_tox_rv_oos.py "
    "tests/test_eval68_pooled_btc_eth_oflow_tox_rv_oos.py",
    "python3 -m pytest -q tests/test_eval68_pooled_btc_eth_oflow_tox_rv_oos.py",
    "# EVAL-68 runs ONLY AFTER EVAL-67 seals; acquisition is gated by "
    "scripts/eval68_phaseb_gate.py (single forward window, no competition).",
    "python3 scripts/eval68_phaseb_gate.py            # WAIT_EVAL67(10)/DUE(20)/SEALED(0)",
    "python3 scripts/eval68_phaseb_gate.py --execute  # at/after threshold & EVAL-67 sealed",
)


class NoRealCaptureError(RuntimeError):
    """Raised when sealing is attempted before real BTC+ETH captures exist."""


# ---------------------------------------------------------------------------
# Pair extraction (pooled-ready) — mirrors eval67.evaluate_predictiveness alignment
# ---------------------------------------------------------------------------
def extract_pairs(
    capture: Dict[str, Any],
    *,
    tox_signal: str,
    bar_seconds: float,
    horizon_bars: int,
) -> Tuple[List[float], List[float]]:
    """Return (xs, ys) = (signal_z_k, forward_rv_k) for one capture+config.

    Identical alignment to EVAL-67: causal end-of-bar signal_z vs. strictly-forward
    realized vol over the next ``horizon_bars`` perp bars.
    """
    states = e62.build_states(capture, tox_signal=tox_signal, bar_seconds=bar_seconds)
    pts = [
        (float(s["spot"]), float(s.get("signal_z", 0.0)))
        for s in states
        if float(s.get("spot", 0.0)) > 0.0
    ]
    if len(pts) < horizon_bars + 5:
        return [], []
    spot = [p[0] for p in pts]
    sigz = [p[1] for p in pts]
    lr = [math.log(spot[i + 1] / spot[i]) for i in range(len(spot) - 1)]
    xs: List[float] = []
    ys: List[float] = []
    for k in range(0, len(lr) - horizon_bars + 1):
        seg = lr[k:k + horizon_bars]
        rv = math.sqrt(sum(r * r for r in seg) / float(horizon_bars))
        xs.append(sigz[k])
        ys.append(rv)
    return xs, ys


def evaluate_pooled(
    captures: Sequence[Dict[str, Any]],
    *,
    tox_signal: str,
    bar_seconds: float,
    horizon_bars: int,
) -> Dict[str, Any]:
    """Pooled rank-IC across BTC+ETH for one config.

    All (signal_z, forward_rv) pairs from every capture are concatenated into a
    single pooled sample; a single Spearman IC, directional permutation p, and
    block-bootstrap 95% CI are computed on that pooled sample. Power adequacy is
    the pooled pair count >= MIN_POOLED_PAIRS.
    """
    underlyings = [str(c.get("underlying", "?")) for c in captures]
    per_underlying: Dict[str, int] = {}
    pooled_x: List[float] = []
    pooled_y: List[float] = []
    for cap in captures:
        xs, ys = extract_pairs(
            cap, tox_signal=tox_signal, bar_seconds=bar_seconds, horizon_bars=horizon_bars
        )
        per_underlying[str(cap.get("underlying", "?"))] = len(xs)
        pooled_x.extend(xs)
        pooled_y.extend(ys)

    n_pairs = len(pooled_x)
    power_ok = bool(n_pairs >= MIN_POOLED_PAIRS)
    base = {
        "signal": tox_signal,
        "bar_seconds": float(bar_seconds),
        "horizon_bars": int(horizon_bars),
        "underlyings": underlyings,
        "per_underlying_n_pairs": per_underlying,
        "n_pairs": n_pairs,
        "n_pairs_power_adequate": power_ok,
        "min_pooled_pairs": MIN_POOLED_PAIRS,
    }
    if n_pairs < 8:
        base.update({"error": "insufficient pooled pairs", "pass": False})
        return base

    ic, perm_p = e65._perm_p_ic(pooled_x, pooled_y, PERMUTATION_PERMS, SEED)
    med, ci_lo, ci_hi = e65._boot_ci_ic(
        pooled_x, pooled_y, BOOTSTRAP_RESAMPLES, BOOTSTRAP_BLOCK, SEED
    )
    passed = bool(ic > 0.0 and perm_p < 0.05 and ci_lo > 0.0 and power_ok)
    base.update({
        "spearman_ic": ic,
        "permutation_p": perm_p,
        "bootstrap_ci": [med, ci_lo, ci_hi],
        "nonzero_signal_pairs": int(sum(1 for v in pooled_x if abs(v) > 1e-9)),
        "pass": passed,
    })
    return base


# ---------------------------------------------------------------------------
# Protocol
# ---------------------------------------------------------------------------
def build_protocol(capture_dir: str) -> Dict[str, Any]:
    base = e65.build_protocol(capture_dir)
    floor = dict(base["floor"])
    floor["min_underlyings"] = MIN_UNDERLYINGS
    return {
        "eval": "EVAL-68",
        "title": "Pooled BTC+ETH disjoint-window OOS replication of the suggestive "
                 "EVAL-65 options order-flow toxicity -> forward realized-vol slice "
                 "(tox/imbalance, bar60, horizon 72), pooled-sample Spearman rank IC "
                 "for power adequacy",
        "extends": "EVAL-65/EVAL-67 (identical signal/statistic/floor reused; BTC and "
                   "ETH pooled into one rank-IC sample on a fresh disjoint real window)",
        "supersedes": "nothing — power-adequate pooled replication of the suggestive "
                      "EVAL-65 slice; non-replication, underpowered, or BLOCKED is a "
                      "valid sealed result",
        "capture_dir": str(capture_dir),
        "underlyings_required": list(UNDERLYINGS),
        "disjoint_from": "data/raw/eval63/three_way_{BTC,ETH}_20261116T064816Z.json "
                         "(window 2026-11-09T06:48:16Z..2026-11-16T06:48:16Z)",
        "disjointness_rule": (
            "A capture is usable only if [window_start, window_end] does not overlap "
            "[2026-11-09T06:48:16Z, 2026-11-16T06:48:16Z]. Because the free Deribit "
            "perp 1m endpoint returns at most 5001 candles (300000 s), each capture "
            "must also span >=300000 s. The earliest floor-compliant end is "
            "2026-11-19T18:08:16Z (sealed end + 300000 s); for margin use "
            "2026-11-20T00:00:00Z or later. A naive trailing --days 7 capture before "
            "the sealed window has cleared will overlap and must seal BLOCKED."
        ),
        "capture_window_rule": (
            "Only after EVAL-67 has sealed: --underlying BTC --underlying ETH "
            "--days 3.7 --end <now-ISO> --out-dir data/raw/eval68 --seal. At end "
            "2026-11-20T00:00:00Z this gives start 2026-11-16T07:12:00Z (disjoint "
            "from 2026-11-16T06:48:16Z; span 319680 s). Do not weaken the EVAL-64 floor."
        ),
        "tox_signals": list(TOX_SIGNALS),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": base["signal"],
        "target": base["target"],
        "statistic": (
            "Pooled Spearman rank correlation IC = rho(signal_z_k, rv_forward_k) over "
            "the concatenation of BTC and ETH pairs for each config"
        ),
        "stats": base["stats"],
        "go_bar": (
            "GO only if, pooled across BTC+ETH and at least one of the pre-registered "
            "configs (tox::bar60::h72, imbalance::bar60::h72), the pooled Spearman "
            "IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > "
            "0, pooled pairs >= 790 (80% power), pooled BH-FDR rejects that config, the "
            "EVAL-64 floor is met on BOTH underlyings, and both capture windows are "
            "disjoint from the sealed window; else NO-GO CONFIRMED (PASS) when "
            "floor+disjoint+power but not predictive, INCONCLUSIVE (UNDERPOWERED) when "
            "floor+disjoint but pooled pairs < 790, or BLOCKED when floor/disjoint fails."
        ),
        "data_availability": {
            "note": "fresh real BTC+ETH three-way capture, disjoint from the sealed "
                    "eval63 window; public read-only, polite rate limiting, single "
                    "acquisition process; no synthetic data",
            "sealed_window": [SEALED_WINDOW_START, SEALED_WINDOW_END],
            "earliest_disjoint_capture_end": EARLIEST_DISJOINT_CAPTURE_END,
            "deribit_perp_1m_retention_seconds_approx": 300000,
        },
        "floor": floor,
        "min_underlyings": MIN_UNDERLYINGS,
        "min_pooled_pairs": MIN_POOLED_PAIRS,
    }


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def _capture_inventory(capture_dir: str) -> List[Dict[str, Any]]:
    return e61._capture_inventory(capture_dir)


def run_eval68(
    *,
    capture_dir: str = DEFAULT_CAPTURE_DIR,
    write: bool = True,
    task_label: str = DEFAULT_TASK_LABEL,
) -> Dict[str, Any]:
    generated_at = e65._utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    captures = _capture_inventory(str(capture_dir_abs))
    # Pooled panel: keep only the two crypto underlyings.
    captures = [c for c in captures if str(c.get("underlying", "")).upper() in UNDERLYINGS]

    if write and not captures:
        raise NoRealCaptureError(
            f"no real BTC/ETH capture found in {capture_dir_abs}; run "
            "scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH "
            f"--days 3.7 --end <at/after {EARLIEST_DISJOINT_CAPTURE_END}> "
            f"--out-dir {capture_dir_abs} and verify three_way_BTC_*.json and "
            "three_way_ETH_*.json (disjoint from the sealed window) before sealing"
        )

    per_underlying_floor: Dict[str, Dict[str, Any]] = {}
    disjointness: Dict[str, Dict[str, Any]] = {}
    for c in captures:
        inst = str(c.get("underlying", "?"))
        per_underlying_floor[inst] = _underlying_floor_strict(c)
        # Reuse EVAL-67 disjointness math (sealed window is shared BTC+ETH).
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
    # Only evaluate configs when both underlyings are present and floor+disjoint ok;
    # otherwise there is nothing meaningful to pool.
    if captures and not missing:
        for sig in TOX_SIGNALS:
            for bar_s in GRID_BAR_SECONDS:
                for horizon in FORWARD_HORIZONS_BARS:
                    try:
                        res = evaluate_pooled(
                            captures, tox_signal=sig, bar_seconds=bar_s, horizon_bars=horizon
                        )
                    except BaseException as exc:  # noqa: BLE001
                        errors.append(
                            f"{sig}::bar{bar_s}::h{horizon}: {exc!r}"
                        )
                        continue
                    per_config.append(res)

    p_values = {
        f"{r['signal']}::bar{r['bar_seconds']}::h{r['horizon_bars']}":
            e65._finite(r.get("permutation_p"), 1.0)
        for r in per_config
        if r.get("n_pairs", 0) > 0
    }
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}
    rejected = set(bh.get("rejected") or [])

    pass_configs: List[str] = []
    for r in per_config:
        key = f"{r['signal']}::bar{r['bar_seconds']}::h{r['horizon_bars']}"
        if r.get("pass") and key in rejected:
            pass_configs.append(key)

    max_pooled_pairs = max((r.get("n_pairs", 0) for r in per_config), default=0)
    power_adequate = bool(max_pooled_pairs >= MIN_POOLED_PAIRS)
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
        "EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS"
        if floor_and_disjoint_ok
        else "EVAL_68_BLOCKED_FLOOR_OR_DISJOINTNESS"
    )

    protocol = build_protocol(capture_dir)
    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict,
        "verdict_detail": (
            "pooled OOS replication (disjoint real BTC+ETH window) of the suggestive "
            "EVAL-65 slice tox/imbalance::bar60::h72; pooled-sample Spearman rank IC "
            "with EVAL-62 signal + EVAL-64 feasible floor reused"
            if floor_and_disjoint_ok
            else "capture below the pre-registered feasible floor and/or missing an "
                 "underlying and/or overlapping the sealed window; no GO/NO-GO verdict"
        ),
        "floor_ok": bool(floor_ok),
        "disjointness_ok": bool(disjoint_ok),
        "floor_and_disjoint_ok": floor_and_disjoint_ok,
        "missing_underlyings": missing,
        "capture_dir": str(capture_dir_abs),
        "underlyings": sorted(present),
        "floor": protocol["floor"],
        "disjointness_rule": protocol["disjointness_rule"],
        "per_underlying_floor": per_underlying_floor,
        "disjointness": disjointness,
        "protocol": protocol,
        "per_config": per_config,
        "pooled": {
            "bh_fdr": bh,
            "pass_configs": pass_configs,
            "max_pooled_pairs": max_pooled_pairs,
            "power_adequate": power_adequate,
            "min_pooled_pairs": MIN_POOLED_PAIRS,
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
            "Pooled across BTC and ETH, the suggestive EVAL-65 slice "
            "(tox/imbalance, bar60, horizon 72) replicates out-of-sample on a fresh "
            "disjoint real forward window: pooled Spearman IC > 0, directional "
            "permutation p < 0.05, block-bootstrap 95% CI lower > 0, >=790 pooled "
            "pairs (80% power), and BH-FDR rejects, at the sealed EVAL-64 floor on "
            "both underlyings."
        ),
        "extends": p["extends"],
        "disjointness_rule": p["disjointness_rule"],
        "data_availability": p["data_availability"],
        "protocol": p,
        "capture_dir": report["capture_dir"],
    }


def _build_prereg_md(r: Dict[str, Any]) -> str:
    p = r["protocol"]
    fl = p["floor"]
    lines = [
        f"# {PREREG_ID} — pooled BTC+ETH OOS replication of suggestive EVAL-65 slice "
        f"(tox/imbalance::bar60::h72, pooled-sample Spearman rank IC)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Hypothesis: {r['hypothesis']}",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Extends: {p['extends']}",
        f"- Disjoint from: {p['disjoint_from']}",
        "",
        "## Pre-declared protocol",
        "",
        f"- Underlyings: {p['underlyings_required']}",
        f"- Tox signals: {p['tox_signals']}",
        f"- Bar grid (s): {p['bar_seconds_grid']}",
        f"- Forward horizons (bars): {p['forward_horizons_bars']}",
        f"- Signal: {p['signal']}",
        f"- Target: {p['target']}",
        f"- Statistic: {p['statistic']}",
        f"- Stats: perm {p['stats']['permutation_perms']} ({p['stats']['permutation']}) / "
        f"bootstrap {p['stats']['bootstrap_resamples']} block {p['stats']['bootstrap_block']} / "
        f"BH-FDR alpha {p['stats']['fdr_alpha']} / seed {p['stats']['seed']}",
        f"- Power adequacy: pooled pairs >= {p['min_pooled_pairs']}",
        "",
        "## Pre-declared disjointness + capture-window rule",
        "",
        p["disjointness_rule"],
        "",
        p["capture_window_rule"],
        "",
        "## Pre-declared GO bar",
        "",
        p["go_bar"],
        "",
        "## Pre-registered feasible floor (reused verbatim from sealed EVAL-64)",
        "",
        f"- min surface snapshots/underlying: {fl['min_surface_snapshots_per_underlying']}",
        f"- min surface 5m bars/underlying: {fl['min_surface_bars_5m_per_underlying']}",
        f"- min Deribit option trades/underlying: {fl['min_option_trades_per_underlying']}",
        f"- min perp 5m bars/underlying: {fl['min_perp_bars_5m_per_underlying']}",
        f"- min perp span seconds/underlying: {fl['min_perp_span_seconds_per_underlying']}",
        f"- min common 5m bars/underlying: {fl['min_common_bars_per_underlying']}",
        f"- min underlyings (BTC+ETH): {p['min_underlyings']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {r['report_id']} — pooled BTC+ETH OOS replication of suggestive EVAL-65 "
        f"slice (tox/imbalance::bar60::h72)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        f"- Disjointness OK: {r.get('disjointness_ok')}",
        f"- Missing underlyings: {r.get('missing_underlyings')}",
        f"- Max pooled pairs: {r['pooled']['max_pooled_pairs']} "
        f"(>= {r['pooled']['min_pooled_pairs']} required; power adequate: "
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
        "## Per-underlying floor",
        "",
        "| underlying | snaps | surf inst | 5m bars | deribit trades | perp bars | perp span s | common 5m | ok |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for inst, fl in r["per_underlying_floor"].items():
        lines.append(
            f"| {inst} | {fl['n_surface_snapshots']} | {fl['n_surface_instruments']} | "
            f"{fl['n_surface_bars_5m']} | {fl['n_option_trades']} | "
            f"{fl['n_perp_bars_5m']} | {fl['perp_span_seconds']:.0f} | "
            f"{fl['n_common_bars_5m']} | {fl['ok']} |"
        )
    lines += ["", "## Pooled per-config", "",
              "| signal | bar_s | horizon | underlyings | per-underlying n | pooled n | power ok | IC | perm_p | CI95 | pass |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in r.get("per_config", []):
        ci = c.get("bootstrap_ci") or [float("nan")] * 3
        lines.append(
            f"| {c.get('signal')} | {c.get('bar_seconds')} | {c.get('horizon_bars')} | "
            f"{','.join(c.get('underlyings', []))} | {c.get('per_underlying_n_pairs')} | "
            f"{c.get('n_pairs')} | {c.get('n_pairs_power_adequate')} | "
            f"{e65._finite(c.get('spearman_ic'), 0.0):.4f} | "
            f"{e65._finite(c.get('permutation_p'), 1.0):.4f} | "
            f"[{e65._finite(ci[1], 0.0):.4f}, {e65._finite(ci[2], 0.0):.4f}] | {c.get('pass')} |"
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
        f"# {BLOCKED_ID} — pooled BTC+ETH OOS replication of suggestive EVAL-65 "
        f"slice (below the pre-registered feasible floor and/or missing an underlying "
        f"and/or overlapping the sealed window)",
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
        "The capture does not meet the pre-registered feasible floor (reused from "
        "sealed EVAL-64), is missing a required underlying, and/or overlaps the sealed "
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
        "generated_at": e65._utc_now_iso(),
        "task": task_label,
        "protocol": protocol,
        "capture_dir": str(capture_dir),
    }
    return _build_prereg(report)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-68: pooled BTC+ETH disjoint-window OOS replication of the "
                    "suggestive EVAL-65 options order-flow toxicity -> realized-vol "
                    "slice (tox/imbalance, bar60, horizon 72)"
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
        report = run_eval68(
            capture_dir=args.capture_dir, write=write, task_label=args.task_label
        )
    except NoRealCaptureError as exc:
        print(json.dumps({
            "verdict": "NOT_SEALED",
            "reason": "no_real_capture",
            "error": str(exc),
        }, indent=2))
        return 2
    except BaseException as exc:  # noqa: BLE001
        traceback.print_exc()
        if write:
            blocked = _build_blocked_report({
                "generated_at": e65._utc_now_iso(),
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
        "max_pooled_pairs": report.get("pooled", {}).get("max_pooled_pairs"),
        "power_adequate": report.get("pooled", {}).get("power_adequate"),
        "bh_fdr_rejected": report.get("pooled", {}).get("bh_fdr", {}).get("rejected"),
        "n_configs": len(report.get("per_config", [])),
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())