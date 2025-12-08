#!/usr/bin/env python3
"""
Test Instagram Like/Unlike API Endpoints
"""
import requests
import json
import time

# API endpoints
BASE_URL = "http://localhost:8000/api/v1/instagram"

def test_like_post():
    """Test liking an Instagram post"""
    print("=" * 60)
    print("📤 Testing Instagram Like Post API")
    print("=" * 60)

    # You need to replace this with a real Instagram post URL
    # Example: https://www.instagram.com/p/ABC123xyz/
    post_url = input("\n🔗 Enter Instagram post URL to like: ").strip()

    if not post_url:
        print("❌ No URL provided")
        return

    # Extract media_id from URL (shortcode between /p/ and /)
    if '/p/' in post_url:
        media_id = post_url.split('/p/')[-1].rstrip('/').split('/')[0]
    else:
        media_id = post_url

    print(f"\n📝 Media ID: {media_id}")
    print(f"🎯 Endpoint: POST {BASE_URL}/media/{media_id}/like")
    print("\n⏳ Sending like request...")
    print("   (This may take 10-15 seconds with browser automation)")
    print()

    try:
        response = requests.post(
            f"{BASE_URL}/media/{media_id}/like",
            timeout=60
        )

        print(f"📊 Status Code: {response.status_code}")
        print("\n📥 Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))

        if response.status_code == 200 and response.json().get('success'):
            print("\n✅ SUCCESS: Post liked!")
            return True
        else:
            print("\n❌ FAILED: Could not like post")
            return False

    except requests.exceptions.Timeout:
        print("\n⏰ Request timed out (>60s)")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_unlike_post():
    """Test unliking an Instagram post"""
    print("\n" + "=" * 60)
    print("📤 Testing Instagram Unlike Post API")
    print("=" * 60)

    post_url = input("\n🔗 Enter Instagram post URL to unlike: ").strip()

    if not post_url:
        print("❌ No URL provided")
        return

    if '/p/' in post_url:
        media_id = post_url.split('/p/')[-1].rstrip('/').split('/')[0]
    else:
        media_id = post_url

    print(f"\n📝 Media ID: {media_id}")
    print(f"🎯 Endpoint: DELETE {BASE_URL}/media/{media_id}/like")
    print("\n⏳ Sending unlike request...")
    print()

    try:
        response = requests.delete(
            f"{BASE_URL}/media/{media_id}/like",
            timeout=60
        )

        print(f"📊 Status Code: {response.status_code}")
        print("\n📥 Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))

        if response.status_code == 200 and response.json().get('success'):
            print("\n✅ SUCCESS: Post unliked!")
            return True
        else:
            print("\n❌ FAILED: Could not unlike post")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_like_unlike_cycle():
    """Test complete like/unlike cycle on same post"""
    print("\n" + "=" * 60)
    print("🔄 Testing Complete Like/Unlike Cycle")
    print("=" * 60)

    post_url = input("\n🔗 Enter Instagram post URL for cycle test: ").strip()

    if not post_url:
        print("❌ No URL provided")
        return

    if '/p/' in post_url:
        media_id = post_url.split('/p/')[-1].rstrip('/').split('/')[0]
    else:
        media_id = post_url

    print(f"\n📝 Media ID: {media_id}")
    print("\n📍 Step 1: Like the post")

    try:
        # Step 1: Like
        response = requests.post(f"{BASE_URL}/media/{media_id}/like", timeout=60)
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Result: {result.get('message', 'No message')}")

        if not result.get('success'):
            print("   ❌ Like failed, aborting cycle test")
            return False

        print("   ✅ Like successful")

        # Wait between actions
        print("\n⏳ Waiting 5 seconds before unlike...")
        time.sleep(5)

        # Step 2: Unlike
        print("\n📍 Step 2: Unlike the post")
        response = requests.delete(f"{BASE_URL}/media/{media_id}/like", timeout=60)
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Result: {result.get('message', 'No message')}")

        if result.get('success'):
            print("   ✅ Unlike successful")
            print("\n🎉 COMPLETE CYCLE TEST PASSED!")
            return True
        else:
            print("   ❌ Unlike failed")
            return False

    except Exception as e:
        print(f"\n❌ Cycle test error: {e}")
        return False


def main():
    """Main test menu"""
    print("\n" + "=" * 60)
    print("🧪 Instagram Like/Unlike API Test Suite")
    print("=" * 60)
    print("\nAvailable Tests:")
    print("1. Test Like Post")
    print("2. Test Unlike Post")
    print("3. Test Complete Like/Unlike Cycle")
    print("4. Run All Tests")
    print("0. Exit")

    while True:
        choice = input("\n👉 Select test (0-4): ").strip()

        if choice == '0':
            print("\n👋 Exiting test suite")
            break
        elif choice == '1':
            test_like_post()
        elif choice == '2':
            test_unlike_post()
        elif choice == '3':
            test_like_unlike_cycle()
        elif choice == '4':
            print("\n🚀 Running all tests...")
            test_like_post()
            time.sleep(3)
            test_unlike_post()
            time.sleep(3)
            test_like_unlike_cycle()
        else:
            print("❌ Invalid choice, please select 0-4")


if __name__ == "__main__":
    main()
