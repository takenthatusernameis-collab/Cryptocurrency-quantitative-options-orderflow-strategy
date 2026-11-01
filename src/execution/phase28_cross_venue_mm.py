"""
Phase 28: Cross-Venue Options Market Making & Quote Arbitrage (crypto options + orderflow).
Aggregates per-venue Phase 27 quotes, detects cross-venue quote dislocations,
chooses best bid/ask across venues, routes via Phase 24 router.
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

from src.execution.phase24_cross_venue_router import CrossVenueRouter
from src.monitoring.phase18_observability import Phase18Observability
from src.options.phase27_market_maker import OptionsMarketMaker, MMConfig, Greeks, Fill, Quote
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
    h = hashlib.sha256(f"{seed}|p28|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p28_{tag}_{h}"


@dataclass(frozen=True)
class CrossVenueMMConfig:
    seed: int = 42
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL", "XRP")
    expiries: tuple = ("7D", "30D", "90D")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    base_spread_bps: float = 6.0
    risk_aversion: float = 0.5
    max_inventory: float = 200.0
    max_position_notional_usd: float = 2000000.0
    delta_limit: float = 500.0
    gamma_limit: float = 200.0
    vega_limit: float = 40000.0
    adverse_selection_threshold: float = 0.15
    min_quote_size: float = 0.01
    max_quote_size: float = 50.0
    dislocation_threshold_bps: float = 0.5
    enforce_gates: bool = True


@dataclass(frozen=True)
class VenueQuote:
    quote_id: str
    underlying: str
    expiry: str
    strike: float
    option_type: str
    venue: str
    bid: float
    ask: float
    bid_size: float
    ask_size: float
    mid: float
    spread_bps: float
    reservation_price: float
    orderflow_score: float
    adverse_selection_score: float
    paper_only: bool
    timestamp: str


@dataclass(frozen=True)
class CrossVenueQuote:
    quote_id: str
    underlying: str
    expiry: str
    strike: float
    option_type: str
    best_bid: float
    best_ask: float
    best_bid_venue: str
    best_ask_venue: str
    bid_size: float
    ask_size: float
    mid: float
    spread_bps: float
    dislocation_bps: float
    venues_quoted: List[str]
    paper_only: bool
    timestamp: str


@dataclass(frozen=True)
class Dislocation:
    dislocation_id: str
    underlying: str
    expiry: str
    strike: float
    option_type: str
    buy_venue: str
    sell_venue: str
    buy_ask: float
    sell_bid: float
    dislocation_bps: float
    notional_usd: float
    exploitable: bool
    paper_only: bool
    timestamp: str


@dataclass(frozen=True)
class RouteDecision:
    decision_id: str
    underlying: str
    side: str
    notional_usd: float
    primary_venue: str
    backup_venues: List[str]
    routed_split: Dict[str, float]
    expected_cost_bps: float
    expected_latency_ms: float
    paper_only: bool
    timestamp: str


class CrossVenueMarketMaker:
    def __init__(self, config: Optional[CrossVenueMMConfig] = None, seed: int = 42):
        self.config = config or CrossVenueMMConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("CrossVenueMarketMaker: paper_only must remain True (live path hard-gated)")
        self.config = CrossVenueMMConfig(
            seed=int(self.config.seed),
            paper_only=True,
            underlyings=tuple(self.config.underlyings),
            expiries=tuple(self.config.expiries),
            venues=tuple(self.config.venues),
            base_spread_bps=float(self.config.base_spread_bps),
            risk_aversion=float(self.config.risk_aversion),
            max_inventory=float(self.config.max_inventory),
            max_position_notional_usd=float(self.config.max_position_notional_usd),
            delta_limit=float(self.config.delta_limit),
            gamma_limit=float(self.config.gamma_limit),
            vega_limit=float(self.config.vega_limit),
            adverse_selection_threshold=float(self.config.adverse_selection_threshold),
            min_quote_size=float(self.config.min_quote_size),
            max_quote_size=float(self.config.max_quote_size),
            dislocation_threshold_bps=float(self.config.dislocation_threshold_bps),
            enforce_gates=bool(self.config.enforce_gates),
        )
        self.seed = int(self.config.seed)
        self._counter = 0
        self.mms: Dict[str, OptionsMarketMaker] = {}
        for idx, v in enumerate(self.config.venues):
            vcfg = MMConfig(
                seed=self.seed + 1000 + idx,
                paper_only=True,
                underlyings=self.config.underlyings,
                expiries=self.config.expiries,
                venues=(str(v).lower(),),
                base_spread_bps=self.config.base_spread_bps,
                risk_aversion=self.config.risk_aversion,
                max_inventory=self.config.max_inventory,
                max_position_notional_usd=self.config.max_position_notional_usd,
                delta_limit=self.config.delta_limit,
                gamma_limit=self.config.gamma_limit,
                vega_limit=self.config.vega_limit,
                adverse_selection_threshold=self.config.adverse_selection_threshold,
                min_quote_size=self.config.min_quote_size,
                max_quote_size=self.config.max_quote_size,
                enforce_gates=self.config.enforce_gates,
            )
            self.mms[str(v).lower()] = OptionsMarketMaker(config=vcfg)
        self.router = CrossVenueRouter(seed=self.seed + 20000)
        self.obs = Phase18Observability(seed=self.seed + 30000, paper_only=True)
        self.inventory: Dict[str, float] = {}
        self.venue_inventory: Dict[str, Dict[str, float]] = {v: {} for v in self.config.venues}
        self.greeks: Dict[str, Greeks] = {}
        self.quotes: List[CrossVenueQuote] = []
        self.dislocations: List[Dislocation] = []
        self.route_decisions: List[RouteDecision] = []
        self.fills: List[Fill] = []
        self.audit: List[Dict[str, Any]] = []

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        h = hashlib.sha256(f"{self.seed}|p28|{tag}|{self._counter}".encode()).hexdigest()[:12]
        return f"p28_{tag}_{h}"

    def make_venue_quotes(
        self,
        underlying: str,
        expiry: str,
        strike: float,
        option_type: str,
        mid: float,
        tape: List[Dict[str, Any]],
        depth: float,
        notional_usd: float,
        recent_trades: Optional[List[Dict[str, Any]]] = None,
    ) -> List[VenueQuote]:
        if not math.isfinite(mid) or mid <= 0:
            raise ValueError("mid must be positive finite")
        if not math.isfinite(depth) or depth < 0:
            raise ValueError("depth must be non-negative finite")
        venue_quotes: List[VenueQuote] = []
        inventory = self.inventory.get(underlying, 0.0)
        for v in self.config.venues:
            mm = self.mms[v]
            q = mm.make_quote(underlying, expiry, strike, option_type, v, mid, inventory, None, tape, depth, notional_usd, recent_trades)
            vq = VenueQuote(
                quote_id=self._next_id("venue_quote"),
                underlying=str(underlying),
                expiry=str(expiry),
                strike=float(strike),
                option_type=str(option_type),
                venue=str(v).lower(),
                bid=float(q.bid),
                ask=float(q.ask),
                bid_size=float(q.bid_size),
                ask_size=float(q.ask_size),
                mid=float(q.mid),
                spread_bps=float(q.spread_bps),
                reservation_price=float(q.reservation_price),
                orderflow_score=float(q.orderflow_score),
                adverse_selection_score=float(q.adverse_selection_score),
                paper_only=True,
                timestamp=_utc_now(),
            )
            _assert_finite(asdict(vq), f"venue_quote_{vq.quote_id}")
            venue_quotes.append(vq)
        self._log("venue_quotes", {"underlying": underlying, "venue_count": len(venue_quotes), "mid": mid})
        return venue_quotes

    def aggregate_best_quote(
        self,
        underlying: str,
        expiry: str,
        strike: float,
        option_type: str,
        venue_quotes: List[VenueQuote],
    ) -> CrossVenueQuote:
        if not venue_quotes:
            raise ValueError("venue_quotes must be non-empty")
        best_bid = max(vq.bid for vq in venue_quotes)
        best_ask = min(vq.ask for vq in venue_quotes)
        bid_vq = max(venue_quotes, key=lambda vq: vq.bid)
        ask_vq = min(venue_quotes, key=lambda vq: vq.ask)
        if best_ask <= best_bid:
            best_ask = best_bid * 1.0001
        mid = (best_bid + best_ask) / 2.0
        spread_bps = (best_ask - best_bid) / mid * 10000.0 if mid > 0 else 0.0
        max_bid = max(vq.bid for vq in venue_quotes)
        min_ask = min(vq.ask for vq in venue_quotes)
        dislocation_bps = (max_bid - min_ask) / min_ask * 10000.0 if min_ask > 0 else 0.0
        cvq = CrossVenueQuote(
            quote_id=self._next_id("cv_quote"),
            underlying=str(underlying),
            expiry=str(expiry),
            strike=float(strike),
            option_type=str(option_type),
            best_bid=float(best_bid),
            best_ask=float(best_ask),
            best_bid_venue=str(bid_vq.venue),
            best_ask_venue=str(ask_vq.venue),
            bid_size=float(bid_vq.bid_size),
            ask_size=float(ask_vq.ask_size),
            mid=float(mid),
            spread_bps=float(max(0.0, spread_bps)),
            dislocation_bps=float(max(0.0, dislocation_bps)),
            venues_quoted=[vq.venue for vq in venue_quotes],
            paper_only=True,
            timestamp=_utc_now(),
        )
        _assert_finite(asdict(cvq), f"cv_quote_{cvq.quote_id}")
        self.quotes.append(cvq)
        self._log("aggregate_quote", {"underlying": underlying, "best_bid": best_bid, "best_ask": best_ask, "spread_bps": spread_bps, "dislocation_bps": dislocation_bps})
        return cvq

    def detect_dislocations(
        self,
        underlying: str,
        expiry: str,
        strike: float,
        option_type: str,
        venue_quotes: List[VenueQuote],
        notional_usd: float = 100000.0,
    ) -> List[Dislocation]:
        dislocations: List[Dislocation] = []
        for buy_vq in venue_quotes:
            for sell_vq in venue_quotes:
                if sell_vq.venue == buy_vq.venue:
                    continue
                if sell_vq.bid > buy_vq.ask:
                    disloc_bps = (sell_vq.bid - buy_vq.ask) / buy_vq.ask * 10000.0
                    if disloc_bps >= self.config.dislocation_threshold_bps:
                        d = Dislocation(
                            dislocation_id=self._next_id("disloc"),
                            underlying=str(underlying),
                            expiry=str(expiry),
                            strike=float(strike),
                            option_type=str(option_type),
                            buy_venue=str(buy_vq.venue),
                            sell_venue=str(sell_vq.venue),
                            buy_ask=float(buy_vq.ask),
                            sell_bid=float(sell_vq.bid),
                            dislocation_bps=float(disloc_bps),
                            notional_usd=float(notional_usd),
                            exploitable=True,
                            paper_only=True,
                            timestamp=_utc_now(),
                        )
                        _assert_finite(asdict(d), f"dislocation_{d.dislocation_id}")
                        dislocations.append(d)
                        self.dislocations.append(d)
        self._log("detect_dislocations", {"underlying": underlying, "count": len(dislocations)})
        return dislocations

    def route_decision(
        self,
        underlying: str,
        side: str,
        notional_usd: float,
        idx: int = 0,
    ) -> RouteDecision:
        dec = self.router.route(str(underlying), str(side), float(notional_usd), venues=list(self.config.venues), idx=idx)
        rd = RouteDecision(
            decision_id=self._next_id("route"),
            underlying=str(underlying),
            side=str(side).lower(),
            notional_usd=float(notional_usd),
            primary_venue=str(dec.primary_venue),
            backup_venues=list(dec.backup_venues),
            routed_split=dict(dec.routed_split),
            expected_cost_bps=float(dec.expected_cost_bps),
            expected_latency_ms=float(dec.expected_latency_ms),
            paper_only=True,
            timestamp=_utc_now(),
        )
        _assert_finite(asdict(rd), f"route_{rd.decision_id}")
        self.route_decisions.append(rd)
        self._log("route", {"underlying": underlying, "side": side, "primary_venue": dec.primary_venue})
        return rd

    def update_greeks(self, underlying: str, greeks: Greeks) -> None:
        self.greeks[str(underlying)] = greeks
        _assert_finite(asdict(greeks), f"greeks_{underlying}")
        for mm in self.mms.values():
            mm.update_greeks(underlying, greeks)

    def apply_fill(self, fill: Fill, venue: Optional[str] = None) -> None:
        self.fills.append(fill)
        key = fill.underlying
        self.inventory[key] = self.inventory.get(key, 0.0) + (fill.fill_qty if fill.side == "buy" else -fill.fill_qty)
        self.inventory[key] = float(max(-self.config.max_inventory, min(self.config.max_inventory, self.inventory[key])))
        if venue is not None:
            v = str(venue).lower()
            self.venue_inventory.setdefault(v, {})
            self.venue_inventory[v][key] = self.venue_inventory[v].get(key, 0.0) + (fill.fill_qty if fill.side == "buy" else -fill.fill_qty)
            self.venue_inventory[v][key] = float(max(-self.config.max_inventory, min(self.config.max_inventory, self.venue_inventory[v][key])))
        self._log("fill", {"fill_id": fill.fill_id, "underlying": key, "side": fill.side, "qty": fill.fill_qty, "inventory": self.inventory[key], "venue": venue})

    def risk_state(self) -> Dict[str, Any]:
        total_delta = sum(g.delta for g in self.greeks.values())
        total_gamma = sum(g.gamma for g in self.greeks.values())
        total_vega = sum(g.vega for g in self.greeks.values())
        total_notional = sum(abs(v) * 100000.0 for v in self.inventory.values())
        rep = {
            "seed": self.seed,
            "inventory": {k: float(v) for k, v in self.inventory.items()},
            "venue_inventory": {v: {k: float(q) for k, q in inv.items()} for v, inv in self.venue_inventory.items()},
            "greeks": {k: asdict(g) for k, g in self.greeks.items()},
            "total_delta": float(total_delta),
            "total_gamma": float(total_gamma),
            "total_vega": float(total_vega),
            "total_position_notional_usd": float(total_notional),
            "within_limits": bool(abs(total_delta) <= self.config.delta_limit and abs(total_gamma) <= self.config.gamma_limit and total_vega <= self.config.vega_limit and total_notional <= self.config.max_position_notional_usd),
            "venue_count": len(self.mms),
            "quote_count": len(self.quotes),
            "dislocation_count": len(self.dislocations),
            "route_count": len(self.route_decisions),
            "fill_count": len(self.fills),
            "paper_only": True,
        }
        _assert_finite(rep, "cv_mm_risk_state")
        return rep

    def generate_report(self) -> Dict[str, Any]:
        rep = {
            "report": "PHASE28_CROSS_VENUE_MM_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "config": asdict(self.config),
            "risk_state": self.risk_state(),
            "venue_quotes": [asdict(q) for q in []],
            "quotes": [asdict(q) for q in self.quotes],
            "dislocations": [asdict(d) for d in self.dislocations],
            "route_decisions": [asdict(d) for d in self.route_decisions],
            "fills": [asdict(f) for f in self.fills],
            "audit": self.audit,
            "paper_only": True,
        }
        _assert_finite(rep, "cross_venue_mm_report")
        return serialize_metrics_strict(rep)

    def save_report(self, report: Dict[str, Any], outdir: str = "research_state") -> str:
        Path(outdir).mkdir(parents=True, exist_ok=True)
        pjson = Path(outdir) / "PHASE28_CROSS_VENUE_MM_REPORT.json"
        pmd = Path(outdir) / "PHASE28_CROSS_VENUE_MM_REPORT.md"
        pjson.write_text(json.dumps(report, indent=2))
        pmd.write_text(
            f"# PHASE28_CROSS_VENUE_MM_REPORT\n\nStatus: ok\nQuotes: {len(self.quotes)}\n"
            f"Dislocations: {len(self.dislocations)}\nRoutes: {len(self.route_decisions)}\n"
            f"Fills: {len(self.fills)}\nPaper-only: True\n"
        )
        return str(pjson)


__all__ = ["CrossVenueMarketMaker", "CrossVenueMMConfig", "VenueQuote", "CrossVenueQuote", "Dislocation", "RouteDecision"]
