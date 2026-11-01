"""Phase 16: Advanced Orderflow Signal Fusion + Cross-Asset Options Vol Surface Arb."""
from __future__ import annotations

import json
import math
from pathlib import Path

from src.alpha.phase16_campaign import Phase16Campaign
from src.alpha.orderflow_alpha import OrderflowAlphaEngine
from src.alpha.vol_surface_rv import VolSurfaceRVEngine, VolSurfaceRVConfig
from src.alpha.signal_fusion import SignalFusion
from src.data.schemas import OptionContract, OptionQuote, OptionsChain, OrderflowSnapshot, Trade
from src.telemetry.serialization import assert_json_valid
from datetime import datetime, timezone, timedelta


class TestPhase16Imports:
    def test_campaign_import(self):
        from src.alpha.phase16_campaign import Phase16Campaign
        c = Phase16Campaign(symbols=("BTC",), seed=1, cycles=1)
        assert hasattr(c, "run")

    def test_script_exists(self):
        assert Path("scripts/run_phase16_orderflow_vol_arb_campaign.py").exists()


class TestPhase16Orderflow:
    def test_orderflow_engine_deterministic_p16(self):
        camp = Phase16Campaign(symbols=("BTC",), seed=123)
        snap = camp._gen_orderflow("BTC")
        eng = OrderflowAlphaEngine(seed=123)
        f1 = eng.extract_features(snap)
        f2 = eng.extract_features(snap)
        assert f1.cumulative_delta == f2.cumulative_delta
        rep = eng.generate_report([f1])
        assert_json_valid(rep)

    def test_orderflow_features_finite(self):
        camp = Phase16Campaign(symbols=("ETH",), seed=7)
        snap = camp._gen_orderflow("ETH")
        eng = OrderflowAlphaEngine(seed=7)
        f = eng.extract_features(snap)
        for v in [f.cumulative_delta, f.delta_divergence, f.absorption_score, f.sweep_score,
                  f.vpin_lite, f.liquidity_vacuum_score, f.footprint_imbalance,
                  f.net_aggression, f.large_trade_ratio]:
            assert math.isfinite(v)
        assert isinstance(f.valid, bool)


class TestPhase16VolSurfaceRV:
    def test_rv_engine_deterministic_p16(self):
        camp = Phase16Campaign(symbols=("BTC",), seed=42)
        chain = camp._gen_chain("BTC")
        eng = VolSurfaceRVEngine(VolSurfaceRVConfig(seed=42))
        opps1 = eng.detect_dislocations(chain, spot=65000.0)
        opps2 = eng.detect_dislocations(chain, spot=65000.0)
        assert [o.rationale_hash for o in opps1] == [o.rationale_hash for o in opps2]
        rep = eng.generate_report(opps1, 42)
        assert_json_valid(rep)

    def test_rv_opps_finite(self):
        camp = Phase16Campaign(symbols=("BTC", "ETH"), seed=9)
        eng = VolSurfaceRVEngine(VolSurfaceRVConfig(seed=9))
        for sym in ("BTC", "ETH"):
            chain = camp._gen_chain(sym)
            spot = 65000.0 if sym == "BTC" else 3400.0
            opps = eng.detect_dislocations(chain, spot=spot)
            for o in opps:
                assert math.isfinite(o.mark_iv)
                assert math.isfinite(o.fitted_iv)
                assert math.isfinite(o.residual_iv)
                assert math.isfinite(o.residual_sigma_vega_weighted)
                assert math.isfinite(o.vega)
                assert o.arb_ok is True or o.arb_ok is False


