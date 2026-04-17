# Testing Guide

This document defines the reproducible test entry points for MealMate.

## Baseline Environment
- Python `3.12`
- Dependencies installed via `requirements.txt`
- Local `.env` created from `.env.example`

## Full Test Suite
```bash
pytest -q
```

Expected baseline behavior:
- unit/integration tests run directly
- Playwright E2E tests are skipped if browser binaries are not installed

## Strict Warning Mode
```bash
pytest -q -W error
```

Use this mode to fail the run on warnings in the active baseline path.

## Browser E2E (Optional Local)
Install browser binaries:
```bash
python -m playwright install chromium
```

Run browser tests:
```bash
pytest -q tests/e2e
```

## Focused Runs
```bash
pytest -q tests/test_beta_aggressive_user_flow.py
pytest -q tests/test_beta_aggressive_admin_flow.py
```

## Notes
- CI runs `pytest -q -W error` as the baseline quality gate.
- If a test requires external tooling that is not installed (for example Playwright browsers), the test is expected to skip rather than fail.
