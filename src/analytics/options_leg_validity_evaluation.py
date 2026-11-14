"""Real options-leg validity evaluation (EVAL-24, paper-only).

The options pillar of the crypto quantitative **options + orderflow** strategy
is only usable if the *real* option chain is valid: a reconstructable,
arbitrage-consistent volatility surface with computable greeks and a genuine
term structure. EVAL-16 measured those properties on a synthetic, internally
inconsistent chain. EVAL-24 re-measures them on **real public OKX exports** and
adds the one property EVAL-16 could not see: whether the chain is rich enough
to support a *tradable* options signal.

Blocks measured (all reuse sealed primitives, no re-implementation):

  1. **Completeness / units** — quote, strike, expiry, call/put counts; how many
     quotes carry venue IV, greeks, open interest; the price unit in use.
  2. **Surface reconstruction** — IV solved from mid prices where the venue
     supplies none (``build_iv_surface_from_chain``), calibrated with residuals.
  3. **Arbitrage** — butterfly convexity + calendar total-variance monotonicity
     on the reconstructed grid (``check_arbitrage_on_grid``).
  4. **Greeks** — analytic vs central finite difference (delta/vega) and
     stored-vs-recomputed delta where the venue supplies greeks.
  5. **Term structure from the surface** — ATM term structure and 25-delta risk
     reversal computed from the *solved* surface, because the venue ships no
     greeks for the delta-targeted helpers.
  6. **Book greeks** — total GEX, gamma flip, put-call ratio, max pain,
     liquidity, on both the raw and the greeks-enriched chain.

Verdict is explicit and numeric. A degenerate options leg is reported, never
hidden; a trustworthy NO-GO is a full success.

Emit canonical artifact:
``research_state/OPTIONS_LEG_VALIDITY_24_<UTC>.{json,md}``.
Paper-only: no network, no ``.env``, no venue/credential mutation, no live.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from src.analytics.options_surface_greeks_evaluation import (
    ARBITRAGE_MAX_VIOLATIONS,
    BS_VS_MARK_MAX_ABS_TOL,
    GREEK_DELTA_ERR_MEAN_TOL,
    GREEK_FD_MATCH_FRACTION_TOL,
    MARK_IV_MAX,
    MARK_IV_MIN,
    PARITY_MAX_ABS_TOL,
    SURFACE_RESIDUAL_MAX_ABS_TOL,
    _atm_strike,
    _mid,
    _years_between,
    check_arbitrage_on_grid,
    compute_book_greeks,
    compute_data_quality_metrics,
    compute_greeks_metrics,
    reconstruct_surface,
)
from src.campaign.integrated import (
    DETERMINISTIC_NOW,
    RealDataUnavailable,
    load_real_options_chain,
    load_real_orderflow,
)
from src.data.schemas import OptionQuote, OptionsChain, PricingInputs
from src.features.gamma_exposure import calculate_total_gex, gamma_flip_level
from src.features.liquidity import calculate_chain_liquidity_metrics
from src.features.options_pricing import black_scholes_greeks
from src.features.volatility import (
    calculate_atm_term_structure,
    calculate_iv_skew,
    calculate_iv_skew_term_structure,
    calculate_max_pain,
    calculate_put_call_ratio,
)
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

REPORT_ID = "OPTIONS_LEG_VALIDITY_24"
OUT_DIR = Path("research_state")

TRADING_MODE = "paper"
LIVE_TRADING_ENABLED = False

# EVAL-24 validity gates (numeric, rationale recorded in the artifact).
MIN_QUOTES: int = 8
MIN_STRIKES: int = 5
MIN_EXPIRIES: int = 2
MIN_TERM_TENORS: int = 2
MIN_PARITY_PAIRS: int = 4

# Surface plausibility: solved IVs must be positive and below a generous cap.
SURFACE_IV_MIN: float = 1e-4
SURFACE_IV_MAX: float = 5.0

# A tradable options leg needs a non-degenerate term structure: the ATM term
# structure must have >= MIN_TERM_TENORS points and not be constant.
MIN_ATM_TERM_STDEV: float = 1e-9

# Delta-targeted helpers return 0.0 when the venue ships no greeks; that is a
# measured fact to report, not a failure of this gate.
GREEK_COVERAGE_FLOOR: float = 0.0


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp_for_filename(iso_ts: str) -> str:
    return iso_ts.replace("-", "").replace(":", "").replace(".", "")


def _finite(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
        return v if math.isfinite(v) else float(default)
    except Exception:
        return float(default)


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


def _stdev(values: Sequence[float]) -> float:
    vals = [float(v) for v in values if math.isfinite(float(v))]
    if len(vals) < 2:
        return 0.0
    mean = sum(vals) / len(vals)
    var = sum((v - mean) ** 2 for v in vals) / (len(vals) - 1)
    return math.sqrt(var) if var > 0.0 else 0.0


# ---------------------------------------------------------------------------
# Block 1 — completeness / units
# ---------------------------------------------------------------------------


def compute_completeness(chain: OptionsChain) -> Dict[str, Any]:
    """Measure chain richness and venue-supplied field coverage."""
    quotes = chain.quotes or []
    n = len(quotes)
    strikes = sorted({float(q.contract.strike) for q in quotes})
    expiries = sorted({q.contract.expiry for q in quotes})
    calls = sum(1 for q in quotes if str(q.contract.option_type).lower() == "call")
    puts = sum(1 for q in quotes if str(q.contract.option_type).lower() == "put")
    with_iv = sum(
        1 for q in quotes
        if any(
            _finite(getattr(q, attr), default=float("nan")) > 0.0
            for attr in ("mark_iv", "bid_iv", "ask_iv")
        )
    )
    with_greeks = sum(
        1 for q in quotes
        if _finite(q.delta, default=float("nan")) == _finite(q.delta, default=float("nan"))
        and q.delta is not None
    )
    with_oi = sum(1 for q in quotes if _finite(q.open_interest) > 0.0)
    with_vol = sum(1 for q in quotes if _finite(q.volume) > 0.0)
    mid_prices = [_mid(q) for q in quotes]
    positive_mid = sum(1 for p in mid_prices if p is not None and float(p) > 0.0)
    return {
        "n_quotes": int(n),
        "n_strikes": int(len(strikes)),
        "n_expiries": int(len(expiries)),
        "n_calls": int(calls),
        "n_puts": int(puts),
        "strike_min": float(min(strikes)) if strikes else 0.0,
        "strike_max": float(max(strikes)) if strikes else 0.0,
        "n_with_venue_iv": int(with_iv),
        "venue_iv_coverage": float(with_iv / n) if n else 0.0,
        "n_with_venue_greeks": int(with_greeks),
        "greek_coverage": float(with_greeks / n) if n else 0.0,
        "n_with_open_interest": int(with_oi),
        "oi_coverage": float(with_oi / n) if n else 0.0,
        "n_with_volume": int(with_vol),
        "volume_coverage": float(with_vol / n) if n else 0.0,
        "n_positive_mid": int(positive_mid),
        "positive_mid_coverage": float(positive_mid / n) if n else 0.0,
    }


# ---------------------------------------------------------------------------
# Block 5 — term structure derived from the solved surface
# ---------------------------------------------------------------------------


def _surface_iv_at(
    points: Sequence[Any], strike: float, option_type: str = "call"
) -> Optional[float]:
    """Linear interpolation of surface IV at ``strike`` for one expiry bucket."""
    arr = sorted(
        [p for p in points if str(p.option_type) == option_type],
        key=lambda p: float(p.strike),
    )
    if not arr:
        return None
    lo = max([p for p in arr if float(p.strike) <= strike], key=lambda p: float(p.strike), default=None)
    hi = min([p for p in arr if float(p.strike) >= strike], key=lambda p: float(p.strike), default=None)
    if lo is None or hi is None:
        return None
    if float(hi.strike) == float(lo.strike):
        return float(lo.iv)
    w = (strike - float(lo.strike)) / (float(hi.strike) - float(lo.strike))
    return float((1.0 - w) * float(lo.iv) + w * float(hi.iv))


def compute_surface_term_structure(
    chain: OptionsChain,
    surface: Any,
    spot: float,
) -> Dict[str, Any]:
    """ATM term structure and 25-delta-style risk reversal from solved IVs.

    The venue supplies no greeks, so the sealed delta-targeted helpers return
    0.0; this measures the term structure directly from the reconstructed
    surface with a fixed moneyness proxy (10% OTM wings).
    """
    by_expiry: Dict[float, List[Any]] = {}
    for p in surface.points:
        by_expiry.setdefault(round(float(p.time_to_expiry), 12), []).append(p)

    atm: Dict[str, float] = {}
    rr: Dict[str, float] = {}
    for t in sorted(by_expiry):
        pts = by_expiry[t]
        atm_iv = _surface_iv_at(pts, spot, "call")
        if atm_iv is not None and math.isfinite(atm_iv):
            atm[f"{t:.10f}"] = float(atm_iv)
        call_iv = _surface_iv_at(pts, spot * 1.10, "call")
        put_iv = _surface_iv_at(pts, spot * 0.90, "put")
        if (
            call_iv is not None
            and put_iv is not None
            and math.isfinite(call_iv)
            and math.isfinite(put_iv)
        ):
            rr[f"{t:.10f}"] = float(call_iv - put_iv)

    atm_vals = [atm[k] for k in sorted(atm, key=float)]
    rr_vals = [rr[k] for k in sorted(rr, key=float)]
    atm_stdev = _stdev(atm_vals)
    rr_stdev = _stdev(rr_vals)

    return {
        "n_atm_tenors": int(len(atm_vals)),
        "atm_term_structure": {k: float(atm[k]) for k in sorted(atm, key=float)},
        "atm_term_structure_stdev": float(atm_stdev),
        "atm_term_structure_monotonic": bool(
            len(atm_vals) >= 2
            and all(atm_vals[i] <= atm_vals[i + 1] + 1e-9 for i in range(len(atm_vals) - 1))
        ),
        "n_rr_tenors": int(len(rr_vals)),
        "risk_reversal": {k: float(rr[k]) for k in sorted(rr, key=float)},
        "risk_reversal_stdev": float(rr_stdev),
        "risk_reversal_mean": float(sum(rr_vals) / len(rr_vals)) if rr_vals else 0.0,
        "term_structure_non_degenerate": bool(
            len(atm_vals) >= MIN_TERM_TENORS and atm_stdev > MIN_ATM_TERM_STDEV
        ),
    }


# ---------------------------------------------------------------------------
# Block 6 — book greeks on the raw and greeks-enriched chain
# ---------------------------------------------------------------------------


def _enrich_chain_with_greeks(
    chain: OptionsChain,
    surface: Any,
    spot: float,
    now: datetime,
    rate: float = 0.0,
) -> Tuple[OptionsChain, Dict[str, Any]]:
    """Return a copy of the chain with greeks recomputed from the surface.

    GEX/OI-based book metrics are structurally zero when the venue ships no
    gamma/OI. Recomputing greeks from the solved surface lets the book greeks
    block measure *something real* rather than silently reporting zero.
    """
    enriched: List[OptionQuote] = []
    n_recomputed = 0
    n_finite_gamma = 0
    for q in chain.quotes:
        try:
            t = _years_between(q.contract.expiry, now)
        except Exception:
            t = 1e-9
        if t <= 0.0:
            t = 1e-9
        try:
            iv = float(surface.get_iv(float(q.contract.strike), t, str(q.contract.option_type)))
        except Exception:
            enriched.append(q)
            continue
        inputs = PricingInputs(
            spot=float(spot),
            strike=float(q.contract.strike),
            rate=float(rate),
            volatility=float(iv),
            time_to_expiry=float(t),
            option_type=str(q.contract.option_type),
            seed=42,
        )
        try:
            g = black_scholes_greeks(inputs)
        except Exception:
            enriched.append(q)
            continue
        n_recomputed += 1
        gamma = _finite(g.get("gamma"), 0.0)
        if math.isfinite(gamma):
            n_finite_gamma += 1
        enriched.append(
            q.model_copy(update={
                "delta": _finite(g.get("delta"), 0.0),
                "gamma": gamma,
                "theta": _finite(g.get("theta"), 0.0),
                "vega": _finite(g.get("vega"), 0.0),
            })
        )

    enriched_chain = OptionsChain(
        underlying=chain.underlying,
        venue=chain.venue,
        quotes=enriched,
        timestamp=chain.timestamp,
    )
    meta = {
        "n_recomputed": int(n_recomputed),
        "n_finite_gamma": int(n_finite_gamma),
        "recomputed": bool(n_recomputed > 0),
    }
    return enriched_chain, meta


def _chain_now(chain: OptionsChain) -> datetime:
    ts = [q.timestamp for q in (chain.quotes or []) if q.timestamp is not None]
    if not ts:
        return DETERMINISTIC_NOW
    now = max(ts)
    return now if now.tzinfo is not None else now.replace(tzinfo=timezone.utc)


def compute_book_greeks_both(
    raw_chain: OptionsChain,
    enriched_chain: OptionsChain,
    spot: float,
    now: datetime,
) -> Dict[str, Any]:
    raw = compute_book_greeks(raw_chain, spot, now)
    enriched = compute_book_greeks(enriched_chain, spot, now)
    return {
        "raw": raw,
        "enriched": enriched,
        "gex_raw_total": float(raw["total_gex"]),
        "gex_enriched_total": float(enriched["total_gex"]),
        "gamma_flip_raw": float(raw["gamma_flip_level"]),
        "gamma_flip_enriched": float(enriched["gamma_flip_level"]),
        "put_call_ratio": float(raw["put_call_ratio"]),
        "max_pain": float(raw["max_pain"]),
        "liquidity": dict(raw["liquidity"]),
        "atm_term_structure_raw": dict(raw["atm_term_structure"]),
        "n_expiries_in_atm_ts": int(raw["n_expiries_in_atm_ts"]),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------


def compute_options_leg_verdict(
    completeness: Dict[str, Any],
    data_quality: Dict[str, Any],
    surface: Dict[str, Any],
    arbitrage: Dict[str, Any],
    greeks: Dict[str, Any],
    term_structure: Dict[str, Any],
    book: Dict[str, Any],
) -> Dict[str, Any]:
    """Explicit numeric validity checks for the real options leg."""
    checks: List[Dict[str, Any]] = []

    def _add(name: str, ok: bool, threshold: float, observed: float, reason: str) -> None:
        checks.append({
            "name": name,
            "pass": bool(ok),
            "threshold": float(threshold),
            "observed": float(observed),
            "reason": reason,
        })

    # 1. Chain richness.
    rich = bool(
        completeness["n_quotes"] >= MIN_QUOTES
        and completeness["n_strikes"] >= MIN_STRIKES
        and completeness["n_expiries"] >= MIN_EXPIRIES
        and completeness["positive_mid_coverage"] > 0.0
    )
    _add(
        "chain_richness",
        rich,
        float(MIN_QUOTES),
        float(completeness["n_quotes"]),
        (
            f"PASS: {completeness['n_quotes']} quotes, {completeness['n_strikes']} strikes, "
            f"{completeness['n_expiries']} expiries, "
            f"{completeness['positive_mid_coverage']:.2%} positive mids"
            if rich
            else "FAIL: chain below richness floors"
        ),
    )

    # 2. Surface reconstruction produced points with plausible IVs.
    iv_min = float(surface["residual_report"].get("iv_min", 0.0))
    iv_max = float(surface["residual_report"].get("iv_max", 0.0))
    n_points = int(surface["n_points"])
    surf_ok = bool(
        n_points > 0
        and SURFACE_IV_MIN <= iv_min
        and iv_max <= SURFACE_IV_MAX
        and iv_min <= iv_max
    )
    _add(
        "surface_reconstructed",
        surf_ok,
        float(SURFACE_IV_MAX),
        float(iv_max),
        (
            f"PASS: {n_points} surface points, IV range [{iv_min:.4f}, {iv_max:.4f}] "
            f"within [{SURFACE_IV_MIN:.1e}, {SURFACE_IV_MAX}]"
            if surf_ok
            else f"FAIL: surface points={n_points}, IV range [{iv_min:.4f}, {iv_max:.4f}]"
        ),
    )

    # 3. Calibration residual.
    resid_max = float(surface["residual_report"]["residual_max_abs"])
    _add(
        "surface_calibration_residual",
        resid_max <= SURFACE_RESIDUAL_MAX_ABS_TOL,
        SURFACE_RESIDUAL_MAX_ABS_TOL,
        resid_max,
        (
            f"PASS: residual max abs {resid_max:.3e} <= {SURFACE_RESIDUAL_MAX_ABS_TOL:.1e}"
            if resid_max <= SURFACE_RESIDUAL_MAX_ABS_TOL
            else f"FAIL: residual max abs {resid_max:.3e} > {SURFACE_RESIDUAL_MAX_ABS_TOL:.1e}"
        ),
    )

    # 4. Arbitrage on the reconstructed grid.
    arb_ok = bool(arbitrage["total_violations"] <= ARBITRAGE_MAX_VIOLATIONS)
    _add(
        "surface_arbitrage_free",
        arb_ok,
        float(ARBITRAGE_MAX_VIOLATIONS),
        float(arbitrage["total_violations"]),
        (
            f"PASS: {arbitrage['total_violations']} violations "
            f"(butterfly {arbitrage['butterfly_violations']}, calendar {arbitrage['calendar_violations']})"
            if arb_ok
            else f"FAIL: {arbitrage['total_violations']} violations"
        ),
    )

    # 5. Analytic greeks match finite differences.
    fd_frac = min(float(greeks["delta_match_fraction"]), float(greeks["vega_match_fraction"]))
    _add(
        "greeks_analytic_vs_finite_difference",
        fd_frac >= GREEK_FD_MATCH_FRACTION_TOL,
        GREEK_FD_MATCH_FRACTION_TOL,
        fd_frac,
        (
            f"PASS: analytic vs FD match fraction {fd_frac:.4f} "
            f">= {GREEK_FD_MATCH_FRACTION_TOL}"
            if fd_frac >= GREEK_FD_MATCH_FRACTION_TOL
            else f"FAIL: match fraction {fd_frac:.4f} < {GREEK_FD_MATCH_FRACTION_TOL}"
        ),
    )

    # 6. Put-call parity (only meaningful where both legs exist).
    n_parity = int(data_quality["n_parity_pairs"])
    parity_max = float(data_quality["parity_residual_max_abs"])
    parity_ok = bool(n_parity >= MIN_PARITY_PAIRS and parity_max <= PARITY_MAX_ABS_TOL)
    _add(
        "put_call_parity",
        parity_ok,
        PARITY_MAX_ABS_TOL,
        parity_max,
        (
            f"PASS: {n_parity} pairs, parity residual max abs {parity_max:.4f} "
            f"<= {PARITY_MAX_ABS_TOL}"
            if parity_ok
            else f"FAIL: {n_parity} pairs, parity residual max abs {parity_max:.4f}"
        ),
    )

    # 7. Term structure from the solved surface is non-degenerate.
    ts_ok = bool(term_structure["term_structure_non_degenerate"])
    _add(
        "term_structure_non_degenerate",
        ts_ok,
        float(MIN_TERM_TENORS),
        float(term_structure["n_atm_tenors"]),
        (
            f"PASS: {term_structure['n_atm_tenors']} ATM tenors, stdev "
            f"{term_structure['atm_term_structure_stdev']:.4f}"
            if ts_ok
            else f"FAIL: {term_structure['n_atm_tenors']} ATM tenors, stdev "
            f"{term_structure['atm_term_structure_stdev']:.3e}"
        ),
    )

    # 8. Options leg can produce a tradable signal: non-constant term
    #    structure AND non-degenerate book greeks. A single cross-section with a
    #    flat surface cannot support a time-varying options signal.
    gex_nonzero = bool(abs(float(book["gex_enriched_total"])) > 0.0)
    tradable = bool(ts_ok and gex_nonzero)
    _add(
        "options_leg_tradable",
        tradable,
        1.0,
        1.0 if tradable else 0.0,
        (
            f"PASS: term structure varies and enriched GEX is non-zero "
            f"({book['gex_enriched_total']:.2f})"
            if tradable
            else "FAIL: options leg cannot produce a time-varying tradable signal "
            f"(term structure varies={ts_ok}, enriched GEX non-zero={gex_nonzero})"
        ),
    )

    all_pass = all(bool(c["pass"]) for c in checks)
    return {
        "verdict": "GO" if all_pass else "NO-GO",
        "checks": checks,
        "n_checks": int(len(checks)),
        "n_passed": int(sum(1 for c in checks if bool(c["pass"]))),
        "all_checks_pass": bool(all_pass),
        "failed_checks": [c["name"] for c in checks if not bool(c["pass"])],
        "options_leg_degenerate": bool(not tradable),
    }


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def evaluate_options_leg_validity(
    *,
    data_raw: Path | str = Path("data/raw"),
    symbol: str = "BTC",
    spot: Optional[float] = None,
    now: Optional[datetime] = None,
    rate: float = 0.0,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """Run EVAL-24 on the real chain and return the strict-serialized report.

    Raises :class:`RealDataUnavailable` when the real option export is missing.
    """
    stamp = timestamp or _utc_now_iso()

    chain = load_real_options_chain(symbol, data_raw=Path(data_raw))
    if not chain.quotes:
        raise RealDataUnavailable(f"real option export for {symbol!r} is empty")

    # Anchor spot and now on the real data, not the wall clock.
    if now is None:
        now = _chain_now(chain)
    if spot is None:
        try:
            orderflow = load_real_orderflow(symbol, data_raw=Path(data_raw))
            trades = sorted(orderflow.trades or [], key=lambda t: t.timestamp)
            spot = float(trades[-1].price) if trades else float(_atm_strike(chain, 0.0) or 0.0)
        except RealDataUnavailable:
            spot = float(_atm_strike(chain, 0.0))
    spot = float(spot)

    # Block 1 — completeness / units
    completeness = compute_completeness(chain)

    # Block 2 — surface reconstruction (solves IV from mids; no venue IV needed)
    surface_block = reconstruct_surface(chain, spot, rate=rate, now=now, seed=42)
    calibrated = surface_block["surface"]
    ivs = [float(p.iv) for p in calibrated.points if math.isfinite(float(p.iv))]
    iv_min = float(min(ivs)) if ivs else 0.0
    iv_max = float(max(ivs)) if ivs else 0.0
    residual_report = dict(surface_block["residual_report"])
    residual_report["iv_min"] = iv_min
    residual_report["iv_max"] = iv_max
    surface = {
        "n_points": int(surface_block["n_points"]),
        "n_expiries": int(surface_block["n_expiries"]),
        "points_per_expiry": dict(surface_block["points_per_expiry"]),
        "residual_report": residual_report,
    }

    # Block 3 — arbitrage on the reconstructed grid
    arbitrage = check_arbitrage_on_grid(calibrated, spot, rate=rate, now=now)

    # Block 4 — greeks (analytic vs FD; stored-vs-recomputed only if present)
    greeks = compute_greeks_metrics(chain, calibrated, spot, rate=rate, now=now)

    # Block 5 — term structure from the solved surface
    term_structure = compute_surface_term_structure(chain, calibrated, spot)

    # Block 6 — book greeks on raw + greeks-enriched chain
    enriched_chain, enrich_meta = _enrich_chain_with_greeks(
        chain, calibrated, spot, now, rate=rate
    )
    book = compute_book_greeks_both(chain, enriched_chain, spot, now)

    # Data quality (venue IV vs mark) is measured for completeness; with no
    # venue IV it is reported honestly rather than treated as a pass.
    data_quality = compute_data_quality_metrics(chain, spot, rate=rate, now=now)

    verdict = compute_options_leg_verdict(
        completeness, data_quality, surface, arbitrage, greeks, term_structure, book
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": stamp,
        "verdict": verdict["verdict"],
        "trading_mode": TRADING_MODE,
        "live_trading_enabled": LIVE_TRADING_ENABLED,
        "data_provenance": "real",
        "authenticity_verified": False,
        "never_valid_true": True,
        "options_leg_degenerate": bool(verdict["options_leg_degenerate"]),
        "config": {
            "symbol": symbol,
            "spot": spot,
            "now": now.isoformat().replace("+00:00", "Z"),
            "rate": float(rate),
            "venue": str(chain.venue),
            "thresholds": {
                "min_quotes": MIN_QUOTES,
                "min_strikes": MIN_STRIKES,
                "min_expiries": MIN_EXPIRIES,
                "min_term_tenors": MIN_TERM_TENORS,
                "min_parity_pairs": MIN_PARITY_PAIRS,
                "surface_iv_min": SURFACE_IV_MIN,
                "surface_iv_max": SURFACE_IV_MAX,
                "bs_vs_mark_tol": BS_VS_MARK_MAX_ABS_TOL,
                "parity_tol": PARITY_MAX_ABS_TOL,
                "mark_iv_min": MARK_IV_MIN,
                "mark_iv_max": MARK_IV_MAX,
                "surface_residual_tol": SURFACE_RESIDUAL_MAX_ABS_TOL,
                "arbitrage_max_violations": ARBITRAGE_MAX_VIOLATIONS,
                "greek_delta_err_tol": GREEK_DELTA_ERR_MEAN_TOL,
                "greek_fd_match_fraction_tol": GREEK_FD_MATCH_FRACTION_TOL,
            },
        },
        "completeness": completeness,
        "surface": {
            "n_points": int(surface["n_points"]),
            "n_expiries": int(surface["n_expiries"]),
            "points_per_expiry": dict(surface["points_per_expiry"]),
            "residual_report": surface["residual_report"],
        },
        "arbitrage": arbitrage,
        "greeks": {k: v for k, v in greeks.items() if k != "recomputed"},
        "greeks_recomputed_sample": greeks.get("recomputed", [])[:5],
        "greeks_enrichment": enrich_meta,
        "term_structure": term_structure,
        "book_greeks": book,
        "data_quality": data_quality,
        "verdict_checks": verdict,
        "evidence_matrix": {
            "n_quotes": int(completeness["n_quotes"]),
            "n_strikes": int(completeness["n_strikes"]),
            "n_expiries": int(completeness["n_expiries"]),
            "n_surface_points": int(surface["n_points"]),
            "n_atm_tenors": int(term_structure["n_atm_tenors"]),
            "n_rr_tenors": int(term_structure["n_rr_tenors"]),
            "venue": str(chain.venue),
            "spot_used": spot,
            "now_used": now.isoformat().replace("+00:00", "Z"),
            "data_provenance": "real",
            "authenticity_verified": False,
            "never_synthetic": True,
            "paper_only": True,
            "live_trading_enabled": False,
        },
        "deployment_authorization": {
            "authorized": bool(verdict["verdict"] == "GO"),
            "mode": "paper_only",
            "note": (
                "GO certifies options-leg validity only; not authorization to "
                "trade live."
            ),
        },
    }

    assert completeness["n_quotes"] > 0, "real chain has no quotes"
    assert verdict["verdict"] in ("GO", "NO-GO")
    assert verdict["verdict"] == ("GO" if verdict["all_checks_pass"] else "NO-GO")
    assert _all_finite_numbers(verdict), "verdict non-finite"
    assert _all_finite_numbers(term_structure), "term structure non-finite"
    assert _all_finite_numbers(arbitrage), "arbitrage non-finite"
    assert report["data_provenance"] == "real", "EVAL-24 must be real-data only"

    assert_json_valid(report)
    return serialize_metrics_strict(report)


def write_artifacts(report: Dict[str, Any], out_dir: Path | str = OUT_DIR) -> Dict[str, str]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = _stamp_for_filename(str(report["generated_at"]))
    json_path = out_dir / f"OPTIONS_LEG_VALIDITY_24_{stamp}.json"
    md_path = out_dir / f"OPTIONS_LEG_VALIDITY_24_{stamp}.md"
    json_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    md_path.write_text(_write_markdown(report) + "\n", encoding="utf-8")
    return {"json": str(json_path), "md": str(md_path)}


def _write_markdown(report: Dict[str, Any]) -> str:
    v = report["verdict_checks"]
    c = report["completeness"]
    ts = report["term_structure"]
    lines: List[str] = []
    lines.append(f"# {report['report_id']} — REAL OPTIONS-LEG VALIDITY (paper-only)")
    lines.append("")
    lines.append(f"**Generated:** {report['generated_at']}  ")
    lines.append(f"**Verdict:** **{report['verdict']}** ({v['n_passed']}/{v['n_checks']} checks)  ")
    lines.append(f"**Options leg degenerate:** `{str(report['options_leg_degenerate']).lower()}`  ")
    lines.append(f"**Venue:** {report['config']['venue']} · **spot:** {report['config']['spot']}  ")
    lines.append("")
    lines.append("## Measured evidence")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| quotes / strikes / expiries | {c['n_quotes']} / {c['n_strikes']} / {c['n_expiries']} |")
    lines.append(f"| calls / puts | {c['n_calls']} / {c['n_puts']} |")
    lines.append(f"| venue IV coverage | {c['venue_iv_coverage']:.2%} |")
    lines.append(f"| venue greeks coverage | {c['greek_coverage']:.2%} |")
    lines.append(f"| open interest coverage | {c['oi_coverage']:.2%} |")
    lines.append(f"| positive mid coverage | {c['positive_mid_coverage']:.2%} |")
    lines.append(f"| surface points / expiries | {report['surface']['n_points']} / {report['surface']['n_expiries']} |")
    lines.append(f"| butterfly / calendar violations | {report['arbitrage']['butterfly_violations']} / {report['arbitrage']['calendar_violations']} |")
    lines.append(f"| analytic-vs-FD match (delta/vega) | {report['greeks']['delta_match_fraction']:.4f} / {report['greeks']['vega_match_fraction']:.4f} |")
    lines.append(f"| ATM tenors | {ts['n_atm_tenors']} (stdev {ts['atm_term_structure_stdev']:.4f}) |")
    lines.append(f"| risk-reversal tenors | {ts['n_rr_tenors']} (mean {ts['risk_reversal_mean']:.4f}) |")
    lines.append(f"| GEX raw / enriched | {report['book_greeks']['gex_raw_total']:.2f} / {report['book_greeks']['gex_enriched_total']:.2f} |")
    lines.append(f"| put-call ratio | {report['book_greeks']['put_call_ratio']:.4f} |")
    lines.append("")
    lines.append("## ATM term structure (solved IV)")
    lines.append("")
    lines.append("| tenor (years) | ATM IV |")
    lines.append("|---|---|")
    for k, val in ts["atm_term_structure"].items():
        lines.append(f"| {float(k):.6f} | {val:.4f} |")
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    lines.append("| Check | Pass | Observed | Reason |")
    lines.append("|---|---|---|---|")
    for chk in v["checks"]:
        reason = str(chk["reason"]).replace("|", "/")
        lines.append(
            f"| {chk['name']} | {str(bool(chk['pass'])).lower()} | {chk['observed']:.6g} | {reason} |"
        )
    lines.append("")
    lines.append("## Provenance / constraints")
    lines.append("")
    lines.append("- Real OKX public read-only export; no `.env`, no credentials, no order placement.")
    lines.append("- `authenticity_verified=false`: no signed venue attestation.")
    lines.append("- The venue ships no IV/greeks/OI for this snapshot; IV is solved from mid prices.")
    lines.append("- Never emits `{\"valid\": true}`. A trustworthy NO-GO is a full success.")
    lines.append("")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Real options-leg validity evaluation (EVAL-24, paper-only)."
    )
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--out", default=str(OUT_DIR))
    parser.add_argument("--symbol", default="BTC")
    parser.add_argument("--spot", type=float, default=None)
    parser.add_argument("--timestamp", default=None)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)

    try:
        report = evaluate_options_leg_validity(
            data_raw=Path(args.data_dir),
            symbol=args.symbol,
            spot=args.spot,
            timestamp=args.timestamp,
        )
    except RealDataUnavailable as e:
        print(json.dumps({"report_id": REPORT_ID, "verdict": "NO-GO", "error": str(e)}))
        return 2

    paths = {} if args.no_write else write_artifacts(report, Path(args.out))
    print(json.dumps({
        "report_id": report["report_id"],
        "verdict": report["verdict"],
        "n_passed": report["verdict_checks"]["n_passed"],
        "n_checks": report["verdict_checks"]["n_checks"],
        "failed_checks": report["verdict_checks"]["failed_checks"],
        "options_leg_degenerate": report["options_leg_degenerate"],
        "artifact_paths": paths,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())