"""Composite signal generation with regime awareness and confidence calibration."""

from dataclasses import dataclass
from math import isfinite
from typing import Any, Dict, Iterable, List, Mapping, Sequence


@dataclass
class Signal:
    symbol: str
    direction: str  # 'long', 'short', 'neutral'
    strength: float  # -1 to 1
    confidence: float  # 0 to 1
    components: Dict[str, float]
    regime: str = "unknown"
    metadata: Dict[str, Any] | None = None


def _sign(x: float) -> float:
    if not isfinite(x):
        return 0.0
    if x > 0:
        return 1.0
    elif x < 0:
        return -1.0
    return 0.0


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    if not isfinite(v):
        return default
    return v


def _clamp(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    if not isfinite(x):
        return 0.0 if lo <= 0.0 <= hi else lo
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


class CompositeSignalGenerator:
    """Regime-aware composite signal generator.

    Detects market regime from GEX sign/magnitude and skew, then adjusts
    component weights accordingly. Confidence reflects component agreement
    (dispersion), not just |composite|. Hardened against degenerate/non-finite
    inputs with feature-leakage safe, deterministic behavior.
    """

    def __init__(self) -> None:
        self.base_weights: Dict[str, float] = {
            "gamma": 0.25,
            "orderflow": 0.30,
            "vol_skew": 0.25,
            "put_call": 0.20,
        }
        self.regime_weights: Dict[str, Dict[str, float]] = {
            "high_vol_negative_gex": {"gamma": 0.45, "orderflow": 0.30, "vol_skew": 0.15, "put_call": 0.10},
            "low_vol_positive_gex": {"gamma": 0.15, "orderflow": 0.25, "vol_skew": 0.30, "put_call": 0.30},
            "skew_bearish": {"gamma": 0.25, "orderflow": 0.30, "vol_skew": 0.35, "put_call": 0.10},
            "skew_bullish": {"gamma": 0.25, "orderflow": 0.30, "vol_skew": 0.10, "put_call": 0.35},
            "neutral": {"gamma": 0.25, "orderflow": 0.30, "vol_skew": 0.25, "put_call": 0.20},
        }
        # Regime hysteresis state for stability against noisy inputs
        self._prev_regime: str = "neutral"
        self._regime_stability_count: int = 0
        self._hysteresis_threshold: int = 2  # Require N confirmations to flip
        self._regime_flip_penalty: float = 0.7  # Confidence penalty during regime transition

    def _detect_regime_raw(self, total_gex: float, iv_skew: float, put_call_ratio: float) -> str:
        gex = _safe_float(total_gex, 0.0)
        skew = _safe_float(iv_skew, 0.0)
        pcr = _safe_float(put_call_ratio, 1.0)
        if pcr <= 0.0:
            pcr = 1.0
        if gex < -1e8:
            return "high_vol_negative_gex"
        if gex > 1e8:
            return "low_vol_positive_gex"
        if skew > 0.05:
            return "skew_bearish"
        if skew < -0.05:
            return "skew_bullish"
        if skew > 0.02 and pcr > 1.2:
            return "high_vol_negative_gex"
        if skew < -0.02 and pcr < 0.8:
            return "low_vol_positive_gex"
        return "neutral"

    def _detect_regime(self, total_gex: float, iv_skew: float, put_call_ratio: float) -> str:
        raw_regime = self._detect_regime_raw(total_gex, iv_skew, put_call_ratio)
        # Apply hysteresis to prevent rapid regime flipping
        # First regime detection or after reset - set immediately
        if self._regime_stability_count == 0 and self._prev_regime == "neutral":
            # Check if this is first detection - initialize
            self._prev_regime = raw_regime
            self._regime_stability_count = 1
            return raw_regime
        if raw_regime == self._prev_regime:
            self._regime_stability_count += 1
            return raw_regime
        else:
            # Different regime detected - require confirmation
            if self._regime_stability_count >= self._hysteresis_threshold:
                # Sufficient stability in previous regime, allow flip
                self._prev_regime = raw_regime
                self._regime_stability_count = 1
                return raw_regime
            else:
                # Not enough confirmation yet, stick with previous regime
                self._regime_stability_count += 1
                return self._prev_regime

    def reset_regime_state(self) -> None:
        """Reset regime hysteresis state (useful for backtesting independence)."""
        self._prev_regime = "neutral"
        self._regime_stability_count = 0

    def _get_weights(self, regime: str) -> Dict[str, float]:
        w = self.regime_weights.get(regime, self.regime_weights["neutral"]).copy()
        s = sum(w.values())
        if not isfinite(s) or s <= 0.0:
            w = self.regime_weights["neutral"].copy()
            s = sum(w.values())
        if s > 0.0:
            for k in list(w.keys()):
                w[k] = w[k] / s
        return w

    def generate_signal(
        self,
        symbol: str,
        spot_price: float = 0.0,
        total_gex: float = 0.0,
        cum_delta: float = 0.0,
        of_imbalance: float = 0.0,
        iv_skew: float = 0.0,
        put_call_ratio: float = 1.0,
        chain: Any = None,
        **kwargs: Any,
    ) -> Signal:
        spot_price_s = _safe_float(spot_price, 0.0)
        total_gex_s = _safe_float(total_gex, 0.0)
        cum_delta_s = _safe_float(cum_delta, 0.0)
        of_imbalance_s = _safe_float(of_imbalance, 0.0)
        iv_skew_s = _safe_float(iv_skew, 0.0)
        put_call_ratio_s = _safe_float(put_call_ratio, 1.0)
        if put_call_ratio_s <= 0.0:
            put_call_ratio_s = 1.0

        pin_zone_info: Dict[str, Any] = {}
        flip_zone_info: Dict[str, Any] = {}
        if chain is not None:
            try:
                from ..features.gamma_exposure import calculate_pin_zone, calculate_flip_zones

                try:
                    pz = calculate_pin_zone(chain, spot_price_s)
                    if isinstance(pz, dict):
                        pin_zone_info = {k: _safe_float(v, 0.0) for k, v in pz.items()}
                except Exception:
                    pin_zone_info = {}
                try:
                    fz = calculate_flip_zones(chain, spot_price_s)
                    if isinstance(fz, dict):
                        flip_zone_info = {k: _safe_float(v, 0.0) for k, v in fz.items()}
                except Exception:
                    flip_zone_info = {}
            except Exception:
                pin_zone_info = {}
                flip_zone_info = {}

        components: Dict[str, float] = {}

        if total_gex_s != 0.0 and isfinite(total_gex_s):
            gamma_signal = -_sign(total_gex_s) * min(abs(total_gex_s) / 1e9, 1.0)
        else:
            gamma_signal = 0.0
        components["gamma"] = _clamp(gamma_signal, -1.0, 1.0)

        of_signal = (cum_delta_s / 10000.0 + of_imbalance_s) / 2.0
        components["orderflow"] = _clamp(of_signal, -1.0, 1.0)

        skew_signal = -_clamp(iv_skew_s * 10.0, -1.0, 1.0)
        components["vol_skew"] = _clamp(skew_signal, -1.0, 1.0)

        pcr = put_call_ratio_s
        if pcr > 1.0:
            pc_signal = -_clamp((pcr - 1.0) / 2.0, 0.0, 1.0)
        elif pcr < 1.0:
            pc_signal = _clamp((1.0 - pcr) / 0.5, 0.0, 1.0) * 0.5
        else:
            pc_signal = 0.0
        components["put_call"] = _clamp(pc_signal, -1.0, 1.0)

        regime = self._detect_regime(total_gex_s, iv_skew_s, put_call_ratio_s)
        weights = self._get_weights(regime)

        composite = 0.0
        for k in sorted(weights.keys()):
            composite += weights[k] * components.get(k, 0.0)
        composite = _clamp(composite, -1.0, 1.0)

        comp_values = list(components.values())
        comp_signs = [_sign(v) for v in comp_values if abs(v) > 1e-12]
        if len(comp_signs) >= 2:
            has_pos = any(s > 0 for s in comp_signs)
            has_neg = any(s < 0 for s in comp_signs)
            if has_pos and has_neg:
                pos_count = sum(1 for s in comp_signs if s > 0)
                neg_count = sum(1 for s in comp_signs if s < 0)
                majority_ratio = max(pos_count, neg_count) / len(comp_signs)
                if not isfinite(majority_ratio):
                    majority_ratio = 0.5
                if majority_ratio >= 0.75:
                    composite = composite * 0.85
                elif majority_ratio >= 0.67:
                    composite = composite * 0.75
                else:
                    composite = composite * 0.4
                composite = _clamp(composite, -1.0, 1.0)

        # Apply regime transition penalty for stability
        raw_regime_check = self._detect_regime_raw(total_gex_s, iv_skew_s, put_call_ratio_s)
        if raw_regime_check != self._prev_regime and self._regime_stability_count < self._hysteresis_threshold:
            composite = composite * self._regime_flip_penalty
            composite = _clamp(composite, -1.0, 1.0)

        if composite > 0.3:
            direction = "long"
        elif composite < -0.3:
            direction = "short"
        else:
            direction = "neutral"

        comp_values = list(components.values())
        if comp_values:
            mean_abs = sum(abs(v) for v in comp_values) / len(comp_values)
            if not isfinite(mean_abs):
                mean_abs = 0.0
            if composite != 0.0 and isfinite(composite):
                comp_sign = _sign(composite)
                agreements = sum(1 for v in comp_values if _sign(v) == comp_sign)
                agreement_ratio = agreements / len(comp_values)
            else:
                agreement_ratio = 0.0
            dispersion = sum((abs(v) - mean_abs) ** 2 for v in comp_values) / len(comp_values)
            if not isfinite(dispersion) or dispersion < 0.0:
                dispersion = 0.0
            dispersion = dispersion ** 0.5
            max_dispersion = 1.0
            agreement_confidence = _clamp(agreement_ratio, 0.0, 1.0)
            if max_dispersion > 0.0:
                dispersion_confidence = _clamp(1.0 - dispersion / max_dispersion, 0.0, 1.0)
            else:
                dispersion_confidence = 0.0
            magnitude_confidence = _clamp(abs(composite), 0.0, 1.0)
            confidence = 0.4 * agreement_confidence + 0.3 * dispersion_confidence + 0.3 * magnitude_confidence
        else:
            confidence = 0.0
        confidence = _clamp(confidence, 0.0, 1.0)

        # Additional penalty during uncertain regime transitions
        raw_regime_check_final = self._detect_regime_raw(total_gex_s, iv_skew_s, put_call_ratio_s)
        if raw_regime_check_final != self._prev_regime and self._regime_stability_count < self._hysteresis_threshold:
            confidence = confidence * self._regime_flip_penalty
            confidence = _clamp(confidence, 0.0, 1.0)

        return Signal(
            symbol=symbol,
            direction=direction,
            strength=float(composite),
            confidence=float(confidence),
            components=components,
            regime=regime,
            metadata={"pin_zone": pin_zone_info, "flip_zones": flip_zone_info} if (pin_zone_info or flip_zone_info) else None,
        )

    def generate_signals_batch(
        self,
        items: Iterable[Mapping[str, Any]] | Sequence[Mapping[str, Any]],
        reset_regime: bool = False,
    ) -> List[Signal]:
        """Generate signals for a batch of inputs with deterministic ordering.

        Preserves regime hysteresis state across the batch (sequential processing)
        for parity with time-ordered streams. Set reset_regime=True to start
        from neutral state for this batch (useful for independent evaluation).
        """
        if reset_regime:
            self.reset_regime_state()
        results: List[Signal] = []
        # Iterate in deterministic order
        try:
            seq = list(items)
        except Exception:
            return results
        for it in seq:
            if not isinstance(it, Mapping):
                continue
            try:
                symbol = it.get("symbol") or it.get("ticker") or ""
                if not isinstance(symbol, str):
                    symbol = str(symbol)
                spot_price = it.get("spot_price", it.get("spot", 0.0))
                total_gex = it.get("total_gex", it.get("gex", 0.0))
                cum_delta = it.get("cum_delta", it.get("delta", 0.0))
                of_imbalance = it.get("of_imbalance", it.get("orderflow_imbalance", 0.0))
                iv_skew = it.get("iv_skew", it.get("skew", 0.0))
                put_call_ratio = it.get("put_call_ratio", it.get("pcr", 1.0))
                chain = it.get("chain")
                sig = self.generate_signal(
                    symbol=symbol,
                    spot_price=spot_price,
                    total_gex=total_gex,
                    cum_delta=cum_delta,
                    of_imbalance=of_imbalance,
                    iv_skew=iv_skew,
                    put_call_ratio=put_call_ratio,
                    chain=chain,
                )
                results.append(sig)
            except Exception:
                # On any error, produce a safe neutral signal to maintain determinism
                try:
                    symbol_e = ""
                    it_e = it
                    if isinstance(it_e, Mapping):
                        sym = it_e.get("symbol") or it_e.get("ticker") or ""
                        if isinstance(sym, str):
                            symbol_e = sym
                        else:
                            symbol_e = str(sym)
                    results.append(
                        Signal(
                            symbol=symbol_e,
                            direction="neutral",
                            strength=0.0,
                            confidence=0.0,
                            components={"gamma": 0.0, "orderflow": 0.0, "vol_skew": 0.0, "put_call": 0.0},
                            regime=self._prev_regime if hasattr(self, "_prev_regime") else "neutral",
                            metadata=None,
                        )
                    )
                except Exception:
                    continue
        return results

    def generate_signals_vectorized(
        self,
        items: Iterable[Mapping[str, Any]] | Sequence[Mapping[str, Any]],
        reset_regime: bool = False,
    ) -> List[Signal]:
        """Vectorized-style batch API with identical behavior to generate_signals_batch."""
        return self.generate_signals_batch(items, reset_regime=reset_regime)
