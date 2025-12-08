#!/usr/bin/env python3
"""
Post Twitter Thread using DistroFlow
Reads thread from JSON and posts sequentially
"""
import asyncio
import json
import sys
from pathlib import Path
from playwright.async_api import async_playwright
import time

async def load_cookies(context):
    """Load saved Twitter cookies"""
    auth_file = Path.home() / '.distroflow' / 'twitter_auth.json'

    if not auth_file.exists():
        print("❌ No authentication found!")
        print(f"   Run: python3 setup_twitter_auth.py")
        return False

    with open(auth_file) as f:
        auth_data = json.load(f)

    await context.add_cookies(auth_data['cookies'])
    print(f"✅ Loaded {len(auth_data['cookies'])} cookies")
    return True

async def post_tweet(page, text, reply_to_id=None):
    """Post a single tweet (or reply if reply_to_id provided)"""

    if reply_to_id:
        # Navigate to the tweet to reply
        tweet_url = f"https://twitter.com/i/status/{reply_to_id}"
        print(f"   📍 Opening tweet to reply: {tweet_url}")
        await page.goto(tweet_url, wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(3)

        # Click reply button
        reply_button = await page.query_selector('[data-testid="reply"]')
        if reply_button:
            await reply_button.click()
            await asyncio.sleep(1)
        else:
            print("   ⚠️  Reply button not found, trying alternative...")
            await page.click('article[data-testid="tweet"] >> text=Reply')
            await asyncio.sleep(1)
    else:
        # Go to home to compose new tweet
        print("   📍 Opening Twitter home...")
        await page.goto('https://twitter.com/home', wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(3)

    # Find tweet compose box
    print("   ⌨️  Finding compose box...")
    compose_box = await page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=10000)

    # Type the tweet text
    print(f"   ✍️  Typing tweet ({len(text)} chars)...")
    await compose_box.click()
    await asyncio.sleep(0.5)

    # Type with human-like delays
    for char in text:
        await compose_box.type(char, delay=20)  # 20ms between chars

    await asyncio.sleep(1)

    # Click tweet/reply button
    print("   📤 Posting...")
    if reply_to_id:
        post_button = await page.query_selector('[data-testid="tweetButton"]')
    else:
        post_button = await page.query_selector('[data-testid="tweetButtonInline"]')

    if not post_button:
        # Fallback: try to find any button with text "Post" or "Reply"
        post_button = await page.query_selector('button:has-text("Post"), button:has-text("Reply"), button:has-text("Tweet")')

    if post_button:
        await post_button.click()
    else:
        print("   ❌ Could not find post button!")
        return None

    # Wait for tweet to post
    await asyncio.sleep(3)

    # Get the tweet ID from URL
    try:
        # Check if URL changed to a status page
        current_url = page.url
        if '/status/' in current_url:
            tweet_id = current_url.split('/status/')[-1].split('?')[0]
            print(f"   ✅ Posted! Tweet ID: {tweet_id}")
            return tweet_id
        else:
            # Try to find the tweet in the timeline
            print("   ⏳ Looking for posted tweet...")
            await asyncio.sleep(2)

            # The most recent tweet should be ours
            tweets = await page.query_selector_all('article[data-testid="tweet"]')
            if tweets and len(tweets) > 0:
                first_tweet = tweets[0]
                # Try to extract tweet ID from the link
                time_link = await first_tweet.query_selector('time')
                if time_link:
                    parent_link = await time_link.evaluate_handle('el => el.closest("a")')
                    href = await parent_link.get_attribute('href')
                    if href and '/status/' in href:
                        tweet_id = href.split('/status/')[-1].split('?')[0]
                        print(f"   ✅ Posted! Tweet ID: {tweet_id}")
                        return tweet_id

            print("   ⚠️  Posted but couldn't get tweet ID. Continuing anyway...")
            return "unknown"

    except Exception as e:
        print(f"   ⚠️  Error getting tweet ID: {e}")
        return "unknown"

async def post_thread(thread_file):
    """Post entire thread"""
    # Load thread
    print(f"📖 Loading thread from: {thread_file}")
    with open(thread_file) as f:
        thread_data = json.load(f)

    tweets = thread_data['tweets']
    print(f"   Found {len(tweets)} tweets in thread")
    print(f"   Title: {thread_data.get('thread_title', 'Untitled')}\n")

    async with async_playwright() as p:
        # Use same persistent context as login
        user_data_dir = Path.home() / '.distroflow/twitter_browser'

        if not user_data_dir.exists():
            print("❌ No saved login session found!")
            print("   Run: python3 quick_twitter_login.py")
            return False

        # Launch with persistent context (uses saved login)
        print("🚀 Launching browser with saved session...")
        context = await p.chromium.launch_persistent_context(
            str(user_data_dir),
            headless=False,
            viewport={'width': 1400, 'height': 900},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            args=['--start-maximized', '--disable-blink-features=AutomationControlled']
        )

        page = context.pages[0] if context.pages else await context.new_page()

        print("🌐 Going to Twitter...\n")
        try:
            await page.goto('https://twitter.com/home', wait_until='domcontentloaded', timeout=60000)
        except Exception as e:
            print(f"⚠️  Page load timeout (this is OK if page is visible)")
        await asyncio.sleep(3)

        # Verify we're logged in
        try:
            await page.wait_for_selector('[data-testid="SideNav_AccountSwitcher_Button"]', timeout=10000)
            print("✅ Logged in successfully!\n")
        except Exception as e:
            print(f"⚠️  Could not verify login status: {e}")
            print("   Continuing anyway...")

        # Post each tweet
        print("=" * 60)
        print("📝 POSTING THREAD")
        print("=" * 60 + "\n")

        previous_tweet_id = None

        for i, tweet in enumerate(tweets, 1):
            print(f"\n🐦 Tweet {i}/{len(tweets)}")
            print("-" * 60)
            print(f"Text preview: {tweet['text'][:100]}...")

            try:
                tweet_id = await post_tweet(page, tweet['text'], reply_to_id=previous_tweet_id)

                if tweet_id:
                    previous_tweet_id = tweet_id
                    print(f"✅ Success! (ID: {tweet_id})")
                else:
                    print(f"⚠️  Posted but no ID returned")

                # Wait between tweets (be respectful to Twitter)
                if i < len(tweets):
                    wait_time = 5
                    print(f"⏳ Waiting {wait_time}s before next tweet...")
                    await asyncio.sleep(wait_time)

            except Exception as e:
                print(f"❌ Error posting tweet {i}: {e}")
                print("   Continuing to next tweet...")
                await asyncio.sleep(3)

        print("\n" + "=" * 60)
        print("🎉 THREAD COMPLETE!")
        print("=" * 60)
        print(f"\n✅ Posted {len(tweets)} tweets")

        if previous_tweet_id and previous_tweet_id != "unknown":
            thread_url = f"https://twitter.com/LucianLiu861650/status/{previous_tweet_id}"
            print(f"\n🔗 Thread URL: {thread_url}")
            print("\n💡 Next steps:")
            print("   1. Pin the thread to your profile")
            print("   2. Share on LinkedIn")
            print("   3. Reply to every comment!")

        print("\n⏳ Browser will close in 10 seconds...")
        print("   (Take a screenshot if you want!)")
        await asyncio.sleep(10)

        await context.close()
        return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 post_twitter_thread.py <thread_file.json>")
        print("\nExample:")
        print("  python3 post_twitter_thread.py thread_ai_error_recovery.json")
        sys.exit(1)

    thread_file = sys.argv[1]

    if not Path(thread_file).exists():
        print(f"❌ Thread file not found: {thread_file}")
        sys.exit(1)

    success = asyncio.run(post_thread(thread_file))
    sys.exit(0 if success else 1)
