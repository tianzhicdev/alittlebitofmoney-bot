#!/usr/bin/env python3
"""
State manager for marketing bot.
Persists state to ~/.marketing-bot/state.json across sessions.

Usage:
    python state_manager.py read
    python state_manager.py record_broadcast "content preview text"
    python state_manager.py record_reply "at://did:plc:xxx/app.bsky.feed.post/yyy"
    python state_manager.py update_sha "abc123def456"
"""

import json
import sys
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Check current directory first, then ~/.marketing-bot
if Path("state.json").exists() or not (Path.home() / ".marketing-bot").exists():
    STATE_DIR = Path(".")
else:
    STATE_DIR = Path.home() / ".marketing-bot"
STATE_FILE = STATE_DIR / "state.json"

DEFAULT_STATE = {
    "last_broadcast_time": None,
    "last_commit_sha": None,
    "last_bluesky_search_time": None,
    "replied_to_posts": [],
    "replies_today": 0,
    "replies_today_date": None,
    "post_history": []
}


def load_state():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            state = json.load(f)
        # Merge with defaults for any missing keys
        for key, val in DEFAULT_STATE.items():
            if key not in state:
                state[key] = val
        return state
    return dict(DEFAULT_STATE)


def save_state(state):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def can_broadcast(state):
    if state["last_broadcast_time"] is None:
        return True
    last = datetime.fromisoformat(state["last_broadcast_time"])
    return datetime.now(timezone.utc) - last > timedelta(hours=6)


def replies_remaining_today(state):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if state.get("replies_today_date") != today:
        return 10  # reset for new day
    return max(0, 10 - state.get("replies_today", 0))


def record_broadcast(state, content_preview):
    now = datetime.now(timezone.utc).isoformat()
    state["last_broadcast_time"] = now
    state["post_history"].append({
        "time": now,
        "type": "broadcast",
        "content_preview": content_preview[:200]
    })
    # Keep only last 50 entries
    state["post_history"] = state["post_history"][-50:]
    save_state(state)
    return state


def record_reply(state, post_uri):
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    
    state["replied_to_posts"].append(post_uri)
    # Keep only last 500 URIs
    state["replied_to_posts"] = state["replied_to_posts"][-500:]
    
    if state.get("replies_today_date") != today:
        state["replies_today"] = 1
        state["replies_today_date"] = today
    else:
        state["replies_today"] = state.get("replies_today", 0) + 1
    
    state["last_bluesky_search_time"] = now.isoformat()
    save_state(state)
    return state


def update_sha(state, sha):
    state["last_commit_sha"] = sha
    save_state(state)
    return state


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: state_manager.py <command> [args]"}))
        sys.exit(1)
    
    command = sys.argv[1]
    state = load_state()
    
    if command == "read":
        # Add computed fields
        state["_can_broadcast"] = can_broadcast(state)
        state["_replies_remaining_today"] = replies_remaining_today(state)
        print(json.dumps(state, indent=2))
    
    elif command == "record_broadcast":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Usage: state_manager.py record_broadcast <content>"}))
            sys.exit(1)
        state = record_broadcast(state, sys.argv[2])
        print(json.dumps({"ok": True, "last_broadcast_time": state["last_broadcast_time"]}))
    
    elif command == "record_reply":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Usage: state_manager.py record_reply <post_uri>"}))
            sys.exit(1)
        state = record_reply(state, sys.argv[2])
        print(json.dumps({"ok": True, "replies_today": state["replies_today"]}))
    
    elif command == "update_sha":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Usage: state_manager.py update_sha <sha>"}))
            sys.exit(1)
        state = update_sha(state, sys.argv[2])
        print(json.dumps({"ok": True, "last_commit_sha": state["last_commit_sha"]}))
    
    else:
        print(json.dumps({"error": f"Unknown command: {command}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
