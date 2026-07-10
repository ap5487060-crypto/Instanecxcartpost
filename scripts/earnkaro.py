"""
earnkaro.py - EarnKaro affiliate link converter
API format confirmed from user's dashboard.
"""

import os
import requests
import json

EARNKARO_API_KEY = os.environ.get("EARNKARO_API_KEY", "")
EARNKARO_ENDPOINT = "https://ekaro-api.affiliaters.in/api/converter/public"


def convert_link(product_url: str) -> str | None:
    if not EARNKARO_API_KEY:
        print("[ERROR] EARNKARO_API_KEY not set")
        return None

    headers = {
        "Authorization": f"Bearer {EARNKARO_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = json.dumps({
        "deal": product_url,
        "convert_option": "convert_only"
    })

    try:
        resp = requests.post(EARNKARO_ENDPOINT, data=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        print(f"[EarnKaro] response: {data}")

        # Try multiple response key possibilities
        link = (
            data.get("data")
            or data.get("shortUrl")
            or data.get("short_url")
            or data.get("url")
            or data.get("converted_url")
            or data.get("profit_link")
        )
        if isinstance(link, dict):
            link = link.get("url") or link.get("shortUrl") or link.get("converted_url")

        if link:
            print(f"[OK] EarnKaro link: {link}")
        else:
            print(f"[WARN] Could not extract link from response: {data}")
        return link

    except Exception as e:
        print(f"[ERROR] EarnKaro failed for {product_url}: {e}")
        return None


if __name__ == "__main__":
    test = "https://www.amazon.in/dp/B08N5WRWNW"
    print(convert_link(test))
