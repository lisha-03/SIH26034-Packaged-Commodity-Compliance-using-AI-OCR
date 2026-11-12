import os
from flask import Blueprint, request, jsonify, send_file

from auth.auth import login_required
from database.db import get_connection
from config import IMAGES_DIR

bp = Blueprint("history_routes", __name__, url_prefix="/api")


@bp.route("/history", methods=["GET"])
@login_required
def inspection_history():
    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "").strip()

    query = """
        SELECT i.id as inspection_id, i.scanned_at, i.compliance_score, i.overall_status,
               i.is_demo, i.image_path, p.product_name, u.full_name as officer_name
        FROM inspections i
        JOIN products p ON p.id = i.product_id
        JOIN users u ON u.id = i.officer_id
        WHERE 1=1
    """
    params = []
    if search:
        query += " AND p.product_name LIKE ?"
        params.append(f"%{search}%")
    if status_filter:
        query += " AND i.overall_status = ?"
        params.append(status_filter)
    query += " ORDER BY i.scanned_at DESC"

    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify([dict(r) for r in rows])


@bp.route("/inspections/<int:inspection_id>", methods=["GET"])
@login_required
def inspection_detail(inspection_id):
    conn = get_connection()
    inspection = conn.execute(
        """SELECT i.*, p.product_name, u.full_name as officer_name
           FROM inspections i
           JOIN products p ON p.id = i.product_id
           JOIN users u ON u.id = i.officer_id
           WHERE i.id = ?""",
        (inspection_id,),
    ).fetchone()
    if inspection is None:
        conn.close()
        return jsonify({"error": "Inspection not found."}), 404

    declarations = conn.execute(
        "SELECT * FROM extracted_declarations WHERE inspection_id = ?", (inspection_id,)
    ).fetchone()
    violations = conn.execute(
        "SELECT * FROM violations WHERE inspection_id = ?", (inspection_id,)
    ).fetchall()
    report = conn.execute(
        "SELECT * FROM reports WHERE inspection_id = ?", (inspection_id,)
    ).fetchone()
    conn.close()

    return jsonify({
        "inspection": dict(inspection),
        "declarations": dict(declarations) if declarations else None,
        "violations": [dict(v) for v in violations],
        "report_available": report is not None,
    })


@bp.route("/inspections/<int:inspection_id>/report", methods=["GET"])
@login_required
def download_report(inspection_id):
    conn = get_connection()
    report = conn.execute(
        "SELECT * FROM reports WHERE inspection_id = ?", (inspection_id,)
    ).fetchone()
    conn.close()
    if report is None or not os.path.exists(report["pdf_path"]):
        return jsonify({"error": "Report not available for this inspection."}), 404
    return send_file(report["pdf_path"], as_attachment=True,
                      download_name=f"compliance_report_{inspection_id}.pdf")


@bp.route("/inspections/<int:inspection_id>/image", methods=["GET"])
@login_required
def get_inspection_image(inspection_id):
    conn = get_connection()
    row = conn.execute("SELECT image_path FROM inspections WHERE id = ?", (inspection_id,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Inspection not found."}), 404
    path = os.path.join(IMAGES_DIR, row["image_path"])
    if not os.path.exists(path):
        return jsonify({"error": "Image not found."}), 404
    return send_file(path)


@bp.route("/products/<int:product_id>", methods=["GET"])
@login_required
def product_details(product_id):
    conn = get_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if product is None:
        conn.close()
        return jsonify({"error": "Product not found."}), 404
    inspections = conn.execute(
        "SELECT * FROM inspections WHERE product_id = ? ORDER BY scanned_at DESC", (product_id,)
    ).fetchall()
    conn.close()
    return jsonify({
        "product": dict(product),
        "inspections": [dict(i) for i in inspections],
    })
