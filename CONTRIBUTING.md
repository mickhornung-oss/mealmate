# Contributing

## Development Baseline
1. Use Python 3.12.
2. Create a fresh virtual environment.
3. Install dependencies with `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env`.

Detailed setup: `docs/development/SETUP.md`

## Before Opening a Pull Request
1. Run tests:
   - `pytest -q`
   - `pytest -q -W error`
2. Run syntax compilation baseline:
   - `python -m compileall app tests`
3. Ensure no local artifacts are committed:
   - virtual environments
   - database files
   - cache folders
   - diagnostic output files

## Scope Expectations
- Keep changes focused and reviewable.
- Prefer small, coherent commits.
- Avoid unrelated refactors in the same PR.
