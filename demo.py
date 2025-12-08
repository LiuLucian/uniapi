#!/usr/bin/env python3
"""
UniAPI 使用示例
演示如何使用Python SDK调用各个平台的API
"""

from instagram_sdk import InstagramAPI
from tiktok_sdk import TikTokAPI
from facebook_sdk import FacebookAPI
from linkedin_sdk import LinkedInAPI


def demo_instagram():
    """Instagram API 示例"""
    print("\n" + "="*50)
    print("📸 Instagram API 示例")
    print("="*50)

    api = InstagramAPI()

    # 1. 获取用户信息
    print("\n1️⃣ 获取用户信息")
    try:
        user = api.get_user("instagram")
        print(f"✅ 用户名: {user.get('username')}")
        print(f"   粉丝数: {user.get('followers', 'N/A')}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    # 2. 点赞帖子
    print("\n2️⃣ 点赞帖子")
    try:
        result = api.like_post("https://www.instagram.com/p/example/")
        print(f"✅ {result.get('message', '操作成功')}")
    except Exception as e:
        print(f"ℹ️  示例: {e}")

    # 3. 评论帖子
    print("\n3️⃣ 评论帖子")
    try:
        result = api.comment("https://www.instagram.com/p/example/", "Great post!")
        print(f"✅ {result.get('message', '评论成功')}")
    except Exception as e:
        print(f"ℹ️  示例: {e}")


def demo_tiktok():
    """TikTok API 示例"""
    print("\n" + "="*50)
    print("🎵 TikTok API 示例")
    print("="*50)

    api = TikTokAPI()

    # 1. 获取用户信息
    print("\n1️⃣ 获取用户信息")
    try:
        user = api.get_user("@tiktok")
        print(f"✅ 用户名: {user.get('username')}")
        print(f"   粉丝数: {user.get('followers', 'N/A')}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    # 2. 点赞视频
    print("\n2️⃣ 点赞视频")
    try:
        result = api.like_video("https://www.tiktok.com/@user/video/123")
        print(f"✅ {result.get('message', '操作成功')}")
    except Exception as e:
        print(f"ℹ️  示例: {e}")


def demo_facebook():
    """Facebook API 示例"""
    print("\n" + "="*50)
    print("👥 Facebook API 示例")
    print("="*50)

    api = FacebookAPI()

    # 1. 获取用户信息
    print("\n1️⃣ 获取用户信息")
    try:
        user = api.get_user("facebook")
        print(f"✅ 用户名: {user.get('username')}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    # 2. 点赞帖子
    print("\n2️⃣ 点赞帖子")
    try:
        result = api.like_post("https://www.facebook.com/post/123")
        print(f"✅ {result.get('message', '操作成功')}")
    except Exception as e:
        print(f"ℹ️  示例: {e}")


def demo_linkedin():
    """LinkedIn API 示例"""
    print("\n" + "="*50)
    print("💼 LinkedIn API 示例")
    print("="*50)

    api = LinkedInAPI()

    # 1. 获取用户信息
    print("\n1️⃣ 获取用户信息")
    try:
        user = api.get_user("linkedin")
        print(f"✅ 用户名: {user.get('username')}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    # 2. 连接用户
    print("\n2️⃣ 连接用户")
    try:
        result = api.connect("user123")
        print(f"✅ {result.get('message', '操作成功')}")
    except Exception as e:
        print(f"ℹ️  示例: {e}")


def demo_batch_operations():
    """批量操作示例"""
    print("\n" + "="*50)
    print("⚡ 批量操作示例")
    print("="*50)

    api = InstagramAPI()

    # 批量点赞多个帖子
    print("\n批量点赞多个Instagram帖子")
    urls = [
        "https://www.instagram.com/p/post1/",
        "https://www.instagram.com/p/post2/",
        "https://www.instagram.com/p/post3/"
    ]

    try:
        results = api.batch_like(urls, delay=5)  # 每个操作间隔5秒
        print(f"✅ 成功点赞 {len([r for r in results if r.get('success')])} 个帖子")
    except Exception as e:
        print(f"ℹ️  示例: {e}")


def main():
    """主函数"""
    print("\n" + "🚀"*25)
    print("UniAPI - Universal Social Media API Platform")
    print("官方API风格的多平台社交媒体统一接口")
    print("🚀"*25)

    print("\n⚠️  注意: 这是演示代码")
    print("   请确保已配置platforms_auth.json文件")
    print("   并且UniAPI服务正在运行 (./start_uniapi.sh)")

    # 检查服务是否运行
    import requests
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("\n✅ UniAPI服务正在运行")
        else:
            print("\n❌ UniAPI服务未响应")
            return
    except:
        print("\n❌ UniAPI服务未运行")
        print("   请先运行: cd backend && ./start_uniapi.sh")
        return

    # 运行各平台示例
    demo_instagram()
    demo_tiktok()
    demo_facebook()
    demo_linkedin()
    demo_batch_operations()

    print("\n" + "="*50)
    print("✨ 示例完成!")
    print("="*50)
    print("\n📚 更多信息:")
    print("   - API文档: http://localhost:8000/api/docs")
    print("   - 快速开始: QUICK_START.md")
    print("   - 完整文档: README.md")
    print("")


if __name__ == "__main__":
    main()
