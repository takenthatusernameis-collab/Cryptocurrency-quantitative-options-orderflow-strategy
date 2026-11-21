#!/usr/bin/env python3
"""EVAL-173: single-asset causal near-ATM implied-vol skew -> forward realized return variance."""

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

import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
import scripts.eval172_single_asset_atm_iv_forward_variance as e172  # noqa: E402
from src.analytics.real_walkforward_certification import _benjamini_hochberg  # noqa: E402

REPORT_ID = "EVAL_173_SINGLE_ASSET_SKEW_FORWARD_VARIANCE_COMBINED"
PREREG_ID = "EVAL_173_SINGLE_ASSET_SKEW_FORWARD_VARIANCE_PREREGISTRATION"
BLOCKED_ID = "EVAL_173_SINGLE_ASSET_SKEW_FORWARD_VARIANCE_BLOCKED"

SURFACE_SIGNAL = "skew"
TARGET = "forward_variance"

GRID_BAR_SECONDS: Tuple[float, ...] = e172.GRID_BAR_SECONDS
FORWARD_HORIZONS_BARS: Tuple[int, ...] = e172.FORWARD_HORIZONS_BARS
SIGNAL_WINDOW_SECONDS: float = e71.SIGNAL_WINDOW_SECONDS
ATM_BAND: float = e71.ATM_BAND

PERMUTATION_PERMS = e65.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e65.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e65.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
ZWINDOW = e62.ZWINDOW

MIN_USABLE_PAIRS_PER_CONFIG = 120

FLOOR: Dict[str, Any] = {
    "min_underlyings": int(e71.FLOOR["min_underlyings"]),
    "min_option_trades_per_underlying": int(e71.FLOOR["min_option_trades_per_underlying"]),
    "min_near_atm_option_trades_per_underlying": int(e71.FLOOR["min_near_atm_option_trades_per_underlying"]),
    "min_perp_candles_per_underlying": int(e71.FLOOR["min_perp_candles_per_underlying"]),
    "min_perp_span_seconds_per_underlying": float(e71.FLOOR["min_perp_span_seconds_per_underlying"]),
    "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
    "note": (
        "Reuses the sealed EVAL-71 surface floor verbatim, applied to BOTH BTC and ETH. "
        "Below the floor the campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 ladder floor."
    ),
}

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval172_single_asset_atm_iv_forward_variance.py",
    "scripts/eval173_single_asset_skew_forward_variance.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval173_single_asset_skew_forward_variance.py tests/test_eval173_single_asset_skew_forward_variance.py",
    "python3 -m pytest -q tests/test_eval173_single_asset_skew_forward_variance.py",
    "python3 scripts/eval173_single_asset_skew_forward_variance.py --capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval173_single_asset_skew_forward_variance.py --capture-dir data/raw/eval61 --seal --task-label EVAL173-SINGLE-ASSET-SKEW-FORWARD-VARIANCE",
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite(x: Any, default: float = 0.0) -> float:
    return e71._finite(x, default)


_forward_return_variance = e172._forward_return_variance


def _underlying_floor(capture: Dict[str, Any]) -> Dict[str, Any]:
    return e71._underlying_surface_floor(capture)


