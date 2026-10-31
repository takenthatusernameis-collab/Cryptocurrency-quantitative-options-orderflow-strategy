"""Campaign orchestration: atomic checkpoint/resume lifecycle for the quant strategy.

A production strategy is only as good as its campaign lifecycle. This package
provides deterministic, atomic, resumable campaign orchestration:

- :mod:`src.campaign.state` defines the campaign state machine and strict
  JSON serialization (``allow_nan=False``).
- :mod:`src.campaign.checkpoint` provides atomic write-to-temp-then-rename
  checkpointing so no partial/torn artifact is ever observable.
- :mod:`src.campaign.orchestrator` implements run/resume/status/abort verbs
  with skip-completed and replay-failed semantics.
"""

from .checkpoint import (
    CheckpointCorruptionError,
    atomic_read_checkpoint,
    atomic_write_checkpoint,
)
from .orchestrator import (
    CampaignAbortError,
    CampaignOrchestrator,
    CampaignStateError,
    RunResult,
)
from .state import (
    CampaignState,
    StepState,
    campaign_state_to_dict,
    deserialize_campaign_state,
    serialize_campaign_state,
)

__all__ = [
    "CampaignState",
    "StepState",
    "CampaignOrchestrator",
    "RunResult",
    "CampaignStateError",
    "CampaignAbortError",
    "CheckpointCorruptionError",
    "atomic_read_checkpoint",
    "atomic_write_checkpoint",
    "serialize_campaign_state",
    "deserialize_campaign_state",
    "campaign_state_to_dict",
]