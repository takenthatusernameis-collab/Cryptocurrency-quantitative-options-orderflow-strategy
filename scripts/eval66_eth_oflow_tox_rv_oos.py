#!/usr/bin/env python3
"""EVAL-66: isolated, out-of-sample replication on a **disjoint** real ETH window
of the only suggestive EVAL-65 slice (`tox::bar60.0::h72`, `imbalance::bar60.0::h72`).

This is a strict copy-and-retarget of sealed EVAL-65 (predictiveness, Spearman rank
IC between causal options order-flow toxicity and forward realized volatility):
- ETH-only
- configs restricted to tox/imbalance at bar60, horizon 72 (pre-registered)
- reuses sealed EVAL-62 `build_states` and EVAL-64 feasible floor verbatim
- same stats/GO bar (IC>0, directional permutation p<0.05, block-bootstrap 95% CI
  lower>0, BH-FDR rejects)
- artifact IDs EVAL_66_ETH_OFLOW_TOX_RV_OOS_{PREREGISTRATION,COMBINED|BLOCKED}

If the feasible floor is not met on the fresh disjoint capture, seal BLOCKED (never
NO-GO) and do not weaken the floor.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Reuse sealed EVAL-61/EVAL-62 measurement + EVAL-64 feasible floor + EVAL-65 stats.
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_66_ETH_OFLOW_TOX_RV_OOS_COMBINED"
PREREG_ID = "EVAL_66_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION"
BLOCKED_ID = "EVAL_66_ETH_OFLOW_TOX_RV_OOS_BLOCKED"

# Pre-registered configs: only the suggestive EVAL-65 ETH slice.
TOX_SIGNALS: Tuple[str, ...] = ("tox", "imbalance")
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0,)
FORWARD_HORIZONS_BARS: Tuple[int, ...] = (72,)

# Stats (identical to EVAL-65).
PERMUTATION_PERMS = e65.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e65.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e65.BOOTSTRAP_BLOCK
FDR_ALPHA = e65.FDR_ALPHA
SEED = e65.SEED

# Feasible floor reused verbatim from sealed EVAL-64.
_underlying_floor_strict = e64._underlying_floor_strict
MIN_UNDERLYINGS = 1  # ETH-only replication

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval60_acquire_three_way.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval64_orderflow_realized_vol_markpath_feasible.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval66_eth_oflow_tox_rv_oos.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval66_eth_oflow_tox_rv_oos.py "
    "tests/test_eval66_eth_oflow_tox_rv_oos.py",
    "python3 -m pytest -q tests/test_eval66_eth_oflow_tox_rv_oos.py",
    "mkdir -p data/raw/eval66",
    "python3 scripts/eval60_acquire_three_way.py --underlying ETH --days 7 --out-dir data/raw/eval66 --seal",
    "python3 scripts/eval66_eth_oflow_tox_rv_oos.py --capture-dir data/raw/eval66 --no-write",
    "python3 scripts/eval66_eth_oflow_tox_rv_oos.py --capture-dir data/raw/eval66 --seal --task-label EVAL66-ETH-OFLOW-TOX-RV-OOS",
    'python3 scripts/check_session_sealed.py --task-id "INIT-2026-11-16T08:49:47Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION" '
    '--glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" '
    '--require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_COMBINED_*" '
    '--require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_BLOCKED_*"',
)


# ---------------------------------------------------------------------------
# Local wrappers around EVAL-65 helpers bound to EVAL-66 constants
# ---------------------------------------------------------------------------
def evaluate_predictiveness(
    capture: Dict[str, Any],
    *,
    tox_signal: str,
    bar_seconds: float,
    horizon_bars: int,
) -> Dict[str, Any]:
    """EVAL-65 statistic but with EVAL-66 stats constants."""
    inst = capture.get("underlying", "UNKNOWN")
    states = e62.build_states(capture, tox_signal=tox_signal, bar_seconds=bar_seconds)
    pts = [
        (float(s["spot"]), float(s.get("signal_z", 0.0)))
        for s in states
        if float(s.get("spot", 0.0)) > 0.0
    ]
    if len(pts) < horizon_bars + 5:
        return {
            "underlying": inst, "signal": tox_signal,
            "bar_seconds": float(bar_seconds), "horizon_bars": int(horizon_bars),
            "error": "insufficient priced states", "n_pairs": 0, "pass": False,
        }
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

    if len(xs) < 8:
        return {
            "underlying": inst, "signal": tox_signal,
            "bar_seconds": float(bar_seconds), "horizon_bars": int(horizon_bars),
            "error": "insufficient aligned pairs", "n_pairs": len(xs), "pass": False,
        }

    ic, perm_p = e65._perm_p_ic(xs, ys, PERMUTATION_PERMS, SEED)
    med, ci_lo, ci_hi = e65._boot_ci_ic(xs, ys, BOOTSTRAP_RESAMPLES, BOOTSTRAP_BLOCK, SEED)
    passed = bool(ic > 0.0 and perm_p < 0.05 and ci_lo > 0.0 and len(xs) >= 20)
    return {
        "underlying": inst,
        "signal": tox_signal,
        "bar_seconds": float(bar_seconds),
        "horizon_bars": int(horizon_bars),
        "n_pairs": len(xs),
        "n_states": len(states),
        "spearman_ic": ic,
        "permutation_p": perm_p,
        "bootstrap_ci": [med, ci_lo, ci_hi],
        "nonzero_signal_pairs": int(sum(1 for v in xs if abs(v) > 1e-9)),
        "pass": passed,
    }


# ---------------------------------------------------------------------------
# Protocol + orchestration
# ---------------------------------------------------------------------------
def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-66",
        "title": "Isolated disjoint-window OOS replication (ETH-only) of the suggestive "
                 "EVAL-65 options order-flow toxicity -> forward realized-vol slice "
                 "(tox/imbalance, bar60, horizon 72), wrapper-free Spearman rank IC",
        "extends": "EVAL-65 (identical signal/statistic/floor reused; restricted to the "
                   "single ETH predictive slice on a fresh disjoint real window)",
        "supersedes": "nothing — final replication check for the only suggestive "
                      "EVAL-65 ETH slice; non-replication or BLOCKED closes campaign",
        "capture_dir": str(capture_dir),
        "underlyings_required": ["ETH"],
        "disjoint_from": "data/raw/eval63/three_way_ETH_20261116T064816Z.json "
                         "(window 2026-11-09T06:48:16Z..2026-11-16T06:48:16Z)",
        "tox_signals": list(TOX_SIGNALS),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": e65.build_protocol(capture_dir)["signal"],
        "target": e65.build_protocol(capture_dir)["target"],
        "statistic": e65.build_protocol(capture_dir)["statistic"],
        "stats": e65.build_protocol(capture_dir)["stats"],
        "go_bar": (
            "GO only if, on ETH and at least one of the pre-registered configs "
            "(tox::bar60::h72, imbalance::bar60::h72), Spearman IC > 0, directional "
            "permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled "
            "BH-FDR rejects that config; else NO-GO CONFIRMED (PASS)."
        ),
        "data_availability": {
            "note": "fresh real ETH 7d capture, disjoint from eval63 ETH window; "
                    "public read-only, polite rate limiting, single acquisition process; "
                    "no synthetic data",
        },
        "floor": e65.build_protocol(capture_dir)["floor"],
        "min_underlyings": MIN_UNDERLYINGS,
    }


def run_eval66(
    *,
    capture_dir: str = "data/raw/eval66",
    write: bool = True,
    task_label: str = "EVAL66-ETH-OFLOW-TOX-RV-OOS",
) -> Dict[str, Any]:
    generated_at = e65._utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    captures = e61._capture_inventory(str(capture_dir_abs))
    # ETH-only replication
    captures = [c for c in captures if str(c.get("underlying", "")).upper() == "ETH"]

    per_underlying_floor: Dict[str, Dict[str, Any]] = {}
    for c in captures:
        inst = c.get("underlying", "?")
        per_underlying_floor[inst] = _underlying_floor_strict(c)

    floor_ok = bool(
        len(captures) >= MIN_UNDERLYINGS
        and per_underlying_floor
        and all(v["ok"] for v in per_underlying_floor.values())
    )

    per_config: List[Dict[str, Any]] = []
    errors: List[str] = []
    for cap in captures:
        for sig in TOX_SIGNALS:
            for bar_s in GRID_BAR_SECONDS:
                for horizon in FORWARD_HORIZONS_BARS:
                    try:
                        res = evaluate_predictiveness(
                            cap, tox_signal=sig, bar_seconds=bar_s, horizon_bars=horizon
                        )
                    except BaseException as exc:  # noqa: BLE001
                        errors.append(
                            f"{cap.get('underlying')}::{sig}::bar{bar_s}::h{horizon}: {exc!r}"
                        )
                        continue
                    per_config.append(res)

    p_values = {
        f"{r['underlying']}::{r['signal']}::bar{r['bar_seconds']}::h{r['horizon_bars']}":
            e65._finite(r.get("permutation_p"), 1.0)
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
        best = max(valid, key=lambda r: e65._finite(r.get("spearman_ic"), -1e9)) if valid else None
        pass_configs = []
        for r in valid:
            key = (
                f"{r['underlying']}::{r['signal']}::bar{r['bar_seconds']}::"
                f"h{r['horizon_bars']}"
            )
            if r.get("pass") and key in rejected:
                pass_configs.append(key)
        inst_summary.append({
            "underlying": inst,
            "n_configs": len(rows),
            "best_ic": e65._finite(best.get("spearman_ic"), 0.0) if best else 0.0,
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
    campaign_state = "EVAL_66_ETH_OFLOW_TOX_RV_OOS" if floor_ok else "EVAL_66_BLOCKED_FLOOR"

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "isolated OOS replication (disjoint real ETH window) of the suggestive "
            "EVAL-65 slice tox/imbalance::bar60::h72; wrapper-free Spearman rank IC "
            "with EVAL-62 signal + EVAL-64 feasible floor reused"
            if floor_ok else "capture below the pre-registered feasible floor; no verdict"
        ),
        "floor_ok": bool(floor_ok),
        "capture_dir": str(capture_dir_abs),
        "underlyings": sorted(per_underlying_floor),
        "floor": build_protocol(capture_dir)["floor"],
        "per_underlying_floor": per_underlying_floor,
        "protocol": build_protocol(capture_dir),
        "per_config": per_config,
        "per_underlying": inst_summary,
        "pooled": {
            "bh_fdr": bh,
            "all_underlyings_pass": all_pass,
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


def _build_prereg(report: Dict[str, Any]) -> Dict[str, Any]:
    p = report["protocol"]
    return {
        "prereg_id": PREREG_ID,
        "generated_at": report["generated_at"],
        "task": report["task"],
        "hypothesis": (
            "The suggestive EVAL-65 ETH slice (tox/imbalance, bar60, horizon 72) "
            "replicates out-of-sample on a fresh disjoint real ETH 7d window: "
            "Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% "
            "CI lower > 0, and BH-FDR rejects, at the sealed EVAL-64 feasible floor."
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
        f"# {PREREG_ID} — ETH OOS replication of suggestive EVAL-65 slice "
        f"(tox/imbalance::bar60::h72, wrapper-free Spearman rank IC)",
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
        f"- min underlyings (ETH-only): {p['min_underlyings']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {r['report_id']} — ETH OOS replication of suggestive EVAL-65 slice "
        f"(tox/imbalance::bar60::h72)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
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
    lines += ["", "## Per-underlying (best config by Spearman IC)", "",
              "| underlying | configs | best IC | best config | n pass | any pass |",
              "|---|---|---|---|---|---|"]
    for s in r["per_underlying"]:
        lines.append(
            f"| {s['underlying']} | {s['n_configs']} | {s['best_ic']:.4f} | "
            f"{s['best_config']} | {s['n_pass']} | {s['any_pass']} |"
        )
    lines += ["", "## Per-config", "",
              "| underlying | signal | bar_s | horizon | n_pairs | IC | perm_p | CI95 | pass |",
              "|---|---|---|---|---|---|---|---|---|"]
    for c in r.get("per_config", []):
        ci = c.get("bootstrap_ci") or [float("nan")] * 3
        lines.append(
            f"| {c.get('underlying')} | {c.get('signal')} | {c.get('bar_seconds')} | "
            f"{c.get('horizon_bars')} | {c.get('n_pairs')} | "
            f"{e65._finite(c.get('spearman_ic'), 0.0):.4f} | "
            f"{e65._finite(c.get('permutation_p'), 1.0):.4f} | "
            f"[{e65._finite(ci[1], 0.0):.4f}, {e65._finite(ci[2], 0.0):.4f}] | {c.get('pass')} |"
        )
    lines += ["", "## Pooled", "",
              f"- BH-FDR rejected: {r['pooled']['bh_fdr'].get('rejected')}",
              f"- All underlyings pass: {r['pooled']['all_underlyings_pass']}"]
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
    lines = [
        f"# {BLOCKED_ID} — ETH OOS replication of suggestive EVAL-65 slice "
        f"(below the pre-registered feasible floor)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        "- Verdict: **BLOCKED** (measured; not NO-GO)",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Underlyings: {', '.join(r['underlyings'])}",
        f"- Floor met: {r['floor_ok']}",
        "",
        "The capture does not meet the pre-registered feasible floor (reused from "
        "sealed EVAL-64), so no GO/NO-GO verdict is emitted. Do NOT weaken the floor, "
        "do NOT use synthetic data, and do NOT emit NO-GO on under-floor data.",
        "",
        "## Per-underlying floor",
        "",
    ]
    for inst, fl in r["per_underlying_floor"].items():
        lines.append(f"- {inst}: {json.dumps(fl['checks'])}")
    lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-66: isolated disjoint-window ETH OOS replication of the "
                    "suggestive EVAL-65 options order-flow toxicity -> realized-vol "
                    "slice (tox/imbalance, bar60, horizon 72)"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval66")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined/blocked (default)")
    ap.add_argument("--task-label", default="EVAL66-ETH-OFLOW-TOX-RV-OOS")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval66(
            capture_dir=args.capture_dir, write=write, task_label=args.task_label
        )
    except BaseException as exc:  # noqa: BLE001
        traceback.print_exc()
        if write:
            blocked = _build_blocked_report({
                "generated_at": e65._utc_now_iso(),
                "task": args.task_label,
                "verdict": "BLOCKED",
                "capture_dir": args.capture_dir,
                "underlyings": [],
                "per_underlying_floor": {},
                "floor": build_protocol(args.capture_dir)["floor"],
                "floor_ok": False,
                "errors": [repr(exc)],
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
