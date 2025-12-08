# Instagram API - 用户使用指南

UniAPI 提供完整的 Instagram API 接口，支持所有官方API功能，并扩展了官方API不支持的自动化操作。

## 快速开始

### 1. 获取访问权限

#### 配置认证信息

在项目根目录创建 `.env` 文件：

```bash
# .env
INSTAGRAM_SESSION_ID=your_session_id_here
```

**如何获取 Session ID：**

1. 使用 Firefox 浏览器登录 Instagram
2. 打开开发者工具（F12）
3. 进入 Storage → Cookies → https://www.instagram.com
4. 找到 `sessionid` cookie，复制其值
5. 粘贴到 `.env` 文件

### 2. 启动 API 服务

```bash
# 终端 1: 启动主 API 服务
cd /Users/l.u.c/my-app/uniapi/backend
uvicorn main:app --reload --port 8000

# 终端 2: 启动 Instagram 自动化服务
python3 platforms/instagram/instagram_bridge_server.py
```

服务启动后：
- **API 端点**: `http://localhost:8000/api/v1/instagram`
- **API 文档**: `http://localhost:8000/docs` (自动生成)

### 3. 验证服务状态

```bash
curl http://localhost:8000/api/v1/instagram/health
```

**响应示例：**
```json
{
  "status": "ok",
  "message": "Instagram API is running",
  "bridge_status": "connected"
}
```

---

## API 使用示例

### Python 客户端

#### 安装依赖

```bash
pip install requests
```

#### 基础用法

```python
import requests

class InstagramAPI:
    def __init__(self, base_url="http://localhost:8000/api/v1/instagram"):
        self.base_url = base_url

    def like_post(self, post_url):
        """点赞帖子"""
        media_id = self._extract_media_id(post_url)
        response = requests.post(f"{self.base_url}/media/{media_id}/like")
        return response.json()

    def follow_user(self, username):
        """关注用户"""
        response = requests.post(f"{self.base_url}/users/{username}/follow")
        return response.json()

    def comment_on_post(self, post_url, text):
        """评论帖子"""
        media_id = self._extract_media_id(post_url)
        response = requests.post(
            f"{self.base_url}/media/{media_id}/comments",
            json={"text": text}
        )
        return response.json()

    def get_user_posts(self, username, max_results=20):
        """获取用户帖子列表"""
        response = requests.get(
            f"{self.base_url}/users/{username}/media",
            params={"max_results": max_results}
        )
        return response.json()

    def search_by_tag(self, tag, max_results=20):
        """按标签搜索帖子"""
        response = requests.get(
            f"{self.base_url}/tags/{tag}/media/recent",
            params={"max_results": max_results}
        )
        return response.json()

    def send_dm(self, username, message):
        """发送私信"""
        response = requests.post(
            f"{self.base_url}/users/{username}/dm",
            json={"username": username, "message": message}
        )
        return response.json()

    @staticmethod
    def _extract_media_id(post_url):
        """从URL提取media_id"""
        if '/p/' in post_url:
            return post_url.split('/p/')[-1].split('/')[0]
        return post_url


# 使用示例
api = InstagramAPI()

# 点赞帖子
result = api.like_post("https://www.instagram.com/p/ABC123xyz/")
print(result)

# 关注用户
result = api.follow_user("username")
print(result)

# 评论帖子
result = api.comment_on_post(
    "https://www.instagram.com/p/ABC123xyz/",
    "Great post! 🔥"
)
print(result)

# 获取用户帖子
posts = api.get_user_posts("username", max_results=10)
print(f"Found {len(posts['posts'])} posts")

# 搜索标签
results = api.search_by_tag("travel", max_results=20)
print(f"Found {len(results['posts'])} posts")

# 发送私信
result = api.send_dm("username", "Hello from UniAPI!")
print(result)
```

---

### JavaScript/Node.js 客户端