class TestPhase16Fusion:
    def test_fusion_gates_p16(self):
        eng = VolSurfaceRVEngine(VolSurfaceRVConfig(seed=7))
        camp = Phase16Campaign(symbols=("ETH",), seed=7)
        chain = camp._gen_chain("ETH")
        opps = eng.detect_dislocations(chain, spot=3400.0)
        ofeng = OrderflowAlphaEngine(seed=7)
        feat = ofeng.extract_features(camp._gen_orderflow("ETH"))
        fusion = SignalFusion(seed=7, max_abs_delta=0.15, max_abs_vega=0.10, gamma_band=0.05, min_liquidity=0.0, min_dte=1, max_dte=90)
        intents = fusion.fuse(opps, [feat], {"ETH": 0.01})
        for it in intents:
            assert abs(it.delta_est) <= 0.15 + 1e-12
            assert abs(it.vega_est) <= 0.10 + 1e-12
            assert abs(it.gamma_est) <= 0.05 + 1e-12
            assert math.isfinite(it.confidence)
        rep = fusion.generate_report(intents)
        assert_json_valid(rep)

    def test_fusion_deterministic_p16(self):
        eng = VolSurfaceRVEngine(VolSurfaceRVConfig(seed=11))
        camp = Phase16Campaign(symbols=("BTC",), seed=11)
        chain = camp._gen_chain("BTC")
        opps = eng.detect_dislocations(chain, spot=65000.0)
        ofeng = OrderflowAlphaEngine(seed=11)
        feat = ofeng.extract_features(camp._gen_orderflow("BTC"))
        fusion = SignalFusion(seed=11)
        i1 = fusion.fuse(opps, [feat], {"BTC": 0.01})
        i2 = fusion.fuse(opps, [feat], {"BTC": 0.01})
        assert [x.intent_id for x in i1] == [x.intent_id for x in i2]


class TestPhase16CampaignBasics:
    def test_campaign_init_paper_only(self):
        c = Phase16Campaign(symbols=("BTC", "ETH"), seed=42, venues=("deribit", "okx", "binance"), cycles=5)
        assert c.paper_only is True
        assert c.campaign_id == "phase16_42"

    def test_campaign_live_forbidden(self):
        try:
            Phase16Campaign(paper_only=False)
            assert False, "should raise"
        except ValueError:
            pass


class TestPhase16Determinism:
    def test_deterministic_campaign_small_p16(self, tmp_path):
        c1 = Phase16Campaign(symbols=("BTC",), seed=777, venues=("deribit", "okx"), cycles=2, outdir=tmp_path / "a")
        c2 = Phase16Campaign(symbols=("BTC",), seed=777, venues=("deribit", "okx"), cycles=2, outdir=tmp_path / "b")
        r1 = c1.run()
        r2 = c2.run()
        assert r1["status"] == r2["status"]
        assert r1["campaign_id"] == r2["campaign_id"]

    def test_campaign_artifacts_created_p16(self, tmp_path):
        c = Phase16Campaign(symbols=("BTC", "ETH"), seed=888, venues=("deribit", "okx", "binance"), cycles=3, outdir=tmp_path)
        r = c.run()
        assert len(r["artifacts"]) >= 6
        for a in r["artifacts"]:
            assert Path(a).exists()


class TestPhase16RequiredArtifacts:
    def test_all_required_artifacts_exist(self, tmp_path):
        c = Phase16Campaign(symbols=("BTC", "ETH"), seed=42, venues=("deribit", "okx", "binance"), cycles=5, outdir=tmp_path)
        r = c.run()
        assert (tmp_path / "PHASE16_ORDERFLOW_VOL_ARB_REPORT.json").exists()
        assert (tmp_path / "PHASE16_ORDERFLOW_VOL_ARB_REPORT.md").exists()
        assert (tmp_path / "ORDERFLOW_SIGNAL_FUSION_REPORT.json").exists()
        assert (tmp_path / "ORDERFLOW_SIGNAL_FUSION_REPORT.md").exists()
        assert (tmp_path / "VOL_SURFACE_ARB_REPORT.json").exists()
        assert (tmp_path / "VOL_SURFACE_ARB_REPORT.md").exists()

    def test_master_has_required_fields_p16(self, tmp_path):
        c = Phase16Campaign(symbols=("BTC", "ETH"), seed=42, venues=("deribit", "okx", "binance"), cycles=5, outdir=tmp_path)
        r = c.run()
        m = r["master_report"]
        assert m["campaign_id"] == "phase16_42"
        assert m["seed"] == 42
        assert m["paper_only"] is True
        assert m["status"] == "completed"
        assert "git_sha" in m
        assert "artifacts" in m
        assert "counts" in m


