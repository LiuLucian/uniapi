# 录制最终Demo GIF

## 准备（1分钟）

```bash
cd /Users/l.u.c/my-app/uniapi

# 确保demo脚本存在
ls demo_visual.py

# 测试运行一次
python3 demo_visual.py
```

## 录制步骤（15秒GIF）

### 工具选择

**推荐：macOS自带录屏**（最简单）
1. Command+Shift+5
2. 选择"录制所选部分"
3. 框住终端窗口
4. 点击"录制"

### 录制内容

**准备终端：**
- 放大字体：Command+"+" 放到18号
- 清空终端：`clear`
- 终端窗口调到合适大小（不要太大）

**执行命令：**
```bash
cd /Users/l.u.c/my-app/uniapi
python3 demo_visual.py
```

**等待完成**（约10-12秒自动播放完）

**停止录制**：点击屏幕顶部的停止按钮

### 保存为GIF

**方法1：在线转换（最简单）**
1. 保存录屏为 `demo.mov`
2. 访问 https://ezgif.com/video-to-gif
3. 上传 `demo.mov`
4. 设置：
   - Start time: 0
   - End time: 自动
   - Size: Width 800px
   - Frame rate: 10-15 fps
5. 点击 "Convert to GIF"
6. 下载，重命名为 `demo.gif`

**方法2：用ffmpeg（如果已安装）**
```bash
brew install ffmpeg
ffmpeg -i demo.mov -vf "fps=15,scale=800:-1:flags=lanczos" -loop 0 demo.gif
```

### 优化GIF大小

```bash
# 如果GIF超过5MB
brew install gifsicle
gifsicle -O3 --colors 128 --lossy=80 demo.gif -o demo_optimized.gif

# 使用优化后的
mv demo_optimized.gif demo.gif
```

## 添加到README

替换这段：
```markdown
**📹 Demo Video Coming Soon**
*One-click startup → Browse API docs → Send Instagram DM in 3 lines of code*
```

改为：
```markdown
<img src="demo.gif" alt="UniAPI Demo" width="700">
<p align="center"><i>✨ One interface, 5 platforms - that's it.</i></p>
```

## Commit和Push

```bash
git add demo.gif README.md demo_visual.py
git commit -m "feat: Add visual demo GIF"
# 你自己push
```

---

## 关键点

✅ **终端字体够大** - 18号
✅ **窗口大小合适** - 不要录整个屏幕
✅ **GIF文件<5MB** - GitHub显示流畅
✅ **循环播放** - 访客可以反复看

**总时间：5-10分钟搞定**
