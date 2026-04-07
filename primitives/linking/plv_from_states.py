"""Linking function: PLV between two oscillator phase trajectories."""

from __future__ import annotations

import numpy as np


def plv_from_oscillator_states(
    phases: np.ndarray,
    fs: float,
    pair: tuple[int, int] = (0, 1),
) -> dict:
    """Plain-circular PLV between two raw phase channels.

    Parameters
    ----------
    phases : np.ndarray
        Shape (n_samples, n_oscillators) \u2014 the canonical output of the
        Kuramoto / Stuart\u2013Landau primitives.
    """
    del fs
    phases = np.asarray(phases, dtype=float)
    if phases.ndim != 2:
        raise ValueError("plv_from_oscillator_states expects (n_samples, n_oscillators)")
    i, j = pair
    diff = phases[:, i] - phases[:, j]
    plv = float(np.abs(np.mean(np.exp(1j * diff))))
    return {
        "linking_function": "plv_from_oscillator_states",
        "pair": [int(i), int(j)],
        "plv": plv,
        "n_samples": int(phases.shape[0]),
    }
