# SIH26034 — Packaged Commodity Compliance using AI/OCR

An AI-assisted screening prototype that scans packaged-commodity label
images, runs real OCR (Tesseract), extracts mandatory declarations, checks
them against a documented Legal Metrology compliance rule engine, and
produces a compliance score, violation report, and a downloadable PDF —
with a full enforcement dashboard and inspection history.

> ⚠️ **This is an AI-assisted compliance screening tool, not a final legal
> authority.** All flagged issues must be verified by an authorized Legal
> Metrology enforcement officer. See `docs/limitations_future_scope.md`
> and the in-app Settings/About page for important sourcing notes about
> the legal reference used.

---

## 1. Project Overview

Built for Smart India Hackathon problem statement **SIH26034**. Officers
upload (or scan a demo) product label images; the system runs real OCR,
lets the officer review/correct the extracted fields, then runs a
transparent, documented rule engine to flag missing/non-compliant
mandatory declarations, score the product, and generate a PDF report —
all persisted in a searchable inspection history with a live dashboard.

## 2. Problem Statement

Packaged commodities sold in India must carry mandatory declarations
under the Legal Metrology Act, 2009 and the Legal Metrology (Packaged
Commodities) Rules, 2011 (manufacturer/packer/importer name & address,
net quantity, MRP, mfg/packing date, consumer care details, etc.). Manual
inspection of every product on every shelf is not scalable. This
prototype automates the first pass of that screening.

## 3. Features

- Session-based login with role-based access (Admin / Enforcement Officer)
- Real Tesseract OCR + OpenCV pre-processing (no fake/predefined output)
- Editable extracted-fields review step before compliance analysis
- Documented, non-arbitrary compliance rule engine and scoring formula
- PASS / FAIL / WARNING / MANUAL_VERIFICATION per mandatory declaration
- Real PDF compliance report generation (ReportLab)
- Live enforcement dashboard (charts + stats, computed from the DB — no
  hardcoded numbers)
- Persistent, searchable/filterable inspection history (SQLite)
- Admin user management
- 3 clearly-labelled demo/synthetic products for testing

## 4. Architecture

See `docs/architecture.md` for the full diagram. Summary:

```
frontend/  React + Vite + Tailwind + Recharts SPA
backend/   Flask REST API
  |-- auth/       session auth, password hashing
  |-- ocr/         Tesseract + OpenCV pipeline
  |-- rules/        compliance rule engine + legal reference data
  |-- reports/       PDF generation (ReportLab)
  |-- database/       SQLite schema + connection helper
  |-- api/             Flask blueprints (routes)
  `-- demo_data/        synthetic demo label images + generator script
```

## 5. Technology Stack

| Layer      | Technology |
|-------------|-------------|
| Frontend     | React 18, Vite, Tailwind CSS, Recharts, Axios |
| Backend       | Python 3, Flask, Flask-CORS |
| Database       | SQLite |
| OCR             | Tesseract (via pytesseract) + OpenCV + Pillow |
| Reports          | ReportLab (PDF) |
| Auth              | Werkzeug password hashing + Flask sessions |

All free/open-source. No paid APIs, no cloud services required.

## 6. Folder Structure

```
SIH26034_Packaged_Commodity_Compliance/
|-- README.md
|-- docs/
|   |-- architecture.md
|   |-- database_design.md
|   |-- ocr_workflow.md
|   |-- compliance_rule_engine.md
|   |-- api_documentation.md
|   |-- user_workflow.md
|   `-- limitations_future_scope.md
|-- backend/
|   |-- app.py                  <- main Flask entry point
|   |-- init_db.py               <- run once to create DB + demo users
|   |-- config.py
|   |-- requirements.txt
|   |-- auth/
|   |-- ocr/
|   |-- rules/
|   |-- reports/
|   |-- database/
|   |-- api/
|   |-- utils/
|   |-- demo_data/
|   |   |-- generate_demo_images.py
|   |   `-- images/               <- 3 generated demo labels
|   `-- uploads/                   <- created at runtime (images/, reports/)
`-- frontend/
    |-- package.json
    |-- vite.config.js
    |-- tailwind.config.js
    |-- index.html
    `-- src/
        |-- App.jsx, AuthContext.jsx, api.js, main.jsx
        |-- pages/     (Login, Dashboard, ScanProduct, InspectionDetail,
        |               InspectionHistory, UserManagement, Settings)
        `-- components/ (Layout, StatusBadge)
