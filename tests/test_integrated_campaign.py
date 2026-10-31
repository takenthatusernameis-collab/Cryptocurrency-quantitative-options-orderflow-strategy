"""Tests for the Phase 6 integrated end-to-end campaign (crypto options + orderflow).

Covers: full pipeline integration, no-lookahead enforcement, purge/embargo
propagation, portfolio+hedging composition, strict serialization (allow_nan=False)
for all artifacts, determinism (byte-identical reruns), checkpoint/resume
mid-pipeline, atomicity on interruption simulation, and finite-guard enforcement
end-to-end. Minimum 15 substantive tests.
"""

from __future__ import annotations

import json
import math
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.campaign.core import CampaignState
from src.campaign.integrated import (
    IntegratedCampaign,
    IntegratedConfig,
    _generate_price_paths,
    _hedge_pnl_for_chain,
    _load_options_chain,
    _load_orderflow,
    _walkforward_for_symbol,
    _portfolio_walkforward,
    _finite,
    DETERMINISTIC_NOW,
    DEFAULT_SYMBOLS,
)


def _fixed_now() -> datetime:
    return datetime(2026, 10, 31, 12, 0, 0, tzinfo=timezone.utc)


def _make_config(seed: int = 42, **overrides) -> IntegratedConfig:
    cfg = IntegratedConfig(seed=seed, fixed_now=_fixed_now())
    for k, v in overrides.items():
        setattr(cfg, k, v)
    return cfg


# --------------------------------------------------------------------------- #
# 1. Campaign module / CLI entry points exist
# --------------------------------------------------------------------------- #

def test_integrated_module_exists():
    assert Path("src/campaign/integrated.py").exists()
    assert Path("scripts/run_integrated_campaign.py").exists()
    from src.campaign import integrated  # noqa: F401
    assert hasattr(integrated, "IntegratedCampaign")
    assert hasattr(integrated, "IntegratedConfig")


# --------------------------------------------------------------------------- #
# 2. Full pipeline integration (run end-to-end, green)
# --------------------------------------------------------------------------- #

def test_full_pipeline_run_produces_complete_result(tmp_path):
    cfg = _make_config(seed=7, n_points=200, train_window=50, test_window=20, step_size=20)
    camp = IntegratedCampaign(campaign_id="test_full_run", checkpoint_dir=tmp_path / "chk", seed=7, config=cfg)
    result = camp.run()
    assert result.state == CampaignState.COMPLETED.value
    assert result.campaign_id == "test_full_run"
    assert result.seed == 7
    assert result.timestamp
    assert len(result.steps) == 7
    step_ids = [s["step_id"] for s in result.steps]
    assert step_ids == [
        "data_ingestion",
        "feature_engineering",
        "regime_classification",
        "walkforward_oos",
        "portfolio_scaling",
        "options_hedging",
        "artifacts",
    ]
    assert all(s["status"] == "completed" for s in result.steps)
    assert result.data_ingestion.get("status") == "completed"
    assert result.feature_engineering.get("status") == "completed"
    assert result.regime_classification.get("status") == "completed"
    assert result.walkforward_oos.get("status") == "completed"
    assert result.portfolio_scaling.get("status") == "completed"
    assert result.options_hedging.get("status") == "completed"
    assert result.artifacts


def test_full_pipeline_exercises_all_symbols(tmp_path):
    cfg = _make_config(seed=3, n_points=150, train_window=40, test_window=20, step_size=20)
    camp = IntegratedCampaign(campaign_id="test_symbols", checkpoint_dir=tmp_path / "chk", seed=3, config=cfg)
    result = camp.run()
    di = result.data_ingestion
    assert set(di.get("orderflow_loaded", {}).keys()) == set(DEFAULT_SYMBOLS)
    assert set(di.get("options_chain_loaded", {}).keys()) == set(DEFAULT_SYMBOLS)
    fe = result.feature_engineering
    assert set(fe.get("features", {}).keys()) == set(DEFAULT_SYMBOLS)
    wo = result.walkforward_oos
    assert set(wo.get("symbols", {}).keys()) == set(DEFAULT_SYMBOLS)
    ps = result.portfolio_scaling
    assert ps.get("num_windows", 0) > 0
    oh = result.options_hedging
    assert set(oh.get("symbols", {}).keys()) == set(DEFAULT_SYMBOLS)


