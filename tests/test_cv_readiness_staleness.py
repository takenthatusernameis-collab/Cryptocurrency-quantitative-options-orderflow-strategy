"""Deterministic CV staleness / readiness determinism tests (paper-only, tmp fixtures).

Covers the false-green regression: `check_cv()` must NOT report a fresh/passed CV
when the checkpoint timestamp is missing, malformed, or older than max_age, when
the checkpoint schema is ambiguous/incomplete, or when the `latest.json` pointer
references a missing immutable artifact. Only a fully-formed, fresh, green
checkpoint with a resolvable pointer passes.
"""
from __future__ import annotations

import json
from pathlib import Path

import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import check_paper_ops_readiness as c  # noqa: E402

LATEST = "research_state/campaign_checkpoints/CONTINUOUS_VALIDATION_AND_MONITORING_latest.json"


def _write_latest(tmp_repo: Path, checkpoint: dict, pointer_missing: bool = False) -> Path:
    cp_dir = tmp_repo / "research_state" / "campaign_checkpoints"
    cp_dir.mkdir(parents=True, exist_ok=True)
    path = cp_dir / "CONTINUOUS_VALIDATION_AND_MONITORING_latest.json"
    path.write_text(json.dumps(checkpoint, allow_nan=False), encoding="utf-8")
    # Resolve the pointer so a well-formed checkpoint reads as pointer_ok.
    if not pointer_missing:
        art_dir = tmp_repo / "research_state"
        art_dir.mkdir(parents=True, exist_ok=True)
        art = art_dir / "CONTINUOUS_VALIDATION_20261107T045148Z.json"
        art.write_text(json.dumps({"campaign": {"status": "complete"}}, allow_nan=False), encoding="utf-8")
    return path


def _base_checkpoint(ts: str = "2026-11-07T04:51:48.529360Z", pointer_missing: bool = False) -> dict:
    return {
        "campaign_id": "continuous_validation_and_monitoring",
        "status": "complete",
        "timestamp": ts,
        "paper_only": True,
        "live_trading_enabled": False,
        "gates": {
            "all_critical_passed": True,
            "iterations_5_5": True,
            "iterations_passed_zero_failed": True,
            "reconciliation_freshness_gte_0_99_met_with_measurements": True,
            "paper_only": True,
            "live_trading_not_enabled": True,
        },
        "reconciliation_freshness": {
            "slo_id": "slo_reconciliation_freshness",
            "target_gte": 0.99,
            "met": True,
            "all_iterations_met": True,
            "all_iterations_have_measurements": True,
            "measurements_per_iteration": [1, 1, 1, 1, 1],
        },
        "artifacts": {
            "continuous_validation": (
                "research_state/CONTINUOUS_VALIDATION_MISSING.json"
                if pointer_missing
                else "research_state/CONTINUOUS_VALIDATION_20261107T045148Z.json"
            )
        },
    }


def test_missing_timestamp_not_fresh_not_passed(tmp_path):
    cp = _base_checkpoint(ts=None)
    del cp["timestamp"]
    _write_latest(tmp_path, cp)
    cv = c.check_cv(repo=tmp_path, max_age_hours=2.0)
    assert cv["exists"] is True
    assert cv["timestamp_valid"] is False
    assert cv["fresh_within_max_age_hours"] is False
    assert cv["passed"] is False
    assert any("cv_missing_or_invalid_timestamp" in r for r in cv["reasons"])


def test_malformed_timestamp_not_fresh_not_passed(tmp_path):
    cp = _base_checkpoint(ts="not-a-timestamp")
    _write_latest(tmp_path, cp)
    cv = c.check_cv(repo=tmp_path, max_age_hours=2.0)
    assert cv["timestamp_valid"] is False
    assert cv["fresh_within_max_age_hours"] is False
    assert cv["passed"] is False
    assert any("cv_missing_or_invalid_timestamp" in r for r in cv["reasons"])


def test_stale_age_not_fresh_not_passed(tmp_path):
    cp = _base_checkpoint(ts="2020-01-01T00:00:00Z")
    _write_latest(tmp_path, cp)
    cv = c.check_cv(repo=tmp_path, max_age_hours=2.0)
    assert cv["timestamp_valid"] is True
    assert cv["fresh_within_max_age_hours"] is False
    assert cv["passed"] is False
    assert any("cv_not_fresh_within_max_age_hours" in r for r in cv["reasons"])


def test_stale_pointer_missing_artifact_not_passed(tmp_path):
    cp = _base_checkpoint(pointer_missing=True)
    _write_latest(tmp_path, cp, pointer_missing=True)
    cv = c.check_cv(repo=tmp_path, max_age_hours=2.0)
    assert cv["timestamp_valid"] is True
    assert cv["pointer_ok"] is False
    assert cv["passed"] is False
    assert any("cv_stale_pointer_missing_artifact" in r for r in cv["reasons"])


def test_ambiguous_schema_missing_gates_not_passed(tmp_path):
    cp = _base_checkpoint()
    del cp["gates"]
    _write_latest(tmp_path, cp)
    cv = c.check_cv(repo=tmp_path, max_age_hours=2.0)
    assert cv["schema_ok"] is False
    assert cv["passed"] is False
    assert any("cv_missing_gates_dict" in r for r in cv["reasons"])


def test_ambiguous_schema_invalid_measurements_not_passed(tmp_path):
    cp = _base_checkpoint()
    cp["reconciliation_freshness"]["measurements_per_iteration"] = [1, 1, 0, 1, 1]
    _write_latest(tmp_path, cp)
    cv = c.check_cv(repo=tmp_path, max_age_hours=2.0)
    assert cv["schema_ok"] is False
    assert cv["passed"] is False
    assert any("cv_rf_measurements_per_iteration_invalid" in r for r in cv["reasons"])


def test_green_checkpoint_passes(tmp_path):
    cp = _base_checkpoint()
    _write_latest(tmp_path, cp)
    cv = c.check_cv(repo=tmp_path, max_age_hours=2.0)
    assert cv["exists"] is True
    assert cv["timestamp_valid"] is True
    assert cv["schema_ok"] is True
    assert cv["pointer_ok"] is True
    assert cv["fresh_within_max_age_hours"] is True
    assert cv["passed"] is True
    assert cv["reasons"] == []
