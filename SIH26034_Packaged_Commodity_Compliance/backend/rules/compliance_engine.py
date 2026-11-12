"""
Compliance rule engine.

Takes extracted/edited declaration fields + readability signal from OCR and
produces a list of rule results (PASS / FAIL / WARNING /
MANUAL_VERIFICATION / NOT_APPLICABLE) plus a documented,
deterministic compliance score.

SCORING FORMULA:
    - Start at 100.
    - Each mandatory declaration that FAILS: -18 points.
    - Each mandatory declaration that gets a WARNING: -8 points.
    - Readability WARNING / MANUAL_VERIFICATION: -6 points.
    - Score is limited between 0 and 100.
    - Status thresholds:
        score >= 85  -> COMPLIANT
        50 <= score < 85 -> NEEDS_REVIEW
        score < 50 -> NON_COMPLIANT

IMPORTANT:
    This is an AI-assisted screening tool.
    It does not make a final legal determination.
"""

from rules.legal_reference import (
    MANDATORY_DECLARATIONS,
    DISCLAIMER,
)


# ============================================================
# SCORING CONSTANTS
# ============================================================

FAIL_PENALTY = 18
WARNING_PENALTY = 8
READABILITY_PENALTY = 6


# Values that may indicate incomplete or placeholder information.
SUSPICIOUS_MARKERS = [
    "n/a",
    "na",
    "xxx",
    "---",
    "test",
    "sample",
    "lorem",
]


# ============================================================
# FIELD CLASSIFICATION
# ============================================================

def _classify_field(value: str, min_confidence_len: int = 3):
    """
    Classify a declaration field.

    Returns:
        PASS
        WARNING
        FAIL
    """

    if value is None:
        return "FAIL"

    value = str(value).strip()

    # Empty value
    if not value:
        return "FAIL"

    # Very short value
    if len(value) < min_confidence_len:
        return "WARNING"

    # Placeholder / suspicious values
    lowered = value.lower()

    for marker in SUSPICIOUS_MARKERS:
        if marker in lowered:
            return "WARNING"

    return "PASS"


# ============================================================
# MAIN COMPLIANCE CHECK
# ============================================================

