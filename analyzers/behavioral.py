"""Behavioral analyzers \u2014 RT distributions, accuracy curves, learning trajectories.

These return summary statistics; downstream LLM agents read these dicts, never
the raw arrays.
"""

from __future__ import annotations

import numpy as np


def compute_rt_distribution_stats(
    rts: np.ndarray,
    fs: float | None = None,
) -> dict:
    """Quantile and shape summary of an RT array (units: seconds).

    ``fs`` is accepted for signature compatibility with the analyzer registry
    but is not used.
    """
    del fs
    rts = np.asarray(rts, dtype=float)
    rts = rts[~np.isnan(rts)]
    if rts.size == 0:
        return {"metric": "rt_distribution", "n": 0}
    q = np.quantile(rts, [0.1, 0.25, 0.5, 0.75, 0.9])
    return {
        "metric": "rt_distribution",
        "n": int(rts.size),
        "mean_s": float(np.mean(rts)),
        "median_s": float(q[2]),
        "q10_s": float(q[0]),
        "q25_s": float(q[1]),
        "q75_s": float(q[3]),
        "q90_s": float(q[4]),
        "std_s": float(np.std(rts, ddof=1)) if rts.size > 1 else 0.0,
    }


def compute_accuracy_curve(
    correct: np.ndarray,
    condition: np.ndarray,
    fs: float | None = None,
) -> dict:
    """Mean accuracy per unique condition level.

    Parameters
    ----------
    correct : np.ndarray
        0/1 array of trial outcomes.
    condition : np.ndarray
        Same shape as ``correct``; condition label per trial (numeric).
    """
    del fs
    correct = np.asarray(correct, dtype=float)
    condition = np.asarray(condition)
    levels = np.unique(condition)
    means: list[float] = []
    counts: list[int] = []
    for lv in levels:
        sel = condition == lv
        means.append(float(np.mean(correct[sel])))
        counts.append(int(sel.sum()))
    return {
        "metric": "accuracy_curve",
        "levels": [float(l) if isinstance(l, (int, float, np.floating, np.integer)) else str(l) for l in levels],
        "accuracy_per_level": means,
        "n_per_level": counts,
        "monotone_increasing": bool(all(means[i] <= means[i + 1] + 1e-12 for i in range(len(means) - 1))),
    }


def compute_learning_trajectory(
    correct: np.ndarray,
    fs: float | None = None,
    window: int = 20,
) -> dict:
    """Sliding-window accuracy trajectory plus a coarse summary.

    Returns first-window and last-window accuracy and the slope of a
    least-squares line through the trajectory.
    """
    del fs
    correct = np.asarray(correct, dtype=float)
    n = correct.shape[0]
    if n < window:
        return {"metric": "learning_trajectory", "n": int(n), "n_windows": 0}
    traj = np.array(
        [correct[i : i + window].mean() for i in range(0, n - window + 1)]
    )
    x = np.arange(traj.shape[0], dtype=float)
    if traj.shape[0] >= 2:
        slope, intercept = np.polyfit(x, traj, 1)
    else:
        slope, intercept = 0.0, float(traj[0])
    return {
        "metric": "learning_trajectory",
        "n": int(n),
        "n_windows": int(traj.shape[0]),
        "first_window_acc": float(traj[0]),
        "last_window_acc": float(traj[-1]),
        "slope": float(slope),
        "intercept": float(intercept),
        "window": int(window),
    }
