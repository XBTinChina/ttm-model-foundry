"""Tests for analyzers/trivial_pass_patterns.py."""

from __future__ import annotations

import numpy as np

from analyzers.trivial_pass_patterns import (
    check_trivial_pass,
    is_constant_output,
    is_monotone_trend,
    is_white_noise_correlation,
)


def test_constant_positive():
    assert is_constant_output(np.full(100, 0.7)) is True


def test_constant_negative():
    rng = np.random.default_rng(0)
    assert is_constant_output(rng.standard_normal(100)) is False


def test_monotone_positive():
    assert is_monotone_trend(np.linspace(0, 1, 100), min_r2=0.95) is True


def test_monotone_negative():
    rng = np.random.default_rng(0)
    sig = np.sin(np.linspace(0, 6 * np.pi, 200)) + 0.1 * rng.standard_normal(200)
    assert is_monotone_trend(sig, min_r2=0.95) is False


def test_white_noise_positive():
    rng = np.random.default_rng(0)
    assert is_white_noise_correlation(rng.standard_normal(500)) is True


def test_white_noise_negative_for_strong_ar1():
    rng = np.random.default_rng(0)
    n = 500
    x = np.zeros(n)
    for k in range(1, n):
        x[k] = 0.9 * x[k - 1] + rng.standard_normal()
    assert is_white_noise_correlation(x) is False


def test_check_trivial_pass_flags_constant():
    sigs = [{"signature_id": "FS01", "metric_function": "compute_band_power"}]
    outputs = {"FS01": np.full(200, 1.0)}
    flags = check_trivial_pass(outputs, sigs)
    assert len(flags) == 1
    assert flags[0].pattern == "constant_output"


def test_check_trivial_pass_returns_empty_when_clean():
    rng = np.random.default_rng(0)
    sig = np.sin(np.linspace(0, 6 * np.pi, 200)) + 0.1 * rng.standard_normal(200)
    sigs = [{"signature_id": "FS01", "metric_function": "compute_band_power"}]
    outputs = {"FS01": sig}
    flags = check_trivial_pass(outputs, sigs)
    # Sinusoid is not constant, not monotone, not white noise.
    assert flags == []


def test_check_trivial_pass_never_raises_on_unknown_signature():
    flags = check_trivial_pass({}, [{"signature_id": "X", "metric_function": "compute_band_power"}])
    assert flags == []
