# Instagram API Testing Guide

Complete guide for testing all Instagram API features implemented in UniAPI.

## Overview

The Instagram API implementation includes comprehensive test suites for all features:
- **Like/Unlike** posts
- **Follow/Unfollow** users
- **Comment** on posts
- **Get post details**
- **Get user posts** list
- **Search by hashtag**
- **Send Direct Messages**

## Test Scripts

All test scripts are located in `/Users/l.u.c/my-app/uniapi/backend/`

| Script | Purpose | Features Tested |
|--------|---------|----------------|
| `test_instagram_all.py` | **Master Test Suite** | Unified interface to all test scripts |
| `test_instagram_like.py` | Like/Unlike Tests | Like post, Unlike post, Complete cycle |
| `test_instagram_follow.py` | Follow/Unfollow Tests | Follow user, Unfollow user, Complete cycle, Get profile |
| `test_instagram_comment.py` | Comment Tests | Single comment, Multiple comments, Emoji comments |
| `test_instagram_data.py` | Data Retrieval Tests | Get post details, Get user posts, Search by tag |
| `test_dm_real.py` | Direct Message Tests | Send DM to user |

## Quick Start

### 1. Start Required Servers

```bash
# Terminal 1: Start FastAPI server
cd /Users/l.u.c/my-app/uniapi/backend
uvicorn main:app --reload --port 8000

# Terminal 2: Start Instagram Bridge Server
cd /Users/l.u.c/my-app/uniapi/backend
python3 platforms/instagram/instagram_bridge_server.py
```

### 2. Run Master Test Suite

```bash
cd /Users/l.u.c/my-app/uniapi/backend
python3 test_instagram_all.py
```

The master test suite will:
1. Check server status (FastAPI + Bridge Server)
2. Display interactive menu with all test options
3. Allow you to run individual or all test suites

## Individual Test Scripts

### Like/Unlike Tests

```bash
python3 test_instagram_like.py
```

**Available Tests:**
1. Test Like Post - Like any Instagram post
2. Test Unlike Post - Unlike any Instagram post
3. Test Complete Like/Unlike Cycle - Like then unlike the same post
4. Run All Tests

**Example Usage:**
- Provide Instagram post URL: `https://www.instagram.com/p/ABC123xyz/`
- System extracts media ID and performs action
- Browser automation runs in visible mode (non-headless)
- Expected time: 10-15 seconds per action

### Follow/Unfollow Tests

```bash
python3 test_instagram_follow.py
```

**Available Tests:**
1. Test Follow User - Follow an Instagram user
2. Test Unfollow User - Unfollow an Instagram user
3. Test Complete Follow/Unfollow Cycle - Follow then unfollow
4. Test Get User Profile (Bonus) - Retrieve user profile info
5. Run All Tests

**Example Usage:**
- Provide username: `username` or `@username`
- System handles @ symbol automatically
- Unfollow includes confirmation dialog handling
- Expected time: 10-15 seconds per action

### Comment Tests

```bash
python3 test_instagram_comment.py
```

**Available Tests:**
1. Test Single Comment - Post one comment
2. Test Multiple Comments (Batch) - Post multiple test comments
3. Test Comment with Emojis - Use predefined emoji-rich comments
4. Run All Tests

**Example Usage:**
- Single comment: Enter post URL, then type comment (multi-line supported)
- Multiple comments: Specify count (1-5), auto-generates timestamped test comments
- Emoji comments: Choose from preset emoji-rich comments
- Expected time: 10-15 seconds per comment

**Multi-line Comment Input:**
```
💬 Enter your comment:
   (Press Enter twice when done, or Ctrl+C to cancel)

This is line 1
This is line 2

👆 (Press Enter twice to finish)
```

### Data Retrieval Tests

```bash
python3 test_instagram_data.py
```

**Available Tests:**
1. Test Get Post Details - Extract post metadata (likes, comments, caption, author)
2. Test Get User Posts - Fetch user's post list with scrolling
3. Test Search by Tag - Search posts by hashtag
4. Test Complete Data Flow - Get user posts → Get first post details
5. Run All Tests

