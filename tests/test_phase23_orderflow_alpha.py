#!/usr/bin/env python3
import json
import math

from src.signals.phase23_orderflow_alpha import OrderflowAlpha, OrderflowAlphaConfig
from src.signals.phase23_regime_detector import RegimeDetector, RegimeDetectorConfig
from src.signals.phase23_signal_fusion import SignalFusion, SignalFusionConfig
from src.analytics.phase23_alpha_decay import AlphaDecay, AlphaDecayConfig


class TestPhase23OrderflowAlphaPaperOnly:
    def test_paper_only_enforced(self):
        o = OrderflowAlpha(seed=1)
        assert o.config.paper_only is True

    def test_rejects_live_not_paper(self):
        try:
            OrderflowAlpha(config=OrderflowAlphaConfig(paper_only=False), seed=1)
            assert False
        except ValueError:
            pass

    def test_imbalance_range(self):
        o = OrderflowAlpha(seed=5)
        for bv, av in [(100, 0), (0, 100), (100, 100), (300, 100)]:
            imb = o.compute_imbalance(bv, av)
            assert -1.0 <= imb <= 1.0
            assert math.isfinite(imb)

    def test_toxic_detection(self):
        o = OrderflowAlpha(seed=7)
        tox, score = o.detect_toxic_flow(0.5, 5.0, 3.0)
        assert isinstance(tox, bool)
        assert 0.0 <= score <= 10.0

    def test_tape_pressure(self):
        o = OrderflowAlpha(seed=11)
        pres = o.tape_pressure([0.1, 0.2, -0.1], None)
        assert -1.0 <= pres <= 1.0
        assert math.isfinite(pres)

    def test_generate_signal_deterministic(self):
        o1 = OrderflowAlpha(seed=42)
        o2 = OrderflowAlpha(seed=42)
        s1 = o1.generate_signal("BTC", "deribit", 1000, 500, 2.0, [0.1, 0.2], 0)
        s2 = o2.generate_signal("BTC", "deribit", 1000, 500, 2.0, [0.1, 0.2], 0)
        assert s1.signal_id == s2.signal_id
        assert s1.imbalance == s2.imbalance
        assert s1.paper_only is True

    def test_generate_signal_structure(self):
        o = OrderflowAlpha(seed=13)
        s = o.generate_signal("ETH", "binance", 500, 1000, 1.5, [0.05], 1)
        assert s.symbol == "ETH"
        assert s.venue == "binance"
        assert s.direction in {"buy", "sell", "neutral"}
        assert 0.0 <= s.confidence <= 1.0
        assert -1.0 <= s.alpha_score <= 1.0
        assert math.isfinite(s.tape_pressure)
        assert math.isfinite(s.toxic_score)

    def test_report_structure(self):
        o = OrderflowAlpha(seed=23)
        sigs = [o.generate_signal("BTC", "deribit", 1000, 800, 2.0, [0.1], i) for i in range(5)]
        rep = o.generate_report(sigs)
        assert rep["report"] == "PHASE23_ORDERFLOW_ALPHA_REPORT"
        assert rep["signal_count"] == 5
        assert rep["paper_only"] is True
        assert "summary" in rep
        json.dumps(rep)


class TestPhase23RegimeDetectorPaperOnly:
    def test_paper_only_enforced(self):
        r = RegimeDetector(seed=1)
        assert r.config.paper_only is True

    def test_rejects_live_not_paper(self):
        try:
            RegimeDetector(config=RegimeDetectorConfig(paper_only=False), seed=1)
            assert False
        except ValueError:
            pass

    def test_classify_deterministic(self):
        r1 = RegimeDetector(seed=42)
        r2 = RegimeDetector(seed=42)
        rets = [0.01, -0.005, 0.008, 0.002, -0.001]
        s1 = r1.classify_regime("BTC", rets, 90000.0, 0)
        s2 = r2.classify_regime("BTC", rets, 90000.0, 0)
        assert s1.state_id == s2.state_id
        assert s1.regime == s2.regime
        assert s1.paper_only is True

    def test_classify_structure(self):
        r = RegimeDetector(seed=17)
        rets = [-0.01, -0.008, -0.005, 0.001, 0.002]
        st = r.classify_regime("ETH", rets, 3000.0, 1)
        assert st.symbol == "ETH"
        assert st.regime in {"vol", "trend", "mean_reversion", "range"}
        assert st.vol_regime in {"low", "med", "high"}
        assert 0.0 <= st.confidence <= 1.0
        assert math.isfinite(st.trend_strength)
        assert math.isfinite(st.mr_score)

    def test_report_structure(self):
        r = RegimeDetector(seed=19)
        states = [r.classify_regime("BTC", [0.01, 0.002, -0.001], 90000.0, i) for i in range(4)]
        rep = r.generate_report(states)
        assert rep["report"] == "PHASE23_REGIME_DETECTION_REPORT"
        assert rep["state_count"] == 4
        assert rep["paper_only"] is True
        json.dumps(rep)


