"""Volatility surface, skew, and term structure analysis."""

from datetime import datetime, timezone
from math import isfinite
from typing import Dict, List, Optional, Tuple

import numpy as np

from ..data.schemas import OptionsChain, OptionQuote


def _to_float(x: Optional[float]) -> Optional[float]:
    if x is None:
        return None
    try:
        v = float(x)
    except Exception:
        return None
    if not isfinite(v):
        return None
    return v


def _delta_abs(q: OptionQuote) -> Optional[float]:
    d = _to_float(q.delta)
    if d is None:
        return None
    return abs(d)


def calculate_put_call_ratio(quotes: List[OptionQuote]) -> float:
    """Calculate put/call ratio by volume."""
    if not quotes:
        return 0.0
    call_volume = 0.0
    put_volume = 0.0
    for q in quotes:
        v = _to_float(q.volume)
        if v is None:
            v = 0.0
        t = (q.contract.option_type or "").lower()
        if t == "call":
            call_volume += v
        elif t == "put":
            put_volume += v
    if call_volume == 0.0:
        if put_volume > 0.0:
            return float("inf")
        return 0.0
    ratio = put_volume / call_volume
    if not isfinite(ratio):
        return float("inf") if put_volume > 0.0 else 0.0
    return ratio


def calculate_put_call_oi_ratio(quotes: List[OptionQuote]) -> float:
    """Calculate put/call ratio by open interest."""
    if not quotes:
        return 0.0
    call_oi = 0.0
    put_oi = 0.0
    for q in quotes:
        oi = _to_float(q.open_interest)
        if oi is None:
            oi = 0.0
        t = (q.contract.option_type or "").lower()
        if t == "call":
            call_oi += oi
        elif t == "put":
            put_oi += oi
    if call_oi == 0.0:
        if put_oi > 0.0:
            return float("inf")
        return 0.0
    ratio = put_oi / call_oi
    if not isfinite(ratio):
        return float("inf") if put_oi > 0.0 else 0.0
    return ratio


def calculate_iv_skew(quotes: List[OptionQuote], spot_price: float) -> float:
    """Calculate volatility skew (25-delta put IV minus 25-delta call IV).

    Selects OTM puts with delta closest to -0.25 and OTM calls with delta closest
    to +0.25 (using |delta| ~ 0.25), picks mid IV when available else last/mark IV,
    and returns ``iv_put - iv_call``. Returns 0.0 if insufficient data or result
    non-finite.
    """
    if not quotes or spot_price is None:
        return 0.0
    sp = _to_float(spot_price)
    if sp is None or sp <= 0.0:
        return 0.0
    otm_puts = []
    otm_calls = []
    for q in quotes:
        iv = _to_float(q.mark_iv)
        if iv is None:
            iv = _to_float(q.bid_iv)
        if iv is None:
            iv = _to_float(q.ask_iv)
        if iv is None:
            continue
        m = q.contract.strike / sp if sp != 0.0 else 0.0
        if not isfinite(m):
            continue
        t = (q.contract.option_type or "").lower()
        if t == "put" and m < 0.95:
            otm_puts.append(iv)
        elif t == "call" and m > 1.05:
            otm_calls.append(iv)
    if not otm_puts or not otm_calls:
        return 0.0
    avg_put_iv = sum(otm_puts) / len(otm_puts)
    avg_call_iv = sum(otm_calls) / len(otm_calls)
    skew = avg_put_iv - avg_call_iv
    if not isfinite(skew):
        return 0.0
    return skew


