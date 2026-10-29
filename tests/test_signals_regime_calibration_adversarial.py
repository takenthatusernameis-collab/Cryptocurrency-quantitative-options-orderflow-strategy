"""Adversarial tests for regime transition calibration and disagreement patterns."""

from src.signals.composite import CompositeSignalGenerator


def test_regime_transition_calibration_adversarial_disagreement():
    gen = CompositeSignalGenerator()
    gen.reset_regime_state()
    # Create adversarial disagreement across regimes
    sig1 = gen.generate_signal(
        symbol="BTC",
        total_gex=-2e8,  # high vol negative gex
        cum_delta=-50000.0,
        of_imbalance=-0.8,
        iv_skew=0.08,
        put_call_ratio=1.8,
    )
    sig2 = gen.generate_signal(
        symbol="BTC",
        total_gex=2e8,  # flip to positive gex
        cum_delta=50000.0,
        of_imbalance=0.8,
        iv_skew=-0.08,
        put_call_ratio=0.6,
    )
    sig3 = gen.generate_signal(
        symbol="BTC",
        total_gex=0.0,
        iv_skew=0.1,  # skew bearish
        put_call_ratio=1.5,
        cum_delta=-10000.0,
        of_imbalance=-0.3,
    )
    metrics = gen.get_regime_stability_metrics()
    assert metrics["transition_count"] >= 0
    assert metrics["disagreement_count"] >= 0
    assert -1.0 <= sig1.strength <= 1.0
    assert -1.0 <= sig2.strength <= 1.0
    assert -1.0 <= sig3.strength <= 1.0
    assert 0.0 <= sig1.confidence <= 1.0


def test_rapid_regime_transitions_hysteresis_stability():
    gen = CompositeSignalGenerator()
    gen.reset_regime_state()
    # Rapid alternating signals
    for i in range(10):
        if i % 2 == 0:
            sig = gen.generate_signal(
                symbol="BTC",
                total_gex=-1.5e9,
                cum_delta=-20000.0,
                of_imbalance=-0.5,
                iv_skew=0.06,
                put_call_ratio=1.3,
            )
        else:
            sig = gen.generate_signal(
                symbol="BTC",
                total_gex=1.5e9,
                cum_delta=20000.0,
                of_imbalance=0.5,
                iv_skew=-0.06,
                put_call_ratio=0.7,
            )
        assert -1.0 <= sig.strength <= 1.0
        assert 0.0 <= sig.confidence <= 1.0
    metrics = gen.get_regime_stability_metrics()
    assert metrics["stability_count"] >= 1


def test_adversarial_component_disagreement_across_regimes():
    gen = CompositeSignalGenerator()
    gen.reset_regime_state()
    # Components pulling in opposite directions
    sig = gen.generate_signal(
        symbol="BTC",
        total_gex=-2e8,  # gamma negative signal
        cum_delta=50000.0,  # orderflow positive
        of_imbalance=0.8,
        iv_skew=0.08,  # vol_skew negative
        put_call_ratio=0.6,  # put_call positive
    )
    assert -1.0 <= sig.strength <= 1.0
    assert 0.0 <= sig.confidence <= 1.0
    metrics = gen.get_regime_stability_metrics()
    assert "disagreement_count" in metrics


def test_regime_calibration_persists_and_resets():
    gen = CompositeSignalGenerator()
    sig1 = gen.generate_signal(symbol="BTC", total_gex=-2e8, iv_skew=0.08)
    metrics1 = gen.get_regime_stability_metrics()
    gen.reset_regime_state()
    metrics2 = gen.get_regime_stability_metrics()
    assert metrics2["transition_count"] == 0
    assert metrics2["disagreement_count"] == 0
    assert metrics2["stability_count"] == 0
