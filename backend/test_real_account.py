#!/usr/bin/env python3
"""
Real Account Test - Non-interactive testing of Instagram API
Tests all core functions automatically
"""

import sys
import os

# Add parent directory to path to import instagram_sdk
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from instagram_sdk import InstagramAPI, InstagramAPIError
import time


def print_section(title):
    """Print section header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def test_health_check(api):
    """Test 1: API Health Check"""
    print_section("Test 1: API Health Check")

    try:
        result = api.health_check()
        print(f"✅ API Status: {result.get('status')}")
        print(f"   Message: {result.get('message')}")
        print(f"   Bridge Status: {result.get('bridge_status', 'unknown')}")
        return True
    except InstagramAPIError as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_get_user_profile(api, username="instagram"):
    """Test 2: Get User Profile"""
    print_section(f"Test 2: Get User Profile (@{username})")

    try:
        user = api.get_user(username)
        print(f"✅ Profile Retrieved:")
        print(f"   👤 Username: {user.get('username', 'N/A')}")
        print(f"   🔗 Profile URL: {user.get('profile_url', 'N/A')}")
        print(f"   📝 Bio: {user.get('bio', 'N/A')[:100]}...")
        print(f"   👥 Followers: {user.get('followers', 'N/A')}")
        print(f"   📸 Following: {user.get('following', 'N/A')}")
        print(f"   📊 Posts: {user.get('posts', 'N/A')}")
        return True
    except InstagramAPIError as e:
        print(f"❌ Failed to get profile: {e}")
        return False


def test_get_user_posts(api, username="instagram", limit=5):
    """Test 3: Get User Posts"""
    print_section(f"Test 3: Get User Posts (@{username}, limit={limit})")

    try:
        posts = api.get_user_posts(username, limit=limit)
        print(f"✅ Retrieved {len(posts)} posts:")
        for i, post in enumerate(posts[:5], 1):
            print(f"   {i}. {post.get('url', 'N/A')}")
        return posts
    except InstagramAPIError as e:
        print(f"❌ Failed to get posts: {e}")
        return []


def test_search_by_tag(api, tag="travel", limit=5):
    """Test 4: Search by Tag"""
    print_section(f"Test 4: Search by Tag (#{tag}, limit={limit})")

    try:
        results = api.search_by_tag(tag, limit=limit)
        print(f"✅ Found {len(results)} posts:")
        for i, post in enumerate(results[:5], 1):
            print(f"   {i}. {post.get('url', 'N/A')}")
        return results
    except InstagramAPIError as e:
        print(f"❌ Failed to search by tag: {e}")
        return []


def test_get_post_details(api, post_url):
    """Test 5: Get Post Details"""
    print_section("Test 5: Get Post Details")

    if not post_url:
        print("⏭️  Skipping (no post URL available)")
        return False

    print(f"Post URL: {post_url}")

    try:
        details = api.get_post(post_url)
        print(f"✅ Post Details Retrieved:")
        print(f"   📝 Caption: {details.get('caption', 'N/A')[:100]}...")
        print(f"   ❤️  Likes: {details.get('likes', 'N/A')}")
        print(f"   💬 Comments: {details.get('comments', 'N/A')}")
        print(f"   👤 Author: {details.get('author', 'N/A')}")
        return True
    except InstagramAPIError as e:
        print(f"❌ Failed to get post details: {e}")
        return False


def main():
    print("=" * 60)
    print("  Instagram API - Real Account Automated Test")
    print("=" * 60)
    print("\nThis script tests all core API functions automatically.")
    print("No user interaction required.\n")

    # Initialize API with auto delay
    api = InstagramAPI(
        auto_delay=True,
        min_delay=3,
        max_delay=8
    )

    # Track results
    results = {
        'passed': 0,
        'failed': 0,
        'total': 0
    }

    # Test 1: Health Check
    results['total'] += 1
    if test_health_check(api):
        results['passed'] += 1
    else:
        results['failed'] += 1
        print("\n❌ API not available. Please check servers are running:")
        print("   Terminal 1: uvicorn main:app --reload --port 8000")
        print("   Terminal 2: python3 platforms/instagram/instagram_bridge_server.py")
        sys.exit(1)

    time.sleep(2)

    # Test 2: Get User Profile
    results['total'] += 1
    if test_get_user_profile(api, "instagram"):
        results['passed'] += 1
    else:
        results['failed'] += 1

    time.sleep(2)

    # Test 3: Get User Posts
    results['total'] += 1
    posts = test_get_user_posts(api, "instagram", limit=5)
    if posts:
        results['passed'] += 1
    else:
        results['failed'] += 1

    time.sleep(2)

    # Test 4: Search by Tag
    results['total'] += 1
    tag_results = test_search_by_tag(api, "travel", limit=5)
    if tag_results:
        results['passed'] += 1
    else:
        results['failed'] += 1

    time.sleep(2)

    # Test 5: Get Post Details (using first post from Test 3)
    results['total'] += 1
    if posts and len(posts) > 0:
        first_post_url = posts[0].get('url')
        if test_get_post_details(api, first_post_url):
            results['passed'] += 1
        else:
            results['failed'] += 1
    else:
        print_section("Test 5: Get Post Details")
        print("⏭️  Skipping (no posts available from previous test)")
        results['total'] -= 1

    # Summary
    print_section("Test Summary")
    print(f"\n✅ Passed: {results['passed']}/{results['total']}")
    print(f"❌ Failed: {results['failed']}/{results['total']}")

    success_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    print(f"📊 Success Rate: {success_rate:.1f}%")

    if results['passed'] == results['total']:
        print("\n🎉 All tests passed! Instagram API is working perfectly.")
    elif results['passed'] > 0:
        print(f"\n⚠️  Some tests failed. Please check error messages above.")
    else:
        print(f"\n❌ All tests failed. Please check server status and authentication.")

    print("\n" + "=" * 60)
    print("\n📚 For interactive testing, run:")
    print("   python3 example_usage.py")
    print("\n📚 For detailed testing guide, see:")
    print("   INSTAGRAM_TESTING_GUIDE.md")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
