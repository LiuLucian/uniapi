# Bridge Server Comparison: Twitter vs Instagram

This document compares the two bridge servers to show the pattern and differences.

## Architectural Similarities

Both servers follow the same pattern:

1. **Flask REST API** - HTTP endpoints for operations
2. **Playwright automation** - Browser automation for actions
3. **Cookie-based auth** - Use saved session cookies
4. **Async wrapper** - `asyncio.run()` for async Playwright code
5. **Consistent responses** - `{"success": bool, ...}` format
6. **Emoji logging** - Friendly log messages with emoji prefixes

## File Locations

```
/Users/l.u.c/my-app/uniapi/backend/platforms/
├── twitter/
│   ├── twitter_bridge_server.py       # Port 5001
│   └── twitter_operations.py          # Twitter operations class
└── instagram/
    ├── instagram_bridge_server.py      # Port 5002
    ├── instagram_poster.py             # Used for post creation
    ├── instagram_scraper.py            # Used for user data
    └── instagram_dm_sender_optimized.py # Used for DMs
```

## Port Assignment

- **Twitter**: Port 5001
- **Instagram**: Port 5002

## Authentication Differences

### Twitter Bridge Server

Uses persistent browser context with saved user data:

```python
user_data_dir = Path.home() / '.distroflow/twitter_browser'

context = await p.chromium.launch_persistent_context(
    str(user_data_dir),
    headless=False,
    ...
)
```

- Cookies, local storage, and session data persist between runs
- No need to inject cookies manually
- Login state fully preserved

### Instagram Bridge Server

Uses cookie injection for each session:

```python
context = await browser.new_context(...)

await context.add_cookies([{
    'name': 'sessionid',
    'value': self.sessionid,
    'domain': '.instagram.com',
    'path': '/'
}])
```

- Fresh browser context each time
- Sessionid loaded from `platforms_auth.json`
- Session must be manually refreshed when expired

## Endpoint Comparison

| Endpoint | Twitter (5001) | Instagram (5002) | Notes |
|----------|----------------|------------------|-------|
| **Health Check** | ✅ `/health` | ✅ `/health` | Identical |
| **Create Post** | ✅ `/post` | ✅ `/post` | Instagram requires image |
| **Get User** | ✅ `/user/<username>` | ✅ `/user/<username>` | Different data structure |
| **Send DM** | ❌ Not implemented | ✅ `/dm` | Instagram only |
| **Like Post** | ✅ `/like` | ❌ Not implemented | Twitter only |
| **Retweet** | ✅ `/retweet` | ❌ Not implemented | Twitter only |
| **Delete Post** | ✅ `/tweet/<id>` DELETE | ❌ Not implemented | Twitter only |
| **Get Post** | ✅ `/tweet/<id>` GET | ❌ Not implemented | Twitter only |
| **Follow User** | ✅ `/follow` | ⚠️  Auto (in DM flow) | Instagram auto-follows for DM |
| **Get User Tweets** | ✅ `/user/<username>/tweets` | ❌ Not implemented | Twitter only |
| **Search** | ✅ `/search/tweets` | ❌ Not implemented | Twitter only |

## Request/Response Examples

### Create Post

**Twitter:**
```bash
POST http://localhost:5001/post
{
  "tweets": [
    {"text": "First tweet"},
    {"text": "Second tweet (reply to first)"}
  ]
}

Response:
{
  "success": true,
  "tweet_ids": ["123456", "789012"],
  "urls": ["https://twitter.com/user/status/123456", ...],
  "count": 2
}
```

**Instagram:**
```bash
POST http://localhost:5002/post
{
  "caption": "Post caption with #hashtags",
  "image_path": "/absolute/path/to/image.jpg"
}

Response:
{
  "success": true,
  "message": "Post created successfully",
  "url": "https://www.instagram.com/"
}
```

**Key Differences:**
- Twitter: Text-only posts, supports threads (multiple tweets)
- Instagram: Requires image, single post only, caption with hashtags

### Get User Profile

**Twitter:**
```bash
GET http://localhost:5001/user/username

Response:
{
  "id": "123456789",
  "username": "username",
  "name": "Full Name",
  "description": "Bio text",
  "followers_count": "1234",
  "following_count": "567"
}
```

**Instagram:**
```bash
GET http://localhost:5002/user/username

Response:
{
  "success": true,
  "username": "username",
  "profile_url": "https://www.instagram.com/username/",
  "title": "Username (@username) • Instagram",
  "bio": "Bio text",
  "followers": "1.2K"
}
```

**Key Differences:**
- Twitter: Uses numeric user ID, precise follower counts
- Instagram: No numeric ID exposed, formatted follower count (e.g., "1.2K")

## Code Structure Comparison

### Twitter Bridge Server

