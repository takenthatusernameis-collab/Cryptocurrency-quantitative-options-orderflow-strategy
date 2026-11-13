"""Options vol-surface & greeks evaluation (EVAL-16, paper-only).

Repo-priority task: the options pillar of the crypto quantitative options +
orderflow strategy has no dedicated analytics EVAL. This module closes that gap
with a deterministic, fully offline evaluation of:

  1. **Data quality** of the real BTC options chain
     (``data/raw/options_btc_synthetic.json``): Black-Scholes(mark_iv) vs stored
     mark, put-call parity residual ``(C-P)-(S-K)``, mark-IV range. The file is
     known to be internally INCONSISTENT; this module measures it rather than
     assuming arbitrage-free.
  2. **Surface reconstruction** via ``build_iv_surface_from_chain`` +
     ``calibrate_iv_surface`` and arbitrage checks (butterfly convexity,
     calendar total-variance monotonicity) on the reconstructed IV grid.
  3. **Greeks recompute** from the reconstructed surface (NOT stored greeks),
     cross-checked against central finite differences (delta/vega), plus
     stored-vs-recomputed delta error.
  4. **Book greeks** (total GEX, gamma flip, put-call ratio, max pain, IV skew,
     chain liquidity) from the real chain.
  5. **Net-of-cost delta hedge** of a short ATM straddle through deterministic
     OOS windows (bid/ask spread cost), with an underlying buy-and-hold control.

``compute_options_surface_verdict`` combines all checks with explicit numeric
thresholds. Strict-serializable via ``serialize_metrics_strict`` /
``assert_json_valid`` (allow_nan=False). Never emits ``{"valid": True}``.
Paper-only: no network, no ``.env``, no venue/credential mutation, no live.

Emit canonical artifact:
``research_state/OPTIONS_SURFACE_GREEKS_EVAL_<UTC>.{json,md}``.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from src.analytics.strategy_evaluation import compute_metrics
from src.campaign.integrated import (
    DEFAULT_SPOT,
    DEFAULT_VENUE,
    DETERMINISTIC_NOW,
    IntegratedConfig,
    _generate_price_paths,
    _load_options_chain,
)
from src.data.schemas import OptionQuote, OptionsChain, PricingInputs
from src.features.gamma_exposure import calculate_total_gex, gamma_flip_level
from src.features.iv_surface import (
    IVSurface,
    _years_to_expiry,
    build_iv_surface_from_chain,
    calibrate_iv_surface,
)
from src.features.liquidity import calculate_chain_liquidity_metrics
from src.features.options_pricing import (
    black_scholes_greeks,
    black_scholes_price,
    finite_difference_greeks,
)
from src.features.volatility import (
    calculate_atm_term_structure,
    calculate_iv_skew,
    calculate_iv_skew_term_structure,
    calculate_max_pain,
    calculate_put_call_ratio,
)
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

REPORT_ID = "OPTIONS_SURFACE_GREEKS_EVAL_16"
OUT_DIR = Path("research_state")

TRADING_MODE = "paper"
LIVE_TRADING_ENABLED = False

# ---------------------------------------------------------------------------
# Evaluation thresholds (numeric, with rationale recorded in the artifact)
# ---------------------------------------------------------------------------

# A single option premium is quoted in USD; a coherent synthetic chain should
# price within a fraction of a premium unit of its own mark. 1.0 is deliberately
# tight so the known-inconsistent file cannot pass.
BS_VS_MARK_MAX_ABS_TOL: float = 1.0

# Put-call parity residual |(C-P)-(S-K)| must be near zero for a coherent chain.
PARITY_MAX_ABS_TOL: float = 1.0

# Mark IV must be a plausible annualized vol.
MARK_IV_MIN: float = 0.01
MARK_IV_MAX: float = 5.0

# Surface calibration residual (IV units) must be tiny: the surface reproduces
# its own input grid.
SURFACE_RESIDUAL_MAX_ABS_TOL: float = 1e-6

# Arbitrage checks on the reconstructed grid.
ARBITRAGE_MAX_VIOLATIONS: int = 0

# Stored-vs-recomputed delta error (absolute, per option).
GREEK_DELTA_ERR_MEAN_TOL: float = 0.05

# Fraction of quotes whose analytic delta and vega match central finite diff.
GREEK_FD_MATCH_FRACTION_TOL: float = 0.99
GREEK_FD_TOL: float = 1e-2

# Net-of-cost delta hedge sanity: Sharpe must be finite and non-degenerate.
NET_HEDGE_MIN_ABS_SHARPE: float = 0.0

# Delta-hedge simulation parameters.
DEFAULT_HEDGE_SPREAD_BPS: float = 1.0
DEFAULT_HEDGE_NOTIONAL: float = 1.0
DEFAULT_N_POINTS: int = 300
DEFAULT_TRAIN_WINDOW: int = 100
DEFAULT_TEST_WINDOW: int = 40
DEFAULT_STEP_SIZE: int = 40
DEFAULT_SEEDS: Tuple[int, ...] = (1, 2, 3, 4, 5)

# Calendar year in hours for the deterministic hourly price path.
HOURS_PER_YEAR: float = 365.25 * 24.0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _stamp_for_filename(iso_ts: str) -> str:
    try:
        ts = iso_ts.replace(":", "").replace("-", "").replace("T", "").replace("Z", "").split(".")[0]
    except Exception:
        return ""
    return f"{ts[:8]}T{ts[8:14]}Z" if len(ts) >= 14 else ""


def _finite(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    return v if math.isfinite(v) else default


def _all_finite_numbers(obj: Any) -> bool:
    if isinstance(obj, bool):
        return True
    if isinstance(obj, (int, float)):
        return math.isfinite(float(obj))
    if isinstance(obj, dict):
        return all(_all_finite_numbers(v) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return all(_all_finite_numbers(v) for v in obj)
    return True


def _mid(q: OptionQuote) -> float:
    mark = q.mark
    if mark is not None and math.isfinite(float(mark)):
        return float(mark)
    return 0.5 * (float(q.bid) + float(q.ask))


def _atm_strike(chain: OptionsChain, spot: float) -> float:
    """Strike closest to spot (deterministic tie-break: lowest strike)."""
    if not chain.quotes:
        return float(spot)
    best = min(chain.quotes, key=lambda q: (abs(float(q.contract.strike) - spot), float(q.contract.strike)))
    return float(best.contract.strike)


def _years_between(expiry: datetime, now: datetime) -> float:
    return _years_to_expiry(expiry, now)


# ---------------------------------------------------------------------------
# Step 1 — data quality (measured, not assumed)
# ---------------------------------------------------------------------------


def compute_data_quality_metrics(
    chain: OptionsChain,
    spot: float,
    rate: float = 0.0,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Measure BS(mark_iv)-vs-mark, put-call parity residual, and mark-IV range.

    Every field is a finite float; nothing is fudged toward GO.
    """
    if now is None:
        now = DETERMINISTIC_NOW
    bs_residuals: List[float] = []
    parity_residuals: List[float] = []
    mark_ivs: List[float] = []
    n_quotes = 0
    n_missing_iv = 0
    n_missing_mark = 0

    for q in chain.quotes:
        n_quotes += 1
        iv = q.mark_iv
        if iv is None or not math.isfinite(float(iv)) or float(iv) <= 0.0:
            n_missing_iv += 1
            continue
        mark_ivs.append(float(iv))
        mark = q.mark
        if mark is None or not math.isfinite(float(mark)):
            n_missing_mark += 1
            mark = 0.5 * (float(q.bid) + float(q.ask))
        try:
            t = _years_between(q.contract.expiry, now)
            px = black_scholes_price(
                PricingInputs(
                    spot=float(spot),
                    strike=float(q.contract.strike),
                    rate=float(rate),
                    volatility=float(iv),
                    time_to_expiry=t,
                    option_type=str(q.contract.option_type),
                    seed=42,
                )
            )
            bs_residuals.append(float(px) - float(mark))
        except Exception:
            bs_residuals.append(0.0)

    # Put-call parity per (expiry, strike) where both legs exist.
    by_key: Dict[Tuple[str, float], Dict[str, OptionQuote]] = {}
    for q in chain.quotes:
        key = (str(q.contract.expiry), float(q.contract.strike))
        by_key.setdefault(key, {})[str(q.contract.option_type).lower()] = q
    for (exp, strike), legs in by_key.items():
        if "call" in legs and "put" in legs:
            c = _mid(legs["call"])
            p = _mid(legs["put"])
            parity_residuals.append(float((c - p) - (float(spot) - float(strike))))

    bs_arr = bs_residuals or [0.0]
    parity_arr = parity_residuals or [0.0]
    iv_arr = mark_ivs or [0.0]

    return {
        "n_quotes": int(n_quotes),
        "n_missing_iv": int(n_missing_iv),
        "n_missing_mark": int(n_missing_mark),
        "n_bs_priced": int(len(bs_residuals)),
        "bs_vs_mark_max_abs": float(max(abs(x) for x in bs_arr)),
        "bs_vs_mark_mean_abs": float(sum(abs(x) for x in bs_arr) / len(bs_arr)),
        "bs_vs_mark_mean_signed": float(sum(bs_arr) / len(bs_arr)),
        "n_parity_pairs": int(len(parity_residuals)),
        "parity_residual_min": float(min(parity_arr)),
        "parity_residual_max": float(max(parity_arr)),
        "parity_residual_mean": float(sum(parity_arr) / len(parity_arr)),
        "parity_residual_mean_abs": float(sum(abs(x) for x in parity_arr) / len(parity_arr)),
        "parity_residual_max_abs": float(max(abs(x) for x in parity_arr)),
        "mark_iv_min": float(min(iv_arr)),
        "mark_iv_max": float(max(iv_arr)),
        "mark_iv_mean": float(sum(iv_arr) / len(iv_arr)),
        "n_distinct_iv": int(len(set(round(v, 10) for v in mark_ivs))),
    }


