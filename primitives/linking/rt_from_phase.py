"""Linking function: derive an RT from an oscillator's phase trajectory.

The model declares ``function_id: rt_from_phase_threshold`` and
``function_params: {threshold: <radians>}``. This function is the executable.
"""

from __future__ import annotations

import numpy as np


def rt_from_phase_threshold(
    phase: np.ndarray,
    fs: float,
    threshold: float = 1.5,
    onset_ms: float = 0.0,
) -> dict:
    """Time (s, relative to onset_ms) at which ``phase`` first exceeds ``threshold``.

    Returns NaN if the threshold is never crossed.
    """
    phase = np.asarray(phase, dtype=float)
    if phase.ndim != 1:
        raise ValueError("rt_from_phase_threshold expects 1-D phase")
    onset_sample = int(round(onset_ms * 1e-3 * fs))
    above = np.where(phase[onset_sample:] > threshold)[0]
    if above.size == 0:
        rt_s = float("nan")
    else:
        rt_s = float(above[0] / fs)
    return {
        "linking_function": "rt_from_phase_threshold",
        "threshold": float(threshold),
        "rt_s": rt_s,
    }
