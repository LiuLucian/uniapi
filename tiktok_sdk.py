"""
TikTok API SDK
官方风格的 TikTok API 客户端库

使用示例:
    from tiktok_sdk import TikTokAPI

    api = TikTokAPI()

    # 点赞视频
    api.like_video("https://www.tiktok.com/@user/video/123456")

    # 关注用户
    api.follow("username")

    # 评论视频
    api.comment("https://www.tiktok.com/@user/video/123456", "Amazing!")

    # 获取用户视频
    videos = api.get_user_videos("username", limit=10)
"""

import requests
import time
import random
from typing import List, Dict, Optional
from urllib.parse import urlparse


class TikTokAPIError(Exception):
    """TikTok API 错误"""
    pass


class RateLimitError(TikTokAPIError):
    """速率限制错误"""
    pass


class AuthenticationError(TikTokAPIError):
    """认证错误"""
    pass


class TikTokAPI:
    """
    TikTok API 客户端

    支持所有 TikTok 官方 API 功能，以及扩展的自动化功能。
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/api/v1/tiktok",
        timeout: int = 60,
        auto_delay: bool = True,
        min_delay: float = 3.0,
        max_delay: float = 8.0
    ):
        """
        初始化 TikTok API 客户端

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
                raise TikTokAPIError(f"API Error: {error_msg}")

        except requests.exceptions.Timeout:
            raise TikTokAPIError("Request timeout")
        except requests.exceptions.ConnectionError:
            raise TikTokAPIError("Connection error. Is the API server running?")

    # ==================== 用户操作 ====================

    def get_user(self, username: str) -> Dict:
        """
        获取用户资料

        Args:
            username: TikTok 用户名（不含 @）

        Returns:
            用户资料字典
        """
        username = username.lstrip('@')
        return self._make_request('GET', f'/users/{username}')

    def follow(self, username: str) -> Dict:
        """
        关注用户

        Args:
            username: TikTok 用户名（不含 @）

        Returns:
            操作结果
        """
        username = username.lstrip('@')
        return self._make_request('POST', f'/users/{username}/follow')

    def get_user_videos(
        self,
        username: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        获取用户的视频列表

        Args:
            username: TikTok 用户名（不含 @）
            limit: 最大视频数量

        Returns:
            视频列表
        """
        username = username.lstrip('@')
        result = self._make_request(
            'GET',
            f'/users/{username}/videos',
            params={'max_count': limit}
        )
        return result.get('videos', [])

    # ==================== 视频操作 ====================

    def like_video(self, video_url: str) -> Dict:
        """
        点赞视频

        Args:
            video_url: 视频 URL

        Returns:
            操作结果
        """
        return self._make_request(
            'POST',
            '/videos/like',
            json={'video_url': video_url}
        )

    def comment(self, video_url: str, text: str) -> Dict:
        """
        评论视频

        Args:
            video_url: 视频 URL
            text: 评论内容

        Returns:
            操作结果
        """
        return self._make_request(
            'POST',
            '/videos/comment',
            json={
                'video_url': video_url,
                'comment_text': text
            }
        )

    # ==================== 私信操作 ====================

    def send_dm(self, username: str, message: str) -> Dict:
        """
        发送私信

        Args:
            username: 接收者用户名（不含 @）
            message: 消息内容

        Returns:
            操作结果
        """
        username = username.lstrip('@')
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
        video_urls: List[str],
        delay: Optional[float] = None
    ) -> List[Dict]:
        """
        批量点赞视频

        Args:
            video_urls: 视频 URL 列表
            delay: 操作间隔（秒），None 使用默认延迟

        Returns:
            操作结果列表
        """
        results = []
        original_auto_delay = self.auto_delay

        if delay is not None:
            self.auto_delay = False

        try:
            for url in video_urls:
                result = self.like_video(url)
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
            usernames: 用户名列表（可含或不含 @）
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

class TikTok(TikTokAPI):
    """TikTokAPI 的便捷别名"""
    pass


# ==================== 使用示例 ====================

if __name__ == '__main__':
    # 初始化 API
    api = TikTokAPI()

    # 检查服务状态
    if not api.is_available():
        print("❌ API 服务未运行")
        print("请先启动服务：")
        print("  uvicorn main:app --reload --port 8000")
        print("  python3 platforms/tiktok/tiktok_bridge_server.py")
        exit(1)

    print("✅ API 服务正常运行\n")

    # 示例 1: 获取用户资料
    print("示例 1: 获取用户资料")
    try:
        user = api.get_user("tiktok")
        print(f"  用户名: {user['username']}")
        print(f"  粉丝数: {user.get('followers', 'N/A')}")
        print(f"  点赞数: {user.get('likes', 'N/A')}")
    except TikTokAPIError as e:
        print(f"  错误: {e}")

    # 示例 2: 获取用户视频
    print("\n示例 2: 获取用户视频")
    try:
        videos = api.get_user_videos("tiktok", limit=5)
        print(f"  找到 {len(videos)} 个视频")
        for i, video in enumerate(videos[:3], 1):
            print(f"    {i}. {video.get('video_url', 'N/A')}")
            print(f"       点赞: {video.get('likes', 0)}, 评论: {video.get('comments', 0)}")
    except TikTokAPIError as e:
        print(f"  错误: {e}")

    # 示例 3: 点赞视频
    print("\n示例 3: 点赞视频")
    video_url = "https://www.tiktok.com/@user/video/123456"  # 替换为真实 URL
    try:
        result = api.like_video(video_url)
        if result['success']:
            print(f"  ✅ 点赞成功")
    except TikTokAPIError as e:
        print(f"  错误: {e}")

    # 示例 4: 批量操作
    print("\n示例 4: 批量点赞")
    video_urls = [
        "https://www.tiktok.com/@user/video/123",
        "https://www.tiktok.com/@user/video/456",
        "https://www.tiktok.com/@user/video/789"
    ]
    try:
        results = api.batch_like(video_urls, delay=5)
        success_count = sum(1 for r in results if r.get('success'))
        print(f"  成功: {success_count}/{len(results)}")
    except TikTokAPIError as e:
        print(f"  错误: {e}")

    # 示例 5: 发送私信
    print("\n示例 5: 发送私信")
    try:
        result = api.send_dm("username", "你好！这是一条测试消息。")
        if result['success']:
            print(f"  ✅ 私信发送成功")
    except TikTokAPIError as e:
        print(f"  错误: {e}")
