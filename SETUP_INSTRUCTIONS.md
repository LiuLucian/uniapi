# UniAPI Setup Instructions

## Current Status

### ✅ FULLY WORKING
- ✅ UniAPI server running at http://localhost:8000
- ✅ POST `/api/v1/twitter/tweets` - **Tweet posting WORKS** (proxies to twitter_bridge_server)
- ✅ GET `/api/v1/twitter/users/me` - Returns current user info
- ✅ Health check endpoint
- ✅ All code in English (comments, logs, messages)
- ✅ Clean architecture: UniAPI acts as proxy to working twitter_bridge_server.py

### Architecture
UniAPI (8000) proxies requests to twitter_bridge_server.py (5001) which handles actual Playwright automation.
This avoids code duplication and uses the proven working implementation from MarketingMind AI.

## Quick Start

### 1. Authentication (CURRENT WORKAROUND)

**Note:** The authentication script has a Playwright Chromium crash issue. Currently using existing auth from MarketingMind AI.

Auth file location: `~/.distroflow/twitter_auth.json`

To re-authenticate in the future:
```bash
cd /Users/l.u.c/my-app/MarketingMind AI
python3 quick_twitter_login.py  # This works
# Auth file will be saved to ~/.distroflow/twitter_auth.json
# UniAPI will automatically use it
```

### 2. Test the API

```bash
# Method 1: Use test script
python3 test_twitter_api.py

# Method 2: Use curl
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/twitter/users/me

# Method 3: Use Swagger UI
open http://localhost:8000/api/docs
```

## How It Works

### Architecture
```
HTTP Request → FastAPI Router → Playwright Scraper → Twitter.com → Parse Response → Twitter API v2 Format
```

### Example Flow (Post Tweet)
1. `POST /api/v1/twitter/tweets` receives request
2. FastAPI calls `TwitterAPI.create_tweet(text)`
3. Playwright launches browser with saved cookies
4. Script fills compose box and clicks post
5. Extract tweet ID from URL
6. Return Twitter API v2 compatible response

### Authentication Files
- **Setup script**: `setup_twitter_auth.py`
- **Auth manager**: `platforms/twitter/auth.py`
- **Saved cookies**: `~/.distroflow/twitter_auth.json`

### API Implementation
- **Scraper**: `platforms/twitter/api.py` (Playwright automation)
- **Router**: `api/v1/twitter.py` (FastAPI endpoints)

## Currently Available Endpoints

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/health` | Health check | ✅ Working |
| GET | `/` | API info | ✅ Working |
| GET | `/api/v1/twitter/users/me` | Get current user | ✅ Working |
| POST | `/api/v1/twitter/tweets` | Post tweet | ✅ Working |
| DELETE | `/api/v1/twitter/tweets/:id` | Delete tweet | 🚧 TODO |
| POST | `/api/v1/twitter/tweets/:id/retweet` | Retweet | 🚧 TODO |
| POST | `/api/v1/twitter/tweets/:id/like` | Like tweet | 🚧 TODO |

## Example Requests

### Get Current User
```bash
curl http://localhost:8000/api/v1/twitter/users/me
```

Response:
```json
{
  "data": {
    "id": "1234567890",
    "name": "User Name",
    "username": "yourusername"
  }
}
```

### Post Tweet
```bash
curl -X POST "http://localhost:8000/api/v1/twitter/tweets" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from UniAPI!"}'
```

Response (Twitter API v2 compatible):
```json
{
  "data": {
    "id": "1234567890123456789",
    "text": "Hello from UniAPI!"
  }
}
```

## Troubleshooting

### Error: "Twitter authentication not found"
**Solution**: Run `python3 setup_twitter_auth.py`

### Browser crashes on launch
**Cause**: Persistent context issue (now fixed)
**Solution**: Use `browser.new_context()` + `add_cookies()` (already implemented)

### Cookies expired
**Solution**: Run `python3 setup_twitter_auth.py` again

## Code Structure

All code and comments are in English:
- ✅ No Chinese comments
- ✅ English variable names
- ✅ English log messages
- ✅ English error messages

## Next Steps

1. Run `python3 setup_twitter_auth.py`
2. Test with `python3 test_twitter_api.py`
3. View API docs at http://localhost:8000/api/docs