```javascript
const axios = require('axios');

class InstagramAPI {
  constructor(baseURL = 'http://localhost:8000/api/v1/instagram') {
    this.baseURL = baseURL;
  }

  async likePost(postUrl) {
    const mediaId = this.extractMediaId(postUrl);
    const response = await axios.post(`${this.baseURL}/media/${mediaId}/like`);
    return response.data;
  }

  async followUser(username) {
    const response = await axios.post(`${this.baseURL}/users/${username}/follow`);
    return response.data;
  }

  async commentOnPost(postUrl, text) {
    const mediaId = this.extractMediaId(postUrl);
    const response = await axios.post(
      `${this.baseURL}/media/${mediaId}/comments`,
      { text }
    );
    return response.data;
  }

  async getUserPosts(username, maxResults = 20) {
    const response = await axios.get(`${this.baseURL}/users/${username}/media`, {
      params: { max_results: maxResults }
    });
    return response.data;
  }

  async searchByTag(tag, maxResults = 20) {
    const response = await axios.get(`${this.baseURL}/tags/${tag}/media/recent`, {
      params: { max_results: maxResults }
    });
    return response.data;
  }

  async sendDM(username, message) {
    const response = await axios.post(`${this.baseURL}/users/${username}/dm`, {
      username,
      message
    });
    return response.data;
  }

  extractMediaId(postUrl) {
    if (postUrl.includes('/p/')) {
      return postUrl.split('/p/')[1].split('/')[0];
    }
    return postUrl;
  }
}

// 使用示例
const api = new InstagramAPI();

// 点赞帖子
api.likePost('https://www.instagram.com/p/ABC123xyz/')
  .then(result => console.log(result));

// 关注用户
api.followUser('username')
  .then(result => console.log(result));

// 评论帖子
api.commentOnPost('https://www.instagram.com/p/ABC123xyz/', 'Great! 🔥')
  .then(result => console.log(result));

// 获取用户帖子
api.getUserPosts('username', 10)
  .then(posts => console.log(`Found ${posts.posts.length} posts`));

// 搜索标签
api.searchByTag('travel', 20)
  .then(results => console.log(`Found ${results.posts.length} posts`));

// 发送私信
api.sendDM('username', 'Hello!')
  .then(result => console.log(result));
```

---

### cURL 命令行使用

```bash
# 点赞帖子
curl -X POST http://localhost:8000/api/v1/instagram/media/ABC123xyz/like

# 取消点赞
curl -X DELETE http://localhost:8000/api/v1/instagram/media/ABC123xyz/like

# 关注用户
curl -X POST http://localhost:8000/api/v1/instagram/users/username/follow

# 取消关注
curl -X DELETE http://localhost:8000/api/v1/instagram/users/username/follow

# 评论帖子
curl -X POST http://localhost:8000/api/v1/instagram/media/ABC123xyz/comments \
  -H "Content-Type: application/json" \
  -d '{"text": "Great post! 🔥"}'

# 获取帖子详情
curl http://localhost:8000/api/v1/instagram/media/ABC123xyz

# 获取用户资料
curl http://localhost:8000/api/v1/instagram/users/username

# 获取用户帖子列表
curl "http://localhost:8000/api/v1/instagram/users/username/media?max_results=10"

# 搜索标签
curl "http://localhost:8000/api/v1/instagram/tags/travel/media/recent?max_results=20"

# 发送私信
curl -X POST http://localhost:8000/api/v1/instagram/users/username/dm \
  -H "Content-Type: application/json" \
  -d '{"username": "username", "message": "Hello from UniAPI!"}'

# 发布帖子
curl -X POST http://localhost:8000/api/v1/instagram/media \
  -H "Content-Type: application/json" \
  -d '{
    "caption": "My new post #instagram",
    "image_path": "/path/to/image.jpg"
  }'
```

---

## 完整 API 参考

### 用户操作

#### 获取用户资料
```http
GET /api/v1/instagram/users/{username}
```

**响应：**
```json
{
  "success": true,
  "username": "username",
  "profile_url": "https://www.instagram.com/username/",
  "bio": "User bio text",
  "followers": "1.2K"
}
```

#### 关注用户
```http
POST /api/v1/instagram/users/{username}/follow
```

#### 取消关注
```http
DELETE /api/v1/instagram/users/{username}/follow
```

#### 获取用户帖子
```http
GET /api/v1/instagram/users/{username}/media?max_results=20
```

**响应：**
```json
{
  "success": true,
  "username": "username",
  "posts": [
    {
      "url": "https://www.instagram.com/p/ABC123/",
      "shortcode": "ABC123"
    }
  ],
  "count": 10
}
```

---

### 帖子操作

#### 点赞帖子
```http
POST /api/v1/instagram/media/{media_id}/like
```