def calculate_max_pain(chain: OptionsChain) -> float:
    """Calculate max pain strike price."""
    if not chain or not chain.quotes:
        return 0.0
    strikes = set()
    for q in chain.quotes:
        s = _to_float(q.contract.strike)
        if s is not None and isfinite(s):
            strikes.add(s)
    if not strikes:
        return 0.0
    max_pain_strike = 0.0
    min_pain = float("inf")
    for strike in strikes:
        total_pain = 0.0
        for q in chain.quotes:
            oi = _to_float(q.open_interest)
            if oi is None:
                oi = 0.0
            if oi == 0.0:
                continue
            t = (q.contract.option_type or "").lower()
            if t == "call":
                if q.contract.strike < strike:
                    diff = strike - q.contract.strike
                    if isfinite(diff):
                        total_pain += diff * oi
            else:
                if q.contract.strike > strike:
                    diff = q.contract.strike - strike
                    if isfinite(diff):
                        total_pain += diff * oi
        if total_pain < min_pain:
            min_pain = total_pain
            max_pain_strike = strike
    if not isfinite(min_pain):
        return 0.0
    return max_pain_strike


def _get_iv(q: OptionQuote) -> Optional[float]:
    iv = _to_float(q.mark_iv)
    if iv is None:
        iv = _to_float(q.bid_iv)
    if iv is None:
        iv = _to_float(q.ask_iv)
    return iv


def _tenor_years(expiry: datetime, now: Optional[datetime] = None) -> float:
    if now is None:
        now = datetime.now(timezone.utc)
    if expiry.tzinfo is None:
        try:
            expiry = expiry.replace(tzinfo=timezone.utc)
        except Exception:
            pass
    if now.tzinfo is None:
        try:
            now = now.replace(tzinfo=timezone.utc)
        except Exception:
            pass
    try:
        dt = (expiry - now).total_seconds()
    except Exception:
        return float("nan")
    if not isfinite(dt):
        return float("nan")
    if dt < 0.0:
        dt = 0.0
    years = dt / (365.25 * 24.0 * 3600.0)
    if not isfinite(years):
        return float("nan")
    return years


def calculate_put_call_skew(
    quotes: List[OptionQuote],
    spot_price: float,
    delta_target: float = 0.25,
    tol: float = 0.05,
    expiry: Optional[datetime] = None,
) -> float:
    if not quotes or spot_price is None:
        return 0.0
    sp = _to_float(spot_price)
    if sp is None or sp <= 0.0:
        return 0.0
    dt = _to_float(delta_target)
    if dt is None or dt <= 0.0:
        dt = 0.25
    t = _to_float(tol)
    if t is None or t < 0.0:
        t = 0.05
    put_ivs = []
    call_ivs = []
    for q in quotes:
        if expiry is not None and q.contract.expiry != expiry:
            try:
                if q.contract.expiry.date() != expiry.date():
                    continue
            except Exception:
                continue
        iv = _get_iv(q)
        if iv is None:
            continue
        dabs = _delta_abs(q)
        if dabs is not None and abs(dabs - dt) <= t:
            ot = (q.contract.option_type or "").lower()
            if ot == "put":
                put_ivs.append(iv)
            elif ot == "call":
                call_ivs.append(iv)
            continue
        m = q.contract.strike / sp
        if not isfinite(m):
            continue
        ot = (q.contract.option_type or "").lower()
        if ot == "put" and m < 1.0 - dt - t * 0.5:
            put_ivs.append(iv)
        elif ot == "call" and m > 1.0 + dt + t * 0.5:
            call_ivs.append(iv)
    if not put_ivs or not call_ivs:
        return 0.0
    p = sum(put_ivs) / len(put_ivs)
    c = sum(call_ivs) / len(call_ivs)
    skew = p - c
    if not isfinite(skew):
        return 0.0
    return skew


