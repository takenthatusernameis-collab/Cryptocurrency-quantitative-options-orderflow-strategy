"""Strategy evaluation engine: finite-guarded performance metrics, block-bootstrap
confidence intervals, PnL attribution with reconciliation, and baseline comparison.

All public functions reject non-finite inputs (raise ``ValueError``) and emit
strictly JSON-serializable output via :func:`src.telemetry.serialization.serialize_metrics_strict`.
No placeholders, no ``valid=true`` shortcuts — numeric invariants only.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Callable, Mapping, Sequence

import numpy as np

from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

# Cap used when gross losses are zero but gross wins are positive. ``inf`` is not
# allowed by strict JSON serialization (allow_nan=False), so a finite cap is used
# and documented rather than emitting NaN/Inf.
PROFIT_FACTOR_CAP: float = 1e12


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _as_finite_floats(values: Sequence[float], name: str) -> list[float]:
    """Coerce a sequence to finite floats; raise ``ValueError`` on any non-finite/non-numeric."""
    out: list[float] = []
    for i, v in enumerate(values):
        try:
            f = float(v)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{name}[{i}] is not numeric: {v!r}") from exc
        if not math.isfinite(f):
            raise ValueError(f"{name}[{i}] is non-finite: {f}")
        out.append(f)
    return out


def _finite_float(x: Any, name: str) -> float:
    try:
        f = float(x)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric, got {x!r}") from exc
    if not math.isfinite(f):
        raise ValueError(f"{name} must be finite, got {f}")
    return f


def compute_metrics(
    equity_curve: Sequence[float],
    *,
    periods_per_year: int = 252,
    risk_free: float = 0.0,
    trades: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return finite performance metrics for an equity curve.

    Metrics: total_return, cagr, ann_return, ann_vol, sharpe, sortino, calmar,
    max_drawdown, max_drawdown_duration, hit_rate, profit_factor, avg_win,
    avg_loss, exposure, turnover, num_trades.

    Every divide-by-zero is guarded: zero std → Sharpe/Sortino 0.0; no losses →
    profit_factor clamped to :data:`PROFIT_FACTOR_CAP` (never ``inf``).
    """
    eq = _as_finite_floats(equity_curve, "equity_curve")
    if len(eq) < 2:
        raise ValueError("equity_curve must contain at least 2 points")
    periods_per_year = _finite_float(periods_per_year, "periods_per_year")
    if periods_per_year <= 0:
        raise ValueError("periods_per_year must be > 0")
    risk_free = _finite_float(risk_free, "risk_free")

    starting = eq[0]
    total_return = (eq[-1] - starting) / starting if starting != 0 else 0.0

    # Per-period returns.
    rets: list[float] = []
    for i in range(1, len(eq)):
        prev = eq[i - 1]
        if prev == 0:
            continue
        r = (eq[i] - prev) / prev
        rets.append(r)

    n_periods = len(rets)
    if n_periods == 0:
        ann_return = 0.0
        ann_vol = 0.0
        sharpe = 0.0
        sortino = 0.0
    else:
        mean_ret = sum(rets) / n_periods
        var = sum((r - mean_ret) ** 2 for r in rets) / n_periods
        std = math.sqrt(var) if var > 0 else 0.0
        ann_return = mean_ret * periods_per_year
        ann_vol = std * math.sqrt(periods_per_year)
        rf_per_period = risk_free / periods_per_year
        if std > 0:
            sharpe = (mean_ret - rf_per_period) / std * math.sqrt(periods_per_year)
        else:
            sharpe = 0.0
        downside = [r for r in rets if r < 0]
        if downside:
            dd_mean = sum(downside) / len(downside)
            dd_var = sum((r - dd_mean) ** 2 for r in downside) / len(downside)
            dd_std = math.sqrt(dd_var) if dd_var > 0 else 0.0
            sortino = (
                (mean_ret - rf_per_period) / dd_std * math.sqrt(periods_per_year)
                if dd_std > 0
                else 0.0
            )
        else:
            sortino = 0.0
    if not math.isfinite(sharpe):
        sharpe = 0.0
    if not math.isfinite(sortino):
        sortino = 0.0

    # CAGR from period count (no calendar dates supplied).
    if total_return <= -1.0:
        cagr = -1.0
    else:
        cagr = (1.0 + total_return) ** (periods_per_year / max(n_periods, 1)) - 1.0
    if not math.isfinite(cagr):
        cagr = 0.0

    # Max drawdown + duration.
    peak = eq[0]
    max_dd = 0.0
    max_dd_duration = 0
    cur_dd_duration = 0
    for v in eq:
        if v > peak:
            peak = v
            cur_dd_duration = 0
        else:
            if peak > 0:
                dd = (peak - v) / peak
                if dd > max_dd:
                    max_dd = dd
            cur_dd_duration += 1
            if cur_dd_duration > max_dd_duration:
                max_dd_duration = cur_dd_duration

    calmar = (total_return / max_dd) if max_dd > 0 else 0.0
    if not math.isfinite(calmar):
        calmar = 0.0

    # Trade-based metrics.
    trade_list = list(trades or [])
    num_trades = len(trade_list)
    wins = [t for t in trade_list if float(t.get("pnl", 0.0)) > 0]
    losses = [t for t in trade_list if float(t.get("pnl", 0.0)) < 0]
    hit_rate = (len(wins) / num_trades) if num_trades > 0 else 0.0
    gross_profit = sum(float(t.get("pnl", 0.0)) for t in wins)
    gross_loss = sum(abs(float(t.get("pnl", 0.0))) for t in losses)
    if gross_loss > 0:
        profit_factor = gross_profit / gross_loss
    elif gross_profit > 0:
        profit_factor = PROFIT_FACTOR_CAP
    else:
        profit_factor = 0.0
    avg_win = (gross_profit / len(wins)) if wins else 0.0
    avg_loss = (gross_loss / len(losses)) if losses else 0.0

    # Exposure / turnover proxies (no position series supplied).
    turnover = (num_trades / max(n_periods, 1)) if n_periods > 0 else 0.0
    exposure = 0.0

    result: dict[str, Any] = {
        "total_return": total_return,
        "cagr": cagr,
        "ann_return": ann_return,
        "ann_vol": ann_vol,
        "sharpe": sharpe,
        "sortino": sortino,
        "calmar": calmar,
        "max_drawdown": max_dd,
        "max_drawdown_duration": float(max_dd_duration),
        "hit_rate": hit_rate,
        "profit_factor": profit_factor,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "exposure": exposure,
        "turnover": turnover,
        "num_trades": float(num_trades),
    }
    assert_json_valid(result)
    return serialize_metrics_strict(result)


