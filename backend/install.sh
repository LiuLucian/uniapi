#!/bin/bash

# UniAPI 一键安装脚本

echo "============================================================"
echo "📦 UniAPI 一键安装程序"
echo "============================================================"
echo ""

# 检查Python版本
echo "🔍 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装，请先安装Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python版本: $PYTHON_VERSION"
echo ""

# 安装Python依赖
echo "📦 安装Python依赖..."

# 优先使用requirements.txt
if [ -f "requirements.txt" ]; then
    echo "使用 requirements.txt 安装依赖..."

    # 尝试使用 pip3 install -r requirements.txt
    if pip3 install -r requirements.txt 2>/dev/null; then
        echo "✅ 依赖安装成功"
    # 如果失败，尝试 --user
    elif pip3 install --user -r requirements.txt 2>/dev/null; then
        echo "✅ 依赖安装成功 (使用 --user)"
    # 如果还失败，尝试 --break-system-packages (仅macOS/某些Linux)
    elif pip3 install --break-system-packages -r requirements.txt 2>/dev/null; then
        echo "✅ 依赖安装成功 (使用 --break-system-packages)"
    else
        echo "❌ Python依赖安装失败"
        echo "请尝试手动安装: pip3 install -r requirements.txt"
        exit 1
    fi
else
    # 没有requirements.txt，使用旧方法
    echo "未找到 requirements.txt，使用直接安装..."
    pip3 install fastapi uvicorn pydantic pydantic-settings httpx playwright beautifulsoup4 flask python-dotenv loguru 2>/dev/null || \
    pip3 install --user fastapi uvicorn pydantic pydantic-settings httpx playwright beautifulsoup4 flask python-dotenv loguru 2>/dev/null || \
    pip3 install --break-system-packages fastapi uvicorn pydantic pydantic-settings httpx playwright beautifulsoup4 flask python-dotenv loguru

    if [ $? -ne 0 ]; then
        echo "❌ Python依赖安装失败"
        exit 1
    fi
fi

echo "✅ Python依赖安装完成"
echo ""

# 安装Playwright浏览器
echo "🌐 安装Playwright浏览器驱动..."
playwright install chromium
playwright install firefox

if [ $? -ne 0 ]; then
    echo "⚠️  Playwright浏览器安装失败，稍后可手动运行: playwright install"
else
    echo "✅ Playwright浏览器安装完成"
fi
echo ""

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p logs
mkdir -p data
echo "✅ 目录创建完成"
echo ""

# 复制配置文件示例
if [ ! -f "platforms_auth.json" ]; then
    echo "📝 创建配置文件模板..."
    if [ -f "platforms_auth.json.example" ]; then
        cp platforms_auth.json.example platforms_auth.json
        echo "✅ 已创建 platforms_auth.json，请填入你的Cookie"
    else
        cat > platforms_auth.json << 'EOF'
{
  "twitter": {
    "cookies": {
      "auth_token": "",
      "ct0": ""
    }
  },
  "instagram": {
    "cookies": {
      "sessionid": ""
    }
  },
  "tiktok": {
    "sessionid": ""
  },
  "facebook": {
    "cookies": {
      "c_user": "",
      "xs": ""
    }
  },
  "linkedin": {
    "cookies": {
      "li_at": "",
      "JSESSIONID": ""
    }
  }
}
EOF
        echo "✅ 已创建 platforms_auth.json 配置文件"
    fi
else
    echo "ℹ️  platforms_auth.json 已存在，跳过"
fi
echo ""

# 设置脚本权限
echo "🔧 设置脚本执行权限..."
chmod +x start_uniapi.sh
chmod +x stop_uniapi.sh
echo "✅ 权限设置完成"
echo ""

echo "============================================================"
echo "✅ 安装完成！"
echo "============================================================"
echo ""
echo "📋 下一步："
echo ""
echo "1. 配置认证信息（二选一）："
echo "   方式A - 自动获取Cookie："
echo "     python3 platforms/instagram/save_cookies.py"
echo "     python3 platforms/tiktok/save_cookies.py"
echo "     (以此类推其他平台)"
echo ""
echo "   方式B - 手动编辑配置文件："
echo "     nano platforms_auth.json"
echo ""
echo "2. 启动服务："
echo "     ./start_uniapi.sh"
echo ""
echo "3. 访问API文档："
echo "     http://localhost:8000/api/docs"
echo ""
echo "4. 使用Python SDK："
echo "     from instagram_sdk import InstagramAPI"
echo "     api = InstagramAPI()"
echo "     user = api.get_user('instagram')"
echo ""
echo "============================================================"
