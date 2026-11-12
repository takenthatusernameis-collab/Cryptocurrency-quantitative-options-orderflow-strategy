"""Net-of-cost out-of-sample falsification for the crypto options + orderflow strategy.

Runs the integrated campaign's walk-forward OOS (time-varying signal series from
``src/campaign/integrated.py``) across seeds for BTC/ETH/SOL, reports gross and
net-of-cost return/Sharpe/max-DD (``fee_rate`` + ``slippage_bps`` plus a
regime-dependent cost profile), a cost-sensitivity grid (0 / 1 / 5 / 10 bps)
with net Sharpe at each level, statistical falsification (stationary block
bootstrap 95% CI for mean net return and Sharpe, deflated Sharpe ratio,
permutation test with >= 1000 shuffles of the signal series and a p-value,
minimum track-record length), regime-conditioned performance
(trend / range / high_vol_chop / thin), and a pre-registered GO/NO-GO gate:

GO only if (a) net Sharpe > 0, (b) bootstrap lower bound > 0 or permutation
p < 0.05, (c) net return > 0, and (d) this holds for >= 7/10 seeds.
Otherwise NO-GO with the exact failing condition.

Finite-guarded; strict-serializable via ``serialize_metrics_strict`` /
``assert_json_valid``. Never emits ``{"valid": True}``.
"""

from __future__ import annotations

import argparse
import functools
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy.stats import kurtosis, norm, skew

from src.analytics.strategy_evaluation import (
    assert_json_valid,
    block_bootstrap_ci,
)
from src.backtest.engine import (
    BacktestConfig,
    BacktestEngine,
    RegimeShiftConfig,
    RiskConfig,
    WalkForwardBacktest,
    detect_regime_from_window,
)
from src.campaign.integrated import (
    DEFAULT_SYMBOLS,
    DEFAULT_SPOT,
    DETERMINISTIC_NOW,
    IntegratedConfig,
    _features_for_symbol,
    _generate_price_paths,
    _load_options_chain,
    _load_orderflow,
    _time_varying_signal_series,
)
from src.data.schemas import PricingInputs
from src.features.iv_surface import build_iv_surface_from_chain
from src.features.options_pricing import black_scholes_greeks
from src.signals.composite import CompositeSignalGenerator
from src.telemetry.serialization import serialize_metrics_strict

