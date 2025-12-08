# UniAPI Quick Start Guide

## 1️⃣ One-Click Installation

```bash
# Clone the project
git clone https://github.com/LiuLucian/uniapi.git
cd uniapi/backend

# One-click install all dependencies
./install.sh
```

## 2️⃣ Configure Authentication

### Method 1: Auto-Extract (Recommended)

We provide automated cookie extraction tools for each platform:

```bash
# Instagram
python3 platforms/instagram/save_cookies.py

# TikTok
python3 platforms/tiktok/save_cookies.py

# Facebook
python3 platforms/facebook/save_cookies.py

# LinkedIn
python3 platforms/linkedin/save_cookies.py

# Twitter
python3 platforms/twitter/save_cookies.py
```

### Method 2: Manual Configuration

1. Copy the example configuration file:
```bash
cp platforms_auth.json.example platforms_auth.json
```

2. Manually fill in cookies for each platform (obtained through browser DevTools)

## 3️⃣ Start Services

```bash
# One-click start all services
./start_uniapi.sh

# After startup, automatic health checks will run
# All ✅ marks indicate successful startup
```

## 4️⃣ Use the API

### Method 1: Python SDK (Recommended)

Create a file `test.py`:

```python
from instagram_sdk import InstagramAPI
from tiktok_sdk import TikTokAPI

# Instagram example
insta = InstagramAPI()

# Get user info
user = insta.get_user("instagram")
print(f"Username: {user['username']}, Followers: {user['followers']}")

# Like a post
result = insta.like_post("https://www.instagram.com/p/ABC123/")
print(result)

# Send DM
result = insta.send_dm("username", "Hello from UniAPI!")
print(result)

# TikTok example
tiktok = TikTokAPI()

# Get user
user = tiktok.get_user("@username")
print(user)

# Like a video
result = tiktok.like_video("https://www.tiktok.com/@user/video/123")
print(result)
```

Run the test:
```bash
python3 test.py
```

### Method 2: Direct REST API Calls

```bash
# View API documentation
open http://localhost:8000/api/docs

# Test with curl
curl http://localhost:8000/api/v1/instagram/users/instagram

# Like a post
curl -X POST http://localhost:8000/api/v1/instagram/posts/like \
  -H "Content-Type: application/json" \
  -d '{"post_url": "https://www.instagram.com/p/ABC123/"}'
```

## 5️⃣ Stop Services

```bash
./stop_uniapi.sh
```

## FAQ

### Q: "Dependencies not installed" error?
A: Run `pip3 install --break-system-packages fastapi uvicorn playwright pydantic-settings`, then run `playwright install`

### Q: Health check failed?
A: Check log files:
```bash
tail -f logs/fastapi.log
tail -f logs/instagram_bridge.log
```

### Q: How to get cookies?
A:
1. Open browser and log in to the target platform
2. Press F12 to open DevTools
3. Go to Application/Storage tab
4. Find Cookies section, copy the required cookie values

### Q: What operations are supported?
A: Each platform supports:
- Get user information
- Like/favorite content
- Comment
- Send DM
- Follow/connect users
- Batch operations

Detailed API documentation: http://localhost:8000/api/docs

## Architecture

```
User Code
   ↓
Python SDK (instagram_sdk.py, tiktok_sdk.py, etc.)
   ↓
FastAPI Main Server (Port 8000)
   ↓
Bridge Servers (Ports 5001-5005)
   ↓
Playwright Browser Automation
   ↓
Social Media Platforms
```

## Next Steps

- View complete documentation: `README.md`
- Check example code: `example_usage.py`
- API reference: http://localhost:8000/api/docs
