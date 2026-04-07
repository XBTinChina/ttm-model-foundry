# ttm-model-foundry

An agentic foundry that takes a single scientific theory and produces a
co-evolved bundle of:

- a (possibly revised) **theory**,
- a **computational model** that instantiates it,
- **predictions** the model entails, and
- **experimental designs** that could falsify those predictions,

— or, when no such bundle is reachable, a structured **intractability
report**. The full architecture, failure-mode taxonomy, and engineering rules
live in the design brief; this README is the entry point to the codebase.

---

## Table of contents

1. [What this repository is](#what-this-repository-is)
2. [Current build status](#current-build-status)
3. [Repository layout](#repository-layout)
4. [Installation](#installation)
5. [Running the tests](#running-the-tests)
6. [Core concepts](#core-concepts)
   - [Theory inputs and model specs](#theory-inputs-and-model-specs)
   - [Analyzers and linking functions](#analyzers-and-linking-functions)
   - [Primitives](#primitives)
   - [Skills (models and experiments)](#skills-models-and-experiments)
   - [Verdicts](#verdicts)
   - [Trivial-pass detectors](#trivial-pass-detectors)
7. [Validation pipeline](#validation-pipeline)
8. [Adding a skill entry](#adding-a-skill-entry)
9. [Adding an analyzer or linking function](#adding-an-analyzer-or-linking-function)
10. [Adding a primitive](#adding-a-primitive)
11. [Configuration](#configuration)
12. [Conventions and engineering rules](#conventions-and-engineering-rules)
13. [Roadmap](#roadmap)

---

## What this repository is

The foundry is structured as a small set of cooperating agents (Ontologist,
Programmer, Falsifier, Co-Reviser, Experimenter, Alignment Judge, Controller)
that talk to each other only through a fixed contract:

- **JSON Schema** documents pin down the shape of every artifact that crosses
  an agent boundary (`schemas/`).
- A **registry** of trusted, deterministic analyzers and linking functions
  pins down what an agent is allowed to invoke when it wants to extract a
  number from a simulation (`analyzers/`).
- A **primitives library** pins down the trusted executable building blocks
  the future Programmer agent is allowed to compose models from
  (`primitives/`).
- **Skill folders** are read-only knowledge bases that describe known model
  families and experimental paradigms in a uniform template (`skills/`).
- A small set of **verdicts** is the only legal vocabulary an agent can use
  to report a result back to the controller (`src/controller/verdicts.py`).

The point of all of this scaffolding is so that no agent can ever silently
"invent" a metric, a primitive, or a verdict that nothing else in the system
understands. Every reference is checked at construction time.

## Current build status

This commit lands **Steps 1–5** of the build order:

1. The data contracts (JSON Schemas).
2. The analyzer / linking-function registry.
3. The trivial-pass detectors.
4. The minimal skill folders (models + experiments) and their indices.
5. The primitives library.

There are **no agents and no LLM-calling code yet**. This slice is the
smallest object that proves the foundation is sound; the agents come in later
steps (see [Roadmap](#roadmap)).

## Repository layout

```
schemas/      # JSON Schema contracts (theory input, model spec)
analyzers/    # Deterministic analyzer registry + functions
primitives/   # Trusted executable library the future Programmer composes from
  linking/      # Observable-from-state functions (PLV, RT-from-phase, ...)
  oscillators/  # Kuramoto, Stuart-Landau, Wilson-Cowan, ...
skills/       # Read-only knowledge folders
  models/         # Model-family entries + SKILL.md index
  experiments/    # Experimental paradigm entries + SKILL.md index
src/          # Validators, IO helpers, controller plumbing
  controller/     # Verdicts (and, later, the state machine)
  io/             # Skill-folder loader
  validators/     # Layered schema + registry + LHS-coverage checks
configs/      # YAML stubs for later steps (loop caps, budgets, paths)
tests/        # pytest suite for everything in this slice
```

## Installation

The project targets Python ≥ 3.11 and uses a standard PEP 621 layout.

```bash
pip install -e .[dev]
```

Runtime dependencies are intentionally small: `numpy`, `scipy`, `jsonschema`,
and `pyyaml`. The `dev` extra adds `pytest`.

## Running the tests

```bash
pytest -v
```

All tests should pass on a fresh checkout. The suite covers:

| Test file | What it locks down |
|---|---|
| `tests/test_schemas.py` | JSON Schema validation of theory inputs and model specs, including the cross-field rules layered on top in `schema_checks.py`. |
| `tests/test_analyzer_registry.py` | Every analyzer and linking function is importable, callable, and reachable through `get_analyzer` / `get_linking_function`. |
| `tests/test_primitives.py` | Each primitive integrator runs end-to-end on a smoke input and produces finite output of the expected shape. |
| `tests/test_skill_coverage.py` | Parity gate: every primitive named in a model skill exists under `primitives/`, and every analyzer named in an experiment skill is registered. |
| `tests/test_trivial_pass.py` | The deterministic trivial-pass detectors flag the patterns they are supposed to and never raise. |
| `tests/test_verdicts.py` | The verdict enum's spelling, partitioning into inner/outer/terminal sets, and `VerdictMessage` carrier behavior. |

If `test_skill_coverage.py` fails, you have introduced a skill entry that
references something the registry or primitives library does not yet provide
— see [Adding a skill entry](#adding-a-skill-entry).

## Core concepts

### Theory inputs and model specs

Two JSON Schemas define every artifact that crosses an agent boundary:

- **`schemas/theory_input.schema.json`** — the input contract for a single
  scientific theory consumed by the foundry. Required fields: `theory_id`,
  `theory_name`, `parent_kernel_id`, `core_claim`, `mechanism`, `scope`,
  `main_assumptions`, `alternatives_ruled_out`,
  `distinctive_falsifiable_prediction`, `what_would_falsify_it`, `notes`.
  The two falsification fields are required and non-empty so that the
  Ontologist can convert them into the model's pre-registered falsification
  signatures.

- **`schemas/model_spec.schema.json`** — the model specification (M). Pins
  down `primary_state_variables`, `structural_parameters`,
  `equations_of_motion`, `linking_functions`, `falsification_signatures`,
  `target_phenomena`, and a `theory_anchor` that fingerprints the
  mechanistic claim with a sha256 hash so revisions can be compared against
  the original. At least one structural parameter must declare `sweep:
  true` (the §9 "mandatory parameter sweep" rule).

The JSON Schema layer expresses what it can. Two rules from the brief that
JSON Schema cannot express live in `src/validators/schema_checks.py`
instead:

1. Every `metric_function` and `function_id` referenced in M must exist in
   the analyzer / linking-function registries.
2. Every left-hand-side variable in `equations_of_motion` must appear in
   `primary_state_variables`.

`validate_theory_input` and `validate_model_spec` raise
`SchemaValidationError` on any failure of either layer.

### Analyzers and linking functions

`analyzers/registry.py` exposes two name → callable maps:

- `ANALYZERS` — deterministic metric functions a model can name from its
  `falsification_signatures.metric_function`. The current set covers
  spectral (`compute_band_power`, `compute_psd_peak`,
  `compute_peak_frequency`), phase (`compute_phase_locking_value`,
  `compute_inter_trial_coherence`, `compute_pairwise_phase_consistency`),
  coupling (`compute_phase_amplitude_coupling`,
  `compute_granger_causality_pair`), ERP
  (`compute_erp_component_amplitude`, `compute_erp_component_latency`), and
  behavioral (`compute_rt_distribution_stats`, `compute_accuracy_curve`,
  `compute_learning_trajectory`) analyses.

- `LINKING_FUNCTIONS` — observable-from-state functions a model can name
  from its `linking_functions.function_id`. Currently:
  `rt_from_phase_threshold` and `plv_from_oscillator_states`.

Use `get_analyzer(name)` / `get_linking_function(name)` to look one up
(KeyError on miss, with the missing name in the message), or
`list_analyzers()` / `list_linking_functions()` to enumerate.

### Primitives

The primitives library is the set of trusted executable building blocks the
future Programmer agent will compose simulations from. Today it contains:

- `primitives/oscillators/kuramoto.py` — globally coupled phase
  oscillators with sinusoidal coupling.
- `primitives/oscillators/stuart_landau.py` — normal form of a Hopf
  bifurcation, complex-amplitude with cubic nonlinearity.
- `primitives/oscillators/wilson_cowan.py` — excitatory–inhibitory
  population dynamics with sigmoidal firing-rate functions.
- `primitives/linking/plv_from_states.py` — phase-locking value computed
  from stored oscillator state.
- `primitives/linking/rt_from_phase.py` — reaction time computed from a
  phase-threshold crossing.

Each primitive is exercised by `tests/test_primitives.py` on a smoke input
so we know it integrates and returns finite, well-shaped output.

### Skills (models and experiments)

`skills/` is a read-only knowledge base in plain Markdown. The Ontologist
agent will read `skills/models/SKILL.md` first, then request the full body
of any entries it wants. Likewise the Experimenter reads
`skills/experiments/SKILL.md`.

Each entry follows the template defined in §11 of the build brief. Two
sections are machine-parsed by `src/io/skill_loader.py` and gated by
`tests/test_skill_coverage.py`:

- **Model entries** must include a `## Compatible primitives` section whose
  bullets are dotted module paths under `primitives/`.
- **Experiment entries** must include a `## Key dependent measures` section
  whose bullets are analyzer function names registered in
  `analyzers/registry.py`.

Other H2 sections (background, assumptions, references, …) are free-form
prose and ignored by the loader.

### Verdicts

`src/controller/verdicts.py` defines the `Verdict` enum, which is the only
legal vocabulary an agent can use to report a result. The enum values are
partitioned into three frozen sets:

- **Inner-loop verdicts** (from the Falsifier): `CONFORMS`,
  `IMPLEMENTATION_BUG`, `NUMERICAL_INSTABILITY`, `BEHAVIORAL_FAILURE`,
  `SPEC_FAILURE`, `THEORY_UNDERSPECIFIED`.
- **Outer-loop verdicts** (from the Alignment Judge): `ALIGNED`,
  `PREDICTION_NOT_DERIVABLE`, `EXPERIMENT_NONDIAGNOSTIC`,
  `EMPIRICAL_EQUIVALENCE`.
- **Terminal verdicts** (from the controller): `CONVERGED`,
  `CONVERGED_BUT_THEORY_SUBSTANTIALLY_REVISED`, `INTRACTABLE`,
  `BUDGET_EXHAUSTED`, `STAGNATED`.

A `VerdictMessage` dataclass carries a verdict together with its
`source_agent`, an arbitrary `payload`, and a timestamp. The state machine
(Step 6, future) routes solely on these values, so adding or renaming a
verdict is a contract change.

### Trivial-pass detectors

`analyzers/trivial_pass_patterns.py` ships deterministic detectors for
patterns that look like a successful falsification signature but are
actually trivial — a constant signal, a pure linear ramp, a spurious
correlation between independent white noise. They never raise; they return
`TrivialPassFlag` objects that the controller will attach to a run as
human-review hints. The brief's rule is "trigger a human-review flag
without blocking convergence".

## Validation pipeline

The end-to-end validation an artifact goes through today is:

1. **Pure JSON Schema** (`Draft202012Validator`) against
   `theory_input.schema.json` or `model_spec.schema.json`.
2. **`paradigm ∈ paradigm_choices_allowed`** (cannot be expressed in JSON
   Schema because it references a sibling array).
3. **Registry existence**: every `metric_function` in
   `falsification_signatures` must be in `ANALYZERS`; every `function_id`
   in `linking_functions` must be in `LINKING_FUNCTIONS`.
4. **Equation LHS coverage**: every left-hand-side variable in
   `equations_of_motion` (extracted from either the sympy form or the LaTeX
   form, with a fallback to the explicit `variable` field) must appear in
   `primary_state_variables`.
5. **Theory anchor format**: `claim_hash` is enforced as a 64-character
   lowercase hex string by the schema. The "no downgrade" check against a
   parent anchor lives in `src/validators/no_downgrade.py` and is
   future work for Step 10.

Any failure raises `SchemaValidationError` with a diagnostic listing every
offending JSON path.

## Adding a skill entry

1. Add the markdown under `skills/models/<category>/<name>.md` or
   `skills/experiments/<category>/<name>.md`. Follow the templates already in
   the folder.
2. If it is a **model** entry, the `## Compatible primitives` bullets must
   point to importable modules under `primitives/`. Add the implementation
   if it is missing (see [Adding a primitive](#adding-a-primitive)).
3. If it is an **experiment** entry, the `## Key dependent measures`
   bullets must name functions registered in `analyzers/registry.py`. Add
   the analyzer if it is missing
   (see [Adding an analyzer or linking function](#adding-an-analyzer-or-linking-function)).
4. Update `skills/<category>/SKILL.md` (the index table) so the Ontologist /
   Experimenter can find the new entry without scanning the filesystem.
5. Run `pytest tests/test_skill_coverage.py` — it is the parity gate.

## Adding an analyzer or linking function

1. Implement the function under `analyzers/<topic>.py` (for a metric) or
   `primitives/linking/<name>.py` (for an observable-from-state function).
2. Import it from `analyzers/registry.py` and add it to either `ANALYZERS`
   or `LINKING_FUNCTIONS`. The dictionary key is the public name agents
   will reference from a model spec — keep it stable.
3. Add coverage in `tests/test_analyzer_registry.py` (or the relevant
   primitive test) so the function is exercised on a smoke input.
4. Run the full suite. `test_skill_coverage.py` will tell you if any
   already-published skill entry pointed at this name and is now satisfied.

## Adding a primitive

1. Add the module under `primitives/<topic>/<name>.py`. Keep it pure (no
   I/O, no global state) and accept a small dataclass / dict of parameters
   so the Programmer can build it from a model spec.
2. Add a smoke test in `tests/test_primitives.py` that integrates the
   primitive on a tiny input and asserts the output is finite and the
   expected shape.
3. If a model skill entry is going to reference this primitive, add the
   dotted module path to that entry's `## Compatible primitives` bullets.

## Configuration

`configs/foundry.yaml` is a stub during the foundation build — no runtime
code reads it yet. Its keys mirror what the brief implies will be needed:

- **`caps`** — per-loop retry caps (inner loop implementation, stability,
  and behavioral retries; middle-loop revisions; outer-loop alignment
  retries; outer-loop empirical-equivalence back-flows). These come live
  with the inner loop in Step 9 and the outer loop in Step 11.
- **`budget`** — `max_total_tokens` and `max_total_calls` hard caps for the
  cost monitor (Section 9 of the brief). Live at Step 6.
- **`paths`** — `runs_dir`, `schemas_dir`, `skills_dir`, `primitives_dir`.
  The last three are already in use; `runs_dir` becomes live with the
  controller in Step 6.

Two further stub files (`configs/models.yaml`, `configs/repertoire.yaml`)
hold placeholder content that later steps will populate.

## Conventions and engineering rules

A few rules are worth being explicit about because the test suite enforces
them:

- **No silent invention.** Every metric function, linking function, and
  primitive that a model spec references must be reachable through the
  registry / filesystem at validation time. There is no "just-in-time"
  registration.
- **Schemas are the contract.** If you need to change the shape of a theory
  input or a model spec, edit the JSON Schema first, then the layered
  checks in `src/validators/schema_checks.py`, then the tests, then any
  callers. The schemas are the source of truth.
- **Verdicts are the contract too.** Adding, renaming, or repartitioning a
  verdict is a breaking change for the state machine and must be reflected
  in `tests/test_verdicts.py`.
- **Trivial-pass detectors never block.** They surface human-review flags
  and must never raise.
- **Skill markdown is read-only data.** Anything machine-actionable in a
  skill entry must be expressible as a bullet under a known H2 so the
  loader can pick it up.

## Roadmap

The build order in the design brief continues past the foundation slice:

- **Step 6** — controller state machine, run directories, cost monitoring.
- **Step 7–8** — Ontologist agent and the no-downgrade validator.
- **Step 9** — Programmer / Falsifier inner loop (with the retry caps that
  are currently stubbed in `configs/foundry.yaml`).
- **Step 10** — Co-Reviser (middle loop) and the parent-anchor
  no-downgrade enforcement.
- **Step 11** — Experimenter and Alignment Judge (outer loop), plus the
  richer agent-facing skill loader.

Each step is meant to land as a self-contained slice with its own tests.
This README should be updated as those steps land so a reader can still
understand the whole system from this file alone.
