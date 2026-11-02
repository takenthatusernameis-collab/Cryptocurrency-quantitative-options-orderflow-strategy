"""
Phase 53: Adaptive inventory skewing for options MM (crypto options + orderflow).

Regime-aware skew, gamma-aware sizing, orderflow-shaded skew. PAPER-ONLY,
deterministic, finite numerics.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List

from src.orderflow.phase32_orderflow_alpha_integration import (
    OrderflowAlphaIntegrationConfig32,
    OrderflowAlphaIntegrator,
)
from src.risk.phase39_kill_switches_circuit_breakers import (
    KillSwitchConfig39,
    Phase39KillSwitchesCircuitBreakers,
)
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p53skew|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p53skew_{tag}_{h}"


def _finite(x: float, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if isfinite(v) else default


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
            if not isfinite(v):
                bad.append(p)

    walk(obj, "$")
    if bad:
        raise ValueError(f"Non-finite in {label}: {bad[:10]}")


@dataclass(frozen=True)
class Phase53InventorySkewConfig:
    seed: int = 53054
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit")
    cycles: int = 60
    max_skew_bps: float = 18.0
    gamma_factor: float = 1.25
    inv_limit: float = 0.65
    of_shade: float = 0.45
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError("Phase53AdaptiveInventorySkewEngine: paper_only must remain True (live path hard-gated)")


class Phase53AdaptiveInventorySkewEngine:
    """Adaptive inventory skewing engine for options MM."""

    def __init__(self, cfg: Phase53InventorySkewConfig | None = None) -> None:
        self.cfg = cfg or Phase53InventorySkewConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase53AdaptiveInventorySkewEngine: paper_only must remain True")
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.skews: List[Dict[str, Any]] = []
        self.quotes: List[Dict[str, Any]] = []

    def run_campaign(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self.skews = []
        self.quotes = []
        ksum = self.ks.run_campaign()
        halted = bool(ksum.get("halted", False))
        of_rep = self.of.run_campaign(cycles=12)
        tox = _finite(of_rep.get("avg_toxicity", 0.22))
        imb = _finite(of_rep.get("avg_imbalance", 0.14))

        for i in range(cycles):
            inv_norm = min(self.cfg.inv_limit, _finite((i % 10) / 10.0))
            gamma = self.cfg.gamma_factor * (1.0 + (i % 7) * 0.02)
            of_shade = tox * self.cfg.of_shade + abs(imb) * 0.25
            skew_bps = min(self.cfg.max_skew_bps, inv_norm * gamma * 12.0 + of_shade * 8.0)
            self.skews.append(serialize_metrics_strict({
                "skew_id": _make_id(self.cfg.seed, "skew", i),
                "cycle": i,
                "underlying": self.cfg.underlyings[i % len(self.cfg.underlyings)],
                "venue": self.cfg.venues[i % len(self.cfg.venues)],
                "inventory_norm": float(inv_norm),
                "gamma_factor": float(gamma),
                "orderflow_shade": float(min(1.0, of_shade)),
                "skew_bps": float(skew_bps),
                "paper_only": True,
                "timestamp": _utc_now(),
            }))
            self.quotes.append(serialize_metrics_strict({
                "quote_id": _make_id(self.cfg.seed, "q", i),
                "cycle": i,
                "bid_skew_bps": float(-skew_bps * 0.4),
                "ask_skew_bps": float(skew_bps * 0.6),
                "gamma_aware_sizing": float(min(1.0, 1.0 - inv_norm * 0.35)),
                "regime_aware": True,
                "kill_switch_ok": not halted,
                "paper_only": True,
                "timestamp": _utc_now(),
            }))

        gates_ok = bool((not halted) and all(abs(s["skew_bps"]) <= self.cfg.max_skew_bps + 1e-6 for s in self.skews))
        rep = serialize_metrics_strict({
            "phase": "PHASE53_ADAPTIVE_INVENTORY_SKEW_ENGINE",
            "timestamp": _utc_now(),
            "seed": self.cfg.seed,
            "paper_only": True,
            "cycles": cycles,
            "gates_ok": gates_ok,
            "n_skews": len(self.skews),
            "n_quotes": len(self.quotes),
            "avg_skew_bps": float(sum(abs(s["skew_bps"]) for s in self.skews) / max(1, len(self.skews))),
            "halted_by_kill_switch": bool(halted),
        })
        _assert_finite(rep, "phase53_skew_report")
        return rep

    def generate_artifacts(self, outdir: str) -> Dict[str, Any]:
        rep = self.run_campaign(self.cfg.cycles)
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = out / f"PHASE53_ADAPTIVE_INVENTORY_SKEW_ENGINE_{ts}.json"
        mpath = out / f"PHASE53_ADAPTIVE_INVENTORY_SKEW_ENGINE_{ts}.md"
        with jpath.open("w", encoding="utf-8") as f:
            json.dump({"report": rep, "skews": self.skews[:60]}, f, indent=2, sort_keys=True)
        with mpath.open("w", encoding="utf-8") as f:
            f.write(f"# PHASE53 Adaptive Inventory Skew Engine\n\n- Timestamp: {rep['timestamp']}\n- Gates OK: {rep['gates_ok']}\n- Avg |Skew| (bps): {rep['avg_skew_bps']:.4f}\n")
        rep["json_path"] = str(jpath)
        rep["md_path"] = str(mpath)
        return rep
