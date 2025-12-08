"""
Instagram DM Sender - Instagram私信发送器
正确流程：搜索 → 点帖子 → 点视频中头像 → 发消息
"""

import json
import logging
from typing import Dict
from playwright.sync_api import sync_playwright
from dm_sender_base import DMSenderBase
from ai_scraper_healer import AIScraperHealer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InstagramDMSender(DMSenderBase):
    """Instagram私信发送器 - 通过搜索和帖子访问用户"""

    def __init__(self, auth_file: str = "platforms_auth.json", use_ai_healer: bool = True):
        """初始化Instagram DM发送器"""
        try:
            with open(auth_file, 'r') as f:
                config = json.load(f)
            auth_config = config.get('instagram', {})
        except FileNotFoundError:
            logger.error(f"❌ Auth file {auth_file} not found")
            auth_config = {}

        super().__init__(auth_config, 'Instagram')
        self.sessionid = auth_config.get('sessionid', '')
        self.use_ai_healer = use_ai_healer
        self.ai_healer = AIScraperHealer() if use_ai_healer else None

        if self.use_ai_healer:
            logger.info("🤖 AI Healer enabled for auto-fixing")

    def _setup_browser(self):
        """设置Playwright浏览器并加载Instagram cookies"""
        if not self.playwright:
            logger.info("🌐 Setting up Instagram browser...")
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=False,
                slow_mo=800,  # 慢速模式，更像人类
                args=['--disable-blink-features=AutomationControlled']
            )
            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1280, 'height': 900}
            )

            # 加载sessionid cookie
            if self.sessionid:
                self.context.add_cookies([{
                    'name': 'sessionid',
                    'value': self.sessionid,
                    'domain': '.instagram.com',
                    'path': '/'
                }])
                logger.info("   ✅ Instagram cookies loaded")

            self.page = self.context.new_page()

    def send_dm(self, user_profile: Dict, message: str) -> bool:
        """
        发送Instagram DM
        正确流程：搜索用户名 → 点击帖子/视频 → 点击头像 → 发消息

        Args:
            user_profile: 用户资料（必须包含username）
            message: 消息内容

        Returns:
            是否成功发送
        """
        username = user_profile.get('username', user_profile.get('instagram_username'))
        if not username:
            logger.error("❌ No Instagram username found")
            return False

        # 移除@符号
        username = username.lstrip('@')

        try:
            self._setup_browser()

            logger.info(f"💬 Sending DM to @{username} via search workflow...")

            # 步骤1: 访问Instagram主页
            logger.info("📱 Step 1: Going to Instagram homepage...")
            self.page.goto('https://www.instagram.com/', timeout=30000)
            self._random_delay(2, 3)

            # 检查是否登录
            if 'login' in self.page.url:
                logger.error("❌ Not logged in to Instagram")
                return False

            logger.info("   ✅ Logged in")

            # 关闭可能的通知弹窗
            try:
                # 查找"以后再说"按钮（中文）或"Not Now"（英文）
                not_now_selectors = [
                    'button:has-text("以后再说")',
                    'button:has-text("Not Now")',
                    'button:has-text("稍后")',
                    'button:has-text("暂不")',
                ]

                for selector in not_now_selectors:
                    try:
                        dismiss_button = self.page.wait_for_selector(selector, timeout=3000)
                        if dismiss_button:
                            logger.info("   🔕 Closing notification popup...")
                            dismiss_button.click()
                            self._random_delay(1, 2)
                            break
                    except:
                        continue
            except Exception as e:
                logger.debug(f"   No notification popup to dismiss: {e}")

            # 步骤2: 搜索用户名
            logger.info(f"🔍 Step 2: Searching for '@{username}'...")

            # 点击搜索图标（支持中英文）
            search_icon_selectors = [
                'svg[aria-label="搜索"]',  # 中文
                'svg[aria-label="Search"]',  # 英文
                'span:has-text("搜索")',  # 中文文本
                'span:has-text("Search")',  # 英文文本
                'a[href="#"]:has(svg[aria-label="Search"])',
                'a[href="#"]:has(svg[aria-label="搜索"])',
            ]

            search_clicked = False
            for selector in search_icon_selectors:
                try:
                    search_icon = self.page.wait_for_selector(selector, timeout=3000)
                    if search_icon:
                        search_icon.click()
                        logger.info("   ✅ Clicked search icon")
                        search_clicked = True
                        self._random_delay(1, 2)
                        break
                except:
                    continue

            if not search_clicked:
                logger.error("❌ Could not find search icon")
                return False

            # 输入搜索关键词
            search_input_selectors = [
                'input[placeholder="Search"]',
                'input[aria-label="Search input"]',
                'input[type="text"]',
            ]

            search_input = None
            for selector in search_input_selectors:
                try:
                    search_input = self.page.wait_for_selector(selector, timeout=3000)
                    if search_input:
                        logger.info(f"   ✅ Found search input: {selector}")
                        break
                except:
                    continue

            if not search_input:
                logger.error("❌ Could not find search input")
                return False

            # 输入用户名
            self._type_like_human(search_input, username)
            self._random_delay(2, 3)

            # 步骤3: 点击搜索结果中的用户
            logger.info("👤 Step 3: Clicking on user profile from results...")

            user_result_selectors = [
                f'a[href="/{username}/"]',
                f'div:has-text("@{username}")',
                'div[role="button"]:has-text("' + username + '")',
            ]

            user_result = None
            for selector in user_result_selectors:
                try:
                    user_result = self.page.wait_for_selector(selector, timeout=5000)
                    if user_result:
                        logger.info(f"   ✅ Found user result: {selector}")
                        user_result.click()
                        self._random_delay(2, 3)
                        break
                except:
                    continue

            if not user_result:
                logger.warning("   ⚠️  Could not find user in search results, trying direct profile URL...")
                self.page.goto(f'https://www.instagram.com/{username}/', timeout=30000)
                self._random_delay(2, 3)

            # 步骤4: AI建议 - 在profile页面直接点Message按钮（不要通过帖子）
            logger.info("💬 Step 4: Looking for Message button on profile page...")

            # 确保在profile页面
            if f'instagram.com/{username}' not in self.page.url:
                logger.info(f"   Navigating to profile page...")
                self.page.goto(f'https://www.instagram.com/{username}/', timeout=30000)
                self._random_delay(2, 3)

            # 根据AI Healer建议 - profile页面的Message按钮会直接打开DM界面
            message_button_selectors = [
                'div[role="button"]:has-text("消息")',  # 中文
                'div[role="button"]:has-text("发消息")',  # 中文变体
                'div[role="button"]:has-text("Message")',  # 英文
                'button:has-text("消息")',  # 备选
                'button:has-text("发消息")',
                'button:has-text("Message")',
            ]

            message_button = None
            for selector in message_button_selectors:
                try:
                    message_button = self.page.wait_for_selector(selector, timeout=5000)
                    if message_button and message_button.is_visible():
                        logger.info(f"   ✅ Found Message button on profile: {selector}")
                        # 使用JavaScript点击确保成功
                        self.page.evaluate('(element) => element.click()', message_button)
                        self._random_delay(3, 5)  # 等待DM界面加载
                        break
                except:
                    continue

            if not message_button:
                logger.warning("   ⚠️  No Message button on profile, trying direct DM URL (AI fallback)...")
                # AI建议的替代方案：直接访问 /direct/new/ 并搜索用户
                self.page.goto(f'https://www.instagram.com/direct/new/', timeout=30000)
                self._random_delay(2, 3)

                # 在新建消息页面搜索用户
                recipient_input_selectors = [
                    'input[placeholder*="Search"]',
                    'input[placeholder*="搜索"]',
                    'input[name="queryBox"]',
                ]

                for selector in recipient_input_selectors:
                    try:
                        recipient_input = self.page.wait_for_selector(selector, timeout=3000)
                        if recipient_input:
                            logger.info("   ✅ Found recipient search input")
                            self._type_like_human(recipient_input, username)
                            self._random_delay(2, 3)

                            # 点击搜索结果
                            result_selectors = [
                                f'div:has-text("{username}")',
                                f'span:has-text("{username}")',
                                'div[role="button"]',
                            ]

                            for result_selector in result_selectors:
                                try:
                                    result = self.page.wait_for_selector(result_selector, timeout=3000)
                                    if result:
                                        result.click()
                                        self._random_delay(1, 2)
                                        logger.info("   ✅ Clicked on user in search results")
                                        break
                                except:
                                    continue
                            break
                    except:
                        continue

            # 步骤5: 等待DM界面加载并验证
            logger.info("⏳ Step 5: Waiting for DM interface to load...")
            self._random_delay(3, 5)

            # 检查URL是否变化到direct/t/
            current_url = self.page.url
            logger.info(f"   Current URL: {current_url}")

            # AI建议：如果还在profile页面，说明Message按钮没有打开DM界面
            if '/direct/' not in current_url:
                logger.warning("   ⚠️  Still on profile page - Message button didn't open DM interface")
                logger.info("   💡 Using AI fallback: Navigate to /direct/new/ and search user")

                # AI建议的替代方案：直接访问新建消息页面
                self.page.goto('https://www.instagram.com/direct/new/', timeout=30000)
                self._random_delay(2, 3)

                # 查找收件人搜索框
                recipient_search_selectors = [
                    'input[placeholder*="Search"]',
                    'input[placeholder*="搜索"]',
                    'input[name="queryBox"]',
                    'input[aria-label*="Search"]',
                ]

                recipient_input = None
                for selector in recipient_search_selectors:
                    try:
                        recipient_input = self.page.wait_for_selector(selector, timeout=5000)
                        if recipient_input:
                            logger.info(f"   ✅ Found recipient search: {selector}")
                            break
                    except:
                        continue

                if recipient_input:
                    # 输入用户名 (使用fill避免DOM detachment问题)
                    try:
                        # 先尝试使用fill (更稳定)
                        recipient_input.fill(username)
                        logger.info(f"   ✅ Filled username: {username}")
                    except:
                        # 如果fill失败，尝试传统方式
                        try:
                            self._type_like_human(recipient_input, username)
                        except:
                            # 最后尝试直接JavaScript输入
                            self.page.evaluate(f'(el) => {{ el.value = "{username}"; el.dispatchEvent(new Event("input", {{ bubbles: true }})); }}', recipient_input)

                    self._random_delay(2, 3)

                    # 点击搜索结果中的用户
                    user_result_selectors = [
                        f'div[role="button"]:has-text("{username}")',
                        f'button:has-text("{username}")',
                        'div[role="button"]',  # 通用结果按钮
                    ]

                    for selector in user_result_selectors:
                        try:
                            user_result = self.page.wait_for_selector(selector, timeout=3000)
                            if user_result:
                                logger.info("   ✅ Clicking on user in search results")
                                user_result.click()
                                self._random_delay(2, 3)
                                break
                        except:
                            continue

                    # 点击"Chat"或"聊天"按钮开始对话
                    chat_button_selectors = [
                        'button:has-text("Chat")',
                        'button:has-text("聊天")',
                        'div[role="button"]:has-text("Chat")',
                        'div[role="button"]:has-text("聊天")',
                    ]

                    for selector in chat_button_selectors:
                        try:
                            chat_button = self.page.wait_for_selector(selector, timeout=3000)
                            if chat_button:
                                logger.info("   ✅ Clicking Chat button")
                                chat_button.click()
                                self._random_delay(3, 4)
                                break
                        except:
                            continue

                    logger.info(f"   New URL after direct/new flow: {self.page.url}")
                else:
                    logger.error("   ❌ Could not find recipient search input")

            # 步骤7: 输入消息
            logger.info("✏️  Step 7: Typing message...")

            message_box_selectors = [
                'div[contenteditable="true"][role="textbox"]',  # Instagram DM输入框
                'div[contenteditable="true"]',  # 通用contenteditable
                'textarea[placeholder*="Message"]',
                'textarea[placeholder*="消息"]',  # 中文
                'textarea[aria-label*="Message"]',
                'textarea[aria-label*="消息"]',
                'div[aria-label*="Message"]',
                'div[aria-label*="消息"]',
            ]

            message_box = None
            for selector in message_box_selectors:
                try:
                    message_box = self.page.wait_for_selector(selector, timeout=5000)
                    if message_box:
                        logger.info(f"   ✅ Found message input: {selector}")
                        break
                except:
                    continue

            if not message_box:
                logger.warning("⚠️  Could not find message input box with standard selectors")

                if self.use_ai_healer and self.ai_healer:
                    logger.info("🤖 Activating AI Healer to find message input...")

                    # 让AI分析页面
                    analysis = self.ai_healer.analyze_page_with_vision(
                        page=self.page,
                        task_description=f"Find the message input box to send a DM to {username}. I need to type a message.",
                        current_url=self.page.url,
                        error_message=f"Could not find message input with selectors: {message_box_selectors}"
                    )

                    logger.info(f"🧠 AI Analysis: {analysis.get('problem_analysis', 'No analysis')[:200]}...")
                    logger.info(f"🎯 AI Confidence: {analysis.get('confidence', 0)}")

                    if analysis.get('confidence', 0) >= 0.7:
                        # 应用AI建议的操作
                        self.ai_healer.apply_human_like_actions(self.page, analysis)

                        # 尝试AI建议的选择器
                        success, working_selector = self.ai_healer.try_selectors_with_ai_guidance(
                            page=self.page,
                            ai_analysis=analysis,
                            action="fill"
                        )

                        if success:
                            logger.info(f"✅ AI Healer found working selector: {working_selector}")
                            message_box = self.page.wait_for_selector(working_selector, timeout=3000)
                        else:
                            # 尝试AI建议的替代方案
                            alt_approach = analysis.get('alternative_approach', '')
                            if alt_approach:
                                logger.info(f"💡 Trying AI alternative approach: {alt_approach[:100]}...")
                                # 这里可以添加执行替代方案的逻辑

                if not message_box:
                    logger.error("❌ Could not find message input box (even with AI)")
                    logger.info("   Checking page elements for debugging...")

                    # Debug: 查找所有可能的输入元素
                    all_textareas = self.page.query_selector_all('textarea')
                    all_contenteditable = self.page.query_selector_all('[contenteditable="true"]')
                    all_inputs = self.page.query_selector_all('input[type="text"]')

                    logger.info(f"   Found {len(all_textareas)} textareas")
                    logger.info(f"   Found {len(all_contenteditable)} contenteditable divs")
                    logger.info(f"   Found {len(all_inputs)} text inputs")

                    return False

            # 输入消息内容
            self._type_like_human(message_box, message)
            self._random_delay(1, 2)

            # 步骤8: 发送消息
            logger.info("📤 Step 8: Sending message...")

            send_button_selectors = [
                'button:has-text("Send")',
                'div[role="button"]:has-text("Send")',
                'button[type="submit"]',
            ]

            send_button = None
            for selector in send_button_selectors:
                try:
                    send_button = self.page.wait_for_selector(selector, timeout=3000)
                    if send_button and not send_button.is_disabled():
                        logger.info(f"   ✅ Found send button")
                        send_button.click()
                        self._random_delay(2, 3)
                        break
                except:
                    continue

            if not send_button:
                logger.error("❌ Could not find send button")
                return False

            logger.info("✅ Message sent successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Error sending Instagram DM: {e}")
            import traceback
            traceback.print_exc()
            return False


# 测试代码
if __name__ == "__main__":
    sender = InstagramDMSender()

    test_user = {
        'username': 'test_user',
        'name': 'Test User'
    }

    test_message = """Hey, I came across your content — really inspiring!

I'm building HireMeAI (https://interviewasssistant.com), helps with interview prep.

Would love your thoughts!"""

    formatted_message = sender.format_message(test_message, test_user)
    print(f"\n📝 Formatted message:\n{formatted_message}\n")
