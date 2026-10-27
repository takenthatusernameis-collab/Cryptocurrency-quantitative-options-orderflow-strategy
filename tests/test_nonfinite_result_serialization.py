"""Tests for non-finite result serialization safety in strategy metrics."""

import json
import math

import numpy as np
import pytest


def sanitize_metrics(metrics: dict) -> dict:
    """Replace non-finite floats with None so JSON serialization is safe."""
    cleaned = {}
    for key, value in metrics.items():
        if isinstance(value, float):
            if math.isnan(value) or math.isinf(value):
                cleaned[key] = None
            else:
                cleaned[key] = value
        elif isinstance(value, np.floating):
            if np.isnan(value) or np.isinf(value):
                cleaned[key] = None
            else:
                cleaned[key] = float(value)
        else:
            cleaned[key] = value
    return cleaned


def test_json_rejects_nonfinite_by_default():
    with pytest.raises((ValueError, OverflowError)):
        json.dumps({"sharpe": float("nan")}, allow_nan=False)
    with pytest.raises((ValueError, OverflowError)):
        json.dumps({"drawdown": float("inf")}, allow_nan=False)


def test_sanitize_replaces_nan_and_inf():
    metrics = {
        "sharpe": float("nan"),
        "sortino": float("inf"),
        "max_dd": -float("inf"),
        "win_rate": 0.65,
        "trades": 120,
    }
    cleaned = sanitize_metrics(metrics)
    assert cleaned["sharpe"] is None
    assert cleaned["sortino"] is None
    assert cleaned["max_dd"] is None
    assert cleaned["win_rate"] == 0.65
    assert cleaned["trades"] == 120


def test_sanitize_is_json_serializable():
    metrics = {"sharpe": float("nan"), "sortino": 1.5}
    cleaned = sanitize_metrics(metrics)
    payload = json.dumps(cleaned, allow_nan=False)
    assert "null" in payload


def test_numpy_nonfinite_handled():
    metrics = {"var": np.float64(np.nan), "cvar": np.float64(np.inf), "mean": np.float64(0.05)}
    cleaned = sanitize_metrics(metrics)
    assert cleaned["var"] is None
    assert cleaned["cvar"] is None
    assert cleaned["mean"] == 0.05
    json.dumps(cleaned, allow_nan=False)
