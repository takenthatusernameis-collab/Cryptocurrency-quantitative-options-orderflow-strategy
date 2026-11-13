"""Numeric-invariant tests for src/analytics/hedge_cost_optimizer.py (EVAL-11)."""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path

from src.analytics.hedge_cost_optimizer import (
    MAX_ABS_DELTA_USD,
    MIN_HEDGES_PER_SEED,
    evaluate_hedge_cost_optimizer,
)


def _tiny_report() -> dict:
    return evaluate_hedge_cost_optimizer(
        search_seeds=[1],
        final_seeds=[1],
        target_delta_grid=[0.0, 20_000.0],
        toxicity_threshold_grid=[0.7],
        cost_budget_grid=[1.0, 4.0],
        n_points=200,
        train_window=80,
        test_window=30,
        step_size=30,
        purge=10,
        embargo=5,
    )


def test_optimizer_best_config_is_feasible_and_finite() -> None:
    report = _tiny_report()
    assert report["report_id"] == "HEDGE_COST_OPTIMIZER_EVAL_11"
    assert report["never_valid_true"] is True
    assert report["search"]["num_configs"] == 4
    assert report["search"]["num_feasible"] >= 1
    assert report["best_config"] is not None
    assert report["best_config"]["feasible"] is True
    assert report["best_config"]["failure_reasons"] == []
    assert report["best_config"]["mean_net_sharpe"] == max(
        item["mean_net_sharpe"] for item in report["search"]["surface"] if item["feasible"]
    )
    best_final = report["best_config_final"]
    assert best_final is not None
    assert best_final["mean_abs_delta_usd"] <= MAX_ABS_DELTA_USD
    assert best_final["total_hedges"] >= MIN_HEDGES_PER_SEED * best_final["num_seeds"]
    assert all(
        math.isfinite(best_final[key])
        for key in ("mean_net_sharpe", "mean_net_return", "mean_abs_delta_usd")
    )


def test_optimizer_marks_gate_disabled_config_infeasible() -> None:
    report = evaluate_hedge_cost_optimizer(
        search_seeds=[1],
        final_seeds=[1],
        target_delta_grid=[0.0],
        toxicity_threshold_grid=[0.5, 0.7],
        cost_budget_grid=[2.0],
        n_points=200,
        train_window=80,
        test_window=30,
        step_size=30,
        purge=10,
        embargo=5,
    )
    surface = report["search"]["surface"]
    gate_disabled = [item for item in surface if item["config"]["toxicity_threshold"] == 0.5]
    assert gate_disabled
    assert all(not item["feasible"] for item in gate_disabled)
    assert all(
        "insufficient_hedge_activity" in item["failure_reasons"] for item in gate_disabled
    )


def test_optimizer_is_deterministic_after_timestamp_removal() -> None:
    kwargs = dict(
        search_seeds=[1],
        final_seeds=[1],
        target_delta_grid=[0.0],
        toxicity_threshold_grid=[0.7],
        cost_budget_grid=[2.0],
        n_points=200,
        train_window=80,
        test_window=30,
        step_size=30,
        purge=10,
        embargo=5,
    )
    first = evaluate_hedge_cost_optimizer(**kwargs)
    second = evaluate_hedge_cost_optimizer(**kwargs)
    first.pop("generated_at", None)
    second.pop("generated_at", None)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_optimizer_cli_writes_artifacts(tmp_path: Path) -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path.cwd())
    proc = subprocess.run(
        [
            sys.executable,
            "src/analytics/hedge_cost_optimizer.py",
            "--search-seeds",
            "1",
            "--final-seeds",
            "1",
            "--target-delta-grid",
            "0",
            "--toxicity-threshold-grid",
            "0.7",
            "--cost-budget-grid",
            "2",
            "--n-points",
            "200",
            "--train-window",
            "80",
            "--test-window",
            "30",
            "--step-size",
            "30",
            "--write",
            "--out-dir",
            str(tmp_path),
            "--timestamp",
            "2026-11-13T010000Z",
        ],
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
        env=env,
    )
    assert proc.returncode == 0, proc.stderr
    json_files = sorted(tmp_path.glob("HEDGE_COST_OPTIMIZER_*.json"))
    md_files = sorted(tmp_path.glob("HEDGE_COST_OPTIMIZER_*.md"))
    assert json_files and md_files
    artifact = json.loads(json_files[-1].read_text(encoding="utf-8"))
    assert artifact["report_id"] == "HEDGE_COST_OPTIMIZER_EVAL_11"
    assert artifact["config"]["hedge_cost_bps_inert"] is True
    assert artifact["search"]["num_configs"] == 1
    assert artifact["best_config_final"]["feasible"] is True
    assert artifact != {"valid": True}