"""
Phase 27: Inventory Risk Management for Crypto Options Market Making
Production-grade, deterministic, paper-only safe.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import hashlib
import json
import math
from pathlib import Path


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


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


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p27inv|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p27inv_{tag}_{h}"


@dataclass(frozen=True)
class InventoryRiskConfig:
    seed: int = 42
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL", "XRP")
    expiries: tuple = ("7D", "30D", "90D")
    max_delta_total: float = 500.0
    max_delta_per_symbol: float = 200.0
    max_gamma_total: float = 200.0
    max_vega_total: float = 40000.0
    max_theta_total: float = -100000.0
    max_inventory_per_symbol: float = 100.0
    max_position_notional_usd: float = 2000000.0
    gamma_scalp_threshold_bps: float = 5.0
    delta_hedge_cadence_sec: float = 60.0
    stress_multiplier: float = 1.5
    enforce_hard_limits: bool = True


@dataclass(frozen=True)
class InventorySnapshot:
    snapshot_id: str
    underlying: str
    expiry: str
    strike: float
    option_type: str
    position_qty: float
    notional_usd: float
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float
    inventory_utilization: float
    within_limits: bool
    paper_only: bool
    timestamp: str


@dataclass(frozen=True)
class HedgeTrigger:
    trigger_id: str
    underlying: str
    reason: str
    severity: str
    delta: float
    gamma: float
    suggested_hedge_qty: float
    timestamp: str
    paper_only: bool


@dataclass(frozen=True)
class LimitCheck:
    limit_id: str
    metric: str
    value: float
    limit: float
    utilized: float
    status: str
    timestamp: str
    paper_only: bool


class InventoryRiskManager:
    def __init__(self, config: Optional[InventoryRiskConfig] = None, seed: int = 42):
        self.config = config or InventoryRiskConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("InventoryRiskManager: paper_only must remain True (live path hard-gated)")
        self.config = InventoryRiskConfig(
            seed=int(self.config.seed),
            paper_only=True,
            underlyings=tuple(self.config.underlyings),
            expiries=tuple(self.config.expiries),
            max_delta_total=float(self.config.max_delta_total),
            max_delta_per_symbol=float(self.config.max_delta_per_symbol),
            max_gamma_total=float(self.config.max_gamma_total),
            max_vega_total=float(self.config.max_vega_total),
            max_theta_total=float(self.config.max_theta_total),
            max_inventory_per_symbol=float(self.config.max_inventory_per_symbol),
            max_position_notional_usd=float(self.config.max_position_notional_usd),
            gamma_scalp_threshold_bps=float(self.config.gamma_scalp_threshold_bps),
            delta_hedge_cadence_sec=float(self.config.delta_hedge_cadence_sec),
            stress_multiplier=float(self.config.stress_multiplier),
            enforce_hard_limits=bool(self.config.enforce_hard_limits),
        )
        self.seed = int(self.config.seed)
        self._counter = 0
        self.snapshots: List[InventorySnapshot] = []
        self.triggers: List[HedgeTrigger] = []
        self.limit_checks: List[LimitCheck] = []
        self.audit: List[Dict[str, Any]] = []
        self.hedges: List[Dict[str, Any]] = []

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        h = hashlib.sha256(f"{self.seed}|p27inv|{tag}|{self._counter}".encode()).hexdigest()[:12]
        return f"p27inv_{tag}_{h}"

    def snapshot(
        self,
        underlying: str,
        expiry: str,
        strike: float,
        option_type: str,
        position_qty: float,
        mid_price: float,
        delta: float,
        gamma: float,
        vega: float,
        theta: float,
        rho: float,
        notional_usd: Optional[float] = None,
    ) -> InventorySnapshot:
        if not all(math.isfinite(x) for x in [position_qty, mid_price, delta, gamma, vega, theta, rho]):
            raise ValueError("non-finite snapshot inputs")
        notional = float(notional_usd) if notional_usd is not None else abs(position_qty) * mid_price
        inv_util = abs(position_qty) / max(1e-9, self.config.max_inventory_per_symbol)
        within = (
            abs(delta) <= self.config.max_delta_per_symbol + 1e-9
            and abs(position_qty) <= self.config.max_inventory_per_symbol + 1e-9
        )
        snap = InventorySnapshot(
            snapshot_id=self._next_id("snap"),
            underlying=str(underlying),
            expiry=str(expiry),
            strike=float(strike),
            option_type=str(option_type),
            position_qty=float(position_qty),
            notional_usd=float(notional),
            delta=float(delta),
            gamma=float(gamma),
            vega=float(vega),
            theta=float(theta),
            rho=float(rho),
            inventory_utilization=float(min(1.0, inv_util)),
            within_limits=bool(within),
            paper_only=True,
            timestamp=_utc_now(),
        )
        _assert_finite(asdict(snap), f"snapshot_{snap.snapshot_id}")
        self.snapshots.append(snap)
        self._log("snapshot", {"snapshot_id": snap.snapshot_id, "underlying": underlying, "position_qty": position_qty, "within_limits": within})
        return snap

    def check_limits(self, snapshots: List[InventorySnapshot]) -> Dict[str, Any]:
        checks: List[LimitCheck] = []
        total_delta = sum(s.delta for s in snapshots)
        total_gamma = sum(s.gamma for s in snapshots)
        total_vega = sum(s.vega for s in snapshots)
        total_theta = sum(s.theta for s in snapshots)
        total_notional = sum(s.notional_usd for s in snapshots)
        by_symbol_delta: Dict[str, float] = {}
        by_symbol_inventory: Dict[str, float] = {}
        for s in snapshots:
            by_symbol_delta[s.underlying] = by_symbol_delta.get(s.underlying, 0.0) + s.delta
            by_symbol_inventory[s.underlying] = by_symbol_inventory.get(s.underlying, 0.0) + s.position_qty

        def add(metric: str, value: float, limit: float, utilized: float, status: str) -> None:
            checks.append(
                LimitCheck(
                    limit_id=self._next_id("limit"),
                    metric=metric,
                    value=float(value),
                    limit=float(limit),
                    utilized=float(utilized),
                    status=status,
                    timestamp=_utc_now(),
                    paper_only=True,
                )
            )

        d_util = abs(total_delta) / max(1e-9, self.config.max_delta_total)
        add("total_delta", total_delta, self.config.max_delta_total, d_util, "block" if abs(total_delta) > self.config.max_delta_total + 1e-9 else ("warn" if d_util > 0.8 else "ok"))
        for sym, val in by_symbol_delta.items():
            u = abs(val) / max(1e-9, self.config.max_delta_per_symbol)
            add(f"delta_{sym}", val, self.config.max_delta_per_symbol, u, "block" if abs(val) > self.config.max_delta_per_symbol + 1e-9 else ("warn" if u > 0.8 else "ok"))
        g_util = abs(total_gamma) / max(1e-9, self.config.max_gamma_total)
        add("total_gamma", total_gamma, self.config.max_gamma_total, g_util, "block" if abs(total_gamma) > self.config.max_gamma_total + 1e-9 else ("warn" if g_util > 0.8 else "ok"))
        v_util = total_vega / max(1e-9, self.config.max_vega_total)
        add("total_vega", total_vega, self.config.max_vega_total, v_util, "block" if total_vega > self.config.max_vega_total + 1e-9 else ("warn" if v_util > 0.8 else "ok"))
        add("total_theta", total_theta, abs(self.config.max_theta_total), abs(total_theta) / max(1e-9, abs(self.config.max_theta_total)), "block" if total_theta < self.config.max_theta_total - 1e-9 else "ok")
        for sym, val in by_symbol_inventory.items():
            u = abs(val) / max(1e-9, self.config.max_inventory_per_symbol)
            add(f"inventory_{sym}", val, self.config.max_inventory_per_symbol, u, "block" if abs(val) > self.config.max_inventory_per_symbol + 1e-9 else ("warn" if u > 0.8 else "ok"))
        n_util = total_notional / max(1e-9, self.config.max_position_notional_usd)
        add("total_notional", total_notional, self.config.max_position_notional_usd, n_util, "block" if total_notional > self.config.max_position_notional_usd + 1e-9 else ("warn" if n_util > 0.8 else "ok"))

        blocks = [c for c in checks if c.status == "block"]
        passed = (len(blocks) == 0) or not self.config.enforce_hard_limits
        self.limit_checks.extend(checks)
        rep = {
            "timestamp": _utc_now(),
            "totals": {"delta": float(total_delta), "gamma": float(total_gamma), "vega": float(total_vega), "theta": float(total_theta), "notional_usd": float(total_notional)},
            "by_symbol_delta": {k: float(v) for k, v in by_symbol_delta.items()},
            "by_symbol_inventory": {k: float(v) for k, v in by_symbol_inventory.items()},
            "checks": [asdict(c) for c in checks],
            "passed": bool(passed),
            "enforce_hard_limits": bool(self.config.enforce_hard_limits),
            "paper_only": True,
        }
        _assert_finite(rep, "inventory_limits")
        return rep

    def gamma_scalp_triggers(self, snapshots: List[InventorySnapshot], price_move_bps: float) -> List[HedgeTrigger]:
        triggers: List[HedgeTrigger] = []
        for s in snapshots:
            gamma_pnl_bps = abs(s.gamma) * (price_move_bps / 10000.0) ** 2 * 10000.0
            if gamma_pnl_bps > self.config.gamma_scalp_threshold_bps:
                qty = -s.delta
                triggers.append(
                    HedgeTrigger(
                        trigger_id=self._next_id("gamma_scalp"),
                        underlying=s.underlying,
                        reason="gamma_scalp",
                        severity="warn" if gamma_pnl_bps < self.config.gamma_scalp_threshold_bps * 2 else "critical",
                        delta=float(s.delta),
                        gamma=float(s.gamma),
                        suggested_hedge_qty=float(qty),
                        timestamp=_utc_now(),
                        paper_only=True,
                    )
                )
        self.triggers.extend(triggers)
        self._log("gamma_scalp_triggers", {"count": len(triggers), "price_move_bps": price_move_bps})
        return triggers

    def delta_hedge_cadence(self, snapshots: List[InventorySnapshot]) -> Dict[str, Any]:
        due = []
        for s in snapshots:
            if abs(s.delta) > self.config.max_delta_per_symbol * 0.25:
                due.append({"underlying": s.underlying, "delta": s.delta, "suggested_hedge_qty": -s.delta, "reason": "delta_hedge_cadence"})
        rep = {
            "cadence_sec": float(self.config.delta_hedge_cadence_sec),
            "due_hedges": due,
            "count": len(due),
            "paper_only": True,
            "timestamp": _utc_now(),
        }
        _assert_finite(rep, "delta_hedge_cadence")
        return rep

    def stress_test(self, snapshots: List[InventorySnapshot], shock_pct: float = 0.1) -> Dict[str, Any]:
        total_impact = 0.0
        per_symbol: Dict[str, float] = {}
        for s in snapshots:
            shock = float(shock_pct)
            impact = s.delta * shock * s.notional_usd + 0.5 * s.gamma * (shock ** 2) * s.notional_usd
            total_impact += impact
            per_symbol[s.underlying] = per_symbol.get(s.underlying, 0.0) + impact
        stressed = total_impact * self.config.stress_multiplier
        rep = {
            "shock_pct": float(shock_pct),
            "stress_multiplier": float(self.config.stress_multiplier),
            "total_pnl_impact_usd": float(total_impact),
            "stressed_pnl_impact_usd": float(stressed),
            "per_symbol": {k: float(v) for k, v in per_symbol.items()},
            "breached": bool(stressed < -self.config.max_position_notional_usd * 0.05),
            "paper_only": True,
            "timestamp": _utc_now(),
        }
        _assert_finite(rep, "stress_test")
        return rep

    def generate_report(self, snapshots: Optional[List[InventorySnapshot]] = None) -> Dict[str, Any]:
        snaps = snapshots if snapshots is not None else self.snapshots
        limits = self.check_limits(snaps)
        rep = {
            "report": "PHASE27_INVENTORY_RISK_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "config": asdict(self.config),
            "snapshot_count": len(snaps),
            "snapshots": [asdict(s) for s in snaps],
            "limits": limits,
            "triggers": [asdict(t) for t in self.triggers],
            "hedges": self.hedges,
            "audit": self.audit,
            "paper_only": True,
        }
        _assert_finite(rep, "inventory_risk_report")
        return rep

    def save_report(self, report: Dict[str, Any], outdir: str = "research_state") -> str:
        Path(outdir).mkdir(parents=True, exist_ok=True)
        pjson = Path(outdir) / "PHASE27_INVENTORY_RISK_REPORT.json"
        pmd = Path(outdir) / "PHASE27_INVENTORY_RISK_REPORT.md"
        pjson.write_text(json.dumps(report, indent=2))
        pmd.write_text(f"# PHASE27_INVENTORY_RISK_REPORT\n\nStatus: ok\nSnapshots: {len(self.snapshots)}\nLimits passed: {report.get('limits', {}).get('passed')}\nPaper-only: True\n")
        return str(pjson)


__all__ = ["InventoryRiskManager", "InventoryRiskConfig", "InventorySnapshot", "HedgeTrigger", "LimitCheck"]
