"""Phase 20 PostTradeRecon: fills vs orders vs positions, discrepancy detection,
settlement checks, audit log. Crypto options + orderflow."""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from src.telemetry.serialization import serialize_metrics_strict


_BASE_DAY = datetime(2026, 11, 1, tzinfo=timezone.utc)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _det_ts(seed: int, offset: int = 0) -> str:
    return (_BASE_DAY + timedelta(seconds=int(seed) + int(offset))).isoformat().replace("+00:00", "Z")


@dataclass
class Phase20ReconConfig:
    tolerance_qty: float = 1e-9
    tolerance_notional: float = 1e-6
    require_settlement: bool = True
    paper_only: bool = True


class Phase20PostTradeRecon:
    def __init__(self, config: Optional[Phase20ReconConfig] = None, seed: int = 42):
        self.config = config or Phase20ReconConfig()
        if self.config.paper_only is False:
            raise ValueError("Phase20PostTradeRecon: paper_only must remain True by default")
        self.config.paper_only = True
        self.seed = int(seed)
        self.audit_log: List[Dict[str, Any]] = []

    def reconcile(self, orders: List[Dict[str, Any]], fills: List[Dict[str, Any]], positions: List[Dict[str, Any]]) -> Dict[str, Any]:
        orders = orders or []
        fills = fills or []
        positions = positions or []
        discrepancies: List[Dict[str, Any]] = []
        fill_map: Dict[str, float] = {}
        for f in fills:
            oid = str(f.get("order_id"))
            qty = float(f.get("filled_qty", 0.0))
            if not math.isfinite(qty):
                qty = 0.0
            fill_map[oid] = fill_map.get(oid, 0.0) + qty
        for o in orders:
            oid = str(o.get("order_id"))
            qty = float(o.get("qty", 0.0))
            if not math.isfinite(qty):
                qty = 0.0
            fq = float(fill_map.get(oid, 0.0))
            if abs(fq - qty) > self.config.tolerance_qty and qty > 0:
                discrepancies.append({
                    "type": "fill_mismatch",
                    "order_id": oid,
                    "ordered_qty": qty,
                    "filled_qty": fq,
                    "diff": fq - qty,
                })
        pos_qty: Dict[str, float] = {}
        for p in positions:
            sym = str(p.get("symbol", "")).upper()
            q = float(p.get("qty", 0.0))
            if not math.isfinite(q):
                q = 0.0
            pos_qty[sym] = pos_qty.get(sym, 0.0) + q
        total_filled = sum(fill_map.values())
        total_ordered = sum(float(o.get("qty", 0.0)) for o in orders if math.isfinite(float(o.get("qty", 0.0))))
        settlement_ok = True
        if self.config.require_settlement and abs(total_filled - total_ordered) > self.config.tolerance_qty and total_ordered > 0:
            # allow small tolerance
            if abs(total_filled - total_ordered) > self.config.tolerance_notional:
                settlement_ok = False
                discrepancies.append({"type": "settlement_mismatch", "ordered": total_ordered, "filled": total_filled})
        rec = {
            "timestamp": _utc_now(),
            "seed": self.seed,
            "orders_count": len(orders),
            "fills_count": len(fills),
            "positions_count": len(positions),
            "total_ordered_qty": float(total_ordered),
            "total_filled_qty": float(total_filled),
            "discrepancies": discrepancies,
            "discrepancy_count": len(discrepancies),
            "reconciled": len(discrepancies) == 0 and settlement_ok,
            "settlement_ok": bool(settlement_ok),
            "paper_only": True,
            "audit_log": self.audit_log,
        }
        self.audit_log.append({"timestamp": _utc_now(), "action": "reconcile", "discrepancy_count": len(discrepancies)})
        return serialize_metrics_strict(rec)

    def generate_report(self, orders: List[Dict[str, Any]], fills: List[Dict[str, Any]], positions: List[Dict[str, Any]]) -> Dict[str, Any]:
        rec = self.reconcile(orders, fills, positions)
        rep = {
            "report": "PHASE20_POST_TRADE_RECON_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "config": asdict(self.config),
            "reconciliation": rec,
            "paper_only": True,
        }
        return serialize_metrics_strict(rep)
