"""
Fast OCR engine for packaged commodity compliance.

Uses:
    - Tesseract OCR via pytesseract
    - OpenCV preprocessing
    - Pillow
    - Limited rotation/preprocessing attempts
    - OCR timeout protection

This version is optimized for a local hackathon prototype.
OCR results should always be manually verified by an authorized officer.
"""

import re

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageOps

from rules.legal_reference import EXTRACTED_FIELDS


# ============================================================
# CONFIGURATION
# ============================================================

MAX_IMAGE_DIMENSION = 1600
OCR_TIMEOUT_SECONDS = 8

ROTATIONS = [0, 90]
PSM_MODES = [6, 11]


# ============================================================
# IMAGE LOADING
# ============================================================

def _load_image(image_path: str):
    """Load image and respect EXIF orientation."""

    pil_image = Image.open(image_path)
    pil_image = ImageOps.exif_transpose(pil_image)
    pil_image = pil_image.convert("RGB")

    img = np.array(pil_image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    if img is None or img.size == 0:
        raise ValueError(
            "Could not read image file. "
            "It may be corrupted or unsupported."
        )

    return img


# ============================================================
# ROTATION
# ============================================================

def _rotate_image(img, angle):

    if angle == 0:
        return img

    if angle == 90:
        return cv2.rotate(
            img,
            cv2.ROTATE_90_CLOCKWISE
        )

    if angle == 180:
        return cv2.rotate(
            img,
            cv2.ROTATE_180
        )

    if angle == 270:
        return cv2.rotate(
            img,
            cv2.ROTATE_90_COUNTERCLOCKWISE
        )

    return img


# ============================================================
# RESIZE
# ============================================================

def _resize_image(img):

    height, width = img.shape[:2]
    largest_dimension = max(height, width)

    if largest_dimension <= MAX_IMAGE_DIMENSION:
        return img

    scale = MAX_IMAGE_DIMENSION / largest_dimension

    new_width = max(1, int(width * scale))
    new_height = max(1, int(height * scale))

    return cv2.resize(
        img,
        (new_width, new_height),
        interpolation=cv2.INTER_AREA
    )


# ============================================================
# PREPROCESSING
# ============================================================

def _preprocess_variants(img):

    img = _resize_image(img)

    gray = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2GRAY
    )

    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    _, otsu = cv2.threshold(
        enhanced,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return [
        ("gray", gray),
        ("enhanced", enhanced),
        ("otsu", otsu),
    ]


# ============================================================
# OCR
# ============================================================

def _ocr_once(image, psm=6):

    pil_img = Image.fromarray(image)

    config = f"--oem 3 --psm {psm}"

    try:

        data = pytesseract.image_to_data(
            pil_img,
            config=config,
            output_type=pytesseract.Output.DICT,
            timeout=OCR_TIMEOUT_SECONDS
        )

    except RuntimeError:

        return {
            "raw_text": "",
            "avg_confidence": 0.0,
            "word_count": 0,
        }

    confidences = []
    words = []

    texts = data.get("text", [])
    confs = data.get("conf", [])

    for index, value in enumerate(confs):

        try:
            confidence = float(value)
        except (ValueError, TypeError):
            continue

        text_value = ""

        if index < len(texts):
            text_value = str(texts[index]).strip()

        if text_value:
            words.append(text_value)

        if confidence >= 0:
            confidences.append(confidence)

    raw_text = " ".join(words)

    raw_text = _clean_ocr_text(raw_text)

    average_confidence = (
        sum(confidences) / len(confidences)
        if confidences
        else 0.0
    )

    return {
        "raw_text": raw_text,
        "avg_confidence": average_confidence,
        "word_count": len(words),
    }


# ============================================================
# TEXT CLEANING
# ============================================================

def _clean_ocr_text(text: str):

    if not text:
        return ""

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        line = re.sub(
            r"[ \t]+",
            " ",
            line
        )

        lines.append(line)

    return "\n".join(lines)


# ============================================================
# OCR RESULT SCORING
# ============================================================

def _score_ocr_result(result):

    confidence = result["avg_confidence"]
    word_count = result["word_count"]
    text = result["raw_text"]

    score = confidence

    score += min(word_count, 40) * 0.25

    score += min(len(text), 500) / 100

    return score


# ============================================================
# BEST OCR
# ============================================================

def _run_best_ocr(image_path: str):

    original = _load_image(image_path)

    best_result = None
    best_score = -1

    for angle in ROTATIONS:

        rotated = _rotate_image(
            original,
            angle
        )

        variants = _preprocess_variants(
            rotated
        )

        for variant_name, processed_image in variants:

            for psm in PSM_MODES:

                result = _ocr_once(
                    processed_image,
                    psm=psm
                )

                result["rotation"] = angle
                result["preprocessing"] = variant_name
                result["psm"] = psm

                score = _score_ocr_result(
                    result
                )

                if score > best_score:

                    best_score = score
                    best_result = result

    if best_result is None:

        raise RuntimeError(
            "Tesseract OCR could not process the uploaded image."
        )

    return best_result


# ============================================================
# PUBLIC OCR FUNCTION
# ============================================================

def run_ocr(image_path: str):

    result = _run_best_ocr(
        image_path
    )

    confidence = float(
        result["avg_confidence"]
    )

    if confidence >= 65:
        readability_status = "READABLE"

    elif confidence >= 40:
        readability_status = "DIFFICULT"

    else:
        readability_status = "MANUAL_VERIFICATION"

    return {
        "raw_text": result["raw_text"],
        "avg_confidence": round(
            confidence,
            1
        ),
        "readability_status": readability_status,
        "word_count": result["word_count"],
    }


# ============================================================
# REGEX HELPER
# ============================================================

def _first_match(patterns, text):

    if not text:
        return ""

    for pattern in patterns:

        try:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:

                value = match.group(1).strip()

                value = re.sub(
                    r"\s+",
                    " ",
                    value
                )

                if value:
                    return value

        except re.error:
            continue

    return ""


# ============================================================
# DECLARATION EXTRACTION PATTERNS
# ============================================================

# ------------------------------------------------------------
# MRP
# ------------------------------------------------------------
# Supports OCR mistakes such as:
# MRP: 20.00
# MRP 20.00
# MRP & 20.00
# MRP ₹20.00
# MRP Rs. 20.00

_MRP_PATTERNS = [

    r"(?:MRP|M\.R\.P\.?)"
    r"\s*[:\-=&₹]*\s*"
    r"(?:Rs\.?|INR)?\s*"
    r"([0-9]+(?:[.,][0-9]+)?)",

    r"(?:Maximum\s+Retail\s+Price)"
    r"\s*[:\-=&₹]*\s*"
    r"(?:Rs\.?|INR)?\s*"
    r"([0-9]+(?:[.,][0-9]+)?)",
]


# ------------------------------------------------------------
# NET QUANTITY
# ------------------------------------------------------------

_NET_QTY_PATTERNS = [

    r"(?:Net\s*(?:Wt|Weight|Qty|Quantity))\.?"
    r"\s*[:\-]?\s*"
    r"([0-9]+(?:[.,][0-9]+)?\s*"
    r"(?:mg|kg|g|ml|l|cl|gm|gram|grams|"
    r"kilogram|kilograms|millilitre|milliliter|"
    r"litre|liter)s?)",

    r"\b([0-9]+(?:[.,][0-9]+)?\s*"
    r"(?:mg|kg|g|ml|l)\b)",
]


# ------------------------------------------------------------
# MANUFACTURE / PACKING DATE
# ------------------------------------------------------------

_DATE_PATTERNS = [

    # PKD / Packed / Mfg date
    r"(?:PKD|Pkd|Packed|Packing|Mfg|Mfd|Manufactured)"
    r"[\s\.\-]*(?:Date|On|Dt)?"
    r"\s*[:\-]?\s*"
    r"([0-9]{1,2}[/\-][0-9]{1,2}[/\-][0-9]{2,4})",

    r"(?:PKD|Pkd|Packed|Packing|Mfg|Mfd|Manufactured)"
    r"[\s\.\-]*(?:Date|On|Dt)?"
    r"\s*[:\-]?\s*"
    r"([A-Za-z]{3,9}\s*[0-9]{4})",

    r"(?:PKD|Pkd|Packed|Packing|Mfg|Mfd|Manufactured)"
    r"[\s\.\-]*(?:Date|On|Dt)?"
    r"\s*[:\-]?\s*"
    r"([0-9]{1,2}[/\-][0-9]{4})",
]


# ============================================================
# CONSUMER CARE
# ============================================================

def _extract_consumer_care(text):

    if not text:
        return ""

    # First try the labelled consumer-care section.
    match = re.search(
        r"(?:Consumer\s*Care|Customer\s*Care|"
        r"Consumer\s*Complaints?|For\s+feedback\s*/?\s*complaints?)"
        r"\s*[:\-]?\s*"
        r"(.{8,350})",
        text,
        re.IGNORECASE
    )

    if match:

        value = match.group(1)

        # Stop before another major declaration.
        value = re.split(
            r"\b(?:Website|Ingredients|Net\s*Quantity|MRP|"
            r"PKD|Batch\s*No|FSSAI|Manufactured\s*By|"
            r"Packed\s*By)\b",
            value,
            flags=re.IGNORECASE
        )[0]

        value = re.sub(
            r"\s+",
            " ",
            value
        ).strip()

        if value:
            return value[:350]

    # Fallback: phone number.
    phone = re.search(
        r"(?:Toll\s*Free|Helpline|Customer\s*Service)?"
        r"\s*[:\-]?\s*"
        r"(\+?[0-9][0-9\-\s]{7,18}[0-9])",
        text,
        re.IGNORECASE
    )

    if phone:
        return phone.group(1).strip()

    # Fallback: email.
    email = re.search(
        r"([A-Za-z0-9._%+\-]+@"
        r"[A-Za-z0-9.\-]+\.[A-Za-z]{2,})",
        text
    )

    if email:
        return email.group(1).strip()

    return ""


# ============================================================
# MANUFACTURER
# ============================================================

def _extract_manufacturer(text):

    if not text:
        return ""

    patterns = [

        # Example:
        # MANUFACTURED BY: BRITANNIA INDUSTRIES LIMITED
        r"(?:Manufactured\s*By|Mfd\.?\s*By)"
        r"\s*[:\-]?\s*"
        r"(.{3,150}?)"
        r"(?=\s+(?:FROM\s+PACKAGING|Plot\s+No\.?|Address|"
        r"Regd\.?\s+Office|Registered\s+Office)\b)",

        # Example:
        # PACKED BY: COMPANY NAME
        r"(?:Packed\s*By|Pkd\.?\s*By)"
        r"\s*[:\-]?\s*"
        r"(.{3,150}?)"
        r"(?=\s+(?:Plot\s+No\.?|Address|Regd\.?|Registered)\b)",

        # Marketed by
        r"(?:Marketed\s*By)"
        r"\s*[:\-]?\s*"
        r"(.{3,150}?)"
        r"(?=\s+(?:Plot\s+No\.?|Address|Regd\.?|Registered)\b)",

        # Imported by
        r"(?:Imported\s*By|Importer)"
        r"\s*[:\-]?\s*"
        r"(.{3,150}?)"
        r"(?=\s+(?:Plot\s+No\.?|Address|Regd\.?|Registered)\b)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            value = match.group(1)

            value = re.sub(
                r"\s+",
                " ",
                value
            ).strip()

            # Remove accidental OCR label text.
            value = re.sub(
                r"^(?:BEST\s+BEFORE.*?|NET\s+QUANTITY.*?)(?=\b[A-Z])",
                "",
                value,
                flags=re.IGNORECASE
            ).strip()

            if value:
                return value

    return ""


# ============================================================
# ADDRESS
# ============================================================

def _extract_address(text, manufacturer=""):

    if not text:
        return ""

    # If manufacturer was found, search after it.
    search_text = text

    if manufacturer:

        manufacturer_index = text.lower().find(
            manufacturer.lower()
        )

        if manufacturer_index >= 0:

            search_text = text[
                manufacturer_index + len(manufacturer):
            ]

    patterns = [

        # Plot / Industrial Area / Hoskote etc.
        r"((?:Plot\s+No\.?|Plot|No\.)"
        r".{10,220}?"
        r"(?:India|Karnataka|Bengaluru|Bangalore|"
        r"District|PIN|-\s*[0-9]{6}))",

        # Address label
        r"(?:Address)"
        r"\s*[:\-]?\s*"
        r"(.{8,200})",

        # Registered office
        r"(?:Regd\.?\s*Office|Registered\s*Office)"
        r"\s*[:\-]?\s*"
        r"(.{8,200})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            search_text,
            re.IGNORECASE
        )

        if match:

            value = match.group(1)

            value = re.sub(
                r"\s+",
                " ",
                value
            ).strip()

            if value:
                return value

    return ""


# ============================================================
# PRODUCT NAME
# ============================================================

def _extract_product_name(lines):

    # Product name extraction must be conservative.
    # We should NOT randomly select nutrition or address text.

    product_labels = [
        r"(?:Product\s*Name|Name\s*of\s*(?:the\s*)?Product)"
        r"\s*[:\-]\s*(.+)",

        r"(?:Product)\s*[:\-]\s*(.+)",
    ]

    for line in lines:

        for pattern in product_labels:

            match = re.search(
                pattern,
                line,
                re.IGNORECASE
            )

            if match:

                value = match.group(1).strip()

                if 2 <= len(value) <= 100:
                    return value

    # Only accept a likely product title from the first few lines
    # when it looks like a standalone title.
    for line in lines[:8]:

        clean = line.strip()

        if len(clean) < 3 or len(clean) > 80:
            continue

        lower = clean.lower()

        blocked = [
            "nutritional information",
            "ingredients",
            "energy",
            "protein",
            "carbohydrate",
            "sugar",
            "total fat",
            "saturated fat",
            "sodium",
            "manufactured",
            "manufactured by",
            "net quantity",
            "mrp",
            "best before",
            "fssai",
            "batch",
            "consumer care",
            "address",
        ]

        if any(
            word in lower
            for word in blocked
        ):
            continue

        # Don't accept lines that are mostly symbols/numbers.
        alphanumeric_count = sum(
            char.isalnum()
            for char in clean
        )

        if alphanumeric_count < 4:
            continue

        # Avoid long sentence-like OCR fragments.
        if clean.count(",") >= 3:
            continue

        return clean

    return ""


# ============================================================
# OTHER DECLARATIONS
# ============================================================

def _extract_other_declarations(lines, fields):

    # Meaningful compliance-related labels to capture.
    keywords = [
        "best before",
        "batch",
        "lot",
        "fssai",
        "ingredients",
        "contains",
        "allergen",
        "store",
        "storage",
        "flavour",
        "manufactured",
        "packed",
        "packaging",
        "website",
        "barcode",
        "lic.",
        "license",
        "licence",
    ]

    used_values = [
        str(value).lower().strip()
        for key, value in fields.items()
        if key != "other_declarations" and value
    ]

    leftover = []

    for line in lines:

        clean = line.strip()

        if not clean:
            continue

        lower = clean.lower()

        # Skip already extracted declaration values.
        already_used = False

        for used in used_values:

            if not used:
                continue

            if lower == used:
                already_used = True
                break

        if already_used:
            continue

        # Capture lines containing useful declaration keywords.
        if any(
            keyword in lower
            for keyword in keywords
        ):
            leftover.append(clean)

    # Remove duplicates while preserving order.
    unique = []

    for item in leftover:

        if item not in unique:
            unique.append(item)

    return " | ".join(unique[:10])


# ============================================================
# PUBLIC DECLARATION EXTRACTION
# ============================================================

def extract_declarations(raw_text: str):

    text = raw_text or ""

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    fields = {
        field: ""
        for field in EXTRACTED_FIELDS
    }

    # --------------------------------------------------------
    # MRP
    # --------------------------------------------------------

    fields["mrp"] = _first_match(
        _MRP_PATTERNS,
        text
    )

    # --------------------------------------------------------
    # NET QUANTITY
    # --------------------------------------------------------

    fields["net_quantity"] = _first_match(
        _NET_QTY_PATTERNS,
        text
    )

    # --------------------------------------------------------
    # MANUFACTURER
    # --------------------------------------------------------

    fields["manufacturer"] = _extract_manufacturer(
        text
    )

    # --------------------------------------------------------
    # ADDRESS
    # --------------------------------------------------------

    fields["address"] = _extract_address(
        text,
        fields["manufacturer"]
    )

    # --------------------------------------------------------
    # MANUFACTURE / PACKING DATE
    # --------------------------------------------------------

    fields["mfg_date"] = _first_match(
        _DATE_PATTERNS,
        text
    )

    # --------------------------------------------------------
    # CONSUMER CARE
    # --------------------------------------------------------

    fields["consumer_care"] = _extract_consumer_care(
        text
    )

    # --------------------------------------------------------
    # PRODUCT NAME
    # --------------------------------------------------------

    fields["product_name"] = _extract_product_name(
        lines
    )

    # --------------------------------
    # OTHER DECLARATIONS
    # --------------------------------------------------------

    fields["other_declarations"] = (
        _extract_other_declarations(
            lines,
            fields
        )
    )

    return fields