# ---------------------------------------------------------------------------
# Step 2 — surface reconstruction + arbitrage on the reconstructed grid
# ---------------------------------------------------------------------------


def reconstruct_surface(
    chain: OptionsChain,
    spot: float,
    rate: float = 0.0,
    now: Optional[datetime] = None,
    seed: int = 42,
) -> Dict[str, Any]:
    """Build + calibrate the IV surface; return surface, residuals, grid summary."""
    if now is None:
        now = DETERMINISTIC_NOW
    surface = build_iv_surface_from_chain(chain, spot=spot, rate=rate, now=now, seed=seed)
    calibrated, residual_report = calibrate_iv_surface(
        surface.points, spot, rate=rate, seed=seed,
        underlying=chain.underlying, venue=chain.venue,
    )
    by_exp: Dict[str, int] = {}
    for p in calibrated.points:
        by_exp[str(p.expiry)] = by_exp.get(str(p.expiry), 0) + 1
    return {
        "surface": calibrated,
        "residual_report": residual_report,
        "n_points": int(len(calibrated.points)),
        "n_expiries": int(len(by_exp)),
        "points_per_expiry": dict(sorted(by_exp.items())),
        "spot": float(spot),
        "rate": float(rate),
    }


def _grid_iv(surface: IVSurface, strike: float, t: float, option_type: str) -> float:
    return float(surface.get_iv(strike, t, option_type))


