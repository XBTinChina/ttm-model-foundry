"""Deterministic trivial-pass detectors (\u00a78 of the build brief).

These never raise. They return ``TrivialPassFlag`` objects that the
controller (Step 6, future) attaches to a run as human-review hints. Per the
brief: "trigger a human-review flag without blocking convergence".
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass
class TrivialPassFlag:
    """One detected suspicious pattern. ``signature_id`` is optional."""

    pattern: str   # "constant_output" | "monotone_trend" | "white_noise_correlation"
    signature_id: str | None
    detail: str


def is_constant_output(arr: np.ndarray, atol: float = 1e-9) -> bool:
    """True if the signal varies by less than ``atol`` end-to-end."""
    arr = np.asarray(arr, dtype=float)
    if arr.size == 0:
        return False
    return bool(np.nanmax(arr) - np.nanmin(arr) <= atol)


def is_monotone_trend(arr: np.ndarray, min_r2: float = 0.95) -> bool:
    """True if a linear fit explains \u2265 ``min_r2`` of the variance.

    Indicates the "signature" is just a linear ramp \u2014 not a structural
    consequence of the model.
    """
    arr = np.asarray(arr, dtype=float)
    arr = arr[~np.isnan(arr)]
    if arr.size < 3:
        return False
    var = float(np.var(arr))
    if var <= 0.0:
        # constant; covered by is_constant_output
        return False
    x = np.arange(arr.size, dtype=float)
    slope, intercept = np.polyfit(x, arr, 1)
    fit = slope * x + intercept
    ss_res = float(np.sum((arr - fit) ** 2))
    ss_tot = float(np.sum((arr - arr.mean()) ** 2))
    if ss_tot <= 0.0:
        return False
    r2 = 1.0 - ss_res / ss_tot
    return bool(r2 >= min_r2)


def is_white_noise_correlation(arr: np.ndarray, alpha: float = 0.05) -> bool:
    """True if ``arr`` is statistically indistinguishable from white noise.

    Uses the Ljung-Box-style heuristic: compute lag-1 autocorrelation and
    compare its absolute value to the white-noise critical value
    ``z_{1-alpha/2} / sqrt(n)``. If |r1| < critical, the series is consistent
    with white noise.
    """
    arr = np.asarray(arr, dtype=float)
    arr = arr[~np.isnan(arr)]
    n = arr.size
    if n < 10:
        return False
    arr = arr - arr.mean()
    denom = float(np.sum(arr ** 2))
    if denom <= 0.0:
        return False
    r1 = float(np.sum(arr[1:] * arr[:-1]) / denom)
    # Two-sided z critical value (table-based to avoid pulling in scipy.stats here).
    z_table = {0.10: 1.6449, 0.05: 1.9600, 0.01: 2.5758}
    z = z_table.get(round(alpha, 2), 1.9600)
    crit = z / np.sqrt(n)
    return bool(abs(r1) < crit)


def check_trivial_pass(
    simulation_outputs: dict[str, np.ndarray],
    signatures: Iterable[dict],
) -> list[TrivialPassFlag]:
    """Run all three detectors against each signature's referenced array.

    Parameters
    ----------
    simulation_outputs:
        Mapping from signature_id (or metric_function name) to the 1-D array
        the analyzer would consume.
    signatures:
        Iterable of falsification-signature dicts (as in M).
    """
    flags: list[TrivialPassFlag] = []
    for sig in signatures:
        sig_id = sig.get("signature_id")
        key = sig_id or sig.get("metric_function")
        if key not in simulation_outputs:
            continue
        arr = simulation_outputs[key]
        if is_constant_output(arr):
            flags.append(
                TrivialPassFlag(
                    pattern="constant_output",
                    signature_id=sig_id,
                    detail=f"signal range below tolerance for {key}",
                )
            )
            continue
        if is_monotone_trend(arr):
            flags.append(
                TrivialPassFlag(
                    pattern="monotone_trend",
                    signature_id=sig_id,
                    detail=f"linear fit R\u00b2 \u2265 0.95 for {key}",
                )
            )
            continue
        if is_white_noise_correlation(arr):
            flags.append(
                TrivialPassFlag(
                    pattern="white_noise_correlation",
                    signature_id=sig_id,
                    detail=f"lag-1 autocorrelation indistinguishable from noise for {key}",
                )
            )
    return flags
