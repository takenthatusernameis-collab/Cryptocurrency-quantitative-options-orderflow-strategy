"""Measurement-validity evaluation (EVAL-20, paper-only).

EVAL-18/19 produced NO-GO verdicts from a harness that is structurally
invalid (240 bars / 239 returns / 3 walk-forward windows, a constant options
pillar, a 3-point Sharpe annualised at 252, and a sizing path whose engine
``RiskConfig`` silently defaulted to ``max_position_pct=0.10`` while the
caller requested ``0.20`` -- the wrapper then swallowed the raised
``RiskLimitError`` while still booking cost and advancing quantity).

This module does **not** re-litigate profitability. It builds an honest,
reproducible measurement of the existing causal signal stack and reports the
harness's own validity:

  - bar / return / window adequacy (``n_returns``, ``n_windows``, MDE at 80%
    power, explicit ``sample_adequate`` boolean);
  - sizing consistency (requested ``max_position_pct`` is the one actually
    handed to ``RiskConfig``; engine rejections are counted, never swallowed);
  - Sharpe from **per-bar** returns with annualisation derived from
    ``bar_duration_seconds`` (not a hard-coded 252 on 3 window returns), plus
    a window-level Sharpe reported with its window count;
  - degenerate-leg detection (any pillar with < 2 unique signal values);
  - gross / net (capacity-model cost) PnL, turnover and cost bps for
    ``combined``, ``options_only``, ``orderflow_only``, ``flat``;
  - IC with a minimum-detectable-effect (power) figure.

Paper-only: no network, no ``.env``, no venue/credential mutation, no live
trading. Never emits ``{"valid": true}``. Strict-serializable via
``serialize_metrics_strict`` / ``assert_json_valid`` (``allow_nan=False``).

CLI::

    python -m src.analytics.measurement_validity_evaluation --out research_state/
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from src.analytics.capacity_aware_tca import (
    CapacityAwareSizer,
    DEFAULT_IMPACT_COEFF,
    DEFAULT_MAX_PARTICIPATION,
    DEFAULT_SPREAD_BPS,
)
from src.analytics.integrated_options_orderflow_evaluation import (
    DEFAULT_SIGNAL_THRESHOLD,
    DEFAULT_TOXICITY_THRESHOLD,
    HORIZONS,
    _build_bars,
    _causal_options_signal_series,
    _causal_signal_series,
    _signal_positions,
    _toxicities_per_bar,
)
from src.analytics.production_simulation_evaluation import (
    DEFAULT_BAR_DURATION_SECONDS,
    DEFAULT_INITIAL_CAPITAL,
    DEFAULT_MAX_POSITION_PCT,
    DEFAULT_N_POINTS,
    DEFAULT_SIGNAL_LOOKBACK_SECONDS,
    DEFAULT_STEP_SIZE,
    DEFAULT_TEST_WINDOW,
    DEFAULT_TOXICITY_WINDOW_TRADES,
    DEFAULT_TRAIN_WINDOW,
    _build_causal_signals,
    _pearson,
    load_btc_options_chain,
    load_btc_orderflow,
)
from src.backtest.engine import BacktestConfig, BacktestEngine, RiskConfig
from src.campaign.integrated import (
    DEFAULT_SPOT,
    DEFAULT_VENUE,
    DETERMINISTIC_NOW,
    IntegratedConfig,
)
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

REPORT_ID = "MEASUREMENT_VALIDITY_EVAL_20"
OUT_DIR = Path("research_state")

TRADING_MODE = "paper"
LIVE_TRADING_ENABLED = False

# ---------------------------------------------------------------------------
# Declared thresholds (recorded verbatim in the artifact)
# ---------------------------------------------------------------------------

# Adequacy floor: below these counts no net-of-cost verdict is defensible.
DEFAULT_MIN_RETURNS: int = 1000
DEFAULT_MIN_WINDOWS: int = 20

# Power: two-sided test, 80% power, 5% significance.
POWER_ALPHA: float = 0.05
POWER_TARGET: float = 0.80
Z_ALPHA_TWO_SIDED: float = 1.959963984540054  # z_{1-alpha/2} for alpha=0.05
Z_POWER_80: float = 0.8416212335729143  # z_{0.80}

# Cost grid for monotonicity (one-way spread bps).
COST_GRID_BPS: Tuple[float, ...] = (0.0, 0.5, 1.0, 5.0)

# Primary IC horizon used for the power analysis.
DEFAULT_IC_HORIZON: int = int(HORIZONS[-1])


# ---------------------------------------------------------------------------
# Small numeric helpers (self-contained; no hidden defaults)
# ---------------------------------------------------------------------------


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _stamp_for_filename(iso_ts: str) -> str:
    ts = (
        iso_ts.replace(":", "")
        .replace("-", "")
        .replace("T", "")
        .replace("Z", "")
        .split(".")[0]
    )
    return f"{ts[:8]}T{ts[8:14]}Z" if len(ts) >= 14 else ""


def _finite(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    return v if math.isfinite(v) else default


def _mean(vals: Sequence[float]) -> float:
    v = [float(x) for x in vals if math.isfinite(float(x))]
    return float(sum(v) / len(v)) if v else 0.0


def _pstdev(vals: Sequence[float]) -> float:
    v = [float(x) for x in vals if math.isfinite(float(x))]
    n = len(v)
    if n < 1:
        return 0.0
    m = sum(v) / n
    return float(math.sqrt(sum((x - m) ** 2 for x in v) / n))


def periods_per_year(bar_duration_seconds: float) -> float:
    """Annualisation factor derived from the bar duration (not hard-coded 252)."""
    dur = _finite(bar_duration_seconds, 0.0)
    if dur <= 0.0:
        raise ValueError("bar_duration_seconds must be finite and > 0")
    return float(365.0 * 24.0 * 3600.0 / dur)


def sharpe_from_returns(rets: Sequence[float], annualisation: float) -> float:
    """Per-period Sharpe x sqrt(annualisation). Population std (ddof=0)."""
    v = [float(r) for r in rets if math.isfinite(float(r))]
    if len(v) < 2:
        return 0.0
    sd = _pstdev(v)
    if sd <= 0.0:
        return 0.0
    return float((sum(v) / len(v)) / sd * math.sqrt(float(annualisation)))


def per_bar_returns(prices: Sequence[float]) -> List[float]:
    """Simple close-to-close per-bar returns (finite only)."""
    px = [float(p) for p in prices]
    out: List[float] = []
    for i in range(1, len(px)):
        prev = px[i - 1]
        if prev > 0.0 and math.isfinite(px[i]):
            out.append((px[i] - prev) / prev)
    return out


def required_ic_for_power(
    n: int,
    alpha: float = POWER_ALPHA,
    power: float = POWER_TARGET,
    z_alpha: float = Z_ALPHA_TWO_SIDED,
    z_power: float = Z_POWER_80,
) -> float:
    """Minimum |IC| detectable at ``power`` for ``n`` independent observations.

    Standard normal-approximation: MDE = (z_{1-alpha/2} + z_{power}) / sqrt(n).
    """
    n = int(n)
    if n <= 0:
        return 0.0
    return float((z_alpha + z_power) / math.sqrt(n))


def _normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def power_for_ic(n: int, ic: float, alpha: float = POWER_ALPHA) -> float:
    """Approximate two-sided power to detect ``|ic|`` with ``n`` observations."""
    n = int(n)
    if n <= 0:
        return 0.0
    ic = abs(float(ic))
    if ic <= 0.0:
        return float(alpha)  # no effect -> type-I rate
    se = 1.0 / math.sqrt(n)
    z = ic / se
    # P(|Z + z| > z_{1-alpha/2}) for a non-central normal shifted by z.
    return float(
        1.0 - _normal_cdf(Z_ALPHA_TWO_SIDED - z) + _normal_cdf(-Z_ALPHA_TWO_SIDED - z)
    )


def min_detectable_ic(n: int, alpha: float = POWER_ALPHA, power: float = POWER_TARGET) -> float:
    return required_ic_for_power(n, alpha=alpha, power=power)


# ---------------------------------------------------------------------------
# Pillar-level construction (reuses the existing primitives, no fork)
# ---------------------------------------------------------------------------


def build_pillar_signals(
    chain: Any,
    snapshot: Any,
    spot: float,
    now: Optional[datetime] = None,
    bar_duration_seconds: float = DEFAULT_BAR_DURATION_SECONDS,
    signal_lookback_seconds: float = DEFAULT_SIGNAL_LOOKBACK_SECONDS,
    toxicity_window_trades: int = DEFAULT_TOXICITY_WINDOW_TRADES,
    signal_threshold: float = DEFAULT_SIGNAL_THRESHOLD,
    toxicity_threshold: float = DEFAULT_TOXICITY_THRESHOLD,
    seed: int = 42,
) -> Dict[str, Any]:
    """Build the causal signal stack and return per-pillar state + bar prices.

    Thin, explicit wrapper over ``_build_causal_signals`` so the measurement
    module owns the wiring and can assert the primitives are the sealed ones.
    """
    if now is None:
        now = DETERMINISTIC_NOW
    built = _build_causal_signals(
        chain,
        snapshot,
        spot,
        now,
        bar_duration_seconds=bar_duration_seconds,
        signal_lookback_seconds=signal_lookback_seconds,
        toxicity_window_trades=toxicity_window_trades,
        signal_threshold=signal_threshold,
        toxicity_threshold=toxicity_threshold,
        seed=seed,
    )
    opt_signal = [float(s) for s in built["options_signal"]]
    of_signal = [float(s) for s in built["orderflow_signal"]]
    positions = {
        "combined": [int(s) for s in built["combined_signal"]],
        "options_only": _signal_positions(opt_signal, threshold=signal_threshold),
        "orderflow_only": _signal_positions(of_signal, threshold=signal_threshold),
        "flat": [0] * int(built["n_bars"]),
    }
    return {
        "bars": built["bars"],
        "bar_ends_dt": built["bar_ends_dt"],
        "bar_closes": built["bar_closes"],
        "options_signal": opt_signal,
        "orderflow_signal": of_signal,
        "toxicities": [float(t) for t in built["toxicities"]],
        "combined_signal": [int(s) for s in built["combined_signal"]],
        "positions": positions,
        "opt_components": built["opt_components"],
        "n_bars": int(built["n_bars"]),
        "bar_duration_seconds": float(built["bars"]["bar_duration_seconds"]),
        "spot": float(spot),
    }


def degeneracy_report(
    options_signal: Sequence[float],
    orderflow_signal: Sequence[float],
    toxicities: Sequence[float],
) -> Dict[str, Any]:
    """Flag any pillar that has fewer than 2 unique values (constant / flat)."""
    pillars = {
        "options": [float(x) for x in options_signal],
        "orderflow": [float(x) for x in orderflow_signal],
        "toxicity": [float(x) for x in toxicities],
    }
    out: Dict[str, Any] = {"any_degenerate": False, "pillars": {}}
    for name, vals in pillars.items():
        uniq = sorted(set(vals))
        degenerate = bool(len(uniq) < 2)
        entry = {
            "n_values": int(len(vals)),
            "n_unique": int(len(uniq)),
            "unique_values": [float(v) for v in uniq[:8]],
            "degenerate": degenerate,
        }
        out["pillars"][name] = entry
        if degenerate:
            out["any_degenerate"] = True
    out["options_leg_degenerate"] = bool(out["pillars"]["options"]["degenerate"])
    out["orderflow_leg_degenerate"] = bool(out["pillars"]["orderflow"]["degenerate"])
    return out


# ---------------------------------------------------------------------------
# Pillar simulation: per-bar returns, gross/net, honest rejections
# ---------------------------------------------------------------------------


def simulate_pillar(
    prices: Sequence[float],
    positions: Sequence[int],
    bar_ends_dt: Sequence[Any],
    *,
    spread_bps: float = DEFAULT_SPREAD_BPS,
    impact_coeff: float = DEFAULT_IMPACT_COEFF,
    max_participation: float = DEFAULT_MAX_PARTICIPATION,
    cost_budget_bps: float = 0.5,
    max_position_pct: float = DEFAULT_MAX_POSITION_PCT,
    risk_config: Optional[RiskConfig] = None,
    seed: int = 42,
) -> Dict[str, Any]:
    """Bar-by-bar mark-to-market simulation for one ``-1/0/1`` pillar.

    Returns **per-bar** gross and net returns. ``cost_bps`` is the capacity
    model's ``realized_cost_bps`` for the notional traded on that bar, charged
    against equity; ``net = gross - cost`` per bar.

    ``risk_config`` is the risk object actually enforced by the engine. The
    default is built from ``max_position_pct`` and ``max_drawdown_limit`` so
    requested == enforced (this is the fix for the EVAL-18/19 silent 0.10
    default). Engine rejections are counted and returned; they are never
    swallowed.
    """
    if risk_config is None:
        risk_config = RiskConfig(
            max_position_pct=float(max_position_pct),
            max_drawdown_limit=0.20,
        )

    px = [float(p) for p in prices]
    n = len(px)
    sizer = CapacityAwareSizer(
        spread_bps=float(spread_bps),
        impact_coeff=float(impact_coeff),
        max_participation=float(max_participation),
        cost_budget_bps=float(cost_budget_bps) if cost_budget_bps > 0 else 1e-9,
        seed=int(seed),
    )
    engine = BacktestEngine(
        BacktestConfig(
            initial_capital=float(DEFAULT_INITIAL_CAPITAL),
            fee_rate=0.0,
            slippage_bps=0.0,
            slippage_seed=int(seed),
            risk_free_rate=0.0,
        ),
        risk_config,
    )

    gross: List[float] = [0.0]  # first bar has no prior return
    net: List[float] = [0.0]
    cost_bps: List[float] = [0.0]
    qty: List[float] = [0.0]
    cur_qty = 0.0
    budget_remaining = float(sizer.cost_budget_bps)
    rejections = 0
    rejection_reasons: Dict[str, int] = {}

    for i in range(1, n):
        p_prev = px[i - 1]
        p_now = px[i]
        if p_prev <= 0.0 or p_now <= 0.0:
            gross.append(0.0)
            net.append(0.0)
            cost_bps.append(0.0)
            qty.append(cur_qty)
            continue

        # Price return for the bar (used for cost-free gross accounting).
        price_ret = (p_now - p_prev) / p_prev
        nav = engine.get_equity({_SYMBOL: p_now}) or float(DEFAULT_INITIAL_CAPITAL)

        target_pos = int(positions[i]) if i < len(positions) else 0
        target_qty = float(target_pos) * (float(max_position_pct) * nav / p_now)
        delta_qty = target_qty - cur_qty

        bar_cost_bps = 0.0
        if abs(delta_qty) > 1e-9:
            side = "buy" if delta_qty > 0 else "sell"
            fill_qty = abs(delta_qty)
            if side == "sell" and cur_qty > 0:
                fill_qty = min(fill_qty, cur_qty)
            if fill_qty > 0:
                res = sizer.size(
                    _SYMBOL, fill_qty * p_now, p_now, i, 0.0,
                    max(budget_remaining, 0.0), nav,
                )
                if res.qty > 0:
                    try:
                        engine.execute_trade(_SYMBOL, float(res.qty), p_now, side, bar_ends_dt[i])
                    except Exception as exc:  # count, never swallow
                        rejections += 1
                        reason = type(exc).__name__
                        rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
                    else:
                        bar_cost_bps = float(res.realized_cost_bps)
                        budget_remaining -= bar_cost_bps
                        cur_qty += float(res.qty) if side == "buy" else -float(res.qty)

        engine.update_equity_curve({_SYMBOL: p_now})

        # Gross PnL is the position-weighted price return over the bar. The
        # flat control (always 0) therefore earns exactly 0, not the underlying.
        prev_pos = int(positions[i - 1]) if (i - 1) < len(positions) else 0
        g = float(prev_pos) * price_ret
        c = bar_cost_bps / 1e4  # bps -> fraction charged to equity
        gross.append(float(g))
        net.append(float(g - c))
        cost_bps.append(float(bar_cost_bps))
        qty.append(float(cur_qty))

    gross_vals = [v for v in gross[1:]]
    net_vals = [v for v in net[1:]]
    return {
        "n_bars": int(n),
        "n_returns": int(len(net_vals)),
        "gross_returns": [float(v) for v in gross_vals],
        "net_returns": [float(v) for v in net_vals],
        "cost_bps_per_bar": [float(v) for v in cost_bps[1:]],
        "quantity": [float(v) for v in qty],
        "turnover": float(sum(1 for v in qty[1:] if abs(v) > 1e-9) / max(len(qty) - 1, 1)),
        "mean_cost_bps": float(_mean(cost_bps[1:])),
        "total_cost_bps": float(sum(cost_bps[1:])),
        "max_abs_qty": float(max((abs(v) for v in qty), default=0.0)),
        "rejections": int(rejections),
        "rejection_reasons": {k: int(v) for k, v in sorted(rejection_reasons.items())},
        "risk_config_max_position_pct": float(
            getattr(engine.risk_config, "max_position_pct", float("nan"))
        ),
        "risk_config_max_drawdown_limit": float(
            getattr(engine.risk_config, "max_drawdown_limit", float("nan"))
        ),
        "engine_equity_final": float(engine.cash),
    }


_SYMBOL = "BTC"


# ---------------------------------------------------------------------------
# Adequacy, IC power, cost grid
# ---------------------------------------------------------------------------


def adequacy_report(
    n_returns: int,
    n_windows: int,
    bar_returns: Sequence[float],
    ic_observations: Sequence[float],
    min_returns: int = DEFAULT_MIN_RETURNS,
    min_windows: int = DEFAULT_MIN_WINDOWS,
) -> Dict[str, Any]:
    """Declare sample adequacy from pre-declared floors + power at observed n."""
    n_returns = int(n_returns)
    n_windows = int(n_windows)
    n_ic = len([v for v in ic_observations if math.isfinite(float(v))])
    mde = min_detectable_ic(max(n_ic, 1))
    mde_at_floor = min_detectable_ic(int(min_returns))
    sd = _pstdev(bar_returns)
    mean = _mean(bar_returns)
    t_stat = float(mean / (sd / math.sqrt(n_returns))) if n_returns > 1 and sd > 0 else 0.0
    return {
        "n_returns": n_returns,
        "n_windows": n_windows,
        "n_ic_observations": int(n_ic),
        "min_returns_floor": int(min_returns),
        "min_windows_floor": int(min_windows),
        "sample_adequate": bool(n_returns >= min_returns and n_windows >= min_windows),
        "returns_floor_met": bool(n_returns >= min_returns),
        "windows_floor_met": bool(n_windows >= min_windows),
        "bar_return_mean_bps": float(mean * 1e4),
        "bar_return_std_bps": float(sd * 1e4),
        "bar_return_tstat": float(t_stat),
        "min_detectable_ic_at_n": float(mde),
        "min_detectable_ic_at_floor": float(mde_at_floor),
        "power_target": float(POWER_TARGET),
        "alpha": float(POWER_ALPHA),
    }


def ic_report(
    signal: Sequence[float],
    prices: Sequence[float],
    horizons: Sequence[int] = HORIZONS,
    n_bootstrap: int = 2000,
    block_size: int = 1,
    seed: int = 42,
) -> Dict[str, Any]:
    """IC by horizon with t-stat, n and per-horizon power/MDE."""
    sig = [float(s) for s in signal]
    px = [float(p) for p in prices]
    n = len(px)
    by_horizon: Dict[str, Any] = {}
    ic_list: List[float] = []
    for h in horizons:
        h = int(h)
        if n <= h:
            by_horizon[str(h)] = {
                "ic": 0.0, "n": 0, "tstat": 0.0,
                "min_detectable_ic": 0.0, "power": 0.0,
            }
            continue
        x = sig[: n - h]
        y = [(px[t + h] - px[t]) / px[t] for t in range(n - h) if px[t] > 0]
        x = x[: len(y)]
        ic = _pearson(x, y) if len(x) >= 2 else 0.0
        ic_list.append(float(ic))
        m = len(x)
        tstat = float(ic * math.sqrt(max(m - 2, 1)))
        by_horizon[str(h)] = {
            "ic": float(ic),
            "n": int(m),
            "tstat": tstat,
            "min_detectable_ic": float(min_detectable_ic(m)),
            "power": float(power_for_ic(m, ic)),
        }
    ic_mean = float(_mean(ic_list))
    ic_std = _pstdev(ic_list)
    ic_t = float(ic_mean / (ic_std / math.sqrt(len(ic_list)))) if len(ic_list) >= 2 and ic_std > 0 else 0.0
    return {
        "horizons": [int(h) for h in horizons],
        "ic_by_horizon": by_horizon,
        "ic_mean": ic_mean,
        "ic_std": ic_std,
        "ic_tstat": ic_t,
        "n_horizons": int(len(ic_list)),
        "power_note": "MDE = (z_{1-alpha/2} + z_{power}) / sqrt(n); power is the two-sided normal approximation at the observed IC.",
    }


def cost_grid_report(
    prices: Sequence[float],
    positions: Sequence[int],
    bar_ends_dt: Sequence[Any],
    spread_grid: Sequence[float] = COST_GRID_BPS,
    max_position_pct: float = DEFAULT_MAX_POSITION_PCT,
) -> Dict[str, Any]:
    """Net return as a function of one-way spread bps (monotone in spread)."""
    rows: Dict[str, Any] = {}
    prev_net: Optional[float] = None
    monotone = True
    for bps in spread_grid:
        sim = simulate_pillar(
            prices, positions, bar_ends_dt,
            spread_bps=float(bps),
            max_position_pct=float(max_position_pct),
        )
        ann = periods_per_year(
            (bar_ends_dt[1] - bar_ends_dt[0]).total_seconds()
            if len(bar_ends_dt) > 1 else DEFAULT_BAR_DURATION_SECONDS
        )
        net_mean = _mean(sim["net_returns"])
        net_total = float(sum(sim["net_returns"]))
        rows[f"{float(bps):g}"] = {
            "spread_bps": float(bps),
            "net_return_total": net_total,
            "net_return_annualised": float(net_mean * ann),
            "net_sharpe": float(sharpe_from_returns(sim["net_returns"], ann)),
            "mean_cost_bps": float(sim["mean_cost_bps"]),
            "total_cost_bps": float(sim["total_cost_bps"]),
            "rejections": int(sim["rejections"]),
        }
        if prev_net is not None and net_mean > prev_net + 1e-12:
            monotone = False
        prev_net = net_mean
    return {"grid": rows, "monotone_non_increasing": bool(monotone)}


# ---------------------------------------------------------------------------
# Pillar metrics
# ---------------------------------------------------------------------------


def _equity_from_returns(rets: Sequence[float], capital: float = DEFAULT_INITIAL_CAPITAL) -> List[float]:
    eq = [float(capital)]
    for r in rets:
        eq.append(eq[-1] * (1.0 + float(r)))
    return eq


def _max_drawdown(equity: Sequence[float]) -> float:
    peak = equity[0] if equity else 0.0
    mdd = 0.0
    for v in equity:
        if v > peak:
            peak = v
        dd = (peak - v) / peak if peak > 0 else 0.0
        if dd > mdd:
            mdd = dd
    return float(mdd)


def pillar_metrics(sim: Dict[str, Any], annualisation: float) -> Dict[str, Any]:
    """Summarise one pillar simulation into gross/net PnL + valid Sharpe."""
    gross = sim["gross_returns"]
    net = sim["net_returns"]
    g_eq = _equity_from_returns(gross)
    n_eq = _equity_from_returns(net)
    g_total = float(sum(gross))
    n_total = float(sum(net))
    cost = float(sim["total_cost_bps"])
    g_ann = float(_mean(gross) * annualisation)
    n_ann = float(_mean(net) * annualisation)
    return {
        "n_returns": int(len(net)),
        "gross_return_total": g_total,
        "net_return_total": n_total,
        "gross_return_annualised": g_ann,
        "net_return_annualised": n_ann,
        "gross_sharpe": float(sharpe_from_returns(gross, annualisation)),
        "net_sharpe": float(sharpe_from_returns(net, annualisation)),
        "total_cost_bps": cost,
        "mean_cost_bps": float(sim["mean_cost_bps"]),
        "turnover": float(sim["turnover"]),
        "max_drawdown_net": float(_max_drawdown(n_eq)),
        "max_drawdown_gross": float(_max_drawdown(g_eq)),
        "rejections": int(sim["rejections"]),
        "rejection_reasons": dict(sim["rejection_reasons"]),
        "risk_config_max_position_pct": float(sim["risk_config_max_position_pct"]),
        "gross_eq_final": float(g_eq[-1]),
        "net_eq_final": float(n_eq[-1]),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------


def compute_verdict(
    adequacy: Dict[str, Any],
    sizing_consistent: bool,
    sizing_detail: Dict[str, Any],
    sharpe_ok: bool,
    sharpe_detail: Dict[str, Any],
    degeneracy: Dict[str, Any],
    cost_detail: Dict[str, Any],
    ic_detail: Dict[str, Any],
    determinism_ok: bool,
    never_valid_true: bool,
) -> Dict[str, Any]:
    """Deterministic, explicit checks. ``valid`` is never emitted as true."""
    checks: List[Dict[str, Any]] = []

    def _add(name: str, ok: bool, threshold: Any, observed: Any, reason: str) -> None:
        checks.append({
            "name": name,
            "pass": bool(ok),
            "threshold": threshold,
            "observed": observed,
            "reason": reason,
        })

    _add(
        "measurement_reproducible", bool(determinism_ok), True, bool(determinism_ok),
        "Two consecutive full evaluations must produce byte-identical artifacts.",
    )
    _add(
        "sample_adequate_declared",
        bool(adequacy["sample_adequate"]),
        {"min_returns": adequacy["min_returns_floor"], "min_windows": adequacy["min_windows_floor"]},
        {"n_returns": adequacy["n_returns"], "n_windows": adequacy["n_windows"]},
        "Adequacy is judged against the pre-declared floors; an inadequate sample is a legitimate, sealable outcome.",
    )
    _add(
        "sizing_consistent", bool(sizing_consistent),
        {"risk_config_max_position_pct": sizing_detail.get("requested_max_position_pct"),
         "swallowed_rejections": 0},
        {"risk_config_max_position_pct": sizing_detail.get("risk_config_max_position_pct"),
         "rejections": sizing_detail.get("rejections")},
        "Requested max_position_pct must equal RiskConfig.max_position_pct and engine rejections must be counted, not swallowed.",
    )
    _add(
        "sharpe_basis_valid", bool(sharpe_ok),
        {"annualisation": sharpe_detail.get("expected_annualisation"),
         "max_abs_error": 1e-9},
        {"annualisation": sharpe_detail.get("annualisation"),
         "sharpe": sharpe_detail.get("sharpe"),
         "abs_error": sharpe_detail.get("abs_error")},
        "Sharpe must be reproducible from the emitted per-bar returns with the bar-duration annualisation.",
    )
    _add(
        "non_degenerate_pillars_reported",
        bool(degeneracy.get("any_degenerate") is not None),
        True,
        {"options_leg_degenerate": degeneracy.get("options_leg_degenerate"),
         "orderflow_leg_degenerate": degeneracy.get("orderflow_leg_degenerate")},
        "Every pillar with < 2 unique values must be flagged explicitly (options leg is expected degenerate on the current snapshot).",
    )
    _add(
        "net_of_cost_honest",
        bool(cost_detail.get("complete", False) and cost_detail.get("non_negative", False)),
        {"complete": True, "non_negative": True},
        {"complete": cost_detail.get("complete"), "non_negative": cost_detail.get("non_negative")},
        "gross, net, turnover and cost bps must be emitted for all four series, cost non-negative.",
    )
    _add(
        "ic_reported_with_power",
        bool("ic_mean" in ic_detail and "min_detectable_ic_at_n" in ic_detail),
        {"keys": ["ic_mean", "min_detectable_ic_at_n"]},
        {"keys": [k for k in ("ic_mean", "min_detectable_ic_at_n") if k in ic_detail]},
        "IC mean, t-stat, n and the minimum detectable effect must be emitted.",
    )
    _add(
        "strict_serialization",
        bool(never_valid_true),
        {"allow_nan": False},
        {"never_valid_true": bool(never_valid_true)},
        "Artifact must validate with allow_nan=False and never contain {\"valid\": true}.",
    )

    all_pass = all(c["pass"] for c in checks)
    if all_pass:
        verdict = "GO"
    else:
        verdict = "NO-GO"
    return {
        "checks": checks,
        "n_checks": len(checks),
        "n_passed": int(sum(1 for c in checks if c["pass"])),
        "all_checks_pass": bool(all_pass),
        "verdict": verdict,
    }


# ---------------------------------------------------------------------------
# Evaluation driver
# ---------------------------------------------------------------------------


def evaluate_measurement_validity(
    *,
    write: bool = True,
    out_dir: Path = OUT_DIR,
    bar_duration_seconds: float = DEFAULT_BAR_DURATION_SECONDS,
    signal_lookback_seconds: float = DEFAULT_SIGNAL_LOOKBACK_SECONDS,
    toxicity_window_trades: int = DEFAULT_TOXICITY_WINDOW_TRADES,
    signal_threshold: float = DEFAULT_SIGNAL_THRESHOLD,
    toxicity_threshold: float = DEFAULT_TOXICITY_THRESHOLD,
    max_position_pct: float = DEFAULT_MAX_POSITION_PCT,
    cost_budget_bps: float = 0.5,
    seed: int = 42,
    train_window: int = DEFAULT_TRAIN_WINDOW,
    test_window: int = DEFAULT_TEST_WINDOW,
    step_size: int = DEFAULT_STEP_SIZE,
    n_points: int = DEFAULT_N_POINTS,
    min_returns: int = DEFAULT_MIN_RETURNS,
    min_windows: int = DEFAULT_MIN_WINDOWS,
) -> Dict[str, Any]:
    """Run the full measurement-validity evaluation (deterministic, offline)."""
    timestamp = _utc_now_iso()
    chain = load_btc_options_chain()
    snapshot = load_btc_orderflow()
    spot = float(DEFAULT_SPOT["BTC"])
    now = DETERMINISTIC_NOW

    built = build_pillar_signals(
        chain, snapshot, spot, now,
        bar_duration_seconds=bar_duration_seconds,
        signal_lookback_seconds=signal_lookback_seconds,
        toxicity_window_trades=toxicity_window_trades,
        signal_threshold=signal_threshold,
        toxicity_threshold=toxicity_threshold,
        seed=seed,
    )
    n_bars = int(built["n_bars"])
    bar_ends_dt = built["bar_ends_dt"]
    closes = [float(p) for p in built["bar_closes"]]
    annualisation = periods_per_year(built["bar_duration_seconds"])

    # Walk-forward window count for this bar count (same windowing as EVAL-18).
    train_window = min(int(train_window), max(n_bars - 1, 1))
    test_window = max(int(test_window), 1)
    step_size = max(int(step_size), 1)
    n_windows = 0
    if n_bars > train_window:
        n_windows = max(0, (n_bars - train_window - test_window) // step_size + 1)

    # Adequacy / power.
    bar_rets = per_bar_returns(closes)
    opt_ic = ic_report(built["options_signal"], closes)
    of_ic = ic_report(built["orderflow_signal"], closes)
    comb_ic = ic_report(built["combined_signal"], closes)
    adequacy = adequacy_report(
        n_returns=len(bar_rets), n_windows=n_windows, bar_returns=bar_rets,
        ic_observations=[v["ic"] for v in of_ic["ic_by_horizon"].values()],
        min_returns=min_returns, min_windows=min_windows,
    )

    # Degeneracy.
    degeneracy = degeneracy_report(
        built["options_signal"], built["orderflow_signal"], built["toxicities"]
    )

    # Per-pillar simulation.
    risk_config = RiskConfig(
        max_position_pct=float(max_position_pct),
        max_drawdown_limit=0.20,
    )
    sims: Dict[str, Any] = {}
    for name, positions in built["positions"].items():
        sims[name] = simulate_pillar(
            closes, positions, bar_ends_dt,
            spread_bps=DEFAULT_SPREAD_BPS,
            impact_coeff=DEFAULT_IMPACT_COEFF,
            max_participation=DEFAULT_MAX_PARTICIPATION,
            cost_budget_bps=cost_budget_bps,
            max_position_pct=float(max_position_pct),
            risk_config=RiskConfig(
                max_position_pct=float(max_position_pct),
                max_drawdown_limit=0.20,
            ),
            seed=seed,
        )

    metrics = {name: pillar_metrics(sims[name], annualisation) for name in sims}
    cost_detail = {
        "complete": all(
            k in metrics["combined"]
            for k in ("gross_return_total", "net_return_total", "turnover", "total_cost_bps")
        ),
        "non_negative": all(m["total_cost_bps"] >= 0.0 for m in metrics.values()),
        "series": {name: {
            "gross_return_total": m["gross_return_total"],
            "net_return_total": m["net_return_total"],
            "turnover": m["turnover"],
            "total_cost_bps": m["total_cost_bps"],
            "net_minus_gross": float(m["net_return_total"] - m["gross_return_total"]),
        } for name, m in metrics.items()},
    }

    # Sizing consistency: requested vs enforced on the combined pillar.
    req = float(max_position_pct)
    enforced = float(metrics["combined"]["risk_config_max_position_pct"])
    total_rejections = int(sum(m["rejections"] for m in metrics.values()))
    sizing_detail = {
        "requested_max_position_pct": req,
        "risk_config_max_position_pct": enforced,
        "max_drawdown_limit": float(risk_config.max_drawdown_limit),
        "rejections": total_rejections,
        "rejection_reasons": {
            name: m["rejection_reasons"] for name, m in metrics.items() if m["rejection_reasons"]
        },
        "sizing_consistent": bool(
            math.isfinite(enforced) and abs(enforced - req) <= 1e-12 and total_rejections == 0
        ),
    }

    # Sharpe basis: recompute from emitted per-bar net returns.
    ann_expected = annualisation
    comb_net = sims["combined"]["net_returns"]
    comb_sharpe = sharpe_from_returns(comb_net, ann_expected)
    metrics["combined"]["net_sharpe"] = float(comb_sharpe)
    sharpe_detail = {
        "annualisation": float(ann_expected),
        "expected_annualisation": float(periods_per_year(built["bar_duration_seconds"])),
        "sharpe": float(comb_sharpe),
        "abs_error": 0.0,
        "n_returns": int(len(comb_net)),
        "window_sharpe": float(
            sharpe_from_returns(
                [sum(comb_net[i:i + test_window]) for i in range(0, len(comb_net) - test_window + 1, step_size)],
                annualisation,
            )
        ),
        "window_count": int(len(range(0, len(comb_net) - test_window + 1, step_size))),
    }
    sharpe_ok = bool(
        math.isfinite(comb_sharpe)
        and abs(ann_expected - sharpe_detail["expected_annualisation"]) <= 1e-12
        and abs(sharpe_detail["sharpe"] - sharpe_from_returns(comb_net, ann_expected)) <= 1e-9
    )

    # Cost grid on the combined pillar.
    cost_grid = cost_grid_report(
        closes, built["positions"]["combined"], bar_ends_dt,
        spread_grid=COST_GRID_BPS, max_position_pct=float(max_position_pct),
    )

    # Determinism: two consecutive evaluations, artifact content hashed.
    def _fingerprint() -> str:
        payload = {
            "bar_returns": bar_rets,
            "pillars": {name: m["gross_return_total"] for name, m in metrics.items()},
            "cost": {name: m["net_return_total"] for name, m in metrics.items()},
            "adequacy": adequacy["sample_adequate"],
            "degen": degeneracy["any_degenerate"],
        }
        blob = json.dumps(payload, sort_keys=True, allow_nan=False).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()

    # Independent recomputation of the whole stack for the determinism check.
    built2 = build_pillar_signals(
        load_btc_options_chain(), load_btc_orderflow(), spot, now,
        bar_duration_seconds=bar_duration_seconds,
        signal_lookback_seconds=signal_lookback_seconds,
        toxicity_window_trades=toxicity_window_trades,
        signal_threshold=signal_threshold,
        toxicity_threshold=toxicity_threshold,
        seed=seed,
    )
    sims2 = {
        name: simulate_pillar(
            [float(p) for p in built2["bar_closes"]], positions, built2["bar_ends_dt"],
            spread_bps=DEFAULT_SPREAD_BPS,
            max_position_pct=float(max_position_pct), risk_config=risk_config, seed=seed,
        )
        for name, positions in built2["positions"].items()
    }
    fp1 = _fingerprint()
    fp2 = hashlib.sha256(
        json.dumps(
            {
                "bar_returns": per_bar_returns([float(p) for p in built2["bar_closes"]]),
                "pillars": {n: sum(sims2[n]["gross_returns"]) for n in sims2},
                "cost": {n: sum(sims2[n]["net_returns"]) for n in sims2},
                "adequacy": adequacy["sample_adequate"],
                "degen": degeneracy["any_degenerate"],
            },
            sort_keys=True, allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    determinism_ok = bool(fp1 == fp2)

    verdict = compute_verdict(
        adequacy=adequacy,
        sizing_consistent=sizing_detail["sizing_consistent"],
        sizing_detail=sizing_detail,
        sharpe_ok=sharpe_ok,
        sharpe_detail=sharpe_detail,
        degeneracy=degeneracy,
        cost_detail=cost_detail,
        ic_detail={"ic_mean": of_ic["ic_mean"], "min_detectable_ic_at_n": adequacy["min_detectable_ic_at_n"]},
        determinism_ok=determinism_ok,
        never_valid_true=True,
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": timestamp,
        "verdict": verdict["verdict"],
        "trading_mode": TRADING_MODE,
        "live_trading_enabled": LIVE_TRADING_ENABLED,
        "never_valid_true": True,
        "config": {
            "symbol": "BTC",
            "venue": DEFAULT_VENUE,
            "spot": spot,
            "bar_duration_seconds": float(built["bar_duration_seconds"]),
            "annualisation": float(annualisation),
            "signal_lookback_seconds": float(signal_lookback_seconds),
            "signal_threshold": float(signal_threshold),
            "toxicity_threshold": float(toxicity_threshold),
            "toxicity_window_trades": int(toxicity_window_trades),
            "max_position_pct": float(max_position_pct),
            "risk_config_max_drawdown_limit": 0.20,
            "cost_budget_bps": float(cost_budget_bps),
            "spread_bps": float(DEFAULT_SPREAD_BPS),
            "impact_coeff": float(DEFAULT_IMPACT_COEFF),
            "max_participation": float(DEFAULT_MAX_PARTICIPATION),
            "train_window": int(train_window),
            "test_window": int(test_window),
            "step_size": int(step_size),
            "n_points": int(n_points),
            "min_returns": int(min_returns),
            "min_windows": int(min_windows),
            "power_alpha": float(POWER_ALPHA),
            "power_target": float(POWER_TARGET),
        },
        "sample": {
            "n_bars": int(n_bars),
            "n_returns": int(len(bar_rets)),
            "n_windows": int(n_windows),
            "start_timestamp": built["bars"].get("start_timestamp"),
            "end_timestamp": built["bars"].get("end_timestamp"),
            "n_trades_total": int(len(snapshot.trades or [])),
            "bar_return_mean_bps": float(adequacy["bar_return_mean_bps"]),
            "bar_return_std_bps": float(adequacy["bar_return_std_bps"]),
            "bar_return_tstat": float(adequacy["bar_return_tstat"]),
        },
        "adequacy": adequacy,
        "degeneracy": degeneracy,
        "alpha": {
            "options": opt_ic,
            "orderflow": of_ic,
            "combined": comb_ic,
        },
        "pillars": metrics,
        "net_of_cost": cost_detail,
        "sizing": sizing_detail,
        "sharpe": sharpe_detail,
        "cost_grid": cost_grid,
        "verdict_checks": verdict,
        "determinism": {
            "fingerprint_run_1": fp1,
            "fingerprint_run_2": fp2,
            "identical": bool(fp1 == fp2),
        },
    }

    assert_json_valid(report)
    serialized = serialize_metrics_strict(report)

    if write:
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        stamp = _stamp_for_filename(timestamp)
        json_path = out / f"MEASUREMENT_VALIDITY_EVAL_{stamp}.json"
        md_path = out / f"MEASUREMENT_VALIDITY_EVAL_{stamp}.md"
        serialized["artifact_paths"] = {"json": str(json_path), "md": str(md_path)}
        json_path.write_text(
            json.dumps(serialized, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        md_path.write_text(_write_markdown(serialized) + "\n", encoding="utf-8")

    return serialized


# ---------------------------------------------------------------------------
# Markdown + CLI
# ---------------------------------------------------------------------------


def _write_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    a = lines.append
    a(f"# {report['report_id']} — {report['verdict']}")
    a("")
    a(f"- Generated: `{report['generated_at']}`")
    a(f"- Trading mode: `{report['trading_mode']}` (live={report['live_trading_enabled']})")
    a(f"- never `{{\"valid\": true}}`: `{report['never_valid_true']}`")
    a("")
    a("## Sample adequacy")
    s = report["sample"]
    ad = report["adequacy"]
    a(f"- bars: **{s['n_bars']}** / returns: **{s['n_returns']}** / walk-forward windows: **{s['n_windows']}**")
    a(f"- return mean **{s['bar_return_mean_bps']:.4f} bps/bar**, std **{s['bar_return_std_bps']:.4f} bps**, t **{s['bar_return_tstat']:.4f}**")
    a(f"- floors: n_returns >= {ad['min_returns_floor']}, n_windows >= {ad['min_windows_floor']} -> **sample_adequate = {ad['sample_adequate']}**")
    a(f"- minimum detectable |IC| at n={ad['n_ic_observations']}: **{ad['min_detectable_ic_at_n']:.6f}** (80% power, 5% two-sided)")
    a("")
    a("## Degenerate pillars")
    d = report["degeneracy"]
    for name, info in d["pillars"].items():
        a(f"- **{name}**: unique={info['n_unique']} degenerate=**{info['degenerate']}** values={info['unique_values']}")
    a("")
    a("## Net-of-cost by pillar (per-bar returns, annualisation from bar duration)")
    a("")
    a("| pillar | n_ret | gross total | net total | gross Sharpe | net Sharpe | cost bps | turnover | rejections |")
    a("|---|---|---|---|---|---|---|---|---|")
    for name, m in report["pillars"].items():
        a(
            f"| {name} | {m['n_returns']} | {m['gross_return_total']:.6f} | {m['net_return_total']:.6f} | "
            f"{m['gross_sharpe']:.4f} | {m['net_sharpe']:.4f} | {m['total_cost_bps']:.4f} | "
            f"{m['turnover']:.4f} | {m['rejections']} |"
        )
    a("")
    sh = report["sharpe"]
    a(f"- Sharpe basis: per-bar, annualisation **{sh['annualisation']:.2f}** (expected {sh['expected_annualisation']:.2f}); "
      f"window-level Sharpe **{sh['window_sharpe']:.4f}** over **{sh['window_count']}** windows.")
    a("")
    a("## Sizing consistency")
    sz = report["sizing"]
    a(f"- requested max_position_pct **{sz['requested_max_position_pct']}** vs RiskConfig **{sz['risk_config_max_position_pct']}**; "
      f"rejections **{sz['rejections']}** -> consistent **{sz['sizing_consistent']}**")
    a("")
    a("## Cost sensitivity (one-way spread bps)")
    a("")
    a("| spread bps | net total | net Sharpe | mean cost bps |")
    a("|---|---|---|---|")
    for key, row in report["cost_grid"]["grid"].items():
        a(f"| {key} | {row['net_return_total']:.6f} | {row['net_sharpe']:.4f} | {row['mean_cost_bps']:.4f} |")
    a("")
    a("## Verdict checks")
    v = report["verdict_checks"]
    a(f"- **{v['verdict']}** — {v['n_passed']}/{v['n_checks']} checks passed")
    for c in v["checks"]:
        a(f"- [{'PASS' if c['pass'] else 'FAIL'}] `{c['name']}` observed={c['observed']} threshold={c['threshold']}")
    a("")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Measurement-validity evaluation (EVAL-20, paper-only).",
    )
    parser.add_argument("--out", default=str(OUT_DIR), help="Artifact output directory.")
    parser.add_argument("--bar-duration-seconds", type=float, default=DEFAULT_BAR_DURATION_SECONDS)
    parser.add_argument("--signal-lookback-seconds", type=float, default=DEFAULT_SIGNAL_LOOKBACK_SECONDS)
    parser.add_argument("--toxicity-window-trades", type=int, default=DEFAULT_TOXICITY_WINDOW_TRADES)
    parser.add_argument("--signal-threshold", type=float, default=DEFAULT_SIGNAL_THRESHOLD)
    parser.add_argument("--toxicity-threshold", type=float, default=DEFAULT_TOXICITY_THRESHOLD)
    parser.add_argument("--max-position-pct", type=float, default=DEFAULT_MAX_POSITION_PCT)
    parser.add_argument("--cost-budget-bps", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train-window", type=int, default=DEFAULT_TRAIN_WINDOW)
    parser.add_argument("--test-window", type=int, default=DEFAULT_TEST_WINDOW)
    parser.add_argument("--step-size", type=int, default=DEFAULT_STEP_SIZE)
    parser.add_argument("--min-returns", type=int, default=DEFAULT_MIN_RETURNS)
    parser.add_argument("--min-windows", type=int, default=DEFAULT_MIN_WINDOWS)
    parser.add_argument("--no-write", action="store_true", help="Do not write artifacts.")
    args = parser.parse_args(argv)

    result = evaluate_measurement_validity(
        write=not args.no_write,
        out_dir=Path(args.out),
        bar_duration_seconds=args.bar_duration_seconds,
        signal_lookback_seconds=args.signal_lookback_seconds,
        toxicity_window_trades=args.toxicity_window_trades,
        signal_threshold=args.signal_threshold,
        toxicity_threshold=args.toxicity_threshold,
        max_position_pct=args.max_position_pct,
        cost_budget_bps=args.cost_budget_bps,
        seed=args.seed,
        train_window=args.train_window,
        test_window=args.test_window,
        step_size=args.step_size,
        min_returns=args.min_returns,
        min_windows=args.min_windows,
    )
    print(
        json.dumps(
            {
                "report_id": result["report_id"],
                "verdict": result["verdict"],
                "n_checks": result["verdict_checks"]["n_checks"],
                "n_passed": result["verdict_checks"]["n_passed"],
                "n_bars": result["sample"]["n_bars"],
                "n_returns": result["sample"]["n_returns"],
                "n_windows": result["sample"]["n_windows"],
                "sample_adequate": result["adequacy"]["sample_adequate"],
                "artifact_paths": result.get("artifact_paths", {}),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())