**Example Usage:**
- Get Post Details: Provide post URL
- Get User Posts: Provide username + max results (default 20)
- Search by Tag: Provide tag without # + max results
- Expected time: 15-30 seconds (includes scrolling for lists)

**Response Format Example:**
```json
{
  "success": true,
  "caption": "Great photo! #travel",
  "likes": 1234,
  "comments": 56,
  "author": "username"
}
```

### Direct Message Tests

```bash
python3 test_dm_real.py
```

**Usage:**
- Edit script to change target username (default: `lucianliu6`)
- Edit message content
- Run script
- Expected time: 10-20 seconds

**Existing Test:**
```python
url = "http://localhost:8000/api/v1/instagram/users/lucianliu6/dm"
data = {
    "username": "lucianliu6",
    "message": "Hello! Testing Instagram API from UniAPI. 🚀"
}
```

## API Endpoint Reference

### Base URL
```
http://localhost:8000/api/v1/instagram
```

### Endpoints

#### Interactions
```bash
# Like Post
POST /media/{media_id}/like

# Unlike Post
DELETE /media/{media_id}/like

# Follow User
POST /users/{username}/follow

# Unfollow User
DELETE /users/{username}/follow

# Comment on Post
POST /media/{media_id}/comments
Content-Type: application/json
{"text": "Great post!"}
```

#### Data Retrieval
```bash
# Get Post Details
GET /media/{media_id}

# Get User Posts
GET /users/{username}/media?max_results=20

# Search by Tag
GET /tags/{tag}/media/recent?max_results=20

# Get User Profile
GET /users/{username}
```

#### Direct Messages
```bash
# Send DM
POST /users/{username}/dm
Content-Type: application/json
{"username": "target", "message": "Hello!"}
```

#### Health Check
```bash
# API Health
GET /health

# Response:
{
  "status": "ok",
  "message": "Instagram API is running",
  "bridge_status": "connected"
}
```

## Testing with cURL

### Like a Post
```bash
curl -X POST http://localhost:8000/api/v1/instagram/media/ABC123xyz/like
```

### Follow a User
```bash
curl -X POST http://localhost:8000/api/v1/instagram/users/username/follow
```

### Comment on Post
```bash
curl -X POST http://localhost:8000/api/v1/instagram/media/ABC123xyz/comments \
  -H "Content-Type: application/json" \
  -d '{"text": "Great post! 🔥"}'
```

### Get User Posts
```bash
curl "http://localhost:8000/api/v1/instagram/users/username/media?max_results=10"
```

### Search by Tag
```bash
curl "http://localhost:8000/api/v1/instagram/tags/travel/media/recent?max_results=20"
```

### Send DM
```bash
curl -X POST http://localhost:8000/api/v1/instagram/users/username/dm \
  -H "Content-Type: application/json" \
  -d '{"username": "username", "message": "Hello from UniAPI!"}'
```

## Architecture

### Two-Layer System

```
┌─────────────────────────────────────────┐
│         FastAPI Layer (Port 8000)       │
│  - API Routes (api/v1/instagram.py)     │
│  - Request validation (Pydantic)        │
│  - Error handling                       │
└─────────────┬───────────────────────────┘
              │ HTTP (httpx)
              ↓
┌─────────────────────────────────────────┐
│   Instagram Bridge Server (Port 5002)   │
│  - Flask server                         │
│  - Playwright automation                │
│  - Browser control (Firefox)            │
│  - Cookie-based authentication          │
└─────────────────────────────────────────┘
```

### Authentication

The system uses **cookie-based authentication** from `INSTAGRAM_SESSION_ID` environment variable.

**To set up:**
```bash
# Add to .env file
INSTAGRAM_SESSION_ID=your_session_id_here
```

**To get sessionid:**
1. Log into Instagram in Firefox
2. Open DevTools (F12) → Storage → Cookies
3. Find `sessionid` cookie value
4. Copy value to `.env`

