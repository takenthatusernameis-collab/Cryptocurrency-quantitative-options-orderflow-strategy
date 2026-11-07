from __future__ import annotations

import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import generate_r4_credential_controls_checklist as g  # noqa: E402
import validate_r3_r7_reduction_evidence as v  # noqa: E402


def test_gen_r4_strict_produces_valid_artifact():
    d = g.gen_r4_strict(g._utc())
    ok, issues = v.validate_artifact(d, "R4")
    assert ok, issues
    assert d["artifact_type"] == v.ARTIFACT_TYPES["R4"]
    assert d["paper_only"] is True
    assert d["live_trading_enabled"] is False
    assert d["next9_unblocked"] is False
    assert d["attestation_only"] is True
    assert d["advisory"] is True
    assert d["strictness"] == "enhanced_extraction_v2"
    assert isinstance(d["checklist"], list) and len(d["checklist"]) > 0
    controls = {c["control"] for c in d["checklist"]}
    assert "secrets_not_committed" in controls
    assert "live_trading_default_false" in controls
    assert "env_example_live_trading_false" in controls
    assert isinstance(d["flags"]["deterministic_pass"], bool)
    assert isinstance(d["warn_flags"], list)
    # per-venue rows derived from cross-venue artifacts (or defaults)
    venue_rows = [c for c in d["checklist"] if c.get("venue")]
    assert venue_rows, "expected per-venue credential control rows"
    assert "venue_credential_coverage" in d
    assert d["venue_credential_coverage"].get("venues")


def test_main_writes_valid_r4_artifact(tmp_path, monkeypatch):
    import generate_r4_credential_controls_checklist as gmod

    rs = tmp_path / "research_state"
    rs.mkdir(parents=True)
    (rs / "campaign_checkpoints").mkdir(parents=True)
    (rs / "CROSSVENUE_ORCHESTRATION_REPORT.json").write_text(json.dumps({"paper_only": True, "venues": ["deribit", "okx"], "config": {"venues": ["deribit", "okx"]}}))
    monkeypatch.setattr(gmod, "RS", rs)
    monkeypatch.setattr(gmod, "REPO", tmp_path)
    (tmp_path / "src" / "config").mkdir(parents=True)
    (tmp_path / "src" / "config" / "secrets.py").write_text('LIVE_TRADING_ENABLED = "false"\n')
    (tmp_path / ".env.example").write_text("LIVE_TRADING_ENABLED=false\n")
    rc = gmod.main(["--effective-until-hours", "168"])
    assert rc == 0
    out = list(rs.glob("R4_CREDENTIAL_CONTROLS_CHECKLIST_*.json"))
    assert len(out) == 1
    d = json.loads(out[0].read_text())
    ok, issues = v.validate_artifact(d, "R4")
    assert ok, issues
    assert d["next9_unblocked"] is False
    assert "effective_until_utc" in d
    assert d["flags"].get("effective_until_advisory") is True
    assert d["venue_credential_coverage"]["venues"] == ["deribit", "okx"]
    venue_rows = [c for c in d["checklist"] if c.get("venue") == "deribit"]
    assert venue_rows


def test_secret_scanner_ignores_benign_gate_names(tmp_path, monkeypatch):
    import generate_r4_credential_controls_checklist as gmod

    rs = tmp_path / "research_state"
    rs.mkdir(parents=True)
    # benign artifact value that should NOT trigger (risk_manager_init contains 'key' substring? no, but test a harmless token-like word boundary case)
    (rs / "PAPER_OPS_SESSION_GATE_20260101T000000Z.json").write_text(json.dumps({
        "gates": {"risk_manager_init": True, "paper_ops_ready": True},
        "action_required": ["record_a1_a7_human_approvals_before_next9"],
    }))
    monkeypatch.setattr(gmod, "RS", rs)
    monkeypatch.setattr(gmod, "REPO", tmp_path)
    (tmp_path / "src" / "config").mkdir(parents=True)
    (tmp_path / "src" / "config" / "secrets.py").write_text('LIVE_TRADING_ENABLED = "false"\n')
    (tmp_path / ".env.example").write_text("LIVE_TRADING_ENABLED=false\n")
    d = gmod.gen_r4_strict("20260101T000000Z")
    ok, issues = v.validate_artifact(d, "R4")
    assert ok, issues
    assert d["secrets_committed"] is False
    assert d["secret_scan"]["hit_count"] == 0


def test_effective_until_default_off_no_field():
    d = g.gen_r4_strict(g._utc())
    assert "effective_until_utc" not in d
    assert d.get("flags", {}).get("effective_until_advisory") is None


