"""
generate_image.py
Takes a product dict (title, image_url, price, category_color, etc.) and
produces a clean, Instagram-ready square (1080x1080) banner:
- product photo centered on a soft background
- category color strip + category name
- price + discount badge
- "ORDER NOW - LINK IN BIO" call-to-action bar

Uses only PIL (no external font files needed - falls back to default font
if custom fonts are not present in scripts/fonts/).
"""

import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps

CANVAS_SIZE = (1080, 1080)
FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")


def _font(name, size):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _download_image(url):
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return Image.open(BytesIO(resp.content)).convert("RGBA")


def _hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def _wrap_text(draw, text, font, max_width):
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = f"{line} {w}".strip()
        if draw.textlength(test, font=font) <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def generate_product_image(product: dict, output_path: str):
    """
    product keys used: title, image_url, price, mrp, discount_pct,
    category, category_color
    """
    color = _hex_to_rgb(product.get("category_color", "#2563EB"))

    canvas = Image.new("RGB", CANVAS_SIZE, "white")
    draw = ImageDraw.Draw(canvas)

    # top color strip with category name
    draw.rectangle([0, 0, CANVAS_SIZE[0], 90], fill=color)
    cat_font = _font("Poppins-Bold.ttf", 38)
    draw.text((40, 22), product.get("category", "TRENDING").upper(), font=cat_font, fill="white")

    # product photo, centered, max 780x600 box
    try:
        prod_img = _download_image(product["image_url"])
        prod_img = ImageOps.contain(prod_img, (780, 600))
        px = (CANVAS_SIZE[0] - prod_img.width) // 2
        py = 130
        # soft shadow card behind image
        card = Image.new("RGB", (prod_img.width + 40, prod_img.height + 40), "#F5F5F5")
        canvas.paste(card, (px - 20, py - 20))
        canvas.paste(prod_img, (px, py), prod_img)
    except Exception as e:
        print(f"[WARN] could not load product image: {e}")
        py = 130

    # title text
    title_font = _font("Poppins-SemiBold.ttf", 40)
    title_y = py + 630
    lines = _wrap_text(draw, product.get("title", ""), title_font, CANVAS_SIZE[0] - 80)[:2]
    for i, line in enumerate(lines):
        draw.text((40, title_y + i * 48), line, font=title_font, fill="#111111")

    # price + discount badge
    price_y = title_y + len(lines) * 48 + 20
    price_font = _font("Poppins-Bold.ttf", 54)
    mrp_font = _font("Poppins-Regular.ttf", 32)

    price = product.get("price")
    mrp = product.get("mrp")
    discount = product.get("discount_pct")

    x_cursor = 40
    if price:
        price_text = f"Rs {price:,}"
        draw.text((x_cursor, price_y), price_text, font=price_font, fill=color)
        x_cursor += int(draw.textlength(price_text, font=price_font)) + 20

    if mrp and mrp > (price or 0):
        mrp_text = f"Rs {mrp:,}"
        draw.text((x_cursor, price_y + 12), mrp_text, font=mrp_font, fill="#999999")
        # strike-through line
        w = draw.textlength(mrp_text, font=mrp_font)
        draw.line([(x_cursor, price_y + 30), (x_cursor + w, price_y + 30)], fill="#999999", width=2)
        x_cursor += int(w) + 20

    if discount:
        badge_text = f"{discount}% OFF"
        badge_font = _font("Poppins-Bold.ttf", 30)
        bw = draw.textlength(badge_text, font=badge_font) + 30
        draw.rounded_rectangle([x_cursor, price_y, x_cursor + bw, price_y + 50], radius=10, fill="#DC2626")
        draw.text((x_cursor + 15, price_y + 8), badge_text, font=badge_font, fill="white")

    # bottom CTA bar
    cta_h = 110
    draw.rectangle([0, CANVAS_SIZE[1] - cta_h, CANVAS_SIZE[0], CANVAS_SIZE[1]], fill="#111111")
    cta_font = _font("Poppins-Bold.ttf", 42)
    cta_text = "ORDER NOW - LINK IN BIO"
    tw = draw.textlength(cta_text, font=cta_font)
    draw.text(((CANVAS_SIZE[0] - tw) / 2, CANVAS_SIZE[1] - cta_h + 32), cta_text, font=cta_font, fill="white")

    canvas.save(output_path, quality=95)
    return output_path


if __name__ == "__main__":
    sample = {
        "title": "Wireless Bluetooth Earbuds with Noise Cancellation",
        "image_url": "https://m.media-amazon.com/images/I/61eDgd5aYML._SL1500_.jpg",
        "price": 1299,
        "mrp": 2999,
        "discount_pct": 57,
        "category": "Electronics",
        "category_color": "#2563EB",
    }
    os.makedirs("/tmp/out", exist_ok=True)
    generate_product_image(sample, "/tmp/out/sample.jpg")
    print("Saved /tmp/out/sample.jpg")
