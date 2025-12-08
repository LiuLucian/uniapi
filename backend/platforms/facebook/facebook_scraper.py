"""
Facebook Scraper - 完整版
参照Reddit/Twitter模式：搜索关键词 → 找帖子 → 抓用户
"""

import json
import time
import random
import logging
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright
from src.platform_scraper_base import PlatformScraperBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FacebookScraper(PlatformScraperBase):
    """Facebook爬虫 - 搜索帖子并抓取互动用户"""

    def __init__(self, auth_file: str = "platforms_auth.json"):
        """初始化"""
        with open(auth_file, 'r') as f:
            config = json.load(f)

        super().__init__(config.get('facebook', {}), 'Facebook')
        self.cookies = self.auth_config.get('cookies', {})

        self.playwright = None
        self.browser = None
        self.page = None

    def _start_browser(self):
        """启动浏览器（带反检测）"""
        if self.browser:
            return

        logger.info("🚀 Starting Facebook browser...")

        self.playwright = sync_playwright().start()

        # 使用更好的反检测设置
        self.browser = self.playwright.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )

        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/Los_Angeles',
        )

        # 隐藏webdriver特征
        self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        # 加载cookies
        if self.cookies:
            cookies_list = [{
                'name': name,
                'value': value,
                'domain': '.facebook.com',
                'path': '/'
            } for name, value in self.cookies.items()]
            self.context.add_cookies(cookies_list)

        self.page = self.context.new_page()
        logger.info("✅ Browser started")

    def _close_browser(self):
        """关闭浏览器"""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("🔒 Browser closed")
        except Exception as e:
            # 忽略关闭时的错误
            pass

    def search_posts_from_groups(self, group_ids: List[str], max_posts_per_group: int = 10) -> List[Dict]:
        """
        从Facebook群组获取帖子（避开搜索页面的崩溃问题）

        Args:
            group_ids: 群组ID列表或群组名称列表
            max_posts_per_group: 每个群组最多抓取帖子数

        Returns:
            帖子列表，每个包含 {url, author, group}
        """
        self._start_browser()

        logger.info(f"🔍 Fetching posts from {len(group_ids)} Facebook groups...")

        all_posts = []

        for group_id in group_ids:
            logger.info(f"\n📌 Group: {group_id}")

            try:
                # 访问群组页面
                group_url = f"https://www.facebook.com/groups/{group_id}"
                self.page.goto(group_url, wait_until='domcontentloaded', timeout=60000)
                time.sleep(random.uniform(3, 5))

                # 检查登录
                if "login" in self.page.url:
                    logger.error("❌ Not logged in")
                    continue

                # 滚动加载帖子
                logger.info("   📜 Loading posts...")
                for _ in range(3):
                    self.page.evaluate("window.scrollBy(0, 800)")
                    time.sleep(random.uniform(1, 2))

                # 查找帖子链接
                posts_in_group = []
                seen_urls = set()

                # Facebook群组帖子链接模式
                post_link_selectors = [
                    'a[href*="/posts/"]',
                    'a[href*="/permalink/"]',
                ]

                for selector in post_link_selectors:
                    try:
                        links = self.page.query_selector_all(selector)

                        for link in links:
                            if len(posts_in_group) >= max_posts_per_group:
                                break

                            href = link.get_attribute('href')
                            if not href:
                                continue

                            # 补全URL
                            if href.startswith('/'):
                                href = f'https://www.facebook.com{href}'

                            # 去重
                            if href in seen_urls:
                                continue

                            # 只要群组内的帖子
                            if f'/groups/{group_id}' in href and '/posts/' in href:
                                seen_urls.add(href)

                                posts_in_group.append({
                                    'url': href,
                                    'author': 'Unknown',  # 可以后续提取
                                    'group_id': group_id,
                                    'platform': 'facebook'
                                })

                    except Exception as e:
                        logger.debug(f"   Error with selector {selector}: {e}")
                        continue

                logger.info(f"   ✅ Found {len(posts_in_group)} posts in group")
                all_posts.extend(posts_in_group)

                # 群组间延迟
                time.sleep(random.uniform(2, 4))

            except Exception as e:
                logger.error(f"   ❌ Error: {e}")
                continue

        logger.info(f"\n✅ Total: {len(all_posts)} posts from {len(group_ids)} groups")
        return all_posts

    def get_post_comments(self, post_url: str, max_comments: int = 50) -> List[Dict]:
        """
        从Facebook帖子抓评论（核心功能2）

        Args:
            post_url: 帖子URL
            max_comments: 最多抓取评论数

        Returns:
            评论列表，每个包含 {username, text, profile_url}
        """
        self._start_browser()

        logger.info(f"📖 Scraping comments from post...")
        logger.info(f"   URL: {post_url}")

        try:
            # 访问帖子（使用domcontentloaded避免crash）
            self.page.goto(post_url, wait_until='domcontentloaded', timeout=60000)
            time.sleep(random.uniform(3, 5))

            # 检查登录
            if "login" in self.page.url:
                logger.error("❌ Not logged in")
                return []

            # 点击"View more comments"按钮
            logger.info("   🔽 Expanding comments...")
            for _ in range(3):
                try:
                    more_selectors = [
                        'div[role="button"]:has-text("View more comments")',
                        'div[role="button"]:has-text("查看更多评论")',
                        'span:has-text("View more comments")',
                    ]

                    for selector in more_selectors:
                        try:
                            more_btn = self.page.query_selector(selector)
                            if more_btn:
                                more_btn.click()
                                time.sleep(random.uniform(1, 2))
                                break
                        except:
                            continue
                except:
                    break

            # 滚动加载评论
            logger.info("   📜 Scrolling to load comments...")
            for _ in range(5):
                self.page.evaluate("window.scrollBy(0, 500)")
                time.sleep(random.uniform(0.5, 1))

            # 抓取评论
            comments = []
            seen = set()

            # Facebook评论通常在 div[role="article"] 中
            comment_elements = self.page.query_selector_all('div[role="article"]')

            logger.info(f"   Found {len(comment_elements)} potential comments")

            for elem in comment_elements[:max_comments * 2]:  # 多抓一些，去重后再限制
                try:
                    # 提取用户名和链接
                    author_link = elem.query_selector('a[role="link"]')
                    if not author_link:
                        continue

                    username = author_link.inner_text().strip()
                    profile_url = author_link.get_attribute('href') or ''

                    # 补全profile URL
                    if profile_url and profile_url.startswith('/'):
                        profile_url = f'https://www.facebook.com{profile_url}'

                    # 提取评论文本
                    text_elem = elem.query_selector('div[dir="auto"]')
                    if not text_elem:
                        continue

                    text = text_elem.inner_text().strip()

                    # 去重并过滤
                    if username and text and len(text) > 10 and username not in seen:
                        comments.append({
                            'username': username,
                            'text': text,
                            'profile_url': profile_url,
                            'platform': 'facebook',
                            'post_url': post_url
                        })
                        seen.add(username)

                        if len(comments) >= max_comments:
                            break

                except Exception as e:
                    logger.debug(f"Error extracting comment: {e}")
                    continue

            logger.info(f"✅ Extracted {len(comments)} comments")
            return comments

        except Exception as e:
            logger.error(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return []

    def search_users(self, group_ids: List[str], limit: int = 100) -> List[Dict]:
        """
        完整流程：访问群组 → 找帖子 → 抓用户
        （避开搜索页面，改用群组）

        Args:
            group_ids: Facebook群组ID列表（例如 ["jobsearch", "careeradvice"]）
            limit: 目标用户数量

        Returns:
            用户列表（从评论中提取）
        """
        logger.info(f"\n🔍 Starting Facebook user search...")
        logger.info(f"   Groups: {', '.join(group_ids)}")
        logger.info(f"   Target: {limit} users")

        all_users = []
        seen_usernames = set()

        # Step 1: 从群组获取帖子
        posts = self.search_posts_from_groups(group_ids, max_posts_per_group=5)

        if not posts:
            logger.warning("   ⚠️  No posts found in groups")
            return []

        logger.info(f"\n✅ Found {len(posts)} posts, now extracting users...")

        # Step 2: 从每个帖子抓取用户
        for i, post in enumerate(posts, 1):
            if len(all_users) >= limit:
                break

            logger.info(f"\n   [{i}/{len(posts)}] Post: {post['url'][:60]}...")

            try:
                # 抓取评论（得到用户）
                comments = self.get_post_comments(post['url'], max_comments=30)

                # 转换评论为用户格式
                for comment in comments:
                    username = comment['username']

                    if username in seen_usernames:
                        continue

                    seen_usernames.add(username)

                    # 构造用户数据
                    user = {
                        'username': username,
                        'profile_url': comment.get('profile_url', ''),
                        'bio': comment.get('text', '')[:200],  # 用评论作为bio
                        'platform': 'facebook',
                        'found_via': f"Comment in group {post.get('group_id', 'unknown')}",
                        'comment_text': comment.get('text', ''),
                        'post_url': post['url']
                    }

                    all_users.append(user)

                    if len(all_users) >= limit:
                        break

            except Exception as e:
                logger.error(f"   ❌ Error: {e}")
                continue

            # 帖子间延迟
            if i < len(posts):
                time.sleep(random.uniform(2, 4))

        logger.info(f"\n✅ Total users found: {len(all_users)}")
        return all_users[:limit]

    def get_user_profile(self, user_id: str) -> Dict:
        """
        获取用户详细资料（抽象方法实现）
        注：Facebook DM系统不需要此功能，仅为满足基类要求
        """
        logger.warning("⚠️  get_user_profile not implemented for Facebook DM system")
        return {}

    def extract_email(self, user_profile: Dict) -> Optional[str]:
        """
        从用户资料中提取邮箱（抽象方法实现）
        注：Facebook DM系统不需要此功能，仅为满足基类要求
        """
        logger.warning("⚠️  extract_email not implemented for Facebook DM system")
        return None

    def __del__(self):
        """清理"""
        self._close_browser()


if __name__ == "__main__":
    scraper = FacebookScraper()

    # 测试1: 搜索帖子
    print("\n" + "="*70)
    print("Test 1: Search Posts")
    print("="*70)

    posts = scraper.search_posts("job interview tips", max_posts=3)
    for i, post in enumerate(posts, 1):
        print(f"\n[{i}] Author: {post['author']}")
        print(f"    URL: {post['url']}")

    # 测试2: 完整流程 - 搜索用户
    print("\n" + "="*70)
    print("Test 2: Search Users (Full Pipeline)")
    print("="*70)

    users = scraper.search_users(
        keywords=["interview preparation", "career advice"],
        limit=20
    )

    for i, user in enumerate(users, 1):
        print(f"\n[{i}] {user['username']}")
        print(f"    Profile: {user['profile_url']}")
        print(f"    Comment: {user['comment_text'][:100]}...")

    scraper._close_browser()
