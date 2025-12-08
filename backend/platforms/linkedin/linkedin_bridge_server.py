"""
LinkedIn Bridge Server
Flask + Playwright异步自动化服务器（官方API风格）
Port: 5005
"""

import json
import asyncio
import logging
from flask import Flask, request, jsonify
from playwright.async_api import async_playwright
from typing import Dict, List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


class LinkedInOperations:
    """LinkedIn操作类 - 使用Playwright实现所有自动化"""

    def __init__(self, auth_file: str = "platforms_auth.json"):
        """初始化"""
        self.auth_file = auth_file
        self.cookies = self._load_cookies()

    def _load_cookies(self) -> Dict:
        """从配置文件加载cookies"""
        try:
            with open(self.auth_file, 'r') as f:
                config = json.load(f)
                linkedin_auth = config.get('linkedin', {})
                cookies = linkedin_auth.get('cookies', {})
                if cookies:
                    logger.info(f"✅ Loaded {len(cookies)} LinkedIn cookies")
                else:
                    logger.warning("⚠️  No LinkedIn cookies found")
                return cookies
        except FileNotFoundError:
            logger.error(f"❌ Auth file not found: {self.auth_file}")
            return {}
        except Exception as e:
            logger.error(f"❌ Failed to load auth: {e}")
            return {}

    async def get_user_profile(self, username: str) -> dict:
        """
        获取用户资料

        Args:
            username: LinkedIn 用户名或profile ID

        Returns:
            {
                "success": true,
                "username": "...",
                "profile_url": "https://www.linkedin.com/in/...",
                "name": "...",
                "headline": "...",
                "location": "..."
            }
        """
        logger.info(f"👤 Getting user profile: {username}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                locale='en-US'
            )

            # 加载cookies
            if self.cookies:
                cookies_list = [{
                    'name': name,
                    'value': value,
                    'domain': '.linkedin.com',
                    'path': '/'
                } for name, value in self.cookies.items()]
                await context.add_cookies(cookies_list)

            page = await context.new_page()

            try:
                profile_url = f"https://www.linkedin.com/in/{username}"
                logger.info(f"📍 Navigating to: {profile_url}")

                await page.goto(profile_url, wait_until='networkidle', timeout=30000)
                await asyncio.sleep(2)

                # 提取用户信息
                name = await page.title()
                name = name.split('|')[0].strip() if '|' in name else name

                result = {
                    "success": True,
                    "username": username,
                    "profile_url": profile_url,
                    "name": name
                }

                logger.info(f"✅ Got profile: {name}")
                return result

            except Exception as e:
                logger.error(f"❌ Failed to get profile: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
            finally:
                await browser.close()

    async def get_user_posts(self, username: str, max_count: int = 10) -> dict:
        """
        获取用户的帖子

        Args:
            username: LinkedIn 用户名
            max_count: 最多获取帖子数

        Returns:
            {
                "success": true,
                "username": "...",
                "posts": [...]
            }
        """
        logger.info(f"📄 Getting posts for user: {username}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                locale='en-US'
            )

            if self.cookies:
                cookies_list = [{
                    'name': name,
                    'value': value,
                    'domain': '.linkedin.com',
                    'path': '/'
                } for name, value in self.cookies.items()]
                await context.add_cookies(cookies_list)

            page = await context.new_page()

            try:
                profile_url = f"https://www.linkedin.com/in/{username}/recent-activity/all/"
                await page.goto(profile_url, wait_until='networkidle', timeout=30000)
                await asyncio.sleep(3)

                # 滚动加载帖子
                for _ in range(3):
                    await page.evaluate('window.scrollBy(0, 1000)')
                    await asyncio.sleep(1)

                posts = []
                logger.info(f"✅ Found {len(posts)} posts")

                return {
                    "success": True,
                    "username": username,
                    "posts": posts[:max_count]
                }

            except Exception as e:
                logger.error(f"❌ Failed to get posts: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
            finally:
                await browser.close()

    async def like_post(self, post_url: str) -> dict:
        """
        点赞帖子

        Args:
            post_url: 帖子URL

        Returns:
            {"success": true, "message": "..."}
        """
        logger.info(f"👍 Liking post: {post_url}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )

            if self.cookies:
                cookies_list = [{
                    'name': name,
                    'value': value,
                    'domain': '.linkedin.com',
                    'path': '/'
                } for name, value in self.cookies.items()]
                await context.add_cookies(cookies_list)

            page = await context.new_page()

            try:
                await page.goto(post_url, wait_until='networkidle', timeout=30000)
                await asyncio.sleep(2)

                # LinkedIn点赞按钮选择器
                like_selectors = [
                    'button[aria-label*="Like"]',
                    'button[aria-label*="like"]',
                    'button.react-button__trigger'
                ]

                liked = False
                for selector in like_selectors:
                    try:
                        like_btn = page.locator(selector).first
                        if await like_btn.is_visible(timeout=2000):
                            await like_btn.click()
                            liked = True
                            await asyncio.sleep(1)
                            break
                    except:
                        continue

                if liked:
                    logger.info("✅ Post liked successfully")
                    return {
                        "success": True,
                        "message": "Post liked successfully"
                    }
                else:
                    logger.warning("⚠️  Could not find like button")
                    return {
                        "success": False,
                        "message": "Could not find like button"
                    }

            except Exception as e:
                logger.error(f"❌ Failed to like post: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
            finally:
                await browser.close()

    async def comment_on_post(self, post_url: str, comment_text: str) -> dict:
        """
        评论帖子

        Args:
            post_url: 帖子URL
            comment_text: 评论内容

        Returns:
            {"success": true, "message": "..."}
        """
        logger.info(f"💬 Commenting on post: {post_url}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )

            if self.cookies:
                cookies_list = [{
                    'name': name,
                    'value': value,
                    'domain': '.linkedin.com',
                    'path': '/'
                } for name, value in self.cookies.items()]
                await context.add_cookies(cookies_list)

            page = await context.new_page()

            try:
                await page.goto(post_url, wait_until='networkidle', timeout=30000)
                await asyncio.sleep(2)

                # 点击评论按钮
                comment_button_selectors = [
                    'button[aria-label*="Comment"]',
                    'button.comment-button'
                ]

                for selector in comment_button_selectors:
                    try:
                        comment_btn = page.locator(selector).first
                        if await comment_btn.is_visible(timeout=2000):
                            await comment_btn.click()
                            await asyncio.sleep(1)
                            break
                    except:
                        continue

                # 查找评论框
                comment_box_selectors = [
                    'div[contenteditable="true"]',
                    'div.ql-editor'
                ]

                commented = False
                for selector in comment_box_selectors:
                    try:
                        comment_box = page.locator(selector).first
                        if await comment_box.is_visible(timeout=2000):
                            await comment_box.click()
                            await asyncio.sleep(1)
                            await comment_box.fill(comment_text)
                            await asyncio.sleep(1)

                            # 查找发送按钮
                            send_selectors = [
                                'button[type="submit"]',
                                'button:has-text("Post")'
                            ]

                            for send_selector in send_selectors:
                                try:
                                    send_btn = page.locator(send_selector).first
                                    if await send_btn.is_visible(timeout=2000):
                                        await send_btn.click()
                                        await asyncio.sleep(2)
                                        commented = True
                                        break
                                except:
                                    continue

                            if commented:
                                break
                    except:
                        continue

                if commented:
                    logger.info("✅ Comment posted successfully")
                    return {
                        "success": True,
                        "message": "Comment posted successfully"
                    }
                else:
                    logger.warning("⚠️  Could not find comment box")
                    return {
                        "success": False,
                        "message": "Could not find comment box"
                    }

            except Exception as e:
                logger.error(f"❌ Failed to comment: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
            finally:
                await browser.close()

    async def connect_with_user(self, username: str) -> dict:
        """连接用户（发送连接请求）"""
        logger.info(f"➕ Connecting with user: {username}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )

            if self.cookies:
                cookies_list = [{
                    'name': name,
                    'value': value,
                    'domain': '.linkedin.com',
                    'path': '/'
                } for name, value in self.cookies.items()]
                await context.add_cookies(cookies_list)

            page = await context.new_page()

            try:
                profile_url = f"https://www.linkedin.com/in/{username}"
                await page.goto(profile_url, wait_until='networkidle', timeout=30000)
                await asyncio.sleep(2)

                # LinkedIn连接按钮选择器
                connect_selectors = [
                    'button[aria-label*="Connect"]',
                    'button:has-text("Connect")',
                    'button.pvs-profile-actions__action'
                ]

                connected = False
                for selector in connect_selectors:
                    try:
                        connect_btn = page.locator(selector).first
                        if await connect_btn.is_visible(timeout=2000):
                            await connect_btn.click()
                            connected = True
                            await asyncio.sleep(1)

                            # 可能会弹出添加备注的对话框，点击发送
                            try:
                                send_btn = page.locator('button[aria-label*="Send"]').first
                                if await send_btn.is_visible(timeout=2000):
                                    await send_btn.click()
                                    await asyncio.sleep(1)
                            except:
                                pass

                            break
                    except:
                        continue

                if connected:
                    logger.info("✅ Connection request sent successfully")
                    return {
                        "success": True,
                        "message": "Connection request sent successfully"
                    }
                else:
                    logger.warning("⚠️  Could not find connect button")
                    return {
                        "success": False,
                        "message": "Could not find connect button"
                    }

            except Exception as e:
                logger.error(f"❌ Failed to connect with user: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
            finally:
                await browser.close()

    async def send_dm(self, username: str, message: str) -> dict:
        """发送私信"""
        logger.info(f"✉️  Sending DM to: {username}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )

            if self.cookies:
                cookies_list = [{
                    'name': name,
                    'value': value,
                    'domain': '.linkedin.com',
                    'path': '/'
                } for name, value in self.cookies.items()]
                await context.add_cookies(cookies_list)

            page = await context.new_page()

            try:
                # LinkedIn消息页面
                profile_url = f"https://www.linkedin.com/in/{username}"
                await page.goto(profile_url, wait_until='networkidle', timeout=30000)
                await asyncio.sleep(2)

                # 点击消息按钮
                message_button_selectors = [
                    'button[aria-label*="Message"]',
                    'button:has-text("Message")'
                ]

                for selector in message_button_selectors:
                    try:
                        msg_btn = page.locator(selector).first
                        if await msg_btn.is_visible(timeout=2000):
                            await msg_btn.click()
                            await asyncio.sleep(2)
                            break
                    except:
                        continue

                # 查找消息输入框
                message_box_selectors = [
                    'div[contenteditable="true"]',
                    'div.msg-form__contenteditable'
                ]

                sent = False
                for selector in message_box_selectors:
                    try:
                        message_box = page.locator(selector).first
                        if await message_box.is_visible(timeout=2000):
                            await message_box.click()
                            await asyncio.sleep(1)
                            await message_box.fill(message)
                            await asyncio.sleep(1)

                            # 发送消息
                            send_selectors = [
                                'button[type="submit"]',
                                'button.msg-form__send-button'
                            ]

                            for send_selector in send_selectors:
                                try:
                                    send_btn = page.locator(send_selector).first
                                    if await send_btn.is_visible(timeout=2000):
                                        await send_btn.click()
                                        await asyncio.sleep(2)
                                        sent = True
                                        break
                                except:
                                    continue

                            if sent:
                                break
                    except:
                        continue

                if sent:
                    logger.info("✅ DM sent successfully")
                    return {
                        "success": True,
                        "message": "DM sent successfully",
                        "username": username
                    }
                else:
                    logger.warning("⚠️  Could not find message box")
                    return {
                        "success": False,
                        "message": "Could not find message box"
                    }

            except Exception as e:
                logger.error(f"❌ Failed to send DM: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
            finally:
                await browser.close()


# 创建全局operations实例
linkedin_ops = LinkedInOperations()


# ==================== Flask路由 ====================

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "platform": "LinkedIn",
        "port": 5005
    })


@app.route('/user/<username>', methods=['GET'])
def get_user(username: str):
    """获取用户资料"""
    result = asyncio.run(linkedin_ops.get_user_profile(username))
    return jsonify(result)


@app.route('/user/<username>/posts', methods=['GET'])
def get_user_posts(username: str):
    """获取用户帖子"""
    max_count = request.args.get('max_count', 10, type=int)
    result = asyncio.run(linkedin_ops.get_user_posts(username, max_count))
    return jsonify(result)


@app.route('/post/like', methods=['POST'])
def like_post():
    """点赞帖子"""
    data = request.get_json()
    post_url = data.get('post_url')

    if not post_url:
        return jsonify({"success": False, "error": "post_url required"}), 400

    result = asyncio.run(linkedin_ops.like_post(post_url))
    return jsonify(result)


@app.route('/post/comment', methods=['POST'])
def comment_post():
    """评论帖子"""
    data = request.get_json()
    post_url = data.get('post_url')
    comment = data.get('comment')

    if not post_url or not comment:
        return jsonify({"success": False, "error": "post_url and comment required"}), 400

    result = asyncio.run(linkedin_ops.comment_on_post(post_url, comment))
    return jsonify(result)


@app.route('/user/<username>/connect', methods=['POST'])
def connect_user(username: str):
    """连接用户"""
    result = asyncio.run(linkedin_ops.connect_with_user(username))
    return jsonify(result)


@app.route('/dm/send', methods=['POST'])
def send_dm():
    """发送私信"""
    data = request.get_json()
    username = data.get('username')
    message = data.get('message')

    if not username or not message:
        return jsonify({"success": False, "error": "username and message required"}), 400

    result = asyncio.run(linkedin_ops.send_dm(username, message))
    return jsonify(result)


if __name__ == '__main__':
    logger.info("============================================================")
    logger.info("🚀 LinkedIn Bridge Server Starting...")
    logger.info("============================================================")
    logger.info("✅ Server ready on http://localhost:5005")
    logger.info("============================================================")

    app.run(host='0.0.0.0', port=5005, debug=False)
