"""
LinkedIn API SDK - 官方风格的 LinkedIn API 客户端库
"""
import requests
import time
import random
from typing import List, Dict, Optional


class LinkedInAPIError(Exception):
    """LinkedIn API 错误"""
    pass


class LinkedInAPI:
    """LinkedIn API 客户端"""

    def __init__(self, base_url: str = "http://localhost:8000/api/v1/linkedin", timeout: int = 60, auto_delay: bool = True, min_delay: float = 3.0, max_delay: float = 8.0):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.auto_delay = auto_delay
        self.min_delay = min_delay
        self.max_delay = max_delay
        self._last_request_time = 0

    def _wait_if_needed(self):
        if not self.auto_delay:
            return
        elapsed = time.time() - self._last_request_time
        if elapsed < self.min_delay:
            delay = random.uniform(self.min_delay, self.max_delay)
            time.sleep(delay)
        self._last_request_time = time.time()

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        self._wait_if_needed()
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, timeout=self.timeout, **kwargs)
            data = response.json()
            if response.status_code == 200:
                return data
            else:
                raise LinkedInAPIError(f"API Error: {data.get('error', 'Unknown error')}")
        except requests.exceptions.Timeout:
            raise LinkedInAPIError("Request timeout")
        except requests.exceptions.ConnectionError:
            raise LinkedInAPIError("Connection error. Is the API server running?")

    def get_user(self, username: str) -> Dict:
        return self._make_request('GET', f'/users/{username}')

    def connect(self, username: str) -> Dict:
        return self._make_request('POST', f'/users/{username}/connect')

    def get_user_posts(self, username: str, limit: int = 10) -> List[Dict]:
        result = self._make_request('GET', f'/users/{username}/posts', params={'max_count': limit})
        return result.get('posts', [])

    def like_post(self, post_url: str) -> Dict:
        return self._make_request('POST', '/posts/like', json={'post_url': post_url})

    def comment(self, post_url: str, text: str) -> Dict:
        return self._make_request('POST', '/posts/comment', json={'post_url': post_url, 'comment': text})

    def send_dm(self, username: str, message: str) -> Dict:
        return self._make_request('POST', '/dm/send', json={'username': username, 'message': message})

    def health_check(self) -> Dict:
        return self._make_request('GET', '/health')

    def is_available(self) -> bool:
        try:
            result = self.health_check()
            return result.get('status') == 'ok'
        except:
            return False


class LinkedIn(LinkedInAPI):
    """LinkedInAPI 的便捷别名"""
    pass
