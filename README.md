# UniAPI - Universal Social Media API Platform

<div align="center">

**官方API风格的多平台社交媒体统一接口**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Playwright](https://img.shields.io/badge/Playwright-1.40+-red.svg)](https://playwright.dev/)

</div>

## ✨ 特性

- 🎯 **统一接口**: 所有平台使用相同的API接口，学习成本低
- 🚀 **官方风格**: API设计模仿官方API，简洁优雅
- 🔐 **Cookie认证**: 基于浏览器Cookie，无需申请开发者权限
- 🤖 **浏览器自动化**: 使用Playwright绕过API限制
- 📦 **一键部署**: 自动化安装和启动脚本
- 🌐 **多平台支持**: Twitter、Instagram、TikTok、Facebook、LinkedIn

## 🚀 支持的平台

| 平台 | Bridge Server | SDK | 状态 |
|------|--------------|-----|------|
| **Twitter** | Port 5001 | `twitter_sdk.py` | ✅ 100% |
| **Instagram** | Port 5002 | `instagram_sdk.py` | ✅ 100% |
| **TikTok** | Port 5003 | `tiktok_sdk.py` | ✅ 100% |
| **Facebook** | Port 5004 | `facebook_sdk.py` | ✅ 100% |
| **LinkedIn** | Port 5005 | `linkedin_sdk.py` | ✅ 100% |

## 🏗️ 架构设计

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

## 📦 快速开始

### 1️⃣ 克隆项目

```bash
git clone https://github.com/Liu-Lucian/uniapi.git
cd uniapi
```

### 2️⃣ 一键安装

```bash
cd backend
./install.sh
```

这将自动安装：
- Python依赖 (FastAPI, Playwright, etc.)
- Playwright浏览器驱动
- 创建必要的目录和配置文件

### 3️⃣ 配置认证信息

编辑 `backend/platforms_auth.json`，填入各平台的Cookie：

```json
{
  "instagram": {
    "cookies": {
      "sessionid": "你的Instagram sessionid"
    }
  },
  "twitter": {
    "cookies": {
      "auth_token": "你的Twitter auth_token",
      "ct0": "你的Twitter ct0"
    }
  }
  // ... 其他平台
}
```

> 💡 如何获取Cookie？参考 [QUICK_START.md](QUICK_START.md)

### 4️⃣ 启动服务

```bash
cd backend
./start_uniapi.sh
```

服务启动后会自动进行健康检查，看到所有 ✅ 标记即表示成功。

### 5️⃣ 使用API

#### 方式1: 使用Python SDK（推荐）

```python
from instagram_sdk import InstagramAPI
from tiktok_sdk import TikTokAPI

# Instagram示例
insta = InstagramAPI()
user = insta.get_user("instagram")
print(f"用户名: {user['username']}, 粉丝: {user['followers']}")

insta.like_post("https://www.instagram.com/p/ABC123/")
insta.send_dm("username", "Hello from UniAPI!")

# TikTok示例
tiktok = TikTokAPI()
user = tiktok.get_user("@username")
tiktok.like_video("https://www.tiktok.com/@user/video/123")
```

#### 方式2: 直接调用REST API

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

## 🏗️ 统一API接口

所有平台SDK都遵循**相同的接口设计**：

```python
# 用户操作
api.get_user(username)              # 获取用户信息
api.follow_user(username)           # 关注用户

# 内容操作
api.like_post(url)                  # 点赞/喜欢
api.comment(url, text)              # 评论
api.send_dm(username, message)      # 发送私信

# 批量操作
api.batch_like(urls, delay=5)       # 批量点赞（自动延迟）
```

## 🛠️ 管理命令

```bash
# 启动所有服务
cd backend && ./start_uniapi.sh

# 停止所有服务
cd backend && ./stop_uniapi.sh

# 查看日志
tail -f backend/logs/fastapi.log
tail -f backend/logs/instagram_bridge.log

# 检查服务状态
curl http://localhost:8000/health
curl http://localhost:5002/health  # Instagram bridge
```

## 📁 项目结构

```
uniapi/
├── backend/
│   ├── main.py                 # FastAPI主服务器
│   ├── platforms/              # 平台Bridge服务器
│   │   ├── twitter/
│   │   ├── instagram/
│   │   ├── tiktok/
│   │   ├── facebook/
│   │   └── linkedin/
│   ├── api/v1/                 # FastAPI路由
│   ├── core/                   # 核心配置
│   ├── start_uniapi.sh         # 启动脚本
│   ├── stop_uniapi.sh          # 停止脚本
│   └── install.sh              # 安装脚本
├── instagram_sdk.py            # Instagram Python SDK
├── tiktok_sdk.py               # TikTok Python SDK
├── facebook_sdk.py             # Facebook Python SDK
├── linkedin_sdk.py             # LinkedIn Python SDK
├── twitter_sdk.py              # Twitter Python SDK
├── demo.py                     # 示例代码
├── QUICK_START.md              # 快速开始指南
└── README.md                   # 本文件
```

## 🔧 技术栈

- **FastAPI** - 高性能Python Web框架
- **Playwright** - 跨浏览器自动化工具
- **Flask** - Bridge服务器框架
- **Pydantic** - 数据验证和类型提示
- **Httpx** - 异步HTTP客户端

## 📝 常见问题

### Q: 为什么不直接使用官方API？

A: 大多数社交媒体平台的官方API：
- 需要申请开发者权限（审核流程复杂）
- 功能受限（如Instagram不支持私信API）
- 有严格的调用限制
- 需要付费（如LinkedIn API）

UniAPI通过浏览器自动化绕过这些限制，提供更灵活的解决方案。

### Q: Cookie会过期吗？

A: 会的。通常Cookie有效期为30-90天。过期后需要重新登录并更新 `platforms_auth.json`。

### Q: 是否违反平台规则？

A: 自动化操作可能违反平台服务条款。请仅用于个人学习和测试，不要用于商业用途或大规模操作。

### Q: 如何避免被检测？

A:
- 使用 `auto_delay=True` 启用随机延迟
- 不要频繁操作（建议每次操作间隔5-10秒）
- 使用专用账号，不要用主账号

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

## 🤝 贡献

欢迎提交Issue和Pull Request！

## ⚠️ 免责声明

本项目仅供学习交流使用。使用本项目造成的任何后果由使用者自行承担，作者不承担任何责任。

---

**UniAPI v1.0.0** - 由 [Claude Code](https://claude.com/claude-code) 构建 🤖