def calculate_risk_reversal(
    quotes: List[OptionQuote],
    spot_price: float,
    delta_target: float = 0.25,
    tol: float = 0.05,
    expiry: Optional[datetime] = None,
) -> float:
    if not quotes or spot_price is None:
        return 0.0
    sp = _to_float(spot_price)
    if sp is None or sp <= 0.0:
        return 0.0
    dt = _to_float(delta_target)
    if dt is None or dt <= 0.0:
        dt = 0.25
    t = _to_float(tol)
    if t is None or t < 0.0:
        t = 0.05
    put_ivs = []
    call_ivs = []
    for q in quotes:
        if expiry is not None:
            try:
                if q.contract.expiry != expiry and q.contract.expiry.date() != expiry.date():
                    continue
            except Exception:
                continue
        iv = _get_iv(q)
        if iv is None:
            continue
        dabs = _delta_abs(q)
        if dabs is not None and abs(dabs - dt) <= t:
            ot = (q.contract.option_type or "").lower()
            if ot == "call":
                call_ivs.append(iv)
            elif ot == "put":
                put_ivs.append(iv)
            continue
        m = q.contract.strike / sp
        if not isfinite(m):
            continue
        ot = (q.contract.option_type or "").lower()
        if ot == "call" and m > 1.0 + dt + t * 0.5:
            call_ivs.append(iv)
        elif ot == "put" and m < 1.0 - dt - t * 0.5:
            put_ivs.append(iv)
    if not call_ivs or not put_ivs:
        return 0.0
    c = sum(call_ivs) / len(call_ivs)
    p = sum(put_ivs) / len(put_ivs)
    rr = c - p
    if not isfinite(rr):
        return 0.0
    return rr


def calculate_risk_reversal_term_structure(
    quotes: List[OptionQuote],
    spot_price: float,
    delta_target: float = 0.25,
    tol: float = 0.05,
    now: Optional[datetime] = None,
) -> Dict[float, float]:
    """Compute risk reversal (25Δ call - 25Δ put) by tenor (years).

    Groups quotes by expiry, computes RR per expiry via
    ``calculate_risk_reversal`` using mid/last/mark IV and |delta| matching to
    ``delta_target`` within tolerance, converts expiry to years-to-maturity via
    ``_tenor_years``, returns sorted dict keyed by tenor.
    """
    if not quotes or spot_price is None:
        return {}
    sp = _to_float(spot_price)
    if sp is None or sp <= 0.0:
        return {}
    by_exp: Dict[str, List[OptionQuote]] = {}
    for q in quotes:
        try:
            key = q.contract.expiry.isoformat()
        except Exception:
            continue
        by_exp.setdefault(key, []).append(q)
    out = {}
    for key, qlist in by_exp.items():
        exp = qlist[0].contract.expiry
        rr = calculate_risk_reversal(qlist, sp, delta_target=delta_target, tol=tol, expiry=exp)
        if not isfinite(rr):
            continue
        t = _tenor_years(exp, now=now)
        if not isfinite(t):
            continue
        out[float(t)] = float(rr)
    return dict(sorted(out.items()))


def calculate_skew_term_structure(
    quotes: List[OptionQuote],
    spot_price: float,
    delta_target: float = 0.25,
    tol: float = 0.05,
    now: Optional[datetime] = None,
) -> Dict[float, float]:
    """Compute put-call skew (25Δ put - 25Δ call) by tenor (years).

    Groups by expiry and uses ``calculate_put_call_skew`` per expiry with delta
    matching; returns tenor-sorted dict of skew values.
    """
    if not quotes or spot_price is None:
        return {}
    sp = _to_float(spot_price)
    if sp is None or sp <= 0.0:
        return {}
    by_exp: Dict[str, List[OptionQuote]] = {}
    for q in quotes:
        try:
            key = q.contract.expiry.isoformat()
        except Exception:
            continue
        by_exp.setdefault(key, []).append(q)
    out = {}
    for key, qlist in by_exp.items():
        exp = qlist[0].contract.expiry
        sk = calculate_put_call_skew(qlist, sp, delta_target=delta_target, tol=tol, expiry=exp)
        if not isfinite(sk):
            continue
        t = _tenor_years(exp, now=now)
        if not isfinite(t):
            continue
        out[float(t)] = float(sk)
    return dict(sorted(out.items()))


