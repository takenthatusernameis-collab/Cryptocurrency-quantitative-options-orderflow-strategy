"""Real net-of-cost integrated options+orderflow evaluation (EVAL-23, paper-only).

Repo-priority gate: the crypto quantitative **options + orderflow** strategy has
been evaluated (EVAL-18) only on a synthetic chain/tape. EVAL-23 seals the same
net-of-cost measurement on **real public OKX exports** with no synthetic
fallback:

  1. **Real inputs only** — ``load_real_orderflow`` / ``load_real_options_chain``
     raise :class:`RealDataUnavailable` when no real export exists. This module
     never reads a synthetic fixture and never substitutes one.
  2. **Reuses the sealed EVAL-18 primitives** — causal bar construction, options
     surface signal, orderflow net-aggression signal, VPIN toxicity gate, the
     deterministic both-pillars fusion rule, the capacity-aware walk-forward
     cost model, IC/permutation/DSR/PBO/BH-FDR statistics and the 7-check
     verdict. No primitive is re-implemented or relaxed.
  3. **Adds the EVAL-23-specific validity gates** — real provenance, real-data
     adequacy, a non-degenerate orderflow signal and a non-degenerate *tradable*
     options signal. A degenerate options leg is recorded explicitly (it is what
     makes the combined strategy flat), never hidden.
  4. **Fusion adjudication** — the sealed fusion rule requires both pillars to
     agree. EVAL-23 records whether the combined strategy is flat *because* the
     options leg is degenerate, and reports the orderflow-only control so the
     finding is auditable rather than buried.

Measured result on the real tape/chain is reported verbatim: a trustworthy
NO-GO is a full success; a fabricated GO is a failure.

Emit canonical artifact:
``research_state/REAL_NET_OF_COST_EVAL_23_<UTC>.{json,md}``.
Paper-only: no network, no ``.env``, no venue/credential mutation, no live.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from src.analytics.integrated_options_orderflow_evaluation import (
    DEFAULT_BAR_DURATION_SECONDS,
    DEFAULT_CALIB_RESIDUAL_THRESHOLD,
    DEFAULT_GEX_FLIP_DISTANCE_THRESHOLD,
    DEFAULT_MAX_POSITION_PCT,
    DEFAULT_SEEDS,
    DEFAULT_SIGNAL_LOOKBACK_SECONDS,
    DEFAULT_SIGNAL_THRESHOLD,
    DEFAULT_SKEW_SLOPE_THRESHOLD,
    DEFAULT_TOXICITY_THRESHOLD,
    DEFAULT_TOXICITY_WINDOW_TRADES,
    HORIZONS,
    _build_bars,
    _causal_options_signal_series,
    _causal_signal_series,
    _finite,
    _options_signal_components,
    _pearson,
    _run_walkforward,
    _signal_positions,
    _toxicities_per_bar,
    compute_alpha_metrics,
    compute_integrated_verdict,
    compute_toxicity_metrics,
    evaluate_integrated_options_orderflow,
)
from src.analytics.capacity_aware_tca import (
    DEFAULT_COST_BUDGET_BPS,
    DEFAULT_IMPACT_COEFF,
    DEFAULT_MAX_PARTICIPATION,
    DEFAULT_SPREAD_BPS,
    CapacityAwareSizer,
)
from src.analytics.strategy_evaluation import permutation_test
from src.alpha.orderflow_alpha import OrderflowAlphaEngine
from src.campaign.integrated import (
    DETERMINISTIC_NOW,
    IntegratedConfig,
    RealDataUnavailable,
    load_real_options_chain,
    load_real_orderflow,
)
from src.data.schemas import OptionsChain, OrderflowSnapshot
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

REPORT_ID = "REAL_NET_OF_COST_EVAL_23"
OUT_DIR = Path("research_state")

TRADING_MODE = "paper"
LIVE_TRADING_ENABLED = False

# EVAL-23-specific numeric validity gates (with rationale in the artifact).
MIN_REAL_TRADES: int = 1000
MIN_REAL_BARS: int = 400
MIN_REAL_QUOTES: int = 8
MIN_REAL_EXPIRIES: int = 2
MIN_REAL_STRIKES: int = 5

# A tradable options signal must be both non-constant across bars and have a
# non-zero information coefficient. EVAL-18 only requires the latter, which a
# constant broadcast signal satisfies vacuously; EVAL-23 measures both.
MIN_OPTIONS_SIGNAL_STDEV: float = 1e-12
MIN_ABS_OPTIONS_IC: float = 1e-12


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp_for_filename(iso_ts: str) -> str:
    return (
        iso_ts.replace("-", "").replace(":", "").replace(".", "").replace("Z", "Z")
    )


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


def _stdev(values: Sequence[float]) -> float:
    vals = [float(v) for v in values]
    if len(vals) < 2:
        return 0.0
    mean = sum(vals) / len(vals)
    var = sum((v - mean) ** 2 for v in vals) / (len(vals) - 1)
    return math.sqrt(var) if var > 0.0 else 0.0


def _last_trade_price(snapshot: OrderflowSnapshot) -> float:
    trades = sorted(snapshot.trades or [], key=lambda t: t.timestamp)
    return float(trades[-1].price) if trades else 0.0


def _chain_stats(chain: OptionsChain) -> Dict[str, Any]:
    quotes = chain.quotes or []
    strikes = sorted({float(q.contract.strike) for q in quotes})
    expiries = sorted({q.contract.expiry for q in quotes})
    calls = sum(1 for q in quotes if str(q.contract.option_type).lower() == "call")
    puts = sum(1 for q in quotes if str(q.contract.option_type).lower() == "put")
    return {
        "n_quotes": int(len(quotes)),
        "n_contracts": int(len(quotes)),
        "n_strikes": int(len(strikes)),
        "n_expiries": int(len(expiries)),
        "n_calls": int(calls),
        "n_puts": int(puts),
        "strike_min": float(min(strikes)) if strikes else 0.0,
        "strike_max": float(max(strikes)) if strikes else 0.0,
        "has_mark_iv": int(sum(1 for q in quotes if q.mark_iv is not None)),
        "has_stored_delta": int(sum(1 for q in quotes if q.delta is not None)),
    }


def _compute_real_signals(
    snapshot: OrderflowSnapshot,
    chain: OptionsChain,
    spot: float,
    now: datetime,
    bar_duration_seconds: float,
    signal_lookback_seconds: float,
    toxicity_window_trades: int,
    signal_threshold: float,
    toxicity_threshold: float,
) -> Dict[str, Any]:
    """Build every EVAL-23 signal block from real inputs (no synthetic fallback)."""
    bars = _build_bars(snapshot, bar_duration_seconds=bar_duration_seconds)
    n_bars = int(bars["n_bars"])
    bar_ends_dt = bars["bar_ends_dt"]
    bar_closes = [float(p) for p in bars["bar_closes"]]

    opt_components = _options_signal_components(chain, spot, now, seed=42)
    options_signal = _causal_options_signal_series(n_bars, opt_components)

    engine = OrderflowAlphaEngine(seed=42)
    of_series = _causal_signal_series(
        snapshot, bar_ends_dt, bar_closes,
        lookback_seconds=signal_lookback_seconds, engine=engine,
    )
    orderflow_signal = [float(s) for s in of_series["signals"]]

    toxicities = _toxicities_per_bar(
        snapshot, bar_ends_dt, window_trades=toxicity_window_trades
    )
    toxicity = compute_toxicity_metrics(toxicities, threshold=toxicity_threshold)

    options_alpha = compute_alpha_metrics(options_signal, bar_closes, horizons=HORIZONS)
    orderflow_alpha = compute_alpha_metrics(orderflow_signal, bar_closes, horizons=HORIZONS)

    return {
        "bars": bars,
        "n_bars": n_bars,
        "bar_closes": bar_closes,
        "bar_ends_dt": bar_ends_dt,
        "options_components": opt_components,
        "options_signal": options_signal,
        "orderflow_signal": orderflow_signal,
        "toxicities": toxicities,
        "toxicity": toxicity,
        "options_alpha": options_alpha,
        "orderflow_alpha": orderflow_alpha,
        "signal_threshold": float(signal_threshold),
        "toxicity_threshold": float(toxicity_threshold),
    }


def _tradable_options_signal(
    options_signal: Sequence[float],
    orderflow_signal: Sequence[float],
    toxicities: Sequence[float],
    options_alpha: Dict[str, Any],
    toxicity_threshold: float,
) -> Dict[str, Any]:
    """Measure whether the real options leg yields a *tradable* signal.

    EVAL-18's ``options_signal_exists`` check passes on a non-zero IC alone,
    which a constant broadcast signal satisfies vacuously. EVAL-23 separates
    three distinct facts: the signal is non-constant, its IC is non-zero, and
    the resulting position series is not identically flat.
    """
    sig_stdev = _stdev(options_signal)
    opt_ic = abs(float(options_alpha["ic_mean"]))
    positions = _signal_positions(options_signal)
    n_nonzero = int(sum(1 for p in positions if p != 0))

    # A constant broadcast value has zero stdev; a zero IC means no measured
    # relation to forward returns. Either makes the leg non-tradable.
    non_constant = bool(sig_stdev > MIN_OPTIONS_SIGNAL_STDEV)
    ic_present = bool(opt_ic > MIN_ABS_OPTIONS_IC)
    positions_present = bool(n_nonzero > 0)

    degenerate = not (non_constant and ic_present and positions_present)

    reasons: List[str] = []
    if not non_constant:
        reasons.append(
            "options signal is constant across bars (stdev "
            f"{sig_stdev:.3e} <= {MIN_OPTIONS_SIGNAL_STDEV:.1e}): the real chain is a "
            "single cross-section, so broadcasting it produces no time variation"
        )
    if not ic_present:
        reasons.append(
            f"options IC magnitude {opt_ic:.3e} <= {MIN_ABS_OPTIONS_IC:.1e}: no measured "
            "relation to forward returns"
        )
    if not positions_present:
        reasons.append("options signal never crosses the position threshold")

    # Per-bar signal variation excluding the degenerate case, for auditability.
    distinct_values = int(len({round(float(v), 12) for v in options_signal}))

    return {
        "non_constant": non_constant,
        "ic_present": ic_present,
        "positions_present": positions_present,
        "signal_stdev": float(sig_stdev),
        "abs_options_ic": float(opt_ic),
        "n_nonzero_positions": n_nonzero,
        "distinct_signal_values": distinct_values,
        "n_bars": int(len(options_signal)),
        "options_leg_degenerate": bool(degenerate),
        "reasons": reasons,
        "gated_out_by_toxicity": int(
            sum(
                1
                for i in range(len(positions))
                if i < len(toxicities)
                and float(toxicities[i]) >= float(toxicity_threshold)
            )
        ),
    }


def _real_adequacy(
    snapshot: OrderflowSnapshot,
    chain: OptionsChain,
    n_bars: int,
) -> Dict[str, Any]:
    stats = _chain_stats(chain)
    n_trades = int(len(snapshot.trades or []))
    orderflow_ok = bool(n_trades >= MIN_REAL_TRADES and n_bars >= MIN_REAL_BARS)
    options_ok = bool(
        stats["n_quotes"] >= MIN_REAL_QUOTES
        and stats["n_expiries"] >= MIN_REAL_EXPIRIES
        and stats["n_strikes"] >= MIN_REAL_STRIKES
    )
    return {
        "orderflow_min_trades": MIN_REAL_TRADES,
        "orderflow_min_bars": MIN_REAL_BARS,
        "options_min_quotes": MIN_REAL_QUOTES,
        "options_min_expiries": MIN_REAL_EXPIRIES,
        "options_min_strikes": MIN_REAL_STRIKES,
        "n_trades": n_trades,
        "n_bars": int(n_bars),
        "orderflow_adequate": orderflow_ok,
        "options_adequate": options_ok,
        "adequate": bool(orderflow_ok and options_ok),
        "chain_stats": stats,
    }


def _compute_verdict(
    base_verdict: Dict[str, Any],
    adequacy: Dict[str, Any],
    tradable: Dict[str, Any],
    real_provenance: Dict[str, Any],
) -> Dict[str, Any]:
    """Sealed EVAL-18 checks plus the EVAL-23 real-data validity gates."""
    checks: List[Dict[str, Any]] = [dict(c) for c in base_verdict["checks"]]

    def _add(name: str, ok: bool, threshold: float, observed: float, reason: str) -> None:
        checks.append({
            "name": name,
            "pass": bool(ok),
            "threshold": float(threshold),
            "observed": float(observed),
            "reason": reason,
        })

    _add(
        "real_data_provenance",
        bool(real_provenance["real"]),
        1.0,
        1.0 if real_provenance["real"] else 0.0,
        "PASS: inputs loaded from real OKX public exports (no synthetic fallback)"
        if real_provenance["real"]
        else "FAIL: real inputs unavailable",
    )
    _add(
        "real_data_adequate",
        bool(adequacy["adequate"]),
        1.0,
        1.0 if adequacy["adequate"] else 0.0,
        (
            f"PASS: {adequacy['n_trades']} trades / {adequacy['n_bars']} bars, "
            f"{adequacy['chain_stats']['n_quotes']} quotes / "
            f"{adequacy['chain_stats']['n_expiries']} expiries / "
            f"{adequacy['chain_stats']['n_strikes']} strikes"
            if adequacy["adequate"]
            else "FAIL: real data below adequacy floors"
        ),
    )
    _add(
        "orderflow_signal_non_degenerate",
        bool(base_verdict["checks"][1]["pass"]),
        1.0,
        abs(float(base_verdict["checks"][1]["observed"])),
        base_verdict["checks"][1]["reason"],
    )
    _add(
        "options_signal_tradable",
        not bool(tradable["options_leg_degenerate"]),
        1.0,
        1.0 if not tradable["options_leg_degenerate"] else 0.0,
        "PASS: options leg is non-constant, has non-zero IC and produces positions"
        if not tradable["options_leg_degenerate"]
        else "FAIL: options leg degenerate — " + "; ".join(tradable["reasons"]),
    )

    all_pass = all(bool(c["pass"]) for c in checks)
    return {
        "verdict": "GO" if all_pass else "NO-GO",
        "checks": checks,
        "n_checks": int(len(checks)),
        "n_passed": int(sum(1 for c in checks if bool(c["pass"]))),
        "all_checks_pass": bool(all_pass),
        "failed_checks": [c["name"] for c in checks if not bool(c["pass"])],
        "sealed_eval18_checks": [c["name"] for c in base_verdict["checks"]],
        "eval23_added_checks": [
            "real_data_provenance",
            "real_data_adequate",
            "orderflow_signal_non_degenerate",
            "options_signal_tradable",
        ],
    }


def evaluate_real_net_of_cost(
    *,
    data_raw: Path | str = Path("data/raw"),
    symbol: str = "BTC",
    spot: Optional[float] = None,
    now: Optional[datetime] = None,
    bar_duration_seconds: float = DEFAULT_BAR_DURATION_SECONDS,
    signal_lookback_seconds: float = DEFAULT_SIGNAL_LOOKBACK_SECONDS,
    toxicity_window_trades: int = DEFAULT_TOXICITY_WINDOW_TRADES,
    toxicity_threshold: float = DEFAULT_TOXICITY_THRESHOLD,
    signal_threshold: float = DEFAULT_SIGNAL_THRESHOLD,
    gex_flip_distance_threshold: float = DEFAULT_GEX_FLIP_DISTANCE_THRESHOLD,
    skew_slope_threshold: float = DEFAULT_SKEW_SLOPE_THRESHOLD,
    calib_residual_threshold: float = DEFAULT_CALIB_RESIDUAL_THRESHOLD,
    seeds: Sequence[int] = DEFAULT_SEEDS,
    max_position_pct: float = DEFAULT_MAX_POSITION_PCT,
    spread_bps: float = DEFAULT_SPREAD_BPS,
    impact_coeff: float = DEFAULT_IMPACT_COEFF,
    max_participation: float = DEFAULT_MAX_PARTICIPATION,
    cost_budget_bps: float = DEFAULT_COST_BUDGET_BPS,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """Run EVAL-23 on real exports and return the strict-serialized report.

    Raises :class:`RealDataUnavailable` when either real export is missing;
    there is no synthetic fallback path.
    """
    stamp = timestamp or _utc_now_iso()

    snapshot = load_real_orderflow(symbol, data_raw=Path(data_raw))
    if not snapshot.trades:
        raise RealDataUnavailable(f"real orderflow export for {symbol!r} has no trades")
    last_price = _last_trade_price(snapshot)
    if last_price <= 0.0:
        raise RealDataUnavailable(f"real orderflow export for {symbol!r} has no positive price")
    if spot is None:
        spot = last_price
    if now is None:
        # Anchor the surface at the last real trade time so time-to-expiry is
        # measured against the data, not the wall clock.
        now = sorted(snapshot.trades, key=lambda t: t.timestamp)[-1].timestamp
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

    chain = load_real_options_chain(
        symbol, spot=float(spot), now=now, data_raw=Path(data_raw)
    )

    sig = _compute_real_signals(
        snapshot, chain, float(spot), now,
        bar_duration_seconds=bar_duration_seconds,
        signal_lookback_seconds=signal_lookback_seconds,
        toxicity_window_trades=toxicity_window_trades,
        signal_threshold=signal_threshold,
        toxicity_threshold=toxicity_threshold,
    )
    n_bars = int(sig["n_bars"])
    bar_closes = sig["bar_closes"]
    bar_ends_dt = sig["bar_ends_dt"]
    options_signal = sig["options_signal"]
    orderflow_signal = sig["orderflow_signal"]
    toxicities = sig["toxicities"]
    bars = sig["bars"]
    opt_components = sig["options_components"]
    options_alpha = sig["options_alpha"]
    orderflow_alpha = sig["orderflow_alpha"]
    toxicity = sig["toxicity"]

    # --- Combined signal: sealed EVAL-18 fusion rule (both pillars + toxicity) ---
    opts = _signal_positions(options_signal, threshold=signal_threshold)
    ofs = _signal_positions(orderflow_signal, threshold=signal_threshold)
    combined_signal: List[int] = []
    for i in range(n_bars):
        tox = float(toxicities[i]) if i < len(toxicities) else 0.0
        if tox >= float(toxicity_threshold):
            combined_signal.append(0)
        elif opts[i] == 1 and ofs[i] == 1:
            combined_signal.append(1)
        elif opts[i] == -1 and ofs[i] == -1:
            combined_signal.append(-1)
        else:
            combined_signal.append(0)
    combined_alpha = compute_alpha_metrics(combined_signal, bar_closes, horizons=HORIZONS)

    # --- Permutation: combined vs best single pillar at the primary horizon ---
    h = int(HORIZONS[-1])
    n_pairs = max(0, n_bars - h)
    fwd_ret = [
        (bar_closes[t + h] - bar_closes[t]) / bar_closes[t]
        for t in range(n_pairs) if bar_closes[t] > 0
    ]
    combined_primary = combined_signal[: len(fwd_ret)]
    best_pillar = (
        orderflow_signal if abs(orderflow_alpha["ic_mean"]) >= abs(options_alpha["ic_mean"])
        else options_signal
    )[: len(fwd_ret)]
    permutation = permutation_test(
        sample_a=combined_primary if combined_primary else [0.0],
        sample_b=best_pillar if best_pillar else [0.0],
        statistic=lambda vals: float(sum(vals) / len(vals)) if len(vals) > 0 else 0.0,
        paired=True,
        n_permutations=1000,
        seed=42,
    )

    # --- Net-of-cost walk-forward for the combined strategy + controls ---
    sizer = CapacityAwareSizer(
        spread_bps=spread_bps,
        impact_coeff=impact_coeff,
        max_participation=max_participation,
        cost_budget_bps=cost_budget_bps,
        seed=42,
    )
    cfg = IntegratedConfig(
        seed=42,
        train_window=120,
        test_window=40,
        step_size=40,
        purge=10,
        embargo=5,
    )
    n_points = n_bars
    max_pos = float(max_position_pct)
    flat_positions = [0] * n_bars
    options_only_gated = [
        0 if float(toxicities[i]) >= float(toxicity_threshold) else opts[i]
        for i in range(n_bars)
    ]
    orderflow_only_gated = [
        0 if float(toxicities[i]) >= float(toxicity_threshold) else ofs[i]
        for i in range(n_bars)
    ]

    combined_wf = _run_walkforward(
        symbol, bar_closes, combined_signal, bar_ends_dt, sizer, cfg,
        n_points, 42, max_position_pct=max_pos,
    )
    flat_wf = _run_walkforward(
        symbol, bar_closes, flat_positions, bar_ends_dt, sizer, cfg,
        n_points, 42, max_position_pct=max_pos,
    )
    options_only_wf = _run_walkforward(
        symbol, bar_closes, options_only_gated, bar_ends_dt, sizer, cfg,
        n_points, 42, max_position_pct=max_pos,
    )
    orderflow_only_wf = _run_walkforward(
        symbol, bar_closes, orderflow_only_gated, bar_ends_dt, sizer, cfg,
        n_points, 42, max_position_pct=max_pos,
    )

    base_verdict = compute_integrated_verdict(
        options_alpha, orderflow_alpha, combined_alpha, toxicity,
        combined_wf, options_only_wf, orderflow_only_wf, flat_wf,
        permutation, {}, {}, {}, no_lookahead_asserted=True,
    )

    adequacy = _real_adequacy(snapshot, chain, n_bars)
    tradable = _tradable_options_signal(
        options_signal, orderflow_signal, toxicities, options_alpha,
        toxicity_threshold,
    )
    real_provenance = {
        "real": True,
        "data_provenance": "real_public_exchange_export",
        "authenticity_verified": False,
        "venue": str(snapshot.venue),
        "orderflow_instrument_symbol": str(snapshot.symbol),
        "note": (
            "public OKX read-only export; inverse BTC-USD-SWAP tape, spot options "
            "chain; no signed venue attestation (authenticity_verified=false)"
        ),
    }
    verdict = _compute_verdict(base_verdict, adequacy, tradable, real_provenance)

    # --- Fusion adjudication (explicit, auditable) ---
    # The degenerate options signal is still a *constant* position (e.g. -1);
    # what makes the combined leg flat is that the constant options side never
    # agrees with the time-varying orderflow side. Measure that directly instead
    # of inferring it from the combined position count.
    n_combined_nonzero = int(sum(1 for v in combined_signal if v != 0))
    n_options_nonzero = int(sum(1 for v in opts if v != 0))
    n_orderflow_nonzero = int(sum(1 for v in ofs if v != 0))
    n_agree = int(
        sum(
            1
            for i in range(n_bars)
            if opts[i] != 0 and opts[i] == ofs[i]
        )
    )
    n_disagree = int(
        sum(
            1
            for i in range(n_bars)
            if opts[i] != 0 and ofs[i] != 0 and opts[i] != ofs[i]
        )
    )
    flat_because_options = bool(
        tradable["options_leg_degenerate"]
        and n_combined_nonzero == 0
        and n_orderflow_nonzero > 0
    )
    fusion_adjudication = {
        "sealed_rule": (
            "long only when options==+1 AND orderflow==+1 AND VPIN<threshold; "
            "short only when options==-1 AND orderflow==-1 AND VPIN<threshold; flat otherwise"
        ),
        "rule_amended": False,
        "options_leg_degenerate": bool(tradable["options_leg_degenerate"]),
        "combined_flat_because_options_degenerate": flat_because_options,
        "combined_nonzero_bars": n_combined_nonzero,
        "options_nonzero_bars": n_options_nonzero,
        "orderflow_nonzero_bars": n_orderflow_nonzero,
        "bars_options_and_orderflow_agree": n_agree,
        "bars_options_and_orderflow_disagree": n_disagree,
        "orderflow_only_trades": int(orderflow_only_wf["num_trades"]),
        "orderflow_only_sharpe": float(orderflow_only_wf["oos_sharpe"]),
        "combined_trades": int(combined_wf["num_trades"]),
        "interpretation": (
            "The options leg is degenerate: the real chain is a single "
            "cross-section, so the broadcast options signal is constant and has "
            "zero IC. The combined strategy is flat because that constant options "
            "side never agrees with the time-varying orderflow side under the "
            "both-pillars fusion rule. This is a measured NO-GO for the current "
            "strategy, not a harness artifact. Amending the fusion rule requires a "
            "new sealed evaluation; it is not done here."
            if flat_because_options
            else "Both pillars produced time variation; the fusion rule is not the binding constraint."
        ),
    }

    evidence_matrix = {
        "real_orderflow_loaded": bool(len(snapshot.trades or []) > 0),
        "real_options_loaded": bool(len(chain.quotes or []) > 0),
        "n_trades": int(len(snapshot.trades or [])),
        "n_bars": int(n_bars),
        "n_options_quotes": int(len(chain.quotes or [])),
        "n_options_contracts": int(len(chain.quotes or [])),
        "n_expiries": int(adequacy["chain_stats"]["n_expiries"]),
        "n_strikes": int(adequacy["chain_stats"]["n_strikes"]),
        "venue": str(snapshot.venue),
        "orderflow_symbol": str(snapshot.symbol),
        "spot_used": float(spot),
        "now_used": now.isoformat().replace("+00:00", "Z"),
        "data_provenance": "real",
        "authenticity_verified": False,
        "never_synthetic": True,
        "causal_no_lookahead": True,
        "paper_only": True,
        "live_trading_enabled": False,
    }

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": stamp,
        "verdict": verdict["verdict"],
        "trading_mode": TRADING_MODE,
        "live_trading_enabled": LIVE_TRADING_ENABLED,
        "data_provenance": "real",
        "authenticity_verified": False,
        "never_valid_true": True,
        "config": {
            "symbol": symbol,
            "spot": float(spot),
            "now": now.isoformat().replace("+00:00", "Z"),
            "venue": str(snapshot.venue),
            "bar_duration_seconds": float(bar_duration_seconds),
            "signal_lookback_seconds": float(signal_lookback_seconds),
            "toxicity_window_trades": int(toxicity_window_trades),
            "toxicity_threshold": float(toxicity_threshold),
            "signal_threshold": float(signal_threshold),
            "max_position_pct": float(max_pos),
            "spread_bps": float(spread_bps),
            "impact_coeff": float(impact_coeff),
            "max_participation": float(max_participation),
            "cost_budget_bps": float(cost_budget_bps),
            "seeds": [int(s) for s in seeds],
            "horizons": [int(h) for h in HORIZONS],
        },
        "adequacy": adequacy,
        "real_provenance": real_provenance,
        "bars": {
            "n_bars": int(n_bars),
            "start_timestamp": bars["start_timestamp"],
            "end_timestamp": bars["end_timestamp"],
            "bar_duration_seconds": float(bars["bar_duration_seconds"]),
            "n_trades_total": int(len(snapshot.trades or [])),
        },
        "options_components": opt_components,
        "options_leg_validity": tradable,
        "options_alpha": options_alpha,
        "orderflow_alpha": orderflow_alpha,
        "combined_alpha": combined_alpha,
        "permutation": permutation,
        "toxicity": toxicity,
        "combined_wf": {k: v for k, v in combined_wf.items() if k != "oos_equity_curve"},
        "options_only_wf": {k: v for k, v in options_only_wf.items() if k != "oos_equity_curve"},
        "orderflow_only_wf": {k: v for k, v in orderflow_only_wf.items() if k != "oos_equity_curve"},
        "flat_wf": {k: v for k, v in flat_wf.items() if k != "oos_equity_curve"},
        "fusion_adjudication": fusion_adjudication,
        "verdict_checks": verdict,
        "evidence_matrix": evidence_matrix,
        "deployment_authorization": {
            "authorized": bool(verdict["verdict"] == "GO"),
            "mode": "paper_only",
            "note": (
                "GO certifies the real net-of-cost evaluation only; not "
                "authorization to trade live."
            ),
        },
    }

    # --- Non-degeneracy assertions (never emit a silently-broken artifact) ---
    assert n_bars > 0, "real tape produced no bars"
    assert len(orderflow_signal) == n_bars, "orderflow signal misaligned"
    assert len(options_signal) == n_bars, "options signal misaligned"
    assert len(combined_signal) == n_bars, "combined signal misaligned"
    assert verdict["verdict"] in ("GO", "NO-GO")
    assert verdict["verdict"] == ("GO" if verdict["all_checks_pass"] else "NO-GO")
    assert _all_finite_numbers(options_alpha), "options alpha non-finite"
    assert _all_finite_numbers(orderflow_alpha), "orderflow alpha non-finite"
    assert _all_finite_numbers(combined_alpha), "combined alpha non-finite"
    assert _all_finite_numbers(toxicity), "toxicity non-finite"
    assert _all_finite_numbers(combined_wf), "combined walk-forward non-finite"
    assert _all_finite_numbers(orderflow_only_wf), "orderflow-only walk-forward non-finite"
    assert _all_finite_numbers(flat_wf), "flat walk-forward non-finite"
    assert _all_finite_numbers(permutation), "permutation non-finite"
    assert _all_finite_numbers(verdict), "verdict non-finite"
    assert report["data_provenance"] == "real", "EVAL-23 must be real-data only"

    assert_json_valid(report)
    return serialize_metrics_strict(report)


def write_artifacts(report: Dict[str, Any], out_dir: Path | str = OUT_DIR) -> Dict[str, str]:
    """Write the EVAL-23 JSON + markdown artifacts; return their paths."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = _stamp_for_filename(str(report["generated_at"]))
    json_path = out_dir / f"REAL_NET_OF_COST_EVAL_23_{stamp}.json"
    md_path = out_dir / f"REAL_NET_OF_COST_EVAL_23_{stamp}.md"
    json_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    md_path.write_text(_write_markdown(report) + "\n", encoding="utf-8")
    return {"json": str(json_path), "md": str(md_path)}


