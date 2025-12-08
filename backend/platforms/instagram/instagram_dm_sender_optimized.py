"""
Instagram DM Sender - 优化版 + AI Healer
架构：Follow → 发消息（优先纯选择器，失败时用AI Vision诊断）
"""

import json
import logging
import time
import random
import os
from typing import Dict, Optional
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AI Healer（按需导入）
try:
    from ai_scraper_healer import AIScraperHealer
    AI_HEALER_AVAILABLE = True
except:
    AI_HEALER_AVAILABLE = False
    logger.warning("⚠️  AI Healer not available")


class InstagramDMSender:
    """Instagram私信发送器 - 优化版 + AI Healer"""

    def __init__(self, auth_file: str = "platforms_auth.json", use_ai_healer: bool = True):
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

        # AI Healer
        self.use_ai_healer = use_ai_healer and AI_HEALER_AVAILABLE
        self.ai_healer = None
        if self.use_ai_healer:
            try:
                self.ai_healer = AIScraperHealer()
                logger.info("✅ AI Healer enabled")
            except:
                logger.warning("⚠️  AI Healer failed to initialize")
                self.use_ai_healer = False

    def _setup_browser(self):
        """设置浏览器（无AI，纯Playwright）"""
        if not self.playwright:
            logger.info("🌐 Setting up Instagram browser...")
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=False,
                # slow_mo=500,  # 取消慢动作
                args=['--disable-blink-features=AutomationControlled']
            )
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

            self.page = self.context.new_page()

    def _random_delay(self, min_sec: float = 1.0, max_sec: float = 3.0):
        """随机延迟（模拟人类）- 已禁用"""
        pass  # 取消等待

    def _close_notifications(self):
        """关闭通知弹窗（无AI，固定选择器）"""
        try:
            dismiss_selectors = [
                'button:has-text("Not Now")',
                'button:has-text("以后再说")',
                'button:has-text("稍后")',
            ]
            for selector in dismiss_selectors:
                try:
                    btn = self.page.wait_for_selector(selector, timeout=2000)
                    if btn:
                        btn.click()
                        self._random_delay(0.5, 1)
                        break
                except:
                    continue
        except:
            pass

    def send_dm(self, user: Dict, message: str) -> bool:
        """
        发送Instagram DM

        核心流程（无AI）：
        1. 访问用户profile
        2. Follow用户（如果未关注）
        3. 点击"发消息"按钮
        4. 输入消息
        5. 发送

        Args:
            user: 用户信息 {'username': '...', ...}
            message: 消息内容

        Returns:
            是否成功
        """
        username = user.get('username', '').lstrip('@')
        if not username:
            logger.error("❌ No username")
            return False

        try:
            self._setup_browser()

            logger.info(f"💬 Sending DM to @{username}...")

            # 步骤1: 访问用户profile（无AI，直接URL）
            logger.info("📱 Step 1: Going to profile...")
            self.page.goto(f'https://www.instagram.com/{username}/', timeout=30000)
            self._random_delay(2, 3)

            # 关闭弹窗
            self._close_notifications()

            # 步骤2: Follow用户（可选，如果已关注会跳过）
            logger.info("👥 Step 2: Following user...")

            follow_selectors = [
                'button:has-text("Follow")',
                'button:has-text("关注")',
                'div[role="button"]:has-text("Follow")',
                'div[role="button"]:has-text("关注")',
            ]

            followed = False
            for selector in follow_selectors:
                try:
                    follow_btn = self.page.wait_for_selector(selector, timeout=3000)
                    if follow_btn and follow_btn.is_visible():
                        logger.info(f"   ✅ Following...")
                        self.page.evaluate('(el) => el.click()', follow_btn)
                        self._random_delay(2, 3)
                        followed = True
                        break
                except:
                    continue

            if not followed:
                logger.info("   ℹ️  Already following")

            # 步骤3: 点击"发消息"按钮（固定选择器，无AI）
            logger.info("💬 Step 3: Opening message...")

            # 优先中文，再英文
            message_selectors = [
                'div[role="button"]:has-text("发消息")',
                'div[role="button"]:has-text("消息")',
                'button:has-text("发消息")',
                'button:has-text("Message")',
                'div[role="button"]:has-text("Message")',
            ]

            message_opened = False

            # 可能需要点击多次（Instagram有时会显示菜单）
            for selector in message_selectors:
                try:
                    msg_btn = self.page.wait_for_selector(selector, timeout=5000)
                    if msg_btn and msg_btn.is_visible():
                        logger.info(f"   ✅ Found button: {selector}")
                        msg_btn.click()
                        self._random_delay(1, 2)

                        # 关闭可能出现的弹窗菜单（加入密友名单等）
                        close_selectors = [
                            'svg[aria-label="关闭"]',
                            '[aria-label="关闭"]',
                            'svg[aria-label="Close"]',
                            '[aria-label="Close"]',
                        ]
                        for close_sel in close_selectors:
                            try:
                                close_btn = self.page.query_selector(close_sel)
                                if close_btn and close_btn.is_visible():
                                    logger.info(f"   ℹ️  Closing popup menu...")
                                    close_btn.click()
                                    self._random_delay(0.5, 1)
                                    break
                            except:
                                continue

                        self._random_delay(1, 2)

                        # 检查是否打开了消息对话框（通过查找输入框）
                        try:
                            input_check = self.page.query_selector('div[contenteditable="true"]')
                            if input_check and input_check.is_visible():
                                logger.info("   ✅ Message dialog opened!")
                                message_opened = True
                                break
                        except:
                            pass

                        # 如果还没打开，继续尝试下一个选择器（可能是菜单里的按钮）
                        logger.info("   ℹ️  Dialog not opened yet, trying next selector...")

                except Exception as e:
                    logger.debug(f"   ❌ {selector} failed: {e}")
                    continue

            if not message_opened:
                logger.warning("⚠️  Standard selectors failed for message button")

                # 尝试AI Healer
                if self.use_ai_healer and self.ai_healer:
                    logger.info("🤖 Calling AI Healer to analyze page...")
                    ai_analysis = self.ai_healer.analyze_page_with_vision(
                        page=self.page,
                        task_description="Find and click the Message/发消息 button on Instagram profile",
                        current_url=self.page.url,
                        error_message="Could not find message button with standard selectors"
                    )

                    # 尝试AI建议的选择器
                    success, working_selector = self.ai_healer.try_selectors_with_ai_guidance(
                        page=self.page,
                        ai_analysis=ai_analysis,
                        action="click"
                    )

                    if success:
                        logger.info(f"✅ AI Healer found working selector: {working_selector}")
                        self._random_delay(3, 4)
                        message_opened = True
                    else:
                        logger.error("❌ AI Healer also failed")
                        return False
                else:
                    logger.error("❌ Could not find message button and AI Healer not available")
                    return False

            # 步骤4: 找到输入框（固定选择器）
            logger.info("✏️  Step 4: Typing message...")

            # 等待消息对话框完全加载
            self._random_delay(2, 3)

            input_selectors = [
                'div[contenteditable="true"][role="textbox"]',
                'div[contenteditable="true"][aria-label*="消息"]',
                'div[contenteditable="true"][aria-label*="Message"]',
                'div[contenteditable="true"]',
                'textarea[placeholder*="Message"]',
                'textarea[placeholder*="消息"]',
                'p[contenteditable="true"]',
            ]

            message_input = None
            for selector in input_selectors:
                try:
                    message_input = self.page.wait_for_selector(selector, timeout=5000)
                    if message_input and message_input.is_visible():
                        logger.info(f"   ✅ Found input: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"   ❌ {selector} failed: {e}")
                    continue

            # 最后尝试：查找所有可见的contenteditable
            if not message_input:
                logger.info("   ℹ️  Trying all visible contenteditable...")
                try:
                    all_editable = self.page.query_selector_all('[contenteditable="true"]')
                    for elem in all_editable:
                        if elem.is_visible():
                            message_input = elem
                            logger.info("   ✅ Found visible contenteditable")
                            break
                except:
                    pass

            if not message_input:
                logger.warning("⚠️  Standard selectors failed for input box")

                # 尝试AI Healer
                if self.use_ai_healer and self.ai_healer:
                    logger.info("🤖 Calling AI Healer for input box...")
                    ai_analysis = self.ai_healer.analyze_page_with_vision(
                        page=self.page,
                        task_description="Find the message input box (contenteditable or textarea) in Instagram DM dialog",
                        current_url=self.page.url,
                        error_message="Could not find message input with standard selectors"
                    )

                    # 尝试AI建议的选择器
                    for selector_info in ai_analysis.get('suggested_selectors', []):
                        selector = selector_info.get('selector')
                        try:
                            elem = self.page.wait_for_selector(selector, timeout=3000)
                            if elem and elem.is_visible():
                                message_input = elem
                                logger.info(f"✅ AI Healer found input: {selector}")
                                break
                        except:
                            continue

                if not message_input:
                    logger.error("❌ Input not found (AI Healer also failed)")
                    return False

            # 输入消息（无AI）
            message_input.click()
            self._random_delay(0.5, 1)
            message_input.fill(message)
            self._random_delay(1, 2)

            # 步骤5: 发送（固定选择器）
            logger.info("📤 Step 5: Sending...")

            # 优先中文，再英文
            send_selectors = [
                'div[role="button"]:has-text("发送")',
                'button:has-text("发送")',
                'div[role="button"]:has-text("Send")',
                'button:has-text("Send")',
            ]

            sent = False
            for selector in send_selectors:
                try:
                    send_btns = self.page.query_selector_all(selector)
                    for btn in send_btns:
                        if btn.is_visible() and not btn.is_disabled():
                            btn.click()
                            logger.info(f"   ✅ Sent via button: {selector}")
                            self._random_delay(1, 2)
                            sent = True
                            break
                    if sent:
                        break
                except Exception as e:
                    logger.debug(f"   ❌ {selector} failed: {e}")
                    continue

            # 如果找不到Send按钮，尝试Enter键
            if not sent:
                try:
                    logger.info("   ℹ️  Trying Enter key...")
                    message_input.press('Enter')
                    logger.info("   ✅ Sent via Enter")
                    self._random_delay(1, 2)
                    sent = True
                except:
                    pass

            if sent:
                logger.info("✅ Message sent successfully!")
                return True

            logger.error("❌ Could not send")
            return False

        except Exception as e:
            logger.error(f"❌ Error: {e}")
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


if __name__ == "__main__":
    # 测试
    sender = InstagramDMSender()

    test_user = {'username': 'uciantrepreneur'}
    test_message = """Hey, I saw your comment about entrepreneurship!

I'm building HireMeAI (https://interviewasssistant.com), an AI interview prep platform.

Would love your feedback!"""

    success = sender.send_dm(test_user, test_message)
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")

    sender.cleanup()