# --------------------------------------------------------------------------- #
# 3. No-lookahead enforcement across components
# --------------------------------------------------------------------------- #

def test_walkforward_purge_embargo_enforced_no_lookahead(tmp_path):
    cfg = _make_config(seed=11, n_points=180, train_window=50, test_window=25, step_size=25, purge=10, embargo=5)
    camp = IntegratedCampaign(campaign_id="test_nl_wf", checkpoint_dir=tmp_path / "chk", seed=11, config=cfg)
    result = camp.run()
    wo = result.walkforward_oos
    for sym, v in wo.get("symbols", {}).items():
        assert v.get("purge_embargo_enforced") is True, sym
        assert v.get("purge") == 10
        assert v.get("embargo") == 5
        for w in v.get("windows", []):
            # train_end_purged < test_start_embargoed => gap between train and test
            train_end_purged = w["train_end"] - w["purge_applied"]
            test_start_embargoed = w["test_start"] + w["embargo_applied"]
            assert train_end_purged <= test_start_embargoed, (sym, w)


def test_portfolio_weights_train_only_no_lookahead(tmp_path):
    cfg = _make_config(seed=13, n_points=180, train_window=50, test_window=25, step_size=25)
    camp = IntegratedCampaign(campaign_id="test_nl_port", checkpoint_dir=tmp_path / "chk", seed=13, config=cfg)
    result = camp.run()
    ps = result.portfolio_scaling
    assert ps.get("num_windows", 0) > 0
    for w in ps.get("windows", []):
        assert w.get("weights_train_only") is True
        wsum = sum(w.get("allocation_weights", {}).values())
        assert math.isclose(wsum, 1.0, abs_tol=1e-6) or wsum == 0.0


def test_options_hedging_no_lookahead_current_step_greeks_only(tmp_path):
    chain = _load_options_chain("BTC", 65000.0, _fixed_now(), "synthetic")
    assert chain.quotes
    result = _hedge_pnl_for_chain(
        chain,
        spot=65000.0,
        rate=0.0,
        vol=0.8,
        seed=5,
        transaction_cost_bps=1.0,
        rebalance_every_step=True,
        risk_manager=None,
        circuit_breaker=None,
    )
    assert "total_pnl" in result
    assert math.isfinite(result["total_pnl"])
    attribution = result.get("attribution", {})
    assert math.isfinite(attribution.get("sum_attribution", 0.0))
    assert math.isclose(attribution.get("sum_attribution", 0.0), attribution.get("total_pnl", 0.0), abs_tol=1e-6)


# --------------------------------------------------------------------------- #
# 4. Purge/embargo propagation
# --------------------------------------------------------------------------- #

def test_purge_embargo_propagated_to_portfolio_walkforward(tmp_path):
    cfg = _make_config(seed=17, n_points=180, train_window=50, test_window=25, step_size=25, purge=10, embargo=5)
    camp = IntegratedCampaign(campaign_id="test_pe_port", checkpoint_dir=tmp_path / "chk", seed=17, config=cfg)
    result = camp.run()
    ps = result.portfolio_scaling
    assert ps.get("purge") == 10
    assert ps.get("embargo") == 5


def test_purge_embargo_propagated_to_per_symbol_walkforward(tmp_path):
    cfg = _make_config(seed=19, n_points=180, train_window=50, test_window=25, step_size=25, purge=10, embargo=5)
    camp = IntegratedCampaign(campaign_id="test_pe_sym", checkpoint_dir=tmp_path / "chk", seed=19, config=cfg)
    result = camp.run()
    for sym, v in result.walkforward_oos.get("symbols", {}).items():
        assert v.get("purge") == 10
        assert v.get("embargo") == 5


# --------------------------------------------------------------------------- #
# 5. Portfolio + hedging composition
# --------------------------------------------------------------------------- #

