"""
post_facebook.py
Posts an image + caption + direct buy link to a Facebook Page using the
Graph API. Facebook (unlike Instagram feed) allows a clickable link
directly in the post, so we include the affiliate link right in the message.

Requires:
- FB_PAGE_ACCESS_TOKEN   Page access token (from the same Facebook App)
- FB_PAGE_ID             Facebook Page ID
"""

import os
import requests

GRAPH_VERSION = "v19.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_VERSION}"

FB_PAGE_ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN", "")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "")


def post_photo(image_url: str, message: str):
    url = f"{BASE_URL}/{FB_PAGE_ID}/photos"
    params = {
        "url": image_url,
        "caption": message,
        "access_token": FB_PAGE_ACCESS_TOKEN,
    }
    resp = requests.post(url, data=params, timeout=20)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    test_url = "https://example.com/sample.jpg"
    print(post_photo(test_url, "Test product - Buy now: https://example.com"))