#### 取消点赞
```http
DELETE /api/v1/instagram/media/{media_id}/like
```

#### 评论帖子
```http
POST /api/v1/instagram/media/{media_id}/comments
Content-Type: application/json

{
  "text": "Great post!"
}
```

#### 获取帖子详情
```http
GET /api/v1/instagram/media/{media_id}
```

**响应：**
```json
{
  "success": true,
  "media_id": "ABC123",
  "caption": "Post caption",
  "likes": 1234,
  "comments": 56,
  "author": "username"
}
```

#### 发布帖子
```http
POST /api/v1/instagram/media
Content-Type: application/json

{
  "caption": "My new post #instagram",
  "image_path": "/path/to/image.jpg"
}
```

---

### 搜索与发现

#### 按标签搜索
```http
GET /api/v1/instagram/tags/{tag}/media/recent?max_results=20
```

**响应：**
```json
{
  "success": true,
  "tag": "travel",
  "posts": [
    {
      "url": "https://www.instagram.com/p/ABC123/",
      "shortcode": "ABC123"
    }
  ],
  "count": 20
}
```

---

### 私信操作

#### 发送私信
```http
POST /api/v1/instagram/users/{username}/dm
Content-Type: application/json

{
  "username": "target_username",
  "message": "Hello! This is a message."
}
```

**响应：**
```json
{
  "success": true,
  "message": "DM sent successfully",
  "username": "target_username"
}
```

---

## 实战场景示例

### 场景1: 自动点赞和评论营销

```python
api = InstagramAPI()

# 1. 搜索相关标签的帖子
posts = api.search_by_tag("fitness", max_results=50)

for post in posts['posts'][:10]:  # 只处理前10个
    post_url = post['url']

    # 2. 点赞帖子
    api.like_post(post_url)
    print(f"✅ Liked: {post_url}")

    # 3. 发表评论
    api.comment_on_post(post_url, "Great content! 💪")
    print(f"💬 Commented on: {post_url}")

    # 避免频繁操作，添加延迟
    import time
    time.sleep(10)
```

### 场景2: 批量关注和私信

```python
api = InstagramAPI()

# 目标用户列表
target_users = ["user1", "user2", "user3"]

message_template = """
Hi {username}! 👋

I noticed your amazing content.
Would love to connect!

Best regards
"""

for username in target_users:
    # 1. 关注用户
    result = api.follow_user(username)
    print(f"✅ Followed: @{username}")

    # 2. 发送个性化私信
    message = message_template.format(username=username)
    api.send_dm(username, message)
    print(f"📨 Sent DM to: @{username}")

    # 延迟避免限流
    import time
    time.sleep(30)
```

### 场景3: 竞品监控

```python
api = InstagramAPI()

# 监控竞品账号
competitors = ["competitor1", "competitor2"]

for competitor in competitors:
    # 获取最新帖子
    posts = api.get_user_posts(competitor, max_results=5)

    print(f"\n📊 @{competitor} 最新帖子:")
    for post in posts['posts']:
        # 获取帖子详情
        details = api.get_post_details(post['url'])
        print(f"  • {details['caption'][:50]}...")
        print(f"    👍 {details['likes']} 💬 {details['comments']}")
```

### 场景4: 用户互动自动化

```python
api = InstagramAPI()

# 获取自己的帖子
my_posts = api.get_user_posts("my_username", max_results=10)

for post in my_posts['posts']:
    # 获取帖子详情
    details = api.get_post_details(post['url'])

    print(f"\n帖子: {post['url']}")
    print(f"互动数据: {details['likes']} 点赞, {details['comments']} 评论")

    # 可以进一步分析评论者并回关等
```

---

## 高级功能

### 批量操作封装