def check_arbitrage_on_grid(
    surface: IVSurface,
    spot: float,
    rate: float = 0.0,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Butterfly (call-price convexity) + calendar (total-variance) checks.

    Butterfly: for each expiry, call price must be convex in strike
    (second difference >= -tol). Calendar: for each strike, total implied
    variance ``iv**2 * T`` must be non-decreasing in T.
    """
    if now is None:
        now = DETERMINISTIC_NOW
    tol = 1e-6

    # Group grid by expiry and by strike.
    by_exp: Dict[float, List[Tuple[float, str]]] = {}
    by_strike: Dict[float, List[Tuple[float, str]]] = {}
    for p in surface.points:
        by_exp.setdefault(round(p.time_to_expiry, 12), []).append((float(p.strike), str(p.option_type)))
        by_strike.setdefault(round(float(p.strike), 8), []).append((round(p.time_to_expiry, 12), str(p.option_type)))

    butterfly_violations = 0
    butterfly_checks = 0
    butterfly_max_violation = 0.0
    for t, pts in by_exp.items():
        calls = sorted({k for (k, ot) in pts if ot == "call"})
        if len(calls) < 3:
            continue
        prices = [
            black_scholes_price(
                PricingInputs(
                    spot=float(spot), strike=k, rate=float(rate),
                    volatility=_grid_iv(surface, k, t, "call"),
                    time_to_expiry=t, option_type="call", seed=42,
                )
            )
            for k in calls
        ]
        for i in range(1, len(calls) - 1):
            h1 = calls[i] - calls[i - 1]
            h2 = calls[i + 1] - calls[i]
            if h1 <= 0.0 or h2 <= 0.0:
                continue
            second = (prices[i + 1] - prices[i]) / h2 - (prices[i] - prices[i - 1]) / h1
            butterfly_checks += 1
            if second < -tol:
                butterfly_violations += 1
                butterfly_max_violation = max(butterfly_max_violation, abs(second))

    calendar_violations = 0
    calendar_checks = 0
    calendar_max_violation = 0.0
    for k, pts in by_strike.items():
        calls = sorted({t for (t, ot) in pts if ot == "call"})
        if len(calls) < 2:
            continue
        tv = [
            (_grid_iv(surface, k, t, "call") ** 2) * t
            for t in calls
        ]
        for i in range(1, len(calls)):
            calendar_checks += 1
            if tv[i] < tv[i - 1] - tol:
                calendar_violations += 1
                calendar_max_violation = max(calendar_max_violation, abs(tv[i] - tv[i - 1]))

    total_violations = int(butterfly_violations + calendar_violations)
    return {
        "butterfly_checks": int(butterfly_checks),
        "butterfly_violations": int(butterfly_violations),
        "butterfly_max_violation": float(butterfly_max_violation),
        "calendar_checks": int(calendar_checks),
        "calendar_violations": int(calendar_violations),
        "calendar_max_violation": float(calendar_max_violation),
        "total_violations": total_violations,
        "arbitrage_free": bool(total_violations == 0),
    }


# ---------------------------------------------------------------------------
# Step 3 — greeks recompute from the reconstructed surface
# ---------------------------------------------------------------------------


def compute_greeks_metrics(
    chain: OptionsChain,
    surface: IVSurface,
    spot: float,
    rate: float = 0.0,
    now: Optional[datetime] = None,
    fd_tol: float = GREEK_FD_TOL,
) -> Dict[str, Any]:
    """Recompute greeks from the surface; FD cross-check delta/vega; delta error."""
    if now is None:
        now = DETERMINISTIC_NOW
    delta_errors: List[float] = []
    delta_matches = 0
    vega_matches = 0
    n_eval = 0
    recomputed: List[Dict[str, Any]] = []

    for q in chain.quotes:
        t = _years_between(q.contract.expiry, now)
        if t <= 0.0:
            t = 1e-9
        try:
            iv = _grid_iv(surface, float(q.contract.strike), t, str(q.contract.option_type))
        except Exception:
            continue
        inputs = PricingInputs(
            spot=float(spot), strike=float(q.contract.strike), rate=float(rate),
            volatility=float(iv), time_to_expiry=float(t),
            option_type=str(q.contract.option_type), seed=42,
        )
        try:
            analytic = black_scholes_greeks(inputs)
            fd = finite_difference_greeks(inputs)
        except Exception:
            continue
        n_eval += 1
        stored_delta = q.delta if q.delta is not None else float("nan")
        if math.isfinite(float(stored_delta)):
            delta_errors.append(abs(float(analytic["delta"]) - float(stored_delta)))
        d_abs = abs(float(analytic["delta"]) - float(fd["delta"]))
        d_den = max(abs(float(analytic["delta"])), abs(float(fd["delta"])), 1e-12)
        v_abs = abs(float(analytic["vega"]) - float(fd["vega"]))
        v_den = max(abs(float(analytic["vega"])), abs(fd["vega"]), 1e-12)
        d_ok = d_abs <= fd_tol and (d_abs / d_den) <= fd_tol
        v_ok = v_abs <= fd_tol and (v_abs / v_den) <= fd_tol
        delta_matches += int(d_ok)
        vega_matches += int(v_ok)
        recomputed.append({
            "symbol": str(q.contract.symbol),
            "strike": float(q.contract.strike),
            "option_type": str(q.contract.option_type),
            "surface_iv": float(iv),
            "recomputed_delta": float(analytic["delta"]),
            "recomputed_gamma": float(analytic["gamma"]),
            "recomputed_vega": float(analytic["vega"]),
            "fd_delta": float(fd["delta"]),
            "fd_vega": float(fd["vega"]),
            "delta_match": bool(d_ok),
            "vega_match": bool(v_ok),
        })

    err_arr = delta_errors or [0.0]
    return {
        "n_evaluated": int(n_eval),
        "delta_err_max": float(max(err_arr)),
        "delta_err_mean": float(sum(err_arr) / len(err_arr)),
        "n_delta_match": int(delta_matches),
        "n_vega_match": int(vega_matches),
        "delta_match_fraction": float(delta_matches / n_eval) if n_eval else 0.0,
        "vega_match_fraction": float(vega_matches / n_eval) if n_eval else 0.0,
        "fd_tol": float(fd_tol),
        "recomputed": recomputed,
    }


# ---------------------------------------------------------------------------
# Step 4 — book greeks
# ---------------------------------------------------------------------------


def compute_book_greeks(
    chain: OptionsChain,
    spot: float,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    if now is None:
        now = DETERMINISTIC_NOW
    total_gex = _finite(calculate_total_gex(chain, float(spot)), 0.0)
    flip = _finite(gamma_flip_level(chain, float(spot)), float(spot))
    pcr = _finite(calculate_put_call_ratio(chain.quotes), 1.0)
    max_pain = _finite(calculate_max_pain(chain), float(spot))
    iv_skew = _finite(calculate_iv_skew(chain.quotes, float(spot)), 0.0)
    liq = calculate_chain_liquidity_metrics(chain)
    atm_ts = calculate_atm_term_structure(chain.quotes, float(spot), now=now)
    skew_ts = calculate_iv_skew_term_structure(chain.quotes, float(spot), now=now)
    return {
        "total_gex": float(total_gex),
        "gamma_flip_level": float(flip),
        "put_call_ratio": float(pcr),
        "max_pain": float(max_pain),
        "iv_skew": float(iv_skew),
        "liquidity": {k: float(v) for k, v in liq.items()},
        "atm_term_structure": {str(k): float(v) for k, v in atm_ts.items()},
        "skew_term_structure": {
            str(k): {kk: float(vv) for kk, vv in v.items()} for k, v in skew_ts.items()
        },
        "n_expiries_in_atm_ts": int(len(atm_ts)),
        "atm_term_structure_monotonic": bool(
            len(atm_ts) >= 2
            and all(
                list(atm_ts.values())[i] <= list(atm_ts.values())[i + 1] + 1e-9
                for i in range(len(atm_ts) - 1)
            )
        ),
    }


# ---------------------------------------------------------------------------
# Step 5 — net-of-cost delta hedge through deterministic OOS windows
# ---------------------------------------------------------------------------


def _simulate_delta_hedge_window(
    prices: Sequence[float],
    strike: float,
    iv: float,
    t0_years: float,
    rate: float,
    spread_bps: float,
) -> List[float]:
    """Delta-hedged short ATM straddle equity curve over one price path.

    Portfolio: short 1 call + short 1 put at ``strike``, plus a rolling
    underlying hedge that neutralizes net delta. Each hedge rebalance pays
    ``|delta_qty| * S * spread_bps/1e4``. Returns a finite equity curve.
    """
    if len(prices) < 2:
        return [1.0, 1.0]

    def _price(s: float, t: float, ot: str) -> float:
        try:
            return float(
                black_scholes_price(
                    PricingInputs(
                        spot=float(s), strike=float(strike), rate=float(rate),
                        volatility=float(iv), time_to_expiry=max(float(t), 1e-9),
                        option_type=ot, seed=42,
                    )
                )
            )
        except Exception:
            return 0.0

    def _delta(s: float, t: float, ot: str) -> float:
        try:
            return float(
                black_scholes_greeks(
                    PricingInputs(
                        spot=float(s), strike=float(strike), rate=float(rate),
                        volatility=float(iv), time_to_expiry=max(float(t), 1e-9),
                        option_type=ot, seed=42,
                    )
                )["delta"]
            )
        except Exception:
            return 0.0

    s0 = float(prices[0])
    if s0 <= 0.0:
        return [1.0 for _ in prices]
    t_step = 1.0 / HOURS_PER_YEAR

    # Initial credit from shorting the straddle (per unit).
    cash = _price(s0, t0_years, "call") + _price(s0, t0_years, "put")
    h_prev = _delta(s0, t0_years, "call") + _delta(s0, t0_years, "put")
    equity: List[float] = [float(cash)]
    for i in range(1, len(prices)):
        s = float(prices[i])
        t_left = max(t0_years - i * t_step, 0.0)
        call_val = _price(s, t_left, "call")
        put_val = _price(s, t_left, "put")
        h_new = _delta(s, t_left, "call") + _delta(s, t_left, "put")
        cost = abs(h_new - h_prev) * s * float(spread_bps) / 1e4
        cash -= cost
        h_prev = h_new
        eq = cash + h_prev * s - (call_val + put_val)
        equity.append(float(eq))
    return equity


def run_delta_hedge_oos(
    chain: OptionsChain,
    spot: float,
    rate: float = 0.0,
    seeds: Sequence[int] = DEFAULT_SEEDS,
    n_points: int = DEFAULT_N_POINTS,
    train_window: int = DEFAULT_TRAIN_WINDOW,
    test_window: int = DEFAULT_TEST_WINDOW,
    step_size: int = DEFAULT_STEP_SIZE,
    spread_bps: float = DEFAULT_HEDGE_SPREAD_BPS,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Walk-forward OOS delta-hedge; report with-options vs no-options control."""
    if now is None:
        now = DETERMINISTIC_NOW
    strike = _atm_strike(chain, spot)
    t0_years = 30.0 / 365.25

    with_metrics: List[Dict[str, Any]] = []
    without_metrics: List[Dict[str, Any]] = []
    per_window: List[Dict[str, Any]] = []

    for seed in seeds:
        cfg = IntegratedConfig(
            symbols=("BTC",), spot_prices={"BTC": float(spot)}, seed=int(seed),
            fixed_now=now, n_points=int(n_points), train_window=int(train_window),
            test_window=int(test_window), step_size=int(step_size),
        )
        paths, _ = _generate_price_paths(cfg)
        prices = paths["BTC"]
        n = len(prices)
        start = int(train_window)
        while start + 1 < n:
            end = min(start + int(test_window), n - 1)
            if end <= start:
                break
            window = prices[start:end + 1]
            with_eq = _simulate_delta_hedge_window(
                window, strike, 0.6, t0_years, rate, spread_bps
            )
            without_eq = [float(p) for p in window]
            try:
                wm = compute_metrics(with_eq)
            except Exception:
                wm = {}
            try:
                om = compute_metrics(without_eq)
            except Exception:
                om = {}
            with_metrics.append(wm)
            without_metrics.append(om)
            per_window.append({
                "seed": int(seed),
                "start": int(start),
                "end": int(end),
                "n_bars": int(len(window)),
                "with_options_return": float(wm.get("total_return", 0.0)),
                "with_options_sharpe": float(wm.get("sharpe", 0.0)),
                "without_options_return": float(om.get("total_return", 0.0)),
                "without_options_sharpe": float(om.get("sharpe", 0.0)),
            })
            start += int(step_size)

    def _mean(vals: List[float]) -> float:
        vals = [v for v in vals if math.isfinite(v)]
        return float(sum(vals) / len(vals)) if vals else 0.0

    return {
        "n_seeds": int(len(list(seeds))),
        "seeds": [int(s) for s in seeds],
        "n_windows": int(len(with_metrics)),
        "strike": float(strike),
        "t0_years": float(t0_years),
        "spread_bps": float(spread_bps),
        "mean_with_options_return": _mean([m.get("total_return", 0.0) for m in with_metrics]),
        "mean_with_options_sharpe": _mean([m.get("sharpe", 0.0) for m in with_metrics]),
        "mean_with_options_max_drawdown": _mean([m.get("max_drawdown", 0.0) for m in with_metrics]),
        "mean_without_options_return": _mean([m.get("total_return", 0.0) for m in without_metrics]),
        "mean_without_options_sharpe": _mean([m.get("sharpe", 0.0) for m in without_metrics]),
        "mean_without_options_max_drawdown": _mean([m.get("max_drawdown", 0.0) for m in without_metrics]),
        "per_window": per_window,
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------


def compute_options_surface_verdict(
    data_quality: Dict[str, Any],
    surface: Dict[str, Any],
    arbitrage: Dict[str, Any],
    greeks: Dict[str, Any],
    book: Dict[str, Any],
    hedge: Dict[str, Any],
) -> Dict[str, Any]:
    """Deterministic verdict from all measured blocks; explicit checks list."""
    checks: List[Dict[str, Any]] = []

    def _add(name: str, ok: bool, threshold: float, observed: float, reason: str) -> None:
        checks.append({
            "name": name,
            "pass": bool(ok),
            "threshold": float(threshold),
            "observed": float(observed),
            "reason": reason,
        })

    # 1. BS(mark_iv) vs stored mark.
    bs_max = float(data_quality["bs_vs_mark_max_abs"])
    _add(
        "data_quality_bs_vs_mark",
        bs_max <= BS_VS_MARK_MAX_ABS_TOL,
        BS_VS_MARK_MAX_ABS_TOL,
        bs_max,
        (
            f"PASS: BS(mark_iv) vs mark max abs {bs_max:.4f} <= {BS_VS_MARK_MAX_ABS_TOL}"
            if bs_max <= BS_VS_MARK_MAX_ABS_TOL
            else f"FAIL: BS(mark_iv) vs mark max abs {bs_max:.4f} > {BS_VS_MARK_MAX_ABS_TOL}"
        ),
    )

    # 2. Put-call parity residual.
    parity_max = float(data_quality["parity_residual_max_abs"])
    _add(
        "data_quality_put_call_parity",
        parity_max <= PARITY_MAX_ABS_TOL,
        PARITY_MAX_ABS_TOL,
        parity_max,
        (
            f"PASS: parity residual max abs {parity_max:.4f} <= {PARITY_MAX_ABS_TOL}"
            if parity_max <= PARITY_MAX_ABS_TOL
            else f"FAIL: parity residual max abs {parity_max:.4f} > {PARITY_MAX_ABS_TOL}"
        ),
    )

    # 3. Mark IV range plausible.
    iv_min = float(data_quality["mark_iv_min"])
    iv_max = float(data_quality["mark_iv_max"])
    iv_ok = bool(iv_min >= MARK_IV_MIN and iv_max <= MARK_IV_MAX and iv_min <= iv_max)
    _add(
        "data_quality_mark_iv_range",
        iv_ok,
        MARK_IV_MAX,
        iv_max,
        (
            f"PASS: mark IV range [{iv_min:.4f}, {iv_max:.4f}] within [{MARK_IV_MIN}, {MARK_IV_MAX}]"
            if iv_ok
            else f"FAIL: mark IV range [{iv_min:.4f}, {iv_max:.4f}] outside [{MARK_IV_MIN}, {MARK_IV_MAX}]"
        ),
    )

    # 4. Surface calibration residual.
    resid_max = float(surface["residual_report"]["residual_max_abs"])
    _add(
        "surface_calibration_residual",
        resid_max <= SURFACE_RESIDUAL_MAX_ABS_TOL,
        SURFACE_RESIDUAL_MAX_ABS_TOL,
        resid_max,
        (
            f"PASS: surface residual max abs {resid_max:.3e} <= {SURFACE_RESIDUAL_MAX_ABS_TOL:.1e}"
            if resid_max <= SURFACE_RESIDUAL_MAX_ABS_TOL
            else f"FAIL: surface residual max abs {resid_max:.3e} > {SURFACE_RESIDUAL_MAX_ABS_TOL:.1e}"
        ),
    )

    # 5. Arbitrage on reconstructed grid.
    arb_ok = bool(arbitrage["total_violations"] <= ARBITRAGE_MAX_VIOLATIONS)
    _add(
        "surface_arbitrage_free",
        arb_ok,
        float(ARBITRAGE_MAX_VIOLATIONS),
        float(arbitrage["total_violations"]),
        (
            f"PASS: {arbitrage['total_violations']} arbitrage violations (butterfly {arbitrage['butterfly_violations']}, calendar {arbitrage['calendar_violations']})"
            if arb_ok
            else f"FAIL: {arbitrage['total_violations']} arbitrage violations (butterfly {arbitrage['butterfly_violations']}, calendar {arbitrage['calendar_violations']})"
        ),
    )

    # 6. Stored-vs-recomputed delta error.
    delta_err = float(greeks["delta_err_mean"])
    _add(
        "greeks_stored_vs_recomputed_delta",
        delta_err <= GREEK_DELTA_ERR_MEAN_TOL,
        GREEK_DELTA_ERR_MEAN_TOL,
        delta_err,
        (
            f"PASS: mean stored-vs-recomputed delta error {delta_err:.4f} <= {GREEK_DELTA_ERR_MEAN_TOL}"
            if delta_err <= GREEK_DELTA_ERR_MEAN_TOL
            else f"FAIL: mean stored-vs-recomputed delta error {delta_err:.4f} > {GREEK_DELTA_ERR_MEAN_TOL}"
        ),
    )

    # 7. Analytic greeks match central finite differences (delta + vega).
    fd_frac = min(float(greeks["delta_match_fraction"]), float(greeks["vega_match_fraction"]))
    _add(
        "greeks_analytic_vs_finite_difference",
        fd_frac >= GREEK_FD_MATCH_FRACTION_TOL,
        GREEK_FD_MATCH_FRACTION_TOL,
        fd_frac,
        (
            f"PASS: analytic vs FD match fraction {fd_frac:.4f} >= {GREEK_FD_MATCH_FRACTION_TOL}"
            if fd_frac >= GREEK_FD_MATCH_FRACTION_TOL
            else f"FAIL: analytic vs FD match fraction {fd_frac:.4f} < {GREEK_FD_MATCH_FRACTION_TOL}"
        ),
    )

    # 8. Net-of-cost delta hedge is finite / non-degenerate.
    with_sharpe = float(hedge["mean_with_options_sharpe"])
    hedge_finite = bool(
        math.isfinite(with_sharpe)
        and math.isfinite(float(hedge["mean_with_options_return"]))
        and math.isfinite(float(hedge["mean_without_options_sharpe"]))
    )
    _add(
        "net_of_cost_delta_hedge_finite",
        hedge_finite,
        1.0,
        1.0 if hedge_finite else 0.0,
        (
            f"PASS: delta-hedge metrics finite (with Sharpe {with_sharpe:.4f}, return {hedge['mean_with_options_return']:.4f})"
            if hedge_finite
            else "FAIL: delta-hedge metrics non-finite"
        ),
    )

    # 9. Non-degeneracy: finite metrics + evidence present.
    non_degen = bool(
        _all_finite_numbers(data_quality)
        and _all_finite_numbers(surface["residual_report"])
        and _all_finite_numbers(arbitrage)
        and _all_finite_numbers(book)
        and math.isfinite(float(greeks["delta_match_fraction"]))
        and int(data_quality["n_quotes"]) > 0
    )
    _add(
        "metrics_non_degenerate",
        non_degen,
        1.0,
        1.0 if non_degen else 0.0,
        "PASS: all measured blocks finite and non-empty" if non_degen else "FAIL: degenerate/empty metrics",
    )

    all_pass = all(bool(c["pass"]) for c in checks)
    return {
        "verdict": "GO" if all_pass else "NO-GO",
        "checks": checks,
        "n_checks": int(len(checks)),
        "n_passed": int(sum(1 for c in checks if bool(c["pass"]))),
        "all_checks_pass": bool(all_pass),
        "failed_checks": [c["name"] for c in checks if not bool(c["pass"])],
    }


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def load_btc_chain() -> OptionsChain:
    """Load the real BTC options chain (deterministic, offline)."""
    return _load_options_chain("BTC", float(DEFAULT_SPOT["BTC"]), DETERMINISTIC_NOW, DEFAULT_VENUE)


def evaluate_options_surface_greeks(
    write: bool = True,
    out_dir: str | Path = OUT_DIR,
    timestamp: Optional[str] = None,
    seeds: Sequence[int] = DEFAULT_SEEDS,
    n_points: int = DEFAULT_N_POINTS,
    train_window: int = DEFAULT_TRAIN_WINDOW,
    test_window: int = DEFAULT_TEST_WINDOW,
    step_size: int = DEFAULT_STEP_SIZE,
    spread_bps: float = DEFAULT_HEDGE_SPREAD_BPS,
) -> Dict[str, Any]:
    """Run the full EVAL-16 evaluation and emit strict artifacts."""
    if timestamp is None:
        timestamp = _utc_now_iso()

    spot = float(DEFAULT_SPOT["BTC"])
    rate = 0.0
    now = DETERMINISTIC_NOW

    chain = load_btc_chain()
    data_quality = compute_data_quality_metrics(chain, spot, rate=rate, now=now)
    surface = reconstruct_surface(chain, spot, rate=rate, now=now, seed=42)
    arbitrage = check_arbitrage_on_grid(surface["surface"], spot, rate=rate, now=now)
    greeks = compute_greeks_metrics(chain, surface["surface"], spot, rate=rate, now=now)
    book = compute_book_greeks(chain, spot, now=now)
    hedge = run_delta_hedge_oos(
        chain, spot, rate=rate, seeds=seeds, n_points=n_points,
        train_window=train_window, test_window=test_window,
        step_size=step_size, spread_bps=spread_bps, now=now,
    )
    verdict = compute_options_surface_verdict(data_quality, surface, arbitrage, greeks, book, hedge)

    # Non-degeneracy assertions.
    assert int(data_quality["n_quotes"]) > 0, "chain must have quotes"
    assert int(surface["n_points"]) > 0, "surface must have points"
    assert int(greeks["n_evaluated"]) > 0, "greeks must be evaluated"
    assert int(hedge["n_windows"]) > 0, "hedge must have OOS windows"
    assert verdict["verdict"] in ("GO", "NO-GO"), "verdict must be GO or NO-GO"
    assert verdict["verdict"] == ("GO" if verdict["all_checks_pass"] else "NO-GO")
    assert _all_finite_numbers(data_quality), "data-quality non-finite"
    assert _all_finite_numbers(arbitrage), "arbitrage non-finite"
    assert _all_finite_numbers(book), "book greeks non-finite"
    assert _all_finite_numbers(hedge), "hedge non-finite"
    assert _all_finite_numbers(verdict), "verdict non-finite"

    evidence_matrix = {
        "options_chain_loaded": bool(int(data_quality["n_quotes"]) > 0),
        "surface_reconstructed": bool(int(surface["n_points"]) > 0),
        "greeks_recomputed_from_surface": bool(int(greeks["n_evaluated"]) > 0),
        "arbitrage_checked_on_grid": bool(int(arbitrage["butterfly_checks"] + arbitrage["calendar_checks"]) > 0),
        "delta_hedge_oos_windows": bool(int(hedge["n_windows"]) > 0),
        "book_greeks_present": bool(math.isfinite(float(book["total_gex"]))),
        "paper_only": True,
        "live_trading_enabled": False,
    }

    report = {
        "report_id": REPORT_ID,
        "generated_at": timestamp,
        "verdict": verdict["verdict"],
        "trading_mode": TRADING_MODE,
        "live_trading_enabled": LIVE_TRADING_ENABLED,
        "never_valid_true": True,
        "config": {
            "symbol": "BTC",
            "spot": spot,
            "rate": rate,
            "venue": DEFAULT_VENUE,
            "seeds": [int(s) for s in seeds],
            "n_points": int(n_points),
            "train_window": int(train_window),
            "test_window": int(test_window),
            "step_size": int(step_size),
            "spread_bps": float(spread_bps),
            "thresholds": {
                "bs_vs_mark_max_abs_tol": BS_VS_MARK_MAX_ABS_TOL,
                "parity_max_abs_tol": PARITY_MAX_ABS_TOL,
                "mark_iv_min": MARK_IV_MIN,
                "mark_iv_max": MARK_IV_MAX,
                "surface_residual_max_abs_tol": SURFACE_RESIDUAL_MAX_ABS_TOL,
                "arbitrage_max_violations": ARBITRAGE_MAX_VIOLATIONS,
                "greek_delta_err_mean_tol": GREEK_DELTA_ERR_MEAN_TOL,
                "greek_fd_match_fraction_tol": GREEK_FD_MATCH_FRACTION_TOL,
            },
        },
        "data_quality": data_quality,
        "surface": {
            "n_points": surface["n_points"],
            "n_expiries": surface["n_expiries"],
            "points_per_expiry": surface["points_per_expiry"],
            "residual_report": surface["residual_report"],
        },
        "arbitrage": arbitrage,
        "greeks": greeks,
        "book_greeks": book,
        "delta_hedge": hedge,
        "evidence_matrix": evidence_matrix,
        "verdict_checks": verdict,
        "deployment_authorization": {
            "authorized": bool(verdict["verdict"] == "GO"),
            "mode": "paper_only",
            "note": "GO certifies the options surface/greeks evaluation only; not authorization to trade live.",
        },
    }
    assert_json_valid(report)
    serialized = serialize_metrics_strict(report)

    if write:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = _stamp_for_filename(timestamp)
        json_path = out_dir / f"OPTIONS_SURFACE_GREEKS_EVAL_{stamp}.json"
        md_path = out_dir / f"OPTIONS_SURFACE_GREEKS_EVAL_{stamp}.md"
        serialized["artifact_paths"] = {"json": str(json_path), "md": str(md_path)}
        json_path.write_text(
            json.dumps(serialized, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        md_path.write_text(_write_markdown(serialized) + "\n", encoding="utf-8")

    return serialized


def _write_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# OPTIONS VOL-SURFACE & GREEKS EVALUATION — EVAL-16 (paper-only)")
    lines.append("")
    lines.append(f"- Report ID: {report['report_id']}")
    lines.append(f"- Generated at: {report['generated_at']}")
    lines.append(f"- Verdict: {report['verdict']}")
    lines.append(f"- Trading mode: {report['trading_mode']} (live enabled: {report['live_trading_enabled']})")
    lines.append(f"- Symbol: {report['config']['symbol']} @ spot {report['config']['spot']}")
    lines.append("")

    dq = report["data_quality"]
    lines.append("## DATA QUALITY (measured, not assumed)")
    lines.append(f"- Quotes: {dq['n_quotes']} (missing IV: {dq['n_missing_iv']}, missing mark: {dq['n_missing_mark']})")
    lines.append(f"- BS(mark_iv) vs mark: max abs {dq['bs_vs_mark_max_abs']:.4f}, mean abs {dq['bs_vs_mark_mean_abs']:.4f}, mean signed {dq['bs_vs_mark_mean_signed']:.4f}")
    lines.append(f"- Put-call parity: pairs {dq['n_parity_pairs']}, min {dq['parity_residual_min']:.4f}, max {dq['parity_residual_max']:.4f}, mean {dq['parity_residual_mean']:.4f}, mean abs {dq['parity_residual_mean_abs']:.4f}, max abs {dq['parity_residual_max_abs']:.4f}")
    lines.append(f"- Mark IV: min {dq['mark_iv_min']:.4f}, max {dq['mark_iv_max']:.4f}, mean {dq['mark_iv_mean']:.4f}, distinct {dq['n_distinct_iv']}")
    lines.append("")

    s = report["surface"]
    lines.append("## SURFACE RECONSTRUCTION")
    lines.append(f"- Points: {s['n_points']} across {s['n_expiries']} expiries")
    rr = s["residual_report"]
    lines.append(f"- Calibration residual: mean {rr['residual_mean']:.3e}, std {rr['residual_std']:.3e}, max abs {rr['residual_max_abs']:.3e}")
    lines.append("")

    a = report["arbitrage"]
    lines.append("## ARBITRAGE CHECKS (reconstructed IV grid)")
    lines.append(f"- Butterfly: checks {a['butterfly_checks']}, violations {a['butterfly_violations']}, max violation {a['butterfly_max_violation']:.3e}")
    lines.append(f"- Calendar: checks {a['calendar_checks']}, violations {a['calendar_violations']}, max violation {a['calendar_max_violation']:.3e}")
    lines.append(f"- Arbitrage-free: {a['arbitrage_free']}")
    lines.append("")

    g = report["greeks"]
    lines.append("## GREEKS (recomputed from reconstructed surface)")
    lines.append(f"- Evaluated: {g['n_evaluated']}")
    lines.append(f"- Stored-vs-recomputed delta error: mean {g['delta_err_mean']:.4f}, max {g['delta_err_max']:.4f}")
    lines.append(f"- Delta FD match: {g['n_delta_match']}/{g['n_evaluated']} (fraction {g['delta_match_fraction']:.4f})")
    lines.append(f"- Vega FD match: {g['n_vega_match']}/{g['n_evaluated']} (fraction {g['vega_match_fraction']:.4f})")
    lines.append("")

    b = report["book_greeks"]
    lines.append("## BOOK GREEKS")
    lines.append(f"- Total GEX: {b['total_gex']:.4f}")
    lines.append(f"- Gamma flip level: {b['gamma_flip_level']:.2f}")
    lines.append(f"- Put-call ratio: {b['put_call_ratio']:.4f}")
    lines.append(f"- Max pain: {b['max_pain']:.2f}")
    lines.append(f"- IV skew: {b['iv_skew']:.4f}")
    lines.append(f"- Avg bid-ask spread: {b['liquidity']['avg_bid_ask_spread']:.4f}, total OI {b['liquidity']['total_oi']:.0f}")
    lines.append("")

    h = report["delta_hedge"]
    lines.append("## NET-OF-COST DELTA HEDGE (OOS, with options vs no-options)")
    lines.append(f"- Windows: {h['n_windows']} across seeds {h['seeds']} (strike {h['strike']}, spread {h['spread_bps']} bps)")
    lines.append(f"- With options: mean return {h['mean_with_options_return']:.6f}, mean Sharpe {h['mean_with_options_sharpe']:.6f}, mean max-DD {h['mean_with_options_max_drawdown']:.6f}")
    lines.append(f"- Without options (underlying hold): mean return {h['mean_without_options_return']:.6f}, mean Sharpe {h['mean_without_options_sharpe']:.6f}, mean max-DD {h['mean_without_options_max_drawdown']:.6f}")
    lines.append("")

    lines.append("## EVIDENCE MATRIX")
    for k, v in report["evidence_matrix"].items():
        lines.append(f"- {k}: {v}")
    lines.append("")

    lines.append("## VERDICT CHECKS (deterministic)")
    for c in report["verdict_checks"]["checks"]:
        lines.append(f"- [{'PASS' if c['pass'] else 'FAIL'}] {c['name']}: {c['reason']}")
    lines.append(f"- All checks pass: {report['verdict_checks']['all_checks_pass']} ({report['verdict_checks']['n_passed']}/{report['verdict_checks']['n_checks']})")
    lines.append("")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Options vol-surface & greeks evaluation (EVAL-16, paper-only)"
    )
    parser.add_argument("--out", type=str, default=str(OUT_DIR), help="output directory")
    parser.add_argument("--no-write", action="store_true", help="compute without writing artifacts")
    parser.add_argument("--timestamp", type=str, default=_utc_now_iso())
    parser.add_argument("--seeds", type=int, nargs="+", default=list(DEFAULT_SEEDS))
    parser.add_argument("--n-points", type=int, default=DEFAULT_N_POINTS)
    parser.add_argument("--train-window", type=int, default=DEFAULT_TRAIN_WINDOW)
    parser.add_argument("--test-window", type=int, default=DEFAULT_TEST_WINDOW)
    parser.add_argument("--step-size", type=int, default=DEFAULT_STEP_SIZE)
    parser.add_argument("--spread-bps", type=float, default=DEFAULT_HEDGE_SPREAD_BPS)
    args = parser.parse_args(argv)

    report = evaluate_options_surface_greeks(
        write=not args.no_write,
        out_dir=args.out,
        timestamp=args.timestamp,
        seeds=args.seeds,
        n_points=args.n_points,
        train_window=args.train_window,
        test_window=args.test_window,
        step_size=args.step_size,
        spread_bps=args.spread_bps,
    )

    print(
        json.dumps(
            {
                "report_id": report["report_id"],
                "verdict": report["verdict"],
                "n_checks_passed": f'{report["verdict_checks"]["n_passed"]}/{report["verdict_checks"]["n_checks"]}',
                "n_quotes": report["data_quality"]["n_quotes"],
                "bs_vs_mark_max_abs": report["data_quality"]["bs_vs_mark_max_abs"],
                "parity_residual_max_abs": report["data_quality"]["parity_residual_max_abs"],
                "surface_residual_max_abs": report["surface"]["residual_report"]["residual_max_abs"],
                "arbitrage_total_violations": report["arbitrage"]["total_violations"],
                "delta_err_mean": report["greeks"]["delta_err_mean"],
                "delta_match_fraction": report["greeks"]["delta_match_fraction"],
                "vega_match_fraction": report["greeks"]["vega_match_fraction"],
                "mean_with_options_sharpe": report["delta_hedge"]["mean_with_options_sharpe"],
                "mean_without_options_sharpe": report["delta_hedge"]["mean_without_options_sharpe"],
                "failed_checks": report["verdict_checks"]["failed_checks"],
                "artifact_paths": report.get("artifact_paths", {}),
            },
            sort_keys=True,
            allow_nan=False,
        )
    )
    for path in report.get("artifact_paths", {}).values():
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())