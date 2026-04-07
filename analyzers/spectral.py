"""Spectral analyzers. Each function returns a structured-stats dict.

These are deterministic primitives consumed by the Behavioral Analyzer (a
non-LLM agent in the future Step 9). Per the build brief \u00a79, no analyzer ever
returns plots or raw arrays \u2014 only summary statistics that an LLM can read
without vision.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import welch


def compute_band_power(
    data: np.ndarray,
    fs: float,
    band: tuple[float, float],
    nperseg: int | None = None,
) -> dict:
    """Average power in ``band`` (Hz) via Welch's method.

    Parameters
    ----------
    data : np.ndarray
        Shape (n_samples,) or (n_channels, n_samples).
    fs : float
        Sampling rate (Hz).
    band : tuple of float
        (low, high) in Hz.
    """
    data = np.asarray(data, dtype=float)
    if data.ndim == 1:
        data = data[None, :]
    n = data.shape[-1]
    if nperseg is None:
        nperseg = min(256, n)
    freqs, psd = welch(data, fs=fs, nperseg=nperseg, axis=-1)
    lo, hi = band
    mask = (freqs >= lo) & (freqs <= hi)
    if not mask.any():
        power = float("nan")
    else:
        power = float(np.mean(psd[..., mask]))
    return {
        "metric": "band_power",
        "band_hz": [float(lo), float(hi)],
        "power": power,
        "n_channels": int(data.shape[0]),
    }


def compute_psd_peak(
    data: np.ndarray,
    fs: float,
    fmin: float = 1.0,
    fmax: float | None = None,
    nperseg: int | None = None,
) -> dict:
    """Peak power and frequency of the PSD within [fmin, fmax]."""
    data = np.asarray(data, dtype=float)
    if data.ndim == 1:
        data = data[None, :]
    n = data.shape[-1]
    if nperseg is None:
        nperseg = min(256, n)
    if fmax is None:
        fmax = fs / 2.0
    freqs, psd = welch(data, fs=fs, nperseg=nperseg, axis=-1)
    psd_mean = psd.mean(axis=0)
    mask = (freqs >= fmin) & (freqs <= fmax)
    if not mask.any():
        return {
            "metric": "psd_peak",
            "peak_freq_hz": float("nan"),
            "peak_power": float("nan"),
        }
    band_freqs = freqs[mask]
    band_psd = psd_mean[mask]
    idx = int(np.argmax(band_psd))
    return {
        "metric": "psd_peak",
        "peak_freq_hz": float(band_freqs[idx]),
        "peak_power": float(band_psd[idx]),
    }


def compute_peak_frequency(
    data: np.ndarray,
    fs: float,
    band: tuple[float, float] = (1.0, 80.0),
    nperseg: int | None = None,
) -> dict:
    """Frequency of maximum PSD within ``band`` (a thinner alias of psd_peak)."""
    res = compute_psd_peak(data, fs=fs, fmin=band[0], fmax=band[1], nperseg=nperseg)
    return {
        "metric": "peak_frequency",
        "band_hz": [float(band[0]), float(band[1])],
        "peak_freq_hz": res["peak_freq_hz"],
    }
