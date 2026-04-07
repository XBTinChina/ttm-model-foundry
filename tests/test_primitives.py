"""Tests for the three primitives in primitives/oscillators/.

Verifies determinism, output shape, and numerical stability.
"""

from __future__ import annotations

import numpy as np
import pytest

from primitives.linking.plv_from_states import plv_from_oscillator_states
from primitives.linking.rt_from_phase import rt_from_phase_threshold
from primitives.oscillators.kuramoto import simulate_kuramoto
from primitives.oscillators.stuart_landau import simulate_stuart_landau
from primitives.oscillators.wilson_cowan import simulate_wilson_cowan


# --- Kuramoto -------------------------------------------------------------


def test_kuramoto_shape():
    out = simulate_kuramoto(N=8, K=1.5, T=1.0, dt=1e-3, seed=0)
    assert out.shape == (1000, 8)
    assert np.all(np.isfinite(out))


def test_kuramoto_determinism():
    a = simulate_kuramoto(N=8, K=1.5, T=1.0, dt=1e-3, seed=42)
    b = simulate_kuramoto(N=8, K=1.5, T=1.0, dt=1e-3, seed=42)
    np.testing.assert_array_equal(a, b)


def test_kuramoto_strong_coupling_synchronizes():
    out = simulate_kuramoto(N=16, K=10.0, T=2.0, dt=1e-3, seed=0)
    # Order parameter at the end should be high.
    final = out[-1]
    r = np.abs(np.mean(np.exp(1j * final)))
    assert r > 0.5


@pytest.mark.parametrize("K", [0.0, 1.0, 3.0, 5.0])
def test_kuramoto_stable_across_K(K):
    out = simulate_kuramoto(N=8, K=K, T=1.0, dt=1e-3, seed=0)
    assert np.all(np.isfinite(out))


# --- Stuart-Landau --------------------------------------------------------


def test_stuart_landau_shape_and_determinism():
    a = simulate_stuart_landau(N=4, K=0.5, mu=1.0, T=1.0, dt=1e-3, seed=7)
    b = simulate_stuart_landau(N=4, K=0.5, mu=1.0, T=1.0, dt=1e-3, seed=7)
    assert a.shape == (1000, 4)
    np.testing.assert_array_equal(a, b)
    assert np.all(np.isfinite(a))


@pytest.mark.parametrize("mu", [-0.2, 0.5, 1.5])
def test_stuart_landau_stable(mu):
    out = simulate_stuart_landau(N=4, K=0.3, mu=mu, T=1.0, dt=1e-3, seed=0)
    assert np.all(np.isfinite(out))


# --- Wilson-Cowan ---------------------------------------------------------


def test_wilson_cowan_shape():
    out = simulate_wilson_cowan(T=1.0, dt=1e-3, seed=0)
    assert out.shape == (1000, 2)
    assert np.all(np.isfinite(out))


def test_wilson_cowan_determinism():
    a = simulate_wilson_cowan(T=1.0, dt=1e-3, seed=3)
    b = simulate_wilson_cowan(T=1.0, dt=1e-3, seed=3)
    np.testing.assert_array_equal(a, b)


def test_wilson_cowan_state_in_unit_interval():
    out = simulate_wilson_cowan(T=1.0, dt=1e-3, seed=0)
    assert out.min() >= 0.0
    assert out.max() <= 1.0


# --- Linking functions ----------------------------------------------------


def test_plv_from_oscillator_states_uses_kuramoto_output():
    phases = simulate_kuramoto(N=4, K=8.0, T=2.0, dt=1e-3, seed=0)
    out = plv_from_oscillator_states(phases, fs=1000.0, pair=(0, 1))
    assert 0.0 <= out["plv"] <= 1.0
    assert out["n_samples"] == phases.shape[0]


def test_rt_from_phase_threshold_returns_finite_when_crossed():
    phase = np.linspace(0, 3.0, 1000)
    out = rt_from_phase_threshold(phase, fs=1000.0, threshold=1.5)
    assert np.isfinite(out["rt_s"])
    assert out["rt_s"] > 0


def test_rt_from_phase_threshold_nan_when_never_crossed():
    phase = np.zeros(1000)
    out = rt_from_phase_threshold(phase, fs=1000.0, threshold=1.5)
    assert np.isnan(out["rt_s"])
