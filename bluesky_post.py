#!/usr/bin/env python3
"""
Post to Bluesky.

Usage:
    python bluesky_post.py "Your post text here"
"""

import json
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Try multiple .env locations
for env_path in [Path(".env"), Path.home() / ".marketing-bot" / ".env"]:
    if env_path.exists():
        load_dotenv(env_path)
        break
else:
    load_dotenv()  # fall back to environment variables

HANDLE = os.getenv("BLUESKY_HANDLE")
APP_PASSWORD = os.getenv("BLUESKY_APP_PASSWORD")


def post(text):
    from atproto import Client, client_utils

    if not HANDLE or not APP_PASSWORD:
        print(json.dumps({"error": "BLUESKY_HANDLE and BLUESKY_APP_PASSWORD must be set in ~/.marketing-bot/.env"}))
        sys.exit(1)

    client = Client()
    client.login(HANDLE, APP_PASSWORD)

    # Use TextBuilder for rich text (auto-detects links and mentions)
    tb = client_utils.TextBuilder()
    tb.text(text)

    response = client.send_post(tb)

    print(json.dumps({
        "ok": True,
        "platform": "bluesky",
        "uri": response.uri,
        "cid": response.cid,
        "text_length": len(text)
    }))


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: bluesky_post.py <text>"}))
        sys.exit(1)

    text = sys.argv[1]
    if len(text) > 300:
        print(json.dumps({"error": f"Text too long: {len(text)} chars (max 300)"}))
        sys.exit(1)

    post(text)


if __name__ == "__main__":
    main()