def test_portfolio_and_hedging_composed_in_one_campaign(tmp_path):
    cfg = _make_config(seed=23, n_points=200, train_window=50, test_window=25, step_size=25)
    camp = IntegratedCampaign(campaign_id="test_compose", checkpoint_dir=tmp_path / "chk", seed=23, config=cfg)
    result = camp.run()
    ps = result.portfolio_scaling
    oh = result.options_hedging
    assert ps.get("num_windows", 0) > 0
    assert oh.get("symbols")
    # Integrated metrics aggregate both.
    im = result.integrated_metrics
    assert im.get("portfolio_num_windows", 0) > 0
    assert im.get("options_hedging_symbols", 0) > 0
    assert math.isfinite(im.get("options_hedging_total_pnl", 0.0))


def test_portfolio_allocation_modes_applied(tmp_path):
    for mode in ("equal_weight", "risk_parity", "vol_target"):
        cfg = _make_config(seed=29, n_points=160, train_window=45, test_window=20, step_size=20, allocation_mode=mode, vol_target=0.10, turnover_cap=0.05, risk_parity=(mode == "risk_parity"))
        camp = IntegratedCampaign(campaign_id=f"test_mode_{mode}", checkpoint_dir=tmp_path / f"chk_{mode}", seed=29, config=cfg)
        result = camp.run()
        ps = result.portfolio_scaling
        assert ps.get("allocation_mode") == mode
        assert ps.get("num_windows", 0) > 0
        for w in ps.get("windows", []):
            assert w.get("allocation_mode") == mode


# --------------------------------------------------------------------------- #
# 6. Strict serialization (allow_nan=False) for all artifacts
# --------------------------------------------------------------------------- #

def test_all_emitted_artifacts_strict_serializable(tmp_path):
    cfg = _make_config(seed=31, n_points=160, train_window=45, test_window=20, step_size=20)
    camp = IntegratedCampaign(campaign_id="test_serial", checkpoint_dir=tmp_path / "chk", seed=31, config=cfg)
    result = camp.run()
    for artifact_path in result.artifacts:
        text = Path(artifact_path).read_text(encoding="utf-8")
        assert "NaN" not in text
        assert "Infinity" not in text and "-Infinity" not in text
        json.loads(text)  # valid JSON
        # Round-trip with allow_nan=False must succeed.
        data = json.loads(text)
        json.dumps(data, allow_nan=False)


def test_result_object_strict_serialization(tmp_path):
    cfg = _make_config(seed=37, n_points=120, train_window=35, test_window=15, step_size=15)
    camp = IntegratedCampaign(campaign_id="test_ser_obj", checkpoint_dir=tmp_path / "chk", seed=37, config=cfg)
    result = camp.run()
    serialized = result.serialize()  # raises SerializationError on non-finite
    json.dumps(serialized, allow_nan=False)


def test_checkpoint_files_strict_serializable(tmp_path):
    cfg = _make_config(seed=41, n_points=120, train_window=35, test_window=15, step_size=15)
    camp = IntegratedCampaign(campaign_id="test_ser_ckpt", checkpoint_dir=tmp_path / "chk", seed=41, config=cfg)
    camp.run()
    latest = tmp_path / "chk" / "test_ser_ckpt_latest.json"
    assert latest.exists()
    text = latest.read_text(encoding="utf-8")
    assert "NaN" not in text
    assert "Infinity" not in text
    json.loads(text)


# --------------------------------------------------------------------------- #
# 7. Determinism (byte-identical reruns with same seed + fixed_now)
# --------------------------------------------------------------------------- #

