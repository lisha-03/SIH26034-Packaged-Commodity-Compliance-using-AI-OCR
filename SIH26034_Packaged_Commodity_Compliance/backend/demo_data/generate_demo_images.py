"""
Generates three clearly-labelled DEMO / SYNTHETIC product label images used
to test the OCR + compliance pipeline. These are NOT official SIH datasets
and are for demonstration purposes only, as noted in the README.

Run:  python demo_data/generate_demo_images.py
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
os.makedirs(OUT_DIR, exist_ok=True)


def _font(size):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def demo_product_1():
    """Mostly compliant: all mandatory declarations present, clearly readable."""
    img = Image.new("RGB", (900, 700), "white")
    d = ImageDraw.Draw(img)
    lines = [
        ("SUNRISE PREMIUM WHEAT FLOUR", _font(34)),
        ("(DEMO / SYNTHETIC LABEL - NOT A REAL PRODUCT)", _font(16)),
        ("", _font(20)),
        ("Mfd By: Sunrise Foods Pvt Ltd", _font(24)),
        ("Address: Plot 14, Industrial Area, Pune, Maharashtra 411001", _font(20)),
        ("Net Wt: 1000g", _font(24)),
        ("MRP: Rs 55.00 (Inclusive of all taxes)", _font(24)),
        ("Mfg Date: 03/2026", _font(24)),
        ("Consumer Care: 1800-123-4567 / care@sunrisefoods.in", _font(20)),
    ]
    y = 30
    for text, font in lines:
        d.text((40, y), text, fill="black", font=font)
        y += 55
    return img


def demo_product_2():
    """Missing declaration: intentionally omits Mfg Date and Consumer Care."""
    img = Image.new("RGB", (900, 700), "white")
    d = ImageDraw.Draw(img)
    lines = [
        ("GOLDEN DROP MUSTARD OIL", _font(34)),
        ("(DEMO / SYNTHETIC LABEL - NOT A REAL PRODUCT)", _font(16)),
        ("", _font(20)),
        ("Marketed By: Golden Drop Agro Industries", _font(24)),
        ("Address: 22 Market Road, Kanpur, Uttar Pradesh 208001", _font(20)),
        ("Net Qty: 500ml", _font(24)),
        ("MRP: Rs 120.00", _font(24)),
        # Mfg date intentionally omitted
        # Consumer care intentionally omitted
    ]
    y = 30
    for text, font in lines:
        d.text((40, y), text, fill="black", font=font)
        y += 55
    return img


def demo_product_3():
    """Readability issue: very small text + blur simulation."""
    img = Image.new("RGB", (900, 700), "white")
    d = ImageDraw.Draw(img)
    lines = [
        ("BLUE OCEAN INSTANT NOODLES", _font(30)),
        ("(DEMO / SYNTHETIC LABEL - NOT A REAL PRODUCT)", _font(14)),
    ]
    y = 25
    for text, font in lines:
        d.text((40, y), text, fill="black", font=font)
        y += 45

    small_lines = [
        "Mfd By: Blue Ocean Snacks Ltd, Chennai, Tamil Nadu 600001",
        "Net Wt: 70g",
        "MRP: Rs 14.00",
        "Mfg Date: 05/2026",
        "Consumer Care: 044-2233-4455",
    ]
    y = 130
    tiny_font = _font(9)  # deliberately tiny to simulate a readability problem
    for text in small_lines:
        d.text((40, y), text, fill=(90, 90, 90), font=tiny_font)
        y += 22

    img = img.filter(ImageFilter.GaussianBlur(radius=1.6))
    return img


if __name__ == "__main__":
    demo_product_1().save(os.path.join(OUT_DIR, "demo_product_1.png"))
    demo_product_2().save(os.path.join(OUT_DIR, "demo_product_2.png"))
    demo_product_3().save(os.path.join(OUT_DIR, "demo_product_3.png"))
    print(f"Generated 3 demo label images in {OUT_DIR}")