class TestPhase16Integrity:
    def test_no_nan_inf_in_all_json_p16(self, tmp_path):
        c = Phase16Campaign(symbols=("BTC", "ETH"), seed=55, venues=("deribit", "okx", "binance"), cycles=4, outdir=tmp_path)
        r = c.run()
        for art in r["artifacts"]:
            if art.endswith(".json"):
                data = json.loads(Path(art).read_text())
                s = json.dumps(data)
                assert "NaN" not in s
                assert "Infinity" not in s
                assert_json_valid(data)

    def test_reports_have_campaign_metadata(self, tmp_path):
        c = Phase16Campaign(symbols=("BTC",), seed=66, venues=("deribit",), cycles=2, outdir=tmp_path)
        r = c.run()
        for name in ["PHASE16_ORDERFLOW_VOL_ARB_REPORT.json", "ORDERFLOW_SIGNAL_FUSION_REPORT.json", "VOL_SURFACE_ARB_REPORT.json"]:
            data = json.loads((tmp_path / name).read_text())
            assert data.get("campaign_id") == "phase16_66"
            assert data.get("paper_only") is True
            assert data.get("seed") == 66


class TestPhase16Integration:
    def test_full_integration_seed42_btc_eth_three_venues_p16(self, tmp_path):
        c = Phase16Campaign(symbols=("BTC", "ETH"), seed=42, venues=("deribit", "okx", "binance"), cycles=5, outdir=tmp_path)
        r = c.run()
        assert r["status"] == "completed"
        m = r["master_report"]
        assert m["counts"]["rv_opportunities"] >= 0
        assert m["counts"]["orderflow_features"] == 2
        assert "fused_intents" in m["counts"]

    def test_multi_symbol_integration_p16(self, tmp_path):
        c = Phase16Campaign(symbols=("BTC", "ETH"), seed=2024, venues=("deribit", "okx", "binance"), cycles=3, outdir=tmp_path)
        r = c.run()
        m = r["master_report"]
        assert set(m["symbols"]) == {"BTC", "ETH"}

    def test_campaign_cycles_respected_p16(self, tmp_path):
        c = Phase16Campaign(symbols=("BTC",), seed=303, venues=("deribit",), cycles=7, outdir=tmp_path)
        r = c.run()
        assert r["master_report"]["cycles"] == 7


class TestPhase16Stress:
    def test_many_cycles_p16(self, tmp_path):
        c = Phase16Campaign(symbols=("BTC", "ETH"), seed=404, venues=("deribit", "okx", "binance"), cycles=10, outdir=tmp_path)
        r = c.run()
        assert r["status"] == "completed"
        assert len(r["artifacts"]) >= 6

    def test_different_seeds_produce_different_campaign_ids_p16(self, tmp_path):
        c1 = Phase16Campaign(symbols=("BTC",), seed=1, cycles=1, outdir=tmp_path / "x")
        c2 = Phase16Campaign(symbols=("BTC",), seed=2, cycles=1, outdir=tmp_path / "y")
        r1 = c1.run()
        r2 = c2.run()
        assert r1["campaign_id"] != r2["campaign_id"]

    def test_artifacts_count_nonzero_p16(self, tmp_path):
        c = Phase16Campaign(symbols=("BTC",), seed=505, cycles=1, outdir=tmp_path)
        r = c.run()
        assert len(r["artifacts"]) > 0
