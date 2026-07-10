"""
update_bio_page.py
Regenerates docs/index.html - the page linked in the Instagram/Facebook bio.
Lists today's products as cards with a big "Order Now" button per product.
GitHub Pages serves the docs/ folder automatically once enabled in repo
Settings -> Pages -> Source: /docs.
"""

import os
from datetime import datetime

DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Today's Best Deals</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background:#f4f4f6; margin:0; padding:20px; }}
  h1 {{ text-align:center; font-size:22px; color:#111; }}
  .updated {{ text-align:center; color:#777; font-size:13px; margin-bottom:20px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:16px; max-width:900px; margin:0 auto; }}
  .card {{ background:white; border-radius:14px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.08); }}
  .card img {{ width:100%; height:160px; object-fit:cover; }}
  .card-body {{ padding:10px; }}
  .card-title {{ font-size:14px; font-weight:600; color:#222; height:38px; overflow:hidden; }}
  .price {{ font-size:16px; font-weight:700; margin-top:6px; }}
  .badge {{ display:inline-block; font-size:11px; color:white; padding:3px 8px; border-radius:6px; margin-top:4px; }}
  .buy-btn {{ display:block; text-align:center; background:#111; color:white; text-decoration:none; padding:10px; margin-top:10px; border-radius:8px; font-weight:600; font-size:14px; }}
  .buy-btn:active {{ opacity:0.8; }}
</style>
</head>
<body>
  <h1>🔥 Today's Trending Deals</h1>
  <div class="updated">Updated: {updated_time}</div>
  <div class="grid">
    {cards}
  </div>
</body>
</html>
"""

CARD_TEMPLATE = """
<div class="card">
  <img src="{image_url}" alt="{title}">
  <div class="card-body">
    <div class="card-title">{title}</div>
    <div class="price" style="color:{color}">Rs {price}</div>
    <a class="buy-btn" href="{link}" target="_blank" rel="noopener">Order Now</a>
  </div>
</div>
"""


def build_bio_page(products: list):
    os.makedirs(DOCS_DIR, exist_ok=True)
    cards_html = ""
    for p in products:
        cards_html += CARD_TEMPLATE.format(
            image_url=p.get("image_url", ""),
            title=p.get("title", "")[:60],
            color=p.get("category_color", "#111111"),
            price=p.get("price", "-"),
            link=p.get("affiliate_link", "#"),
        )

    html = PAGE_TEMPLATE.format(
        updated_time=datetime.now().strftime("%d %b %Y, %I:%M %p"),
        cards=cards_html,
    )

    out_path = os.path.join(DOCS_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] Bio page written to {out_path}")


if __name__ == "__main__":
    sample = [{
        "image_url": "https://m.media-amazon.com/images/I/61eDgd5aYML._SL1500_.jpg",
        "title": "Sample Product",
        "category_color": "#2563EB",
        "price": 999,
        "affiliate_link": "https://earnkaro.com/xyz",
    }]
    build_bio_page(sample)
