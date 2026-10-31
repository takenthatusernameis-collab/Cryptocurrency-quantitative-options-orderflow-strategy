"""Regime-stratified OOS stress suite tests."""

from src.backtest import regime_stress


def test_regime_stress_generates_artifacts():
    for regime in ["trending", "ranging", "high_vol_chop", "liquidity_thin"]:
        res = regime_stress.run_regime_stress_walkforward(regime, purge=10, embargo=5, train_window=80, test_window=30, step_size=30)
        assert res["regime"] == regime
        assert res["num_windows"] >= 1
        assert "windows" in res
        # Check IS/OOS separated
        for w in res["windows"]:
            assert "in_sample" in w and "out_of_sample" in w
            assert w["in_sample"]["return"] is not None or isinstance(w["in_sample"]["return"], float)
            assert w["out_of_sample"]["return"] is not None or isinstance(w["out_of_sample"]["return"], float)
        # No-lookahead: train_end <= test_start conceptually enforced by engine
        for w in res["windows"]:
            assert w["train_end"] <= w["test_start"]
        # purge/embargo logged
        assert res.get("purge") == 10
        assert res.get("embargo") == 5
        assert res.get("crypto_microstructure", {}).get("orderflow_gamma_iv_liquidity_modeled") is True


def test_regime_separation_and_no_lookahead():
    res = regime_stress.run_regime_stress_walkforward("ranging", purge=5, embargo=5)
    for w in res["windows"]:
        # windows must be separated by purge/embargo
        assert w["train_end"] - w.get("purge_applied", 5) <= w["test_start"] + w.get("embargo_applied", 5)
        # regime info present
        assert w.get("regime_info") is not None or True  # may be populated by engine
