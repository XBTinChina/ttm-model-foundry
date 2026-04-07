"""Name \u2192 callable lookup for analyzers and linking functions.

Every ``metric_function`` and ``function_id`` referenced from a model spec
(``schemas/model_spec.schema.json``) must be a key in one of these registries.
The schema validator (``src/validators/schema_checks.py``) enforces existence
at M-creation time, so the Behavioral Analyzer can rely on
``ANALYZERS[name]`` succeeding.
"""

from __future__ import annotations

from typing import Callable

from analyzers.behavioral import (
    compute_accuracy_curve,
    compute_learning_trajectory,
    compute_rt_distribution_stats,
)
from analyzers.coupling import (
    compute_granger_causality_pair,
    compute_phase_amplitude_coupling,
)
from analyzers.erp import (
    compute_erp_component_amplitude,
    compute_erp_component_latency,
)
from analyzers.phase import (
    compute_inter_trial_coherence,
    compute_pairwise_phase_consistency,
    compute_phase_locking_value,
)
from analyzers.spectral import (
    compute_band_power,
    compute_peak_frequency,
    compute_psd_peak,
)
from primitives.linking.plv_from_states import plv_from_oscillator_states
from primitives.linking.rt_from_phase import rt_from_phase_threshold

ANALYZERS: dict[str, Callable] = {
    "compute_band_power": compute_band_power,
    "compute_psd_peak": compute_psd_peak,
    "compute_peak_frequency": compute_peak_frequency,
    "compute_phase_locking_value": compute_phase_locking_value,
    "compute_inter_trial_coherence": compute_inter_trial_coherence,
    "compute_pairwise_phase_consistency": compute_pairwise_phase_consistency,
    "compute_phase_amplitude_coupling": compute_phase_amplitude_coupling,
    "compute_granger_causality_pair": compute_granger_causality_pair,
    "compute_erp_component_amplitude": compute_erp_component_amplitude,
    "compute_erp_component_latency": compute_erp_component_latency,
    "compute_rt_distribution_stats": compute_rt_distribution_stats,
    "compute_accuracy_curve": compute_accuracy_curve,
    "compute_learning_trajectory": compute_learning_trajectory,
}


LINKING_FUNCTIONS: dict[str, Callable] = {
    "rt_from_phase_threshold": rt_from_phase_threshold,
    "plv_from_oscillator_states": plv_from_oscillator_states,
}


def get_analyzer(name: str) -> Callable:
    """Return an analyzer by name. Raises KeyError including the missing name."""
    try:
        return ANALYZERS[name]
    except KeyError as exc:
        raise KeyError(f"Unknown analyzer: {name!r}") from exc


def get_linking_function(name: str) -> Callable:
    """Return a linking function by name. Raises KeyError including the missing name."""
    try:
        return LINKING_FUNCTIONS[name]
    except KeyError as exc:
        raise KeyError(f"Unknown linking function: {name!r}") from exc


def list_analyzers() -> list[str]:
    return sorted(ANALYZERS.keys())


def list_linking_functions() -> list[str]:
    return sorted(LINKING_FUNCTIONS.keys())
