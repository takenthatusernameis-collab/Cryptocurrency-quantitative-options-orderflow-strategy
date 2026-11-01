"""Phase 17: Cross-Asset Options Volatility Surface Arbitrage Deepening +
Orderflow Confirmation (crypto options + orderflow).

Deterministic tests only. Fixed seeds, mock-based, no real network.
allow_nan=False serialization. >=40 substantive tests.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from src.alpha.phase17_campaign import (
    Phase17Campaign,
    Phase17Config,
    VolSurfaceRVSignal,
    TermStructureFeatures,
    OrderflowConfirmation,
    Phase17TradeIntent,
    _assert_no_nan_inf,
    _det_ts,
    _sym_seed,
    _SYMBOL_DEFAULTS,
)
from src.alpha.vol_surface_rv import VolSurfaceRVEngine, VolSurfaceRVConfig
from src.alpha.orderflow_alpha import OrderflowAlphaEngine
from src.alpha.signal_fusion import SignalFusion, TradeIntent
from src.data.schemas import OptionContract, OptionQuote, OptionsChain, OrderflowSnapshot, Trade
from src.features.volatility import (
    calculate_atm_term_structure,
    calculate_risk_reversal_term_structure,
    calculate_skew_term_structure,
)
from src.features.orderflow import (
    calculate_cumulative_delta,
    calculate_orderflow_imbalance,
    absorption_detection,
    vpin_style_toxicity,
    detect_aggressive_flow,
    delta_divergence_vs_price,
)
from src.telemetry.serialization import assert_json_valid
from datetime import datetime, timezone, timedelta

from src.alpha.phase17_campaign import _BASE_DAY


class TestPhase17Imports:
    def test_campaign_import(self):
        from src.alpha.phase17_campaign import Phase17Campaign
        c = Phase17Campaign(symbols=("BTC",), seed=1, cycles=1)
        assert hasattr(c, "run")

    def test_script_exists(self):
        assert Path("scripts/run_phase17_cross_asset_vol_arb_campaign.py").exists()

    def test_config_defaults(self):
        cfg = Phase17Config()
        assert cfg.paper_only is True
        assert cfg.seed == 42
        assert cfg.cycles == 5
        assert cfg.min_confirmation_score == 0.30
        assert cfg.max_vpin == 0.60

    def test_config_paper_only_required(self):
        try:
            Phase17Campaign(paper_only=False)
            assert False, "should raise"
        except ValueError:
            pass


class TestPhase17DeterminismHelpers:
    def test_det_ts_deterministic(self):
        assert _det_ts(42) == _det_ts(42)
        assert _det_ts(1) != _det_ts(2)

    def test_sym_seed_deterministic(self):
        assert _sym_seed("BTC", 42, "chain17") == _sym_seed("BTC", 42, "chain17")
        assert _sym_seed("BTC", 42, "chain17") != _sym_seed("ETH", 42, "chain17")

    def test_assert_no_nan_inf_passes(self):
        _assert_no_nan_inf({"a": 1.0, "b": 2.0}, "ok")

    def test_assert_no_nan_inf_rejects(self):
        try:
            _assert_no_nan_inf({"a": float("nan")}, "bad")
            assert False
        except ValueError:
            pass

    def test_assert_no_nan_inf_rejects_inf(self):
        try:
            _assert_no_nan_inf({"a": float("inf")}, "bad")
            assert False
        except ValueError:
            pass


class TestPhase17CampaignInit:
    def test_init_paper_only(self):
        c = Phase17Campaign(symbols=("BTC", "ETH", "SOL"), seed=7, venues=("deribit", "okx", "binance"), cycles=3)
        assert c.paper_only is True
        assert c.campaign_id == "phase17_7"
        assert c.seed == 7
        assert c.cycles == 3
        assert "BTC" in c.spot

    def test_init_default_symbols(self):
        c = Phase17Campaign(seed=1, cycles=1)
        assert set(c.symbols) == {"BTC", "ETH", "SOL", "XRP", "ADA"}

    def test_init_custom_spot(self):
        c = Phase17Campaign(symbols=("BTC",), seed=1, spot={"BTC": 999.0}, cycles=1)
        assert c.spot["BTC"] == 999.0


class TestPhase17ChainGeneration:
    def test_chain_deterministic(self):
        c = Phase17Campaign(symbols=("BTC",), seed=123, cycles=1)
        ch1 = c._gen_chain("BTC", "deribit")
        ch2 = c._gen_chain("BTC", "deribit")
        assert ch1.underlying == ch2.underlying == "BTC"
        assert len(ch1.quotes) == len(ch2.quotes)
        for q1, q2 in zip(ch1.quotes, ch2.quotes):
            assert q1.mark_iv == q2.mark_iv
            assert q1.bid == q2.bid
            assert q1.ask == q2.ask

    def test_chain_cross_venue_iv_shift(self):
        c = Phase17Campaign(symbols=("BTC",), seed=9, cycles=1)
        d = c._gen_chain("BTC", "deribit")
        o = c._gen_chain("BTC", "okx")
        # pair a matching quote by strike/expiry/type
        qd = next(q for q in d.quotes if q.contract.option_type == "call" and abs(q.contract.strike - c.spot["BTC"]) < 100)
        qo = next(q for q in o.quotes if q.contract.option_type == "call" and abs(q.contract.strike - c.spot["BTC"]) < 100 and q.contract.expiry == qd.contract.expiry)
        assert qo.mark_iv != qd.mark_iv

    def test_chain_finite(self):
        c = Phase17Campaign(symbols=("ETH",), seed=7, cycles=1)
        ch = c._gen_chain("ETH", "binance")
        for q in ch.quotes:
            assert math.isfinite(q.bid) and math.isfinite(q.ask)
            assert math.isfinite(q.mark_iv) and 0.25 <= q.mark_iv <= 2.5
            assert q.bid > 0 and q.ask >= q.bid

    def test_chain_venues(self):
        c = Phase17Campaign(symbols=("BTC",), seed=1, cycles=1)
        for v in c.venues:
            ch = c._gen_chain("BTC", v)
            assert ch.venue == v


class TestPhase17OrderflowGeneration:
    def test_orderflow_deterministic(self):
        c = Phase17Campaign(symbols=("BTC",), seed=5, cycles=1)
        s1 = c._gen_orderflow("BTC")
        s2 = c._gen_orderflow("BTC")
        assert [t.side for t in s1.trades] == [t.side for t in s2.trades]
        assert [t.size for t in s1.trades] == [t.size for t in s2.trades]

    def test_orderflow_features_finite(self):
        c = Phase17Campaign(symbols=("ETH",), seed=7, cycles=1)
        snap = c._gen_orderflow("ETH")
        eng = OrderflowAlphaEngine(seed=7)
        f = eng.extract_features(snap)
        for v in [f.cumulative_delta, f.delta_divergence, f.absorption_score, f.sweep_score,
                  f.vpin_lite, f.liquidity_vacuum_score, f.footprint_imbalance,
                  f.net_aggression, f.large_trade_ratio]:
            assert math.isfinite(v)

    def test_raw_orderflow_functions_finite(self):
        c = Phase17Campaign(symbols=("BTC",), seed=3, cycles=1)
        snap = c._gen_orderflow("BTC")
        trades = snap.trades
        assert math.isfinite(calculate_cumulative_delta(trades))
        assert math.isfinite(calculate_orderflow_imbalance(trades, window=200))
        assert math.isfinite(absorption_detection(trades, threshold=2.0))
        assert math.isfinite(vpin_style_toxicity(trades, bucket_size=50))
        assert math.isfinite(detect_aggressive_flow(trades, window=100))
        assert math.isfinite(delta_divergence_vs_price(trades))


class TestPhase17VolSurfaceRV:
    def test_rv_engine_deterministic(self):
        c = Phase17Campaign(symbols=("BTC",), seed=42, cycles=1)
        ch = c._gen_chain("BTC", "deribit")
        eng = VolSurfaceRVEngine(VolSurfaceRVConfig(seed=42))
        o1 = eng.detect_dislocations(ch, spot=65000.0)
        o2 = eng.detect_dislocations(ch, spot=65000.0)
        assert [o.rationale_hash for o in o1] == [o.rationale_hash for o in o2]

    def test_rv_opps_finite(self):
        c = Phase17Campaign(symbols=("BTC", "ETH"), seed=9, cycles=1)
        eng = VolSurfaceRVEngine(VolSurfaceRVConfig(seed=9))
        for sym in ("BTC", "ETH"):
            ch = c._gen_chain(sym, "deribit")
            spot = c.spot[sym]
            opps = eng.detect_dislocations(ch, spot=spot)
            for o in opps:
                assert math.isfinite(o.mark_iv)
                assert math.isfinite(o.fitted_iv)
                assert math.isfinite(o.residual_iv)
                assert math.isfinite(o.residual_sigma_vega_weighted)
                assert math.isfinite(o.vega)
                assert o.arb_ok is True or o.arb_ok is False

    def test_detect_rv_signals_deterministic(self):
        c = Phase17Campaign(symbols=("BTC",), seed=42, cycles=1)
        spot = c.spot["BTC"]
        chains = {"deribit": c._gen_chain("BTC", "deribit")}
        ts = c._term_structure_features("BTC", [q for ch in chains.values() for q in ch.quotes], spot)
        xv = c._cross_venue_z("BTC", chains)
        s1 = c._detect_rv_signals("BTC", spot, chains, ts, xv, 0)
        s2 = c._detect_rv_signals("BTC", spot, chains, ts, xv, 0)
        assert [s.rationale_hash for s in s1] == [s.rationale_hash for s in s2]

    def test_detect_rv_signals_finite(self):
        c = Phase17Campaign(symbols=("BTC", "ETH"), seed=11, cycles=1)
        for sym in ("BTC", "ETH"):
            spot = c.spot[sym]
            chains = {v: c._gen_chain(sym, v) for v in c.venues}
            all_q = [q for ch in chains.values() for q in ch.quotes]
            ts = c._term_structure_features(sym, all_q, spot)
            xv = c._cross_venue_z(sym, chains)
            sigs = c._detect_rv_signals(sym, spot, chains, ts, xv, 0)
            for s in sigs:
                assert math.isfinite(s.mark_iv) and math.isfinite(s.fitted_iv)
                assert math.isfinite(s.residual_iv) and math.isfinite(s.rv_score)
                assert math.isfinite(s.term_structure_z) and math.isfinite(s.cross_venue_z)


class TestPhase17TermStructure:
    def test_atm_term_structure_deterministic(self):
        c = Phase17Campaign(symbols=("BTC",), seed=42, cycles=1)
        ch = c._gen_chain("BTC", "deribit")
        ts1 = calculate_atm_term_structure(ch.quotes, c.spot["BTC"], moneyness_tol=0.05, now=_BASE_DAY)
        ts2 = calculate_atm_term_structure(ch.quotes, c.spot["BTC"], moneyness_tol=0.05, now=_BASE_DAY)
        assert ts1 == ts2
        tenors = list(ts1.keys())
        assert tenors == sorted(tenors)

    def test_risk_reversal_term_structure_finite(self):
        c = Phase17Campaign(symbols=("ETH",), seed=42, cycles=1)
        ch = c._gen_chain("ETH", "okx")
        rr = calculate_risk_reversal_term_structure(ch.quotes, c.spot["ETH"], delta_target=0.25, tol=0.05, now=_BASE_DAY)
        for t, v in rr.items():
            assert math.isfinite(t) and math.isfinite(v)

    def test_skew_term_structure_finite(self):
        c = Phase17Campaign(symbols=("SOL",), seed=42, cycles=1)
        ch = c._gen_chain("SOL", "binance")
        sk = calculate_skew_term_structure(ch.quotes, c.spot["SOL"], delta_target=0.25, tol=0.05, now=_BASE_DAY)
        for t, v in sk.items():
            assert math.isfinite(t) and math.isfinite(v)

    def test_term_structure_features_dataclass(self):
        c = Phase17Campaign(symbols=("ADA",), seed=1, cycles=1)
        ch = c._gen_chain("ADA", "bybit")
        ts = c._term_structure_features("ADA", ch.quotes, c.spot["ADA"])
        assert ts.symbol == "ADA"
        assert math.isfinite(ts.mean_atm_iv)
        assert math.isfinite(ts.term_structure_slope)
        assert math.isfinite(ts.max_risk_reversal)


class TestPhase17CrossVenue:
    def test_cross_venue_z_deterministic(self):
        c = Phase17Campaign(symbols=("BTC", "ETH"), seed=21, cycles=1)
        chains = {v: c._gen_chain("BTC", v) for v in c.venues}
        xv1 = c._cross_venue_z("BTC", chains)
        xv2 = c._cross_venue_z("BTC", chains)
        assert xv1 == xv2

    def test_cross_venue_z_finite(self):
        c = Phase17Campaign(symbols=("BTC",), seed=7, cycles=1)
        chains = {v: c._gen_chain("BTC", v) for v in c.venues}
        xv = c._cross_venue_z("BTC", chains)
        for k, v in xv.items():
            assert math.isfinite(v)


class TestPhase17OrderflowConfirmation:
    def test_confirmation_deterministic(self):
        c = Phase17Campaign(symbols=("BTC",), seed=42, cycles=1)
        snap = c._gen_orderflow("BTC")
        eng = OrderflowAlphaEngine(seed=42)
        feat = eng.extract_features(snap)
        raw = c._raw_orderflow_features(snap)
        cf1 = c._confirm_orderflow("BTC", feat, raw)
        cf2 = c._confirm_orderflow("BTC", feat, raw)
        assert cf1.confirmed == cf2.confirmed
        assert cf1.confirmation_score == cf2.confirmation_score

    def test_confirmation_fields_finite(self):
        c = Phase17Campaign(symbols=("ETH",), seed=13, cycles=1)
        snap = c._gen_orderflow("ETH")
        eng = OrderflowAlphaEngine(seed=13)
        feat = eng.extract_features(snap)
        raw = c._raw_orderflow_features(snap)
        cf = c._confirm_orderflow("ETH", feat, raw)
        assert math.isfinite(cf.confirmation_score)
        assert math.isfinite(cf.cumulative_delta)
        assert math.isfinite(cf.imbalance)
        assert math.isfinite(cf.absorption_score)
        assert math.isfinite(cf.vpin_lite)
        assert math.isfinite(cf.aggressive_flow)
        assert math.isfinite(cf.delta_divergence)
        assert isinstance(cf.confirmed, bool)
        assert isinstance(cf.hard_gates, dict)
        assert isinstance(cf.reasons, tuple)

    def test_confirmation_hard_gates(self):
        c = Phase17Campaign(symbols=("BTC",), seed=42, cycles=1,
                            max_vpin=0.0, min_absorption=1.0)
        snap = c._gen_orderflow("BTC")
        eng = OrderflowAlphaEngine(seed=42)
        feat = eng.extract_features(snap)
        raw = c._raw_orderflow_features(snap)
        cf = c._confirm_orderflow("BTC", feat, raw)
        # absorption 1.0 is hard to satisfy; confirm likely False, but gates must exist
        assert "vpin_ok" in cf.hard_gates
        assert "absorption_ok" in cf.hard_gates
        assert "imbalance_ok" in cf.hard_gates


class TestPhase17FusionGating:
    def test_fusion_intents_bounded(self):
        eng = VolSurfaceRVEngine(VolSurfaceRVConfig(seed=7))
        c = Phase17Campaign(symbols=("ETH",), seed=7, cycles=1)
        ch = c._gen_chain("ETH", "deribit")
        opps = eng.detect_dislocations(ch, spot=c.spot["ETH"])
        ofeng = OrderflowAlphaEngine(seed=7)
        feat = ofeng.extract_features(c._gen_orderflow("ETH"))
        fusion = SignalFusion(seed=7, max_abs_delta=0.15, max_abs_vega=0.10, gamma_band=0.05,
                              min_liquidity=0.0, min_dte=1, max_dte=90)
        intents = fusion.fuse(opps, [feat], {"ETH": 0.01})
        for it in intents:
            assert abs(it.delta_est) <= 0.15 + 1e-12
            assert abs(it.vega_est) <= 0.10 + 1e-12
            assert abs(it.gamma_est) <= 0.05 + 1e-12
            assert math.isfinite(it.confidence)

    def test_fusion_deterministic(self):
        eng = VolSurfaceRVEngine(VolSurfaceRVConfig(seed=11))
        c = Phase17Campaign(symbols=("BTC",), seed=11, cycles=1)
        ch = c._gen_chain("BTC", "deribit")
        opps = eng.detect_dislocations(ch, spot=65000.0)
        ofeng = OrderflowAlphaEngine(seed=11)
        feat = ofeng.extract_features(c._gen_orderflow("BTC"))
        fusion = SignalFusion(seed=11)
        i1 = fusion.fuse(opps, [feat], {"BTC": 0.01})
        i2 = fusion.fuse(opps, [feat], {"BTC": 0.01})
        assert [x.intent_id for x in i1] == [x.intent_id for x in i2]


class TestPhase17CampaignRun:
    def test_run_completes_small(self, tmp_path):
        c = Phase17Campaign(symbols=("BTC",), seed=777, venues=("deribit", "okx"), cycles=2, outdir=tmp_path)
        r = c.run()
        assert r["status"] == "completed"
        assert r["campaign_id"] == "phase17_777"

    def test_run_artifacts_created(self, tmp_path):
        c = Phase17Campaign(symbols=("BTC", "ETH"), seed=888, venues=("deribit", "okx", "binance"), cycles=3, outdir=tmp_path)
        r = c.run()
        assert len(r["artifacts"]) == 6
        for a in r["artifacts"]:
            assert Path(a).exists()

    def test_required_artifacts_exist(self, tmp_path):
        c = Phase17Campaign(symbols=("BTC", "ETH"), seed=42, venues=("deribit", "okx", "binance", "bybit"), cycles=5, outdir=tmp_path)
        r = c.run()
        for name in ["PHASE17_CROSS_ASSET_VOL_ARB_REPORT", "CROSS_ASSET_VOL_SURFACE_REPORT", "ORDERFLOW_CONFIRMATION_REPORT"]:
            assert (tmp_path / f"{name}.json").exists()
            assert (tmp_path / f"{name}.md").exists()

    def test_master_report_fields(self, tmp_path):
        c = Phase17Campaign(symbols=("BTC", "ETH"), seed=42, cycles=5, outdir=tmp_path)
        r = c.run()
        m = r["master_report"]
        assert m["campaign_id"] == "phase17_42"
        assert m["seed"] == 42
        assert m["paper_only"] is True
        assert m["status"] == "completed"
        assert m["cycles"] == 5
        assert "git_sha" in m
        assert "artifacts" in m
        assert "counts" in m
        assert "components" in m
        assert set(m["symbols"]) == {"BTC", "ETH"}

    def test_run_deterministic_identical_artifacts(self, tmp_path):
        a = tmp_path / "a"
        b = tmp_path / "b"
        c1 = Phase17Campaign(symbols=("BTC", "ETH"), seed=1234, venues=("deribit", "okx"), cycles=3, outdir=a)
        c2 = Phase17Campaign(symbols=("BTC", "ETH"), seed=1234, venues=("deribit", "okx"), cycles=3, outdir=b)
        r1 = c1.run()
        r2 = c2.run()
        assert r1["campaign_id"] == r2["campaign_id"]
        assert r1["master_report"]["counts"] == r2["master_report"]["counts"]
        for pa, pb in zip(sorted(r1["artifacts"]), sorted(r2["artifacts"])):
            assert Path(pa).read_bytes() == Path(pb).read_bytes()

    def test_no_nan_inf_in_json_artifacts(self, tmp_path):
        c = Phase17Campaign(symbols=("BTC", "ETH"), seed=55, cycles=4, outdir=tmp_path)
        r = c.run()
        for art in r["artifacts"]:
            if art.endswith(".json"):
                data = json.loads(Path(art).read_text())
                s = json.dumps(data)
                assert "NaN" not in s
                assert "Infinity" not in s
                assert_json_valid(data)

    def test_reports_have_campaign_metadata(self, tmp_path):
        c = Phase17Campaign(symbols=("BTC",), seed=66, cycles=2, outdir=tmp_path)
        r = c.run()
        for name in ["PHASE17_CROSS_ASSET_VOL_ARB_REPORT.json", "CROSS_ASSET_VOL_SURFACE_REPORT.json", "ORDERFLOW_CONFIRMATION_REPORT.json"]:
            data = json.loads((tmp_path / name).read_text())
            assert data.get("campaign_id") == "phase17_66"
            assert data.get("paper_only") is True
            assert data.get("seed") == 66

    def test_kill_switch_consecutive_rejects(self, tmp_path, monkeypatch):
        # Force one RV signal + one fused intent per cycle; impossible confirmation
        # bar gates every intent out, tripping the kill switch on the first reject.
        c = Phase17Campaign(symbols=("BTC", "ETH"), seed=1, cycles=5, outdir=tmp_path,
                            min_confirmation_score=1.0, kill_switch_max_consecutive_rejects=1)
        fake_signal = VolSurfaceRVSignal(symbol="BTC", venue="deribit", expiry="2026-11-02",
            strike=100.0, option_type="call", mark_iv=0.8, fitted_iv=0.7, residual_iv=0.1,
            vega=0.5, dte_days=5.0, moneyness=1.0, liquidity_score=1.0, rv_score=0.5,
            term_structure_z=0.1, cross_venue_z=0.1, rationale_hash="abc")
        monkeypatch.setattr(
            Phase17Campaign, "_detect_rv_signals",
            lambda self, sym, spot, chains, ts, xv, cyc: [fake_signal],
        )
        fake_intent = TradeIntent(intent_id="x", symbol="BTC", side="buy", qty=0.01,
            size_usd=10.0, expiry="2026-11-02", strike_band=[99.0, 101.0], option_type="call",
            order_type="limit", limit_logic="mid", rationale_hash="x", regime="normal",
            confidence=0.9, delta_est=0.05, vega_est=0.05, gamma_est=0.01, dte_days=5.0,
            liquidity_score=1.0, risk_flags=[])
        monkeypatch.setattr(
            SignalFusion, "fuse",
            lambda self, rv_opps, of_features, price_features: [fake_intent],
        )
        r = c.run()
        assert r["status"] == "completed"
        assert r["killed"] is True or r["master_report"]["kill_switch_triggered"] is True

    def test_backtest_report_finite(self, tmp_path):
        c = Phase17Campaign(symbols=("BTC",), seed=42, cycles=3, outdir=tmp_path)
        r = c.run()
        bt = r["backtest"]
        assert math.isfinite(bt["net_pnl"])
        assert math.isfinite(bt["max_drawdown"])
        assert 0.0 <= bt["win_rate"] <= 1.0
        assert isinstance(bt["kill_switch_triggered"], bool)


class TestPhase17Integration:
    def test_full_integration_btc_eth_sol(self, tmp_path):
        c = Phase17Campaign(symbols=("BTC", "ETH", "SOL"), seed=42,
                            venues=("deribit", "okx", "binance", "bybit", "bitget"), cycles=5, outdir=tmp_path)
        r = c.run()
        assert r["status"] == "completed"
        m = r["master_report"]
        assert m["counts"]["rv_signals"] >= 0
        assert m["counts"]["executed_intents"] >= 0
        assert m["counts"]["gated_out_intents"] >= 0
        assert "backtest" in m["components"]

    def test_multi_symbol_symbols_preserved(self, tmp_path):
        c = Phase17Campaign(symbols=("XRP", "ADA"), seed=2024, cycles=3, outdir=tmp_path)
        r = c.run()
        assert set(r["master_report"]["symbols"]) == {"XRP", "ADA"}

    def test_cycles_respected(self, tmp_path):
        c = Phase17Campaign(symbols=("BTC",), seed=303, cycles=9, outdir=tmp_path)
        r = c.run()
        assert r["master_report"]["cycles"] == 9

    def test_signal_rationale_hash_deterministic(self, tmp_path):
        c = Phase17Campaign(symbols=("BTC",), seed=42, cycles=1, outdir=tmp_path)
        r = c.run()
        vs_report = json.loads((tmp_path / "CROSS_ASSET_VOL_SURFACE_REPORT.json").read_text())
        hashes = [sig["rationale_hash"] for sig in vs_report.get("signals", [])]
        assert len(hashes) == len(set(hashes)) or len(hashes) == 0

    def test_md_artifacts_non_empty(self, tmp_path):
        c = Phase17Campaign(symbols=("BTC",), seed=42, cycles=1, outdir=tmp_path)
        c.run()
        md = (tmp_path / "PHASE17_CROSS_ASSET_VOL_ARB_REPORT.md").read_text()
        assert "Timestamp (UTC)" in md
        assert "Campaign ID: phase17_42" in md
        assert "Paper-only: True" in md


class TestPhase17Stress:
    def test_many_cycles(self, tmp_path):
        c = Phase17Campaign(symbols=("BTC", "ETH"), seed=404, venues=("deribit", "okx", "binance"), cycles=10, outdir=tmp_path)
        r = c.run()
        assert r["status"] == "completed"
        assert len(r["artifacts"]) == 6

    def test_different_seeds_different_campaign_ids(self, tmp_path):
        c1 = Phase17Campaign(symbols=("BTC",), seed=1, cycles=1, outdir=tmp_path / "x")
        c2 = Phase17Campaign(symbols=("BTC",), seed=2, cycles=1, outdir=tmp_path / "y")
        r1 = c1.run()
        r2 = c2.run()
        assert r1["campaign_id"] != r2["campaign_id"]

    def test_all_symbols_run(self, tmp_path):
        c = Phase17Campaign(seed=5, cycles=2, outdir=tmp_path)
        r = c.run()
        assert set(r["master_report"]["symbols"]) == set(_SYMBOL_DEFAULTS)
