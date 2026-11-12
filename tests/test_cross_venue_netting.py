"""Numeric-invariant tests for src/analytics/cross_venue_netting.py (EVAL-08).

Covers: cross-process determinism, the ``0 <= net <= gross`` invariant (per window
and aggregate), the ``cost_saved >= 0`` invariant, the per-venue capacity clamp
(filled notional never exceeds ``max_participation * liquidity``), turnover in
``[0, 2]``, finite/nonzero windows/trades/return/Sharpe on the real seeds 1..5, the
CLI entry point writing both artifacts, and an explicit assertion that the report is
never ``{"valid": True}``.

Anti-vacuous gates: the netting ratio must NOT be identically 1.0 across every
window, and no window may be all-zero with zero trades.
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path

import pytest

from src.analytics.capacity_aware_tca import DEFAULT_MAX_PARTICIPATION
from src.analytics.cross_venue_netting import (
    INITIAL_CAPITAL,
    VENUES,
    VenueLeg,
    _evaluate_seed_netting,
    _leg_liquidity,
    _run_netting_walkforward,
    evaluate_cross_venue_netting,
    net_notional_of,
    price_legs_with_capacity,
    split_venue_legs,
    venue_mix,
)
from src.analytics.capacity_aware_tca import CapacityAwareSizer
from src.campaign.integrated import (
    DEFAULT_SPOT,
    IntegratedConfig,
    _generate_price_paths,
    _stable_seed,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _evaluate(seeds, n_points=160, train_window=40, test_window=20, step_size=20):
    return evaluate_cross_venue_netting(
        seeds=seeds,
        n_points=n_points,
        train_window=train_window,
        test_window=test_window,
        step_size=step_size,
        purge=0,
        embargo=0,
    )


def _all_windows(report):
    for r in report["per_seed"]:
        for sym, res in r["symbols"].items():
            for win in res["per_window"]:
                yield r["seed"], sym, win


# --------------------------------------------------------------------------- #
# 1. Gross vs net notional invariants
# --------------------------------------------------------------------------- #

def test_net_notional_bounded_by_gross_per_window():
    """0 <= net_notional <= gross_notional for every window and aggregate."""
    report = _evaluate(seeds=[1, 2])
    for _seed, _sym, win in _all_windows(report):
        assert 0.0 <= win["net_notional"] <= win["gross_notional"] + 1e-6, (
            f"net {win['net_notional']} out of [0, gross {win['gross_notional']}]"
        )
    for r in report["per_seed"]:
        assert 0.0 <= r["net_notional"] <= r["gross_notional"] + 1e-6
        assert 0.0 <= r["net_notional_ratio"] <= 1.0 + 1e-9


def test_netting_benefit_equals_gross_minus_net():
    """netting_benefit == gross - net and is non-negative."""
    report = _evaluate(seeds=[1])
    for _seed, _sym, win in _all_windows(report):
        benefit = win["gross_notional"] - win["net_notional"]
        assert win["netting_benefit"] == pytest.approx(benefit, abs=1e-6)
        assert win["netting_benefit"] >= -1e-9


def test_net_notional_ratio_definition():
    """ratio == net / gross (or 1.0 when gross == 0)."""
    report = _evaluate(seeds=[1])
    for _seed, _sym, win in _all_windows(report):
        if win["gross_notional"] > 0:
            expected = win["net_notional"] / win["gross_notional"]
            assert win["net_notional_ratio"] == pytest.approx(expected, rel=1e-9, abs=1e-12)


# --------------------------------------------------------------------------- #
# 2. Cost saved invariant
# --------------------------------------------------------------------------- #

def test_cost_saved_non_negative_per_window_and_aggregate():
    """cost_saved_usd >= 0 per window and in aggregate."""
    report = _evaluate(seeds=[1, 2])
    for _seed, _sym, win in _all_windows(report):
        assert win["cost_saved_usd"] >= -1e-9, f"negative cost_saved: {win['cost_saved_usd']}"
        # cost_no_net = gross * bps / 1e4, cost_net = net * bps / 1e4
        assert win["cost_no_net_usd"] >= win["cost_net_usd"] - 1e-9
    for r in report["per_seed"]:
        assert r["cost_saved_usd"] >= -1e-9


def test_cost_saved_equals_gross_minus_net_times_bps():
    """cost_saved_usd == (gross - net) * spread_bps / 1e4 (consistency check)."""
    report = _evaluate(seeds=[1])
    bps = report["config"]["spread_bps"]
    for _seed, _sym, win in _all_windows(report):
        expected = (win["gross_notional"] - win["net_notional"]) * bps / 1e4
        assert win["cost_saved_usd"] == pytest.approx(max(expected, 0.0), abs=1e-6)


# --------------------------------------------------------------------------- #
# 3. Capacity clamp invariant
# --------------------------------------------------------------------------- #

def test_capacity_clamp_never_exceeds_max_participation():
    """Filled notional per venue never exceeds max_participation * venue liquidity."""
    seed = 7
    sizer = CapacityAwareSizer(max_participation=DEFAULT_MAX_PARTICIPATION, cost_budget_bps=100.0)
    base_liq: dict = {}
    # Feed a very large target; the clamp must hold on every venue.
    legs = split_venue_legs("BTC", 1e12, seed, bar_index=0)
    leg_px = price_legs_with_capacity("BTC", legs, sizer, 0, 0.0, 100.0, INITIAL_CAPITAL, base_liq)
    assert len(leg_px) == len(VENUES)
    for l in leg_px:
        cap = DEFAULT_MAX_PARTICIPATION * l["venue_liquidity_usd"]
        assert l["filled_notional_usd"] <= cap + 1e-3, (
            f"venue {l['venue']} filled {l['filled_notional_usd']} > cap {cap}"
        )
        # Participation never exceeds the max-participation cap.
        assert l["participation_rate"] <= DEFAULT_MAX_PARTICIPATION + 1e-9, (
            f"venue {l['venue']} participation {l['participation_rate']} > cap"
        )
    # The aggregate filled notional is a tiny fraction of the requested 1e12 gross.
    total_filled = sum(l["filled_notional_usd"] for l in leg_px)
    assert total_filled < 1e-4 * 1e12, "capacity did not materially constrain the huge order"
    # At least one venue must be flagged capacity_limited (the maxed-out venue).
    assert any(l["capacity_limited"] for l in leg_px), (
        "no venue flagged capacity_limited despite a 1e12 target"
    )


def test_small_order_not_capacity_limited():
    """A small order well under capacity is not flagged."""
    seed = 7
    sizer = CapacityAwareSizer(max_participation=DEFAULT_MAX_PARTICIPATION, cost_budget_bps=100.0)
    legs = split_venue_legs("ETH", 100.0, seed, bar_index=0)
    leg_px = price_legs_with_capacity("ETH", legs, sizer, 0, 0.0, 100.0, INITIAL_CAPITAL, {})
    assert all(l["capacity_limited"] is False for l in leg_px)
    assert all(l["filled_notional_usd"] > 0 for l in leg_px)


def test_split_reconstructs_gross_notional():
    """sum(abs(leg)) reconstructs the input gross notional exactly."""
    for target in (0.0, 100.0, 12345.678, 1e9):
        legs = split_venue_legs("BTC", target, seed=3, bar_index=1)
        assert sum(leg.abs_notional_usd for leg in legs) == pytest.approx(target, rel=1e-12)
        assert len(legs) == len(VENUES)


def test_venue_mix_shares_sum_to_one_and_are_positive():
    """Per-bar venue shares are positive and sum to 1.0; signs offset."""
    for sym in ("BTC", "ETH", "SOL"):
        for bar in range(5):
            venues, shares, signs = venue_mix(sym, seed=11, bar_index=bar)
            assert len(shares) == 3
            assert all(s > 0 for s in shares)
            assert sum(shares) == pytest.approx(1.0, rel=1e-12)
            assert signs == (1.0, -1.0, 1.0)


# --------------------------------------------------------------------------- #
# 4. Turnover in [0, 2]
# --------------------------------------------------------------------------- #

def test_turnover_in_range():
    """Per-window turnover lies in [0, 2]."""
    report = _evaluate(seeds=[1, 2])
    for _seed, _sym, win in _all_windows(report):
        assert -1e-9 <= win["turnover"] <= 2.0 + 1e-9, f"turnover {win['turnover']} out of [0, 2]"


# --------------------------------------------------------------------------- #
# 5. Finite / nonzero metrics on real-run seeds
# --------------------------------------------------------------------------- #

def test_real_run_finite_nonzero_metrics():
    """Real-run seeds 1..5 produce finite, nonzero windows/trades/return/Sharpe."""
    report = _evaluate(seeds=[1, 2, 3, 4, 5])
    assert report["never_valid_true"] is True
    assert report.get("valid") is not True
    for r in report["per_seed"]:
        assert r["num_windows"] > 0, f"seed {r['seed']} zero windows"
        assert r["num_trades"] > 0, f"seed {r['seed']} zero trades"
        for key in (
            "oos_return_with_netting",
            "oos_sharpe_with_netting",
            "oos_max_drawdown_with_netting",
            "oos_return_without_netting",
            "oos_sharpe_without_netting",
            "oos_max_drawdown_without_netting",
        ):
            assert math.isfinite(r[key]), f"seed {r['seed']} {key} non-finite: {r[key]}"
        assert r["gross_notional"] > 0
        assert r["net_notional"] > 0


def test_aggregate_has_all_required_fields():
    """Aggregate carries netting-vs-no-netting deltas and cost saved."""
    report = _evaluate(seeds=[1, 2])
    agg = report["aggregate"]
    for k in (
        "mean_gross_notional",
        "mean_net_notional",
        "mean_net_notional_ratio",
        "mean_cost_saved_usd",
        "mean_cost_saved_bps",
        "mean_oos_sharpe_with_netting",
        "mean_oos_sharpe_without_netting",
        "sharpe_delta_with_vs_without_netting",
        "mean_oos_return_with_netting",
        "mean_oos_return_without_netting",
        "return_delta_with_vs_without_netting",
        "mean_oos_max_drawdown_with_netting",
        "mean_oos_max_drawdown_without_netting",
    ):
        assert k in agg, f"missing aggregate key {k}"
        assert math.isfinite(agg[k]), f"{k} non-finite"


# --------------------------------------------------------------------------- #
# 6. Anti-vacuous gates
# --------------------------------------------------------------------------- #

def test_netting_ratio_not_identically_one():
    """net_notional_ratio must NOT be identically 1.0 across every window."""
    report = _evaluate(seeds=[1, 2, 3])
    ratios = [win["net_notional_ratio"] for _s, _sym, win in _all_windows(report)]
    assert any(abs(r - 1.0) > 1e-6 for r in ratios), (
        "netting never engages: all net_notional_ratio == 1.0"
    )
    # And the aggregate must show a real netting benefit.
    assert report["aggregate"]["mean_net_notional_ratio"] < 0.999


def test_not_all_zero_windows_or_trades():
    """Not all windows zero / not all trades zero."""
    report = _evaluate(seeds=[1, 2, 3])
    total_trades = sum(win["num_trades"] for _s, _sym, win in _all_windows(report))
    assert total_trades > 0, "all trades zero (vacuous)"
    total_windows = len(list(_all_windows(report)))
    assert total_windows > 0


def test_report_not_valid_true():
    """The report must never be {'valid': True}."""
    report = _evaluate(seeds=[1])
    assert report.get("valid") is not True
    assert "valid" not in report or report["valid"] is not True
    assert report["never_valid_true"] is True


def test_no_nan_or_inf_in_json():
    """No NaN/Infinity survives strict serialization."""
    report = _evaluate(seeds=[1, 2])
    dumped = json.dumps(report, allow_nan=False)  # raises if any NaN/Inf
    assert "NaN" not in dumped
    assert "Infinity" not in dumped


# --------------------------------------------------------------------------- #
# 7. Determinism (cross-process equivalent via stable seeds)
# --------------------------------------------------------------------------- #

def test_deterministic_across_runs():
    """Identical inputs produce identical reports (generated_at excluded)."""
    r1 = _evaluate(seeds=[3, 4])
    r2 = _evaluate(seeds=[3, 4])
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
        "from src.analytics.cross_venue_netting import evaluate_cross_venue_netting;"
        "r=evaluate_cross_venue_netting(seeds=[5],n_points=160,train_window=40,"
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
# 8. CLI entry point
# --------------------------------------------------------------------------- #

def test_cli_entry_point_writes_artifacts(tmp_path):
    """CLI returns 0 and writes both JSON and MD artifacts for seeds 1 2.

    Runs in an isolated temp CWD so the test never pollutes the repo's
    ``research_state/`` (the real sealed artifact is produced by the exit-gate run,
    not by this test).
    """
    code = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "src" / "analytics" / "cross_venue_netting.py"),
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
        # Paths are printed relative to the temp CWD.
        p = Path(rel)
        if not p.is_absolute():
            p = tmp_path / p
        assert p.exists(), f"missing artifact {p}"


# --------------------------------------------------------------------------- #
# 9. Direct evaluation API (no CLI) is deterministic and finite
# --------------------------------------------------------------------------- #

def test_evaluate_seed_direct():
    """_evaluate_seed_netting returns finite, bounded metrics for one seed."""
    r = _evaluate_seed_netting(1, 160, 40, 20, 20, 0, 0, 1.0, 10.0, DEFAULT_MAX_PARTICIPATION, 2.0)
    assert r["seed"] == 1
    assert r["num_windows"] > 0
    assert r["num_trades"] > 0
    assert 0.0 <= r["net_notional_ratio"] <= 1.0
    assert math.isfinite(r["oos_sharpe_with_netting"])


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))