#!/bin/bash

# UniAPI Backend 启动脚本

echo "🚀 启动 UniAPI 后端服务..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖
if [ ! -f "venv/bin/uvicorn" ]; then
    echo "📥 安装依赖..."
    pip install -r requirements.txt
    playwright install chromium
fi

# 检查 .env 文件
if [ ! -f "../.env" ]; then
    echo "⚠️  .env 文件不存在，从模板复制..."
    cp ../.env.example ../.env
    echo "⚠️  请编辑 .env 文件设置配置"
fi

# 检查 Twitter 认证
AUTH_FILE="$HOME/.distroflow/twitter_browser/auth.json"
if [ ! -f "$AUTH_FILE" ]; then
    echo "⚠️  警告：Twitter 认证文件不存在"
    echo "⚠️  位置：$AUTH_FILE"
    echo "⚠️  请先在 MarketingMind AI 项目中登录 Twitter"
fi

# 启动服务
echo "✅ 启动 FastAPI 服务..."
python3 main.py