# Cost-sensitivity grid in bps (one-way transaction cost per trade).
COST_GRID_BPS: Tuple[int, ...] = (0, 1, 5, 10)
# Pre-registered GO gate: minimum fraction of seeds that must pass all conditions.
GO_SEED_FRACTION: float = 0.70
# Minimum walk-forward windows required for a track record to be admissible.
MIN_TRACK_RECORD_WINDOWS: int = 5
# Regime blocks mirroring src/campaign/integrated.py _generate_price_paths.
REGIME_BLOCKS: Tuple[str, ...] = ("trend", "range", "high_vol_chop", "thin")
# Map campaign vol regimes -> RegimeShiftConfig cost-multiplier regime keys.
VOL_REGIME_COST_KEYS = {
    "low_vol": "low_vol",
    "normal": "normal",
    "high_vol": "high_vol",
    "stress": "stress",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _finite(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if math.isfinite(v) else default


def _sharpe_of_returns(rets: List[float], periods_per_year: float = 252.0) -> float:
    vals = [float(r) for r in rets if math.isfinite(float(r))]
    if len(vals) < 2:
        return 0.0
    mean = sum(vals) / len(vals)
    std = math.sqrt(sum((r - mean) ** 2 for r in vals) / len(vals))
    if std <= 0.0 or not math.isfinite(std):
        return 0.0
    sr = mean / std * math.sqrt(periods_per_year)
    return sr if math.isfinite(sr) else 0.0


def _deflated_sharpe(rets: List[float], sr_observed: float, sr_benchmark: float = 0.0) -> float:
    """Bailey-Lopez-Prado deflated Sharpe ratio: P(SR* > SR_observed)."""
    vals = [float(r) for r in rets if math.isfinite(float(r))]
    n = len(vals)
    if n < 3:
        return 0.0
    if not math.isfinite(sr_observed) or not math.isfinite(sr_benchmark):
        return 0.0
    mean = sum(vals) / n
    var = sum((r - mean) ** 2 for r in vals) / n
    std = math.sqrt(var)
    if std <= 0.0 or not math.isfinite(std):
        return 0.0
    sr = mean / std * math.sqrt(252.0)
    if not math.isfinite(sr):
        sr = sr_observed
    try:
        g3 = float(skew(vals))
        g4 = float(kurtosis(vals, fisher=False))
    except Exception:
        g3, g4 = 0.0, 3.0
    if not math.isfinite(g3):
        g3 = 0.0
    if not math.isfinite(g4):
        g4 = 3.0
    try:
        var_term = (1.0 + ((g3 - 1.0) / 4.0) * sr ** 2 + ((g4 - 3.0) / 2.0) * sr ** 4) / (n - 1)
    except Exception:
        return 0.0
    if var_term <= 0.0 or not math.isfinite(var_term):
        return 0.0
    try:
        z = (math.atanh(sr) - math.atanh(sr_benchmark)) / math.sqrt(var_term)
    except Exception:
        return 0.0
    if not math.isfinite(z):
        return 0.0
    return float(1.0 - norm.cdf(z))


def _path_regime(index: int, n_points: int) -> str:
    """Regime block (trend / range / high_vol_chop / thin) covering ``index``."""
    block_len = max(1, n_points // len(REGIME_BLOCKS))
    bi = min(index // block_len, len(REGIME_BLOCKS) - 1)
    return REGIME_BLOCKS[bi]


def _window_regime(test_start: int, test_end: int, n_points: int) -> str:
    """Dominant regime block of a test window (midpoint rule)."""
    mid = (test_start + test_end) // 2
    return _path_regime(mid, n_points)


def _vol_regime(prices: List[float], start: int, end: int) -> str:
    seg = [float(p) for p in prices[max(0, start):end] if _finite(p) > 0]
    return detect_regime_from_window(seg)


def _backtest_config(fee_rate: float, slippage_bps: float, seed: int) -> BacktestConfig:
    return BacktestConfig(
        initial_capital=100000.0,
        fee_rate=float(fee_rate),
        slippage_bps=float(slippage_bps),
        slippage_seed=int(seed),
        risk_free_rate=0.0,
    )


def _risk_config() -> RiskConfig:
    return RiskConfig()


def _run_symbol_walkforward(
    symbol: str,
    prices: List[float],
    signals: List[int],
    timestamps: List[datetime],
    fee_rate: float,
    slippage_bps: float,
    seed: int,
    train_window: int,
    test_window: int,
    step_size: int,
    purge: int,
    embargo: int,
    n_points: int,
) -> Dict[str, Any]:
    """Run OOS walk-forward for one symbol at one cost level."""
    wfb = WalkForwardBacktest(
        purge=purge,
        embargo=embargo,
        config=_backtest_config(fee_rate, slippage_bps, seed),
        risk_config=_risk_config(),
    )
    wfres = wfb.run_walk_forward(
        price_series={symbol: list(prices)},
        signals={symbol: list(signals)},
        timestamps=list(timestamps),
        train_window=train_window,
        test_window=test_window,
        step_size=step_size,
        rolling=True,
        anchored=False,
        min_train_size=40,
        purge=purge,
        embargo=embargo,
    )
    per_window: List[Dict[str, Any]] = []
    regime_buckets: Dict[str, List[float]] = {}
    regime_trades: Dict[str, int] = {}
    for w in wfres.windows:
        r = _finite(w.out_of_sample_return)
        regime = _window_regime(w.test_start, w.test_end, n_points)
        regime_buckets.setdefault(regime, []).append(r)
        regime_trades[regime] = regime_trades.get(regime, 0) + int(getattr(w.oos_metrics, "total_trades", 0) or 0)
        per_window.append(
            {
                "train_start": w.train_start,
                "train_end": w.train_end,
                "test_start": w.test_start,
                "test_end": w.test_end,
                "in_sample_return": _finite(w.in_sample_return),
                "out_of_sample_return": r,
                "out_of_sample_sharpe": _finite(w.out_of_sample_sharpe),
                "regime": regime,
                "vol_regime": _vol_regime(prices, w.test_start, w.test_end),
            }
        )
    returns = [p["out_of_sample_return"] for p in per_window]
    equity = [100000.0]
    for r in returns:
        equity.append(equity[-1] * (1.0 + r))
    total_return = (equity[-1] / equity[0] - 1.0) if equity[0] > 0 else 0.0
    sharpe = _sharpe_of_returns(returns)
    mdd = 0.0
    peak = equity[0]
    for v in equity:
        if v > peak:
            peak = v
        dd = (peak - v) / peak if peak > 0 else 0.0
        if dd > mdd:
            mdd = dd
    regime_perf = {}
    for regime, rs in regime_buckets.items():
        regime_perf[regime] = {
            "num_windows": len(rs),
            "mean_return": sum(rs) / len(rs) if rs else 0.0,
            "sharpe": _sharpe_of_returns(rs),
            "trade_count": int(regime_trades.get(regime, 0)),
        }
    result: Dict[str, Any] = {
        "symbol": symbol,
        "fee_rate": fee_rate,
        "slippage_bps": slippage_bps,
        "num_windows": len(wfres.windows),
        "oos_trade_count": int(len(wfres.oos_trades)),
        "oos_return": float(total_return),
        "oos_sharpe": float(sharpe),
        "oos_max_drawdown": float(mdd),
        "stability_ratio": _finite(wfres.stability_ratio),
        "degradation": _finite(wfres.degradation),
        "traded_notional": float(sum(float(t.price) * float(t.quantity) for t in wfres.oos_trades)),
        "purge": purge,
        "embargo": embargo,
        "train_window": train_window,
        "test_window": test_window,
        "step_size": step_size,
        "per_window_returns": returns,
        "per_window": per_window,
        "oos_equity_curve": [float(v) for v in equity],
        "regime_performance": regime_perf,
        "regime_coverage": {k: len(v) for k, v in regime_buckets.items()},
    }
    assert_json_valid(result)
    return result


def _build_signal_series(
    sym: str,
    prices: List[float],
    static_features: Dict[str, Any],
    static_context: Dict[str, Any],
    seed: int,
) -> Tuple[List[int], List[Dict[str, Any]]]:
    """Build the campaign's time-varying signal series for one symbol."""
    signal_gen = CompositeSignalGenerator()
    signal_gen.reset_regime_state()
    series, diagnostics = _time_varying_signal_series(
        signal_gen,
        sym,
        list(prices),
        static_features,
        static_context["chain"],
        static_context["iv_surface"],
        static_context["greeks_summary"],
    )
    return series, diagnostics


def _static_context(sym: str, spot: float, now: datetime, seed: int) -> Dict[str, Any]:
    chain = _load_options_chain(sym, spot, now, "synthetic")
    of = _load_orderflow(sym, "synthetic")
    try:
        iv_surface = build_iv_surface_from_chain(chain, spot=spot, rate=0.0, now=now, seed=seed)
    except Exception:
        iv_surface = None
    greeks_summary: Optional[Dict[str, Any]] = None
    if chain.quotes:
        atm = min(chain.quotes, key=lambda q: abs(float(q.contract.strike) - spot))
        try:
            texp = max((atm.contract.expiry - now).total_seconds() / 86400.0 / 365.0, 1e-6)
            g = black_scholes_greeks(
                PricingInputs(
                    spot=spot,
                    strike=float(atm.contract.strike),
                    rate=0.0,
                    volatility=_finite(getattr(atm, "mark_iv", None), 0.8),
                    time_to_expiry=texp,
                    option_type=atm.contract.option_type,
                    seed=seed,
                )
            )
            greeks_summary = {"delta": g["delta"], "gamma": g["gamma"], "vega": g["vega"], "theta": g["theta"], "rho": g["rho"]}
        except Exception:
            greeks_summary = None
    features = _features_for_symbol(sym, spot, chain, of, iv_surface, greeks_summary, CompositeSignalGenerator())
    return {"chain": chain, "iv_surface": iv_surface, "greeks_summary": greeks_summary, "features": features}


def _evaluate_seed(
    seed: int,
    n_points: int,
    train_window: int,
    test_window: int,
    step_size: int,
    purge: int,
    embargo: int,
    n_permutations: int,
) -> Dict[str, Any]:
    """Evaluate one seed across BTC/ETH/SOL: gross, net grid, statistics, gate."""
    cfg = IntegratedConfig(seed=seed, n_points=n_points, train_window=train_window,
                           test_window=test_window, step_size=step_size, purge=purge, embargo=embargo)
    now = cfg.fixed_now or DETERMINISTIC_NOW
    price_series, timestamps = _generate_price_paths(cfg)
    per_symbol: Dict[str, Dict[str, Any]] = {}
    static_contexts: Dict[str, Dict[str, Any]] = {}
    for sym in cfg.symbols:
        spot = float(cfg.spot_prices.get(sym, DEFAULT_SPOT[sym]))
        static_contexts[sym] = _static_context(sym, spot, now, seed)
    signals: Dict[str, List[int]] = {}
    for sym in cfg.symbols:
        series, _diag = _build_signal_series(
            sym, price_series[sym], static_contexts[sym]["features"], static_contexts[sym], seed
        )
        signals[sym] = series

    # Gross run (zero cost) and net-of-cost grid per symbol.
    grid: Dict[str, Dict[str, Any]] = {}
    for bps in COST_GRID_BPS:
        fee_rate = bps / 10000.0
        grid[str(bps)] = {}
        for sym in cfg.symbols:
            grid[str(bps)][sym] = _run_symbol_walkforward(
                sym, price_series[sym], signals[sym], timestamps,
                fee_rate, float(bps), seed, train_window, test_window, step_size, purge, embargo, n_points,
            )

    # Portfolio (equal weight across symbols) per cost level: average per-window returns.
    portfolio_by_bps: Dict[str, Dict[str, Any]] = {}
    for bps in COST_GRID_BPS:
        key = str(bps)
        windows_per_sym: Dict[str, List[float]] = {}
        n_windows = 0
        trades = 0
        for sym in cfg.symbols:
            res = grid[key][sym]
            windows_per_sym[sym] = list(res["per_window_returns"])
            n_windows = max(n_windows, res["num_windows"])
            trades += res["oos_trade_count"]
        port_returns: List[float] = []
        for i in range(n_windows):
            vals = [windows_per_sym[s][i] for s in cfg.symbols if i < len(windows_per_sym[s])]
            if vals:
                port_returns.append(sum(vals) / len(vals))
        equity = [100000.0]
        for r in port_returns:
            equity.append(equity[-1] * (1.0 + r))
        total_return = (equity[-1] / equity[0] - 1.0) if equity[0] > 0 else 0.0
        sharpe = _sharpe_of_returns(port_returns)
        mdd = 0.0
        peak = equity[0]
        for v in equity:
            if v > peak:
                peak = v
            dd = (peak - v) / peak if peak > 0 else 0.0
            if dd > mdd:
                mdd = dd
        portfolio_by_bps[key] = {
            "bps": float(bps),
            "fee_rate": bps / 10000.0,
            "slippage_bps": float(bps),
            "num_windows": n_windows,
            "oos_trade_count": int(trades),
            "oos_return": float(total_return),
            "oos_sharpe": float(sharpe),
            "oos_max_drawdown": float(mdd),
            "per_window_returns": port_returns,
            "oos_equity_curve": [float(v) for v in equity],
        }

    gross = portfolio_by_bps["0"]
    net_bps = "1"  # pre-registered net-of-cost baseline (1 bp one-way transaction cost)
    net = portfolio_by_bps[net_bps]

    # Statistical falsification on portfolio per-window net returns.
    rets = list(net["per_window_returns"])
    n_windows = net["num_windows"]
    mean_return = sum(rets) / len(rets) if rets else 0.0
    try:
        ci_return = block_bootstrap_ci(rets, np.mean, seed=seed, n_bootstrap=2000, block_size=min(3, max(1, len(rets))))
        ci_sharpe = block_bootstrap_ci(rets, _sharpe_of_returns, seed=seed + 1, n_bootstrap=2000, block_size=min(3, max(1, len(rets))))
    except Exception:
        ci_return = (mean_return, mean_return, mean_return)
        ci_sharpe = (net["oos_sharpe"], net["oos_sharpe"], net["oos_sharpe"])
    # Percentile bootstrap CIs need not contain the point estimate for small,
    # skewed samples; clamp conservatively so lo <= point <= hi always holds.
    ci_return = (float(ci_return[0]), min(float(ci_return[1]), mean_return), max(float(ci_return[2]), mean_return))
    ci_sharpe = (float(ci_sharpe[0]), min(float(ci_sharpe[1]), net["oos_sharpe"]), max(float(ci_sharpe[2]), net["oos_sharpe"]))
    bootstrap_ci = {
        "mean_net_return": {"point": float(mean_return), "lo": float(ci_return[1]), "hi": float(ci_return[2])},
        "net_sharpe": {"point": float(net["oos_sharpe"]), "lo": float(ci_sharpe[1]), "hi": float(ci_sharpe[2])},
        "n_windows": n_windows,
        "block_size": min(3, max(1, len(rets))),
        "n_bootstrap": 2000,
    }

    # Permutation test: null distribution of portfolio net return under shuffled signals.
    rng = np.random.default_rng(seed)
    null_returns: List[float] = []
    null_sharpes: List[float] = []
    for _ in range(int(n_permutations)):
        perm_symbol_returns: List[List[float]] = []
        perm_trades = 0
        for sym in cfg.symbols:
            perm_series = list(signals[sym])
            for i in range(len(perm_series) - 1, 0, -1):
                j = int(rng.integers(0, i + 1))
                perm_series[i], perm_series[j] = perm_series[j], perm_series[i]
            pres = _run_symbol_walkforward(
                sym, price_series[sym], perm_series, timestamps,
                net["fee_rate"], net["slippage_bps"], seed, train_window, test_window, step_size, purge, embargo, n_points,
            )
            perm_symbol_returns.append(list(pres["per_window_returns"]))
            perm_trades += pres["oos_trade_count"]
        nw = max(len(v) for v in perm_symbol_returns)
        prs: List[float] = []
        for i in range(nw):
            vals = [v[i] for v in perm_symbol_returns if i < len(v)]
            if vals:
                prs.append(sum(vals) / len(vals))
        peq = [100000.0]
        for r in prs:
            peq.append(peq[-1] * (1.0 + r))
        pret = (peq[-1] / peq[0] - 1.0) if peq[0] > 0 else 0.0
        psr = _sharpe_of_returns(prs)
        null_returns.append(float(pret))
        null_sharpes.append(float(psr))
    observed_ret = net["oos_return"]
    p_value = sum(1 for v in null_returns if v >= observed_ret) / len(null_returns) if null_returns else 1.0
    p_value_sharpe = sum(1 for v in null_sharpes if v >= net["oos_sharpe"]) / len(null_sharpes) if null_sharpes else 1.0
    permutation = {
        "n_permutations": int(n_permutations),
        "observed_net_return": float(observed_ret),
        "observed_net_sharpe": float(net["oos_sharpe"]),
        "null_mean_return": float(sum(null_returns) / len(null_returns)) if null_returns else 0.0,
        "null_mean_sharpe": float(sum(null_sharpes) / len(null_sharpes)) if null_sharpes else 0.0,
        "p_value_return": float(p_value),
        "p_value_sharpe": float(p_value_sharpe),
        "significant_at_05": bool(p_value < 0.05),
    }

    # Deflated Sharpe on net per-window returns.
    deflated_sharpe = _deflated_sharpe(rets, net["oos_sharpe"], sr_benchmark=0.0)

    # Regime-conditioned performance at net baseline (path regimes trend/range/high_vol_chop/thin).
    regime_agg: Dict[str, Dict[str, Any]] = {}
    for sym in cfg.symbols:
        for pw in grid[net_bps][sym]["per_window"]:
            regime = pw["regime"]
            bucket = regime_agg.setdefault(regime, {"returns": [], "windows": 0, "trades": 0})
            bucket["returns"].append(pw["out_of_sample_return"])
            bucket["windows"] += 1
            bucket["trades"] += int(pw.get("trade_count", 0) or 0)
    regime_conditioned = {}
    for regime, bucket in regime_agg.items():
        rs = bucket["returns"]
        regime_conditioned[regime] = {
            "num_windows": int(bucket["windows"]),
            "trade_count": int(bucket["trades"]),
            "mean_return": float(sum(rs) / len(rs)) if rs else 0.0,
            "sharpe": float(_sharpe_of_returns(rs)),
            "total_return": float((functools.reduce(lambda a, b: a * (1.0 + b), rs, 1.0) - 1.0)) if rs else 0.0,
        }

    # Regime-dependent cost profile (vol regime -> effective cost bps).
    regime_cost_cfg = RegimeShiftConfig()
    cost_profile: Dict[str, Dict[str, Any]] = {}
    for vol_regime, mult in regime_cost_cfg.cost_multipliers.items():
        cost_profile[vol_regime] = {
            "cost_multiplier": float(mult),
            "effective_cost_bps_net_baseline": float(net["fee_rate"] * 10000.0 * mult),
        }

    # GO/NO-GO gate (per-seed conditions; >= 7/10 seeds must pass).
    bootstrap_lo = float(bootstrap_ci["mean_net_return"]["lo"])
    cond_a = bool(net["oos_sharpe"] > 0.0)
    cond_b = bool(bootstrap_lo > 0.0 or permutation["p_value_return"] < 0.05)
    cond_c = bool(net["oos_return"] > 0.0)
    track_record_ok = bool(n_windows >= MIN_TRACK_RECORD_WINDOWS)
    conditions = {
        "net_sharpe_positive": {"pass": cond_a, "value": float(net["oos_sharpe"]), "criterion": "net Sharpe > 0"},
        "bootstrap_or_permutation": {
            "pass": cond_b,
            "value": float(bootstrap_lo),
            "p_value": float(permutation["p_value_return"]),
            "criterion": "bootstrap lower bound > 0 or permutation p < 0.05",
        },
        "net_return_positive": {"pass": cond_c, "value": float(net["oos_return"]), "criterion": "net return > 0"},
        "admissible_track_record": {
            "pass": track_record_ok,
            "value": float(n_windows),
            "criterion": f"num_windows >= {MIN_TRACK_RECORD_WINDOWS}",
        },
    }
    seed_pass = bool(cond_a and cond_b and cond_c and track_record_ok)
    return {
        "seed": int(seed),
        "symbols": {sym: grid["1"][sym] for sym in cfg.symbols},
        "cost_grid": {k: {kk: vv for kk, vv in v.items() if kk not in ("per_window", "per_window_returns", "oos_equity_curve")} for k, v in portfolio_by_bps.items()},
        "gross": {k: v for k, v in gross.items() if k not in ("per_window", "per_window_returns", "oos_equity_curve")},
        "net": {k: v for k, v in net.items() if k not in ("per_window", "per_window_returns", "oos_equity_curve")},
        "bootstrap_ci": bootstrap_ci,
        "deflated_sharpe": float(deflated_sharpe),
        "permutation": permutation,
        "track_record": {
            "num_windows": int(n_windows),
            "min_track_record_windows": int(MIN_TRACK_RECORD_WINDOWS),
            "admissible": track_record_ok,
            "oos_periods": int(len(rets)),
        },
        "regime_conditioned": regime_conditioned,
        "regime_cost_profile": cost_profile,
        "conditions": conditions,
        "pass": seed_pass,
    }


def evaluate_strategy_falsification(
    seeds: Optional[List[int]] = None,
    n_points: int = 500,
    train_window: int = 120,
    test_window: int = 40,
    step_size: int = 40,
    purge: int = 10,
    embargo: int = 5,
    n_permutations: int = 1000,
) -> Dict[str, Any]:
    """Run net-of-cost OOS falsification across seeds; returns a strict-serializable report."""
    if seeds is None:
        seeds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    seeds = [int(s) for s in seeds]

    per_seed: List[Dict[str, Any]] = []
    passing = 0
    for seed in seeds:
        res = _evaluate_seed(seed, n_points, train_window, test_window, step_size, purge, embargo, n_permutations)
        per_seed.append(res)
        if res["pass"]:
            passing += 1

    total = len(per_seed)
    pass_fraction = passing / total if total else 0.0
    verdict = "GO" if pass_fraction >= GO_SEED_FRACTION else "NO-GO"

    failing_conditions: List[str] = []
    for res in per_seed:
        for name, cond in res["conditions"].items():
            if not bool(cond["pass"]):
                failing_conditions.append(f"seed {res['seed']}: {name}")

    net_sharpes = [float(r["net"]["oos_sharpe"]) for r in per_seed]
    net_returns = [float(r["net"]["oos_return"]) for r in per_seed]
    gross_sharpes = [float(r["gross"]["oos_sharpe"]) for r in per_seed]
    gross_returns = [float(r["gross"]["oos_return"]) for r in per_seed]

    # Cost grid (portfolio level), averaged across seeds.
    cost_grid_agg: Dict[str, Dict[str, Any]] = {}
    for bps in COST_GRID_BPS:
        key = str(bps)
        sh = [r["cost_grid"][key]["oos_sharpe"] for r in per_seed]
        rt = [r["cost_grid"][key]["oos_return"] for r in per_seed]
        cost_grid_agg[key] = {
            "bps": float(bps),
            "mean_net_sharpe": float(sum(sh) / len(sh)) if sh else 0.0,
            "mean_net_return": float(sum(rt) / len(rt)) if rt else 0.0,
        }

    p_values = [float(r["permutation"]["p_value_return"]) for r in per_seed]
    deflated = [float(r["deflated_sharpe"]) for r in per_seed]
    bootstrap_los = [float(r["bootstrap_ci"]["mean_net_return"]["lo"]) for r in per_seed]

    aggregate = {
        "seeds": [int(s) for s in seeds],
        "num_seeds": int(total),
        "seeds_passing": int(passing),
        "pass_fraction": float(pass_fraction),
        "go_seed_fraction": float(GO_SEED_FRACTION),
        "verdict": verdict,
        "mean_net_sharpe": float(sum(net_sharpes) / len(net_sharpes)) if net_sharpes else 0.0,
        "mean_net_return": float(sum(net_returns) / len(net_returns)) if net_returns else 0.0,
        "mean_gross_sharpe": float(sum(gross_sharpes) / len(gross_sharpes)) if gross_sharpes else 0.0,
        "mean_gross_return": float(sum(gross_returns) / len(gross_returns)) if gross_returns else 0.0,
        "sharpe_advancement_vs_gross": float((sum(net_sharpes) / len(net_sharpes)) - (sum(gross_sharpes) / len(gross_sharpes))) if net_sharpes else 0.0,
        "return_advancement_vs_gross": float((sum(net_returns) / len(net_returns)) - (sum(gross_returns) / len(gross_returns))) if net_returns else 0.0,
        "mean_bootstrap_lower_bound": float(sum(bootstrap_los) / len(bootstrap_los)) if bootstrap_los else 0.0,
        "mean_permutation_p_value": float(sum(p_values) / len(p_values)) if p_values else 1.0,
        "mean_deflated_sharpe": float(sum(deflated) / len(deflated)) if deflated else 0.0,
        "failing_conditions": failing_conditions,
    }

    report: Dict[str, Any] = {
        "report_id": "STRATEGY_FALSIFICATION_EVAL_06",
        "generated_at": _utc_now_iso(),
        "config": {
            "seeds": [int(s) for s in seeds],
            "n_points": int(n_points),
            "train_window": int(train_window),
            "test_window": int(test_window),
            "step_size": int(step_size),
            "purge": int(purge),
            "embargo": int(embargo),
            "n_permutations": int(n_permutations),
            "cost_grid_bps": [int(b) for b in COST_GRID_BPS],
            "net_baseline_bps": 1.0,
            "symbols": list(DEFAULT_SYMBOLS),
            "initial_capital": 100000.0,
        },
        "per_seed": per_seed,
        "aggregate": aggregate,
        "cost_grid": cost_grid_agg,
        "gates": {
            "net_sharpe_positive": {
                "pass": bool(aggregate["mean_net_sharpe"] > 0.0),
                "criterion": "mean net Sharpe > 0 across seeds",
            },
            "bootstrap_or_permutation": {
                "pass": bool(aggregate["mean_bootstrap_lower_bound"] > 0.0 or aggregate["mean_permutation_p_value"] < 0.05),
                "criterion": "mean bootstrap lower bound > 0 or mean permutation p < 0.05",
            },
            "net_return_positive": {
                "pass": bool(aggregate["mean_net_return"] > 0.0),
                "criterion": "mean net return > 0 across seeds",
            },
            "seed_majority": {
                "pass": bool(pass_fraction >= GO_SEED_FRACTION),
                "value": float(pass_fraction),
                "criterion": f">= {GO_SEED_FRACTION} of seeds pass all conditions",
            },
        },
        "verdict": verdict,
        "never_valid_true": True,
    }
    assert_json_valid(report)
    return serialize_metrics_strict(report)


def _write_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    agg = report["aggregate"]
    lines.append("# STRATEGY FALSIFICATION REPORT — EVAL-06 (Net-of-Cost OOS Falsification)")
    lines.append("")
    lines.append(f"- Report ID: {report['report_id']}")
    lines.append(f"- Generated at: {report['generated_at']}")
    lines.append(f"- Symbols: {', '.join(report['config']['symbols'])}")
    lines.append(f"- Seeds: {report['config']['seeds']}")
    lines.append(f"- Cost grid (bps): {report['config']['cost_grid_bps']} (net baseline: {report['config']['net_baseline_bps']} bp)")
    lines.append(f"- Permutations: {report['config']['n_permutations']}")
    lines.append("")
    lines.append("## VERDICT")
    lines.append("")
    lines.append(f"## {agg['verdict']}")
    lines.append("")
    lines.append("## Aggregate")
    lines.append("")
    for k in ("num_seeds", "seeds_passing", "pass_fraction", "go_seed_fraction",
              "mean_net_sharpe", "mean_net_return", "mean_gross_sharpe", "mean_gross_return",
              "sharpe_advancement_vs_gross", "return_advancement_vs_gross",
              "mean_bootstrap_lower_bound", "mean_permutation_p_value", "mean_deflated_sharpe"):
        lines.append(f"- {k}: {agg[k]}")
    lines.append("")
    lines.append("## Cost grid (mean net Sharpe / net return across seeds)")
    lines.append("")
    for key in sorted(report["cost_grid"], key=lambda k: float(report["cost_grid"][k]["bps"])):
        v = report["cost_grid"][key]
        lines.append(f"- {v['bps']} bps: net_sharpe={v['mean_net_sharpe']:.6f}, net_return={v['mean_net_return']:.6f}")
    lines.append("")
    lines.append("## Gates")
    lines.append("")
    for k, v in report["gates"].items():
        lines.append(f"- {k}: pass={bool(v['pass'])} | {v['criterion']}")
    lines.append("")
    lines.append("## Failing conditions")
    lines.append("")
    if agg["failing_conditions"]:
        for c in agg["failing_conditions"]:
            lines.append(f"- {c}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Per-seed summary")
    lines.append("")
    for r in report["per_seed"]:
        net = r["net"]
        lines.append(f"- seed {r['seed']}: net_sharpe={net['oos_sharpe']:.6f}, net_return={net['oos_return']:.6f}, "
                     f"max_dd={net['oos_max_drawdown']:.6f}, trades={net['oos_trade_count']}, windows={net['num_windows']}, "
                     f"bootstrap_lo={r['bootstrap_ci']['mean_net_return']['lo']:.6f}, "
                     f"perm_p={r['permutation']['p_value_return']:.4f}, deflated_sharpe={r['deflated_sharpe']:.6f}, "
                     f"pass={bool(r['pass'])}")
    lines.append("")
    lines.append("## Regime-conditioned performance (net baseline, last seed shown structure; see JSON for all seeds)")
    lines.append("")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Net-of-cost OOS falsification + GO/NO-GO certification (EVAL-06)"
    )
    parser.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    parser.add_argument("--n-points", type=int, default=500)
    parser.add_argument("--train-window", type=int, default=120)
    parser.add_argument("--test-window", type=int, default=40)
    parser.add_argument("--step-size", type=int, default=40)
    parser.add_argument("--purge", type=int, default=10)
    parser.add_argument("--embargo", type=int, default=5)
    parser.add_argument("--permutations", type=int, default=1000)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--timestamp", type=str, default=_utc_now_iso())
    args = parser.parse_args(argv)

    ts = args.timestamp.replace(":", "").replace("-", "").replace("T", "").replace("Z", "").split(".")[0]
    stamp = f"{ts[:8]}T{ts[8:14]}Z" if len(ts) >= 14 else ts

    report = evaluate_strategy_falsification(
        seeds=args.seeds,
        n_points=args.n_points,
        train_window=args.train_window,
        test_window=args.test_window,
        step_size=args.step_size,
        purge=args.purge,
        embargo=args.embargo,
        n_permutations=args.permutations,
    )

    print(json.dumps(
        {
            "verdict": report["verdict"],
            "seeds_passing": report["aggregate"]["seeds_passing"],
            "num_seeds": report["aggregate"]["num_seeds"],
            "pass_fraction": report["aggregate"]["pass_fraction"],
            "mean_net_sharpe": report["aggregate"]["mean_net_sharpe"],
            "mean_net_return": report["aggregate"]["mean_net_return"],
            "mean_gross_sharpe": report["aggregate"]["mean_gross_sharpe"],
            "mean_gross_return": report["aggregate"]["mean_gross_return"],
            "sharpe_advancement_vs_gross": report["aggregate"]["sharpe_advancement_vs_gross"],
            "return_advancement_vs_gross": report["aggregate"]["return_advancement_vs_gross"],
            "mean_bootstrap_lower_bound": report["aggregate"]["mean_bootstrap_lower_bound"],
            "mean_permutation_p_value": report["aggregate"]["mean_permutation_p_value"],
            "mean_deflated_sharpe": report["aggregate"]["mean_deflated_sharpe"],
            "failing_conditions": report["aggregate"]["failing_conditions"],
            "cost_grid": report["cost_grid"],
        },
        indent=2,
    ))

    if args.write:
        RESEARCH_STATE = Path("research_state")
        RESEARCH_STATE.mkdir(parents=True, exist_ok=True)
        stem = f"STRATEGY_FALSIFICATION_{stamp}"
        json_path = RESEARCH_STATE / f"{stem}.json"
        md_path = RESEARCH_STATE / f"{stem}.md"
        json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        md_path.write_text(_write_markdown(report) + "\n", encoding="utf-8")
        print(f"Wrote {json_path}")
        print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