## Troubleshooting

### Server Not Running

**Problem:** `❌ FastAPI Server (port 8000): Not running`

**Solution:**
```bash
cd /Users/l.u.c/my-app/uniapi/backend
uvicorn main:app --reload --port 8000
```

---

**Problem:** `❌ Instagram Bridge Server (port 5002): Not running`

**Solution:**
```bash
cd /Users/l.u.c/my-app/uniapi/backend
python3 platforms/instagram/instagram_bridge_server.py
```

### Authentication Failed

**Problem:** `No Instagram session found`

**Solution:**
1. Check `.env` file has `INSTAGRAM_SESSION_ID`
2. Verify sessionid is still valid (log into Instagram in browser)
3. Update sessionid if expired

### Selector Not Found

**Problem:** `Could not find [element] button`

**Solution:**
- Instagram UI changes frequently
- Update selectors in `instagram_bridge_server.py`
- Check browser screenshot if test runs in visible mode
- Selectors use multi-fallback strategy for robustness

### Timeout Errors

**Problem:** Request times out after 60s

**Solution:**
- Check internet connection
- Instagram might be rate-limiting (wait 5-10 minutes)
- Try with `headless=False` to see what's happening in browser

## Best Practices

### 1. Rate Limiting
- Don't spam actions
- Use delays between bulk operations
- Instagram has rate limits (~20 actions/hour for likes, ~200/hour for follows)

### 2. Testing Safely
- Use test accounts when possible
- Don't abuse automated actions
- Respect Instagram's Terms of Service

### 3. Browser Automation
- Tests run in **visible mode** (`headless=False`) for debugging
- Firefox is used for macOS stability
- Each action takes 10-30 seconds (realistic human behavior)

### 4. Error Handling
- All endpoints return `{"success": true/false, ...}` format
- Check `success` field before processing data
- Read `error` or `message` fields for details

## Performance Notes

### Timing Expectations

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| Like/Unlike | 10-15s | Includes navigation + click |
| Follow/Unfollow | 10-15s | Includes dialog handling |
| Comment | 10-15s | Includes text input |
| Get Post Details | 10-15s | Page load + extraction |
| Get User Posts | 15-30s | Includes scrolling |
| Search by Tag | 15-30s | Includes scrolling |
| Send DM | 10-20s | May include auto-follow |

### Optimization Tips

1. **Batch Operations:** Use data retrieval to get multiple items, then process
2. **Caching:** Cache user profiles and post details when possible
3. **Parallel Requests:** Multiple independent operations can run concurrently
4. **Error Recovery:** Implement retry logic with exponential backoff

## Test Coverage Summary

✅ **Fully Implemented and Tested:**
- Like Post
- Unlike Post
- Follow User
- Unfollow User
- Comment on Post
- Get Post Details
- Get User Posts
- Search by Hashtag
- Send Direct Message
- Get User Profile

📋 **Test Scripts:**
- 5 comprehensive test suites
- 1 master test runner
- Interactive menus for all tests
- Server health checks
- Detailed error messages

🧪 **Test Features:**
- Like/Unlike cycle tests
- Follow/Unfollow cycle tests
- Multi-comment batch tests
- Emoji support tests
- Complete data flow tests
- cURL examples for all endpoints

## Additional Resources

- **Implementation Status:** `INSTAGRAM_API_FEATURES.md`
- **Bridge Server Code:** `platforms/instagram/instagram_bridge_server.py`
- **FastAPI Routes:** `api/v1/instagram.py`
- **Server Logs:** `instagram_bridge.log`

## Support

If you encounter issues:
1. Check server logs (`instagram_bridge.log`)
2. Run tests with visible browser (`headless=False`)
3. Verify sessionid is valid
4. Check if Instagram UI has changed (update selectors)

---

**Created:** 2025-01-07
**Last Updated:** 2025-01-07
**Version:** 1.0.0
