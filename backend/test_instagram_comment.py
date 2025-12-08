#!/usr/bin/env python3
"""
Test Instagram Comment API Endpoint
"""
import requests
import json
import time
from datetime import datetime

# API endpoints
BASE_URL = "http://localhost:8000/api/v1/instagram"

def test_post_comment():
    """Test commenting on an Instagram post"""
    print("=" * 60)
    print("📤 Testing Instagram Comment API")
    print("=" * 60)

    # Get post URL
    post_url = input("\n🔗 Enter Instagram post URL to comment on: ").strip()

    if not post_url:
        print("❌ No URL provided")
        return

    # Extract media_id from URL
    if '/p/' in post_url:
        media_id = post_url.split('/p/')[-1].rstrip('/').split('/')[0]
    else:
        media_id = post_url

    # Get comment text
    print("\n💬 Enter your comment:")
    print("   (Press Enter twice when done, or Ctrl+C to cancel)")
    print()

    comment_lines = []
    try:
        while True:
            line = input()
            if not line and comment_lines:
                break
            comment_lines.append(line)
    except KeyboardInterrupt:
        print("\n❌ Cancelled")
        return

    comment_text = '\n'.join(comment_lines).strip()

    if not comment_text:
        print("❌ No comment text provided")
        return

    print(f"\n📝 Media ID: {media_id}")
    print(f"💬 Comment: {comment_text[:50]}..." if len(comment_text) > 50 else f"💬 Comment: {comment_text}")
    print(f"🎯 Endpoint: POST {BASE_URL}/media/{media_id}/comments")
    print("\n⏳ Posting comment...")
    print("   (This may take 10-15 seconds with browser automation)")
    print()

    try:
        response = requests.post(
            f"{BASE_URL}/media/{media_id}/comments",
            json={"text": comment_text},
            timeout=60
        )

        print(f"📊 Status Code: {response.status_code}")
        print("\n📥 Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))

        if response.status_code == 200 and response.json().get('success'):
            print("\n✅ SUCCESS: Comment posted!")
            return True
        else:
            print("\n❌ FAILED: Could not post comment")
            return False

    except requests.exceptions.Timeout:
        print("\n⏰ Request timed out (>60s)")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_multiple_comments():
    """Test posting multiple comments to the same post"""
    print("\n" + "=" * 60)
    print("📤 Testing Multiple Comments")
    print("=" * 60)

    post_url = input("\n🔗 Enter Instagram post URL: ").strip()

    if not post_url:
        print("❌ No URL provided")
        return

    if '/p/' in post_url:
        media_id = post_url.split('/p/')[-1].rstrip('/').split('/')[0]
    else:
        media_id = post_url

    num_comments = input("\n🔢 How many test comments? (1-5): ").strip()

    try:
        num_comments = int(num_comments)
        if num_comments < 1 or num_comments > 5:
            print("❌ Please enter a number between 1 and 5")
            return
    except ValueError:
        print("❌ Invalid number")
        return

    print(f"\n📝 Will post {num_comments} test comments")
    print("⏳ Starting in 3 seconds...")
    time.sleep(3)

    success_count = 0
    fail_count = 0

    for i in range(1, num_comments + 1):
        timestamp = datetime.now().strftime("%H:%M:%S")
        comment_text = f"Test comment #{i} posted at {timestamp}"

        print(f"\n📍 Comment {i}/{num_comments}: {comment_text}")

        try:
            response = requests.post(
                f"{BASE_URL}/media/{media_id}/comments",
                json={"text": comment_text},
                timeout=60
            )

            result = response.json()

            if result.get('success'):
                print(f"   ✅ Success")
                success_count += 1
            else:
                print(f"   ❌ Failed: {result.get('message', 'Unknown error')}")
                fail_count += 1

            # Wait between comments to avoid rate limiting
            if i < num_comments:
                wait_time = 10
                print(f"   ⏳ Waiting {wait_time}s before next comment...")
                time.sleep(wait_time)

        except Exception as e:
            print(f"   ❌ Error: {e}")
            fail_count += 1

    print(f"\n📊 Results:")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ❌ Failed: {fail_count}")

    if success_count == num_comments:
        print("\n🎉 ALL COMMENTS POSTED SUCCESSFULLY!")
        return True
    else:
        print(f"\n⚠️  Some comments failed ({fail_count}/{num_comments})")
        return False


def test_comment_with_emojis():
    """Test commenting with emojis and special characters"""
    print("\n" + "=" * 60)
    print("📤 Testing Comment with Emojis")
    print("=" * 60)

    post_url = input("\n🔗 Enter Instagram post URL: ").strip()

    if not post_url:
        print("❌ No URL provided")
        return

    if '/p/' in post_url:
        media_id = post_url.split('/p/')[-1].rstrip('/').split('/')[0]
    else:
        media_id = post_url

    # Predefined emoji-rich comments
    emoji_comments = [
        "🔥🔥🔥 This is amazing!",
        "😍 Love this! 💕",
        "👏👏👏 Great work!",
        "🎉🎊 Congratulations! 🥳",
        "✨ So beautiful! 🌟"
    ]

    print("\n💬 Select a comment:")
    for idx, comment in enumerate(emoji_comments, 1):
        print(f"   {idx}. {comment}")
    print("   0. Custom comment")

    choice = input("\n👉 Your choice (0-5): ").strip()

    try:
        choice = int(choice)
        if choice < 0 or choice > len(emoji_comments):
            print("❌ Invalid choice")
            return
    except ValueError:
        print("❌ Invalid input")
        return

    if choice == 0:
        comment_text = input("\n💬 Enter your custom comment: ").strip()
    else:
        comment_text = emoji_comments[choice - 1]

    if not comment_text:
        print("❌ No comment text")
        return

    print(f"\n📝 Comment: {comment_text}")
    print(f"🎯 Endpoint: POST {BASE_URL}/media/{media_id}/comments")
    print("\n⏳ Posting comment...")
    print()

    try:
        response = requests.post(
            f"{BASE_URL}/media/{media_id}/comments",
            json={"text": comment_text},
            timeout=60
        )

        print(f"📊 Status Code: {response.status_code}")
        print("\n📥 Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))

        if response.status_code == 200 and response.json().get('success'):
            print("\n✅ SUCCESS: Emoji comment posted!")
            return True
        else:
            print("\n❌ FAILED: Could not post comment")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def main():
    """Main test menu"""
    print("\n" + "=" * 60)
    print("🧪 Instagram Comment API Test Suite")
    print("=" * 60)
    print("\nAvailable Tests:")
    print("1. Test Single Comment")
    print("2. Test Multiple Comments (Batch)")
    print("3. Test Comment with Emojis")
    print("4. Run All Tests")
    print("0. Exit")

    while True:
        choice = input("\n👉 Select test (0-4): ").strip()

        if choice == '0':
            print("\n👋 Exiting test suite")
            break
        elif choice == '1':
            test_post_comment()
        elif choice == '2':
            test_multiple_comments()
        elif choice == '3':
            test_comment_with_emojis()
        elif choice == '4':
            print("\n🚀 Running all tests...")
            print("\n--- Test 1: Single Comment ---")
            test_post_comment()
            time.sleep(5)
            print("\n--- Test 2: Multiple Comments ---")
            test_multiple_comments()
            time.sleep(5)
            print("\n--- Test 3: Emoji Comment ---")
            test_comment_with_emojis()
        else:
            print("❌ Invalid choice, please select 0-4")


if __name__ == "__main__":
    main()