def _campaign_floor(per_underlying: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    return e172._campaign_floor(per_underlying)


def _eval_one_config(
    capture: Dict[str, Any],
    *,
    bar_seconds: float,
    horizon_bars: int,
    surface_signal: str = SURFACE_SIGNAL,
) -> Dict[str, Any]:
    return e172._eval_one_config(
        capture,
        bar_seconds=bar_seconds,
        horizon_bars=horizon_bars,
        surface_signal=surface_signal,
    )


def _select_captures(capture_dir: str) -> List[Dict[str, Any]]:
    return e172._select_captures(capture_dir)


def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-173",
        "title": "Single-asset options implied-vol surface SKEW -> forward realized return variance of the signed return predictiveness (Spearman rank IC)",
        "extends": "EVAL-71 (skew surface signal and floor verbatim) + EVAL-111 (single-asset skew path) + EVAL-172 (forward realized return variance target and inference verbatim)",
        "supersedes": "nothing -- complements EVAL-111 (skew -> forward return skewness), EVAL-121 (skew -> kurtosis), EVAL-164 (skew -> CVaR), and EVAL-172 (atm_iv -> variance); no traded-form claim",
        "capture_dir": str(capture_dir),
        "surface_signal": SURFACE_SIGNAL,
        "target": TARGET,
        "signal_window_seconds": float(SIGNAL_WINDOW_SECONDS),
        "atm_band": float(ATM_BAND),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": "causal per-bar near-ATM put-call implied-vol skew from the real option trade tape, forward-filled and expanding-z-scored at end-of-bar k",
        "target_detail": "forward realized return variance = mean((r - mean(r))**2) over the next H perpetual log returns, strictly after the decision at bar k",
        "statistic": "Spearman rank IC = rho(skew_z_k, forward_variance_k); directional permutation H1: IC > 0",
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation": "directional (H1: IC>0), shuffle variance series",
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
            "zwindow": ZWINDOW,
            "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
        },
        "go_bar": "GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).",
        "data_availability": {
            "note": "uses the already-acquired real on-disk three-way captures; no acquisition and no network",
            "capture_dir": str(capture_dir),
        },
        "floor": dict(FLOOR),
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def run_eval173(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL173-SINGLE-ASSET-SKEW-FORWARD-VARIANCE",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    captures = {str(c.get("underlying")): c for c in _select_captures(str(capture_dir_abs))}

    per_underlying_floor: Dict[str, Dict[str, Any]] = {}
    for c in captures.values():
        inst = c.get("underlying", "?")
        per_underlying_floor[inst] = _underlying_floor(c)
    campaign_floor = _campaign_floor(per_underlying_floor)
    floor_ok = bool(campaign_floor.get("ok"))

    per_config: List[Dict[str, Any]] = []
    errors: List[str] = []
    for cap in captures.values():
        for bar_s in GRID_BAR_SECONDS:
            for horizon in FORWARD_HORIZONS_BARS:
                try:
                    per_config.append(_eval_one_config(cap, bar_seconds=bar_s, horizon_bars=horizon))
                except BaseException as exc:  # noqa: BLE001
                    errors.append(f"{cap.get('underlying')}::skew::bar{bar_s}::h{horizon}: {exc!r}")

    p_values = {
        f"{r['underlying']}::{r['signal']}::bar{r['bar_seconds']}::h{r['horizon_bars']}":
            _finite(r.get("permutation_p"), 1.0)
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
        best = max(valid, key=lambda r: _finite(r.get("spearman_ic"), -1e9)) if valid else None
        pass_configs: List[str] = []
        for r in valid:
            key = f"{r['underlying']}::{r['signal']}::bar{r['bar_seconds']}::h{r['horizon_bars']}"
            if r.get("pass") and key in rejected:
                pass_configs.append(key)
        inst_summary.append({
            "underlying": inst,
            "n_configs": len(rows),
            "best_ic": _finite(best.get("spearman_ic"), 0.0) if best else 0.0,
            "best_config": (
                f"{best['signal']}::bar{best['bar_seconds']}::h{best['horizon_bars']}"
                if best else "n/a"
            ),
            "n_pass": len(pass_configs),
            "pass_configs": pass_configs,
            "any_pass": bool(pass_configs),
        })

    all_pass = bool(inst_summary) and all(s["any_pass"] for s in inst_summary)
    go = bool(floor_ok and all_pass and len(rejected) >= 1)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = "EVAL_173_SINGLE_ASSET_SKEW_FORWARD_VARIANCE" if floor_ok else "EVAL_173_BLOCKED_FLOOR"

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": "wrapper-free Spearman rank IC between the causal options skew surface and forward realized return variance on real captures",
        "floor_ok": bool(floor_ok),
        "capture_dir": str(capture_dir_abs),
        "underlyings": sorted(per_underlying_floor),
        "floor": dict(FLOOR),
        "per_underlying_floor": per_underlying_floor,
        "campaign_floor": campaign_floor,
        "protocol": build_protocol(capture_dir),
        "per_config": per_config,
        "per_underlying": inst_summary,
        "pooled": {"bh_fdr": bh, "all_underlyings_pass": all_pass, "campaign_state": campaign_state},
        "errors": errors,
    }

    if not write:
        return report

    e62._seal(PREREG_ID, _build_prereg(report), _build_prereg_md)
    if not floor_ok:
        e62._seal(BLOCKED_ID, _build_blocked_report(report), _build_blocked_md)
        return report
    e62._seal(REPORT_ID, report, _build_md)
    return report


def _build_prereg(report: Dict[str, Any]) -> Dict[str, Any]:
    p = report["protocol"]
    return {
        "prereg_id": PREREG_ID,
        "generated_at": report["generated_at"],
        "task": report["task"],
        "hypothesis": "The causal near-ATM put-call implied-vol skew has a positive monotone relationship with subsequent forward realized return variance of the same underlying's signed return.",
        "extends": p["extends"],
        "data_availability": p["data_availability"],
        "protocol": p,
        "capture_dir": report["capture_dir"],
        "floor": report["floor"],
    }


def _build_prereg_md(r: Dict[str, Any]) -> str:
    p = r["protocol"]
    return "\n".join([
        f"# {PREREG_ID} — single-asset skew -> forward realized return variance",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Hypothesis: {r['hypothesis']}",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Signal: {p['surface_signal']}",
        f"- Target: {p['target']}",
        f"- Bar grid: {p['bar_seconds_grid']}",
        f"- Forward horizons: {p['forward_horizons_bars']}",
        f"- GO bar: {p['go_bar']}",
    ]) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {r['report_id']} — single-asset skew -> forward realized return variance",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        "",
        "| underlying | configs | best IC | best config | n pass | any pass |",
        "|---|---|---|---|---|---|",
    ]
    for s in r["per_underlying"]:
        lines.append(f"| {s['underlying']} | {s['n_configs']} | {s['best_ic']:.4f} | {s['best_config']} | {s['n_pass']} | {s['any_pass']} |")
    lines += ["", "## Pooled", "", f"- BH-FDR rejected: {r['pooled']['bh_fdr'].get('rejected')}", f"- All underlyings pass: {r['pooled']['all_underlyings_pass']}"]
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
        "per_underlying_floor": r["per_underlying_floor"],
        "floor": r["floor"],
        "floor_ok": r["floor_ok"],
        "errors": r.get("errors", []),
    }


