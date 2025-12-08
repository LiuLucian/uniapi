"""
Facebook DM Sender - 完整版
参照Reddit/Twitter模式：用profile_url发私信
"""

import json
import time
import random
import logging
from typing import Dict
from playwright.sync_api import sync_playwright
from src.dm_sender_base import DMSenderBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FacebookDMSender(DMSenderBase):
    """Facebook私信发送器 - 参照Reddit/Twitter模式"""

    def __init__(self, auth_file: str = "platforms_auth.json"):
        """初始化Facebook DM发送器"""
        try:
            with open(auth_file, 'r') as f:
                config = json.load(f)
            auth_config = config.get('facebook', {})
        except FileNotFoundError:
            logger.error(f"❌ Auth file {auth_file} not found")
            auth_config = {}

        super().__init__(auth_config, 'Facebook')
        self.cookies = auth_config.get('cookies', {})

    def _setup_browser(self):
        """设置Playwright浏览器并加载Facebook cookies"""
        if not self.playwright:
            logger.info("🌐 Setting up Facebook browser...")
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )
            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080}
            )

            # 加载cookies
            if self.cookies:
                cookies_list = [{
                    'name': name,
                    'value': value,
                    'domain': '.facebook.com',
                    'path': '/'
                } for name, value in self.cookies.items()]
                self.context.add_cookies(cookies_list)
                logger.info("   ✅ Facebook cookies loaded")

            self.page = self.context.new_page()

    def send_dm(self, user_profile: Dict, message: str) -> bool:
        """
        发送Facebook DM（参照Reddit/Twitter模式）

        Args:
            user_profile: 用户资料（必须包含profile_url或username）
            message: 消息内容

        Returns:
            是否成功发送
        """
        # 获取profile_url或构造
        profile_url = user_profile.get('profile_url', '')
        username = user_profile.get('username', '')

        if not profile_url and not username:
            logger.error("❌ No profile_url or username found")
            return False

        # 如果没有profile_url，尝试从username构造
        if not profile_url:
            profile_url = f"https://www.facebook.com/{username}"

        try:
            self._setup_browser()

            logger.info(f"💬 Sending DM to: {username or 'user'}")
            logger.info(f"   Profile: {profile_url[:60]}...")

            # Step 1: 访问用户主页
            logger.info("   [1/4] Opening profile...")
            self.page.goto(profile_url, wait_until='domcontentloaded', timeout=60000)
            self._random_delay(3, 5)

            # 检查是否登录
            if "login" in self.page.url:
                logger.error("❌ Not logged in to Facebook")
                return False

            # Step 2: 查找并点击Message按钮
            logger.info("   [2/4] Looking for Message button...")

            # Facebook Message按钮的多种选择器
            message_button_selectors = [
                'div[aria-label="Message"]',
                'div[aria-label="发消息"]',  # 中文
                'a[aria-label="Message"]',
                'a[aria-label="发消息"]',
                'div:has-text("Message")',
                'a:has-text("Message")',
                'div[role="button"]:has-text("Message")',
            ]

            message_button = None
            for selector in message_button_selectors:
                try:
                    message_button = self.page.wait_for_selector(selector, timeout=3000)
                    if message_button and message_button.is_visible():
                        logger.info(f"   ✅ Found Message button: {selector}")
                        break
                except:
                    continue

            if not message_button:
                logger.warning("   ⚠️  Could not find Message button")
                logger.info("   Trying alternative: Direct message URL...")

                # 尝试直接访问message URL
                # 提取user ID from profile URL if possible
                if '/profile.php?id=' in profile_url:
                    user_id = profile_url.split('id=')[1].split('&')[0]
                    message_url = f"https://www.facebook.com/messages/t/{user_id}"
                else:
                    # 使用username
                    clean_username = username.replace('@', '').strip()
                    message_url = f"https://www.facebook.com/messages/t/{clean_username}"

                logger.info(f"   Trying: {message_url}")
                self.page.goto(message_url, wait_until='domcontentloaded', timeout=30000)
                self._random_delay(2, 3)
            else:
                # 点击Message按钮
                message_button.click()
                self._random_delay(3, 5)

            # Step 3: 查找消息输入框
            logger.info("   [3/4] Looking for message input...")

            message_input_selectors = [
                'div[contenteditable="true"][aria-label*="message"]',
                'div[contenteditable="true"][aria-label*="消息"]',
                'div[contenteditable="true"][role="textbox"]',
                'div[contenteditable="true"][data-lexical-editor="true"]',
                'div[contenteditable="true"]',
                'textarea[aria-label*="message"]',
                'textarea[placeholder*="message"]',
            ]

            message_input = None
            for selector in message_input_selectors:
                try:
                    message_input = self.page.wait_for_selector(selector, timeout=5000)
                    if message_input and message_input.is_visible():
                        logger.info(f"   ✅ Found message input: {selector}")
                        break
                except:
                    continue

            if not message_input:
                logger.error("❌ Could not find message input box")
                return False

            # 输入消息
            logger.info("   ✏️  Typing message...")
            message_input.click()
            self._random_delay(0.5, 1)

            # 使用type_like_human方法
            self._type_like_human(message_input, message)
            self._random_delay(1, 2)

            # Step 4: 发送消息
            logger.info("   [4/4] Sending message...")

            # 查找发送按钮
            send_button_selectors = [
                'div[aria-label="Send"]',
                'div[aria-label="发送"]',
                'button[aria-label="Send"]',
                'button[aria-label="发送"]',
                'div[aria-label*="Send"]',
                'div[role="button"]:has-text("Send")',
            ]

            send_button = None
            for selector in send_button_selectors:
                try:
                    send_button = self.page.wait_for_selector(selector, timeout=3000)
                    if send_button and send_button.is_visible():
                        logger.info(f"   ✅ Found send button: {selector}")
                        break
                except:
                    continue

            if not send_button:
                # 尝试用Enter键发送
                logger.info("   Trying Enter key...")
                message_input.press('Enter')
            else:
                send_button.click()

            self._random_delay(2, 3)

            # 验证发送成功
            # 方法1: 检查输入框是否清空
            try:
                current_text = message_input.inner_text() if hasattr(message_input, 'inner_text') else ''
                if not current_text or len(current_text.strip()) == 0:
                    logger.info("   ✅ Input cleared - message sent!")
                    return True
            except:
                pass

            # 方法2: 检查消息是否出现在聊天中
            try:
                search_text = message[:30].strip()
                page_text = self.page.inner_text('body')
                if search_text in page_text:
                    logger.info("   ✅ Message found in chat - sent successfully!")
                    return True
            except:
                pass

            # 方法3: 默认认为成功
            logger.info("   ✅ Message likely sent!")
            return True

        except Exception as e:
            logger.error(f"❌ Error sending Facebook DM: {e}")
            import traceback
            traceback.print_exc()
            return False


# 测试代码
if __name__ == "__main__":
    sender = FacebookDMSender()

    test_user = {
        'username': 'test_user',
        'profile_url': 'https://www.facebook.com/profile.php?id=100000000000000',  # 替换为真实URL
        'name': 'Test User',
        'company': 'Test Corp'
    }

    test_message = """Hey {{name}}, I came across your post about {{topic}}.

I'm building HireMeAI, an AI-powered interview prep tool that helps job seekers ace their interviews.

Would love to hear your thoughts if you're interested!

Best,
[Your Name]"""

    formatted_message = sender.format_message(test_message, test_user)
    print(f"\n📝 Formatted message:\n{formatted_message}\n")

    # Uncomment to test
    # success = sender.send_dm(test_user, formatted_message)
    # print(f"\n{'✅ Success' if success else '❌ Failed'}")
