"""
Generates a real, working PDF compliance report using ReportLab.
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from rules.legal_reference import DISCLAIMER

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

STATUS_COLORS = {
    "COMPLIANT": colors.HexColor("#16a34a"),
    "NEEDS_REVIEW": colors.HexColor("#ca8a04"),
    "NON_COMPLIANT": colors.HexColor("#dc2626"),
}
RESULT_COLORS = {
    "PASS": colors.HexColor("#16a34a"),
    "FAIL": colors.HexColor("#dc2626"),
    "WARNING": colors.HexColor("#ca8a04"),
    "MANUAL_VERIFICATION": colors.HexColor("#2563eb"),
}


def generate_report(inspection: dict, declarations: dict, violations: list, image_path: str = None) -> str:
    """
    inspection: dict with keys product_name, id, scanned_at, compliance_score,
                overall_status, ocr_confidence
    declarations: dict of extracted fields
    violations: list of rule result dicts
    image_path: absolute path to the scanned image (optional)

    Returns: absolute path to the generated PDF file.
    """
    filename = f"report_inspection_{inspection['id']}.pdf"
    out_path = os.path.join(REPORTS_DIR, filename)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCustom", parent=styles["Title"], fontSize=18, spaceAfter=6)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], spaceBefore=10, spaceAfter=6)
    normal = styles["Normal"]
    small = ParagraphStyle("Small", parent=styles["Normal"], fontSize=8, textColor=colors.grey)

    doc = SimpleDocTemplate(out_path, pagesize=A4, topMargin=20 * mm, bottomMargin=18 * mm)
    story = []

    story.append(Paragraph("Packaged Commodity Compliance Report", title_style))
    story.append(Paragraph("SIH26034 — AI-Assisted Legal Metrology Screening", normal))
    story.append(Spacer(1, 10))

    status = inspection.get("overall_status", "NEEDS_REVIEW")
    status_color = STATUS_COLORS.get(status, colors.black)

    meta_table_data = [
        ["Product Name", inspection.get("product_name") or declarations.get("product_name") or "N/A"],
        ["Scan Date / Time", inspection.get("scanned_at", "")],
        ["Inspection ID", str(inspection.get("id", ""))],
        ["Compliance Score", f"{inspection.get('compliance_score', 0)} / 100"],
        ["Overall Status", status.replace("_", " ")],
        ["OCR Confidence", f"{inspection.get('ocr_confidence', 0)}%"],
    ]
    meta_table = Table(meta_table_data, colWidths=[55 * mm, 110 * mm])
    meta_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f3f4f6")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (1, 4), (1, 4), status_color),
        ("FONTNAME", (1, 4), (1, 4), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    if image_path and os.path.exists(image_path):
        try:
            story.append(Paragraph("Scanned Product Image", h2))
            story.append(RLImage(image_path, width=70 * mm, height=70 * mm, kind="proportional"))
        except Exception:
            pass

    story.append(Paragraph("Extracted Declarations", h2))
    decl_rows = [["Field", "Extracted Value"]]
    field_labels = {
        "product_name": "Product Name",
        "manufacturer": "Manufacturer / Packer / Importer",
        "address": "Address",
        "net_quantity": "Net Quantity",
        "mrp": "MRP",
        "mfg_date": "Mfg / Packing Date",
        "consumer_care": "Consumer Care",
        "other_declarations": "Other Declarations",
    }
    for key, label in field_labels.items():
        decl_rows.append([label, declarations.get(key) or "(not found)"])
    decl_table = Table(decl_rows, colWidths=[45 * mm, 120 * mm])
    decl_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(decl_table)
    story.append(Spacer(1, 10))

    cell_style = ParagraphStyle("Cell", parent=styles["Normal"], fontSize=8.5, leading=10.5)

    story.append(Paragraph("Compliance Check Results", h2))
    v_rows = [["Requirement", "Result", "Explanation / Evidence", "Legal Reference"]]
    for v in violations:
        result_style = ParagraphStyle(
            "ResultCell", parent=cell_style,
            textColor=RESULT_COLORS.get(v.get("result"), colors.black),
        )
        v_rows.append([
            Paragraph(v.get("rule_title", ""), cell_style),
            Paragraph(v.get("result", ""), result_style),
            Paragraph(f"{v.get('explanation','')}<br/><i>Evidence: {v.get('evidence','')}</i>", small),
            Paragraph(v.get("legal_reference", ""), small),
        ])
    v_table = Table(v_rows, colWidths=[35 * mm, 22 * mm, 75 * mm, 33 * mm], repeatRows=1)
    style_cmds = [
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
        ("FONTSIZE", (0, 0), (-1, 0), 8.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]
    v_table.setStyle(TableStyle(style_cmds))
    story.append(v_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Recommended Actions", h2))
    for v in violations:
        if v.get("result") in ("FAIL", "WARNING", "MANUAL_VERIFICATION"):
            story.append(Paragraph(f"• <b>{v.get('rule_title')}</b>: {v.get('recommended_action')}", normal))
    story.append(Spacer(1, 14))

    story.append(Paragraph("System Disclaimer", h2))
    story.append(Paragraph(DISCLAIMER, small))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", small))

    doc.build(story)
    return out_path
