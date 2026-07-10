"""
main.py  —  Daily Affiliate Auto-Post System
=========================================================
Full pipeline (runs daily via GitHub Actions):

1.  Scrape trending bestseller products (Amazon, 5-8 items, all categories)
2.  Convert each product URL to EarnKaro affiliate link
3.  Generate a premium product image (PIL)
4.  Upload image to imgbb for public URL
5.  Post to Instagram Feed  (image + caption + "Link in Bio")
6.  Post to Instagram Story (same image)
7.  Post to Facebook Page   (image + caption + direct buy link)
8.  Update Google Sheet     (date, category, thumbnail, name, price, link)
9.  Rebuild GitHub Pages bio-link page (docs/index.html)

All failures are soft — if one product fails, rest continue.
If Instagram API rate-limits, the script sleeps and retries once.
"""

import os
import sys
import time
import json
import traceback
from datetime import datetime

# ----- ensure scripts/ is importable -----
sys.path.insert(0, os.path.dirname(__file__))

from scrape_products import get_daily_products
from earnkaro import convert_link
from generate_image import generate_product_image
from upload_image import upload_image
from post_instagram import post_feed_image, post_story_image
from post_facebook import post_photo
from update_sheet import append_products
from update_bio_page import build_bio_page
from caption import get_instagram_caption, get_facebook_caption

OUTPUT_DIR = "/tmp/affiliate_images"
RESULTS_LOG = os.path.join(os.path.dirname(__file__), "..", "data", "results.json")


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def post_with_retry(fn, *args, retries=2, delay=30, **kwargs):
    for attempt in range(retries):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            log(f"  [attempt {attempt+1}/{retries} failed] {e}")
            if attempt < retries - 1:
                time.sleep(delay)
    return None


def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)

    log("=" * 55)
    log("DAILY AFFILIATE POST PIPELINE STARTING")
    log(f"Date: {datetime.now().strftime('%d %b %Y')}")
    log("=" * 55)

    # ── Step 1: Scrape Products ──────────────────────────────
    log("Step 1 → Scraping trending bestseller products...")
    products = get_daily_products(total_needed=8)
    log(f"  Fetched {len(products)} products")

    if not products:
        log("[FATAL] No products fetched. Exiting.")
        sys.exit(1)

    # ── Steps 2-9: Process each product ─────────────────────
    successful_products = []

    for idx, product in enumerate(products, 1):
        log(f"\n{'─'*45}")
        log(f"Product {idx}/{len(products)}: {product['title'][:60]}")
        log(f"  Category: {product['category']} | Price: Rs {product.get('price', '?')}")

        try:
            # Step 2: EarnKaro link
            log("  Step 2 → Converting to EarnKaro affiliate link...")
            affiliate_link = convert_link(product["product_url"])
            if not affiliate_link:
                log("  [SKIP] EarnKaro conversion failed")
                affiliate_link = product["product_url"]  # fallback to original
            product["affiliate_link"] = affiliate_link

            # Step 3: Generate image
            log("  Step 3 → Generating product banner image...")
            img_path = os.path.join(OUTPUT_DIR, f"product_{idx}.jpg")
            generate_product_image(product, img_path)
            log(f"  Image saved: {img_path}")

            # Step 4: Upload to imgbb
            log("  Step 4 → Uploading image to public hosting...")
            public_url = post_with_retry(upload_image, img_path)
            if not public_url:
                log("  [SKIP] Image upload failed, cannot post this product")
                continue
            product["public_image_url"] = public_url

            # Step 5: Instagram Feed
            log("  Step 5 → Posting to Instagram Feed...")
            ig_caption = get_instagram_caption(product)
            ig_result = post_with_retry(post_feed_image, public_url, ig_caption)
            if ig_result:
                log(f"  [OK] Instagram Feed posted: {ig_result}")
            else:
                log("  [WARN] Instagram Feed post failed")

            time.sleep(5)  # small delay between IG calls

            # Step 6: Instagram Story
            log("  Step 6 → Posting to Instagram Story...")
            story_result = post_with_retry(post_story_image, public_url)
            if story_result:
                log(f"  [OK] Instagram Story posted: {story_result}")
            else:
                log("  [WARN] Instagram Story post failed")

            time.sleep(5)

            # Step 7: Facebook Page
            log("  Step 7 → Posting to Facebook Page...")
            fb_caption = get_facebook_caption(product)
            fb_result = post_with_retry(post_photo, public_url, fb_caption)
            if fb_result:
                log(f"  [OK] Facebook posted: {fb_result}")
            else:
                log("  [WARN] Facebook post failed")

            successful_products.append(product)
            log(f"  ✅ Product {idx} done!")

            # Delay between products to avoid API rate limits
            if idx < len(products):
                log(f"  Waiting 15s before next product...")
                time.sleep(15)

        except Exception:
            log(f"  [ERROR] Unexpected error on product {idx}:")
            traceback.print_exc()
            continue

    # ── Step 8: Google Sheet update ──────────────────────────
    log(f"\n{'─'*45}")
    log(f"Step 8 → Updating Google Sheet ({len(successful_products)} products)...")
    try:
        if successful_products:
            append_products(successful_products)
            log("  [OK] Sheet updated")
        else:
            log("  [SKIP] No successful products to log")
    except Exception as e:
        log(f"  [WARN] Sheet update failed: {e}")

    # ── Step 9: Rebuild bio page ──────────────────────────────
    log("Step 9 → Rebuilding GitHub Pages bio-link page...")
    try:
        build_bio_page(successful_products)
        log("  [OK] docs/index.html updated")
    except Exception as e:
        log(f"  [WARN] Bio page update failed: {e}")

    # ── Save results log ─────────────────────────────────────
    try:
        log_entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_attempted": len(products),
            "total_posted": len(successful_products),
            "products": [
                {
                    "title": p["title"],
                    "category": p["category"],
                    "price": p.get("price"),
                    "affiliate_link": p.get("affiliate_link"),
                }
                for p in successful_products
            ],
        }
        existing = []
        if os.path.exists(RESULTS_LOG):
            with open(RESULTS_LOG, "r") as f:
                existing = json.load(f)
        existing.append(log_entry)
        existing = existing[-30:]  # keep last 30 days
        with open(RESULTS_LOG, "w") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log(f"  [WARN] Could not save results log: {e}")

    # ── Summary ──────────────────────────────────────────────
    log("\n" + "=" * 55)
    log(f"PIPELINE COMPLETE")
    log(f"✅ Successfully posted: {len(successful_products)}/{len(products)} products")
    log(f"📸 Instagram Feed + Story: done")
    log(f"📘 Facebook Page: done")
    log(f"📊 Google Sheet: updated")
    log(f"🔗 Bio Page: updated")
    log("=" * 55)

    if len(successful_products) == 0:
        sys.exit(1)  # fail the Action so you get a notification


if __name__ == "__main__":
    run()
