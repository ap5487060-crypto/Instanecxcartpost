"""
upload_image.py
Uploads a locally generated image to imgbb (free image hosting).
Returns a public HTTPS URL which Instagram/Facebook Graph API can access.

Get your free imgbb API key at: https://api.imgbb.com/
(sign up free → dashboard → Get API Key)

Required env var: IMGBB_API_KEY
"""

import os
import base64
import requests

IMGBB_API_KEY = os.environ.get("IMGBB_API_KEY", "")


def upload_image(image_path: str) -> str | None:
    """Upload image file to imgbb, return public URL or None."""
    if not IMGBB_API_KEY:
        print("[ERROR] IMGBB_API_KEY not set")
        return None

    try:
        with open(image_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode("utf-8")

        resp = requests.post(
            "https://api.imgbb.com/1/upload",
            data={
                "key": IMGBB_API_KEY,
                "image": img_data,
                "expiration": 86400,  # 24 hours - enough for Instagram to fetch
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        url = data["data"]["url"]
        print(f"[OK] Image uploaded: {url}")
        return url

    except Exception as e:
        print(f"[ERROR] imgbb upload failed: {e}")
        return None


if __name__ == "__main__":
    # test with a local image path
    test_path = "/tmp/out/sample.jpg"
    if os.path.exists(test_path):
        print(upload_image(test_path))
    else:
        print("Run generate_image.py first to create a test image")
