#!/bin/bash
# UniAPI Startup Script - Runs both Bridge Server and UniAPI

set -e

echo "============================================================"
echo "🚀 Starting UniAPI - Multi-Platform API"
echo "============================================================"
echo ""

# Check if setup was run
if [ ! -d "backend/venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first"
    exit 1
fi

# Kill existing servers if running
echo "🧹 Cleaning up existing servers..."
pkill -f "twitter_bridge_server.py" 2>/dev/null || true
pkill -f "instagram_bridge_server.py" 2>/dev/null || true
pkill -f "uvicorn main:app" 2>/dev/null || true
sleep 2
echo "✅ Cleanup complete"
echo ""

# Start bridge servers in background
echo "🌉 Starting Twitter Bridge Server (Port 5001)..."
cd backend
source venv/bin/activate
nohup python3 platforms/twitter/twitter_bridge_server.py > twitter_bridge.log 2>&1 &
TWITTER_BRIDGE_PID=$!
echo $TWITTER_BRIDGE_PID > twitter_bridge.pid
echo "✅ Twitter Bridge Server started (PID: $TWITTER_BRIDGE_PID)"
sleep 2
echo ""

echo "📸 Starting Instagram Bridge Server (Port 5002)..."
nohup python3 platforms/instagram/instagram_bridge_server.py > instagram_bridge.log 2>&1 &
INSTAGRAM_BRIDGE_PID=$!
echo $INSTAGRAM_BRIDGE_PID > instagram_bridge.pid
echo "✅ Instagram Bridge Server started (PID: $INSTAGRAM_BRIDGE_PID)"
sleep 2
echo ""

# Start UniAPI server in background
echo "🚀 Starting UniAPI Server (Port 8000)..."
nohup python3 main.py > uniapi.log 2>&1 &
UNIAPI_PID=$!
echo $UNIAPI_PID > uniapi.pid
echo "✅ UniAPI started (PID: $UNIAPI_PID)"
sleep 3
echo ""

# Verify servers are running
echo "🔍 Verifying servers..."
if curl -s http://localhost:5001/health > /dev/null 2>&1; then
    echo "✅ Twitter Bridge responding on http://localhost:5001"
else
    echo "⚠️  Twitter Bridge may not be ready yet (check logs: backend/twitter_bridge.log)"
fi

if curl -s http://localhost:5002/health > /dev/null 2>&1; then
    echo "✅ Instagram Bridge responding on http://localhost:5002"
else
    echo "⚠️  Instagram Bridge may not be ready yet (check logs: backend/instagram_bridge.log)"
fi

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ UniAPI responding on http://localhost:8000"
else
    echo "⚠️  UniAPI may not be ready yet (check logs: backend/uniapi.log)"
fi

echo ""
echo "============================================================"
echo "🎉 All servers started successfully!"
echo "============================================================"
echo ""
echo "📝 API Documentation:     http://localhost:8000/api/docs"
echo ""
echo "🌉 Bridge Servers:"
echo "   Twitter:               http://localhost:5001/health"
echo "   Instagram:             http://localhost:5002/health"
echo ""
echo "🚀 UniAPI Endpoints:"
echo "   Twitter:               http://localhost:8000/api/v1/twitter"
echo "   Instagram:             http://localhost:8000/api/v1/instagram"
echo ""
echo "📋 Logs:"
echo "   Twitter Bridge:        tail -f backend/twitter_bridge.log"
echo "   Instagram Bridge:      tail -f backend/instagram_bridge.log"
echo "   UniAPI:                tail -f backend/uniapi.log"
echo ""
echo "⏹️  Stop servers:          ./stop.sh"
echo ""
