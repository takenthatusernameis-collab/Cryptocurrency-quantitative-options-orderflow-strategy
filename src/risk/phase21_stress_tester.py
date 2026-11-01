#!/usr/bin/env python3
import hashlib
import math
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _git_sha() -> str | None:
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


def _det_ts(seed: int, idx: int = 0) -> str:
    h = hashlib.sha256(f"{seed}|p21stress|{idx}".encode()).hexdigest()[:12]
    return f"2026-11-01T14:{h[:2]}:{h[2:4]}Z"


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
class StressConfig:
    seed: int = 42
    paper_only: bool = True
    spot_shocks: tuple = (-0.10, -0.05, 0.0, 0.05, 0.10)
    iv_shocks_pts: tuple = (-10.0, -5.0, 0.0, 5.0, 10.0)
    liquidity_shocks: tuple = (0.5, 0.8, 1.0, 1.2, 1.5)
    max_loss_breach: float = 500000.0
    enforce_hard_limits: bool = True


@dataclass(frozen=True)
class StressScenario:
    scenario_id: str
    spot_shock: float
    iv_shock_pts: float
    liquidity_shock: float
    description: str
    severity: str


@dataclass(frozen=True)
class StressResult:
    result_id: str
    scenario_id: str
    pnl_impact_usd: float
    delta_impact: float
    vega_impact: float
    gamma_impact: float
    liquidity_cost_bps: float
    breached: bool
    breach_reason: Optional[str]
    paper_only: bool
    timestamp: str


class Phase21StressTester:
    def __init__(self, config: Optional[StressConfig] = None, seed: int = 42):
        self.config = config or StressConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("Phase21StressTester: paper_only must remain True")
        self.config = StressConfig(
            seed=int(self.config.seed),
            paper_only=True,
            spot_shocks=tuple(self.config.spot_shocks),
            iv_shocks_pts=tuple(self.config.iv_shocks_pts),
            liquidity_shocks=tuple(self.config.liquidity_shocks),
            max_loss_breach=float(self.config.max_loss_breach),
            enforce_hard_limits=bool(self.config.enforce_hard_limits),
        )
        self.seed = int(self.config.seed)
        self._counter = 0
        self._rcount = 0
        self.audit: List[Dict[str, Any]] = []

    def _sid(self) -> str:
        self._counter += 1
        h = hashlib.sha256(f"{self.seed}|p21scen|{self._counter}".encode()).hexdigest()[:12]
        return f"p21_scn_{h}"

    def _rid(self) -> str:
        self._rcount += 1
        h = hashlib.sha256(f"{self.seed}|p21res|{self._rcount}".encode()).hexdigest()[:12]
        return f"p21_res_{h}"

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def build_scenarios(self) -> List[StressScenario]:
        self._log("build_scenarios", {})
        scenarios: List[StressScenario] = []
        idx = 0
        for ss in self.config.spot_shocks:
            for iv in self.config.iv_shocks_pts:
                for ls in self.config.liquidity_shocks:
                    idx += 1
                    sev = "extreme" if abs(ss) >= 0.10 or abs(iv) >= 10.0 or ls >= 1.5 else ("moderate" if abs(ss) >= 0.05 or abs(iv) >= 5.0 else "mild")
                    desc = f"spot{ss:+.2f}_iv{iv:+.1f}pt_liq{ls:.2f}"
                    scenarios.append(StressScenario(scenario_id=self._sid(), spot_shock=float(ss), iv_shock_pts=float(iv), liquidity_shock=float(ls), description=desc, severity=sev))
        _assert_no_nan_inf([asdict(s) for s in scenarios], "p21_scenarios")
        return scenarios

    def run_stress(
        self,
        scenarios: List[StressScenario],
        base_delta: float = 100.0,
        base_gamma: float = 10.0,
        base_vega: float = 5000.0,
        base_notional: float = 1000000.0,
    ) -> List[StressResult]:
        self._log("run_stress", {"n_scenarios": len(scenarios)})
        results: List[StressResult] = []
        for i, sc in enumerate(scenarios):
            delta_impact = base_delta * sc.spot_shock * 1000.0  # rough
            vega_impact = base_vega * (sc.iv_shock_pts / 100.0) * 10.0
            gamma_impact = base_gamma * (sc.spot_shock ** 2) * 10000.0
            liquidity_cost_bps = 5.0 * sc.liquidity_shock
            pnl_impact = -(abs(delta_impact) + abs(vega_impact) + gamma_impact + base_notional * liquidity_cost_bps / 10000.0)
            if not math.isfinite(pnl_impact):
                pnl_impact = -100000.0
            breached = pnl_impact < -self.config.max_loss_breach
            breach_reason = "max_loss_breach" if breached else None
            if self.config.enforce_hard_limits and breached and breach_reason is None:
                breach_reason = "max_loss_breach"
            results.append(
                StressResult(
                    result_id=self._rid(),
                    scenario_id=sc.scenario_id,
                    pnl_impact_usd=float(pnl_impact),
                    delta_impact=float(delta_impact),
                    vega_impact=float(vega_impact),
                    gamma_impact=float(gamma_impact),
                    liquidity_cost_bps=float(liquidity_cost_bps),
                    breached=bool(breached and self.config.enforce_hard_limits),
                    breach_reason=breach_reason if (breached and self.config.enforce_hard_limits) else None,
                    paper_only=True,
                    timestamp=_det_ts(self.seed, i),
                )
            )
        _assert_no_nan_inf([asdict(r) for r in results], "p21_stress_results")
        return results

    def generate_report(self, scenarios: List[StressScenario], results: List[StressResult]) -> Dict[str, Any]:
        breaches = [r for r in results if r.breached]
        worst = min((r.pnl_impact_usd for r in results), default=0.0)
        rep = {
            "report": "PHASE21_STRESS_TESTING_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "config": asdict(self.config),
            "scenario_count": len(scenarios),
            "result_count": len(results),
            "scenarios": [asdict(s) for s in scenarios],
            "results": [asdict(r) for r in results],
            "summary": {
                "breach_count": len(breaches),
                "worst_pnl_impact_usd": float(worst),
                "all_passed": len(breaches) == 0,
                "paper_only": True,
            },
            "audit": self.audit,
            "git_sha": _git_sha(),
            "paper_only": True,
        }
        _assert_no_nan_inf(rep, "p21_stress_report")
        return rep