class TestPhase23SignalFusionPaperOnly:
    def test_paper_only_enforced(self):
        f = SignalFusion(seed=1)
        assert f.config.paper_only is True

    def test_rejects_live_not_paper(self):
        try:
            SignalFusion(config=SignalFusionConfig(paper_only=False), seed=1)
            assert False
        except ValueError:
            pass

    def test_adaptive_weights_sum(self):
        f = SignalFusion(seed=5)
        for regime in ["trend", "mean_reversion", "vol", "range"]:
            w = f.adaptive_weights(regime)
            s = sum(w.values())
            assert abs(s - 1.0) < 1e-9
            for k, v in w.items():
                assert 0.0 <= v <= 1.0

    def test_fuse_deterministic(self):
        f1 = SignalFusion(seed=42)
        f2 = SignalFusion(seed=42)
        raw = {"orderflow": 0.3, "vol": 0.1, "cross_asset": -0.05}
        fs1 = f1.fuse("BTC", "trend", raw, 0)
        fs2 = f2.fuse("BTC", "trend", raw, 0)
        assert fs1.fusion_id == fs2.fusion_id
        assert fs1.fused_score == fs2.fused_score
        assert fs1.paper_only is True

    def test_fuse_structure(self):
        f = SignalFusion(seed=13)
        raw = {"orderflow": 0.4, "vol": -0.1, "cross_asset": 0.2}
        fs = f.fuse("ETH", "mean_reversion", raw, 1)
        assert fs.symbol == "ETH"
        assert fs.direction in {"long", "short", "neutral"}
        assert -1.0 <= fs.fused_score <= 1.0
        assert 0.0 <= fs.conviction <= 1.0
        assert math.isfinite(fs.risk_adjusted)
        assert fs.weights

    def test_report_structure(self):
        f = SignalFusion(seed=23)
        fused = [f.fuse("BTC", "trend", {"orderflow": 0.2, "vol": 0.1}, i) for i in range(4)]
        rep = f.generate_report(fused)
        assert rep["report"] == "PHASE23_SIGNAL_FUSION_REPORT"
        assert rep["fused_count"] == 4
        assert rep["paper_only"] is True
        json.dumps(rep)


class TestPhase23AlphaDecayPaperOnly:
    def test_paper_only_enforced(self):
        a = AlphaDecay(seed=1)
        assert a.config.paper_only is True

    def test_rejects_live_not_paper(self):
        try:
            AlphaDecay(config=AlphaDecayConfig(paper_only=False), seed=1)
            assert False
        except ValueError:
            pass

    def test_half_life_computation(self):
        a = AlphaDecay(seed=5)
        ic = [0.05, 0.045, 0.04, 0.036, 0.032]
        hl = a.compute_half_life(ic)
        assert hl > 0
        assert math.isfinite(hl)

    def test_monitor_deterministic(self):
        a1 = AlphaDecay(seed=42)
        a2 = AlphaDecay(seed=42)
        ic = [0.05 * (0.9 ** i) for i in range(20)]
        d1 = a1.monitor("BTC", "vol_arb", 0.3, ic, 0)
        d2 = a2.monitor("BTC", "vol_arb", 0.3, ic, 0)
        assert d1.decay_id == d2.decay_id
        assert d1.half_life_bars == d2.half_life_bars
        assert d1.paper_only is True

    def test_monitor_structure(self):
        a = AlphaDecay(seed=13)
        ic = [0.04, 0.038, 0.035, 0.033, 0.03]
        st = a.monitor("ETH", "orderflow_momentum", 0.25, ic, 1)
        assert st.symbol == "ETH"
        assert st.alpha_quality in {"good", "degraded", "poor"}
        assert st.half_life_bars > 0
        assert -1.0 <= st.alpha_level <= 1.0
        assert math.isfinite(st.ic_current)
        assert math.isfinite(st.decay_factor)
        assert math.isfinite(st.time_to_decay)

    def test_report_structure(self):
        a = AlphaDecay(seed=23)
        states = [a.monitor("BTC", "vol_arb", 0.3, [0.05 * (0.9 ** i) for i in range(10)], i) for i in range(4)]
        rep = a.generate_report(states)
        assert rep["report"] == "PHASE23_ALPHA_DECAY_REPORT"
        assert rep["decay_count"] == 4
        assert rep["paper_only"] is True
        json.dumps(rep)
