"""Tests for the layered schema validators."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from src.validators.schema_checks import (
    SchemaValidationError,
    validate_model_spec,
    validate_theory_input,
)

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def theory():
    return json.loads((FIXTURES / "minimal_theory.json").read_text())


@pytest.fixture
def model_spec():
    return json.loads((FIXTURES / "minimal_model_spec.json").read_text())


# --- Theory input ---------------------------------------------------------


def test_valid_theory_passes(theory):
    validate_theory_input(theory)  # no raise


THEORY_REQUIRED_FIELDS = [
    "theory_id",
    "theory_name",
    "parent_kernel_id",
    "core_claim",
    "mechanism",
    "scope",
    "main_assumptions",
    "alternatives_ruled_out",
    "distinctive_falsifiable_prediction",
    "what_would_falsify_it",
    "notes",
]


@pytest.mark.parametrize("field", THEORY_REQUIRED_FIELDS)
def test_missing_theory_field_fails(theory, field):
    bad = copy.deepcopy(theory)
    del bad[field]
    with pytest.raises(SchemaValidationError):
        validate_theory_input(bad)


def test_empty_distinctive_prediction_fails(theory):
    bad = copy.deepcopy(theory)
    bad["distinctive_falsifiable_prediction"] = ""
    with pytest.raises(SchemaValidationError):
        validate_theory_input(bad)


def test_empty_what_would_falsify_it_fails(theory):
    bad = copy.deepcopy(theory)
    bad["what_would_falsify_it"] = ""
    with pytest.raises(SchemaValidationError):
        validate_theory_input(bad)


# --- Model spec -----------------------------------------------------------


def test_valid_model_spec_passes(model_spec):
    validate_model_spec(model_spec)  # no raise


def test_unknown_metric_function_fails(model_spec):
    bad = copy.deepcopy(model_spec)
    bad["falsification_signatures"][0]["metric_function"] = "compute_nonexistent_thing"
    with pytest.raises(SchemaValidationError, match="metric_function"):
        validate_model_spec(bad)


def test_unknown_linking_function_fails(model_spec):
    bad = copy.deepcopy(model_spec)
    bad["linking_functions"][0]["function_id"] = "totally_made_up"
    with pytest.raises(SchemaValidationError, match="function_id"):
        validate_model_spec(bad)


def test_no_swept_parameter_fails(model_spec):
    bad = copy.deepcopy(model_spec)
    for p in bad["structural_parameters"]:
        p["sweep"] = False
    with pytest.raises(SchemaValidationError):
        validate_model_spec(bad)


def test_paradigm_not_in_allowed_list_fails(model_spec):
    bad = copy.deepcopy(model_spec)
    bad["paradigm"] = "spiking_network"  # not in allowed list of fixture
    with pytest.raises(SchemaValidationError, match="paradigm"):
        validate_model_spec(bad)


def test_equation_lhs_missing_from_state_variables_fails(model_spec):
    bad = copy.deepcopy(model_spec)
    bad["primary_state_variables"] = [
        v for v in bad["primary_state_variables"] if v["name"] != "phi_2"
    ]
    with pytest.raises(SchemaValidationError, match="phi_2"):
        validate_model_spec(bad)


def test_bad_claim_hash_fails(model_spec):
    bad = copy.deepcopy(model_spec)
    bad["theory_anchor"]["claim_hash"] = "not-a-hash"
    with pytest.raises(SchemaValidationError):
        validate_model_spec(bad)
