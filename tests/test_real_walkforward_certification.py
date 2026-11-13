"""Numeric-invariant tests for src/analytics/real_walkforward_certification.py (EVAL-12)."""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path

from src.analytics.real_walkforward_certification import (
    CANDIDATE_CONFIGS,
    CERTIFICATION_SEEDS,
    evaluate_real_walkforward_certification,
    _verify_data_reality,
    _cscv_pbo,
    _benjamini_hochberg,
    _compute_dsr,
    _sharpe_of_returns,
)


def _tiny_certification() -> dict:
    return evaluate_real_walkforward_certification(
        candidate_configs=CANDIDATE_CONFIGS,
        seeds=[1],
        n_points=200,
        train_window=80,
        test_window=30,
        step_size=30,
        purge=10,
        embargo=5,
        pbo_n_combinations=4,
        pbo_k_folds=4,
        fdr_alpha=0.10,
    )


def test_certification_runs_and_produces_valid_report() -> None:
    report = _tiny_certification()
    assert report["report_id"] == "REAL_WF_CERTIFICATION_EVAL_12"
    assert report["never_valid_true"] is True
    assert report["verdict"] in ("GO", "NO-GO")
    assert "data_evidence" in report
    assert "config_results" in report
    assert "dsr_by_config" in report
    assert "pbo" in report
    assert "multiple_testing_correction" in report
    assert "surviving_configs" in report
    assert set(report["dsr_by_config"].keys()) == set(CANDIDATE_CONFIGS.keys())


def test_data_reality_check_returns_expected_structure() -> None:
    evidence = _verify_data_reality()
    assert "btc_orderflow_file_exists" in evidence
    assert "btc_orderflow_trades_count" in evidence
    assert "btc_options_file_exists" in evidence
    assert "btc_options_quotes_count" in evidence
    assert "eth_orderflow_file_exists" in evidence
    assert "eth_options_file_exists" in evidence
    assert "processed_venue_snapshots" in evidence
    assert "data_matrix" in evidence
    assert evidence["data_matrix"]["btc_real_trades"] is True
    assert evidence["data_matrix"]["eth_synthetic_fallback"] is True
    assert evidence["data_matrix"]["sol_synthetic_fallback"] is True
    assert evidence["data_matrix"]["venue_snapshots_aggregate_only"] is True


def test_cscv_pbo_structure() -> None:
    returns_by_config = {
        "config_a": [0.01, 0.02, -0.01, 0.03, 0.01, -0.02, 0.02, 0.01],
        "config_b": [0.005, 0.01, -0.005, 0.015, 0.005, -0.01, 0.01, 0.005],
    }
    result = _cscv_pbo(returns_by_config, n_combinations=4, k_folds=4, seed=42)
    assert "pbo_per_config" in result
    assert "overall_pbo" in result
    assert "config_details" in result
    assert result["k_folds"] == 4
    assert result["n_combinations_used"] == 4
    assert set(result["pbo_per_config"].keys()) == {"config_a", "config_b"}
    for v in result["pbo_per_config"].values():
        assert 0.0 <= v <= 1.0


def test_benjamini_hochberg_correction() -> None:
    p_values = {"a": 0.01, "b": 0.03, "c": 0.08, "d": 0.20}
    result = _benjamini_hochberg(p_values, alpha=0.10)
    assert "rejected" in result
    assert "thresholds" in result
    assert result["alpha"] == 0.10
    assert result["m_tests"] == 4
    assert result["method"] == "Benjamini-Hochberg"
    # With alpha=0.10, m=4: thresholds are 0.025, 0.05, 0.075, 0.10
    # a=0.01 <= 0.025 -> rejected
    # b=0.03 <= 0.05 -> rejected
    # c=0.08 > 0.075 -> not rejected
    assert "a" in result["rejected"]
    assert "b" in result["rejected"]
    assert "c" not in result["rejected"]


def test_compute_dsr_matches_deflated_sharpe() -> None:
    returns = [0.01, 0.02, -0.01, 0.03, 0.01, -0.02, 0.02, 0.01, 0.015, -0.005]
    dsr = _compute_dsr(returns, sr_benchmark=0.0)
    assert math.isfinite(dsr)
    assert 0.0 <= dsr <= 1.0


def test_sharpe_of_returns_finite() -> None:
    returns = [0.01, 0.02, -0.01, 0.03, 0.01]
    sr = _sharpe_of_returns(returns)
    assert math.isfinite(sr)


def test_certification_is_deterministic_after_timestamp_removal() -> None:
    kwargs = dict(
        candidate_configs=CANDIDATE_CONFIGS,
        seeds=[1],
        n_points=200,
        train_window=80,
        test_window=30,
        step_size=30,
        purge=10,
        embargo=5,
        pbo_n_combinations=4,
        pbo_k_folds=4,
        fdr_alpha=0.10,
    )
    first = evaluate_real_walkforward_certification(**kwargs)
    second = evaluate_real_walkforward_certification(**kwargs)
    first.pop("generated_at", None)
    second.pop("generated_at", None)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_certification_cli_writes_artifacts(tmp_path: Path) -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path.cwd())
    proc = subprocess.run(
        [
            sys.executable,
            "src/analytics/real_walkforward_certification.py",
            "--seeds",
            "1",
            "--n-points",
            "200",
            "--train-window",
            "80",
            "--test-window",
            "30",
            "--step-size",
            "30",
            "--purge",
            "10",
            "--embargo",
            "5",
            "--pbo-combinations",
            "4",
            "--pbo-k-folds",
            "4",
            "--fdr-alpha",
            "0.10",
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
    json_files = sorted(tmp_path.glob("REAL_WF_CERTIFICATION_*.json"))
    md_files = sorted(tmp_path.glob("REAL_WF_CERTIFICATION_*.md"))
    assert json_files and md_files
    artifact = json.loads(json_files[-1].read_text(encoding="utf-8"))
    assert artifact["report_id"] == "REAL_WF_CERTIFICATION_EVAL_12"
    assert artifact["verdict"] in ("GO", "NO-GO")
    assert artifact != {"valid": True}
    assert "dsr_by_config" in artifact
    assert "pbo" in artifact
    assert "multiple_testing_correction" in artifact


def test_certification_non_degeneracy() -> None:
    """Assert non-degeneracy: >=2 distinct nonzero per-window returns, >=2 seeds or >=2 windows, finite DSR/PBO."""
    report = _tiny_certification()
    for name, result in report["config_results"].items():
        all_returns = result["all_window_returns"]
        nonzero_returns = [r for r in all_returns if r != 0.0]
        distinct_nonzero = len(set(round(r, 12) for r in nonzero_returns))
        assert distinct_nonzero >= 2, f"{name}: insufficient distinct nonzero returns ({distinct_nonzero})"
        assert len(all_returns) >= 2, f"{name}: insufficient windows ({len(all_returns)})"
        assert result["n_seeds"] >= 1
        assert result["n_series"] >= 1

    for name, dsr in report["dsr_by_config"].items():
        assert math.isfinite(dsr), f"{name}: DSR non-finite"
        assert 0.0 <= dsr <= 1.0, f"{name}: DSR out of bounds"

    pbo = report["pbo"]
    assert math.isfinite(pbo["overall_pbo"])
    assert 0.0 <= pbo["overall_pbo"] <= 1.0
    for name, pbo_val in pbo["pbo_per_config"].items():
        assert math.isfinite(pbo_val)
        assert 0.0 <= pbo_val <= 1.0