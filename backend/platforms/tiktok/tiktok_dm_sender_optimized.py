"""
TikTok DM Sender - 优化版（AI Healer自动处理 + 反封禁保护）
架构：Follow → 发消息（AI自由发挥，模拟真人）

反封禁保护机制：
1. 检测"违反社区准则"错误并立即停止
2. 严格速率限制（每小时3-5条，每天20条）
3. 长随机延迟（5-15分钟）
4. 休息机制（每3条休息30-60分钟）
5. 工作时间限制（8AM-10PM）
6. 冷却期管理（检测到限制后等待24小时）
"""

import json
import logging
import time
import random
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from playwright.sync_api import sync_playwright
from ai_scraper_healer import AIScraperHealer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 反封禁配置
RATE_LIMIT_FILE = "tiktok_rate_limit.json"
MAX_DM_PER_HOUR = 3  # 每小时最多3条（保守）
MAX_DM_PER_DAY = 20   # 每天最多20条
MIN_DELAY_MINUTES = 5   # 最小延迟5分钟
MAX_DELAY_MINUTES = 15  # 最大延迟15分钟
REST_AFTER_N_MESSAGES = 3  # 每3条消息后休息
REST_DURATION_MINUTES = (30, 60)  # 休息30-60分钟
COOLDOWN_HOURS = 24  # 检测到限制后冷却24小时
WORK_HOURS = (8, 22)  # 工作时间：8AM-10PM


