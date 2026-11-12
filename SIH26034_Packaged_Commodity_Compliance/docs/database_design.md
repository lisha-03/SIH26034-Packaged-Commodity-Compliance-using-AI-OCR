# Database Design

SQLite database file: `backend/compliance.db` (created automatically on
first run by `backend/database/db.py` / `backend/init_db.py`, from the
schema in `backend/database/schema.sql`).

## Tables

### `users`
Stores login accounts. Passwords are hashed with Werkzeug's
`generate_password_hash` (PBKDF2) — never stored in plain text.

| Column         | Type    | Notes                          |
|-----------------|---------|----------------------------------|
| id               | INTEGER | Primary key                      |
| username         | TEXT    | Unique                           |
| password_hash    | TEXT    | Hashed, never plain text         |
| full_name        | TEXT    |                                    |
| role             | TEXT    | `admin` or `officer`             |
| created_at       | TEXT    | Auto-set                          |

### `products`
One row per distinct product scan (a product can be re-scanned, creating
a new `inspections` row each time — history is per-inspection, not
per-product).

### `inspections`
The core record of a single scan event: which image, which officer, OCR
metadata, compliance score, and overall status.

### `extracted_declarations`
The structured fields extracted (and possibly officer-edited) for one
inspection — one-to-one with `inspections`.

### `violations`
One row per rule check result for an inspection (PASS/FAIL/WARNING/
MANUAL_VERIFICATION), including evidence, legal reference and
recommended action — one-to-many with `inspections`.

### `reports`
Tracks the generated PDF file path for an inspection — one-to-one.

## Entity relationship

```
users 1───* inspections *───1 products
                │
                ├──1───1── extracted_declarations
                ├──1───*── violations
                └──1───1── reports
```

## Why SQLite

Per the hackathon prototype requirements, SQLite was chosen for zero
external setup — the database file is created automatically on first run
and requires no separate server process. For a production deployment this
would be swapped for PostgreSQL, but the schema and access patterns
(plain SQL via `database/db.py`) were kept simple enough that the
migration path is straightforward.
