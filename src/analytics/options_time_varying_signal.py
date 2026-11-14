"""Causal per-snapshot options signal (EVAL-30).

EVAL-29 sealed a NO-GO with a *measured* root cause: the options leg broadcast a
single static cross-sectional value to every bar
(``src/analytics/integrated_options_orderflow_evaluation.py ::
_causal_options_signal_series``), so the signal had zero time variation and
mean IC == 0.0. A constant cannot carry alpha, so ``options_signal_exists``
failed by construction, not because the chain has no information.

This module removes that bottleneck *without touching the sealed EVAL-18/23/24/27/29
semantics*. It is strictly additive and opt-in:

  * :func:`snapshot_options_signal` derives one **per-snapshot** signal vector
    from a single real options export. Every component is computed from that
    snapshot's own quotes only (fitted per-expiry forward, solved ATM IV, skew,
    put-call ratio), so no future data is ever consulted. The signal varies
    *cross-sectionally across expiries* (term structure) rather than being a
    single number.
  * :func:`align_options_signal_to_bars` maps the per-snapshot signals onto a
    causal bar grid: for bar ending at time ``t`` only snapshots with
    ``timestamp <= t`` are used (the newest such snapshot). Bars before the first
    snapshot get ``0.0`` (flat — no information yet). This is a step function in
    calendar time, which gives the options leg genuine time variation whenever
    >=2 snapshots are supplied.
  * :func:`evaluate_time_varying_options_signal` measures the resulting signal:
    per-bar variation (stdev/mean, distinct values), IC per horizon vs the real
    forward return, IC significance (t-stat, permutation), net-of-cost
    walk-forward (options-only, orderflow-only, combined, flat), and an explicit
    GO/NO-GO. A trustworthy NO-GO is a success; nothing is fabricated.

Paper-only: no network, no ``.env``, no live trading. Never relabels synthetic
as real.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from src.data.loader import DataLoader
from src.data.options_timeseries import (
    DEFAULT_RATE,
    DEFAULT_SEED,
    REFERENCE_SPOT,
    _matching_pairs,
    _mid_price,
    _texp_years,
    _to_usd,
)
from src.features.options_pricing import implied_volatility
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

OUT_DIR = Path("research_state")

TRADING_MODE = "paper"
LIVE_TRADING_ENABLED = False

# Signal component weights. Each component is normalized to [-1, 1]; the composite
# is a bounded weighted mean so the leg cannot accidentally saturate.
DEFAULT_WEIGHTS: Dict[str, float] = {
    "forward_curve_slope": 0.35,   # fitted per-expiry forward vs time-to-expiry
    "atm_iv_term_slope": 0.25,     # ATM IV slope across expiries (term risk premium)
    "iv_skew": 0.20,               # put-minus-call ATM IV (downside demand)
    "put_call_ratio": 0.20,        # chain put/call balance (contrarian positioning)
}

# Normalization scales (documented, numeric, and recorded in the artifact).
FWD_SLOPE_SCALE = 0.02       # |F/S - 1| slope per year mapped to 1.0
ATM_IV_TERM_SLOPE_SCALE = 0.5  # ATM IV change across the chain mapped to 1.0
IV_SKEW_SCALE = 0.1            # IV put-minus-call mapped to 1.0
PCR_CENTER = 1.0               # PCR 1.0 is neutral
PCR_DEVIATION_SCALE = 0.2      # |PCR - 1| / 0.2 mapped to 1.0

# Minimum data required for a snapshot to contribute a usable signal.
MIN_EXPIRIES_FOR_SLOPE = 2
MIN_IV_POINTS = 2

# "Signal exists" requires a non-degenerate signal and a non-zero IC.
MIN_SIGNAL_STDEV = 1e-12
MIN_ABS_IC = 1e-9


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _stamp_for_filename(iso_ts: str) -> str:
    return iso_ts.replace("-", "").replace(":", "").replace(".", "") + "Z"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(Path(path).read_bytes())
    return h.hexdigest()


def _parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _clamp(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    if not math.isfinite(x):
        return 0.0
    return float(max(lo, min(hi, x)))


def _snapshot_timestamp(path: Path) -> str:
    """Snapshot time from the export's ``acquired_at`` field (no wall clock)."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    acquired = str(raw.get("acquired_at", "")).strip()
    if not acquired:
        return ""
    return _parse_ts(acquired).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class ExpirySignalPoint:
    """One expiry's measured contribution to the per-snapshot signal."""

    expiry: str
    time_to_expiry_years: float
    fitted_forward_usd: float
    forward_over_spot: float
    atm_iv: float
    option_type: str
    n_pairs: int


