#!/bin/bash

# UniAPI 统一启动脚本
# 一键启动所有Bridge Servers + FastAPI主服务器

echo "============================================================"
echo "🚀 UniAPI - Universal Social Media API Platform"
echo "============================================================"
echo ""

# 进入backend目录
cd "$(dirname "$0")"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# 检查依赖
echo "📦 Checking dependencies..."
python3 -c "import playwright" 2>/dev/null || { echo "❌ Playwright not installed. Run: pip install playwright && playwright install"; exit 1; }
python3 -c "import flask" 2>/dev/null || { echo "❌ Flask not installed. Run: pip install flask"; exit 1; }
python3 -c "import fastapi" 2>/dev/null || { echo "❌ FastAPI not installed. Run: pip install fastapi uvicorn"; exit 1; }

echo "✅ All dependencies found"
echo ""

# 创建日志目录
mkdir -p logs

# 停止所有现有服务
echo "🔄 Stopping existing services..."
pkill -f "twitter_bridge_server.py" 2>/dev/null
pkill -f "instagram_bridge_server.py" 2>/dev/null
pkill -f "tiktok_bridge_server.py" 2>/dev/null
pkill -f "facebook_bridge_server.py" 2>/dev/null
pkill -f "linkedin_bridge_server.py" 2>/dev/null
pkill -f "uvicorn main:app" 2>/dev/null
sleep 2

echo "✅ Stopped existing services"
echo ""

# 启动所有Bridge Servers
echo "🔧 Starting Bridge Servers..."
echo ""

# Twitter Bridge Server (Port 5001)
echo "  [1/5] Starting Twitter Bridge Server (Port 5001)..."
cd platforms/twitter
python3 twitter_bridge_server.py > ../../logs/twitter_bridge.log 2>&1 &
TWITTER_PID=$!
cd ../..
sleep 1

# Instagram Bridge Server (Port 5002)
echo "  [2/5] Starting Instagram Bridge Server (Port 5002)..."
cd platforms/instagram
python3 instagram_bridge_server.py > ../../logs/instagram_bridge.log 2>&1 &
INSTAGRAM_PID=$!
cd ../..
sleep 1

# TikTok Bridge Server (Port 5003)
echo "  [3/5] Starting TikTok Bridge Server (Port 5003)..."
cd platforms/tiktok
python3 tiktok_bridge_server.py > ../../logs/tiktok_bridge.log 2>&1 &
TIKTOK_PID=$!
cd ../..
sleep 1

# Facebook Bridge Server (Port 5004)
echo "  [4/5] Starting Facebook Bridge Server (Port 5004)..."
cd platforms/facebook
python3 facebook_bridge_server.py > ../../logs/facebook_bridge.log 2>&1 &
FACEBOOK_PID=$!
cd ../..
sleep 1

# LinkedIn Bridge Server (Port 5005)
echo "  [5/5] Starting LinkedIn Bridge Server (Port 5005)..."
cd platforms/linkedin
python3 linkedin_bridge_server.py > ../../logs/linkedin_bridge.log 2>&1 &
LINKEDIN_PID=$!
cd ../..
sleep 2

echo ""
echo "✅ All Bridge Servers started"
echo ""

# 启动FastAPI主服务器
echo "🌐 Starting FastAPI Main Server (Port 8000)..."
uvicorn main:app --host 0.0.0.0 --port 8000 > logs/fastapi.log 2>&1 &
FASTAPI_PID=$!
sleep 3

echo "✅ FastAPI Main Server started"
echo ""

# 健康检查
echo "🔍 Health Check..."
echo ""

check_service() {
    local name=$1
    local port=$2
    local url="http://localhost:$port/health"

    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")

    if [ "$response" = "200" ]; then
        echo "  ✅ $name (Port $port) - Running"
        return 0
    else
        echo "  ❌ $name (Port $port) - Not responding"
        return 1
    fi
}

# 检查所有服务
check_service "Twitter Bridge" 5001
check_service "Instagram Bridge" 5002
check_service "TikTok Bridge" 5003
check_service "Facebook Bridge" 5004
check_service "LinkedIn Bridge" 5005
check_service "FastAPI Main" 8000

echo ""
echo "============================================================"
echo "✅ UniAPI is running!"
echo "============================================================"
echo ""
echo "📊 Service Status:"
echo "  • FastAPI Main Server:    http://localhost:8000"
echo "  • API Documentation:      http://localhost:8000/api/docs"
echo "  • Twitter Bridge:         http://localhost:5001/health"
echo "  • Instagram Bridge:       http://localhost:5002/health"
echo "  • TikTok Bridge:          http://localhost:5003/health"
echo "  • Facebook Bridge:        http://localhost:5004/health"
echo "  • LinkedIn Bridge:        http://localhost:5005/health"
echo ""
echo "📝 Logs:"
echo "  • FastAPI:                logs/fastapi.log"
echo "  • Twitter:                logs/twitter_bridge.log"
echo "  • Instagram:              logs/instagram_bridge.log"
echo "  • TikTok:                 logs/tiktok_bridge.log"
echo "  • Facebook:               logs/facebook_bridge.log"
echo "  • LinkedIn:               logs/linkedin_bridge.log"
echo ""
echo "🛑 To stop all services:"
echo "  ./stop_uniapi.sh"
echo ""
echo "============================================================"

# 保存PID
echo "$FASTAPI_PID" > logs/fastapi.pid
echo "$TWITTER_PID" > logs/twitter_bridge.pid
echo "$INSTAGRAM_PID" > logs/instagram_bridge.pid
echo "$TIKTOK_PID" > logs/tiktok_bridge.pid
echo "$FACEBOOK_PID" > logs/facebook_bridge.pid
echo "$LINKEDIN_PID" > logs/linkedin_bridge.pid
