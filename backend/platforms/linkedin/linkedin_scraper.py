"""
LinkedIn Scraper - 领英爬虫
使用Playwright模拟浏览器访问LinkedIn
增强人类行为模拟：随机延迟、鼠标移动、滚动
"""

import json
import time
import random
import logging
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Page, Browser
from src.platform_scraper_base import PlatformScraperBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LinkedInScraper(PlatformScraperBase):
    """LinkedIn平台scraper"""

    def __init__(self, auth_file: str = "linkedin_auth.json"):
        """
        初始化LinkedIn scraper

        Args:
            auth_file: 认证配置文件路径（storage_state JSON）
        """
        # 检查是否使用新的storage_state格式
        import os
        self.use_storage_state = os.path.exists(auth_file) and auth_file.endswith('linkedin_auth.json')

        if self.use_storage_state:
            # 使用storage_state（推荐）
            self.storage_state_file = auth_file
            logger.info(f"Using storage_state from {auth_file}")

            # 初始化base class
            super().__init__({}, 'LinkedIn')

        else:
            # 尝试旧的platforms_auth.json格式
            with open(auth_file, 'r') as f:
                config = json.load(f)

            super().__init__(config.get('linkedin', {}), 'LinkedIn')

            self.cookies = self.auth_config.get('cookies', {})
            self.headers = self.auth_config.get('headers', {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            self.storage_state_file = None

        # Playwright browser
        self.playwright = None
        self.browser = None
        self.page = None

    def _human_like_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """添加随机延迟，模拟人类行为 - 使用非均匀分布"""
        # 使用 beta 分布让时间更不规则（更接近人类行为）
        if random.random() < 0.2:  # 20% 概率快速反应
            delay = random.uniform(min_seconds * 0.5, min_seconds)
        elif random.random() < 0.7:  # 50% 概率正常速度
            delay = random.uniform(min_seconds, (min_seconds + max_seconds) / 2)
        else:  # 30% 概率慢速（思考中）
            delay = random.uniform((min_seconds + max_seconds) / 2, max_seconds * 1.2)
        time.sleep(delay)

    def _random_mouse_movement(self, page: Page):
        """模拟随机鼠标移动 - 完全不规则的时间间隔"""
        num_moves = random.choice([1, 1, 2, 2, 3])  # 更倾向于少量移动
        for i in range(num_moves):
            x = random.randint(100, 1200)
            y = random.randint(100, 800)
            page.mouse.move(x, y)
            # 每次移动的间隔都不同
            if i < num_moves - 1:
                delays = [0.05, 0.08, 0.12, 0.15, 0.18, 0.25, 0.3, 0.35, 0.4, 0.5]
                time.sleep(random.choice(delays))

    def _human_scroll(self, page: Page):
        """人类式滚动 - 完全不规则的时间间隔"""
        # 随机滚动距离
        scroll_choices = [
            (0.3, (100, 300)),    # 30% 小滚动
            (0.5, (300, 600)),    # 50% 中等滚动
            (0.2, (600, 1000))    # 20% 大滚动
        ]
        rand = random.random()
        cumulative = 0
        for prob, (min_s, max_s) in scroll_choices:
            cumulative += prob
            if rand < cumulative:
                scroll = random.randint(min_s, max_s)
                break

        # 分步滚动（人类不会一次滚动）- 每步间隔不同
        steps = random.choice([2, 2, 3, 3, 4, 5])  # 更倾向于2-3步
        scroll_per_step = scroll // steps

        for i in range(steps):
            # 每步滚动距离也略有变化
            variation = random.randint(-20, 20)
            page.evaluate(f"window.scrollBy({{top: {scroll_per_step + variation}, behavior: 'smooth'}})")
            # 每步之间的时间完全不同
            step_delays = [0.03, 0.05, 0.08, 0.1, 0.12, 0.15, 0.18, 0.2, 0.25]
            time.sleep(random.choice(step_delays))

        # 停顿"阅读"内容 - 完全随机
        reading_pauses = [0.5, 0.8, 1.0, 1.2, 1.5, 1.8, 2.0, 2.5, 3.0, 3.5]
        time.sleep(random.choice(reading_pauses))

        # 有时向上滚一点（像重新阅读）
        if random.random() < 0.15:
            scroll_back = random.randint(-200, -50)
            page.evaluate(f"window.scrollBy({{top: {scroll_back}, behavior: 'smooth'}})")
            back_delays = [0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0]
            time.sleep(random.choice(back_delays))

    def _random_pause(self):
        """偶尔停顿，模拟人类分心"""
        if random.random() < 0.1:  # 10%概率
            pause_type = random.choice(['short', 'medium'])
            if pause_type == 'short':
                time.sleep(random.uniform(2, 5))
                logger.info("      ⏸️  Quick pause...")
            else:
                time.sleep(random.uniform(5, 10))
                logger.info("      ⏸️  Short break...")

    def _start_browser(self):
        """启动Playwright浏览器"""
        if self.browser:
            return  # 已经启动

        logger.info("🚀 Starting browser for LinkedIn...")

        self.playwright = sync_playwright().start()

        # 尝试使用Firefox（更难被检测）
        try:
            logger.info("🦊 Trying Firefox browser for better stealth...")
            self.browser = self.playwright.firefox.launch(
                headless=False,  # 可见模式
                firefox_user_prefs={
                    "dom.webdriver.enabled": False,
                    "useAutomationExtension": False,
                    "general.platform.override": "MacIntel",
                    "general.useragent.override": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0"
                }
            )
        except Exception as e:
            logger.warning(f"   Firefox not available, falling back to Chromium: {e}")
            # Fallback to Chromium with enhanced anti-detection
            self.browser = self.playwright.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-automation',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )

        # 创建context - 根据认证方式选择
        if self.use_storage_state and self.storage_state_file:
            # 使用storage_state（推荐，类似Twitter）
            logger.info(f"🔐 Loading authentication from {self.storage_state_file}...")
            context = self.browser.new_context(
                storage_state=self.storage_state_file,
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='zh-CN',
                timezone_id='Asia/Shanghai',
                extra_http_headers={
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
            )
        else:
            # 使用cookies（旧方法）
            context = self.browser.new_context(
                user_agent=self.headers.get('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'),
                viewport={'width': 1920, 'height': 1080},
                locale='zh-CN',
                timezone_id='Asia/Shanghai',
                extra_http_headers={
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
            )

            # 设置cookies
            if self.cookies:
                context.add_cookies([
                    {
                        'name': 'li_at',
                        'value': self.cookies.get('li_at', ''),
                        'domain': '.linkedin.com',
                        'path': '/'
                    },
                    {
                        'name': 'JSESSIONID',
                        'value': self.cookies.get('JSESSIONID', ''),
                        'domain': '.linkedin.com',
                        'path': '/'
                    },
                    {
                        'name': 'liap',
                        'value': self.cookies.get('liap', 'true'),
                        'domain': '.linkedin.com',
                        'path': '/'
                    }
                ])

        self.page = context.new_page()

        # Inject anti-detection script (same as Twitter)
        self.page.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // Override plugins and languages
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en']
            });

            // Override chrome property
            window.chrome = {
                runtime: {}
            };

            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)

        logger.info("✅ Browser started with authentication")

    def _close_browser(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
            self.playwright.stop()
            self.browser = None
            self.playwright = None
            logger.info("🔒 Browser closed")

    def search_users(self, keywords: List[str], limit: int = 100) -> List[Dict]:
        """
        搜索LinkedIn用户

        Args:
            keywords: 搜索关键词
            limit: 结果数量

        Returns:
            用户列表
        """
        self._start_browser()

        # 构建搜索URL
        query = ' '.join(keywords)
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={query.replace(' ', '%20')}"

        logger.info(f"🔍 Searching LinkedIn: {query}")

        try:
            # 首先访问LinkedIn主页，确认登录状态
            logger.info("   Navigating to LinkedIn homepage...")
            self.page.goto("https://www.linkedin.com/feed/", timeout=60000, wait_until='domcontentloaded')

            # 人类行为：到达页面后的鼠标移动
            self._random_mouse_movement(self.page)
            self._human_like_delay(2, 4)

            # 检查是否需要重新登录
            if "login" in self.page.url or "authwall" in self.page.url:
                logger.error("❌ LinkedIn cookies expired - please run linkedin_login_and_save_auth.py")
                return []

            logger.info("   ✅ Successfully logged in")

            # 使用搜索框搜索（模拟真人）
            logger.info("   🔍 Using search box (human-like)...")

            try:
                # 找到搜索框
                search_box = self.page.query_selector('input[placeholder*="Search"]')
                if not search_box:
                    search_box = self.page.query_selector('.search-global-typeahead__input')

                if search_box:
                    # 人类行为：移动鼠标到搜索框附近
                    self._random_mouse_movement(self.page)
                    self._human_like_delay(0.5, 1.5)

                    # 点击搜索框
                    search_box.click()
                    self._human_like_delay(0.8, 1.8)

                    # 模拟逐字输入 - 每个字符的延迟都不同！
                    # 定义多种可能的延迟（毫秒）
                    typing_delays = [
                        30, 45, 60, 75, 80, 90, 100, 110, 120, 135,
                        150, 165, 180, 200, 220, 250, 280, 300, 350
                    ]

                    for i, char in enumerate(query):
                        # 每个字符选择不同的延迟
                        delay = random.choice(typing_delays)

                        # 偶尔打字更慢（思考/犹豫）
                        if random.random() < 0.15:  # 15%概率
                            delay = random.randint(300, 600)

                        # 空格前后通常稍慢
                        if char == ' ' or (i > 0 and query[i-1] == ' '):
                            delay = random.randint(150, 350)

                        search_box.type(char, delay=delay)

                    self._human_like_delay(0.5, 1.2)
                    search_box.press('Enter')
                    self._human_like_delay(2, 3)

                    # 点击"People"标签
                    logger.info("   Clicking on People tab...")
                    people_button = self.page.query_selector('button:has-text("People")')
                    if not people_button:
                        people_button = self.page.query_selector('[aria-label="People"]')

                    if people_button:
                        # 人类行为：移动鼠标后再点击
                        self._random_mouse_movement(self.page)
                        self._human_like_delay(0.5, 1)
                        people_button.click()
                        self._human_like_delay(2, 4)
                    else:
                        logger.warning("   Could not find People tab, continuing anyway...")
                else:
                    logger.warning("   Could not find search box, trying direct URL...")
                    # 如果找不到搜索框，尝试直接URL
                    self.page.goto(search_url, timeout=60000, wait_until='domcontentloaded')
                    self._human_like_delay(3, 5)

            except Exception as e:
                logger.warning(f"   Search box method failed: {e}, trying direct URL...")
                self.page.goto(search_url, timeout=60000, wait_until='domcontentloaded')
                self._human_like_delay(3, 5)

            # 等待搜索结果加载
            logger.info("   ⏳ Waiting for search results...")
            self._random_mouse_movement(self.page)
            self._human_like_delay(2, 4)

            # 检查是否出现错误页面 (LinkedIn sometimes shows error page)
            max_retries = 3
            for retry in range(max_retries):
                page_text = self.page.inner_text('body')
                if "This one's our fault" in page_text or "We're looking into it" in page_text:
                    logger.warning(f"   ⚠️  LinkedIn error page detected (attempt {retry + 1}/{max_retries})")

                    # 尝试点击"Retry search"按钮
                    retry_button = self.page.query_selector('button:has-text("Retry search")')
                    if retry_button:
                        logger.info("   🔄 Clicking 'Retry search' button...")
                        self._random_mouse_movement(self.page)
                        self._human_like_delay(0.5, 1)
                        retry_button.click()
                        self._human_like_delay(3, 5)

                        # 重新等待搜索结果
                        self._human_like_delay(2, 3)
                        continue
                    else:
                        # 如果没有重试按钮，尝试刷新页面
                        logger.info("   🔄 Refreshing page...")
                        self.page.reload()
                        self._human_like_delay(3, 5)
                        continue
                else:
                    # 没有错误，继续
                    break

            # 调试：保存截图和页面HTML
            try:
                self.page.screenshot(path='linkedin_search_debug.png')
                logger.info("   📸 Screenshot saved")

                # 保存HTML用于调试DOM结构
                html_content = self.page.content()
                with open('linkedin_search_debug.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info("   📄 HTML saved for debugging")
            except Exception as e:
                logger.debug(f"   Could not save debug files: {e}")

        except Exception as e:
            logger.error(f"❌ Error navigating to search page: {e}")
            logger.warning("⚠️  This might be due to:")
            logger.warning("   1. Expired cookies - update platforms_auth.json")
            logger.warning("   2. LinkedIn rate limiting - wait a few minutes")
            logger.warning("   3. Network issues - check your connection")
            return []

        users = []
        scroll_attempts = 0
        max_scrolls = limit // 10  # 每次滚动大约加载10个结果

        while len(users) < limit and scroll_attempts < max_scrolls:
            # 人类行为：偶尔分心停顿
            self._random_pause()

            # 尝试多个选择器（LinkedIn经常改变DOM结构）
            # 根据最新的LinkedIn界面更新选择器
            user_cards = self.page.query_selector_all('li.reusable-search__result-container')

            if not user_cards:
                # 尝试更通用的选择器
                user_cards = self.page.query_selector_all('.search-results-container li')

            if not user_cards:
                # 尝试另一个常见选择器
                user_cards = self.page.query_selector_all('[data-chameleon-result-urn]')

            if not user_cards:
                # 最通用的选择器
                user_cards = self.page.query_selector_all('ul.reusable-search__entity-result-list > li')

            logger.info(f"   Found {len(user_cards)} user cards on page")

            # 如果还是找不到，打印页面HTML帮助调试
            if not user_cards and scroll_attempts == 0:
                logger.warning("   ⚠️  Could not find user cards, checking page structure...")
                # 尝试查找People section
                people_section = self.page.query_selector('.search-results-container')
                if people_section:
                    logger.info("   ✓ Found search results container")
                else:
                    logger.warning("   ✗ No search results container found")

            for card in user_cards[len(users):]:  # 只处理新的卡片
                try:
                    # 人类行为：处理每个卡片之间有小延迟 - 完全随机
                    if random.random() < 0.3:  # 30%概率移动鼠标
                        self._random_mouse_movement(self.page)

                    # 提取用户信息 - 尝试多个选择器
                    name_elem = card.query_selector('.entity-result__title-text a')
                    if not name_elem:
                        name_elem = card.query_selector('a.app-aware-link')
                    if not name_elem:
                        name_elem = card.query_selector('.entity-result__title-line a')

                    headline_elem = card.query_selector('.entity-result__primary-subtitle')
                    if not headline_elem:
                        headline_elem = card.query_selector('.entity-result__summary')

                    location_elem = card.query_selector('.entity-result__secondary-subtitle')
                    if not location_elem:
                        location_elem = card.query_selector('.entity-result__location')

                    if name_elem:
                        profile_url = name_elem.get_attribute('href')
                        # 清理profile URL（移除查询参数）
                        if profile_url and '?' in profile_url:
                            profile_url = profile_url.split('?')[0]

                        user = {
                            'name': name_elem.inner_text().strip(),
                            'profile_url': profile_url or '',
                            'headline': headline_elem.inner_text().strip() if headline_elem else '',
                            'location': location_elem.inner_text().strip() if location_elem else '',
                            'platform': 'linkedin'
                        }
                        users.append(user)
                        logger.debug(f"   Added user: {user['name']}")

                        # 人类行为：提取信息后稍微停顿 - 每次都不同
                        card_delays = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.5]
                        time.sleep(random.choice(card_delays))

                        if len(users) >= limit:
                            break

                except Exception as e:
                    logger.debug(f"Error extracting user card: {e}")
                    continue

            # 滚动加载更多（使用人类式滚动）
            if len(users) < limit:
                logger.info(f"   📜 Scrolling for more results... (attempt {scroll_attempts + 1})")
                self._human_scroll(self.page)  # 使用人类式滚动
                scroll_attempts += 1

        logger.info(f"✅ Found {len(users)} users on LinkedIn")
        return users[:limit]

    def get_user_profile(self, user_id: str) -> Dict:
        """
        获取LinkedIn用户详细资料

        Args:
            user_id: 用户profile URL

        Returns:
            用户详细资料
        """
        if not self.browser:
            self._start_browser()

        # user_id 实际上是profile URL
        profile_url = user_id if user_id.startswith('http') else f"https://www.linkedin.com/in/{user_id}"

        logger.debug(f"📖 Fetching profile: {profile_url}")

        try:
            self.page.goto(profile_url, timeout=60000, wait_until='domcontentloaded')

            # 人类行为：到达页面后的鼠标移动和延迟
            self._random_mouse_movement(self.page)
            self._human_like_delay(1.5, 3)

            # 人类行为：滚动查看页面（像阅读资料）
            if random.random() < 0.7:  # 70%概率滚动
                self._human_scroll(self.page)

        except Exception as e:
            logger.warning(f"⚠️  Error loading profile {profile_url}: {e}")
            return {
                'profile_url': profile_url,
                'platform': 'linkedin'
            }

        # 提取详细信息
        profile = {
            'profile_url': profile_url,
            'platform': 'linkedin'
        }

        try:
            # 姓名
            name_elem = self.page.query_selector('h1.text-heading-xlarge')
            if name_elem:
                profile['name'] = name_elem.inner_text().strip()

            # 标题/职位
            headline_elem = self.page.query_selector('.text-body-medium')
            if headline_elem:
                profile['headline'] = headline_elem.inner_text().strip()
                profile['job_title'] = headline_elem.inner_text().strip()

            # 地点
            location_elem = self.page.query_selector('.text-body-small.inline.t-black--light.break-words')
            if location_elem:
                profile['location'] = location_elem.inner_text().strip()

            # 关于/简介
            about_elem = self.page.query_selector('#about ~ .pvs-list__outer-container')
            if about_elem:
                profile['bio'] = about_elem.inner_text().strip()[:500]

            # 当前公司（从经验部分提取）
            experience_elem = self.page.query_selector('#experience ~ .pvs-list__outer-container li')
            if experience_elem:
                company_elem = experience_elem.query_selector('.t-bold span')
                if company_elem:
                    profile['company'] = company_elem.inner_text().strip()

        except Exception as e:
            logger.warning(f"⚠️  Error extracting profile details: {e}")

        return profile

    def extract_email(self, user_profile: Dict) -> Optional[str]:
        """
        从LinkedIn资料提取邮箱

        LinkedIn通常不公开邮箱，需要：
        1. 点击"Contact Info"
        2. 或从公司域名 + Hunter.io推断

        Args:
            user_profile: 用户资料

        Returns:
            邮箱地址或None
        """
        # LinkedIn通常不公开邮箱
        # 我们返回None，让Hunter.io从公司域名推断
        return None

    def get_company_employees(self, company_name: str, limit: int = 50) -> List[Dict]:
        """
        获取公司员工列表

        Args:
            company_name: 公司名称
            limit: 数量限制

        Returns:
            员工列表
        """
        keywords = [company_name, "recruiter"]  # 搜索该公司的招聘人员
        return self.search_users(keywords, limit)

    def __del__(self):
        """析构函数 - 清理资源"""
        self._close_browser()


# 测试代码
if __name__ == "__main__":
    scraper = LinkedInScraper()

    # 测试搜索
    test_keywords = ["recruiter", "hiring manager", "tech"]
    users = scraper.search_users(test_keywords, limit=5)

    print(f"\n✅ Found {len(users)} users:")
    for user in users:
        print(f"  - {user['name']} | {user.get('headline', 'N/A')}")

    # 测试获取详情
    if users:
        profile = scraper.get_user_profile(users[0]['profile_url'])
        print(f"\n📖 Profile details:")
        print(f"  Name: {profile.get('name')}")
        print(f"  Title: {profile.get('job_title')}")
        print(f"  Company: {profile.get('company')}")
        print(f"  Location: {profile.get('location')}")

    scraper._close_browser()
