"""Schema validation for theory inputs and model specs.

Pure JSON Schema cannot express two of the rules from the build brief:

1. Every ``metric_function`` and ``function_id`` referenced in M must exist in
   the analyzer / linking-function registries (\u00a76).
2. Every left-hand-side variable in ``equations_of_motion`` must appear in
   ``primary_state_variables`` (\u00a76).

We layer those checks on top of jsonschema's draft 2020-12 validation here.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import Draft202012Validator

from analyzers.registry import ANALYZERS, LINKING_FUNCTIONS

_SCHEMAS_DIR = Path(__file__).resolve().parents[2] / "schemas"


class SchemaValidationError(ValueError):
    """Raised on any failure of the layered validators."""


def _load_schema(name: str) -> dict:
    return json.loads((_SCHEMAS_DIR / name).read_text())


_THEORY_SCHEMA = _load_schema("theory_input.schema.json")
_MODEL_SCHEMA = _load_schema("model_spec.schema.json")
_THEORY_VALIDATOR = Draft202012Validator(_THEORY_SCHEMA)
_MODEL_VALIDATOR = Draft202012Validator(_MODEL_SCHEMA)


def validate_theory_input(obj: Any) -> None:
    """Validate a candidate theory input. Raises SchemaValidationError on failure."""
    errors = sorted(_THEORY_VALIDATOR.iter_errors(obj), key=lambda e: list(e.path))
    if errors:
        msgs = "; ".join(f"{list(e.path)}: {e.message}" for e in errors)
        raise SchemaValidationError(f"theory_input invalid: {msgs}")


# Match the LHS variable name in either of the two equation forms.
# Sympy form looks like: "Derivative(phi_1, t) - omega_1 - K*sin(...)"
# LaTeX form looks like: "\\frac{d\\phi_1}{dt} = omega_1 + ..."
_SYMPY_LHS = re.compile(r"Derivative\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*,")
_LATEX_LHS = re.compile(r"\\frac\s*\{\s*d\s*\\?([A-Za-z_][A-Za-z0-9_]*)\s*\}\s*\{\s*dt")


def _equation_lhs(eq: dict) -> str | None:
    """Extract the LHS variable from a single equation entry.

    Falls back to ``eq['variable']`` if pattern matches fail. Returns None
    only if nothing recognizable is present.
    """
    sympy_form = eq.get("form_sympy", "") or ""
    latex_form = eq.get("form_latex", "") or ""
    m = _SYMPY_LHS.search(sympy_form)
    if m:
        return m.group(1)
    m = _LATEX_LHS.search(latex_form)
    if m:
        return m.group(1)
    return eq.get("variable") or None


def validate_model_spec(
    obj: Any,
    analyzers: dict[str, Any] | None = None,
    linking_functions: dict[str, Any] | None = None,
) -> None:
    """Validate a candidate model spec.

    Parameters
    ----------
    analyzers, linking_functions:
        Optional registry overrides for testing. Default to the live
        registries imported above.
    """
    analyzers = analyzers if analyzers is not None else ANALYZERS
    linking_functions = (
        linking_functions if linking_functions is not None else LINKING_FUNCTIONS
    )

    # 1. Pure JSON Schema validation.
    errors = sorted(_MODEL_VALIDATOR.iter_errors(obj), key=lambda e: list(e.path))
    if errors:
        msgs = "; ".join(f"{list(e.path)}: {e.message}" for e in errors)
        raise SchemaValidationError(f"model_spec invalid: {msgs}")

    # 2. paradigm \u2208 paradigm_choices_allowed.
    if obj["paradigm"] not in obj["paradigm_choices_allowed"]:
        raise SchemaValidationError(
            f"paradigm {obj['paradigm']!r} not in paradigm_choices_allowed"
        )

    # 3. Every metric_function exists in the analyzer registry.
    missing_metrics = [
        sig["metric_function"]
        for sig in obj["falsification_signatures"]
        if sig["metric_function"] not in analyzers
    ]
    if missing_metrics:
        raise SchemaValidationError(
            f"unknown metric_function(s) in falsification_signatures: {missing_metrics}"
        )

    # 4. Every linking function_id exists in the linking-function registry.
    missing_links = [
        lf["function_id"]
        for lf in obj["linking_functions"]
        if lf["function_id"] not in linking_functions
    ]
    if missing_links:
        raise SchemaValidationError(
            f"unknown function_id(s) in linking_functions: {missing_links}"
        )

    # 5. Every equation LHS appears in primary_state_variables.
    declared_states = {sv["name"] for sv in obj["primary_state_variables"]}
    derived_states: set[str] = set()
    for eq in obj["equations_of_motion"]:
        lhs = _equation_lhs(eq)
        if lhs is None:
            raise SchemaValidationError(
                f"could not infer LHS variable from equation: {eq}"
            )
        derived_states.add(lhs)
    missing_states = derived_states - declared_states
    if missing_states:
        raise SchemaValidationError(
            "equation LHS variables not declared in primary_state_variables: "
            f"{sorted(missing_states)}"
        )

    # 6. theory_anchor.claim_hash format is enforced by the schema (regex);
    #    No-Downgrade enforcement against a parent anchor lives in
    #    src/validators/no_downgrade.py (Step 10, future).


def reload_schemas() -> None:
    """Test helper: reload schemas from disk after editing them."""
    global _THEORY_SCHEMA, _MODEL_SCHEMA, _THEORY_VALIDATOR, _MODEL_VALIDATOR
    _THEORY_SCHEMA = _load_schema("theory_input.schema.json")
    _MODEL_SCHEMA = _load_schema("model_spec.schema.json")
    _THEORY_VALIDATOR = Draft202012Validator(_THEORY_SCHEMA)
    _MODEL_VALIDATOR = Draft202012Validator(_MODEL_SCHEMA)
