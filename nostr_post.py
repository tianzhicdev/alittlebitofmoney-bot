#!/usr/bin/env python3
"""
Post a note to Nostr relays.

Usage:
    python nostr_post.py "Your note text here"

NOTE FOR CODING AGENT: The Nostr Python ecosystem changes rapidly.
As of Feb 2026, check which library is most maintained:
- pynostr (pip install pynostr)
- nostr-sdk (pip install nostr-sdk) — Rust bindings, more reliable
- python-nostr (pip install python-nostr) — older

This script uses pynostr as a starting point. If it's unmaintained,
swap to nostr-sdk. The core logic is the same: create a kind 1 event,
sign it with the private key, publish to relays.

If ALL Python Nostr libraries are broken, fall back to a simple
websocket approach — Nostr is just JSON over WebSocket:

    import websockets, json, hashlib, secp256k1
    event = {"kind": 1, "content": text, "tags": [...], ...}
    # sign with secp256k1
    # send ["EVENT", event] to each relay
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

PRIVATE_KEY = os.getenv("NOSTR_PRIVATE_KEY")
RELAYS = os.getenv("NOSTR_RELAYS", "wss://relay.damus.io,wss://relay.primal.net,wss://nos.lol").split(",")


def post(text):
    try:
        from nostr_sdk import Keys, Client, EventBuilder, NostrSigner, RelayUrl
        import asyncio

        if not PRIVATE_KEY:
            print(json.dumps({"error": "NOSTR_PRIVATE_KEY must be set in ~/.marketing-bot/.env"}))
            sys.exit(1)

        async def publish():
            # Parse private key (handles nsec format)
            if PRIVATE_KEY.startswith("nsec"):
                keys = Keys.parse(PRIVATE_KEY)
            else:
                keys = Keys.from_hex(PRIVATE_KEY)

            # Create client with keys as signer
            signer = NostrSigner.keys(keys)
            client = Client(signer)

            # Add relays
            for relay in RELAYS:
                relay_url = RelayUrl.parse(relay.strip())
                await client.add_relay(relay_url)

            await client.connect()

            # Create and publish event
            event_builder = EventBuilder.text_note(text)
            output = await client.send_event_builder(event_builder)

            pubkey = keys.public_key()

            await client.disconnect()

            return {
                "ok": True,
                "platform": "nostr",
                "event_id": output.id.to_hex(),
                "pubkey": pubkey.to_hex(),
                "relays": [r.strip() for r in RELAYS],
                "text_length": len(text)
            }

        result = asyncio.run(publish())
        print(json.dumps(result))

    except ImportError:
        print(json.dumps({
            "error": "nostr-sdk not installed. Run: pip install nostr-sdk"
        }))
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: nostr_post.py <text>"}))
        sys.exit(1)

    text = sys.argv[1]
    post(text)


if __name__ == "__main__":
    main()
