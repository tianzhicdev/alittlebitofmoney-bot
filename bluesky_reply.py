#!/usr/bin/env python3
"""
Reply to a Bluesky post.

Usage:
    python bluesky_reply.py "at://did:plc:xxx/app.bsky.feed.post/yyy" "reply text"
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


def reply(parent_uri, text):
    from atproto import Client, models, client_utils

    if not HANDLE or not APP_PASSWORD:
        print(json.dumps({"error": "BLUESKY_HANDLE and BLUESKY_APP_PASSWORD must be set"}))
        sys.exit(1)

    client = Client()
    client.login(HANDLE, APP_PASSWORD)

    # Resolve the parent post to get its CID and determine the thread root
    # Parse the URI: at://did/collection/rkey
    parts = parent_uri.replace("at://", "").split("/")
    if len(parts) < 3:
        print(json.dumps({"error": f"Invalid post URI: {parent_uri}"}))
        sys.exit(1)

    repo = parts[0]
    collection = parts[1]
    rkey = parts[2]

    # Get the parent post thread to find root
    thread = client.app.bsky.feed.get_post_thread(
        params={"uri": parent_uri}
    )

    parent_post = thread.thread.post
    parent_ref = models.create_strong_ref(parent_post)

    # Determine root: if parent is itself a reply, use its root; otherwise parent IS root
    if hasattr(parent_post.record, 'reply') and parent_post.record.reply:
        root_ref = parent_post.record.reply.root
    else:
        root_ref = parent_ref

    # Build rich text
    tb = client_utils.TextBuilder()
    tb.text(text)

    response = client.send_post(
        tb,
        reply_to=models.AppBskyFeedPost.ReplyRef(
            parent=parent_ref,
            root=root_ref,
        )
    )

    print(json.dumps({
        "ok": True,
        "platform": "bluesky",
        "type": "reply",
        "parent_uri": parent_uri,
        "reply_uri": response.uri,
        "reply_cid": response.cid,
    }))


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: bluesky_reply.py <parent_uri> <text>"}))
        sys.exit(1)

    parent_uri = sys.argv[1]
    text = sys.argv[2]

    if len(text) > 300:
        print(json.dumps({"error": f"Text too long: {len(text)} chars (max 300)"}))
        sys.exit(1)

    reply(parent_uri, text)


if __name__ == "__main__":
    main()
