"""
Phase 32: Live Risk Controls for Crypto Options Orderflow + Vol Arb.

Position/margin/leverage limits, kill-switch coordination with the Phase 31
LiveDeploymentController, and per-cycle risk gating. Deterministic, finite
numerics, PAPER-ONLY default with hard-gated live paths. Extends Phase 30 vol
risk budget + Phase 31 live deployment controller.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.deployment.phase31_live_deployment_controller import LiveDeploymentController
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p32lr|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p32lr_{tag}_{h}"


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
class LiveRiskControlsConfig32:
    seed: int = 42
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL", "XRP")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 10
    max_position_notional_usd: float = 1_000_000.0
    max_leverage: float = 5.0
    max_margin_usage_pct: float = 0.25
    max_drawdown_pct: float = 0.10
    kill_switch_dd_pct: float = 0.12
    kill_switch_pnl_usd: float = -50_000.0
    max_consecutive_rejects: int = 10
    max_daily_loss_usd: float = 50_000.0
    total_capital_usd: float = 150_000.0


@dataclass(frozen=True)
class PositionLimitResult:
    symbol: str
    side: str
    notional_usd: float
    allowed: bool
    blocked_reasons: Tuple[str, ...]
    leverage: float
    margin_usage_pct: float
    paper_only: bool


@dataclass(frozen=True)
class KillSwitchCoordination:
    kill_switch_active: bool
    reason: str
    triggered_at: str
    cycles_blocked: int
    coordinated_with_phase31: bool
    paper_only: bool


@dataclass(frozen=True)
class LiveRiskCycleResult:
    cycle: int
    timestamp: str
    paper_only: bool
    positions_checked: int
    positions_allowed: int
    positions_blocked: int
    kill_switch_active: bool
    drawdown_pct: float
    margin_usage_pct: float
    leverage: float
    risk_ok: bool
    blocked_reasons: Tuple[str, ...]


class LiveRiskControls:
    """Position/margin/leverage limits with Phase 31 kill-switch coordination."""

    def __init__(
        self,
        config: Optional[LiveRiskControlsConfig32] = None,
        seed: int = 42,
        deployment_controller: Optional[Any] = None,
    ) -> None:
        self.config = config or LiveRiskControlsConfig32(seed=seed)
        if not self.config.paper_only:
            raise ValueError(
                "LiveRiskControls: paper_only must remain True (live path hard-gated)"
            )
        self.config = LiveRiskControlsConfig32(
            seed=int(self.config.seed),
            paper_only=True,
            underlyings=tuple(self.config.underlyings),
            venues=tuple(self.config.venues),
            cycles=int(self.config.cycles),
            max_position_notional_usd=float(self.config.max_position_notional_usd),
            max_leverage=float(self.config.max_leverage),
            max_margin_usage_pct=float(self.config.max_margin_usage_pct),
            max_drawdown_pct=float(self.config.max_drawdown_pct),
            kill_switch_dd_pct=float(self.config.kill_switch_dd_pct),
            kill_switch_pnl_usd=float(self.config.kill_switch_pnl_usd),
            max_consecutive_rejects=int(self.config.max_consecutive_rejects),
            max_daily_loss_usd=float(self.config.max_daily_loss_usd),
            total_capital_usd=float(self.config.total_capital_usd),
        )
        self.seed = int(self.config.seed)
        if deployment_controller is None:
            deployment_controller = LiveDeploymentController(seed=self.seed + 32205)
        self.deployment_controller = deployment_controller
        self._counter = 0
        self.results: List[LiveRiskCycleResult] = []
        self._position_history: List[PositionLimitResult] = []
        self._kill_history: List[KillSwitchCoordination] = []
        self.consecutive_rejects = 0
        self.daily_loss_usd = 0.0
        self.equity = float(self.config.total_capital_usd)
        self.drawdown_pct = 0.0

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        return _make_id(self.seed, tag, self._counter)

    def check_position_limits(
        self,
        symbol: str,
        side: str,
        notional_usd: float,
        equity: Optional[float] = None,
    ) -> PositionLimitResult:
        eq = _finite(equity) if equity is not None else self.equity
        notional = _finite(notional_usd)
        leverage = float(notional / eq) if eq > 0 else 0.0
        margin_usage_pct = float(min(1.0, notional / self.config.total_capital_usd))

        blocked: List[str] = []
        if notional > self.config.max_position_notional_usd:
            blocked.append("max_position_notional")
        if leverage > self.config.max_leverage:
            blocked.append("max_leverage")
        if margin_usage_pct > self.config.max_margin_usage_pct:
            blocked.append("max_margin_usage")
        if self.drawdown_pct >= self.config.max_drawdown_pct:
            blocked.append("max_drawdown")
        if self.daily_loss_usd >= self.config.max_daily_loss_usd:
            blocked.append("max_daily_loss")
        if self.consecutive_rejects >= self.config.max_consecutive_rejects:
            blocked.append("max_consecutive_rejects")

        allowed = bool(len(blocked) == 0)
        if allowed:
            self.consecutive_rejects = 0
        else:
            self.consecutive_rejects += 1

        res = PositionLimitResult(
            symbol=str(symbol),
            side=str(side).lower(),
            notional_usd=notional,
            allowed=allowed,
            blocked_reasons=tuple(blocked),
            leverage=leverage,
            margin_usage_pct=margin_usage_pct,
            paper_only=True,
        )
        _assert_finite(
            {
                "notional_usd": res.notional_usd,
                "leverage": res.leverage,
                "margin_usage_pct": res.margin_usage_pct,
            },
            "position_limit_result",
        )
        self._position_history.append(res)
        return res

    def coordinate_kill_switch(
        self,
        drawdown_pct: float,
        pnl_usd: float,
    ) -> KillSwitchCoordination:
        dd = _finite(drawdown_pct)
        pnl = _finite(pnl_usd)
        self.drawdown_pct = dd

        phase31_active = False
        phase31_reason = ""
        if self.deployment_controller is not None:
            try:
                ks = self.deployment_controller.check_kill_switch(dd, pnl)
                phase31_active = bool(getattr(ks, "active", False))
                phase31_reason = str(getattr(ks, "reason", "") or "")
            except Exception:
                phase31_active = False
                phase31_reason = "phase31_unavailable"

        local_reasons: List[str] = []
        if dd >= self.config.kill_switch_dd_pct:
            local_reasons.append("kill_switch_drawdown")
        if pnl <= self.config.kill_switch_pnl_usd:
            local_reasons.append("kill_switch_pnl")

        active = bool(phase31_active or local_reasons)
        reason = phase31_reason or (",".join(local_reasons) if local_reasons else "")
        triggered_at = _utc_now() if (active and not self._kill_switch_active()) else ""

        ks = KillSwitchCoordination(
            kill_switch_active=active,
            reason=reason,
            triggered_at=triggered_at,
            cycles_blocked=1 if (active and not self._kill_switch_active()) else 0,
            coordinated_with_phase31=self.deployment_controller is not None,
            paper_only=True,
        )
        self._kill_history.append(ks)
        return ks

    def _kill_switch_active(self) -> bool:
        return any(k.kill_switch_active for k in self._kill_history)

    def run_cycle(
        self,
        cycle: int,
        state: Optional[Dict[str, Any]] = None,
        deployment_controller: Optional[Any] = None,
    ) -> LiveRiskCycleResult:
        state = dict(state or {})
        if deployment_controller is not None:
            self.deployment_controller = deployment_controller
        eq = _finite(state.get("equity", self.equity))
        dd = _finite(state.get("drawdown_pct", self.drawdown_pct))
        pnl = _finite(state.get("pnl_usd", 0.0))
        daily_loss = _finite(state.get("daily_loss_usd", self.daily_loss_usd))
        self.equity = eq
        self.drawdown_pct = dd
        self.daily_loss_usd = daily_loss

        positions = state.get("positions", [])
        allowed_count = 0
        blocked_count = 0
        all_blocked: List[str] = []

        for pos in positions:
            sym = str(pos.get("symbol", "ETH"))
            side = str(pos.get("side", "buy"))
            notional = _finite(pos.get("notional_usd", 50000.0))
            res = self.check_position_limits(sym, side, notional, equity=eq)
            if res.allowed:
                allowed_count += 1
            else:
                blocked_count += 1
                all_blocked.extend(list(res.blocked_reasons))

        ks = self.coordinate_kill_switch(dd, pnl)
        margin_usage = float(
            min(1.0, sum(_finite(p.get("notional_usd", 0.0)) for p in positions) / self.config.total_capital_usd)
            if positions
            else 0.0
        )
        leverage = float(
            sum(_finite(p.get("notional_usd", 0.0)) for p in positions) / eq
            if positions and eq > 0
            else 0.0
        )

        risk_ok = bool(
            not ks.kill_switch_active
            and blocked_count == 0
            and dd < self.config.max_drawdown_pct
            and daily_loss < self.config.max_daily_loss_usd
        )

        result = LiveRiskCycleResult(
            cycle=int(cycle),
            timestamp=_utc_now(),
            paper_only=True,
            positions_checked=int(len(positions)),
            positions_allowed=int(allowed_count),
            positions_blocked=int(blocked_count),
            kill_switch_active=bool(ks.kill_switch_active),
            drawdown_pct=dd,
            margin_usage_pct=margin_usage,
            leverage=leverage,
            risk_ok=risk_ok,
            blocked_reasons=tuple(sorted(set(all_blocked))),
        )
        _assert_finite(
            {
                "drawdown_pct": result.drawdown_pct,
                "margin_usage_pct": result.margin_usage_pct,
                "leverage": result.leverage,
            },
            "live_risk_cycle_result",
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
                    "equity": self.equity,
                    "drawdown_pct": self.drawdown_pct,
                    "pnl_usd": 0.0,
                    "daily_loss_usd": self.daily_loss_usd,
                    "positions": [],
                },
            )
            reports.append(
                {
                    "cycle": res.cycle,
                    "positions_checked": res.positions_checked,
                    "positions_allowed": res.positions_allowed,
                    "positions_blocked": res.positions_blocked,
                    "kill_switch_active": res.kill_switch_active,
                    "drawdown_pct": res.drawdown_pct,
                    "margin_usage_pct": res.margin_usage_pct,
                    "leverage": res.leverage,
                    "risk_ok": res.risk_ok,
                    "blocked_reasons": list(res.blocked_reasons),
                }
            )
        return {
            "status": "ok",
            "paper_only": True,
            "cycles": cycles,
            "reports": reports,
            "total_positions_checked": int(sum(r["positions_checked"] for r in reports)),
            "total_positions_blocked": int(sum(r["positions_blocked"] for r in reports)),
            "final_drawdown_pct": float(reports[-1]["drawdown_pct"]) if reports else 0.0,
            "final_risk_ok": bool(reports[-1]["risk_ok"]) if reports else True,
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
                        "positions_checked": r.positions_checked,
                        "positions_allowed": r.positions_allowed,
                        "positions_blocked": r.positions_blocked,
                        "kill_switch_active": r.kill_switch_active,
                        "drawdown_pct": r.drawdown_pct,
                        "margin_usage_pct": r.margin_usage_pct,
                        "leverage": r.leverage,
                        "risk_ok": r.risk_ok,
                        "blocked_reasons": list(r.blocked_reasons),
                    }
                    for r in self.results
                ],
                "total_positions_checked": int(
                    sum(r.positions_checked for r in self.results)
                ),
                "total_positions_blocked": int(
                    sum(r.positions_blocked for r in self.results)
                ),
                "final_drawdown_pct": float(
                    self.results[-1].drawdown_pct
                )
                if self.results
                else 0.0,
                "final_risk_ok": bool(self.results[-1].risk_ok)
                if self.results
                else True,
            }
        )
        last = self.results[-1] if self.results else None
        report = {
            "report": "PHASE32_LIVE_RISK_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "paper_only": True,
            "cycles": int(len(self.results)),
            "total_positions_checked": int(campaign["total_positions_checked"]),
            "total_positions_blocked": int(campaign["total_positions_blocked"]),
            "final_drawdown_pct": float(campaign["final_drawdown_pct"]),
            "final_risk_ok": bool(campaign["final_risk_ok"]),
            "config": asdict(self.config),
            "last_cycle": int(last.cycle) if last else 0,
            "last_drawdown_pct": float(last.drawdown_pct) if last else 0.0,
            "last_margin_usage_pct": float(last.margin_usage_pct) if last else 0.0,
            "last_leverage": float(last.leverage) if last else 0.0,
            "cycle_results": [
                {
                    "cycle": r.cycle,
                    "positions_checked": r.positions_checked,
                    "positions_allowed": r.positions_allowed,
                    "positions_blocked": r.positions_blocked,
                    "kill_switch_active": r.kill_switch_active,
                    "drawdown_pct": r.drawdown_pct,
                    "margin_usage_pct": r.margin_usage_pct,
                    "leverage": r.leverage,
                    "risk_ok": r.risk_ok,
                    "blocked_reasons": list(r.blocked_reasons),
                }
                for r in self.results
            ],
            "kill_switch_history": [
                {
                    "kill_switch_active": k.kill_switch_active,
                    "reason": k.reason,
                    "triggered_at": k.triggered_at,
                    "cycles_blocked": k.cycles_blocked,
                    "coordinated_with_phase31": k.coordinated_with_phase31,
                }
                for k in self._kill_history
            ],
        }
        _assert_finite(report, "phase32_live_risk_report")
        rep_json = Path(outdir) / "PHASE32_LIVE_RISK_REPORT.json"
        rep_md = Path(outdir) / "PHASE32_LIVE_RISK_REPORT.md"
        rep_json.write_text(__import__("json").dumps(serialize_metrics_strict(report), indent=2))
        rep_md.write_text(
            f"# PHASE32_LIVE_RISK_REPORT\n\n"
            f"Timestamp: {report['timestamp']}\nPaper-only: {report['paper_only']}\n"
            f"Seed: {report['seed']}\nCycles: {report['cycles']}\n"
            f"Total positions checked: {report['total_positions_checked']}\n"
            f"Total positions blocked: {report['total_positions_blocked']}\n"
            f"Final drawdown: {report['final_drawdown_pct']:.4f}\n"
            f"Final risk ok: {report['final_risk_ok']}\n"
        )
        return {
            "status": "ok",
            "json": str(rep_json),
            "md": str(rep_md),
            "paper_only": True,
            "report": report,
        }


__all__ = [
    "LiveRiskControls",
    "LiveRiskControlsConfig32",
    "PositionLimitResult",
    "KillSwitchCoordination",
    "LiveRiskCycleResult",
]
