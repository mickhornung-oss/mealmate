# Changelog

All notable changes to this project are documented in this file.

The format is based on Keep a Changelog and follows Semantic Versioning.

## [v1.0.0] - 2026-04-17

### Added
- Established a professional public repository baseline with consolidated root structure and documentation architecture.
- Added reproducible setup, testing, deployment, operability, and security documentation under `docs/`.
- Added a stable CI baseline with warning-strict test coverage (`pytest -q -W error`).
- Added targeted contract/regression tests for write paths, read/query/render paths, API/error behavior, auth/permission checks, and state/conflict/idempotency boundaries.
- Added a dedicated release-readiness contract test suite for environment and operability documentation guarantees.

### Changed
- Consolidated product identity to `MealMate` across core code paths and public-facing documentation.
- Refined large legacy service/router areas into clearer domain/service boundaries while preserving external behavior.
- Standardized conflict, failure, and access-denied behavior in critical router use cases without changing success-path semantics.
- Hardened observability in critical mutation/conflict hotspots with structured operational logging and request-id correlation.
- Consolidated environment/runtime expectations in `.env.example` and aligned setup/run/deployment docs with the validated baseline.

### Fixed
- Removed multiple historical contract inconsistencies around conflict handling, replay/idempotency behavior, and permission/error edges.
- Eliminated avoidable baseline warnings and stabilized strict warning mode (`-W error`).
- Closed documentation drift between code, CI/test gates, and operational diagnostics.

### Internal
- Completed the full hardening and release-preparation audit sequence (`docs/audit/00` through `docs/audit/15`).
- Promoted `services.py` into a compatibility/entry layer and moved domain-heavy logic into focused modules.
- Added internal handover documentation for each hardening block to keep future maintenance decisions traceable.
