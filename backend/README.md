# UniAPI Backend

Universal Social Media API - Twitter API v2 compatible interface

## Quick Start

```bash
# Start UniAPI server
cd /Users/l.u.c/my-app/uniapi/backend
source venv/bin/activate
python main.py

# Server runs on http://localhost:8000
```

## Prerequisites

**IMPORTANT**: twitter_bridge_server.py must be running on port 5001

```bash
# In separate terminal:
cd "/Users/l.u.c/my-app/MarketingMind AI"
python3 twitter_bridge_server.py

# Should show: ✅ Server ready on http://localhost:5001
```

## API Endpoints

### POST /api/v1/twitter/tweets
Create a tweet

```bash
curl -X POST "http://localhost:8000/api/v1/twitter/tweets" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from UniAPI!"}'
```

Response:
```json
{
  "data": {
    "id": "1234567890",
    "text": "Hello from UniAPI!"
  }
}
```

### GET /api/v1/twitter/users/me
Get current user info

```bash
curl http://localhost:8000/api/v1/twitter/users/me
```

Response:
```json
{
  "data": {
    "id": "1234567890",
    "name": "Lucian Liu",
    "username": "LucianLiu861650"
  }
}
```

## Architecture

```
┌─────────────┐       ┌──────────────────────┐       ┌─────────┐
│   Client    │──────>│  UniAPI (port 8000)  │──────>│ Twitter │
└─────────────┘       └──────────────────────┘   │   └─────────┘
                              │                    │
                              v                    │
                      ┌──────────────────────┐    │
                      │twitter_bridge_server │────┘
                      │    (port 5001)       │
                      └──────────────────────┘
```

UniAPI provides a clean Twitter API v2 compatible interface and proxies requests to the working twitter_bridge_server.py implementation.

## Files

- `main.py` - FastAPI server entry point
- `api/v1/twitter.py` - Twitter API v2 endpoints (proxy implementation)
- `platforms/twitter/api.py` - Unused (was direct Playwright implementation)
- `platforms/twitter/auth.py` - Authentication helpers

## Notes

- All authentication is handled by twitter_bridge_server.py using cookies from `~/.distroflow/twitter_auth.json`
- No need to re-implement Playwright automation - reuses working code
- Clean separation: UniAPI = API layer, twitter_bridge_server = implementation layer
