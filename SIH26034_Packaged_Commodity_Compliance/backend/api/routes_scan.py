import os
import shutil
import uuid

from flask import Blueprint, request, jsonify, session, send_file

from auth.auth import login_required
from config import IMAGES_DIR, DEMO_IMAGES_DIR
from utils.validators import allowed_file, validate_file_size
from ocr.ocr_engine import run_ocr, extract_declarations
from rules.compliance_engine import run_compliance_check
from rules.legal_reference import EXTRACTED_FIELDS
from reports.report_generator import generate_report
from database.db import get_connection

bp = Blueprint("scan_routes", __name__, url_prefix="/api/scan")


def _run_ocr_and_respond(saved_path: str, label: str, is_demo: bool):
    try:
        ocr_result = run_ocr(saved_path)
    except Exception as e:
        return jsonify({"error": f"OCR processing failed: {str(e)}"}), 500

    declarations = extract_declarations(ocr_result["raw_text"])

    return jsonify({
        "image_filename": os.path.basename(saved_path),
        "image_label": label,
        "is_demo": is_demo,
        "ocr_raw_text": ocr_result["raw_text"],
        "ocr_confidence": ocr_result["avg_confidence"],
        "readability_status": ocr_result["readability_status"],
        "word_count": ocr_result["word_count"],
        "declarations": declarations,
    })


@bp.route("/upload", methods=["POST"])
@login_required
def upload_and_ocr():
    if "image" not in request.files:
        return jsonify({"error": "No image file was provided."}), 400
    file = request.files["image"]
    label = request.form.get("label", "front")

    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type. Please upload a JPG or PNG image."}), 400
    if not validate_file_size(file):
        return jsonify({"error": "File is too large. Maximum size is 8 MB."}), 400

    ext = file.filename.rsplit(".", 1)[1].lower()
    saved_name = f"{uuid.uuid4().hex}.{ext}"
    saved_path = os.path.join(IMAGES_DIR, saved_name)

    try:
        file.save(saved_path)
    except Exception:
        return jsonify({"error": "Could not save the uploaded file. Please try again."}), 500

    return _run_ocr_and_respond(saved_path, label, is_demo=False)


@bp.route("/demo/<int:demo_id>", methods=["POST"])
@login_required
def scan_demo_product(demo_id):
    demo_filename = f"demo_product_{demo_id}.png"
    demo_path = os.path.join(DEMO_IMAGES_DIR, demo_filename)
    if not os.path.exists(demo_path):
        return jsonify({"error": "Demo product not found."}), 404

    saved_name = f"{uuid.uuid4().hex}.png"
    saved_path = os.path.join(IMAGES_DIR, saved_name)
    shutil.copyfile(demo_path, saved_path)

    return _run_ocr_and_respond(saved_path, "front", is_demo=True)


@bp.route("/demo-image/<int:demo_id>", methods=["GET"])
@login_required
def demo_image_preview(demo_id):
    demo_filename = f"demo_product_{demo_id}.png"
    demo_path = os.path.join(DEMO_IMAGES_DIR, demo_filename)
    if not os.path.exists(demo_path):
        return jsonify({"error": "Demo product not found."}), 404
    return send_file(demo_path)


@bp.route("/analyze", methods=["POST"])
@login_required
def analyze():
    """
    Accepts the (possibly officer-edited) declaration fields plus OCR
    metadata, runs the compliance rule engine, persists everything to the
    database, generates a PDF report, and returns the full inspection
    result.
    """
    data = request.get_json(silent=True) or {}

    image_filename = data.get("image_filename")
    if not image_filename:
        return jsonify({"error": "image_filename is required (upload or scan a demo product first)."}), 400
    image_path = os.path.join(IMAGES_DIR, image_filename)
    if not os.path.exists(image_path):
        return jsonify({"error": "Uploaded image could not be found on the server."}), 400

    declarations_in = data.get("declarations") or {}
    declarations = {f: (declarations_in.get(f) or "").strip() for f in EXTRACTED_FIELDS}
    ocr_confidence = float(data.get("ocr_confidence") or 0)
    readability_status = data.get("readability_status") or "MANUAL_VERIFICATION"
    ocr_raw_text = data.get("ocr_raw_text") or ""
    image_label = data.get("image_label") or "front"
    is_demo = 1 if data.get("is_demo") else 0

    try:
        results, score, status = run_compliance_check(declarations, ocr_confidence, readability_status)
    except Exception as e:
        return jsonify({"error": f"Compliance analysis failed: {str(e)}"}), 500

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO products (product_name, created_by) VALUES (?, ?)",
            (declarations.get("product_name") or "Unnamed Product", session["user_id"]),
        )
        product_id = cur.lastrowid

        cur.execute(
            """INSERT INTO inspections
               (product_id, officer_id, image_path, image_label, is_demo, ocr_raw_text,
                ocr_confidence, readability_status, compliance_score, overall_status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (product_id, session["user_id"], image_filename, image_label, is_demo, ocr_raw_text,
             ocr_confidence, readability_status, score, status),
        )
        inspection_id = cur.lastrowid

        cur.execute(
            """INSERT INTO extracted_declarations
               (inspection_id, product_name, manufacturer, address, net_quantity, mrp,
                mfg_date, consumer_care, other_declarations)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (inspection_id, declarations["product_name"], declarations["manufacturer"],
             declarations["address"], declarations["net_quantity"], declarations["mrp"],
             declarations["mfg_date"], declarations["consumer_care"], declarations["other_declarations"]),
        )

        for r in results:
            cur.execute(
                """INSERT INTO violations
                   (inspection_id, rule_key, rule_title, result, explanation, evidence,
                    legal_reference, recommended_action)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (inspection_id, r["rule_key"], r["rule_title"], r["result"], r["explanation"],
                 r["evidence"], r["legal_reference"], r["recommended_action"]),
            )

        conn.commit()

        # Generate the PDF report
        inspection_row = conn.execute(
            "SELECT * FROM inspections WHERE id = ?", (inspection_id,)
        ).fetchone()
        inspection_dict = dict(inspection_row)
        inspection_dict["product_name"] = declarations.get("product_name")

        try:
            pdf_path = generate_report(inspection_dict, declarations, results, image_path)
            cur.execute(
                "INSERT INTO reports (inspection_id, pdf_path) VALUES (?, ?)",
                (inspection_id, pdf_path),
            )
            conn.commit()
        except Exception as e:
            pdf_path = None
            # Report generation failure should not block the compliance result
            print(f"[WARN] PDF report generation failed for inspection {inspection_id}: {e}")

    finally:
        conn.close()

    return jsonify({
        "inspection_id": inspection_id,
        "product_id": product_id,
        "compliance_score": score,
        "overall_status": status,
        "results": results,
        "declarations": declarations,
        "pdf_available": pdf_path is not None,
    })
