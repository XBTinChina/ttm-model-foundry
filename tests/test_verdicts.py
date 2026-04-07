"""Sanity tests for the verdict enum from the build brief \u00a77."""

from __future__ import annotations

from src.controller.verdicts import (
    INNER_LOOP_VERDICTS,
    OUTER_LOOP_VERDICTS,
    TERMINAL_VERDICTS,
    Verdict,
    VerdictMessage,
)


def test_partition_is_disjoint_and_complete():
    all_v = set(Verdict)
    union = INNER_LOOP_VERDICTS | OUTER_LOOP_VERDICTS | TERMINAL_VERDICTS
    assert union == all_v
    assert not (INNER_LOOP_VERDICTS & OUTER_LOOP_VERDICTS)
    assert not (INNER_LOOP_VERDICTS & TERMINAL_VERDICTS)
    assert not (OUTER_LOOP_VERDICTS & TERMINAL_VERDICTS)


def test_verdict_message_carries_payload():
    msg = VerdictMessage(
        verdict=Verdict.IMPLEMENTATION_BUG,
        source_agent="sandbox",
        payload={"traceback": "ZeroDivisionError"},
    )
    assert msg.verdict is Verdict.IMPLEMENTATION_BUG
    assert msg.payload["traceback"] == "ZeroDivisionError"
