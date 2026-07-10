"""
update_sheet.py
Appends today's posted products into a Google Sheet, one row per product:
Date | Category | Image (thumbnail formula) | Product Name | Price | Buy Link

Auth: uses a Google Cloud Service Account JSON (same project you already
use for youtube-comment-bot). Share your target Google Sheet with the
service account's email as Editor - that email is auto-generated when you
create the service account, e.g. bot@your-project.iam.gserviceaccount.com.

The Sheet itself should separately be set to "Anyone with link - Viewer"
in normal Google Sheets sharing settings, so the public can view but only
the service account (acting as owner/editor) can write.

Required env vars:
- GOOGLE_SERVICE_ACCOUNT_JSON  (the full JSON key content, as a string)
- GOOGLE_SHEET_ID              (the sheet ID from its URL)
"""

import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")
SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")

HEADER = ["Date", "Category", "Image", "Product Name", "Price", "Buy Link"]


def _get_client():
    creds_dict = json.loads(SERVICE_ACCOUNT_JSON)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)


def append_products(products: list):
    """products: list of dicts with title, price, category, affiliate_link, image_url"""
    if not SHEET_ID or not SERVICE_ACCOUNT_JSON:
        print("[WARN] Sheet ID or service account JSON missing, skipping sheet update")
        return

    client = _get_client()
    sheet = client.open_by_key(SHEET_ID).sheet1

    # ensure header row exists
    existing = sheet.get_all_values()
    if not existing:
        sheet.append_row(HEADER)

    today = datetime.now().strftime("%d-%b-%Y")
    rows = []
    for p in products:
        rows.append([
            today,
            p.get("category", ""),
            f'=IMAGE("{p.get("image_url","")}")',
            p.get("title", ""),
            f'Rs {p["price"]}' if p.get("price") else "",
            p.get("affiliate_link", ""),
        ])

    if rows:
        sheet.append_rows(rows, value_input_option="USER_ENTERED")
        print(f"[OK] Added {len(rows)} rows to sheet")


if __name__ == "__main__":
    sample = [{
        "category": "Electronics",
        "image_url": "https://m.media-amazon.com/images/I/61eDgd5aYML._SL1500_.jpg",
        "title": "Test Product",
        "price": 999,
        "affiliate_link": "https://earnkaro.com/xyz",
    }]
    append_products(sample)
