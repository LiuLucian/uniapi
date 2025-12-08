"""
TikTok Scraper - TikTok爬虫
使用Playwright + cookie登录爬取（参考Twitter scraper）
"""

import json
import time
import logging
import random
import re
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Page, Browser
from src.platform_scraper_base import PlatformScraperBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TikTokScraper(PlatformScraperBase):
    """TikTok平台scraper - 使用Playwright爬取"""

    def __init__(self, auth_file: str = "platforms_auth.json"):
        """
        初始化TikTok scraper

        Args:
            auth_file: 认证配置文件路径
        """
        try:
            with open(auth_file, 'r') as f:
                config = json.load(f)
            auth_config = config.get('tiktok', {})
        except FileNotFoundError:
            logger.error(f"❌ Auth file {auth_file} not found")
            auth_config = {}

        super().__init__(auth_config, 'TikTok')

        # TikTok配置
        self.sessionid = self.auth_config.get('sessionid', '')
        self.msToken = self.auth_config.get('msToken', '')
        self.base_url = "https://www.tiktok.com"

        # Playwright相关
        self.playwright = None
        self.browser = None
        self.context = None

    def _setup_browser(self):
        """设置Playwright浏览器（带cookies）"""
        if not self.playwright:
            self.playwright = sync_playwright().start()

            # 使用Chromium（类似Chrome）
            self.browser = self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )

            # 创建context并添加cookies
            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )

            # 添加cookies
            if self.sessionid:
                self.context.add_cookies([
                    {
                        'name': 'sessionid',
                        'value': self.sessionid,
                        'domain': '.tiktok.com',
                        'path': '/'
                    },
                    {
                        'name': 'msToken',
                        'value': self.msToken,
                        'domain': '.tiktok.com',
                        'path': '/'
                    }
                ])

            logger.info("✅ TikTok browser initialized with cookies")

    def _human_delay(self, min_sec: float = 1.0, max_sec: float = 3.0):
        """模拟人类延迟"""
        time.sleep(random.uniform(min_sec, max_sec))

    def search_users(self, keywords: List[str], limit: int = 100) -> List[Dict]:
        """
        搜索TikTok用户（创作者）- 使用Playwright爬取

        策略：
        1. 用cookie登录TikTok
        2. 搜索关键词
        3. 从搜索结果提取用户

        Args:
            keywords: 搜索关键词
            limit: 结果数量

        Returns:
            用户列表
        """
        if not self.sessionid:
            logger.error("❌ TikTok session required")
            return []

        logger.info(f"🔍 Searching TikTok for creators (limit: {limit})")

        users = []
        seen_usernames = set()

        try:
            # 设置浏览器
            self._setup_browser()
            page = self.context.new_page()

            query = ' '.join(keywords) if keywords else 'startup'

            # 访问搜索页面
            search_url = f"https://www.tiktok.com/search/user?q={query}"
            logger.info(f"   Navigating to: {search_url}")
            page.goto(search_url, wait_until='domcontentloaded', timeout=60000)

            self._human_delay(3, 5)

            # 滚动加载更多用户
            for scroll in range(min(10, limit // 2)):
                # 查找所有用户链接
                user_links = page.query_selector_all('a[href*="/@"]')

                logger.info(f"   Found {len(user_links)} user links on page (scroll {scroll + 1})")

                for link in user_links:
                    if len(users) >= limit:
                        break

                    try:
                        href = link.get_attribute('href')
                        if not href or '/@' not in href:
                            continue

                        username = href.split('/@')[-1].split('?')[0].split('/')[0]

                        if not username or username in seen_usernames:
                            continue

                        # 简化版：只提取基本信息
                        user = {
                            'user_id': username,
                            'username': username,
                            'nickname': username,  # 稍后可以访问profile页面获取
                            'signature': "",
                            'profile_url': f"https://www.tiktok.com/@{username}",
                            'follower_count': 0,  # 稍后可以访问profile页面获取
                            'platform': 'tiktok'
                        }

                        users.append(user)
                        seen_usernames.add(username)
                        logger.info(f"   ✓ Found: @{username}")

                    except Exception as e:
                        logger.debug(f"   Error extracting username: {e}")
                        continue

                # 滚动加载更多
                if len(users) < limit:
                    page.evaluate("window.scrollBy(0, 1000)")
                    self._human_delay(2, 4)

            page.close()
            logger.info(f"✅ Found {len(users)} creators on TikTok")
            return users[:limit]

        except Exception as e:
            logger.error(f"❌ Error searching TikTok: {e}")
            import traceback
            traceback.print_exc()
            return users

        finally:
            # 清理资源
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()

    def _parse_count(self, count_str: str) -> int:
        """解析粉丝数（处理 K、M 等单位）"""
        count_str = count_str.strip().replace(',', '')

        if 'K' in count_str.upper():
            return int(float(count_str.replace('K', '').replace('k', '')) * 1000)
        elif 'M' in count_str.upper():
            return int(float(count_str.replace('M', '').replace('m', '')) * 1000000)
        else:
            try:
                return int(count_str)
            except:
                return 0

    def get_user_profile(self, user_id: str) -> Dict:
        """
        获取TikTok用户详细资料

        Args:
            user_id: 用户名

        Returns:
            用户详细资料
        """
        logger.debug(f"📖 Fetching TikTok profile: {user_id}")

        if not self.sessionid:
            return {
                'username': user_id,
                'profile_url': f"https://www.tiktok.com/@{user_id}",
                'platform': 'tiktok',
                'status': 'no_session'
            }

        try:
            # TikTok的用户API
            user_url = f"{self.api_url}/user/detail/"
            params = {'uniqueId': user_id}

            response = requests.get(
                user_url,
                params=params,
                headers=self.headers,
                cookies=self.cookies,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                user_info = data.get('userInfo', {}).get('user', {})

                return {
                    'user_id': user_info.get('id'),
                    'username': user_id,
                    'nickname': user_info.get('nickname', ''),
                    'signature': user_info.get('signature', ''),
                    'profile_url': f"https://www.tiktok.com/@{user_id}",
                    'follower_count': user_info.get('followerCount', 0),
                    'following_count': user_info.get('followingCount', 0),
                    'video_count': user_info.get('videoCount', 0),
                    'platform': 'tiktok'
                }

        except Exception as e:
            logger.debug(f"   Error fetching profile: {e}")

        return {
            'username': user_id,
            'profile_url': f"https://www.tiktok.com/@{user_id}",
            'platform': 'tiktok',
            'status': 'not_found'
        }

    def extract_email(self, user_profile: Dict) -> Optional[str]:
        """
        从TikTok资料提取邮箱

        TikTok有时在signature中包含联系信息

        Args:
            user_profile: 用户资料

        Returns:
            邮箱地址或None
        """
        signature = user_profile.get('signature', '')

        if signature:
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            matches = re.findall(email_pattern, signature)

            if matches:
                return matches[0]

        return None

    def search_hashtag_videos(self, hashtag: str, limit: int = 20) -> List[Dict]:
        """
        搜索特定hashtag的视频

        Args:
            hashtag: hashtag名称（不含#）
            limit: 数量限制

        Returns:
            视频列表
        """
        if not self.sessionid:
            logger.error("❌ TikTok session required")
            return []

        videos = []

        try:
            search_url = f"{self.api_url}/challenge/item_list/"
            params = {
                'challengeID': hashtag,
                'count': limit
            }

            response = requests.get(
                search_url,
                params=params,
                headers=self.headers,
                cookies=self.cookies,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                logger.info(f"   Found videos for #{hashtag}")

        except Exception as e:
            logger.debug(f"   Error searching hashtag: {e}")

        return videos


# 测试代码
if __name__ == "__main__":
    scraper = TikTokScraper()

    # 测试搜索用户
    users = scraper.search_users(["startup"], limit=10)

    print(f"\n✅ Found {len(users)} users:")
    for user in users:
        print(f"  - @{user.get('username')} ({user.get('follower_count', 0)} followers)")
        print(f"    Signature: {user.get('signature', '')[:100]}")
