#!/usr/bin/env python3
"""
Instagram 登录并保存认证信息
Instagram Login and Save Authentication

使用方法 / Usage:
    python3 instagram_login_and_save_auth.py

功能 / Features:
1. 打开浏览器，显示 Instagram 登录页面
2. 你手动登录你的 Instagram 账号
3. 登录成功后，自动提取 sessionid cookie
4. 保存到 platforms_auth.json
5. 验证认证是否有效
"""

import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright

# 配置文件路径
AUTH_FILE = Path(__file__).parent / "platforms_auth.json"

async def login_and_save_instagram_auth():
    """登录 Instagram 并保存认证信息"""

    print("=" * 60)
    print("Instagram 认证设置 / Instagram Authentication Setup")
    print("=" * 60)
    print()

    async with async_playwright() as p:
        # 启动浏览器（非无头模式，方便用户登录）
        print("🌐 启动浏览器... / Launching browser...")
        browser = await p.chromium.launch(
            headless=False,  # 显示浏览器窗口
            args=['--start-maximized']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )

        page = await context.new_page()

        # 访问 Instagram
        print("📱 正在打开 Instagram... / Opening Instagram...")
        await page.goto('https://www.instagram.com/', wait_until='networkidle')

        print()
        print("=" * 60)
        print("⚠️  请在浏览器中登录你的 Instagram 账号")
        print("   Please login to your Instagram account in the browser")
        print("=" * 60)
        print()
        print("登录步骤 / Login Steps:")
        print("1. 在打开的浏览器窗口中输入用户名和密码")
        print("   Enter your username and password in the browser")
        print("2. 完成任何验证步骤（如果有）")
        print("   Complete any verification steps (if any)")
        print("3. 等待进入 Instagram 首页")
        print("   Wait until you see Instagram homepage")
        print("4. 登录成功后，回到此终端按 Enter 键")
        print("   After successful login, come back here and press Enter")
        print()

        # 等待用户登录
        input("👉 登录完成后按 Enter 键继续... / Press Enter after login...")

        # 等待页面稳定
        await asyncio.sleep(2)

        # 获取当前 URL，检查是否登录成功
        current_url = page.url
        print(f"\n📍 当前页面 / Current page: {current_url}")

        if 'login' in current_url.lower() or 'accounts/login' in current_url.lower():
            print("\n❌ 错误：似乎还没有登录成功")
            print("   Error: It seems you haven't logged in successfully")
            print("   请重新运行脚本并确保完成登录")
            await browser.close()
            return False

        # 提取所有 cookies
        print("\n🔑 正在提取认证信息... / Extracting authentication...")
        cookies = await context.cookies()

        # 查找 sessionid cookie
        sessionid = None
        for cookie in cookies:
            if cookie['name'] == 'sessionid':
                sessionid = cookie['value']
                break

        if not sessionid:
            print("\n❌ 错误：未找到 sessionid cookie")
            print("   Error: sessionid cookie not found")
            print("   请确保已完全登录 Instagram")
            await browser.close()
            return False

        print(f"✅ 成功提取 sessionid: {sessionid[:20]}...")

        # 读取现有的 auth 配置（如果存在）
        auth_data = {}
        if AUTH_FILE.exists():
            try:
                with open(AUTH_FILE, 'r', encoding='utf-8') as f:
                    auth_data = json.load(f)
                print(f"📖 读取现有配置文件 / Read existing config file")
            except:
                pass

        # 更新 Instagram 认证信息
        auth_data['instagram'] = {
            'sessionid': sessionid
        }

        # 保留使用说明（如果存在）
        if '_instructions' not in auth_data:
            auth_data['_instructions'] = {
                "how_to_get_instagram_sessionid": [
                    "运行此脚本: python3 instagram_login_and_save_auth.py",
                    "或手动操作:",
                    "1. Open Instagram in your web browser (https://www.instagram.com)",
                    "2. Login to your Instagram account",
                    "3. Open Browser Developer Tools (F12 or Right-click → Inspect)",
                    "4. Go to Application tab → Cookies → https://www.instagram.com",
                    "5. Find the cookie named 'sessionid'",
                    "6. Copy the cookie value",
                    "7. Paste it in the 'sessionid' field above",
                    "8. Save this file",
                    "9. Restart UniAPI servers: ./stop.sh && ./start.sh"
                ]
            }

        # 保存到文件
        with open(AUTH_FILE, 'w', encoding='utf-8') as f:
            json.dump(auth_data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 认证信息已保存到: {AUTH_FILE}")
        print(f"   Authentication saved to: {AUTH_FILE}")

        # 验证认证是否有效
        print("\n🧪 验证认证... / Verifying authentication...")

        # 访问个人主页，看是否能访问
        await page.goto('https://www.instagram.com/accounts/edit/', wait_until='domcontentloaded')
        await asyncio.sleep(3)

        current_url = page.url
        if 'accounts/edit' in current_url:
            print("✅ 认证验证成功！/ Authentication verified!")

            # 尝试获取用户名
            try:
                username_input = await page.query_selector('input[name="username"]')
                if username_input:
                    username = await username_input.get_attribute('value')
                    if username:
                        print(f"👤 登录账号 / Logged in as: @{username}")

                        # 也保存用户名到配置中
                        auth_data['instagram']['username'] = username
                        with open(AUTH_FILE, 'w', encoding='utf-8') as f:
                            json.dump(auth_data, f, indent=2, ensure_ascii=False)
            except:
                pass
        else:
            print("⚠️  无法验证认证，但 sessionid 已保存")
            print("   Cannot verify auth, but sessionid is saved")

        await browser.close()

        print("\n" + "=" * 60)
        print("✅ 设置完成！/ Setup Complete!")
        print("=" * 60)
        print()
        print("下一步 / Next Steps:")
        print("1. 重启 UniAPI 服务器 / Restart UniAPI servers:")
        print("   cd /Users/l.u.c/my-app/uniapi")
        print("   ./stop.sh && ./start.sh")
        print()
        print("2. 运行测试脚本 / Run test script:")
        print("   python3 test_instagram_api.py")
        print()

        return True

if __name__ == "__main__":
    try:
        result = asyncio.run(login_and_save_instagram_auth())
        if result:
            print("🎉 Instagram 认证设置成功！")
        else:
            print("❌ Instagram 认证设置失败，请重试")
    except KeyboardInterrupt:
        print("\n\n⚠️  用户取消操作")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
