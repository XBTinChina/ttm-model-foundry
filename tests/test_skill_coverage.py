"""Parity gate from \u00a711 of the build brief.

Two rules:
1. Every ``Compatible primitives`` reference in skills/models/ resolves to
   an importable Python module under primitives/.
2. Every ``Key dependent measures`` reference in skills/experiments/
   resolves to a name in analyzers/registry.ANALYZERS.

Adding a markdown skill entry without backing implementation must cause this
test to fail with a clear message.
"""

from __future__ import annotations

import importlib

import pytest

from analyzers.registry import ANALYZERS
from src.io.skill_loader import list_experiment_entries, list_model_entries


def test_at_least_three_model_entries():
    entries = list_model_entries()
    assert len(entries) >= 3, f"Expected \u22653 model skill entries, got {len(entries)}"


def test_at_least_three_experiment_entries():
    entries = list_experiment_entries()
    assert len(entries) >= 3, f"Expected \u22653 experiment skill entries, got {len(entries)}"


def test_every_model_entry_compatible_primitives_resolve():
    failures: list[str] = []
    for entry in list_model_entries():
        bullets = entry.bullets("Compatible primitives")
        if not bullets:
            failures.append(f"{entry.path}: no 'Compatible primitives' section")
            continue
        for dotted in bullets:
            try:
                importlib.import_module(dotted)
            except Exception as exc:  # noqa: BLE001
                failures.append(f"{entry.path}: cannot import {dotted!r}: {exc}")
    assert not failures, "Skill/primitives parity violations:\n  " + "\n  ".join(failures)


def test_every_experiment_entry_dependent_measures_resolve():
    failures: list[str] = []
    for entry in list_experiment_entries():
        bullets = entry.bullets("Key dependent measures")
        if not bullets:
            failures.append(f"{entry.path}: no 'Key dependent measures' section")
            continue
        for name in bullets:
            if name not in ANALYZERS:
                failures.append(
                    f"{entry.path}: dependent measure {name!r} not in analyzer registry"
                )
    assert not failures, "Skill/analyzer parity violations:\n  " + "\n  ".join(failures)


@pytest.mark.parametrize(
    "entry_path_substr",
    ["kuramoto", "stuart_landau", "wilson_cowan",
     "frequency_tagging", "synchronization_continuation", "two_alternative_forced_choice"],
)
def test_required_seed_entries_present(entry_path_substr):
    all_paths = [
        str(e.path) for e in list_model_entries() + list_experiment_entries()
    ]
    assert any(entry_path_substr in p for p in all_paths), (
        f"missing seed skill entry: {entry_path_substr}"
    )
