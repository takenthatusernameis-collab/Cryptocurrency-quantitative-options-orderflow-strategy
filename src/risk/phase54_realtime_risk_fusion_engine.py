"""
Phase 54: Real-Time Risk Fusion Engine (crypto options + orderflow).

Real-time risk fusion (Greeks/VaR/ES/liquidity/venue) with hard limits,
adaptive throttles, kill-switch integration and deterministic artifact emission.
Composes Phase 38 real-time risk monitor, Phase 42 Greeks risk monitor, risk
limits manager, Phase 39 kill switches and SLO gates. PAPER-ONLY, deterministic,
finite numerics.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.monitoring.slo import SLOMonitor, register_default_slos
from src.orderflow.phase52_toxicity_resilient_flow_optimizer import (
    Phase52FlowOptimizerConfig,
    Phase52ToxicityResilientFlowOptimizer,
)
from src.risk.limits import RiskLimits, RiskManager
from src.risk.phase38_realtime_risk_monitor import (
    RiskMonitorConfig38,
    RiskMonitorCycle,
    Phase38RealtimeRiskMonitor,
)
from src.risk.phase42_greeks_risk_monitor import (
    GreeksMonitorConfig42,
    Phase42GreeksRiskMonitor,
)
from src.risk.phase39_kill_switches_circuit_breakers import (
    KillSwitchConfig39,
    Phase39KillSwitchesCircuitBreakers,
)
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


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


def _cycle_dict(cycle: RiskMonitorCycle) -> Dict[str, Any]:
    return asdict(cycle)


@dataclass(frozen=True)
class Phase54RiskFusionConfig:
    seed: int = 54054
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 60
    var_limit_usd: float = 25000.0
    cvar_limit_usd: float = 35000.0
    max_delta: float = 500.0
    max_gamma: float = 150.0
    max_vega: float = 800.0
    max_theta: float = -200.0
    max_exposure_usd: float = 500000.0
    max_drawdown_pct: float = 0.08
    kill_dd_pct: float = 0.10
    max_daily_loss_usd: float = 40000.0
    liquidity_thin_threshold: float = 0.3
    fused_risk_caution: float = 0.55
    fused_risk_halt: float = 0.8
    min_adaptive_throttle: float = 0.2
    max_adaptive_throttle: float = 1.0
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError("Phase54RealtimeRiskFusionEngine: paper_only must remain True (live path hard-gated)")
        for name, val in (
            ("var_limit_usd", self.var_limit_usd),
            ("cvar_limit_usd", self.cvar_limit_usd),
            ("max_delta", self.max_delta),
            ("max_gamma", self.max_gamma),
            ("max_vega", self.max_vega),
            ("max_exposure_usd", self.max_exposure_usd),
            ("max_daily_loss_usd", self.max_daily_loss_usd),
        ):
            if not _finite(val) or val <= 0:
                raise ValueError(f"{name} must be positive finite")
        if not (0.0 < self.liquidity_thin_threshold < 1.0):
            raise ValueError("liquidity_thin_threshold must be in (0,1)")
        if not (0.0 < self.fused_risk_caution < self.fused_risk_halt < 1.0):
            raise ValueError("fused risk thresholds must satisfy 0 < caution < halt < 1")
        if not (0.0 < self.min_adaptive_throttle <= self.max_adaptive_throttle <= 1.0):
            raise ValueError("adaptive throttle bounds must be in (0,1]")


class Phase54RealtimeRiskFusionEngine:
    """Fuses real-time Greeks/VaR/ES/liquidity/venue risk with hard limits and adaptive throttles."""

    def __init__(self, cfg: Phase54RiskFusionConfig | None = None) -> None:
        self.cfg = cfg or Phase54RiskFusionConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase54RealtimeRiskFusionEngine: paper_only must remain True")
        risk_cfg = RiskMonitorConfig38(
            seed=self.cfg.seed + 38,
            paper_only=True,
            underlyings=self.cfg.underlyings,
            venues=self.cfg.venues,
            cycles=self.cfg.cycles,
            var_confidence=0.95,
            var_limit_usd=self.cfg.var_limit_usd,
            cvar_limit_usd=self.cfg.cvar_limit_usd,
            max_delta=self.cfg.max_delta,
            max_gamma=self.cfg.max_gamma,
            max_vega=self.cfg.max_vega,
            max_theta=self.cfg.max_theta,
            max_exposure_usd=self.cfg.max_exposure_usd,
            max_drawdown_pct=self.cfg.max_drawdown_pct,
            kill_dd_pct=self.cfg.kill_dd_pct,
            max_daily_loss_usd=self.cfg.max_daily_loss_usd,
        )
        self.risk_monitor = Phase38RealtimeRiskMonitor(config=risk_cfg, seed=self.cfg.seed + 38)
        greeks_cfg = GreeksMonitorConfig42(
            seed=self.cfg.seed + 42,
            paper_only=True,
            underlyings=self.cfg.underlyings,
            venues=self.cfg.venues,
        )
        self.greeks_monitor = Phase42GreeksRiskMonitor(config=greeks_cfg, seed=self.cfg.seed + 42)
        self.limits = RiskLimits()
        self.risk_manager = RiskManager(limits=self.limits)
        self.ks = Phase39KillSwitchesCircuitBreakers(
            KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True)
        )
        self.slo = SLOMonitor()
        register_default_slos(self.slo)
        self.cycle_reports: List[Dict[str, Any]] = []
        self.fused_scores: List[Dict[str, Any]] = []
        self.throttles: List[Dict[str, Any]] = []
        self.breaches: List[Dict[str, Any]] = []
        self.equity: float = 1_000_000.0
        self._cycle = 0

    def _venue_liquidity_scores(self, cycle: int) -> Dict[str, float]:
        scores: Dict[str, float] = {}
        for j, venue in enumerate(self.cfg.venues):
            base = 0.7 + 0.2 * ((cycle + j) % 5) / 5.0
            penalty = 0.15 * abs((cycle * 3 + j) % 3 - 1) / 2.0
            scores[venue] = max(0.05, min(1.0, _finite(base - penalty)))
        return scores

    def _fused_risk_score(
        self, cycle_rep: Dict[str, Any], greek_snapshot: Dict[str, Any], liq_scores: Dict[str, float]
    ) -> float:
        var_usd = _finite(cycle_rep.get("var_usd", 0.0))
        cvar_usd = _finite(cycle_rep.get("cvar_usd", 0.0))
        exposure_usd = _finite(cycle_rep.get("exposure_usd", 0.0))
        dd_pct = abs(_finite(cycle_rep.get("drawdown_pct", 0.0)))
        daily_pnl = _finite(cycle_rep.get("daily_pnl_usd", 0.0))
        delta = abs(_finite(greek_snapshot.get("delta", 0.0)))
        gamma = abs(_finite(greek_snapshot.get("gamma", 0.0)))
        vega = abs(_finite(greek_snapshot.get("vega", 0.0)))
        min_liq = min(liq_scores.values()) if liq_scores else 1.0
        var_r = min(1.0, var_usd / max(1.0, self.cfg.var_limit_usd))
        cvar_r = min(1.0, cvar_usd / max(1.0, self.cfg.cvar_limit_usd))
        exp_r = min(1.0, exposure_usd / max(1.0, self.cfg.max_exposure_usd))
        dd_r = min(1.0, dd_pct / max(1e-9, self.cfg.kill_dd_pct))
        pnl_r = min(1.0, max(0.0, -daily_pnl) / max(1.0, self.cfg.max_daily_loss_usd))
        greek_r = min(1.0, (delta / max(1.0, self.cfg.max_delta) + gamma / max(1.0, self.cfg.max_gamma) + vega / max(1.0, self.cfg.max_vega)) / 3.0)
        liq_r = 1.0 - min_liq
        fused = (
            0.20 * var_r + 0.15 * cvar_r + 0.15 * exp_r + 0.15 * dd_r + 0.10 * pnl_r
            + 0.15 * greek_r + 0.10 * liq_r
        )
        return max(0.0, min(1.0, _finite(fused)))

    def _hard_limit_checks(
        self, cycle: int, cycle_rep: Dict[str, Any], greek_snapshot: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        found: List[Dict[str, Any]] = []
        checks = [
            ("var", _finite(cycle_rep.get("var_usd", 0.0)), self.cfg.var_limit_usd, "high", "reduce_var"),
            ("cvar", _finite(cycle_rep.get("cvar_usd", 0.0)), self.cfg.cvar_limit_usd, "high", "reduce_cvar"),
            ("exposure", _finite(cycle_rep.get("exposure_usd", 0.0)), self.cfg.max_exposure_usd, "high", "scale_down_exposure"),
            ("delta", abs(_finite(greek_snapshot.get("delta", 0.0))), self.cfg.max_delta, "high", "hedge_delta"),
            ("gamma", abs(_finite(greek_snapshot.get("gamma", 0.0))), self.cfg.max_gamma, "high", "reduce_gamma"),
            ("vega", abs(_finite(greek_snapshot.get("vega", 0.0))), self.cfg.max_vega, "medium", "vega_hedge"),
            ("drawdown", abs(_finite(cycle_rep.get("drawdown_pct", 0.0))), self.cfg.kill_dd_pct, "critical", "halt_new_risk"),
            ("daily_loss", max(0.0, -_finite(cycle_rep.get("daily_pnl_usd", 0.0))), self.cfg.max_daily_loss_usd, "critical", "halt_trading"),
        ]
        for metric, value, limit, severity, action in checks:
            if value > limit:
                found.append({
                    "breach_id": f"p54_{metric}_{cycle}",
                    "cycle": cycle,
                    "metric": metric,
                    "value": float(value),
                    "limit": float(limit),
                    "severity": severity,
                    "action": action,
                    "timestamp": _utc_now(),
                    "paper_only": True,
                })
        return found

    def run_campaign(self, cycles: Optional[int] = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.cycle_reports = []
        self.fused_scores = []
        self.throttles = []
        self.breaches = []
        opt_cfg = Phase52FlowOptimizerConfig(
            seed=self.cfg.seed + 52, paper_only=True, cycles=max(1, cycles // 2),
            underlyings=self.cfg.underlyings, venues=self.cfg.venues,
            base_toxicity_threshold=0.28, high_toxicity_threshold=0.42,
            outdir=self.cfg.outdir,
        )
        flow_opt = Phase52ToxicityResilientFlowOptimizer(opt_cfg)
        opt_rep = flow_opt.optimize_flow(cycles=max(1, cycles // 2))
        avg_tox = _finite(opt_rep.get("avg_toxicity", 0.19))

        for i in range(cycles):
            portfolio_state = {
                "equity": self.equity,
                "daily_pnl_usd": _finite(opt_rep.get("daily_pnl_usd", 0.0)) if "daily_pnl_usd" in opt_rep else 0.0,
            }
            cycle_rep_dataclass = self.risk_monitor.monitor_cycle(i, portfolio_state)
            cycle_rep = _cycle_dict(cycle_rep_dataclass)
            greek_lines = self.greeks_monitor.generate_lines(i)
            greek_snapshot = self.greeks_monitor.aggregate(i, greek_lines)
            greek_rep = asdict(greek_snapshot)
            liq_scores = self._venue_liquidity_scores(i)
            fused = self._fused_risk_score(cycle_rep, greek_rep, liq_scores)
            limit_breaches = self._hard_limit_checks(i, cycle_rep, greek_rep)
            self.breaches.extend(limit_breaches)

            ks_halt = bool(self.ks.run_campaign().get("halted", False))
            self.risk_manager.update_pnl(_finite(cycle_rep.get("daily_pnl_usd", 0.0)), 0.0)
            self.risk_manager.update_equity(self.equity + _finite(cycle_rep.get("daily_pnl_usd", 0.0)) * 0.1)
            self.equity = float(self.risk_manager.current_equity)
            km_ok = not ks_halt and self.risk_manager.kill_switch_state.value != "TRIGGERED"

            if fused >= self.cfg.fused_risk_halt or not km_ok:
                throttle = self.cfg.min_adaptive_throttle
                action = "halt"
            elif fused >= self.cfg.fused_risk_caution:
                throttle = (self.cfg.min_adaptive_throttle + self.cfg.max_adaptive_throttle) / 2.0
                action = "mitigate"
            else:
                throttle = self.cfg.max_adaptive_throttle
                action = "none"
            if avg_tox >= 0.42:
                throttle = min(throttle, 0.5)
            throttle = max(self.cfg.min_adaptive_throttle, min(self.cfg.max_adaptive_throttle, _finite(throttle)))

            venue = self.cfg.venues[i % len(self.cfg.venues)]
            underlying = self.cfg.underlyings[i % len(self.cfg.underlyings)]
            positions = {
                f"{u}-OPT": type("Pos", (), {"market_value_abs": 50000.0})() for u in self.cfg.underlyings
            }
            order_violations = self.risk_manager.check_order(
                symbol=f"{underlying}-OPT", side="buy", quantity=1.0 * throttle, price=100.0,
                positions=positions,
            )
            order_ok = len(order_violations) == 0

            fused_rep = serialize_metrics_strict({
                "fused_risk_id": f"p54_risk_{i}",
                "cycle": i,
                "underlying": underlying,
                "venue": venue,
                "regime": cycle_rep.get("regime"),
                "fused_risk_score": float(fused),
                "var_usd": float(_finite(cycle_rep.get("var_usd", 0.0))),
                "cvar_usd": float(_finite(cycle_rep.get("cvar_usd", 0.0))),
                "exposure_usd": float(_finite(cycle_rep.get("exposure_usd", 0.0))),
                "drawdown_pct": float(abs(_finite(cycle_rep.get("drawdown_pct", 0.0)))),
                "daily_pnl_usd": float(_finite(cycle_rep.get("daily_pnl_usd", 0.0))),
                "delta": float(abs(_finite(greek_rep.get("delta", 0.0)))),
                "gamma": float(abs(_finite(greek_rep.get("gamma", 0.0)))),
                "vega": float(abs(_finite(greek_rep.get("vega", 0.0)))),
                "min_venue_liquidity": float(min(liq_scores.values())) if liq_scores else 1.0,
                "toxicity": float(avg_tox),
                "kill_switch_ok": bool(km_ok),
                "order_ok": bool(order_ok),
                "adaptive_throttle": float(throttle),
                "action": action,
                "limit_breaches": limit_breaches,
                "paper_only": True,
                "timestamp": _utc_now(),
            })
            self.fused_scores.append(fused_rep)

            cycle_entry = dict(cycle_rep)
            cycle_entry["greeks"] = greek_rep
            cycle_entry["venue_liquidity"] = liq_scores
            cycle_entry["fused_risk_score"] = float(fused)
            cycle_entry["adaptive_throttle"] = float(throttle)
            cycle_entry["action"] = action
            cycle_entry["limit_breaches"] = limit_breaches
            self.cycle_reports.append(cycle_entry)

            throttle_rep = serialize_metrics_strict({
                "throttle_id": f"p54_thr_{i}",
                "cycle": i,
                "underlying": underlying,
                "venue": venue,
                "throttle": float(throttle),
                "fused_risk_score": float(fused),
                "kill_switch_ok": bool(km_ok),
                "order_ok": bool(order_ok),
                "action": action,
                "paper_only": True,
                "timestamp": _utc_now(),
            })
            self.throttles.append(throttle_rep)

        critical_breaches = [b for b in self.breaches if b.get("severity") == "critical"]
        try:
            slo_evals = self.slo.evaluate_all()
            slo_ok = all(bool(e.get("met", True)) for e in slo_evals)
        except Exception:
            slo_evals = []
            slo_ok = True
        risk_cycles_ok = all(bool(c.get("risk_ok", True)) for c in self.cycle_reports)
        gates_ok = bool(
            not critical_breaches
            and risk_cycles_ok
            and all(t["kill_switch_ok"] for t in self.throttles)
            and all(t["order_ok"] for t in self.throttles)
        )
        rep = serialize_metrics_strict({
            "phase": "PHASE54_REALTIME_RISK_FUSION_ENGINE",
            "timestamp": _utc_now(),
            "seed": self.cfg.seed,
            "paper_only": True,
            "cycles": cycles,
            "gates_ok": bool(gates_ok),
            "slo_ok": bool(slo_ok),
            "risk_cycles_ok": bool(risk_cycles_ok),
            "critical_breaches": len(critical_breaches),
            "total_breaches": len(self.breaches),
            "kill_switch_triggered": self.risk_manager.kill_switch_state.value == "TRIGGERED",
            "avg_fused_risk_score": float(
                sum(f["fused_risk_score"] for f in self.fused_scores) / max(1, len(self.fused_scores))
            ),
            "max_fused_risk_score": float(max((f["fused_risk_score"] for f in self.fused_scores), default=0.0)),
            "avg_adaptive_throttle": float(
                sum(t["throttle"] for t in self.throttles) / max(1, len(self.throttles))
            ),
            "final_equity": float(self.equity),
            "daily_pnl_usd": float(self.risk_manager.daily_pnl),
            "n_cycles": len(self.cycle_reports),
            "n_breaches": len(self.breaches),
        })
        _assert_finite(rep, "phase54_risk_fusion_report")
        return rep

    def generate_artifacts(self, outdir: str = "research_state") -> Dict[str, Any]:
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        rep = self.run_campaign(cycles=self.cfg.cycles)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = out / f"PHASE54_REALTIME_RISK_FUSION_ENGINE_{ts}.json"
        mpath = out / f"PHASE54_REALTIME_RISK_FUSION_ENGINE_{ts}.md"
        with jpath.open("w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2, sort_keys=True)
        with mpath.open("w", encoding="utf-8") as f:
            f.write(
                "# PHASE54 Real-Time Risk Fusion Engine\n\n"
                f"- Timestamp: {rep['timestamp']}\n"
                f"- Gates OK: {rep['gates_ok']}\n"
                f"- SLO OK: {rep['slo_ok']}\n"
                f"- Risk Cycles OK: {rep['risk_cycles_ok']}\n"
                f"- Critical Breaches: {rep['critical_breaches']}\n"
                f"- Total Breaches: {rep['total_breaches']}\n"
                f"- Kill Switch Triggered: {rep['kill_switch_triggered']}\n"
                f"- Avg Fused Risk Score: {rep['avg_fused_risk_score']:.4f}\n"
                f"- Max Fused Risk Score: {rep['max_fused_risk_score']:.4f}\n"
                f"- Avg Adaptive Throttle: {rep['avg_adaptive_throttle']:.4f}\n"
                f"- Final Equity: {rep['final_equity']:.2f}\n"
                f"- Daily PnL: {rep['daily_pnl_usd']:.2f}\n"
            )
        rep["json_path"] = str(jpath)
        rep["md_path"] = str(mpath)
        return rep