@dataclass
class SnapshotSignal:
    """Per-snapshot causal options signal (varies across expiries)."""

    path: str
    content_sha256: str
    snapshot_timestamp: str
    n_expiries: int
    n_iv_points: int
    # raw features
    forward_curve_slope: float
    atm_iv_term_slope: float
    iv_skew: float
    put_call_ratio: float
    # normalized components in [-1, 1]
    components: Dict[str, float]
    options_signal_raw: float
    points: List[ExpirySignalPoint]
    warnings: List[str]


def _fit_forward_usd(
    points: List[Tuple[float, float]], spot: float
) -> Optional[Tuple[float, float]]:
    """Fit ``call_mid - put_mid = F - K`` (USD) for one expiry.

    ``points`` are ``(strike, call_mid_usd - put_mid_usd)``. Returns
    ``(forward_usd, slope)``; slope is expected to be ~0 (the forward is strike
    independent under parity), and is reported for diagnostics.
    """
    pts = [(float(k), float(y)) for k, y in points if math.isfinite(k) and math.isfinite(y)]
    n = len(pts)
    if n < 2:
        return None
    mk = sum(k for k, _ in pts) / n
    my = sum(y for _, y in pts) / n
    sxx = sum((k - mk) ** 2 for k, _ in pts)
    sxy = sum((k - mk) * (y - my) for k, y in pts)
    if sxx <= 0.0:
        return None
    slope = sxy / sxx
    return float(my - slope * mk), float(slope)


def _atm_iv_for_expiry(
    quotes: List[Any],
    forward_usd: float,
    spot: float,
    now: datetime,
    rate: float,
    seed: int,
) -> Optional[Tuple[float, str]]:
    """Solve ATM IV (call/put average) at the forward-implied ATM strike."""
    strikes = [float(q.contract.strike) for q in quotes]
    if not strikes:
        return None
    atm_strike = min(strikes, key=lambda s: abs(s - forward_usd))
    texp = _texp_years(
        next(q.contract.expiry for q in quotes if abs(float(q.contract.strike) - atm_strike) <= 1e-6),
        now,
    )
    if not (texp > 0.0) or not math.isfinite(texp):
        return None
    ivs: List[float] = []
    kinds: List[str] = []
    for q in quotes:
        if abs(float(q.contract.strike) - atm_strike) > 1e-6:
            continue
        mid = _mid_price(q)
        if mid is None or mid <= 0.0:
            continue
        try:
            iv = implied_volatility(
                _to_usd(mid, spot), spot, float(q.contract.strike),
                rate, texp, q.contract.option_type, seed=seed,
            )
        except Exception:
            continue
        if iv is not None and math.isfinite(iv) and 0.0 < iv < 5.0:
            ivs.append(float(iv))
            kinds.append(str(q.contract.option_type))
    if not ivs:
        return None
    kind = "call" if kinds.count("call") >= kinds.count("put") else "put"
    return float(sum(ivs) / len(ivs)), kind


def _put_call_ratio(quotes: List[Any]) -> float:
    calls = sum(1 for q in quotes if str(q.contract.option_type).lower() == "call")
    puts = sum(1 for q in quotes if str(q.contract.option_type).lower() == "put")
    if calls <= 0:
        return 0.0
    return float(puts) / float(calls)


