# WORKLOG

Development history and feature changes for alittlebitofmoney-bot.

## 2026-02-24

### Documentation
- Created comprehensive README.md with full feature documentation
- Documented marketing cycle phases and decision criteria
- Added script reference and state file schema
- Created WORKLOG.md for tracking changes

### Repository Setup
- Committed initial bot implementation to GitHub
- Added .gitignore for sensitive files (.env, .DS_Store, __pycache__)
- Set up deployment to macmini production environment
- Removed .env from git history (security fix)

### Initial Implementation
- Built multi-platform posting: Bluesky, X/Twitter, Nostr
- Implemented state management with JSON persistence
- Added GitHub commit monitoring
- Created Bluesky search and reply functionality
- Added rate limiting (6-hour broadcast gap, 10 replies/day)
- Built human-in-the-loop approval workflow

## Features Implemented

### Social Media Integration
- **Bluesky**: Post, search, reply with atproto SDK
- **X/Twitter**: Post with Tweepy
- **Nostr**: Post to multiple relays with pynostr
- Rich text support for links and mentions

### State Management
- Persistent state tracking in `state.json`
- Broadcast time tracking with 6-hour cooldown
- Daily reply counter with automatic reset
- Post history (last 50 entries)
- Replied-to URIs tracking (last 500)

### GitHub Integration
- Commit monitoring via GitHub API
- SHA tracking to detect new commits
- Structured commit data (message, files, dates)

### Intelligent Reply System
- Bluesky conversation search
- Reply criteria evaluation
- Duplicate reply prevention
- Rate limiting per day and per cycle

### Claude Code Skill
- SKILL.md definition for Claude Code integration
- Detailed phase-by-phase instructions
- Decision-making criteria
- Post composition guidelines

---

**Note**: Update this log whenever you add features, fix bugs, or make significant changes.
