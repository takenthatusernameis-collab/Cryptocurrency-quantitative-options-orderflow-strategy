"""Cross-venue arbitrage + market-making orchestrator (Phase 15).

Unified coordination of arbitrage detection, delta-neutral market making, and
latency-aware routing for crypto options + orderflow. PnL tracking, kill-switch
integration, and deterministic state serialization. Default paper-only.
"""

from __future__ import annotations

import hashlib
import math
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.arbitrage import (
    ArbitrageDetector,
    ArbitrageConfig,
    ArbitrageOpportunity,
    ArbitrageQuote,
    default_arbitrage_config,
)
from src.marketmaking import DeltaNeutralMM, MMConfig, default_mm_config
from src.execution.latency_aware_router import (
    LatencyAwareRouter,
    LatencyRouterConfig,
    default_latency_router_config,
)
from src.telemetry.serialization import serialize_metrics_strict, assert_json_valid
from src.errors import DataError, RiskLimitError, ValidationError, get_logger
from src.utils.numerical_guards import safe_divide, validate_finite

_logger = get_logger(__name__)

DEFAULT_SYMBOLS = ("BTC", "ETH")
DEFAULT_VENUES = ("deribit", "okx", "binance")
_BASE_TS = datetime(2026, 11, 1, tzinfo=timezone.utc)


def _det_ts(seed: int) -> str:
    return (_BASE_TS + timedelta(seconds=int(seed))).isoformat().replace("+00:00", "Z")


