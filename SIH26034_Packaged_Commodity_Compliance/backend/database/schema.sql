-- SIH26034 Packaged Commodity Compliance - Database Schema

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'officer')),
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT,
    created_by INTEGER,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS inspections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    officer_id INTEGER NOT NULL,
    image_path TEXT,
    image_label TEXT DEFAULT 'front',
    is_demo INTEGER DEFAULT 0,
    ocr_raw_text TEXT,
    ocr_confidence REAL,
    readability_status TEXT,
    compliance_score INTEGER,
    overall_status TEXT CHECK(overall_status IN ('COMPLIANT', 'NEEDS_REVIEW', 'NON_COMPLIANT')),
    scanned_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (officer_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS extracted_declarations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inspection_id INTEGER NOT NULL,
    product_name TEXT,
    manufacturer TEXT,
    address TEXT,
    net_quantity TEXT,
    mrp TEXT,
    mfg_date TEXT,
    consumer_care TEXT,
    other_declarations TEXT,
    FOREIGN KEY (inspection_id) REFERENCES inspections(id)
);

CREATE TABLE IF NOT EXISTS violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inspection_id INTEGER NOT NULL,
    rule_key TEXT NOT NULL,
    rule_title TEXT NOT NULL,
    result TEXT NOT NULL CHECK(result IN ('PASS', 'FAIL', 'WARNING', 'MANUAL_VERIFICATION')),
    explanation TEXT,
    evidence TEXT,
    legal_reference TEXT,
    recommended_action TEXT,
    FOREIGN KEY (inspection_id) REFERENCES inspections(id)
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inspection_id INTEGER NOT NULL UNIQUE,
    pdf_path TEXT,
    generated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (inspection_id) REFERENCES inspections(id)
);
