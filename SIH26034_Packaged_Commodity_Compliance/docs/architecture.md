# System Architecture

## Overview

The prototype is a classic three-tier web application:

```
┌─────────────────────┐        HTTP/JSON (session cookie)       ┌─────────────────────┐
│   React + Vite SPA  │  <----------------------------------->  │   Flask REST API     │
│   (frontend/)        │                                         │   (backend/)          │
└─────────────────────┘                                         └──────────┬───────────┘
                                                                              │
                                                    ┌─────────────────────────┼─────────────────────────┐
                                                    │                         │                         │
                                             ┌──────▼──────┐          ┌───────▼───────┐         ┌───────▼───────┐
                                             │  ocr/        │          │  rules/        │         │  reports/      │
                                             │  Tesseract    │          │  Compliance     │         │  ReportLab PDF │
                                             │  + OpenCV     │          │  rule engine    │         │  generator     │
                                             └──────────────┘          └───────────────┘         └───────────────┘
                                                                              │
                                                                       ┌──────▼───────┐
                                                                       │  SQLite DB    │
                                                                       │ compliance.db │
                                                                       └──────────────┘
```

## Request flow (a single scan)

1. **Frontend** — officer uploads an image (or picks a demo product) on the
   Scan Product page.
2. `POST /api/scan/upload` (or `/api/scan/demo/<id>`) saves the image to
   `backend/uploads/images/` and runs it through `ocr/ocr_engine.py`
   (Tesseract + OpenCV pre-processing), then `extract_declarations()`
   parses the raw OCR text into structured fields with regex/keyword
   heuristics.
3. The officer reviews/edits the extracted fields in the browser.
4. `POST /api/scan/analyze` sends the (possibly edited) fields back to the
   server. `rules/compliance_engine.py` runs each field through the rule
   engine (`rules/legal_reference.py`) and returns PASS / FAIL / WARNING /
   MANUAL_VERIFICATION per requirement, plus a documented compliance score.
5. The result is persisted across 4 tables (`products`, `inspections`,
   `extracted_declarations`, `violations`) and a PDF is generated via
   `reports/report_generator.py` and stored in `uploads/reports/`, tracked
   in the `reports` table.
6. The frontend redirects to `/inspections/:id`, which reads back the full
   result from the database (not from in-memory state), proving
   persistence.

## Modular separation

| Concern              | Location                        |
|-----------------------|----------------------------------|
| Authentication         | `backend/auth/`                 |
| OCR                     | `backend/ocr/`                  |
| Rule engine & legal ref | `backend/rules/`                |
| PDF reports             | `backend/reports/`              |
| Database access         | `backend/database/`             |
| REST API routes         | `backend/api/`                  |
| UI                       | `frontend/src/`                 |

This separation means, for example, the OCR engine could be swapped for a
cloud OCR provider by only editing `ocr/ocr_engine.py` — nothing else in
the system depends on Tesseract specifically.
