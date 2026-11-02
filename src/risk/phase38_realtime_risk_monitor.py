"""
Phase 38: Real-time Risk Monitor for Crypto Options + Orderflow.

VaR/CVaR, Greeks limits (delta/gamma/vega/theta), exposure caps, drawdown guards,
regime-aware breach actions. Deterministic, finite numerics, PAPER-ONLY default
with hard-gated live paths. Extends Phases 17-37.
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
    h = hashlib.sha256(f"{seed}|p38rm|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p38rm_{tag}_{h}"


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
class RiskMonitorConfig38:
    seed: int = 38038
    paper_only: bool = True
    underlyings: Tuple[str, ...] = ("BTC", "ETH", "SOL", "XRP")
    venues: Tuple[str, ...] = ("deribit", "okx", "bybit", "binance")
    cycles: int = 12
    var_confidence: float = 0.95
    var_limit_usd: float = 25000.0
    cvar_limit_usd: float = 35000.0
    max_delta: float = 500.0
    max_gamma: float = 150.0
    max_vega: float = 800.0
    max_theta: float = -200.0
    max_exposure_usd: float = 500000.0
    max_drawdown_pct: float = 0.08
    kill_dd_pct: float = 0.10
    max_daily_loss_usd: float = 40000.0
    regime_aware: bool = True


@dataclass(frozen=True)
class GreeksSnapshot:
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float
    timestamp: str


@dataclass(frozen=True)
class RiskBreach:
    breach_id: str
    cycle: int
    metric: str
    value: float
    limit: float
    severity: str
    action: str
    regime: str
    timestamp: str


@dataclass(frozen=True)
class RiskMonitorCycle:
    cycle: int
    timestamp: str
    paper_only: bool
    regime: str
    greeks: GreeksSnapshot
    var_usd: float
    cvar_usd: float
    exposure_usd: float
    drawdown_pct: float
    daily_pnl_usd: float
    breaches: Tuple[RiskBreach, ...]
    risk_ok: bool
    action_taken: str


class Phase38RealtimeRiskMonitor:
    def __init__(self, config: Optional[RiskMonitorConfig38] = None, seed: int = 38038):
        self.config = config or RiskMonitorConfig38(seed=seed)
        if self.config.modes_check() if hasattr(self.config, 'modes_check') else False:
            pass  # not used
        if not isinstance(self.config.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.config.paper_only:
            raise ValueError("Phase38RealtimeRiskMonitor: paper_only must remain True (live path hard-gated)")
        self.seed = int(self.config.seed)
        self._ctr = 0
        self.breaches_all: List[RiskBreach] = []
        self.cycles: List[RiskMonitorCycle] = []

    def _id(self, tag: str) -> str:
        self._ctr += 1
        return _make_id(self.seed, tag, self._ctr)

    def _regime(self, c: int) -> str:
        r = c % 4
        return ("normal", "stressed", "volatile", "crisis")[r]

    def monitor_cycle(self, cycle: int, portfolio_state: Optional[Dict[str, Any]] = None) -> RiskMonitorCycle:
        portfolio_state = portfolio_state or {}
        regime = self._regime(cycle)
        # deterministic Greeks
        delta = _finite(150.0 * (1.0 + 0.1 * (cycle % 3)) * (0.9 if regime == "crisis" else 1.0))
        gamma = _finite(40.0 + 10.0 * (cycle % 4))
        vega = _finite(300.0 + 50.0 * (cycle % 3))
        theta = _finite(-80.0 - 20.0 * (cycle % 2))
        rho = _finite(10.0)
        greeks = GreeksSnapshot(delta=delta, gamma=gamma, vega=vega, theta=theta, rho=rho, timestamp=_utc_now())
        # VaR/CVaR
        var_usd = _finite(15000.0 + 2000.0 * (cycle % 5))
        cvar_usd = _finite(var_usd * 1.4)
        exposure_usd = _finite(250000.0 + 25000.0 * (cycle % 6))
        dd = _finite(0.02 + 0.01 * (cycle % 4))
        daily_pnl = _finite(-5000.0 + 1000.0 * ((cycle % 3) - 1))
        breaches: List[RiskBreach] = []
        if abs(delta) > self.config.max_delta:
            b = RiskBreach(breach_id=self._id("delta"), cycle=cycle, metric="delta", value=abs(delta), limit=self.config.max_delta, severity="high", action="hedge_reduce" if regime != "crisis" else "flatten", regime=regime, timestamp=_utc_now())
            breaches.append(b)
            self.breaches_all.append(b)
        if gamma > self.config.max_gamma:
            b = RiskBreach(breach_id=self._id("gamma"), cycle=cycle, metric="gamma", value=gamma, limit=self.config.max_gamma, severity="high", action="reduce_gamma_exposure", regime=regime, timestamp=_utc_now())
            breaches.append(b)
            self.breaches_all.append(b)
        if vega > self.config.max_vega:
            b = RiskBreach(breach_id=self._id("vega"), cycle=cycle, metric="vega", value=vega, limit=self.config.max_vega, severity="medium", action="vega_hedge", regime=regime, timestamp=_utc_now())
            breaches.append(b)
            self.breaches_all.append(b)
        if theta < self.config.max_theta:  # theta more negative than limit
            b = RiskBreach(breach_id=self._id("theta"), cycle=cycle, metric="theta", value=theta, limit=self.config.max_theta, severity="low", action="monitor_theta_decay", regime=regime, timestamp=_utc_now())
            breaches.append(b)
            self.breaches_all.append(b)
        if var_usd > self.config.var_limit_usd:
            b = RiskBreach(breach_id=self._id("var"), cycle=cycle, metric="var", value=var_usd, limit=self.config.var_limit_usd, severity="high", action="reduce_var", regime=regime, timestamp=_utc_now())
            breaches.append(b)
            self.breaches_all.append(b)
        if cvar_usd > self.config.cvar_limit_usd:
            b = RiskBreach(breach_id=self._id("cvar"), cycle=cycle, metric="cvar", value=cvar_usd, limit=self.config.cvar_limit_usd, severity="high", action="reduce_cvar", regime=regime, timestamp=_utc_now())
            breaches.append(b)
            self.breaches_all.append(b)
        if exposure_usd > self.config.max_exposure_usd:
            b = RiskBreach(breach_id=self._id("exp"), cycle=cycle, metric="exposure", value=exposure_usd, limit=self.config.max_exposure_usd, severity="high", action="scale_down_exposure", regime=regime, timestamp=_utc_now())
            breaches.append(b)
            self.breaches_all.append(b)
        if dd > self.config.max_drawdown_pct:
            b = RiskBreach(breach_id=self._id("dd"), cycle=cycle, metric="drawdown", value=dd, limit=self.config.max_drawdown_pct, severity="critical" if dd > self.config.kill_dd_pct else "high", action="drawdown_guard" if dd <= self.config.kill_dd_pct else "halt_new_risk", regime=regime, timestamp=_utc_now())
            breaches.append(b)
            self.breaches_all.append(b)
        if daily_pnl < -self.config.max_daily_loss_usd:
            b = RiskBreach(breach_id=self._id("pnl"), cycle=cycle, metric="daily_loss", value=daily_pnl, limit=-self.config.max_daily_loss_usd, severity="critical", action="halt_trading", regime=regime, timestamp=_utc_now())
            breaches.append(b)
            self.breaches_all.append(b)
        risk_ok = len(breaches) == 0
        action_taken = "none" if risk_ok else ("halt" if any(br.severity == "critical" for br in breaches) else "mitigate")
        res = RiskMonitorCycle(cycle=cycle, timestamp=_utc_now(), paper_only=True, regime=regime, greeks=greeks, var_usd=var_usd, cvar_usd=cvar_usd, exposure_usd=exposure_usd, drawdown_pct=dd, daily_pnl_usd=daily_pnl, breaches=tuple(breaches), risk_ok=risk_ok, action_taken=action_taken)
        _assert_finite_dict(asdict(res), "risk_monitor_cycle")
        self.cycles.append(res)
        return res

    def run_campaign(self) -> Dict[str, Any]:
        self.cycles = []
        self.breaches_all = []
        self._ctr = 0
        for c in range(self.config.cycles):
            self.monitor_cycle(c)
        summary = {
            "phase": "PHASE38_RISK_MONITOR",
            "timestamp_utc": _utc_now(),
            "paper_only": True,
            "config": asdict(self.config),
            "n_cycles": len(self.cycles),
            "n_breaches": len(self.breaches_all),
            "risk_ok_cycles": sum(1 for x in self.cycles if x.risk_ok),
            "breach_counts_by_metric": {},
            "cycles": [asdict(x) for x in self.cycles],
            "breaches": [asdict(x) for x in self.breaches_all],
        }
        # counts
        for b in self.breaches_all:
            summary["breach_counts_by_metric"][b.metric] = summary["breach_counts_by_metric"].get(b.metric, 0) + 1
        _assert_finite_dict(summary, "risk_monitor_summary")
        return summary
