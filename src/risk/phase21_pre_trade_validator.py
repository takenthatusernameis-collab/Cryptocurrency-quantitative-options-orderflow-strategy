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
    h = hashlib.sha256(f"{seed}|p21val|{idx}".encode()).hexdigest()[:12]
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
class PreTradeConfig:
    seed: int = 42
    paper_only: bool = True
    max_order_notional: float = 500000.0
    max_delta_add: float = 500.0
    max_vega_add: float = 10000.0
    require_orderflow_confirm: bool = True
    enforce_hard_blocks: bool = True


@dataclass(frozen=True)
class TradeIntent:
    intent_id: str
    symbol: str
    venue: str
    strategy: str
    side: str
    qty: float
    notional_usd: float
    delta_est: float
    vega_est: float
    gamma_est: float
    orderflow_confirmed: bool
    paper_only: bool


@dataclass(frozen=True)
class PreTradeDecision:
    decision_id: str
    intent_id: str
    approved: bool
    blocked: bool
    block_reasons: List[str]
    warnings: List[str]
    override_audit_id: Optional[str]
    paper_only: bool
    timestamp: str


class Phase21PreTradeValidator:
    def __init__(self, config: Optional[PreTradeConfig] = None, seed: int = 42):
        self.config = config or PreTradeConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("Phase21PreTradeValidator: paper_only must remain True")
        self.config = PreTradeConfig(
            seed=int(self.config.seed),
            paper_only=True,
            max_order_notional=float(self.config.max_order_notional),
            max_delta_add=float(self.config.max_delta_add),
            max_vega_add=float(self.config.max_vega_add),
            require_orderflow_confirm=bool(self.config.require_orderflow_confirm),
            enforce_hard_blocks=bool(self.config.enforce_hard_blocks),
        )
        self.seed = int(self.config.seed)
        self._dcounter = 0
        self._ocounter = 0
        self.override_audit: List[Dict[str, Any]] = []
        self.audit: List[Dict[str, Any]] = []

    def _did(self) -> str:
        self._dcounter += 1
        h = hashlib.sha256(f"{self.seed}|p21dec|{self._dcounter}".encode()).hexdigest()[:12]
        return f"p21_dec_{h}"

    def _oid(self) -> str:
        self._ocounter += 1
        h = hashlib.sha256(f"{self.seed}|p21ovr|{self._ocounter}".encode()).hexdigest()[:12]
        return f"p21_ovr_{h}"

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def validate(
        self,
        intents: List[TradeIntent],
        aggregated_delta: float = 0.0,
        aggregated_vega: float = 0.0,
        aggregated_notional: float = 0.0,
        allow_override: bool = False,
    ) -> List[PreTradeDecision]:
        self._log("validate", {"count": len(intents)})
        decisions: List[PreTradeDecision] = []
        for i, intent in enumerate(intents):
            block_reasons: List[str] = []
            warnings: List[str] = []
            if not math.isfinite(intent.notional_usd) or intent.notional_usd < 0.0:
                block_reasons.append("invalid_notional")
            if intent.notional_usd > self.config.max_order_notional + 1e-9:
                block_reasons.append("order_notional_exceeds_limit")
            if abs(intent.delta_est) > self.config.max_delta_add + 1e-9:
                block_reasons.append("delta_add_exceeds_limit")
            if abs(intent.vega_est) > self.config.max_vega_add + 1e-9:
                block_reasons.append("vega_add_exceeds_limit")
            if self.config.require_orderflow_confirm and not intent.orderflow_confirmed:
                block_reasons.append("orderflow_not_confirmed")
            if aggregated_notional + intent.notional_usd > 5000000.0 + 1e-9:  # against global agg
                warnings.append("would_increase_agg_notional")
            if aggregated_delta + intent.delta_est > 2000.0 + 1e-9:
                warnings.append("would_increase_agg_delta")
            if aggregated_vega + intent.vega_est > 50000.0 + 1e-9:
                warnings.append("would_increase_agg_vega")

            blocked = len(block_reasons) > 0 and self.config.enforce_hard_blocks
            approved = not blocked
            override_audit_id = None
            if blocked and allow_override:
                # Only allow override if explicitly requested and logged (paper-only still enforced)
                override_audit_id = self._oid()
                self.override_audit.append({
                    "override_audit_id": override_audit_id,
                    "intent_id": intent.intent_id,
                    "block_reasons": list(block_reasons),
                    "approved_via_override": True,
                    "paper_only": True,
                    "timestamp": _utc_now(),
                })
                blocked = False
                approved = True
                warnings.append("approved_via_audited_override")

            decisions.append(
                PreTradeDecision(
                    decision_id=self._did(),
                    intent_id=intent.intent_id,
                    approved=bool(approved),
                    blocked=bool(blocked),
                    block_reasons=block_reasons,
                    warnings=warnings,
                    override_audit_id=override_audit_id,
                    paper_only=True,
                    timestamp=_det_ts(self.seed, i),
                )
            )
        _assert_no_nan_inf([asdict(d) for d in decisions], "p21_pretrade_decisions")
        return decisions

    def generate_report(self, intents: List[TradeIntent], decisions: List[PreTradeDecision]) -> Dict[str, Any]:
        blocked = [d for d in decisions if d.blocked]
        approved = [d for d in decisions if d.approved and not d.blocked]
        rep = {
            "report": "PHASE21_PRE_TRADE_VALIDATION_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "config": asdict(self.config),
            "intent_count": len(intents),
            "decision_count": len(decisions),
            "intents": [asdict(i) for i in intents],
            "decisions": [asdict(d) for d in decisions],
            "summary": {
                "blocked_count": len(blocked),
                "approved_count": len(approved),
                "override_audit_count": len(self.override_audit),
                "all_hard_blocks_enforced": self.config.enforce_hard_blocks,
                "paper_only": True,
            },
            "override_audit": self.override_audit,
            "audit": self.audit,
            "git_sha": _git_sha(),
            "paper_only": True,
        }
        _assert_no_nan_inf(rep, "p21_pretrade_report")
        return rep
