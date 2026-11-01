"""Phase 19 Execution Risk Engine for crypto options + orderflow.
Pre-trade checks, slippage guards, drawdown/kill-switch integration, enforcement.
Default PAPER-ONLY. No placeholders.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from src.telemetry.serialization import serialize_metrics_strict, assert_json_valid


_BASE_DAY = datetime(2026, 11, 1, tzinfo=timezone.utc)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _det_ts(seed: int) -> str:
    return (_BASE_DAY + timedelta(seconds=int(seed))).isoformat().replace("+00:00", "Z")


def _git_sha() -> Optional[str]:
    sha = os.environ.get("GIT_SHA")
    if sha:
        return str(sha)
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd="/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
        )
        if r.returncode == 0:
            return r.stdout.decode().strip()
    except Exception:
        pass
    return None


def _assert_no_nan_inf(obj: Any, label: str) -> None:
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


@dataclass(frozen=True)
class RiskCheck:
    name: str
    passed: bool
    reason: str
    limit: float
    value: float
    severity: str


class ExecutionRiskEngine:
    def __init__(
        self,
        paper_only: bool = True,
        seed: int = 42,
        max_notional_per_symbol: float = 100000.0,
        max_notional_per_venue: float = 150000.0,
        max_notional_total: float = 250000.0,
        max_delta: float = 500.0,
        max_vega: float = 10000.0,
        max_gamma: float = 200.0,
        max_theta: float = -50000.0,
        max_slippage_bps: float = 15.0,
        max_drawdown_pct: float = 0.10,
        kill_switch_on_breach: bool = True,
    ) -> None:
        if not paper_only:
            raise ValueError("ExecutionRiskEngine: paper_only must remain True")
        self.paper_only = True
        self.seed = int(seed)
        self.max_notional_per_symbol = float(max_notional_per_symbol)
        self.max_notional_per_venue = float(max_notional_per_venue)
        self.max_notional_total = float(max_notional_total)
        self.max_delta = float(max_delta)
        self.max_vega = float(max_vega)
        self.max_gamma = float(max_gamma)
        self.max_theta = float(max_theta)
        self.max_slippage_bps = float(max_slippage_bps)
        self.max_drawdown_pct = float(max_drawdown_pct)
        self.kill_switch_on_breach = bool(kill_switch_on_breach)
        self.kill_switch = False
        self.breaches: List[Dict[str, Any]] = []
        self.audit: List[Dict[str, Any]] = []
        self._log("init", {"paper_only": True})

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def pre_trade_check(
        self,
        intent: Dict[str, Any],
        state: Optional[Dict[str, Any]] = None,
        venue: str = "deribit",
    ) -> Dict[str, Any]:
        state = state or {}
        checks: List[RiskCheck] = []
        passed_all = True

        sym = str(intent.get("symbol", "BTC"))
        qty = float(intent.get("qty", 0.01))
        price = float(intent.get("limit_price", intent.get("price", 1000.0)))
        notional = qty * price * float(intent.get("contract_mult", 1.0))
        delta_est = float(intent.get("delta_est", 0.0))
        vega_est = float(intent.get("vega_est", 0.0))
        gamma_est = float(intent.get("gamma_est", 0.0))
        theta_est = float(intent.get("theta_est", 0.0))

        # per-symbol
        if notional > self.max_notional_per_symbol:
            checks.append(RiskCheck("per_symbol_notional", False, "exceeds per-symbol notional cap", self.max_notional_per_symbol, notional, "block"))
            passed_all = False
            self._breach("per_symbol_notional", sym, notional)
        else:
            checks.append(RiskCheck("per_symbol_notional", True, "ok", self.max_notional_per_symbol, notional, "info"))

        # per-venue
        venue_notional = float(state.get(f"notional_{venue}", notional))
        if venue_notional > self.max_notional_per_venue:
            checks.append(RiskCheck("per_venue_notional", False, "exceeds per-venue notional cap", self.max_notional_per_venue, venue_notional, "block"))
            passed_all = False
            self._breach("per_venue_notional", venue, venue_notional)
        else:
            checks.append(RiskCheck("per_venue_notional", True, "ok", self.max_notional_per_venue, venue_notional, "info"))

        # total
        total = float(state.get("total_notional", notional))
        if total > self.max_notional_total:
            checks.append(RiskCheck("total_notional", False, "exceeds total notional cap", self.max_notional_total, total, "block"))
            passed_all = False
            self._breach("total_notional", "ALL", total)
        else:
            checks.append(RiskCheck("total_notional", True, "ok", self.max_notional_total, total, "info"))

        # greeks
        if abs(delta_est) > self.max_delta:
            checks.append(RiskCheck("delta_cap", False, "delta exceeds cap", self.max_delta, delta_est, "block"))
            passed_all = False
            self._breach("delta_cap", sym, delta_est)
        else:
            checks.append(RiskCheck("delta_cap", True, "ok", self.max_delta, delta_est, "info"))
        if abs(vega_est) > self.max_vega:
            checks.append(RiskCheck("vega_cap", False, "vega exceeds cap", self.max_vega, vega_est, "block"))
            passed_all = False
            self._breach("vega_cap", sym, vega_est)
        else:
            checks.append(RiskCheck("vega_cap", True, "ok", self.max_vega, vega_est, "info"))
        if abs(gamma_est) > self.max_gamma:
            checks.append(RiskCheck("gamma_cap", False, "gamma exceeds cap", self.max_gamma, gamma_est, "block"))
            passed_all = False
            self._breach("gamma_cap", sym, gamma_est)
        else:
            checks.append(RiskCheck("gamma_cap", True, "ok", self.max_gamma, gamma_est, "info"))
        if theta_est < self.max_theta:  # theta more negative
            checks.append(RiskCheck("theta_cap", False, "theta exceeds (more negative) cap", self.max_theta, theta_est, "block"))
            passed_all = False
            self._breach("theta_cap", sym, theta_est)
        else:
            checks.append(RiskCheck("theta_cap", True, "ok", self.max_theta, theta_est, "info"))

        # drawdown
        dd = float(state.get("drawdown_pct", 0.0))
        if dd > self.max_drawdown_pct:
            checks.append(RiskCheck("drawdown_kill", False, "drawdown exceeds kill threshold", self.max_drawdown_pct, dd, "block"))
            passed_all = False
            if self.kill_switch_on_breach:
                self.kill_switch = True
            self._breach("drawdown_kill_switch", sym, dd)
        else:
            checks.append(RiskCheck("drawdown_kill", True, "ok", self.max_drawdown_pct, dd, "info"))

        # slippage guard (deterministic)
        slippage_bps_est = float(intent.get("slippage_bps_est", 2.0))
        if slippage_bps_est > self.max_slippage_bps:
            checks.append(RiskCheck("slippage_guard", False, "slippage estimate exceeds guard", self.max_slippage_bps, slippage_bps_est, "block"))
            passed_all = False
            self._breach("slippage_guard", sym, slippage_bps_est)
        else:
            checks.append(RiskCheck("slippage_guard", True, "ok", self.max_slippage_bps, slippage_bps_est, "info"))

        res = {
            "approved": bool(passed_all and not self.kill_switch),
            "checks": [asdict(c) for c in checks],
            "kill_switch": bool(self.kill_switch),
            "notional": float(notional),
            "symbol": sym,
            "venue": venue,
        }
        self._log("pre_trade_check", {"approved": res["approved"], "symbol": sym, "venue": venue})
        return res

    def _breach(self, btype: str, key: str, value: float) -> None:
        self.breaches.append({"timestamp": _utc_now(), "type": btype, "key": key, "value": float(value)})

    def post_trade_validate(self, fill: Dict[str, Any]) -> Dict[str, Any]:
        fq = float(fill.get("filled_qty", 0.0))
        fp = float(fill.get("fill_price", 0.0))
        exp = float(fill.get("expected_price", fp))
        slippage_bps = abs(fp - exp) / max(exp, 1e-12) * 10000.0
        ok = slippage_bps <= self.max_slippage_bps
        if not ok:
            self._breach("post_trade_slippage", fill.get("order_id", "unknown"), slippage_bps)
        res = {"ok": bool(ok), "slippage_bps": float(slippage_bps), "max_slippage_bps": self.max_slippage_bps}
        self._log("post_trade_validate", res)
        return res

    def trigger_kill_switch(self, reason: str = "manual") -> None:
        self.kill_switch = True
        self._breach("kill_switch_triggered", "MANUAL", 0.0)
        self._log("kill_switch_trigger", {"reason": reason})

    def generate_report(self) -> Dict[str, Any]:
        sha = _git_sha()
        report = {
            "report": "PHASE19_EXECUTION_RISK_REPORT",
            "campaign": "phase19_execution_hardening",
            "timestamp": _det_ts(self.seed),
            "seed": self.seed,
            "git_sha": sha,
            "paper_only": True,
            "hard_gated": True,
            "kill_switch": bool(self.kill_switch),
            "limits": {
                "max_notional_per_symbol": self.max_notional_per_symbol,
                "max_notional_per_venue": self.max_notional_per_venue,
                "max_notional_total": self.max_notional_total,
                "max_delta": self.max_delta,
                "max_vega": self.max_vega,
                "max_gamma": self.max_gamma,
                "max_theta": self.max_theta,
                "max_slippage_bps": self.max_slippage_bps,
                "max_drawdown_pct": self.max_drawdown_pct,
            },
            "breaches": list(self.breaches),
            "breach_count": len(self.breaches),
            "audit_count": len(self.audit),
            "audit_tail": self.audit[-15:],
        }
        _assert_no_nan_inf(report, "phase19_execution_risk")
        assert_json_valid(report)
        return serialize_metrics_strict(report)


__all__ = ["ExecutionRiskEngine", "RiskCheck"]