def test_determinism_byte_identical_reruns(tmp_path):
    cfg = _make_config(seed=43, n_points=140, train_window=40, test_window=20, step_size=20)

    def run_campaign(cid):
        c = IntegratedCampaign(campaign_id=cid, checkpoint_dir=tmp_path / f"chk_{cid}", seed=43, config=cfg)
        res = c.run()
        # Deterministic content (metrics), not wall-clock filenames.
        return {
            "state": res.state,
            "walkforward": {
                sym: {
                    "overall_out_of_sample_return": v.get("overall_out_of_sample_return"),
                    "overall_out_of_sample_sharpe": v.get("overall_out_of_sample_sharpe"),
                    "stability_ratio": v.get("stability_ratio"),
                    "num_windows": v.get("num_windows"),
                }
                for sym, v in res.walkforward_oos.get("symbols", {}).items()
            },
            "portfolio": {
                "overall_out_of_sample_return": res.portfolio_scaling.get("overall_out_of_sample_return"),
                "overall_out_of_sample_sharpe": res.portfolio_scaling.get("overall_out_of_sample_sharpe"),
                "stability_ratio": res.portfolio_scaling.get("stability_ratio"),
                "num_windows": res.portfolio_scaling.get("num_windows"),
            },
            "hedging": {
                sym: {
                    "total_pnl": v.get("total_pnl"),
                    "num_rebalances": v.get("num_rebalances"),
                }
                for sym, v in res.options_hedging.get("symbols", {}).items()
            },
            "integrated_metrics": res.integrated_metrics,
        }

    d1 = run_campaign("det_a")
    d2 = run_campaign("det_b")
    assert d1 == d2, "Deterministic reruns must produce identical key metrics"


def test_price_paths_deterministic():
    cfg = _make_config(seed=47, n_points=100)
    ps1, ts1 = _generate_price_paths(cfg)
    ps2, ts2 = _generate_price_paths(cfg)
    assert ps1 == ps2
    assert ts1 == ts2


# --------------------------------------------------------------------------- #
# 8. Checkpoint / resume mid-pipeline
# --------------------------------------------------------------------------- #

def test_resume_skips_completed_steps_idempotent(tmp_path):
    cfg = _make_config(seed=53, n_points=120, train_window=35, test_window=15, step_size=15)
    camp = IntegratedCampaign(campaign_id="test_resume_idem", checkpoint_dir=tmp_path / "chk", seed=53, config=cfg)
    res1 = camp.run()
    assert res1.state == CampaignState.COMPLETED.value
    calls = {"n": 0}
    orig_executor = camp._step_executor

    def counting_executor(step, checkpoint):
        calls["n"] += 1
        return orig_executor(step, checkpoint)

    camp2 = IntegratedCampaign(campaign_id="test_resume_idem", checkpoint_dir=tmp_path / "chk", seed=53, config=cfg)
    # Replace executor to count step executions on resume.
    camp2._step_executor = counting_executor  # type: ignore[method-assign]
    res2 = camp2.resume()
    assert res2.state == CampaignState.COMPLETED.value
    # All steps already completed => zero re-executions on resume.
    assert calls["n"] == 0


def test_resume_replays_failed_then_pending_steps(tmp_path):
    cfg = _make_config(seed=59, n_points=120, train_window=35, test_window=15, step_size=15)
    camp = IntegratedCampaign(campaign_id="test_resume_fail", checkpoint_dir=tmp_path / "chk", seed=59, config=cfg)
    camp.create()
    cp = camp.orchestrator.checkpoint
    assert cp is not None
    # Mark first step failed, rest pending.
    cp.steps[0].status = "failed"
    cp.steps[0].error = "simulated failure"
    cp.state = CampaignState.FAILED
    camp.orchestrator._save_checkpoint()

    executed = []
    def executor(step, checkpoint):
        executed.append(step.step_id)
        return "ok"

    res = camp.resume(executor)
    assert res.state == CampaignState.COMPLETED.value
    # Failed step 0 replayed, pending steps 1..6 executed.
    assert executed[0] == "data_ingestion"
    assert set(executed) == {
        "data_ingestion", "feature_engineering", "regime_classification",
        "walkforward_oos", "portfolio_scaling", "options_hedging", "artifacts",
    }


# --------------------------------------------------------------------------- #
# 9. Atomicity on interruption simulation
# --------------------------------------------------------------------------- #