def test_per_venue_rows_surface_cross_venue_evidence_refs(tmp_path, monkeypatch):
    import generate_r4_credential_controls_checklist as gmod

    rs = tmp_path / "research_state"
    rs.mkdir(parents=True)
    (rs / "campaign_checkpoints").mkdir(parents=True)
    cross = {
        "paper_only": True,
        "venues": ["deribit", "okx", "binance"],
        "symbols": ["BTC", "ETH"],
        "config": {
            "venues": ["deribit", "okx", "binance"],
            "symbols": ["BTC", "ETH"],
            "taker_fee_bps": {"deribit": 5.0, "okx": 5.0, "binance": 4.0},
        },
        "components": {
            "latency_routing": {
                "latency": {
                    "deribit": {"ewma_ms": 26.46, "samples": 10, "max_sample_ms": 46.83, "within_limit": True},
                    "okx": {"ewma_ms": 23.74, "samples": 10, "max_sample_ms": 44.92, "within_limit": True},
                    "binance": {"ewma_ms": 28.46, "samples": 10, "max_sample_ms": 44.26, "within_limit": True},
                }
            },
            "arbitrage": {"config": {"taker_fee_bps": {"deribit": 5.0, "okx": 5.0, "binance": 4.0}}},
        },
    }
    (rs / "CROSSVENUE_ORCHESTRATION_REPORT.json").write_text(json.dumps(cross))
    (rs / "PHASE37_CROSS_VENUE_ROUTING_REPORT.json").write_text(json.dumps({"ok": True, "cycles": 3}))
    monkeypatch.setattr(gmod, "RS", rs)
    monkeypatch.setattr(gmod, "REPO", tmp_path)
    (tmp_path / "src" / "config").mkdir(parents=True)
    (tmp_path / "src" / "config" / "secrets.py").write_text('LIVE_TRADING_ENABLED = "false"\n')
    (tmp_path / ".env.example").write_text("LIVE_TRADING_ENABLED=false\n")
    d = gmod.gen_r4_strict("20260101T000000Z")
    ok, issues = v.validate_artifact(d, "R4")
    assert ok, issues
    venue_rows = {c["venue"]: c for c in d["checklist"] if c.get("venue")}
    assert set(venue_rows.keys()) == {"deribit", "okx", "binance"}
    for venue in ("deribit", "okx", "binance"):
        row = venue_rows[venue]
        refs = row.get("evidence_refs", [])
        assert any("CROSSVENUE_ORCHESTRATION_REPORT.json" in r for r in refs), f"venue {venue} missing cross-venue evidence refs"
        assert any(f"latency.{venue}." in r for r in refs), f"venue {venue} missing latency evidence ref"
    assert d["venue_credential_coverage"]["venues"] == ["deribit", "okx", "binance"]
    assert d["venue_credential_coverage"]["symbols"] == ["BTC", "ETH"]


def test_per_symbol_credential_scope_default_off(tmp_path, monkeypatch):
    import generate_r4_credential_controls_checklist as gmod

    rs = tmp_path / "research_state"
    rs.mkdir(parents=True)
    (rs / "campaign_checkpoints").mkdir(parents=True)
    (rs / "CROSSVENUE_ORCHESTRATION_REPORT.json").write_text(json.dumps({"paper_only": True, "venues": ["deribit"], "symbols": ["BTC"], "config": {"venues": ["deribit"], "symbols": ["BTC"]}}))
    (rs / "PHASE37_CROSS_VENUE_ROUTING_REPORT.json").write_text(json.dumps({"ok": True, "cycles": 3}))
    monkeypatch.setattr(gmod, "RS", rs)
    monkeypatch.setattr(gmod, "REPO", tmp_path)
    (tmp_path / "src" / "config").mkdir(parents=True)
    (tmp_path / "src" / "config" / "secrets.py").write_text('LIVE_TRADING_ENABLED = "false"\n')
    (tmp_path / ".env.example").write_text("LIVE_TRADING_ENABLED=false\n")
    d = gmod.gen_r4_strict("20260101T000000Z")
    assert d.get("per_symbol_credential_scope") is False
    sym_rows = [c for c in d["checklist"] if c.get("symbol")]
    assert sym_rows == [], "per-symbol credential scope rows must not be emitted by default"


