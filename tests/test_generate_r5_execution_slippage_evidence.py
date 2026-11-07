from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(REPO / "scripts"))
import generate_r5_execution_slippage_evidence as g  # noqa: E402
import validate_r3_r7_reduction_evidence as v  # noqa: E402


def test_gen_r5_strict_produces_valid_artifact():
    ts = g._utc()
    d = g.gen_r5_strict(ts)
    ok, issues = v.validate_artifact(d, "R5")
    assert ok, issues
    assert d["artifact_type"] == v.ARTIFACT_TYPES["R5"]
    assert d["paper_only"] is True
    assert d["live_trading_enabled"] is False
    assert d["next9_unblocked"] is False
    assert d["metrics"]["slippage_assumption_documented"] is True
    assert d["metrics"]["fill_quality_documented"] is True
    assert d["paper_or_backtest_derived"] is True
    assert d["advisory"] is True
    assert isinstance(d["evidence_refs"], list) and len(d["evidence_refs"]) > 0


def test_main_writes_valid_r5_artifact(tmp_path, monkeypatch):
    import generate_r5_execution_slippage_evidence as gmod

    rs = tmp_path / "research_state"
    rs.mkdir(parents=True)
    # generator prints relative_to(REPO); make REPO=tmp_path for this test
    monkeypatch.setattr(gmod, "RS", rs)
    monkeypatch.setattr(gmod, "REPO", tmp_path)
    rc = gmod.main([])
    assert rc == 0
    out = list(rs.glob("R5_EXECUTION_SLIPPAGE_SIM_EVIDENCE_*.json"))
    assert len(out) == 1
    d = json.loads(out[0].read_text())
    ok, issues = v.validate_artifact(d, "R5")
    assert ok, issues
    assert d["metrics"]["within_conservative_caps"] is True


def test_r5_cites_cross_venue_slippage_breakdown():
    d = g.gen_r5_strict(g._utc())
    bd = d["metrics"].get("cross_venue_slippage_breakdown")
    assert isinstance(bd, dict)
    assert set(bd.get("venues", [])) == {"deribit", "okx", "binance"}
    assert set(bd.get("symbols", [])) == {"BTC", "ETH"}
    assert "per_venue" in bd and "per_symbol" in bd
    for venue in ("deribit", "okx", "binance"):
        row = bd["per_venue"][venue]
        assert "ewma_ms" in row and "taker_fee_bps" in row
    for symbol in ("BTC", "ETH"):
        assert set(bd["per_symbol"][symbol]["venues"].keys()) == {"deribit", "okx", "binance"}
    assert isinstance(bd.get("within_conservative_caps"), bool)
    refs = " ".join(d["evidence_refs"])
    assert "CROSSVENUE_ORCHESTRATION_REPORT.json" in refs
    assert "PHASE37_CROSS_VENUE_ROUTING_REPORT.json" in refs


def test_r5_per_symbol_slippage_default_off(tmp_path, monkeypatch):
    import generate_r5_execution_slippage_evidence as gmod

    rs = tmp_path / "research_state"
    rs.mkdir(parents=True)
    cross = {
        "paper_only": True,
        "venues": ["deribit", "okx"],
        "symbols": ["BTC", "ETH"],
        "config": {"venues": ["deribit", "okx"], "symbols": ["BTC", "ETH"], "taker_fee_bps": {"deribit": 5.0, "okx": 5.0}},
        "components": {
            "latency_routing": {
                "latency": {
                    "deribit": {"ewma_ms": 26.46, "samples": 10, "max_sample_ms": 46.83, "within_limit": True},
                    "okx": {"ewma_ms": 23.74, "samples": 10, "max_sample_ms": 44.92, "within_limit": True},
                },
                "slippage": {"avg_slippage_bps": 0.5, "max_slippage_bps": 2.0, "fills": 0, "total_slippage_bps": 0.0},
            },
        },
    }
    (rs / "CROSSVENUE_ORCHESTRATION_REPORT.json").write_text(json.dumps(cross))
    (rs / "PHASE37_CROSS_VENUE_ROUTING_REPORT.json").write_text(json.dumps({"ok": True, "cycles": 3}))
    monkeypatch.setattr(gmod, "RS", rs)
    monkeypatch.setattr(gmod, "REPO", tmp_path)
    d = gmod.gen_r5_strict("20260101T000000Z")
    assert d.get("per_symbol_slippage") is False
    assert not any(w.startswith("per_symbol_slippage_breakdown_emitted") for w in d["warn_flags"])


def test_r5_per_symbol_slippage_emitted_when_flag_set(tmp_path, monkeypatch):
    import generate_r5_execution_slippage_evidence as gmod

    rs = tmp_path / "research_state"
    rs.mkdir(parents=True)
    cross = {
        "paper_only": True,
        "venues": ["deribit", "okx"],
        "symbols": ["BTC", "ETH"],
        "config": {"venues": ["deribit", "okx"], "symbols": ["BTC", "ETH"], "taker_fee_bps": {"deribit": 5.0, "okx": 5.0}},
        "components": {
            "latency_routing": {
                "latency": {
                    "deribit": {"ewma_ms": 26.46, "samples": 10, "max_sample_ms": 46.83, "within_limit": True},
                    "okx": {"ewma_ms": 23.74, "samples": 10, "max_sample_ms": 44.92, "within_limit": True},
                },
                "slippage": {"avg_slippage_bps": 0.5, "max_slippage_bps": 2.0, "fills": 0, "total_slippage_bps": 0.0},
            },
            "market_making": {"per_symbol": {"BTC": {"gross_notional_usd": 1000.0, "net_delta_usd": 10.0}, "ETH": {"gross_notional_usd": 2000.0, "net_delta_usd": -10.0}}},
        },
    }
    (rs / "CROSSVENUE_ORCHESTRATION_REPORT.json").write_text(json.dumps(cross))
    (rs / "PHASE37_CROSS_VENUE_ROUTING_REPORT.json").write_text(json.dumps({"ok": True, "cycles": 3}))
    monkeypatch.setattr(gmod, "RS", rs)
    monkeypatch.setattr(gmod, "REPO", tmp_path)
    d = gmod.gen_r5_strict("20260101T000000Z", per_symbol_slippage=True)
    assert d.get("per_symbol_slippage") is True
    assert any(w == "per_symbol_slippage_breakdown_emitted_advisory" for w in d["warn_flags"])
    bd = d["metrics"]["cross_venue_slippage_breakdown"]
    for symbol in ("BTC", "ETH"):
        for venue in ("deribit", "okx"):
            row = bd["per_symbol"][symbol]["venues"][venue]
            assert "ewma_ms" in row and "taker_fee_bps" in row
    assert bd["per_symbol"]["BTC"]["gross_notional_usd"] == 1000.0
    assert bd["per_symbol"]["ETH"]["net_delta_usd"] == -10.0
    ok, issues = v.validate_artifact(d, "R5")
    assert ok, issues
    assert d["next9_unblocked"] is False
    assert d["live_trading_enabled"] is False
    assert d["paper_only"] is True
