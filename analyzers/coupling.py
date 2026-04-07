"""Cross-frequency and directed-coupling analyzers."""

from __future__ import annotations

import numpy as np
from scipy.signal import butter, filtfilt, hilbert


def _bandpass(data: np.ndarray, fs: float, band: tuple[float, float]) -> np.ndarray:
    nyq = 0.5 * fs
    b, a = butter(
        N=4,
        Wn=[max(band[0] / nyq, 1e-6), min(band[1] / nyq, 0.999999)],
        btype="bandpass",
    )
    return filtfilt(b, a, data, axis=-1)


def compute_phase_amplitude_coupling(
    data: np.ndarray,
    fs: float,
    phase_band: tuple[float, float],
    amp_band: tuple[float, float],
    n_bins: int = 18,
) -> dict:
    """Modulation index (Tort 2010) for phase-amplitude coupling on a 1-D signal."""
    data = np.asarray(data, dtype=float)
    if data.ndim != 1:
        raise ValueError("compute_phase_amplitude_coupling expects 1-D data")
    phase = np.angle(hilbert(_bandpass(data, fs, phase_band)))
    amp = np.abs(hilbert(_bandpass(data, fs, amp_band)))
    edges = np.linspace(-np.pi, np.pi, n_bins + 1)
    bin_idx = np.digitize(phase, edges) - 1
    bin_idx = np.clip(bin_idx, 0, n_bins - 1)
    mean_amp = np.zeros(n_bins)
    for k in range(n_bins):
        sel = bin_idx == k
        mean_amp[k] = amp[sel].mean() if sel.any() else 0.0
    if mean_amp.sum() <= 0:
        mi = float("nan")
    else:
        p = mean_amp / mean_amp.sum()
        # KL divergence to uniform, normalized by log(n_bins)
        with np.errstate(divide="ignore", invalid="ignore"):
            kl = np.nansum(p * np.log(p * n_bins))
        mi = float(kl / np.log(n_bins))
    return {
        "metric": "pac_mi",
        "phase_band_hz": [float(phase_band[0]), float(phase_band[1])],
        "amp_band_hz": [float(amp_band[0]), float(amp_band[1])],
        "modulation_index": mi,
        "n_bins": int(n_bins),
    }


def compute_granger_causality_pair(
    data: np.ndarray,
    fs: float,
    order: int = 5,
) -> dict:
    """Bivariate time-domain Granger causality (X -> Y and Y -> X) via VAR fits.

    Parameters
    ----------
    data : np.ndarray
        Shape (2, n_samples). Row 0 is X, row 1 is Y.
    """
    data = np.asarray(data, dtype=float)
    if data.ndim != 2 or data.shape[0] != 2:
        raise ValueError("compute_granger_causality_pair expects shape (2, n_samples)")
    x, y = data[0], data[1]
    n = x.shape[0]
    if n <= order + 1:
        return {
            "metric": "granger_pair",
            "order": int(order),
            "gc_x_to_y": float("nan"),
            "gc_y_to_x": float("nan"),
        }

    def _var_residual_var(target: np.ndarray, regressors: list[np.ndarray]) -> float:
        # Build lagged design matrix.
        rows = n - order
        cols = sum(1 for _ in regressors) * order
        X = np.zeros((rows, cols))
        for i, reg in enumerate(regressors):
            for k in range(1, order + 1):
                X[:, i * order + (k - 1)] = reg[order - k : n - k]
        Y = target[order:]
        # Add intercept.
        X = np.hstack([np.ones((rows, 1)), X])
        beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
        resid = Y - X @ beta
        return float(np.var(resid))

    # Restricted (autoregression) and full (bivariate) residual variances.
    rss_y_only = _var_residual_var(y, [y])
    rss_y_full = _var_residual_var(y, [y, x])
    rss_x_only = _var_residual_var(x, [x])
    rss_x_full = _var_residual_var(x, [x, y])

    eps = 1e-12
    gc_x_to_y = float(np.log((rss_y_only + eps) / (rss_y_full + eps)))
    gc_y_to_x = float(np.log((rss_x_only + eps) / (rss_x_full + eps)))
    return {
        "metric": "granger_pair",
        "order": int(order),
        "gc_x_to_y": gc_x_to_y,
        "gc_y_to_x": gc_y_to_x,
    }
