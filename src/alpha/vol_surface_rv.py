"""Volatility Surface Relative Value Engine (crypto options)."""
from __future__ import annotations

import math
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.data.schemas import OptionsChain, OptionQuote, PricingInputs
from src.features.iv_surface import IVSurface, build_iv_surface_from_chain
from src.features.options_pricing import black_scholes_greeks
from src.telemetry.serialization import serialize_metrics_strict


def _finite(x: float, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if math.isfinite(v) else default


@dataclass(frozen=True)
class RVOpportunity:
    symbol: str
    venue: str
    expiry: str
    strike: float
    option_type: str
    mark_iv: float
    fitted_iv: float
    residual_iv: float
    residual_sigma_vega_weighted: float
    vega: float
    mid_price: float
    dte_days: float
    moneyness: float
    liquidity_score: float
    arb_ok: bool
    rationale_hash: str


@dataclass
class VolSurfaceRVConfig:
    min_liquidity: float = 0.1
    min_vega: float = 0.01
    rv_threshold_iv: float = 0.005
    rv_threshold_vega_wt: float = 0.02
    max_dte: int = 180
    min_dte: int = 1
    butter_calendar_check: bool = True
    seed: int = 42


class VolSurfaceRVEngine:
    def __init__(self, config: Optional[VolSurfaceRVConfig] = None):
        self.config = config or VolSurfaceRVConfig()

    def fit_surface(self, chain: OptionsChain, spot: float, rate: float = 0.0) -> IVSurface:
        surface = build_iv_surface_from_chain(chain, spot=spot, rate=rate, seed=self.config.seed)
        return surface

    def _liquidity_score(self, q: OptionQuote) -> float:
        bid = _finite(q.bid)
        ask = _finite(q.ask)
        vol = _finite(getattr(q, "volume", 0.0))
        oi = _finite(getattr(q, "open_interest", 0.0))
        spr = 0.0
        if bid > 0 and ask > 0 and ask >= bid:
            mid = 0.5 * (bid + ask)
            spr = (ask - bid) / mid if mid > 1e-18 else 1.0
        score = math.exp(-5.0 * spr) * (1.0 + 0.0001 * vol + 0.00001 * oi)
        return _finite(min(1.0, max(0.0, score)))

    def detect_dislocations(self, chain: OptionsChain, spot: float, rate: float = 0.0,
                            now: Optional[datetime] = None) -> List[RVOpportunity]:
        now = now or datetime.now(timezone.utc)
        surface = self.fit_surface(chain, spot, rate)
        opps: List[RVOpportunity] = []
        for q in chain.quotes:
            c = q.contract
            ot = str(getattr(c, "option_type", "")).strip().lower()
            if ot not in ("call", "put"):
                continue
            exp = getattr(c, "expiry")
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            dte_days = (exp - now).total_seconds() / 86400.0
            if dte_days < self.config.min_dte or dte_days > self.config.max_dte:
                continue
            T = max(1e-12, dte_days / 365.25)
            liq = self._liquidity_score(q)
            if liq < self.config.min_liquidity:
                continue
            bid = _finite(q.bid)
            ask = _finite(q.ask)
            if bid <= 0 or ask <= 0 or ask < bid:
                continue
            mid = 0.5 * (bid + ask)
            mark_iv = _finite(getattr(q, "mark_iv", None) or getattr(q, "bid_iv", None) or getattr(q, "ask_iv", None))
            if mark_iv <= 0:
                continue
            strike = float(getattr(c, "strike"))
            fitted_iv = surface.get_iv(strike, T, ot)
            fitted_iv = _finite(fitted_iv)
            residual_iv = mark_iv - fitted_iv
            try:
                g = black_scholes_greeks(PricingInputs(spot=spot, strike=strike, time_to_expiry=T,
                                                       risk_free_rate=rate, volatility=fitted_iv, option_type=ot))
                vega = _finite(g.get("vega", 0.0))
            except Exception:
                vega = 0.0
            if abs(vega) < self.config.min_vega:
                continue
            vega_wt_resid = residual_iv / (abs(vega) + 1e-12)
            arb_ok = True
            if self.config.butter_calendar_check:
                arb_ok = math.isfinite(residual_iv) and 0.0 < fitted_iv < 5.0 and 0.0 < mark_iv < 5.0
            if abs(residual_iv) < self.config.rv_threshold_iv and abs(vega_wt_resid) < self.config.rv_threshold_vega_wt:
                continue
            moneyness = _finite(strike / spot) if spot > 0 else 1.0
            rationale = f"rv|{chain.underlying}|{exp.date()}|{strike}|{ot}|{residual_iv:.6f}|{vega_wt_resid:.6f}"
            rh = hashlib.sha256(rationale.encode("utf-8")).hexdigest()[:16]
            opps.append(RVOpportunity(
                symbol=chain.underlying,
                venue=chain.venue,
                expiry=exp.isoformat(),
                strike=float(strike),
                option_type=ot,
                mark_iv=float(mark_iv),
                fitted_iv=float(fitted_iv),
                residual_iv=float(residual_iv),
                residual_sigma_vega_weighted=float(vega_wt_resid),
                vega=float(vega),
                mid_price=float(mid),
                dte_days=float(dte_days),
                moneyness=float(moneyness),
                liquidity_score=float(liq),
                arb_ok=bool(arb_ok),
                rationale_hash=rh,
            ))
        opps.sort(key=lambda x: (-abs(x.residual_sigma_vega_weighted), -x.liquidity_score, x.dte_days, x.strike))
        return opps

    def generate_report(self, opps: List[RVOpportunity], seed: int) -> Dict[str, Any]:
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "git_sha": None,
            "seed": int(seed),
            "symbols": sorted(list({o.symbol for o in opps})),
            "count": len(opps),
            "opportunities": [],
        }
        for o in opps:
            report["opportunities"].append({
                "symbol": o.symbol,
                "venue": o.venue,
                "expiry": o.expiry,
                "strike": o.strike,
                "option_type": o.option_type,
                "mark_iv": o.mark_iv,
                "fitted_iv": o.fitted_iv,
                "residual_iv": o.residual_iv,
                "residual_sigma_vega_weighted": o.residual_sigma_vega_weighted,
                "vega": o.vega,
                "mid_price": o.mid_price,
                "dte_days": o.dte_days,
                "moneyness": o.moneyness,
                "liquidity_score": o.liquidity_score,
                "arb_ok": o.arb_ok,
                "rationale_hash": o.rationale_hash,
            })
        return serialize_metrics_strict(report)