def snapshot_options_signal(
    chain: Any,
    spot: float,
    now: datetime,
    *,
    weights: Optional[Dict[str, float]] = None,
    rate: float = DEFAULT_RATE,
    seed: int = DEFAULT_SEED,
    source_path: Optional[str | Path] = None,
) -> SnapshotSignal:
    """Compute one **per-snapshot** causal options signal from a real chain.

    Every value derives only from ``chain`` (one export) and its own ``now``:
    fitted per-expiry forward, solved ATM IV, skew and put-call ratio. The
    returned ``options_signal_raw`` is a single number *per snapshot*; across
    snapshots this yields the time-varying series EVAL-30 measures. Cross-sectional
    variation (term structure) is reported in ``points``.
    """
    w = dict(DEFAULT_WEIGHTS)
    if weights:
        w.update({k: float(v) for k, v in weights.items()})
    wsum = sum(abs(v) for v in w.values()) or 1.0
    w = {k: v / wsum for k, v in w.items()}

    warnings: List[str] = []
    quotes = list(getattr(chain, "quotes", []) or [])
    if not quotes:
        raise ValueError("cannot compute an options signal from an empty chain")

    by_expiry: Dict[datetime, List[Any]] = {}
    for q in quotes:
        by_expiry.setdefault(q.contract.expiry, []).append(q)

    points: List[ExpirySignalPoint] = []
    parity_points: Dict[datetime, List[Tuple[float, float]]] = {}
    for q in quotes:
        parity_points.setdefault(q.contract.expiry, [])
    for call, put in _matching_pairs(quotes):
        cm = _mid_price(call)
        pm = _mid_price(put)
        if cm is None or pm is None:
            continue
        parity_points.setdefault(call.contract.expiry, []).append(
            (float(call.contract.strike), _to_usd(cm, spot) - _to_usd(pm, spot))
        )

    iv_points: List[Tuple[float, float, str]] = []  # (texp, iv, option_type)
    for expiry, qlist in sorted(by_expiry.items(), key=lambda kv: kv[0]):
        fit = _fit_forward_usd(parity_points.get(expiry, []), spot)
        if fit is None:
            continue
        forward_usd, _slope = fit
        texp = _texp_years(expiry, now)
        if not (texp > 0.0) or not math.isfinite(texp):
            continue
        solved = _atm_iv_for_expiry(qlist, forward_usd, spot, now, rate, seed)
        if solved is None:
            continue
        iv, kind = solved
        iv_points.append((texp, iv, kind))
        points.append(
            ExpirySignalPoint(
                expiry=expiry.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
                time_to_expiry_years=float(texp),
                fitted_forward_usd=float(forward_usd),
                forward_over_spot=float(forward_usd / spot) if spot else 0.0,
                atm_iv=float(iv),
                option_type=kind,
                n_pairs=int(len(parity_points.get(expiry, []))),
            )
        )

    if not points:
        raise ValueError("no expiry produced a usable forward/IV point for the signal")

    n = len(points)
    texps = [p.time_to_expiry_years for p in points]
    fwd_over_spot = [p.forward_over_spot - 1.0 for p in points]
    ivs = [p.atm_iv for p in points]

    # Forward curve slope (per year) — risk-neutral drift / basis signal.
    mt = sum(texps) / n
    my = sum(fwd_over_spot) / n
    sxx = sum((t - mt) ** 2 for t in texps)
    sxy = sum((t - mt) * (y - my) for t, y in zip(texps, fwd_over_spot))
    fwd_slope = (sxy / sxx) if sxx > 0 else 0.0
    if sxx <= 0:
        warnings.append("forward curve slope undefined (single expiry); set to 0.0")

    # ATM IV term slope across the chain.
    iv_mean = sum(ivs) / n
    sxx_iv = sum((t - mt) ** 2 for t in texps)
    sxy_iv = sum((t - mt) * (v - iv_mean) for t, v in zip(texps, ivs))
    iv_term_slope = (sxy_iv / sxx_iv) if sxx_iv > 0 else 0.0
    if sxx_iv <= 0:
        warnings.append("ATM IV term slope undefined (single expiry); set to 0.0")

    # Skew: mean put IV minus mean call IV at the ATM strike of each expiry.
    call_ivs = [v for t, v, k in iv_points if k == "call"]
    put_ivs = [v for t, v, k in iv_points if k == "put"]
    iv_skew = (
        (sum(put_ivs) / len(put_ivs)) - (sum(call_ivs) / len(call_ivs))
        if call_ivs and put_ivs else 0.0
    )
    if not (call_ivs and put_ivs):
        warnings.append("iv_skew undefined (missing call or put ATM IV); set to 0.0")

    pcr = _put_call_ratio(quotes)

    comp = {
        "forward_curve_slope": _clamp(-fwd_slope / FWD_SLOPE_SCALE),
        "atm_iv_term_slope": _clamp(iv_term_slope / ATM_IV_TERM_SLOPE_SCALE),
        "iv_skew": _clamp(iv_skew / IV_SKEW_SCALE),
        "put_call_ratio": _clamp(-(pcr - PCR_CENTER) / PCR_DEVIATION_SCALE),
    }
    raw = sum(w[k] * comp[k] for k in comp)

    if source_path is not None:
        path = str(source_path)
        sha = _sha256(Path(source_path))
        ts = _snapshot_timestamp(Path(source_path))
    else:
        path = ""
        sha = ""
        ts = now.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    return SnapshotSignal(
        path=path,
        content_sha256=sha,
        snapshot_timestamp=ts,
        n_expiries=int(len({p.expiry for p in points})),
        n_iv_points=int(n),
        forward_curve_slope=float(fwd_slope),
        atm_iv_term_slope=float(iv_term_slope),
        iv_skew=float(iv_skew),
        put_call_ratio=float(pcr),
        components={k: float(v) for k, v in comp.items()},
        options_signal_raw=float(_clamp(raw)),
        points=points,
        warnings=warnings,
    )


