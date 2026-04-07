"""Verdict enum and carrier for ttm-model-foundry. Section 7 of the build brief.

These verdicts are the only legal communication between agents and the
controller. The state machine (Step 6, future) routes solely on these values.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Verdict(str, Enum):
    """All legal verdicts. Order and spelling are part of the contract."""

    # Inner-loop verdicts (from the Falsifier)
    CONFORMS = "CONFORMS"
    IMPLEMENTATION_BUG = "IMPLEMENTATION_BUG"
    NUMERICAL_INSTABILITY = "NUMERICAL_INSTABILITY"
    BEHAVIORAL_FAILURE = "BEHAVIORAL_FAILURE"
    SPEC_FAILURE = "SPEC_FAILURE"
    THEORY_UNDERSPECIFIED = "THEORY_UNDERSPECIFIED"

    # Outer-loop verdicts (from the Alignment Judge)
    ALIGNED = "ALIGNED"
    PREDICTION_NOT_DERIVABLE = "PREDICTION_NOT_DERIVABLE"
    EXPERIMENT_NONDIAGNOSTIC = "EXPERIMENT_NONDIAGNOSTIC"
    EMPIRICAL_EQUIVALENCE = "EMPIRICAL_EQUIVALENCE"

    # Terminal verdicts (from the controller)
    CONVERGED = "CONVERGED"
    CONVERGED_BUT_THEORY_SUBSTANTIALLY_REVISED = (
        "CONVERGED_BUT_THEORY_SUBSTANTIALLY_REVISED"
    )
    INTRACTABLE = "INTRACTABLE"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    STAGNATED = "STAGNATED"


INNER_LOOP_VERDICTS: frozenset[Verdict] = frozenset(
    {
        Verdict.CONFORMS,
        Verdict.IMPLEMENTATION_BUG,
        Verdict.NUMERICAL_INSTABILITY,
        Verdict.BEHAVIORAL_FAILURE,
        Verdict.SPEC_FAILURE,
        Verdict.THEORY_UNDERSPECIFIED,
    }
)

OUTER_LOOP_VERDICTS: frozenset[Verdict] = frozenset(
    {
        Verdict.ALIGNED,
        Verdict.PREDICTION_NOT_DERIVABLE,
        Verdict.EXPERIMENT_NONDIAGNOSTIC,
        Verdict.EMPIRICAL_EQUIVALENCE,
    }
)

TERMINAL_VERDICTS: frozenset[Verdict] = frozenset(
    {
        Verdict.CONVERGED,
        Verdict.CONVERGED_BUT_THEORY_SUBSTANTIALLY_REVISED,
        Verdict.INTRACTABLE,
        Verdict.BUDGET_EXHAUSTED,
        Verdict.STAGNATED,
    }
)


@dataclass
class VerdictMessage:
    """Concrete carrier for a verdict.

    Every routing decision in the state machine (Step 6) is logged together
    with one of these. Tests can construct them directly.
    """

    verdict: Verdict
    source_agent: str
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
