"""Phase 15 Campaign Orchestrator: cross-exchange arbitrage, delta-neutral
market making & latency-optimized execution (crypto options + orderflow).

Default PAPER-ONLY. Live capital hard-gated. Deterministic seed-42 run over
symbols BTC/ETH and venues Deribit/OKX/Binance. Emits auditable JSON/MD
artifacts under research_state and fails fast on NaN/Inf.
"""

from __future__ import annotations

import json
import math
import os
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.arbitrage import ArbitrageConfig, ArbitrageDetector, ArbitrageQuote
from src.marketmaking import DeltaNeutralMM, MMConfig, black_scholes_greeks
from src.execution.latency_aware_router import LatencyAwareRouter, LatencyRouterConfig
from src.orchestration import CrossVenueOrchestrator, CrossVenueConfig
from src.telemetry.serialization import serialize_metrics_strict, assert_json_valid

_BASE_TS = datetime(2026, 11, 1, tzinfo=timezone.utc)


def _utc_iso(ts: datetime) -> str:
    return ts.isoformat().replace("+00:00", "Z")


def _det_ts(seed: int) -> str:
    return _utc_iso(_BASE_TS + timedelta(seconds=int(seed)))


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


def _write_json_artifact(path: Path, data: Dict[str, Any]) -> str:
    serialized = serialize_metrics_strict(data)
    content = json.dumps(serialized, ensure_ascii=False, indent=2, allow_nan=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return str(path)


def _assert_no_nan_inf(obj: Any, label: str) -> None:
    """Fail fast on NaN/Inf anywhere in a payload."""
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
        raise ValueError(f"Non-finite values detected in {label}: {bad[:10]}")


def _synthetic_quotes(seed: int, symbols: Tuple[str, ...], venues: Tuple[str, ...]) -> List[ArbitrageQuote]:
    rng = random.Random(seed * 7 + 1)
    base = {"BTC": 65000.0, "ETH": 66000.0}
    quotes: List[ArbitrageQuote] = []
    for symbol in symbols:
        spot = base.get(symbol, 65000.0)
        for venue in venues:
            spread_bps = rng.random() * 4.0 + 0.5
            mid = spot * (1.0 + (rng.random() - 0.5) * 0.001)
            half = spread_bps / 2.0 / 10000.0 * mid
            size = rng.random() * 4.0 + 0.5
            quotes.append(
                ArbitrageQuote(
                    venue=venue,
                    symbol=symbol,
                    bid=round(mid - half, 4),
                    ask=round(mid + half, 4),
                    bid_size=round(size, 4),
                    ask_size=round(size, 4),
                    timestamp=_det_ts(seed),
                    received_at=_det_ts(seed),
                    source="synthetic_orderflow",
                )
            )
    return quotes


class Phase15Campaign:
    """Phase 15 cross-venue campaign: arbitrage + delta-neutral MM + routing."""

    def __init__(
        self,
        symbols: Tuple[str, ...] = ("BTC", "ETH"),
        seed: int = 42,
        venues: Tuple[str, ...] = ("deribit", "okx", "binance"),
        paper_only: bool = True,
        outdir: Optional[Path] = None,
        cycles: int = 5,
    ) -> None:
        if not paper_only:
            raise ValueError("Phase15Campaign: paper_only must remain True (live path hard-gated)")
        self.symbols = tuple(str(s).upper() for s in symbols)
        self.seed = int(seed)
        self.venues = tuple(str(v).lower() for v in venues)
        self.paper_only = True  # enforce
        self.outdir = outdir or Path("research_state")
        self.outdir.mkdir(parents=True, exist_ok=True)
        self.cycles = int(cycles)
        self.campaign_id = f"phase15_{self.seed}"
        self.timestamp = _det_ts(self.seed)
        self.artifacts: List[str] = []
        self.results: Dict[str, Any] = {}

    # -- components ---------------------------------------------------------
    def _run_arbitrage(self, spots: Dict[str, float], ivs: Dict[str, float]) -> Dict[str, Any]:
        config = ArbitrageConfig(venues=self.venues, symbols=self.symbols, seed=self.seed)
        detector = ArbitrageDetector(config=config, seed=self.seed)
        quotes = _synthetic_quotes(self.seed, self.symbols, self.venues)
        accepted = detector.submit_quotes(quotes)
        opportunities = detector.detect(spots, ivs)
        report = detector.generate_report(opportunities)
        _assert_no_nan_inf(report, "arbitrage_report")
        assert_json_valid(report)
        path = _write_json_artifact(self.outdir / "ARBITRAGE_REPORT.json", report)
        self.artifacts.append(path)
        return {"report": report, "artifact": path, "counts": report["counts"], "quotes_accepted": accepted}

    def _run_market_making(self, spots: Dict[str, float], ivs: Dict[str, float]) -> Dict[str, Any]:
        config = MMConfig(symbols=self.symbols, venues=self.venues, seed=self.seed)
        mm = DeltaNeutralMM(config=config, seed=self.seed)

        # Deterministic seed positions: one option + one perp per symbol.
        for i, symbol in enumerate(self.symbols):
            strike = spots[symbol] * (1.05 if i % 2 == 0 else 0.95)
            option_type = "call" if i % 2 == 0 else "put"
            side = "long" if i % 2 == 0 else "short"
            greeks = black_scholes_greeks(spots[symbol], strike, 0.05, ivs.get(symbol, 0.6), option_type)
            mm.open_position(
                symbol=symbol,
                venue=self.venues[i % len(self.venues)],
                instrument=f"{symbol}-{int(strike)}-{option_type.upper()[0]}",
                kind="option",
                side=side,
                quantity=0.5 + i,
                strike=strike,
                expiry="2026-12-31",
                option_type=option_type,
                entry_price=greeks["price"],
                mark_price=greeks["price"],
                spot=spots[symbol],
                implied_vol=ivs.get(symbol, 0.6),
            )
            mm.open_position(
                symbol=symbol,
                venue=self.venues[(i + 1) % len(self.venues)],
                instrument=f"{symbol}-PERP",
                kind="perp",
                side="short" if side == "long" else "long",
                quantity=0.25,
                strike=0.0,
                expiry="perpetual",
                option_type=None,
                entry_price=spots[symbol],
                mark_price=spots[symbol],
                spot=spots[symbol],
                implied_vol=0.0,
            )

        mm.update_marks(spots, ivs)
        risk = mm.risk_check()
        if not risk["within_limits"]:
            mm.trigger_kill_switch(f"preflight risk breach: {','.join(risk['breaches'])}", source="campaign")
        report = mm.generate_report()
        _assert_no_nan_inf(report, "market_making_report")
        assert_json_valid(report)
        path = _write_json_artifact(self.outdir / "DELTA_NEUTRAL_MM_REPORT.json", report)
        self.artifacts.append(path)
        return {"report": report, "artifact": path, "counts": report["counts"], "risk": risk}

    def _run_latency_routing(self, spots: Dict[str, float]) -> Dict[str, Any]:
        config = LatencyRouterConfig(venues=self.venues, symbols=self.symbols, seed=self.seed)
        router = LatencyAwareRouter(config=config, seed=self.seed)
        rng = random.Random(self.seed * 13 + 5)

        # Seed quotes and latency samples per venue/symbol.
        for symbol in self.symbols:
            spot = spots[symbol]
            for venue in self.venues:
                spread_bps = rng.random() * 3.0 + 0.5
                half = spread_bps / 2.0 / 10000.0 * spot
                router.update_quote(
                    venue,
                    symbol,
                    round(spot - half, 4),
                    round(spot + half, 4),
                    round(rng.random() * 3.0 + 0.5, 4),
                    round(rng.random() * 3.0 + 0.5, 4),
                    _det_ts(self.seed),
                )
                router.record_latency(venue, round(rng.random() * 45.0 + 5.0, 2), symbol)

        # Route deterministic hedge intents.
        intents = [
            {"symbol": "BTC", "side": "sell", "quantity": 0.1, "price": spots.get("BTC", 65000.0)},
            {"symbol": "ETH", "side": "buy", "quantity": 1.0, "price": spots.get("ETH", 66000.0)},
            {"symbol": "BTC", "side": "buy", "quantity": 0.05, "price": spots.get("BTC", 65000.0)},
        ]
        routes = []
        for intent in intents:
            route = router.route_intent(intent, spot=spots)
            router.track_fill(
                route.order_id,
                route.price,
                quantity=route.quantity,
                commission=route.total_cost_bps / 10000.0 * route.quantity * route.price,
                symbol=intent["symbol"],
            )
            routes.append(route.to_dict())

        # One cancel/replace exercised deterministically.
        replacement_id: Optional[str] = None
        if routes:
            replacement_id = router.replace(routes[0]["order_id"], price=routes[0]["price"] * 0.999)

        report = router.generate_report()
        _assert_no_nan_inf(report, "latency_routing_report")
        assert_json_valid(report)
        path = _write_json_artifact(self.outdir / "LATENCY_ROUTING_REPORT.json", report)
        self.artifacts.append(path)
        return {
            "report": report,
            "artifact": path,
            "counts": report["counts"],
            "routes": routes,
            "replacement_id": replacement_id,
            "latency": report["latency"],
        }

    def _run_orchestrator(self, spots: Dict[str, float], ivs: Dict[str, float]) -> Dict[str, Any]:
        config = CrossVenueConfig(
            symbols=self.symbols,
            venues=self.venues,
            seed=self.seed,
            cycles=self.cycles,
        )
        orchestrator = CrossVenueOrchestrator(config=config, seed=self.seed, paper_only=True, outdir=str(self.outdir))
        quotes = [
            {
                "venue": q.venue,
                "symbol": q.symbol,
                "bid": q.bid,
                "ask": q.ask,
                "bid_size": q.bid_size,
                "ask_size": q.ask_size,
                "timestamp": q.timestamp,
                "received_at": q.received_at,
                "source": q.source,
            }
            for q in _synthetic_quotes(self.seed, self.symbols, self.venues)
        ]
        orchestrator.submit_market_snapshot(quotes, spots, ivs)
        cycles: List[Dict[str, Any]] = []
        for cycle in range(1, self.cycles + 1):
            result = orchestrator.run_cycle(cycle)
            cycles.append(result)
            if result.get("status") == "halted":
                break
        report = orchestrator.generate_report()
        _assert_no_nan_inf(report, "orchestration_report")
        assert_json_valid(report)
        path = _write_json_artifact(self.outdir / "CROSSVENUE_ORCHESTRATION_REPORT.json", report)
        self.artifacts.append(path)
        state_path = orchestrator.save_state(self.outdir / "CROSSVENUE_ORCHESTRATION_STATE.json")
        self.artifacts.append(state_path)
        return {"report": report, "artifact": path, "state": state_path, "counts": report["counts"], "cycles": cycles}

    def _write_md(self, name: str, lines: List[str]) -> str:
        path = self.outdir / name
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.artifacts.append(str(path))
        return str(path)

    def run(self) -> Dict[str, Any]:
        """Execute the full Phase 15 campaign deterministically."""
        results: Dict[str, Any] = {}
        git_sha = _git_sha()
        spots = {s: 65000.0 + (1000.0 if s == "ETH" else 0.0) for s in self.symbols}
        ivs = {"BTC": 0.60, "ETH": 0.70}

        arb = self._run_arbitrage(spots, ivs)
        results["arbitrage"] = arb["report"]
        results["arbitrage_artifact"] = arb["artifact"]

        mm = self._run_market_making(spots, ivs)
        results["market_making"] = mm["report"]
        results["market_making_artifact"] = mm["artifact"]

        rtr = self._run_latency_routing(spots)
        results["latency_routing"] = rtr["report"]
        results["latency_routing_artifact"] = rtr["artifact"]

        orch = self._run_orchestrator(spots, ivs)
        results["orchestration"] = orch["report"]
        results["orchestration_artifact"] = orch["artifact"]
        results["orchestration_state"] = orch["state"]

        master: Dict[str, Any] = {
            "report": "PHASE15_CROSSVENUE_REPORT",
            "campaign": "phase15_crossvenue",
            "campaign_id": self.campaign_id,
            "timestamp": self.timestamp,
            "seed": self.seed,
            "symbols": list(self.symbols),
            "venues": list(self.venues),
            "paper_only": True,
            "status": "completed",
            "git_sha": git_sha,
            "cycles": self.cycles,
            "counts": {
                "arb_opportunities": arb["counts"]["opportunities_detected"],
                "arb_qualified": arb["counts"]["qualified"],
                "mm_positions": mm["counts"]["positions"],
                "router_routes": rtr["counts"]["routes"],
                "router_fills": rtr["counts"]["fills"],
                "orchestrator_cycles": orch["counts"]["cycles"],
                "artifacts": len(self.artifacts),
            },
            "artifacts": [os.path.basename(a) for a in self.artifacts],
            "git_sha": git_sha,
            "components": {
                "arbitrage": arb["report"],
                "market_making": mm["report"],
                "latency_routing": rtr["report"],
                "orchestration": orch["report"],
            },
        }
        master = serialize_metrics_strict(master)
        _assert_no_nan_inf(master, "phase15_master_report")
        assert_json_valid(master)
        master_path = _write_json_artifact(self.outdir / "PHASE15_CROSSVENUE_REPORT.json", master)
        self.artifacts.append(master_path)

        md_lines = [
            "# PHASE15_CROSSVENUE_REPORT",
            f"Timestamp (UTC): {self.timestamp}",
            f"Campaign ID: {self.campaign_id}",
            f"Seed: {self.seed}",
            f"Symbols: {', '.join(self.symbols)}",
            f"Venues: {', '.join(self.venues)}",
            f"Paper-only: {self.paper_only}",
            f"Git SHA: {git_sha}",
            f"Cycles: {self.cycles}",
            f"Status: completed",
            "",
            "## Counts",
        ]
        for key, value in master["counts"].items():
            md_lines.append(f"- {key}: {value}")
        md_lines.append("")
        md_lines.append("## Artifacts")
        for artifact in self.artifacts:
            md_lines.append(f"- {os.path.basename(artifact)}")
        md_path = self.outdir / "PHASE15_CROSSVENUE_REPORT.md"
        md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
        self.artifacts.append(str(md_path))

        # Component MD summaries.
        self._write_md(
            "ARBITRAGE_REPORT.md",
            [
                "# ARBITRAGE_REPORT",
                f"Timestamp (UTC): {self.timestamp}",
                f"Seed: {self.seed}",
                f"Symbols: {', '.join(self.symbols)}",
                f"Venues: {', '.join(self.venues)}",
                f"Paper-only: True",
                f"Quotes accepted: {arb['quotes_accepted']}",
                f"Opportunities detected: {arb['counts']['opportunities_detected']}",
                f"Qualified: {arb['counts']['qualified']}",
                f"Rejections: {arb['counts']['rejections']}",
                f"Artifact: ARBITRAGE_REPORT.json",
                "",
            ],
        )
        self._write_md(
            "DELTA_NEUTRAL_MM_REPORT.md",
            [
                "# DELTA_NEUTRAL_MM_REPORT",
                f"Timestamp (UTC): {self.timestamp}",
                f"Seed: {self.seed}",
                f"Symbols: {', '.join(self.symbols)}",
                f"Paper-only: True",
                f"Positions: {mm['counts']['positions']}",
                f"Trades: {mm['counts']['trades']}",
                f"Net PnL USD: {mm['report']['pnl']['net_pnl_usd']}",
                f"Drawdown pct: {mm['report']['pnl']['drawdown_pct']}",
                f"Risk within limits: {mm['risk']['within_limits']}",
                f"Artifact: DELTA_NEUTRAL_MM_REPORT.json",
                "",
            ],
        )
        self._write_md(
            "LATENCY_ROUTING_REPORT.md",
            [
                "# LATENCY_ROUTING_REPORT",
                f"Timestamp (UTC): {self.timestamp}",
                f"Seed: {self.seed}",
                f"Symbols: {', '.join(self.symbols)}",
                f"Venues: {', '.join(self.venues)}",
                f"Paper-only: True",
                f"Routes: {rtr['counts']['routes']}",
                f"Fills: {rtr['counts']['fills']}",
                f"Cancels: {rtr['counts']['cancels']}",
                f"Replacements: {rtr['counts']['replacements']}",
                f"Avg cost bps: {rtr['report']['routing']['avg_cost_bps']}",
                f"Avg latency ms: {rtr['report']['routing']['avg_latency_ms']}",
                f"Avg slippage bps: {rtr['report']['slippage']['avg_slippage_bps']}",
                f"Artifact: LATENCY_ROUTING_REPORT.json",
                "",
            ],
        )
        self._write_md(
            "CROSSVENUE_ORCHESTRATION_REPORT.md",
            [
                "# CROSSVENUE_ORCHESTRATION_REPORT",
                f"Timestamp (UTC): {self.timestamp}",
                f"Campaign ID: {self.campaign_id}",
                f"Seed: {self.seed}",
                f"Symbols: {', '.join(self.symbols)}",
                f"Venues: {', '.join(self.venues)}",
                f"Paper-only: True",
                f"Cycles: {orch['counts']['cycles']}",
                f"Cycles completed: {orch['counts']['cycles_completed']}",
                f"Cycles halted: {orch['counts']['cycles_halted']}",
                f"Kill switch triggered: {orch['report']['kill_switch']['triggered']}",
                f"Net PnL USD: {orch['report']['pnl']['net_pnl_usd']}",
                f"Drawdown pct: {orch['report']['pnl']['drawdown_pct']}",
                f"Arb fills: {orch['counts']['arb_fills']}",
                f"Hedges: {orch['counts']['hedges']}",
                f"Artifact: CROSSVENUE_ORCHESTRATION_REPORT.json",
                f"State: CROSSVENUE_ORCHESTRATION_STATE.json",
                "",
            ],
        )

        results["master_report"] = master
        results["master_report_artifact"] = master_path
        results["md_artifact"] = str(md_path)
        results["artifacts"] = [str(a) for a in self.artifacts]
        results["status"] = "completed"
        return results


__all__ = ["Phase15Campaign", "_write_json_artifact", "_assert_no_nan_inf"]
