"""
Phase 31: Live Deployment Controller for Crypto Options Vol Surface Arbitrage + Orderflow.

Gated live capital rollout, kill-switch, canary sizing, venue health gates.
Production-grade, deterministic, finite numerics. PAPER-ONLY by default; live path hard-gated.
Extends Phase 20 live-readiness gating and Phase 30 vol surface arb components.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.deployment.phase20_live_readiness_gate import Phase20LiveReadinessGate
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p31deploy|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p31_{tag}_{h}"


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
class DeploymentConfig:
    seed: int = 42
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL", "XRP")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    expiries: tuple = ("7D", "30D", "90D")
    min_equity_usd: float = 100000.0
    max_drawdown_pct: float = 0.08
    kill_switch_dd_pct: float = 0.05
    canary_size_pct: float = 0.10
    max_canary_notional_usd: float = 50000.0
    venue_latency_max_ms: float = 150.0
    venue_error_rate_max: float = 0.02
    min_fill_rate: float = 0.80
    max_concurrent_positions: int = 20
    enforce_gates: bool = True
    modes: tuple = ("paper",)


@dataclass(frozen=True)
class CanaryConfig:
    size_pct: float = 0.10
    max_cycles: int = 50
    profit_target_pct: float = 0.02
    loss_stop_pct: float = 0.01


@dataclass(frozen=True)
class VenueHealth:
    venue: str
    latency_ms: float
    fill_rate: float
    error_rate: float
    ok: bool
    last_check: str


@dataclass(frozen=True)
class DeploymentDecision:
    allowed: bool
    paper_only: bool
    live_allowed: bool
    kill_switch_active: bool
    canary_size_usd: float
    blocked_reasons: Tuple[str, ...]
    checks: Tuple[Dict[str, Any], ...]
    timestamp: str


@dataclass(frozen=True)
class KillSwitchState:
    active: bool
    reason: str
    triggered_at: str
    cycles_blocked: int


class LiveDeploymentController:
    def __init__(
        self,
        config: Optional[DeploymentConfig] = None,
        seed: int = 42,
        readiness_gate: Optional[Phase20LiveReadinessGate] = None,
    ) -> None:
        self.config = config or DeploymentConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError(
                "LiveDeploymentController: paper_only must remain True (live path hard-gated)"
            )
        self.config = DeploymentConfig(
            seed=int(self.config.seed),
            paper_only=True,
            underlyings=tuple(self.config.underlyings),
            venues=tuple(self.config.venues),
            expiries=tuple(self.config.expiries),
            min_equity_usd=float(self.config.min_equity_usd),
            max_drawdown_pct=float(self.config.max_drawdown_pct),
            kill_switch_dd_pct=float(self.config.kill_switch_dd_pct),
            canary_size_pct=float(self.config.canary_size_pct),
            max_canary_notional_usd=float(self.config.max_canary_notional_usd),
            venue_latency_max_ms=float(self.config.venue_latency_max_ms),
            venue_error_rate_max=float(self.config.venue_error_rate_max),
            min_fill_rate=float(self.config.min_fill_rate),
            max_concurrent_positions=int(self.config.max_concurrent_positions),
            enforce_gates=bool(self.config.enforce_gates),
            modes=tuple(self.config.modes),
        )
        self.seed = int(self.config.seed)
        self.readiness_gate = readiness_gate or Phase20LiveReadinessGate(
            paper_only=True, seed=self.seed
        )
        self._counter = 0
        self.kill_switch = KillSwitchState(active=False, reason="", triggered_at="", cycles_blocked=0)
        self.decisions: List[DeploymentDecision] = []
        self.venue_health: Dict[str, VenueHealth] = {}
        self.cycles_deployed = 0
        self.canary_pnl_usd = 0.0
        self.canary_cycles = 0

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        return _make_id(self.seed, tag, self._counter)

    def evaluate_gates(self, state: Optional[Dict[str, Any]] = None) -> DeploymentDecision:
        state = state or {}
        blocked: List[str] = []
        checks: List[Dict[str, Any]] = []

        equity = float(state.get("equity", self.config.min_equity_usd))
        dd = float(state.get("drawdown_pct", 0.0))
        conn_ok = bool(state.get("connectivity_ok", True))
        risk_ok = bool(state.get("risk_limits_ok", True))
        compliance_ok = bool(state.get("compliance_ok", True))
        drift_ok = bool(state.get("drift_within_bounds", True))
        recon_ok = bool(state.get("reconciliation_clean", True))
        recovery_ok = bool(state.get("auto_recovery_ready", True))

        gate_decision = self.readiness_gate.evaluate(
            {
                "capital_allocated_valid": equity >= self.config.min_equity_usd,
                "connectivity_ok": conn_ok,
                "risk_limits_ok": risk_ok,
                "compliance_ok": compliance_ok,
                "drift_within_bounds": drift_ok,
                "reconciliation_clean": recon_ok,
                "auto_recovery_ready": recovery_ok,
                "equity": equity,
                "drawdown_pct": dd,
            }
        )

        checks.append(
            {
                "name": "min_equity",
                "passed": equity >= self.config.min_equity_usd,
                "required": True,
                "reason": f"equity {equity:.2f} >= {self.config.min_equity_usd:.2f}"
                if equity >= self.config.min_equity_usd
                else f"equity {equity:.2f} < {self.config.min_equity_usd:.2f}",
                "severity": "block" if equity < self.config.min_equity_usd else "info",
            }
        )
        if equity < self.config.min_equity_usd:
            blocked.append("min_equity")

        checks.append(
            {
                "name": "max_drawdown",
                "passed": dd <= self.config.max_drawdown_pct,
                "required": True,
                "reason": f"drawdown {dd:.4f} <= {self.config.max_drawdown_pct:.4f}"
                if dd <= self.config.max_drawdown_pct
                else f"drawdown {dd:.4f} > {self.config.max_drawdown_pct:.4f}",
                "severity": "block" if dd > self.config.max_drawdown_pct else "info",
            }
        )
        if dd > self.config.max_drawdown_pct:
            blocked.append("max_drawdown")

        for name, ok in [
            ("connectivity_ok", conn_ok),
            ("risk_limits_ok", risk_ok),
            ("compliance_ok", compliance_ok),
            ("drift_within_bounds", drift_ok),
            ("reconciliation_clean", recon_ok),
            ("auto_recovery_ready", recovery_ok),
        ]:
            checks.append(
                {
                    "name": name,
                    "passed": bool(ok),
                    "required": True,
                    "reason": f"{name} ok" if ok else f"{name} failed",
                    "severity": "block" if not ok else "info",
                }
            )
            if not ok:
                blocked.append(name)

        live_allowed = (
            len(blocked) == 0
            and gate_decision.approval_state == "APPROVED"
            and not self.kill_switch.active
        )
        decision = DeploymentDecision(
            allowed=True,
            paper_only=True,
            live_allowed=False,
            kill_switch_active=self.kill_switch.active,
            canary_size_usd=self._canary_size_usd(equity),
            blocked_reasons=tuple(blocked),
            checks=tuple(checks),
            timestamp=_utc_now(),
        )
        _assert_finite(asdict(decision), "deployment_decision")
        self.decisions.append(decision)
        return decision

    def _canary_size_usd(self, equity: float) -> float:
        size = equity * self.config.canary_size_pct
        return float(min(size, self.config.max_canary_notional_usd))

    def venue_health_check(self, venues: Optional[Tuple[str, ...]] = None) -> List[VenueHealth]:
        venues = venues or tuple(self.config.venues)
        import numpy as np

        rng = np.random.default_rng(self.seed + 31001)
        out: List[VenueHealth] = []
        base_latency = {"deribit": 45.0, "okx": 60.0, "binance": 70.0, "bybit": 65.0, "bitget": 75.0}
        for i, v in enumerate(venues):
            b = float(base_latency.get(v, 70.0))
            latency = float(b * (1.0 + 0.1 * float(rng.random())))
            fill_rate = float(0.85 + 0.1 * float(rng.random()))
            error_rate = float(0.0 + 0.02 * float(rng.random()))
            ok = (
                latency <= self.config.venue_latency_max_ms
                and fill_rate >= self.config.min_fill_rate
                and error_rate <= self.config.venue_error_rate_max
            )
            vh = VenueHealth(
                venue=v,
                latency_ms=latency,
                fill_rate=fill_rate,
                error_rate=error_rate,
                ok=bool(ok),
                last_check=_utc_now(),
            )
            _assert_finite(asdict(vh), f"venue_health_{v}")
            out.append(vh)
            self.venue_health[v] = vh
        return out

    def healthy_venues(self) -> List[str]:
        return [v for v, h in self.venue_health.items() if h.ok]

    def check_kill_switch(self, drawdown_pct: float, pnl_usd: float) -> KillSwitchState:
        dd = float(drawdown_pct)
        pnl = float(pnl_usd)
        reason = ""
        if not self.kill_switch.active and dd >= self.config.kill_switch_dd_pct:
            reason = f"drawdown {dd:.4f} >= kill threshold {self.config.kill_switch_dd_pct:.4f}"
        elif not self.kill_switch.active and pnl <= -abs(self.config.max_canary_notional_usd * 0.5):
            reason = f"canary pnl {pnl:.2f} breached loss stop"
        active = bool(reason) or self.kill_switch.active
        triggered_at = self.kill_switch.triggered_at or (_utc_now() if reason else "")
        cycles_blocked = self.kill_switch.cycles_blocked + (1 if reason and not self.kill_switch.active else 0)
        ks = KillSwitchState(
            active=bool(active),
            reason=reason,
            triggered_at=triggered_at,
            cycles_blocked=int(cycles_blocked),
        )
        _assert_finite({"dd": dd, "pnl": pnl}, "kill_switch_inputs")
        self.kill_switch = ks
        return ks

    def reset_kill_switch(self, audit_reason: str = "manual_reset") -> KillSwitchState:
        self.kill_switch = KillSwitchState(
            active=False, reason="", triggered_at="", cycles_blocked=0
        )
        return self.kill_switch

    def canary_size(self, equity: float, risk_pct: float) -> float:
        equity = float(equity)
        risk_pct = float(risk_pct)
        size = equity * min(self.config.canary_size_pct, max(risk_pct, 0.0))
        return float(min(size, self.config.max_canary_notional_usd))

    def deploy_cycle(
        self,
        cycle: int,
        signals: List[Dict[str, Any]],
        state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        state = state or {}
        decision = self.evaluate_gates(state)
        self.venue_health_check()
        dd = float(state.get("drawdown_pct", 0.0))
        pnl = float(state.get("pnl_usd", 0.0))
        self.check_kill_switch(dd, pnl)

        result: Dict[str, Any] = {
            "cycle": int(cycle),
            "timestamp": _utc_now(),
            "paper_only": True,
            "deploy_allowed": bool(decision.allowed and not self.kill_switch.active),
            "live_allowed": bool(decision.live_allowed),
            "kill_switch_active": bool(self.kill_switch.active),
            "kill_switch_reason": self.kill_switch.reason,
            "canary_size_usd": self._canary_size_usd(float(state.get("equity", self.config.min_equity_usd))),
            "blocked_reasons": list(decision.blocked_reasons),
            "healthy_venues": self.healthy_venues(),
            "venue_health": [asdict(vh) for vh in self.venue_health_check()],
            "signals_deployed": int(len(signals)),
            "deployment_id": self._next_id("deploy"),
        }
        if decision.blocked_reasons or self.kill_switch.active:
            result["deploy_allowed"] = False
            result["skip_reason"] = "; ".join(list(decision.blocked_reasons) + ([self.kill_switch.reason] if self.kill_switch.reason else []))
        if result["deploy_allowed"] and signals:
            self.cycles_deployed += 1
            self.canary_cycles += 1
        _assert_finite(result, "deploy_cycle_result")
        return result

    def generate_report(self, outdir: str = "research_state") -> Dict[str, Any]:
        from pathlib import Path

        Path(outdir).mkdir(parents=True, exist_ok=True)
        report = {
            "report": "PHASE31_LIVE_DEPLOYMENT_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "paper_only": True,
            "config": asdict(self.config),
            "cycles_deployed": int(self.cycles_deployed),
            "canary_cycles": int(self.canary_cycles),
            "canary_pnl_usd": float(self.canary_pnl_usd),
            "kill_switch": asdict(self.kill_switch),
            "healthy_venues": self.healthy_venues(),
            "venue_health": {v: asdict(h) for v, h in self.venue_health.items()},
            "decisions": [asdict(d) for d in self.decisions[-10:]],
            "last_decision": asdict(self.decisions[-1]) if self.decisions else None,
        }
        _assert_finite(report, "phase31_live_deployment_report")
        rep_json = Path(outdir) / "PHASE31_LIVE_DEPLOYMENT_REPORT.json"
        rep_md = Path(outdir) / "PHASE31_LIVE_DEPLOYMENT_REPORT.md"
        rep_json.write_text(
            __import__("json").dumps(serialize_metrics_strict(report), indent=2)
        )
        rep_md.write_text(
            f"# PHASE31_LIVE_DEPLOYMENT_REPORT\n\n"
            f"Timestamp: {report['timestamp']}\nPaper-only: {report['paper_only']}\n"
            f"Cycles deployed: {report['cycles_deployed']}\n"
            f"Canary cycles: {report['canary_cycles']}\n"
            f"Kill switch active: {report['kill_switch']['active']}\n"
            f"Healthy venues: {', '.join(report['healthy_venues']) or 'none'}\n"
        )
        return {
            "status": "ok",
            "json": str(rep_json),
            "md": str(rep_md),
            "paper_only": True,
        }


__all__ = [
    "LiveDeploymentController",
    "DeploymentConfig",
    "CanaryConfig",
    "VenueHealth",
    "DeploymentDecision",
    "KillSwitchState",
]
