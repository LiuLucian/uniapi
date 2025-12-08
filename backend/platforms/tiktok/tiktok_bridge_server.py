#!/usr/bin/env python3
"""
TikTok Bridge Server - Flask API for TikTok Automation
Similar to Instagram Bridge Server architecture

Port: 5003
"""

import asyncio
import json
import logging
import os
from flask import Flask, request, jsonify
from playwright.async_api import async_playwright

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


class TikTokOperations:
    """TikTok operations using Playwright"""

    def __init__(self, auth_file: str = "platforms_auth.json"):
        self.auth_file = auth_file
        self.sessionid = self._load_sessionid()

    def _load_sessionid(self) -> str:
        """Load TikTok sessionid from auth file"""
        try:
            with open(self.auth_file, 'r') as f:
                config = json.load(f)
                tiktok_auth = config.get('tiktok', {})
                return tiktok_auth.get('sessionid', '')
        except Exception as e:
            logger.error(f"Error loading auth: {e}")
            return ''

    async def get_user_profile(self, username: str) -> dict:
        """
        Get TikTok user profile information

        Args:
            username: TikTok username (e.g., '@charlidamelio')

        Returns:
            User profile data
        """
        if not self.sessionid:
            return {'success': False, 'error': 'No TikTok session found'}

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled']
                )

                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )

                # Add cookies
                await context.add_cookies([{
                    'name': 'sessionid',
                    'value': self.sessionid,
                    'domain': '.tiktok.com',
                    'path': '/',
                    'httpOnly': True,
                    'secure': True
                }])

                page = await context.new_page()

                # Navigate to user profile
                username_clean = username.replace('@', '')
                url = f'https://www.tiktok.com/@{username_clean}'

                logger.info(f"📍 Getting profile: {username_clean}")
                await page.goto(url, timeout=30000)
                await asyncio.sleep(3)

                # Extract profile data
                profile_data = {
                    'username': username_clean,
                    'success': True
                }

                # Get follower count
                try:
                    followers_elem = await page.query_selector('[data-e2e="followers-count"]')
                    if followers_elem:
                        followers_text = await followers_elem.inner_text()
                        profile_data['followers'] = followers_text.strip()
                except:
                    profile_data['followers'] = 'Unknown'

                # Get following count
                try:
                    following_elem = await page.query_selector('[data-e2e="following-count"]')
                    if following_elem:
                        following_text = await following_elem.inner_text()
                        profile_data['following'] = following_text.strip()
                except:
                    profile_data['following'] = 'Unknown'

                # Get likes count
                try:
                    likes_elem = await page.query_selector('[data-e2e="likes-count"]')
                    if likes_elem:
                        likes_text = await likes_elem.inner_text()
                        profile_data['likes'] = likes_text.strip()
                except:
                    profile_data['likes'] = 'Unknown'

                # Get bio
                try:
                    bio_elem = await page.query_selector('[data-e2e="user-bio"]')
                    if bio_elem:
                        bio_text = await bio_elem.inner_text()
                        profile_data['bio'] = bio_text.strip()
                except:
                    profile_data['bio'] = ''

                profile_data['profile_url'] = url

                await browser.close()
                return profile_data

        except Exception as e:
            logger.error(f"Error getting profile: {e}")
            return {'success': False, 'error': str(e)}

    async def get_user_videos(self, username: str, max_count: int = 10) -> dict:
        """
        Get user's recent videos

        Args:
            username: TikTok username
            max_count: Maximum number of videos to retrieve

        Returns:
            List of videos
        """
        if not self.sessionid:
            return {'success': False, 'error': 'No TikTok session found'}

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled']
                )

                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )

                await context.add_cookies([{
                    'name': 'sessionid',
                    'value': self.sessionid,
                    'domain': '.tiktok.com',
                    'path': '/',
                    'httpOnly': True,
                    'secure': True
                }])

                page = await context.new_page()

                username_clean = username.replace('@', '')
                url = f'https://www.tiktok.com/@{username_clean}'

                logger.info(f"📍 Getting videos from: {username_clean}")
                await page.goto(url, timeout=30000)
                await asyncio.sleep(3)

                # Scroll to load videos
                for _ in range(3):
                    await page.evaluate('window.scrollBy(0, 1000)')
                    await asyncio.sleep(1)

                # Get video elements
                video_elements = await page.query_selector_all('[data-e2e="user-post-item"]')

                videos = []
                for i, elem in enumerate(video_elements[:max_count]):
                    try:
                        # Get video link
                        link_elem = await elem.query_selector('a')
                        video_url = ''
                        if link_elem:
                            video_url = await link_elem.get_attribute('href')
                            if video_url and not video_url.startswith('http'):
                                video_url = f'https://www.tiktok.com{video_url}'

                        # Get view count
                        views_elem = await elem.query_selector('[data-e2e="video-views"]')
                        views = 'Unknown'
                        if views_elem:
                            views = await views_elem.inner_text()

                        videos.append({
                            'video_url': video_url,
                            'views': views,
                            'index': i
                        })
                    except Exception as e:
                        logger.error(f"Error extracting video {i}: {e}")
                        continue

                await browser.close()

                return {
                    'success': True,
                    'username': username_clean,
                    'videos': videos,
                    'count': len(videos)
                }

        except Exception as e:
            logger.error(f"Error getting videos: {e}")
            return {'success': False, 'error': str(e)}

    async def like_video(self, video_url: str) -> dict:
        """
        Like a TikTok video

        Args:
            video_url: Full TikTok video URL

        Returns:
            Success status
        """
        if not self.sessionid:
            return {'success': False, 'error': 'No TikTok session found'}

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=False,
                    args=['--disable-blink-features=AutomationControlled']
                )

                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )

                await context.add_cookies([{
                    'name': 'sessionid',
                    'value': self.sessionid,
                    'domain': '.tiktok.com',
                    'path': '/',
                    'httpOnly': True,
                    'secure': True
                }])

                page = await context.new_page()

                logger.info(f"📍 Liking video: {video_url}")
                await page.goto(video_url, timeout=30000)
                await asyncio.sleep(3)

                # Find and click like button
                like_selectors = [
                    '[data-e2e="like-icon"]',
                    '[data-e2e="browse-like-icon"]',
                    'button[aria-label*="like"]',
                    'button[aria-label*="Like"]'
                ]

                liked = False
                for selector in like_selectors:
                    try:
                        button = await page.wait_for_selector(selector, timeout=3000)
                        if button and await button.is_visible():
                            await button.click()
                            logger.info(f"✅ Clicked like button: {selector}")
                            liked = True
                            await asyncio.sleep(2)
                            break
                    except:
                        continue

                await browser.close()

                if liked:
                    return {'success': True, 'message': 'Video liked successfully'}
                else:
                    return {'success': False, 'error': 'Could not find like button'}

        except Exception as e:
            logger.error(f"Error liking video: {e}")
            return {'success': False, 'error': str(e)}

    async def comment_on_video(self, video_url: str, comment_text: str) -> dict:
        """
        Comment on a TikTok video

        Args:
            video_url: Full TikTok video URL
            comment_text: Comment text

        Returns:
            Success status
        """
        if not self.sessionid:
            return {'success': False, 'error': 'No TikTok session found'}

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=False,
                    args=['--disable-blink-features=AutomationControlled']
                )

                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )

                await context.add_cookies([{
                    'name': 'sessionid',
                    'value': self.sessionid,
                    'domain': '.tiktok.com',
                    'path': '/',
                    'httpOnly': True,
                    'secure': True
                }])

                page = await context.new_page()

                logger.info(f"📍 Commenting on: {video_url}")
                await page.goto(video_url, timeout=30000)
                await asyncio.sleep(3)

                # Find comment input
                comment_selectors = [
                    '[data-e2e="comment-input"]',
                    'input[placeholder*="comment"]',
                    'textarea[placeholder*="comment"]'
                ]

                commented = False
                for selector in comment_selectors:
                    try:
                        input_elem = await page.wait_for_selector(selector, timeout=3000)
                        if input_elem and await input_elem.is_visible():
                            await input_elem.click()
                            await asyncio.sleep(1)
                            await input_elem.fill(comment_text)
                            await asyncio.sleep(1)

                            # Press Enter to submit
                            await page.keyboard.press('Enter')
                            logger.info(f"✅ Comment posted")
                            commented = True
                            await asyncio.sleep(2)
                            break
                    except:
                        continue

                await browser.close()

                if commented:
                    return {'success': True, 'message': 'Comment posted successfully'}
                else:
                    return {'success': False, 'error': 'Could not find comment input'}

        except Exception as e:
            logger.error(f"Error commenting: {e}")
            return {'success': False, 'error': str(e)}

    async def follow_user(self, username: str) -> dict:
        """
        Follow a TikTok user

        Args:
            username: TikTok username

        Returns:
            Success status
        """
        if not self.sessionid:
            return {'success': False, 'error': 'No TikTok session found'}

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=False,
                    args=['--disable-blink-features=AutomationControlled']
                )

                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )

                await context.add_cookies([{
                    'name': 'sessionid',
                    'value': self.sessionid,
                    'domain': '.tiktok.com',
                    'path': '/',
                    'httpOnly': True,
                    'secure': True
                }])

                page = await context.new_page()

                username_clean = username.replace('@', '')
                url = f'https://www.tiktok.com/@{username_clean}'

                logger.info(f"📍 Following: {username_clean}")
                await page.goto(url, timeout=30000)
                await asyncio.sleep(3)

                # Find and click follow button
                follow_selectors = [
                    '[data-e2e="follow-button"]',
                    'button:has-text("Follow")',
                    'button[aria-label*="Follow"]'
                ]

                followed = False
                for selector in follow_selectors:
                    try:
                        button = await page.wait_for_selector(selector, timeout=3000)
                        if button and await button.is_visible():
                            await button.click()
                            logger.info(f"✅ Clicked follow button")
                            followed = True
                            await asyncio.sleep(2)
                            break
                    except:
                        continue

                await browser.close()

                if followed:
                    return {'success': True, 'message': f'Followed @{username_clean}'}
                else:
                    return {'success': False, 'error': 'Could not find follow button'}

        except Exception as e:
            logger.error(f"Error following user: {e}")
            return {'success': False, 'error': str(e)}

    async def send_dm(self, username: str, message: str) -> dict:
        """
        Send direct message to a TikTok user

        Args:
            username: TikTok username
            message: Message text

        Returns:
            Success status
        """
        if not self.sessionid:
            return {'success': False, 'error': 'No TikTok session found'}

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=False,
                    args=['--disable-blink-features=AutomationControlled']
                )

                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )

                await context.add_cookies([{
                    'name': 'sessionid',
                    'value': self.sessionid,
                    'domain': '.tiktok.com',
                    'path': '/',
                    'httpOnly': True,
                    'secure': True
                }])

                page = await context.new_page()

                username_clean = username.replace('@', '')

                logger.info(f"📍 Sending DM to: {username_clean}")

                # Go to messages page
                await page.goto('https://www.tiktok.com/messages', timeout=30000)
                await asyncio.sleep(3)

                # Search for user
                search_input = await page.query_selector('input[placeholder*="Search"]')
                if search_input:
                    await search_input.fill(username_clean)
                    await asyncio.sleep(2)

                # Click on user
                user_elem = await page.query_selector(f'text={username_clean}')
                if user_elem:
                    await user_elem.click()
                    await asyncio.sleep(2)

                # Type and send message
                message_input = await page.query_selector('[data-e2e="dm-input"]')
                if not message_input:
                    message_input = await page.query_selector('textarea')

                if message_input:
                    await message_input.fill(message)
                    await asyncio.sleep(1)
                    await page.keyboard.press('Enter')
                    await asyncio.sleep(2)

                    await browser.close()
                    return {'success': True, 'message': f'DM sent to @{username_clean}'}
                else:
                    await browser.close()
                    return {'success': False, 'error': 'Could not find message input'}

        except Exception as e:
            logger.error(f"Error sending DM: {e}")
            return {'success': False, 'error': str(e)}


