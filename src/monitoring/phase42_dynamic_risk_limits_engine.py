"""
Phase 42: Dynamic risk limits engine driven by Greeks, margin/collateral,
orderflow liquidity, regime, and cross-venue exposure. Integrates with Phase 40
and kill-switch hooks (Phase 39). Deterministic, PAPER-ONLY.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p42limits|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p42limits_{tag}_{h}"


def _finite(x: float, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if math.isfinite(v) else default


def _assert_finite_dict(d: Dict[str, Any], label: str = "obj") -> None:
    bad: List[str] = []

    def walk(v: Any, p: str) -> None:
        if isinstance(v, dict):
            for k, val in v.items():
                walk(val, f"{p}/{k}")
        elif isinstance(v, (list, tuple)):
            for i, val in enumerate(v):
                walk(val, f"{p}[{i}]")
        elif isinstance(v, float) and not isinstance(v, bool):
            if not math.isfinite(v):
                bad.append(p)

    walk(d, "$")
    if bad:
        raise ValueError(f"Non-finite in {label}: {bad[:10]}")


@dataclass(frozen=True)
class DynamicLimitsConfig42:
    seed: int = 42044
    paper_only: bool = True
    underlyings: Tuple[str, ...] = ("BTC", "ETH", "SOL", "XRP")
    venues: Tuple[str, ...] = ("deribit", "okx", "bybit", "binance")
    cycles: int = 16
    base_delta_limit_usd: float = 600000.0
    base_gamma_limit_usd: float = 300000.0
    base_vega_limit_usd: float = 450000.0
    margin_util_threshold: float = 0.8
    liquidity_min_score: float = 0.4


@dataclass(frozen=True)
class DynamicLimitSet:
    limit_id: str
    underlying: str
    venue: str
    regime: str
    delta_limit_usd: float
    gamma_limit_usd: float
    vega_limit_usd: float
    theta_limit_usd: float
    margin_headroom_usd: float
    orderflow_liquidity_adj: float
    severity: str
    paper_only: bool
    timestamp: str


@dataclass(frozen=True)
class LimitBreach:
    breach_id: str
    underlying: str
    venue: str
    metric: str
    observed_usd: float
    limit_usd: float
    severity: str
    action: str
    kill_switch_hook: bool
    timestamp: str


@dataclass(frozen=True)
class LimitsEvaluation:
    cycle: int
    timestamp: str
    paper_only: bool
    regime: str
    margin_utilization: float
    collateral_available_usd: float
    limit_sets: Tuple[DynamicLimitSet, ...]
    breaches: Tuple[LimitBreach, ...]
    breach_count: int
    max_severity: str
    escalation_required: bool
    trading_enabled: bool
    kill_switch_triggered: bool
    ok: bool
    alerts: Tuple[str, ...]


class Phase42DynamicRiskLimitsEngine:
    def __init__(self, config: Optional[DynamicLimitsConfig42] = None, seed: int = 42044) -> None:
        self.config = config or DynamicLimitsConfig42(seed=seed)
        if not isinstance(self.config.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.config.paper_only:
            raise ValueError("Phase42DynamicRiskLimitsEngine: paper_only must remain True (live path hard-gated)")
        self.config = DynamicLimitsConfig42(
            seed=int(self.config.seed),
            paper_only=True,
            underlyings=tuple(self.config.underlyings),
            venues=tuple(self.config.venues),
            cycles=int(self.config.cycles),
            base_delta_limit_usd=float(self.config.base_delta_limit_usd),
            base_gamma_limit_usd=float(self.config.base_gamma_limit_usd),
            base_vega_limit_usd=float(self.config.base_vega_limit_usd),
            margin_util_threshold=float(self.config.margin_util_threshold),
            liquidity_min_score=float(self.config.liquidity_min_score),
        )
        self.seed = int(self.config.seed)
        self._counter = 0
        self.evals: List[LimitsEvaluation] = []

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        return _make_id(self.seed, tag, self._counter)

    def _regime(self, cycle: int) -> str:
        r = (self.seed + cycle * 13) % 4
        return ("calm", "trend", "volup", "stressed")[r]

    def evaluate(self, cycle: int, greeks_by_venue: Optional[Dict[str, Dict[str, float]]] = None,
                 margin_utilization: float = 0.6, collateral_available_usd: float = 1000000.0,
                 orderflow_liquidity: Optional[Dict[str, float]] = None) -> LimitsEvaluation:
        regime = self._regime(cycle)
        mu = max(0.0, min(1.0, _finite(margin_utilization)))
        collat = _finite(collateral_available_usd)

        if greeks_by_venue is None:
            import random
            rng = random.Random(int(hashlib.sha256(f"{self.seed}|gk|{cycle}".encode()).hexdigest()[:16], 16))
            greeks_by_venue = {}
            for v in self.config.venues[:3]:
                greeks_by_venue[v] = {
                    "delta_usd": rng.uniform(-700000.0, 700000.0),
                    "gamma_usd": rng.uniform(-350000.0, 350000.0),
                    "vega_usd": rng.uniform(-500000.0, 500000.0),
                    "theta_usd": rng.uniform(-200000.0, -50000.0),
                }
        if orderflow_liquidity is None:
            import random
            rng = random.Random(int(hashlib.sha256(f"{self.seed}|liq|{cycle}".encode()).hexdigest()[:16], 16))
            orderflow_liquidity = {v: rng.uniform(0.3, 0.95) for v in self.config.venues[:3]}

        limit_sets: List[DynamicLimitSet] = []
        for v in self.config.venues[:3]:
            liq_adj = orderflow_liquidity.get(v, 0.7)
            regime_adj = 1.0
            if regime == "stressed":
                regime_adj = 0.6
            elif regime == "volup":
                regime_adj = 0.75
            elif regime == "trend":
                regime_adj = 0.9
            margin_adj = 1.0 - 0.3 * mu if mu > self.config.margin_util_threshold else 1.0
            adj = regime_adj * margin_adj * (0.7 + 0.6 * liq_adj)
            sev = "low"
            if adj < 0.7:
                sev = "medium"
            if adj < 0.55 or regime == "stressed":
                sev = "high"
            limit_sets.append(DynamicLimitSet(
                limit_id=self._next_id("lim"),
                underlying="BTC",  # consolidated view simplified
                venue=v,
                regime=regime,
                delta_limit_usd=_finite(self.config.base_delta_limit_usd * adj),
                gamma_limit_usd=_finite(self.config.base_gamma_limit_usd * adj),
                vega_limit_usd=_finite(self.config.base_vega_limit_usd * adj),
                theta_limit_usd=_finite(-abs(self.config.base_delta_limit_usd * 0.25) * adj),
                margin_headroom_usd=_finite(collat * (1.0 - mu)),
                orderflow_liquidity_adj=_finite(liq_adj),
                severity=sev,
                paper_only=True,
                timestamp=_utc_now(),
            ))

        breaches: List[LimitBreach] = []
        for ls in limit_sets:
            gk = greeks_by_venue.get(ls.venue, {})
            d = abs(_finite(gk.get("delta_usd", 0.0)))
            gm = abs(_finite(gk.get("gamma_usd", 0.0)))
            vk = abs(_finite(gk.get("vega_usd", 0.0)))
            if d > ls.delta_limit_usd:
                sev_b = "high" if regime == "stressed" else "medium"
                breaches.append(LimitBreach(
                    breach_id=self._next_id("br"),
                    underlying="BTC",
                    venue=ls.venue,
                    metric="delta",
                    observed_usd=_finite(d),
                    limit_usd=_finite(ls.delta_limit_usd),
                    severity=sev_b,
                    action="reduce_delta|hedge",
                    kill_switch_hook=(sev_b == "high"),
                    timestamp=_utc_now(),
                ))
            if gm > ls.gamma_limit_usd:
                sev_b = "high" if regime in ("stressed", "volup") else "medium"
                breaches.append(LimitBreach(
                    breach_id=self._next_id("br"),
                    underlying="BTC",
                    venue=ls.venue,
                    metric="gamma",
                    observed_usd=_finite(gm),
                    limit_usd=_finite(ls.gamma_limit_usd),
                    severity=sev_b,
                    action="gamma_hedge|size_down",
                    kill_switch_hook=(sev_b == "high" and regime == "stressed"),
                    timestamp=_utc_now(),
                ))
            if vk > ls.vega_limit_usd:
                sev_b = "medium"
                breaches.append(LimitBreach(
                    breach_id=self._next_id("br"),
                    underlying="BTC",
                    venue=ls.venue,
                    metric="vega",
                    observed_usd=_finite(vk),
                    limit_usd=_finite(ls.vega_limit_usd),
                    severity=sev_b,
                    action="vega_reduce|roll",
                    kill_switch_hook=False,
                    timestamp=_utc_now(),
                ))

        breach_count = len(breaches)
        max_sev = "none"
        if breaches:
            if any(b.severity == "high" for b in breaches):
                max_sev = "high"
            elif any(b.severity == "medium" for b in breaches):
                max_sev = "medium"
        escalation_required = breach_count > 0 and (max_sev in ("medium", "high") or mu > self.config.margin_util_threshold)
        kill_switch_triggered = any(b.kill_switch_hook for b in breaches) or (regime == "stressed" and mu > 0.9)
        trading_enabled = not kill_switch_triggered and breach_count == 0
        alerts: List[str] = []
        if mu > self.config.margin_util_threshold:
            alerts.append("margin_util_high")
        if regime == "stressed":
            alerts.append("regime_stressed_dynamic_limits")
        if breach_count > 0:
            alerts.append("risk_breaches_detected")

        ev = LimitsEvaluation(
            cycle=cycle,
            timestamp=_utc_now(),
            paper_only=True,
            regime=regime,
            margin_utilization=_finite(mu),
            collateral_available_usd=_finite(collat),
            limit_sets=tuple(limit_sets),
            breaches=tuple(breaches),
            breach_count=breach_count,
            max_severity=max_sev,
            escalation_required=escalation_required,
            trading_enabled=trading_enabled,
            kill_switch_triggered=kill_switch_triggered,
            ok=(breach_count == 0 and trading_enabled),
            alerts=tuple(alerts),
        )
        _assert_finite_dict(asdict(ev), "LimitsEvaluation")
        self.evals.append(ev)
        return ev

    def run_campaign(self, cycles: Optional[int] = None) -> Dict[str, Any]:
        c = int(cycles) if cycles is not None else int(self.config.cycles)
        evals = []
        import random
        rng = random.Random(self.seed)
        for i in range(1, c + 1):
            mu = rng.uniform(0.5, 0.95)
            collat = rng.uniform(800000.0, 1200000.0)
            evals.append(self.evaluate(i, margin_utilization=mu, collateral_available_usd=collat))
        report = {
            "phase": "PHASE42_DYNAMIC_RISK_LIMITS_ENGINE",
            "seed": self.seed,
            "paper_only": True,
            "cycles": c,
            "evaluations": [asdict(e) for e in evals],
            "total_cycles": len(evals),
            "all_ok": all(e.ok for e in evals),
            "breach_cycles": sum(1 for e in evals if e.breach_count > 0),
            "escalation_cycles": sum(1 for e in evals if e.escalation_required),
            "kill_switch_cycles": sum(1 for e in evals if e.kill_switch_triggered),
        }
        _assert_finite_dict(report, "limits_engine_campaign")
        return report

    def generate_reports(self, outdir: str) -> Dict[str, Any]:
        from pathlib import Path
        import json

        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        camp = self.run_campaign()
        j = out / "PHASE42_DYNAMIC_RISK_LIMITS_ENGINE_REPORT.json"
        j.write_text(json.dumps(camp, indent=2))
        m = out / "PHASE42_DYNAMIC_RISK_LIMITS_ENGINE_REPORT.md"
        m.write_text(f"# Phase 42 Dynamic Risk Limits Engine Report\n\nSeed: {self.seed}\nPaper-only: true\nCycles: {camp['cycles']}\nAll OK: {camp['all_ok']}\nBreach cycles: {camp['breach_cycles']}\nEscalation cycles: {camp['escalation_cycles']}\n")
        return {"json": str(j), "md": str(m)}
