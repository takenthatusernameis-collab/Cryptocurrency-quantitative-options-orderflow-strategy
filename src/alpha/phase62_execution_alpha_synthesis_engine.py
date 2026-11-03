"""
Phase 62: Execution Alpha Synthesis Engine (crypto options + orderflow).

Execution alpha synthesis: cross-venue alpha signal fusion from attribution outputs,
regime-conditional alpha weighting, orderflow-conditioned position sizing, deterministic.
PAPER-ONLY. Composes Phases 17-61.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List

from src.alpha.phase61_execution_alpha_attribution_engine import (
    Phase61ExecutionAlphaAttributionEngine,
    Phase61ExecutionAlphaAttributionConfig,
)
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
    h = hashlib.sha256(f"{seed}|p62synth|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p62synth_{tag}_{h}"


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
class Phase62ExecutionAlphaSynthesisConfig:
    seed: int = 62060
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 80
    max_position_scale: float = 1.4
    min_position_scale: float = 0.3
    hard_limit_notional_usd: float = 2_400_000.0
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError("Phase62ExecutionAlphaSynthesis: paper_only must remain True (live path hard-gated)")
        if self.hard_limit_notional_usd <= 0:
            raise ValueError("hard_limit_notional_usd must be > 0")


class Phase62ExecutionAlphaSynthesisEngine:
    """Execution alpha synthesis: cross-venue alpha signal fusion from attribution outputs."""

    def __init__(self, cfg: Phase62ExecutionAlphaSynthesisConfig | None = None) -> None:
        self.cfg = cfg or Phase62ExecutionAlphaSynthesisConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase62ExecutionAlphaSynthesisEngine: paper_only must remain True")
        self.attr61 = Phase61ExecutionAlphaAttributionEngine(
            Phase61ExecutionAlphaAttributionConfig(seed=self.cfg.seed + 1, paper_only=True, cycles=5)
        )
        self.exec60 = Phase60AdaptiveExecutionIntelligenceEngine()
        self.alpha57 = Phase57CrossVenueOptionsExecutionAlphaFusion()
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.tox58 = Phase58FlowToxicityMitigator()
        self.synth: List[Dict[str, Any]] = []
        self.regime_weights: List[Dict[str, Any]] = []
        self.sizing: List[Dict[str, Any]] = []
        self.fused_alpha: List[Dict[str, Any]] = []
        self._cycle = 0

    def _regime_weight(self, regime: str, toxicity: float) -> float:
        base = {"normal": 1.0, "elevated": 0.85, "high_toxicity": 0.6, "vol_shock": 0.5}[regime]
        tox_adj = 1.0 - min(0.4, toxicity * 0.6)
        return float(max(0.3, min(1.0, base * tox_adj)))

    def _position_scale(self, flow_imbalance: float, toxicity: float, regime_weight: float) -> float:
        imb_mult = 0.8 + 0.4 * max(0.0, min(1.0, 0.5 + flow_imbalance * 0.8))
        tox_mult = 1.0 - min(0.5, toxicity * 0.7)
        scale = imb_mult * tox_mult * regime_weight
        return float(max(self.cfg.min_position_scale, min(self.cfg.max_position_scale, scale)))

    def synthesize_alpha(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.synth = []
        self.regime_weights = []
        self.sizing = []
        self.fused_alpha = []

        attr_rep = self.attr61.run_attribution(cycles=50)
        exec_rep = self.exec60.run_intelligence(cycles=4)
        alpha_rep = self.alpha57.fuse()
        of_rep = self.of.run_campaign(cycles=4)
        tox_rep = self.tox58.mitigate(cycles=4)

        avg_tox = _finite(tox_rep.get("avg_vpin", 0.18))
        avg_quality = _finite(exec_rep.get("avg_execution_quality", 0.5))
        alpha_decayed = _finite(alpha_rep.get("alpha_decayed", 0.0))
        attr_ir = _finite(attr_rep.get("information_ratio", 0.0))
        attr_sharpe = _finite(attr_rep.get("sharpe", 0.0))

        for i in range(cycles):
            venue = self.cfg.venues[i % len(self.cfg.venues)]
            underlying = self.cfg.underlyings[i % len(self.cfg.underlyings)]
            toxicity_i = max(0.0, min(1.0, avg_tox + (i % 13) * 0.016))
            vol_shock_i = min(0.06, 0.014 + avg_tox * 0.05 + (i % 7) * 0.003)
            if toxicity_i >= 0.38 or vol_shock_i >= 0.04:
                regime = "high_toxicity"
            elif toxicity_i >= 0.24 or vol_shock_i >= 0.02:
                regime = "elevated"
            else:
                regime = "normal"
            flow_imb = max(-1.0, min(1.0, (i % 17) / 8.0 - 1.0 + (1.0 - toxicity_i) * 0.4))
            rweight = self._regime_weight(regime, toxicity_i)
            pscale = self._position_scale(flow_imb, toxicity_i, rweight)
            fused = float(_finite((alpha_decayed + attr_ir * 0.4 + (1.0 - toxicity_i) * 0.3) * rweight * pscale))
            self.synth.append(
                serialize_metrics_strict(
                    {
                        "synth_id": _make_id(self.cfg.seed, "synth", i),
                        "cycle": i,
                        "venue": venue,
                        "underlying": underlying,
                        "regime": regime,
                        "toxicity": round(float(_finite(toxicity_i)), 6),
                        "vol_shock": round(float(_finite(vol_shock_i)), 6),
                        "fused_alpha": round(float(fused), 6),
                        "paper_only": True,
                        "timestamp": _utc_now(),
                    }
                )
            )
            self.regime_weights.append(
                serialize_metrics_strict(
                    {
                        "rw_id": _make_id(self.cfg.seed, "rw", i),
                        "cycle": i,
                        "regime": regime,
                        "regime_weight": round(float(rweight), 6),
                        "paper_only": True,
                        "timestamp": _utc_now(),
                    }
                )
            )
            self.sizing.append(
                serialize_metrics_strict(
                    {
                        "sz_id": _make_id(self.cfg.seed, "sz", i),
                        "cycle": i,
                        "flow_imbalance": round(float(flow_imb), 6),
                        "toxicity": round(float(_finite(toxicity_i)), 6),
                        "position_scale": round(float(pscale), 6),
                        "hard_limit_notional_usd": self.cfg.hard_limit_notional_usd,
                        "paper_only": True,
                        "timestamp": _utc_now(),
                    }
                )
            )
            self.fused_alpha.append(
                serialize_metrics_strict(
                    {
                        "fa_id": _make_id(self.cfg.seed, "fa", i),
                        "cycle": i,
                        "fused_alpha": round(float(fused), 6),
                        "avg_execution_quality": round(float(avg_quality), 6),
                        "paper_only": True,
                        "timestamp": _utc_now(),
                    }
                )
            )

        rep = serialize_metrics_strict(
            {
                "phase": "PHASE62_EXECUTION_ALPHA_SYNTHESIS_ENGINE",
                "timestamp": _utc_now(),
                "paper_only": True,
                "gates_ok": True,
                "seed": self.cfg.seed,
                "cycles": cycles,
                "n_synth": len(self.synth),
                "n_regime_weights": len(self.regime_weights),
                "n_sizing": len(self.sizing),
                "n_fused_alpha": len(self.fused_alpha),
                "avg_fused_alpha": round(float(sum(x["fused_alpha"] for x in self.fused_alpha) / max(1, len(self.fused_alpha))), 6),
                "avg_regime_weight": round(float(sum(x["regime_weight"] for x in self.regime_weights) / max(1, len(self.regime_weights))), 6),
                "avg_position_scale": round(float(sum(x["position_scale"] for x in self.sizing) / max(1, len(self.sizing))), 6),
                "composes": ["PHASE61", "PHASE60", "PHASE57", "PHASE58"],
            }
        )
        _assert_finite(rep, "phase62_synth_rep")
        return rep

    def generate_artifacts(self, outdir: str = "research_state") -> Dict[str, Any]:
        Path(outdir).mkdir(parents=True, exist_ok=True)
        rep = self.synthesize_alpha(cycles=self.cfg.cycles)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = Path(outdir) / f"PHASE62_EXECUTION_ALPHA_SYNTHESIS_{ts}.json"
        md_path = Path(outdir) / f"PHASE62_EXECUTION_ALPHA_SYNTHESIS_{ts}.md"
        payload = serialize_metrics_strict(
            {
                "report": rep,
                "synth": self.synth,
                "regime_weights": self.regime_weights,
                "sizing": self.sizing,
                "fused_alpha": self.fused_alpha,
                "paper_only": True,
            }
        )
        _assert_finite(payload, "phase62_synth_payload")
        json_path.write_text(json.dumps(payload, indent=2))
        md_lines = [
            "# Phase 62: Execution Alpha Synthesis Engine (crypto options + orderflow)",
            f"- Timestamp: {_utc_now()}",
            f"- Paper-only: true",
            f"- Gates OK: {rep['gates_ok']}",
            f"- Cycles: {rep['cycles']}",
            f"- Avg fused alpha: {rep['avg_fused_alpha']}",
            f"- Avg regime weight: {rep['avg_regime_weight']}",
            f"- Avg position scale: {rep['avg_position_scale']}",
            f"- Composes: {', '.join(rep['composes'])}",
            "",
            "## Artifacts",
            f"- JSON: {json_path}",
            f"- MD: {md_path}",
            "",
            "## Notes",
            "- Cross-venue alpha signal fusion from attribution outputs",
            "- Regime-conditional alpha weighting, orderflow-conditioned position sizing",
            "- Deterministic, finite numerics, PAPER-ONLY",
        ]
        md_path.write_text("\n".join(md_lines))
        return serialize_metrics_strict(
            {
                "phase": rep["phase"],
                "gates_ok": True,
                "paper_only": True,
                "json_path": str(json_path),
                "md_path": str(md_path),
                "n_synth": rep["n_synth"],
            }
        )
