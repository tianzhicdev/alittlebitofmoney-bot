#!/usr/bin/env python3
"""
Post to X/Twitter (free tier, post only).

Usage:
    python x_post.py "Your tweet text here"
"""

import json
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Try multiple .env locations
for env_path in [Path(".env"), Path.home() / ".marketing-bot" / ".env"]:
    if env_path.exists():
        load_dotenv(env_path, override=True)
        break
else:
    load_dotenv(override=True)  # fall back to environment variables

API_KEY = os.getenv("X_API_KEY")
API_SECRET = os.getenv("X_API_SECRET")
ACCESS_TOKEN = os.getenv("X_API_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("X_API_ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("X_API_BEAR")


def post(text):
    import tweepy

    # Use OAuth 1.0a User Context (works with pay-per-use and free tier)
    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
        print(json.dumps({"error": "X_API_KEY, X_API_SECRET, X_API_ACCESS_TOKEN, X_API_ACCESS_TOKEN_SECRET must be set"}))
        sys.exit(1)

    client = tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )

    response = client.create_tweet(text=text)

    print(json.dumps({
        "ok": True,
        "platform": "x",
        "tweet_id": str(response.data["id"]),
        "text_length": len(text)
    }))


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: x_post.py <text>"}))
        sys.exit(1)

    text = sys.argv[1]
    if len(text) > 280:
        print(json.dumps({"error": f"Text too long: {len(text)} chars (max 280)"}))
        sys.exit(1)

    post(text)


if __name__ == "__main__":
    main()
