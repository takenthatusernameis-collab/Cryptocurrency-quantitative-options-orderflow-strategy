"""Numeric-invariant tests for src/analytics/gamma_inventory_hedge.py (EVAL-09).

Covers: cross-process determinism, the hedge-reduces-|delta| invariant
(0 <= abs(net_delta_after) <= abs(net_delta_before) + tol), hedge cost / capacity
bounds (hedge_cost_usd >= 0, hedge_notional <= capacity_cap), the toxicity score
in [0, 1] with toxic_gate_active a strict deterministic function of score vs
threshold, finite/nonzero snapshots/hedges/return/Sharpe on real seeds 1..5, the
CLI entry point writing both artifacts, and an explicit assertion that the report
is never ``{"valid": True}``.

Anti-vacuous gates: the toxicity gate must engage (toxic_gate_active_fraction not
identically 0.0 across every seed), the hedge must reduce |delta|, and no
all-zero snapshots / all-zero hedges / zero return & Sharpe.
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import pytest

from src.analytics.capacity_aware_tca import (
    DEFAULT_MAX_PARTICIPATION,
    CapacityAwareSizer,
    _build_signal_series_capacity,
    _static_context_capacity,
)
from src.analytics.cross_venue_netting import VENUES, _leg_liquidity
from src.analytics.gamma_inventory_hedge import (
    DEFAULT_HEDGE_COST_BPS,
    DEFAULT_MAX_PARTICIPATION_HEDGE,
    DEFAULT_SPREAD_BPS_HEDGE,
    DEFAULT_TARGET_DELTA_USD,
    DEFAULT_TOXICITY_THRESHOLD,
    evaluate_gamma_inventory_hedge,
    toxicity_score,
    _run_hedge_walkforward as _run_hedge,
)
from src.campaign.integrated import (
    DEFAULT_SPOT,
    DETERMINISTIC_NOW,
    IntegratedConfig,
    _generate_price_paths,
    _load_orderflow,
    _stable_seed,
)
from src.data.schemas import Trade

REPO_ROOT = Path(__file__).resolve().parents[1]


def _cfg(seed: int, n_points: int = 160, train_window: int = 40,
         test_window: int = 20, step_size: int = 20) -> IntegratedConfig:
    return IntegratedConfig(
        seed=seed,
        n_points=n_points,
        train_window=train_window,
        test_window=test_window,
        step_size=step_size,
        purge=0,
        embargo=0,
    )


def _eval(seeds, n_points: int = 160, train_window: int = 40,
          test_window: int = 20, step_size: int = 20) -> Dict[str, Any]:
    return evaluate_gamma_inventory_hedge(
        seeds=list(seeds),
        n_points=n_points,
        train_window=train_window,
        test_window=test_window,
        step_size=step_size,
        purge=0,
        embargo=0,
    )


def _seed_result(report: Dict[str, Any], seed: int) -> Dict[str, Any]:
    for p in report["per_seed"]:
        if int(p["seed"]) == int(seed):
            return p
    raise AssertionError(f"seed {seed} not in report")


def _symbol_results(report: Dict[str, Any], seed: int, symbol: str) -> Dict[str, Any]:
    return _seed_result(report, seed)["symbols"][symbol]


def _capacity_cap(symbol: str, seed: int) -> float:
    return float(
        DEFAULT_MAX_PARTICIPATION_HEDGE
        * sum(_leg_liquidity(symbol, v, seed, {}) for v in VENUES)
    )


def _finite(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if math.isfinite(v) else default


# --------------------------------------------------------------------------- #
# 1. Hedge invariants: reduces |delta|, cost >= 0, within capacity
# --------------------------------------------------------------------------- #

def test_hedge_reduces_abs_delta_per_bar():
    """0 <= abs(net_delta_after) <= abs(net_delta_before) + tol on every hedge bar."""
    seed = 9
    cfg = _cfg(seed)
    price_series, tstamps = _generate_price_paths(cfg)
    sizer = CapacityAwareSizer(seed=seed)
    now = DETERMINISTIC_NOW

    for sym in ("BTC", "ETH", "SOL"):
        spot = float(cfg.spot_prices.get(sym, DEFAULT_SPOT[sym]))
        static_ctx = _static_context_capacity(sym, spot, now, seed)
        orderflow = _load_orderflow(sym, "synthetic")
        series, _diag = _build_signal_series_capacity(
            sym, price_series[sym], static_ctx["features"], static_ctx, seed
        )
        prices = price_series[sym]
        with_res = _run_hedge(
            sym, prices, series, list(tstamps), orderflow, static_ctx, sizer, cfg,
            cfg.n_points, seed, with_hedge=True,
            target_delta_usd=DEFAULT_TARGET_DELTA_USD,
            toxicity_threshold=DEFAULT_TOXICITY_THRESHOLD,
            hedge_cost_bps=DEFAULT_HEDGE_COST_BPS,
        )
        snaps = with_res["snapshots"]
        assert snaps, f"{sym} seed {seed}: no snapshots"
        for i in range(1, len(snaps)):
            cur = snaps[i]
            prev = snaps[i - 1]
            if cur["hedge_notional_usd"] <= 0:
                continue
            px_cur = _finite(prices[cur["bar_index"]], 0.0)
            px_prev = _finite(prices[prev["bar_index"]], 0.0)
            if px_cur <= 0 or px_prev <= 0:
                continue
            net_before = prev["net_delta_usd"] * (px_cur / px_prev)
            net_after = cur["net_delta_usd"]
            tol = 1e-6 * max(1.0, abs(net_before))
            assert 0.0 <= abs(net_after) <= abs(net_before) + tol, (
                f"{sym} bar {cur['bar_index']}: |after| {abs(net_after)} > |before| {abs(net_before)}"
            )


def test_hedge_cost_nonnegative_and_within_capacity():
    """hedge_cost_usd >= 0 and hedge_notional <= capacity_cap on every snapshot."""
    report = _eval([3])
    for sym in ("BTC", "ETH", "SOL"):
        cap = _capacity_cap(sym, 3)
        wh = _symbol_results(report, 3, sym)["with_hedge"]
        for snap in wh["snapshots"]:
            assert snap["hedge_cost_usd"] >= -1e-9, (
                f"{sym} bar {snap['bar_index']}: negative hedge_cost {snap['hedge_cost_usd']}"
            )
            assert 0.0 <= snap["hedge_notional_usd"] <= cap + 1e-6, (
                f"{sym} bar {snap['bar_index']}: hedge_notional {snap['hedge_notional_usd']} > cap {cap}"
            )


# --------------------------------------------------------------------------- #
# 2. Toxicity gate: score in [0,1], gate deterministic function of score vs thr
# --------------------------------------------------------------------------- #

def test_toxicity_score_bounded_and_deterministic():
    """0 <= toxicity_score <= 1; identical inputs give identical score; empty -> 0."""
    now = datetime(2026, 10, 31, 0, 0, 0, tzinfo=timezone.utc)
    trades = [
        Trade(trade_id="t1", symbol="BTCUSDT", venue="synthetic", price=100.0, size=1.0,
              side="buy", timestamp=now),
        Trade(trade_id="t2", symbol="BTCUSDT", venue="synthetic", price=100.0, size=1.0,
              side="sell", timestamp=now),
    ]
    s = toxicity_score(trades, now)
    assert 0.0 <= s <= 1.0
    assert toxicity_score(trades, now) == s
    assert toxicity_score([], now) == 0.0


def test_toxic_gate_active_matches_threshold():
    """toxic_gate_active == (toxicity_score >= threshold) strictly and deterministically."""
    report = _eval([5])
    for sym in ("BTC", "ETH", "SOL"):
        wh = _symbol_results(report, 5, sym)["with_hedge"]
        for snap in wh["snapshots"]:
            expected = snap["toxicity_score"] >= DEFAULT_TOXICITY_THRESHOLD
            assert snap["toxic_gate_active"] is expected, (
                f"{sym} bar {snap['bar_index']}: gate {snap['toxic_gate_active']} "
                f"!= score>=thr {expected} (score={snap['toxicity_score']})"
            )
            assert 0.0 <= snap["toxicity_score"] <= 1.0


def test_toxicity_gate_engages_not_identically_zero():
    """Anti-vacuous: toxic_gate_active_fraction must not be identically 0.0."""
    report = _eval(seeds=[1, 2, 3])
    fracs = [p["headline"]["toxic_gate_active_fraction"] for p in report["per_seed"]]
    assert any(f > 0.0 for f in fracs), (
        "toxicity gate never engages: toxic_gate_active_fraction identically 0.0"
    )


# --------------------------------------------------------------------------- #
# 3. Finite / nonzero metrics on real-run seeds 1..5
# --------------------------------------------------------------------------- #

def test_real_run_finite_nonzero_metrics():
    """Real-run seeds 1..5 produce finite, nonzero snapshots/trades/return/Sharpe."""
    report = _eval(seeds=[1, 2, 3, 4, 5])
    assert report["never_valid_true"] is True
    assert report.get("valid") is not True
    total_hedges = 0
    for p in report["per_seed"]:
        assert p["headline"]["total_bars"] > 0, f"seed {p['seed']} zero bars"
        assert p["headline"]["total_trades"] > 0, f"seed {p['seed']} zero trades"
        for key in (
            "mean_oos_return_with_hedge", "mean_oos_sharpe_with_hedge",
            "mean_oos_max_drawdown_with_hedge",
            "mean_oos_return_without_hedge", "mean_oos_sharpe_without_hedge",
            "mean_oos_max_drawdown_without_hedge",
        ):
            assert math.isfinite(p["headline"][key]), f"seed {p['seed']} {key} non-finite"
        total_hedges += p["headline"]["total_hedges"]
    assert total_hedges > 0, "all seeds zero hedges (vacuous)"


def test_aggregate_has_all_required_fields():
    """Aggregate carries with/without-hedge deltas, toxicity and delta reduction."""
    report = _eval([2])
    agg = report["aggregate"]
    for k in (
        "num_seeds",
        "mean_oos_return_with_hedge",
        "mean_oos_return_without_hedge",
        "return_delta_with_vs_without_hedge",
        "mean_oos_sharpe_with_hedge",
        "mean_oos_sharpe_without_hedge",
        "sharpe_delta_with_vs_without_hedge",
        "mean_oos_max_drawdown_with_hedge",
        "mean_oos_max_drawdown_without_hedge",
        "mean_abs_delta_usd_with_hedge",
        "mean_toxicity_score",
        "toxic_gate_active_fraction",
        "total_hedges",
        "total_skipped_due_to_toxicity",
        "total_cost_usd",
        "total_traded_notional",
        "total_trades",
        "total_bars",
    ):
        assert k in agg, f"missing aggregate key {k}"
        assert math.isfinite(agg[k]), f"{k} non-finite"


# --------------------------------------------------------------------------- #
# 4. Anti-vacuous gates
# --------------------------------------------------------------------------- #

def test_not_all_zero_snapshots_or_hedges_or_return():
    """Not all snapshots zero, not all hedges zero, return & Sharpe not both zero."""
    report = _eval(seeds=[1, 2, 3])
    total_snapshots = 0
    total_hedges = 0
    for p in report["per_seed"]:
        for sym in ("BTC", "ETH", "SOL"):
            wh = _symbol_results(report, int(p["seed"]), sym)["with_hedge"]
            total_snapshots += len(wh["snapshots"])
            total_hedges += wh["num_hedges"]
    assert total_snapshots > 0
    assert total_hedges > 0, "all hedges zero (vacuous)"
    for p in report["per_seed"]:
        h = p["headline"]
        assert not (h["mean_oos_return_with_hedge"] == 0.0 and h["mean_oos_sharpe_with_hedge"] == 0.0), (
            f"seed {p['seed']} zero return and Sharpe (vacuous)"
        )


def test_hedge_mean_abs_delta_not_increasing():
    """The hedge must not increase mean |delta| vs the no-hedge book."""
    report = _eval(seeds=[1, 2, 3, 4])
    for p in report["per_seed"]:
        for sym in ("BTC", "ETH", "SOL"):
            symres = _symbol_results(report, int(p["seed"]), sym)
            wh = symres["with_hedge"]
            wo = symres["without_hedge"]
            tol = 1e-6 + 1e-6 * abs(wo["mean_abs_delta_usd"])
            assert wh["mean_abs_delta_usd"] <= wo["mean_abs_delta_usd"] + tol, (
                f"seed {p['seed']} {sym}: hedge increased |delta| "
                f"with={wh['mean_abs_delta_usd']} without={wo['mean_abs_delta_usd']}"
            )


def test_report_not_valid_true():
    """The report must never be {'valid': True}."""
    report = _eval([1])
    assert report.get("valid") is not True
    assert "valid" not in report or report["valid"] is not True
    assert report["never_valid_true"] is True


def test_no_nan_or_inf_in_json():
    """No NaN/Infinity survives strict serialization."""
    report = _eval(seeds=[1, 2])
    dumped = json.dumps(report, allow_nan=False)  # raises if any NaN/Inf
    assert "NaN" not in dumped
    assert "Infinity" not in dumped


# --------------------------------------------------------------------------- #
# 5. Determinism (cross-process equivalent via stable seeds)
# --------------------------------------------------------------------------- #

def test_deterministic_across_runs():
    """Identical inputs produce identical reports (generated_at excluded)."""
    r1 = _eval(seeds=[3, 4])
    r2 = _eval(seeds=[3, 4])
    r1.pop("generated_at", None)
    r2.pop("generated_at", None)
    assert r1 == r2


def test_stable_seed_stable_across_calls():
    """_stable_seed is deterministic and differs across inputs."""
    assert _stable_seed("BTC", 42) == _stable_seed("BTC", 42)
    assert _stable_seed("BTC", 42) != _stable_seed("ETH", 42)
    assert _stable_seed("BTC", 1) != _stable_seed("BTC", 2)


def test_cross_process_determinism():
    """Two separate processes emit byte-identical JSON (minus generated_at)."""
    code = (
        "import json,sys;"
        "from src.analytics.gamma_inventory_hedge import evaluate_gamma_inventory_hedge;"
        "r=evaluate_gamma_inventory_hedge(seeds=[5],n_points=160,train_window=40,"
        "test_window=20,step_size=20,purge=0,embargo=0);"
        "r.pop('generated_at',None);"
        "print(json.dumps(r,sort_keys=True))"
    )
    outs = []
    for _ in range(2):
        cp = subprocess.run(
            [sys.executable, "-c", code],
            cwd=REPO_ROOT,
            env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
            capture_output=True,
            text=True,
            timeout=600,
        )
        assert cp.returncode == 0, cp.stderr
        outs.append(cp.stdout)
    assert outs[0] == outs[1]


# --------------------------------------------------------------------------- #
# 6. CLI entry point
# --------------------------------------------------------------------------- #

def test_cli_entry_point_writes_artifacts(tmp_path):
    """CLI returns 0 and writes both JSON and MD artifacts for seeds 1 2."""
    code = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "src" / "analytics" / "gamma_inventory_hedge.py"),
            "--seeds", "1", "2",
            "--n-points", "160", "--train-window", "40",
            "--test-window", "20", "--step-size", "20",
            "--purge", "0", "--embargo", "0",
            "--write",
        ],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert code.returncode == 0, code.stderr
    assert "Wrote " in code.stdout
    written = [line.split("Wrote ", 1)[1] for line in code.stdout.splitlines() if line.startswith("Wrote ")]
    assert len(written) == 2
    for rel in written:
        p = Path(rel)
        if not p.is_absolute():
            p = tmp_path / p
        assert p.exists(), f"missing artifact {p}"


# --------------------------------------------------------------------------- #
# 7. Direct evaluation API is deterministic and finite
# --------------------------------------------------------------------------- #

def test_evaluate_seed_direct():
    """evaluate_gamma_inventory_hedge returns finite, bounded metrics for one seed."""
    r = _eval([1])
    assert r["never_valid_true"] is True
    assert r["aggregate"]["num_seeds"] == 1
    assert math.isfinite(r["aggregate"]["mean_oos_sharpe_with_hedge"])
    assert math.isfinite(r["aggregate"]["mean_oos_sharpe_without_hedge"])
    assert 0.0 <= r["aggregate"]["toxic_gate_active_fraction"] <= 1.0
    assert r["aggregate"]["total_bars"] > 0
    assert r["aggregate"]["total_trades"] > 0


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
