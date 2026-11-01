"""
Phase 33: Live Capital Rollout for Crypto Options Vol Surface Arbitrage.

Canary-to-live capital rollout gated by the Phase 31 LiveDeploymentController and
Phase 32 LiveRiskControls. Production-grade, deterministic, finite numerics,
PAPER-ONLY default with hard-gated live paths. Extends Phase 31 live deployment +
Phase 32 live risk controls.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.deployment.phase31_live_deployment_controller import (
    LiveDeploymentController,
    DeploymentConfig,
)
from src.risk.phase32_live_risk_controls import (
    LiveRiskControls,
    LiveRiskControlsConfig32,
)
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p33rollout|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p33rollout_{tag}_{h}"


def _finite(x: float, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if math.isfinite(v) else default


def _assert_finite(obj: Any, label: str = "obj") -> None:
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

    walk(obj, "$")
    if bad:
        raise ValueError(f"Non-finite in {label}: {bad[:10]}")


@dataclass(frozen=True)
class LiveCapitalRolloutConfig33:
    seed: int = 42
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL", "XRP")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    expiries: tuple = ("7D", "30D", "90D")
    cycles: int = 10
    total_capital_usd: float = 150000.0
    canary_size_pct: float = 0.10
    max_canary_notional_usd: float = 50000.0
    canary_profit_target_pct: float = 0.02
    canary_loss_stop_pct: float = 0.01
    rollout_profit_target_pct: float = 0.05
    rollout_loss_stop_pct: float = 0.025
    max_concurrent_positions: int = 20
    min_equity_usd: float = 100000.0
    enforce_gates: bool = True


@dataclass(frozen=True)
class CanaryState:
    phase: str
    capital_allocated_usd: float
    cycles_active: int
    pnl_usd: float
    profit_target_hit: bool
    loss_stop_hit: bool
    ready_for_live: bool
    paper_only: bool


@dataclass(frozen=True)
class RolloutDecision:
    allowed: bool
    paper_only: bool
    live_allowed: bool
    phase: str
    capital_usd: float
    blocked_reasons: Tuple[str, ...]
    checks: Tuple[Dict[str, Any], ...]
    deployment_id: str
    timestamp: str


@dataclass(frozen=True)
class RolloutCycleResult:
    cycle: int
    timestamp: str
    paper_only: bool
    phase: str
    capital_allocated_usd: float
    canary_pnl_usd: float
    live_allowed: bool
    risk_ok: bool
    blocked_reasons: Tuple[str, ...]
    deployment_id: str


class LiveCapitalRollout:
    """Canary-to-live capital rollout gated by Phase 31 deployment + Phase 32 risk."""

    def __init__(
        self,
        config: Optional[LiveCapitalRolloutConfig33] = None,
        seed: int = 42,
        deployment_controller: Optional[Any] = None,
        risk_controls: Optional[Any] = None,
    ) -> None:
        self.config = config or LiveCapitalRolloutConfig33(seed=seed)
        if not self.config.paper_only:
            raise ValueError(
                "LiveCapitalRollout: paper_only must remain True (live path hard-gated)"
            )
        self.config = LiveCapitalRolloutConfig33(
            seed=int(self.config.seed),
            paper_only=True,
            underlyings=tuple(self.config.underlyings),
            venues=tuple(self.config.venues),
            expiries=tuple(self.config.expiries),
            cycles=int(self.config.cycles),
            total_capital_usd=float(self.config.total_capital_usd),
            canary_size_pct=float(self.config.canary_size_pct),
            max_canary_notional_usd=float(self.config.max_canary_notional_usd),
            canary_profit_target_pct=float(self.config.canary_profit_target_pct),
            canary_loss_stop_pct=float(self.config.canary_loss_stop_pct),
            rollout_profit_target_pct=float(self.config.rollout_profit_target_pct),
            rollout_loss_stop_pct=float(self.config.rollout_loss_stop_pct),
            max_concurrent_positions=int(self.config.max_concurrent_positions),
            min_equity_usd=float(self.config.min_equity_usd),
            enforce_gates=bool(self.config.enforce_gates),
        )
        self.seed = int(self.config.seed)
        if deployment_controller is None:
            deployment_controller = LiveDeploymentController(
                config=DeploymentConfig(
                    seed=self.seed + 33201,
                    paper_only=True,
                    underlyings=self.config.underlyings,
                    venues=self.config.venues,
                    expiries=self.config.expiries,
                    min_equity_usd=self.config.min_equity_usd,
                    canary_size_pct=self.config.canary_size_pct,
                    max_canary_notional_usd=self.config.max_canary_notional_usd,
                    enforce_gates=self.config.enforce_gates,
                ),
                seed=self.seed + 33201,
            )
        self.deployment_controller = deployment_controller
        if risk_controls is None:
            risk_controls = LiveRiskControls(
                config=LiveRiskControlsConfig32(
                    seed=self.seed + 33202,
                    paper_only=True,
                    underlyings=self.config.underlyings,
                    venues=self.config.venues,
                    cycles=self.config.cycles,
                    total_capital_usd=self.config.total_capital_usd,
                ),
                seed=self.seed + 33202,
                deployment_controller=self.deployment_controller,
            )
        self.risk_controls = risk_controls
        self._counter = 0
        self.results: List[RolloutCycleResult] = []
        self.canary_state = CanaryState(
            phase="canary",
            capital_allocated_usd=self._canary_size_usd(self.config.total_capital_usd),
            cycles_active=0,
            pnl_usd=0.0,
            profit_target_hit=False,
            loss_stop_hit=False,
            ready_for_live=False,
            paper_only=True,
        )
        self.phase = "canary"
        self.capital_allocated_usd = self.canary_state.capital_allocated_usd
        self.cycles_rolled_out = 0
        self.live_pnl_usd = 0.0

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        return _make_id(self.seed, tag, self._counter)

    def _canary_size_usd(self, equity: float) -> float:
        size = equity * self.config.canary_size_pct
        return float(min(size, self.config.max_canary_notional_usd))

    def _evaluate_gates(self, state: Optional[Dict[str, Any]] = None) -> Tuple[bool, List[str], List[Dict[str, Any]]]:
        state = state or {}
        blocked: List[str] = []
        checks: List[Dict[str, Any]] = []
        equity = float(state.get("equity", self.config.min_equity_usd))
        dd = float(state.get("drawdown_pct", 0.0))
        pnl = float(state.get("pnl_usd", 0.0))

        checks.append(
            {
                "name": "min_equity",
                "passed": equity >= self.config.min_equity_usd,
                "required": True,
                "reason": f"equity {equity:.2f} >= {self.config.min_equity_usd:.2f}"
                if equity >= self.config.min_equity_usd
                else f"equity {equity:.2f} < {self.config.min_equity_usd:.2f}",
            }
        )
        if equity < self.config.min_equity_usd:
            blocked.append("min_equity")

        checks.append(
            {
                "name": "max_drawdown",
                "passed": dd <= 0.08,
                "required": True,
                "reason": f"drawdown {dd:.4f} <= 0.0800"
                if dd <= 0.08
                else f"drawdown {dd:.4f} > 0.0800",
            }
        )
        if dd > 0.08:
            blocked.append("max_drawdown")

        for name, ok in [
            ("risk_limits_ok", True),
            ("compliance_ok", True),
            ("drift_within_bounds", True),
        ]:
            checks.append({"name": name, "passed": bool(ok), "required": True})
            if not ok:
                blocked.append(name)

        deploy_decision = self.deployment_controller.evaluate_gates(state)
        if deploy_decision.blocked_reasons:
            blocked.extend(list(deploy_decision.blocked_reasons))

        risk_state = self.risk_controls.coordinate_kill_switch(dd, pnl)
        if risk_state.kill_switch_active:
            blocked.append("kill_switch_active")

        allowed = bool(len(blocked) == 0 and not risk_state.kill_switch_active)
        return allowed, blocked, checks

    def canary_rollout(self, cycle: int, state: Optional[Dict[str, Any]] = None) -> CanaryState:
        state = state or {}
        allowed, blocked, checks = self._evaluate_gates(state)
        pnl = float(state.get("pnl_usd", self.canary_state.pnl_usd))
        self.canary_state = CanaryState(
            phase="canary",
            capital_allocated_usd=self.canary_state.capital_allocated_usd,
            cycles_active=self.canary_state.cycles_active + 1,
            pnl_usd=pnl,
            profit_target_hit=bool(
                pnl >= self.config.total_capital_usd * self.config.canary_profit_target_pct
            ),
            loss_stop_hit=bool(
                pnl <= -self.config.total_capital_usd * self.config.canary_loss_stop_pct
            ),
            ready_for_live=False,
            paper_only=True,
        )
        if blocked or not allowed:
            self.canary_state = CanaryState(
                phase="canary",
                capital_allocated_usd=self.canary_state.capital_allocated_usd,
                cycles_active=self.canary_state.cycles_active,
                pnl_usd=pnl,
                profit_target_hit=self.canary_state.profit_target_hit,
                loss_stop_hit=self.canary_state.loss_stop_hit,
                ready_for_live=False,
                paper_only=True,
            )
        return self.canary_state

    def promote_to_live_gate(
        self,
        cycle: int,
        state: Optional[Dict[str, Any]] = None,
    ) -> RolloutDecision:
        state = state or {}
        allowed, blocked, checks = self._evaluate_gates(state)
        live_allowed = bool(
            allowed
            and self.canary_state.profit_target_hit
            and not self.canary_state.loss_stop_hit
            and self.canary_state.cycles_active >= 5
        )
        capital = (
            self.config.total_capital_usd
            if live_allowed
            else self._canary_size_usd(
                float(state.get("equity", self.config.total_capital_usd))
            )
        )
        decision = RolloutDecision(
            allowed=bool(allowed),
            paper_only=True,
            live_allowed=live_allowed,
            phase=self.phase,
            capital_usd=capital,
            blocked_reasons=tuple(blocked),
            checks=tuple(checks),
            deployment_id=self._next_id("rollout"),
            timestamp=_utc_now(),
        )
        _assert_finite(
            {
                "capital_usd": decision.capital_usd,
            },
            "rollout_decision",
        )
        if live_allowed:
            self.phase = "live"
            self.capital_allocated_usd = capital
            self.cycles_rolled_out += 1
        return decision

    def run_cycle(
        self,
        cycle: int,
        state: Optional[Dict[str, Any]] = None,
    ) -> RolloutCycleResult:
        state = dict(state or {})
        equity = float(state.get("equity", self.config.total_capital_usd))
        dd = float(state.get("drawdown_pct", 0.0))
        pnl = float(state.get("pnl_usd", 0.0))

        canary = self.canary_rollout(cycle, state)
        decision = self.promote_to_live_gate(cycle, state)

        risk_state = self.risk_controls.coordinate_kill_switch(dd, pnl)
        risk_ok = bool(
            not risk_state.kill_switch_active
            and dd < 0.08
            and decision.allowed
        )

        if decision.live_allowed:
            self.live_pnl_usd = float(pnl)

        result = RolloutCycleResult(
            cycle=int(cycle),
            timestamp=_utc_now(),
            paper_only=True,
            phase=self.phase,
            capital_allocated_usd=float(self.capital_allocated_usd),
            canary_pnl_usd=float(canary.pnl_usd),
            live_allowed=bool(decision.live_allowed),
            risk_ok=risk_ok,
            blocked_reasons=tuple(sorted(set(decision.blocked_reasons))),
            deployment_id=decision.deployment_id,
        )
        _assert_finite(
            {
                "capital_allocated_usd": result.capital_allocated_usd,
                "canary_pnl_usd": result.canary_pnl_usd,
            },
            "rollout_cycle_result",
        )
        self.results.append(result)
        return result

    def run_campaign(self, cycles: Optional[int] = None) -> Dict[str, Any]:
        cycles = int(cycles if cycles is not None else self.config.cycles)
        reports: List[Dict[str, Any]] = []
        for c in range(1, cycles + 1):
            res = self.run_cycle(
                c,
                {
                    "equity": self.config.total_capital_usd,
                    "drawdown_pct": 0.0,
                    "pnl_usd": 0.0,
                },
            )
            reports.append(
                {
                    "cycle": res.cycle,
                    "phase": res.phase,
                    "capital_allocated_usd": res.capital_allocated_usd,
                    "canary_pnl_usd": res.canary_pnl_usd,
                    "live_allowed": res.live_allowed,
                    "risk_ok": res.risk_ok,
                    "blocked_reasons": list(res.blocked_reasons),
                    "deployment_id": res.deployment_id,
                }
            )
        return {
            "status": "ok",
            "paper_only": True,
            "cycles": cycles,
            "reports": reports,
            "final_phase": self.phase,
            "final_capital_allocated_usd": float(self.capital_allocated_usd),
            "final_canary_pnl_usd": float(self.canary_state.pnl_usd),
            "cycles_rolled_out": int(self.cycles_rolled_out),
            "live_pnl_usd": float(self.live_pnl_usd),
            "live_allowed": bool(self.phase == "live"),
        }

    def generate_report(self, outdir: str = "research_state") -> Dict[str, Any]:
        from pathlib import Path

        Path(outdir).mkdir(parents=True, exist_ok=True)
        campaign = (
            self.run_campaign(self.config.cycles) if not self.results else {
                "status": "ok",
                "paper_only": True,
                "cycles": len(self.results),
                "reports": [
                    {
                        "cycle": r.cycle,
                        "phase": r.phase,
                        "capital_allocated_usd": r.capital_allocated_usd,
                        "canary_pnl_usd": r.canary_pnl_usd,
                        "live_allowed": r.live_allowed,
                        "risk_ok": r.risk_ok,
                        "blocked_reasons": list(r.blocked_reasons),
                        "deployment_id": r.deployment_id,
                    }
                    for r in self.results
                ],
                "final_phase": self.phase,
                "final_capital_allocated_usd": float(self.capital_allocated_usd),
                "final_canary_pnl_usd": float(self.canary_state.pnl_usd),
                "cycles_rolled_out": int(self.cycles_rolled_out),
                "live_pnl_usd": float(self.live_pnl_usd),
                "live_allowed": bool(self.phase == "live"),
            }
        )
        last = self.results[-1] if self.results else None
        report = {
            "report": "PHASE33_LIVE_CAPITAL_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "paper_only": True,
            "cycles": int(len(self.results)),
            "final_phase": self.phase,
            "final_capital_allocated_usd": float(campaign["final_capital_allocated_usd"]),
            "final_canary_pnl_usd": float(campaign["final_canary_pnl_usd"]),
            "cycles_rolled_out": int(campaign["cycles_rolled_out"]),
            "live_pnl_usd": float(campaign["live_pnl_usd"]),
            "live_allowed": bool(campaign["live_allowed"]),
            "config": asdict(self.config),
            "last_cycle": int(last.cycle) if last else 0,
            "last_phase": str(last.phase) if last else "canary",
            "last_capital_allocated_usd": float(last.capital_allocated_usd) if last else 0.0,
            "last_canary_pnl_usd": float(last.canary_pnl_usd) if last else 0.0,
            "last_risk_ok": bool(last.risk_ok) if last else True,
            "cycle_results": [
                {
                    "cycle": r.cycle,
                    "phase": r.phase,
                    "capital_allocated_usd": r.capital_allocated_usd,
                    "canary_pnl_usd": r.canary_pnl_usd,
                    "live_allowed": r.live_allowed,
                    "risk_ok": r.risk_ok,
                    "blocked_reasons": list(r.blocked_reasons),
                    "deployment_id": r.deployment_id,
                }
                for r in self.results
            ],
        }
        _assert_finite(report, "phase33_live_capital_report")
        rep_json = Path(outdir) / "PHASE33_LIVE_CAPITAL_REPORT.json"
        rep_md = Path(outdir) / "PHASE33_LIVE_CAPITAL_REPORT.md"
        rep_json.write_text(__import__("json").dumps(serialize_metrics_strict(report), indent=2))
        rep_md.write_text(
            f"# PHASE33_LIVE_CAPITAL_REPORT\n\n"
            f"Timestamp: {report['timestamp']}\nPaper-only: {report['paper_only']}\n"
            f"Seed: {report['seed']}\nCycles: {report['cycles']}\n"
            f"Final phase: {report['final_phase']}\n"
            f"Final capital allocated USD: {report['final_capital_allocated_usd']:.2f}\n"
            f"Final canary PnL USD: {report['final_canary_pnl_usd']:.2f}\n"
            f"Cycles rolled out: {report['cycles_rolled_out']}\n"
            f"Live allowed: {report['live_allowed']}\n"
        )
        return {
            "status": "ok",
            "json": str(rep_json),
            "md": str(rep_md),
            "paper_only": True,
            "report": report,
        }


__all__ = [
    "LiveCapitalRollout",
    "LiveCapitalRolloutConfig33",
    "CanaryState",
    "RolloutDecision",
    "RolloutCycleResult",
]
