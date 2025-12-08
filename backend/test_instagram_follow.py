#!/usr/bin/env python3
"""
Test Instagram Follow/Unfollow API Endpoints
"""
import requests
import json
import time

# API endpoints
BASE_URL = "http://localhost:8000/api/v1/instagram"

def test_follow_user():
    """Test following an Instagram user"""
    print("=" * 60)
    print("📤 Testing Instagram Follow User API")
    print("=" * 60)

    # Get username to follow
    username = input("\n👤 Enter Instagram username to follow: ").strip().lstrip('@')

    if not username:
        print("❌ No username provided")
        return

    print(f"\n📝 Username: @{username}")
    print(f"🎯 Endpoint: POST {BASE_URL}/users/{username}/follow")
    print("\n⏳ Sending follow request...")
    print("   (This may take 10-15 seconds with browser automation)")
    print()

    try:
        response = requests.post(
            f"{BASE_URL}/users/{username}/follow",
            timeout=60
        )

        print(f"📊 Status Code: {response.status_code}")
        print("\n📥 Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))

        if response.status_code == 200 and response.json().get('success'):
            print(f"\n✅ SUCCESS: Now following @{username}!")
            return True
        else:
            print(f"\n❌ FAILED: Could not follow @{username}")
            return False

    except requests.exceptions.Timeout:
        print("\n⏰ Request timed out (>60s)")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_unfollow_user():
    """Test unfollowing an Instagram user"""
    print("\n" + "=" * 60)
    print("📤 Testing Instagram Unfollow User API")
    print("=" * 60)

    username = input("\n👤 Enter Instagram username to unfollow: ").strip().lstrip('@')

    if not username:
        print("❌ No username provided")
        return

    print(f"\n📝 Username: @{username}")
    print(f"🎯 Endpoint: DELETE {BASE_URL}/users/{username}/follow")
    print("\n⏳ Sending unfollow request...")
    print()

    try:
        response = requests.delete(
            f"{BASE_URL}/users/{username}/follow",
            timeout=60
        )

        print(f"📊 Status Code: {response.status_code}")
        print("\n📥 Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))

        if response.status_code == 200 and response.json().get('success'):
            print(f"\n✅ SUCCESS: Unfollowed @{username}!")
            return True
        else:
            print(f"\n❌ FAILED: Could not unfollow @{username}")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_follow_unfollow_cycle():
    """Test complete follow/unfollow cycle on same user"""
    print("\n" + "=" * 60)
    print("🔄 Testing Complete Follow/Unfollow Cycle")
    print("=" * 60)

    username = input("\n👤 Enter Instagram username for cycle test: ").strip().lstrip('@')

    if not username:
        print("❌ No username provided")
        return

    print(f"\n📝 Username: @{username}")
    print("\n⚠️  WARNING: This will follow and then unfollow the user!")
    confirm = input("   Continue? (yes/no): ").strip().lower()

    if confirm != 'yes':
        print("   ❌ Test cancelled")
        return

    print("\n📍 Step 1: Follow the user")

    try:
        # Step 1: Follow
        response = requests.post(f"{BASE_URL}/users/{username}/follow", timeout=60)
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Result: {result.get('message', 'No message')}")

        if not result.get('success'):
            print("   ❌ Follow failed, aborting cycle test")
            return False

        print("   ✅ Follow successful")

        # Wait between actions
        print("\n⏳ Waiting 10 seconds before unfollow...")
        time.sleep(10)

        # Step 2: Unfollow
        print("\n📍 Step 2: Unfollow the user")
        response = requests.delete(f"{BASE_URL}/users/{username}/follow", timeout=60)
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Result: {result.get('message', 'No message')}")

        if result.get('success'):
            print("   ✅ Unfollow successful")
            print("\n🎉 COMPLETE CYCLE TEST PASSED!")
            return True
        else:
            print("   ❌ Unfollow failed")
            return False

    except Exception as e:
        print(f"\n❌ Cycle test error: {e}")
        return False


def test_get_user_profile():
    """Test getting user profile info (bonus test)"""
    print("\n" + "=" * 60)
    print("📤 Testing Instagram Get User Profile API")
    print("=" * 60)

    username = input("\n👤 Enter Instagram username: ").strip().lstrip('@')

    if not username:
        print("❌ No username provided")
        return

    print(f"\n📝 Username: @{username}")
    print(f"🎯 Endpoint: GET {BASE_URL}/users/{username}")
    print("\n⏳ Fetching user profile...")
    print()

    try:
        response = requests.get(
            f"{BASE_URL}/users/{username}",
            timeout=60
        )

        print(f"📊 Status Code: {response.status_code}")
        print("\n📥 Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))

        if response.status_code == 200:
            profile = response.json()
            print("\n✅ Profile retrieved successfully!")
            print(f"\n📋 Profile Summary:")
            print(f"   Username: {profile.get('username', 'N/A')}")
            print(f"   Profile URL: {profile.get('profile_url', 'N/A')}")
            print(f"   Bio: {profile.get('bio', 'N/A')}")
            print(f"   Followers: {profile.get('followers', 'N/A')}")
            return True
        else:
            print("\n❌ Failed to retrieve profile")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def main():
    """Main test menu"""
    print("\n" + "=" * 60)
    print("🧪 Instagram Follow/Unfollow API Test Suite")
    print("=" * 60)
    print("\nAvailable Tests:")
    print("1. Test Follow User")
    print("2. Test Unfollow User")
    print("3. Test Complete Follow/Unfollow Cycle")
    print("4. Test Get User Profile (Bonus)")
    print("5. Run All Tests")
    print("0. Exit")

    while True:
        choice = input("\n👉 Select test (0-5): ").strip()

        if choice == '0':
            print("\n👋 Exiting test suite")
            break
        elif choice == '1':
            test_follow_user()
        elif choice == '2':
            test_unfollow_user()
        elif choice == '3':
            test_follow_unfollow_cycle()
        elif choice == '4':
            test_get_user_profile()
        elif choice == '5':
            print("\n🚀 Running all tests...")
            test_get_user_profile()
            time.sleep(3)
            test_follow_user()
            time.sleep(3)
            test_unfollow_user()
            time.sleep(3)
            test_follow_unfollow_cycle()
        else:
            print("❌ Invalid choice, please select 0-5")


if __name__ == "__main__":
    main()
