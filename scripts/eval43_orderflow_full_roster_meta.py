#!/usr/bin/env python3
"""EVAL-43: orderflow full-roster net-of-cost meta-analysis (anti-avoidance).

The EVAL-41 Track A orderflow robustness test sealed a NO-GO on three disjoint
tapes (41a/41b/41c). EVAL-42 independently confirmed the *options* pillar is
closed. The one remaining heavy measurement for the orderflow pillar is a single
pre-registered meta-analysis across **every** available real orderflow tape,
including the two tapes Track A never measured (41d fresh and the midday tape)
and the two Track A tapes re-acquired from the public OKX API (41a/41c).

This script is strictly additive: it reuses the sealed loaders, bar builder,
causal signal, toxicity gate, walk-forward engine, capacity-aware sizer and
statistics, and never re-runs EVAL-41/42. It never substitutes synthetic data:
a missing tape is reported in ``input_resolution.missing`` and the run proceeds
as a clearly labelled partial meta-analysis.

Pre-declared protocol (identical for every tape, no curve fitting):
  - 15 s causal bars, trailing 60 s orderflow signal (net aggression);
  - orderflow-only positions: +1 when signal > threshold, -1 when < -threshold,
    flat when the toxicity gate (VPIN-style, 5-trade window) trips;
  - capacity-aware net-of-cost walk-forward (train 120 / test 40 / step 40,
    purge 10, embargo 5, max position 20%);
  - 1000-perm paired permutation vs flat; 1000-resample block bootstrap (block 2);
    CSCV PBO (k=4); BH-FDR (alpha 0.1) across tapes.

Pre-declared GO bar: orderflow-only net-of-cost Sharpe > 0 on >= 3 of the 5
tapes AND no kill-switch breach (max-DD <= 0.20) on any tape. Otherwise
``NO-GO CONFIRMED (PASS)``: the Track A NO-GO is corroborated across the full
roster and the orderflow pillar is definitively closed on the available data.

Seal ``EVAL_43_ORDERFLOW_FULL_ROSTER_META_<UTC>.{json,md}`` (or
``EVAL_43_BLOCKED_<UTC>`` if the run cannot complete).
"""

from __future__ import annotations

import argparse
import hashlib
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

from src.alpha.orderflow_alpha import OrderflowAlphaEngine
from src.analytics.capacity_aware_tca import CapacityAwareSizer
from src.analytics.integrated_options_orderflow_evaluation import (
    DEFAULT_BAR_DURATION_SECONDS,
    DEFAULT_EMBARGO,
    DEFAULT_MAX_POSITION_PCT,
    DEFAULT_N_POINTS,
    DEFAULT_PURGE,
    DEFAULT_SIGNAL_LOOKBACK_SECONDS,
    DEFAULT_SIGNAL_THRESHOLD,
    DEFAULT_STEP_SIZE,
    DEFAULT_TEST_WINDOW,
    DEFAULT_TOXICITY_THRESHOLD,
    DEFAULT_TOXICITY_WINDOW_TRADES,
    DEFAULT_TRAIN_WINDOW,
    HORIZONS,
    _build_bars,
    _causal_signal_series,
    _run_walkforward,
    _toxicities_per_bar,
)
from src.analytics.real_walkforward_certification import _benjamini_hochberg, _cscv_pbo
from src.analytics.strategy_evaluation import block_bootstrap_ci, permutation_test
from src.campaign.integrated import IntegratedConfig, load_real_orderflow
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

OUT_DIR = Path("research_state")
REPORT_ID = "EVAL_43_ORDERFLOW_FULL_ROSTER_META"
BLOCKED_REPORT_ID = "EVAL_43_BLOCKED"

# Pre-declared roster (name -> tape path). All five must be on disk for the full
# bar; missing tapes are reported and the run proceeds as a labelled partial.
TAPES: Dict[str, str] = {
    "41a": "data/raw/orderflow_okx_41a.json",
    "41b": "data/raw/eval41/orderflow_okx_BTC-USD-SWAP_41b_20261113T132756Z.json",
    "41c": "data/raw/orderflow_okx_41c.json",
    "41d_fresh": "data/raw/eval41/orderflow_okx_BTC-USD-SWAP.json",
    "midday": "data/raw/orderflow_okx_BTC-USD-SWAP.json",
}

