# LAST CHANCE REPORT

- Generated at: 2026-03-04T18:07:58.637537+00:00
- Status: FAIL

## ENV Summary (keys only)
| Key | Value |
| --- | --- |
| `APP_ENV` | `dev` |
| `APP_NAME` | `MealMate` |
| `COOKIE_NAME` | `access_token` |
| `CSP_IMG_SRC` | `'self' data: https:` |
| `CSRF_COOKIE_NAME` | `csrf_token` |
| `CSRF_HEADER_NAME` | `X-CSRF-Token` |
| `DATABASE_SCHEME` | `sqlite` |
| `TRANSLATEAPI_ENABLED` | `0` |
| `TRANSLATE_AUTO_ON_PUBLISH` | `0` |
| `TRANSLATE_LAZY_ON_VIEW` | `1` |
| `TRANSLATE_TARGET_LANGS` | `en,fr` |
| `TRANSLATION_PROVIDER` | `translateapi` |

## DB Counts (before -> after)
| Metric | Before | After | Delta |
| --- | ---: | ---: | ---: |
| `recipe_image_change_requests` | 4 | 5 | 1 |
| `recipe_images` | 46 | 47 | 1 |
| `recipe_submissions` | 8 | 10 | 2 |
| `recipe_translations` | 6 | 6 | 0 |
| `recipes` | 46 | 47 | 1 |

## Header Checks
- home_csp: `default-src 'self'; img-src 'self' data: https:; style-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'`
- home_status: `200`
- login_set_cookie: `access_token="Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhOTg1NGQwNS03NmEzLTRlMzAtOWJkMi03ODA5ZmQzOTIxNDgiLCJyb2xlIjoidXNlciIsImV4cCI6MTc3MjY1MTI3N30.MFdeakH7OIYzRBkdgi2YlyQfRMocY2fjTOOa3DOmExs"; HttpOnly; Max-Age=86400; Path=/; SameSite=lax`

## Smoke Tool Status
- [PASS] translation_smoke: report=C:\Users\mickh\Desktop\Maschine\Schnittstellen und APIs\Abschluss Projekt\diagnostics\translation_smoke.md
- [PASS] image_smoke: report=C:\Users\mickh\Desktop\Maschine\Schnittstellen und APIs\Abschluss Projekt\diagnostics\image_smoke.md

## User Flow Steps
- [PASS] register: status=303
- [PASS] logout_after_register: status=303
- [PASS] login: status=303
- [PASS] set_username: status=303
- [PASS] change_password: status=303
- [PASS] logout_after_change_password: status=303
- [PASS] login_with_new_password: status=303
- [PASS] forgot_password_request: status=200
- [PASS] forgot_password_token_read: outbox=C:\Users\mickh\Desktop\Maschine\Schnittstellen und APIs\Abschluss Projekt\outbox\reset_links.txt
- [PASS] reset_password_submit: status=303
- [PASS] login_after_reset: status=303
- [PASS] submit_recipe: status=303
- [PASS] submission_visible_in_my_submissions: status=200
- [PASS] submission_not_in_discover: status=200
- [PASS] favorite_toggle: status=303
- [PASS] favorite_visible_in_favorites_page: status=200
- [PASS] review_submit: status=303
- [PASS] review_visible_in_detail: status=200
- [PASS] pdf_download: status=200
- [PASS] image_change_request_submit: status=303, before=4, after=5

## Admin Flow Steps
- [PASS] admin_login: status=303
- [PASS] approve_pending_submission: status=303
- [PASS] approved_recipe_visible_in_discover: recipe_id=47
- [PASS] reject_pending_submission: status=303
- [PASS] rejected_submission_state: submission_id=10
- [PASS] approve_image_change_request: status=303
- [PASS] image_change_request_state: request_id=5
- [PASS] recipe_has_primary_image_after_approve: recipe_id=46
- [FAIL] translation_sanity_for_approved_recipe: Missing translation rows for target langs: en, fr; Missing core language rows (de/en/fr check): de, en, fr

## Top Suspects
- Missing translation rows for target langs: en, fr
- Missing core language rows (de/en/fr check): de, en, fr

## Recommendations
- Likely translation root cause: provider/env trigger mismatch; check TRANSLATEAPI_ENABLED, target langs, and auto/batch run paths.

## Artifacts
- user_email: `last-chance-user-4a260c9ac7@example.local`
- user_submission_title: `LC Pending Recipe 83b351e3`
- approved_recipe_id: `47`
- pending_image_request_id: `5`

