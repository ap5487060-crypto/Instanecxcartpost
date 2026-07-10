"""
scrape_products.py
Fetches trending / bestseller products from Amazon India across multiple
categories. Returns a clean list of dicts: title, image_url, price,
mrp, discount_pct, product_url, category, category_color.

NOTE: Amazon frequently changes its page structure and blocks bots with
captchas. This scraper uses realistic headers and is written defensively
(skips a category if it fails instead of crashing the whole run). If a
category consistently returns 0 products, the CSS selectors below will
need a small update - check the "selectors" section first.
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
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

# category name -> (amazon bestseller URL, hex color for image theme)
CATEGORIES = {
    "Electronics": ("https://www.amazon.in/gp/bestsellers/electronics", "#2563EB"),
    "Fashion": ("https://www.amazon.in/gp/bestsellers/apparel", "#DB2777"),
    "Home & Kitchen": ("https://www.amazon.in/gp/bestsellers/kitchen", "#059669"),
    "Beauty": ("https://www.amazon.in/gp/bestsellers/beauty", "#9333EA"),
    "Mobiles & Accessories": ("https://www.amazon.in/gp/bestsellers/electronics/1389401031", "#EA580C"),
    "Toys & Baby": ("https://www.amazon.in/gp/bestsellers/toys", "#0891B2"),
    "Sports & Fitness": ("https://www.amazon.in/gp/bestsellers/sports", "#16A34A"),
    "Books": ("https://www.amazon.in/gp/bestsellers/books", "#B45309"),
}

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
POSTED_LOG = os.path.join(DATA_DIR, "posted_products.json")


def load_posted_history():
    if os.path.exists(POSTED_LOG):
        with open(POSTED_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_posted_history(history):
    os.makedirs(DATA_DIR, exist_ok=True)
    # keep last 500 entries only, to stop file growing forever
    history = history[-500:]
    with open(POSTED_LOG, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def clean_price(text):
    if not text:
        return None
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else None


def scrape_category(name, url, color, limit=3):
    """Scrape one bestseller category page, return up to `limit` products."""
    products = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            print(f"[WARN] {name}: got status {resp.status_code}, skipping")
            return products

        soup = BeautifulSoup(resp.text, "lxml")
        items = soup.select("div.p13n-sc-uncoverable-faceout") or soup.select("li.zg-item-immersion")

        for item in items[: limit * 3]:  # grab extra in case some fail parsing
            try:
                title_tag = item.select_one("div._cDEzb_p13n-sc-css-line-clamp-3_g3dy1, .p13n-sc-truncate, span.zg-text-center-align")
                title = title_tag.get_text(strip=True) if title_tag else None

                img_tag = item.select_one("img")
                image_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else None

                link_tag = item.select_one("a.a-link-normal")
                product_url = "https://www.amazon.in" + link_tag["href"] if link_tag and link_tag.has_attr("href") else None

                price_tag = item.select_one("span._cDEzb_p13n-sc-price_3mJ9Z, span.p13n-sc-price")
                price = clean_price(price_tag.get_text()) if price_tag else None

                if not (title and image_url and product_url):
                    continue

                products.append({
                    "title": title[:120],
                    "image_url": image_url,
                    "product_url": product_url.split("?")[0],
                    "price": price,
                    "mrp": None,
                    "discount_pct": None,
                    "category": name,
                    "category_color": color,
                })

                if len(products) >= limit:
                    break
            except Exception as e:
                print(f"[WARN] item parse failed in {name}: {e}")
                continue

        time.sleep(random.uniform(1.5, 3.0))  # polite delay between category requests

    except Exception as e:
        print(f"[ERROR] failed scraping {name}: {e}")

    return products


def get_daily_products(total_needed=8):
    """Pick a rotating subset of categories each day and scrape 1-2 products from each."""
    history = load_posted_history()
    posted_urls = {h["product_url"] for h in history}

    cat_items = list(CATEGORIES.items())
    random.shuffle(cat_items)

    collected = []
    per_category = 2

    for name, (url, color) in cat_items:
        if len(collected) >= total_needed:
            break
        found = scrape_category(name, url, color, limit=per_category + 2)
        fresh = [p for p in found if p["product_url"] not in posted_urls]
        collected.extend(fresh[:per_category])

    collected = collected[:total_needed]

    # update history
    for p in collected:
        history.append({"product_url": p["product_url"], "title": p["title"]})
    save_posted_history(history)

    return collected


if __name__ == "__main__":
    products = get_daily_products()
    print(json.dumps(products, ensure_ascii=False, indent=2))
    print(f"\nTotal products fetched: {len(products)}")
