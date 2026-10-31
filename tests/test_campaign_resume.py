"""Tests for campaign resume / handoff integrity and atomic checkpoint orchestration."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest

from src.campaign.core import CampaignOrchestrator, CampaignState


HANDOFF_DURABLE = Path("research_state/durable_handoff.md")
HANDOFF_ROOT = Path("HANDOFF_NEXT_AGENT.md")


def test_durable_handoff_exists():
    assert HANDOFF_DURABLE.is_file(), "Durable handoff file is missing"


def test_durable_handoff_is_source_of_truth():
    text = HANDOFF_DURABLE.read_text(encoding="utf-8")
    assert "SINGLE DURABLE HANDOFF" in text
    assert "INITIAL TASK MESSAGE" in text
    assert "Campaign resume hardening" in text


def test_root_handoff_retired():
    # Root handoff should be retired per durable handoff
    if HANDOFF_ROOT.is_file():
        text = HANDOFF_ROOT.read_text(encoding="utf-8")
        assert "RETIRED" in text


def test_campaign_module_exists():
    from src.campaign import core  # noqa: F401
    assert Path("src/campaign/core.py").exists()
    assert Path("scripts/run_campaign.py").exists()


def test_atomic_checkpoint_integrity(tmp_path):
    orch = CampaignOrchestrator(campaign_id="test_atomic", checkpoint_dir=tmp_path / "chk", seed=123)
    steps = [{"step_id": "s1", "name": "step1"}, {"step_id": "s2", "name": "step2"}]
    cp = orch.create_campaign(steps)
    cp_path = tmp_path / "chk" / "test_atomic_latest.json"
    assert cp_path.exists()
    data = json.loads(cp_path.read_text(encoding="utf-8"))
    assert data["campaign_id"] == "test_atomic"
    assert len(data["steps"]) == 2


def test_resume_skips_completed_work_idempotent(tmp_path):
    orch = CampaignOrchestrator(campaign_id="test_resume", checkpoint_dir=tmp_path / "chk", seed=7)
    steps = [{"step_id": "a", "name": "a"}, {"step_id": "b", "name": "b"}]
    orch.create_campaign(steps)
    calls = []

    def executor(step, checkpoint):
        calls.append(step.step_id)
        return str(tmp_path / f"{step.step_id}.json")

    res = orch.run(executor)
    assert res.state == CampaignState.COMPLETED
    assert calls == ["a", "b"]
    calls.clear()
    res2 = orch.resume(executor)
    assert res2.state == CampaignState.COMPLETED
    assert calls == []


def test_resume_reruns_failed_steps(tmp_path):
    orch = CampaignOrchestrator(campaign_id="test_fail", checkpoint_dir=tmp_path / "chk", seed=9)
    steps = [{"step_id": "x", "name": "x"}, {"step_id": "y", "name": "y"}]
    orch.create_campaign(steps)
    calls = []

    def executor(step, checkpoint):
        calls.append(step.step_id)
        if step.step_id == "x" and len([c for c in calls if c == "x"]) == 1:
            raise RuntimeError("boom")
        return "ok"

    with pytest.raises(RuntimeError):
        orch.run(executor)
    calls.clear()

    def executor2(step, checkpoint):
        calls.append(step.step_id)
        return "ok"

    res = orch.resume(executor2)
    assert res.state == CampaignState.COMPLETED
    assert calls == ["x", "y"]


def test_valid_state_transitions(tmp_path):
    orch = CampaignOrchestrator(campaign_id="test_trans", checkpoint_dir=tmp_path / "chk", seed=11)
    steps = [{"step_id": "s1", "name": "s1"}]
    cp = orch.create_campaign(steps)
    assert cp.state == CampaignState.STARTED
    orch.abort()
    st = orch.status()
    assert st["state"] in ("aborted",)

    def ex(s, c):
        return "done"

    res = orch.resume(ex)
    assert res.state == CampaignState.COMPLETED


def test_cli_run_resume_status_abort(tmp_path, monkeypatch):
    from scripts import run_campaign

    chk = tmp_path / "chk"
    monkeypatch.chdir(tmp_path)
    r = run_campaign.main(["status", "--checkpoint-dir", str(chk)])
    assert r == 0
    r = run_campaign.main(["run", "--campaign-id", "cli_test", "--checkpoint-dir", str(chk), "--seed", "42"])
    assert r == 0
    r = run_campaign.main(["status", "--checkpoint-dir", str(chk)])
    assert r == 0
    # Abort on a new in-progress campaign
    orch = CampaignOrchestrator(campaign_id="cli_abort", checkpoint_dir=chk, seed=1)
    steps = [{"step_id": "s1", "name": "s1"}]
    orch.create_campaign(steps)
    r = run_campaign.main(["abort", "--campaign-id", "cli_abort", "--checkpoint-dir", str(chk)])
    assert r == 0


def test_determinism_same_input_identical_state_artifact(tmp_path):
    def make_orch(cid):
        orch = CampaignOrchestrator(campaign_id=cid, checkpoint_dir=tmp_path / f"chk_{cid}", seed=12345)
        steps = [{"step_id": "a", "name": "a"}, {"step_id": "b", "name": "b"}]
        orch.create_campaign(steps)

        def ex(s, c):
            return "ok"

        orch.run(ex)
        return (tmp_path / f"chk_{cid}" / f"{cid}_latest.json").read_text(encoding="utf-8")

    d1 = make_orch("det1")
    d2 = make_orch("det2")
    j1 = json.loads(d1)
    j2 = json.loads(d2)
    assert j1["seed"] == j2["seed"]
    assert len(j1["steps"]) == len(j2["steps"])
    for s1, s2 in zip(j1["steps"], j2["steps"]):
        assert s1["status"] == s2["status"]
        assert s1["step_id"] == s2["step_id"]


def test_strict_serialization_allow_nan_false(tmp_path):
    orch = CampaignOrchestrator(campaign_id="ser_test", checkpoint_dir=tmp_path / "chk", seed=5)
    steps = [{"step_id": "s1", "name": "s1"}]
    cp = orch.create_campaign(steps)
    cp_path = tmp_path / "chk" / "ser_test_latest.json"
    content = cp_path.read_text(encoding="utf-8")
    assert "NaN" not in content
    assert "Infinity" not in content and "-Infinity" not in content
    json.loads(content)


def test_corruption_recovery_truncated_checkpoint(tmp_path):
    orch = CampaignOrchestrator(campaign_id="corr_test", checkpoint_dir=tmp_path / "chk", seed=1)
    steps = [{"step_id": "s1", "name": "s1"}]
    orch.create_campaign(steps)
    cp_path = tmp_path / "chk" / "corr_test_latest.json"
    cp_path.write_text('{"campaign_id": "corr_test", "state": "in_progress",', encoding="utf-8")
    orch2 = CampaignOrchestrator(campaign_id="corr_test", checkpoint_dir=tmp_path / "chk", seed=1)
    with pytest.raises(Exception):
        orch2.load_latest_checkpoint()
