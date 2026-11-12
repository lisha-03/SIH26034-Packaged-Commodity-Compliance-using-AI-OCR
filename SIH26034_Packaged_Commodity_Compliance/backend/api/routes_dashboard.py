from flask import Blueprint, jsonify
from auth.auth import login_required
from database.db import get_connection

bp = Blueprint("dashboard_routes", __name__, url_prefix="/api/dashboard")


@bp.route("/stats", methods=["GET"])
@login_required
def stats():
    conn = get_connection()

    total = conn.execute("SELECT COUNT(*) c FROM inspections").fetchone()["c"]
    compliant = conn.execute(
        "SELECT COUNT(*) c FROM inspections WHERE overall_status = 'COMPLIANT'"
    ).fetchone()["c"]
    non_compliant = conn.execute(
        "SELECT COUNT(*) c FROM inspections WHERE overall_status = 'NON_COMPLIANT'"
    ).fetchone()["c"]
    needs_review = conn.execute(
        "SELECT COUNT(*) c FROM inspections WHERE overall_status = 'NEEDS_REVIEW'"
    ).fetchone()["c"]
    total_violations = conn.execute(
        "SELECT COUNT(*) c FROM violations WHERE result IN ('FAIL','WARNING')"
    ).fetchone()["c"]

    avg_score_row = conn.execute("SELECT AVG(compliance_score) a FROM inspections").fetchone()
    avg_score = round(avg_score_row["a"], 1) if avg_score_row["a"] is not None else 0

    recent = conn.execute(
        """SELECT i.id as inspection_id, i.scanned_at, i.compliance_score, i.overall_status,
                  p.product_name
           FROM inspections i JOIN products p ON p.id = i.product_id
           ORDER BY i.scanned_at DESC LIMIT 8"""
    ).fetchall()

    common_violations = conn.execute(
        """SELECT rule_title, COUNT(*) as count
           FROM violations
           WHERE result IN ('FAIL','WARNING')
           GROUP BY rule_title
           ORDER BY count DESC
           LIMIT 6"""
    ).fetchall()

    status_breakdown = conn.execute(
        """SELECT overall_status, COUNT(*) as count
           FROM inspections GROUP BY overall_status"""
    ).fetchall()

    conn.close()

    compliance_pct = round((compliant / total) * 100, 1) if total > 0 else 0

    return jsonify({
        "total_scanned": total,
        "compliant": compliant,
        "non_compliant": non_compliant,
        "needs_review": needs_review,
        "total_violations": total_violations,
        "compliance_percentage": compliance_pct,
        "average_score": avg_score,
        "recent_inspections": [dict(r) for r in recent],
        "common_violations": [dict(r) for r in common_violations],
        "status_breakdown": [dict(r) for r in status_breakdown],
    })
