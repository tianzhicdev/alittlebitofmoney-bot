#!/usr/bin/env python3
"""
Search Bluesky for posts matching a query.

Usage:
    python bluesky_search.py "query text"
    python bluesky_search.py "query text" 25    # with limit
"""

import json
import sys
import os
from datetime import datetime, timezone, timedelta
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


def search(query, limit=25):
    from atproto import Client

    if not HANDLE or not APP_PASSWORD:
        print(json.dumps({"error": "BLUESKY_HANDLE and BLUESKY_APP_PASSWORD must be set"}))
        sys.exit(1)

    client = Client()
    client.login(HANDLE, APP_PASSWORD)

    response = client.app.bsky.feed.search_posts(
        params={"q": query, "limit": limit, "sort": "latest"}
    )

    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    results = []

    for post in response.posts:
        created = post.record.created_at
        # Parse the created_at timestamp
        if isinstance(created, str):
            # Handle various ISO formats (Python fromisoformat only handles up to 6 decimal places)
            created_clean = created.replace("Z", "+00:00")
            # Truncate microseconds to 6 digits if longer
            if "." in created_clean and "+" in created_clean:
                parts = created_clean.split(".")
                microsecs_and_tz = parts[1].split("+")
                if len(microsecs_and_tz[0]) > 6:
                    microsecs_and_tz[0] = microsecs_and_tz[0][:6]
                created_clean = parts[0] + "." + "+".join(microsecs_and_tz)
            created_dt = datetime.fromisoformat(created_clean)
        else:
            created_dt = created

        # Only include posts from last 24 hours
        if created_dt.tzinfo and created_dt < cutoff:
            continue

        results.append({
            "uri": post.uri,
            "cid": post.cid,
            "text": post.record.text,
            "author_handle": post.author.handle,
            "author_display_name": post.author.display_name or post.author.handle,
            "created_at": str(created),
            "like_count": post.like_count or 0,
            "reply_count": post.reply_count or 0,
            "repost_count": post.repost_count or 0,
        })

    print(json.dumps({
        "query": query,
        "result_count": len(results),
        "results": results
    }, indent=2))


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: bluesky_search.py <query> [limit]"}))
        sys.exit(1)

    query = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    search(query, limit)


if __name__ == "__main__":
    main()
