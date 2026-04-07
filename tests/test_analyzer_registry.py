"""Tests for the analyzer registry: every registered function is callable
on synthetic data of the documented shape and returns the documented dict.
"""

from __future__ import annotations

import numpy as np
import pytest

from analyzers.registry import (
    ANALYZERS,
    LINKING_FUNCTIONS,
    get_analyzer,
    get_linking_function,
    list_analyzers,
    list_linking_functions,
)


FS = 200.0  # Hz
DUR = 4.0   # seconds
N_SAMPLES = int(FS * DUR)


@pytest.fixture
def t():
    return np.linspace(0, DUR, N_SAMPLES, endpoint=False)


@pytest.fixture
def two_channel_signal(t):
    rng = np.random.default_rng(0)
    s = np.sin(2 * np.pi * 6.0 * t)
    return np.stack([s + 0.1 * rng.standard_normal(N_SAMPLES),
                     s + 0.1 * rng.standard_normal(N_SAMPLES)])


@pytest.fixture
def trial_signal(t):
    rng = np.random.default_rng(0)
    n_trials = 12
    return np.stack([
        np.sin(2 * np.pi * 6.0 * t) + 0.2 * rng.standard_normal(N_SAMPLES)
        for _ in range(n_trials)
    ])


def test_registry_keys_are_unique():
    assert len(list_analyzers()) == len(set(list_analyzers()))
    assert len(list_linking_functions()) == len(set(list_linking_functions()))


def test_registry_has_expected_minimum_count():
    assert len(ANALYZERS) >= 13
    assert len(LINKING_FUNCTIONS) >= 2


def test_get_analyzer_round_trip():
    for name in list_analyzers():
        assert get_analyzer(name) is ANALYZERS[name]


def test_get_analyzer_unknown_raises():
    with pytest.raises(KeyError, match="not_a_real_function"):
        get_analyzer("not_a_real_function")


def test_get_linking_function_unknown_raises():
    with pytest.raises(KeyError, match="not_a_real_lf"):
        get_linking_function("not_a_real_lf")


# --- Per-function smoke tests ---------------------------------------------


def test_compute_band_power(two_channel_signal):
    out = ANALYZERS["compute_band_power"](two_channel_signal, fs=FS, band=(4, 8))
    assert "power" in out and out["power"] > 0


def test_compute_psd_peak(two_channel_signal):
    out = ANALYZERS["compute_psd_peak"](two_channel_signal, fs=FS)
    assert 4 < out["peak_freq_hz"] < 8


def test_compute_peak_frequency(two_channel_signal):
    out = ANALYZERS["compute_peak_frequency"](two_channel_signal, fs=FS, band=(1, 30))
    assert 4 < out["peak_freq_hz"] < 8


def test_compute_phase_locking_value(two_channel_signal):
    out = ANALYZERS["compute_phase_locking_value"](
        two_channel_signal, fs=FS, band=(4, 8)
    )
    assert out["plv"] > 0.5  # both channels carry the same 6 Hz signal


def test_compute_inter_trial_coherence(trial_signal):
    out = ANALYZERS["compute_inter_trial_coherence"](trial_signal, fs=FS, band=(4, 8))
    assert 0 <= out["itc_mean"] <= 1
    assert out["itc_max"] >= out["itc_mean"]


def test_compute_pairwise_phase_consistency(trial_signal):
    out = ANALYZERS["compute_pairwise_phase_consistency"](
        trial_signal, fs=FS, band=(4, 8)
    )
    assert -1 <= out["ppc"] <= 1


def test_compute_phase_amplitude_coupling(t):
    rng = np.random.default_rng(0)
    low = np.sin(2 * np.pi * 6.0 * t)
    amp_envelope = (1 + low) / 2
    high = amp_envelope * np.sin(2 * np.pi * 60.0 * t)
    sig = low + high + 0.05 * rng.standard_normal(t.shape[0])
    out = ANALYZERS["compute_phase_amplitude_coupling"](
        sig, fs=FS, phase_band=(4, 8), amp_band=(40, 80)
    )
    assert out["modulation_index"] > 0


def test_compute_granger_causality_pair():
    rng = np.random.default_rng(0)
    n = 1000
    x = np.zeros(n)
    y = np.zeros(n)
    for k in range(2, n):
        x[k] = 0.6 * x[k - 1] + rng.standard_normal()
        y[k] = 0.5 * y[k - 1] + 0.7 * x[k - 1] + rng.standard_normal()
    out = ANALYZERS["compute_granger_causality_pair"](
        np.stack([x, y]), fs=FS, order=3
    )
    assert out["gc_x_to_y"] > out["gc_y_to_x"]


def test_compute_erp_component_amplitude_and_latency():
    fs = 500.0
    n = 500
    t_ms = (np.arange(n) - 100) * 1000 / fs
    erp = -np.exp(-((t_ms - 200) ** 2) / (2 * 50 ** 2))
    out_amp = ANALYZERS["compute_erp_component_amplitude"](
        erp, fs=fs, window_ms=(150, 300), polarity="negative",
        baseline_ms=(-100, 0), onset_ms=200,
    )
    assert out_amp["amplitude"] < 0
    out_lat = ANALYZERS["compute_erp_component_latency"](
        erp, fs=fs, window_ms=(150, 300), polarity="negative",
        baseline_ms=(-100, 0), onset_ms=200,
    )
    assert "latency_ms" in out_lat


def test_compute_rt_distribution_stats():
    rng = np.random.default_rng(0)
    rts = rng.gamma(shape=2.0, scale=0.2, size=200)
    out = ANALYZERS["compute_rt_distribution_stats"](rts)
    assert out["n"] == 200
    assert out["q10_s"] < out["median_s"] < out["q90_s"]


def test_compute_accuracy_curve():
    correct = np.array([0, 0, 1, 1, 1, 1, 1, 1])
    cond = np.array([0, 0, 1, 1, 2, 2, 3, 3])
    out = ANALYZERS["compute_accuracy_curve"](correct, cond)
    assert out["accuracy_per_level"] == [0.0, 1.0, 1.0, 1.0]
    assert out["monotone_increasing"] is True


def test_compute_learning_trajectory():
    rng = np.random.default_rng(0)
    correct = np.concatenate([
        (rng.random(100) < 0.5).astype(float),
        (rng.random(100) < 0.9).astype(float),
    ])
    out = ANALYZERS["compute_learning_trajectory"](correct, window=20)
    assert out["last_window_acc"] > out["first_window_acc"]
    assert out["slope"] > 0
