"""
post_instagram.py - Updated with detailed error logging
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
    
    # Log exact error for debugging
    if not resp.ok:
        print(f"[ERROR DETAIL] Status: {resp.status_code}")
        print(f"[ERROR DETAIL] Response: {resp.text}")
    
    resp.raise_for_status()
    return resp.json()["id"]


def _publish_media(creation_id: str):
    url = f"{BASE_URL}/{IG_BUSINESS_ACCOUNT_ID}/media_publish"
    params = {"creation_id": creation_id, "access_token": IG_ACCESS_TOKEN}
    resp = requests.post(url, data=params, timeout=20)
    
    if not resp.ok:
        print(f"[ERROR DETAIL] Publish Status: {resp.status_code}")
        print(f"[ERROR DETAIL] Publish Response: {resp.text}")
    
    resp.raise_for_status()
    return resp.json()


def post_feed_image(image_url: str, caption: str):
    creation_id = _create_media_container(image_url, caption=caption, is_story=False)
    time.sleep(3)
    return _publish_media(creation_id)


def post_story_image(image_url: str):
    creation_id = _create_media_container(image_url, is_story=True)
    time.sleep(3)
    return _publish_media(creation_id)
