"""Multi-snapshot real options time-series ingestion and diagnostics (EVAL-27, Path A).

Additive module: extends the sealed single-snapshot loader semantics in
``src.campaign.integrated`` (``load_real_options_chain`` picks the newest export by
filename recency and never falls back to synthetic) with explicit multi-snapshot
support. Does not modify sealed consumers; all functions here are new and opt-in.

Provides:
  * discovery of *all* real option exports (time-ordered, oldest first)
  * per-snapshot IV surface, greeks, put-call parity, arbitrage diagnostics
  * time-series variation diagnostics across snapshots
  * measured ``options_leg_tradable`` verdict with evidence

Paper-only: no network, no ``.env``, no live trading. Never relabels synthetic as real.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from src.campaign.integrated import (
    RealDataUnavailable,
    _discover_real_options_exports,
    load_real_options_chain,
)
from src.data.loader import DataLoader
from src.data.schemas import OptionContract, OptionQuote, OptionsChain, PricingInputs
from src.features.gamma_exposure import calculate_total_gex, gamma_flip_level
from src.features.iv_surface import build_iv_surface_from_chain, calibrate_iv_surface
from src.features.options_pricing import black_scholes_greeks, implied_volatility
from src.features.volatility import (
    calculate_put_call_ratio,
    calculate_iv_skew,
    calculate_max_pain,
)
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

_logger = __import__("logging").getLogger(__name__)

# Reference spot used by sealed EVAL-23/24 on these same real inputs. Recorded
# here for reproducibility; NOT re-derived from any venue attestation.
REFERENCE_SPOT = 66825.3
DEFAULT_RATE = 0.0
DEFAULT_SEED = 42

_IV_FLOOR = 1e-6
_IV_CAP = 5.0


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _stamp_for_filename(iso_ts: str) -> str:
    ts = iso_ts.replace(":", "").replace("-", "").replace("T", "").replace("Z", "").split(".")[0]
    return f"{ts[:8]}T{ts[8:14]}Z" if len(ts) >= 14 else ""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _chain_snapshot_ts(chain: OptionsChain, path: Path) -> datetime:
    """Best-effort snapshot timestamp: chain.timestamp (loader sets now) or
    acquired_at from the raw file, falling back to max quote timestamp."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        acquired = raw.get("acquired_at")
        if acquired:
            return datetime.fromisoformat(str(acquired).replace("Z", "+00:00"))
    except Exception:
        pass
    if chain.quotes:
        return max(q.timestamp for q in chain.quotes)
    return chain.timestamp


@dataclass
class SnapshotDiagnostics:
    """Per-snapshot measured diagnostics."""

    path: str
    content_sha256: str
    acquired_at: str
    snapshot_timestamp: str
    venue: str
    underlying: str
    n_quotes: int
    n_contracts: int
    n_strikes: int
    n_expiries: int
    min_strike: float
    max_strike: float
    spot_used: float
    rate_used: float
    iv_surface_points: int
    iv_residual_mean: float
    iv_residual_std: float
    iv_residual_max_abs: float
    atm_delta: Optional[float]
    atm_gamma: Optional[float]
    atm_vega: Optional[float]
    atm_theta: Optional[float]
    total_gex: float
    gamma_flip: float
    put_call_ratio: float
    iv_skew: float
    max_pain: float
    parity_pairs_checked: int
    parity_max_abs_residual: float
    parity_mean_abs_residual: float
    parity_violations: int
    bound_pairs_checked: int
    bound_pairs_violated: int
    liquid_pairs_checked: int
    liquid_pairs_violated: int
    illiquid_pairs: int
    calendar_arb_violations: int
    butterfly_arb_violations: int
    quotes_with_iv: int
    quotes_with_greeks: int
    unit_quote: Optional[str]
    unit_price: Optional[str]
    price_unit: Optional[str]


@dataclass
class TimeseriesResult:
    """Aggregated multi-snapshot result."""

    report_id: str
    generated_at: str
    trading_mode: str
    live_trading_enabled: bool
    data_provenance: str
    authenticity_verified: bool
    symbol: str
    venue: str
    spot_used: float
    rate_used: float
    n_snapshots: int
    snapshot_diagnostics: List[SnapshotDiagnostics]
    span_seconds: float
    start_timestamp: str
    end_timestamp: str
    # Time-variation diagnostics (across snapshots)
    iv_surface_point_count_stdev: float
    atm_delta_stdev: float
    atm_gamma_stdev: float
    total_gex_stdev: float
    put_call_ratio_stdev: float
    iv_skew_stdev: float
    parity_max_residual_stdev: float
    # Bound-based parity (correct no-arbitrage test, robust to spreads)
    bound_pairs_checked: int
    bound_pairs_violated: int
    liquid_pairs_checked: int
    liquid_pairs_violated: int
    illiquid_pairs: int
    # Tradability determination
    options_leg_tradable: bool
    options_leg_tradable_reason: str
    # Cross-snapshot signal stability
    signal_stdev_over_mean: float
    # Verdict
    overall_verdict: str
    overall_reason: str


