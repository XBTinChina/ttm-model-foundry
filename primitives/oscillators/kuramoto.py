"""Kuramoto network of N globally-coupled phase oscillators.

    d\u03c6_i/dt = \u03c9_i + (K/N) * \u03a3_j sin(\u03c6_j - \u03c6_i)

Pure function: deterministic given ``seed``. Returns the phase trajectory
shaped (n_steps, N) so that downstream linking functions
(``plv_from_oscillator_states``) can consume it directly.
"""

from __future__ import annotations

import numpy as np


def simulate_kuramoto(
    N: int,
    K: float,
    omega: np.ndarray | float | None = None,
    T: float = 2.0,
    dt: float = 1e-3,
    seed: int | None = 0,
    initial_phases: np.ndarray | None = None,
) -> np.ndarray:
    """Integrate the Kuramoto model with Euler steps.

    Parameters
    ----------
    N : int
        Number of oscillators.
    K : float
        Global coupling strength.
    omega : float or (N,) array, optional
        Natural frequencies in rad/s. If None, drawn from N(0, 1) with the
        provided seed.
    T : float
        Total simulated time (s).
    dt : float
        Integration step (s).
    seed : int, optional
        RNG seed.
    initial_phases : (N,) array, optional
        Initial phases. If None, drawn uniform on [0, 2\u03c0).

    Returns
    -------
    phases : (n_steps, N) array of phases (radians, unwrapped).
    """
    if N <= 0:
        raise ValueError("N must be positive")
    if dt <= 0 or T <= 0:
        raise ValueError("T and dt must be positive")
    rng = np.random.default_rng(seed)
    if omega is None:
        omega_arr = rng.standard_normal(N)
    elif np.isscalar(omega):
        omega_arr = np.full(N, float(omega))
    else:
        omega_arr = np.asarray(omega, dtype=float)
        if omega_arr.shape != (N,):
            raise ValueError("omega must have shape (N,)")
    if initial_phases is None:
        phi = rng.uniform(0.0, 2.0 * np.pi, size=N)
    else:
        phi = np.asarray(initial_phases, dtype=float).copy()
        if phi.shape != (N,):
            raise ValueError("initial_phases must have shape (N,)")

    n_steps = int(round(T / dt))
    out = np.empty((n_steps, N), dtype=float)
    out[0] = phi
    for t in range(1, n_steps):
        diff = phi[None, :] - phi[:, None]  # (N, N): phi_j - phi_i
        coupling = (K / N) * np.sum(np.sin(diff), axis=1)
        phi = phi + dt * (omega_arr + coupling)
        out[t] = phi
    return out
