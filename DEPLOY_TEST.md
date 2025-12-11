# 一键部署测试指南

## 🚀 快速测试部署

### 方式1：完整安装（推荐）

```bash
cd /Users/l.u.c/my-app/uniapi
cd backend
./install.sh
```

**预期结果**：
- ✅ Python依赖安装完成
- ✅ Playwright浏览器安装完成
- ✅ 创建必要目录
- ✅ 生成 platforms_auth.json 模板
- ✅ 设置脚本执行权限

### 方式2：快速验证（只装依赖）

```bash
# 在项目根目录
pip3 install -r requirements.txt
playwright install chromium
```

### 方式3：虚拟环境（最安全）

```bash
cd /Users/l.u.c/my-app/uniapi

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
playwright install chromium

# 进入backend
cd backend

# 启动服务
./start_uniapi.sh
```

---

## 📋 部署检查清单

### 1. 前置条件
- [ ] Python 3.8+ 已安装
- [ ] pip3 可用
- [ ] 网络连接正常

### 2. 安装验证
```bash
# 检查Python版本
python3 --version

# 检查依赖是否安装
python3 -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python3 -c "import playwright; print('Playwright: OK')"
python3 -c "import httpx; print('HTTPX: OK')"
```

### 3. 文件验证
```bash
# 检查关键文件是否存在
ls -la backend/install.sh
ls -la backend/start_uniapi.sh
ls -la backend/stop_uniapi.sh

# 检查SDK文件
ls -la *_sdk.py
```

应该看到：
- ✅ instagram_sdk.py
- ✅ twitter_sdk.py
- ✅ tiktok_sdk.py
- ✅ facebook_sdk.py
- ✅ linkedin_sdk.py

### 4. 启动测试（无需配置Cookie）

```bash
cd backend
./start_uniapi.sh
```

**预期输出**：
```
============================================================
🚀 UniAPI 启动程序
============================================================

🔍 检查环境...
✅ Python 3.x 已安装

📦 检查依赖...
✅ FastAPI 已安装
✅ Playwright 已安装
✅ HTTPX 已安装

🌐 启动服务...
✅ Twitter Bridge Server started on port 5001
✅ Instagram Bridge Server started on port 5002
✅ TikTok Bridge Server started on port 5003
✅ Facebook Bridge Server started on port 5004
✅ LinkedIn Bridge Server started on port 5005
✅ UniAPI Main Server started on http://localhost:8000

============================================================
✅ 所有服务启动成功！
============================================================
```

### 5. API访问测试

打开浏览器访问：
```
http://localhost:8000/api/docs
```

应该看到 FastAPI Swagger UI 文档界面。

### 6. 健康检查

```bash
# 检查主服务
curl http://localhost:8000/health

# 检查各平台bridge
curl http://localhost:5001/health  # Twitter
curl http://localhost:5002/health  # Instagram
curl http://localhost:5003/health  # TikTok
curl http://localhost:5004/health  # Facebook
curl http://localhost:5005/health  # LinkedIn
```

---

## ⚠️ 常见问题

### 问题1：pip install 失败

**错误**：`error: externally-managed-environment`

**解决**：使用虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 问题2：playwright install 失败

**错误**：浏览器下载失败

**解决**：
```bash
# 只安装 chromium（最小化）
playwright install chromium

# 或手动指定镜像
PLAYWRIGHT_DOWNLOAD_HOST=https://playwright.azureedge.net playwright install
```

### 问题3：端口被占用

**错误**：`Address already in use`

**解决**：
```bash
# 查找占用进程
lsof -i :8000
lsof -i :5001

# 杀死进程
kill -9 <PID>

# 或使用stop脚本
cd backend && ./stop_uniapi.sh
```

### 问题4：platforms_auth.json 报错

**说明**：这是正常的！没有配置Cookie时，API会返回认证错误。

**不影响部署测试**：只要服务能启动，部署就是成功的。

**配置Cookie**：参考 QUICK_START.md

---

## 📊 部署成功标准

满足以下条件即为部署成功：

✅ **Level 1 - 依赖安装**
- pip install 成功
- playwright install 成功

✅ **Level 2 - 服务启动**
- 6个服务全部启动（Main + 5个Bridge）
- 无报错退出

✅ **Level 3 - API可访问**
- http://localhost:8000/api/docs 可访问
- Swagger UI正常显示

✅ **Level 4 - 健康检查**
- 所有 /health 端点返回 200

**不需要**配置Cookie也算部署成功！Cookie是使用阶段的事情。

---

## 🎉 如果遇到无法解决的问题

1. 检查Python版本：`python3 --version` (需要 3.8+)
2. 检查网络连接
3. 尝试虚拟环境方式
4. 查看详细错误日志
5. 提交 Issue：https://github.com/LiuLucian/uniapi/issues

---

**总结：UniAPI 的"一键部署"指的是依赖安装和服务启动，不包括Cookie配置。**