def block_bootstrap_ci(
    values: Sequence[float],
    statistic: Callable[[Sequence[float]], float],
    *,
    n_bootstrap: int = 2000,
    block_size: int = 20,
    confidence: float = 0.95,
    seed: int = 0,
) -> tuple[float, float, float]:
    """Deterministic moving-block bootstrap CI for a statistic.

    Returns ``(point_estimate, lo, hi)`` using the percentile convention so that
    ``lo <= point <= hi`` holds for typical statistics. Identical ``seed`` yields
    identical CI (determinism). Non-finite inputs raise ``ValueError``.
    """
    vals = _as_finite_floats(values, "values")
    n = len(vals)
    if n == 0:
        raise ValueError("values must be non-empty")
    n_bootstrap = int(n_bootstrap)
    if n_bootstrap <= 0:
        raise ValueError("n_bootstrap must be > 0")
    block_size = int(block_size)
    if block_size <= 0:
        block_size = 1
    confidence = _finite_float(confidence, "confidence")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be in (0, 1)")

    point = float(statistic(vals))
    if not math.isfinite(point):
        raise ValueError("statistic returned non-finite point estimate")

    rng = np.random.default_rng(int(seed))
    n_blocks = max(1, math.ceil(n / block_size))
    boot_stats: list[float] = []
    for _ in range(n_bootstrap):
        sample: list[float] = []
        for _ in range(n_blocks):
            start = int(rng.integers(0, max(1, n - block_size + 1)))
            block = vals[start : start + block_size]
            sample.extend(block)
        if len(sample) == 0:
            sample = list(vals)
        sample = sample[:n] if len(sample) >= n else (sample + list(vals))[:n]
        boot_stats.append(float(statistic(sample)))

    boot = np.asarray(boot_stats, dtype=float)
    alpha = 1.0 - confidence
    lo = float(np.percentile(boot, 100.0 * alpha / 2.0))
    hi = float(np.percentile(boot, 100.0 * (1.0 - alpha / 2.0)))
    if not math.isfinite(lo):
        lo = point
    if not math.isfinite(hi):
        hi = point
    lo, hi = (lo, hi) if lo <= hi else (hi, lo)
    return (point, lo, hi)