def _build_blocked_md(r: Dict[str, Any]) -> str:
    return "\n".join([
        f"# {BLOCKED_ID} — single-asset skew -> forward realized return variance: BELOW FLOOR",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        "- Verdict: **BLOCKED**",
        f"- Capture dir: `{r['capture_dir']}`",
        "",
        "The capture does not meet the sealed EVAL-71 surface floor; no GO/NO-GO verdict is emitted.",
    ]) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="EVAL-173: single-asset skew -> forward realized return variance")
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument("--task-label", default="EVAL173-SINGLE-ASSET-SKEW-FORWARD-VARIANCE")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval173(capture_dir=args.capture_dir, write=write, task_label=args.task_label)
    except BaseException as exc:  # noqa: BLE001
        traceback.print_exc()
        if write:
            blocked = _build_blocked_report({
                "generated_at": _utc_now_iso(), "task": args.task_label, "verdict": "BLOCKED",
                "capture_dir": args.capture_dir, "underlyings": [], "per_underlying_floor": {},
                "floor": dict(FLOOR), "floor_ok": False, "errors": [repr(exc)],
            })
            e62._seal(BLOCKED_ID, blocked, _build_blocked_md)
        return 1

    print(json.dumps({
        "verdict": report.get("verdict"),
        "floor_ok": report.get("floor_ok"),
        "underlyings": report.get("underlyings"),
        "per_underlying": report.get("per_underlying"),
        "bh_fdr_rejected": report.get("pooled", {}).get("bh_fdr", {}).get("rejected"),
        "n_configs": len(report.get("per_config", [])),
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())