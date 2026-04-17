# Release Governance

This document defines how MealMate releases are planned, validated, and cut.

## 1) Versioning Policy
MealMate follows **Semantic Versioning**.

- `MAJOR`: incompatible public contract change
- `MINOR`: backward-compatible feature addition
- `PATCH`: backward-compatible fix/hardening

Current stable baseline: `v1.0.0`.

## 2) What Counts as a Release
A release is a controlled repository state that:
- passes all mandatory quality gates
- has synchronized code, tests, and public documentation
- has a changelog entry for the target version
- is ready to be tagged and published without follow-up fixes

## 3) Release Process (Mandatory)
1. Freeze scope (no new feature work in release cut).
2. Run quality gates from `docs/development/RELEASE_CHECKLIST.md`.
3. Update `CHANGELOG.md` for target version.
4. Verify README and deployment docs match the real runtime behavior.
5. Confirm no local/debug artifacts are present in tracked files.
6. Confirm CI baseline is green.
7. Cut release commit and create version tag (`vX.Y.Z`).

## 4) Rules for Future Releases
- No release without explicit changelog entry.
- No release with failing strict-warning test baseline.
- No release with undocumented required environment changes.
- No release with unresolved contract drift between router behavior and tests.
- Post-release fixes must be delivered as a patch release.

## 5) Operational Baseline per Release
Each release must preserve:
- `/healthz` contract (`200 {"status":"ok"}`)
- request-id correlation (`X-Request-ID`)
- documented conflict/error contracts in operability docs
- reproducible local setup path from `docs/development/SETUP.md`
