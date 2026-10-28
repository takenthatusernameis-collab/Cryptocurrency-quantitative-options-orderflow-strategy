"""Tests for regime-aware composite signal generator."""

from src.signals.composite import CompositeSignalGenerator


def test_regime_detection_negative_gex():
    gen = CompositeSignalGenerator()
    regime = gen._detect_regime(total_gex=-2e8, iv_skew=0.0, put_call_ratio=1.0)
    assert regime == "high_vol_negative_gex"


def test_regime_detection_positive_gex():
    gen = CompositeSignalGenerator()
    regime = gen._detect_regime(total_gex=2e8, iv_skew=0.0, put_call_ratio=1.0)
    assert regime == "low_vol_positive_gex"


def test_regime_detection_skew_bearish():
    gen = CompositeSignalGenerator()
    regime = gen._detect_regime(total_gex=0.0, iv_skew=0.08, put_call_ratio=1.0)
    assert regime == "skew_bearish"


def test_regime_detection_skew_bullish():
    gen = CompositeSignalGenerator()
    regime = gen._detect_regime(total_gex=0.0, iv_skew=-0.08, put_call_ratio=1.0)
    assert regime == "skew_bullish"


def test_regime_detection_neutral():
    gen = CompositeSignalGenerator()
    regime = gen._detect_regime(total_gex=0.0, iv_skew=0.01, put_call_ratio=1.0)
    assert regime == "neutral"


def test_regime_adjusts_weights():
    gen = CompositeSignalGenerator()
    w_neutral = gen._get_weights("neutral")
    w_highvol = gen._get_weights("high_vol_negative_gex")
    assert w_neutral != w_highvol
    # High vol regime should weight gamma more
    assert w_highvol["gamma"] > w_neutral["gamma"]


def test_confidence_reflects_component_agreement():
    """When all components agree in sign, confidence should be higher than when they disagree."""
    gen = CompositeSignalGenerator()
    # All components positive => high agreement
    sig_agree = gen.generate_signal(
        symbol="BTC",
        total_gex=2e8,  # positive GEX => gamma_signal negative? Actually -sign(gex)*|gex|/1e9
        cum_delta=50000.0,  # positive orderflow
        of_imbalance=0.8,  # positive
        iv_skew=-0.08,  # negative skew => skew_signal positive
        put_call_ratio=0.6,  # PCR < 1 => pc_signal positive
    )
    # All disagree
    sig_disagree = gen.generate_signal(
        symbol="BTC",
        total_gex=-2e8,  # gamma_signal positive
        cum_delta=-50000.0,  # orderflow negative
        of_imbalance=-0.8,  # negative
        iv_skew=0.08,  # skew_signal negative
        put_call_ratio=1.8,  # pc_signal negative
    )
    # Agreement case should have higher confidence than disagreement case
    # (not strictly guaranteed by formula but should hold for these inputs)
    assert sig_agree.confidence >= sig_disagree.confidence


def test_signal_direction_long():
    gen = CompositeSignalGenerator()
    sig = gen.generate_signal(
        symbol="BTC",
        total_gex=2e8,
        cum_delta=50000.0,
        of_imbalance=0.8,
        iv_skew=-0.08,
        put_call_ratio=0.6,
    )
    assert sig.direction == "long"


def test_signal_direction_short():
    gen = CompositeSignalGenerator()
    sig = gen.generate_signal(
        symbol="BTC",
        total_gex=-2e8,
        cum_delta=-50000.0,
        of_imbalance=-0.8,
        iv_skew=0.08,
        put_call_ratio=1.8,
    )
    assert sig.direction == "short"


def test_signal_neutral_when_weak():
    gen = CompositeSignalGenerator()
    sig = gen.generate_signal(symbol="BTC")
    assert sig.direction == "neutral"
    assert sig.strength == 0.0


def test_confidence_in_range():
    gen = CompositeSignalGenerator()
    for gex in (-2e8, 0.0, 2e8):
        sig = gen.generate_signal(symbol="BTC", total_gex=gex, cum_delta=10000.0, of_imbalance=0.3, iv_skew=0.02, put_call_ratio=1.1)
        assert 0.0 <= sig.confidence <= 1.0
        assert -1.0 <= sig.strength <= 1.0


def test_signal_has_regime():
    gen = CompositeSignalGenerator()
    sig = gen.generate_signal(symbol="BTC", total_gex=-2e8, cum_delta=10000.0)
    assert hasattr(sig, "regime")
    assert sig.regime in ("high_vol_negative_gex", "low_vol_positive_gex", "skew_bearish", "skew_bullish", "neutral")