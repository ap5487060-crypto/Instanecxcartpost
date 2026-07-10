"""
post_instagram.py
Posts an image to Instagram Feed and Story using the Instagram Graph API.

Requires (set as environment variables / GitHub Secrets):
- IG_ACCESS_TOKEN        long-lived Facebook/Instagram access token
- IG_BUSINESS_ACCOUNT_ID Instagram Business Account ID

Images must be reachable via a public HTTPS URL (Instagram Graph API cannot
accept raw file uploads for this endpoint) - so generated images are first
pushed to the repo's GitHub Pages `docs/` folder (or any public host) and
then this script uses that public URL.
"""

import os
import time
import requests

GRAPH_VERSION = "v19.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_VERSION}"

IG_ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN", "")
IG_BUSINESS_ACCOUNT_ID = os.environ.get("IG_BUSINESS_ACCOUNT_ID", "")


def _create_media_container(image_url: str, caption: str = "", is_story: bool = False):
    url = f"{BASE_URL}/{IG_BUSINESS_ACCOUNT_ID}/media"
    params = {
        "image_url": image_url,
        "access_token": IG_ACCESS_TOKEN,
    }
    if is_story:
        params["media_type"] = "STORIES"
    else:
        params["caption"] = caption

    resp = requests.post(url, data=params, timeout=20)
    resp.raise_for_status()
    return resp.json()["id"]


def _publish_media(creation_id: str):
    url = f"{BASE_URL}/{IG_BUSINESS_ACCOUNT_ID}/media_publish"
    params = {"creation_id": creation_id, "access_token": IG_ACCESS_TOKEN}
    resp = requests.post(url, data=params, timeout=20)
    resp.raise_for_status()
    return resp.json()


def post_feed_image(image_url: str, caption: str):
    creation_id = _create_media_container(image_url, caption=caption, is_story=False)
    time.sleep(3)  # give Instagram a moment to process the container
    return _publish_media(creation_id)


def post_story_image(image_url: str):
    creation_id = _create_media_container(image_url, is_story=True)
    time.sleep(3)
    return _publish_media(creation_id)


if __name__ == "__main__":
    # quick manual test - replace with a real public image URL
    test_url = "https://example.com/sample.jpg"
    print(post_feed_image(test_url, "Test caption #test"))
