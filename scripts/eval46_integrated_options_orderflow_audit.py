#!/usr/bin/env python3
"""EVAL-46: integrated (fused) options+orderflow net-of-cost falsification.

The repository charter is a **combined options + orderflow** strategy. The prior
campaign sealed each pillar in isolation (EVAL-41/42/43 orderflow+options BTC
NO-GO, EVAL-45 ETH orderflow NO-GO / options BLOCKED) and only weakly tested the
combined thesis (EVAL-18 static/degenerate; EVAL-31 3 snapshots, permutation
p=0.768 / PBO=0.75). The full 101-snapshot dense BTC options series has never
been fused with the real orderflow signal in a rigorous, pre-registered,
net-of-cost falsification. This script is that test.

It is strictly additive: it reuses the sealed loaders, bar builder, causal
signal, toxicity gate, fusion, walk-forward engine, capacity-aware sizer and
statistics, and never re-runs EVAL-41/42/43 or edits any ``src/`` module. The
heavy per-bar causal signal/toxicity are re-implemented here with a bisect slice
(verified bit-identical to the sealed ``_causal_signal_series`` /
``_toxicities_per_bar``; ~42x faster) purely to remove the runtime bottleneck —
the sealed module is untouched.

Pre-declared protocol (identical for every tape, no curve fitting):
  - 15 s causal bars, trailing 60 s orderflow signal (net aggression);
  - options signal = causal step function of the newest snapshot <= bar_end
    (``align_options_signal_to_bars`` on the 101 real BTC snapshots);
  - >=3 fusion rules, each with the VPIN toxicity gate (>=0.7 -> flat):
      (a) sign_agreement  — both pillars agree in sign (``_fuse_positions``);
      (b) regime_filter   — options sign as causal regime gate x orderflow
                            direction (product of thresholded signs);
      (c) continuous_zscore — causal expanding z-score of each pillar, summed,
                            thresholded;
  - capacity-aware net-of-cost walk-forward (train 120 / test 40 / step 40,
    purge 10, embargo 5, max position 20%) for combined + options-only +
    orderflow-only + flat controls;
  - 1000-perm paired permutation (combined vs best control); 1000-resample
    block bootstrap (block 2) CI on Sharpe; CSCV PBO (k=4); BH-FDR (alpha 0.1);
    DSR on the combined leg.

Pre-declared GO bar (conservative; the campaign is TERMINATED, so NO-GO is the
default and GO requires strong out-of-sample evidence): GO only if, across
**both** real BTC tapes, at least one fusion rule shows combined net-of-cost
Sharpe > 0, no kill-switch breach (max-DD <= 0.20), permutation p < 0.05, and
bootstrap 95% CI lower bound > 0. Otherwise ``NO-GO CONFIRMED (PASS)``: the
combined thesis is not net-of-cost tradable on the available real BTC data.

Seal ``EVAL_46_PREREGISTRATION_<UTC>.{json,md}`` (before measurement) then
``EVAL_46_INTEGRATED_OPTIONS_ORDERFLOW_<UTC>.{json,md}`` (or
``EVAL_46_BLOCKED_<UTC>`` if the run cannot complete).
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import math
import sys
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
    OrderflowAlphaEngine,
    _build_bars,
    _dsr_of_returns,
    _fuse_positions,
    _parse_ts,
    _run_walkforward,
    _signal_positions,
)
from src.analytics.options_time_varying_signal import (
    align_options_signal_to_bars,
    load_snapshot_signals,
)
from src.analytics.real_walkforward_certification import _benjamini_hochberg, _cscv_pbo
from src.analytics.strategy_evaluation import block_bootstrap_ci, permutation_test
from src.campaign.integrated import (
    IntegratedConfig,
    OrderflowSnapshot,
    load_real_orderflow,
)
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

OUT_DIR = Path("research_state")
REPORT_ID = "EVAL_46_INTEGRATED_OPTIONS_ORDERFLOW"
PREREG_ID = "EVAL_46_PREREGISTRATION"
BLOCKED_ID = "EVAL_46_BLOCKED"

OPTIONS_DIR = "data/raw/options_candles"
TAPES: Dict[str, str] = {
    "41d_fresh": "data/raw/eval41/orderflow_okx_BTC-USD-SWAP.json",
    "midday": "data/raw/eval41/orderflow_okx_BTC-USD-SWAP_midday_20261114T090522Z.json",
}

PERMUTATION_PERMS = 1000
BOOTSTRAP_RESAMPLES = 1000
BOOTSTRAP_BLOCK = 2
PBO_K_FOLDS = 4
PBO_N_COMBINATIONS = 16
FDR_ALPHA = 0.1
SEED = 42
KILL_SWITCH_MAX_DD = 0.20
Z_THRESHOLD = 0.5
Z_MIN_PERIODS = 5

FUSION_RULES: Tuple[str, ...] = ("sign_agreement", "regime_filter", "continuous_zscore")

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/integrated_options_orderflow_evaluation.py",
    "src/analytics/options_time_varying_signal.py",
    "src/analytics/capacity_aware_tca.py",
    "src/analytics/real_walkforward_certification.py",
    "src/analytics/strategy_evaluation.py",
    "src/campaign/integrated.py",
    "src/telemetry/serialization.py",
    "scripts/eval46_integrated_options_orderflow_audit.py",
    "tests/test_eval46_integrated_options_orderflow_audit.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval46_integrated_options_orderflow_audit.py "
    "tests/test_eval46_integrated_options_orderflow_audit.py",
    "python3 -m pytest -q tests/test_eval46_integrated_options_orderflow_audit.py",
    "python3 scripts/eval46_integrated_options_orderflow_audit.py --no-write",
    "python3 scripts/eval46_integrated_options_orderflow_audit.py",
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


def kill_switch_breach(max_drawdown: float) -> bool:
    """Pre-declared kill switch: a drawdown beyond 20% is a breach."""
    return _finite(max_drawdown) > KILL_SWITCH_MAX_DD


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Fast causal signal / toxicity (bisect slice; verified bit-identical to the
# sealed _causal_signal_series / _toxicities_per_bar). The sealed module is not
# modified; this only removes the O(bars x trades) runtime bottleneck.
# ---------------------------------------------------------------------------


def _fast_causal_signal(
    snapshot: OrderflowSnapshot,
    bar_ends: Sequence[datetime],
    lookback_seconds: float,
    engine: OrderflowAlphaEngine,
) -> List[float]:
    trades = sorted(snapshot.trades or [], key=lambda t: _parse_ts(t.timestamp))
    ts = [_parse_ts(t.timestamp) for t in trades]
    lookback = max(float(lookback_seconds), 0.0)
    out: List[float] = []
    for be in bar_ends:
        hi = bisect.bisect_right(ts, be)
        lo = bisect.bisect_right(ts, be - timedelta(seconds=lookback)) if lookback > 0 else 0
        win = trades[lo:hi]
        causal = OrderflowSnapshot(
            symbol=snapshot.symbol, venue=snapshot.venue, trades=win, timestamp=be
        )
        out.append(float(engine.extract_features(causal).net_aggression))
    return out


def _fast_toxicity(
    snapshot: OrderflowSnapshot,
    bar_ends: Sequence[datetime],
    window_trades: int,
) -> List[float]:
    trades = sorted(snapshot.trades or [], key=lambda t: _parse_ts(t.timestamp))
    ts = [_parse_ts(t.timestamp) for t in trades]
    w = max(1, int(window_trades))
    out: List[float] = []
    for be in bar_ends:
        hi = bisect.bisect_right(ts, be)
        win = trades[max(0, hi - w):hi]
        buy_vol = sum(float(t.size) for t in win if str(t.side).lower() == "buy")
        sell_vol = sum(float(t.size) for t in win if str(t.side).lower() == "sell")
        total = buy_vol + sell_vol
        score = 0.0 if total <= 0.0 else abs(buy_vol - sell_vol) / total
        out.append(float(min(1.0, max(0.0, score))))
    return out


# ---------------------------------------------------------------------------
# Fusion rules (pure). Each applies the VPIN toxicity gate.
# ---------------------------------------------------------------------------


def _gated_positions(
    signal: Sequence[float],
    toxicity: Sequence[float],
    *,
    threshold: float = DEFAULT_SIGNAL_THRESHOLD,
    toxicity_threshold: float = DEFAULT_TOXICITY_THRESHOLD,
) -> List[int]:
    """Threshold a single pillar into -1/0/+1 with the toxicity gate."""
    n = min(len(signal), len(toxicity))
    out: List[int] = []
    for i in range(n):
        if _finite(toxicity[i]) >= float(toxicity_threshold):
            out.append(0)
            continue
        s = _finite(signal[i])
        if s > float(threshold):
            out.append(1)
        elif s < -float(threshold):
            out.append(-1)
        else:
            out.append(0)
    return out


def fuse_sign_agreement(
    options_signal: Sequence[float],
    orderflow_signal: Sequence[float],
    toxicity: Sequence[float],
    *,
    toxicity_threshold: float = DEFAULT_TOXICITY_THRESHOLD,
    signal_threshold: float = DEFAULT_SIGNAL_THRESHOLD,
) -> List[int]:
    """Rule (a): trade only when both pillars agree in sign (reuse sealed)."""
    return _fuse_positions(
        options_signal, orderflow_signal, toxicity,
        toxicity_threshold=toxicity_threshold, signal_threshold=signal_threshold,
    )


def fuse_regime_filter(
    options_signal: Sequence[float],
    orderflow_signal: Sequence[float],
    toxicity: Sequence[float],
    *,
    toxicity_threshold: float = DEFAULT_TOXICITY_THRESHOLD,
    signal_threshold: float = DEFAULT_SIGNAL_THRESHOLD,
) -> List[int]:
    """Rule (b): options sign as causal regime gate x orderflow direction.

    regime = sign(options) when |options|>threshold else 0; direction =
    sign(orderflow) when |orderflow|>threshold else 0; position = regime*direction.
    Generalises EVAL-31 Rule A (asymmetric options<0 gate) to a symmetric
    product of thresholded signs. Toxicity gate forces flat.
    """
    n = min(len(options_signal), len(orderflow_signal))
    out: List[int] = []
    for i in range(n):
        if i < len(toxicity) and _finite(toxicity[i]) >= float(toxicity_threshold):
            out.append(0)
            continue
        o = _finite(options_signal[i]) if i < len(options_signal) else 0.0
        f = _finite(orderflow_signal[i]) if i < len(orderflow_signal) else 0.0
        regime = 1 if o > float(signal_threshold) else (-1 if o < -float(signal_threshold) else 0)
        direction = 1 if f > float(signal_threshold) else (-1 if f < -float(signal_threshold) else 0)
        out.append(int(regime * direction))
    return out


def _expanding_zscore(xs: Sequence[float], min_periods: int = Z_MIN_PERIODS) -> List[float]:
    """Causal expanding z-score (uses only past+current values)."""
    out: List[float] = []
    s = 0.0
    s2 = 0.0
    n = 0
    for x in xs:
        v = _finite(x)
        n += 1
        s += v
        s2 += v * v
        if n < max(1, int(min_periods)):
            out.append(0.0)
            continue
        mean = s / n
        var = s2 / n - mean * mean
        std = math.sqrt(max(var, 0.0))
        out.append((v - mean) / std if std > 1e-12 else 0.0)
    return out


def fuse_continuous_zscore(
    options_signal: Sequence[float],
    orderflow_signal: Sequence[float],
    toxicity: Sequence[float],
    *,
    toxicity_threshold: float = DEFAULT_TOXICITY_THRESHOLD,
    z_threshold: float = Z_THRESHOLD,
    min_periods: int = Z_MIN_PERIODS,
    signal_threshold: float = DEFAULT_SIGNAL_THRESHOLD,
) -> List[int]:
    """Rule (c): causal expanding z-score of each pillar, summed, thresholded.

    ``signal_threshold`` is accepted for a uniform fusion signature but unused
    (the continuous rule thresholds in z-score units, not raw-signal units).
    """
    z_opt = _expanding_zscore(options_signal, min_periods=min_periods)
    z_of = _expanding_zscore(orderflow_signal, min_periods=min_periods)
    n = min(len(z_opt), len(z_of))
    out: List[int] = []
    for i in range(n):
        if i < len(toxicity) and _finite(toxicity[i]) >= float(toxicity_threshold):
            out.append(0)
            continue
        cz = z_opt[i] + z_of[i]
        if cz > float(z_threshold):
            out.append(1)
        elif cz < -float(z_threshold):
            out.append(-1)
        else:
            out.append(0)
    return out


FUSION_FUNCS = {
    "sign_agreement": fuse_sign_agreement,
    "regime_filter": fuse_regime_filter,
    "continuous_zscore": fuse_continuous_zscore,
}


# ---------------------------------------------------------------------------
# Tape preparation (fast signal/toxicity + options alignment)
# ---------------------------------------------------------------------------


def _options_manifest_sha256(options_dir: str) -> Dict[str, Any]:
    d = Path(options_dir)
    files = sorted(p for p in d.glob("*.json") if p.is_file())
    h = hashlib.sha256()
    for p in files:
        h.update(p.name.encode("utf-8"))
        h.update(p.read_bytes())
    return {
        "options_dir": options_dir,
        "n_snapshots": len(files),
        "manifest_sha256": h.hexdigest(),
    }


def prepare_tape(
    name: str,
    tape_path: str,
    options_signals: Sequence[Any],
    *,
    symbol: str = "BTC",
    max_trades: Optional[int] = None,
) -> Dict[str, Any]:
    """Load one real tape, build bars, fast causal signal/toxicity, align options."""
    snapshot = load_real_orderflow(str(symbol), orderflow_path=tape_path)
    trades = snapshot.trades or []
    if max_trades is not None and len(trades) > int(max_trades):
        snapshot = snapshot.model_copy(update={"trades": trades[-int(max_trades):]})
    bars = _build_bars(snapshot, bar_duration_seconds=DEFAULT_BAR_DURATION_SECONDS)
    bar_ends = list(bars["bar_ends_dt"])
    prices = [float(v) for v in bars["bar_closes"]]
    engine = OrderflowAlphaEngine(seed=SEED)
    of_sig = _fast_causal_signal(
        snapshot, bar_ends, DEFAULT_SIGNAL_LOOKBACK_SECONDS, engine
    )
    tox = _fast_toxicity(snapshot, bar_ends, DEFAULT_TOXICITY_WINDOW_TRADES)
    aligned = align_options_signal_to_bars(options_signals, bar_ends)
    opt_sig = [float(v) for v in aligned["signals"]]
    path = Path(tape_path)
    return {
        "name": name,
        "tape_path": tape_path,
        "sha256": _sha256(path),
        "n_trades": int(len(snapshot.trades or [])),
        "n_bars": int(bars["n_bars"]),
        "n_flat_bars": int(aligned.get("n_flat_bars", 0)),
        "n_snapshots_used": int(aligned.get("n_snapshots_used", 0)),
        "first_trade_utc": bars["start_timestamp"],
        "last_trade_utc": bars["end_timestamp"],
        "bar_ends": bar_ends,
        "prices": prices,
        "opt_signal": opt_sig,
        "of_signal": of_sig,
        "toxicities": tox,
    }


# ---------------------------------------------------------------------------
# Per-tape measurement
# ---------------------------------------------------------------------------


def _wf_brief(wf: Dict[str, Any]) -> Dict[str, Any]:
    keys = (
        "oos_sharpe", "oos_return", "oos_max_drawdown", "oos_ann_vol",
        "num_trades", "total_cost_usd", "num_windows",
    )
    return {k: wf.get(k) for k in keys}


def evaluate_tape(
    prepared: Dict[str, Any],
    cfg: IntegratedConfig,
    sizer: CapacityAwareSizer,
    *,
    symbol: str = "BTC",
) -> Dict[str, Any]:
    """Run the pre-declared fused protocol on one prepared tape."""
    prices = prepared["prices"]
    timestamps = prepared["bar_ends"]
    opt_sig = prepared["opt_signal"]
    of_sig = prepared["of_signal"]
    tox = prepared["toxicities"]
    n = len(prices)

    legs: Dict[str, List[int]] = {
        "options_only": _gated_positions(opt_sig, tox),
        "orderflow_only": _gated_positions(of_sig, tox),
        "flat": [0] * n,
    }
    for rule in FUSION_RULES:
        legs[f"combined_{rule}"] = FUSION_FUNCS[rule](
            opt_sig, of_sig, tox,
            toxicity_threshold=DEFAULT_TOXICITY_THRESHOLD,
            signal_threshold=DEFAULT_SIGNAL_THRESHOLD,
        )

    wf_args = dict(
        symbol=str(symbol), sizer=sizer, cfg=cfg, n_points=DEFAULT_N_POINTS,
        seed=SEED, max_position_pct=DEFAULT_MAX_POSITION_PCT,
    )
    wf_results: Dict[str, Dict[str, Any]] = {}
    for leg_name, positions in legs.items():
        wf_results[leg_name] = _run_walkforward(
            positions=positions, prices=prices, timestamps=timestamps, **wf_args
        )

    rule_results: List[Dict[str, Any]] = []
    for rule in FUSION_RULES:
        combined_wf = wf_results[f"combined_{rule}"]
        combined_rets = [float(r) for r in combined_wf.get("window_returns", [])]
        opt_wf = wf_results["options_only"]
        of_wf = wf_results["orderflow_only"]
        opt_sh = _finite(opt_wf.get("oos_sharpe"))
        of_sh = _finite(of_wf.get("oos_sharpe"))
        if opt_sh >= of_sh:
            best_control = "options_only"
            best_rets = [float(r) for r in opt_wf.get("window_returns", [])]
        else:
            best_control = "orderflow_only"
            best_rets = [float(r) for r in of_wf.get("window_returns", [])]
        best_sh = max(opt_sh, of_sh)

        perm_p = 1.0
        if combined_rets and best_rets and len(combined_rets) == len(best_rets):
            try:
                perm = permutation_test(
                    combined_rets, best_rets, statistic=_mean,
                    n_permutations=PERMUTATION_PERMS, paired=True, seed=SEED,
                )
                perm_p = float(perm.get("p_value", 1.0))
            except Exception:
                perm_p = 1.0

        try:
            boot = block_bootstrap_ci(
                combined_rets, statistic=_sharpe_of_returns,
                n_bootstrap=BOOTSTRAP_RESAMPLES, block_size=BOOTSTRAP_BLOCK, seed=SEED,
            )
            boot_ci = [float(boot[0]), float(boot[1]), float(boot[2])]
        except Exception:
            boot_ci = [0.0, 0.0, 0.0]

        try:
            dsr = float(_dsr_of_returns(combined_rets, sr_benchmark=0.0))
        except Exception:
            dsr = 0.0

        rule_results.append({
            "rule": rule,
            "combined": _wf_brief(combined_wf),
            "combined_window_returns": combined_rets,
            "best_control": best_control,
            "best_control_sharpe": float(best_sh),
            "permutation_p": float(perm_p),
            "bootstrap_ci": boot_ci,
            "dsr": float(dsr),
            "kill_switch_breach": kill_switch_breach(combined_wf.get("oos_max_drawdown", 0.0)),
            "n_nonzero_positions": int(sum(1 for p in legs[f"combined_{rule}"] if p != 0)),
        })

    # per-tape PBO across all legs (combined rules + controls)
    try:
        pbo = _cscv_pbo(
            {leg: [float(r) for r in wf_results[leg].get("window_returns", [])] for leg in wf_results},
            n_combinations=PBO_N_COMBINATIONS, k_folds=PBO_K_FOLDS, seed=SEED,
        )
    except Exception:
        pbo = {"overall_pbo": 0.0, "note": "pbo failed"}

    return {
        "name": prepared["name"],
        "tape_path": prepared["tape_path"],
        "sha256": prepared["sha256"],
        "n_trades": prepared["n_trades"],
        "n_bars": prepared["n_bars"],
        "n_flat_bars": prepared["n_flat_bars"],
        "n_snapshots_used": prepared["n_snapshots_used"],
        "first_trade_utc": prepared["first_trade_utc"],
        "last_trade_utc": prepared["last_trade_utc"],
        "rule_results": rule_results,
        "control_results": {
            leg: _wf_brief(wf_results[leg])
            for leg in ("options_only", "orderflow_only", "flat")
        },
        "pbo": pbo,
    }


# ---------------------------------------------------------------------------
# Verdict + report
# ---------------------------------------------------------------------------


def pooled_verdict(tape_results: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Apply the pre-declared pooled GO bar to per-tape rule results (pure)."""
    rules = list(FUSION_RULES)
    n_tapes = len(tape_results)
    go_rule: Optional[str] = None
    rule_audit: Dict[str, Any] = {}
    for rule in rules:
        per_tape = [
            (t["name"], rr)
            for t in tape_results
            for rr in t.get("rule_results", [])
            if rr["rule"] == rule
        ]
        passes = []
        for tname, rr in per_tape:
            c = rr["combined"]
            ok = (
                _finite(c.get("oos_sharpe")) > 0.0
                and not bool(rr.get("kill_switch_breach"))
                and _finite(rr.get("permutation_p"), 1.0) < 0.05
                and _finite(rr.get("bootstrap_ci", [0, 0, 0])[1]) > 0.0
            )
            passes.append({"tape": tname, "pass": bool(ok), "oos_sharpe": c.get("oos_sharpe"),
                           "permutation_p": rr.get("permutation_p"),
                           "ci_lower": rr.get("bootstrap_ci", [0, 0, 0])[1],
                           "kill_switch_breach": rr.get("kill_switch_breach")})
        all_pass = bool(per_tape) and len(per_tape) == n_tapes and all(p["pass"] for p in passes)
        rule_audit[rule] = {"per_tape": passes, "all_tapes_pass": bool(all_pass)}
        if all_pass and go_rule is None:
            go_rule = rule
    passed = go_rule is not None
    if passed:
        verdict = "FALSIFIED (GO)"
        reason = (
            f"fusion rule '{go_rule}' shows combined net-of-cost Sharpe > 0, no kill-switch "
            f"breach, permutation p < 0.05 and bootstrap CI lower > 0 on both real BTC tapes "
            f"-> the combined thesis is net-of-cost tradable; requires a sealed out-of-sample "
            f"replication campaign on new real data before any production GO."
        )
    else:
        verdict = "NO-GO CONFIRMED (PASS)"
        reason = (
            f"no fusion rule passed the pre-declared GO bar on both real BTC tapes "
            f"(need combined Sharpe > 0, no kill-switch breach, permutation p < 0.05 and "
            f"bootstrap CI lower > 0 on both) -> the combined options+orderflow thesis is "
            f"NOT net-of-cost tradable on the available real BTC data."
        )
    return {
        "n_tapes": int(n_tapes),
        "go_rule": go_rule,
        "rule_audit": rule_audit,
        "passed": bool(passed),
        "verdict": verdict,
        "verdict_reason": reason,
    }