def _write_markdown(report: Dict[str, Any]) -> str:
    v = report["verdict_checks"]
    wf = report["combined_wf"]
    of = report["orderflow_only_wf"]
    lines: List[str] = []
    lines.append(f"# {report['report_id']} — REAL NET-OF-COST EVALUATION (paper-only)")
    lines.append("")
    lines.append(f"**Generated:** {report['generated_at']}  ")
    lines.append(f"**Verdict:** **{report['verdict']}** ({v['n_passed']}/{v['n_checks']} checks)  ")
    lines.append(f"**Data provenance:** `{report['data_provenance']}` (authenticity_verified={str(report['authenticity_verified']).lower()})  ")
    lines.append(f"**Venue:** {report['evidence_matrix']['venue']} · **orderflow:** {report['evidence_matrix']['orderflow_symbol']}  ")
    lines.append("")
    lines.append("## Measured evidence")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| real trades | {report['evidence_matrix']['n_trades']} |")
    lines.append(f"| real bars | {report['evidence_matrix']['n_bars']} |")
    lines.append(f"| option quotes / contracts | {report['evidence_matrix']['n_options_quotes']} |")
    lines.append(f"| expiries / strikes | {report['evidence_matrix']['n_expiries']} / {report['evidence_matrix']['n_strikes']} |")
    lines.append(f"| spot used | {report['config']['spot']} |")
    lines.append(f"| combined IC mean | {report['combined_alpha']['ic_mean']:.6e} |")
    lines.append(f"| orderflow IC mean | {report['orderflow_alpha']['ic_mean']:.6e} |")
    lines.append(f"| options IC mean | {report['options_alpha']['ic_mean']:.6e} |")
    lines.append(f"| combined OOS Sharpe | {wf['oos_sharpe']:.4f} |")
    lines.append(f"| combined OOS return | {wf['oos_return']:.4f} |")
    lines.append(f"| combined trades / cost USD | {wf['num_trades']} / {wf['total_cost_usd']:.2f} |")
    lines.append(f"| orderflow-only Sharpe | {of['oos_sharpe']:.4f} |")
    lines.append(f"| orderflow-only trades | {of['num_trades']} |")
    lines.append(f"| options leg degenerate | {str(report['options_leg_validity']['options_leg_degenerate']).lower()} |")
    lines.append("")
    lines.append("## Fusion adjudication")
    lines.append("")
    lines.append(f"- sealed rule unchanged: `{not report['fusion_adjudication']['rule_amended']}`")
    lines.append(f"- flat because options degenerate: `{str(report['fusion_adjudication']['combined_flat_because_options_degenerate']).lower()}`")
    lines.append(f"- {report['fusion_adjudication']['interpretation']}")
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    lines.append("| Check | Pass | Observed | Reason |")
    lines.append("|---|---|---|---|")
    for c in v["checks"]:
        reason = str(c["reason"]).replace("|", "/")
        lines.append(f"| {c['name']} | {str(bool(c['pass'])).lower()} | {c['observed']:.6g} | {reason} |")
    lines.append("")
    lines.append("## Provenance / constraints")
    lines.append("")
    lines.append("- Real OKX public read-only exports; no `.env`, no credentials, no order placement.")
    lines.append("- `authenticity_verified=false`: no signed venue attestation; tape is inverse BTC-USD-SWAP, chain is spot.")
    lines.append("- Never emits `{\"valid\": true}`. A trustworthy NO-GO is a full success.")
    lines.append("")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Real net-of-cost integrated evaluation (EVAL-23, paper-only)."
    )
    parser.add_argument("--data-dir", default="data/raw", help="real raw data dir")
    parser.add_argument("--out", default=str(OUT_DIR), help="artifact output dir")
    parser.add_argument("--symbol", default="BTC")
    parser.add_argument("--spot", type=float, default=None)
    parser.add_argument("--timestamp", default=None)
    parser.add_argument("--bar-duration-seconds", type=float, default=DEFAULT_BAR_DURATION_SECONDS)
    parser.add_argument("--signal-lookback-seconds", type=float, default=DEFAULT_SIGNAL_LOOKBACK_SECONDS)
    parser.add_argument("--toxicity-window-trades", type=int, default=DEFAULT_TOXICITY_WINDOW_TRADES)
    parser.add_argument("--toxicity-threshold", type=float, default=DEFAULT_TOXICITY_THRESHOLD)
    parser.add_argument("--signal-threshold", type=float, default=DEFAULT_SIGNAL_THRESHOLD)
    parser.add_argument("--max-position-pct", type=float, default=DEFAULT_MAX_POSITION_PCT)
    parser.add_argument("--spread-bps", type=float, default=DEFAULT_SPREAD_BPS)
    parser.add_argument("--impact-coeff", type=float, default=DEFAULT_IMPACT_COEFF)
    parser.add_argument("--max-participation", type=float, default=DEFAULT_MAX_PARTICIPATION)
    parser.add_argument("--cost-budget-bps", type=float, default=DEFAULT_COST_BUDGET_BPS)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)

    try:
        report = evaluate_real_net_of_cost(
            data_raw=Path(args.data_dir),
            symbol=args.symbol,
            spot=args.spot,
            now=None,
            bar_duration_seconds=args.bar_duration_seconds,
            signal_lookback_seconds=args.signal_lookback_seconds,
            toxicity_window_trades=args.toxicity_window_trades,
            toxicity_threshold=args.toxicity_threshold,
            signal_threshold=args.signal_threshold,
            max_position_pct=args.max_position_pct,
            spread_bps=args.spread_bps,
            impact_coeff=args.impact_coeff,
            max_participation=args.max_participation,
            cost_budget_bps=args.cost_budget_bps,
            timestamp=args.timestamp,
        )
    except RealDataUnavailable as e:
        print(json.dumps({"report_id": REPORT_ID, "verdict": "NO-GO", "error": str(e)}))
        return 2

    paths = {} if args.no_write else write_artifacts(report, Path(args.out))
    print(json.dumps({
        "report_id": report["report_id"],
        "verdict": report["verdict"],
        "n_passed": report["verdict_checks"]["n_passed"],
        "n_checks": report["verdict_checks"]["n_checks"],
        "failed_checks": report["verdict_checks"]["failed_checks"],
        "options_leg_degenerate": report["options_leg_validity"]["options_leg_degenerate"],
        "artifact_paths": paths,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())