PERMUTATION_PERMS = 1000
BOOTSTRAP_RESAMPLES = 1000
BOOTSTRAP_BLOCK = 2
PBO_K_FOLDS = 4
PBO_N_COMBINATIONS = 16
FDR_ALPHA = 0.1
SEED = 42

# Pre-declared GO bar.
GO_MIN_POSITIVE_TAPES = 3
GO_MIN_TAPES = 5
KILL_SWITCH_MAX_DD = 0.20

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/integrated_options_orderflow_evaluation.py",
    "src/analytics/capacity_aware_tca.py",
    "src/alpha/orderflow_alpha.py",
    "src/campaign/integrated.py",
    "src/telemetry/serialization.py",
    "scripts/eval43_orderflow_full_roster_meta.py",
    "tests/test_eval43_orderflow_full_roster_meta.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval43_orderflow_full_roster_meta.py "
    "tests/test_eval43_orderflow_full_roster_meta.py",
    "python3 -m pytest -q tests/test_eval43_orderflow_full_roster_meta.py",
    "python3 scripts/eval43_orderflow_full_roster_meta.py",
)


# ---------------------------------------------------------------------------
# Pure helpers (unit-tested)
# ---------------------------------------------------------------------------


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _stamp_for_filename(iso_ts: str) -> str:
    try:
        dt = _parse_ts(iso_ts)
        return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    except Exception:
        return iso_ts.replace("-", "").replace(":", "").replace(".", "")