# Initialize TikTok operations
tiktok_ops = TikTokOperations()


# Flask Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'TikTok Bridge Server is running',
        'session_configured': bool(tiktok_ops.sessionid)
    })


@app.route('/user/<username>', methods=['GET'])
def get_user(username):
    """Get user profile"""
    logger.info(f"👤 Getting user @{username}")

    result = asyncio.run(tiktok_ops.get_user_profile(username))

    if result.get('success'):
        return jsonify(result)
    else:
        return jsonify(result), 500


@app.route('/user/<username>/videos', methods=['GET'])
def get_user_videos(username):
    """Get user's videos"""
    max_count = request.args.get('max_count', default=10, type=int)

    logger.info(f"📹 Getting videos from @{username} (max: {max_count})")

    result = asyncio.run(tiktok_ops.get_user_videos(username, max_count))

    if result.get('success'):
        return jsonify(result)
    else:
        return jsonify(result), 500


@app.route('/video/like', methods=['POST'])
def like_video():
    """Like a video"""
    data = request.get_json()
    video_url = data.get('video_url')

    if not video_url:
        return jsonify({'success': False, 'error': 'video_url required'}), 400

    logger.info(f"❤️ Liking video: {video_url}")

    result = asyncio.run(tiktok_ops.like_video(video_url))

    if result.get('success'):
        return jsonify(result)
    else:
        return jsonify(result), 500