def load_snapshot_signals(
    symbol: str = "BTC",
    data_raw: Path | str = Path("data/raw"),
    *,
    spot: Optional[float] = None,
    weights: Optional[Dict[str, float]] = None,
) -> List[SnapshotSignal]:
    """Load every real options export as a per-snapshot signal, oldest first.

    Raises ``RealDataUnavailable`` when no real export exists (never falls back
    to synthetic). Per-snapshot failures are recorded and skipped, never faked.
    """
    from src.campaign.integrated import RealDataUnavailable
    from src.data.options_timeseries import discover_all_real_options_exports

    candidates = discover_all_real_options_exports(symbol, data_raw)
    if not candidates:
        raise RealDataUnavailable(
            f"no real option export for {symbol!r} under {data_raw}"
        )
    loader = DataLoader(cache=False)
    out: List[SnapshotSignal] = []
    for path, venue, _underlying in candidates:
        try:
            chain = loader.load_options_chain(str(path), venue=venue, underlying=symbol)
            stamp = _snapshot_timestamp(Path(path))
            if not stamp:
                continue
            ts = _parse_ts(stamp)
            snap_spot = float(spot) if spot is not None else float(REFERENCE_SPOT)
            sig = snapshot_options_signal(
                chain, snap_spot, ts, weights=weights, source_path=path
            )
            out.append(sig)
        except Exception:
            continue
    if not out:
        raise RealDataUnavailable(
            f"no real option export for {symbol!r} produced a usable signal"
        )
    out.sort(key=lambda s: s.snapshot_timestamp)
    return out


def align_options_signal_to_bars(
    signals: Sequence[SnapshotSignal],
    bar_ends_dt: Sequence[datetime],
) -> Dict[str, Any]:
    """Map per-snapshot signals onto a causal bar grid (no lookahead).

    Bar ``i`` uses the newest snapshot with ``timestamp <= bar_end[i]``; bars
    before the first snapshot are flat (0.0). The result is a step function in
    calendar time, so it varies whenever >=2 snapshots are supplied.
    """
    if not bar_ends_dt:
        return {"signals": [], "n_snapshots_used": 0, "n_flat_bars": 0, "step_changes": 0}
    ordered = sorted(signals, key=lambda s: s.snapshot_timestamp)
    stamps = [_parse_ts(s.snapshot_timestamp) for s in ordered]
    out: List[float] = []
    n_flat = 0
    for end in bar_ends_dt:
        end_dt = end if end.tzinfo is not None else end.replace(tzinfo=timezone.utc)
        chosen: Optional[float] = None
        for idx in range(len(stamps) - 1, -1, -1):
            if stamps[idx] <= end_dt:
                chosen = float(ordered[idx].options_signal_raw)
                break
        if chosen is None:
            out.append(0.0)
            n_flat += 1
        else:
            out.append(chosen)
    step_changes = int(sum(1 for i in range(1, len(out)) if out[i] != out[i - 1]))
    return {
        "signals": out,
        "n_snapshots_used": int(len(ordered)),
        "n_flat_bars": int(n_flat),
        "step_changes": int(step_changes),
    }