def calculate_iv_skew_term_structure(
    quotes: List[OptionQuote],
    spot_price: float,
    delta_target: float = 0.25,
    tol: float = 0.05,
    now: Optional[datetime] = None,
) -> Dict[float, Dict[str, float]]:
    """Compute combined IV skew term structure with risk reversal and put-call skew.

    Merges RR and put-call skew term structures by tenor, returning dict
    keyed by years-to-maturity with nested dict containing ``'risk_reversal'``,
    ``'put_call_skew'``, and ``'skew'`` when available.
    """
    if not quotes or spot_price is None:
        return {}
    sp = _to_float(spot_price)
    if sp is None or sp <= 0.0:
        return {}
    rr_ts = calculate_risk_reversal_term_structure(
        quotes, sp, delta_target=delta_target, tol=tol, now=now
    )
    sk_ts = calculate_skew_term_structure(
        quotes, sp, delta_target=delta_target, tol=tol, now=now
    )
    out: Dict[float, Dict[str, float]] = {}
    # Merge by tenor
    all_tenors = set(rr_ts.keys()) | set(sk_ts.keys())
    for t in all_tenors:
        d: Dict[str, float] = {}
        if t in rr_ts and isfinite(rr_ts[t]):
            d["risk_reversal"] = float(rr_ts[t])
        if t in sk_ts and isfinite(sk_ts[t]):
            d["put_call_skew"] = float(sk_ts[t])
        # Provide combined 'skew' alias if both present, else the one present
        if "put_call_skew" in d and "risk_reversal" in d:
            d["skew"] = d["put_call_skew"]
        elif "put_call_skew" in d:
            d["skew"] = d["put_call_skew"]
        elif "risk_reversal" in d:
            d["skew"] = d["risk_reversal"]
        if d:
            out[float(t)] = d
    return dict(sorted(out.items()))


def calculate_atm_term_structure(
    quotes: List[OptionQuote],
    spot_price: float,
    moneyness_tol: float = 0.02,
    now: Optional[datetime] = None,
) -> Dict[float, float]:
    """Compute ATM IV term structure by tenor (years).

    For each expiry, selects ATM options within ``moneyness_tol`` of spot (or
    closest to ATM), averages call/put mid IV (falls back to last/mark), converts
    expiry to years via ``_tenor_years``; returns sorted dict by tenor.
    """
    if not quotes or spot_price is None:
        return {}
    sp = _to_float(spot_price)
    if sp is None or sp <= 0.0:
        return {}
    tol = _to_float(moneyness_tol)
    if tol is None or tol < 0.0:
        tol = 0.02
    by_exp: Dict[str, List[OptionQuote]] = {}
    for q in quotes:
        try:
            key = q.contract.expiry.isoformat()
        except Exception:
            continue
        by_exp.setdefault(key, []).append(q)
    out = {}
    for key, qlist in by_exp.items():
        ivs = []
        for q in qlist:
            m = q.contract.strike / sp
            if not isfinite(m):
                continue
            if abs(m - 1.0) <= tol:
                iv = _get_iv(q)
                if iv is not None:
                    ivs.append(iv)
        if not ivs:
            continue
        atm_iv = sum(ivs) / len(ivs)
        if not isfinite(atm_iv):
            continue
        exp = qlist[0].contract.expiry
        t = _tenor_years(exp, now=now)
        if not isfinite(t):
            continue
        out[float(t)] = float(atm_iv)
    return dict(sorted(out.items()))


def calculate_put_call_ratio_vectorized(quotes: List[OptionQuote]) -> float:
    """Vectorized put/call ratio by volume (identical to `calculate_put_call_ratio`)."""
    if not quotes:
        return 0.0
    types = np.empty(len(quotes), dtype=object)
    volumes = np.zeros(len(quotes), dtype=np.float64)
    for i, q in enumerate(quotes):
        try:
            types[i] = (q.contract.option_type or "").lower()
        except Exception:
            types[i] = ""
        v = _to_float(q.volume)
        volumes[i] = v if v is not None else 0.0
    call_volume = float(volumes[types == "call"].sum())
    put_volume = float(volumes[types == "put"].sum())
    if call_volume == 0.0:
        if put_volume > 0.0:
            return float("inf")
        return 0.0
    ratio = put_volume / call_volume
    if not isfinite(ratio):
        return float("inf") if put_volume > 0.0 else 0.0
    return ratio


