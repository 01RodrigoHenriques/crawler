# Contributing

This repository is kept intentionally small and readable. Changes should improve maintainability,
testability, or operational clarity without expanding scope unnecessarily.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Quality checks

Run these before opening a pull request:

```bash
python -m main --help
python -m ruff format .
python -m ruff check .
python -m mypy .
pytest -q --cov=. --cov-report=term-missing --cov-fail-under=50
```

## Code changes

Keep edits focused and small. Prefer fixing root causes over layering new behavior on top of current issues.

- Preserve existing CLI behavior unless a change is required for packaging or testability.
- Add regression tests for bug fixes and integration tests for workflow-level behavior.
- Avoid mixing formatting-only changes with logic changes when that makes review harder.

## Test expectations

- Unit tests belong in `tests/unit/`.
- Integration tests belong under `tests/integration/` and should use local fixtures or ephemeral services.
- Do not rely on external network access in CI.

## Pull requests

Describe what changed, why it changed, and how it was validated. Include any compatibility impact if the CLI or output layout changes.
