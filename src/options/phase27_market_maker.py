"""
Phase 27: Crypto Options Market Making with Orderflow-Informed Quoting
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
    h = hashlib.sha256(f"{seed}|p27|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p27_{tag}_{h}"


@dataclass(frozen=True)
class MMConfig:
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
    enforce_gates: bool = True


@dataclass(frozen=True)
class Greeks:
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float


@dataclass(frozen=True)
class Quote:
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
    inventory_skew: float
    adverse_selection_score: float
    orderflow_score: float
    paper_only: bool
    timestamp: str


@dataclass(frozen=True)
class Fill:
    fill_id: str
    quote_id: str
    underlying: str
    side: str
    fill_qty: float
    fill_price: float
    timestamp: str
    paper_only: bool


class OptionsMarketMaker:
    def __init__(self, config: Optional[MMConfig] = None, seed: int = 42):
        self.config = config or MMConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("OptionsMarketMaker: paper_only must remain True (live path hard-gated)")
        self.config = MMConfig(
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
            enforce_gates=bool(self.config.enforce_gates),
        )
        self.seed = int(self.config.seed)
        self.inventory: Dict[str, float] = {}
        self.greeks: Dict[str, Greeks] = {}
        self.quotes: List[Quote] = []
        self.fills: List[Fill] = []
        self._counter = 0
        self.audit: List[Dict[str, Any]] = []

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        h = hashlib.sha256(f"{self.seed}|p27|{tag}|{self._counter}".encode()).hexdigest()[:12]
        return f"p27_{tag}_{h}"

    def compute_orderflow_score(self, tape: List[Dict[str, Any]]) -> float:
        if not tape:
            return 0.0
        imb: List[float] = []
        tox: List[float] = []
        for t in tape:
            bid = float(t.get("bid_vol", 0.0))
            ask = float(t.get("ask_vol", 0.0))
            tot = bid + ask
            if tot > 0:
                imb.append((bid - ask) / tot)
            tox.append(float(t.get("toxicity", 0.0)))
        s_imb = sum(imb) / len(imb) if imb else 0.0
        s_tox = sum(tox) / len(tox) if tox else 0.0
        score = 0.6 * s_imb - 0.4 * s_tox
        if not math.isfinite(score):
            raise ValueError("non-finite orderflow score")
        return float(max(-1.0, min(1.0, score)))

    def compute_informed_flow(self, tape: List[Dict[str, Any]], trades: Optional[List[Dict[str, Any]]] = None) -> float:
        of = self.compute_orderflow_score(tape)
        informed = 0.0
        if trades:
            buy_vol = 0.0
            sell_vol = 0.0
            for x in trades:
                side = str(x.get("aggressor_side", "")).lower()
                qty = float(x.get("qty", 0.0))
                if side == "buy":
                    buy_vol += qty
                elif side == "sell":
                    sell_vol += qty
            tot = buy_vol + sell_vol
            if tot > 0:
                informed = (buy_vol - sell_vol) / tot
        if not math.isfinite(informed):
            informed = 0.0
        combined = 0.7 * of + 0.3 * float(max(-1.0, min(1.0, informed)))
        return float(max(-1.0, min(1.0, combined)))

    def reservation_price(self, mid: float, inventory: float, greeks: Optional[Greeks] = None) -> float:
        if not math.isfinite(mid) or mid <= 0:
            raise ValueError("mid must be positive finite")
        inv = float(max(-self.config.max_inventory, min(self.config.max_inventory, inventory)))
        skew = self.config.risk_aversion * inv
        if greeks is not None:
            skew += 0.05 * float(greeks.gamma) * inv
        res = mid - skew
        if not math.isfinite(res) or res <= 0:
            raise ValueError("non-finite or non-positive reservation price")
        return float(res)

    def adverse_selection_filter(self, tape: List[Dict[str, Any]], recent_trades: Optional[List[Dict[str, Any]]] = None, orderflow_score: Optional[float] = None) -> Dict[str, Any]:
        if orderflow_score is None:
            orderflow_score = self.compute_orderflow_score(tape)
        informed = self.compute_informed_flow(tape, recent_trades)
        score = 0.6 * orderflow_score + 0.4 * informed
        score = float(max(-1.0, min(1.0, score)))
        toxicity = 0.0
        if tape:
            toxicity = sum(float(t.get("toxicity", 0.0)) for t in tape) / len(tape)
        adv_prob = 0.5 * abs(score) + 0.5 * toxicity
        adv_prob = float(max(0.0, min(1.0, adv_prob)))
        flagged = adv_prob > self.config.adverse_selection_threshold
        rep = {
            "orderflow_score": float(orderflow_score),
            "informed_flow": float(informed),
            "adverse_selection_score": float(score),
            "toxicity": float(toxicity),
            "adverse_selection_probability": float(adv_prob),
            "flagged": bool(flagged),
            "threshold": float(self.config.adverse_selection_threshold),
        }
        _assert_finite(rep, "adverse_selection_filter")
        return rep

    def quote_size(self, notional_usd: float, inventory: float, depth: float, side: str) -> float:
        base = notional_usd / 100000.0
        inv_pct = inventory / max(1e-9, self.config.max_inventory)
        penalty = 1.0
        if side == "bid" and inventory > 0:
            penalty = max(0.1, 1.0 - inv_pct)
        elif side == "ask" and inventory < 0:
            penalty = max(0.1, 1.0 + inv_pct)
        size = base * penalty * min(1.0, depth)
        size = float(max(self.config.min_quote_size, min(self.config.max_quote_size, size)))
        if not math.isfinite(size):
            raise ValueError("non-finite quote size")
        return size

    def spread_bps(self, orderflow_score: float, adverse_selection_prob: float, depth: float) -> float:
        sprd = self.config.base_spread_bps
        sprd += 2.0 * abs(orderflow_score)
        sprd += 3.0 * adverse_selection_prob
        sprd += 1.0 * max(0.0, (1.0 - depth))
        sprd = float(max(1.0, min(200.0, sprd)))
        if not math.isfinite(sprd):
            raise ValueError("non-finite spread")
        return sprd

    def make_quote(
        self,
        underlying: str,
        expiry: str,
        strike: float,
        option_type: str,
        venue: str,
        mid: float,
        inventory: float,
        greeks: Optional[Greeks],
        tape: List[Dict[str, Any]],
        depth: float,
        notional_usd: float,
        recent_trades: Optional[List[Dict[str, Any]]] = None,
    ) -> Quote:
        if not math.isfinite(mid) or mid <= 0:
            raise ValueError("mid must be positive finite")
        of_score = self.compute_orderflow_score(tape)
        adv = self.adverse_selection_filter(tape, recent_trades, orderflow_score=of_score)
        res_price = self.reservation_price(mid, inventory, greeks)
        inv_skew = res_price - mid
        sprd = self.spread_bps(of_score, adv["adverse_selection_probability"], depth)
        half = sprd / 2.0 / 10000.0 * res_price
        bid = res_price - half
        ask = res_price + half
        if bid <= 0:
            bid = res_price * 0.999
        if ask <= bid:
            ask = bid * 1.0001
        bid_size = self.quote_size(notional_usd, inventory, depth, "bid")
        ask_size = self.quote_size(notional_usd, inventory, depth, "ask")
        if adv["flagged"]:
            bid_size *= 0.5
            ask_size *= 0.5
            sprd *= 1.5
            half = sprd / 2.0 / 10000.0 * res_price
            bid = res_price - half
            ask = res_price + half
        q = Quote(
            quote_id=self._next_id("quote"),
            underlying=str(underlying),
            expiry=str(expiry),
            strike=float(strike),
            option_type=str(option_type),
            venue=str(venue).lower(),
            bid=float(bid),
            ask=float(ask),
            bid_size=float(bid_size),
            ask_size=float(ask_size),
            mid=float(mid),
            spread_bps=float(sprd),
            reservation_price=float(res_price),
            inventory_skew=float(inv_skew),
            adverse_selection_score=float(adv["adverse_selection_score"]),
            orderflow_score=float(of_score),
            paper_only=True,
            timestamp=_utc_now(),
        )
        _assert_finite(asdict(q), f"quote_{q.quote_id}")
        self.quotes.append(q)
        self._log("quote", {"quote_id": q.quote_id, "underlying": underlying, "bid": bid, "ask": ask, "spread_bps": sprd, "flagged": adv["flagged"]})
        return q

    def apply_fill(self, fill: Fill) -> None:
        self.fills.append(fill)
        key = fill.underlying
        self.inventory[key] = self.inventory.get(key, 0.0) + (fill.fill_qty if fill.side == "buy" else -fill.fill_qty)
        self.inventory[key] = float(max(-self.config.max_inventory, min(self.config.max_inventory, self.inventory[key])))
        self._log("fill", {"fill_id": fill.fill_id, "underlying": key, "side": fill.side, "qty": fill.fill_qty, "inventory": self.inventory[key]})

    def update_greeks(self, underlying: str, greeks: Greeks) -> None:
        self.greeks[underlying] = greeks
        _assert_finite(asdict(greeks), f"greeks_{underlying}")

    def risk_state(self) -> Dict[str, Any]:
        total_delta = sum(g.delta for g in self.greeks.values())
        total_gamma = sum(g.gamma for g in self.greeks.values())
        total_vega = sum(g.vega for g in self.greeks.values())
        total_notional = sum(abs(v) * 100000.0 for v in self.inventory.values())
        rep = {
            "seed": self.seed,
            "inventory": {k: float(v) for k, v in self.inventory.items()},
            "greeks": {k: asdict(v) for k, v in self.greeks.items()},
            "total_delta": float(total_delta),
            "total_gamma": float(total_gamma),
            "total_vega": float(total_vega),
            "total_position_notional_usd": float(total_notional),
            "within_limits": bool(abs(total_delta) <= self.config.delta_limit and abs(total_gamma) <= self.config.gamma_limit and total_vega <= self.config.vega_limit and total_notional <= self.config.max_position_notional_usd),
            "paper_only": True,
            "quote_count": len(self.quotes),
            "fill_count": len(self.fills),
        }
        _assert_finite(rep, "risk_state")
        return rep

    def generate_report(self) -> Dict[str, Any]:
        rep = {
            "report": "PHASE27_MARKET_MAKER_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "config": asdict(self.config),
            "risk_state": self.risk_state(),
            "quotes": [asdict(q) for q in self.quotes],
            "fills": [asdict(f) for f in self.fills],
            "audit": self.audit,
            "paper_only": True,
        }
        _assert_finite(rep, "market_maker_report")
        return rep

    def save_report(self, report: Dict[str, Any], outdir: str = "research_state") -> str:
        Path(outdir).mkdir(parents=True, exist_ok=True)
        pjson = Path(outdir) / "PHASE27_MARKET_MAKER_REPORT.json"
        pmd = Path(outdir) / "PHASE27_MARKET_MAKER_REPORT.md"
        pjson.write_text(json.dumps(report, indent=2))
        pmd.write_text(
            f"# PHASE27_MARKET_MAKER_REPORT\n\nStatus: ok\nQuotes: {len(self.quotes)}\nFills: {len(self.fills)}\n"
            f"Inventory: {self.risk_state()['inventory']}\nPaper-only: True\n"
        )
        return str(pjson)


__all__ = ["OptionsMarketMaker", "MMConfig", "Quote", "Fill", "Greeks"]
