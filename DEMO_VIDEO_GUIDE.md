# 📹 Demo Video Recording Guide

## 建议的演示视频内容（30-60秒）

### 方案 A：完整流程演示（推荐）

**时长：60秒**

```bash
# 1. 一键启动（10秒）
cd backend
./start_uniapi.sh
# 显示健康检查的 ✅ 输出

# 2. 打开API文档（10秒）
open http://localhost:8000/api/docs
# 展示Swagger UI界面

# 3. 代码演示（30秒）
# 创建 demo_quick.py 并运行：
cat > demo_quick.py << 'EOF'
from instagram_sdk import InstagramAPI
from tiktok_sdk import TikTokAPI

# Instagram
insta = InstagramAPI()
user = insta.get_user("instagram")
print(f"✅ Instagram: {user['username']}")

# TikTok - 完全相同的接口
tiktok = TikTokAPI()
user = tiktok.get_user("@tiktok")
print(f"✅ TikTok: {user['username']}")

print("\n🎉 5 platforms, 1 unified API!")
EOF

python3 demo_quick.py

# 4. 结束画面（10秒）
# 显示 GitHub 链接: https://github.com/LiuLucian/uniapi
```

### 方案 B：纯代码演示（简洁版）

**时长：30秒**

在终端中逐行展示：

```python
# 打开编辑器，展示代码
from instagram_sdk import InstagramAPI

insta = InstagramAPI()
insta.like_post("https://www.instagram.com/p/ABC123/")  # ✅
insta.send_dm("username", "Hello from UniAPI!")         # ✅

# 切换到TikTok - 完全相同的接口
from tiktok_sdk import TikTokAPI

tiktok = TikTokAPI()
tiktok.like_video("https://www.tiktok.com/@user/video/123")  # ✅
tiktok.send_dm("username", "Hello!")                         # ✅
```

## 录制工具推荐

### macOS
- **Kap** (免费, 开源) - https://getkap.co
  - 支持GIF导出
  - 文件大小优化
  - 推荐设置：30 fps, 1280x720

- **录屏 + ffmpeg转GIF**
  ```bash
  # 使用系统自带录屏（Cmd+Shift+5）
  # 然后转换为GIF
  ffmpeg -i demo.mov -vf "fps=10,scale=800:-1:flags=lanczos" -c:v gif demo.gif
  ```

### 录制技巧

1. **分辨率**：1280x720 或 800x600（适合GitHub展示）
2. **帧率**：10-15 fps（GIF体积小）
3. **文件大小**：< 5MB（GitHub README最佳）
4. **时长**：30-60秒（保持简短）

## 优化GIF文件大小

```bash
# 使用 gifsicle 压缩
brew install gifsicle
gifsicle -O3 --colors 128 demo.gif -o demo_optimized.gif

# 或使用在线工具
# https://ezgif.com/optimize
```

## 上传到GitHub后

取消 README.md 中的注释：

```markdown
<!-- 删除这个注释标记
<img src="demo.gif" alt="UniAPI Demo" width="700">
<p><i>✨ 5 platforms, 1 unified API - that's it.</i></p>
-->
```

删除占位文本：
```markdown
**📹 Demo Video Coming Soon**  # <-- 删除这行
```

## 替代方案：使用 Asciinema（终端录制）

如果不想录制GIF，可以用纯终端录制：

```bash
# 安装 asciinema
brew install asciinema

# 录制
asciinema rec demo.cast

# 上传到 asciinema.org 并嵌入到 README
```

然后在 README 中添加：

```markdown
[![asciicast](https://asciinema.org/a/YOUR_ID.svg)](https://asciinema.org/a/YOUR_ID)
```

## 推荐的最终方案

**最简单有效**：使用 Kap 录制 30 秒演示

1. 启动服务
2. 打开 API 文档
3. 运行 3 行代码示例
4. 显示成功结果
5. GitHub 链接

这样的演示视频最能吸引开发者！
