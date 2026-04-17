# Release Checklist

Use this checklist before creating a release tag.

## Mandatory Gates
- [ ] `python -m compileall app tests` passes
- [ ] `pytest -q` passes
- [ ] `pytest -q -W error` passes
- [ ] `/healthz` returns `200 {"status":"ok"}`
- [ ] CI pipeline is green

## Documentation Gates
- [ ] `README.md` matches current runtime and entry path
- [ ] `CHANGELOG.md` contains target version entry
- [ ] Setup/testing/deployment docs are up to date
- [ ] Operability docs still match active log/contract paths
- [ ] Known limitations are documented

## Configuration and Repository Hygiene Gates
- [ ] `.env.example` includes all required runtime variables
- [ ] No local `.env` secrets are tracked
- [ ] No local DB/cache/temp/debug artifacts are tracked
- [ ] `.gitignore` covers local developer artifacts
- [ ] Root structure contains only intentional public entry files

## Manual Smoke Gates
- [ ] App boot path works from documented startup command
- [ ] Login path works
- [ ] Admin protection behaves as documented
- [ ] Critical conflict contract spot-check passes (e.g. translation batch double-start -> `409`)

## Release Decision
- [ ] Release candidate is accepted for tag cut (`vX.Y.Z`)
- [ ] Follow-up work is moved to backlog, not mixed into release cut
