"""Tests for strict artifact serialization across all JSON-emitting production paths.

Covers: regime_stress.save_regime_artifact, pipelines.build_features.build_features,
and the centralized telemetry guards (serialize_metrics / serialize_metrics_strict).
Goal: NaN/Inf must NEVER reach disk; every artifact is written atomically and is
strictly JSON-valid with allow_nan=False.
"""

from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path

import pytest

from src.backtest import regime_stress
from src.pipelines import build_features
from src.telemetry import SerializationError, serialize_metrics, serialize_metrics_strict


# --------------------------------------------------------------------------- #
# Centralized telemetry guards
# --------------------------------------------------------------------------- #

def test_serialize_metrics_rejects_nonfinite():
    with pytest.raises(SerializationError):
        serialize_metrics({"sharpe": float("nan")})
    with pytest.raises(SerializationError):
        serialize_metrics({"dd": float("inf")})
    with pytest.raises(SerializationError):
        serialize_metrics({"neg_inf": -float("inf")})


def test_serialize_metrics_accepts_finite():
    out = serialize_metrics({"sharpe": 1.5, "n": 3, "ok": True, "none": None})
    assert out["sharpe"] == 1.5
    assert out["n"] == 3
    json.dumps(out, allow_nan=False)


def test_serialize_metrics_strict_emits_valid_json():
    out = serialize_metrics_strict({"a": 1, "b": [1.0, 2.0], "c": {"d": 0.5}})
    s = json.dumps(out, allow_nan=False)
    assert json.loads(s) == out


def test_serialize_metrics_rejects_numpy_nonfinite():
    np = pytest.importorskip("numpy")
    with pytest.raises(SerializationError):
        serialize_metrics({"x": np.float64(np.nan)})
    with pytest.raises(SerializationError):
        serialize_metrics({"y": np.array([1.0, np.inf])})


# --------------------------------------------------------------------------- #
# regime_stress.save_regime_artifact
# --------------------------------------------------------------------------- #

def test_regime_artifact_rejects_nonfinite(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    payload = {"a": 1, "b": float("nan")}
    with pytest.raises(SerializationError):
        regime_stress.save_regime_artifact(payload, "trending")


def test_regime_artifact_rejects_inf(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    payload = {"a": float("inf"), "b": 2}
    with pytest.raises(SerializationError):
        regime_stress.save_regime_artifact(payload, "ranging")


def test_regime_artifact_writes_valid_strict_json(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    payload = {"a": 1, "b": 2.5, "c": [1, 2, 3]}
    path = regime_stress.save_regime_artifact(payload, "trending")
    p = Path(path)
    assert p.exists()
    content = p.read_text(encoding="utf-8")
    assert "NaN" not in content
    assert "Infinity" not in content
    data = json.loads(content)
    assert data["a"] == 1
    assert data["b"] == 2.5


def test_regime_artifact_is_atomic_no_partial_writes(tmp_path, monkeypatch):
    """No partial/torn files should be observable: only the final file exists."""
    monkeypatch.chdir(tmp_path)
    payload = {"ok": True}
    path = regime_stress.save_regime_artifact(payload, "trending")
    p = Path(path)
    assert p.exists()
    # No leftover temp files in research_state
    leftovers = list(p.parent.glob(".*.tmp"))
    assert leftovers == []


# --------------------------------------------------------------------------- #
# pipelines.build_features.build_features
# --------------------------------------------------------------------------- #

def test_build_features_writes_strict_json(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # Ensure raw data exists (use repo synthetic fixtures if present)
    of_src = Path("data/raw/orderflow_btcusdt_synthetic.json")
    opt_src = Path("data/raw/options_btc_synthetic.json")
    if not (of_src.exists() and opt_src.exists()):
        pytest.skip("synthetic raw fixtures not present")
    out_dir = tmp_path / "processed"
    res = build_features.build_features(
        str(of_src), str(opt_src), spot=65000.0, venue="synthetic", output_dir=str(out_dir)
    )
    assert "manifest_path" in res
    manifest = Path(res["manifest_path"])
    assert manifest.exists()
    content = manifest.read_text(encoding="utf-8")
    assert "NaN" not in content and "Infinity" not in content
    json.loads(content)
    latest = out_dir / "features_latest.json"
    assert latest.exists()
    json.loads(latest.read_text(encoding="utf-8"))


def test_build_features_rejects_nonfinite_payload(tmp_path, monkeypatch):
    """If a feature calc returns NaN, build_features must raise SerializationError."""
    monkeypatch.chdir(tmp_path)
    of_src = Path("data/raw/orderflow_btcusdt_synthetic.json")
    opt_src = Path("data/raw/options_btc_synthetic.json")
    if not (of_src.exists() and opt_src.exists()):
        pytest.skip("synthetic raw fixtures not present")

    import src.pipelines.build_features as bf

    def bad_cumulative_delta(trades):
        return float("nan")

    monkeypatch.setattr(bf, "calculate_cumulative_delta", bad_cumulative_delta)
    with pytest.raises(SerializationError):
        bf.build_features(
            str(of_src), str(opt_src), spot=65000.0, venue="synthetic", output_dir=str(tmp_path / "p2")
        )


# --------------------------------------------------------------------------- #
# End-to-end: real regime artifacts are strict-serializable
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("regime", ["trending", "ranging", "high_vol_chop", "liquidity_thin"])
def test_real_regime_artifact_is_strict(regime, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    payload = regime_stress.run_regime_stress_walkforward(regime, purge=10, embargo=5)
    # Must not raise: proves production path is finite-guarded.
    strict = serialize_metrics_strict(payload)
    s = json.dumps(strict, allow_nan=False)
    assert json.loads(s)["regime"] == regime