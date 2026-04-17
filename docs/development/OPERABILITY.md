# Operability Guide

This guide documents where to look when mutation, conflict, or runtime failure paths trigger in MealMate.

## 1) Correlation and request tracing
- Every request gets an `X-Request-ID` header.
- The same value is written to request logs as `request_id=...`.
- For conflict or failure triage, start with the request id and then filter app logs by that id.

## 2) High-signal log events

### Translation batch operations
- Logger: `mealmate.translation.batch` and `mealmate.translations`
- Events:
  - `translation_batch_started`
  - `translation_batch_start_conflict`
  - `translation_batch_start_blocked`
  - `translation_batch_job_created`

Typical diagnosis:
1. If batch start returns `409`, look for `translation_batch_start_conflict`.
2. Confirm active job id/status via `translation_batch_start_blocked`.
3. Verify whether a previous job is still `queued`/`running`.

### Submission moderation transitions
- Logger: `mealmate.submissions`
- Events:
  - `submission_approve_claimed`
  - `submission_approve_publish_conflict`
  - `submission_approve_completed`
  - `submission_reject_claimed`
  - `submission_reject_noop`
  - `submission_reject_replay`
  - `submission_reject_completed`

Typical diagnosis:
1. Repeated approve/reject requests should not create duplicate side effects.
2. `submission_reject_replay` means idempotent no-op handling was used.
3. `submission_approve_publish_conflict` indicates publish race/already-published conflict.

### Image-change moderation transitions
- Logger: `mealmate.admin`
- Events:
  - `image_change_transition_claimed`
  - `image_change_transition_conflict`
  - `image_change_approve_completed`
  - `image_change_reject_completed`

Typical diagnosis:
1. `image_change_transition_conflict` means the request was not in `pending` state at mutation time.
2. For duplicate moderator actions, one request should complete, later retries should conflict (`409`).

## 3) Conflict contract reference

| Use case | Expected status | Meaning |
|---|---:|---|
| Start translation batch while another job is active | `409` | Existing non-terminal batch already running |
| Approve image-change request not pending | `409` | Request already handled or stale |
| Approve submission already published | `409` | Already transitioned/published |
| Reject submission replay on already rejected item | `303` redirect | Intentional idempotent no-op |

## 4) Runtime health and baseline checks
- Health endpoints:
  - `/health`
  - `/healthz`
- Baseline commands:
```bash
python -m compileall app tests
pytest -q
pytest -q -W error
```

## 5) Incident triage quick path
1. Capture `X-Request-ID` from response.
2. Find corresponding `request_complete`/`request_failed` log lines.
3. Filter for the subsystem logger (`mealmate.translations`, `mealmate.submissions`, `mealmate.admin`).
4. Match event name to conflict contract table above.
5. Verify current persisted state in admin pages or DB query before retrying mutation operations.
