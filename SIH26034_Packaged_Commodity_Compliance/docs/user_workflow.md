# User Workflow

## 1. Login
Officer or Admin logs in with username/password (session-based auth).

## 2. Dashboard
Landing page after login. Shows live totals (scanned, compliant,
non-compliant, needs-review), compliance %, average score, a status
breakdown pie chart, a common-violations bar chart, and a recent
inspections table — all computed from the database at request time.

## 3. Scan Product
The officer either:
- **Uploads** a JPG/PNG label image (choosing front/back/side), or
- **Runs a demo/synthetic product** (3 pre-generated label images
  covering: mostly compliant, missing declaration, readability issue)

Either path runs the same real OCR pipeline. The officer then reviews the
extracted declaration fields (product name, manufacturer, address, net
quantity, MRP, mfg date, consumer care, other) and can correct anything
OCR missed or misread.

## 4. Compliance Analysis
Clicking "Run Compliance Analysis" sends the (possibly edited) fields to
the rule engine, which returns PASS/FAIL/WARNING/MANUAL_VERIFICATION for
each mandatory declaration plus a readability check, a documented
compliance score, and an overall status. This is persisted to the
database and a PDF report is generated.

## 5. Inspection Report / Violation Details
The officer is taken to the inspection detail page: score, status badge,
scanned image, extracted declarations, and a detailed breakdown per rule
(explanation, evidence, legal reference, recommended action). A
"Download PDF Report" button produces a real, working PDF.

## 6. Inspection History
Searchable/filterable list of every past inspection (persists across
app restarts, since it's backed by SQLite). Each row links to its report.

## 7. User Management (Admin only)
Admins can create new Admin/Officer accounts and delete existing ones.

## 8. Settings / About
Account info and the system disclaimer (AI-assisted screening only, not
a final legal determination).