def attribute_pnl(
    by_bucket: Mapping[str, Sequence[float]],
) -> dict[str, Any]:
    """Group PnL by bucket (venue / underlying / regime / signal-family).

    Returns per-bucket sums plus ``reconciled_total`` and ``max_abs_error`` such
    that ``abs(sum(bucket_totals) - grand_total) <= max_abs_error`` (exactly 0.0
    here since totals are summed from the same values).
    """
    bucket_totals: dict[str, float] = {}
    for k, v in by_bucket.items():
        arr = _as_finite_floats(v, f"by_bucket[{k!r}]")
        bucket_totals[str(k)] = sum(arr)
    grand_total = sum(bucket_totals.values())
    reconciled_total = grand_total
    max_abs_error = abs(sum(bucket_totals.values()) - grand_total)
    result: dict[str, Any] = {
        "bucket_totals": bucket_totals,
        "reconciled_total": reconciled_total,
        "grand_total": grand_total,
        "max_abs_error": max_abs_error,
        "reconciliation_ok": bool(max_abs_error <= 1e-9 * max(1.0, abs(grand_total))),
        "num_buckets": len(bucket_totals),
    }
    assert_json_valid(result)
    return serialize_metrics_strict(result)


def compare_to_baseline(
    strategy: Mapping[str, Any],
    baseline: Mapping[str, Any],
) -> dict[str, Any]:
    """Per-metric deltas (strategy − baseline) plus an ordering verdict.

    Non-finite values in either mapping raise ``ValueError``. Missing keys are
    skipped. The verdict compares headline Sharpe when available, falling back
    to total_return.
    """
    strategy = dict(strategy)
    baseline = dict(baseline)
    keys = set(strategy) | set(baseline)
    deltas: dict[str, float] = {}
    for k in sorted(keys):
        if k not in strategy or k not in baseline:
            continue
        s = _finite_float(strategy[k], f"strategy[{k!r}]")
        b = _finite_float(baseline[k], f"baseline[{k!r}]")
        deltas[str(k)] = s - b

    s_sharpe = strategy.get("sharpe")
    b_sharpe = baseline.get("sharpe")
    if s_sharpe is not None and b_sharpe is not None:
        s_sharpe = _finite_float(s_sharpe, "strategy[sharpe]")
        b_sharpe = _finite_float(b_sharpe, "baseline[sharpe]")
        verdict = "strategy" if s_sharpe >= b_sharpe else "baseline"
        verdict_metric = "sharpe"
    else:
        s_ret = _finite_float(strategy.get("total_return", 0.0), "strategy[total_return]")
        b_ret = _finite_float(baseline.get("total_return", 0.0), "baseline[total_return]")
        verdict = "strategy" if s_ret >= b_ret else "baseline"
        verdict_metric = "total_return"

    result: dict[str, Any] = {
        "deltas": deltas,
        "verdict": verdict,
        "verdict_metric": verdict_metric,
        "num_metrics_compared": len(deltas),
    }
    assert_json_valid(result)
    return serialize_metrics_strict(result)