def _cid(prefix: str, seed: int, counter: int) -> str:
    digest = hashlib.sha256(f"{seed}|{prefix}|{counter}".encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def _validate_symbol(symbol: str) -> str:
    s = str(symbol).upper()
    if not s:
        raise ValidationError("symbol must be non-empty")
    return s


def _validate_venue(venue: str) -> str:
    v = str(venue).lower()
    if v not in DEFAULT_VENUES:
        raise ValidationError(f"unsupported venue {venue!r}", context={"venue": v, "supported": list(DEFAULT_VENUES)})
    return v


def _git_sha() -> str:
    sha = os.environ.get("GIT_SHA")
    if sha:
        return str(sha)
    try:
        import subprocess

        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


@dataclass
class CrossVenueConfig:
    symbols: Tuple[str, ...] = ("BTC", "ETH")
    venues: Tuple[str, ...] = ("deribit", "okx", "binance")
    seed: int = 42
    paper_only: bool = True
    outdir: str = "research_state"
    cycles: int = 5
    arb_fill_ratio: float = 0.9

    def __post_init__(self) -> None:
        self.symbols = tuple(_validate_symbol(s) for s in self.symbols)
        if not self.symbols:
            raise ValidationError("symbols must be non-empty")
        self.venues = tuple(_validate_venue(v) for v in self.venues)
        if not self.venues:
            raise ValidationError("venues must be non-empty")
        if not math.isfinite(self.seed) or int(self.seed) < 0:
            raise ValidationError("seed must be a non-negative integer")
        self.seed = int(self.seed)
        self.paper_only = True
        if not self.outdir:
            raise ValidationError("outdir must be non-empty")
        self.outdir = str(self.outdir)
        if not math.isfinite(self.cycles) or int(self.cycles) < 1:
            raise ValidationError("cycles must be >= 1")
        self.cycles = int(self.cycles)
        if not math.isfinite(self.arb_fill_ratio) or not 0.0 < self.arb_fill_ratio <= 1.0:
            raise ValidationError("arb_fill_ratio must be in (0,1]")


def default_cross_venue_config() -> CrossVenueConfig:
    return CrossVenueConfig()


@dataclass
class CrossVenueOrchestrator:
    """Unified coordinator for Phase 15 cross-venue strategies."""

    config: Optional[CrossVenueConfig] = None
    seed: int = 42
    paper_only: bool = True
    outdir: Optional[str] = None

    def __post_init__(self) -> None:
        self.config = self.config or default_cross_venue_config()
        self.config.paper_only = True
        self.seed = int(self.seed)
        self.paper_only = True
        self.outdir = self.outdir or self.config.outdir
        Path(self.outdir).mkdir(parents=True, exist_ok=True)

        arb_cfg = ArbitrageConfig(
            venues=self.config.venues,
            symbols=self.config.symbols,
            seed=self.seed,
        )
        mm_cfg = MMConfig(
            symbols=self.config.symbols,
            venues=self.config.venues,
            seed=self.seed,
        )
        rtr_cfg = LatencyRouterConfig(
            venues=self.config.venues,
            symbols=self.config.symbols,
            seed=self.seed,
        )

        self.detector = ArbitrageDetector(config=arb_cfg, seed=self.seed)
        self.mm = DeltaNeutralMM(config=mm_cfg, seed=self.seed)
        self.router = LatencyAwareRouter(config=rtr_cfg, seed=self.seed)

        self.cycle_counter = 0
        self.cycle_results: List[Dict[str, Any]] = []
        self.realized_pnl_usd: float = 0.0
        self.cash_usd: float = 0.0
        self.halted: bool = False
        self.halt_reason: Optional[str] = None
        self.halted_at: Optional[str] = None
        self.snapshot: Optional[Dict[str, Any]] = None
        self.last_report: Optional[Dict[str, Any]] = None
        self._snapshot_counter = 0

    # -- market data --------------------------------------------------------
    def submit_market_snapshot(
        self,
        quotes: List[Dict[str, Any]],
        marks: Dict[str, float],
        implied_vols: Optional[Dict[str, float]] = None,
    ) -> int:
        implied_vols = implied_vols or {}
        accepted = 0
        for entry in quotes:
            if not isinstance(entry, dict):
                raise DataError("quote entry must be a dict", context={"type": type(entry).__name__})
            quote = ArbitrageQuote(
                venue=str(entry["venue"]),
                symbol=str(entry["symbol"]),
                bid=float(entry["bid"]),
                ask=float(entry["ask"]),
                bid_size=float(entry.get("bid_size", 0.0)),
                ask_size=float(entry.get("ask_size", 0.0)),
                timestamp=str(entry["timestamp"]),
                received_at=str(entry.get("received_at", entry["timestamp"])),
                source=str(entry.get("source", "orderflow")),
            )
            if quote.venue not in self.config.venues or quote.symbol not in self.config.symbols:
                continue
            self.detector.submit_quotes([quote])
            self.router.update_quote(
                quote.venue,
                quote.symbol,
                quote.bid,
                quote.ask,
                quote.bid_size,
                quote.ask_size,
                quote.received_at,
            )
            accepted += 1

        spot: Dict[str, float] = {}
        for symbol in self.config.symbols:
            spot[symbol] = float(validate_finite(marks.get(symbol, 65000.0 + (1000.0 if symbol == "ETH" else 0.0)), f"mark[{symbol}]"))
        iv: Dict[str, float] = {}
        for symbol in self.config.symbols:
            raw = implied_vols.get(symbol)
            iv[symbol] = float(validate_finite(raw, f"iv[{symbol}]")) if raw is not None else 0.5

        self._snapshot_counter += 1
        self.snapshot = {
            "snapshot_id": _cid("snap", self.seed, self._snapshot_counter),
            "timestamp": _det_ts(self.seed),
            "seed": self.seed,
            "symbols": list(self.config.symbols),
            "venues": list(self.config.venues),
            "quotes_accepted": accepted,
            "spots": spot,
            "implied_vols": iv,
            "paper_only": True,
        }
        _logger.info("orchestrator.snapshot", snapshot_id=self.snapshot["snapshot_id"], quotes=accepted, seed=self.seed)
        return accepted

    def _synthetic_snapshot(self, cycle: int) -> None:
        """Deterministic synthetic market snapshot for a cycle (seed-driven)."""
        rng_seed = self.seed * 1000 + cycle
        import random

        rng = random.Random(rng_seed)
        base = {"BTC": 65000.0, "ETH": 66000.0}
        ivs = {"BTC": 0.60, "ETH": 0.70}
        quotes: List[Dict[str, Any]] = []
        marks: Dict[str, float] = {}
        for symbol in self.config.symbols:
            drift = 1.0 + (rng.random() - 0.5) * 0.002
            marks[symbol] = base[symbol] * drift
            ivs[symbol] = ivs.get(symbol, 0.6) + (rng.random() - 0.5) * 0.02
            for venue in self.config.venues:
                spread_bps = rng.random() * 3.0 + 0.5
                mid = marks[symbol]
                half = spread_bps / 2.0 / 10000.0 * mid
                bid = mid - half
                ask = mid + half
                size = rng.random() * 5.0 + 0.5
                quotes.append({
                    "venue": venue,
                    "symbol": symbol,
                    "bid": round(bid, 4),
                    "ask": round(ask, 4),
                    "bid_size": round(size, 4),
                    "ask_size": round(size, 4),
                    "timestamp": _det_ts(self.seed),
                    "received_at": _det_ts(self.seed),
                    "source": "synthetic_orderflow",
                })
                self.router.record_latency(venue, rng.random() * 40.0 + 10.0, symbol)
        self.submit_market_snapshot(quotes, marks, ivs)

    # -- kill switch --------------------------------------------------------
    def trigger_kill_switch(self, reason: str, source: str = "orchestrator") -> None:
        self.halted = True
        self.halt_reason = str(reason)
        self.halted_at = _det_ts(self.seed)
        self.mm.trigger_kill_switch(reason, source=source)
        _logger.error("orchestrator.kill_switch", reason=reason, source=source, seed=self.seed)

    def is_halted(self) -> bool:
        return bool(self.halted or self.mm.halted)

    # -- cycle --------------------------------------------------------------
    def run_cycle(self, cycle: Optional[int] = None) -> Dict[str, Any]:
        if self.is_halted():
            return {
                "status": "halted",
                "cycle": cycle if cycle is not None else self.cycle_counter + 1,
                "reason": self.halt_reason,
                "timestamp": _det_ts(self.seed),
                "paper_only": True,
            }

        cycle = self.cycle_counter + 1 if cycle is None else int(cycle)
        self.cycle_counter = max(self.cycle_counter, cycle)
        timestamp = _det_ts(self.seed)

        # Deterministic market data for this cycle.
        self._synthetic_snapshot(cycle)
        snap = self.snapshot
        spots = snap["spots"]
        ivs = snap["implied_vols"]

        # 1) Arbitrage detection + paper execution.
        opportunities = self.detector.detect(spots, ivs)
        arb_report = self.detector.generate_report(opportunities)
        arb_pnl_usd = 0.0
        fills: List[Dict[str, Any]] = []
        for opportunity in opportunities:
            if not opportunity.qualified:
                continue
            size = opportunity.estimated_size * self.config.arb_fill_ratio
            fill_px = (opportunity.bid_price + opportunity.ask_price) / 2.0
            pnl = opportunity.net_edge_usd * self.config.arb_fill_ratio
            if not math.isfinite(pnl):
                raise DataError("non-finite arb pnl", context={"opportunity_id": opportunity.opportunity_id})
            arb_pnl_usd += pnl
            fills.append({
                "fill_id": _cid("fill", self.seed, len(fills) + 1),
                "opportunity_id": opportunity.opportunity_id,
                "symbol": opportunity.symbol,
                "buy_venue": opportunity.buy_venue,
                "sell_venue": opportunity.sell_venue,
                "size": float(size),
                "price": float(fill_px),
                "pnl_usd": float(pnl),
                "net_edge_bps": opportunity.net_edge_bps,
                "timestamp": timestamp,
                "paper_only": True,
            })

        # 2) Market making marks + risk check.
        self.mm.update_marks(spots, ivs)
        risk = self.mm.risk_check()
        if not risk["within_limits"]:
            self.trigger_kill_switch(f"risk_limit_breach: {','.join(risk['breaches'])}", source="risk_check")
            return {
                "status": "halted",
                "cycle": cycle,
                "reason": self.halt_reason,
                "risk_breaches": risk["breaches"],
                "timestamp": timestamp,
                "paper_only": True,
            }
        if self.mm.drawdown_guard_active():
            self.trigger_kill_switch("drawdown_guard_active", source="risk_check")
            return {
                "status": "halted",
                "cycle": cycle,
                "reason": self.halt_reason,
                "timestamp": timestamp,
                "paper_only": True,
            }

        # 3) Delta-neutral hedges via latency-aware router.
        hedge_results: List[Dict[str, Any]] = []
        hedge_cost_bps_total = 0.0
        for symbol in self.config.symbols:
            signal = self.mm.hedge_signal(symbol, spot=spots.get(symbol))
            if signal is None:
                continue
            route = self.router.route_intent(
                {"symbol": symbol, "side": signal["side"], "quantity": signal["size"], "price": signal["px"]},
                spot=spots,
            )
            self.router.track_fill(route.order_id, route.price, quantity=route.quantity, commission=route.total_cost_bps / 10000.0 * route.quantity * route.price, symbol=symbol)
            self.mm.apply_hedge(signal, route.price)
            hedge_cost_bps_total += route.total_cost_bps
            hedge_results.append({
                "symbol": symbol,
                "side": signal["side"],
                "size": signal["size"],
                "route": route.to_dict(),
                "notional_usd": signal["notional_usd"],
                "cost_bps": route.total_cost_bps,
                "timestamp": timestamp,
                "paper_only": True,
            })

        self.mm._recompute_equity()
        self.realized_pnl_usd += arb_pnl_usd
        self.cash_usd += arb_pnl_usd - hedge_cost_bps_total / 10000.0 * sum(h["notional_usd"] for h in hedge_results)

        mm_report = self.mm.generate_report()
        rtr_report = self.router.generate_report()

        cycle_result: Dict[str, Any] = {
            "cycle": cycle,
            "timestamp": timestamp,
            "status": "completed",
            "paper_only": True,
            "spots": spots,
            "implied_vols": ivs,
            "arbitrage": {
                "opportunities": len(opportunities),
                "qualified": sum(1 for o in opportunities if o.qualified),
                "fills": len(fills),
                "pnl_usd": float(arb_pnl_usd),
            },
            "fills": fills,
            "market_making": {
                "positions": len(self.mm.positions),
                "net_pnl_usd": float(mm_report["pnl"]["net_pnl_usd"]),
                "unrealized_pnl_usd": float(mm_report["pnl"]["unrealized_pnl_usd"]),
                "realized_pnl_usd": float(mm_report["pnl"]["realized_pnl_usd"]),
                "drawdown_pct": float(mm_report["pnl"]["drawdown_pct"]),
                "inventory_skew": {s: float(mm_report["per_symbol"][s]["inventory_skew"]) for s in self.config.symbols},
                "net_delta_usd": {s: float(mm_report["per_symbol"][s]["net_delta_usd"]) for s in self.config.symbols},
                "risk_within_limits": bool(risk["within_limits"]),
                "risk_breaches": risk["breaches"],
            },
            "latency_routing": {
                "routes": rtr_report["counts"]["routes"],
                "avg_cost_bps": float(rtr_report["routing"]["avg_cost_bps"]),
                "avg_latency_ms": float(rtr_report["routing"]["avg_latency_ms"]),
                "slippage_bps": float(rtr_report["slippage"]["avg_slippage_bps"]),
            },
            "hedges": hedge_results,
            "hedge_cost_bps_total": float(hedge_cost_bps_total),
            "pnl_snapshot": {
                "realized_pnl_usd": float(self.realized_pnl_usd),
                "cash_usd": float(self.cash_usd),
                "unrealized_pnl_usd": float(mm_report["pnl"]["unrealized_pnl_usd"]),
                "net_pnl_usd": float(self.realized_pnl_usd + self.cash_usd + mm_report["pnl"]["unrealized_pnl_usd"]),
            },
        }
        self.cycle_results.append(cycle_result)
        _logger.info("orchestrator.cycle_complete", cycle=cycle, status="completed", arb_fills=len(fills), hedges=len(hedge_results), seed=self.seed)
        return cycle_result

    # -- reporting / state --------------------------------------------------
    def generate_report(self) -> Dict[str, Any]:
        mm_report = self.mm.generate_report()
        rtr_report = self.router.generate_report()
        arb_report = self.detector.generate_report()
        total_cycles = len(self.cycle_results)
        completed = sum(1 for c in self.cycle_results if c.get("status") == "completed")
        halted = sum(1 for c in self.cycle_results if c.get("status") == "halted")
        total_arb_fills = sum(c["arbitrage"]["fills"] for c in self.cycle_results)
        total_arb_pnl = sum(c["arbitrage"]["pnl_usd"] for c in self.cycle_results)
        total_hedges = sum(len(c["hedges"]) for c in self.cycle_results)
        net_pnl = self.realized_pnl_usd + self.cash_usd + mm_report["pnl"]["unrealized_pnl_usd"]
        report: Dict[str, Any] = {
            "report": "CROSSVENUE_ORCHESTRATION_REPORT",
            "orchestrator": "CrossVenueOrchestrator",
            "campaign": "phase15_crossvenue",
            "campaign_id": f"phase15_{self.seed}",
            "seed": self.seed,
            "symbols": list(self.config.symbols),
            "venues": list(self.config.venues),
            "paper_only": True,
            "timestamp": _det_ts(self.seed),
            "git_sha": _git_sha(),
            "status": "halted" if self.is_halted() else "completed",
            "kill_switch": {
                "triggered": bool(self.halted or self.mm.halted),
                "reason": self.halt_reason or self.mm.halt_reason,
                "halted_at": self.halted_at,
                "source": "orchestrator",
            },
            "counts": {
                "cycles": total_cycles,
                "cycles_completed": completed,
                "cycles_halted": halted,
                "opportunities": arb_report["counts"]["opportunities_detected"],
                "qualified_opportunities": arb_report["counts"]["qualified"],
                "arb_fills": total_arb_fills,
                "hedges": total_hedges,
                "mm_positions": len(self.mm.positions),
                "router_routes": rtr_report["counts"]["routes"],
                "router_fills": rtr_report["counts"]["fills"],
                "router_cancels": rtr_report["counts"]["cancels"],
                "router_replacements": rtr_report["counts"]["replacements"],
            },
            "pnl": {
                "realized_pnl_usd": float(self.realized_pnl_usd),
                "cash_usd": float(self.cash_usd),
                "unrealized_pnl_usd": float(mm_report["pnl"]["unrealized_pnl_usd"]),
                "net_pnl_usd": float(net_pnl),
                "drawdown_pct": float(mm_report["pnl"]["drawdown_pct"]),
            },
            "arbitrage_summary": {
                "report": arb_report["report"],
                "counts": arb_report["counts"],
                "qualified_net_edges_bps": [o["net_edge_bps"] for o in arb_report["opportunities"] if o["qualified"]],
            },
            "market_making_summary": {
                "report": mm_report["report"],
                "counts": mm_report["counts"],
                "pnl": mm_report["pnl"],
                "risk_within_limits": bool(mm_report["risk"]["within_limits"]),
                "breaches": mm_report["risk"]["breaches"],
                "per_symbol": mm_report["per_symbol"],
            },
            "latency_routing_summary": {
                "report": rtr_report["report"],
                "counts": rtr_report["counts"],
                "routing": rtr_report["routing"],
                "slippage": rtr_report["slippage"],
                "latency": rtr_report["latency"],
            },
            "cycles": self.cycle_results,
        }
        serialized = serialize_metrics_strict(report)
        assert_json_valid(serialized)
        self.last_report = serialized
        return serialized

    def validate_invariants(self) -> Dict[str, Any]:
        problems: List[str] = []
        if not self.paper_only:
            problems.append("paper_only not enforced")
        arb_inv = self.detector.validate_invariants()
        mm_inv = self.mm.validate_invariants()
        rtr_inv = self.router.validate_invariants()
        for label, inv in (("arbitrage", arb_inv), ("market_making", mm_inv), ("routing", rtr_inv)):
            if not inv["valid"]:
                problems.extend(f"{label}:{p}" for p in inv["problems"][:10])
        for cycle in self.cycle_results:
            if cycle.get("status") not in ("completed", "halted"):
                problems.append(f"invalid cycle status {cycle.get('cycle')}")
            pnl = cycle.get("pnl_snapshot", {})
            for name in ("realized_pnl_usd", "cash_usd", "unrealized_pnl_usd", "net_pnl_usd"):
                if not math.isfinite(float(pnl.get(name, 0.0))):
                    problems.append(f"non-finite cycle pnl {name} cycle {cycle.get('cycle')}")
        return {
            "valid": len(problems) == 0,
            "problems": problems[:50],
            "problem_count": len(problems),
            "cycle_count": len(self.cycle_results),
            "halted": bool(self.is_halted()),
            "paper_only_enforced": True,
        }

    def save_state(self, path: Path) -> str:
        state = {
            "orchestrator": "CrossVenueOrchestrator",
            "campaign": "phase15_crossvenue",
            "seed": self.seed,
            "symbols": list(self.config.symbols),
            "venues": list(self.config.venues),
            "paper_only": True,
            "timestamp": _det_ts(self.seed),
            "cycle_counter": self.cycle_counter,
            "halted": bool(self.is_halted()),
            "halt_reason": self.halt_reason,
            "realized_pnl_usd": float(self.realized_pnl_usd),
            "cash_usd": float(self.cash_usd),
            "config": asdict(self.config),
            "cycle_results": self.cycle_results,
            "mm_positions": [p.to_dict() for p in self.mm.positions.values()],
            "mm_perp_inventory": {s: float(v) for s, v in self.mm.perp_inventory.items()},
            "router_orders": list(self.router.orders.values()),
            "router_fills": [f.to_dict() for f in self.router.fills],
        }
        serialized = serialize_metrics_strict(state)
        content = __import__("json").dumps(serialized, ensure_ascii=False, indent=2, allow_nan=False)
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return str(path)

    def load_state(self, path: Path) -> None:
        import json

        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if str(data.get("campaign")) != "phase15_crossvenue":
            raise DataError("not a phase15 cross-venue state file", context={"path": str(path)})
        self.cycle_counter = int(data.get("cycle_counter", 0))
        self.halted = bool(data.get("halted", False))
        self.halt_reason = data.get("halt_reason")
        self.realized_pnl_usd = float(data.get("realized_pnl_usd", 0.0))
        self.cash_usd = float(data.get("cash_usd", 0.0))
        self.cycle_results = data.get("cycle_results", [])
        self.halted_at = data.get("halted_at", self.halted_at if self.halted else None)


__all__ = [
    "CrossVenueOrchestrator",
    "CrossVenueConfig",
    "default_cross_venue_config",
    "DEFAULT_SYMBOLS",
    "DEFAULT_VENUES",
]