@app.route('/video/comment', methods=['POST'])
def comment_video():
    """Comment on a video"""
    data = request.get_json()
    video_url = data.get('video_url')
    comment_text = data.get('text')

    if not video_url or not comment_text:
        return jsonify({'success': False, 'error': 'video_url and text required'}), 400

    logger.info(f"💬 Commenting on: {video_url}")

    result = asyncio.run(tiktok_ops.comment_on_video(video_url, comment_text))

    if result.get('success'):
        return jsonify(result)
    else:
        return jsonify(result), 500


@app.route('/user/<username>/follow', methods=['POST'])
def follow_user(username):
    """Follow a user"""
    logger.info(f"👥 Following @{username}")

    result = asyncio.run(tiktok_ops.follow_user(username))

    if result.get('success'):
        return jsonify(result)
    else:
        return jsonify(result), 500


@app.route('/dm/send', methods=['POST'])
def send_dm():
    """Send direct message"""
    data = request.get_json()
    username = data.get('username')
    message = data.get('message')

    if not username or not message:
        return jsonify({'success': False, 'error': 'username and message required'}), 400

    logger.info(f"✉️ Sending DM to @{username}")

    result = asyncio.run(tiktok_ops.send_dm(username, message))

    if result.get('success'):
        return jsonify(result)
    else:
        return jsonify(result), 500


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🚀 TikTok Bridge Server Starting...")
    logger.info("=" * 60)
    logger.info(f"✅ Server ready on http://localhost:5003")
    logger.info("=" * 60)

    app.run(host='0.0.0.0', port=5003, debug=False)