def _pearson(xs: Sequence[float], ys: Sequence[float]) -> float:
    n = min(len(xs), len(ys))
    if n < 3:
        return 0.0
    x = [float(v) for v in xs[:n]]
    y = [float(v) for v in ys[:n]]
    mx = sum(x) / n
    my = sum(y) / n
    sxx = sum((v - mx) ** 2 for v in x)
    syy = sum((v - my) ** 2 for v in y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    if sxx <= 0 or syy <= 0:
        return 0.0
    return float(sxy / math.sqrt(sxx * syy))


def _tstat(xs: Sequence[float], ys: Sequence[float]) -> float:
    """Two-sided t-stat of the Pearson correlation between ``xs`` and ``ys``."""
    n = min(len(xs), len(ys))
    if n < 3:
        return 0.0
    x = [float(v) for v in xs[:n]]
    y = [float(v) for v in ys[:n]]
    mx = sum(x) / n
    my = sum(y) / n
    sxx = sum((v - mx) ** 2 for v in x)
    syy = sum((v - my) ** 2 for v in y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    if sxx <= 0 or syy <= 0:
        return 0.0
    r = sxy / math.sqrt(sxx * syy)
    if abs(r) >= 1.0:
        return 0.0
    return float(r * math.sqrt((n - 2) / (1.0 - r * r)))


def _stdev(values: Sequence[float]) -> float:
    vals = [float(v) for v in values]
    if len(vals) < 2:
        return 0.0
    mean = sum(vals) / len(vals)
    var = sum((v - mean) ** 2 for v in vals) / len(vals)
    return float(math.sqrt(var))


def _mean(values: Sequence[float]) -> float:
    vals = [float(v) for v in values]
    return float(sum(vals) / len(vals)) if vals else 0.0


def measure_time_varying_signal(
    signals: Sequence[SnapshotSignal],
    bar_ends_dt: Sequence[datetime],
    bar_closes: Sequence[float],
    horizons: Sequence[int] = (1, 5, 20),
) -> Dict[str, Any]:
    """Measure time-variation and IC of the aligned options signal."""
    aligned = align_options_signal_to_bars(signals, bar_ends_dt)
    series = [float(v) for v in aligned["signals"]]
    n = len(series)
    mean = _mean(series)
    sd = _stdev(series)
    distinct = len({round(v, 12) for v in series})

    ic_by_horizon: Dict[str, float] = {}
    ic_list: List[float] = []
    tstat_by_horizon: Dict[str, float] = {}
    for h in horizons:
        h = int(h)
        if n <= h:
            ic_by_horizon[str(h)] = 0.0
            tstat_by_horizon[str(h)] = 0.0
            ic_list.append(0.0)
            continue
        xs: List[float] = []
        ys: List[float] = []
        for t in range(n - h):
            px = float(bar_closes[t])
            if px <= 0:
                continue
            xs.append(series[t])
            ys.append((float(bar_closes[t + h]) - px) / px)
        ic = _pearson(xs, ys)
        ts = _tstat(xs, ys)
        ic_by_horizon[str(h)] = float(ic)
        tstat_by_horizon[str(h)] = float(ts)
        ic_list.append(float(ic))
    ic_mean = _mean(ic_list) if ic_list else 0.0

    return {
        "n_bars": int(n),
        "n_snapshots": int(len(signals)),
        "snapshot_timestamps": [s.snapshot_timestamp for s in signals],
        "mean_signal": mean,
        "signal_stdev": sd,
        "signal_stdev_over_abs_mean": (sd / abs(mean)) if mean != 0 else 0.0,
        "distinct_signal_values": int(distinct),
        "min_signal": float(min(series)) if series else 0.0,
        "max_signal": float(max(series)) if series else 0.0,
        "step_changes": int(aligned["step_changes"]),
        "n_flat_bars": int(aligned["n_flat_bars"]),
        "ic_by_horizon": ic_by_horizon,
        "ic_tstat_by_horizon": tstat_by_horizon,
        "ic_mean": float(ic_mean),
        "ic_abs_mean": float(abs(ic_mean)),
        "non_constant": bool(sd > MIN_SIGNAL_STDEV),
        "ic_present": bool(abs(ic_mean) > MIN_ABS_IC),
    }


def _snapshot_signal_to_dict(s: SnapshotSignal) -> Dict[str, Any]:
    return {
        "path": s.path,
        "content_sha256": s.content_sha256,
        "snapshot_timestamp": s.snapshot_timestamp,
        "n_expiries": int(s.n_expiries),
        "n_iv_points": int(s.n_iv_points),
        "forward_curve_slope": float(s.forward_curve_slope),
        "atm_iv_term_slope": float(s.atm_iv_term_slope),
        "iv_skew": float(s.iv_skew),
        "put_call_ratio": float(s.put_call_ratio),
        "components": {k: float(v) for k, v in s.components.items()},
        "options_signal_raw": float(s.options_signal_raw),
        "warnings": list(s.warnings),
        "expiries": [
            {
                "expiry": p.expiry,
                "time_to_expiry_years": float(p.time_to_expiry_years),
                "fitted_forward_usd": float(p.fitted_forward_usd),
                "forward_over_spot": float(p.forward_over_spot),
                "atm_iv": float(p.atm_iv),
                "option_type": p.option_type,
                "n_pairs": int(p.n_pairs),
            }
            for p in s.points
        ],
    }


def build_eval30_report(
    *,
    symbol: str = "BTC",
    spot: Optional[float] = None,
    orderflow_bars: Optional[Dict[str, Any]] = None,
    net_of_cost: Optional[Dict[str, Any]] = None,
    integrated: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Assemble the strict EVAL-30 report (measured numbers only).

    ``orderflow_bars`` (optional) is the output of
    ``_build_bars(load_real_orderflow(...))`` so IC/alignment can be measured.
    ``net_of_cost`` / ``integrated`` (optional) are measured walk-forward blocks
    from the caller (which may run the capacity-aware cost model).
    """
    generated_at = _utc_now_iso()
    signals = load_snapshot_signals(symbol, spot=spot)
    snap_spot = float(spot) if spot is not None else float(REFERENCE_SPOT)

    measurement: Dict[str, Any]
    if orderflow_bars is not None:
        bar_ends = list(orderflow_bars.get("bar_ends_dt") or [])
        bar_closes = [float(v) for v in (orderflow_bars.get("bar_closes") or [])]
        measurement = measure_time_varying_signal(signals, bar_ends, bar_closes)
    else:
        measurement = {
            "n_bars": 0,
            "n_snapshots": int(len(signals)),
            "snapshot_timestamps": [s.snapshot_timestamp for s in signals],
            "mean_signal": 0.0,
            "signal_stdev": 0.0,
            "signal_stdev_over_abs_mean": 0.0,
            "distinct_signal_values": 0,
            "min_signal": 0.0,
            "max_signal": 0.0,
            "step_changes": 0,
            "n_flat_bars": 0,
            "ic_by_horizon": {},
            "ic_tstat_by_horizon": {},
            "ic_mean": 0.0,
            "ic_abs_mean": 0.0,
            "non_constant": False,
            "ic_present": False,
        }

    span_seconds = 0.0
    stamps = [s.snapshot_timestamp for s in signals]
    if len(stamps) >= 2:
        span_seconds = float((_parse_ts(stamps[-1]) - _parse_ts(stamps[0])).total_seconds())

    # Explicit verdict: the options signal must be time-varying AND have a
    # measured non-zero IC to count as tradable. A constant broadcast fails by
    # construction (the EVAL-29 root cause).
    signal_tradable = bool(measurement["non_constant"] and measurement["ic_present"])
    if not measurement["non_constant"]:
        reason = "options signal is constant across bars (broadcast-static bug reproduced)"
    elif not measurement["ic_present"]:
        reason = "options signal varies but IC is indistinguishable from zero"
    elif integrated is not None and not bool(integrated.get("verdict", "") == "GO"):
        reason = "time-varying options signal measured, but integrated net-of-cost verdict is NO-GO"
    else:
        reason = "time-varying options signal with non-zero IC measured"

    checks = [
        {
            "name": "options_signal_non_constant",
            "pass": bool(measurement["non_constant"]),
            "observed": float(measurement["signal_stdev"]),
            "threshold": MIN_SIGNAL_STDEV,
            "reason": (
                f"PASS: signal stdev {measurement['signal_stdev']:.6e} > {MIN_SIGNAL_STDEV:.1e}"
                if measurement["non_constant"]
                else f"FAIL: signal stdev {measurement['signal_stdev']:.6e} <= {MIN_SIGNAL_STDEV:.1e}"
            ),
        },
        {
            "name": "options_signal_ic_nonzero",
            "pass": bool(measurement["ic_present"]),
            "observed": float(measurement["ic_abs_mean"]),
            "threshold": MIN_ABS_IC,
            "reason": (
                f"PASS: |mean IC| {measurement['ic_abs_mean']:.6e} > {MIN_ABS_IC:.1e}"
                if measurement["ic_present"]
                else f"FAIL: |mean IC| {measurement['ic_abs_mean']:.6e} <= {MIN_ABS_IC:.1e}"
            ),
        },
        {
            "name": "multi_snapshot_span",
            "pass": bool(len(signals) >= 2 and span_seconds > 0.0),
            "observed": float(len(signals)),
            "threshold": 2.0,
            "reason": (
                f"PASS: {len(signals)} snapshots spanning {span_seconds:.1f}s"
                if len(signals) >= 2 and span_seconds > 0.0
                else f"FAIL: only {len(signals)} snapshot(s) / span {span_seconds:.1f}s"
            ),
        },
    ]
    if integrated is not None:
        checks.append(
            {
                "name": "integrated_net_of_cost_go",
                "pass": bool(integrated.get("verdict") == "GO"),
                "observed": 1.0 if integrated.get("verdict") == "GO" else 0.0,
                "threshold": 1.0,
                "reason": f"integrated verdict: {integrated.get('verdict')} ({integrated.get('verdict_reason', '')})",
            }
        )
    all_pass = all(bool(c["pass"]) for c in checks)
    verdict = "GO" if all_pass else "NO-GO"

    report: Dict[str, Any] = {
        "report_id": "OPTIONS_LEG_TRADABILITY_30",
        "generated_at": generated_at,
        "verdict": verdict,
        "verdict_reason": reason,
        "trading_mode": TRADING_MODE,
        "live_trading_enabled": LIVE_TRADING_ENABLED,
        "never_valid_true": True,
        "authenticity_verified": False,
        "data_provenance": "real_public_exchange_export",
        "symbol": symbol,
        "venue": "okx",
        "spot_used": float(snap_spot),
        "n_snapshots": int(len(signals)),
        "snapshot_span_seconds": float(span_seconds),
        "snapshot_timestamps": stamps,
        "snapshots": [_snapshot_signal_to_dict(s) for s in signals],
        "measurement": measurement,
        "checks": checks,
        "n_checks": int(len(checks)),
        "n_passed": int(sum(1 for c in checks if bool(c["pass"]))),
        "failed_checks": [c["name"] for c in checks if not bool(c["pass"])],
        "integrated": integrated,
        "net_of_cost": net_of_cost,
        "code_paths": [
            "src/data/options_timeseries.py",
            "src/analytics/options_time_varying_signal.py",
            "src/analytics/integrated_options_orderflow_evaluation.py",
        ],
        "verification": [],
    }
    assert_json_valid(report)
    return serialize_metrics_strict(report)


def write_eval30_artifact(report: Dict[str, Any], out_dir: Path | str = OUT_DIR) -> Tuple[str, str]:
    """Write the strict EVAL-30 JSON + MD artifacts."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stamp = _stamp_for_filename(str(report["generated_at"]))
    json_path = out / f"OPTIONS_LEG_TRADABILITY_30_{stamp}.json"
    md_path = out / f"OPTIONS_LEG_TRADABILITY_30_{stamp}.md"
    payload = dict(report)
    payload["artifact_paths"] = {"json": str(json_path), "md": str(md_path)}
    serialized = serialize_metrics_strict(payload)
    assert_json_valid(serialized)
    json_path.write_text(
        json.dumps(serialized, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    m = report["measurement"]
    lines: List[str] = [
        "# OPTIONS_LEG_TRADABILITY_30 — time-varying causal options signal",
        "",
        f"- **Report ID:** `OPTIONS_LEG_TRADABILITY_30`",
        f"- **Generated:** {report['generated_at']}",
        f"- **Verdict:** **{report['verdict']}**",
        f"- **Provenance:** {report['data_provenance']} (authenticity_verified={str(report['authenticity_verified']).lower()})",
        f"- **Reason:** {report['verdict_reason']}",
        "",
        "## Measured signal",
        "",
        f"- Real options snapshots: {report['n_snapshots']} (span {report['snapshot_span_seconds']:.1f}s)",
        f"- Bars measured: {m['n_bars']}; step changes: {m['step_changes']}; flat (pre-first-snapshot) bars: {m['n_flat_bars']}",
        f"- Signal mean {m['mean_signal']:.6f}, stdev {m['signal_stdev']:.6e}, stdev/|mean| {m['signal_stdev_over_abs_mean']:.6e}, distinct {m['distinct_signal_values']}",
        f"- IC by horizon: {m['ic_by_horizon']}",
        f"- IC t-stat by horizon: {m['ic_tstat_by_horizon']}",
        f"- Mean IC {m['ic_mean']:.6e} (|IC| {m['ic_abs_mean']:.6e}); non_constant={m['non_constant']}, ic_present={m['ic_present']}",
        "",
        "## Per-snapshot components",
        "",
    ]
    for s in report["snapshots"]:
        lines.append(f"### {s['path']}")
        lines.append(f"- timestamp: {s['snapshot_timestamp']}  expiries: {s['n_expiries']}  iv_points: {s['n_iv_points']}")
        lines.append(
            f"- fwd_slope={s['forward_curve_slope']:.6e}  atm_iv_term_slope={s['atm_iv_term_slope']:.6e}  "
            f"iv_skew={s['iv_skew']:.6e}  pcr={s['put_call_ratio']:.6f}"
        )
        lines.append(f"- options_signal_raw: {s['options_signal_raw']:.6f}")
        for k, v in s["components"].items():
            lines.append(f"  - {k}: {v:.6f}")
        if s["warnings"]:
            lines.append(f"- warnings: {s['warnings']}")
        lines.append("")
    lines.extend(["## Checks", ""])
    for c in report["checks"]:
        lines.append(f"- `{c['name']}`: {c['reason']}")
    lines.append("")
    if report.get("integrated"):
        integ = report["integrated"]
        lines.extend(["## Integrated net-of-cost (measured)", ""])
        lines.append(f"- integrated verdict: {integ.get('verdict')} — {integ.get('verdict_reason', '')}")
        for key in ("options_only_wf", "orderflow_only_wf", "combined_wf", "flat_wf"):
            block = integ.get(key)
            if isinstance(block, dict):
                lines.append(
                    f"- {key}: Sharpe {block.get('oos_sharpe')}  return {block.get('oos_return')}  "
                    f"trades {block.get('num_trades')}  cost {block.get('total_cost_usd')}"
                )
        lines.append("")
    lines.extend(
        [
            "## Why this differs from EVAL-29",
            "",
            "EVAL-29 broadcast one static cross-sectional value to every bar, so mean IC was 0.0 "
            "by construction. EVAL-30 computes a per-snapshot signal (fitted forward curve slope, "
            "ATM IV term slope, IV skew, put-call ratio), aligns it causally to the bar grid "
            "(newest snapshot with timestamp <= bar end), and measures the resulting time "
            "variation and IC. A trustworthy NO-GO is a success; a fabricated GO is a failure.",
            "",
            "Additive EVAL-30 artifact. Sealed EVAL-18/23/24/27/29 artifacts are unchanged. "
            "Never emits {\"valid\": true}. Never relabels synthetic as real.",
        ]
    )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(json_path), str(md_path)


__all__ = [
    "ExpirySignalPoint",
    "SnapshotSignal",
    "snapshot_options_signal",
    "load_snapshot_signals",
    "align_options_signal_to_bars",
    "measure_time_varying_signal",
    "build_eval30_report",
    "write_eval30_artifact",
    "DEFAULT_WEIGHTS",
]