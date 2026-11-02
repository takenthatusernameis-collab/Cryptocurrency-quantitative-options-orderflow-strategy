"""
Tests for Phase 41: Cross-Venue Settlement & Finality for Crypto Options + Orderflow
"""
import json
import math
from pathlib import Path

from src.settlement.phase41_cross_venue_settlement import (
    Phase41CrossVenueSettlement,
    Phase41SettlementConfig,
    SettlementInstruction,
    SettlementReceipt,
    SettlementCycle,
)
from src.integration.phase41_settlement_loop import Phase41SettlementLoop, Loop41Config


def test_phase41_config_defaults():
    c = Phase41SettlementConfig()
    assert c.paper_only is True
    assert c.seed == 41041
    assert "BTC" in c.underlyings
    assert "deribit" in c.venues


def test_phase41_config_paper_only_hard_gate():
    try:
        Phase41CrossVenueSettlement(Phase41SettlementConfig(paper_only=False))
        assert False, "should have raised"
    except ValueError:
        pass


def test_phase41_loop_config_paper_only_hard_gate():
    try:
        Phase41SettlementLoop(Loop41Config(paper_only=False, modes="paper"))
        assert False, "should have raised"
    except ValueError:
        pass


def test_phase41_build_instructions():
    s = Phase41CrossVenueSettlement(seed=41041)
    trades = [{"symbol": "BTC-PERP", "venue": "deribit", "qty": 1.0}, {"symbol": "ETH-PERP", "venue": "okx", "qty": -0.5}]
    instrs, meta = s.build_settlement_instructions(0, trades)
    assert len(instrs) == 2
    assert instrs[0].venue == "deribit"
    assert meta["instructions_count"] == 2
    assert math.isfinite(meta["total_notional_usd"])


def test_phase41_settle_instructions():
    s = Phase41CrossVenueSettlement(seed=41042)
    trades = [{"symbol": "BTC-PERP", "venue": "deribit", "qty": 1.0}]
    instrs, _ = s.build_settlement_instructions(0, trades)
    rcpts, meta = s.settle_instructions(0, instrs)
    assert len(rcpts) == 1
    assert rcpts[0].finality in (True, False)
    assert math.isfinite(rcpts[0].settled_notional_usd)
    assert math.isfinite(rcpts[0].collateral_ratio_after)


def test_phase41_run_cycle():
    s = Phase41CrossVenueSettlement(seed=41043)
    trades = [{"symbol": "BTC-PERP", "venue": "deribit", "qty": 1.0}, {"symbol": "ETH-PERP", "venue": "okx", "qty": -1.0}]
    cyc = s.run_cycle(0, trades)
    assert cyc.paper_only is True
    assert cyc.regime in ("normal", "calm", "stressed", "volatile", "crisis")
    assert len(cyc.instructions) == 2
    assert len(cyc.receipts) == 2
    assert isinstance(cyc.finality_ok_all, bool)
    assert isinstance(cyc.margin_gates_ok, bool)
    assert isinstance(cyc.trading_enabled, bool)


def test_phase41_run_campaign():
    s = Phase41CrossVenueSettlement(seed=41044)
    camp = s.run_campaign(cycles=16)
    assert camp["phase"] == "PHASE41_CROSS_VENUE_SETTLEMENT"
    assert camp["paper_only"] is True
    assert camp["n_cycles"] == 16
    assert camp["total_instructions"] > 0
    assert camp["gates_ok"] is True
    assert math.isfinite(camp["total_fees_usd"])


def test_phase41_loop_run(tmp_path):
    cfg = Loop41Config(cycles=4, outdir=str(tmp_path))
    loop = Phase41SettlementLoop(cfg)
    res = loop.run()
    assert res["phase"] == "PHASE41_SETTLEMENT_LOOP"
    assert res["paper_only"] is True
    assert res["gates_ok"] is True
    assert "integrated_with" in res
    assert res["n_cycles"] == 4


