#!/bin/bash
# UniAPI One-Click Setup Script

set -e

echo "============================================================"
echo "🚀 UniAPI Setup - Twitter API without API Keys"
echo "============================================================"
echo ""

# Step 1: Check Python version
echo "📋 Step 1/5: Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+  "
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
echo "✅ Found Python $PYTHON_VERSION"
echo ""

# Step 2: Create virtual environment
echo "📦 Step 2/5: Creating virtual environment..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Step 3: Install dependencies
echo "📥 Step 3/5: Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

# Add Playwright browsers
echo "🌐 Installing Playwright browsers..."
python3 -m playwright install chromium
echo "✅ Dependencies installed"
echo ""

# Step 4: Check Twitter authentication
echo "🔐 Step 4/5: Checking Twitter authentication..."
if [ -d "$HOME/.distroflow/twitter_browser" ]; then
    echo "✅ Twitter authentication found"
else
    echo "⚠️  Twitter authentication not found"
    echo ""
    echo "You need to login to Twitter once. Run:"
    echo "  ./login_twitter.sh"
    echo ""
    read -p "Do you want to login now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd ..
        ./login_twitter.sh
        cd backend
    fi
fi
echo ""

# Step 5: Done
echo "✅ Step 5/5: Setup complete!"
echo ""
echo "============================================================"
echo "🎉 Installation successful!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Start servers:  ./start.sh"
echo "  2. Test API:       python3 backend/test_twitter_api.py"
echo "  3. View docs:      http://localhost:8000/api/docs"
echo ""
