from __future__ import annotations

import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import generate_r6_drift_detection_evidence as g  # noqa: E402
import validate_r3_r7_reduction_evidence as v  # noqa: E402


def test_gen_r6_strict_produces_valid_artifact():
    d = g.gen_r6_strict(g._utc())
    ok, issues = v.validate_artifact(d, "R6")
    assert ok, issues
    assert d["artifact_type"] == v.ARTIFACT_TYPES["R6"]
    assert d["paper_only"] is True
    assert d["live_trading_enabled"] is False
    assert d["next9_unblocked"] is False
    assert d["deterministic"] is True
    assert d["advisory"] is True
    assert isinstance(d["evidence_refs"], list) and len(d["evidence_refs"]) > 0
    assert "cv_checkpoint_green" in d["flags"]
    assert "deterministic_pass" in d["flags"]
    assert isinstance(d["warn_flags"], list)


def test_r6_cites_phase20_and_cv_checkpoint():
    d = g.gen_r6_strict(g._utc())
    refs = " ".join(d["evidence_refs"])
    assert "PHASE20_DRIFT_DETECTION_REPORT.json" in refs
    assert "CONTINUOUS_VALIDATION_AND_MONITORING" in refs or "CONTINUOUS_VALIDATION" in refs


def test_main_writes_valid_r6_artifact(tmp_path, monkeypatch):
    rs = tmp_path / "research_state"
    (rs / "campaign_checkpoints").mkdir(parents=True)
    # minimal phase20
    (rs / "PHASE20_DRIFT_DETECTION_REPORT.json").write_text(json.dumps({
        "report": "PHASE20_DRIFT_DETECTION_REPORT", "timestamp": "2026-11-01T00:00:00Z", "paper_only": True,
        "config": {"pnl_drift_threshold": 0.05, "greeks_drift_threshold": 0.08, "fills_drift_threshold": 0.1, "latency_drift_ms_threshold": 50, "anomaly_threshold": 0.7},
        "detection": {"anomaly_count": 0, "anomaly_score": 0.0, "within_bounds": True, "alerts_count": 0},
    }))
    (rs / "campaign_checkpoints" / "CONTINUOUS_VALIDATION_AND_MONITORING_latest.json").write_text(json.dumps({
        "timestamp": "2026-11-07T00:00:00Z", "paper_only": True, "live_trading_enabled": False,
        "gates": {"all_critical_passed": True, "iterations_5_5": True, "reconciliation_freshness_gte_0_99_met_with_measurements": True},
        "reconciliation_freshness": {"met": True, "all_iterations_have_measurements": True, "measurements_per_iteration": [1, 1, 1, 1, 1]},
        "artifacts": {},
    }))
    monkeypatch.setattr(g, "RS", rs)
    monkeypatch.setattr(g, "REPO", tmp_path)
    rc = g.main([])
    assert rc == 0
    out = list(rs.glob("R6_DRIFT_DETECTION_REPORT_*.json"))
    assert len(out) == 1
    d = json.loads(out[0].read_text())
    ok, issues = v.validate_artifact(d, "R6")
    assert ok, issues
    assert d["flags"]["deterministic_pass"] is True
    assert d["next9_unblocked"] is False
