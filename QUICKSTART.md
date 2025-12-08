# UniAPI 快速开始指南

## 1. 安装依赖（已完成✅）

```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## 2. 配置环境变量（已完成✅）

已从 `.env.example` 创建 `.env` 文件，使用默认配置即可。

## 3. 准备 Twitter 认证

UniAPI 复用你在 **MarketingMind AI** 项目中已保存的 Twitter 登录状态：

```bash
# 认证文件位置
~/.distroflow/twitter_browser/auth.json
```

如果该文件不存在，请先在 MarketingMind AI 项目中登录：

```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
python3 setup_twitter_auth.py
# 或使用其他登录脚本
```

## 4. 启动 UniAPI 服务

### 方法1：使用启动脚本（推荐）

```bash
cd backend
./run.sh
```

### 方法2：手动启动

```bash
cd backend
source venv/bin/activate
python3 main.py
```

服务将在 **http://localhost:8000** 启动

## 5. 查看 API 文档

浏览器访问：

- **Swagger UI（推荐）**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 6. 测试 API

### 方法1：使用测试脚本

```bash
cd backend
source venv/bin/activate
python3 test_twitter_api.py
```

### 方法2：使用 curl 命令

#### 健康检查

```bash
curl http://localhost:8000/health
```

#### 获取当前用户信息

```bash
curl http://localhost:8000/api/v1/twitter/users/me
```

#### 发布推文

```bash
curl -X POST "http://localhost:8000/api/v1/twitter/tweets" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from UniAPI! 🚀 这是通过爬虫API发送的推文"}'
```

## API 响应示例

### 发布推文响应（兼容 Twitter API v2 格式）

```json
{
  "data": {
    "id": "1234567890123456789",
    "text": "Hello from UniAPI! 🚀 这是通过爬虫API发送的推文"
  }
}
```

### 获取用户信息响应

```json
{
  "data": {
    "id": "1234567890",
    "name": "User Name",
    "username": "yourusername"
  }
}
```

## 项目结构说明

```
uniapi/
├── backend/
│   ├── api/v1/
│   │   └── twitter.py        # Twitter API 路由（POST /tweets, GET /users/me 等）
│   ├── platforms/twitter/
│   │   ├── api.py            # Playwright 爬虫实现（实际发推逻辑）
│   │   └── auth.py           # 认证管理（加载 browser session）
│   ├── core/
│   │   └── config.py         # 配置管理
│   ├── main.py               # FastAPI 入口点
│   ├── test_twitter_api.py   # 测试脚本
│   └── venv/                 # Python 虚拟环境
├── .env                      # 环境变量配置
└── QUICKSTART.md             # 本文档
```

## 核心原理

```
用户请求 → FastAPI 路由 → Playwright 爬虫 → Twitter 网页操作 → 返回 API v2 格式响应
```

**示例流程（发推）**:
1. `POST /api/v1/twitter/tweets` 收到请求
2. FastAPI 调用 `TwitterAPI.create_tweet(text)`
3. Playwright 打开 Twitter 网页
4. 自动填写推文内容并点击发布
5. 从 URL 提取推文 ID
6. 返回标准 Twitter API v2 格式响应

## 与 MarketingMind AI 的关系

**MarketingMind AI**: 营销自动化工具
- 抓取评论 → AI 分析 → 自动发私信

**UniAPI**: 通用社交媒体 API 服务
- 提供标准化 API 接口 → 兼容官方 API 格式 → 可被任何应用调用

**复用逻辑**:
- Twitter 爬虫代码来自 `twitter_bridge_server.py`
- Instagram/TikTok 爬虫将来自 `src/` 目录下的各平台 scraper

## 下一步计划

### Phase 1: 完善 Twitter API ✅ 进行中
- [x] 基础架构
- [x] 发布推文
- [x] 获取用户信息
- [ ] 删除推文
- [ ] 转推/点赞
- [ ] 搜索功能

### Phase 2: 添加更多平台
- [ ] Instagram API 实现
- [ ] TikTok API 实现
- [ ] Facebook API 实现

### Phase 3: SaaS 功能
- [ ] 用户认证系统
- [ ] 多租户支持
- [ ] 使用量统计

## 常见问题

### Q: API 返回 "Twitter authentication not found" 错误？

**A**: 需要先登录 Twitter。请运行：

```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
python3 setup_twitter_auth.py
```

### Q: 如何查看详细日志？

**A**: FastAPI 会在终端输出所有请求日志。Playwright 操作过程中的日志会显示：
- ✅ 登录成功
- 📝 输入推文
- 🔗 推文 URL 等信息

### Q: 能同时运行多个请求吗？

**A**: 目前每个请求都会打开新的浏览器上下文，支持并发。但建议控制并发数量避免被 Twitter 检测为异常行为。

### Q: 和官方 Twitter API 的区别？

**A**:
- **官方 API**: 需要申请开发者账号 + API 密钥，有费用和速率限制
- **UniAPI**: 使用爬虫模拟真人操作，无需 API 密钥，完全免费

**响应格式**: 完全兼容 Twitter API v2 标准

## 技术特点

✅ **无需 API 密钥** - 使用爬虫技术，不需要申请官方 API 权限
✅ **完全免费** - 不产生 API 调用费用
✅ **格式兼容** - 严格遵循官方 API 的请求/响应格式
✅ **易于扩展** - 清晰的架构，方便添加新平台
✅ **本地部署** - 完全控制，数据安全

## 开发调试

### 启用非无头模式（查看浏览器操作）

编辑 `backend/core/config.py`：

```python
PLAYWRIGHT_HEADLESS: bool = False  # 改为 False
```

### 增加超时时间

```python
PLAYWRIGHT_TIMEOUT: int = 60000  # 从 30秒 改为 60秒
```

### 查看详细错误信息

FastAPI 会在终端显示完整的错误堆栈，包括 Playwright 操作失败的详细信息。

## 贡献

欢迎提交 Issue 和 Pull Request！

## License

MIT
