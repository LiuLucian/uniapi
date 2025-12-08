#!/bin/bash
# Stop UniAPI and Bridge Server

echo "🛑 Stopping UniAPI servers..."

# Kill by PID files if they exist
if [ -f "backend/twitter_bridge.pid" ]; then
    TWITTER_BRIDGE_PID=$(cat backend/twitter_bridge.pid)
    kill $TWITTER_BRIDGE_PID 2>/dev/null && echo "✅ Stopped Twitter Bridge Server (PID: $TWITTER_BRIDGE_PID)"
    rm backend/twitter_bridge.pid
fi

if [ -f "backend/instagram_bridge.pid" ]; then
    INSTAGRAM_BRIDGE_PID=$(cat backend/instagram_bridge.pid)
    kill $INSTAGRAM_BRIDGE_PID 2>/dev/null && echo "✅ Stopped Instagram Bridge Server (PID: $INSTAGRAM_BRIDGE_PID)"
    rm backend/instagram_bridge.pid
fi

if [ -f "backend/uniapi.pid" ]; then
    UNIAPI_PID=$(cat backend/uniapi.pid)
    kill $UNIAPI_PID 2>/dev/null && echo "✅ Stopped UniAPI (PID: $UNIAPI_PID)"
    rm backend/uniapi.pid
fi

# Fallback: kill by process name
pkill -f "twitter_bridge_server.py" 2>/dev/null && echo "✅ Killed remaining Twitter bridge processes"
pkill -f "instagram_bridge_server.py" 2>/dev/null && echo "✅ Killed remaining Instagram bridge processes"
pkill -f "uvicorn main:app" 2>/dev/null && echo "✅ Killed remaining UniAPI processes"

echo "✅ All servers stopped"
