#!/usr/bin/env python3
"""EVAL-69: pooled BTC+ETH out-of-sample **traded-form** monetization of the
suggestive EVAL-65 options order-flow toxicity -> realized-vol slice, measured
with the correct mark-path net-of-cost P&L on the SAME disjoint forward capture
that EVAL-68 acquires.

Why this exists
---------------
EVAL-65 proved (wrapper-free) that the toxicity signal is *at best weakly
predictive* (one suggestive ETH slice, `imbalance::bar60::h72`, IC 0.1176); EVAL-67
(BTC-only) and EVAL-68 (pooled BTC+ETH, power-adequate) test whether that
predictiveness replicates out-of-sample on a fresh disjoint forward window. The
repo priority is **"crypto OPTIONS surface + OPTIONS order-flow -> tradeable,
net-of-cost alpha"**, so the natural and *unskippable* capstone is: if the signal
predicts, can it be **monetized net-of-cost** out-of-sample with the signal-timed
delta-hedged ATM straddle (the EVAL-62/64 traded form)?

EVAL-62 and EVAL-64 sealed **NO-GO CONFIRMED (PASS)** for that traded form, but
only on the *sealed in-sample* eval63 window. EVAL-69 is the **disjoint forward
OOS** traded-form test — a different claim on a fresh real window, not a re-run of
sealed artifacts. It is a thin extension of EVAL-68 (no `phaseNN_*` wrappers):

- reuses sealed EVAL-62 `build_states` + `markpath_returns` (signal + spot +
  per-bar net-of-cost P&L, byte-for-byte identical to EVAL-62/64), EVAL-64 feasible
  floor verbatim, EVAL-67 disjointness math, and the EVAL-62/65 stats
  (permutation / block-bootstrap / BH-FDR / kill-switch)
- the only new statistic is the **POOLED traded-form**: all per-bar net-of-cost
  returns from BTC and ETH are concatenated per config and a single Sharpe /
  max-drawdown / directional permutation p / block-bootstrap 95% CI is computed on
  the pooled sample, requiring >= 790 pooled returns (power adequacy, mirroring
  EVAL-68's pooled-pair threshold)
- GO requires the pooled statistic to clear the bar, the EVAL-64 floor on BOTH
  underlyings, disjointness on BOTH, and pooled BH-FDR rejection
- under-floor or non-disjoint on a non-empty real capture => BLOCKED (never NO-GO);
  an empty capture directory is not a BLOCKED result (`--seal` refuses to write
  until real three_way_BTC_*.json and three_way_ETH_*.json captures exist)

Acquisition is intentionally **not** performed here: EVAL-69 reuses EVAL-68's
disjoint forward capture (`data/raw/eval68`) so the two campaigns never compete for
the single forward acquisition window. EVAL-69 is gated to run only AFTER EVAL-68
has sealed (see `eval69_phaseb_gate.py`).

Disjointness: both underlyings must be disjoint from the sealed EVAL-64/65 three-way
window 2026-11-09T06:48:16Z..2026-11-16T06:48:16Z (re-checked here via EVAL-67
math; EVAL-68 already enforces it at acquisition). The earliest floor-compliant
forward end is 2026-11-19T18:08:16Z; use 2026-11-20T00:00:00Z or later.
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

# Reuse sealed EVAL-61/62/64/65/67/68 machinery verbatim.
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval67_btc_oflow_tox_rv_oos as e67  # noqa: E402
import scripts.eval68_pooled_btc_eth_oflow_tox_rv_oos as e68  # noqa: E402
from src.analytics.integrated_options_orderflow_evaluation import (  # noqa: E402
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
REPORT_ID = "EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_COMBINED"
PREREG_ID = "EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_PREREGISTRATION"
BLOCKED_ID = "EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_BLOCKED"
PREREG_GLOB = PREREG_ID + "_*"

# Reuse EVAL-68's disjoint forward capture (no second acquisition; no competition).
DEFAULT_CAPTURE_DIR = "data/raw/eval68"
DEFAULT_TASK_LABEL = "EVAL69-POOLED-BTC-ETH-OFLOW-TOX-RV-TRADED-OOS"

# Sealed EVAL-64/65 three-way window (must not overlap, both underlyings).
SEALED_WINDOW_START = "2026-11-09T06:48:16Z"
SEALED_WINDOW_END = "2026-11-16T06:48:16Z"
EARLIEST_DISJOINT_CAPTURE_END = "2026-11-20T00:00:00Z"

# Configs: only the suggestive EVAL-65 slice (identical to EVAL-67/68).
TOX_SIGNALS: Tuple[str, ...] = e67.TOX_SIGNALS
GRID_BAR_SECONDS: Tuple[float, ...] = e67.GRID_BAR_SECONDS

# Stats (identical to EVAL-62/64/65/67/68).
PERMUTATION_PERMS = e62.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e62.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e62.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
KILL_SWITCH_MAX_DD = e62.KILL_SWITCH_MAX_DD

# Feasible floor reused verbatim from sealed EVAL-64.
_underlying_floor_strict = e64._underlying_floor_strict

# Pooled panel requires both crypto underlyings.
UNDERLYINGS: Tuple[str, ...] = ("BTC", "ETH")
MIN_UNDERLYINGS = len(UNDERLYINGS)
# Power adequacy (pre-registered): mirrors EVAL-68's pooled-pair threshold; at the
# EVAL-64 floor (~928 states/underlying at bar60) pooled returns ~1856 >> 790.
MIN_POOLED_RETURNS = 790

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/integrated_options_orderflow_evaluation.py",
    "src/analytics/real_walkforward_certification.py",
    "src/analytics/strategy_evaluation.py",
    "scripts/eval60_acquire_three_way.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval64_orderflow_realized_vol_markpath_feasible.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval67_btc_oflow_tox_rv_oos.py",
    "scripts/eval68_pooled_btc_eth_oflow_tox_rv_oos.py",
    "scripts/eval69_pooled_btc_eth_oflow_tox_rv_traded_oos.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval69_pooled_btc_eth_oflow_tox_rv_traded_oos.py "
    "tests/test_eval69_pooled_btc_eth_oflow_tox_rv_traded_oos.py",
    "python3 -m pytest -q tests/test_eval69_pooled_btc_eth_oflow_tox_rv_traded_oos.py",
    "# EVAL-69 reuses EVAL-68's disjoint forward capture; runs ONLY AFTER EVAL-68 "
    "seals (single forward window, no competition).",
    "python3 scripts/eval69_phaseb_gate.py            # WAIT_EVAL68(10)/DUE(20)/SEALED(0)",
    "python3 scripts/eval69_phaseb_gate.py --execute  # after EVAL-68 sealed",
)


class NoRealCaptureError(RuntimeError):
    """Raised when sealing is attempted before real BTC+ETH captures exist."""


# ---------------------------------------------------------------------------
# Per-underlying traded-form returns (reuse EVAL-62 build_states + markpath_returns)
# ---------------------------------------------------------------------------
def extract_returns(
    capture: Dict[str, Any],
    *,
    tox_signal: str,
    bar_seconds: float,
) -> Dict[str, Any]:
    """Return the per-bar net-of-cost traded-form returns + counts for one capture.

    Byte-for-byte identical to EVAL-62/64: causal signal_z -> side/exposure ->
    signal-timed delta-hedged ATM straddle with correct mark-path net-of-cost P&L.
    """
    inst = capture.get("underlying", "UNKNOWN")
    states = e62.build_states(capture, tox_signal=tox_signal, bar_seconds=bar_seconds)
    sr = e62.markpath_returns(states)
    return {
        "underlying": inst,
        "signal": tox_signal,
        "bar_seconds": float(bar_seconds),
        "n_states": len(states),
        "returns": [float(r) for r in sr["returns"]],
        "nonzero_positions": int(sr["nonzero"]),
        "n_hedge_rebalances": int(sr["n_hedge_rebalances"]),
        "n_side_flips": int(sr["n_side_flips"]),
    }


def evaluate_pooled_traded(
    captures: Sequence[Dict[str, Any]],
    *,
    tox_signal: str,
    bar_seconds: float,
) -> Dict[str, Any]:
    """Pooled traded-form net-of-cost evaluation across BTC+ETH for one config.

    Per-underlying net-of-cost returns are concatenated into a single pooled sample;
    a single Sharpe, max-drawdown, directional permutation p (H1: mean > 0) and
    block-bootstrap 95% CI (Sharpe) are computed on that pooled sample. Power
    adequacy is the pooled return count >= MIN_POOLED_RETURNS.
    """
    underlyings = [str(c.get("underlying", "?")) for c in captures]
    per_underlying: Dict[str, Dict[str, Any]] = {}
    pooled: List[float] = []
    total_nonzero = 0
    for cap in captures:
        res = extract_returns(cap, tox_signal=tox_signal, bar_seconds=bar_seconds)
        inst = str(cap.get("underlying", "?"))
        rets = res["returns"]
        per_underlying[inst] = {
            "n_states": res["n_states"],
            "n_returns": len(rets),
            "nonzero_positions": res["nonzero_positions"],
            "n_hedge_rebalances": res["n_hedge_rebalances"],
            "n_side_flips": res["n_side_flips"],
            "sharpe": _sharpe_of_returns(rets),
        }
        pooled.extend(rets)
        total_nonzero += int(res["nonzero_positions"])

    n_returns = len(pooled)
    power_ok = bool(n_returns >= MIN_POOLED_RETURNS)
    base = {
        "signal": tox_signal,
        "bar_seconds": float(bar_seconds),
        "underlyings": underlyings,
        "per_underlying": per_underlying,
        "n_returns": n_returns,
        "n_returns_power_adequate": power_ok,
        "min_pooled_returns": MIN_POOLED_RETURNS,
        "nonzero_positions": total_nonzero,
    }
    if n_returns < 8:
        base.update({"error": "insufficient pooled returns", "pass": False})
        return base

    sharpe = _sharpe_of_returns(pooled)
    mdd = e62._max_drawdown(pooled)
    flat = [0.0] * len(pooled)
    perm = permutation_test(
        pooled, flat, statistic=e62._mean,
        n_permutations=PERMUTATION_PERMS, paired=True, seed=SEED,
    )
    boot = block_bootstrap_ci(
        pooled, statistic=_sharpe_of_returns,
        n_bootstrap=BOOTSTRAP_RESAMPLES, block_size=BOOTSTRAP_BLOCK, seed=SEED,
    )
    breach = e62.kill_switch_breach(mdd)
    perm_p = e62._finite(perm.get("p_value"), 1.0)
    ci_low = e62._finite(boot[1], 0.0)
    ci_high = e62._finite(boot[2], 0.0)
    passed = bool(
        sharpe > 0.0
        and not breach
        and perm_p < 0.05
        and ci_low > 0.0
        and total_nonzero > 0
        and power_ok
    )
    base.update({
        "sharpe": sharpe,
        "max_drawdown": mdd,
        "kill_switch_breach": breach,
        "permutation_p": perm_p,
        "bootstrap_ci": [boot[0], ci_low, ci_high],
        "mean_return": e62._mean(pooled),
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
        "eval": "EVAL-69",
        "title": "Pooled BTC+ETH disjoint-window OOS traded-form net-of-cost monetization "
                 "of the suggestive EVAL-65 options order-flow toxicity -> realized-vol "
                 "slice (tox/imbalance, bar60), pooled-sample Sharpe / max-DD / permutation "
                 "/ bootstrap on the mark-path net-of-cost P&L",
        "extends": "EVAL-65/EVAL-67/EVAL-68 (identical signal/P&L/floor reused; BTC and ETH "
                   "traded-form returns pooled into one sample on the same disjoint real "
                   "forward window EVAL-68 acquires)",
        "supersedes": "nothing — disjoint forward OOS traded-form test; non-monetization, "
                      "underpowered, or BLOCKED is a valid sealed result. EVAL-62/64 sealed "
                      "NO-GO on the in-sample window only; this is a fresh-window claim.",
        "capture_dir": str(capture_dir),
        "underlyings_required": list(UNDERLYINGS),
        "disjoint_from": "data/raw/eval63/three_way_{BTC,ETH}_20261116T064816Z.json "
                         "(window 2026-11-09T06:48:16Z..2026-11-16T06:48:16Z)",
        "disjointness_rule": (
            "A capture is usable only if [window_start, window_end] does not overlap "
            "[2026-11-09T06:48:16Z, 2026-11-16T06:48:16Z]. Because the free Deribit "
            "perp 1m endpoint returns at most 5001 candles (300000 s), each capture "
            "must also span >=300000 s. EVAL-69 reuses EVAL-68's capture, which "
            "EVAL-68's gate already enforces to be disjoint; EVAL-69 re-checks it here."
        ),
        "capture_window_rule": (
            "EVAL-69 does NOT acquire. It reads EVAL-68's disjoint forward capture at "
            "data/raw/eval68 (three_way_BTC_*.json + three_way_ETH_*.json), acquired by "
            "scripts/eval68_phaseb_gate.py --execute at/after 2026-11-20T00:00:00Z. Do "
            "not weaken the EVAL-64 floor."
        ),
        "tox_signals": list(TOX_SIGNALS),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "signal": base["signal"],
        "target": "signal-timed delta-hedged ATM straddle mark-path net-of-cost P&L "
                  "(EVAL-62/64 traded form), pooled across BTC+ETH",
        "statistic": (
            "Pooled Sharpe / max-drawdown / directional permutation p / block-bootstrap "
            "95% CI of the concatenated per-bar net-of-cost traded-form returns across "
            "BTC and ETH, per config"
        ),
        "stats": base["stats"],
        "go_bar": (
            "GO only if, pooled across BTC+ETH and at least one of the pre-registered "
            "configs (tox::bar60, imbalance::bar60), the pooled Sharpe > 0, no kill-switch "
            "breach (max-DD <= 0.20), directional permutation p < 0.05, block-bootstrap 95% "
            "CI lower > 0, nonzero positions > 0, pooled returns >= 790 (power), pooled "
            "BH-FDR rejects that config, the EVAL-64 floor is met on BOTH underlyings, and "
            "both capture windows are disjoint from the sealed window; else NO-GO CONFIRMED "
            "(PASS) when floor+disjoint+power but not monetizable, INCONCLUSIVE (UNDERPOWERED) "
            "when floor+disjoint but pooled returns < 790, or BLOCKED when floor/disjoint fails."
        ),
        "data_availability": {
            "note": "reuses EVAL-68's fresh real BTC+ETH three-way capture, disjoint from "
                    "the sealed eval63 window; no new acquisition; public read-only; no "
                    "synthetic data",
            "sealed_window": [SEALED_WINDOW_START, SEALED_WINDOW_END],
            "earliest_disjoint_capture_end": EARLIEST_DISJOINT_CAPTURE_END,
            "deribit_perp_1m_retention_seconds_approx": 300000,
        },
        "floor": floor,
        "min_underlyings": MIN_UNDERLYINGS,
        "min_pooled_returns": MIN_POOLED_RETURNS,
    }


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def _capture_inventory(capture_dir: str) -> List[Dict[str, Any]]:
    return e61._capture_inventory(capture_dir)


def run_eval69(
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
            f"no real BTC/ETH capture found in {capture_dir_abs}; EVAL-69 reuses EVAL-68's "
            "disjoint forward capture. Run scripts/eval68_phaseb_gate.py --execute first "
            f"(it writes three_way_BTC_*.json and three_way_ETH_*.json under {capture_dir_abs}) "
            "and verify they are disjoint from the sealed window before sealing."
        )

    per_underlying_floor: Dict[str, Dict[str, Any]] = {}
    disjointness: Dict[str, Dict[str, Any]] = {}
    for c in captures:
        inst = str(c.get("underlying", "?"))
        per_underlying_floor[inst] = _underlying_floor_strict(c)
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
        for sig in TOX_SIGNALS:
            for bar_s in GRID_BAR_SECONDS:
                try:
                    res = evaluate_pooled_traded(
                        captures, tox_signal=sig, bar_seconds=bar_s
                    )
                except BaseException as exc:  # noqa: BLE001
                    errors.append(f"{sig}::bar{bar_s}: {exc!r}")
                    continue
                per_config.append(res)

    p_values = {
        f"{r['signal']}::bar{r['bar_seconds']}": e65._finite(r.get("permutation_p"), 1.0)
        for r in per_config
        if r.get("n_returns", 0) > 0
    }
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}
    rejected = set(bh.get("rejected") or [])

    pass_configs: List[str] = []
    for r in per_config:
        key = f"{r['signal']}::bar{r['bar_seconds']}"
        if r.get("pass") and key in rejected:
            pass_configs.append(key)

    max_pooled_returns = max((r.get("n_returns", 0) for r in per_config), default=0)
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
        "EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS"
        if floor_and_disjoint_ok
        else "EVAL_69_BLOCKED_FLOOR_OR_DISJOINTNESS"
    )

    protocol = build_protocol(capture_dir)
    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict,
        "verdict_detail": (
            "pooled OOS traded-form (disjoint real BTC+ETH window, reused from EVAL-68) of "
            "the suggestive EVAL-65 slice tox/imbalance::bar60; pooled-sample Sharpe / "
            "max-DD / permutation / bootstrap on the mark-path net-of-cost P&L with EVAL-62 "
            "signal/P&L + EVAL-64 feasible floor reused"
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
            "Pooled across BTC and ETH, the suggestive EVAL-65 slice (tox/imbalance, "
            "bar60) is monetizable net-of-cost out-of-sample on a fresh disjoint real "
            "forward window (reused from EVAL-68): pooled Sharpe > 0, no kill-switch "
            "breach (max-DD <= 0.20), directional permutation p < 0.05, block-bootstrap "
            "95% CI lower > 0, >=790 pooled returns (80% power), and BH-FDR rejects, at "
            "the sealed EVAL-64 floor on both underlyings."
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
        f"# {PREREG_ID} — pooled BTC+ETH OOS traded-form net-of-cost monetization of "
        f"suggestive EVAL-65 slice (tox/imbalance::bar60, pooled-sample Sharpe)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Hypothesis: {r['hypothesis']}",
        f"- Capture dir: `{r['capture_dir']}` (reused from EVAL-68; no new acquisition)",
        f"- Extends: {p['extends']}",
        f"- Disjoint from: {p['disjoint_from']}",
        "",
        "## Pre-declared protocol",
        "",
        f"- Underlyings: {p['underlyings_required']}",
        f"- Tox signals: {p['tox_signals']}",
        f"- Bar grid (s): {p['bar_seconds_grid']}",
        f"- Target: {p['target']}",
        f"- Statistic: {p['statistic']}",
        f"- Stats: perm {p['stats']['permutation_perms']} ({p['stats']['permutation']}) / "
        f"bootstrap {p['stats']['bootstrap_resamples']} block {p['stats']['bootstrap_block']} / "
        f"BH-FDR alpha {p['stats']['fdr_alpha']} / seed {p['stats']['seed']}",
        f"- Power adequacy: pooled returns >= {p['min_pooled_returns']}",
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
        f"# {r['report_id']} — pooled BTC+ETH OOS traded-form net-of-cost monetization "
        f"of suggestive EVAL-65 slice (tox/imbalance::bar60)",
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
              "| signal | bar_s | underlyings | per-underlying n | pooled n | power ok | Sharpe | max-DD | perm_p | CI95 | pass |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in r.get("per_config", []):
        ci = c.get("bootstrap_ci") or [float("nan")] * 3
        pu = c.get("per_underlying") or {}
        n_by = {k: v.get("n_returns", 0) for k, v in pu.items()}
        lines.append(
            f"| {c.get('signal')} | {c.get('bar_seconds')} | "
            f"{','.join(c.get('underlyings', []))} | {n_by} | "
            f"{c.get('n_returns')} | {c.get('n_returns_power_adequate')} | "
            f"{e65._finite(c.get('sharpe'), 0.0):.4f} | "
            f"{e65._finite(c.get('max_drawdown'), 0.0):.4f} | "
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
        f"# {BLOCKED_ID} — pooled BTC+ETH OOS traded-form net-of-cost monetization "
        f"(below the pre-registered feasible floor and/or missing an underlying "
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
        description="EVAL-69: pooled BTC+ETH disjoint-window OOS traded-form net-of-cost "
                    "monetization of the suggestive EVAL-65 options order-flow toxicity "
                    "slice (tox/imbalance, bar60); reuses EVAL-68's capture"
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
        report = run_eval69(
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
        "max_pooled_returns": report.get("pooled", {}).get("max_pooled_returns"),
        "power_adequate": report.get("pooled", {}).get("power_adequate"),
        "bh_fdr_rejected": report.get("pooled", {}).get("bh_fdr", {}).get("rejected"),
        "n_configs": len(report.get("per_config", [])),
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())