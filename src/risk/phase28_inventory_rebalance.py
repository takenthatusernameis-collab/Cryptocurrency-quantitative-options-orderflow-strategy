"""
Phase 28: Cross-Venue Inventory Rebalancing for Crypto Options Market Making.
Cross-venue inventory imbalance detection, rebalancing transfer orders, inventory
skew propagation across venues, stress-aware rebalance limits.
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
    h = hashlib.sha256(f"{seed}|p28inv|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p28inv_{tag}_{h}"


@dataclass(frozen=True)
class InventoryRebalanceConfig:
    seed: int = 42
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL", "XRP")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    max_inventory_per_venue: float = 100.0
    max_cross_venue_imbalance: float = 150.0
    rebalance_threshold_bps: float = 10.0
    max_transfer_notional_usd: float = 500000.0
    stress_multiplier: float = 1.5
    enforce_hard_limits: bool = True


@dataclass(frozen=True)
class VenueInventory:
    venue: str
    underlying: str
    position_qty: float
    notional_usd: float
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float
    utilization: float
    within_limits: bool
    paper_only: bool
    timestamp: str


@dataclass(frozen=True)
class Imbalance:
    imbalance_id: str
    underlying: str
    venue_positions: Dict[str, float]
    total_net: float
    mean_position: float
    max_imbalance: float
    imbalance_bps: float
    rebalance_required: bool
    paper_only: bool
    timestamp: str


@dataclass(frozen=True)
class RebalanceOrder:
    order_id: str
    underlying: str
    from_venue: str
    to_venue: str
    qty: float
    price: float
    notional_usd: float
    reason: str
    urgency: str
    paper_only: bool
    timestamp: str


class InventoryRebalancer:
    def __init__(self, config: Optional[InventoryRebalanceConfig] = None, seed: int = 42):
        self.config = config or InventoryRebalanceConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("InventoryRebalancer: paper_only must remain True (live path hard-gated)")
        self.config = InventoryRebalanceConfig(
            seed=int(self.config.seed),
            paper_only=True,
            underlyings=tuple(self.config.underlyings),
            venues=tuple(self.config.venues),
            max_inventory_per_venue=float(self.config.max_inventory_per_venue),
            max_cross_venue_imbalance=float(self.config.max_cross_venue_imbalance),
            rebalance_threshold_bps=float(self.config.rebalance_threshold_bps),
            max_transfer_notional_usd=float(self.config.max_transfer_notional_usd),
            stress_multiplier=float(self.config.stress_multiplier),
            enforce_hard_limits=bool(self.config.enforce_hard_limits),
        )
        self.seed = int(self.config.seed)
        self._counter = 0
        self.snapshots: List[VenueInventory] = []
        self.imbalances: List[Imbalance] = []
        self.rebalance_orders: List[RebalanceOrder] = []
        self.applied: List[RebalanceOrder] = []
        self.audit: List[Dict[str, Any]] = []

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        h = hashlib.sha256(f"{self.seed}|p28inv|{tag}|{self._counter}".encode()).hexdigest()[:12]
        return f"p28inv_{tag}_{h}"

    def snapshot_venue_inventory(
        self,
        venue: str,
        underlying: str,
        position_qty: float,
        mid_price: float,
        delta: float,
        gamma: float,
        vega: float,
        theta: float,
        rho: float,
        notional_usd: Optional[float] = None,
    ) -> VenueInventory:
        if not all(math.isfinite(x) for x in [position_qty, mid_price, delta, gamma, vega, theta, rho]):
            raise ValueError("non-finite venue inventory inputs")
        if mid_price <= 0:
            raise ValueError("mid_price must be positive")
        notional = float(notional_usd) if notional_usd is not None else abs(position_qty) * mid_price
        util = abs(position_qty) / max(1e-9, self.config.max_inventory_per_venue)
        within = (
            abs(position_qty) <= self.config.max_inventory_per_venue + 1e-9
            and abs(delta) <= self.config.max_cross_venue_imbalance + 1e-9
        )
        snap = VenueInventory(
            venue=str(venue).lower(),
            underlying=str(underlying),
            position_qty=float(position_qty),
            notional_usd=float(notional),
            delta=float(delta),
            gamma=float(gamma),
            vega=float(vega),
            theta=float(theta),
            rho=float(rho),
            utilization=float(min(1.0, util)),
            within_limits=bool(within),
            paper_only=True,
            timestamp=_utc_now(),
        )
        _assert_finite(asdict(snap), f"venue_inventory_{snap.venue}_{snap.underlying}")
        self.snapshots.append(snap)
        self._log("snapshot", {"venue": snap.venue, "underlying": underlying, "position_qty": position_qty, "within_limits": within})
        return snap

    def detect_imbalance(self, venue_inventories: List[VenueInventory], underlying: Optional[str] = None) -> Imbalance:
        if not venue_inventories:
            raise ValueError("venue_inventories must be non-empty")
        invs = venue_inventories
        if underlying is not None:
            invs = [s for s in venue_inventories if s.underlying == underlying]
            if not invs:
                raise ValueError(f"no inventories for underlying {underlying}")
        target = str(invs[0].underlying)
        venue_positions: Dict[str, float] = {s.venue: s.position_qty for s in invs}
        total_net = sum(s.position_qty for s in invs)
        n = max(1, len(invs))
        mean_position = total_net / n
        max_imbalance = max(abs(s.position_qty - mean_position) for s in invs)
        denom = max(1e-9, abs(total_net) if abs(total_net) > 1e-9 else max(1e-9, abs(mean_position)))
        imbalance_bps = max_imbalance / denom * 10000.0
        rebalance_required = bool(max_imbalance > self.config.max_cross_venue_imbalance * 0.5 or imbalance_bps > self.config.rebalance_threshold_bps)
        imb = Imbalance(
            imbalance_id=self._next_id("imb"),
            underlying=target,
            venue_positions={k: float(v) for k, v in venue_positions.items()},
            total_net=float(total_net),
            mean_position=float(mean_position),
            max_imbalance=float(max_imbalance),
            imbalance_bps=float(imbalance_bps),
            rebalance_required=rebalance_required,
            paper_only=True,
            timestamp=_utc_now(),
        )
        _assert_finite(asdict(imb), f"imbalance_{imb.imbalance_id}")
        self.imbalances.append(imb)
        self._log("detect_imbalance", {"underlying": target, "total_net": total_net, "max_imbalance": max_imbalance, "rebalance_required": rebalance_required})
        return imb

    def rebalance_plan(self, imbalance: Imbalance, price: float = 100000.0) -> List[RebalanceOrder]:
        if not math.isfinite(price) or price <= 0:
            raise ValueError("price must be positive finite")
        orders: List[RebalanceOrder] = []
        mean = imbalance.mean_position
        threshold = self.config.max_inventory_per_venue * 0.25
        over: List[tuple] = []  # (venue, qty_above_mean)
        under: List[tuple] = []  # (venue, qty_below_mean)
        for venue, qty in imbalance.venue_positions.items():
            if qty > mean + threshold:
                over.append((venue, qty - mean))
            elif qty < mean - threshold:
                under.append((venue, mean - qty))
        over.sort(key=lambda x: x[1], reverse=True)
        under.sort(key=lambda x: x[1], reverse=True)
        ui = 0
        for ovenue, osurplus in over:
            while osurplus > 1e-9 and ui < len(under):
                uvenue, udemand = under[ui]
                if uvenue == ovenue:
                    ui += 1
                    continue
                move = min(osurplus, udemand)
                move = min(move, self.config.max_transfer_notional_usd / max(price, 1e-9))
                if move <= 1e-9:
                    ui += 1
                    continue
                notional = move * price
                urgency = "critical" if osurplus > self.config.max_inventory_per_venue * 0.5 else "warn"
                orders.append(
                    RebalanceOrder(
                        order_id=self._next_id("rebal"),
                        underlying=str(imbalance.underlying),
                        from_venue=str(ovenue),
                        to_venue=str(uvenue),
                        qty=float(move),
                        price=float(price),
                        notional_usd=float(notional),
                        reason="cross_venue_rebalance",
                        urgency=str(urgency),
                        paper_only=True,
                        timestamp=_utc_now(),
                    )
                )
                osurplus -= move
                under[ui] = (uvenue, udemand - move)
                if under[ui][1] <= 1e-9:
                    ui += 1
        self.rebalance_orders.extend(orders)
        self._log("rebalance_plan", {"underlying": imbalance.underlying, "order_count": len(orders), "total_transfer_qty": sum(o.qty for o in orders)})
        return orders

    def apply_rebalance(self, order: RebalanceOrder) -> None:
        if not math.isfinite(order.qty) or order.qty <= 0:
            raise ValueError("rebalance order qty must be positive finite")
        self.applied.append(order)
        self._log("apply_rebalance", {"order_id": order.order_id, "from": order.from_venue, "to": order.to_venue, "qty": order.qty, "notional_usd": order.notional_usd})

    def stress_test(self, venue_inventories: List[VenueInventory], shock_pct: float = 0.1) -> Dict[str, Any]:
        total_impact = 0.0
        per_venue: Dict[str, float] = {}
        per_symbol: Dict[str, float] = {}
        for s in venue_inventories:
            shock = float(shock_pct)
            impact = s.delta * shock * s.notional_usd + 0.5 * s.gamma * (shock ** 2) * s.notional_usd
            total_impact += impact
            per_venue[s.venue] = per_venue.get(s.venue, 0.0) + impact
            per_symbol[s.underlying] = per_symbol.get(s.underlying, 0.0) + impact
        stressed = total_impact * self.config.stress_multiplier
        rep = {
            "shock_pct": float(shock_pct),
            "stress_multiplier": float(self.config.stress_multiplier),
            "total_pnl_impact_usd": float(total_impact),
            "stressed_pnl_impact_usd": float(stressed),
            "per_venue": {k: float(v) for k, v in per_venue.items()},
            "per_symbol": {k: float(v) for k, v in per_symbol.items()},
            "breached": bool(stressed < -self.config.max_transfer_notional_usd * 0.05),
            "venue_count": len(venue_inventories),
            "paper_only": True,
            "timestamp": _utc_now(),
        }
        _assert_finite(rep, "rebalance_stress_test")
        return rep

    def generate_report(self, snapshots: Optional[List[VenueInventory]] = None) -> Dict[str, Any]:
        snaps = snapshots if snapshots is not None else self.snapshots
        rep = {
            "report": "PHASE28_INVENTORY_REBALANCE_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "config": asdict(self.config),
            "snapshot_count": len(snaps),
            "snapshots": [asdict(s) for s in snaps],
            "imbalances": [asdict(i) for i in self.imbalances],
            "rebalance_orders": [asdict(o) for o in self.rebalance_orders],
            "applied_rebalances": [asdict(o) for o in self.applied],
            "audit": self.audit,
            "paper_only": True,
        }
        _assert_finite(rep, "inventory_rebalance_report")
        return rep

    def save_report(self, report: Dict[str, Any], outdir: str = "research_state") -> str:
        Path(outdir).mkdir(parents=True, exist_ok=True)
        pjson = Path(outdir) / "PHASE28_INVENTORY_REBALANCE_REPORT.json"
        pmd = Path(outdir) / "PHASE28_INVENTORY_REBALANCE_REPORT.md"
        pjson.write_text(json.dumps(report, indent=2))
        pmd.write_text(
            f"# PHASE28_INVENTORY_REBALANCE_REPORT\n\nStatus: ok\nSnapshots: {len(self.snapshots)}\n"
            f"Imbalances: {len(self.imbalances)}\nRebalance orders: {len(self.rebalance_orders)}\n"
            f"Applied: {len(self.applied)}\nPaper-only: True\n"
        )
        return str(pjson)


__all__ = ["InventoryRebalancer", "InventoryRebalanceConfig", "VenueInventory", "Imbalance", "RebalanceOrder"]
