# UniAPI 快速开始指南

## 1️⃣ 一键安装

```bash
# 克隆项目
git clone https://github.com/your-username/uniapi.git
cd uniapi/backend

# 一键安装所有依赖
./install.sh
```

## 2️⃣ 配置认证信息

### 方式1: 自动获取（推荐）

对于每个平台，我们提供了自动化的Cookie提取工具：

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

### 方式2: 手动配置

1. 复制示例配置文件：
```bash
cp platforms_auth.json.example platforms_auth.json
```

2. 手动填入各平台的Cookie（通过浏览器开发者工具获取）

## 3️⃣ 启动服务

```bash
# 一键启动所有服务
./start_uniapi.sh

# 服务启动后会自动进行健康检查
# 看到所有✅标记即表示启动成功
```

## 4️⃣ 使用API

### 方式1: 使用Python SDK（推荐）

创建文件 `test.py`:

```python
from instagram_sdk import InstagramAPI
from tiktok_sdk import TikTokAPI

# Instagram示例
insta = InstagramAPI()

# 获取用户信息
user = insta.get_user("instagram")
print(f"用户名: {user['username']}, 粉丝: {user['followers']}")

# 点赞帖子
result = insta.like_post("https://www.instagram.com/p/ABC123/")
print(result)

# 发送私信
result = insta.send_dm("username", "Hello from UniAPI!")
print(result)

# TikTok示例
tiktok = TikTokAPI()

# 获取用户
user = tiktok.get_user("@username")
print(user)

# 点赞视频
result = tiktok.like_video("https://www.tiktok.com/@user/video/123")
print(result)
```

运行测试：
```bash
python3 test.py
```

### 方式2: 直接调用REST API

```bash
# 查看API文档
open http://localhost:8000/api/docs

# 使用curl测试
curl http://localhost:8000/api/v1/instagram/users/instagram

# 点赞帖子
curl -X POST http://localhost:8000/api/v1/instagram/posts/like \
  -H "Content-Type: application/json" \
  -d '{"post_url": "https://www.instagram.com/p/ABC123/"}'
```

## 5️⃣ 停止服务

```bash
./stop_uniapi.sh
```

## 常见问题

### Q: 提示"依赖未安装"怎么办？
A: 运行 `pip3 install --break-system-packages fastapi uvicorn playwright pydantic-settings`，然后运行 `playwright install`

### Q: 健康检查失败？
A: 检查日志文件：
```bash
tail -f logs/fastapi.log
tail -f logs/instagram_bridge.log
```

### Q: 如何获取Cookie？
A:
1. 打开浏览器，登录目标平台
2. 按F12打开开发者工具
3. 切换到Application/Storage标签
4. 找到Cookies部分，复制需要的Cookie值

### Q: 支持哪些操作？
A: 每个平台支持：
- 获取用户信息
- 点赞/喜欢内容
- 评论
- 发送私信
- 关注/连接用户
- 批量操作

详细API文档见：http://localhost:8000/api/docs

## 架构说明

```
用户代码
   ↓
Python SDK (instagram_sdk.py, tiktok_sdk.py, etc.)
   ↓
FastAPI Main Server (Port 8000)
   ↓
Bridge Servers (Ports 5001-5005)
   ↓
Playwright 浏览器自动化
   ↓
社交媒体平台
```

## 下一步

- 查看完整文档: `README.md`
- 查看示例代码: `example_usage.py`
- API参考文档: http://localhost:8000/api/docs
