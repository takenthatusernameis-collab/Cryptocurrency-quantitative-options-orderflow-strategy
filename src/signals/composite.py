"""Composite signal generation with regime awareness and confidence calibration."""

from dataclasses import dataclass
from math import isfinite
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence


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
            "iv_greeks": 0.10,
        }
        self.regime_weights: Dict[str, Dict[str, float]] = {
            "high_vol_negative_gex": {"gamma": 0.45, "orderflow": 0.30, "vol_skew": 0.15, "put_call": 0.10, "iv_greeks": 0.15},
            "low_vol_positive_gex": {"gamma": 0.15, "orderflow": 0.25, "vol_skew": 0.30, "put_call": 0.30, "iv_greeks": 0.10},
            "skew_bearish": {"gamma": 0.25, "orderflow": 0.30, "vol_skew": 0.35, "put_call": 0.10, "iv_greeks": 0.20},
            "skew_bullish": {"gamma": 0.25, "orderflow": 0.30, "vol_skew": 0.10, "put_call": 0.35, "iv_greeks": 0.20},
            "neutral": {"gamma": 0.25, "orderflow": 0.30, "vol_skew": 0.25, "put_call": 0.20, "iv_greeks": 0.10},
        }
        # Regime hysteresis state for stability against noisy inputs
        self._prev_regime: str = "neutral"
        self._regime_stability_count: int = 0
        self._hysteresis_threshold: int = 2  # Require N confirmations to flip
        self._regime_flip_penalty: float = 0.7  # Confidence penalty during regime transition
        # Regime transition calibration and adversarial disagreement tracking
        self._regime_transition_history: List[Dict[str, Any]] = []
        self._disagreement_history: List[Dict[str, Any]] = []
        self._transition_calibration_factor: float = 0.85
        self._max_history: int = 1000

    def _extract_iv_surface_features(
        self, iv_surface: Any, spot_price_s: float
    ) -> Dict[str, float]:
        """Extract rich, numerically stable features from an IV surface.

        Returns a dict with skew, term_slope, level, and curvature proxies.
        All values are finite-guarded; missing data yields 0.0.
        """
        feats: Dict[str, float] = {
            "skew": 0.0,
            "term_slope": 0.0,
            "level": 0.0,
            "curvature": 0.0,
        }
        if iv_surface is None:
            return feats
        iv_dict: Dict[str, Any] = {}
        try:
            if isinstance(iv_surface, dict):
                iv_dict = iv_surface
            elif hasattr(iv_surface, "to_dict"):
                d = iv_surface.to_dict()
                if isinstance(d, dict):
                    iv_dict = d
            elif hasattr(iv_surface, "__dict__"):
                iv_dict = dict(getattr(iv_surface, "__dict__", {}))
        except Exception:
            return feats
        points = iv_dict.get("points", []) if isinstance(iv_dict.get("points"), list) else []
        if not points:
            return feats
        try:
            atm_ivs: List[float] = []
            short_ivs: List[float] = []
            long_ivs: List[float] = []
            call_ivs: List[float] = []
            put_ivs: List[float] = []
            for p in points:
                if not isinstance(p, dict):
                    continue
                strike = _safe_float(p.get("strike"), 0.0)
                iv_p = _safe_float(p.get("iv"), float("nan"))
                if not isfinite(iv_p) or iv_p <= 0.0:
                    continue
                tte = _safe_float(p.get("time_to_expiry"), 0.0)
                otype = str(p.get("option_type", "")).strip().lower()
                if otype.startswith("c"):
                    call_ivs.append(iv_p)
                elif otype.startswith("p"):
                    put_ivs.append(iv_p)
                if spot_price_s > 0 and strike > 0:
                    mny = strike / spot_price_s
                    if 0.9 <= mny <= 1.1:
                        atm_ivs.append(iv_p)
                        if tte > 0:
                            if tte < 30.0 / 365.0:
                                short_ivs.append(iv_p)
                            elif tte > 60.0 / 365.0:
                                long_ivs.append(iv_p)
            if atm_ivs:
                feats["level"] = sum(atm_ivs) / len(atm_ivs)
            if call_ivs and put_ivs:
                feats["skew"] = (sum(put_ivs) / len(put_ivs)) - (sum(call_ivs) / len(call_ivs))
            if short_ivs and long_ivs:
                feats["term_slope"] = (sum(long_ivs) / len(long_ivs)) - (sum(short_ivs) / len(short_ivs))
            # Curvature: ATM IV minus average of short and long ATM IVs
            if feats["level"] != 0.0 and short_ivs and long_ivs:
                avg_ends = (sum(short_ivs) / len(short_ivs) + sum(long_ivs) / len(long_ivs)) / 2.0
                feats["curvature"] = feats["level"] - avg_ends
        except Exception:
            pass
        for k in list(feats.keys()):
            feats[k] = _safe_float(feats[k], 0.0)
        return feats

    def _extract_greeks_features(self, greeks_summary: Optional[Dict[str, Any]]) -> Dict[str, float]:
        """Extract normalized Greeks features for signal blending.

        Returns dict with delta_momentum, gamma_exposure, vega_sensitivity,
        theta_decay, and net_greek. All finite-guarded.
        """
        feats: Dict[str, float] = {
            "delta_momentum": 0.0,
            "gamma_exposure": 0.0,
            "vega_sensitivity": 0.0,
            "theta_decay": 0.0,
            "net_greek": 0.0,
        }
        if greeks_summary is None or not isinstance(greeks_summary, dict):
            return feats
        try:
            delta = _safe_float(greeks_summary.get("delta"), 0.0)
            gamma = _safe_float(greeks_summary.get("gamma"), 0.0)
            vega = _safe_float(greeks_summary.get("vega"), 0.0)
            theta = _safe_float(greeks_summary.get("theta"), 0.0)
            # Normalize to bounded ranges for blending stability
            feats["delta_momentum"] = _clamp(delta * 0.15, -0.3, 0.3)
            feats["gamma_exposure"] = _clamp(gamma * 50.0, -0.3, 0.3)
            feats["vega_sensitivity"] = _clamp(vega * 0.02, -0.2, 0.2)
            feats["theta_decay"] = _clamp(-theta * 0.01, -0.1, 0.1)
            feats["net_greek"] = _clamp(
                feats["delta_momentum"] * 0.4 + feats["gamma_exposure"] * 0.35
                + feats["vega_sensitivity"] * 0.15 + feats["theta_decay"] * 0.1,
                -1.0, 1.0,
            )
        except Exception:
            pass
        for k in list(feats.keys()):
            feats[k] = _safe_float(feats[k], 0.0)
        return feats

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
        self._regime_transition_history.clear()
        self._disagreement_history.clear()

    def _calibrate_regime_transition(
        self,
        raw_regime: str,
        current_regime: str,
        total_gex: float,
        iv_skew: float,
        put_call_ratio: float,
    ) -> float:
        """Calibrate regime transitions based on historical patterns and adversarial conditions."""
        calibration_penalty = 1.0
        # Track transition
        if raw_regime != current_regime:
            transition_info = {
                "from": current_regime,
                "to": raw_regime,
                "gex": total_gex,
                "skew": iv_skew,
                "pcr": put_call_ratio,
                "stability_count": self._regime_stability_count,
            }
            self._regime_transition_history.append(transition_info)
            if len(self._regime_transition_history) > self._max_history:
                self._regime_transition_history = self._regime_transition_history[-self._max_history :]
            # More aggressive penalty for rapid/unconfirmed transitions
            if self._regime_stability_count < self._hysteresis_threshold:
                calibration_penalty = self._transition_calibration_factor * self._regime_flip_penalty
            elif self._regime_stability_count < self._hysteresis_threshold + 1:
                calibration_penalty = max(0.75, self._transition_calibration_factor)
            # Extra calibration for adversarial disagreement patterns
            if len(self._disagreement_history) > 0:
                recent_disagreements = [d for d in self._disagreement_history[-10:] if d.get("severe", False)]
                if len(recent_disagreements) >= 3:
                    calibration_penalty *= 0.8
        return calibration_penalty

    def _analyze_disagreement_patterns(self, components: Dict[str, float]) -> Dict[str, Any]:
        """Analyze adversarial disagreement patterns among components for calibration."""
        comp_values = list(components.values())
        if not comp_values:
            return {"severe": False, "ratio": 0.0}
        comp_signs = [_sign(v) for v in comp_values if abs(v) > 1e-12]
        if len(comp_signs) < 2:
            return {"severe": False, "ratio": 1.0}
        has_pos = any(s > 0 for s in comp_signs)
        has_neg = any(s < 0 for s in comp_signs)
        if has_pos and has_neg:
            pos_count = sum(1 for s in comp_signs if s > 0)
            neg_count = sum(1 for s in comp_signs if s < 0)
            majority_ratio = max(pos_count, neg_count) / len(comp_signs)
            if not isfinite(majority_ratio):
                majority_ratio = 0.5
            severe = majority_ratio < 0.67  # High disagreement
            analysis = {"severe": severe, "ratio": majority_ratio, "pos_count": pos_count, "neg_count": neg_count}
            self._disagreement_history.append(analysis)
            if len(self._disagreement_history) > self._max_history:
                self._disagreement_history = self._disagreement_history[-self._max_history :]
            return analysis
        return {"severe": False, "ratio": 1.0}

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
        iv_surface: Any = None,
        greeks_summary: Dict[str, Any] | None = None,
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

        # IV surface / Greeks feature consumption (backward compatible).
        # Features are extracted through the dedicated, numerically guarded
        # helpers so IV surface and Greeks meaningfully drive signal
        # components rather than living only in metadata. When IV/Greeks are
        # absent all features are 0.0, preserving existing behavior exactly.
        iv_feats = self._extract_iv_surface_features(iv_surface, spot_price_s)
        greek_feats = self._extract_greeks_features(greeks_summary)

        iv_surf_factor = 0.0
        if iv_surface is not None:
            # Surface skew and term structure move the gamma/skew components.
            iv_surf_factor += _clamp(iv_feats["skew"] * 2.0, -0.3, 0.3)
            iv_surf_factor += _clamp(iv_feats["term_slope"] * 1.5, -0.15, 0.15)
            # Explicit iv_skew input refines the surface read.
            if iv_skew_s != 0.0:
                iv_surf_factor += _clamp(-iv_skew_s * 0.15, -0.15, 0.15)

        greeks_factor = 0.0
        if greeks_summary is not None and isinstance(greeks_summary, dict):
            # Gamma exposure amplifies flow, delta positions the bias, vega
            # scales volatility sensitivity.
            if greek_feats["gamma_exposure"] != 0.0:
                greeks_factor += _clamp(greek_feats["gamma_exposure"], -0.2, 0.2)
            if greek_feats["delta_momentum"] != 0.0:
                greeks_factor += _clamp(greek_feats["delta_momentum"], -0.1, 0.1)
            if greek_feats["vega_sensitivity"] != 0.0:
                greeks_factor += _clamp(greek_feats["vega_sensitivity"], -0.05, 0.05)

        # Blend IV/Greeks into gamma component (backward compatible, additive)
        gamma_signal = _clamp(gamma_signal + iv_surf_factor * 1.2 + greeks_factor * 0.85, -1.0, 1.0)
        components["gamma"] = _clamp(gamma_signal, -1.0, 1.0)

        of_signal = (cum_delta_s / 10000.0 + of_imbalance_s) / 2.0
        # Incorporate Greeks delta/gamma/vega/theta into orderflow more deeply
        if greeks_summary is not None and isinstance(greeks_summary, dict):
            if greek_feats["delta_momentum"] != 0.0:
                of_signal = _clamp(of_signal + greek_feats["delta_momentum"] * 0.5, -1.0, 1.0)
            if greek_feats["gamma_exposure"] != 0.0:
                of_signal = _clamp(of_signal + _clamp(greek_feats["gamma_exposure"] * 0.5, -0.15, 0.15), -1.0, 1.0)
            if greek_feats["vega_sensitivity"] != 0.0:
                of_signal = _clamp(of_signal + _clamp(greek_feats["vega_sensitivity"] * 0.4, -0.08, 0.08), -1.0, 1.0)
            if greek_feats["theta_decay"] != 0.0:
                of_signal = _clamp(of_signal - _clamp(greek_feats["theta_decay"] * 0.5, -0.05, 0.05), -1.0, 1.0)
        # Blend IV surface directly into orderflow
        if iv_surface is not None and iv_surf_factor != 0.0:
            of_signal = _clamp(of_signal + iv_surf_factor * 0.4, -1.0, 1.0)
        components["orderflow"] = _clamp(of_signal, -1.0, 1.0)

        skew_signal = -_clamp(iv_skew_s * 10.0, -1.0, 1.0)
        # Enhance vol_skew with IV surface term structure and skew
        if iv_surface is not None:
            skew_signal = _clamp(skew_signal + iv_feats["skew"] * 1.0, -1.0, 1.0)
            skew_signal = _clamp(skew_signal + iv_feats["term_slope"] * 2.0, -1.0, 1.0)
            if iv_surf_factor != 0.0:
                skew_signal = _clamp(skew_signal + iv_surf_factor * 0.8, -1.0, 1.0)
        # Greeks vega tilt
        if greeks_summary is not None and isinstance(greeks_summary, dict):
            if greek_feats["vega_sensitivity"] != 0.0:
                skew_signal = _clamp(skew_signal + _clamp(greek_feats["vega_sensitivity"] * 0.4, -0.08, 0.08), -1.0, 1.0)
        components["vol_skew"] = _clamp(skew_signal, -1.0, 1.0)

        # iv_greeks component: net Greek exposure blended with IV surface skew,
        # so the iv_greeks weight present in every regime actually drives the
        # composite. Zero when IV/Greeks are absent (backward compatible).
        iv_greeks_signal = _clamp(
            greek_feats["net_greek"] * 0.7 + iv_feats["skew"] * 0.3,
            -1.0, 1.0,
        )
        components["iv_greeks"] = _clamp(iv_greeks_signal, -1.0, 1.0)

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
                # Track disagreement patterns
                self._analyze_disagreement_patterns(components)
                # A clear majority consensus (>= 0.75) is directional consensus, not
                # disagreement: preserve the composite sign/magnitude so a strong
                # majority is not flattened into neutrality. Apply direction-flattening
                # penalties only when there is genuine component disagreement.
                if majority_ratio < 0.67:
                    composite = composite * 0.4
                elif majority_ratio < 0.75:
                    composite = composite * 0.75
                composite = _clamp(composite, -1.0, 1.0)
            else:
                # Still track for consistency
                self._analyze_disagreement_patterns(components)

        # Apply regime transition penalty for stability
        raw_regime_check = self._detect_regime_raw(total_gex_s, iv_skew_s, put_call_ratio_s)
        if raw_regime_check != self._prev_regime and self._regime_stability_count < self._hysteresis_threshold:
            composite = composite * self._regime_flip_penalty
            composite = _clamp(composite, -1.0, 1.0)

        # Enhanced regime transition calibration
        trans_calibration = self._calibrate_regime_transition(raw_regime_check, self._prev_regime, total_gex_s, iv_skew_s, put_call_ratio_s)
        if trans_calibration < 1.0:
            composite = composite * trans_calibration
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

        confidence = confidence * self._regime_flip_penalty
        confidence = _clamp(confidence, 0.0, 1.0)

        # Build metadata with IV surface and Greeks info (store them as accepted)
        meta: Dict[str, Any] = {}
        try:
            if iv_surface is not None:
                meta["iv_surface"] = iv_surface
        except Exception:
            pass
        try:
            if greeks_summary is not None:
                meta["greeks_summary"] = greeks_summary
        except Exception:
            pass
        try:
            if pin_zone_info:
                meta["pin_zone"] = pin_zone_info
            if flip_zone_info:
                meta["flip_zones"] = flip_zone_info
        except Exception:
            pass

        signal = Signal(
            symbol=symbol,
            direction=direction,
            strength=composite,
            confidence=confidence,
            components=components,
            regime=regime,
            metadata=meta if meta else None,
        )
        return signal

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

    def get_regime_stability_metrics(self) -> Dict[str, Any]:
        """Get regime transition calibration and stability metrics."""
        return {
            "current_regime": self._prev_regime,
            "stability_count": self._regime_stability_count,
            "hysteresis_threshold": self._hysteresis_threshold,
            "transition_count": len(self._regime_transition_history),
            "disagreement_count": len(self._disagreement_history),
            "recent_transitions": self._regime_transition_history[-5:] if self._regime_transition_history else [],
            "recent_disagreements": self._disagreement_history[-5:] if self._disagreement_history else [],
        }

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
                iv_surface = it.get("iv_surface") or it.get("iv_surfaces")
                greeks_summary = it.get("greeks_summary") or it.get("greeks")
                sig = self.generate_signal(
                    symbol=symbol,
                    spot_price=spot_price,
                    total_gex=total_gex,
                    cum_delta=cum_delta,
                    of_imbalance=of_imbalance,
                    iv_skew=iv_skew,
                    put_call_ratio=put_call_ratio,
                    chain=chain,
                    iv_surface=iv_surface,
                    greeks_summary=greeks_summary,
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
