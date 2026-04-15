# Image Smoke Report

- Generated at: 2026-03-04T18:07:57.299789+00:00
- Status: PASS

## DB Counts
| Metric | Value |
| --- | ---: |
| `recipe_images_total` | 46 |
| `recipes_with_primary_image` | 45 |
| `recipes_with_source_or_title_url` | 0 |

## Home Page Check
- GET / status: 200
- img src count: 54
- unique img src count: 45
- CSP: `default-src 'self'; img-src 'self' data: https:; style-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'`

### Top img src values
| Src | Count |
| --- | ---: |
| `/images/46` | 3 |
| `/images/45` | 2 |
| `/images/44` | 2 |
| `/images/43` | 2 |
| `/images/41` | 2 |

## Sample Recipe Checks
| Recipe ID | Title | Expected Kind | Expected Src | Detail Status | Result | Note |
| ---: | --- | --- | --- | ---: | --- | --- |
| 46 | LC Pending Recipe 331d7393 | placeholder | `-` | 200 | PASS | - |
| 45 | LC Pending Recipe b4d2ec5f | db | `/images/46` | 200 | PASS | - |
| 44 | LC Pending Recipe 66e437e1 | db | `/images/45` | 200 | PASS | - |
| 43 | LC Pending Recipe 4cbf2f08 | db | `/images/44` | 200 | PASS | - |
| 37 | BeaverTails | db | `/images/37` | 200 | PASS | - |

## Warnings
- none

## Failures
- none

