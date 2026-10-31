"""Core campaign orchestration with atomic checkpoints and resume."""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.errors import BacktestError, ValidationError
from src.telemetry.serialization import serialize_metrics_strict


class CampaignState(str, Enum):
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


@dataclass
class Step:
    step_id: str
    name: str
    status: str = "pending"  # pending/completed/failed/skipped
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    result_path: Optional[str] = None


@dataclass
class CampaignCheckpoint:
    campaign_id: str
    state: CampaignState
    created_at: str
    updated_at: str
    steps: List[Step] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    seed: int = 42
    artifacts: List[str] = field(default_factory=list)


class CampaignOrchestrator:
    def __init__(self, campaign_id: Optional[str] = None, checkpoint_dir: Optional[Path] = None, seed: int = 42):
        self.campaign_id = campaign_id or f"campaign_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        self.checkpoint_dir = checkpoint_dir or Path("research_state/campaign_checkpoints")
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.seed = int(seed)
        self.checkpoint: Optional[CampaignCheckpoint] = None
        self.latest_checkpoint_path = self.checkpoint_dir / f"{self.campaign_id}_latest.json"

    def _atomic_write_json(self, path: Path, data: Dict[str, Any]) -> None:
        # Strict serialization with allow_nan=False
        serialized = serialize_metrics_strict(data)
        # serialize_metrics_strict may return dict; write as JSON with allow_nan=False
        content = json.dumps(serialized, ensure_ascii=False, indent=2, allow_nan=False)
        fd, tmp_path = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent), suffix=".tmp")
        try:
            os.write(fd, content.encode("utf-8"))
            os.close(fd)
            fd = None
            # Atomic rename
            os.replace(tmp_path, path)
            tmp_path = None
        finally:
            if fd is not None:
                os.close(fd)
            if tmp_path is not None and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

    def create_campaign(self, steps: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> CampaignCheckpoint:
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        step_objs = []
        for s in steps:
            step_objs.append(Step(step_id=s["step_id"], name=s.get("name", s["step_id"]), status="pending"))
        checkpoint = CampaignCheckpoint(
            campaign_id=self.campaign_id,
            state=CampaignState.STARTED,
            created_at=now,
            updated_at=now,
            steps=step_objs,
            metadata=metadata or {},
            seed=self.seed,
            artifacts=[],
        )
        self.checkpoint = checkpoint
        self._save_checkpoint()
        return checkpoint

    def _checkpoint_to_dict(self, cp: CampaignCheckpoint) -> Dict[str, Any]:
        return {
            "campaign_id": cp.campaign_id,
            "state": cp.state.value,
            "created_at": cp.created_at,
            "updated_at": cp.updated_at,
            "steps": [asdict(s) for s in cp.steps],
            "metadata": cp.metadata,
            "seed": cp.seed,
            "artifacts": cp.artifacts,
        }

    def _dict_to_checkpoint(self, d: Dict[str, Any]) -> CampaignCheckpoint:
        steps = []
        for s in d.get("steps", []):
            steps.append(Step(**s))
        return CampaignCheckpoint(
            campaign_id=d["campaign_id"],
            state=CampaignState(d["state"]),
            created_at=d["created_at"],
            updated_at=d["updated_at"],
            steps=steps,
            metadata=d.get("metadata", {}),
            seed=int(d.get("seed", 42)),
            artifacts=d.get("artifacts", []),
        )

    def _save_checkpoint(self) -> Path:
        if self.checkpoint is None:
            raise BacktestError("No checkpoint to save")
        self.checkpoint.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        data = self._checkpoint_to_dict(self.checkpoint)
        # Save to both latest and timestamped
        self._atomic_write_json(self.latest_checkpoint_path, data)
        ts_path = self.checkpoint_dir / f"{self.campaign_id}_{self.checkpoint.updated_at.replace(':','')}.json"
        self._atomic_write_json(ts_path, data)
        return ts_path

    def load_latest_checkpoint(self) -> Optional[CampaignCheckpoint]:
        if self.latest_checkpoint_path.exists():
            try:
                data = json.loads(self.latest_checkpoint_path.read_text(encoding="utf-8"))
                cp = self._dict_to_checkpoint(data)
                self.checkpoint = cp
                return cp
            except Exception as e:
                raise ValidationError(f"Corrupted checkpoint: {e}", context={"path": str(self.latest_checkpoint_path)})
        return None

    def run(self, step_executor=None) -> CampaignCheckpoint:
        if self.checkpoint is None:
            self.load_latest_checkpoint()
        if self.checkpoint is None:
            raise BacktestError("No campaign to run")
        self.checkpoint.state = CampaignState.IN_PROGRESS
        self._save_checkpoint()
        for step in self.checkpoint.steps:
            if step.status == "completed":
                continue  # skip completed
            step.status = "in_progress"
            step.started_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            self._save_checkpoint()
            try:
                if step_executor:
                    result = step_executor(step, self.checkpoint)
                    if isinstance(result, str):
                        step.result_path = result
                step.status = "completed"
                step.completed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                step.error = None
            except Exception as e:
                step.status = "failed"
                step.error = str(e)
                self.checkpoint.state = CampaignState.FAILED
                self._save_checkpoint()
                raise
            self._save_checkpoint()
        self.checkpoint.state = CampaignState.COMPLETED
        self._save_checkpoint()
        return self.checkpoint

    def resume(self, step_executor=None) -> CampaignCheckpoint:
        cp = self.load_latest_checkpoint()
        if cp is None:
            raise BacktestError("No checkpoint to resume")
        self.checkpoint = cp
        # Resume re-runs failed steps and continues from pending/in_progress
        if self.checkpoint.state == CampaignState.COMPLETED:
            return self.checkpoint  # already complete, idempotent
        if self.checkpoint.state == CampaignState.ABORTED:
            self.checkpoint.state = CampaignState.IN_PROGRESS
        elif self.checkpoint.state == CampaignState.FAILED:
            self.checkpoint.state = CampaignState.IN_PROGRESS
        self._save_checkpoint()
        for step in self.checkpoint.steps:
            if step.status == "completed":
                continue  # skip completed (idempotent)
            if step.status in ("failed", "pending", "in_progress"):
                step.status = "in_progress"
                step.started_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                self._save_checkpoint()
                try:
                    if step_executor:
                        result = step_executor(step, self.checkpoint)
                        if isinstance(result, str):
                            step.result_path = result
                    step.status = "completed"
                    step.completed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                    step.error = None
                except Exception as e:
                    step.status = "failed"
                    step.error = str(e)
                    self.checkpoint.state = CampaignState.FAILED
                    self._save_checkpoint()
                    raise
                self._save_checkpoint()
        self.checkpoint.state = CampaignState.COMPLETED
        self._save_checkpoint()
        return self.checkpoint

    def status(self) -> Dict[str, Any]:
        cp = self.load_latest_checkpoint() or self.checkpoint
        if cp is None:
            return {"status": "no_campaign"}
        return {
            "campaign_id": cp.campaign_id,
            "state": cp.state.value,
            "steps_total": len(cp.steps),
            "steps_completed": sum(1 for s in cp.steps if s.status == "completed"),
            "steps_failed": sum(1 for s in cp.steps if s.status == "failed"),
            "steps_pending": sum(1 for s in cp.steps if s.status == "pending"),
            "updated_at": cp.updated_at,
        }

    def abort(self) -> CampaignCheckpoint:
        cp = self.load_latest_checkpoint() or self.checkpoint
        if cp is None:
            raise BacktestError("No campaign to abort")
        self.checkpoint = cp
        self.checkpoint.state = CampaignState.ABORTED
        self._save_checkpoint()
        return self.checkpoint
