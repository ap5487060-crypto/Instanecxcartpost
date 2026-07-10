"""
scrape_products.py
Fetches trending bestseller products from Amazon India.
- Har category se 1 product guaranteed
- Sirf real product pages (/dp/ URLs)
- Sahi price (decimal handled)
- Duplicate prevention
"""

import requests
from bs4 import BeautifulSoup
import random
import time
import re
import json
import os

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Category name → (URL, color)
CATEGORIES = {
    "Electronics":          ("https://www.amazon.in/gp/bestsellers/electronics",            "#2563EB"),
    "Mobiles":              ("https://www.amazon.in/gp/bestsellers/electronics/1389401031", "#EA580C"),
    "Fashion":              ("https://www.amazon.in/gp/bestsellers/apparel",                "#DB2777"),
    "Home & Kitchen":       ("https://www.amazon.in/gp/bestsellers/kitchen",                "#059669"),
    "Beauty":               ("https://www.amazon.in/gp/bestsellers/beauty",                 "#9333EA"),
    "Sports & Fitness":     ("https://www.amazon.in/gp/bestsellers/sports",                 "#16A34A"),
    "Toys & Baby":          ("https://www.amazon.in/gp/bestsellers/toys",                   "#0891B2"),
    "Books":                ("https://www.amazon.in/gp/bestsellers/books",                  "#B45309"),
}

DATA_DIR  = os.path.join(os.path.dirname(__file__), "..", "data")
POSTED_LOG = os.path.join(DATA_DIR, "posted_products.json")


# ── Helpers ────────────────────────────────────────────────────────────────

