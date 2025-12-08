# Instagram Bridge Server - Quick Start Guide

Get the Instagram Bridge Server running in 5 minutes.

## Prerequisites

✅ Python 3.8+
✅ Playwright installed
✅ Instagram account

## Step 1: Install Dependencies

```bash
pip install flask playwright
playwright install chromium
```

## Step 2: Get Your Instagram Session ID

1. **Open Instagram in your browser** and log in
2. **Open Developer Tools** (Press F12 or Right-click → Inspect)
3. **Go to Application/Storage tab** → Cookies → https://www.instagram.com
4. **Find and copy** the `sessionid` cookie value

It will look like: `123456789%3AaBcDeFgHiJkLmNoPq%3A28%3AAYdW...`

## Step 3: Create Auth File

Create `platforms_auth.json` in this directory:

```bash
cd /Users/l.u.c/my-app/uniapi/backend/platforms/instagram
nano platforms_auth.json
```

Paste this content (replace with your sessionid):

```json
{
  "instagram": {
    "sessionid": "paste_your_sessionid_here"
  }
}
```

Save and exit (Ctrl+X, then Y, then Enter).

## Step 4: Start the Server

```bash
python3 instagram_bridge_server.py
```

You should see:

```
============================================================
🚀 Instagram Bridge Server Starting...
============================================================
✅ Server ready on http://localhost:5002
============================================================
```

## Step 5: Test the Server

Open a new terminal and run:

```bash
# Test health endpoint
curl http://localhost:5002/health

# Should return:
# {"status":"ok","message":"Instagram Bridge Server is running"}
```

Or run the test suite:

```bash
python3 test_bridge_server.py
```

## Step 6: Try the Endpoints

### Get a User Profile

```bash
curl http://localhost:5002/user/instagram
```

Response:
```json
{
  "success": true,
  "username": "instagram",
  "profile_url": "https://www.instagram.com/instagram/",
  "bio": "...",
  "followers": "..."
}
```

### Create a Post (Requires Image)

```bash
curl -X POST http://localhost:5002/post \
  -H "Content-Type: application/json" \
  -d '{
    "caption": "Hello from Instagram Bridge Server! #automation",
    "image_path": "/Users/yourname/Pictures/test-image.jpg"
  }'
```

**Important**:
- Replace `/Users/yourname/Pictures/test-image.jpg` with an actual image path
- Must be absolute path
- Supported formats: JPG, PNG

### Send a DM

```bash
curl -X POST http://localhost:5002/dm \
  -H "Content-Type: application/json" \
  -d '{
    "username": "target_username",
    "message": "Hey! Testing the bridge server."
  }'
```

**Note**: The server will automatically follow the user first (required by Instagram).

## Common Issues

### "No Instagram session found"

**Problem**: Session cookie not loaded

**Solution**: Check that `platforms_auth.json` exists and has correct format

```bash
cat platforms_auth.json
# Should show your sessionid
```

### "Image required for Instagram post"

**Problem**: Trying to post without an image

**Solution**: Instagram always requires an image. Provide `image_path` parameter:

```bash
curl -X POST http://localhost:5002/post \
  -H "Content-Type: application/json" \
  -d '{
    "caption": "Test post",
    "image_path": "/absolute/path/to/image.jpg"
  }'
```

### "Could not find Create button"

**Problem**: Session expired or Instagram UI changed

**Solutions**:
1. Get a fresh sessionid (repeat Step 2)
2. Update `platforms_auth.json`
3. Restart the server

### Server won't start

**Problem**: Port 5002 already in use

**Solution**: Kill existing process or change port:

```bash
# Kill existing server
lsof -ti:5002 | xargs kill -9

# Or edit instagram_bridge_server.py and change port:
# app.run(host='0.0.0.0', port=5003, debug=False)
```

## Architecture Overview

```
┌─────────────────┐
│   Your App      │
│   (Postiz)      │
└────────┬────────┘
         │ HTTP
         │ POST /post
         │ GET /user/:username
         │ POST /dm
         ▼
┌─────────────────┐
│ Instagram       │
│ Bridge Server   │ ← You are here (Port 5002)
│ (Flask)         │
└────────┬────────┘
         │
         │ Playwright
         │ Browser Automation
         ▼
┌─────────────────┐
│   Instagram     │
│   Web UI        │
└─────────────────┘
```

## Next Steps

1. ✅ **Read the full README**: `README_BRIDGE_SERVER.md`
2. ✅ **Compare with Twitter**: `BRIDGE_SERVER_COMPARISON.md`
3. ✅ **Integrate with your app**: Use the REST API endpoints
4. ✅ **Monitor the logs**: Watch for errors and rate limits

## Development Workflow

```bash
# Terminal 1: Run server
python3 instagram_bridge_server.py

# Terminal 2: Test endpoints
curl http://localhost:5002/health
python3 test_bridge_server.py

# Terminal 3: Watch logs
tail -f instagram_bridge_server.log  # If logging to file
```

## Security Reminder

⚠️  **Keep your sessionid private!**
- Never commit `platforms_auth.json` to git
- Add it to `.gitignore`
- Treat it like a password

```bash
# Add to .gitignore
echo "platforms_auth.json" >> .gitignore
```

## API Reference

All endpoints return JSON with consistent format:

**Success Response:**
```json
{
  "success": true,
  "data": "...",
  "message": "..."
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message"
}
```

## Getting Help

- **Server logs**: Check console output for errors
- **Browser window**: Server runs in non-headless mode - you can see what it's doing
- **Test suite**: Run `python3 test_bridge_server.py` to diagnose issues
- **Comparison guide**: Check `BRIDGE_SERVER_COMPARISON.md` for Twitter vs Instagram differences

## Summary

You now have:
- ✅ Instagram Bridge Server running on port 5002
- ✅ REST API endpoints for Instagram automation
- ✅ Test suite for validation
- ✅ Full documentation

**Main File**: `/Users/l.u.c/my-app/uniapi/backend/platforms/instagram/instagram_bridge_server.py`

**Server URL**: `http://localhost:5002`

**Endpoints**:
- GET `/health` - Health check
- POST `/post` - Create Instagram post
- GET `/user/<username>` - Get user profile
- POST `/dm` - Send direct message

Happy automating! 🚀
