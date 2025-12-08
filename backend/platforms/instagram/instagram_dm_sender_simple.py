"""
Instagram DM Sender - 简化版
直接使用 /direct/new/ 搜索用户并发送
"""

import json
import logging
import time
import random
from typing import Dict
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InstagramDMSenderSimple:
    """Instagram私信发送器 - 简化版本"""

    def __init__(self, auth_file: str = "platforms_auth.json"):
        """初始化"""
        try:
            with open(auth_file, 'r') as f:
                config = json.load(f)
            self.sessionid = config.get('instagram', {}).get('sessionid', '')
        except FileNotFoundError:
            logger.error(f"❌ Auth file {auth_file} not found")
            self.sessionid = ''

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def _setup_browser(self):
        """设置浏览器"""
        if not self.playwright:
            logger.info("🌐 Setting up Instagram browser...")
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=False, slow_mo=500)
            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )

            if self.sessionid:
                self.context.add_cookies([{
                    'name': 'sessionid',
                    'value': self.sessionid,
                    'domain': '.instagram.com',
                    'path': '/'
                }])
                logger.info("   ✅ Instagram cookies loaded")

            self.page = self.context.new_page()

    def send_dm(self, username: str, message: str) -> bool:
        """
        发送Instagram DM

        Args:
            username: Instagram用户名（不带@）
            message: 消息内容

        Returns:
            是否成功发送
        """
        username = username.lstrip('@')

        try:
            self._setup_browser()

            logger.info(f"💬 Sending DM to @{username}...")

            # 步骤1: 直接访问新建消息页面
            logger.info("📱 Step 1: Going to DM interface...")
            self.page.goto('https://www.instagram.com/direct/new/', timeout=30000)
            time.sleep(3)

            # 关闭弹窗
            try:
                dismiss = self.page.wait_for_selector('button:has-text("Not Now"), button:has-text("以后再说")', timeout=2000)
                if dismiss:
                    dismiss.click()
                    time.sleep(1)
            except:
                pass

            # 步骤2: 搜索用户
            logger.info(f"🔍 Step 2: Searching for @{username}...")

            search_input = self.page.wait_for_selector('input[placeholder*="Search"], input[placeholder*="搜索"]', timeout=5000)
            if not search_input:
                logger.error("❌ Search input not found")
                return False

            # 使用fill输入
            search_input.fill(username)
            logger.info(f"   ✅ Filled: {username}")
            time.sleep(2)

            # 步骤3: 点击第一个搜索结果
            logger.info("👤 Step 3: Clicking first result...")

            results = self.page.query_selector_all('div[role="button"]')
            if results and len(results) > 0:
                logger.info(f"   ✅ Found {len(results)} results")
                # 点击第一个结果（通常是用户）
                self.page.evaluate('(el) => el.click()', results[0])
                time.sleep(2)

                # 检查是否弹出Chat按钮
                logger.info("💬 Step 4: Looking for Chat button...")

                try:
                    chat_btn = self.page.wait_for_selector('button:has-text("Chat"), button:has-text("聊天"), div[role="button"]:has-text("Chat")', timeout=3000)
                    if chat_btn:
                        logger.info("   ✅ Found Chat button, clicking...")
                        self.page.evaluate('(el) => el.click()', chat_btn)
                        time.sleep(3)
                        logger.info(f"   URL after chat: {self.page.url}")
                    else:
                        logger.info("   ℹ️  No Chat button found")
                except:
                    logger.info("   ℹ️  No Chat button (already in DM or no permission)")

                # 检查URL是否变化
                current_url = self.page.url
                logger.info(f"   Current URL: {current_url}")

                if '/direct/t/' in current_url:
                    logger.info("   ✅ Successfully opened DM thread")
                elif '/direct/new' in current_url:
                    logger.warning("   ⚠️  Still on /direct/new/ - user might not be messageable")
                    # 尝试点击"Next"或"下一步"按钮
                    try:
                        next_btn = self.page.wait_for_selector('button:has-text("Next"), button:has-text("下一步")', timeout=2000)
                        if next_btn:
                            logger.info("   Clicking Next button...")
                            self.page.evaluate('(el) => el.click()', next_btn)
                            time.sleep(2)
                    except:
                        pass
            else:
                logger.error("❌ No search results found")
                return False

            # 步骤5: 找到消息输入框
            logger.info("✏️  Step 5: Typing message...")

            input_selectors = [
                'div[contenteditable="true"][role="textbox"]',
                'div[contenteditable="true"]',
                'textarea[placeholder*="Message"]',
            ]

            message_input = None
            for selector in input_selectors:
                try:
                    message_input = self.page.wait_for_selector(selector, timeout=5000)
                    if message_input and message_input.is_visible():
                        logger.info(f"   ✅ Found input: {selector}")
                        break
                except:
                    continue

            if not message_input:
                logger.error("❌ Message input not found")
                # Debug
                logger.info(f"   Current URL: {self.page.url}")
                all_inputs = self.page.query_selector_all('textarea, input[type="text"], div[contenteditable="true"]')
                logger.info(f"   Found {len(all_inputs)} potential inputs")
                return False

            # 输入消息
            message_input.fill(message)
            logger.info(f"   ✅ Typed message")
            time.sleep(1)

            # 步骤6: 发送
            logger.info("📤 Step 6: Sending...")

            send_btn = self.page.wait_for_selector('button:has-text("Send"), button:has-text("发送")', timeout=3000)
            if send_btn and not send_btn.is_disabled():
                self.page.evaluate('(el) => el.click()', send_btn)
                logger.info("   ✅ Clicked Send button")
                time.sleep(2)

                logger.info("✅ Message sent successfully!")
                return True
            else:
                logger.error("❌ Send button not found or disabled")
                return False

        except Exception as e:
            logger.error(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def cleanup(self):
        """清理资源"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()


# 测试代码
if __name__ == "__main__":
    sender = InstagramDMSenderSimple()

    test_username = "uciantrepreneur"  # 从AI分析结果中获取的用户
    test_message = """Hey, I saw your comment about entrepreneurship — really insightful!

I'm building HireMeAI (https://interviewasssistant.com), an AI-powered interview prep platform.

Would love to get your thoughts if you're open to it!"""

    print("\n🧪 Testing Instagram DM...")
    print(f"Target: @{test_username}")
    print()

    success = sender.send_dm(test_username, test_message)

    if success:
        print("\n✅ TEST PASSED")
    else:
        print("\n❌ TEST FAILED")

    sender.cleanup()
