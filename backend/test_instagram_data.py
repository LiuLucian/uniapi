#!/usr/bin/env python3
"""
Test Instagram Data Retrieval API Endpoints
- Get Post Details
- Get User Posts
- Search by Tag
"""
import requests
import json

# API endpoints
BASE_URL = "http://localhost:8000/api/v1/instagram"

def test_get_post_details():
    """Test getting Instagram post details"""
    print("=" * 60)
    print("📤 Testing Instagram Get Post Details API")
    print("=" * 60)

    post_url = input("\n🔗 Enter Instagram post URL: ").strip()

    if not post_url:
        print("❌ No URL provided")
        return

    # Extract media_id from URL
    if '/p/' in post_url:
        media_id = post_url.split('/p/')[-1].rstrip('/').split('/')[0]
    else:
        media_id = post_url

    print(f"\n📝 Media ID: {media_id}")
    print(f"🎯 Endpoint: GET {BASE_URL}/media/{media_id}")
    print("\n⏳ Fetching post details...")
    print("   (This may take 10-15 seconds with browser automation)")
    print()

    try:
        response = requests.get(
            f"{BASE_URL}/media/{media_id}",
            timeout=60
        )

        print(f"📊 Status Code: {response.status_code}")
        print("\n📥 Response:")
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if response.status_code == 200 and result.get('success'):
            print("\n✅ SUCCESS: Post details retrieved!")

            # Display summary
            print("\n📋 Post Summary:")
            print(f"   Caption: {result.get('caption', 'N/A')[:100]}...")
            print(f"   Likes: {result.get('likes', 'N/A')}")
            print(f"   Comments: {result.get('comments', 'N/A')}")
            print(f"   Author: {result.get('author', 'N/A')}")
            return True
        else:
            print("\n❌ FAILED: Could not fetch post details")
            return False

    except requests.exceptions.Timeout:
        print("\n⏰ Request timed out (>60s)")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_get_user_posts():
    """Test getting user's Instagram posts"""
    print("\n" + "=" * 60)
    print("📤 Testing Instagram Get User Posts API")
    print("=" * 60)

    username = input("\n👤 Enter Instagram username: ").strip().lstrip('@')

    if not username:
        print("❌ No username provided")
        return

    max_results = input("🔢 Max number of posts (default 20): ").strip()

    if not max_results:
        max_results = 20
    else:
        try:
            max_results = int(max_results)
        except ValueError:
            print("❌ Invalid number, using default 20")
            max_results = 20

    print(f"\n📝 Username: @{username}")
    print(f"📊 Max results: {max_results}")
    print(f"🎯 Endpoint: GET {BASE_URL}/users/{username}/media?max_results={max_results}")
    print("\n⏳ Fetching user posts...")
    print("   (This may take 15-30 seconds depending on scroll amount)")
    print()

    try:
        response = requests.get(
            f"{BASE_URL}/users/{username}/media",
            params={"max_results": max_results},
            timeout=90
        )

        print(f"📊 Status Code: {response.status_code}")
        print("\n📥 Response:")
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if response.status_code == 200 and result.get('success'):
            posts = result.get('posts', [])
            print(f"\n✅ SUCCESS: Retrieved {len(posts)} posts from @{username}!")

            # Display post URLs
            if posts:
                print("\n📋 Post URLs:")
                for idx, post in enumerate(posts[:10], 1):  # Show first 10
                    print(f"   {idx}. {post.get('url', 'N/A')}")

                if len(posts) > 10:
                    print(f"   ... and {len(posts) - 10} more")

            return True
        else:
            print("\n❌ FAILED: Could not fetch user posts")
            return False

    except requests.exceptions.Timeout:
        print("\n⏰ Request timed out (>90s)")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_search_by_tag():
    """Test searching Instagram posts by hashtag"""
    print("\n" + "=" * 60)
    print("📤 Testing Instagram Search by Tag API")
    print("=" * 60)

    tag = input("\n🏷️  Enter hashtag (without #): ").strip().lstrip('#')

    if not tag:
        print("❌ No tag provided")
        return

    max_results = input("🔢 Max number of posts (default 20): ").strip()

    if not max_results:
        max_results = 20
    else:
        try:
            max_results = int(max_results)
        except ValueError:
            print("❌ Invalid number, using default 20")
            max_results = 20

    print(f"\n📝 Tag: #{tag}")
    print(f"📊 Max results: {max_results}")
    print(f"🎯 Endpoint: GET {BASE_URL}/tags/{tag}/media/recent?max_results={max_results}")
    print("\n⏳ Searching posts...")
    print("   (This may take 15-30 seconds depending on scroll amount)")
    print()

    try:
        response = requests.get(
            f"{BASE_URL}/tags/{tag}/media/recent",
            params={"max_results": max_results},
            timeout=90
        )

        print(f"📊 Status Code: {response.status_code}")
        print("\n📥 Response:")
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if response.status_code == 200 and result.get('success'):
            posts = result.get('posts', [])
            print(f"\n✅ SUCCESS: Found {len(posts)} posts for #{tag}!")

            # Display post URLs
            if posts:
                print("\n📋 Post URLs:")
                for idx, post in enumerate(posts[:10], 1):  # Show first 10
                    print(f"   {idx}. {post.get('url', 'N/A')}")

                if len(posts) > 10:
                    print(f"   ... and {len(posts) - 10} more")

            return True
        else:
            print("\n❌ FAILED: Could not search posts")
            return False

    except requests.exceptions.Timeout:
        print("\n⏰ Request timed out (>90s)")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_complete_data_flow():
    """Test complete data retrieval flow"""
    print("\n" + "=" * 60)
    print("🔄 Testing Complete Data Retrieval Flow")
    print("=" * 60)

    username = input("\n👤 Enter Instagram username: ").strip().lstrip('@')

    if not username:
        print("❌ No username provided")
        return

    print("\n📍 Step 1: Get User Posts")
    print("   Fetching posts...")

    try:
        # Step 1: Get user posts
        response = requests.get(
            f"{BASE_URL}/users/{username}/media",
            params={"max_results": 5},
            timeout=90
        )

        result = response.json()

        if not result.get('success'):
            print("   ❌ Failed to get user posts")
            return False

        posts = result.get('posts', [])
        print(f"   ✅ Retrieved {len(posts)} posts")

        if not posts:
            print("   ⚠️  No posts found for this user")
            return False

        # Step 2: Get details for first post
        first_post = posts[0]
        post_url = first_post.get('url', '')

        if '/p/' in post_url:
            media_id = post_url.split('/p/')[-1].rstrip('/').split('/')[0]
        else:
            print("   ❌ Could not extract media ID from post URL")
            return False

        print(f"\n📍 Step 2: Get Post Details")
        print(f"   Post URL: {post_url}")
        print("   Fetching details...")

        response = requests.get(
            f"{BASE_URL}/media/{media_id}",
            timeout=60
        )

        result = response.json()

        if result.get('success'):
            print("   ✅ Retrieved post details")
            print(f"   Caption: {result.get('caption', 'N/A')[:50]}...")
            print(f"   Likes: {result.get('likes', 'N/A')}")
            print(f"   Comments: {result.get('comments', 'N/A')}")

            print("\n🎉 COMPLETE DATA FLOW TEST PASSED!")
            return True
        else:
            print("   ❌ Failed to get post details")
            return False

    except Exception as e:
        print(f"\n❌ Flow test error: {e}")
        return False


def main():
    """Main test menu"""
    print("\n" + "=" * 60)
    print("🧪 Instagram Data Retrieval API Test Suite")
    print("=" * 60)
    print("\nAvailable Tests:")
    print("1. Test Get Post Details")
    print("2. Test Get User Posts")
    print("3. Test Search by Tag")
    print("4. Test Complete Data Flow")
    print("5. Run All Tests")
    print("0. Exit")

    while True:
        choice = input("\n👉 Select test (0-5): ").strip()

        if choice == '0':
            print("\n👋 Exiting test suite")
            break
        elif choice == '1':
            test_get_post_details()
        elif choice == '2':
            test_get_user_posts()
        elif choice == '3':
            test_search_by_tag()
        elif choice == '4':
            test_complete_data_flow()
        elif choice == '5':
            print("\n🚀 Running all tests...")
            print("\n--- Test 1: Get Post Details ---")
            test_get_post_details()
            print("\n--- Test 2: Get User Posts ---")
            test_get_user_posts()
            print("\n--- Test 3: Search by Tag ---")
            test_search_by_tag()
            print("\n--- Test 4: Complete Flow ---")
            test_complete_data_flow()
        else:
            print("❌ Invalid choice, please select 0-5")


if __name__ == "__main__":
    main()
