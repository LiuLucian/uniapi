# Reddit Post for r/Python

**Title:** I built a unified API for Instagram/TikTok/Twitter/Facebook/LinkedIn - same interface for all platforms

---

**Post Content:**

Hey r/Python! 👋

I built **UniAPI** - a unified REST API that lets you interact with Instagram, TikTok, Twitter, Facebook, and LinkedIn using the **exact same interface** for all platforms.

## What My Project Does

UniAPI provides a unified REST API for social media platforms that normally require complex developer approval, have expensive pricing tiers, or offer limited functionality through official APIs. Instead of dealing with 5 different SDKs, authentication flows, and data structures, you get one consistent interface:

- **Get user information** across all platforms
- **Like/favorite content** with the same method
- **Send DMs** uniformly
- **Comment on posts** with identical code
- **Follow users** using one interface
- **Batch operations** with built-in rate limiting

The system uses **FastAPI + Playwright** for browser automation, bypassing official API limitations entirely.

## Target Audience

This project is intended for:

- **Developers** building social media management tools, analytics dashboards, or marketing automation
- **Researchers** studying social media behavior without dealing with API approval processes
- **Personal automation** for managing multiple social media accounts
- **Learning projects** exploring web automation and API design

**Production readiness:** This is an educational/personal-use tool. It uses browser automation which may violate platform ToS. **Not recommended for commercial use at scale** or applications requiring high reliability. Think of it as a prototype/learning tool rather than production infrastructure.

## Comparison

**vs. Official APIs:**
- **No approval needed** - Official APIs require weeks/months of review (Meta, LinkedIn) or paid tiers (Twitter $100/month minimum)
- **More features** - Instagram's official API doesn't support DMs at all; this does
- **Free** - No monthly fees vs. Twitter's $100/month or LinkedIn's partnership requirements
- **Unified interface** - One SDK vs. learning 5 different API structures

**vs. Similar Projects:**
- **[Instagrapi](https://github.com/adw0rd/instagrapi)** - Instagram-only, UniAPI supports 5 platforms
- **[Tweepy](https://github.com/tweepy/tweepy)** - Official Twitter API wrapper, still requires paid API access
- **[facebook-sdk](https://github.com/mobolic/facebook-sdk)** - Official SDK, requires app approval
- **[python-linkedin](https://github.com/ozgur/python-linkedin)** - Outdated, LinkedIn changed authentication

**Trade-offs:**
- ✅ Works immediately without approval
- ✅ Supports more features than official APIs
- ✅ Free and open source
- ❌ Uses browser automation (slower than API calls)
- ❌ May violate platform ToS (use at your own risk)
- ❌ Requires cookie-based auth (need to re-authenticate when cookies expire)

## Code Example

Same code structure for all platforms:

```python
from instagram_sdk import InstagramAPI
from tiktok_sdk import TikTokAPI

# Instagram
insta = InstagramAPI()
insta.like_post("https://www.instagram.com/p/ABC123/")
insta.send_dm("username", "Hello!")

# TikTok - EXACT same interface
tiktok = TikTokAPI()
tiktok.like_video("https://www.tiktok.com/@user/video/123")
tiktok.send_dm("username", "Hello!")
```

No OAuth dance, no developer applications, no monthly fees.

## Technical Architecture

**Architecture:**
```
Your Code
   ↓
Python SDK (instagram_sdk.py, tiktok_sdk.py, etc.)
   ↓
FastAPI Main Server (Port 8000)
   ↓
Platform Bridge Servers (Ports 5001-5005)
   ↓
Playwright Browser Automation
   ↓
Social Media Platforms
```

**Authentication:** Simple cookie-based auth - just export your browser cookies (one-time setup)

**Tech Stack:**
- FastAPI for the REST API
- Playwright for browser automation
- Flask for platform bridge servers
- Pydantic for data validation

## Features

✅ **All 5 platforms supported:** Twitter, Instagram, TikTok, Facebook, LinkedIn
✅ **Unified interface:** Same methods across all platforms
✅ **One-click deployment:** Automated installation scripts
✅ **No approval needed:** Works with your existing accounts
✅ **Free & open source:** MIT License

## Supported Operations

- Get user information
- Like/favorite posts
- Comment on content
- Send DMs
- Follow users
- Batch operations with auto-delay

## Example Use Cases

- Social media management tools
- Marketing automation
- Analytics dashboards
- Personal automation scripts
- Research projects

## Project Links

**GitHub:** https://github.com/LiuLucian/uniapi

Installation is literally:
```bash
git clone https://github.com/LiuLucian/uniapi.git
cd uniapi/backend
./install.sh
./start_uniapi.sh
```

Full docs at http://localhost:8000/api/docs after startup.

---

**⚠️ Disclaimer:** This uses browser automation to bypass official API limitations. Use responsibly and be aware of platform ToS. Intended for personal use, learning, and testing - not commercial automation at scale.

---

**Feedback welcome!** This is v1.0 and I'd love to hear:
- What features would be most useful?
- Which platforms should I prioritize?
- Any bugs or issues you encounter?

If you find this useful, a ⭐ on GitHub would mean a lot!

---

**Built with [Claude Code](https://claude.com/claude-code) 🤖**
