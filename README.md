# ttm-model-foundry

Agentic foundry that takes one scientific theory and produces a co-evolved
bundle of (revised theory, computational model, predictions, experimental
designs) — or a structured intractability report. See the design brief for
the full architecture, failure-mode taxonomy, and engineering rules.

## Status

This commit lands **Steps 1–5** of the build order: the contracts, the
analyzer registry, the trivial-pass detectors, the minimal skill folders, and
the primitives library. **No agents and no LLM-calling code yet.** This is the
smallest object that proves the foundation is sound; agents come in later
steps.

## Layout

```
schemas/      # JSON Schema contracts (theory input, model spec)
analyzers/    # Deterministic analyzer registry + functions
primitives/   # Trusted executable library the future Programmer composes from
skills/       # Read-only knowledge folders (models + experiments)
src/          # Validators, IO helpers, controller plumbing
configs/      # Stubs for later steps
tests/        # pytest suite for everything in this slice
```

## Setup

```bash
pip install -e .[dev]
pytest -v
```

All tests should pass on a fresh checkout.

## Adding a skill entry

1. Add the markdown under `skills/models/<category>/<name>.md` or
   `skills/experiments/<category>/<name>.md`. Follow the templates already in
   the folder.
2. If it is a model entry, the `## Compatible primitives` bullets must point
   to importable modules under `primitives/`. Add the implementation if it is
   missing.
3. If it is an experiment entry, the `## Key dependent measures` bullets must
   name functions registered in `analyzers/registry.py`. Add the analyzer if
   it is missing.
4. Update `skills/<category>/SKILL.md` (the index).
5. Run `pytest tests/test_skill_coverage.py` — it is the parity gate.