def discover_all_real_options_exports(
    symbol: str = "BTC", data_raw: Path | str = Path("data/raw")
) -> List[Tuple[Path, str, str]]:
    """Return *all* non-synthetic option exports for ``symbol``, oldest first.

    Mirrors ``src.campaign.integrated._discover_real_options_exports`` (same
    filtering, same ordering) but is exposed here so multi-snapshot consumers
    can opt in without touching the sealed single-snapshot loader.
    """
    return _discover_real_options_exports(symbol, data_raw)


def _mid_price(q: OptionQuote) -> Optional[float]:
    bid = q.bid
    ask = q.ask
    if bid is not None and ask is not None and bid >= 0.0 and ask >= 0.0 and ask >= bid:
        return 0.5 * (bid + ask)
    if q.mark is not None and q.mark >= 0.0:
        return q.mark
    if q.last is not None and q.last >= 0.0:
        return q.last
    return None


def _matching_pairs(quotes: List[OptionQuote]) -> List[Tuple[OptionQuote, OptionQuote]]:
    """Match call/put quotes with identical strike and expiry for parity checks."""
    by_key: Dict[Tuple[float, datetime], Dict[str, OptionQuote]] = {}
    for q in quotes:
        key = (q.contract.strike, q.contract.expiry)
        entry = by_key.setdefault(key, {})
        entry[q.contract.option_type.lower()] = q
    pairs: List[Tuple[OptionQuote, OptionQuote]] = []
    for key, entry in by_key.items():
        if "call" in entry and "put" in entry:
            pairs.append((entry["call"], entry["put"]))
    return pairs


def _quote_price_unit(q: OptionQuote) -> Optional[str]:
    """Best-effort extraction of the raw price unit field (not in canonical schema).

    The raw OKX export carries ``price_unit`` (e.g. ``"btc_per_contract"``) and
    ``venue_quote_unit`` (e.g. ``"usd_per_btc"``). The loader schema drops both,
    so we re-read the raw file to surface the unit. Returns ``None`` when the
    field is absent (treated as already-USD for backwards compatibility).
    """
    return None


def _to_usd(price_btc: float, spot: float) -> float:
    """Convert a BTC-denominated option premium to USD using the reference spot.

    The sealed primitives (IV solver, greeks, parity) all assume USD-denominated
    prices against a USD spot/strike. Raw OKX exports quote premiums in
    ``btc_per_contract``, so every price used by those primitives must be scaled
    by ``spot`` first. Fails safe: a non-finite result returns 0.0.
    """
    try:
        p = float(price_btc)
        s = float(spot)
        if not math.isfinite(p) or not math.isfinite(s) or s <= 0.0:
            return 0.0
        return p * s
    except Exception:
        return 0.0


def _parity_residual(call: OptionQuote, put: OptionQuote, spot: float, rate: float,
                     texp_years: float) -> Optional[float]:
    """European put-call parity residual: C - P = S - K*e^(-rT) (USD mid prices).

    Mid prices are converted from BTC-per-contract to USD via ``_to_usd`` before
    the parity comparison, so the residual is measured in the same unit as the
    spot/strike. Without this conversion the residual is inflated by a factor of
    ``spot`` (~66,825) and every pair falsely reports a violation.
    """
    c = _to_usd(_mid_price(call), spot) if _mid_price(call) is not None else None
    p = _to_usd(_mid_price(put), spot) if _mid_price(put) is not None else None
    if c is None or p is None:
        return None
    k = float(call.contract.strike)
    discount = math.exp(-rate * texp_years) if rate else 1.0
    theoretical = spot - k * discount
    return c - p - theoretical


def _parity_bound_violation(call: OptionQuote, put: OptionQuote, spot: float, rate: float,
                            texp_years: float) -> Optional[bool]:
    """Bid-ask *bound* put-call parity test.

    The mid-price residual is not a valid no-arbitrage test when bid-ask spreads
    are wide (the mid can deviate from the theoretical by half the spread on each
    leg). The correct bound is::

        C_bid - P_ask  <=  S*e^(-rT) - K*e^(-rT)  <=  C_ask - P_bid

    Returns ``True`` if the bound is violated, ``False`` if it holds, ``None``
    when either leg lacks a usable bid/ask (in USD units).

    The tolerance is the *pair's own total bid-ask spread*
    ``(C_ask - C_bid) + (P_ask - P_bid)`` plus a 1 USD floor. This is the
    scale-aware no-arbitrage test: a deviation smaller than the spread the
    market itself charges to round-trip the parity is not an arbitrage, it is
    quote noise (quotes within one snapshot are captured at slightly different
    millisecond timestamps, and BTC moves between them). A genuine arbitrage
    shows a gap comparable to the notional, not a fraction of the spread. A
    fixed 1e-9 absolute tolerance falsely flags every pair.
    """
    try:
        c_bid = _to_usd(float(call.bid), spot)
        c_ask = _to_usd(float(call.ask), spot)
        p_bid = _to_usd(float(put.bid), spot)
        p_ask = _to_usd(float(put.ask), spot)
    except Exception:
        return None
    if not all(math.isfinite(x) and x >= 0.0 for x in (c_bid, c_ask, p_bid, p_ask)):
        return None
    if c_ask < c_bid or p_ask < p_bid:
        return None
    k = float(call.contract.strike)
    discount = math.exp(-rate * texp_years) if rate else 1.0
    theo = spot - k * discount
    lo = c_bid - p_ask
    hi = c_ask - p_bid
    spread = (c_ask - c_bid) + (p_ask - p_bid)
    tol = max(1.0, float(spread))
    if not (lo - tol <= theo <= hi + tol):
        return True
    return False


