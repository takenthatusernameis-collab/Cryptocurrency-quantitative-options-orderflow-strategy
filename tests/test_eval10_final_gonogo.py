"""Numeric-invariant tests for src/analytics/eval10_final_gonogo.py (EVAL-10).

Asserts real mathematical properties: determinism, finite values, CI bracketing,
permutation p-range, cost-grid monotonicity, seed-level aggregation, and the
strict GO/NO-GO verdict function. Never ``valid=true`` shortcuts.
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from src.analytics.eval10_final_gonogo import (
    COST_GRID_BPS,
    GO_SEED_FRACTION,
    NET_BASELINE_BPS,
    evaluate_final_gonogo,
)


def _run_cli(*extra: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path.cwd())
    return subprocess.run(
        [sys.executable, "src/analytics/eval10_final_gonogo.py", *extra],
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
        env=env,
    )


def test_eval10_determinism_byte_identical() -> None:
    """The report must be byte-identical across two independent evaluations.

    ``generated_at`` is a wall-clock stamp and is normalized out; the numeric
    computation (seeds, bootstrap, permutation, cost grid) is fully deterministic.
    """
    r1 = evaluate_final_gonogo(seeds=[1, 2, 3, 4, 5])
    r2 = evaluate_final_gonogo(seeds=[1, 2, 3, 4, 5])
    for r in (r1, r2):
        r.pop("generated_at", None)
    b1 = json.dumps(r1, sort_keys=True).encode("utf-8")
    b2 = json.dumps(r2, sort_keys=True).encode("utf-8")
    assert b1 == b2, "EVAL-10 report is not deterministic across runs"


def test_eval10_report_not_valid_true() -> None:
    report = evaluate_final_gonogo(seeds=[1, 2, 3, 4, 5])
    assert report != {"valid": True}
    assert report.get("never_valid_true") is True


def test_eval10_pass_fraction_range_and_finite() -> None:
    report = evaluate_final_gonogo(seeds=[1, 2, 3, 4, 5])
    agg = report["aggregate"]
    assert 0.0 <= agg["pass_fraction"] <= 1.0
    assert math.isfinite(agg["mean_net_sharpe"])
    assert math.isfinite(agg["mean_net_return"])


def test_eval10_verdict_function() -> None:
    report = evaluate_final_gonogo(seeds=[1, 2, 3, 4, 5])
    agg = report["aggregate"]
    expected = "GO" if agg["pass_fraction"] >= GO_SEED_FRACTION else "NO-GO"
    assert agg["verdict"] == expected
    assert agg["verdict"] in ("GO", "NO-GO")
    # EVAL-10 on the verified EVAL-09 data yields NO-GO (0/5 seeds pass).
    assert agg["pass_fraction"] == 0.0
    assert agg["seeds_passing"] == 0
    assert agg["num_seeds"] == 5


def test_eval10_series_pass_fraction_diagnostic() -> None:
    """series_pass_fraction is a distinct diagnostic, never confused with pass_fraction."""
    report = evaluate_final_gonogo(seeds=[1, 2, 3, 4, 5])
    agg = report["aggregate"]
    assert 0.0 <= agg["series_pass_fraction"] <= 1.0
    # Expected 3/15 = 0.2 (ETH passes in seeds 1/3/5 only).
    assert agg["series_pass_fraction"] == pytest.approx(0.2, abs=1e-9)
    assert agg["pass_fraction"] != agg["series_pass_fraction"]


def test_eval10_bootstrap_ci_bracketing() -> None:
    report = evaluate_final_gonogo(seeds=[1, 2, 3, 4, 5])
    agg = report["aggregate"]
    for key in ("bootstrap_ci_mean_net_return", "bootstrap_ci_mean_net_sharpe"):
        v = agg[key]
        assert math.isfinite(v["point"]) and math.isfinite(v["lo"]) and math.isfinite(v["hi"]), key
        assert v["lo"] <= v["point"] <= v["hi"], (key, v)


def test_eval10_permutation_p_range() -> None:
    report = evaluate_final_gonogo(seeds=[1, 2, 3, 4, 5])
    p = report["aggregate"]["permutation_with_vs_without_hedge"]
    assert 0.0 < p["p_value"] <= 1.0
    assert p["paired"] is True
    assert p["n_permutations"] >= 1000
    assert math.isfinite(p["observed_difference"])
    # with-hedge is materially worse than without-hedge on this data.
    assert p["observed_difference"] < 0.0


def test_eval10_cost_grid_monotone_nonincreasing() -> None:
    report = evaluate_final_gonogo(seeds=[1, 2, 3, 4, 5])
    grid = report["aggregate"]["cost_grid"]
    sharpes = [grid[str(b)]["mean_net_sharpe"] for b in COST_GRID_BPS]
    returns = [grid[str(b)]["mean_net_return"] for b in COST_GRID_BPS]
    for v in sharpes + returns:
        assert math.isfinite(v)
    # Monotone nonincreasing in bps (verified: −22.7599 / −22.7659 / −22.7902 / −22.8208).
    for i in range(len(COST_GRID_BPS) - 1):
        assert sharpes[i] >= sharpes[i + 1], (COST_GRID_BPS, sharpes)
        assert returns[i] >= returns[i + 1], (COST_GRID_BPS, returns)
    # Baseline (1 bp) matches the verified EVAL-09 aggregate within tolerance.
    b1 = grid[str(int(NET_BASELINE_BPS))]
    assert b1["mean_net_return"] == pytest.approx(-0.558011, abs=1e-4)
    assert b1["mean_net_sharpe"] == pytest.approx(-22.765930, abs=1e-4)


def test_eval10_per_seed_structure() -> None:
    report = evaluate_final_gonogo(seeds=[1, 2, 3, 4, 5])
    for r in report["per_seed"]:
        assert "seed" in r and "symbols" in r and "seed_pass" in r
        assert "failing_conditions" in r and isinstance(r["failing_conditions"], list)
        for sym, s in r["symbols"].items():
            assert "conditions" in s and "pass" in s
            assert "cost_grid" in s and str(int(NET_BASELINE_BPS)) in s["cost_grid"]
            # Non-degeneracy: each series admissible.
            wh = s["with_hedge"]
            rets = wh["window_returns"]
            assert len(rets) >= 2
            nonzero = [v for v in rets if v != 0.0]
            assert len(set(nonzero)) >= 2


def test_eval10_cli_writes_artifacts(tmp_path: Path) -> None:
    proc = _run_cli("--seeds", "1", "2", "3", "4", "5", "--write")
    assert proc.returncode == 0, proc.stderr
    # Stdout is the JSON object followed by "Wrote ..." lines; parse the first object.
    obj, _end = json.JSONDecoder().raw_decode(proc.stdout)
    out = obj
    assert out["verdict"] == "NO-GO"
    research_state = Path("research_state")
    json_files = sorted(research_state.glob("STRATEGY_EVAL_10_FINAL_GONOGO_*.json"))
    md_files = sorted(research_state.glob("STRATEGY_EVAL_10_FINAL_GONOGO_*.md"))
    assert json_files, "no EVAL-10 JSON artifact written"
    assert md_files, "no EVAL-10 markdown artifact written"
    latest_json = json.loads(json_files[-1].read_text(encoding="utf-8"))
    assert latest_json["report_id"] == "STRATEGY_EVAL_10_FINAL_GONOGO"
    assert latest_json["aggregate"]["verdict"] == "NO-GO"
    assert latest_json != {"valid": True}
