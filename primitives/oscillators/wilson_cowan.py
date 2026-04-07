"""Wilson\u2013Cowan excitatory/inhibitory population model (single column).

    \u03c4_E dE/dt = -E + S(c_EE * E - c_EI * I + P)
    \u03c4_I dI/dt = -I + S(c_IE * E - c_II * I + Q)

with S(x) = 1 / (1 + exp(-a * (x - theta))).

Returns the (n_steps, 2) state trajectory [E(t), I(t)]. Wilson\u2013Cowan is not
a phase model, so its output is *not* fed directly to the phase-domain linking
functions; the Programmer (future Step 9) is expected to take the band-limited
PSD of E(t) for spectral signatures.
"""

from __future__ import annotations

import numpy as np


def _sigmoid(x: np.ndarray, a: float, theta: float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-a * (x - theta)))


def simulate_wilson_cowan(
    params: dict | None = None,
    T: float = 2.0,
    dt: float = 1e-3,
    seed: int | None = 0,
) -> np.ndarray:
    if dt <= 0 or T <= 0:
        raise ValueError("T and dt must be positive")
    p = {
        "tau_E": 0.010,
        "tau_I": 0.020,
        "c_EE": 16.0,
        "c_EI": 12.0,
        "c_IE": 15.0,
        "c_II": 3.0,
        "P": 1.0,
        "Q": 0.0,
        "a": 1.3,
        "theta": 4.0,
        "noise_std": 0.0,
    }
    if params:
        p.update(params)

    rng = np.random.default_rng(seed)
    n_steps = int(round(T / dt))
    out = np.zeros((n_steps, 2), dtype=float)
    E, I = 0.1, 0.1
    out[0] = (E, I)
    for t in range(1, n_steps):
        input_E = p["c_EE"] * E - p["c_EI"] * I + p["P"]
        input_I = p["c_IE"] * E - p["c_II"] * I + p["Q"]
        dE = (-E + _sigmoid(np.array(input_E), p["a"], p["theta"])) / p["tau_E"]
        dI = (-I + _sigmoid(np.array(input_I), p["a"], p["theta"])) / p["tau_I"]
        if p["noise_std"] > 0:
            dE = dE + rng.standard_normal() * p["noise_std"] / np.sqrt(dt)
            dI = dI + rng.standard_normal() * p["noise_std"] / np.sqrt(dt)
        E = float(E + dt * dE)
        I = float(I + dt * dI)
        # clip to keep things finite under sane parameter ranges
        E = max(0.0, min(E, 1.0))
        I = max(0.0, min(I, 1.0))
        out[t] = (E, I)
    return out
