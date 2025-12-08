"""
LinkedIn DM Sender - LinkedIn私信发送器
"""

import json
import logging
import time
from typing import Dict, Optional
from playwright.sync_api import sync_playwright
from src.dm_sender_base import DMSenderBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LinkedInDMSender(DMSenderBase):
    """LinkedIn私信发送器"""

    def __init__(self, auth_file: str = "linkedin_auth.json"):
        """
        初始化LinkedIn DM发送器

        Args:
            auth_file: LinkedIn认证文件路径
        """
        try:
            with open(auth_file, 'r') as f:
                auth_config = json.load(f)
        except FileNotFoundError:
            logger.error(f"❌ LinkedIn auth file {auth_file} not found")
            auth_config = {}

        super().__init__(auth_config, 'LinkedIn')
        self.cookies = auth_config.get('cookies', [])

    def _setup_browser(self):
        """设置Playwright浏览器并加载LinkedIn cookies"""
        if not self.playwright:
            logger.info("🌐 Setting up LinkedIn browser...")
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=False,  # 显示浏览器以便调试
                args=['--disable-blink-features=AutomationControlled']
            )
            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1280, 'height': 720}
            )

            # 加载cookies
            if self.cookies:
                self.context.add_cookies(self.cookies)
                logger.info("   ✅ LinkedIn cookies loaded")
            else:
                logger.warning("   ⚠️  No LinkedIn cookies found, may need to login")

            self.page = self.context.new_page()

    def send_dm(self, user_profile: Dict, message: str) -> bool:
        """
        发送LinkedIn私信

        Args:
            user_profile: 用户资料（必须包含profile_url）
            message: 消息内容

        Returns:
            是否成功发送
        """
        profile_url = user_profile.get('profile_url', user_profile.get('linkedin_url'))
        if not profile_url:
            logger.error("❌ No LinkedIn profile URL found")
            return False

        try:
            self._setup_browser()

            logger.info(f"💬 Sending DM to {user_profile.get('name', 'user')}...")
            logger.info(f"   Profile: {profile_url}")

            # 访问个人主页
            self.page.goto(profile_url, wait_until='domcontentloaded', timeout=30000)
            self._random_delay(2, 4)

            # 检查是否需要登录
            if 'authwall' in self.page.url or 'login' in self.page.url:
                logger.error("❌ Not logged in to LinkedIn")
                return False

            # 方法1: 尝试点击"Message"按钮
            message_button_selectors = [
                'button:has-text("Message")',
                'button[aria-label*="Message"]',
                'a:has-text("Message")',
                '.artdeco-button:has-text("Message")',
                'button.message-anywhere-button',
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
                logger.warning("   ⚠️  No 'Message' button found, trying 'Connect' instead")
                # 如果没有Message按钮，尝试发送连接请求
                return self._send_connection_request(user_profile, message)

            # 点击Message按钮
            message_button.click()
            self._random_delay(1, 2)

            # 等待消息输入框
            message_box_selectors = [
                'div[contenteditable="true"]',
                'div.msg-form__contenteditable',
                'div.msg-form__msg-content-container',
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
                'button[type="submit"]',
                'button.msg-form__send-button',
                'button:has-text("Send")',
            ]

            send_button = None
            for selector in send_button_selectors:
                try:
                    send_button = self.page.query_selector(selector)
                    if send_button and send_button.is_enabled():
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
            logger.error(f"❌ Error sending LinkedIn DM: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _send_connection_request(self, user_profile: Dict, message: str) -> bool:
        """
        发送LinkedIn连接请求（带消息）

        Args:
            user_profile: 用户资料
            message: 消息内容

        Returns:
            是否成功发送
        """
        try:
            logger.info("   📤 Sending connection request with note...")

            # 查找Connect按钮
            connect_button_selectors = [
                'button:has-text("Connect")',
                'button[aria-label*="Connect"]',
                '.artdeco-button:has-text("Connect")',
            ]

            connect_button = None
            for selector in connect_button_selectors:
                try:
                    connect_button = self.page.wait_for_selector(selector, timeout=3000)
                    if connect_button:
                        logger.info(f"   ✅ Found connect button: {selector}")
                        break
                except:
                    continue

            if not connect_button:
                logger.error("❌ Could not find Connect button")
                return False

            connect_button.click()
            self._random_delay(1, 2)

            # 点击"Add a note"
            try:
                add_note_button = self.page.wait_for_selector('button:has-text("Add a note")', timeout=3000)
                add_note_button.click()
                self._random_delay(1, 2)

                # 输入消息（LinkedIn连接请求限制300字符）
                note_message = message[:300]
                note_box = self.page.wait_for_selector('textarea[name="message"]', timeout=3000)
                self._type_like_human(note_box, note_message)
                self._random_delay(1, 2)

                # 发送连接请求
                send_button = self.page.wait_for_selector('button[aria-label="Send now"]', timeout=3000)
                send_button.click()
                logger.info("   ✅ Connection request with note sent!")
                self._random_delay(2, 3)

                return True

            except Exception as e:
                logger.warning(f"   ⚠️  Could not add note, sending connection without note: {e}")
                # 如果无法添加备注，直接发送连接请求
                try:
                    send_button = self.page.wait_for_selector('button[aria-label="Send now"]', timeout=3000)
                    send_button.click()
                    logger.info("   ✅ Connection request sent (no note)")
                    return True
                except:
                    return False

        except Exception as e:
            logger.error(f"❌ Error sending connection request: {e}")
            return False

    def send_message(self, user_profile_url: str, message: str) -> bool:
        """
        发送LinkedIn消息（简化接口）

        Args:
            user_profile_url: 用户profile URL
            message: 消息内容

        Returns:
            是否成功发送
        """
        user_profile = {
            'profile_url': user_profile_url,
            'name': 'LinkedIn User'
        }
        return self.send_dm(user_profile, message)

    def __del__(self):
        """析构函数，关闭浏览器"""
        self._close_browser()


# 测试代码
if __name__ == "__main__":
    sender = LinkedInDMSender()

    # 测试用户资料
    test_user = {
        'name': 'Test User',
        'profile_url': 'https://www.linkedin.com/in/test-user/',
        'company': 'Test Company',
        'project': 'Test Project'
    }

    # 测试消息
    test_message = """Hey {{name}}, I came across your work at {{company}} — really liked what you're doing with {{project}}.

I'm building something called HireMeAI, it helps teams prep for interviews with AI feedback and auto-review tools.

If you're open to it, I'd love to get your quick thoughts — always great hearing from people actually running interviews."""

    formatted_message = sender.format_message(test_message, test_user)
    print(f"\n📝 Formatted message:\n{formatted_message}\n")

    # 发送测试消息
    # success = sender.send_dm(test_user, formatted_message)
    # print(f"\n{'✅' if success else '❌'} Test result: {success}")
