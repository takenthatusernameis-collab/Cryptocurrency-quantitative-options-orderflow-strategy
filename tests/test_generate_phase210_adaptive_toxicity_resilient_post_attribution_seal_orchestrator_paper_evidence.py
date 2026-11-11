import os
from scripts import generate_phase210_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence as gen


def test_phase210_generate_no_write_valid():
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    d = gen.generate(cycles=12, seed=210210, write=False)
    assert d["validation"]["valid"] is True
    assert d["validation"]["issues"] == []
    assert d["paper_only"] is True
    assert d["live_trading_enabled"] is False
    assert d["next9_unblocked"] is False
    assert "PHASE209" in d["campaign"]["composes"]
    assert "PHASE32" in d["campaign"]["composes"]