def test_phase41_reports_written_by_loop(tmp_path):
    cfg = Loop41Config(cycles=3, outdir=str(tmp_path))
    loop = Phase41SettlementLoop(cfg)
    res = loop.run()
    assert (tmp_path / "PHASE41_SETTLEMENT_LOOP_REPORT.json").exists()
    assert (tmp_path / "PHASE41_CAMPAIGN_SUMMARY.json").exists()
    assert (tmp_path / "PHASE41_CROSS_VENUE_SETTLEMENT_REPORT.json").exists()
    assert (tmp_path / "PHASE41_SETTLEMENT_SUMMARY.json").exists()


def test_phase41_crypto_options_symbol():
    s = Phase41CrossVenueSettlement(seed=41045)
    trades = [{"symbol": "ETH-20261226-4000-P", "qty": -2.0, "venue": "deribit"}]
    instrs, _ = s.build_settlement_instructions(0, trades)
    assert instrs[0].symbol == "ETH-20261226-4000-P"


def test_phase41_finality_tracking():
    s = Phase41CrossVenueSettlement(seed=41046)
    trades = [{"symbol": "BTC-PERP", "venue": "deribit", "qty": 1.0}]
    instrs, _ = s.build_settlement_instructions(0, trades)
    rcpts, _ = s.settle_instructions(0, instrs)
    assert isinstance(rcpts[0].finality, bool)
    assert isinstance(rcpts[0].confirmations, int)


def test_phase41_margin_impact():
    s = Phase41CrossVenueSettlement(seed=41047)
    trades = [{"symbol": "BTC-PERP", "venue": "okx", "qty": 2.0}]
    instrs, _ = s.build_settlement_instructions(0, trades)
    rcpts, _ = s.settle_instructions(0, instrs, collateral_balances={"okx:USDC": 50000.0})
    assert math.isfinite(rcpts[0].margin_impact_usd)
    assert math.isfinite(rcpts[0].collateral_ratio_after)


def test_phase41_discrepancy_dataclass():
    ins = SettlementInstruction("i1", 0, "deribit", "BTC-PERP", "buy", 1.0, 65000.0, "USDC", 6500.0, "k1", 1, "2026-01-01T00:00:00Z")
    assert ins.venue == "deribit"


def test_phase41_receipt_dataclass():
    rc = SettlementReceipt("r1", "i1", 0, "deribit", "BTC-PERP", "settled", 1.0, 65000.0, 19.5, True, 12, 6500.0, 3.2, "2026-01-01T00:00:00Z")
    assert rc.finality is True


def test_phase41_cycle_dataclass():
    ins = SettlementInstruction("i1", 0, "deribit", "BTC-PERP", "buy", 1.0, 65000.0, "USDC", 6500.0, "k1", 1, "2026-01-01T00:00:00Z")
    rc = SettlementReceipt("r1", "i1", 0, "deribit", "BTC-PERP", "settled", 1.0, 65000.0, 19.5, True, 12, 6500.0, 3.2, "2026-01-01T00:00:00Z")
    cyc = SettlementCycle(0, "2026-01-01T00:00:00Z", True, "normal", (ins,), (rc,), 65000.0, 19.5, 0, 0, True, True, True, "", "abc123")
    assert cyc.finality_ok_all is True


def test_phase41_campaign_summary_structure():
    s = Phase41CrossVenueSettlement(seed=41048)
    camp = s.run_campaign(cycles=5)
    required = ["phase", "timestamp_utc", "seed", "paper_only", "n_cycles", "total_instructions", "total_receipts", "total_fees_usd", "total_pending", "total_failed", "finality_ok_all_cycles", "margin_gates_ok_all_cycles", "trading_enabled_all_cycles", "gates_ok"]
    for r in required:
        assert r in camp


def test_phase41_all_finite_in_campaign():
    s = Phase41CrossVenueSettlement(seed=41049)
    camp = s.run_campaign(cycles=10)
    def check(x):
        if isinstance(x, float):
            assert math.isfinite(x)
        elif isinstance(x, dict):
            for v in x.values():
                check(v)
        elif isinstance(x, list):
            for v in x:
                check(v)
        elif isinstance(x, tuple):
            for v in x:
                check(v)
    check(camp)
