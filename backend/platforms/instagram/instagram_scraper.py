"""
Instagram Scraper - Instagram爬虫
使用session cookie访问Instagram数据
"""

import json
import time
import logging
import requests
from typing import List, Dict, Optional
from src.platform_scraper_base import PlatformScraperBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InstagramScraper(PlatformScraperBase):
    """Instagram平台scraper"""

    def __init__(self, auth_file: str = "platforms_auth.json"):
        """
        初始化Instagram scraper

        Args:
            auth_file: 认证配置文件路径
        """
        try:
            with open(auth_file, 'r') as f:
                config = json.load(f)
            auth_config = config.get('instagram', {})
        except FileNotFoundError:
            logger.error(f"❌ Auth file {auth_file} not found")
            auth_config = {}

        super().__init__(auth_config, 'Instagram')

        # Instagram配置
        self.sessionid = self.auth_config.get('sessionid', '')
        self.base_url = "https://www.instagram.com"
        self.api_url = "https://www.instagram.com/api/v1"

        # 设置headers和cookies
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'X-IG-App-ID': '936619743392459',
            'X-Requested-With': 'XMLHttpRequest'
        }

        self.cookies = {
            'sessionid': self.sessionid
        }

    def search_users(self, keywords: List[str], limit: int = 100) -> List[Dict]:
        """
        搜索Instagram用户

        策略：
        1. 搜索hashtag相关的帖子
        2. 获取帖子作者
        3. 筛选活跃创作者

        Args:
            keywords: 搜索关键词（hashtag）
            limit: 结果数量

        Returns:
            用户列表
        """
        if not self.sessionid:
            logger.error("❌ Instagram session required")
            return []

        logger.info(f"🔍 Searching Instagram for creators (limit: {limit})")

        users = []
        seen_usernames = set()

        try:
            # 使用hashtag搜索
            query = keywords[0] if keywords else 'startup'

            # Instagram的搜索API
            search_url = f"{self.base_url}/web/search/topsearch/"
            params = {
                'query': query,
                'context': 'blended'
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
                results = data.get('users', [])

                logger.info(f"   Found {len(results)} users from search")

                for result in results[:limit]:
                    user_data = result.get('user', {})
                    username = user_data.get('username')

                    if username and username not in seen_usernames:
                        # 获取用户详细信息
                        profile = self._get_user_profile(username)
                        if profile and profile.get('follower_count', 0) >= 1000:
                            users.append(profile)
                            seen_usernames.add(username)

                    time.sleep(1)  # Rate limiting

                    if len(users) >= limit:
                        break

            elif response.status_code == 401:
                logger.error("❌ Instagram session expired - please update sessionid")
            else:
                logger.warning(f"   ⚠️  Search failed: {response.status_code}")

        except Exception as e:
            logger.error(f"❌ Error searching Instagram: {e}")

        logger.info(f"✅ Found {len(users)} creators on Instagram")
        return users[:limit]

    def _get_user_profile(self, username: str) -> Optional[Dict]:
        """
        获取用户详细信息

        Args:
            username: Instagram用户名

        Returns:
            用户数据字典
        """
        try:
            # 使用Instagram的公开API
            profile_url = f"{self.base_url}/api/v1/users/web_profile_info/"
            params = {'username': username}

            response = requests.get(
                profile_url,
                params=params,
                headers=self.headers,
                cookies=self.cookies,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                user_data = data.get('data', {}).get('user', {})

                return {
                    'user_id': user_data.get('id'),
                    'username': username,
                    'full_name': user_data.get('full_name', ''),
                    'biography': user_data.get('biography', '')[:500],
                    'profile_url': f"https://www.instagram.com/{username}/",
                    'follower_count': user_data.get('edge_followed_by', {}).get('count', 0),
                    'following_count': user_data.get('edge_follow', {}).get('count', 0),
                    'post_count': user_data.get('edge_owner_to_timeline_media', {}).get('count', 0),
                    'is_business': user_data.get('is_business_account', False),
                    'is_verified': user_data.get('is_verified', False),
                    'external_url': user_data.get('external_url', ''),
                    'platform': 'instagram'
                }

        except Exception as e:
            logger.debug(f"   Error getting profile {username}: {e}")
            return None

    def get_user_profile(self, user_id: str) -> Dict:
        """
        获取Instagram用户详细资料

        Args:
            user_id: 用户名

        Returns:
            用户详细资料
        """
        logger.debug(f"📖 Fetching Instagram profile: {user_id}")

        profile = self._get_user_profile(user_id)

        if profile:
            return profile
        else:
            return {
                'username': user_id,
                'profile_url': f"https://www.instagram.com/{user_id}/",
                'platform': 'instagram',
                'status': 'not_found'
            }

    def extract_email(self, user_profile: Dict) -> Optional[str]:
        """
        从Instagram资料提取邮箱

        Instagram有时在biography或external_url中包含联系信息

        Args:
            user_profile: 用户资料

        Returns:
            邮箱地址或None
        """
        # 从biography中提取邮箱
        bio = user_profile.get('biography', '')

        if bio:
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            matches = re.findall(email_pattern, bio)

            if matches:
                return matches[0]

        # 检查external_url
        external_url = user_profile.get('external_url', '')
        if external_url and '@' in external_url:
            # 有时URL中包含邮箱
            import re
            matches = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', external_url)
            if matches:
                return matches[0]

        return None

    def search_hashtag_posts(self, hashtag: str, limit: int = 20) -> List[Dict]:
        """
        搜索特定hashtag的帖子

        Args:
            hashtag: hashtag名称（不含#）
            limit: 数量限制

        Returns:
            帖子列表
        """
        if not self.sessionid:
            logger.error("❌ Instagram session required")
            return []

        posts = []

        try:
            # Instagram的hashtag endpoint
            tag_url = f"{self.base_url}/explore/tags/{hashtag}/"

            response = requests.get(
                tag_url,
                headers=self.headers,
                cookies=self.cookies,
                params={'__a': '1'},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                # 解析帖子数据
                logger.info(f"   Found posts for #{hashtag}")

        except Exception as e:
            logger.debug(f"   Error searching hashtag: {e}")

        return posts


# 测试代码
if __name__ == "__main__":
    scraper = InstagramScraper()

    # 测试搜索用户
    users = scraper.search_users(["startup"], limit=10)

    print(f"\n✅ Found {len(users)} users:")
    for user in users:
        print(f"  - @{user.get('username')} ({user.get('follower_count', 0)} followers)")
        print(f"    Bio: {user.get('biography', '')[:100]}")
