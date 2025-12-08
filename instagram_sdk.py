"""
Instagram API SDK
官方风格的 Instagram API 客户端库

使用示例:
    from instagram_sdk import InstagramAPI

    api = InstagramAPI()

    # 点赞
    api.like_post("https://www.instagram.com/p/ABC123/")

    # 关注
    api.follow("username")

    # 评论
    api.comment("https://www.instagram.com/p/ABC123/", "Great!")

    # 获取用户帖子
    posts = api.get_user_posts("username", limit=10)
"""

import requests
import time
import random
from typing import List, Dict, Optional, Union
from urllib.parse import urlparse


class InstagramAPIError(Exception):
    """Instagram API 错误"""
    pass


class RateLimitError(InstagramAPIError):
    """速率限制错误"""
    pass


class AuthenticationError(InstagramAPIError):
    """认证错误"""
    pass


class InstagramAPI:
    """
    Instagram API 客户端

    支持所有 Instagram 官方 API 功能，以及扩展的自动化功能。
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/api/v1/instagram",
        timeout: int = 60,
        auto_delay: bool = True,
        min_delay: float = 3.0,
        max_delay: float = 8.0
    ):
        """
        初始化 Instagram API 客户端

        Args:
            base_url: API 基础URL
            timeout: 请求超时时间（秒）
            auto_delay: 是否自动添加延迟（防止速率限制）
            min_delay: 最小延迟时间（秒）
            max_delay: 最大延迟时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.auto_delay = auto_delay
        self.min_delay = min_delay
        self.max_delay = max_delay
        self._last_request_time = 0

    def _wait_if_needed(self):
        """根据设置添加延迟"""
        if not self.auto_delay:
            return

        elapsed = time.time() - self._last_request_time
        if elapsed < self.min_delay:
            delay = random.uniform(self.min_delay, self.max_delay)
            time.sleep(delay)

        self._last_request_time = time.time()

    def _extract_media_id(self, url_or_id: str) -> str:
        """从 URL 提取 media_id"""
        if '/p/' in url_or_id or '/reel/' in url_or_id:
            parts = url_or_id.split('/')
            for i, part in enumerate(parts):
                if part in ('p', 'reel') and i + 1 < len(parts):
                    return parts[i + 1].rstrip('/')
        return url_or_id

    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict:
        """发送 HTTP 请求"""
        self._wait_if_needed()

        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(
                method,
                url,
                timeout=self.timeout,
                **kwargs
            )

            data = response.json()

            if response.status_code == 200:
                return data
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code in (401, 403):
                raise AuthenticationError("Authentication failed")
            else:
                error_msg = data.get('error', data.get('message', 'Unknown error'))
                raise InstagramAPIError(f"API Error: {error_msg}")

        except requests.exceptions.Timeout:
            raise InstagramAPIError("Request timeout")
        except requests.exceptions.ConnectionError:
            raise InstagramAPIError("Connection error. Is the API server running?")

    # ==================== 用户操作 ====================

    def get_user(self, username: str) -> Dict:
        """
        获取用户资料

        Args:
            username: Instagram 用户名

        Returns:
            用户资料字典
        """
        return self._make_request('GET', f'/users/{username}')

    def follow(self, username: str) -> Dict:
        """
        关注用户

        Args:
            username: Instagram 用户名

        Returns:
            操作结果
        """
        return self._make_request('POST', f'/users/{username}/follow')

    def unfollow(self, username: str) -> Dict:
        """
        取消关注用户

        Args:
            username: Instagram 用户名

        Returns:
            操作结果
        """
        return self._make_request('DELETE', f'/users/{username}/follow')

    def get_user_posts(
        self,
        username: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        获取用户的帖子列表

        Args:
            username: Instagram 用户名
            limit: 最大帖子数量

        Returns:
            帖子列表
        """
        result = self._make_request(
            'GET',
            f'/users/{username}/media',
            params={'max_results': limit}
        )
        return result.get('posts', [])

    # ==================== 帖子操作 ====================

    def like_post(self, post_url: str) -> Dict:
        """
        点赞帖子

        Args:
            post_url: 帖子 URL 或 media_id

        Returns:
            操作结果
        """
        media_id = self._extract_media_id(post_url)
        return self._make_request('POST', f'/media/{media_id}/like')

    def unlike_post(self, post_url: str) -> Dict:
        """
        取消点赞

        Args:
            post_url: 帖子 URL 或 media_id

        Returns:
            操作结果
        """
        media_id = self._extract_media_id(post_url)
        return self._make_request('DELETE', f'/media/{media_id}/like')

    def comment(self, post_url: str, text: str) -> Dict:
        """
        评论帖子

        Args:
            post_url: 帖子 URL 或 media_id
            text: 评论内容

        Returns:
            操作结果
        """
        media_id = self._extract_media_id(post_url)
        return self._make_request(
            'POST',
            f'/media/{media_id}/comments',
            json={'text': text}
        )

    def get_post(self, post_url: str) -> Dict:
        """
        获取帖子详情

        Args:
            post_url: 帖子 URL 或 media_id

        Returns:
            帖子详情
        """
        media_id = self._extract_media_id(post_url)
        return self._make_request('GET', f'/media/{media_id}')

    def create_post(self, image_path: str, caption: str) -> Dict:
        """
        发布新帖子

        Args:
            image_path: 图片文件路径
            caption: 帖子描述

        Returns:
            操作结果
        """
        return self._make_request(
            'POST',
            '/media',
            json={
                'image_path': image_path,
                'caption': caption
            }
        )

    # ==================== 搜索与发现 ====================

    def search_by_tag(self, tag: str, limit: int = 20) -> List[Dict]:
        """
        按标签搜索帖子

        Args:
            tag: 标签名称（不含 #）
            limit: 最大结果数量

        Returns:
            帖子列表
        """
        tag = tag.lstrip('#')
        result = self._make_request(
            'GET',
            f'/tags/{tag}/media/recent',
            params={'max_results': limit}
        )
        return result.get('posts', [])

    # ==================== 私信操作 ====================

    def send_dm(self, username: str, message: str) -> Dict:
        """
        发送私信

        Args:
            username: 接收者用户名
            message: 消息内容

        Returns:
            操作结果
        """
        return self._make_request(
            'POST',
            f'/users/{username}/dm',
            json={
                'username': username,
                'message': message
            }
        )

    # ==================== 批量操作 ====================

    def batch_like(
        self,
        post_urls: List[str],
        delay: Optional[float] = None
    ) -> List[Dict]:
        """
        批量点赞帖子

        Args:
            post_urls: 帖子 URL 列表
            delay: 操作间隔（秒），None 使用默认延迟

        Returns:
            操作结果列表
        """
        results = []
        original_auto_delay = self.auto_delay

        if delay is not None:
            self.auto_delay = False

        try:
            for url in post_urls:
                result = self.like_post(url)
                results.append(result)

                if delay is not None:
                    time.sleep(delay)

        finally:
            self.auto_delay = original_auto_delay

        return results

    def batch_follow(
        self,
        usernames: List[str],
        delay: Optional[float] = None
    ) -> List[Dict]:
        """
        批量关注用户

        Args:
            usernames: 用户名列表
            delay: 操作间隔（秒）

        Returns:
            操作结果列表
        """
        results = []
        original_auto_delay = self.auto_delay

        if delay is not None:
            self.auto_delay = False

        try:
            for username in usernames:
                result = self.follow(username)
                results.append(result)

                if delay is not None:
                    time.sleep(delay)

        finally:
            self.auto_delay = original_auto_delay

        return results

    def batch_send_dms(
        self,
        recipients: List[tuple],
        delay: float = 30
    ) -> List[Dict]:
        """
        批量发送私信

        Args:
            recipients: [(username, message), ...] 列表
            delay: 操作间隔（秒）

        Returns:
            操作结果列表
        """
        results = []

        for username, message in recipients:
            result = self.send_dm(username, message)
            results.append(result)
            time.sleep(delay)

        return results

    # ==================== 工具方法 ====================

    def health_check(self) -> Dict:
        """检查 API 服务状态"""
        return self._make_request('GET', '/health')

    def is_available(self) -> bool:
        """检查 API 是否可用"""
        try:
            result = self.health_check()
            return result.get('status') == 'ok'
        except:
            return False


# ==================== 便捷别名 ====================

class Instagram(InstagramAPI):
    """InstagramAPI 的便捷别名"""
    pass


# ==================== 使用示例 ====================

if __name__ == '__main__':
    # 初始化 API
    api = InstagramAPI()

    # 检查服务状态
    if not api.is_available():
        print("❌ API 服务未运行")
        print("请先启动服务：")
        print("  uvicorn main:app --reload --port 8000")
        print("  python3 platforms/instagram/instagram_bridge_server.py")
        exit(1)

    print("✅ API 服务正常运行\n")

    # 示例 1: 获取用户资料
    print("示例 1: 获取用户资料")
    try:
        user = api.get_user("instagram")
        print(f"  用户名: {user['username']}")
        print(f"  粉丝数: {user.get('followers', 'N/A')}")
    except InstagramAPIError as e:
        print(f"  错误: {e}")

    # 示例 2: 点赞帖子
    print("\n示例 2: 点赞帖子")
    post_url = "https://www.instagram.com/p/ABC123/"  # 替换为真实 URL
    try:
        result = api.like_post(post_url)
        if result['success']:
            print(f"  ✅ 点赞成功")
    except InstagramAPIError as e:
        print(f"  错误: {e}")

    # 示例 3: 搜索标签
    print("\n示例 3: 搜索标签")
    try:
        posts = api.search_by_tag("travel", limit=5)
        print(f"  找到 {len(posts)} 个帖子")
        for i, post in enumerate(posts[:3], 1):
            print(f"    {i}. {post['url']}")
    except InstagramAPIError as e:
        print(f"  错误: {e}")

    # 示例 4: 批量操作
    print("\n示例 4: 批量点赞")
    post_urls = [
        "https://www.instagram.com/p/ABC1/",
        "https://www.instagram.com/p/ABC2/",
        "https://www.instagram.com/p/ABC3/"
    ]
    try:
        results = api.batch_like(post_urls, delay=5)
        success_count = sum(1 for r in results if r.get('success'))
        print(f"  成功: {success_count}/{len(results)}")
    except InstagramAPIError as e:
        print(f"  错误: {e}")
