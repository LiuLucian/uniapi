# Instagram Bridge Server

Flask server on port 5002 that bridges Postiz and Instagram using Playwright automation.

## Architecture

Follows the same pattern as `twitter_bridge_server.py`:
- Flask REST API endpoints
- Playwright browser automation
- Cookie-based authentication
- Async operations wrapped with `asyncio.run()`

## Setup

1. **Install dependencies** (if not already installed):
```bash
pip install flask playwright
playwright install chromium
```

2. **Configure authentication**:

Create `platforms_auth.json` in the same directory:
```json
{
  "instagram": {
    "sessionid": "your_instagram_session_id_here"
  }
}
```

To get your Instagram sessionid:
- Log in to Instagram in your browser
- Open Developer Tools (F12)
- Go to Application/Storage → Cookies → https://www.instagram.com
- Copy the value of the `sessionid` cookie

## Running the Server

```bash
cd /Users/l.u.c/my-app/uniapi/backend/platforms/instagram
python3 instagram_bridge_server.py
```

Server will start on: `http://localhost:5002`

## API Endpoints

### 1. Health Check
```bash
GET /health

Response:
{
  "status": "ok",
  "message": "Instagram Bridge Server is running"
}
```

**Example:**
```bash
curl http://localhost:5002/health
```

### 2. Create Post
```bash
POST /post
Content-Type: application/json

Body:
{
  "caption": "Post caption with #hashtags",
  "image_path": "/absolute/path/to/image.jpg"
}

Response (Success):
{
  "success": true,
  "message": "Post created successfully",
  "url": "https://www.instagram.com/"
}

Response (Error):
{
  "success": false,
  "error": "Error message"
}
```

**Example:**
```bash
curl -X POST http://localhost:5002/post \
  -H "Content-Type: application/json" \
  -d '{
    "caption": "Hello from Instagram Bridge Server! #automation #instagram",
    "image_path": "/Users/username/Pictures/image.jpg"
  }'
```

**Important Notes:**
- Instagram **requires an image** for posts (unlike Twitter which supports text-only)
- The `image_path` must be an **absolute path** to an existing image file
- Supported formats: JPG, PNG (recommended: 1080x1080 or 1080x1350)

### 3. Get User Profile
```bash
GET /user/<username>

Response (Success):
{
  "success": true,
  "username": "username",
  "profile_url": "https://www.instagram.com/username/",
  "title": "Username (@username) • Instagram",
  "bio": "User biography text",
  "followers": "1.2K"
}

Response (Error):
{
  "success": false,
  "error": "Error message"
}
```

**Example:**
```bash
curl http://localhost:5002/user/instagram
```

### 4. Send DM
```bash
POST /dm
Content-Type: application/json

Body:
{
  "username": "target_username",
  "message": "Hello! This is a DM from the bridge server."
}

Response (Success):
{
  "success": true,
  "message": "DM sent successfully",
  "username": "target_username"
}

Response (Error):
{
  "success": false,
  "error": "Error message"
}
```

**Example:**
```bash
curl -X POST http://localhost:5002/dm \
  -H "Content-Type: application/json" \
  -d '{
    "username": "instagram",
    "message": "Hey! Testing the Instagram bridge server."
  }'
```

**Important Notes:**
- The server will automatically follow the user if not already following (Instagram requires this to send DMs to non-followers)
- Browser runs in non-headless mode for DM sending (Instagram's anti-bot detection)

## Implementation Details

### Async Wrapper Pattern

All operations use `asyncio.run()` to execute async Playwright code:

```python
@app.route('/post', methods=['POST'])
def create_post_endpoint():
    # ... validation ...
    result = asyncio.run(instagram_ops.create_post(caption, image_path))
    return jsonify(result)
```

This matches the Twitter bridge server pattern.

### Browser Context

Each operation:
1. Launches fresh browser with persistent context
2. Loads cookies from auth file
3. Performs the operation
4. Closes browser

This ensures clean state and prevents session conflicts.

### Error Handling

All endpoints return consistent JSON responses:
- Success: `{"success": true, ...}`
- Error: `{"success": false, "error": "message"}`

HTTP status codes:
- 200: Success
- 400: Bad request (missing parameters)
- 500: Server error (operation failed)

## Comparison with Twitter Bridge Server

| Feature | Twitter | Instagram |
|---------|---------|-----------|
| Port | 5001 | 5002 |
| Text-only posts | ✅ Yes | ❌ No (requires image) |
| Headless posting | ❌ No | ❌ No |
| Authentication | Persistent context | Cookie injection |
| DM following | Not required | ✅ Required |

## Troubleshooting

### "No Instagram session found"
- Check `platforms_auth.json` exists in the same directory
- Verify the `sessionid` is not expired
- Try logging in manually and getting a fresh sessionid

### "Image required for Instagram post"
- Instagram always requires at least one image
- Provide absolute path to image file in `image_path` parameter

### "Could not find Create button"
- Session may be expired - refresh your sessionid
- Instagram UI may have changed - selectors may need updating

### "Could not open message dialog"
- Make sure you're not rate-limited by Instagram
- Try manually sending a few DMs through the browser first
- The user may have DMs disabled

### Browser doesn't close
- Playwright browsers auto-close when the context is closed
- If stuck, kill process manually: `pkill -f chromium`

## Development

### Running Tests

Test the server manually:

```bash
# Start server
python3 instagram_bridge_server.py

# In another terminal, test endpoints
curl http://localhost:5002/health
curl http://localhost:5002/user/instagram
```

### Adding New Endpoints

Follow the Twitter bridge server pattern:

1. Add async method to `InstagramOperations` class
2. Create Flask route that calls `asyncio.run(method())`
3. Return JSON response with consistent format
4. Add logging with emoji prefixes (📍, ✅, ❌)

Example:
```python
class InstagramOperations:
    async def new_operation(self, param):
        """New operation"""
        try:
            async with async_playwright() as p:
                # ... playwright code ...
                return {'success': True, 'data': 'result'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

@app.route('/new-endpoint', methods=['POST'])
def new_endpoint():
    data = request.get_json()
    result = asyncio.run(instagram_ops.new_operation(data.get('param')))
    return jsonify(result)
```

## Security Notes

1. **Authentication**: The sessionid cookie provides full access to your Instagram account
2. **Local only**: Server binds to `0.0.0.0` but should only be accessed locally
3. **No encryption**: Traffic is unencrypted - use only on trusted networks
4. **Rate limiting**: Instagram has rate limits - don't spam requests

## Future Improvements

- [ ] Add story posting support
- [ ] Add comment/like operations
- [ ] Implement request rate limiting
- [ ] Add response caching for user profiles
- [ ] Support multiple image uploads (carousel)
- [ ] Add video post support
- [ ] Implement proper error recovery for expired sessions

## See Also

- Twitter bridge server: `../twitter/twitter_bridge_server.py`
- Instagram poster: `instagram_poster.py`
- Instagram scraper: `instagram_scraper.py`
- Instagram DM sender: `instagram_dm_sender_optimized.py`
