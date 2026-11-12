# API Documentation

Base URL (dev): `http://localhost:5000/api`
Auth: session cookie (set on login). All routes below except `/auth/login`
and `/health` require an active session (`401` returned otherwise).

## Auth

| Method | Path             | Body                              | Notes                         |
|--------|------------------|------------------------------------|---------------------------------|
| POST   | /auth/login       | `{username, password}`             | Sets session cookie             |
| POST   | /auth/logout      | —                                   | Clears session                  |
| GET    | /auth/me          | —                                   | Current user info               |

## Scan / OCR / Compliance

| Method | Path                     | Body / Params                                        | Notes |
|--------|---------------------------|--------------------------------------------------------|-------|
| POST   | /scan/upload               | multipart: `image` (file), `label` (front/back/side)  | Runs real OCR, returns extracted fields |
| POST   | /scan/demo/\<1\|2\|3\>      | —                                                       | Copies a demo label image and runs the same real OCR pipeline |
| GET    | /scan/demo-image/\<id\>     | —                                                       | Serves the raw demo image (for preview) |
| POST   | /scan/analyze               | `{image_filename, image_label, is_demo, ocr_raw_text, ocr_confidence, readability_status, declarations}` | Runs compliance engine, persists to DB, generates PDF |

## Dashboard

| Method | Path              | Notes |
|--------|--------------------|-------|
| GET    | /dashboard/stats    | Live counts, percentages, recent inspections, common violations, status breakdown — all computed from the DB at request time |

## History / Inspections / Products

| Method | Path                                   | Params                          |
|--------|------------------------------------------|-----------------------------------|
| GET    | /history                                  | `?search=&status=`                |
| GET    | /inspections/\<id\>                        | Full inspection + declarations + violations |
| GET    | /inspections/\<id\>/report                 | Downloads the PDF report          |
| GET    | /inspections/\<id\>/image                  | Serves the scanned image          |
| GET    | /products/\<id\>                           | Product + all its inspections     |

## Users (admin only)

| Method | Path             | Body                                                |
|--------|------------------|--------------------------------------------------------|
| GET    | /users            | —                                                        |
| POST   | /users            | `{username, password, full_name, role}`                 |
| DELETE | /users/\<id\>      | —                                                        |

## Error format

All errors return `{"error": "human-readable message"}` with an
appropriate HTTP status code (400/401/403/404/413/500).