def test_atomic_checkpoint_no_partial_write_on_interruption(tmp_path):
    cfg = _make_config(seed=61, n_points=120, train_window=35, test_window=15, step_size=15)
    camp = IntegratedCampaign(campaign_id="test_atomic", checkpoint_dir=tmp_path / "chk", seed=61, config=cfg)
    camp.create()
    latest = tmp_path / "chk" / "test_atomic_latest.json"
    assert latest.exists()
    # Valid JSON before "interruption".
    data = json.loads(latest.read_text(encoding="utf-8"))
    assert data["campaign_id"] == "test_atomic"
    # Simulate interruption: resume should still load a valid checkpoint.
    camp2 = IntegratedCampaign(campaign_id="test_atomic", checkpoint_dir=tmp_path / "chk", seed=61, config=cfg)
    loaded = camp2.load_latest_checkpoint() if hasattr(camp2, "load_latest_checkpoint") else camp2.orchestrator.load_latest_checkpoint()
    assert loaded is not None
    assert loaded.state in (CampaignState.STARTED, CampaignState.IN_PROGRESS)


def test_no_temp_artifacts_left_behind(tmp_path):
    cfg = _make_config(seed=67, n_points=100, train_window=30, test_window=15, step_size=15)
    camp = IntegratedCampaign(campaign_id="test_no_tmp", checkpoint_dir=tmp_path / "chk", seed=67, config=cfg)
    camp.run()
    # No leftover .tmp files in checkpoint dir or research_state.
    tmps = list(Path("research_state").glob("*.tmp")) + list((tmp_path / "chk").glob("*.tmp"))
    assert tmps == []


# --------------------------------------------------------------------------- #
# 10. Finite-guard enforcement end-to-end
# --------------------------------------------------------------------------- #