def build_protocol() -> Dict[str, Any]:
    return {
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
        "fusion_rules": list(FUSION_RULES),
        "z_threshold": float(Z_THRESHOLD),
        "z_min_periods": int(Z_MIN_PERIODS),
        "cost_model_bps_nav_per_window": 2.0,
        "guardrail_bps": 0.5,
        "kill_switch_max_drawdown": float(KILL_SWITCH_MAX_DD),
        "permutation_perms": int(PERMUTATION_PERMS),
        "bootstrap_resamples": int(BOOTSTRAP_RESAMPLES),
        "bootstrap_block": int(BOOTSTRAP_BLOCK),
        "pbo_k_folds": int(PBO_K_FOLDS),
        "pbo_n_combinations": int(PBO_N_COMBINATIONS),
        "fdr_alpha": float(FDR_ALPHA),
        "seed": int(SEED),
        "go_bar": (
            "GO only if, across both real BTC tapes, at least one fusion rule shows combined "
            "net-of-cost Sharpe > 0, no kill-switch breach (max-DD <= 0.20), permutation "
            "p < 0.05 and bootstrap 95% CI lower > 0; otherwise NO-GO CONFIRMED (PASS)."
        ),
    }


def build_prereg(
    *,
    generated_at: str,
    options_meta: Dict[str, Any],
    tape_meta: Dict[str, Any],
    protocol: Dict[str, Any],
    task_id: str,
) -> Dict[str, Any]:
    return {
        "report_id": PREREG_ID,
        "generated_at": generated_at,
        "task_id": task_id,
        "status": "PREREGISTERED",
        "hypothesis": (
            "The fused options+orderflow strategy is net-of-cost tradable on dense real BTC "
            "data: at least one pre-declared fusion rule yields combined Sharpe > 0 with no "
            "kill-switch breach, permutation p < 0.05 and bootstrap CI lower > 0 on both tapes."
        ),
        "options_dataset": options_meta,
        "tapes": tape_meta,
        "protocol": protocol,
        "fusion_rules_detail": {
            "sign_agreement": "both pillars agree in sign (_fuse_positions), toxicity gate",
            "regime_filter": "options sign as causal regime gate x orderflow direction (product of thresholded signs), toxicity gate",
            "continuous_zscore": "causal expanding z-score of each pillar, summed, thresholded at z_threshold, toxicity gate",
        },
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def _build_report(
    *,
    generated_at: str,
    tape_results: List[Dict[str, Any]],
    options_meta: Dict[str, Any],
    tape_meta: Dict[str, Any],
    protocol: Dict[str, Any],
    task_label: str,
) -> Dict[str, Any]:
    pooled = pooled_verdict(tape_results)
    p_values = {
        f"{t['name']}::{rr['rule']}": float(rr.get("permutation_p", 1.0))
        for t in tape_results
        for rr in t.get("rule_results", [])
    }
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}
    # pooled PBO across all tape x leg configs
    pooled_returns: Dict[str, List[float]] = {}
    for t in tape_results:
        for rr in t.get("rule_results", []):
            pooled_returns[f"{t['name']}::combined_{rr['rule']}"] = [
                float(r) for r in rr.get("combined_window_returns", [])
            ]
    try:
        pooled_pbo = _cscv_pbo(
            pooled_returns, n_combinations=PBO_N_COMBINATIONS, k_folds=PBO_K_FOLDS, seed=SEED
        ) if len(pooled_returns) >= 2 else {"overall_pbo": 0.0, "note": "insufficient configs"}
    except Exception:
        pooled_pbo = {"overall_pbo": 0.0, "note": "pbo failed"}
    return {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task_id": f"INIT-{generated_at}-{task_label}",
        "campaign_state": "TERMINATED (EVAL-36 TERMINATE_NO_GO); EVAL-37 PASS 9/9",
        "verdict": pooled["verdict"],
        "verdict_reason": pooled["verdict_reason"],
        "verdict_scope": "FULL_DENSE_BTC",
        "options_dataset": options_meta,
        "tapes": tape_meta,
        "protocol": protocol,
        "tape_results": tape_results,
        "pooled": pooled,
        "pooled_pbo": pooled_pbo,
        "bh_fdr": bh,
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def build_prereg_md(p: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# {p['report_id']} — pre-registration (EVAL-46 integrated options+orderflow)")
    lines.append("")
    lines.append(f"- **Report ID:** `{p['report_id']}`")
    lines.append(f"- **Generated:** {p['generated_at']}")
    lines.append(f"- **Task ID:** `{p['task_id']}`")
    lines.append(f"- **Status:** {p['status']}")
    lines.append("")
    lines.append("## Hypothesis")
    lines.append(p["hypothesis"])
    lines.append("")
    lines.append("## Options dataset")
    od = p["options_dataset"]
    lines.append(f"- snapshots: {od['n_snapshots']}; distinct levels: {od['n_distinct_levels']}")
    lines.append(f"- span: {od.get('first_snapshot_utc')} → {od.get('last_snapshot_utc')}")
    lines.append(f"- manifest sha256: `{od['manifest_sha256']}`")
    lines.append("")
    lines.append("## Orderflow tapes")
    for name, meta in p["tapes"].items():
        lines.append(f"- `{name}`: `{meta['path']}` — {meta['n_trades']} trades, {meta['n_bars']} bars, sha256 `{meta['sha256'][:16]}…`")
    lines.append("")
    lines.append("## Protocol")
    for k, v in p["protocol"].items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Fusion rules")
    for k, v in p["fusion_rules_detail"].items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    lines.append("## Commands")
    for cmd in p["commands"]:
        lines.append(f"```bash\n{cmd}\n```")
    return "\n".join(lines)


def build_md(r: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# {r['report_id']} — integrated options+orderflow net-of-cost falsification")
    lines.append("")
    lines.append(f"- **Report ID:** `{r['report_id']}`")
    lines.append(f"- **Generated:** {r['generated_at']}")
    lines.append(f"- **Task ID:** `{r['task_id']}`")
    lines.append(f"- **Verdict:** **{r['verdict']}**")
    lines.append(f"- **Scope:** {r['verdict_scope']}")
    lines.append(f"- **Reason:** {r['verdict_reason']}")
    lines.append("")
    lines.append("## Inputs")
    lines.append(f"- Options: {r['options_dataset']['n_snapshots']} snapshots, manifest sha256 `{r['options_dataset']['manifest_sha256'][:16]}…`")
    for name, meta in r["tapes"].items():
        lines.append(f"- tape `{name}`: `{meta['path']}` — {meta['n_trades']} trades, {meta['n_bars']} bars, sha256 `{meta['sha256'][:16]}…`")
    lines.append("")
    lines.append("## Per-tape fused results")
    lines.append("| tape | rule | combined Sharpe | max-DD | trades | cost $ | perm p | CI | kill-switch | nonzero |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for t in r["tape_results"]:
        for rr in t["rule_results"]:
            c = rr["combined"]
            ci = rr.get("bootstrap_ci", [0.0, 0.0, 0.0])
            lines.append(
                f"| {t['name']} | {rr['rule']} | {c.get('oos_sharpe'):.4f} | "
                f"{c.get('oos_max_drawdown'):.4f} | {c.get('num_trades')} | "
                f"{c.get('total_cost_usd'):.2f} | {rr['permutation_p']:.4f} | "
                f"[{ci[1]:.4f},{ci[2]:.4f}] | {rr['kill_switch_breach']} | "
                f"{rr['n_nonzero_positions']} |"
            )
    lines.append("")
    lines.append("## Controls (per tape)")
    lines.append("| tape | options-only Sharpe | orderflow-only Sharpe | flat Sharpe |")
    lines.append("|---|---|---|---|")
    for t in r["tape_results"]:
        cr = t["control_results"]
        lines.append(
            f"| {t['name']} | {cr['options_only'].get('oos_sharpe'):.4f} | "
            f"{cr['orderflow_only'].get('oos_sharpe'):.4f} | {cr['flat'].get('oos_sharpe'):.4f} |"
        )
    lines.append("")
    lines.append("## Pooled verdict")
    p = r["pooled"]
    lines.append(f"- GO rule: {p['go_rule']}")
    for rule, audit in p["rule_audit"].items():
        lines.append(f"- rule `{rule}` all-tapes-pass: {audit['all_tapes_pass']}")
        for pt in audit["per_tape"]:
            lines.append(f"    - {pt['tape']}: pass={pt['pass']} Sharpe={pt['oos_sharpe']:.4f} p={pt['permutation_p']:.4f} CI_low={pt['ci_lower']:.4f}")
    lines.append(f"- Passed: {p['passed']}")
    lines.append(f"- BH-FDR: {json.dumps(r['bh_fdr'], sort_keys=True)}")
    lines.append(f"- Pooled PBO: {json.dumps(r['pooled_pbo'], sort_keys=True)}")
    lines.append("")
    lines.append("## Commands")
    for cmd in r["commands"]:
        lines.append(f"```bash\n{cmd}\n```")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Sealing
# ---------------------------------------------------------------------------


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    serialized = serialize_metrics_strict(payload)
    assert_json_valid(serialized)
    path.write_text(json.dumps(serialized, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _seal(report_id: str, report: Dict[str, Any], md_builder=None) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _stamp_for_filename(report["generated_at"])
    jpath = OUT_DIR / f"{report_id}_{stamp}.json"
    mpath = OUT_DIR / f"{report_id}_{stamp}.md"
    _write_json(jpath, report)
    builder = md_builder or build_md
    mpath.write_text(builder(report) + "\n", encoding="utf-8")
    return {"json": str(jpath), "md": str(mpath)}


def _build_blocked_report(generated_at: str, exc: BaseException, task_label: str) -> Dict[str, Any]:
    return {
        "report_id": BLOCKED_ID,
        "generated_at": generated_at,
        "task_id": f"INIT-{generated_at}-{task_label}",
        "status": "BLOCKED",
        "verdict": "BLOCKED",
        "verdict_reason": "EVAL-46 could not complete; see error.",
        "error_type": type(exc).__name__,
        "error": str(exc),
        "traceback": traceback.format_exc(),
        "commands": list(COMMANDS),
    }


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def run_eval46(
    write: bool = True,
    *,
    tape_overrides: Optional[Dict[str, str]] = None,
    max_trades: Optional[int] = None,
    symbol: str = "BTC",
    task_label: str = "EVAL-46-INTEGRATED-OPTIONS-ORDERFLOW-NET-OF-COST-FALSIFY-AND-SEAL",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    declared = dict(TAPES)
    for name, path in (tape_overrides or {}).items():
        if path:
            declared[name] = str(path)

    # Resolve + load options once.
    if not Path(OPTIONS_DIR).is_dir():
        raise SystemExit(f"options dir missing: {OPTIONS_DIR}")
    options_signals = load_snapshot_signals(str(symbol), OPTIONS_DIR)
    options_meta = _options_manifest_sha256(OPTIONS_DIR)
    options_meta["first_snapshot_utc"] = min(
        (s.snapshot_timestamp for s in options_signals), default=None
    )
    options_meta["last_snapshot_utc"] = max(
        (s.snapshot_timestamp for s in options_signals), default=None
    )
    options_meta["n_distinct_levels"] = len({round(float(s.options_signal_raw), 6) for s in options_signals})

    # Prepare each tape (fast signal/toxicity + align).
    tape_meta: Dict[str, Any] = {}
    prepared_list: List[Dict[str, Any]] = []
    for name in declared:
        path = declared[name]
        if not Path(path).is_file():
            continue
        prepared = prepare_tape(
            name, path, options_signals, symbol=symbol, max_trades=max_trades
        )
        prepared_list.append(prepared)
        tape_meta[name] = {
            "path": path,
            "sha256": prepared["sha256"],
            "n_trades": prepared["n_trades"],
            "n_bars": prepared["n_bars"],
            "n_flat_bars": prepared["n_flat_bars"],
            "n_snapshots_used": prepared["n_snapshots_used"],
            "first_trade_utc": prepared["first_trade_utc"],
            "last_trade_utc": prepared["last_trade_utc"],
        }
    if not prepared_list:
        raise SystemExit("no tapes resolved on disk")

    protocol = build_protocol()
    task_id = f"INIT-{generated_at}-{task_label}"

    # 1) Seal preregistration BEFORE measurement.
    prereg = build_prereg(
        generated_at=generated_at,
        options_meta=options_meta,
        tape_meta=tape_meta,
        protocol=protocol,
        task_id=task_id,
    )
    prereg_paths: Dict[str, str] = {}
    if write:
        prereg_paths = _seal(PREREG_ID, prereg, md_builder=build_prereg_md)
        prereg["artifact_paths"] = prereg_paths
        _write_json(Path(prereg_paths["json"]), prereg)

    # 2) Measurement.
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
    for prepared in prepared_list:
        try:
            tape_results.append(
                evaluate_tape(prepared=prepared, cfg=cfg, sizer=sizer, symbol=symbol)
            )
        except Exception as exc:  # noqa: BLE001 - record and continue (partial)
            errors.append({"tape": prepared["name"], "error_type": type(exc).__name__, "error": str(exc)})

    report = _build_report(
        generated_at=generated_at,
        tape_results=tape_results,
        options_meta=options_meta,
        tape_meta=tape_meta,
        protocol=protocol,
        task_label=task_label,
    )
    report["tape_errors"] = errors
    report["preregistration_artifact"] = prereg_paths.get("json") if prereg_paths else None
    assert _all_finite(report), "non-finite values in report"

    artifact_paths: Dict[str, str] = {}
    if write:
        artifact_paths = _seal(REPORT_ID, report)
        report["artifact_paths"] = artifact_paths
        _write_json(Path(artifact_paths["json"]), report)
    else:
        report["artifact_paths"] = artifact_paths
    return report


def main(argv: Any = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--max-trades", type=int, default=None,
                    help="truncate each tape to the last N trades (smoke test only)")
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
    task_label = "EVAL-46-INTEGRATED-OPTIONS-ORDERFLOW-NET-OF-COST-FALSIFY-AND-SEAL"
    try:
        report = run_eval46(
            write=not args.no_write,
            tape_overrides=overrides or None,
            max_trades=args.max_trades,
            task_label=task_label,
        )
    except Exception as exc:  # noqa: BLE001 - seal a BLOCKED artifact, never silent
        traceback.print_exc()
        paths = {}
        if not args.no_write:
            paths = _seal(
                BLOCKED_ID,
                _build_blocked_report(generated_at, exc, task_label),
            )
        print(json.dumps({
            "report_id": BLOCKED_ID,
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
        "go_rule": report["pooled"]["go_rule"],
        "passed": report["pooled"]["passed"],
        "tape_errors": report.get("tape_errors", []),
        "artifact_paths": report.get("artifact_paths", {}),
        "preregistration_artifact": report.get("preregistration_artifact"),
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