def test_per_symbol_credential_scope_emitted_when_flag_set(tmp_path, monkeypatch):
    import generate_r4_credential_controls_checklist as gmod

    rs = tmp_path / "research_state"
    rs.mkdir(parents=True)
    (rs / "campaign_checkpoints").mkdir(parents=True)
    (rs / "CROSSVENUE_ORCHESTRATION_REPORT.json").write_text(json.dumps({"paper_only": True, "venues": ["deribit", "okx"], "symbols": ["BTC", "ETH"], "config": {"venues": ["deribit", "okx"], "symbols": ["BTC", "ETH"]}}))
    (rs / "PHASE37_CROSS_VENUE_ROUTING_REPORT.json").write_text(json.dumps({"ok": True, "cycles": 3}))
    monkeypatch.setattr(gmod, "RS", rs)
    monkeypatch.setattr(gmod, "REPO", tmp_path)
    (tmp_path / "src" / "config").mkdir(parents=True)
    (tmp_path / "src" / "config" / "secrets.py").write_text('LIVE_TRADING_ENABLED = "false"\n')
    (tmp_path / ".env.example").write_text("LIVE_TRADING_ENABLED=false\n")
    d = gmod.gen_r4_strict("20260101T000000Z", per_symbol_credential_scope=True)
    assert d.get("per_symbol_credential_scope") is True
    sym_rows = [c for c in d["checklist"] if c.get("symbol")]
    assert len(sym_rows) == 4, f"expected 4 per-symbol rows (2 venues x 2 symbols), got {len(sym_rows)}"
    for row in sym_rows:
        assert row["confirmed"] is False
        assert row.get("scope") == "paper_only"
        assert "venue" in row and row["venue"] in ("deribit", "okx")
        assert "symbol" in row and row["symbol"] in ("BTC", "ETH")
        assert row.get("evidence_refs")
    ok, issues = v.validate_artifact(d, "R4")
    assert ok, issues


def test_secret_scanner_catches_real_secret_patterns(tmp_path, monkeypatch):
    import generate_r4_credential_controls_checklist as gmod

    rs = tmp_path / "research_state"
    rs.mkdir(parents=True)
    (rs / "PAPER_OPS_SESSION_GATE_20260101T000000Z.json").write_text(json.dumps({
        "gates": {"paper_ops_ready": True},
        "api_key": "sk_live51ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    }))
    monkeypatch.setattr(gmod, "RS", rs)
    monkeypatch.setattr(gmod, "REPO", tmp_path)
    (tmp_path / "src" / "config").mkdir(parents=True)
    (tmp_path / "src" / "config" / "secrets.py").write_text('LIVE_TRADING_ENABLED = "false"\n')
    (tmp_path / ".env.example").write_text("LIVE_TRADING_ENABLED=false\n")
    d = gmod.gen_r4_strict("20260101T000000Z")
    assert d["secrets_committed"] is True
    assert d["secret_scan"]["hit_count"] > 0
    assert any("secret_pattern" in h for h in d["secret_scan"]["hits"])
    # artifact with secrets must not validate as pass
    ok, issues = v.validate_artifact(d, "R4")
    assert not ok
    assert any("secrets_committed_must_be_false" in i for i in issues)


def test_r4_never_unblocks_next9(tmp_path, monkeypatch):
    import generate_r4_credential_controls_checklist as gmod

    rs = tmp_path / "research_state"
    rs.mkdir(parents=True)
    (rs / "campaign_checkpoints").mkdir(parents=True)
    (rs / "CROSSVENUE_ORCHESTRATION_REPORT.json").write_text(json.dumps({"paper_only": True, "venues": ["deribit"], "symbols": ["BTC"], "config": {"venues": ["deribit"], "symbols": ["BTC"]}}))
    (rs / "PHASE37_CROSS_VENUE_ROUTING_REPORT.json").write_text(json.dumps({"ok": True, "cycles": 3}))
    monkeypatch.setattr(gmod, "RS", rs)
    monkeypatch.setattr(gmod, "REPO", tmp_path)
    (tmp_path / "src" / "config").mkdir(parents=True)
    (tmp_path / "src" / "config" / "secrets.py").write_text('LIVE_TRADING_ENABLED = "false"\n')
    (tmp_path / ".env.example").write_text("LIVE_TRADING_ENABLED=false\n")
    d = gmod.gen_r4_strict("20260101T000000Z", per_symbol_credential_scope=True, effective_until_hours=168)
    assert d["next9_unblocked"] is False
    assert d["live_trading_enabled"] is False
    assert d["paper_only"] is True
    assert d["attestation_only"] is True
    assert d["advisory"] is True
    ok, issues = v.validate_artifact(d, "R4")
    assert ok, issues
