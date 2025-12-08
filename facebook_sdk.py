"""
Facebook API SDK
官方风格的 Facebook API 客户端库

使用示例:
    from facebook_sdk import FacebookAPI

    api = FacebookAPI()

    # 点赞帖子
    api.like_post("https://www.facebook.com/...")

    # 关注用户
    api.follow("username")

    # 评论帖子
    api.comment("https://www.facebook.com/...", "Great post!")

    # 获取用户帖子
    posts = api.get_user_posts("username", limit=10)
"""

import requests
import time
import random
from typing import List, Dict, Optional


class FacebookAPIError(Exception):
    """Facebook API 错误"""
    pass


class RateLimitError(FacebookAPIError):
    """速率限制错误"""
    pass


class AuthenticationError(FacebookAPIError):
    """认证错误"""
    pass


class FacebookAPI:
    """
    Facebook API 客户端

    支持所有 Facebook Graph API 功能，以及扩展的自动化功能。
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/api/v1/facebook",
        timeout: int = 60,
        auto_delay: bool = True,
        min_delay: float = 3.0,
        max_delay: float = 8.0
    ):
        """
        初始化 Facebook API 客户端

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
                raise FacebookAPIError(f"API Error: {error_msg}")

        except requests.exceptions.Timeout:
            raise FacebookAPIError("Request timeout")
        except requests.exceptions.ConnectionError:
            raise FacebookAPIError("Connection error. Is the API server running?")

    # ==================== 用户操作 ====================

    def get_user(self, username: str) -> Dict:
        """
        获取用户资料

        Args:
            username: Facebook 用户名或用户ID

        Returns:
            用户资料字典
        """
        return self._make_request('GET', f'/users/{username}')

    def follow(self, username: str) -> Dict:
        """
        关注用户（Facebook 为添加好友/关注）

        Args:
            username: Facebook 用户名

        Returns:
            操作结果
        """
        return self._make_request('POST', f'/users/{username}/follow')

    def get_user_posts(
        self,
        username: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        获取用户的帖子列表

        Args:
            username: Facebook 用户名
            limit: 最大帖子数量

        Returns:
            帖子列表
        """
        result = self._make_request(
            'GET',
            f'/users/{username}/posts',
            params={'max_count': limit}
        )
        return result.get('posts', [])

    # ==================== 帖子操作 ====================

    def like_post(self, post_url: str) -> Dict:
        """
        点赞帖子

        Args:
            post_url: 帖子 URL

        Returns:
            操作结果
        """
        return self._make_request(
            'POST',
            '/posts/like',
            json={'post_url': post_url}
        )

    def comment(self, post_url: str, text: str) -> Dict:
        """
        评论帖子

        Args:
            post_url: 帖子 URL
            text: 评论内容

        Returns:
            操作结果
        """
        return self._make_request(
            'POST',
            '/posts/comment',
            json={
                'post_url': post_url,
                'comment': text
            }
        )

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
            '/dm/send',
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

class Facebook(FacebookAPI):
    """FacebookAPI 的便捷别名"""
    pass


# ==================== 使用示例 ====================

if __name__ == '__main__':
    # 初始化 API
    api = FacebookAPI()

    # 检查服务状态
    if not api.is_available():
        print("❌ API 服务未运行")
        print("请先启动服务：")
        print("  uvicorn main:app --reload --port 8000")
        print("  python3 platforms/facebook/facebook_bridge_server.py")
        exit(1)

    print("✅ API 服务正常运行\n")

    # 示例 1: 获取用户资料
    print("示例 1: 获取用户资料")
    try:
        user = api.get_user("facebook")
        print(f"  用户名: {user['username']}")
        print(f"  姓名: {user.get('name', 'N/A')}")
    except FacebookAPIError as e:
        print(f"  错误: {e}")

    # 示例 2: 获取用户帖子
    print("\n示例 2: 获取用户帖子")
    try:
        posts = api.get_user_posts("facebook", limit=5)
        print(f"  找到 {len(posts)} 个帖子")
        for i, post in enumerate(posts[:3], 1):
            print(f"    {i}. {post.get('post_url', 'N/A')}")
    except FacebookAPIError as e:
        print(f"  错误: {e}")

    # 示例 3: 点赞帖子
    print("\n示例 3: 点赞帖子")
    post_url = "https://www.facebook.com/..."  # 替换为真实 URL
    try:
        result = api.like_post(post_url)
        if result['success']:
            print(f"  ✅ 点赞成功")
    except FacebookAPIError as e:
        print(f"  错误: {e}")

    # 示例 4: 批量操作
    print("\n示例 4: 批量点赞")
    post_urls = [
        "https://www.facebook.com/post1",
        "https://www.facebook.com/post2",
        "https://www.facebook.com/post3"
    ]
    try:
        results = api.batch_like(post_urls, delay=5)
        success_count = sum(1 for r in results if r.get('success'))
        print(f"  成功: {success_count}/{len(results)}")
    except FacebookAPIError as e:
        print(f"  错误: {e}")

    # 示例 5: 发送私信
    print("\n示例 5: 发送私信")
    try:
        result = api.send_dm("username", "你好！这是一条测试消息。")
        if result['success']:
            print(f"  ✅ 私信发送成功")
    except FacebookAPIError as e:
        print(f"  错误: {e}")