def calculate_iv_skew_vectorized(quotes: List[OptionQuote], spot_price: float) -> float:
    """Vectorized IV skew (25-delta put IV - 25-delta call IV).

    Semantically identical to `calculate_iv_skew`.
    """
    if not quotes or spot_price is None:
        return 0.0
    sp = _to_float(spot_price)
    if sp is None or sp <= 0.0:
        return 0.0
    types = np.empty(len(quotes), dtype=object)
    strikes = np.zeros(len(quotes), dtype=np.float64)
    ivs = np.zeros(len(quotes), dtype=np.float64)
    has_iv = np.zeros(len(quotes), dtype=bool)
    for i, q in enumerate(quotes):
        try:
            types[i] = (q.contract.option_type or "").lower()
        except Exception:
            types[i] = ""
        try:
            strikes[i] = float(q.contract.strike)
        except Exception:
            strikes[i] = float("nan")
        iv = _get_iv(q)
        if iv is None:
            continue
        ivs[i] = float(iv)
        has_iv[i] = True
    moneyness = strikes / sp if sp != 0.0 else 0.0
    valid = has_iv & np.isfinite(moneyness)
    otm_puts = ivs[(types == "put") & (moneyness < 0.95) & valid]
    otm_calls = ivs[(types == "call") & (moneyness > 1.05) & valid]
    if otm_puts.size == 0 or otm_calls.size == 0:
        return 0.0
    avg_put_iv = float(otm_puts.mean())
    avg_call_iv = float(otm_calls.mean())
    skew = avg_put_iv - avg_call_iv
    if not isfinite(skew):
        return 0.0
    return skew


def calculate_max_pain_vectorized(chain: OptionsChain) -> float:
    """Vectorized max pain strike (identical to `calculate_max_pain`)."""
    if not chain or not chain.quotes:
        return 0.0
    strikes_set = set()
    for q in chain.quotes:
        s = _to_float(q.contract.strike)
        if s is not None and isfinite(s):
            strikes_set.add(s)
    if not strikes_set:
        return 0.0
    strikes_arr = np.array(sorted(strikes_set), dtype=np.float64)
    types = np.empty(len(chain.quotes), dtype=object)
    quote_strikes = np.zeros(len(chain.quotes), dtype=np.float64)
    ois = np.zeros(len(chain.quotes), dtype=np.float64)
    for i, q in enumerate(chain.quotes):
        try:
            types[i] = (q.contract.option_type or "").lower()
        except Exception:
            types[i] = ""
        try:
            quote_strikes[i] = float(q.contract.strike)
        except Exception:
            quote_strikes[i] = float("nan")
        oi = _to_float(q.open_interest)
        ois[i] = oi if oi is not None else 0.0
    calls = types == "call"
    puts = types == "put"
    min_pain = float("inf")
    max_pain_strike = 0.0
    for strike in strikes_arr:
        call_diff = np.where(quote_strikes < strike, strike - quote_strikes, 0.0)
        put_diff = np.where(quote_strikes > strike, quote_strikes - strike, 0.0)
        total_pain = float((call_diff * ois * calls).sum() + (put_diff * ois * puts).sum())
        if total_pain < min_pain:
            min_pain = total_pain
            max_pain_strike = float(strike)
    if not isfinite(min_pain):
        return 0.0
    return max_pain_strike


# Backwards compatible aliases
put_call_skew = calculate_put_call_skew
risk_reversal = calculate_risk_reversal
skew_term_structure = calculate_skew_term_structure
risk_reversal_term_structure = calculate_risk_reversal_term_structure
iv_skew_term_structure = calculate_iv_skew_term_structure
atm_term_structure = calculate_atm_term_structure
calculate_iv_skew_by_tenor = calculate_iv_skew_term_structure
