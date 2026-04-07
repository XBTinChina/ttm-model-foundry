"""Phase-based analyzers (PLV, ITC, PPC).

All inputs are real time-series. Phase is extracted by Hilbert transform on a
band-limited copy of the signal (band-pass via FFT). Outputs are summary
statistics, never raw arrays.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import butter, filtfilt, hilbert


def _bandpass(data: np.ndarray, fs: float, band: tuple[float, float]) -> np.ndarray:
    lo, hi = band
    nyq = 0.5 * fs
    low = max(lo / nyq, 1e-6)
    high = min(hi / nyq, 0.999999)
    b, a = butter(N=4, Wn=[low, high], btype="bandpass")
    # filtfilt requires len(data) > padlen; default padlen ~ 3*max(len(a), len(b))
    return filtfilt(b, a, data, axis=-1)


def _instantaneous_phase(
    data: np.ndarray, fs: float, band: tuple[float, float] | None
) -> np.ndarray:
    if band is not None:
        data = _bandpass(data, fs, band)
    analytic = hilbert(data, axis=-1)
    return np.angle(analytic)


def compute_phase_locking_value(
    data: np.ndarray,
    fs: float,
    band: tuple[float, float],
    window_ms: tuple[float, float] | None = None,
    pair: tuple[int, int] = (0, 1),
) -> dict:
    """PLV between two channels of ``data`` over an optional time window.

    Parameters
    ----------
    data : np.ndarray
        Shape (n_channels, n_samples) with n_channels >= 2.
    """
    data = np.asarray(data, dtype=float)
    if data.ndim != 2 or data.shape[0] < 2:
        raise ValueError("compute_phase_locking_value expects shape (>=2, n_samples)")
    i, j = pair
    phases = _instantaneous_phase(data[[i, j]], fs=fs, band=band)
    if window_ms is not None:
        s0 = int(round(window_ms[0] * 1e-3 * fs))
        s1 = int(round(window_ms[1] * 1e-3 * fs))
        s0 = max(s0, 0)
        s1 = min(s1, phases.shape[-1])
        phases = phases[..., s0:s1]
    diff = phases[0] - phases[1]
    plv = float(np.abs(np.mean(np.exp(1j * diff))))
    return {
        "metric": "plv",
        "band_hz": [float(band[0]), float(band[1])],
        "pair": [int(i), int(j)],
        "plv": plv,
        "n_samples": int(phases.shape[-1]),
    }


def compute_inter_trial_coherence(
    data: np.ndarray,
    fs: float,
    band: tuple[float, float],
) -> dict:
    """ITC across trials. ``data`` shape: (n_trials, n_samples)."""
    data = np.asarray(data, dtype=float)
    if data.ndim != 2:
        raise ValueError("compute_inter_trial_coherence expects shape (n_trials, n_samples)")
    phases = _instantaneous_phase(data, fs=fs, band=band)
    itc_per_sample = np.abs(np.mean(np.exp(1j * phases), axis=0))
    return {
        "metric": "itc",
        "band_hz": [float(band[0]), float(band[1])],
        "itc_mean": float(np.mean(itc_per_sample)),
        "itc_max": float(np.max(itc_per_sample)),
        "n_trials": int(data.shape[0]),
    }


def compute_pairwise_phase_consistency(
    data: np.ndarray,
    fs: float,
    band: tuple[float, float],
) -> dict:
    """PPC across trials. ``data`` shape: (n_trials, n_samples).

    Uses the unbiased estimator: PPC = (|sum(e^{i\u03c6})|^2 - n) / (n*(n-1)).
    """
    data = np.asarray(data, dtype=float)
    if data.ndim != 2 or data.shape[0] < 2:
        raise ValueError("compute_pairwise_phase_consistency expects (>=2, n_samples)")
    phases = _instantaneous_phase(data, fs=fs, band=band)
    # mean phase per trial
    mean_phase = np.angle(np.mean(np.exp(1j * phases), axis=-1))
    n = mean_phase.shape[0]
    s = np.sum(np.exp(1j * mean_phase))
    ppc = (np.abs(s) ** 2 - n) / (n * (n - 1))
    return {
        "metric": "ppc",
        "band_hz": [float(band[0]), float(band[1])],
        "ppc": float(ppc),
        "n_trials": int(n),
    }
