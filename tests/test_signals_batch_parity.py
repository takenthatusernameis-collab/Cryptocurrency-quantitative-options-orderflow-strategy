"""Adversarial tests for batched/vectorized composite signals with parity to scalar."""

from src.signals.composite import CompositeSignalGenerator


def test_batch_parity_scalar_same_sequence():
    gen = CompositeSignalGenerator()
    gen.reset_regime_state()
    items = [
        {"symbol": "BTC", "total_gex": -2e8, "cum_delta": -50000.0, "of_imbalance": -0.8, "iv_skew": 0.08, "put_call_ratio": 1.8},
        {"symbol": "ETH", "total_gex": 2e8, "cum_delta": 50000.0, "of_imbalance": 0.8, "iv_skew": -0.08, "put_call_ratio": 0.6},
        {"symbol": "SOL", "total_gex": 0.0, "cum_delta": 0.0, "of_imbalance": 0.0, "iv_skew": 0.01, "put_call_ratio": 1.0},
    ]
    batch = gen.generate_signals_batch(items)
    # Reset and compute scalar
    gen2 = CompositeSignalGenerator()
    scalar = []
    for it in items:
        scalar.append(gen2.generate_signal(**{k: v for k, v in it.items() if k != "chain"}))
    assert len(batch) == len(scalar)
    for b, s in zip(batch, scalar):
        assert b.symbol == s.symbol
        assert b.direction == s.direction
        assert abs(b.strength - s.strength) < 1e-12
        assert abs(b.confidence - s.confidence) < 1e-12
        assert b.regime == s.regime
        # components parity
        for k in ("gamma", "orderflow", "vol_skew", "put_call"):
            assert k in b.components and k in s.components
            assert abs(b.components[k] - s.components[k]) < 1e-12


def test_batch_hysteresis_preserved_across_sequence():
    gen = CompositeSignalGenerator()
    gen.reset_regime_state()
    items = [
        {"symbol": "BTC", "total_gex": -2e8, "iv_skew": 0.0, "put_call_ratio": 1.0},
        {"symbol": "BTC", "total_gex": 2e8, "iv_skew": 0.0, "put_call_ratio": 1.0},  # flip attempt
        {"symbol": "BTC", "total_gex": 2e8, "iv_skew": 0.0, "put_call_ratio": 1.0},  # confirmation
    ]
    batch = gen.generate_signals_batch(items)
    # First should be high_vol_negative_gex (or as detected), transitions require confirmation
    assert batch[0].regime == "high_vol_negative_gex"
    # Second might still be in previous regime due to hysteresis
    assert batch[1].regime in ("high_vol_negative_gex", "low_vol_positive_gex")
    assert batch[2].regime == "low_vol_positive_gex"


def test_batch_deterministic_ordering():
    gen = CompositeSignalGenerator()
    gen.reset_regime_state()
    items = [
        {"symbol": "B", "total_gex": 0.0},
        {"symbol": "A", "total_gex": 0.0},
        {"symbol": "C", "total_gex": -1e8},
    ]
    batch = gen.generate_signals_batch(items)
    assert [s.symbol for s in batch] == ["B", "A", "C"]


def test_batch_handles_nonfinite_and_malformed():
    gen = CompositeSignalGenerator()
    gen.reset_regime_state()
    items = [
        {"symbol": "BTC", "total_gex": float("nan"), "cum_delta": float("inf"), "iv_skew": float("-inf"), "put_call_ratio": float("nan")},
        None,
        "bad",
        {"symbol": 123, "total_gex": "oops", "of_imbalance": []},
    ]
    batch = gen.generate_signals_batch(items)
    # Should produce results for valid-ish entries, skip truly bad ones safely
    assert isinstance(batch, list)
    for s in batch:
        assert 0.0 <= s.confidence <= 1.0
        assert -1.0 <= s.strength <= 1.0
        assert s.direction in ("long", "short", "neutral")
        assert isinstance(s.components, dict)
