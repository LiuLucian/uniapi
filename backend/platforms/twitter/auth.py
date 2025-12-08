"""
Twitter Authentication Management
Handles browser sessions and cookies
"""
from pathlib import Path
import json
from typing import Optional, List
from pydantic import BaseModel


class TwitterAuth(BaseModel):
    """Twitter authentication credentials"""
    cookies: List[dict]
    user_agent: str


def get_twitter_auth() -> TwitterAuth:
    """
    Dependency injection for Twitter authentication

    In production, this would:
    1. Get user from JWT token
    2. Load their saved Twitter credentials from database
    3. Return TwitterAuth object

    For now, load from file (similar to MarketingMind AI)
    """
    auth_file = Path.home() / ".distroflow/twitter_auth.json"

    if not auth_file.exists():
        raise Exception("Twitter authentication not found. Please run: python3 setup_twitter_auth.py")

    with open(auth_file) as f:
        auth_data = json.load(f)

    return TwitterAuth(
        cookies=auth_data.get("cookies", []),
        user_agent=auth_data.get("user_agent", "Mozilla/5.0")
    )