class TikTokDMSender:
    """TikTok私信发送器 - AI Healer版（自动处理验证码和反爬）"""

    def __init__(self, auth_file: str = "platforms_auth.json", use_ai_healer: bool = True):
        """初始化"""
        try:
            with open(auth_file, 'r') as f:
                config = json.load(f)
            self.sessionid = config.get('tiktok', {}).get('sessionid', '')
        except FileNotFoundError:
            logger.error(f"❌ Auth file {auth_file} not found")
            self.sessionid = ''

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

        # AI Healer - 自动处理反爬和验证码
        self.use_ai_healer = use_ai_healer
        self.healer = AIScraperHealer() if use_ai_healer else None

        # 反封禁保护
        self.rate_limits = self._load_rate_limits()
        self.messages_sent_this_session = 0

    def _load_rate_limits(self) -> Dict:
        """加载速率限制数据"""
        if not os.path.exists(RATE_LIMIT_FILE):
            return {
                'hourly_messages': [],
                'daily_messages': [],
                'last_cooldown': None,
                'total_sent': 0
            }
        try:
            with open(RATE_LIMIT_FILE, 'r') as f:
                return json.load(f)
        except:
            return {
                'hourly_messages': [],
                'daily_messages': [],
                'last_cooldown': None,
                'total_sent': 0
            }

    def _save_rate_limits(self):
        """保存速率限制数据"""
        with open(RATE_LIMIT_FILE, 'w') as f:
            json.dump(self.rate_limits, f, indent=2)

    def _is_within_work_hours(self) -> bool:
        """检查是否在工作时间内"""
        current_hour = datetime.now().hour
        return WORK_HOURS[0] <= current_hour < WORK_HOURS[1]

    def _check_rate_limits(self):
        """
        检查速率限制

        Returns:
            (可以发送, 原因说明)
        """
        now = datetime.now()

        # 1. 检查冷却期
        if self.rate_limits.get('last_cooldown'):
            cooldown_end = datetime.fromisoformat(self.rate_limits['last_cooldown']) + timedelta(hours=COOLDOWN_HOURS)
            if now < cooldown_end:
                remaining = (cooldown_end - now).total_seconds() / 3600
                return False, f"⏸️  在冷却期内 (还需等待 {remaining:.1f} 小时)"

        # 2. 检查工作时间
        if not self._is_within_work_hours():
            return False, f"⏰ 不在工作时间内 (工作时间: {WORK_HOURS[0]}:00-{WORK_HOURS[1]}:00)"

        # 3. 清理过期的时间戳
        one_hour_ago = (now - timedelta(hours=1)).isoformat()
        one_day_ago = (now - timedelta(days=1)).isoformat()

        self.rate_limits['hourly_messages'] = [
            ts for ts in self.rate_limits.get('hourly_messages', [])
            if ts > one_hour_ago
        ]
        self.rate_limits['daily_messages'] = [
            ts for ts in self.rate_limits.get('daily_messages', [])
            if ts > one_day_ago
        ]

        # 4. 检查小时限制
        if len(self.rate_limits['hourly_messages']) >= MAX_DM_PER_HOUR:
            return False, f"⏱️  已达到每小时限制 ({MAX_DM_PER_HOUR}条/小时)"

        # 5. 检查每日限制
        if len(self.rate_limits['daily_messages']) >= MAX_DM_PER_DAY:
            return False, f"📅 已达到每日限制 ({MAX_DM_PER_DAY}条/天)"

        # 6. 检查是否需要休息
        if self.messages_sent_this_session > 0 and self.messages_sent_this_session % REST_AFTER_N_MESSAGES == 0:
            rest_duration = random.randint(*REST_DURATION_MINUTES)
            return False, f"😴 发送 {REST_AFTER_N_MESSAGES} 条后休息 {rest_duration} 分钟"

        return True, "✅ 可以发送"

    def _record_message_sent(self):
        """记录消息发送"""
        now = datetime.now().isoformat()
        self.rate_limits['hourly_messages'].append(now)
        self.rate_limits['daily_messages'].append(now)
        self.rate_limits['total_sent'] = self.rate_limits.get('total_sent', 0) + 1
        self.messages_sent_this_session += 1
        self._save_rate_limits()

    def _enter_cooldown(self, reason: str = "检测到限制"):
        """进入冷却期"""
        logger.warning(f"🚨 {reason}，进入 {COOLDOWN_HOURS} 小时冷却期")
        self.rate_limits['last_cooldown'] = datetime.now().isoformat()
        self._save_rate_limits()

    def _check_for_community_violation(self) -> bool:
        """检查页面是否显示社区准则违规"""
        try:
            page_text = self.page.inner_text('body').lower()
            violation_keywords = [
                'community guidelines',
                'violated',
                'restriction',
                '社区准则',
                '违反',
                '限制',
                'temporarily restricted',
                'account restricted'
            ]

            for keyword in violation_keywords:
                if keyword in page_text:
                    logger.error(f"🚫 检测到社区准则违规关键词: {keyword}")
                    return True
            return False
        except:
            return False

    def _setup_browser(self):
        """设置浏览器（无AI，纯Playwright）"""
        if not self.playwright:
            logger.info("🌐 Setting up TikTok browser...")
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=False,
                slow_mo=500,
                args=['--disable-blink-features=AutomationControlled']
            )
            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )

            if self.sessionid:
                self.context.add_cookies([{
                    'name': 'sessionid',
                    'value': self.sessionid,
                    'domain': '.tiktok.com',
                    'path': '/'
                }])

            self.page = self.context.new_page()

    def _random_delay(self, min_sec: float = 1.0, max_sec: float = 3.0):
        """随机延迟（模拟人类）"""
        time.sleep(random.uniform(min_sec, max_sec))

    def _handle_captcha_or_block(self, task_description: str) -> Optional[str]:
        """
        使用AI Healer处理验证码或反爬检测

        Args:
            task_description: 任务描述（如"搜索关键词"、"发送消息"）

        Returns:
            AI生成的代码（如果成功），否则None
        """
        if not self.use_ai_healer or not self.healer:
            return None

        logger.info(f"🤖 AI Healer analyzing: {task_description}")

        try:
            # 截图当前页面
            screenshot_path = f"tiktok_healer_{int(time.time())}.png"
            self.page.screenshot(path=screenshot_path)

            # 让AI自由发挥
            prompt = f"""
TikTok detected automation and showed a CAPTCHA or block page.

Task: {task_description}

Please analyze the screenshot and generate Python code using Playwright to:
1. Handle any CAPTCHAs or verification (if possible)
2. Simulate human behavior (random mouse movements, delays, scrolling)
3. Complete the task naturally like a real user would

Important:
- Use random delays between actions (1-3 seconds)
- Simulate mouse movements before clicks
- Scroll naturally
- If CAPTCHA is too complex, suggest manual intervention

Return executable Python code using the 'page' variable.
"""

            code = self.healer.diagnose_and_fix(
                screenshot_path=screenshot_path,
                error_message=f"TikTok anti-bot detection for: {task_description}",
                current_code="",  # 让AI完全自由发挥
                prompt_override=prompt
            )

            # 清理截图
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)

            return code

        except Exception as e:
            logger.error(f"❌ AI Healer failed: {e}")
            return None

    def send_dm(self, user: Dict, message: str) -> bool:
        """
        发送TikTok DM（带反封禁保护）

        核心流程：
        1. 【新增】检查速率限制和工作时间
        2. 访问用户profile（使用保存的链接）
        3. Follow用户（如果未关注）
        4. 点击"Message"按钮
        5. 输入消息
        6. 发送
        7. 【新增】检测社区准则违规
        8. 【新增】添加随机延迟

        Args:
            user: 用户信息 {'username': '...', 'profile_url': '...', ...}
            message: 消息内容

        Returns:
            是否成功
        """
        username = user.get('username', '').lstrip('@')
        profile_url = user.get('profile_url', '')  # 从评论抓取时保存的链接

        if not username:
            logger.error("❌ No username")
            return False

        # ===== 反封禁保护：发送前检查 =====
        can_send, reason = self._check_rate_limits()
        if not can_send:
            logger.warning(f"⚠️  跳过发送: {reason}")
            # 如果需要休息，执行休息
            if "休息" in reason:
                rest_duration = random.randint(*REST_DURATION_MINUTES)
                logger.info(f"😴 休息 {rest_duration} 分钟...")
                time.sleep(rest_duration * 60)
            return False

        try:
            self._setup_browser()

            logger.info(f"💬 Sending DM to @{username}...")

            # 步骤1: 访问用户profile（直接使用保存的链接！）
            logger.info("📱 Step 1: Going to profile...")
            if profile_url:
                # 使用保存的profile链接（避免用户名问题）
                logger.info(f"   Using saved profile URL: {profile_url}")
                self.page.goto(profile_url, timeout=30000)
            else:
                # 备用方案：尝试构造URL
                logger.info(f"   Constructing URL from username: @{username}")
                self.page.goto(f'https://www.tiktok.com/@{username}', timeout=30000)
            self._random_delay(2, 3)

            # 步骤2: Follow用户（可选，如果已关注会跳过）
            logger.info("👥 Step 2: Following user...")

            follow_selectors = [
                'button[data-e2e="follow-button"]',
                'button:has-text("Follow")',
                'button:has-text("关注")',
            ]

            followed = False
            for selector in follow_selectors:
                try:
                    follow_btn = self.page.wait_for_selector(selector, timeout=3000)
                    if follow_btn and follow_btn.is_visible():
                        # 检查是否已经关注
                        text = follow_btn.inner_text()
                        if 'Following' in text or '已关注' in text:
                            logger.info("   ℹ️  Already following")
                            followed = True
                            break

                        logger.info(f"   ✅ Following...")
                        self.page.evaluate('(el) => el.click()', follow_btn)
                        self._random_delay(2, 3)
                        followed = True
                        break
                except:
                    continue

            if not followed:
                logger.info("   ℹ️  Follow button not found (might already be following)")

            # 步骤3: 点击"Message"按钮（固定选择器，无AI）
            logger.info("💬 Step 3: Opening message...")

            message_selectors = [
                'button[data-e2e="message-button"]',
                'button:has-text("Message")',
                'button:has-text("消息")',
                'div[role="button"]:has-text("Message")',
            ]

            message_opened = False
            for selector in message_selectors:
                try:
                    msg_btn = self.page.wait_for_selector(selector, timeout=3000)
                    if msg_btn and msg_btn.is_visible():
                        logger.info(f"   ✅ Found message button")
                        self.page.evaluate('(el) => el.click()', msg_btn)
                        self._random_delay(2, 3)
                        message_opened = True
                        break
                except:
                    continue

            if not message_opened:
                logger.error("❌ Could not find message button")
                logger.info("   Trying alternative: Direct message URL...")
                # 尝试直接访问消息页面
                self.page.goto(f'https://www.tiktok.com/messages', timeout=30000)
                self._random_delay(2, 3)

                # 搜索用户
                search_input = self.page.wait_for_selector('input[placeholder*="Search"]', timeout=5000)
                if search_input:
                    search_input.fill(username)
                    self._random_delay(2, 3)
                    # 点击第一个结果
                    results = self.page.query_selector_all('div[role="button"]')
                    if results and len(results) > 0:
                        self.page.evaluate('(el) => el.click()', results[0])
                        self._random_delay(2, 3)
                else:
                    return False

            # 步骤4: 找到输入框（固定选择器）
            logger.info("✏️  Step 4: Typing message...")

            input_selectors = [
                'div[contenteditable="true"][data-e2e="message-input"]',
                'div[contenteditable="true"]',
                'textarea[placeholder*="Message"]',
                'textarea[placeholder*="消息"]',
            ]

            message_input = None
            max_retries = 3  # 增加重试次数
            for retry in range(max_retries):
                for selector in input_selectors:
                    try:
                        message_input = self.page.wait_for_selector(selector, timeout=5000)
                        if message_input and message_input.is_visible():
                            logger.info(f"   ✅ Found input")
                            break
                    except:
                        continue

                if message_input:
                    break

                # 如果没找到输入框，尝试修复
                if retry < max_retries - 1:
                    logger.warning(f"   ⚠️  Input not found (attempt {retry + 1}/{max_retries})")
                    logger.info("   🔄 Trying to fix...")

                    # 策略1: 按ESC键关闭可能的弹窗
                    try:
                        self.page.keyboard.press('Escape')
                        self._random_delay(0.5, 1)
                    except:
                        pass

                    # 策略2: 等待网络空闲（页面可能还在加载）
                    try:
                        logger.info("   ⏳ Waiting for page to finish loading...")
                        self.page.wait_for_load_state('networkidle', timeout=10000)
                        self._random_delay(1, 2)
                    except:
                        logger.info("   ⚠️  Page still loading, continuing anyway...")

                    # 策略3: 重新点击Message按钮
                    logger.info("   🔄 Re-clicking message button...")
                    for selector in message_selectors:
                        try:
                            btn = self.page.query_selector(selector)
                            if btn and btn.is_visible():
                                self.page.evaluate('(el) => el.click()', btn)
                                self._random_delay(2, 3)
                                break
                        except:
                            continue

            if not message_input:
                logger.error("❌ Input not found after retries")
                logger.info("   💡 Possible reasons:")
                logger.info("      - Page stuck loading (screenshot shows spinning circle)")
                logger.info("      - Need to refresh or click Message button again")
                logger.info("      - May need manual intervention")
                return False

            # 输入消息（无AI）
            message_input.fill(message)
            self._random_delay(1, 2)

            # 步骤5: 发送（固定选择器）
            logger.info("📤 Step 5: Sending...")

            # 记录发送前输入框内容（用于验证是否成功）
            input_text_before = message_input.inner_text() if hasattr(message_input, 'inner_text') else message[:20]

            sent_success = False

            # 方法1: 尝试点击发送按钮
            send_selectors = [
                'button[data-e2e="send-button"]',
                'div[role="button"]:has-text("Send")',
                'div[role="button"]:has-text("发送")',
                'button:has-text("Send")',
                'button:has-text("发送")',
            ]

            for selector in send_selectors:
                try:
                    send_btns = self.page.query_selector_all(selector)
                    for btn in send_btns:
                        if btn.is_visible() and not btn.is_disabled():
                            self.page.evaluate('(el) => el.click()', btn)
                            logger.info("   ✅ Clicked send button")
                            self._random_delay(2, 3)
                            sent_success = True
                            break
                    if sent_success:
                        break
                except:
                    continue

            # 方法2: 如果找不到Send按钮，尝试Enter键
            if not sent_success:
                try:
                    logger.info("   Trying Enter key...")
                    message_input.press('Enter')
                    logger.info("   ✅ Pressed Enter")
                    self._random_delay(2, 3)
                    sent_success = True
                except:
                    logger.warning("   ⚠️  Could not press Enter")

            # 验证是否成功发送：检查消息是否出现在聊天界面
            if sent_success:
                logger.info("🔍 Verifying message was sent...")
                time.sleep(2)

                # ===== 反封禁保护：检测社区准则违规 =====
                if self._check_for_community_violation():
                    self._enter_cooldown("检测到社区准则违规")
                    logger.error("❌ 消息可能被拦截，已进入冷却期")
                    return False

                # 检查方法1: 输入框是否被清空
                try:
                    current_input = message_input.inner_text() if hasattr(message_input, 'inner_text') else ''
                    if not current_input or len(current_input.strip()) == 0:
                        logger.info("   ✅ Input cleared - message sent!")
                        logger.info("✅ Message sent successfully!")
                        # ===== 反封禁保护：记录发送 =====
                        self._record_message_sent()
                        # ===== 反封禁保护：随机延迟（5-15分钟）=====
                        delay_minutes = random.randint(MIN_DELAY_MINUTES, MAX_DELAY_MINUTES)
                        logger.info(f"⏳ 等待 {delay_minutes} 分钟后继续...")
                        time.sleep(delay_minutes * 60)
                        return True
                except:
                    pass

                # 检查方法2: 查找消息气泡（包含我们发送的文本）
                try:
                    # 简化消息文本用于搜索（取前30个字符）
                    search_text = message[:30].strip()
                    page_text = self.page.inner_text('body')

                    if search_text in page_text:
                        logger.info(f"   ✅ Found message in chat - message sent!")
                        logger.info("✅ Message sent successfully!")
                        # ===== 反封禁保护：记录发送 =====
                        self._record_message_sent()
                        # ===== 反封禁保护：随机延迟（5-15分钟）=====
                        delay_minutes = random.randint(MIN_DELAY_MINUTES, MAX_DELAY_MINUTES)
                        logger.info(f"⏳ 等待 {delay_minutes} 分钟后继续...")
                        time.sleep(delay_minutes * 60)
                        return True
                except:
                    pass

                # 如果无法验证但操作执行了，假设成功
                logger.info("   ⚠️  Could not verify, but send action completed")
                logger.info("✅ Message likely sent successfully!")
                # ===== 反封禁保护：记录发送 =====
                self._record_message_sent()
                # ===== 反封禁保护：随机延迟（5-15分钟）=====
                delay_minutes = random.randint(MIN_DELAY_MINUTES, MAX_DELAY_MINUTES)
                logger.info(f"⏳ 等待 {delay_minutes} 分钟后继续...")
                time.sleep(delay_minutes * 60)
                return True

            logger.error("❌ Could not send message")
            return False

        except Exception as e:
            logger.error(f"❌ Error: {e}")
            # ===== 反封禁保护：检查是否因违规导致错误 =====
            if self.page and self._check_for_community_violation():
                self._enter_cooldown("发送失败，检测到社区准则违规")
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
    sender = TikTokDMSender()

    test_user = {'username': 'garyvee'}
    test_message = """Hey, I saw your content about entrepreneurship!

I'm building HireMeAI (https://interviewasssistant.com), an AI interview prep platform.

Would love your feedback!"""

    success = sender.send_dm(test_user, test_message)
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")

    sender.cleanup()
