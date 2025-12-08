#!/usr/bin/env python3
"""
Twitter Bridge Server - 连接Postiz和Playwright
在宿主机运行，接收Postiz的发帖请求，使用Playwright真实发送
"""
import asyncio
import json
from pathlib import Path
from flask import Flask, request, jsonify
from playwright.async_api import async_playwright
import logging
from twitter_operations import TwitterOperations

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
twitter_ops = TwitterOperations()

async def post_single_tweet(page, text, reply_to_id=None):
    """Post a single tweet"""
    try:
        if reply_to_id:
            # Reply to tweet
            tweet_url = f"https://twitter.com/i/status/{reply_to_id}"
            logger.info(f"📍 Opening tweet to reply: {tweet_url}")
            await page.goto(tweet_url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(3)

            # Click reply button
            reply_button = await page.query_selector('[data-testid="reply"]')
            if reply_button:
                await reply_button.click()
                await asyncio.sleep(1)
        else:
            # New tweet
            logger.info("📍 Opening Twitter home...")
            await page.goto('https://twitter.com/home', wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(3)

        # Find compose box
        logger.info("⌨️  Finding compose box...")
        compose_box = await page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=10000)

        # Type tweet
        logger.info(f"✍️  Typing tweet ({len(text)} chars)...")
        await compose_box.click()
        await asyncio.sleep(0.5)

        # Type with delays
        await compose_box.fill(text)
        await asyncio.sleep(1)

        # Click post button
        logger.info("📤 Posting...")
        if reply_to_id:
            post_button = await page.query_selector('[data-testid="tweetButton"]')
        else:
            post_button = await page.query_selector('[data-testid="tweetButtonInline"]')

        if not post_button:
            post_button = await page.query_selector('button:has-text("Post"), button:has-text("Reply"), button:has-text("Tweet")')

        if post_button:
            await post_button.click()
        else:
            logger.error("❌ Could not find post button!")
            return None

        # Wait for post
        await asyncio.sleep(3)

        # Get tweet ID
        current_url = page.url
        if '/status/' in current_url:
            tweet_id = current_url.split('/status/')[-1].split('?')[0]
            logger.info(f"✅ Posted! Tweet ID: {tweet_id}")
            return tweet_id
        else:
            # Try to find from timeline
            await asyncio.sleep(2)
            tweets = await page.query_selector_all('article[data-testid="tweet"]')
            if tweets and len(tweets) > 0:
                first_tweet = tweets[0]
                time_link = await first_tweet.query_selector('time')
                if time_link:
                    parent_link = await time_link.evaluate_handle('el => el.closest("a")')
                    href = await parent_link.get_attribute('href')
                    if href and '/status/' in href:
                        tweet_id = href.split('/status/')[-1].split('?')[0]
                        logger.info(f"✅ Posted! Tweet ID: {tweet_id}")
                        return tweet_id

            logger.warning("⚠️  Posted but couldn't get tweet ID")
            return "unknown"

    except Exception as e:
        logger.error(f"❌ Error posting tweet: {e}")
        return None

async def post_tweets_task(tweets):
    """完整的发推任务 - 启动浏览器、发推、关闭浏览器"""
    user_data_dir = Path.home() / '.distroflow/twitter_browser'

    if not user_data_dir.exists():
        logger.error("❌ No saved login session found!")
        return None

    logger.info("🚀 Launching browser...")

    async with async_playwright() as p:
        # Launch browser with persistent context
        context = await p.chromium.launch_persistent_context(
            str(user_data_dir),
            headless=False,  # Twitter检测headless
            viewport={'width': 1400, 'height': 900},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            args=[
                '--disable-blink-features=AutomationControlled',
                '--start-maximized',
                '--no-sandbox'
            ]
        )

        page = context.pages[0] if context.pages else await context.new_page()

        # Verify login
        try:
            await page.goto('https://twitter.com/home', wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(2)
            await page.wait_for_selector('[data-testid="SideNav_AccountSwitcher_Button"]', timeout=10000)
            logger.info("✅ Logged in successfully!")
        except Exception as e:
            logger.error(f"❌ Failed to verify login: {e}")
            await context.close()
            return None

        # Post tweets
        tweet_ids = []
        previous_id = None

        for i, tweet in enumerate(tweets):
            text = tweet.get('text', '')
            if not text:
                continue

            logger.info(f"🐦 Posting tweet {i+1}/{len(tweets)}")
            tweet_id = await post_single_tweet(page, text, reply_to_id=previous_id)

            if tweet_id:
                tweet_ids.append(tweet_id)
                previous_id = tweet_id

            # Wait between tweets
            if i < len(tweets) - 1:
                await asyncio.sleep(5)

        # Close browser
        await context.close()
        logger.info("🔒 Browser closed")

        return tweet_ids

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Twitter Bridge Server is running'
    })

