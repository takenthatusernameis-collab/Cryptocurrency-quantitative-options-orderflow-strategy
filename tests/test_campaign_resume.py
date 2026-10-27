"""Tests for campaign resume / handoff integrity."""

from pathlib import Path

import pytest

HANDOFF = Path("research_state/INITIAL_TASK_HANDOFF.md")


def test_handoff_exists():
    assert HANDOFF.is_file(), "Durable handoff file is missing"


def test_handoff_has_required_sections():
    text = HANDOFF.read_text(encoding="utf-8")
    for section in ("Initial Task Message", "Immediate Objectives", "Next Focus Campaign", "MANDATE"):
        assert section in text, f"Handoff missing required section: {section}"


def test_handoff_has_timestamp():
    text = HANDOFF.read_text(encoding="utf-8")
    assert "Timestamp (UTC)" in text
    assert "2026-" in text


def test_next_focus_campaign_has_phases():
    text = HANDOFF.read_text(encoding="utf-8")
    for phase in ("Phase 1", "Phase 2", "Phase 3", "Phase 4", "Phase 5"):
        assert phase in text, f"Handoff missing focus campaign phase: {phase}"