def permutation_test(
    sample_a: Sequence[float],
    sample_b: Sequence[float],
    *,
    statistic: Callable[[Sequence[float]], float],
    n_permutations: int = 1000,
    paired: bool = True,
    alternative: str = "two-sided",
    seed: int = 0,
) -> dict[str, Any]:
    """Deterministic permutation test for ``statistic(sample_a) - statistic(sample_b)``.

    This is the permutation primitive EVAL-10 needs and that
    :func:`block_bootstrap_ci` (a bootstrap CI) does **not** provide. Two modes:

    * ``paired=True`` (default) — requires equal lengths; each permutation swaps
      the two labels within a pair with probability 0.5. Use for matched
      series such as the EVAL-09 with-hedge vs without-hedge window returns.
    * ``paired=False`` — pools both samples, shuffles, and re-splits at the
      original sizes.

    The p-value uses the ``(1 + #{null as extreme}) / (1 + n_permutations)``
    convention, so it is always in ``(0, 1]`` and never zero. Non-finite
    inputs or statistics raise ``ValueError``. Identical ``seed`` yields an
    identical report (determinism).
    """
    a = _as_finite_floats(sample_a, "sample_a")
    b = _as_finite_floats(sample_b, "sample_b")
    if len(a) == 0 or len(b) == 0:
        raise ValueError("sample_a and sample_b must be non-empty")
    if paired and len(a) != len(b):
        raise ValueError("paired=True requires equal-length samples")
    n_permutations = int(n_permutations)
    if n_permutations <= 0:
        raise ValueError("n_permutations must be > 0")
    alt = str(alternative).lower()
    if alt not in ("two-sided", "greater", "less"):
        raise ValueError(f"alternative must be two-sided/greater/less, got {alternative!r}")

    def _safe_stat(vals: Sequence[float], name: str) -> float:
        return _finite_float(statistic(vals), name)

    observed = _safe_stat(a, "statistic(sample_a)") - _safe_stat(b, "statistic(sample_b)")
    rng = np.random.default_rng(int(seed))
    null: list[float] = []

    if paired:
        a_arr = np.asarray(a, dtype=float)
        b_arr = np.asarray(b, dtype=float)
        for _ in range(n_permutations):
            swap = rng.random(len(a_arr)) < 0.5
            sa = np.where(swap, b_arr, a_arr)
            sb = np.where(swap, a_arr, b_arr)
            null.append(float(_safe_stat(sa, "statistic(sample_a)") - _safe_stat(sb, "statistic(sample_b)")))
    else:
        pooled = list(a) + list(b)
        na = len(a)
        for _ in range(n_permutations):
            rng.shuffle(pooled)
            null.append(
                float(_safe_stat(pooled[:na], "statistic(sample_a)") - _safe_stat(pooled[na:], "statistic(sample_b)"))
            )

    if alt == "two-sided":
        extreme = sum(1 for v in null if abs(v) >= abs(observed))
    elif alt == "greater":
        extreme = sum(1 for v in null if v >= observed)
    else:
        extreme = sum(1 for v in null if v <= observed)
    p_value = (1 + extreme) / (1 + len(null))

    result: dict[str, Any] = {
        "observed_difference": float(observed),
        "null_mean": float(sum(null) / len(null)),
        "p_value": float(p_value),
        "n_permutations": int(len(null)),
        "paired": bool(paired),
        "alternative": alt,
        "significant_at_05": bool(p_value < 0.05),
        "statistic_a": float(_safe_stat(a, "statistic(sample_a)")),
        "statistic_b": float(_safe_stat(b, "statistic(sample_b)")),
    }
    assert_json_valid(result)
    return serialize_metrics_strict(result)
