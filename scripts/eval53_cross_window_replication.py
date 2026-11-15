#!/usr/bin/env python3
"""EVAL-53: independent cross-window replication of the EVAL-52 fused
options SURFACE x options-venue ORDER FLOW signal on a new synchronized
~24h Deribit capture (BTC+ETH, window B), measured with the sealed EVAL-52
protocol and combined into a cross-window meta verdict.

The repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is a **combined options + orderflow** strategy. EVAL-46..52 sealed the full
charter ladder ``NO-GO CONFIRMED (PASS)`` including the pure options-side
fusion (EVAL-52). EVAL-53 tests whether the EVAL-52 NO-GO is temporally
stable or window-specific: an independent cross-window replication on a new
synchronized ~24h Deribit capture (window B) vs the sealed window-A capture
(``data/raw/eval52/``, immutable).

Strictly additive: it reuses the sealed EVAL-52 measurement helpers
(``evaluate_config``, ``surface_signal_series``, ``build_bars``,
``_underlying_floor``, ``_capture_inventory``, ``build_protocol`` and the
statistics helpers) and the sealed EVAL-52 acquisition primitive
(``acquire_underlying``). It never re-runs/re-seals EVAL-02..52, never edits
``src/``, never duplicates sealed logic, and never falls back to synthetic
data.

Pre-declared protocol (identical to sealed EVAL-52; no curve fitting):
  * grid: 3 fusion rules ({sign_agreement, regime_filter, continuous_zscore})
    x 3 order-flow signals ({imbalance, notional_imbalance, call_minus_put})
    x 2 bar sizes ({60s, 300s});
  * causal expanding z-score window 20; net-of-cost 5 bps on turnover;
  * 1000 paired permutations + 1000 block-bootstrap (block 2) + CSCV PBO k=4
    + BH-FDR alpha 0.1 + DSR; seed 42; kill-switch max-DD 0.20.

Pre-declared GO bar: GO CONFIRMED only if the per-config GO bar (net-of-cost
Sharpe > 0, no kill-switch breach max-DD <= 0.20, permutation p < 0.05,
bootstrap 95% CI lower > 0) holds on **both** windows for **the same** config
on **both** BTC and ETH (strict cross-window replication) AND pooled PBO < 0.5
on both windows; else ``NO-GO CONFIRMED (PASS)`` when both windows are
floor-passing. Below the heavy-work floor on window B -> ``BLOCKED`` (measured,
never NO-GO, never a substitute for a floor-passing verdict).

Seal (in order): ``EVAL_53_WINDOW_B_ACQUISITION_<UTC>`` manifest, then
``EVAL_53_PREREGISTRATION_<UTC>`` **before** the measurement verdict, then
``EVAL_53_CROSS_WINDOW_COMBINED_<UTC>`` (or ``EVAL_53_BLOCKED_<UTC>`` only if
window B is below floor).

Usage::

    export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
    python3 -m py_compile scripts/eval53_cross_window_replication.py tests/test_eval53_cross_window_replication.py
    python3 -m pytest -q tests/test_eval53_cross_window_replication.py
    # smoke (window B must already exist):
    python3 scripts/eval53_cross_window_replication.py \
        --window-a-dir data/raw/eval52 --window-b-dir data/raw/eval53 --no-write
    # seal (acquires window B if missing, measures, pre-registers, seals verdict):
    python3 scripts/eval53_cross_window_replication.py \
        --window-a-dir data/raw/eval52 --window-b-dir data/raw/eval53
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# --- Sealed EVAL-52 primitives (reused, never duplicated or modified) --- #
import scripts.eval52_options_surface_orderflow_net_of_cost as e52  # noqa: E402
import scripts.eval52_acquire_synchronized_options as acq52  # noqa: E402
import scripts.eval51_acquire_options_orderflow as acq51  # noqa: E402 (_session_client)
from src.analytics.integrated_options_orderflow_evaluation import (  # noqa: E402
    _dsr_of_returns,
    _options_signal_components,
    _sharpe_of_returns,
)
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
    _cscv_pbo,
)
from src.analytics.strategy_evaluation import (  # noqa: E402
    block_bootstrap_ci,
    permutation_test,
)

REPORT_ID = "EVAL_53_CROSS_WINDOW_COMBINED"
PREREG_ID = "EVAL_53_PREREGISTRATION"
ACQ_ID = "EVAL_53_WINDOW_B_ACQUISITION"
BLOCKED_ID = "EVAL_53_BLOCKED"
TASK_LABEL_DEFAULT = (
    "EVAL-53-CROSS-WINDOW-SYNCHRONIZED-SURFACE-X-ORDERFLOW-REPLICATION"
)
OUT_DIR = ROOT / "research_state"
DEFAULT_WINDOW_A_DIR = "data/raw/eval52"
DEFAULT_WINDOW_B_DIR = "data/raw/eval53"

# Reuse EVAL-52 constants verbatim (identical protocol, no fitting).
GRID_BAR_SECONDS = e52.GRID_BAR_SECONDS
OF_SIGNALS = e52.OF_SIGNALS
FUSION_RULES = e52.FUSION_RULES
FUSION_FUNCS = e52.FUSION_FUNCS
ZWINDOW = e52.ZWINDOW
COST_BPS = e52.COST_BPS
PERMUTATION_PERMS = e52.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e52.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e52.BOOTSTRAP_BLOCK
PBO_K_FOLDS = e52.PBO_K_FOLDS
PBO_N_COMBINATIONS = e52.PBO_N_COMBINATIONS
FDR_ALPHA = e52.FDR_ALPHA
SEED = e52.SEED
KILL_SWITCH_MAX_DD = e52.KILL_SWITCH_MAX_DD
MIN_SNAPSHOTS = e52.MIN_SNAPSHOTS
MIN_BARS = e52.MIN_BARS
MIN_INSTRUMENTS = e52.MIN_INSTRUMENTS
MIN_TRADES = e52.MIN_TRADES
MIN_SPAN_SECONDS = e52.MIN_SPAN_SECONDS
MIN_COMMON_BARS = e52.MIN_COMMON_BARS
MIN_UNDERLYINGS = e52.MIN_UNDERLYINGS


# ---------------------------------------------------------------------------
# Pure helpers
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
        dd = (peak - eq) / peak if peak > 0 else 0.0
        mdd = max(mdd, dd)
    return mdd


def _config_id(r: Dict[str, Any]) -> str:
    return f"{r['underlying']}::{r['fusion']}::{r['signal']}::bar{r['bar_seconds']}"


def _underlying_of(config_id: str) -> str:
    return config_id.split("::")[0]


# ---------------------------------------------------------------------------
# Window measurement (sealed EVAL-52 protocol, returns a report dict; no seal)
# ---------------------------------------------------------------------------
def measure_window(
    capture_dir: str, task_label: str, generated_at: str
) -> Dict[str, Any]:
    """Measure one window with the sealed EVAL-52 protocol. Returns a report
    dict (floor, per-config grid, PBO, BH-FDR, per-underlying). Does not seal
    anything and does not depend on the other window."""
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    empty = {
        "capture_dir": str(capture_dir_abs), "generated_at": generated_at,
        "task": task_label, "floor_ok": False, "underlyings": [],
        "per_underlying_floor": {}, "per_config": [], "per_underlying": [],
        "pooled": {"overall_pbo": 0.0, "bh_fdr": {"rejected": []},
                   "all_underlyings_pass": False},
        "errors": [], "verdict": "BLOCKED", "config_pass": [],
    }
    if not capture_dir_abs.is_dir():
        empty["errors"].append(f"capture dir missing: {capture_dir_abs}")
        return empty

    captures = e52._capture_inventory(str(capture_dir_abs))
    per_underlying_floor: Dict[str, Dict[str, Any]] = {}
    surface_by_inst: Dict[str, List[Tuple[int, float]]] = {}
    for c in captures:
        inst = c.get("underlying", "?")
        per_underlying_floor[inst] = e52._underlying_floor(c)
        try:
            surface_by_inst[inst] = e52.surface_signal_series(
                c, c.get("perp_candles", []) or []
            )
        except Exception:  # noqa: BLE001
            surface_by_inst[inst] = []

    floor_ok = bool(
        len(captures) >= MIN_UNDERLYINGS
        and per_underlying_floor
        and all(v["ok"] for v in per_underlying_floor.values())
    )

    per_config: List[Dict[str, Any]] = []
    returns_by_config: Dict[str, List[float]] = {}
    errors: List[str] = []
    for cap in captures:
        inst = cap.get("underlying", "?")
        surf = surface_by_inst.get(inst, [])
        for fusion in FUSION_RULES:
            for sig in OF_SIGNALS:
                for bar_s in GRID_BAR_SECONDS:
                    try:
                        res = e52.evaluate_config(
                            cap, surf, fusion=fusion, of_signal=sig,
                            bar_seconds=bar_s,
                        )
                    except BaseException as exc:  # noqa: BLE001
                        errors.append(
                            f"{inst}::{fusion}::{sig}::bar{bar_s}: {exc!r}"
                        )
                        continue
                    per_config.append(res)
                    if res.get("n_returns", 0) > 0:
                        bars = e52.build_bars(cap, surf, bar_s)
                        pos = FUSION_FUNCS[fusion](
                            [b["surface"] for b in bars],
                            [b[sig] for b in bars],
                        )
                        returns_by_config[_config_id(res)] = (
                            e52.strategy_returns(bars, pos)["returns"]
                        )

    pbo = (
        _cscv_pbo(
            returns_by_config, n_combinations=PBO_N_COMBINATIONS,
            k_folds=PBO_K_FOLDS, seed=SEED,
        )
        if len(returns_by_config) >= 2
        else {"overall_pbo": 0.0, "note": "insufficient configs"}
    )
    p_values = {
        _config_id(r): _finite(r.get("permutation_p"), 1.0)
        for r in per_config if r.get("n_returns", 0) > 0
    }
    bh = (
        _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values
        else {"rejected": []}
    )

    by_inst: Dict[str, List[Dict[str, Any]]] = {}
    for r in per_config:
        by_inst.setdefault(r["underlying"], []).append(r)
    inst_summary: List[Dict[str, Any]] = []
    for inst, rows in by_inst.items():
        best = max(rows, key=lambda r: _finite(r.get("sharpe"), -1e9))
        inst_summary.append({
            "underlying": inst, "n_configs": len(rows),
            "best_sharpe": _finite(best.get("sharpe"), 0.0),
            "best_config": _config_id(best),
            "any_pass": bool(any(r.get("pass") for r in rows)),
        })

    pooled_pbo = _finite(pbo.get("overall_pbo"), 0.0)
    all_pass = bool(inst_summary) and all(s["any_pass"] for s in inst_summary)
    config_pass = sorted(
        _config_id(r) for r in per_config if r.get("pass")
    )

    return {
        "capture_dir": str(capture_dir_abs), "generated_at": generated_at,
        "task": task_label, "floor_ok": bool(floor_ok),
        "underlyings": sorted(per_underlying_floor),
        "per_underlying_floor": per_underlying_floor,
        "per_config": per_config, "per_underlying": inst_summary,
        "pooled": {
            "overall_pbo": pooled_pbo, "bh_fdr": bh,
            "all_underlyings_pass": all_pass,
        },
        "errors": errors,
        "verdict": ("NO-GO CONFIRMED (PASS)" if floor_ok else "BLOCKED"),
        "config_pass": config_pass,
    }


# ---------------------------------------------------------------------------
# Cross-window meta verdict
# ---------------------------------------------------------------------------
def cross_window_meta(
    report_a: Dict[str, Any], report_b: Dict[str, Any]
) -> Dict[str, Any]:
    """Compare window A (sealed eval52) and window B (new capture) on the
    identical protocol. Strict cross-window replication: the SAME config passes
    on both windows."""
    floor_ok_a = bool(report_a.get("floor_ok"))
    floor_ok_b = bool(report_b.get("floor_ok"))
    pbo_a = _finite(report_a.get("pooled", {}).get("overall_pbo"), 1.0)
    pbo_b = _finite(report_b.get("pooled", {}).get("overall_pbo"), 1.0)
    pass_a = set(report_a.get("config_pass", []))
    pass_b = set(report_b.get("config_pass", []))
    replicated = sorted(pass_a & pass_b)
    rep_underlyings = {_underlying_of(cid) for cid in replicated}

    go = bool(
        floor_ok_a and floor_ok_b
        and pbo_a < 0.5 and pbo_b < 0.5
        and "BTC" in rep_underlyings and "ETH" in rep_underlyings
    )
    if not floor_ok_b:
        verdict = "BLOCKED"
    elif go:
        verdict = "GO CONFIRMED"
    else:
        verdict = "NO-GO CONFIRMED (PASS)"
    return {
        "verdict": verdict, "go": bool(go),
        "floor_ok_a": floor_ok_a, "floor_ok_b": floor_ok_b,
        "pooled_pbo_a": pbo_a, "pooled_pbo_b": pbo_b,
        "replicated_configs": replicated,
        "replicated_underlyings": sorted(rep_underlyings),
        "n_configs_a": len(pass_a), "n_configs_b": len(pass_b),
        "n_replicated": len(replicated),
    }


# ---------------------------------------------------------------------------
# Window-B acquisition (reuses sealed EVAL-52 acquisition primitive)
# ---------------------------------------------------------------------------
def _window_b_complete(window_b_dir: str) -> bool:
    dir_abs = Path(window_b_dir)
    if not dir_abs.is_dir():
        return False
    captures = e52._capture_inventory(str(dir_abs))
    return len(captures) >= MIN_UNDERLYINGS and all(
        e52._underlying_floor(c)["ok"] for c in captures
    )


def acquire_window_b(
    window_b_dir: str,
    generated_at: str,
    stamp: str,
    task_id: str,
    *,
    days: float = 1.0,
    underlyings: Tuple[str, ...] = ("BTC", "ETH"),
    max_per_expiry: int = acq52.DEFAULT_MAX_PER_EXPIRY,
    max_expiry_days: int = acq52.DEFAULT_MAX_EXPIRY_DAYS,
    max_trades: int = acq52.DEFAULT_MAX_TRADES_PER_INSTRUMENT,
    min_quotes: int = acq52.DEFAULT_MIN_QUOTES,
    delay: float = acq52.DEFAULT_DELAY,
) -> Dict[str, Any]:
    """Capture synchronized real Deribit options surface + options-venue order
    flow (window B) for each underlying, reusing ``acq52.acquire_underlying``,
    then seal an ``EVAL_53_WINDOW_B_ACQUISITION_<UTC>`` manifest."""
    out_dir = Path(window_b_dir)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    end_dt = datetime.now(timezone.utc)
    end_ms = int(end_dt.timestamp() * 1000)
    start_ms = int(
        (end_dt - timedelta(days=float(days))).timestamp() * 1000
    )
    window_start = acq51._iso_ms(start_ms)
    window_end = acq51._iso_ms(end_ms)

    client = acq51._session_client()
    results: List[Dict[str, Any]] = []
    for underlying in underlyings:
        results.append(acq52.acquire_underlying(
            client, underlying, start_ms, end_ms, out_dir, stamp,
            max_per_expiry=max_per_expiry,
            max_expiry_days=max_expiry_days,
            max_trades=max_trades,
            min_quotes=min_quotes,
            delay=delay,
        ))

    written = _seal_acquisition_manifest(
        results, generated_at, task_id, window_start, window_end
    )
    return {"manifest": written, "captures": [r["summary"] for r in results]}


def _seal_acquisition_manifest(
    results: List[Dict[str, Any]], generated_at: str, task_id: str,
    window_start: str, window_end: str,
) -> Dict[str, str]:
    stamp = _stamp_for_filename(generated_at)
    manifest = {
        "manifest_id": ACQ_ID,
        "task_id": task_id,
        "generated_at": generated_at,
        "schema": acq52.SCHEMA,
        "venue": "deribit",
        "window_start": window_start,
        "window_end": window_end,
        "underlyings": [r["summary"]["underlying"] for r in results],
        "captures": {
            r["summary"]["underlying"]: {
                "path": str(r["path"]), "sha256": acq51._sha256(Path(r["path"])),
                **r["summary"],
            }
            for r in results
        },
        "synthetic": False,
        "provenance": (
            "real Deribit public options surface (5m candles) + options-venue "
            "order flow (signed trades) + perpetual candles; synchronized "
            "window B; no synthetic data"
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / f"{ACQ_ID}_{stamp}.json"
    json_path.write_text(json.dumps(manifest, indent=2, default=str))
    lines = [
        f"# {ACQ_ID} — real Deribit synchronized options surface x options order flow (window B)",
        "",
        f"- Generated: `{generated_at}`",
        f"- Task: `{task_id}`",
        f"- Window: `{window_start}` .. `{window_end}`",
        f"- Underlyings: {', '.join(manifest['underlyings'])}",
        f"- Synthetic: **{manifest['synthetic']}**",
        "",
        "## Per-underlying integrity",
        "",
    ]
    for r in results:
        s = r["summary"]
        sf = s["surface"]
        of = s["orderflow"]
        lines += [
            f"### {s['underlying']} (`{s['path']}`)",
            "",
            f"- surface snapshots: {sf['n_snapshots']} / instruments with data {sf['n_instruments_with_data']} / "
            f"5m bars {sf['n_bars_5m']} / span {sf['span_seconds']} s",
            f"- order-flow trades: {of['n_option_trades']} / instruments with trades {of['n_instruments_with_trades']} / "
            f"span {of['span_seconds']} s",
            f"- surface non-degenerate: **{sf['non_degenerate']}**; order-flow non-degenerate: **{of['non_degenerate']}**",
            "",
        ]
    md_path = json_path.with_suffix(".md")
    md_path.write_text("\n".join(lines) + "\n")
    return {"json": str(json_path), "md": str(md_path)}


# ---------------------------------------------------------------------------
# Reporting builders (EVAL-53 IDs; never EVAL-52 IDs)
# ---------------------------------------------------------------------------
def build_prereg(
    report_a: Dict[str, Any], report_b: Dict[str, Any], meta: Dict[str, Any],
    task_id: str, generated_at: str,
) -> Dict[str, Any]:
    return {
        "prereg_id": PREREG_ID,
        "generated_at": generated_at,
        "task": task_id,
        "hypothesis": (
            "The EVAL-52 fused options-surface x options-venue-order-flow NO-GO "
            "is temporally stable across an independent synchronized ~24h Deribit "
            "capture (window B, BTC+ETH)."
        ),
        "window_a_dir": report_a.get("capture_dir", DEFAULT_WINDOW_A_DIR),
        "window_b_dir": report_b.get("capture_dir", DEFAULT_WINDOW_B_DIR),
        "protocol": e52.build_protocol(
            report_a.get("capture_dir", DEFAULT_WINDOW_A_DIR)
        ),
        "meta_go_bar": (
            "GO CONFIRMED only if the per-config GO bar (net-of-cost Sharpe > 0, "
            "no kill-switch breach max-DD <= 0.20, permutation p < 0.05, "
            "bootstrap 95% CI lower > 0) holds on both windows for the same "
            "config on both BTC and ETH, and pooled PBO < 0.5 on both windows;"
            " else NO-GO CONFIRMED (PASS) when both windows floor-passing; "
            "BLOCKED if window B is below the heavy-work floor."
        ),
        "floor": e52.build_protocol(
            report_a.get("capture_dir", DEFAULT_WINDOW_A_DIR)
        )["floor"],
    }


def build_prereg_md(p: Dict[str, Any]) -> str:
    proto = p["protocol"]
    lines = [
        f"# {p['prereg_id']} — EVAL-53 cross-window surface x options order-flow replication",
        "",
        f"- Generated: `{p['generated_at']}`",
        f"- Task: `{p['task']}`",
        f"- Hypothesis: {p['hypothesis']}",
        f"- Window A (sealed eval52): `{p['window_a_dir']}`",
        f"- Window B (new capture): `{p['window_b_dir']}`",
        "",
        "## Pre-declared protocol (sealed EVAL-52, reused verbatim)",
        "",
        f"- Surface components: {proto['surface_components']}",
        f"- Order-flow signals: {proto['orderflow_signals']}",
        f"- Fusion rules: {proto['fusion_rules']}",
        f"- Bar grid (s): {proto['bar_seconds_grid']}",
        f"- z-window: {proto['zwindow']}; cost: {proto['cost_bps']} bps",
        f"- Stats: perm {proto['stats']['permutation_perms']} paired / "
        f"bootstrap {proto['stats']['bootstrap_resamples']} block {proto['stats']['bootstrap_block']} / "
        f"PBO k={proto['stats']['pbo_k_folds']} / BH-FDR alpha {proto['stats']['fdr_alpha']} / "
        f"seed {proto['stats']['seed']}",
        f"- Kill-switch max-DD: {proto['kill_switch_max_dd']}",
        "",
        "## Pre-declared cross-window GO bar",
        "",
        p["meta_go_bar"],
        "",
        "## Heavy-work floor (must be met to seal a verdict)",
        "",
        f"- min surface snapshots/underlying: {p['floor']['min_surface_snapshots_per_underlying']}",
        f"- min bars/underlying: {p['floor']['min_bars_per_underlying']}",
        f"- min instruments/underlying: {p['floor']['min_instruments_per_underlying']}",
        f"- min option trades/underlying: {p['floor']['min_option_trades_per_underlying']}",
        f"- min span seconds/underlying: {p['floor']['min_span_seconds_per_underlying']}",
        f"- min common 5m bars/underlying: {p['floor']['min_common_bars_per_underlying']}",
        f"- min underlyings: {p['floor']['min_underlyings']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_combined_report(
    report_a: Dict[str, Any], report_b: Dict[str, Any],
    meta: Dict[str, Any], acq_written: Optional[Dict[str, Any]],
    task_id: str, generated_at: str,
) -> Dict[str, Any]:
    return {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_id,
        "verdict": meta["verdict"],
        "verdict_detail": (
            "independent cross-window replication of EVAL-52 fused options "
            "surface x options-venue order flow (window A sealed eval52 vs "
            "window B new Deribit capture)"
        ),
        "go": bool(meta["go"]),
        "floor_ok_a": meta["floor_ok_a"],
        "floor_ok_b": meta["floor_ok_b"],
        "pooled_pbo_a": meta["pooled_pbo_a"],
        "pooled_pbo_b": meta["pooled_pbo_b"],
        "window_a": report_a.get("capture_dir", DEFAULT_WINDOW_A_DIR),
        "window_b": report_b.get("capture_dir", DEFAULT_WINDOW_B_DIR),
        "underlyings_a": report_a.get("underlyings", []),
        "underlyings_b": report_b.get("underlyings", []),
        "per_underlying_floor_a": report_a.get("per_underlying_floor", {}),
        "per_underlying_floor_b": report_b.get("per_underlying_floor", {}),
        "per_underlying_a": report_a.get("per_underlying", []),
        "per_underlying_b": report_b.get("per_underlying", []),
        "pooled_a": report_a.get("pooled", {}),
        "pooled_b": report_b.get("pooled", {}),
        "replicated_configs": meta["replicated_configs"],
        "replicated_underlyings": meta["replicated_underlyings"],
        "n_configs_a": meta["n_configs_a"],
        "n_configs_b": meta["n_configs_b"],
        "n_replicated": meta["n_replicated"],
        "errors_a": report_a.get("errors", []),
        "errors_b": report_b.get("errors", []),
        "acquisition": acq_written or {},
    }


def build_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {r['report_id']} — EVAL-53 cross-window surface x options order-flow replication",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}** (GO: {r['go']})",
        f"- Floor OK window A: {r['floor_ok_a']} | window B: {r['floor_ok_b']}",
        f"- Pooled PBO window A: {r['pooled_pbo_a']:.4f} | window B: {r['pooled_pbo_b']:.4f}",
        f"- Replicated configs: {r['n_replicated']} ({', '.join(r['replicated_configs']) or 'none'})",
        f"- Replicated underlyings: {', '.join(r['replicated_underlyings']) or 'none'}",
        "",
        "## Per-underlying floor — window A (sealed eval52)",
        "",
    ]
    for inst, fl in r["per_underlying_floor_a"].items():
        lines.append(
            f"- {inst}: snaps {fl['n_surface_snapshots']} / surf inst {fl['n_surface_instruments']} / "
            f"5m bars {fl['n_surface_bars_5m']} / trades {fl['n_option_trades']} / "
            f"of inst {fl['n_of_instruments']} / span {fl['of_span_seconds']:.0f}s / "
            f"common 5m {fl['n_common_bars_5m']} / ok {fl['ok']}"
        )
    lines += ["", "## Per-underlying floor — window B (new capture)", ""]
    for inst, fl in r["per_underlying_floor_b"].items():
        lines.append(
            f"- {inst}: snaps {fl['n_surface_snapshots']} / surf inst {fl['n_surface_instruments']} / "
            f"5m bars {fl['n_surface_bars_5m']} / trades {fl['n_option_trades']} / "
            f"of inst {fl['n_of_instruments']} / span {fl['of_span_seconds']:.0f}s / "
            f"common 5m {fl['n_common_bars_5m']} / ok {fl['ok']}"
        )
    lines += ["", "## Per-underlying best — window A", ""]
    for s in r["per_underlying_a"]:
        lines.append(
            f"- {s['underlying']}: {s['n_configs']} configs, best Sharpe {s['best_sharpe']:.4f}, "
            f"{s['best_config']}, any pass {s['any_pass']}"
        )
    lines += ["", "## Per-underlying best — window B", ""]
    for s in r["per_underlying_b"]:
        lines.append(
            f"- {s['underlying']}: {s['n_configs']} configs, best Sharpe {s['best_sharpe']:.4f}, "
            f"{s['best_config']}, any pass {s['any_pass']}"
        )
    if r["errors_a"]:
        lines += ["", "## Errors — window A", ""] + [f"- {e}" for e in r["errors_a"]]
    if r["errors_b"]:
        lines += ["", "## Errors — window B", ""] + [f"- {e}" for e in r["errors_b"]]
    return "\n".join(lines) + "\n"


def _build_blocked_report(
    report_a: Dict[str, Any], report_b: Dict[str, Any],
    meta: Dict[str, Any], acq_written: Optional[Dict[str, Any]],
    task_id: str, generated_at: str,
) -> Dict[str, Any]:
    return {
        "report_id": BLOCKED_ID,
        "generated_at": generated_at,
        "task": task_id,
        "verdict": "BLOCKED",
        "verdict_detail": (
            "window B below the pre-registered heavy-work floor; no GO/NO-GO "
            "verdict emitted"
        ),
        "floor_ok_a": meta["floor_ok_a"],
        "floor_ok_b": meta["floor_ok_b"],
        "pooled_pbo_a": meta["pooled_pbo_a"],
        "pooled_pbo_b": meta["pooled_pbo_b"],
        "window_a": report_a.get("capture_dir", DEFAULT_WINDOW_A_DIR),
        "window_b": report_b.get("capture_dir", DEFAULT_WINDOW_B_DIR),
        "underlyings_a": report_a.get("underlyings", []),
        "underlyings_b": report_b.get("underlyings", []),
        "per_underlying_floor_b": report_b.get("per_underlying_floor", {}),
        "replicated_configs": meta["replicated_configs"],
        "errors_b": report_b.get("errors", []),
        "acquisition": acq_written or {},
    }


def build_blocked_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {r['report_id']} — EVAL-53 cross-window surface x options order-flow (below heavy-work floor)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        "- Verdict: **BLOCKED** (measured; not NO-GO)",
        f"- Floor OK window A: {r['floor_ok_a']} | window B: {r['floor_ok_b']}",
        f"- Window B: `{r['window_b']}`",
        "",
        "The window-B capture does not meet the pre-registered heavy-work floor,",
        "so no GO/NO-GO verdict is emitted. Widen the capture and resume.",
        "",
        "## Per-underlying floor — window B",
        "",
    ]
    for inst, fl in r["per_underlying_floor_b"].items():
        lines.append(f"- {inst}: {json.dumps(fl.get('checks', {}))}")
    if r["errors_b"]:
        lines += ["", "## Errors — window B", ""] + [f"- {e}" for e in r["errors_b"]]
    lines.append("")
    return "\n".join(lines) + "\n"


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, default=str))


def _seal(
    report_id: str, report: Dict[str, Any], md_builder=None
) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _stamp_for_filename(report.get("generated_at") or _utc_now_iso())
    written: Dict[str, str] = {}
    j = OUT_DIR / f"{report_id}_{stamp}.json"
    _write_json(j, report)
    written["json"] = str(j)
    if md_builder is not None:
        m = OUT_DIR / f"{report_id}_{stamp}.md"
        m.write_text(md_builder(report), encoding="utf-8")
        written["md"] = str(m)
    return written


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-53 cross-window surface x options-venue order-flow replication"
    )
    ap.add_argument("--window-a-dir", default=DEFAULT_WINDOW_A_DIR)
    ap.add_argument("--window-b-dir", default=DEFAULT_WINDOW_B_DIR)
    ap.add_argument("--no-write", action="store_true",
                    help="compute + print, seal nothing")
    ap.add_argument("--acquire-window-b", action="store_true",
                    help="acquire synchronized real Deribit window B before measuring")
    ap.add_argument("--days", type=float, default=1.0,
                    help="trailing window length in days for window B")
    ap.add_argument("--task-label", default=TASK_LABEL_DEFAULT)
    args = ap.parse_args(argv)

    write = not args.no_write
    generated_at = _utc_now_iso()
    stamp = _stamp_for_filename(generated_at)
    task_id = f"INIT-{generated_at}-{args.task_label}"

    acq_written: Optional[Dict[str, Any]] = None
    if args.acquire_window_b or (write and not _window_b_complete(args.window_b_dir)):
        try:
            acq_written = acquire_window_b(
                args.window_b_dir, generated_at, stamp, task_id, days=args.days,
            )
        except Exception as exc:  # noqa: BLE001
            traceback.print_exc()
            acq_written = {"error": repr(exc), "stage": "acquire_window_b"}

    report_a = measure_window(args.window_a_dir, task_id, generated_at)
    report_b = measure_window(args.window_b_dir, task_id, generated_at)
    meta = cross_window_meta(report_a, report_b)

    if write:
        # Pre-register BEFORE the measurement verdict.
        prereg = build_prereg(report_a, report_b, meta, task_id, generated_at)
        _seal(PREREG_ID, prereg, build_prereg_md)
        if not meta["floor_ok_b"]:
            blocked = _build_blocked_report(
                report_a, report_b, meta, acq_written, task_id, generated_at
            )
            _seal(BLOCKED_ID, blocked, build_blocked_md)
        else:
            combined = _build_combined_report(
                report_a, report_b, meta, acq_written, task_id, generated_at
            )
            _seal(REPORT_ID, combined, build_md)

    print(json.dumps({
        "task_id": task_id,
        "verdict": meta["verdict"],
        "go": bool(meta["go"]),
        "floor_ok_a": meta["floor_ok_a"],
        "floor_ok_b": meta["floor_ok_b"],
        "pooled_pbo_a": meta["pooled_pbo_a"],
        "pooled_pbo_b": meta["pooled_pbo_b"],
        "n_configs_a": meta["n_configs_a"],
        "n_configs_b": meta["n_configs_b"],
        "n_replicated": meta["n_replicated"],
        "replicated_configs": meta["replicated_configs"],
        "window_a": report_a.get("capture_dir"),
        "window_b": report_b.get("capture_dir"),
        "acquisition": acq_written,
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        raise
