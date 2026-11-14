#!/usr/bin/env python3
"""EVAL-35: Orderflow-only second independent real data window validation (paper-only).

Validates the orderflow-only pillar on a second ~6.5h OKX BTC-USD-SWAP tape
(not previously used in EVAL-23..34) under net-of-cost accounting with:
  - toxicity gate VPIN >= 0.70 -> flat
  - capacity-aware sizing: spread 2 bps, impact 0.01, max participation 12.5%, cost budget 0.5 bps

Success criterion: orderflow-only non-degenerate (Sharpe > 1.0, trades > 0, cost > 0)
and within the EVAL-34 held-out band (Sharpe ~4.8115, ~129 trades, ~$157 cost).

Portfolio certification decision (one of two pre-declared options):
  - CERTIFY_DEPLOY_PAPER_ONLY: second window confirms orderflow-only tradable
  - TERMINATE_NO_GO: second window fails to replicate (Sharpe <= 1.0, 0 trades, adverse IC)

Seals research_state/ORDERFLOW_ONLY_SECOND_WINDOW_VALIDATION_35_<UTC>.{json,md}.
Never emits {"valid": true}. Never falls back to synthetic data.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analytics.capacity_aware_tca import CapacityAwareSizer
from src.analytics.integrated_options_orderflow_evaluation import (
    _build_bars,
    _causal_signal_series,
    _run_walkforward,
    _toxicities_per_bar,
    DEFAULT_BAR_DURATION_SECONDS,
    DEFAULT_EMBARGO,
    DEFAULT_MAX_POSITION_PCT,
    DEFAULT_PURGE,
    DEFAULT_SIGNAL_LOOKBACK_SECONDS,
    DEFAULT_STEP_SIZE,
    DEFAULT_TEST_WINDOW,
    DEFAULT_TRAIN_WINDOW,
    IntegratedConfig,
    compute_toxicity_metrics,
)
from src.analytics.strategy_evaluation import compute_metrics
from src.alpha.orderflow_alpha import OrderflowAlphaEngine
from src.backtest.engine import BacktestConfig, BacktestEngine, RiskConfig, WalkForwardBacktest
from src.campaign.integrated import RealDataUnavailable, _discover_real_orderflow_exports
from src.data.loader import DataLoader
from src.data.schemas import OrderflowSnapshot, Trade
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

REPORT_ID = "ORDERFLOW_ONLY_SECOND_WINDOW_VALIDATION_35"
OUT_DIR = Path("research_state")
TAPE_PATH = Path("data/raw/orderflow_okx_BTC-USD-SWAP_20261114T080515Z.json")

TRADING_MODE = "paper"
LIVE_TRADING_ENABLED = False

# EVAL-35 parameters (pre-declared, not fitted)
BAR_DURATION_SECONDS = 15.0
SIGNAL_LOOKBACK_SECONDS = 60.0
TOXICITY_WINDOW_TRADES = 5
TOXICITY_THRESHOLD = 0.70
SIGNAL_THRESHOLD = 0.1
SPREAD_BPS = 2.0
IMPACT_COEFF = 0.01
MAX_PARTICIPATION = 0.125
COST_BUDGET_BPS = 0.5
MAX_POSITION_PCT = 0.20
INITIAL_CAPITAL = 100000.0
SEED = 42

# Kill-switch thresholds (paper-only, per EVAL-34 caveats / EVAL-35 spec)
KILL_SWITCH_MAX_DD_PCT = 0.20
KILL_SWITCH_TOXICITY_PCT = 0.80
KILL_SWITCH_COST_BPS = 5.0
MAX_NOTIONAL_USD = 1_000_000.0
MAX_DAILY_LOSS_USD = 50_000.0

# EVAL-34 held-out reference band (sealed EVAL-32/EVAL-33/EVAL-34)
EVAL34_ORDERFLOW_ONLY_SHARPE = 4.811462185754629
EVAL34_ORDERFLOW_ONLY_TRADES = 129
EVAL34_ORDERFLOW_ONLY_COST_USD = 157.0180100586245

# Non-degenerate success thresholds
MIN_SHARPE = 1.0


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _stamp_for_filename(iso_ts: str) -> str:
    try:
        ts = iso_ts.replace(":", "").replace("-", "").replace("T", "").replace("Z", "").split(".")[0]
    except Exception:
        return ""
    return f"{ts[:8]}T{ts[8:14]}Z" if len(ts) >= 14 else ""


def _finite(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    return v if math.isfinite(v) else default


def _all_finite_numbers(obj: Any) -> bool:
    if isinstance(obj, bool):
        return True
    if isinstance(obj, (int, float)):
        return math.isfinite(float(obj))
    if isinstance(obj, dict):
        return all(_all_finite_numbers(v) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return all(_all_finite_numbers(v) for v in obj)
    return True


def _signal_positions(signals: Sequence[float], threshold: float = SIGNAL_THRESHOLD) -> List[int]:
    thr = float(threshold)
    positions: List[int] = []
    for s in signals:
        s = float(s)
        if s > thr:
            positions.append(1)
        elif s < -thr:
            positions.append(-1)
        else:
            positions.append(0)
    return positions


def _load_new_tape(path: Path = TAPE_PATH) -> OrderflowSnapshot:
    """Load the new independent real tape via the real loader (no synthetic fallback)."""
    loader = DataLoader(cache=False)
    if not path.exists():
        raise RealDataUnavailable(f"new EVAL-35 tape not found: {path}")
    snap = loader.load_orderflow(str(path), venue="okx", symbol="BTC")
    if not snap.trades:
        raise RealDataUnavailable(f"new EVAL-35 tape has no trades: {path}")
    return snap


def _run_orderflow_only_walkforward(
    symbol: str,
    prices: Sequence[float],
    positions: Sequence[int],
    timestamps: Sequence[datetime],
    sizer: CapacityAwareSizer,
    seed: int,
) -> Dict[str, Any]:
    """OOS walk-forward of the orderflow-only signal with capacity-aware costs."""
    cfg = IntegratedConfig(
        seed=seed,
        n_points=500,
        train_window=DEFAULT_TRAIN_WINDOW,
        test_window=DEFAULT_TEST_WINDOW,
        step_size=DEFAULT_STEP_SIZE,
        purge=DEFAULT_PURGE,
        embargo=DEFAULT_EMBARGO,
    )
    return _run_walkforward(
        symbol,
        list(prices),
        list(positions),
        list(timestamps),
        sizer,
        cfg,
        500,
        seed,
        max_position_pct=MAX_POSITION_PCT,
    )


def _kill_switch_triggers(
    max_dd: float,
    cost_usd: float,
    notional_usd: float,
    nav: float,
    toxic_gate_active_fraction: float,
) -> Dict[str, Any]:
    """Evaluate kill-switch triggers (read-only, no state mutation)."""
    triggers: List[str] = []
    dd_breach = bool(max_dd >= KILL_SWITCH_MAX_DD_PCT)
    cost_bps = (cost_usd / max(nav, 1.0)) * 1e4
    cost_breach = bool(cost_bps >= KILL_SWITCH_COST_BPS)
    tox_breach = bool(toxic_gate_active_fraction >= KILL_SWITCH_TOXICITY_PCT)
    notional_breach = bool(notional_usd >= MAX_NOTIONAL_USD)
    if dd_breach:
        triggers.append("max_drawdown")
    if cost_breach:
        triggers.append("cost_bps")
    if tox_breach:
        triggers.append("toxicity")
    if notional_breach:
        triggers.append("max_notional")
    return {
        "max_drawdown": float(max_dd),
        "max_drawdown_threshold": float(KILL_SWITCH_MAX_DD_PCT),
        "max_drawdown_breached": dd_breach,
        "cost_bps": float(cost_bps),
        "cost_bps_threshold": float(KILL_SWITCH_COST_BPS),
        "cost_bps_breached": cost_breach,
        "toxic_gate_active_fraction": float(toxic_gate_active_fraction),
        "toxicity_threshold": float(KILL_SWITCH_TOXICITY_PCT),
        "toxicity_breached": tox_breach,
        "total_notional_usd": float(notional_usd),
        "max_notional_usd": float(MAX_NOTIONAL_USD),
        "notional_breached": notional_breach,
        "triggers": triggers,
        "any_breach": bool(len(triggers) > 0),
    }


def build_report() -> Dict[str, Any]:
    generated_at = _utc_now_iso()

    # --- 1. Load the new independent real tape (no synthetic fallback) ---
    snapshot = _load_new_tape()
    symbol = str(snapshot.symbol)
    venue = str(snapshot.venue)
    n_trades_total = int(len(snapshot.trades or []))

    # --- 2. Build causal bars (15s) from the orderflow tape ---
    bars = _build_bars(snapshot, bar_duration_seconds=BAR_DURATION_SECONDS)
    n_bars = int(bars["n_bars"])
    bar_ends_dt: List[datetime] = bars["bar_ends_dt"]
    bar_closes = [float(p) for p in bars["bar_closes"]]
    bar_start = str(bars["start_timestamp"])
    bar_end = str(bars["end_timestamp"])
    span_seconds = (bars["end_timestamp_dt"] if "end_timestamp_dt" in bars else None)

    # --- 3. Causal orderflow signal via OrderflowAlphaEngine (net_aggression) ---
    engine = OrderflowAlphaEngine(seed=SEED)
    of_series = _causal_signal_series(
        snapshot, bar_ends_dt, bar_closes,
        lookback_seconds=SIGNAL_LOOKBACK_SECONDS, engine=engine,
    )
    orderflow_signal = [float(s) for s in of_series["signals"]]

    # --- 4. VPIN toxicity per bar (causal) ---
    toxicities = _toxicities_per_bar(snapshot, bar_ends_dt, window_trades=TOXICITY_WINDOW_TRADES)
    toxicity = compute_toxicity_metrics(toxicities, threshold=TOXICITY_THRESHOLD)

    # --- 5. Apply toxicity gate VPIN >= 0.70 -> flat to orderflow-only positions ---
    orderflow_only_positions = _signal_positions(orderflow_signal, threshold=SIGNAL_THRESHOLD)
    orderflow_only_gated = [
        0 if float(toxicities[i]) >= TOXICITY_THRESHOLD else orderflow_only_positions[i]
        for i in range(len(orderflow_only_positions))
    ]

    # --- 6. Capacity-aware sizing: spread 2bps, impact 0.01, max participation 12.5%, cost budget 0.5bps ---
    sizer = CapacityAwareSizer(
        spread_bps=SPREAD_BPS,
        impact_coeff=IMPACT_COEFF,
        max_participation=MAX_PARTICIPATION,
        cost_budget_bps=COST_BUDGET_BPS,
        seed=SEED,
    )

    # --- 7. Net-of-cost orderflow-only walk-forward ---
    wf = _run_orderflow_only_walkforward(
        "BTC", bar_closes, orderflow_only_gated, bar_ends_dt, sizer, SEED,
    )

    oos_sharpe = float(wf["oos_sharpe"])
    oos_return = float(wf["oos_return"])
    oos_max_dd = float(wf["oos_max_drawdown"])
    oos_ann_vol = float(wf["oos_ann_vol"])
    total_cost_usd = float(wf["total_cost_usd"])
    total_notional = float(wf["total_traded_notional"])
    num_trades = int(wf["num_trades"])
    num_windows = int(wf["num_windows"])
    equity_curve = [float(v) for v in wf.get("oos_equity_curve", [])]

    # --- 8. Kill-switch triggers ---
    kill_switch = _kill_switch_triggers(
        max_dd=oos_max_dd,
        cost_usd=total_cost_usd,
        notional_usd=total_notional,
        nav=INITIAL_CAPITAL,
        toxic_gate_active_fraction=float(toxicity["toxic_gate_active_fraction"]),
    )

    # --- 9. Non-degenerate success vs EVAL-34 band ---
    sharpe_ok = bool(math.isfinite(oos_sharpe) and oos_sharpe > MIN_SHARPE)
    trades_ok = bool(num_trades > 0)
    cost_ok = bool(math.isfinite(total_cost_usd) and total_cost_usd > 0.0)
    non_degenerate = bool(sharpe_ok and trades_ok and cost_ok)

    within_band_sharpe = bool(
        math.isfinite(oos_sharpe)
        and abs(oos_sharpe - EVAL34_ORDERFLOW_ONLY_SHARPE) <= max(1.0, 0.5 * abs(EVAL34_ORDERFLOW_ONLY_SHARPE))
    )
    within_band_trades = bool(
        num_trades > 0 and abs(num_trades - EVAL34_ORDERFLOW_ONLY_TRADES) <= max(50, 0.5 * EVAL34_ORDERFLOW_ONLY_TRADES)
    )
    within_band_cost = bool(
        math.isfinite(total_cost_usd)
        and abs(total_cost_usd - EVAL34_ORDERFLOW_ONLY_COST_USD) <= max(50.0, 0.5 * EVAL34_ORDERFLOW_ONLY_COST_USD)
    )
    within_band = bool(within_band_sharpe and within_band_trades and within_band_cost)

    # --- 10. Portfolio certification decision (one of two pre-declared options) ---
    if non_degenerate and within_band and not kill_switch["any_breach"]:
        decision = "CERTIFY_DEPLOY_PAPER_ONLY"
        rationale = (
            f"CERTIFY DEPLOY (paper-only). Second independent real window confirms the "
            f"orderflow-only pillar is tradable under net-of-cost accounting: "
            f"Sharpe {oos_sharpe:.4f} (EVAL-34 band ~{EVAL34_ORDERFLOW_ONLY_SHARPE:.4f}), "
            f"{num_trades} trades (EVAL-34 band ~{EVAL34_ORDERFLOW_ONLY_TRADES}), "
            f"${total_cost_usd:.2f} cost (EVAL-34 band ~${EVAL34_ORDERFLOW_ONLY_COST_USD:.2f}), "
            f"max-DD {oos_max_dd:.4f} (kill-switch {KILL_SWITCH_MAX_DD_PCT:.0%}), "
            f"toxicity gate active {float(toxicity['toxic_gate_active_fraction']):.4f} "
            f"(kill-switch {KILL_SWITCH_TOXICITY_PCT:.0%}). No kill-switch breach. "
            f"Proceed to paper-only rollout per EVAL-34 caveats."
        )
    else:
        decision = "TERMINATE_NO_GO"
        reasons: List[str] = []
        if not sharpe_ok:
            reasons.append(f"Sharpe {oos_sharpe:.4f} <= {MIN_SHARPE} or non-finite")
        if not trades_ok:
            reasons.append(f"{num_trades} trades == 0")
        if not cost_ok:
            reasons.append(f"cost ${total_cost_usd:.2f} <= 0 or non-finite")
        if not within_band:
            reasons.append("outside EVAL-34 held-out band")
        if kill_switch["any_breach"]:
            reasons.append(f"kill-switch breach: {', '.join(kill_switch['triggers'])}")
        rationale = (
            f"TERMINATE / NO-GO. Second independent real window failed to replicate the "
            f"orderflow-only pillar: {'; '.join(reasons)}. Measured: Sharpe {oos_sharpe:.4f}, "
            f"{num_trades} trades, ${total_cost_usd:.2f} cost, max-DD {oos_max_dd:.4f}. "
            f"Options+orderflow remains NOT net-of-cost tradable; issue final termination memo (EVAL-36)."
        )

    decision_block = {
        "decision": decision,
        "rationale": rationale,
        "pre_declared_options": ["CERTIFY_DEPLOY_PAPER_ONLY", "TERMINATE_NO_GO"],
        "max_notional_usd": float(MAX_NOTIONAL_USD),
        "max_daily_loss_usd": float(MAX_DAILY_LOSS_USD),
        "max_drawdown_pct": float(KILL_SWITCH_MAX_DD_PCT),
        "toxicity_kill_switch_pct": float(KILL_SWITCH_TOXICITY_PCT),
        "cost_kill_switch_bps": float(KILL_SWITCH_COST_BPS),
        "non_degenerate": non_degenerate,
        "within_eval34_band": within_band,
        "kill_switch_breach": kill_switch["any_breach"],
    }

    # --- 11. Assemble report ---
    config_block = {
        "symbol": symbol,
        "venue": venue,
        "bar_duration_seconds": float(BAR_DURATION_SECONDS),
        "signal_lookback_seconds": float(SIGNAL_LOOKBACK_SECONDS),
        "signal_threshold": float(SIGNAL_THRESHOLD),
        "toxicity_window_trades": int(TOXICITY_WINDOW_TRADES),
        "toxicity_threshold": float(TOXICITY_THRESHOLD),
        "spread_bps": float(SPREAD_BPS),
        "impact_coeff": float(IMPACT_COEFF),
        "max_participation": float(MAX_PARTICIPATION),
        "cost_budget_bps": float(COST_BUDGET_BPS),
        "max_position_pct": float(MAX_POSITION_PCT),
        "initial_capital": float(INITIAL_CAPITAL),
        "seed": int(SEED),
        "train_window": int(DEFAULT_TRAIN_WINDOW),
        "test_window": int(DEFAULT_TEST_WINDOW),
        "step_size": int(DEFAULT_STEP_SIZE),
        "purge": int(DEFAULT_PURGE),
        "embargo": int(DEFAULT_EMBARGO),
        "kill_switch_max_dd_pct": float(KILL_SWITCH_MAX_DD_PCT),
        "kill_switch_toxicity_pct": float(KILL_SWITCH_TOXICITY_PCT),
        "kill_switch_cost_bps": float(KILL_SWITCH_COST_BPS),
        "max_notional_usd": float(MAX_NOTIONAL_USD),
        "max_daily_loss_usd": float(MAX_DAILY_LOSS_USD),
        "min_sharpe": float(MIN_SHARPE),
        "eval34_reference": {
            "sharpe": float(EVAL34_ORDERFLOW_ONLY_SHARPE),
            "trades": int(EVAL34_ORDERFLOW_ONLY_TRADES),
            "cost_usd": float(EVAL34_ORDERFLOW_ONLY_COST_USD),
        },
        "trading_mode": TRADING_MODE,
        "live_trading_enabled": LIVE_TRADING_ENABLED,
    }

    tape_block = {
        "tape_path": str(TAPE_PATH),
        "schema": str(getattr(snapshot, "schema", "okx_public_trades_v1")) if hasattr(snapshot, "schema") else "okx_public_trades_v1",
        "n_trades_total": n_trades_total,
        "n_bars": n_bars,
        "bar_duration_seconds": float(BAR_DURATION_SECONDS),
        "start_timestamp": bar_start,
        "end_timestamp": bar_end,
        "source": "okx_public_history_trades",
        "authenticated": False,
        "public_read_only": True,
        "independent_of_eval_23_to_34": True,
        "previous_window_utc": "2026-11-14T04:05:35Z->10:33:35Z",
    }

    signal_block = {
        "n_bars": int(len(orderflow_signal)),
        "mean_signal": float(sum(orderflow_signal) / len(orderflow_signal)) if orderflow_signal else 0.0,
        "long_bars": int(sum(1 for v in orderflow_only_gated if v == 1)),
        "short_bars": int(sum(1 for v in orderflow_only_gated if v == -1)),
        "flat_bars": int(sum(1 for v in orderflow_only_gated if v == 0)),
        "gated_flat_bars": int(sum(1 for i, v in enumerate(orderflow_only_gated) if v == 0 and orderflow_only_positions[i] != 0)),
    }

    report = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task_id": f"INIT-{generated_at}-EVAL-35-ORDERFLOW-ONLY-SECOND-WINDOW-VALIDATION",
        "trading_mode": TRADING_MODE,
        "live_trading_enabled": LIVE_TRADING_ENABLED,
        "never_valid_true": True,
        "authenticity_verified": False,
        "data_provenance": "real_public_exchange_export",
        "symbol": symbol,
        "venue": venue,
        "provenance_caveats": [
            "Public read-only OKX exports; no signed venue attestation.",
            "Inverse BTC-USD-SWAP orderflow tape.",
            "Paper-only; no live trading; .env absent.",
            "authenticity_verified=false.",
            "Second independent real data window; distinct from EVAL-23..34 span.",
        ],
        "config": config_block,
        "tape": tape_block,
        "signal": signal_block,
        "toxicity": {
            "n_bars": int(toxicity["n_bars"]),
            "mean_toxicity": float(toxicity["mean_toxicity"]),
            "p95_toxicity": float(toxicity["p95_toxicity"]),
            "toxicity_threshold": float(toxicity["toxicity_threshold"]),
            "fraction_above_threshold": float(toxicity["fraction_above_threshold"]),
            "toxic_gate_active_fraction": float(toxicity["toxic_gate_active_fraction"]),
            "gate_engages": bool(toxicity["gate_engages"]),
            "toxicity_measured": bool(toxicity["toxicity_measured"]),
            "min_toxicity": float(toxicity["min_toxicity"]),
            "max_toxicity": float(toxicity["max_toxicity"]),
        },
        "walkforward": {
            "symbol": str(wf.get("symbol", "BTC")),
            "seed": int(wf.get("seed", SEED)),
            "num_windows": num_windows,
            "oos_return": oos_return,
            "oos_sharpe": oos_sharpe,
            "oos_max_drawdown": oos_max_dd,
            "oos_ann_vol": oos_ann_vol,
            "total_cost_usd": total_cost_usd,
            "total_traded_notional": total_notional,
            "num_trades": num_trades,
            "spread_bps": float(wf.get("spread_bps", SPREAD_BPS)),
            "impact_coeff": float(wf.get("impact_coeff", IMPACT_COEFF)),
            "max_participation": float(wf.get("max_participation", MAX_PARTICIPATION)),
            "cost_budget_bps": float(wf.get("cost_budget_bps", COST_BUDGET_BPS)),
            "oos_equity_curve": [float(v) for v in equity_curve],
            "window_returns": [float(v) for v in wf.get("window_returns", [])],
        },
        "kill_switch": kill_switch,
        "success": {
            "sharpe_ok": sharpe_ok,
            "trades_ok": trades_ok,
            "cost_ok": cost_ok,
            "non_degenerate": non_degenerate,
            "within_band_sharpe": within_band_sharpe,
            "within_band_trades": within_band_trades,
            "within_band_cost": within_band_cost,
            "within_band": within_band,
            "min_sharpe": float(MIN_SHARPE),
            "eval34_band": {
                "sharpe": float(EVAL34_ORDERFLOW_ONLY_SHARPE),
                "trades": int(EVAL34_ORDERFLOW_ONLY_TRADES),
                "cost_usd": float(EVAL34_ORDERFLOW_ONLY_COST_USD),
            },
            "measured_vs_band": {
                "sharpe_delta": float(oos_sharpe - EVAL34_ORDERFLOW_ONLY_SHARPE) if math.isfinite(oos_sharpe) else 0.0,
                "trades_delta": float(num_trades - EVAL34_ORDERFLOW_ONLY_TRADES),
                "cost_delta_usd": float(total_cost_usd - EVAL34_ORDERFLOW_ONLY_COST_USD),
            },
        },
        "portfolio_certification": decision_block,
        "verdict": "GO" if (non_degenerate and within_band and not kill_switch["any_breach"]) else "NO-GO",
        "verdict_reason": (
            f"orderflow-only second-window validation: decision={decision}; "
            f"Sharpe={oos_sharpe:.4f} (band ~{EVAL34_ORDERFLOW_ONLY_SHARPE:.4f}), "
            f"trades={num_trades} (band ~{EVAL34_ORDERFLOW_ONLY_TRADES}), "
            f"cost=${total_cost_usd:.2f} (band ~${EVAL34_ORDERFLOW_ONLY_COST_USD:.2f}), "
            f"max-DD={oos_max_dd:.4f}; non_degenerate={non_degenerate}, within_band={within_band}"
        ),
        "evidence_matrix": {
            "real_tape_loaded": bool(n_trades_total > 0),
            "n_trades_total": n_trades_total,
            "bars_constructed": bool(n_bars > 0),
            "n_bars": n_bars,
            "causal_orderflow_signal_computed": bool(len(orderflow_signal) == n_bars),
            "toxicity_measured": bool(toxicity["toxicity_measured"]),
            "toxicity_gate_applied": True,
            "capacity_aware_sizing_applied": True,
            "walkforward_run": bool(num_windows > 0),
            "paper_only": True,
            "live_trading_enabled": False,
            "no_synthetic_fallback": True,
            "never_valid_true": True,
        },
        "commands": [
            "python3 -m py_compile scripts/eval35_orderflow_only_second_window_validation.py tests/test_eval35_orderflow_only_second_window_validation.py",
            "python3 -m pytest -q tests/test_eval35_orderflow_only_second_window_validation.py",
            "python3 scripts/eval35_orderflow_only_second_window_validation.py",
        ],
        "code_paths": [
            "src/analytics/capacity_aware_tca.py",
            "src/analytics/integrated_options_orderflow_evaluation.py",
            "src/analytics/strategy_evaluation.py",
            "src/alpha/orderflow_alpha.py",
            "src/campaign/integrated.py",
            "src/data/loader.py",
            "src/data/public_export_acquisition.py",
            "src/telemetry/serialization.py",
            "scripts/eval35_orderflow_only_second_window_validation.py",
            "tests/test_eval35_orderflow_only_second_window_validation.py",
        ],
    }

    assert _all_finite_numbers({k: v for k, v in report.items()
                                if k not in ("tape", "signal", "walkforward", "kill_switch", "success",
                                              "evidence_matrix", "commands", "code_paths",
                                              "provenance_caveats", "portfolio_certification")}), "non-finite scalar values in report"
    assert_json_valid(report)
    serialized = serialize_metrics_strict(report)
    return serialized


def build_md(r: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# {r['report_id']} — Orderflow-only second independent real data window validation (EVAL-35, paper-only)")
    lines.append("")
    lines.append(f"- **Report ID:** `{r['report_id']}`")
    lines.append(f"- **Generated:** {r['generated_at']}")
    lines.append(f"- **Task ID:** `{r['task_id']}`")
    lines.append(f"- **Verdict:** **{r['verdict']}**")
    lines.append(f"- **Reason:** {r['verdict_reason']}")
    lines.append(f"- **Provenance:** {r['data_provenance']} (authenticity_verified={r['authenticity_verified']})")
    lines.append(f"- **Trading mode:** {r['trading_mode']} (live enabled: {r['live_trading_enabled']})")
    for c in r["provenance_caveats"]:
        lines.append(f"- Caveat: {c}")
    lines.append("")

    t = r["tape"]
    lines.append("## TAPE (second independent real data window, OKX BTC-USD-SWAP)")
    lines.append(f"- Path: `{t['tape_path']}`")
    lines.append(f"- Trades: {t['n_trades_total']}; Bars: {t['n_bars']} ({t['bar_duration_seconds']}s each)")
    lines.append(f"- Span: {t['start_timestamp']} -> {t['end_timestamp']}")
    lines.append(f"- Independent of EVAL-23..34 ({t['previous_window_utc']}): {t['independent_of_eval_23_to_34']}")
    lines.append(f"- Source: {t['source']} (authenticated={t['authenticated']}, public_read_only={t['public_read_only']})")
    lines.append("")

    s = r["signal"]
    lines.append("## ORDERFLOW-ONLY SIGNAL (causal, net_aggression via OrderflowAlphaEngine)")
    lines.append(f"- Bars: {s['n_bars']}; long {s['long_bars']}; short {s['short_bars']}; flat {s['flat_bars']}")
    lines.append(f"- Gated flat (toxicity VPIN>=0.70->flat): {s['gated_flat_bars']}")
    lines.append(f"- Mean signal: {s['mean_signal']:.6f}")
    lines.append("")

    tox = r["toxicity"]
    lines.append("## TOXICITY (VPIN, causal, threshold 0.70)")
    lines.append(f"- Mean {tox['mean_toxicity']:.6f}; p95 {tox['p95_toxicity']:.6f}; range [{tox['min_toxicity']:.6f}, {tox['max_toxicity']:.6f}]")
    lines.append(f"- Fraction above threshold: {tox['fraction_above_threshold']:.6f}; gate engages: {tox['gate_engages']}; toxicity measured: {tox['toxicity_measured']}")
    lines.append("")

    wf = r["walkforward"]
    lines.append("## NET-OF-COST ORDERFLOW-ONLY WALK-FORWARD (capacity-aware sizing)")
    lines.append(f"- Return: {wf['oos_return']:.6f}; Sharpe: {wf['oos_sharpe']:.6f}; max-DD: {wf['oos_max_drawdown']:.6f}; ann_vol: {wf['oos_ann_vol']:.6f}")
    lines.append(f"- Cost: ${wf['total_cost_usd']:.2f}; notional: ${wf['total_traded_notional']:.2f}; trades: {wf['num_trades']}; windows: {wf['num_windows']}")
    lines.append(f"- spread {wf['spread_bps']} bps; impact {wf['impact_coeff']}; max participation {wf['max_participation']}; cost budget {wf['cost_budget_bps']} bps")
    lines.append("")

    ks = r["kill_switch"]
    lines.append("## KILL-SWITCH TRIGGERS (read-only evaluation)")
    lines.append(f"- max-DD {ks['max_drawdown']:.4f} >= {ks['max_drawdown_threshold']:.0%}: {ks['max_drawdown_breached']}")
    lines.append(f"- cost {ks['cost_bps']:.4f} bps >= {ks['cost_bps_threshold']} bps: {ks['cost_bps_breached']}")
    lines.append(f"- toxicity gate active {ks['toxic_gate_active_fraction']:.4f} >= {ks['toxicity_threshold']:.0%}: {ks['toxicity_breached']}")
    lines.append(f"- notional ${ks['total_notional_usd']:.2f} >= ${ks['max_notional_usd']:,}: {ks['notional_breached']}")
    lines.append(f"- Triggers: {ks['triggers']}; any breach: {ks['any_breach']}")
    lines.append("")

    sc = r["success"]
    lines.append("## SUCCESS vs EVAL-34 HELD-OUT BAND")
    lines.append(f"- Sharpe {sc['measured_vs_band']['sharpe_delta']:+.4f} vs band {sc['eval34_band']['sharpe']:.4f}: ok={sc['sharpe_ok']} (>{sc['min_sharpe']})")
    lines.append(f"- Trades {sc['measured_vs_band']['trades_delta']:+.0f} vs band {sc['eval34_band']['trades']}: ok={sc['trades_ok']} (>0)")
    lines.append(f"- Cost ${sc['measured_vs_band']['cost_delta_usd']:+.2f} vs band ${sc['eval34_band']['cost_usd']:.2f}: ok={sc['cost_ok']} (>0)")
    lines.append(f"- Non-degenerate: {sc['non_degenerate']}; within band: {sc['within_band']}")
    lines.append("")

    pc = r["portfolio_certification"]
    lines.append("## PORTFOLIO CERTIFICATION DECISION")
    lines.append(f"- **Decision:** **{pc['decision']}**")
    lines.append("")
    lines.append("### Rationale")
    lines.append(pc["rationale"])
    lines.append("")
    lines.append(f"- Max notional: ${pc['max_notional_usd']:,}; max daily loss: ${pc['max_daily_loss_usd']:,}")
    lines.append(f"- Max drawdown: {pc['max_drawdown_pct']:.0%}; toxicity kill-switch: {pc['toxicity_kill_switch_pct']:.0%}; cost kill-switch: {pc['cost_kill_switch_bps']} bps")
    lines.append(f"- Non-degenerate: {pc['non_degenerate']}; within EVAL-34 band: {pc['within_eval34_band']}; kill-switch breach: {pc['kill_switch_breach']}")
    lines.append("")

    lines.append("## EVIDENCE MATRIX")
    for k, v in r["evidence_matrix"].items():
        lines.append(f"- {k}: {v}")
    lines.append("")

    lines.append("## COMMANDS")
    for cmd in r["commands"]:
        lines.append(f"```bash\n{cmd}\n```")

    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="EVAL-35 orderflow-only second window validation (paper-only)")
    ap.add_argument("--no-write", action="store_true", help="compute without writing artifacts")
    args = ap.parse_args(argv)
    report = build_report()
    print(json.dumps({
        "report_id": report["report_id"],
        "verdict": report["verdict"],
        "verdict_reason": report["verdict_reason"],
        "portfolio_certification": report["portfolio_certification"]["decision"],
        "oos_sharpe": report["walkforward"]["oos_sharpe"],
        "oos_trades": report["walkforward"]["num_trades"],
        "oos_cost_usd": report["walkforward"]["total_cost_usd"],
        "oos_max_dd": report["walkforward"]["oos_max_drawdown"],
        "non_degenerate": report["success"]["non_degenerate"],
        "within_eval34_band": report["success"]["within_band"],
        "artifact_paths": report.get("artifact_paths", {}),
    }, sort_keys=True))
    if not args.no_write:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = _stamp_for_filename(report["generated_at"])
        jpath = OUT_DIR / f"{REPORT_ID}_{stamp}.json"
        mpath = OUT_DIR / f"{REPORT_ID}_{stamp}.md"
        jpath.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        md = build_md(report)
        mpath.write_text(md + "\n", encoding="utf-8")
        report["artifact_paths"] = {"json": str(jpath), "md": str(mpath)}
        jpath.write_text(json.dumps(serialize_metrics_strict(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Wrote {jpath}")
        print(f"Wrote {mpath}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
