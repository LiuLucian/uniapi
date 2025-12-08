#!/usr/bin/env python3
"""
Visual Demo - 看起来像真实API调用
展示HTTP请求、响应、状态码
"""

import time
import sys
from datetime import datetime

def typewriter(text, delay=0.02):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def demo_api_call(platform, emoji, endpoint, operation):
    print(f"\n{emoji} {platform}")
    print("─" * 60)
    
    # 显示请求
    typewriter(f"→ POST http://localhost:8000/api/v1/{endpoint}", delay=0.01)
    print(f"  Headers: Authorization: Bearer ***")
    print(f'  Body: {{"target": "demo_user", "action": "{operation}"}}')
    
    # 模拟网络延迟
    sys.stdout.write("  Sending")
    for _ in range(3):
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(0.3)
    print(" ✓")
    
    # 显示响应
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"← 200 OK ({timestamp})")
    print(f'  {{"success": true, "platform": "{platform.lower()}", "message": "{operation} completed"}}')
    
    time.sleep(0.5)

def main():
    print("\n" + "=" * 60)
    print(" 🚀 UniAPI - Unified Social Media API Demo")
    print("=" * 60)
    print("\n Starting servers...")
    time.sleep(0.5)
    print(" ✅ Main API Server: http://localhost:8000")
    print(" ✅ Instagram Bridge: Port 5002")
    print(" ✅ Twitter Bridge: Port 5001")
    print(" ✅ TikTok Bridge: Port 5003\n")
    
    time.sleep(1)
    
    print("=" * 60)
    print(" Testing Unified Interface Across Platforms")
    print("=" * 60)
    
    # Demo 3个平台
    demo_api_call("Instagram", "📸", "instagram/send_dm", "DM sent")
    demo_api_call("Twitter", "🐦", "twitter/send_dm", "DM sent")
    demo_api_call("TikTok", "🎵", "tiktok/send_dm", "DM sent")
    
    print("\n" + "=" * 60)
    print(" 🎯 Same Code, All Platforms")
    print("=" * 60)
    print("""
from instagram_sdk import InstagramAPI
from twitter_sdk import TwitterAPI

insta = InstagramAPI()
insta.send_dm("user", "Hello!")  # ← Same method

twitter = TwitterAPI()
twitter.send_dm("user", "Hello!")  # ← Same method
""")
    
    print("=" * 60)
    print(" ✨ One interface, 5 platforms!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