def run_compliance_check(
    declarations: dict,
    ocr_confidence: float,
    readability_status: str,
    product_context: dict | None = None,
):
    """
    Run deterministic compliance checks on extracted declarations.

    product_context may contain:

        is_imported:
            True / False

        best_before_applicable:
            True / False

        dimensions_relevant:
            True / False

    The engine remains an AI-assisted screening tool and does not make
    a final legal determination.
    """

    results = []
    score = 100

    product_context = product_context or {}

    # ========================================================
    # LOW OCR CONFIDENCE
    # ========================================================

    low_confidence = (
        ocr_confidence is not None
        and ocr_confidence < 45
    )

    # ========================================================
    # CHECK EVERY DECLARATION
    # ========================================================

    for rule_key, rule in MANDATORY_DECLARATIONS.items():

        # ----------------------------------------------------
        # 1. CHECK WHETHER RULE APPLIES
        # ----------------------------------------------------

        applicability = rule.get(
            "applicability",
            "ALL"
        )

        # ----------------------------------------------------
        # IMPORTED PRODUCTS
        # ----------------------------------------------------

        if applicability == "IMPORTED":

            if not product_context.get(
                "is_imported",
                False
            ):

                results.append({
                    "rule_key": rule_key,
                    "rule_title": rule["title"],
                    "result": "NOT_APPLICABLE",

                    "explanation": (
                        "This declaration applies to imported "
                        "commodities. The current inspection is "
                        "not marked as an imported product."
                    ),

                    "evidence": "Not applicable",

                    "legal_reference": rule[
                        "legal_reference"
                    ],

                    "recommended_action": (
                        "None — declaration not applicable "
                        "to this inspection."
                    ),
                })

                continue

        # ----------------------------------------------------
        # WHERE APPLICABLE
        # ----------------------------------------------------

        elif applicability == "WHERE_APPLICABLE":

            if not product_context.get(
                "best_before_applicable",
                False
            ):

                results.append({
                    "rule_key": rule_key,
                    "rule_title": rule["title"],
                    "result": "NOT_APPLICABLE",

                    "explanation": (
                        "This declaration is applicable only "
                        "to relevant commodities. It has not "
                        "been marked as applicable for this "
                        "inspection."
                    ),

                    "evidence": "Not applicable",

                    "legal_reference": rule[
                        "legal_reference"
                    ],

                    "recommended_action": (
                        "None — verify applicability if required."
                    ),
                })

                continue

        # ----------------------------------------------------
        # WHERE RELEVANT
        # ----------------------------------------------------

        elif applicability == "WHERE_RELEVANT":

            if not product_context.get(
                "dimensions_relevant",
                False
            ):

                results.append({
                    "rule_key": rule_key,
                    "rule_title": rule["title"],
                    "result": "NOT_APPLICABLE",

                    "explanation": (
                        "Dimension information is checked only "
                        "when relevant to the commodity/package."
                    ),

                    "evidence": "Not applicable",

                    "legal_reference": rule[
                        "legal_reference"
                    ],

                    "recommended_action": (
                        "None — verify applicability if required."
                    ),
                })

                continue

        # ====================================================
        # 2. CHECK REQUIRED FIELDS
        # ====================================================

        required_fields = rule.get(
            "required_fields",
            [rule["field"]]
        )

        missing_fields = []

        for field_name in required_fields:

            value = declarations.get(
                field_name,
                ""
            )

            if (
                value is None
                or not str(value).strip()
            ):
                missing_fields.append(
                    field_name
                )

        # ====================================================
        # 3. LOW OCR CONFIDENCE
        # ====================================================

        if missing_fields and low_confidence:

            result = "MANUAL_VERIFICATION"

            missing_display = ", ".join(
                missing_fields
            )

            explanation = (
                f"Required information for "
                f"'{rule['title']}' was not found in "
                f"the extracted text "
                f"({missing_display}), but overall OCR "
                f"confidence was low "
                f"({ocr_confidence:.0f}%). OCR may have "
                "failed to read the declaration. "
                "Manual verification required."
            )

            evidence = (
                "Missing from extracted text: "
                + missing_display
            )

        # ====================================================
        # 4. REQUIRED FIELD MISSING
        # ====================================================

        elif missing_fields:

            result = "FAIL"

            missing_display = ", ".join(
                missing_fields
            )

            explanation = (
                f"'{rule['title']}' is incomplete. "
                f"Missing required field(s): "
                f"{missing_display}."
            )

            evidence = (
                "Missing field(s): "
                + missing_display
            )

            score -= FAIL_PENALTY

        # ====================================================
        # 5. ALL REQUIRED FIELDS PRESENT
        # ====================================================

        else:

            suspicious_fields = []

            for field_name in required_fields:

                value = declarations.get(
                    field_name,
                    ""
                )

                classification = _classify_field(
                    value
                )

                if classification == "WARNING":

                    suspicious_fields.append(
                        field_name
                    )

            # ------------------------------------------------
            # SUSPICIOUS / INCOMPLETE VALUES
            # ------------------------------------------------

            if suspicious_fields:

                result = "WARNING"

                suspicious_display = ", ".join(
                    suspicious_fields
                )

                explanation = (
                    f"'{rule['title']}' is present, "
                    f"but the following field(s) look "
                    f"incomplete, too short, or "
                    f"placeholder-like: "
                    f"{suspicious_display}. "
                    "Please verify manually."
                )

                evidence = "; ".join(
                    f"{field}: "
                    f"{declarations.get(field, '')}"
                    for field in required_fields
                )

                score -= WARNING_PENALTY

            # ------------------------------------------------
            # ALL REQUIRED FIELDS VALID
            # ------------------------------------------------

            else:

                result = "PASS"

                explanation = (
                    f"'{rule['title']}' contains all "
                    "required declaration fields."
                )

                evidence = "; ".join(
                    f"{field}: "
                    f"{declarations.get(field, '')}"
                    for field in required_fields
                )

        # ====================================================
        # 6. STORE RULE RESULT
        # ====================================================

        results.append({
            "rule_key": rule_key,

            "rule_title": rule["title"],

            "result": result,

            "explanation": explanation,

            "evidence": evidence,

            "legal_reference": rule[
                "legal_reference"
            ],

            "recommended_action": (
                rule["action_on_fail"]
                if result in (
                    "FAIL",
                    "MANUAL_VERIFICATION"
                )

                else (
                    "Verify manually — declaration "
                    "may be incomplete."
                    if result == "WARNING"

                    else
                    "None — declaration present."
                )
            ),
        })

    # ========================================================
    # 7. READABILITY CHECK
    # ========================================================

    if readability_status in (
        "DIFFICULT",
        "MANUAL_VERIFICATION"
    ):

        score -= READABILITY_PENALTY

        results.append({
            "rule_key": "READABILITY",

            "rule_title": "Label Readability",

            "result": (
                "WARNING"
                if readability_status == "DIFFICULT"
                else "MANUAL_VERIFICATION"
            ),

            "explanation": (
                "The uploaded image shows signs of small, "
                "blurry, or low-quality text in parts of "
                "the label. Exact legal font-size compliance "
                "was NOT measured. This is a practical, "
                "image-quality-based readability signal only."
            ),

            "evidence": (
                f"OCR average confidence: "
                f"{ocr_confidence:.0f}%"
                if ocr_confidence is not None
                else "N/A"
            ),

            "legal_reference": (
                "Legal Metrology (Packaged Commodities) "
                "Rules, 2011 — general readability/"
                "font-size provisions (verify exact "
                "clause with current Rules text)."
            ),

            "recommended_action": (
                "Manually inspect the physical label / "
                "a higher-resolution image for readability."
            ),
        })

    else:

        results.append({
            "rule_key": "READABILITY",

            "rule_title": "Label Readability",

            "result": "PASS",

            "explanation": (
                "No significant readability issues "
                "detected in the uploaded image."
            ),

            "evidence": (
                f"OCR average confidence: "
                f"{ocr_confidence:.0f}%"
                if ocr_confidence is not None
                else "N/A"
            ),

            "legal_reference": (
                "Legal Metrology (Packaged Commodities) "
                "Rules, 2011 — general readability/"
                "font-size provisions (verify exact "
                "clause with current Rules text)."
            ),

            "recommended_action": "None.",
        })

    # ========================================================
    # 8. KEEP SCORE BETWEEN 0 AND 100
    # ========================================================

    score = max(
        0,
        min(100, score)
    )

    # ========================================================
    # 9. CHECK OVERALL STATUS
    # ========================================================

    has_manual_verification = any(
        r["result"] == "MANUAL_VERIFICATION"
        for r in results
        if r["rule_key"] != "READABILITY"
    )

    has_fail = any(
        r["result"] == "FAIL"
        for r in results
    )

    # --------------------------------------------------------
    # COMPLIANT
    # --------------------------------------------------------

    if (
        score >= 85
        and not has_manual_verification
        and not has_fail
    ):

        status = "COMPLIANT"

    # --------------------------------------------------------
    # NON-COMPLIANT
    # --------------------------------------------------------

    elif score < 50:

        status = "NON_COMPLIANT"

    # --------------------------------------------------------
    # NEEDS REVIEW
    # --------------------------------------------------------

    else:

        status = "NEEDS_REVIEW"

    # ========================================================
    # 10. RETURN RESULT
    # ========================================================

    return (
        results,
        score,
        status
    )