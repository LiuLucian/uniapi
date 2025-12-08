#!/usr/bin/env python3
"""
自动保存Instagram Cookies
完全自动化 - 打开浏览器，等待登录，自动保存
"""

import asyncio
import json
import os
from playwright.async_api import async_playwright


async def auto_save_instagram_cookies():
    """自动保存Instagram cookies"""

    print("=" * 60)
    print("  Instagram Cookies 自动保存工具")
    print("=" * 60)
    print()
    print("🚀 启动浏览器...")

    async with async_playwright() as p:
        # 启动浏览器 (非无头模式)
        browser = await p.firefox.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 打开Instagram
        print("🌐 打开 Instagram...")
        await page.goto('https://www.instagram.com/', wait_until='domcontentloaded')

        print()
        print("=" * 60)
        print("  ⏳ 请在浏览器中登录你的 Instagram 账号")
        print("=" * 60)
        print()
        print("提示：")
        print("  1. 在打开的浏览器窗口中输入用户名和密码")
        print("  2. 完成任何验证步骤")
        print("  3. 等待进入 Instagram 首页")
        print()
        print("⏰ 等待 60 秒让你完成登录...")
        print("   (登录完成后脚本会自动继续)")
        print()

        # 等待60秒
        for i in range(60, 0, -10):
            print(f"   ⏳ 剩余 {i} 秒...")
            await asyncio.sleep(10)

        print()
        print("✅ 时间到！开始提取 cookies...")

        # 获取所有cookies
        cookies = await context.cookies()

        # 查找sessionid
        sessionid = None
        for cookie in cookies:
            if cookie['name'] == 'sessionid' and 'instagram.com' in cookie['domain']:
                sessionid = cookie['value']
                break

        if not sessionid:
            print()
            print("❌ 错误：未找到 sessionid cookie")
            print()
            print("可能的原因：")
            print("  1. 你还没有登录Instagram")
            print("  2. 登录还没有完成")
            print("  3. Instagram阻止了登录")
            print()
            print("💡 请重新运行脚本，并确保在60秒内完成登录")
            await browser.close()
            return False

        print(f"✅ 找到 sessionid: {sessionid[:20]}...")

        # 保存到platforms_auth.json
        auth_file = 'platforms_auth.json'

        if os.path.exists(auth_file):
            with open(auth_file, 'r') as f:
                auth_data = json.load(f)
        else:
            auth_data = {}

        # 更新Instagram配置
        auth_data['instagram'] = {
            'cookies': {
                'sessionid': sessionid
            }
        }

        # 保存
        with open(auth_file, 'w') as f:
            json.dump(auth_data, f, indent=2)

        print(f"✅ Cookies 已保存到: {auth_file}")

        # 同时保存到.env
        env_file = '.env'
        env_lines = []

        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                env_lines = f.readlines()

        # 删除旧的INSTAGRAM_SESSION_ID
        env_lines = [line for line in env_lines if not line.startswith('INSTAGRAM_SESSION_ID=')]

        # 添加新的
        env_lines.append(f'INSTAGRAM_SESSION_ID={sessionid}\n')

        with open(env_file, 'w') as f:
            f.writelines(env_lines)

        print(f"✅ Session ID 已保存到: {env_file}")
        print()
        print("=" * 60)
        print("  🎉 配置完成！")
        print("=" * 60)
        print()
        print("下一步：")
        print("  1. 重启 Instagram Bridge Server:")
        print("     kill $(lsof -ti:5002)")
        print("     cd platforms/instagram && python3 instagram_bridge_server.py > ../../instagram_bridge.log 2>&1 &")
        print()
        print("  2. 运行测试:")
        print("     python3 test_real_account.py")
        print()

        await browser.close()
        return True


if __name__ == '__main__':
    try:
        success = asyncio.run(auto_save_instagram_cookies())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
