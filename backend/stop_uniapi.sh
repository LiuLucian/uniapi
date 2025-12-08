#!/bin/bash

# UniAPI 统一停止脚本

echo "============================================================"
echo "🛑 Stopping UniAPI Services..."
echo "============================================================"
echo ""

# 进入backend目录
cd "$(dirname "$0")"

# 停止所有服务
echo "Stopping all services..."

# 使用pkill停止所有相关进程
pkill -f "twitter_bridge_server.py"
pkill -f "instagram_bridge_server.py"
pkill -f "tiktok_bridge_server.py"
pkill -f "facebook_bridge_server.py"
pkill -f "linkedin_bridge_server.py"
pkill -f "uvicorn main:app"

# 删除PID文件
rm -f logs/*.pid

sleep 2

echo ""
echo "✅ All UniAPI services stopped"
echo ""
echo "============================================================"
