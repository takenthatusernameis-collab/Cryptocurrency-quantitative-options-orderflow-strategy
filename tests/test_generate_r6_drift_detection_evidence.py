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


def _write_r6_minimal_state(tmp_path):
    rs = tmp_path / "research_state"
    rs.mkdir(parents=True)
    (rs / "campaign_checkpoints").mkdir(parents=True)
    (rs / "PHASE20_DRIFT_DETECTION_REPORT.json").write_text(json.dumps({
        "report": "PHASE20_DRIFT_DETECTION_REPORT", "timestamp": "2026-11-01T13:35:37Z", "paper_only": True,
        "config": {"pnl_drift_threshold": 0.05, "greeks_drift_threshold": 0.08, "fills_drift_threshold": 0.1, "latency_drift_ms_threshold": 50.0, "anomaly_threshold": 0.7, "paper_only": True},
        "baseline": {"pnl": 10000.0, "greeks": {"delta": 0.1, "gamma": 0.01, "vega": 0.05}, "fills_rate": 0.98, "latency_ms": 15.0},
        "current": {"pnl": 10250.0, "greeks": {"delta": 0.105, "gamma": 0.0105, "vega": 0.052}, "fills_rate": 0.97, "latency_ms": 18.0},
        "detection": {"anomaly_count": 0, "anomaly_score": 0.0, "within_bounds": True, "alerts_count": 0},
    }))
    for name, payload in [
        ("OBSERVABILITY_REPORT.json", {"report": "OBSERVABILITY_REPORT", "num_entries": 3}),
        ("ALERT_AUDIT.json", {"audit": {"num_unresolved": 0}}),
        ("HEALTH_SLO_REPORT.json", {"health": {"status": "pass", "checks": []}}),
        ("RESILIENCE_AUDIT.json", {}),
        ("CONTINUOUS_VALIDATION.json", {"gates": {"all_critical_passed": True}}),
    ]:
        (rs / name).write_text(json.dumps(payload))
    (rs / "campaign_checkpoints" / "CONTINUOUS_VALIDATION_AND_MONITORING_latest.json").write_text(json.dumps({
        "timestamp": "2026-11-07T10:28:17Z", "paper_only": True, "live_trading_enabled": False,
        "gates": {"all_critical_passed": True, "iterations_5_5": True, "reconciliation_freshness_gte_0_99_met_with_measurements": True},
        "reconciliation_freshness": {"met": True, "all_iterations_have_measurements": True, "measurements_per_iteration": [1, 1, 1, 1, 1]},
        "artifacts": {
            "observability": "research_state/OBSERVABILITY_REPORT.json",
            "alert_audit": "research_state/ALERT_AUDIT.json",
            "health_slo": "research_state/HEALTH_SLO_REPORT.json",
            "resilience": "research_state/RESILIENCE_AUDIT.json",
            "continuous_validation": "research_state/CONTINUOUS_VALIDATION.json",
        },
    }))
    (rs / "CROSSVENUE_ORCHESTRATION_REPORT.json").write_text(json.dumps({
        "paper_only": True,
        "venues": ["deribit", "okx", "binance"],
        "symbols": ["BTC", "ETH"],
        "config": {"venues": ["deribit", "okx", "binance"], "symbols": ["BTC", "ETH"], "taker_fee_bps": {"deribit": 5.0, "okx": 4.0, "binance": 4.5}},
        "components": {
            "latency_routing": {
                "latency": {
                    "deribit": {"ewma_ms": 26.46, "samples": 10, "max_sample_ms": 46.83, "within_limit": True},
                    "okx": {"ewma_ms": 23.74, "samples": 10, "max_sample_ms": 44.92, "within_limit": True},
                    "binance": {"ewma_ms": 21.10, "samples": 10, "max_sample_ms": 41.20, "within_limit": True},
                },
                "slippage": {"avg_slippage_bps": 0.5, "max_slippage_bps": 2.0, "fills": 120, "total_slippage_bps": 0.6},
            },
        },
    }))
    (rs / "PHASE37_CROSS_VENUE_ROUTING_REPORT.json").write_text(json.dumps({"ok": True, "cycles": 3}))
    return rs


def test_r6_cross_venue_latency_drift_default_off(tmp_path, monkeypatch):
    import generate_r6_drift_detection_evidence as gmod

    rs = _write_r6_minimal_state(tmp_path)
    monkeypatch.setattr(gmod, "RS", rs)
    monkeypatch.setattr(gmod, "REPO", tmp_path)
    d = gmod.gen_r6_strict("20260101T000000Z", cross_venue_latency_drift=False)
    assert d.get("cross_venue_latency_drift") is False
    assert not any(w.startswith("cross_venue_latency_drift_breakdown_emitted") for w in d["warn_flags"])
    ok, issues = v.validate_artifact(d, "R6")
    assert ok, issues
    assert d["next9_unblocked"] is False


def test_r6_cross_venue_latency_drift_emitted_when_flag_set(tmp_path, monkeypatch):
    import generate_r6_drift_detection_evidence as gmod

    rs = _write_r6_minimal_state(tmp_path)
    monkeypatch.setattr(gmod, "RS", rs)
    monkeypatch.setattr(gmod, "REPO", tmp_path)
    d = gmod.gen_r6_strict("20260101T000000Z", cross_venue_latency_drift=True)
    assert d.get("cross_venue_latency_drift") is True
    assert any(w == "cross_venue_latency_drift_breakdown_emitted_advisory" for w in d["warn_flags"])
    bd = d["cross_venue_latency_drift_breakdown"]
    assert set(bd.get("venues", [])) == {"deribit", "okx", "binance"}
    assert set(bd.get("symbols", [])) == {"BTC", "ETH"}
    for venue in ("deribit", "okx", "binance"):
        row = bd["per_venue"][venue]
        assert "ewma_ms" in row and "taker_fee_bps" in row
        assert row["latency_drift_ms_vs_baseline"] is not None
    for symbol in ("BTC", "ETH"):
        assert set(bd["per_symbol"][symbol]["venues"].keys()) == {"deribit", "okx", "binance"}
        assert bd["per_symbol"][symbol]["delta_drift"] is not None
    assert bd["global_latency_drift_ms"] == 3.0
    assert bd["within_latency_threshold"] is True
    ok, issues = v.validate_artifact(d, "R6")
    assert ok, issues
    assert d["next9_unblocked"] is False
    assert d["live_trading_enabled"] is False
    assert d["paper_only"] is True