```python
# Separate operations class
from twitter_operations import TwitterOperations

app = Flask(__name__)
twitter_ops = TwitterOperations()

@app.route('/post', methods=['POST'])
def post_tweet_endpoint():
    result = asyncio.run(post_tweets_task(tweets))
    return jsonify(result)
```

**Pattern:**
- Operations split into separate file (`twitter_operations.py`)
- Standalone async functions for complex operations
- Operations class handles browser lifecycle

### Instagram Bridge Server

```python
# Operations class in same file
class InstagramOperations:
    async def create_post(self, caption, image_path):
        # ... implementation ...
        pass

instagram_ops = InstagramOperations()

@app.route('/post', methods=['POST'])
def create_post_endpoint():
    result = asyncio.run(instagram_ops.create_post(caption, image_path))
    return jsonify(result)
```

**Pattern:**
- Operations class in same file (simpler structure)
- All operations as class methods
- Each method manages its own browser lifecycle

## Browser Configuration

### Twitter

```python
context = await p.chromium.launch_persistent_context(
    str(user_data_dir),
    headless=False,  # Twitter detects headless
    viewport={'width': 1400, 'height': 900},
    user_agent='Mozilla/5.0 ...',
    args=[
        '--disable-blink-features=AutomationControlled',
        '--start-maximized',
        '--no-sandbox'
    ]
)
```

**Key Features:**
- Persistent context for full session preservation
- Wider viewport (1400x900)
- Multiple anti-detection args
- Maximized window

### Instagram

```python
browser = await p.chromium.launch(
    headless=False,  # Instagram detects headless
    args=['--disable-blink-features=AutomationControlled']
)

context = await browser.new_context(
    user_agent='Mozilla/5.0 ...'
)
```

**Key Features:**
- Fresh context each time
- Standard viewport (default)
- Minimal anti-detection
- Normal window size

## Error Handling

Both servers use the same error response format:

```python
try:
    # ... operation ...
    return {'success': True, 'data': result}
except Exception as e:
    logger.error(f"❌ Error: {e}")
    return {'success': False, 'error': str(e)}
```

Endpoints return:
- `200` - Success
- `400` - Bad request (missing parameters)
- `500` - Server error (operation failed)

## Performance Characteristics

| Aspect | Twitter | Instagram |
|--------|---------|-----------|
| **Post Creation** | ~5-10 sec | ~15-25 sec |
| **Get User** | ~3-5 sec | ~5-8 sec |
| **DM Sending** | N/A | ~10-15 sec |
| **Browser Startup** | ~2 sec (reuses context) | ~2 sec (fresh each time) |
| **Memory Usage** | Higher (persistent) | Lower (fresh context) |

## Rate Limiting

### Twitter
- Aggressive anti-bot detection
- Rate limits on posting (varies by account age)
- Recommend delays: 5-10 seconds between posts

### Instagram
- Very aggressive anti-bot detection
- Rate limits on follows/unfollows
- Rate limits on DMs (especially new accounts)
- Recommend delays: 2-5 minutes between DMs

## Future Enhancements

### Twitter Bridge Server
- [ ] Add media upload support (images, videos)
- [ ] Implement quote tweet functionality
- [ ] Add bookmark operations
- [ ] Support for polls

### Instagram Bridge Server
- [ ] Add story posting
- [ ] Support carousel posts (multiple images)
- [ ] Add like/comment operations
- [ ] Implement post deletion
- [ ] Add video post support
- [ ] Support for reels

## When to Use Which Pattern

### Use Twitter Pattern (Persistent Context) When:
- Session data is complex (cookies + local storage + indexed DB)
- Platform has strict anti-bot detection
- Operations require continuous logged-in state
- You need to preserve browser history and cache

### Use Instagram Pattern (Fresh Context + Cookie Injection) When:
- Authentication is simple (single sessionid cookie)
- You want clean state for each operation
- Memory usage is a concern
- You need to easily swap between accounts

## Testing

### Twitter
```bash
# Start server
cd /Users/l.u.c/my-app/uniapi/backend/platforms/twitter
python3 twitter_bridge_server.py

# Test
curl http://localhost:5001/health
```

### Instagram
```bash
# Start server
cd /Users/l.u.c/my-app/uniapi/backend/platforms/instagram
python3 instagram_bridge_server.py

# Test
curl http://localhost:5002/health
python3 test_bridge_server.py
```

## Summary

Both bridge servers provide a clean REST API interface to automate social media platforms using Playwright. The key differences are:

1. **Authentication**: Twitter uses persistent context, Instagram uses cookie injection
2. **Complexity**: Twitter has more endpoints, Instagram is simpler
3. **Media**: Instagram requires images for posts, Twitter allows text-only
4. **Structure**: Twitter splits operations into separate file, Instagram keeps everything together

Choose the pattern that best fits your use case and platform requirements.