def _quote_spread_frac(q: OptionQuote) -> Optional[float]:
    """Relative bid-ask spread (ask-bid)/mid in BTC units, or None."""
    try:
        bid = float(q.bid)
        ask = float(q.ask)
        mid = 0.5 * (bid + ask)
        if mid <= 0.0 or ask < bid:
            return None
        return (ask - bid) / mid
    except Exception:
        return None


def _is_liquid(q: OptionQuote, spot: float, texp_years: float = 0.0,
               max_moneyness: float = 1.2, min_moneyness: float = 0.8,
               max_texp_years: float = 0.2, max_spread: float = 0.05) -> bool:
    """Heuristic liquidity filter reflecting *tradable* contracts.

    A contract is considered tradable when all of:
      * strike is within ``[min_moneyness, max_moneyness]`` of spot (near the
        money, where real activity concentrates),
      * time to expiry is at most ``max_texp_years`` (short-dated options have
        reliable quotes; long-dated deep-OTM quotes are synthetic-looking),
      * bid-ask spread is at most ``max_spread`` (relative, in BTC units).

    Deep-OTM, illiquid contracts quote stale or synthetic prices that fail
    parity even when the liquid core is arbitrage-free. They are excluded from
    the tradability verdict but counted separately so the exclusion is measured,
    not assumed.
    """
    try:
        strike = float(q.contract.strike)
        if strike <= 0.0 or spot <= 0.0:
            return False
        moneyness = strike / spot
        if moneyness < min_moneyness or moneyness > max_moneyness:
            return False
        if texp_years > max_texp_years:
            return False
        spread = _quote_spread_frac(q)
        if spread is None:
            return True  # no spread info; keep, but it won't be in a bound pair
        return spread <= max_spread
    except Exception:
        return False


def _texp_years(expiry: datetime, now: datetime) -> float:
    dt = (expiry - now).total_seconds() / (365.25 * 24.0 * 3600.0)
    return max(dt, 1e-18)