def load_posted_history():
    if os.path.exists(POSTED_LOG):
        with open(POSTED_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_posted_history(history):
    os.makedirs(DATA_DIR, exist_ok=True)
    history = history[-500:]
    with open(POSTED_LOG, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def clean_price(text):
    """₹1,299.00  →  1299   |   ₹50,000.00  →  50000"""
    if not text:
        return None
    cleaned = re.sub(r"[^\d.]", "", text.strip())
    try:
        return int(float(cleaned))
    except Exception:
        return None


def is_real_product(url: str) -> bool:
    """Only allow Amazon product detail pages."""
    if not url:
        return False
    return "/dp/" in url and "/apay/" not in url and "/gp/" not in url


def get_text(tag):
    return tag.get_text(strip=True) if tag else None


# ── Core scraper ───────────────────────────────────────────────────────────

def scrape_category(name: str, url: str, color: str, posted_urls: set, limit: int = 3):
    """
    Scrape one Amazon bestseller category page.
    Returns up to `limit` fresh (not yet posted) products.
    """
    products = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        if resp.status_code != 200:
            print(f"  [WARN] {name}: HTTP {resp.status_code}")
            return products

        soup = BeautifulSoup(resp.text, "lxml")

        # Try multiple container selectors (Amazon changes these periodically)
        items = (
            soup.select("div.p13n-sc-uncoverable-faceout")
            or soup.select("li.zg-item-immersion")
            or soup.select("div[data-asin]")
            or soup.select("div.zg-grid-general-faceout")
        )

        if not items:
            print(f"  [WARN] {name}: No items found (page structure may have changed)")
            return products

        print(f"  {name}: found {len(items)} raw items")

        for item in items:
            if len(products) >= limit:
                break
            try:
                # ── Title ────────────────────────────────────────────────
                title_tag = (
                    item.select_one("div._cDEzb_p13n-sc-css-line-clamp-3_g3dy1")
                    or item.select_one("div._cDEzb_p13n-sc-css-line-clamp-1_1Fn1y")
                    or item.select_one(".p13n-sc-truncate")
                    or item.select_one("span.zg-text-center-align")
                    or item.select_one("a span")
                    or item.select_one(".a-truncate-full")
                )
                title = get_text(title_tag)

                # ── Image ────────────────────────────────────────────────
                img_tag = item.select_one("img.a-dynamic-image") or item.select_one("img")
                image_url = None
                if img_tag:
                    image_url = (
                        img_tag.get("src")
                        or img_tag.get("data-src")
                    )
                    # Try to get higher-res image
                    if image_url and "_SL" in image_url:
                        image_url = re.sub(r"_SL\d+_", "_SL500_", image_url)

                # ── Product URL ──────────────────────────────────────────
                link_tag = item.select_one("a.a-link-normal[href*='/dp/']") or item.select_one("a[href*='/dp/']")
                product_url = None
                if link_tag and link_tag.get("href"):
                    href = link_tag["href"]
                    if href.startswith("/"):
                        href = "https://www.amazon.in" + href
                    # Clean tracking params
                    product_url = href.split("?")[0].split("/ref=")[0]

                # ── Price ────────────────────────────────────────────────
                price_tag = (
                    item.select_one("span._cDEzb_p13n-sc-price_3mJ9Z")
                    or item.select_one("span.p13n-sc-price")
                    or item.select_one("span.a-price-whole")
                    or item.select_one("span.a-offscreen")
                )
                price = clean_price(get_text(price_tag))

                # ── Validation ───────────────────────────────────────────
                if not title:
                    continue
                if not is_real_product(product_url):
                    print(f"    SKIP (not a product page): {product_url}")
                    continue
                if product_url in posted_urls:
                    print(f"    SKIP (already posted): {title[:40]}")
                    continue
                if not image_url or image_url.startswith("data:"):
                    continue

                products.append({
                    "title":          title[:120],
                    "image_url":      image_url,
                    "product_url":    product_url,
                    "price":          price,
                    "mrp":            None,
                    "discount_pct":   None,
                    "category":       name,
                    "category_color": color,
                })
                print(f"    ✅ {title[:50]} | Rs {price}")

            except Exception as e:
                print(f"    [WARN] Item parse error: {e}")
                continue

        # Polite delay between requests
        time.sleep(random.uniform(2.0, 4.0))

    except Exception as e:
        print(f"  [ERROR] {name} scrape failed: {e}")

    return products


# ── Main public function ───────────────────────────────────────────────────

def get_daily_products(total_needed: int = 8):
    """
    Fetch today's products.
    Strategy: rotate through ALL categories, 1 product each,
    until total_needed is reached. This guarantees category variety.
    """
    history     = load_posted_history()
    posted_urls = {h["product_url"] for h in history}

    cat_items = list(CATEGORIES.items())
    random.shuffle(cat_items)          # different order each day

    collected = []

    print(f"\nFetching {total_needed} products from {len(cat_items)} categories...\n")

    # Pass 1 — 1 product per category (variety guaranteed)
    for name, (url, color) in cat_items:
        if len(collected) >= total_needed:
            break
        print(f"[{name}]")
        found = scrape_category(name, url, color, posted_urls, limit=4)
        if found:
            collected.append(found[0])
            posted_urls.add(found[0]["product_url"])

    # Pass 2 — if still short, take 2nd product from each category
    if len(collected) < total_needed:
        print("\nPass 2 — fetching extras to fill quota...")
        for name, (url, color) in cat_items:
            if len(collected) >= total_needed:
                break
            found = scrape_category(name, url, color, posted_urls, limit=4)
            extras = [p for p in found if p["product_url"] not in posted_urls]
            if extras:
                collected.append(extras[0])
                posted_urls.add(extras[0]["product_url"])

    collected = collected[:total_needed]

    # Save to history (duplicate prevention)
    for p in collected:
        history.append({"product_url": p["product_url"], "title": p["title"]})
    save_posted_history(history)

    print(f"\n✅ Total products ready: {len(collected)}/{total_needed}")
    return collected


# ── Quick test ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    products = get_daily_products(8)
    print("\n" + "="*60)
    for i, p in enumerate(products, 1):
        print(f"{i}. [{p['category']}] {p['title'][:50]}")
        print(f"   Price: Rs {p['price']} | URL: {p['product_url'][:60]}")
    print("="*60)
