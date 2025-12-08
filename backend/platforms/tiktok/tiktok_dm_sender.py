"""
TikTok DM Sender - TikTok私信发送器
"""

import json
import logging
from typing import Dict
from playwright.sync_api import sync_playwright
from src.dm_sender_base import DMSenderBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TikTokDMSender(DMSenderBase):
    """TikTok私信发送器"""

    def __init__(self, auth_file: str = "platforms_auth.json"):
        """初始化TikTok DM发送器"""
        try:
            with open(auth_file, 'r') as f:
                config = json.load(f)
            auth_config = config.get('tiktok', {})
        except FileNotFoundError:
            logger.error(f"❌ Auth file {auth_file} not found")
            auth_config = {}

        super().__init__(auth_config, 'TikTok')
        self.sessionid = auth_config.get('sessionid', '')
        self.msToken = auth_config.get('msToken', '')

    def _setup_browser(self):
        """设置Playwright浏览器并加载TikTok cookies"""
        if not self.playwright:
            logger.info("🌐 Setting up TikTok browser...")
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )
            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                viewport={'width': 1280, 'height': 720}
            )

            # 加载cookies
            cookies = []
            if self.sessionid:
                cookies.append({
                    'name': 'sessionid',
                    'value': self.sessionid,
                    'domain': '.tiktok.com',
                    'path': '/'
                })
            if self.msToken:
                cookies.append({
                    'name': 'msToken',
                    'value': self.msToken,
                    'domain': '.tiktok.com',
                    'path': '/'
                })

            if cookies:
                self.context.add_cookies(cookies)
                logger.info("   ✅ TikTok cookies loaded")

            self.page = self.context.new_page()

    def send_dm(self, user_profile: Dict, message: str) -> bool:
        """
        发送TikTok DM

        Args:
            user_profile: 用户资料（必须包含username）
            message: 消息内容

        Returns:
            是否成功发送
        """
        username = user_profile.get('username', user_profile.get('unique_id'))
        if not username:
            logger.error("❌ No TikTok username found")
            return False

        # 移除@符号
        username = username.lstrip('@')

        try:
            self._setup_browser()

            logger.info(f"💬 Sending DM to @{username}...")

            # 访问用户主页
            profile_url = f"https://www.tiktok.com/@{username}"
            self.page.goto(profile_url, wait_until='domcontentloaded', timeout=30000)
            self._random_delay(3, 5)

            # 检查是否登录
            if 'login' in self.page.url:
                logger.error("❌ Not logged in to TikTok")
                return False

            # TikTok的Message功能可能在不同位置
            # 查找Message按钮（支持中英文）
            message_button_selectors = [
                'button:has-text("消息")',  # 中文
                'button:has-text("Message")',  # 英文
                'button[data-e2e="message-button"]',
                'div[data-e2e="message-button"]',
                'span:has-text("消息")',  # 中文文本
                'span:has-text("Message")',  # 英文文本
            ]

            message_button = None
            for selector in message_button_selectors:
                try:
                    message_button = self.page.wait_for_selector(selector, timeout=3000)
                    if message_button:
                        logger.info(f"   ✅ Found message button: {selector}")
                        break
                except:
                    continue

            if not message_button:
                logger.warning("   ⚠️  Could not find Message button on TikTok")
                logger.info("   ℹ️  TikTok may require following the user first, or DMs may not be enabled")
                return False

            # 点击Message按钮
            message_button.click()
            self._random_delay(2, 3)

            # 等待消息输入框
            message_box_selectors = [
                'div[contenteditable="true"][data-e2e="message-input"]',
                'textarea[placeholder*="Message"]',
                'div[contenteditable="true"]',
            ]

            message_box = None
            for selector in message_box_selectors:
                try:
                    message_box = self.page.wait_for_selector(selector, timeout=5000)
                    if message_box:
                        logger.info(f"   ✅ Found message box: {selector}")
                        break
                except:
                    continue

            if not message_box:
                logger.error("❌ Could not find message input box")
                return False

            # 输入消息
            logger.info("   ✏️  Typing message...")
            self._type_like_human(message_box, message)
            self._random_delay(1, 2)

            # 发送消息
            send_button_selectors = [
                'button[data-e2e="message-send-button"]',
                'button[type="submit"]',
                'button:has-text("Send")',
                'div[data-e2e="send-button"]',
            ]

            send_button = None
            for selector in send_button_selectors:
                try:
                    send_button = self.page.wait_for_selector(selector, timeout=3000)
                    if send_button:
                        logger.info(f"   ✅ Found send button: {selector}")
                        break
                except:
                    continue

            if not send_button:
                logger.error("❌ Could not find send button")
                return False

            send_button.click()
            logger.info("   ✅ Message sent!")
            self._random_delay(2, 3)

            return True

        except Exception as e:
            logger.error(f"❌ Error sending TikTok DM: {e}")
            import traceback
            traceback.print_exc()
            return False


# 测试代码
if __name__ == "__main__":
    sender = TikTokDMSender()

    test_user = {
        'username': 'test_user',
        'name': 'Test User'
    }

    test_message = """Hey {{name}}, I came across your content — really liked it!

I'm building something called HireMeAI, it helps teams prep for interviews with AI feedback and auto-review tools.

If you're open to it, I'd love to get your quick thoughts — always great hearing from people actually running interviews."""

    formatted_message = sender.format_message(test_message, test_user)
    print(f"\n📝 Formatted message:\n{formatted_message}\n")
