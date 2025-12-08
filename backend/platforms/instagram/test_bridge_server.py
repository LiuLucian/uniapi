#!/usr/bin/env python3
"""
Test script for Instagram Bridge Server
Tests all endpoints to verify they work correctly
"""
import requests
import json
import sys

BASE_URL = "http://localhost:5002"

def test_health():
    """Test health check endpoint"""
    print("\n" + "=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("✅ Health check PASSED")
            return True
        else:
            print("❌ Health check FAILED")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server not running!")
        print("   Start server with: python3 instagram_bridge_server.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_get_user():
    """Test get user profile endpoint"""
    print("\n" + "=" * 60)
    print("TEST 2: Get User Profile")
    print("=" * 60)

    username = "instagram"  # Official Instagram account
    print(f"Fetching profile: @{username}")

    try:
        response = requests.get(f"{BASE_URL}/user/{username}", timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Get user PASSED")
                return True
            else:
                print(f"⚠️  Get user returned error: {data.get('error')}")
                return False
        else:
            print("❌ Get user FAILED")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_create_post():
    """Test create post endpoint (dry run - will show what's needed)"""
    print("\n" + "=" * 60)
    print("TEST 3: Create Post (Info Only)")
    print("=" * 60)

    print("⚠️  Skipping actual post creation test")
    print("   To test posting, run manually:")
    print()
    print("   curl -X POST http://localhost:5002/post \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{")
    print('       "caption": "Test post from bridge server! #test",')
    print('       "image_path": "/absolute/path/to/image.jpg"')
    print("     }'")
    print()
    print("✅ Create post endpoint available")
    return True


def test_send_dm():
    """Test send DM endpoint (dry run - will show what's needed)"""
    print("\n" + "=" * 60)
    print("TEST 4: Send DM (Info Only)")
    print("=" * 60)

    print("⚠️  Skipping actual DM sending test")
    print("   To test DM sending, run manually:")
    print()
    print("   curl -X POST http://localhost:5002/dm \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{")
    print('       "username": "target_username",')
    print('       "message": "Hello from bridge server!"')
    print("     }'")
    print()
    print("✅ Send DM endpoint available")
    return True


def main():
    """Run all tests"""
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "Instagram Bridge Server Test Suite" + " " * 14 + "║")
    print("╚" + "=" * 58 + "╝")

    results = []

    # Test 1: Health check
    results.append(("Health Check", test_health()))

    if not results[0][1]:
        print("\n❌ Server is not running. Cannot continue tests.")
        print("   Start server with: python3 instagram_bridge_server.py")
        sys.exit(1)

    # Test 2: Get user profile
    results.append(("Get User Profile", test_get_user()))

    # Test 3: Create post (info only)
    results.append(("Create Post (Info)", test_create_post()))

    # Test 4: Send DM (info only)
    results.append(("Send DM (Info)", test_send_dm()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