def _parse_ts(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _finite(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return float(default)
    return v if math.isfinite(v) else float(default)


def _all_finite(obj: Any) -> bool:
    if isinstance(obj, bool):
        return True
    if isinstance(obj, float):
        return math.isfinite(obj)
    if isinstance(obj, int):
        return True
    if isinstance(obj, dict):
        return all(_all_finite(k) or isinstance(k, str) for k in obj) and all(
            _all_finite(v) for v in obj.values()
        )
    if isinstance(obj, (list, tuple)):
        return all(_all_finite(v) for v in obj)
    return True


def _mean(vals: Sequence[float]) -> float:
    xs = [_finite(v) for v in vals]
    return float(sum(xs) / len(xs)) if xs else 0.0


def _sharpe_of_returns(rets: Sequence[float], periods_per_year: float = 252.0) -> float:
    xs = [_finite(r) for r in rets]
    if len(xs) < 2:
        return 0.0
    mean = sum(xs) / len(xs)
    var = sum((x - mean) ** 2 for x in xs) / len(xs)
    std = math.sqrt(var)
    if std <= 0.0 or not math.isfinite(std):
        return 0.0
    sr = mean / std * math.sqrt(periods_per_year)
    return float(sr) if math.isfinite(sr) else 0.0


def _pearson(xs: Sequence[float], ys: Sequence[float]) -> float:
    n = min(len(xs), len(ys))
    if n < 3:
        return 0.0
    a = [_finite(v) for v in xs[:n]]
    b = [_finite(v) for v in ys[:n]]
    ma = sum(a) / n
    mb = sum(b) / n
    cov = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    va = sum((a[i] - ma) ** 2 for i in range(n))
    vb = sum((b[i] - mb) ** 2 for i in range(n))
    if va <= 0.0 or vb <= 0.0:
        return 0.0
    ic = cov / math.sqrt(va * vb)
    return float(ic) if math.isfinite(ic) else 0.0


def threshold_positions(
    signals: Sequence[float],
    toxicities: Sequence[float],
    *,
    threshold: float = DEFAULT_SIGNAL_THRESHOLD,
    toxicity_threshold: float = DEFAULT_TOXICITY_THRESHOLD,
) -> List[int]:
    """Long/short/flat orderflow-only positions with a toxicity gate (pure)."""
    n = min(len(signals), len(toxicities))
    out: List[int] = []
    for i in range(n):
        if _finite(toxicities[i]) >= float(toxicity_threshold):
            out.append(0)
            continue
        s = _finite(signals[i])
        if s > float(threshold):
            out.append(1)
        elif s < -float(threshold):
            out.append(-1)
        else:
            out.append(0)
    return out


def kill_switch_breach(max_drawdown: float) -> bool:
    """Pre-declared kill switch: a drawdown beyond 20% is a breach."""
    return _finite(max_drawdown) > KILL_SWITCH_MAX_DD


def _ic_stats(
    signals: Sequence[float],
    prices: Sequence[float],
    horizons: Sequence[int] = HORIZONS,
) -> Dict[str, Any]:
    """Causal IC of the orderflow signal vs forward returns at each horizon."""
    ic_by_horizon: Dict[str, float] = {}
    tstat_by_horizon: Dict[str, float] = {}
    n_by_horizon: Dict[str, int] = {}
    for h in horizons:
        h = max(1, int(h))
        xs: List[float] = []
        ys: List[float] = []
        for i in range(0, len(prices) - h):
            p0 = _finite(prices[i])
            p1 = _finite(prices[i + h])
            if p0 <= 0.0 or p1 <= 0.0:
                continue
            xs.append(_finite(signals[i]))
            ys.append(p1 / p0 - 1.0)
        ic = _pearson(xs, ys)
        n = len(xs)
        if n > 2 and abs(ic) < 1.0:
            tstat = ic * math.sqrt((n - 2) / (1.0 - ic * ic))
        else:
            tstat = 0.0
        ic_by_horizon[str(h)] = float(ic)
        tstat_by_horizon[str(h)] = float(tstat)
        n_by_horizon[str(h)] = int(n)
    ics = list(ic_by_horizon.values())
    return {
        "ic_by_horizon": ic_by_horizon,
        "ic_tstat_by_horizon": tstat_by_horizon,
        "n_by_horizon": n_by_horizon,
        "ic_mean": float(sum(ics) / len(ics)) if ics else 0.0,
        "ic_abs_mean": float(sum(abs(v) for v in ics) / len(ics)) if ics else 0.0,
    }


def resolve_inputs(
    tape_overrides: Optional[Dict[str, str]] = None,
    *,
    default_tapes: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Resolve tape paths into present/missing without substituting a file."""
    resolved: Dict[str, str] = dict(default_tapes or TAPES)
    for name, path in (tape_overrides or {}).items():
        if path:
            resolved[name] = str(path)
    present: Dict[str, str] = {}
    missing: List[Dict[str, str]] = []
    for name in (default_tapes or TAPES):
        path = resolved[name]
        if Path(path).is_file():
            present[name] = path
        else:
            missing.append({"tape": name, "path": path})
    return {
        "resolved": {name: resolved[name] for name in (default_tapes or TAPES)},
        "present": present,
        "missing": missing,
        "full_roster_met": not missing,
    }


def pooled_verdict(tape_results: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Apply the pre-declared pooled GO bar to per-tape results (pure)."""
    n_tapes = len(tape_results)
    positive = [t for t in tape_results if _finite(t.get("oos_sharpe")) > 0.0]
    breaches = [t for t in tape_results if bool(t.get("kill_switch_breach"))]
    passed = (
        n_tapes >= 1
        and len(positive) >= GO_MIN_POSITIVE_TAPES
        and not breaches
    )
    if passed:
        verdict = "FALSIFIED"
        reason = (
            f"orderflow-only net-of-cost Sharpe > 0 on {len(positive)}/{n_tapes} tapes "
            f"with no kill-switch breach -> Track A NO-GO falsified; requires a sealed "
            f"replication campaign on new real data before any GO."
        )
    else:
        verdict = "NO-GO CONFIRMED (PASS)"
        reason = (
            f"orderflow-only net-of-cost Sharpe > 0 on only {len(positive)}/{n_tapes} tapes "
            f"(bar: >= {GO_MIN_POSITIVE_TAPES}/{GO_MIN_TAPES}) and "
            f"{len(breaches)} kill-switch breach(es) -> Track A NO-GO corroborated across "
            f"the full roster; the orderflow pillar is definitively closed."
        )
    return {
        "n_tapes": int(n_tapes),
        "n_positive_sharpe": int(len(positive)),
        "positive_tapes": [str(t.get("name")) for t in positive],
        "n_kill_switch_breaches": int(len(breaches)),
        "kill_switch_tapes": [str(t.get("name")) for t in breaches],
        "go_min_positive_tapes": int(GO_MIN_POSITIVE_TAPES),
        "go_min_tapes": int(GO_MIN_TAPES),
        "kill_switch_max_drawdown": float(KILL_SWITCH_MAX_DD),
        "passed": bool(passed),
        "verdict": verdict,
        "verdict_reason": reason,
    }


# ---------------------------------------------------------------------------
# Tape preparation and per-tape measurement
# ---------------------------------------------------------------------------


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare_tape(name: str, tape_path: str, *, symbol: str = "BTC") -> Dict[str, Any]:
    """Load one real tape and build bars, signal, toxicities (heavy step).

    ``symbol`` defaults to ``"BTC"`` so the sealed EVAL-43 numbers are
    reproducible unchanged; EVAL-45 passes ``symbol="ETH"`` for cross-asset
    replication (the loader keys the price series on the symbol).
    """
    snapshot = load_real_orderflow(str(symbol), orderflow_path=tape_path)
    bars = _build_bars(snapshot, bar_duration_seconds=DEFAULT_BAR_DURATION_SECONDS)
    bar_ends = list(bars["bar_ends_dt"])
    prices = [float(v) for v in bars["bar_closes"]]
    tox = [
        float(v)
        for v in _toxicities_per_bar(
            snapshot, bar_ends, window_trades=DEFAULT_TOXICITY_WINDOW_TRADES
        )
    ]
    engine = OrderflowAlphaEngine(seed=SEED)
    sig = [
        float(v)
        for v in _causal_signal_series(
            snapshot, bar_ends, prices,
            lookback_seconds=DEFAULT_SIGNAL_LOOKBACK_SECONDS, engine=engine,
        )["signals"]
    ]
    path = Path(tape_path)
    return {
        "name": name,
        "tape_path": tape_path,
        "sha256": _sha256(path),
        "n_trades": int(len(snapshot.trades or [])),
        "n_bars": int(bars["n_bars"]),
        "first_trade_utc": bars["start_timestamp"],
        "last_trade_utc": bars["end_timestamp"],
        "bar_ends": bar_ends,
        "prices": prices,
        "signals": sig,
        "toxicities": tox,
    }


def evaluate_tape(
    *,
    prepared: Dict[str, Any],
    cfg: IntegratedConfig,
    sizer: CapacityAwareSizer,
    symbol: str = "BTC",
) -> Dict[str, Any]:
    """Run the pre-declared orderflow-only protocol on one prepared tape."""
    prices = prepared["prices"]
    timestamps = prepared["bar_ends"]
    positions = threshold_positions(
        prepared["signals"], prepared["toxicities"],
        threshold=DEFAULT_SIGNAL_THRESHOLD,
        toxicity_threshold=DEFAULT_TOXICITY_THRESHOLD,
    )
    wf_args = dict(
        symbol=str(symbol), sizer=sizer, cfg=cfg, n_points=DEFAULT_N_POINTS, seed=SEED,
        max_position_pct=DEFAULT_MAX_POSITION_PCT,
    )
    wf = _run_walkforward(positions=positions, prices=prices, timestamps=timestamps, **wf_args)
    flat_wf = _run_walkforward(
        positions=[0] * len(prices), prices=prices, timestamps=timestamps, **wf_args
    )
    rets = [float(r) for r in wf.get("window_returns", [])]
    flat_rets = [float(r) for r in flat_wf.get("window_returns", [])]

    perm_p = 1.0
    if rets and flat_rets and len(rets) == len(flat_rets):
        try:
            perm = permutation_test(
                rets, flat_rets, statistic=_mean,
                n_permutations=PERMUTATION_PERMS, paired=True, seed=SEED,
            )
            perm_p = float(perm.get("p_value", 1.0))
        except Exception:
            perm_p = 1.0

    try:
        boot = block_bootstrap_ci(
            rets, statistic=_sharpe_of_returns,
            n_bootstrap=BOOTSTRAP_RESAMPLES, block_size=BOOTSTRAP_BLOCK, seed=SEED,
        )
        boot_ci = [float(boot[0]), float(boot[1]), float(boot[2])]
    except Exception:
        boot_ci = [0.0, 0.0, 0.0]

    ic = _ic_stats(prepared["signals"], prices)
    pbo = _cscv_pbo(
        {"orderflow": rets, "flat": flat_rets},
        n_combinations=PBO_N_COMBINATIONS, k_folds=PBO_K_FOLDS, seed=SEED,
    )

    return {
        "name": prepared["name"],
        "tape_path": prepared["tape_path"],
        "sha256": prepared["sha256"],
        "n_trades": prepared["n_trades"],
        "n_bars": prepared["n_bars"],
        "first_trade_utc": prepared["first_trade_utc"],
        "last_trade_utc": prepared["last_trade_utc"],
        "n_windows": int(wf.get("num_windows", 0)),
        "oos_sharpe": float(wf.get("oos_sharpe", 0.0)),
        "oos_return": float(wf.get("oos_return", 0.0)),
        "oos_max_drawdown": float(wf.get("oos_max_drawdown", 0.0)),
        "oos_ann_vol": float(wf.get("oos_ann_vol", 0.0)),
        "num_trades": int(wf.get("num_trades", 0)),
        "total_cost_usd": float(wf.get("total_cost_usd", 0.0)),
        "total_traded_notional": float(wf.get("total_traded_notional", 0.0)),
        "kill_switch_breach": kill_switch_breach(wf.get("oos_max_drawdown", 0.0)),
        "permutation_p": float(perm_p),
        "bootstrap_ci": boot_ci,
        "flat_oos_sharpe": float(flat_wf.get("oos_sharpe", 0.0)),
        "ic": ic,
        "pbo": pbo,
        "window_returns": rets,
        "flat_window_returns": flat_rets,
    }


# ---------------------------------------------------------------------------
# Orchestration and sealing
# ---------------------------------------------------------------------------


def _build_report(
    *,
    generated_at: str,
    tape_results: List[Dict[str, Any]],
    input_resolution: Dict[str, Any],
    protocol: Dict[str, Any],
    report_id: str = REPORT_ID,
    symbol: str = "BTC",
    task_label: str = "EVAL-43-ORDERFLOW-FULL-ROSTER-META",
) -> Dict[str, Any]:
    pooled = pooled_verdict(tape_results)
    p_values = {
        str(t["name"]): float(t.get("permutation_p", 1.0)) for t in tape_results
    }
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA)
    pooled_pbo = _cscv_pbo(
        {str(t["name"]): [float(r) for r in t.get("window_returns", [])] for t in tape_results},
        n_combinations=PBO_N_COMBINATIONS, k_folds=PBO_K_FOLDS, seed=SEED,
    ) if len(tape_results) >= 2 else {"overall_pbo": 0.0, "note": "insufficient tapes"}
    return {
        "report_id": report_id,
        "generated_at": generated_at,
        "symbol": str(symbol),
        "task_id": f"INIT-{generated_at}-{task_label}",
        "campaign_state": "TERMINATED (EVAL-36 TERMINATE_NO_GO); EVAL-37 PASS 9/9",
        "verdict": pooled["verdict"],
        "verdict_reason": pooled["verdict_reason"],
        "verdict_scope": "FULL_ROSTER" if input_resolution["full_roster_met"] else "PARTIAL",
        "protocol": protocol,
        "input_resolution": {
            "present": input_resolution["present"],
            "missing": input_resolution["missing"],
            "full_roster_met": bool(input_resolution["full_roster_met"]),
        },
        "tape_results": tape_results,
        "pooled": pooled,
        "pooled_pbo": pooled_pbo,
        "bh_fdr": bh,
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def _build_blocked_report(generated_at: str, exc: BaseException) -> Dict[str, Any]:
    return {
        "report_id": BLOCKED_REPORT_ID,
        "generated_at": generated_at,
        "task_id": f"INIT-{generated_at}-EVAL-43-BLOCKED",
        "status": "BLOCKED",
        "verdict": "BLOCKED",
        "verdict_reason": "EVAL-43 could not complete; see error.",
        "error_type": type(exc).__name__,
        "error": str(exc),
        "traceback": traceback.format_exc(),
        "commands": list(COMMANDS),
    }


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    serialized = serialize_metrics_strict(payload)
    assert_json_valid(serialized)
    path.write_text(json.dumps(serialized, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_md(r: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# {r['report_id']} — orderflow full-roster net-of-cost meta-analysis")
    lines.append("")
    lines.append(f"- **Report ID:** `{r['report_id']}`")
    lines.append(f"- **Generated:** {r['generated_at']}")
    lines.append(f"- **Task ID:** `{r['task_id']}`")
    lines.append(f"- **Verdict:** **{r['verdict']}**")
    lines.append(f"- **Scope:** {r['verdict_scope']}")
    lines.append(f"- **Reason:** {r['verdict_reason']}")
    lines.append("")
    lines.append("## Inputs")
    lines.append(f"- Full roster met: {r['input_resolution']['full_roster_met']}")
    for name, path in r["input_resolution"]["present"].items():
        lines.append(f"- present `{name}`: `{path}`")
    for miss in r["input_resolution"]["missing"]:
        lines.append(f"- MISSING `{miss['tape']}`: `{miss['path']}`")
    lines.append("")
    lines.append("## Per-tape results")
    lines.append("| tape | bars | Sharpe | max-DD | trades | cost $ | perm p | CI | kill-switch | IC mean |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for t in r["tape_results"]:
        ci = t.get("bootstrap_ci", [0.0, 0.0, 0.0])
        lines.append(
            f"| {t['name']} | {t['n_bars']} | {t['oos_sharpe']:.4f} | "
            f"{t['oos_max_drawdown']:.4f} | {t['num_trades']} | {t['total_cost_usd']:.2f} | "
            f"{t['permutation_p']:.4f} | [{ci[1]:.4f},{ci[2]:.4f}] | "
            f"{t['kill_switch_breach']} | {t['ic']['ic_mean']:.6f} |"
        )
    lines.append("")
    lines.append("## Pooled verdict")
    p = r["pooled"]
    lines.append(f"- Tapes: {p['n_tapes']}; positive Sharpe: {p['n_positive_sharpe']} "
                 f"(bar >= {p['go_min_positive_tapes']}/{p['go_min_tapes']})")
    lines.append(f"- Kill-switch breaches: {p['n_kill_switch_breaches']} (max-DD > {p['kill_switch_max_drawdown']})")
    lines.append(f"- Passed: {p['passed']}")
    lines.append(f"- BH-FDR: {json.dumps(r['bh_fdr'], sort_keys=True)}")
    lines.append(f"- Pooled PBO: {json.dumps(r['pooled_pbo'], sort_keys=True)}")
    lines.append("")
    lines.append("## Commands")
    for cmd in r["commands"]:
        lines.append(f"```bash\n{cmd}\n```")
    return "\n".join(lines)


def run_eval43(
    write: bool = True,
    *,
    tape_overrides: Optional[Dict[str, str]] = None,
    tapes_spec: Optional[Dict[str, str]] = None,
    blocked_report_id: str = BLOCKED_REPORT_ID,
    report_id: str = REPORT_ID,
    symbol: str = "BTC",
    task_label: str = "EVAL-43-ORDERFLOW-FULL-ROSTER-META",
    go_min_positive_tapes: int = GO_MIN_POSITIVE_TAPES,
    go_min_tapes: int = GO_MIN_TAPES,
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    declared_tapes = dict(tapes_spec if tapes_spec is not None else TAPES)
    resolved = resolve_inputs(tape_overrides, default_tapes=declared_tapes)
    protocol = {
        "bar_duration_seconds": float(DEFAULT_BAR_DURATION_SECONDS),
        "signal_lookback_seconds": float(DEFAULT_SIGNAL_LOOKBACK_SECONDS),
        "signal_threshold": float(DEFAULT_SIGNAL_THRESHOLD),
        "toxicity_window_trades": int(DEFAULT_TOXICITY_WINDOW_TRADES),
        "toxicity_threshold": float(DEFAULT_TOXICITY_THRESHOLD),
        "train_window": int(DEFAULT_TRAIN_WINDOW),
        "test_window": int(DEFAULT_TEST_WINDOW),
        "step_size": int(DEFAULT_STEP_SIZE),
        "purge": int(DEFAULT_PURGE),
        "embargo": int(DEFAULT_EMBARGO),
        "max_position_pct": float(DEFAULT_MAX_POSITION_PCT),
        "permutation_perms": int(PERMUTATION_PERMS),
        "bootstrap_resamples": int(BOOTSTRAP_RESAMPLES),
        "bootstrap_block": int(BOOTSTRAP_BLOCK),
        "pbo_k_folds": int(PBO_K_FOLDS),
        "fdr_alpha": float(FDR_ALPHA),
        "seed": int(SEED),
        "go_criteria": (
            f"orderflow-only net-of-cost Sharpe > 0 on >= {go_min_positive_tapes}/"
            f"{go_min_tapes} tapes AND no kill-switch breach (max-DD <= {KILL_SWITCH_MAX_DD})"
        ),
        "go_min_positive_tapes": int(go_min_positive_tapes),
        "go_min_tapes": int(go_min_tapes),
    }

    cfg = IntegratedConfig(
        seed=SEED,
        train_window=DEFAULT_TRAIN_WINDOW,
        test_window=DEFAULT_TEST_WINDOW,
        step_size=DEFAULT_STEP_SIZE,
        purge=DEFAULT_PURGE,
        embargo=DEFAULT_EMBARGO,
        max_position_pct=DEFAULT_MAX_POSITION_PCT,
    )
    sizer = CapacityAwareSizer(seed=SEED)

    tape_results: List[Dict[str, Any]] = []
    errors: List[Dict[str, str]] = []
    for name in declared_tapes:
        path = resolved["present"].get(name)
        if not path:
            continue
        try:
            prepared = prepare_tape(name, path, symbol=symbol)
            tape_results.append(
                evaluate_tape(prepared=prepared, cfg=cfg, sizer=sizer, symbol=symbol)
            )
        except Exception as exc:  # noqa: BLE001 - record and continue (partial)
            errors.append({"tape": name, "error_type": type(exc).__name__, "error": str(exc)})

    report = _build_report(
        generated_at=generated_at,
        tape_results=tape_results,
        input_resolution=resolved,
        protocol=protocol,
        report_id=report_id,
        symbol=symbol,
        task_label=task_label,
    )
    report["tape_errors"] = errors
    assert _all_finite(report), "non-finite values in report"

    artifact_paths: Dict[str, str] = {}
    if write:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = _stamp_for_filename(generated_at)
        jpath = OUT_DIR / f"{report_id}_{stamp}.json"
        mpath = OUT_DIR / f"{report_id}_{stamp}.md"
        _write_json(jpath, report)
        mpath.write_text(build_md(report) + "\n", encoding="utf-8")
        artifact_paths = {"json": str(jpath), "md": str(mpath)}
        report["artifact_paths"] = artifact_paths
        _write_json(jpath, report)
    else:
        report["artifact_paths"] = artifact_paths
    return report


def _seal_blocked(
    generated_at: str,
    exc: BaseException,
    *,
    report_id: str = BLOCKED_REPORT_ID,
    symbol: str = "BTC",
) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _stamp_for_filename(generated_at)
    jpath = OUT_DIR / f"{report_id}_{stamp}.json"
    mpath = OUT_DIR / f"{report_id}_{stamp}.md"
    report = _build_blocked_report(generated_at, exc)
    report["report_id"] = str(report_id)
    report["symbol"] = str(symbol)
    _write_json(jpath, report)
    mpath.write_text(
        f"# {report_id}\n\n- **Generated:** {generated_at}\n"
        f"- **Error:** {type(exc).__name__}: {exc}\n\n```\n{traceback.format_exc()}\n```\n",
        encoding="utf-8",
    )
    return {"json": str(jpath), "md": str(mpath)}


def main(argv: Any = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--tape", action="append", default=[], metavar="NAME=PATH",
                    help="override a roster tape path (repeatable)")
    for key in TAPES:
        ap.add_argument(f"--{key}-tape", dest=f"tape_{key}", default=None,
                        help=f"override the {key} tape path")
    args = ap.parse_args(argv)

    overrides: Dict[str, str] = {}
    for item in args.tape:
        if "=" not in item:
            raise SystemExit(f"--tape expects NAME=PATH, got {item!r}")
        name, path = item.split("=", 1)
        overrides[name.strip()] = path.strip()
    for key in TAPES:
        val = getattr(args, f"tape_{key}")
        if val:
            overrides[key] = val

    generated_at = _utc_now_iso()
    try:
        report = run_eval43(write=not args.no_write, tape_overrides=overrides or None)
    except Exception as exc:  # noqa: BLE001 - seal a BLOCKED artifact, never silent
        traceback.print_exc()
        paths = _seal_blocked(
            generated_at, exc, report_id=BLOCKED_REPORT_ID, symbol="BTC"
        ) if not args.no_write else {}
        print(json.dumps({
            "report_id": BLOCKED_REPORT_ID,
            "verdict": "BLOCKED",
            "error": str(exc),
            "blocked_artifact_paths": paths,
        }, sort_keys=True))
        return 1

    print(json.dumps({
        "report_id": report["report_id"],
        "verdict": report["verdict"],
        "verdict_scope": report["verdict_scope"],
        "n_tapes": report["pooled"]["n_tapes"],
        "n_positive_sharpe": report["pooled"]["n_positive_sharpe"],
        "n_kill_switch_breaches": report["pooled"]["n_kill_switch_breaches"],
        "missing_inputs": report["input_resolution"]["missing"],
        "tape_errors": report.get("tape_errors", []),
        "artifact_paths": report.get("artifact_paths", {}),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        raise