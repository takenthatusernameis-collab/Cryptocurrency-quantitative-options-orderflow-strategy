"""Signal Fusion + Gating producing TradeIntent objects."""
from __future__ import annotations

import math
import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.telemetry.serialization import serialize_metrics_strict
from src.signals.composite import CompositeSignalGenerator, Signal


def _finite(x: float, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if math.isfinite(v) else default


@dataclass(frozen=True)
class TradeIntent:
    intent_id: str
    symbol: str
    side: str  # buy/sell
    qty: float
    size_usd: float
    expiry: str
    strike_band: List[float]
    option_type: str
    order_type: str
    limit_logic: str
    rationale_hash: str
    regime: str
    confidence: float
    delta_est: float
    vega_est: float
    gamma_est: float
    dte_days: float
    liquidity_score: float
    risk_flags: List[str]


class SignalFusion:
    def __init__(self, seed: int = 42,
                 max_abs_delta: float = 0.15,
                 max_abs_vega: float = 0.10,
                 gamma_band: float = 0.05,
                 min_liquidity: float = 0.15,
                 min_dte: int = 1,
                 max_dte: int = 90):
        self.seed = int(seed)
        self.max_abs_delta = float(max_abs_delta)
        self.max_abs_vega = float(max_abs_vega)
        self.gamma_band = float(gamma_band)
        self.min_liquidity = float(min_liquidity)
        self.min_dte = int(min_dte)
        self.max_dte = int(max_dte)
        self.regime_gen = CompositeSignalGenerator()

    def _regime(self, features: Dict[str, float]) -> str:
        try:
            sig = self.regime_gen.generate(features)
            return str(getattr(sig, "regime", "normal") or "normal")
        except Exception:
            return "normal"

    def fuse(self, rv_opps: List[Any], of_features: List[Any], price_features: Dict[str, float]) -> List[TradeIntent]:
        intents: List[TradeIntent] = []
        regime = self._regime(price_features)
        # simple weighting
        w_rv = 0.6 if regime in ("low_vol", "normal") else 0.4
        w_of = 0.4 if regime in ("low_vol", "normal") else 0.6
        # build map of orderflow
        of_map = {}
        for f in of_features:
            try:
                of_map[getattr(f, "symbol")] = f
            except Exception:
                pass
        for opp in rv_opps:
            sym = getattr(opp, "symbol")
            liq = _finite(getattr(opp, "liquidity_score", 0.0))
            dte = _finite(getattr(opp, "dte_days", 0.0))
            vega = _finite(getattr(opp, "vega", 0.0))
            if liq < self.min_liquidity:
                continue
            if dte < self.min_dte or dte > self.max_dte:
                continue
            rv_score = abs(_finite(getattr(opp, "residual_sigma_vega_weighted", 0.0)))
            of_s = of_map.get(sym)
            of_score = 0.0
            if of_s is not None:
                of_score = abs(_finite(getattr(of_s, "net_aggression", 0.0))) * 0.5 + abs(_finite(getattr(of_s, "vpin_lite", 0.0))) * 0.5
            conf = _finite(min(1.0, w_rv * rv_score + w_of * of_score))
            if conf < 0.1:
                continue
            delta_est = _finite(min(self.max_abs_delta, rv_score * 0.1))
            vega_est = _finite(min(self.max_abs_vega, abs(vega) * 0.01))
            gamma_est = _finite(min(self.gamma_band, rv_score * 0.01))
            if abs(delta_est) > self.max_abs_delta or abs(vega_est) > self.max_abs_vega or abs(gamma_est) > self.gamma_band:
                continue
            # direction: if residual positive (mark > fitted) maybe fade? or follow flow; deterministic simple rule
            resid = _finite(getattr(opp, "residual_iv", 0.0))
            side = "sell" if resid > 0 else "buy"
            strike = float(getattr(opp, "strike"))
            strike_band = [strike * 0.99, strike * 1.01]
            rationale = f"fuse|{sym}|{side}|{conf:.4f}|{getattr(opp,'rationale_hash','')}"
            rh = hashlib.sha256(rationale.encode("utf-8")).hexdigest()[:16]
            intent_id = hashlib.sha256(f"{sym}|{getattr(opp,'expiry')}|{strike}|{side}|{rh}".encode("utf-8")).hexdigest()[:16]
            intents.append(TradeIntent(
                intent_id=intent_id,
                symbol=sym,
                side=side,
                qty=0.01,
                size_usd=10.0,
                expiry=str(getattr(opp, "expiry")),
                strike_band=strike_band,
                option_type=str(getattr(opp, "option_type")),
                order_type="limit",
                limit_logic="mid+-tick",
                rationale_hash=rh,
                regime=regime,
                confidence=float(conf),
                delta_est=float(delta_est),
                vega_est=float(vega_est),
                gamma_est=float(gamma_est),
                dte_days=float(dte),
                liquidity_score=float(liq),
                risk_flags=[],
            ))
        intents.sort(key=lambda x: (-x.confidence, x.symbol, x.expiry))
        return intents

    def generate_report(self, intents: List[TradeIntent]) -> Dict[str, Any]:
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "git_sha": None,
            "seed": self.seed,
            "count": len(intents),
            "intents": [asdict(i) for i in intents],
        }
        return serialize_metrics_strict(report)
