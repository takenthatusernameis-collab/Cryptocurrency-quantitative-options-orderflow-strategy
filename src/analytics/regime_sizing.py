"""Regime-conditional position sizing for the crypto options+orderflow strategy.

Detects the volatility regime (low_vol / normal / high_vol / stress) from the
training price path and scales position size per regime (smaller size in
stress / high_vol). Runs walk-forward backtests comparing regime-conditional
sizing vs flat sizing across seeds, with block-bootstrap CIs and baseline
deltas. Finite-guarded, strict-serializable via
:func:`serialize_metrics_strict` / :func:`assert_json_valid`. No placeholders,
no ``valid=true`` shortcuts, no all-zero-signal pass.

This advances EVAL-02 (evaluation harness) by improving the *strategy itself*
(regime-aware sizing), which is the EVAL-03 objective.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from src.analytics.strategy_evaluation import (
    assert_json_valid,
    block_bootstrap_ci,
    compare_to_baseline,
    compute_metrics,
)
from src.backtest.engine import (
    BacktestConfig,
    BacktestEngine,
    RiskConfig,
    WalkForwardBacktest,
    detect_regime_from_window,
    serialize_metrics_strict,
)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class RegimeSizingConfig:
    """Regime-conditional sizing parameters.

    ``position_size_multipliers`` scales the base position size by regime so
    that stress / high_vol regimes trade smaller size than low_vol / normal.
    All multipliers are finite and > 0.
    """

    regime_labels: List[str] = field(
        default_factory=lambda: ["low_vol", "normal", "high_vol", "stress"]
    )
    detection_window: int = 20
    vol_thresholds: Tuple[float, float, float] = (0.005, 0.015, 0.03)
    position_size_multipliers: Dict[str, float] = field(
        default_factory=lambda: {
            "low_vol": 1.0,
            "normal": 1.0,
            "high_vol": 0.7,
            "stress": 0.4,
        }
    )
    min_confidence_by_regime: Dict[str, float] = field(
        default_factory=lambda: {
            "low_vol": 0.3,
            "normal": 0.35,
            "high_vol": 0.45,
            "stress": 0.6,
        }
    )
    initial_capital: float = 100000.0
    fee_rate: float = 0.0005
    slippage_bps: float = 1.0
    slippage_seed: int = 42
    max_position_pct: float = 0.1
    stop_loss_pct: float = 0.02
    take_profit_pct: float = 0.04
    max_drawdown_limit: float = 0.2
    allow_shorting: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.detection_window, int) or self.detection_window < 1:
            self.detection_window = 20
        if not isinstance(self.vol_thresholds, tuple) or len(self.vol_thresholds) != 3:
            raise ValueError("vol_thresholds must be a 3-tuple")
        for v in self.vol_thresholds:
            if not math.isfinite(float(v)) or float(v) < 0:
                raise ValueError("vol_threshold entries must be finite and >= 0")
        for k, v in self.position_size_multipliers.items():
            fv = float(v)
            if not math.isfinite(fv) or fv <= 0:
                raise ValueError(
                    f"position_size_multipliers[{k!r}] must be finite and > 0, got {v!r}"
                )
        for k, v in self.min_confidence_by_regime.items():
            fv = float(v)
            if not math.isfinite(fv) or not 0.0 < fv <= 1.0:
                raise ValueError(
                    f"min_confidence_by_regime[{k!r}] must be in (0, 1], got {v!r}"
                )


# ---------------------------------------------------------------------------
# Regime-aware engine
# ---------------------------------------------------------------------------

class RegimeSizingEngine(BacktestEngine):
    """BacktestEngine that scales position size by a regime multiplier.

    ``calculate_position_size`` delegates to the parent and multiplies the
    resulting quantity by ``position_size_multiplier``. This is the hook that
    makes regime-conditional sizing actually affect executed notional.
    """

    def __init__(
        self,
        config: BacktestConfig,
        risk_config: RiskConfig,
        position_size_multiplier: float = 1.0,
    ) -> None:
        super().__init__(config=config, risk_config=risk_config)
        mult = float(position_size_multiplier)
        if not math.isfinite(mult) or mult <= 0:
            mult = 1.0
        self.position_size_multiplier: float = mult

    def calculate_position_size(
        self, price: float, side: str = "long", risk_pct: Optional[float] = None
    ) -> float:
        qty = super().calculate_position_size(price, side=side, risk_pct=risk_pct)
        return qty * self.position_size_multiplier


# ---------------------------------------------------------------------------
# Signal / price generation (deterministic, time-varying)
# ---------------------------------------------------------------------------

def momentum_signal(prices: Sequence[float], lookback: int = 20) -> List[int]:
    """Time-varying momentum signal: +1 if price > lookback-back price, -1 if <,
    0 if equal. Never a static snapshot; every index is computed from its own
    lookback window so the signal series is genuinely time-varying."""
    sig: List[int] = []
    for i in range(len(prices)):
        lo = max(0, i - lookback)
        d = prices[i] - prices[lo]
        if d > 0:
            sig.append(1)
        elif d < 0:
            sig.append(-1)
        else:
            sig.append(0)
    return sig


def generate_price_path(
    seed: int,
    n_points: int = 400,
    start_price: float = 50000.0,
    drift: float = 0.0003,
    vol: float = 0.015,
) -> Tuple[List[float], List[datetime]]:
    """Deterministic GBM price path with strictly increasing timestamps.

    Used so the walk-forward always has real, nonzero, time-varying prices
    and signals; no dependence on the legacy integrated.py static-snapshot
    path.
    """
    rng = np.random.default_rng(int(seed))
    prices = [float(start_price)]
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    timestamps = [base]
    for i in range(1, int(n_points)):
        r = float(drift) + float(vol) * float(rng.standard_normal())
        prices.append(prices[-1] * (1.0 + r))
        timestamps.append(base + timedelta(hours=i))
    return prices, timestamps


# ---------------------------------------------------------------------------
# Per-window regime-conditional simulation
# ---------------------------------------------------------------------------

def _make_backtest_config(cfg: RegimeSizingConfig, seed: int) -> BacktestConfig:
    return BacktestConfig(
        initial_capital=cfg.initial_capital,
        fee_rate=cfg.fee_rate,
        slippage_bps=cfg.slippage_bps,
        slippage_seed=int(cfg.slippage_seed) + int(seed),
        risk_free_rate=0.0,
    )


def _make_risk_config(cfg: RegimeSizingConfig) -> RiskConfig:
    return RiskConfig(
        max_position_pct=cfg.max_position_pct,
        stop_loss_pct=cfg.stop_loss_pct,
        take_profit_pct=cfg.take_profit_pct,
        max_drawdown_limit=cfg.max_drawdown_limit,
        allow_shorting=cfg.allow_shorting,
    )


def _simulate_period_with_engine(
    engine: BacktestEngine,
    prices: Sequence[float],
    signals: Sequence[int],
    timestamps: Sequence[datetime],
    start: int,
    end: int,
    symbol: str,
) -> None:
    """Replay signals over [start, end) on a single-symbol engine.

    Mirrors WalkForwardBacktest._simulate_period but for a single symbol so
    the regime engine's overridden calculate_position_size is honoured. Every
    tick enforces SL/TP/drawdown via update_equity_curve.
    """
    n = min(end, len(prices), len(signals), len(timestamps))
    start = max(0, start)
    if start >= n:
        return
    for i in range(start, n):
        price = float(prices[i])
        if not math.isfinite(price) or price <= 0:
            continue
        ts = timestamps[i]
        sig = int(signals[i])
        current_prices = {symbol: price}
        if sig == 1 and symbol not in engine.positions:
            try:
                qty = engine.calculate_position_size(price, side="long")
                if qty > 0 and math.isfinite(qty):
                    engine.execute_trade(symbol, qty, price, "buy", ts)
            except Exception:
                pass
        elif sig == -1:
            if symbol in engine.positions and engine.positions[symbol].side == "long":
                try:
                    pos = engine.positions[symbol]
                    engine.execute_trade(symbol, pos.quantity, price, "sell", ts)
                except Exception:
                    pass
            elif symbol not in engine.positions:
                try:
                    qty = engine.calculate_position_size(price, side="short")
                    if qty > 0 and math.isfinite(qty):
                        engine.execute_trade(symbol, qty, price, "sell", ts)
                except Exception:
                    pass
        # sig == 0 -> hold
        engine.update_equity_curve(current_prices)


def _detect_regime(prices: Sequence[float], cfg: RegimeSizingConfig) -> str:
    return detect_regime_from_window(
        prices,
        window=cfg.detection_window,
        thresholds=cfg.vol_thresholds,
    )


def _regime_multiplier(regime: str, cfg: RegimeSizingConfig) -> float:
    mult = cfg.position_size_multipliers.get(regime, 1.0)
    fv = float(mult)
    if not math.isfinite(fv) or fv <= 0:
        fv = 1.0
    return fv


@dataclass
class RegimeWalkForwardResult:
    """Aggregate result of one regime-conditional or flat walk-forward run."""

    mode: str  # "regime" or "flat"
    num_windows: int
    oos_trade_count: int
    oos_return: float
    oos_sharpe: float
    oos_max_drawdown: float
    oos_equity_curve: List[float]
    metrics: Dict[str, Any]
    regime_coverage: Dict[str, int]
    bootstrap_ci: Dict[str, Any]


def run_walk_forward_mode(
    mode: str,
    prices: Sequence[float],
    signals: Sequence[int],
    timestamps: Sequence[datetime],
    cfg: RegimeSizingConfig,
    seed: int,
    train_window: int = 100,
    test_window: int = 30,
    step_size: int = 30,
) -> RegimeWalkForwardResult:
    """Run walk-forward in either ``regime`` or ``flat`` sizing mode.

    ``regime``: per-window regime detected from train prices; position size
      scaled by regime multiplier. Requires >= 2 windows to be meaningful.
    ``flat``: constant multiplier 1.0 (baseline) via WalkForwardBacktest.
    Returns a RegimeWalkForwardResult with finite metrics.
    """
    symbol = "BTC"
    n = len(prices)
    if n < train_window + test_window + 1:
        raise ValueError(
            f"price path too short: n={n}, need > train_window+test_window={train_window + test_window}"
        )

    config = _make_backtest_config(cfg, seed)
    risk_config = _make_risk_config(cfg)

    if mode == "flat":
        wfb = WalkForwardBacktest(config=config, risk_config=risk_config)
        results = wfb.run_walk_forward(
            price_series={symbol: list(prices)},
            signals={symbol: list(signals)},
            timestamps=list(timestamps),
            train_window=train_window,
            test_window=test_window,
            step_size=step_size,
            rolling=True,
            anchored=False,
            min_train_size=40,
        )
        equity = [float(config.initial_capital)] + [float(v) for v in results.oos_equity_curve]
        trades = [{"pnl": float(t.pnl), "symbol": t.symbol} for t in results.oos_trades]
        metrics = compute_metrics(equity, trades=trades)
        rets: List[float] = []
        for i in range(1, len(equity)):
            prev = equity[i - 1]
            if prev == 0:
                continue
            rets.append((equity[i] - prev) / prev)
        ci = block_bootstrap_ci(rets, np.mean, seed=seed, n_bootstrap=500, block_size=10)
        bootstrap_ci = {
            "mean_period_return": ci[0],
            "ci_lo": ci[1],
            "ci_hi": ci[2],
            "n_returns": len(rets),
        }
        return RegimeWalkForwardResult(
            mode="flat",
            num_windows=len(results.windows),
            oos_trade_count=len(results.oos_trades),
            oos_return=float(results.overall_out_of_sample_return),
            oos_sharpe=float(results.overall_out_of_sample_sharpe),
            oos_max_drawdown=float(results.overall_out_of_sample_max_drawdown),
            oos_equity_curve=equity,
            metrics=metrics,
            regime_coverage=dict(results.regime_shift_coverage),
            bootstrap_ci=bootstrap_ci,
        )

    # --- regime mode: per-window regime-conditional sizing ---
    regime_config = cfg
    all_equity: List[float] = [float(config.initial_capital)]
    all_trades: List[Any] = []
    regime_coverage: Dict[str, int] = {}
    window_idx = 0
    train_start = 0
    while True:
        train_end = train_start + train_window
        if train_end >= n:
            break
        test_start = train_end
        test_end = min(test_start + test_window, n)
        if test_start >= test_end:
            break
        train_prices = prices[train_start:train_end]
        regime = _detect_regime(train_prices, regime_config)
        multiplier = _regime_multiplier(regime, regime_config)
        regime_coverage[regime] = regime_coverage.get(regime, 0) + 1

        engine = RegimeSizingEngine(
            config=config, risk_config=risk_config, position_size_multiplier=multiplier
        )
        _simulate_period_with_engine(
            engine,
            prices,
            signals,
            timestamps,
            test_start,
            test_end,
            symbol,
        )
        if engine.equity_curve:
            # Concatenate OOS equity (skip first point to avoid duplication)
            for eq in engine.equity_curve[1:]:
                all_equity.append(float(eq))
        all_trades.extend(engine.trades)
        train_start += step_size
        window_idx += 1
        if window_idx > 10000:
            break

    equity = all_equity
    trades = [{"pnl": float(t.pnl), "symbol": t.symbol} for t in all_trades]
    metrics = compute_metrics(equity, trades=trades)
    rets: List[float] = []
    for i in range(1, len(equity)):
        prev = equity[i - 1]
        if prev == 0:
            continue
        rets.append((equity[i] - prev) / prev)
    ci = block_bootstrap_ci(rets, np.mean, seed=seed, n_bootstrap=500, block_size=10)
    bootstrap_ci = {
        "mean_period_return": ci[0],
        "ci_lo": ci[1],
        "ci_hi": ci[2],
        "n_returns": len(rets),
    }

    # Aggregate OOS metrics from the concatenated equity curve via a temp engine.
    eng = BacktestEngine(config=config, risk_config=risk_config)
    eng.equity_curve = equity
    eng.trades = all_trades
    agg = eng.calculate_metrics()

    return RegimeWalkForwardResult(
        mode="regime",
        num_windows=window_idx,
        oos_trade_count=len(all_trades),
        oos_return=float(agg.total_return),
        oos_sharpe=float(agg.sharpe_ratio),
        oos_max_drawdown=float(agg.max_drawdown),
        oos_equity_curve=equity,
        metrics=metrics,
        regime_coverage=regime_coverage,
        bootstrap_ci=bootstrap_ci,
    )


# ---------------------------------------------------------------------------
# Multi-seed evaluation: regime vs flat
# ---------------------------------------------------------------------------

@dataclass
class RegimeSizingEvaluation:
    """Aggregated regime-conditional sizing evaluation across seeds."""

    seeds: List[int]
    per_seed: List[Dict[str, Any]]
    regime_avg: Dict[str, float]
    flat_avg: Dict[str, float]
    delta: Dict[str, float]
    comparison: Dict[str, Any]
    gates: Dict[str, Any]
    verdict: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seeds": self.seeds,
            "per_seed": self.per_seed,
            "regime_avg": self.regime_avg,
            "flat_avg": self.flat_avg,
            "delta": self.delta,
            "comparison": self.comparison,
            "gates": self.gates,
            "verdict": self.verdict,
        }

    def serialize(self) -> Dict[str, Any]:
        assert_json_valid(self.to_dict())
        return serialize_metrics_strict(self.to_dict())


def evaluate_regime_sizing(
    seeds: Optional[List[int]] = None,
    n_points: int = 400,
    train_window: int = 100,
    test_window: int = 30,
    step_size: int = 30,
    lookback: int = 20,
    cfg: Optional[RegimeSizingConfig] = None,
) -> RegimeSizingEvaluation:
    """Run regime-conditional vs flat sizing across seeds and compare.

    For each seed: generate a deterministic price path + time-varying momentum
    signal, run flat (baseline) and regime walk-forwards, compute metrics +
    block-bootstrap CI. Aggregate across seeds and run compare_to_baseline
    (regime vs flat). Returns a RegimeSizingEvaluation with real cited numbers.

    A run that yields 0 windows / 0 trades / 0 return is treated as failure
    (the gates reflect this).
    """
    if seeds is None:
        seeds = [1, 2, 3, 4, 5]
    if cfg is None:
        cfg = RegimeSizingConfig()

    per_seed: List[Dict[str, Any]] = []
    regime_rows: List[Dict[str, float]] = []
    flat_rows: List[Dict[str, float]] = []

    for seed in seeds:
        prices, timestamps = generate_price_path(seed, n_points=n_points)
        signals = momentum_signal(prices, lookback=lookback)

        flat = run_walk_forward_mode(
            "flat", prices, signals, timestamps, cfg, seed,
            train_window=train_window, test_window=test_window, step_size=step_size,
        )
        regime = run_walk_forward_mode(
            "regime", prices, signals, timestamps, cfg, seed,
            train_window=train_window, test_window=test_window, step_size=step_size,
        )

        per_seed.append(
            {
                "seed": seed,
                "num_windows": regime.num_windows,
                "oos_trade_count": regime.oos_trade_count,
                "regime": {
                    "oos_return": regime.oos_return,
                    "oos_sharpe": regime.oos_sharpe,
                    "oos_max_drawdown": regime.oos_max_drawdown,
                    "regime_coverage": regime.regime_coverage,
                    "bootstrap_ci": regime.bootstrap_ci,
                },
                "flat": {
                    "oos_return": flat.oos_return,
                    "oos_sharpe": flat.oos_sharpe,
                    "oos_max_drawdown": flat.oos_max_drawdown,
                    "regime_coverage": flat.regime_coverage,
                    "bootstrap_ci": flat.bootstrap_ci,
                },
            }
        )
        regime_rows.append(
            {
                "oos_return": regime.oos_return,
                "oos_sharpe": regime.oos_sharpe,
                "oos_max_drawdown": regime.oos_max_drawdown,
            }
        )
        flat_rows.append(
            {
                "oos_return": flat.oos_return,
                "oos_sharpe": flat.oos_sharpe,
                "oos_max_drawdown": flat.oos_max_drawdown,
            }
        )

    def _avg(rows: List[Dict[str, float]], key: str) -> float:
        vals = [float(r[key]) for r in rows if key in r and math.isfinite(float(r[key]))]
        return sum(vals) / len(vals) if vals else 0.0

    regime_avg = {k: _avg(regime_rows, k) for k in ("oos_return", "oos_sharpe", "oos_max_drawdown")}
    flat_avg = {k: _avg(flat_rows, k) for k in ("oos_return", "oos_sharpe", "oos_max_drawdown")}

    delta = {
        "oos_return_delta": regime_avg["oos_return"] - flat_avg["oos_return"],
        "oos_sharpe_delta": regime_avg["oos_sharpe"] - flat_avg["oos_sharpe"],
        "max_drawdown_delta": regime_avg["oos_max_drawdown"] - flat_avg["oos_max_drawdown"],
    }

    comparison = compare_to_baseline(
        {
            "sharpe": regime_avg["oos_sharpe"],
            "total_return": regime_avg["oos_return"],
            "max_drawdown": regime_avg["oos_max_drawdown"],
        },
        {
            "sharpe": flat_avg["oos_sharpe"],
            "total_return": flat_avg["oos_return"],
            "max_drawdown": flat_avg["oos_max_drawdown"],
        },
    )

    total_trades = sum(int(p["oos_trade_count"]) for p in per_seed)
    total_windows = sum(int(p["num_windows"]) for p in per_seed)
    regime_ret = regime_avg["oos_return"]
    regime_sharpe = regime_avg["oos_sharpe"]

    gates: Dict[str, Any] = {
        "nonzero_windows": {
            "pass": bool(total_windows > 0),
            "value": float(total_windows),
            "criterion": "total walk-forward windows > 0 across all seeds",
        },
        "nonzero_trades": {
            "pass": bool(total_trades > 0),
            "value": float(total_trades),
            "criterion": "total OOS trade count > 0 across all seeds",
        },
        "nonzero_regime_oos_return": {
            "pass": bool(regime_ret != 0.0),
            "value": regime_ret,
            "criterion": "regime-conditional aggregate OOS return != 0",
        },
        "finite_regime_metrics": {
            "pass": bool(
                math.isfinite(regime_ret)
                and math.isfinite(regime_sharpe)
                and math.isfinite(regime_avg["oos_max_drawdown"])
            ),
            "value": regime_sharpe,
            "criterion": "regime Sharpe / return / max-dd all finite",
        },
        "beats_flat_sharpe": {
            "pass": bool(regime_sharpe > flat_avg["oos_sharpe"]),
            "value": delta["oos_sharpe_delta"],
            "criterion": "regime Sharpe > flat sizing Sharpe",
        },
    }
    all_pass = all(g["pass"] for g in gates.values())
    verdict = "GO" if all_pass else "NO-GO"

    return RegimeSizingEvaluation(
        seeds=list(seeds),
        per_seed=per_seed,
        regime_avg=regime_avg,
        flat_avg=flat_avg,
        delta=delta,
        comparison=comparison,
        gates=gates,
        verdict=verdict,
    )


def main(argv: Optional[List[str]] = None) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Regime-conditional vs flat sizing walk-forward evaluation (EVAL-03)"
    )
    parser.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3, 4, 5])
    parser.add_argument("--n-points", type=int, default=400)
    parser.add_argument("--train-window", type=int, default=100)
    parser.add_argument("--test-window", type=int, default=30)
    parser.add_argument("--step-size", type=int, default=30)
    parser.add_argument("--lookback", type=int, default=20)
    parser.add_argument("--write", action="store_true")
    parser.add_argument(
        "--timestamp", type=str, default=datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )
    args = parser.parse_args(argv)

    eval_result = evaluate_regime_sizing(
        seeds=args.seeds,
        n_points=args.n_points,
        train_window=args.train_window,
        test_window=args.test_window,
        step_size=args.step_size,
        lookback=args.lookback,
    )
    report = eval_result.serialize()
    print(
        json.dumps(
            {
                "verdict": report["verdict"],
                "regime_sharpe": report["regime_avg"]["oos_sharpe"],
                "regime_return": report["regime_avg"]["oos_return"],
                "regime_max_drawdown": report["regime_avg"]["oos_max_drawdown"],
                "flat_sharpe": report["flat_avg"]["oos_sharpe"],
                "flat_return": report["flat_avg"]["oos_return"],
                "sharpe_delta": report["delta"]["oos_sharpe_delta"],
                "total_windows": sum(int(p["num_windows"]) for p in report["per_seed"]),
                "total_trades": sum(int(p["oos_trade_count"]) for p in report["per_seed"]),
                "gates_pass": all(g["pass"] for g in report["gates"].values()),
            },
            indent=2,
        )
    )

    if args.write:
        from pathlib import Path

        RESEARCH_STATE = Path("research_state")
        RESEARCH_STATE.mkdir(parents=True, exist_ok=True)
        stem = f"REGIME_SIZING_{args.timestamp.replace(':', '')}"
        json_path = RESEARCH_STATE / f"{stem}.json"
        json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(f"Wrote {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
