# Compliance Rule Engine

Location: `backend/rules/compliance_engine.py` + `backend/rules/legal_reference.py`

## Sourcing note (read this first)

The reference file supplied with this project
(`TheLegalMetrologyAct.mht`) is the Department of Consumer Affairs
website page listing *links* to download various Legal Metrology Acts,
Rules and amendment notifications — it does not itself contain the
operative statutory text. `rules/legal_reference.py` documents this in
full at the top of the file.

Because no complete statutory text was supplied, the five mandatory
declarations checked below are built from the well-established, publicly
known structure of **Rule 6 of the Legal Metrology (Packaged
Commodities) Rules, 2011**. This is standard, widely published regulatory
knowledge — but an authorized officer must verify each rule against the
current, complete Rules text before using this for real enforcement.

## Mandatory declarations checked

| Rule Key        | Requirement                                   | Legal Reference (documented) |
|-------------------|------------------------------------------------|---------------------------------|
| MANUFACTURER      | Name & address of manufacturer/packer/importer | Rule 6(1)(a) |
| NET_QUANTITY       | Net quantity                                     | Rule 6(1)(b) |
| MRP                 | Maximum Retail Price                             | Rule 6(1)(e) |
| MFG_DATE            | Month & year of manufacture/packing/import       | Rule 6(1)(f) |
| CONSUMER_CARE       | Consumer care / grievance contact                | Rule 6(1)(d) |

Plus a non-legal, informational **Label Readability** check (see
`docs/ocr_workflow.md`).

## Per-field classification

For each field, `_classify_field()` returns:

- **FAIL** — value is empty.
- **WARNING** — value is present but suspiciously short (<3 chars) or
  matches a placeholder-like marker (`n/a`, `xxx`, `test`, `sample`, `---`,
  `lorem`).
- **PASS** — value looks like a real declaration.

If overall OCR confidence was below 45% **and** the field is empty, the
result is upgraded from FAIL to **MANUAL_VERIFICATION** — the system
refuses to assert a violation it isn't confident about.

## Scoring formula (documented, not arbitrary)

```
Start at 100.
Each FAILed mandatory declaration:      -18 points
Each WARNING on a mandatory declaration: -8 points
A readability WARNING/MANUAL_VERIFICATION on the whole label: -6 points
Score floor: 0

Status thresholds:
  score >= 85 AND no MANUAL_VERIFICATION AND no FAIL  -> COMPLIANT
  score < 50                                            -> NON_COMPLIANT
  otherwise                                             -> NEEDS_REVIEW
```

The "no MANUAL_VERIFICATION" condition on COMPLIANT is deliberate: the
system must never claim full compliance while it is unsure about a field
— it can only say NEEDS_REVIEW in that case, deferring to the human
officer.

## Output shape

Each rule produces:
```json
{
  "rule_key": "MRP",
  "rule_title": "Maximum Retail Price (MRP)",
  "result": "PASS | FAIL | WARNING | MANUAL_VERIFICATION",
  "explanation": "...",
  "evidence": "the extracted value, or '(not found in extracted text)'",
  "legal_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 — Rule 6(1)(e)",
  "recommended_action": "..."
}
```
