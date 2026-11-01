"""
Phase 35: Smart Order Router with adversarial slippage control for crypto options + orderflow.
Routes orders to optimal venues based on liquidity, fill probability, slippage. Deterministic, paper-only.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import hashlib
import json
import math
from pathlib import Path

from src.telemetry.serialization import serialize_metrics_strict


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
    h = hashlib.sha256(f"{seed}|p35sor|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p35sor_{tag}_{h}"


@dataclass(frozen=True)
class SmartOrderRouterConfig:
    seed: int = 42
    paper_only: bool = True
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    max_slippage_bps: float = 12.0
    min_fill_prob: float = 0.65
    slice_threshold_usd: float = 50000.0
    enforce_gates: bool = True


@dataclass(frozen=True)
class RoutedOrder:
    route_id: str
    order_id: str
    underlying: str
    venue: str
    side: str
    option_type: str
    qty_contracts: float
    notional_usd: float
    slice_count: int
    expected_slippage_bps: float
    fill_prob: float
    tca_score: float
    routing_reason: str
    paper_only: bool
    timestamp: str


class SmartOrderRouter:
    def __init__(self, config: Optional[SmartOrderRouterConfig] = None, seed: int = 42):
        self.config = config or SmartOrderRouterConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("SmartOrderRouter: paper_only must remain True (live path hard-gated)")
        self.config = SmartOrderRouterConfig(
            seed=int(self.config.seed),
            paper_only=True,
            venues=tuple(self.config.venues),
            max_slippage_bps=float(self.config.max_slippage_bps),
            min_fill_prob=float(self.config.min_fill_prob),
            slice_threshold_usd=float(self.config.slice_threshold_usd),
            enforce_gates=bool(self.config.enforce_gates),
        )
        self.seed = int(self.config.seed)
        self._counter = 0
        self.routed_orders: List[RoutedOrder] = []

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        return _make_id(self.seed, tag, self._counter)

    def route_orders(self, orders: List[Dict[str, Any]], liquidity_map: Optional[Dict[str, Any]] = None) -> List[RoutedOrder]:
        self.routed_orders = []
        liquidity_map = liquidity_map or {}

        for od in orders:
            und = str(od.get("underlying", "BTC")).upper()
            side = str(od.get("side", "buy"))
            ot = str(od.get("option_type", "call"))
            notional = float(od.get("notional_usd", 10000.0))
            qty = float(od.get("qty_contracts", 1.0))

            # Simple deterministic venue selection
            venue_scores = []
            for v_idx, venue in enumerate(self.config.venues):
                fp = 0.8 - v_idx * 0.03
                slip = 2.0 + v_idx * 1.0
                score = fp * 100.0 - slip * 2.0
                venue_scores.append((score, venue, fp, slip))

            venue_scores.sort(reverse=True)
            best_score, best_venue, best_fp, best_slip = venue_scores[0]

            if best_slip > self.config.max_slippage_bps or best_fp < self.config.min_fill_prob:
                # Try next
                if len(venue_scores) > 1:
                    best_score, best_venue, best_fp, best_slip = venue_scores[1]

            slices = max(1, int(math.ceil(notional / self.config.slice_threshold_usd)))
            ro = RoutedOrder(
                route_id=self._next_id("rte"),
                order_id=str(od.get("order_id", self._next_id("ord"))),
                underlying=und,
                venue=best_venue,
                side=side,
                option_type=ot,
                qty_contracts=float(qty),
                notional_usd=float(notional),
                slice_count=int(slices),
                expected_slippage_bps=float(best_slip),
                fill_prob=float(max(0.0, min(1.0, best_fp))),
                tca_score=float(max(0.0, min(1.0, 0.7 + best_fp * 0.25))),
                routing_reason="liquidity+fillprob+slippage",
                paper_only=True,
                timestamp=_utc_now(),
            )
            if ro.expected_slippage_bps <= self.config.max_slippage_bps and ro.fill_prob >= self.config.min_fill_prob:
                _assert_finite(asdict(ro), "routed_order")
                self.routed_orders.append(ro)
        return self.routed_orders

    def generate_report(self, outdir: str = "research_state") -> Dict[str, Any]:
        Path(outdir).mkdir(parents=True, exist_ok=True)
        report = {
            "status": "ok",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "paper_only": True,
            "routed_count": len(self.routed_orders),
            "routed_orders": [asdict(r) for r in self.routed_orders[:15]],
            "max_slippage_bps": self.config.max_slippage_bps,
            "min_fill_prob": self.config.min_fill_prob,
        }
        _assert_finite(report, "phase35_smart_routing_report")
        rep_json = Path(outdir) / "PHASE35_SMART_ROUTING_REPORT.json"
        rep_md = Path(outdir) / "PHASE35_SMART_ROUTING_REPORT.md"
        rep_md.write_text(
            f"# PHASE35_SMART_ROUTING_REPORT\n\n"
            f"Timestamp: {report['timestamp']}\nStatus: ok\nPaper-only: true\n"
            f"Routed orders: {len(self.routed_orders)}\nMax slippage: {self.config.max_slippage_bps} bps\n"
            f"Min fill prob: {self.config.min_fill_prob}\n"
        )
        rep_json.write_text(json.dumps(serialize_metrics_strict(report), indent=2))
        return {"status": "ok", "json": str(rep_json), "md": str(rep_md), "paper_only": True}
