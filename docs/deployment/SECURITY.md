# Security Verification Checklist

Use this checklist for manual verification of security-critical behavior.

## 1) Login Rate Limit
1. Send 6 POST requests to `/login` within one minute.
2. Expect first 5 requests to be processed normally.
3. Expect request 6 to return `429 Too Many Requests`.

## 2) Registration Rate Limit
1. Send 4 POST requests to `/register` within one minute.
2. Expect rate limiting after request 3.

## 3) CSRF Protection (Missing Token)
1. Trigger a protected POST endpoint without CSRF token.
2. Example: `POST /logout`.
3. Expect `403`.

## 4) CSRF Protection (Valid Token)
1. Load a page to receive `csrf_token` cookie.
2. Send POST with matching `X-CSRF-Token` header or form field.
3. Expect normal success/redirect flow.

## 5) Security Headers
Check response headers on `/` and verify:
- `Content-Security-Policy`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- `Strict-Transport-Security` in production HTTPS traffic

## 6) Upload Validation
1. Upload file with blocked MIME type -> expect failure.
2. Upload file exceeding `MAX_UPLOAD_MB` -> expect failure.
3. Upload file with mismatched magic bytes -> expect failure.

## 7) CSV Upload Validation (Admin)
1. Upload oversized CSV (`MAX_CSV_UPLOAD_MB`) -> expect rejection.
2. Upload non-CSV file via CSV endpoint -> expect rejection.

## 8) Trusted Hosts
1. Configure explicit `ALLOWED_HOSTS`.
2. Send request with invalid `Host` header.
3. Expect host validation failure.

## 9) Request ID
1. Request `/`.
2. Verify response includes `X-Request-ID`.
3. Verify the same request id appears in logs.
