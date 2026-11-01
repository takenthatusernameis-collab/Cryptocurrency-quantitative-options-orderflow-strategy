"""Phase 18 Greeks Snapshot report helper (crypto options + orderflow)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from src.alpha.phase17_campaign import Phase17TradeIntent, _assert_no_nan_inf
from src.analytics.phase18_attribution import Phase18Attribution
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class Phase18GreeksSnapshot:
    def __init__(self, seed: int = 42, paper_only: bool = True) -> None:
        if not paper_only:
            raise ValueError("Phase18GreeksSnapshot: paper_only must remain True")
        self.seed = int(seed)
        self.paper_only = True
        self.timestamp = _utc_now()

    def generate_report(self, intents: List[Phase17TradeIntent]) -> Dict[str, Any]:
        attr = Phase18Attribution(seed=self.seed, paper_only=True)
        greeks = attr.compute_greeks_snapshot(intents)
        by_sym: Dict[str, Dict[str, float]] = {}
        for g in greeks:
            s = g.symbol
            if s not in by_sym:
                by_sym[s] = {"delta_net": 0.0, "gamma_net": 0.0, "vega_net": 0.0, "theta_net": 0.0, "notional_usd": 0.0, "count": 0}
            by_sym[s]["delta_net"] += g.delta * g.notional_usd
            by_sym[s]["gamma_net"] += g.gamma * g.notional_usd
            by_sym[s]["vega_net"] += g.vega * g.notional_usd
            by_sym[s]["theta_net"] += g.theta * g.notional_usd
            by_sym[s]["notional_usd"] += g.notional_usd
            by_sym[s]["count"] += 1
        report = {
            "report": "PHASE18_GREEKS_SNAPSHOT_REPORT",
            "campaign": "phase18_observability_attribution",
            "timestamp": self.timestamp,
            "seed": self.seed,
            "paper_only": True,
            "count": len(greeks),
            "greeks": [g.__dict__ for g in greeks],
            "portfolio_greeks_by_symbol": by_sym,
            "portfolio_totals": {
                "delta_net": float(sum(v["delta_net"] for v in by_sym.values())),
                "gamma_net": float(sum(v["gamma_net"] for v in by_sym.values())),
                "vega_net": float(sum(v["vega_net"] for v in by_sym.values())),
                "theta_net": float(sum(v["theta_net"] for v in by_sym.values())),
                "notional_usd": float(sum(v["notional_usd"] for v in by_sym.values())),
            },
        }
        _assert_no_nan_inf(report, "phase18_greeks_snapshot")
        return serialize_metrics_strict(report)


__all__ = ["Phase18GreeksSnapshot"]
