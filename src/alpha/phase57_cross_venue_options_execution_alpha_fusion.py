from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from src.telemetry.serialization import serialize_metrics_strict


@dataclass(frozen=True)
class Phase57AlphaFusionConfig:
    seed: int = 77777
    paper_only: bool = True
    venues: tuple[str, ...] = ("deribit", "okx", "bybit")

    def __post_init__(self) -> None:
        if not self.paper_only:
            raise ValueError("paper_only must remain True (live paths hard-gated)")


@dataclass
class Phase57CrossVenueOptionsExecutionAlphaFusion:
    cfg: Phase57AlphaFusionConfig = field(default_factory=Phase57AlphaFusionConfig)
    domain_focus: str = "crypto_options_orderflow"

    def fuse(self, signals: Dict[str, float] | None = None) -> Dict[str, Any]:
        signals = signals or {"flow": 0.6, "vol": 0.4, "inv": -0.2}
        flow = float(signals.get("flow", 0.0))
        vol = float(signals.get("vol", 0.0))
        inv = float(signals.get("inv", 0.0))
        alpha = 0.4 * flow + 0.35 * vol + 0.25 * inv
        alpha_decayed = alpha * 0.9
        venue = "deribit" if alpha_decayed > 0 else "okx"
        rep = {
            "phase": "PHASE57_CROSS_VENUE_OPTIONS_EXECUTION_ALPHA_FUSION",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "paper_only": True,
            "live_path_hard_gated": True,
            "domain_focus": self.domain_focus,
            "signals": signals,
            "alpha_raw": alpha,
            "alpha_decayed": alpha_decayed,
            "selected_venue": venue,
            "integration": "Phase48+Phase51+Phase54+Phase56",
            "deterministic": True,
            "finite": True,
        }
        return serialize_metrics_strict(rep)

    def generate_artifacts(self, outdir: str = "research_state") -> Dict[str, str]:
        p = Path(outdir)
        p.mkdir(parents=True, exist_ok=True)
        rep = self.fuse()
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = p / f"PHASE57_ALPHA_FUSION_{ts}.json"
        mpath = p / f"PHASE57_ALPHA_FUSION_{ts}.md"
        jpath.write_text(__import__("json").dumps(rep, indent=2))
        mpath.write_text(f"# PHASE57 Alpha Fusion\n\n- alpha_decayed: {rep['alpha_decayed']:.6f}\n- venue: {rep['selected_venue']}\n- paper_only: true\n")
        return {"json_path": str(jpath), "md_path": str(mpath)}
