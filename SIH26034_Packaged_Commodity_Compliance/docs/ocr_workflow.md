# OCR Workflow

## Engine

Real OCR via [Tesseract](https://github.com/tesseract-ocr/tesseract)
(`pytesseract` Python binding). No predefined/fake text is ever returned —
every scan reads the actual pixels of the uploaded image.

## Pipeline (`backend/ocr/ocr_engine.py`)

1. **Pre-processing** (OpenCV): grayscale conversion → bilateral filter
   (denoise while preserving edges) → adaptive Gaussian thresholding. This
   materially improves Tesseract's accuracy on photographed labels versus
   raw color images.
2. **Text extraction**: `pytesseract.image_to_string()` on the processed
   image.
3. **Confidence & readability signal**: `pytesseract.image_to_data()`
   returns per-word confidence scores. The average is used to classify the
   label as:
   - `READABLE` (avg confidence ≥ 65%)
   - `DIFFICULT` (40–65%)
   - `MANUAL_VERIFICATION` (< 40%)

   This is a **practical, image-quality-based signal**, not a measurement
   of physical font size against the legally mandated minimum — the
   system does not claim to do the latter (see `docs/limitations.md`).

4. **Structured field extraction** (`extract_declarations()`): the raw
   OCR text is parsed with a set of regex/keyword patterns tuned to how
   these declarations typically appear on Indian packaged-commodity
   labels (e.g. `MRP: Rs 55.00`, `Net Wt: 1000g`, `Mfg Date: 03/2026`,
   `Consumer Care: 1800-...`). Fields that cannot be confidently matched
   are left blank rather than guessed — the officer fills them in during
   the review step.

## Officer review step

The extracted fields are always shown in an editable form before
compliance analysis runs (`ScanProduct.jsx`). This exists specifically
because OCR — even when working correctly — can misread a label or fail
to find a declaration that is genuinely present but oddly formatted. The
compliance engine analyzes whatever is in the form at the moment
"Run Compliance Analysis" is clicked, whether that came from OCR or from
manual officer correction.

## Low-confidence handling

If overall OCR confidence is below 45%, the compliance engine does **not**
assert FAIL for empty fields — it marks them `MANUAL_VERIFICATION`
instead, because a blank field under low confidence could mean either
"genuinely missing" or "OCR simply failed to read it." This is
implemented in `rules/compliance_engine.py`.