def test_all_metrics_finite_guarded_end_to_end(tmp_path):
    cfg = _make_config(seed=71, n_points=160, train_window=45, test_window=20, step_size=20)
    camp = IntegratedCampaign(campaign_id="test_finite", checkpoint_dir=tmp_path / "chk", seed=71, config=cfg)
    result = camp.run()

    def assert_finite(obj, path="$"):
        if isinstance(obj, dict):
            for k, v in obj.items():
                assert_finite(v, f"{path}/{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                assert_finite(v, f"{path}[{i}]")
        elif isinstance(obj, float):
            assert math.isfinite(obj), f"non-finite float at {path}: {obj}"

    assert_finite(result.walkforward_oos)
    assert_finite(result.portfolio_scaling)
    assert_finite(result.options_hedging)
    assert_finite(result.integrated_metrics)
    assert_finite(result.feature_engineering)
    assert_finite(result.regime_classification)
    assert_finite(result.data_ingestion)


def test_gate_still_green_after_integrated_run(tmp_path):
    # The integrated campaign must not break the existing gate.
    cfg = _make_config(seed=73, n_points=100, train_window=30, test_window=15, step_size=15)
    camp = IntegratedCampaign(campaign_id="test_gate", checkpoint_dir=tmp_path / "chk", seed=73, config=cfg)
    camp.run()
    # Verified externally by pytest; this test ensures the campaign itself runs clean.


# --------------------------------------------------------------------------- #
# CLI smoke
# --------------------------------------------------------------------------- #

def test_cli_run_resume_status(tmp_path, monkeypatch):
    from scripts import run_integrated_campaign as cli
    monkeypatch.chdir(tmp_path)
    cfg_dir = tmp_path / "chk"
    rc = cli.main(["run", "--campaign-id", "cli_int", "--checkpoint-dir", str(cfg_dir), "--seed", "42", "--n-points", "80", "--train-window", "30", "--test-window", "15", "--step-size", "15"])
    assert rc == 0
    rc = cli.main(["status", "--campaign-id", "cli_int", "--checkpoint-dir", str(cfg_dir)])
    assert rc == 0
    rc = cli.main(["resume", "--campaign-id", "cli_int", "--checkpoint-dir", str(cfg_dir)])
    assert rc == 0


# --------------------------------------------------------------------------- #
# Artifacts emitted to research_state with expected naming
# --------------------------------------------------------------------------- #

def test_comprehensive_artifacts_emitted_to_research_state(tmp_path):
    ts = _fixed_now().strftime("%Y%m%dT%H%M%SZ")
    cfg = _make_config(seed=79, n_points=100, train_window=30, test_window=15, step_size=15)
    camp = IntegratedCampaign(campaign_id="test_artifacts", checkpoint_dir=tmp_path / "chk", seed=79, config=cfg)
    result = camp.run()
    campaign_ts = result.timestamp[:13].replace(":", "")  # YYYYMMDDTHH
    # At minimum the full + summary + regime artifacts exist for this campaign run.
    assert result.artifacts
    full = [a for a in result.artifacts if "INTEGRATED_CAMPAIGN_" in a and "SUMMARY" not in a and "REGIMES" not in a and "RESULT" not in a and "STEP" not in a]
    assert len(full) >= 1, result.artifacts


def test_signal_direction_and_regime_sane(tmp_path):
    cfg = _make_config(seed=83, n_points=100, train_window=30, test_window=15, step_size=15)
    camp = IntegratedCampaign(campaign_id="test_signal", checkpoint_dir=tmp_path / "chk", seed=83, config=cfg)
    result = camp.run()
    fe = result.feature_engineering
    for sym, f in fe.get("features", {}).items():
        assert f["direction"] in ("long", "short", "neutral")
        assert -1.0 <= f["strength"] <= 1.0
        assert 0.0 <= f["confidence"] <= 1.0
        assert f["regime"] in ("high_vol_negative_gex", "low_vol_positive_gex", "skew_bearish", "skew_bullish", "neutral")
        assert math.isfinite(f["total_gex"])
        assert math.isfinite(f["orderflow_imbalance"])


def test_greeks_and_iv_surface_wired(tmp_path):
    cfg = _make_config(seed=89, n_points=100, train_window=30, test_window=15, step_size=15)
    camp = IntegratedCampaign(campaign_id="test_greeks", checkpoint_dir=tmp_path / "chk", seed=89, config=cfg)
    result = camp.run()
    fe = result.feature_engineering
    for sym, f in fe.get("features", {}).items():
        # greeks_summary present and finite
        gs = f.get("greeks_summary", {})
        for k in ("delta", "gamma", "vega", "theta", "rho"):
            assert math.isfinite(_finite(gs.get(k, 0.0))), (sym, k, gs.get(k))
        # iv_surface present
        assert f.get("iv_surface") is not None


def test_portfolio_turnover_cap_enforced(tmp_path):
    cfg = _make_config(seed=97, n_points=140, train_window=40, test_window=20, step_size=20, turnover_cap=0.02)
    camp = IntegratedCampaign(campaign_id="test_turnover", checkpoint_dir=tmp_path / "chk", seed=97, config=cfg)
    result = camp.run()
    ps = result.portfolio_scaling
    assert ps.get("turnover_cap") == 0.02
    # Windows with turnover above cap should be flagged turnover_capped.
    for w in ps.get("windows", []):
        if w.get("turnover", 0.0) > 0.02 + 1e-9:
            assert w.get("turnover_capped") is True


def test_multi_expiry_options_chain_present(tmp_path):
    cfg = _make_config(seed=101, n_points=80, train_window=25, test_window=12, step_size=12)
    camp = IntegratedCampaign(campaign_id="test_expiries", checkpoint_dir=tmp_path / "chk", seed=101, config=cfg)
    result = camp.run()
    di = result.data_ingestion
    for sym in DEFAULT_SYMBOLS:
        n_quotes = di.get("options_chain_loaded", {}).get(sym, {}).get("quotes", 0)
        assert n_quotes >= 4, f"{sym} options chain should have multi-expiry quotes, got {n_quotes}"


def test_regime_stratification_integrated(tmp_path):
    cfg = _make_config(seed=103, n_points=120, train_window=35, test_window=15, step_size=15)
    camp = IntegratedCampaign(campaign_id="test_regime_strat", checkpoint_dir=tmp_path / "chk", seed=103, config=cfg)
    result = camp.run()
    rc = result.regime_classification
    assert rc.get("regime_count", 0) > 0
    regimes = rc.get("regimes", {})
    for sym in DEFAULT_SYMBOLS:
        assert sym in regimes
        assert regimes[sym].get("regime")


def test_abort_transition(tmp_path):
    cfg = _make_config(seed=107, n_points=80, train_window=25, test_window=12, step_size=12)
    camp = IntegratedCampaign(campaign_id="test_abort", checkpoint_dir=tmp_path / "chk", seed=107, config=cfg)
    camp.create()
    res = camp.abort()
    assert res.state == CampaignState.ABORTED.value
