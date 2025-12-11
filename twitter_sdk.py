"""
Twitter SDK - Unified API Interface
Compatible with UniAPI
"""

import httpx
from typing import Dict, List, Optional, Any


class TwitterAPI:
    """
    Twitter API SDK - Unified Interface
    
    Usage:
        api = TwitterAPI()
        user = api.get_user("twitter")
        api.like_tweet("https://twitter.com/user/status/123")
        api.send_dm("username", "Hello!")
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize Twitter API client
        
        Args:
            base_url: UniAPI main server URL (default: http://localhost:8000)
        """
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1/twitter"
        self.client = httpx.Client(timeout=30.0)
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Internal request handler"""
        url = f"{self.api_base}{endpoint}"
        response = self.client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    
    # User Operations
    
    def get_user(self, username: str) -> Dict[str, Any]:
        """
        Get user profile information
        
        Args:
            username: Twitter username (without @)
            
        Returns:
            User profile data
        """
        return self._request("GET", f"/users/{username}")
    
    def follow_user(self, username: str) -> Dict[str, Any]:
        """Follow a user"""
        return self._request("POST", "/users/follow", json={"username": username})
    
    def unfollow_user(self, username: str) -> Dict[str, Any]:
        """Unfollow a user"""
        return self._request("POST", "/users/unfollow", json={"username": username})
    
    # Tweet Operations
    
    def get_tweet(self, tweet_url: str) -> Dict[str, Any]:
        """Get tweet details"""
        return self._request("GET", "/tweets", params={"url": tweet_url})
    
    def post_tweet(self, text: str, media: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Post a new tweet
        
        Args:
            text: Tweet text content
            media: Optional list of media URLs/paths
        """
        data = {"text": text}
        if media:
            data["media"] = media
        return self._request("POST", "/tweets", json=data)
    
    def like_tweet(self, tweet_url: str) -> Dict[str, Any]:
        """Like a tweet"""
        return self._request("POST", "/tweets/like", json={"tweet_url": tweet_url})
    
    def unlike_tweet(self, tweet_url: str) -> Dict[str, Any]:
        """Unlike a tweet"""
        return self._request("POST", "/tweets/unlike", json={"tweet_url": tweet_url})
    
    def retweet(self, tweet_url: str) -> Dict[str, Any]:
        """Retweet a tweet"""
        return self._request("POST", "/tweets/retweet", json={"tweet_url": tweet_url})
    
    def reply_tweet(self, tweet_url: str, text: str) -> Dict[str, Any]:
        """Reply to a tweet"""
        return self._request("POST", "/tweets/reply", json={
            "tweet_url": tweet_url,
            "text": text
        })
    
    # Direct Message Operations
    
    def send_dm(self, username: str, message: str) -> Dict[str, Any]:
        """
        Send direct message to a user
        
        Args:
            username: Target username (without @)
            message: Message content
        """
        return self._request("POST", "/dm/send", json={
            "username": username,
            "message": message
        })
    
    def get_dms(self, username: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get direct messages"""
        params = {"username": username} if username else {}
        return self._request("GET", "/dm", params=params)
    
    # Search Operations
    
    def search_tweets(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search tweets by query
        
        Args:
            query: Search query string
            max_results: Maximum number of results
        """
        return self._request("GET", "/search/tweets", params={
            "query": query,
            "max_results": max_results
        })
    
    def search_users(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """Search users by query"""
        return self._request("GET", "/search/users", params={
            "query": query,
            "max_results": max_results
        })
    
    # Timeline Operations
    
    def get_timeline(self, max_tweets: int = 20) -> List[Dict[str, Any]]:
        """Get home timeline"""
        return self._request("GET", "/timeline", params={"max_tweets": max_tweets})
    
    def get_user_tweets(self, username: str, max_tweets: int = 20) -> List[Dict[str, Any]]:
        """Get user's tweets"""
        return self._request("GET", f"/users/{username}/tweets", params={
            "max_tweets": max_tweets
        })
    
    # Batch Operations
    
    def batch_like(self, tweet_urls: List[str], delay: int = 5) -> List[Dict[str, Any]]:
        """
        Like multiple tweets with delay
        
        Args:
            tweet_urls: List of tweet URLs
            delay: Delay between operations (seconds)
        """
        return self._request("POST", "/batch/like", json={
            "tweet_urls": tweet_urls,
            "delay": delay
        })
    
    def batch_follow(self, usernames: List[str], delay: int = 5) -> List[Dict[str, Any]]:
        """Follow multiple users with delay"""
        return self._request("POST", "/batch/follow", json={
            "usernames": usernames,
            "delay": delay
        })
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'client'):
            self.client.close()


# Convenience function
def get_api() -> TwitterAPI:
    """Get Twitter API instance"""
    return TwitterAPI()
