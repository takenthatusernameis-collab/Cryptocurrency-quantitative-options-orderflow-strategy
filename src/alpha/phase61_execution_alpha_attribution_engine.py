"""
Phase 61: Execution Alpha Attribution Engine (crypto options + orderflow).

Execution alpha attribution: PnL/attribution decomposition by venue, strategy,
toxicity regime and orderflow signal; Sharpe/IR decomposition; deterministic.
PAPER-ONLY. Composes Phases 51, 57, 60.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite, sqrt
from pathlib import Path
from typing import Any, Dict, List

from src.alpha.phase57_cross_venue_options_execution_alpha_fusion import (
    Phase57CrossVenueOptionsExecutionAlphaFusion,
)
from src.execution.phase60_adaptive_execution_intelligence_engine import (
    Phase60AdaptiveExecutionIntelligenceEngine,
)
from src.orderflow.phase32_orderflow_alpha_integration import (
    OrderflowAlphaIntegrationConfig32,
    OrderflowAlphaIntegrator,
)
from src.orderflow.phase58_flow_toxicity_mitigator import Phase58FlowToxicityMitigator
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p61attr|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p61attr_{tag}_{h}"


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
class Phase61ExecutionAlphaAttributionConfig:
    seed: int = 61060
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 80
    risk_free_rate: float = 0.02
    hard_limit_notional_usd: float = 2_000_000.0
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError("Phase61ExecutionAlphaAttribution: paper_only must remain True (live path hard-gated)")
        if self.hard_limit_notional_usd <= 0:
            raise ValueError("hard_limit_notional_usd must be > 0")


class Phase61ExecutionAlphaAttributionEngine:
    """Execution alpha attribution: PnL/attribution decomposition by venue, strategy, toxicity regime and orderflow signal."""

    def __init__(self, cfg: Phase61ExecutionAlphaAttributionConfig | None = None) -> None:
        self.cfg = cfg or Phase61ExecutionAlphaAttributionConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase61ExecutionAlphaAttributionEngine: paper_only must remain True")
        self.exec60 = Phase60AdaptiveExecutionIntelligenceEngine()
        self.alpha57 = Phase57CrossVenueOptionsExecutionAlphaFusion()
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.tox58 = Phase58FlowToxicityMitigator()
        self.attribution: List[Dict[str, Any]] = []
        self.venue_pnl: List[Dict[str, Any]] = []
        self.strategy_pnl: List[Dict[str, Any]] = []
        self.regime_pnl: List[Dict[str, Any]] = []
        self.signal_pnl: List[Dict[str, Any]] = []
        self.sharpe_ir: List[Dict[str, Any]] = []
        self._cycle = 0

    def _sharpe(self, returns: List[float]) -> float:
        if not returns:
            return 0.0
        mean = sum(returns) / len(returns)
        var = sum((r - mean) ** 2 for r in returns) / len(returns)
        std = sqrt(var) if var > 0 else 0.0
        if std <= 0:
            return 0.0
        return (mean - self.cfg.risk_free_rate / 252.0) / std * sqrt(252.0)

    def _information_ratio(self, active_returns: List[float], benchmark_returns: List[float]) -> float:
        if not active_returns or not benchmark_returns:
            return 0.0
        n = min(len(active_returns), len(benchmark_returns))
        diffs = [active_returns[i] - benchmark_returns[i] for i in range(n)]
        mean_diff = sum(diffs) / n
        var_diff = sum((d - mean_diff) ** 2 for d in diffs) / n
        std_diff = sqrt(var_diff) if var_diff > 0 else 0.0
        if std_diff <= 0:
            return 0.0
        return mean_diff / std_diff * sqrt(252.0)

    def run_attribution(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.attribution = []
        self.venue_pnl = []
        self.strategy_pnl = []
        self.regime_pnl = []
        self.signal_pnl = []
        self.sharpe_ir = []

        exec_rep = self.exec60.run_intelligence(cycles=4)
        alpha_rep = self.alpha57.fuse()
        of_rep = self.of.run_campaign(cycles=3)
        tox_rep = self.tox58.mitigate(cycles=4)

        avg_tox = _finite(tox_rep.get("avg_vpin", 0.18))
        avg_quality = _finite(exec_rep.get("avg_execution_quality", 0.5))
        alpha_decayed = _finite(alpha_rep.get("alpha_decayed", 0.0))

        strategy_names = ("delta_vol_arb", "orderflow_skew", "cross_venue_rv", "toxicity_mm", "regime_hedge")
        regime_names = ("normal", "elevated", "high_toxicity", "vol_shock")
        signal_names = ("flow_imbalance", "trade_toxicity", "liquidation_pressure", "spread_widening")

        base_pnl_by_strategy: Dict[str, float] = {s: 10000.0 * (1.0 + 0.05 * i) for i, s in enumerate(strategy_names)}
        base_pnl_by_venue: Dict[str, float] = {v: 8000.0 * (1.0 + 0.03 * i) for i, v in enumerate(self.cfg.venues)}
        base_pnl_by_regime: Dict[str, float] = {r: 9000.0 * (1.0 + 0.04 * i) for i, r in enumerate(regime_names)}
        base_pnl_by_signal: Dict[str, float] = {s: 7000.0 * (1.0 + 0.06 * i) for i, s in enumerate(signal_names)}

        for i in range(cycles):
            venue = self.cfg.venues[i % len(self.cfg.venues)]
            underlying = self.cfg.underlyings[i % len(self.cfg.underlyings)]
            toxicity_i = max(0.0, min(1.0, avg_tox + (i % 13) * 0.018))
            vol_shock_i = min(0.06, 0.015 + avg_tox * 0.05 + (i % 7) * 0.003)
            regime = (
                "high_toxicity" if toxicity_i >= 0.38 or vol_shock_i >= 0.04
                else "elevated" if toxicity_i >= 0.24 or vol_shock_i >= 0.02
                else "normal"
            )
            latency_ms = 5.0 + (i % 8) * 3.0 + toxicity_i * 6.0
            slippage_bps = 0.2 + (i % 9) * 0.15 + toxicity_i * 0.5

            strategy_pnl_i: Dict[str, float] = {}
            for s in strategy_names:
                vol_mult = 1.0 + toxicity_i * 0.5
                pnl = base_pnl_by_strategy[s] * vol_mult * (0.95 + 0.1 * (i % 10) / 10.0)
                pnl -= slippage_bps * 50.0
                strategy_pnl_i[s] = float(_finite(pnl))

            venue_pnl_i = float(_finite(base_pnl_by_venue[venue] * (1.0 + toxicity_i * 0.3) - slippage_bps * 40.0))
            regime_pnl_i = float(_finite(base_pnl_by_regime[regime] * (1.0 - toxicity_i * 0.2)))
            signal_pnl_i: Dict[str, float] = {}
            for s in signal_names:
                pnl = base_pnl_by_signal[s] * (1.0 + toxicity_i * 0.4) * (0.9 + 0.2 * (i % 8) / 8.0)
                signal_pnl_i[s] = float(_finite(pnl))

            total_strategy_pnl = sum(strategy_pnl_i.values())
            total_signal_pnl = sum(signal_pnl_i.values())
            total_pnl = venue_pnl_i + regime_pnl_i + total_strategy_pnl

            self.attribution.append(serialize_metrics_strict({
                "attr_id": _make_id(self.cfg.seed, "attr", i),
                "cycle": i,
                "venue": venue,
                "underlying": underlying,
                "regime": regime,
                "toxicity": float(_finite(toxicity_i)),
                "vol_shock": float(_finite(vol_shock_i)),
                "latency_ms": float(_finite(latency_ms)),
                "slippage_bps": float(_finite(slippage_bps)),
                "total_pnl_usd": float(_finite(total_pnl)),
                "venue_pnl_usd": float(_finite(venue_pnl_i)),
                "regime_pnl_usd": float(_finite(regime_pnl_i)),
                "strategy_pnl_usd": float(_finite(total_strategy_pnl)),
                "signal_pnl_usd": float(_finite(total_signal_pnl)),
                "alpha_decayed": float(_finite(alpha_decayed)),
                "execution_quality": float(_finite(avg_quality)),
                "paper_only": True,
                "timestamp": _utc_now(),
            }))

            self.venue_pnl.append(serialize_metrics_strict({
                "vp_id": _make_id(self.cfg.seed, "vp", i),
                "cycle": i,
                "venue": venue,
                "underlying": underlying,
                "pnl_usd": float(_finite(venue_pnl_i)),
                "toxicity": float(_finite(toxicity_i)),
                "paper_only": True,
                "timestamp": _utc_now(),
            }))

            self.strategy_pnl.append(serialize_metrics_strict({
                "sp_id": _make_id(self.cfg.seed, "sp", i),
                "cycle": i,
                "strategy": strategy_names[i % len(strategy_names)],
                "pnl_usd": float(_finite(strategy_pnl_i[strategy_names[i % len(strategy_names)]])),
                "regime": regime,
                "paper_only": True,
                "timestamp": _utc_now(),
            }))

            self.regime_pnl.append(serialize_metrics_strict({
                "rp_id": _make_id(self.cfg.seed, "rp", i),
                "cycle": i,
                "regime": regime,
                "pnl_usd": float(_finite(regime_pnl_i)),
                "toxicity": float(_finite(toxicity_i)),
                "paper_only": True,
                "timestamp": _utc_now(),
            }))

            self.signal_pnl.append(serialize_metrics_strict({
                "sig_id": _make_id(self.cfg.seed, "sig", i),
                "cycle": i,
                "signal": signal_names[i % len(signal_names)],
                "pnl_usd": float(_finite(signal_pnl_i[signal_names[i % len(signal_names)]])),
                "toxicity": float(_finite(toxicity_i)),
                "paper_only": True,
                "timestamp": _utc_now(),
            }))

        returns = [a["total_pnl_usd"] / 100000.0 for a in self.attribution]
        bench_returns = [r * 0.6 for r in returns]
        sharpe = self._sharpe(returns)
        ir = self._information_ratio(returns, bench_returns)

        for i, s in enumerate(strategy_names):
            strat_returns = [sp["pnl_usd"] / 100000.0 for sp in self.strategy_pnl if sp["strategy"] == s]
            self.sharpe_ir.append(serialize_metrics_strict({
                "si_id": _make_id(self.cfg.seed, "si", i),
                "strategy": s,
                "sharpe": float(_finite(self._sharpe(strat_returns))),
                "information_ratio": float(_finite(self._information_ratio(strat_returns, bench_returns[:len(strat_returns)]))),
                "total_pnl_usd": float(_finite(sum(sp["pnl_usd"] for sp in self.strategy_pnl if sp["strategy"] == s))),
                "paper_only": True,
                "timestamp": _utc_now(),
            }))

        n_attr = len(self.attribution)
        gates_ok = bool(
            all(_finite(a["total_pnl_usd"]) for a in self.attribution)
            and sharpe >= -5.0
            and ir >= -5.0
        )
        rep = serialize_metrics_strict({
            "phase": "PHASE61_EXECUTION_ALPHA_ATTRIBUTION_ENGINE",
            "timestamp": _utc_now(),
            "seed": self.cfg.seed,
            "paper_only": True,
            "cycles": cycles,
            "gates_ok": bool(gates_ok),
            "avg_toxicity": float(_finite(avg_tox)),
            "avg_execution_quality": float(_finite(avg_quality)),
            "alpha_decayed": float(_finite(alpha_decayed)),
            "n_attribution": int(n_attr),
            "n_venue_pnl": len(self.venue_pnl),
            "n_strategy_pnl": len(self.strategy_pnl),
            "n_regime_pnl": len(self.regime_pnl),
            "n_signal_pnl": len(self.signal_pnl),
            "n_sharpe_ir": len(self.sharpe_ir),
            "sharpe": float(_finite(sharpe)),
            "information_ratio": float(_finite(ir)),
            "total_pnl_usd": float(_finite(sum(a["total_pnl_usd"] for a in self.attribution))),
            "venue_pnl_usd": float(_finite(sum(a["pnl_usd"] for a in self.venue_pnl))),
            "strategy_pnl_usd": float(_finite(sum(a["pnl_usd"] for a in self.strategy_pnl))),
            "regime_pnl_usd": float(_finite(sum(a["pnl_usd"] for a in self.regime_pnl))),
            "signal_pnl_usd": float(_finite(sum(a["pnl_usd"] for a in self.signal_pnl))),
            "exec60_ok": bool(exec_rep.get("gates_ok", False)),
            "alpha57_ok": bool(alpha_rep.get("deterministic", False)),
            "tox58_ok": bool(tox_rep.get("gates_ok", False)),
            "composed_phases": "17-60",
        })
        _assert_finite(rep, "phase61_exec_alpha_attribution_report")
        return rep

    def generate_artifacts(self, outdir: str = "research_state") -> Dict[str, Any]:
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        rep = self.run_attribution(cycles=self.cfg.cycles)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = out / f"PHASE61_EXECUTION_ALPHA_ATTRIBUTION_{ts}.json"
        mpath = out / f"PHASE61_EXECUTION_ALPHA_ATTRIBUTION_{ts}.md"
        with jpath.open("w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2, sort_keys=True)
        with mpath.open("w", encoding="utf-8") as f:
            f.write(
                f"# PHASE61 Execution Alpha Attribution Engine\n\n"
                f"- Timestamp: {rep['timestamp']}\n"
                f"- Gates OK: {rep['gates_ok']}\n"
                f"- Paper Only: {rep['paper_only']}\n"
                f"- Cycles: {rep['cycles']}\n"
                f"- Sharpe: {rep['sharpe']:.4f} | Information Ratio: {rep['information_ratio']:.4f}\n"
                f"- Total PnL USD: {rep['total_pnl_usd']:.2f}\n"
                f"- Venue PnL: {rep['venue_pnl_usd']:.2f} | Strategy PnL: {rep['strategy_pnl_usd']:.2f}\n"
                f"- Regime PnL: {rep['regime_pnl_usd']:.2f} | Signal PnL: {rep['signal_pnl_usd']:.2f}\n"
                f"- Attribution: {rep['n_attribution']} | Venue PnL: {rep['n_venue_pnl']}\n"
                f"- Strategy PnL: {rep['n_strategy_pnl']} | Regime PnL: {rep['n_regime_pnl']}\n"
                f"- Signal PnL: {rep['n_signal_pnl']} | Sharpe/IR: {rep['n_sharpe_ir']}\n"
                f"- Avg Toxicity: {rep['avg_toxicity']:.4f} | Avg Exec Quality: {rep['avg_execution_quality']:.4f}\n"
                f"- Composed: {rep['composed_phases']}\n"
            )
        rep["json_path"] = str(jpath)
        rep["md_path"] = str(mpath)
        return rep
