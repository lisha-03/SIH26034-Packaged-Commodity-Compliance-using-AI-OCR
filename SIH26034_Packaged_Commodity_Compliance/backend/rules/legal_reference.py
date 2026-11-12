"""
Legal reference data used by the compliance rule engine.

SOURCING NOTE (important — read this):
The file supplied with this project ("TheLegalMetrologyAct.mht" / the PDF
version of it) is a page from the Department of Consumer Affairs website
listing links to download various Legal Metrology Acts, Rules and
amendment notifications. It does NOT itself contain the operative text of
the Legal Metrology Act, 2009 or the Legal Metrology (Packaged
Commodities) Rules, 2011 — only titles and download links.

Because no full statutory text was supplied, the mandatory-declaration
checklist below is built from the well-established, publicly known
structure of Rule 6 of the Legal Metrology (Packaged Commodities) Rules,
2011 (the core declarations every pre-packaged commodity must carry).
This is standard, widely published regulatory knowledge, not an invented
list — but it is NOT a substitute for the full, current rule text.

BEFORE using this prototype for any real enforcement decision, an
authorized officer must verify each rule against the current, complete
text of the Act/Rules (download the actual PDFs from the links on the
Department of Consumer Affairs Legal Metrology page). This module and the
system as a whole are explicitly an AI-ASSISTED SCREENING TOOL, not a
final legal authority — see DISCLAIMER below and in every generated
report.
"""

DISCLAIMER = (
    "This system provides AI-assisted compliance screening only. "
    "It does not make a final legal determination of non-compliance. "
    "All flagged issues must be verified by an authorized Legal Metrology "
    "enforcement officer against the current text of the Legal Metrology "
    "Act, 2009 and the Legal Metrology (Packaged Commodities) Rules, 2011 "
    "before any enforcement action is taken."
)

# Each entry describes one mandatory declaration checked by the engine.
MANDATORY_DECLARATIONS = {
    "MANUFACTURER": {
        "title": "Name and Address of Manufacturer/Packer/Importer",
        "field": "manufacturer",
        "required_fields": [
            "manufacturer",
            "address",
            ],
            "legal_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 — Rule 6(1)(a)",
            "description": (
                "Every package must declare the name and address of the "
                "manufacturer, or where the manufacturer is not the packer, "
                "the name and address of the packer/importer."
                ),
                "action_on_fail": (
                    "Flag package; manufacturer/packer/importer identity and address "
                    "should be verified by an authorized officer."
                    ),
},
    "NET_QUANTITY": {
        "title": "Net Quantity",
        "field": "net_quantity",
        "legal_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 — Rule 6(1)(b)",
        "description": (
            "Every package must declare the net quantity in terms of "
            "standard units of weight, measure or number."
        ),
        "action_on_fail": "Flag for under-declaration/over-declaration verification against actual weight.",
    },
    "MRP": {
        "title": "Maximum Retail Price (MRP)",
        "field": "mrp",
        "legal_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 — Rule 6(1)(e)",
        "description": (
            "Every package must declare the retail sale price, inclusive "
            "of all taxes, expressed as 'Maximum Retail Price' or 'MRP'."
        ),
        "action_on_fail": "Flag for potential overcharging risk to consumers.",
    },
    "MFG_DATE": {
        "title": "Month and Year of Manufacture/Packing/Import",
        "field": "mfg_date",
        "legal_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 — Rule 6(1)(f)",
        "description": (
            "Every package must declare the month and year in which the "
            "commodity was manufactured, packed or imported."
        ),
        "action_on_fail": "Flag — product freshness/shelf-life cannot be verified by the consumer.",
    },
    "CONSUMER_CARE": {
        "title": "Consumer Care / Grievance Contact Details",
        "field": "consumer_care",
        "legal_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 — Rule 6(1)(d)",
        "description": (
            "Every package must declare a telephone number, email or "
            "address through which a consumer can register a complaint."
        ),
        "action_on_fail": "Flag — consumer has no channel to raise a grievance about the product.",
    },
}

# Fields the OCR/extraction stage attempts to populate.
EXTRACTED_FIELDS = [
    "product_name",
    "manufacturer",
    "address",
    "net_quantity",
    "mrp",
    "mfg_date",
    "consumer_care",
    "other_declarations",
]
