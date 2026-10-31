"""Campaign orchestration: atomic checkpoint/resume lifecycle for the quant strategy.

A production strategy is only as good as its campaign lifecycle. This package
provides deterministic, atomic, resumable campaign orchestration (modules to be
implemented per durable_handoff.md INITIAL TASK MESSAGE).
"""