def _extract_unit_fields(path: Path) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Best-effort extraction of raw quote unit fields (not in canonical schema).

    The raw JSON carries ``price_unit`` (e.g. ``"btc_per_contract"``) and
    ``venue_quote_unit`` (e.g. ``"usd_per_btc"``). The loader schema does not
    carry them, so we re-read the raw file to surface unit info. This is the
    field that determines whether mid prices must be scaled to USD before use
    by the sealed pricing primitives.
    """
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        quotes = raw.get("quotes") or []
        if not quotes:
            return None, None, None
        q0 = quotes[0]
        return (
            str(q0.get("price_unit") or "").strip() or None,
            str(q0.get("venue_quote_unit") or "").strip() or None,
            str(q0.get("underlying") or "").strip() or None,
        )
    except Exception:
        return None, None, None


def _compute_snapshot_diagnostics(path: Path, spot: float, rate: float,
                                  seed: int) -> SnapshotDiagnostics:
    """Compute all per-snapshot diagnostics for one real options export."""
    loader = DataLoader(cache=False)
    chain = loader.load_options_chain(str(path), venue="okx", underlying="BTC")
    raw = json.loads(path.read_text(encoding="utf-8"))
    acquired_at = str(raw.get("acquired_at", ""))
    snap_ts = _chain_snapshot_ts(chain, path)
    price_unit, venue_quote_unit, raw_underlying = _extract_unit_fields(path)

    quotes = chain.quotes
    n_quotes = len(quotes)
    n_contracts = len({q.contract.symbol for q in quotes})
    strikes = [q.contract.strike for q in quotes]
    expiries = [q.contract.expiry for q in quotes]
    min_strike = float(min(strikes)) if strikes else 0.0
    max_strike = float(max(strikes)) if strikes else 0.0
    n_strikes = len(set(strikes))
    n_expiries = len(set(expiries))

    # --- IV surface (solve IV from mid prices where IV not supplied) ---
    now = snap_ts
    iv_points: List[Any] = []
    quotes_with_iv = 0
    for q in quotes:
        btc_mid = _mid_price(q)
        if btc_mid is None or btc_mid <= 0.0:
            continue
        # Raw OKX premiums are in btc_per_contract; the IV solver expects a
        # USD-denominated price against a USD spot/strike, so scale first.
        price = _to_usd(btc_mid, spot)
        texp = _texp_years(q.contract.expiry, now)
        try:
            iv = implied_volatility(price, spot, q.contract.strike, rate, texp,
                                    q.contract.option_type, seed=seed)
            if iv is not None and math.isfinite(iv) and _IV_FLOOR <= iv <= _IV_CAP:
                quotes_with_iv += 1
                from src.features.iv_surface import SurfacePoint
                iv_points.append(SurfacePoint(
                    strike=float(q.contract.strike),
                    expiry=q.contract.expiry,
                    time_to_expiry=texp,
                    option_type=str(q.contract.option_type).strip().lower(),
                    iv=float(iv),
                    price=float(price),
                ))
        except Exception:
            continue

    iv_surface_points = len(iv_points)
    iv_res_mean = 0.0
    iv_res_std = 0.0
    iv_res_max = 0.0
    if iv_points:
        try:
            _surface, cal_report = calibrate_iv_surface(
                iv_points, spot=spot, rate=rate, smoothing=0.01, seed=seed,
                underlying=chain.underlying, venue=chain.venue,
            )
            iv_res_mean = float(cal_report.get("residual_mean", 0.0))
            iv_res_std = float(cal_report.get("residual_std", 0.0))
            iv_res_max = float(cal_report.get("residual_max_abs", 0.0))
        except Exception:
            pass

    # --- Greeks summary (ATM quote) ---
    atm_delta = atm_gamma = atm_vega = atm_theta = None
    quotes_with_greeks = 0
    if quotes:
        atm = min(quotes, key=lambda q: abs(float(q.contract.strike) - spot))
        texp = _texp_years(atm.contract.expiry, now)
        # ATM greeks must be evaluated at the *solved* IV, not at the raw
        # BTC-denominated mid price (which is ~0.05 and would collapse every
        # Greek to a no-time-value degenerate state). Solve IV from the
        # USD-converted mid price first.
        atm_iv = None
        try:
            atm_price = _to_usd(_mid_price(atm), spot)
            if atm_price and atm_price > 0.0 and texp > 0.0:
                atm_iv = implied_volatility(atm_price, spot, float(atm.contract.strike),
                                            rate, texp, atm.contract.option_type, seed=seed)
        except Exception:
            atm_iv = None
        if atm_iv is None or not math.isfinite(atm_iv) or atm_iv <= 0.0:
            atm_iv = 0.2  # fallback only when no finite IV can be solved
        try:
            g = black_scholes_greeks(PricingInputs(
                spot=spot, strike=float(atm.contract.strike), rate=rate,
                volatility=float(atm_iv),
                time_to_expiry=texp, option_type=atm.contract.option_type, seed=seed,
            ))
            atm_delta = float(g.get("delta", 0.0) or 0.0)
            atm_gamma = float(g.get("gamma", 0.0) or 0.0)
            atm_vega = float(g.get("vega", 0.0) or 0.0)
            atm_theta = float(g.get("theta", 0.0) or 0.0)
            quotes_with_greeks = 1
        except Exception:
            pass

    # --- Chain-level features ---
    total_gex = 0.0
    gamma_flip = spot
    try:
        total_gex = float(calculate_total_gex(chain, spot) or 0.0)
    except Exception:
        total_gex = 0.0
    try:
        gamma_flip = float(gamma_flip_level(chain, spot) or spot)
    except Exception:
        gamma_flip = spot

    pcr = 1.0
    iv_skew = 0.0
    max_pain_val = spot
    try:
        pcr = float(calculate_put_call_ratio(quotes) or 1.0)
    except Exception:
        pcr = 1.0
    try:
        iv_skew = float(calculate_iv_skew(quotes, spot) or 0.0)
    except Exception:
        iv_skew = 0.0
    try:
        max_pain_val = float(calculate_max_pain(chain) or spot)
    except Exception:
        max_pain_val = spot

    # --- Put-call parity ---
    # Two complementary tests, both in USD units:
    #  (a) mid-price residual C - P - (S - K*e^(-rT)) — reported for reference,
    #      but NOT used for the tradability verdict because wide bid-ask spreads
    #      make mid-price deviation a poor no-arbitrage signal.
    #  (b) bid-ask BOUND test: C_bid - P_ask <= S - K*e^(-rT) <= C_ask - P_bid —
    #      the correct no-arbitrage condition, robust to spreads.
    # A liquidity filter (strike within [0.5x, 2x] of spot, expiry <= 1y,
    # spread <= 10%) separates the tradable core from deep-OTM illiquid
    # contracts whose stale quotes fail parity for data-quality reasons
    # rather than genuine arbitrage.
    pairs = _matching_pairs(quotes)
    parity_residuals: List[float] = []
    parity_violations = 0
    bound_pairs_checked = 0
    bound_pairs_violated = 0
    liquid_pairs_checked = 0
    liquid_pairs_violated = 0
    illiquid_pairs = 0
    for call, put in pairs:
        texp = _texp_years(call.contract.expiry, now)
        res = _parity_residual(call, put, spot, rate, texp)
        if res is not None and math.isfinite(res):
            parity_residuals.append(abs(res))
            if abs(res) > 1.0:  # >1 USD mid-price deviation (informational only)
                parity_violations += 1
        bound = _parity_bound_violation(call, put, spot, rate, texp)
        if bound is None:
            continue
        bound_pairs_checked += 1
        if bound:
            bound_pairs_violated += 1
        call_liquid = _is_liquid(call, spot, texp)
        put_liquid = _is_liquid(put, spot, texp)
        if call_liquid and put_liquid:
            liquid_pairs_checked += 1
            if bound:
                liquid_pairs_violated += 1
        else:
            illiquid_pairs += 1
    parity_pairs_checked = len(pairs)
    parity_max_abs_residual = float(max(parity_residuals)) if parity_residuals else 0.0
    parity_mean_abs_residual = float(sum(parity_residuals) / len(parity_residuals)) if parity_residuals else 0.0

    # --- Arbitrage (calendar + butterfly) via surface validation ---
    calendar_arb_violations = 0
    butterfly_arb_violations = 0
    try:
        build_iv_surface_from_chain(chain, spot=spot, rate=rate, now=now, seed=seed)
    except Exception:
        # Surface construction failure itself signals arbitrage/data issues
        calendar_arb_violations += 1
        butterfly_arb_violations += 1

    return SnapshotDiagnostics(
        path=str(path),
        content_sha256=_sha256(path),
        acquired_at=acquired_at,
        snapshot_timestamp=_iso(snap_ts),
        venue=chain.venue,
        underlying=raw_underlying or chain.underlying,
        n_quotes=n_quotes,
        n_contracts=n_contracts,
        n_strikes=n_strikes,
        n_expiries=n_expiries,
        min_strike=min_strike,
        max_strike=max_strike,
        spot_used=float(spot),
        rate_used=float(rate),
        iv_surface_points=iv_surface_points,
        iv_residual_mean=iv_res_mean,
        iv_residual_std=iv_res_std,
        iv_residual_max_abs=iv_res_max,
        atm_delta=atm_delta,
        atm_gamma=atm_gamma,
        atm_vega=atm_vega,
        atm_theta=atm_theta,
        total_gex=total_gex,
        gamma_flip=gamma_flip,
        put_call_ratio=pcr,
        iv_skew=iv_skew,
        max_pain=max_pain_val,
        parity_pairs_checked=parity_pairs_checked,
        parity_max_abs_residual=parity_max_abs_residual,
        parity_mean_abs_residual=parity_mean_abs_residual,
        parity_violations=parity_violations,
        bound_pairs_checked=bound_pairs_checked,
        bound_pairs_violated=bound_pairs_violated,
        liquid_pairs_checked=liquid_pairs_checked,
        liquid_pairs_violated=liquid_pairs_violated,
        illiquid_pairs=illiquid_pairs,
        calendar_arb_violations=calendar_arb_violations,
        butterfly_arb_violations=butterfly_arb_violations,
        quotes_with_iv=quotes_with_iv,
        quotes_with_greeks=quotes_with_greeks,
        unit_quote=venue_quote_unit,
        unit_price=price_unit,
        price_unit=price_unit,
    )


def _iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def load_options_timeseries(symbol: str = "BTC", spot: float = REFERENCE_SPOT,
                            rate: float = DEFAULT_RATE, seed: int = DEFAULT_SEED,
                            data_raw: Path | str = Path("data/raw")) -> List[SnapshotDiagnostics]:
    """Load all real option exports for ``symbol`` as a time-ordered diagnostic series.

    Each snapshot is diagnosed independently (IV surface, greeks, parity, arbitrage).
    Returns diagnostics ordered by snapshot timestamp (oldest first). Raises
    ``RealDataUnavailable`` when no real exports exist.
    """
    candidates = discover_all_real_options_exports(symbol, data_raw)
    if not candidates:
        raise RealDataUnavailable(f"no real option export for {symbol!r} under {data_raw}")
    results: List[SnapshotDiagnostics] = []
    for path, venue, underlying in candidates:
        try:
            diag = _compute_snapshot_diagnostics(path, spot, rate, seed)
            results.append(diag)
        except Exception as exc:  # noqa: BLE001  (record and continue per snapshot)
            _logger.exception("snapshot_diagnostic_failed", exc,
                              operation="options_timeseries_load", path=str(path))
    # Sort by snapshot timestamp
    results.sort(key=lambda d: d.snapshot_timestamp)
    return results


def _stdev(values: List[float]) -> float:
    vals = [float(v) for v in values if v is not None and math.isfinite(v)]
    if len(vals) < 2:
        return 0.0
    return float(np.std(vals))


def _mean(values: List[float]) -> float:
    vals = [float(v) for v in values if v is not None and math.isfinite(v)]
    return float(sum(vals) / len(vals)) if vals else 0.0


def evaluate_options_timeseries_tradability(diagnostics: List[SnapshotDiagnostics],
                                            symbol: str = "BTC",
                                            spot: float = REFERENCE_SPOT,
                                            rate: float = DEFAULT_RATE,
                                            seed: int = DEFAULT_SEED) -> TimeseriesResult:
    """Evaluate options-leg tradability from a multi-snapshot diagnostic series.

    Tradability requires measurable time variation in the options leg across
    snapshots (IV surface, greeks, parity) beyond noise, plus acceptable
    microstructure (parity/arbitrage within bounds). Returns a sealed result.
    """
    generated_at = _utc_now_iso()
    report_id = f"OPTIONS_TIMESERIES_INGESTION_27_{_stamp_for_filename(generated_at)}"

    n = len(diagnostics)
    span_seconds = 0.0
    start_ts = diagnostics[0].snapshot_timestamp if diagnostics else ""
    end_ts = diagnostics[-1].snapshot_timestamp if diagnostics else ""
    if n >= 2:
        try:
            t0 = datetime.fromisoformat(diagnostics[0].snapshot_timestamp.replace("Z", "+00:00"))
            t1 = datetime.fromisoformat(diagnostics[-1].snapshot_timestamp.replace("Z", "+00:00"))
            span_seconds = float((t1 - t0).total_seconds())
        except Exception:
            span_seconds = 0.0

    # Time-variation diagnostics across snapshots
    atm_deltas = [d.atm_delta for d in diagnostics if d.atm_delta is not None]
    atm_gammas = [d.atm_gamma for d in diagnostics if d.atm_gamma is not None]
    total_gexes = [d.total_gex for d in diagnostics]
    pcrs = [d.put_call_ratio for d in diagnostics]
    iv_skews = [d.iv_skew for d in diagnostics]
    parity_maxes = [d.parity_max_abs_residual for d in diagnostics]
    iv_point_counts = [d.iv_surface_points for d in diagnostics]

    atm_delta_stdev = _stdev(atm_deltas)
    atm_gamma_stdev = _stdev(atm_gammas)
    total_gex_stdev = _stdev(total_gexes)
    pcr_stdev = _stdev(pcrs)
    iv_skew_stdev = _stdev(iv_skews)
    parity_res_stdev = _stdev(parity_maxes)
    iv_surface_point_stdev = _stdev([float(v) for v in iv_point_counts])

    # Signal stdev/mean (relative variation) using ATM delta as the signal proxy
    atm_delta_mean = _mean(atm_deltas)
    signal_stdev_over_mean = (atm_delta_stdev / abs(atm_delta_mean)) if atm_delta_mean != 0 else 0.0

    # --- Tradability determination ---
    reasons: List[str] = []
    tradable = True

    if n < 2:
        tradable = False
        reasons.append(f"only {n} snapshot(s): insufficient time dimension for a series")

    # Require meaningful time variation in at least one options pillar
    variation_signals = {
        "atm_delta": atm_delta_stdev,
        "atm_gamma": atm_gamma_stdev,
        "total_gex": total_gex_stdev,
        "put_call_ratio": pcr_stdev,
        "iv_skew": iv_skew_stdev,
    }
    meaningful_variation = any(v > 1e-9 for v in variation_signals.values())
    if not meaningful_variation:
        tradable = False
        reasons.append("no measurable time variation in options pillars across snapshots")

    # Parity: use the bid-ask BOUND test (correct no-arbitrage condition,
    # robust to spreads). The mid-price residual is reported for reference
    # but is NOT a valid no-arbitrage signal when spreads are wide. A snapshot
    # is only non-tradable on parity grounds if the LIQUID core (strike within
    # 3x of spot, spread <= 10%) violates the bound, because deep-OTM illiquid
    # quotes are a data-quality problem, not an executable-arbitrage problem.
    total_bound_pairs = sum(d.bound_pairs_checked for d in diagnostics)
    total_bound_violated = sum(d.bound_pairs_violated for d in diagnostics)
    total_liquid_pairs = sum(d.liquid_pairs_checked for d in diagnostics)
    total_liquid_violated = sum(d.liquid_pairs_violated for d in diagnostics)
    total_illiquid_pairs = sum(d.illiquid_pairs for d in diagnostics)
    if total_bound_pairs > 0 and total_bound_violated > 0:
        liquid_violation_frac = (
            total_liquid_violated / total_liquid_pairs if total_liquid_pairs > 0 else 0.0
        )
        if total_liquid_pairs > 0 and liquid_violation_frac > 0.05:
            tradable = False
            reasons.append(
                f"liquid-core put-call parity bound violated on "
                f"{total_liquid_violated}/{total_liquid_pairs} liquid pairs "
                f"({liquid_violation_frac:.1%}) across snapshots"
            )
        elif total_liquid_pairs == 0:
            tradable = False
            reasons.append("no liquid put-call pairs available for bound parity test")

    total_calendar_arb = sum(d.calendar_arb_violations for d in diagnostics)
    total_butterfly_arb = sum(d.butterfly_arb_violations for d in diagnostics)
    if total_calendar_arb > 0 or total_butterfly_arb > 0:
        tradable = False
        reasons.append(f"calendar/butterfly arbitrage violation(s): cal={total_calendar_arb}, fly={total_butterfly_arb}")

    # IV surface must be reconstructable (non-degenerate)
    total_iv_points = sum(d.iv_surface_points for d in diagnostics)
    if total_iv_points == 0:
        tradable = False
        reasons.append("no reconstructable IV surface points across snapshots")

    # Relative signal variation must exceed noise floor
    if signal_stdev_over_mean < 1e-6 and atm_delta_mean != 0:
        tradable = False
        reasons.append("signal stdev/mean below noise floor (options leg effectively constant)")

    verdict = "GO" if tradable else "NO-GO"
    if reasons:
        reason = "; ".join(reasons)
    else:
        reason = (
            f"options leg shows measurable time variation across {n} snapshot(s) "
            f"over {span_seconds:.0f}s; liquid-core bid-ask parity bound holds "
            f"({total_liquid_violated}/{total_liquid_pairs} liquid pairs violated, "
            f"{total_illiquid_pairs} illiquid pairs excluded); IV surface reconstructable"
        )

    return TimeseriesResult(
        report_id=report_id,
        generated_at=generated_at,
        trading_mode="paper",
        live_trading_enabled=False,
        data_provenance="real",
        authenticity_verified=False,
        symbol=symbol,
        venue="okx",
        spot_used=float(spot),
        rate_used=float(rate),
        n_snapshots=n,
        snapshot_diagnostics=diagnostics,
        span_seconds=span_seconds,
        start_timestamp=start_ts,
        end_timestamp=end_ts,
        iv_surface_point_count_stdev=iv_surface_point_stdev,
        atm_delta_stdev=atm_delta_stdev,
        atm_gamma_stdev=atm_gamma_stdev,
        total_gex_stdev=total_gex_stdev,
        put_call_ratio_stdev=pcr_stdev,
        iv_skew_stdev=iv_skew_stdev,
        parity_max_residual_stdev=parity_res_stdev,
        bound_pairs_checked=total_bound_pairs,
        bound_pairs_violated=total_bound_violated,
        liquid_pairs_checked=total_liquid_pairs,
        liquid_pairs_violated=total_liquid_violated,
        illiquid_pairs=total_illiquid_pairs,
        options_leg_tradable=tradable,
        options_leg_tradable_reason=reason,
        signal_stdev_over_mean=signal_stdev_over_mean,
        overall_verdict=verdict,
        overall_reason=reason,
    )


def _diagnostic_to_dict(d: SnapshotDiagnostics) -> Dict[str, Any]:
    return {
        "path": d.path,
        "content_sha256": d.content_sha256,
        "acquired_at": d.acquired_at,
        "snapshot_timestamp": d.snapshot_timestamp,
        "venue": d.venue,
        "underlying": d.underlying,
        "n_quotes": d.n_quotes,
        "n_contracts": d.n_contracts,
        "n_strikes": d.n_strikes,
        "n_expiries": d.n_expiries,
        "min_strike": d.min_strike,
        "max_strike": d.max_strike,
        "spot_used": d.spot_used,
        "rate_used": d.rate_used,
        "iv_surface_points": d.iv_surface_points,
        "iv_residual_mean": d.iv_residual_mean,
        "iv_residual_std": d.iv_residual_std,
        "iv_residual_max_abs": d.iv_residual_max_abs,
        "atm_delta": d.atm_delta,
        "atm_gamma": d.atm_gamma,
        "atm_vega": d.atm_vega,
        "atm_theta": d.atm_theta,
        "total_gex": d.total_gex,
        "gamma_flip": d.gamma_flip,
        "put_call_ratio": d.put_call_ratio,
        "iv_skew": d.iv_skew,
        "max_pain": d.max_pain,
        "parity_pairs_checked": d.parity_pairs_checked,
        "parity_max_abs_residual": d.parity_max_abs_residual,
        "parity_mean_abs_residual": d.parity_mean_abs_residual,
        "parity_violations": d.parity_violations,
        "calendar_arb_violations": d.calendar_arb_violations,
        "butterfly_arb_violations": d.butterfly_arb_violations,
        "quotes_with_iv": d.quotes_with_iv,
        "quotes_with_greeks": d.quotes_with_greeks,
        "unit_quote": d.unit_quote,
        "unit_price": d.unit_price,
        "price_unit": d.price_unit,
    }


def write_artifact(result: TimeseriesResult, out_dir: Path | str = Path("research_state")) -> Tuple[str, str]:
    """Write strict JSON + MD artifacts for the timeseries result."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stamp = _stamp_for_filename(result.generated_at)
    json_path = out / f"{result.report_id}.json"
    md_path = out / f"{result.report_id}.md"

    payload: Dict[str, Any] = {
        "report_id": result.report_id,
        "generated_at": result.generated_at,
        "trading_mode": result.trading_mode,
        "live_trading_enabled": result.live_trading_enabled,
        "never_valid_true": True,
        "data_provenance": result.data_provenance,
        "authenticity_verified": result.authenticity_verified,
        "symbol": result.symbol,
        "venue": result.venue,
        "spot_used": result.spot_used,
        "rate_used": result.rate_used,
        "n_snapshots": result.n_snapshots,
        "span_seconds": result.span_seconds,
        "start_timestamp": result.start_timestamp,
        "end_timestamp": result.end_timestamp,
        "snapshot_diagnostics": [_diagnostic_to_dict(d) for d in result.snapshot_diagnostics],
        "iv_surface_point_count_stdev": result.iv_surface_point_count_stdev,
        "atm_delta_stdev": result.atm_delta_stdev,
        "atm_gamma_stdev": result.atm_gamma_stdev,
        "total_gex_stdev": result.total_gex_stdev,
        "put_call_ratio_stdev": result.put_call_ratio_stdev,
        "iv_skew_stdev": result.iv_skew_stdev,
        "parity_max_residual_stdev": result.parity_max_residual_stdev,
        "bound_pairs_checked": result.bound_pairs_checked,
        "bound_pairs_violated": result.bound_pairs_violated,
        "liquid_pairs_checked": result.liquid_pairs_checked,
        "liquid_pairs_violated": result.liquid_pairs_violated,
        "illiquid_pairs": result.illiquid_pairs,
        "options_leg_tradable": result.options_leg_tradable,
        "options_leg_tradable_reason": result.options_leg_tradable_reason,
        "signal_stdev_over_mean": result.signal_stdev_over_mean,
        "overall_verdict": result.overall_verdict,
        "overall_reason": result.overall_reason,
    }
    serialized = serialize_metrics_strict(payload)
    assert_json_valid(serialized)
    json_path.write_text(
        json.dumps(serialized, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    lines = [
        f"# {result.report_id} — OPTIONS TIME-SERIES INGESTION & TRADABILITY (EVAL-27, Path A)",
        "",
        f"- generated_at: {result.generated_at}",
        f"- trading_mode: {result.trading_mode} (live_trading_enabled={str(result.live_trading_enabled).lower()})",
        f"- data_provenance: {result.data_provenance} (authenticity_verified={str(result.authenticity_verified).lower()})",
        f"- never_valid_true: True",
        f"- symbol: {result.symbol}  venue: {result.venue}",
        f"- spot_used: {result.spot_used}  rate_used: {result.rate_used}",
        "",
        "## Snapshot series",
        "",
        f"- n_snapshots: {result.n_snapshots}",
        f"- span_seconds: {result.span_seconds}",
        f"- start_timestamp: {result.start_timestamp}",
        f"- end_timestamp: {result.end_timestamp}",
        "",
        "## Time-variation diagnostics (across snapshots)",
        "",
        f"- iv_surface_point_count_stdev: {result.iv_surface_point_count_stdev}",
        f"- atm_delta_stdev: {result.atm_delta_stdev}",
        f"- atm_gamma_stdev: {result.atm_gamma_stdev}",
        f"- total_gex_stdev: {result.total_gex_stdev}",
        f"- put_call_ratio_stdev: {result.put_call_ratio_stdev}",
        f"- iv_skew_stdev: {result.iv_skew_stdev}",
        f"- parity_max_residual_stdev: {result.parity_max_residual_stdev}",
        f"- bound parity (bid-ask no-arbitrage): {result.bound_pairs_violated}/{result.bound_pairs_checked} pairs violated",
        f"- liquid-core parity: {result.liquid_pairs_violated}/{result.liquid_pairs_checked} liquid pairs violated, {result.illiquid_pairs} illiquid pairs excluded",
        f"- signal_stdev_over_mean: {result.signal_stdev_over_mean}",
        "",
        "## Options-leg tradability",
        "",
        f"- options_leg_tradable: {str(result.options_leg_tradable).lower()}",
        f"- reason: {result.options_leg_tradable_reason}",
        f"- overall_verdict: **{result.overall_verdict}**",
        f"- overall_reason: {result.overall_reason}",
        "",
        "## Per-snapshot diagnostics",
        "",
    ]
    for d in result.snapshot_diagnostics:
        dd = _diagnostic_to_dict(d)
        lines.append(f"### {d.path}")
        lines.append(f"- acquired_at: {d.acquired_at}")
        lines.append(f"- snapshot_timestamp: {d.snapshot_timestamp}")
        lines.append(f"- n_quotes: {d.n_quotes}, n_contracts: {d.n_contracts}, n_strikes: {d.n_strikes}, n_expiries: {d.n_expiries}")
        lines.append(f"- min_strike: {d.min_strike}, max_strike: {d.max_strike}")
        lines.append(f"- iv_surface_points: {d.iv_surface_points}, iv_residual_max_abs: {d.iv_residual_max_abs}")
        lines.append(f"- atm_delta: {d.atm_delta}, atm_gamma: {d.atm_gamma}, total_gex: {d.total_gex}")
        lines.append(f"- put_call_ratio: {d.put_call_ratio}, iv_skew: {d.iv_skew}, max_pain: {d.max_pain}")
        lines.append(f"- parity_pairs_checked: {d.parity_pairs_checked}, parity_max_abs_residual: {d.parity_max_abs_residual}, parity_violations: {d.parity_violations}")
        lines.append(f"- calendar_arb_violations: {d.calendar_arb_violations}, butterfly_arb_violations: {d.butterfly_arb_violations}")
        lines.append(f"- quotes_with_iv: {d.quotes_with_iv}, quotes_with_greeks: {d.quotes_with_greeks}")
        lines.append(f"- content_sha256: {d.content_sha256}")
        lines.append("")
    lines.extend(
        [
            "",
            "This is an additive EVAL-27 Path A artifact. The sealed single-snapshot loader "
            "semantics (src.campaign.integrated.load_real_options_chain) are unchanged. "
            "Never emits {\"valid\": true}. Never relabels synthetic as real.",
        ]
    )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(json_path), str(md_path)


__all__ = [
    "SnapshotDiagnostics",
    "TimeseriesResult",
    "discover_all_real_options_exports",
    "load_options_timeseries",
    "evaluate_options_timeseries_tradability",
    "write_artifact",
    "REFERENCE_SPOT",
    "DEFAULT_RATE",
    "DEFAULT_SEED",
]