```python
class InstagramBatchAPI(InstagramAPI):
    """批量操作封装"""

    def batch_like_posts(self, post_urls, delay=5):
        """批量点赞"""
        results = []
        for url in post_urls:
            result = self.like_post(url)
            results.append(result)
            time.sleep(delay)
        return results

    def batch_follow_users(self, usernames, delay=10):
        """批量关注"""
        results = []
        for username in usernames:
            result = self.follow_user(username)
            results.append(result)
            time.sleep(delay)
        return results

    def batch_send_dms(self, users_messages, delay=30):
        """批量发送私信

        Args:
            users_messages: [(username, message), ...]
        """
        results = []
        for username, message in users_messages:
            result = self.send_dm(username, message)
            results.append(result)
            time.sleep(delay)
        return results


# 使用示例
batch_api = InstagramBatchAPI()

# 批量点赞
post_urls = [
    "https://www.instagram.com/p/ABC1/",
    "https://www.instagram.com/p/ABC2/",
    "https://www.instagram.com/p/ABC3/"
]
batch_api.batch_like_posts(post_urls, delay=10)
```

---

## 错误处理

### 标准错误响应

```json
{
  "success": false,
  "error": "Error message here",
  "message": "Detailed error description"
}
```

### 常见错误码

| HTTP 状态码 | 含义 | 解决方案 |
|------------|------|---------|
| 200 | 成功 | - |
| 400 | 请求参数错误 | 检查请求参数格式 |
| 500 | 服务器内部错误 | 查看服务器日志 |
| 503 | Bridge服务不可用 | 检查Bridge服务是否启动 |

### Python 错误处理示例

```python
def safe_like_post(api, post_url):
    """安全的点赞操作"""
    try:
        result = api.like_post(post_url)

        if result.get('success'):
            print(f"✅ Successfully liked: {post_url}")
            return True
        else:
            print(f"❌ Failed to like: {result.get('error')}")
            return False

    except requests.exceptions.Timeout:
        print(f"⏰ Timeout while liking: {post_url}")
        return False

    except requests.exceptions.ConnectionError:
        print(f"🔌 Connection error. Check if API is running.")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
```

---

## 性能优化建议

### 1. 合理使用延迟

```python
import time

# 避免频繁操作
time.sleep(5)  # 操作之间延迟5秒

# 随机延迟更自然
import random
time.sleep(random.uniform(3, 10))
```

### 2. 批量操作

```python
# ✅ 推荐：先获取所有数据，再批量处理
posts = api.get_user_posts("username", max_results=50)
for post in posts['posts']:
    process_post(post)

# ❌ 不推荐：单独调用多次
for i in range(50):
    post = api.get_single_post(i)  # 多次调用
```

### 3. 缓存数据

```python
import json
from pathlib import Path

# 缓存用户信息
def get_user_with_cache(api, username):
    cache_file = Path(f"cache/{username}.json")

    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)

    user = api.get_user(username)
    cache_file.parent.mkdir(exist_ok=True)

    with open(cache_file, 'w') as f:
        json.dump(user, f)

    return user
```

---

## 限制与注意事项

### 速率限制

Instagram 有严格的速率限制，建议：

- **点赞/取消点赞**: 最多 200次/小时
- **关注/取消关注**: 最多 20次/小时
- **评论**: 最多 20次/小时
- **私信**: 最多 50次/小时
- **搜索**: 最多 100次/小时

### 最佳实践

1. **使用延迟**: 操作之间至少间隔 3-5 秒
2. **随机化行为**: 使用随机延迟和不同的操作顺序
3. **避免过度自动化**: 混合手动和自动操作
4. **监控账号状态**: 注意 Instagram 的警告信息
5. **使用专用账号**: 不要在主账号上测试

---

## 常见问题 FAQ

### Q: 如何更新 Session ID？

**A:** Session ID 会过期，重新登录后更新 `.env` 文件中的值即可。

### Q: API 响应很慢怎么办？

**A:** 每个操作需要浏览器自动化，正常耗时 10-30 秒。这是为了模拟真实用户行为。

### Q: 可以并发调用 API 吗？

**A:** 不建议。Instagram 会检测异常行为。建议串行调用并添加延迟。

### Q: 支持哪些图片格式？

**A:** 支持 JPG, PNG。建议尺寸 1080x1080 像素。

### Q: 如何避免被 Instagram 封号？

**A:**
- 使用专用测试账号
- 严格控制操作频率
- 使用真实的延迟
- 不要在短时间内大量操作

---

## 技术支持

- **文档**: `INSTAGRAM_TESTING_GUIDE.md`
- **API 文档**: `http://localhost:8000/docs`
- **功能状态**: `INSTAGRAM_API_FEATURES.md`

---

**最后更新**: 2025-01-07
**版本**: 1.0.0
**作者**: UniAPI Team
