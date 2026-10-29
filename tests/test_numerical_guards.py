"""Tests for numerical guards (src/utils/numerical_guards.py).

Covers safe_divide, safe_log, safe_sqrt, safe_pct_change, ensure_finite,
validate_finite, safe_mean, and clamp across normal, degenerate, and
adversarial inputs. No NaN/Inf may leak from any guard.
"""

import math

from src.errors import FeatureError, NonFiniteResultError
from src.utils.numerical_guards import (
    clamp,
    ensure_finite,
    safe_divide,
    safe_log,
    safe_mean,
    safe_pct_change,
    safe_sqrt,
    validate_finite,
)


def test_safe_divide_normal():
    assert safe_divide(10.0, 2.0) == 5.0
    assert safe_divide(-6.0, 3.0) == -2.0
    assert safe_divide(0.0, 5.0) == 0.0


def test_safe_divide_zero_denominator_default():
    assert safe_divide(1.0, 0.0) == 0.0
    assert safe_divide(1.0, 0.0, default=42.0) == 42.0


def test_safe_divide_zero_denominator_raises():
    try:
        safe_divide(1.0, 0.0, raise_on_zero=True)
    except FeatureError:
        pass
    else:
        raise AssertionError("expected FeatureError for zero denominator")


def test_safe_divide_non_finite_operand():
    assert safe_divide(float("nan"), 2.0) == 0.0
    assert safe_divide(1.0, float("inf")) == 0.0
    assert safe_divide(float("inf"), 2.0) == 0.0


def test_safe_divide_non_convertible():
    assert safe_divide("abc", 2.0) == 0.0
    assert safe_divide(1.0, None) == 0.0


def test_safe_log_normal():
    assert safe_log(1.0) == 0.0
    assert abs(safe_log(math.e) - 1.0) < 1e-12


def test_safe_log_non_positive_default():
    assert safe_log(0.0) == 0.0
    assert safe_log(-1.0) == 0.0
    assert safe_log(-1.0, default=-9.0) == -9.0


def test_safe_log_non_positive_raises():
    try:
        safe_log(0.0, raise_on_nonpositive=True)
    except FeatureError:
        pass
    else:
        raise AssertionError("expected FeatureError for log of zero")


def test_safe_log_non_finite():
    assert safe_log(float("nan")) == 0.0
    assert safe_log(float("inf")) == 0.0


def test_safe_sqrt_normal():
    assert safe_sqrt(4.0) == 2.0
    assert safe_sqrt(0.0) == 0.0


def test_safe_sqrt_negative_default():
    assert safe_sqrt(-1.0) == 0.0
    assert safe_sqrt(-1.0, default=7.0) == 7.0


def test_safe_sqrt_negative_raises():
    try:
        safe_sqrt(-1.0, raise_on_negative=True)
    except FeatureError:
        pass
    else:
        raise AssertionError("expected FeatureError for sqrt of negative")


def test_safe_sqrt_non_finite():
    assert safe_sqrt(float("nan")) == 0.0
    assert safe_sqrt(float("inf")) == 0.0


def test_safe_pct_change_normal():
    assert safe_pct_change(110.0, 100.0) == 0.1
    assert safe_pct_change(90.0, 100.0) == -0.1


def test_safe_pct_change_zero_previous_default():
    assert safe_pct_change(5.0, 0.0) == 0.0
    assert safe_pct_change(5.0, 0.0, default=3.0) == 3.0


def test_safe_pct_change_zero_previous_raises():
    try:
        safe_pct_change(5.0, 0.0, raise_on_zero=True)
    except FeatureError:
        pass
    else:
        raise AssertionError("expected FeatureError for pct-change on zero")


def test_safe_pct_change_non_finite():
    assert safe_pct_change(float("nan"), 100.0) == 0.0
    assert safe_pct_change(110.0, float("inf")) == 0.0


def test_ensure_finite_finite_passthrough():
    assert ensure_finite(3.5) == 3.5
    assert ensure_finite(3, name="int_val") == 3.0


def test_ensure_finite_non_finite_raises():
    for bad in (float("nan"), float("inf"), float("-inf")):
        try:
            ensure_finite(bad, name="x")
        except NonFiniteResultError:
            pass
        else:
            raise AssertionError(f"expected NonFiniteResultError for {bad}")


def test_ensure_finite_non_convertible_raises():
    try:
        ensure_finite("not_a_number", name="x")
    except NonFiniteResultError:
        pass
    else:
        raise AssertionError("expected NonFiniteResultError for non-convertible")


def test_validate_finite_finite_passthrough():
    assert validate_finite(2.5, "x") == 2.5


def test_validate_finite_non_finite_raises():
    for bad in (float("nan"), float("inf")):
        try:
            validate_finite(bad, "x")
        except NonFiniteResultError:
            pass
        else:
            raise AssertionError(f"expected NonFiniteResultError for {bad}")


def test_safe_mean_normal():
    assert safe_mean([1.0, 2.0, 3.0]) == 2.0


def test_safe_mean_empty():
    assert safe_mean([]) == 0.0
    assert safe_mean([], default=5.0) == 5.0


def test_safe_mean_skips_non_finite():
    assert safe_mean([1.0, float("nan"), 3.0, None, "x"]) == 2.0


def test_clamp_normal():
    assert clamp(5.0, 0.0, 10.0) == 5.0
    assert clamp(-1.0, 0.0, 10.0) == 0.0
    assert clamp(100.0, 0.0, 10.0) == 10.0


def test_clamp_non_finite():
    assert clamp(float("nan"), 0.0, 10.0) == 0.0
    assert clamp(5.0, float("nan"), 10.0) == 0.0


def test_clamp_invalid_bounds():
    assert clamp(5.0, 10.0, 0.0) == 0.0
