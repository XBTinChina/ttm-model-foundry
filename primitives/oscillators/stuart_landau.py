"""Network of N coupled Stuart\u2013Landau oscillators (normal form of a Hopf bifurcation).

    dz_i/dt = (\u03bc + i\u03c9_i) z_i - |z_i|^2 z_i + (K/N) * \u03a3_j (z_j - z_i)

Returns the *phase* trajectory \u03c6_i = arg(z_i), shape (n_steps, N), so that
downstream linking functions can consume it identically to the Kuramoto
output.
"""

from __future__ import annotations

import numpy as np


def simulate_stuart_landau(
    N: int,
    K: float,
    mu: float = 1.0,
    omega: np.ndarray | float | None = None,
    T: float = 2.0,
    dt: float = 1e-3,
    seed: int | None = 0,
) -> np.ndarray:
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

    # Random small initial conditions on the unit disk.
    angles = rng.uniform(0.0, 2.0 * np.pi, size=N)
    radii = rng.uniform(0.1, 0.5, size=N)
    z = radii * np.exp(1j * angles)

    n_steps = int(round(T / dt))
    out = np.empty((n_steps, N), dtype=float)
    out[0] = np.angle(z)
    for t in range(1, n_steps):
        coupling = (K / N) * (np.sum(z) - N * z)
        dz = ((mu + 1j * omega_arr) * z) - (np.abs(z) ** 2) * z + coupling
        z = z + dt * dz
        out[t] = np.angle(z)
    return out