@app.route('/post', methods=['POST'])
def post_tweet_endpoint():
    """
    Post tweet(s) endpoint
    Request body:
    {
        "tweets": [
            {"text": "First tweet"},
            {"text": "Second tweet (reply)"}
        ]
    }
    Response:
    {
        "success": true,
        "tweet_ids": ["123", "456"],
        "urls": ["https://twitter.com/user/status/123", ...]
    }
    """
    try:
        data = request.get_json()
        tweets = data.get('tweets', [])

        if not tweets:
            return jsonify({'error': 'No tweets provided'}), 400

        logger.info(f"📝 Received request to post {len(tweets)} tweet(s)")

        # Run the complete task in a new event loop (like terminal execution)
        tweet_ids = asyncio.run(post_tweets_task(tweets))

        if not tweet_ids:
            return jsonify({'error': 'Failed to post tweets'}), 500

        # Build URLs
        urls = [f"https://twitter.com/LucianLiu861650/status/{tid}" for tid in tweet_ids if tid != "unknown"]

        return jsonify({
            'success': True,
            'tweet_ids': tweet_ids,
            'urls': urls,
            'count': len(tweet_ids)
        })

    except Exception as e:
        logger.error(f"❌ Error in post endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/like', methods=['POST'])
def like_tweet_endpoint():
    """
    Like a tweet
    Request body: {"tweet_id": "1234567890"}
    Response: {"success": true, "tweet_id": "1234567890", "action": "liked"}
    """
    try:
        data = request.get_json()
        tweet_id = data.get('tweet_id')

        if not tweet_id:
            return jsonify({'error': 'tweet_id required'}), 400

        logger.info(f"👍 Liking tweet {tweet_id}")
        result = asyncio.run(twitter_ops.like_tweet(tweet_id))

        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ Error liking tweet: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/unlike', methods=['POST'])
def unlike_tweet_endpoint():
    """
    Unlike a tweet
    Request body: {"tweet_id": "1234567890"}
    Response: {"success": true, "tweet_id": "1234567890", "action": "unliked"}
    """
    try:
        data = request.get_json()
        tweet_id = data.get('tweet_id')

        if not tweet_id:
            return jsonify({'error': 'tweet_id required'}), 400

        logger.info(f"👎 Unliking tweet {tweet_id}")
        result = asyncio.run(twitter_ops.unlike_tweet(tweet_id))

        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ Error unliking tweet: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/retweet', methods=['POST'])
def retweet_endpoint():
    """
    Retweet a tweet
    Request body: {"tweet_id": "1234567890"}
    Response: {"success": true, "tweet_id": "1234567890", "action": "retweeted"}
    """
    try:
        data = request.get_json()
        tweet_id = data.get('tweet_id')

        if not tweet_id:
            return jsonify({'error': 'tweet_id required'}), 400

        logger.info(f"🔁 Retweeting tweet {tweet_id}")
        result = asyncio.run(twitter_ops.retweet(tweet_id))

        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ Error retweeting: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/unretweet', methods=['POST'])
def unretweet_endpoint():
    """
    Undo retweet
    Request body: {"tweet_id": "1234567890"}
    Response: {"success": true, "tweet_id": "1234567890", "action": "unretweeted"}
    """
    try:
        data = request.get_json()
        tweet_id = data.get('tweet_id')

        if not tweet_id:
            return jsonify({'error': 'tweet_id required'}), 400

        logger.info(f"↩️  Unretweeting tweet {tweet_id}")
        result = asyncio.run(twitter_ops.unretweet(tweet_id))

        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ Error unretweeting: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/tweet/<tweet_id>', methods=['DELETE'])
def delete_tweet_endpoint(tweet_id):
    """
    Delete a tweet
    Response: {"success": true, "tweet_id": "1234567890", "action": "deleted"}
    """
    try:
        logger.info(f"🗑️  Deleting tweet {tweet_id}")
        result = asyncio.run(twitter_ops.delete_tweet(tweet_id))

        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ Error deleting tweet: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/tweet/<tweet_id>', methods=['GET'])
def get_tweet_endpoint(tweet_id):
    """
    Get tweet details
    Response: {
        "id": "1234567890",
        "text": "Tweet content",
        "author_username": "username",
        "reply_count": "5",
        "retweet_count": "10",
        "like_count": "25"
    }
    """
    try:
        logger.info(f"📖 Getting tweet {tweet_id}")
        result = asyncio.run(twitter_ops.get_tweet(tweet_id))

        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ Error getting tweet: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/user/<username>', methods=['GET'])
def get_user_endpoint(username):
    """Get user profile by username"""
    try:
        logger.info(f"👤 Getting user @{username}")
        result = asyncio.run(twitter_ops.get_user_by_username(username))
        return jsonify(result)
    except Exception as e:
        logger.error(f"❌ Error getting user: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/follow', methods=['POST'])
def follow_user_endpoint():
    """Follow a user"""
    try:
        data = request.get_json()
        username = data.get('username')
        if not username:
            return jsonify({'error': 'username required'}), 400
        
        logger.info(f"➕ Following @{username}")
        result = asyncio.run(twitter_ops.follow_user(username))
        return jsonify(result)
    except Exception as e:
        logger.error(f"❌ Error following user: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/unfollow', methods=['POST'])
def unfollow_user_endpoint():
    """Unfollow a user"""
    try:
        data = request.get_json()
        username = data.get('username')
        if not username:
            return jsonify({'error': 'username required'}), 400
        
        logger.info(f"➖ Unfollowing @{username}")
        result = asyncio.run(twitter_ops.unfollow_user(username))
        return jsonify(result)
    except Exception as e:
        logger.error(f"❌ Error unfollowing user: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/user/<username>/tweets', methods=['GET'])
def get_user_tweets_endpoint(username):
    """Get user's recent tweets"""
    try:
        max_count = request.args.get('max_count', 20, type=int)
        logger.info(f"📝 Getting tweets from @{username}")
        result = asyncio.run(twitter_ops.get_user_tweets(username, max_count))
        return jsonify({'tweets': result, 'count': len(result)})
    except Exception as e:
        logger.error(f"❌ Error getting user tweets: {e}")
        return jsonify({'error': str(e)}), 500



@app.route('/search/tweets', methods=['GET'])
def search_tweets_endpoint():
    """Search recent tweets"""
    try:
        query = request.args.get('query', '')
        max_count = request.args.get('max_count', 20, type=int)
        
        if not query:
            return jsonify({'error': 'query parameter required'}), 400
        
        logger.info(f"🔍 Searching tweets: {query}")
        result = asyncio.run(twitter_ops.search_tweets(query, max_count))
        return jsonify({'tweets': result, 'count': len(result)})
    except Exception as e:
        logger.error(f"❌ Error searching tweets: {e}")
        return jsonify({'error': str(e)}), 500

def run_server():
    """Run the Flask server"""
    logger.info("=" * 60)
    logger.info("🚀 Twitter Bridge Server Starting...")
    logger.info("=" * 60)
    logger.info("✅ Server ready on http://localhost:5001")
    logger.info("=" * 60 + "\n")

    app.run(host='0.0.0.0', port=5001, debug=False)

if __name__ == '__main__':
    run_server()