```

## 7. Installation & Setup

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** and npm
- **Tesseract OCR** installed on your system and available on PATH

Install Tesseract:
- **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
- **macOS (Homebrew)**: `brew install tesseract`
- **Windows**: Download the installer from
  https://github.com/UB-Mannheim/tesseract/wiki and add it to your PATH.

Verify: `tesseract --version`

## 8. Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate the 3 demo/synthetic label images
python demo_data/generate_demo_images.py

# Create the database and seed demo login accounts
python init_db.py
```

## 9. Frontend Setup

Open a **second terminal**:

```bash
cd frontend
npm install
```

## 10. Database Setup

Handled automatically by `python init_db.py` above — it creates
`backend/compliance.db` from `backend/database/schema.sql` and seeds two
demo accounts. Safe to re-run; it won't duplicate existing users.

## 11. OCR Setup

No extra setup beyond installing the Tesseract binary (step 7) and the
Python dependencies (step 8, which includes `pytesseract`). The app calls
the `tesseract` binary on your PATH automatically.

## 12. How to Run

**Terminal 1 — Backend** (from `backend/`, with venv activated):
```bash
python app.py
```
Runs at `http://localhost:5000`.

**Terminal 2 — Frontend** (from `frontend/`):
```bash
npm run dev
```
Runs at `http://localhost:5173` — open this URL in your browser. The
Vite dev server proxies `/api` calls to the Flask backend automatically.

## 13. Demo Login Credentials

| Role    | Username    | Password     |
|---------|-------------|--------------|
| Admin    | `admin`     | `admin123`   |
| Officer   | `officer1`   | `officer123`  |

(Created by `python init_db.py`. Change these before any real deployment.)

## 14. How to Test

1. Log in as `officer1`.
2. Go to **Scan Product**.
3. Click one of the 3 demo product buttons (no upload needed), **or**
   upload your own JPG/PNG label image.
4. Review the OCR-extracted fields (edit any that look wrong).
5. Click **Run Compliance Analysis**.
6. You'll land on the inspection report — check the score, status badge,
   and per-rule breakdown, then click **Download PDF Report**.
7. Go to **Inspection History** to see it listed and searchable.
8. Go to **Dashboard** to see the live stats update.
9. (Admin only) Go to **User Management** to add/remove accounts.

## 15. Sample Demo Products

Generated by `backend/demo_data/generate_demo_images.py` (clearly
labelled as synthetic, not an official SIH dataset):

| # | Product | Design | Expected Result |
|---|----------|---------|-------------------|
| 1 | Sunrise Premium Wheat Flour | All 5 mandatory declarations present, clean text | Mostly/fully PASS -> COMPLIANT |
| 2 | Golden Drop Mustard Oil | Mfg date & consumer care intentionally omitted | FAIL on those two -> NEEDS_REVIEW |
| 3 | Blue Ocean Instant Noodles | All fields present but rendered in tiny, blurred text | Low OCR confidence -> MANUAL_VERIFICATION / readability WARNING -> NEEDS_REVIEW |

## 16. Compliance Scoring

Fully documented (not arbitrary) in `docs/compliance_rule_engine.md` and
in the code comments at the top of `backend/rules/compliance_engine.py`.
Summary: start at 100, -18 per failed mandatory declaration, -8 per
warning, -6 for a readability issue; COMPLIANT requires score >= 85 **and**
no manual-verification items.

## 17. Limitations

See `docs/limitations_future_scope.md` — most importantly: the legal
reference file supplied with this project was a links/navigation page,
not the full statutory text, so the mandatory-declaration list should be
cross-checked against the current Rules text before real-world use.

## 18. Future Enhancements

See `docs/limitations_future_scope.md` for the full list (image-region
evidence highlighting, multi-image per-inspection merging, calibrated
font-size measurement, bulk scanning, editable DOCX export, etc.)

## 19. SIH Demonstration Flow (suggested)

1. Show the dashboard empty/fresh (or with a couple of prior demo scans).
2. Log in as an Enforcement Officer.
3. Scan **Demo Product 1** -> walk through OCR -> editable fields ->
   analysis -> COMPLIANT result -> download the PDF report live.
4. Scan **Demo Product 2** -> show it correctly flags the two missing
   declarations with evidence and legal reference -> NEEDS_REVIEW.
5. Scan **Demo Product 3** -> show the readability/low-confidence handling
   -> explain why the system says MANUAL_VERIFICATION instead of guessing.
6. Switch to the Dashboard -> show the numbers/charts update live from the
   database.
7. Show Inspection History -> search/filter.
8. (Optional) Log in as Admin -> show User Management.
9. Close with the disclaimer: AI-assisted screening, human officer makes
   the final call.
