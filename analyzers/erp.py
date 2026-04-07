"""ERP component summary statistics.

These are deliberately templated: an ERP component is defined by a name, a
polarity, and a search window. The analyzer returns the extremum within the
window. This is enough for qualitative falsification signatures (e.g. "N400
amplitude is more negative in mismatch than match") without committing to any
parametric inference.
"""

from __future__ import annotations

import numpy as np


def _baseline_correct(erp: np.ndarray, fs: float, baseline_ms: tuple[float, float]) -> np.ndarray:
    s0 = int(round(baseline_ms[0] * 1e-3 * fs))
    s1 = int(round(baseline_ms[1] * 1e-3 * fs))
    s0 = max(s0, 0)
    s1 = max(s1, s0 + 1)
    return erp - np.mean(erp[..., s0:s1], axis=-1, keepdims=True)


def compute_erp_component_amplitude(
    erp: np.ndarray,
    fs: float,
    window_ms: tuple[float, float],
    polarity: str = "negative",
    baseline_ms: tuple[float, float] = (-100.0, 0.0),
    onset_ms: float = 0.0,
) -> dict:
    """Peak amplitude of an ERP component within ``window_ms``.

    Parameters
    ----------
    erp : np.ndarray
        Shape (n_samples,). Time-locked, channel-averaged ERP.
    onset_ms : float
        Time (ms) of stimulus onset relative to start of the array.
    """
    erp = np.asarray(erp, dtype=float)
    if erp.ndim != 1:
        raise ValueError("compute_erp_component_amplitude expects 1-D ERP")
    erp = _baseline_correct(erp, fs, baseline_ms=(baseline_ms[0] - onset_ms, baseline_ms[1] - onset_ms))
    s0 = int(round((window_ms[0] - 0.0) * 1e-3 * fs)) + int(round(onset_ms * 1e-3 * fs))
    s1 = int(round((window_ms[1] - 0.0) * 1e-3 * fs)) + int(round(onset_ms * 1e-3 * fs))
    s0 = max(s0, 0)
    s1 = min(s1, erp.shape[0])
    if s1 <= s0:
        return {"metric": "erp_amplitude", "amplitude": float("nan")}
    seg = erp[s0:s1]
    if polarity == "negative":
        amp = float(np.min(seg))
    else:
        amp = float(np.max(seg))
    return {
        "metric": "erp_amplitude",
        "polarity": polarity,
        "window_ms": [float(window_ms[0]), float(window_ms[1])],
        "amplitude": amp,
    }


def compute_erp_component_latency(
    erp: np.ndarray,
    fs: float,
    window_ms: tuple[float, float],
    polarity: str = "negative",
    baseline_ms: tuple[float, float] = (-100.0, 0.0),
    onset_ms: float = 0.0,
) -> dict:
    """Latency (ms, relative to onset_ms) of the peak in ``window_ms``."""
    erp = np.asarray(erp, dtype=float)
    if erp.ndim != 1:
        raise ValueError("compute_erp_component_latency expects 1-D ERP")
    erp = _baseline_correct(erp, fs, baseline_ms=(baseline_ms[0] - onset_ms, baseline_ms[1] - onset_ms))
    onset_samples = int(round(onset_ms * 1e-3 * fs))
    s0 = int(round(window_ms[0] * 1e-3 * fs)) + onset_samples
    s1 = int(round(window_ms[1] * 1e-3 * fs)) + onset_samples
    s0 = max(s0, 0)
    s1 = min(s1, erp.shape[0])
    if s1 <= s0:
        return {"metric": "erp_latency", "latency_ms": float("nan")}
    seg = erp[s0:s1]
    if polarity == "negative":
        idx = int(np.argmin(seg))
    else:
        idx = int(np.argmax(seg))
    abs_sample = s0 + idx
    latency_ms = (abs_sample - onset_samples) * 1000.0 / fs
    return {
        "metric": "erp_latency",
        "polarity": polarity,
        "window_ms": [float(window_ms[0]), float(window_ms[1])],
        "latency_ms": float(latency_ms),
    }
