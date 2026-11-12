# Limitations & Future Scope

## Limitations (be upfront about these in your SIH demo)

1. **Legal reference sourcing.** The supplied `TheLegalMetrologyAct.mht`
   was a links/navigation page, not the operative statutory text. The
   5-declaration checklist is built from the well-known structure of Rule
   6 of the Legal Metrology (Packaged Commodities) Rules, 2011, but has
   not been cross-verified clause-by-clause against the current, complete
   Rules text. See `docs/compliance_rule_engine.md`.

2. **Readability check is a proxy, not a legal font-size measurement.**
   The system flags low OCR confidence / small-blurry text as a
   readability signal. It does **not** measure text height in millimetres
   against the specific minimum font-size requirement in the Rules. This
   is stated explicitly in the UI and PDF report.

3. **OCR/extraction accuracy on real-world photos.** The regex/keyword
   field extractor was tuned against fairly standard label phrasing
   (`MRP:`, `Net Wt:`, `Mfd By:`, etc.). Labels with unusual formatting,
   multiple languages, or heavy stylization may need more manual
   correction from the officer. This is by design — the officer review
   step exists specifically for this.

4. **No image-region highlighting.** Evidence is shown as extracted text
   values, not bounding boxes drawn on the image itself. Tesseract's
   `image_to_data()` does return per-word bounding boxes, so this is a
   natural next step (see Future Scope).

5. **Single-instance SQLite.** Fine for a hackathon demo / single officer
   workstation; would need to move to PostgreSQL/MySQL with proper
   concurrency handling for multi-officer production use.

6. **No deployment/production hardening.** Flask's built-in dev server is
   used (`debug=True`). Production would need a WSGI server (gunicorn/
   uwsgi), HTTPS, and a rotated `SECRET_KEY`.

## Future scope

- Highlight the exact image region behind each extracted declaration
  (using Tesseract's word bounding boxes) so the "Evidence" step visually
  points at the label, not just quotes text.
- Multi-image support per inspection (front + back + side) merged into
  one combined compliance result rather than treated as three fully
  separate scans.
- A genuine millimetre-level font-size check using image DPI metadata and
  calibration markers, once the applicable clause's exact numeric
  requirement has been confirmed against the current Rules text.
- Bulk/batch scanning for retail-store sweeps.
- Exportable, filterable analytics (by manufacturer, region, time period)
  for policy-level insights.
- Editable report export (e.g. DOCX) in addition to PDF, as originally
  scoped.
