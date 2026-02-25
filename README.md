# alittlebitofmoney-bot

Semi-automated marketing bot for [alittlebitofmoney.com](https://alittlebitofmoney.com). Posts to Bluesky, X/Twitter, and Nostr, and intelligently searches for relevant conversations to join.

**Please update me when there are feature changes.**

## Features

- **Multi-Platform Broadcasting**: Post announcements to Bluesky, X/Twitter, and Nostr simultaneously
- **GitHub Integration**: Monitor repository commits for announcement-worthy changes
- **Intelligent Search & Reply**: Find relevant conversations on Bluesky and reply when genuinely helpful
- **State Management**: Track posting history, reply limits, and processed commits
- **Human-in-the-Loop**: All posts and replies require user approval before publishing
- **Rate Limiting**: 6-hour minimum between broadcasts, max 10 replies per day

## Architecture

- **State Persistence**: `state.json` tracks bot activity and enforces rate limits
- **Credential Management**: `.env` file for API keys (supports both local and `~/.marketing-bot/`)
- **Claude Code Skill**: Integrates as a Claude Code skill for AI-assisted marketing

## Quick Start

### 1. Install Dependencies

```bash
pip install atproto tweepy pynostr python-dotenv requests --break-system-packages
```

### 2. Configure Credentials

Create `.env` in the repo root or `~/.marketing-bot/.env`:

```bash
# Bluesky
BLUESKY_HANDLE=your.handle.bsky.social
BLUESKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx

# X/Twitter
X_API_KEY=your_api_key
X_API_SECRET=your_api_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_TOKEN_SECRET=your_access_token_secret

# Nostr
NOSTR_PRIVATE_KEY=your_hex_private_key
NOSTR_RELAYS=wss://relay1.com,wss://relay2.com

# GitHub
GITHUB_REPO=owner/repo
```

### 3. Run Marketing Cycle

In Claude Code:
```
run marketing
```

Or manually:
```bash
python state_manager.py read
python github_check.py
python bluesky_post.py "Your announcement here"
python x_post.py "Your announcement here"
python nostr_post.py "Your announcement here"
python bluesky_search.py "search query"
python bluesky_reply.py "at://post/uri" "Your reply"
```

## Marketing Cycle Phases

### Phase 1: Check State
- Load `state.json` to verify rate limits
- Check last broadcast time (6-hour minimum gap)
- Check daily reply count (max 10/day)
- Get last processed commit SHA

### Phase 2: Evaluate Commits
Monitor GitHub for announcement-worthy changes:

**Worth Announcing**:
- New features or endpoint support
- New models added
- Significant documentation improvements
- Pricing changes
- Major performance/reliability improvements

**NOT Worth Announcing**:
- Bug fixes, typo fixes, refactors
- CI/CD changes, dependency updates
- Internal reorganization
- README formatting

### Phase 3: Compose & Broadcast
If there's something worth announcing:

1. Compose platform-specific posts following guidelines
2. Show drafts to user for approval
3. Post to all platforms
4. Record broadcast in state

**Post Guidelines**:
- Sound like a developer, NOT a marketer
- Include concrete details (model name, endpoint, curl snippet)
- Max 2 relevant hashtags
- No emojis except ⚡ for Lightning
- Always end with: https://alittlebitofmoney.com
- **Bluesky**: max 300 characters
- **X/Twitter**: max 280 characters
- **Nostr**: max 500 characters (more detailed)

### Phase 4: Search & Reply (Bluesky)
Find conversations where mentioning the service is genuinely helpful:

**Search Queries** (rotate 3-4 per cycle):
- "OpenAI API no account"
- "pay per request AI"
- "Lightning Network API"
- "API key annoying"
- "AI API micropayments"
- "L402 protocol"
- "Bitcoin AI payment"
- "sats API"

**Reply Criteria** (ALL must be true):
1. Post is <24 hours old
2. Haven't already replied (checked in state)
3. Person has a real question/problem we solve
4. Reply is genuinely helpful even without product mention
5. Mention feels natural, not forced

**Do NOT Reply if**:
- Post is joke/meme/rant
- Promoting competing product
- Only tangential relation
- Connection feels stretched
- Already has 10+ replies

**Safety Limits**: Max 3 replies per cycle, max 10 per day

### Phase 5: Summary
Report to user:
- Commits checked
- Broadcast status (posted/skipped + reason)
- Search results and replies
- Next suggested run time

## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `state_manager.py read` | Load current state | Returns JSON state |
| `state_manager.py record_broadcast "text"` | Record a broadcast | Updates state file |
| `state_manager.py record_reply "uri"` | Record a reply | Updates state file |
| `state_manager.py update_sha "sha"` | Update last commit SHA | Updates state file |
| `github_check.py` | Get recent commits | Returns JSON list of commits |
| `bluesky_post.py "text"` | Post to Bluesky | Returns post URI |
| `bluesky_search.py "query"` | Search Bluesky posts | Returns JSON results |
| `bluesky_reply.py "uri" "text"` | Reply to a Bluesky post | Returns reply URI |
| `x_post.py "text"` | Post to X/Twitter | Returns tweet ID |
| `nostr_post.py "text"` | Post to Nostr relays | Returns event ID |

## State File Schema

`state.json` structure:
```json
{
  "last_broadcast_time": "2026-02-24T12:00:00+00:00",
  "last_commit_sha": "abc123...",
  "last_bluesky_search_time": "2026-02-24T14:30:00+00:00",
  "replied_to_posts": ["at://...", "at://..."],
  "replies_today": 5,
  "replies_today_date": "2026-02-24",
  "post_history": [
    {
      "time": "2026-02-24T12:00:00+00:00",
      "type": "broadcast",
      "content_preview": "Added support for..."
    }
  ]
}
```

## Project Structure

```
.
├── bluesky_post.py       # Post to Bluesky
├── bluesky_reply.py      # Reply on Bluesky
├── bluesky_search.py     # Search Bluesky posts
├── x_post.py             # Post to X/Twitter
├── nostr_post.py         # Post to Nostr relays
├── github_check.py       # Check GitHub commits
├── state_manager.py      # State persistence
├── state.json            # Bot state (auto-created)
├── SKILL.md              # Claude Code skill definition
└── references/
    └── product_doc.md    # Product info for composing posts
```

## Usage with Claude Code

This bot is designed as a Claude Code skill. When active:

1. Say "run marketing" or "marketing cycle"
2. Claude reads state, checks commits, searches conversations
3. Claude makes judgment calls on what's worth posting
4. Claude drafts posts and replies
5. You approve before anything publishes
6. Claude updates state automatically

## Human-in-the-Loop Philosophy

This is NOT a fully automated bot. Every post and reply requires user approval. The AI (Claude) does the thinking and drafting, but YOU have final say. This ensures:
- High-quality, authentic communication
- No spam or off-brand messaging
- Compliance with platform terms of service
- Genuine helpfulness in replies

## Credential Setup

See platform documentation for obtaining credentials:
- **Bluesky**: Settings → App Passwords
- **X/Twitter**: [developer.twitter.com](https://developer.twitter.com)
- **Nostr**: Use a client to generate keypair
- **GitHub**: Personal access token or read-only public access

## License

See LICENSE file.

## Contributing

See WORKLOG.md for recent changes and development history.
