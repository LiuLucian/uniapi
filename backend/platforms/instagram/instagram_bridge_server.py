#!/usr/bin/env python3
"""
Instagram Bridge Server - Connect Postiz and Playwright
Runs on host machine, receives requests from Postiz and uses Playwright to execute actions
"""
import asyncio
import json
import logging
from pathlib import Path
from flask import Flask, request, jsonify
from playwright.async_api import async_playwright
import sys
import os

# Add parent directory to path to import Instagram modules
sys.path.append(os.path.dirname(__file__))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


class InstagramOperations:
    """Instagram operations using Playwright"""

    def __init__(self, auth_file: str = "platforms_auth.json"):
        self.auth_file = auth_file
        self.sessionid = self._load_sessionid()

    def _load_sessionid(self) -> str:
        """Load Instagram sessionid from auth file"""
        try:
            with open(self.auth_file, 'r') as f:
                config = json.load(f)
                instagram_auth = config.get('instagram', {})
                cookies = instagram_auth.get('cookies', {})
                return cookies.get('sessionid', '')
        except Exception as e:
            logger.error(f"Error loading auth: {e}")
            return ''

    async def create_post(self, caption: str, image_path: str = None) -> dict:
        """
        Create Instagram post

        Args:
            caption: Post caption text
            image_path: Path to image file (required for Instagram)

        Returns:
            Result dictionary with success status
        """
        if not self.sessionid:
            return {'success': False, 'error': 'No Instagram session found'}

        if not image_path:
            return {'success': False, 'error': 'Image required for Instagram post'}

        try:
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(
                    headless=False,
                    args=['--disable-blink-features=AutomationControlled']
                )

                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )

                # Add cookies
                await context.add_cookies([{
                    'name': 'sessionid',
                    'value': self.sessionid,
                    'domain': '.instagram.com',
                    'path': '/',
                    'httpOnly': True,
                    'secure': True
                }])

                page = await context.new_page()

                # Navigate to Instagram
                logger.info("📍 Navigating to Instagram...")
                await page.goto('https://www.instagram.com', timeout=30000)
                await asyncio.sleep(3)

                # Click Create button
                logger.info("📍 Clicking Create button...")
                create_selectors = [
                    'a[href="#"]:has-text("Create")',
                    'svg[aria-label*="New post"]',
                    'svg[aria-label*="Create"]',
                    '[aria-label*="Create"]',
                    'a[href="#"]>svg[aria-label*="Create"]'
                ]

                create_clicked = False
                for selector in create_selectors:
                    try:
                        button = await page.wait_for_selector(selector, timeout=3000)
                        if button and await button.is_visible():
                            await button.click()
                            logger.info(f"✅ Clicked Create button: {selector}")
                            create_clicked = True
                            await asyncio.sleep(2)
                            break
                    except:
                        continue

                if not create_clicked:
                    await browser.close()
                    return {'success': False, 'error': 'Could not find Create button'}

                # Select Post type if dialog appears
                logger.info("📍 Selecting Post type...")
                post_selectors = [
                    'span:has-text("Post")',
                    'button:has-text("Post")',
                    'div:has-text("Post")'
                ]

                for selector in post_selectors:
                    try:
                        option = await page.wait_for_selector(selector, timeout=3000)
                        if option and await option.is_visible():
                            await option.click()
                            await asyncio.sleep(2)
                            break
                    except:
                        continue

                # Upload image
                logger.info(f"📍 Uploading image: {image_path}")
                absolute_path = os.path.abspath(image_path)

                file_input_selectors = [
                    'input[type="file"]',
                    'form input[type="file"]',
                    'input[accept*="image"]'
                ]

                uploaded = False
                for selector in file_input_selectors:
                    try:
                        file_input = await page.wait_for_selector(selector, timeout=5000)
                        if file_input:
                            await file_input.set_input_files(absolute_path)
                            logger.info("✅ Image uploaded")
                            uploaded = True
                            await asyncio.sleep(3)
                            break
                    except:
                        continue

                if not uploaded:
                    await browser.close()
                    return {'success': False, 'error': 'Could not upload image'}

                # Click Next buttons (may need multiple times)
                logger.info("📍 Clicking Next buttons...")
                next_selectors = [
                    'button:has-text("Next")',
                    'div:has-text("Next")'
                ]

                for attempt in range(3):
                    for selector in next_selectors:
                        try:
                            next_button = await page.wait_for_selector(selector, timeout=3000)
                            if next_button and await next_button.is_visible():
                                await next_button.click()
                                logger.info(f"✅ Clicked Next (attempt {attempt + 1})")
                                await asyncio.sleep(2)
                                break
                        except:
                            continue

                # Fill caption
                logger.info(f"📍 Filling caption ({len(caption)} chars)...")
                caption_selectors = [
                    'textarea[aria-label*="caption"]',
                    'textarea[aria-label*="Caption"]',
                    'div[contenteditable="true"][aria-label*="caption"]',
                    'textarea:first-of-type',
                    'div[contenteditable="true"]:first-of-type'
                ]

                caption_filled = False
                for selector in caption_selectors:
                    try:
                        caption_input = await page.wait_for_selector(selector, timeout=3000)
                        if caption_input and await caption_input.is_visible():
                            await caption_input.click()
                            await asyncio.sleep(0.5)
                            await caption_input.fill(caption)
                            logger.info("✅ Caption filled")
                            caption_filled = True
                            break
                    except:
                        continue

                if not caption_filled:
                    logger.warning("⚠️  Could not fill caption")

                await asyncio.sleep(2)

                # Click Share button
                logger.info("📍 Clicking Share button...")
                share_selectors = [
                    'button:has-text("Share")',
                    'button:has-text("Post")',
                    'button[type="submit"]',
                    '[aria-label*="Share"]'
                ]

                share_clicked = False
                for selector in share_selectors:
                    try:
                        share_button = await page.wait_for_selector(selector, timeout=3000)
                        if share_button and await share_button.is_visible():
                            await share_button.click()
                            logger.info("✅ Share button clicked")
                            share_clicked = True
                            break
                    except:
                        continue

                if not share_clicked:
                    await browser.close()
                    return {'success': False, 'error': 'Could not click Share button'}

                # Wait for post to complete
                logger.info("⏳ Waiting for post to complete...")
                await asyncio.sleep(10)

                # Check for success
                success_indicators = [
                    'div:has-text("post has been shared")',
                    'div:has-text("Post shared")'
                ]

                post_success = False
                for indicator in success_indicators:
                    try:
                        element = await page.wait_for_selector(indicator, timeout=3000)
                        if element:
                            post_success = True
                            break
                    except:
                        continue

                await browser.close()

                if post_success:
                    logger.info("✅ Instagram post created successfully!")
                    return {
                        'success': True,
                        'message': 'Post created successfully',
                        'url': 'https://www.instagram.com/'  # Instagram doesn't provide direct post URL easily
                    }
                else:
                    logger.info("⚠️  Post status unknown, assuming success")
                    return {
                        'success': True,
                        'message': 'Post likely created (status unknown)',
                        'url': 'https://www.instagram.com/'
                    }

        except Exception as e:
            logger.error(f"❌ Error creating post: {e}")
            return {'success': False, 'error': str(e)}

    async def get_user_profile(self, username: str) -> dict:
        """
        Get Instagram user profile

        Args:
            username: Instagram username

        Returns:
            User profile dictionary
        """
        if not self.sessionid:
            return {'success': False, 'error': 'No Instagram session found'}

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()

                await context.add_cookies([{
                    'name': 'sessionid',
                    'value': self.sessionid,
                    'domain': '.instagram.com',
                    'path': '/'
                }])

                page = await context.new_page()

                # Navigate to user profile
                username = username.lstrip('@')
                url = f'https://www.instagram.com/{username}/'
                logger.info(f"📍 Fetching profile: {url}")

                await page.goto(url, timeout=30000)
                await asyncio.sleep(3)

                # Extract profile data
                try:
                    # Get basic info from meta tags
                    title = await page.title()

                    # Try to extract follower count
                    follower_text = await page.locator('a[href*="/followers/"]').first.text_content()

                    # Try to extract bio
                    bio_selectors = [
                        'div.-vDIg span',
                        'h1'
                    ]

                    bio = ''
                    for selector in bio_selectors:
                        try:
                            bio_elem = await page.query_selector(selector)
                            if bio_elem:
                                bio = await bio_elem.text_content()
                                break
                        except:
                            continue

                    await browser.close()

                    return {
                        'success': True,
                        'username': username,
                        'profile_url': url,
                        'title': title,
                        'bio': bio or '',
                        'followers': follower_text or 'Unknown'
                    }

                except Exception as e:
                    await browser.close()
                    logger.error(f"Error extracting profile data: {e}")
                    return {
                        'success': True,
                        'username': username,
                        'profile_url': url,
                        'error': 'Could not extract all profile data'
                    }

        except Exception as e:
            logger.error(f"❌ Error getting profile: {e}")
            return {'success': False, 'error': str(e)}

    async def send_dm(self, username: str, message: str) -> dict:
        """
        Send Instagram DM

        Args:
            username: Instagram username
            message: Message text

        Returns:
            Result dictionary
        """
        if not self.sessionid:
            return {'success': False, 'error': 'No Instagram session found'}

        try:
            async with async_playwright() as p:
                browser = await p.firefox.launch(
                    headless=False
                )

                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 800},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )

                await context.add_cookies([{
                    'name': 'sessionid',
                    'value': self.sessionid,
                    'domain': '.instagram.com',
                    'path': '/'
                }])

                page = await context.new_page()

                # Navigate to user profile
                username = username.lstrip('@')
                logger.info(f"💬 Sending DM to @{username}...")
                await page.goto(f'https://www.instagram.com/{username}/', timeout=30000)
                await asyncio.sleep(3)

                # Close notifications if they appear
                try:
                    not_now = await page.query_selector('button:has-text("Not Now")')
                    if not_now:
                        await not_now.click()
                        await asyncio.sleep(1)
                except:
                    pass

                # Close any popup/modal that might be blocking the page
                logger.info("🔍 Closing any popups...")
                try:
                    # Try to find and close the X button on popup
                    close_selectors = [
                        'button[aria-label="Close"]',
                        'svg[aria-label="Close"]',
                        'button:has-text("✕")',
                        '[role="button"]:has-text("✕")'
                    ]
                    for selector in close_selectors:
                        try:
                            close_btn = await page.query_selector(selector)
                            if close_btn and await close_btn.is_visible():
                                await close_btn.click()
                                await asyncio.sleep(1)
                                logger.info("✅ Closed popup")
                                break
                        except:
                            continue
                except:
                    pass

                # Click Follow button if needed
                logger.info("👥 Following user...")
                follow_selectors = [
                    'button:has-text("Follow")',
                    'div[role="button"]:has-text("Follow")'
                ]

                for selector in follow_selectors:
                    try:
                        follow_btn = await page.wait_for_selector(selector, timeout=3000)
                        if follow_btn and await follow_btn.is_visible():
                            await follow_btn.click()
                            await asyncio.sleep(2)
                            break
                    except:
                        continue

                # Close any popup again after following
                try:
                    close_selectors = [
                        'button[aria-label="Close"]',
                        'svg[aria-label="Close"]',
                        'button:has-text("✕")',
                        '[role="button"]:has-text("✕")'
                    ]
                    for selector in close_selectors:
                        try:
                            close_btn = await page.query_selector(selector)
                            if close_btn and await close_btn.is_visible():
                                await close_btn.click()
                                await asyncio.sleep(1)
                                break
                        except:
                            continue
                except:
                    pass

                # Click Message button
                logger.info("💬 Opening message dialog...")
                message_selectors = [
                    'button:has-text("Message")',
                    'div[role="button"]:has-text("Message")'
                ]

                message_opened = False
                for selector in message_selectors:
                    try:
                        msg_btn = await page.wait_for_selector(selector, timeout=5000)
                        if msg_btn and await msg_btn.is_visible():
                            await msg_btn.click()
                            await asyncio.sleep(2)

                            # Check if message dialog opened
                            input_check = await page.query_selector('div[contenteditable="true"]')
                            if input_check and await input_check.is_visible():
                                message_opened = True
                                break
                    except:
                        continue

                if not message_opened:
                    await browser.close()
                    return {'success': False, 'error': 'Could not open message dialog'}

                # Find message input
                logger.info("✏️  Typing message...")
                input_selectors = [
                    'div[contenteditable="true"][role="textbox"]',
                    'div[contenteditable="true"][aria-label*="Message"]',
                    'div[contenteditable="true"]',
                    'textarea[placeholder*="Message"]'
                ]

                message_input = None
                for selector in input_selectors:
                    try:
                        message_input = await page.wait_for_selector(selector, timeout=5000)
                        if message_input and await message_input.is_visible():
                            break
                    except:
                        continue

                if not message_input:
                    await browser.close()
                    return {'success': False, 'error': 'Could not find message input'}

                # Type message
                await message_input.click()
                await asyncio.sleep(0.5)
                await message_input.fill(message)
                await asyncio.sleep(1)

                # Send message
                logger.info("📤 Sending...")
                send_selectors = [
                    'div[role="button"]:has-text("Send")',
                    'button:has-text("Send")'
                ]

                sent = False
                for selector in send_selectors:
                    try:
                        send_buttons = await page.query_selector_all(selector)
                        for btn in send_buttons:
                            if await btn.is_visible():
                                await btn.click()
                                logger.info("✅ Message sent!")
                                sent = True
                                await asyncio.sleep(2)
                                break
                        if sent:
                            break
                    except:
                        continue

                # If no Send button found, try Enter key
                if not sent:
                    try:
                        await message_input.press('Enter')
                        logger.info("✅ Message sent via Enter!")
                        sent = True
                        await asyncio.sleep(2)
                    except:
                        pass

                await browser.close()

                if sent:
                    return {
                        'success': True,
                        'message': 'DM sent successfully',
                        'username': username
                    }
                else:
                    return {'success': False, 'error': 'Could not send message'}

        except Exception as e:
            logger.error(f"❌ Error sending DM: {e}")
            return {'success': False, 'error': str(e)}

    async def like_post(self, post_url: str) -> dict:
        """
        Like an Instagram post

        Args:
            post_url: Instagram post URL or shortcode

        Returns:
            Result dictionary
        """
        if not self.sessionid:
            return {'success': False, 'error': 'No Instagram session found'}

        try:
            async with async_playwright() as p:
                browser = await p.firefox.launch(headless=False)
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 800},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )

                await context.add_cookies([{
                    'name': 'sessionid',
                    'value': self.sessionid,
                    'domain': '.instagram.com',
                    'path': '/'
                }])

                page = await context.new_page()

                # Navigate to post
                logger.info(f"👍 Liking post: {post_url}")
                await page.goto(post_url, timeout=30000)
                await asyncio.sleep(3)

                # Close popups
                try:
                    close_selectors = ['button[aria-label="Close"]', 'svg[aria-label="Close"]']
                    for selector in close_selectors:
                        close_btn = await page.query_selector(selector)
                        if close_btn and await close_btn.is_visible():
                            await close_btn.click()
                            await asyncio.sleep(1)
                            break
                except:
                    pass

                # Find and click like button
                like_selectors = [
                    'svg[aria-label="Like"]',
                    'span:has-text("Like")',
                    'article svg[aria-label="Like"]'
                ]

                liked = False
                for selector in like_selectors:
                    try:
                        like_btn = await page.wait_for_selector(selector, timeout=5000)
                        if like_btn and await like_btn.is_visible():
                            await like_btn.click()
                            logger.info("✅ Post liked!")
                            liked = True
                            await asyncio.sleep(2)
                            break
                    except:
                        continue

                await browser.close()

                if liked:
                    return {'success': True, 'message': 'Post liked successfully'}
                else:
                    return {'success': False, 'error': 'Could not find like button'}

        except Exception as e:
            logger.error(f"❌ Error liking post: {e}")
            return {'success': False, 'error': str(e)}

    async def unlike_post(self, post_url: str) -> dict:
        """Unlike an Instagram post"""
        if not self.sessionid:
            return {'success': False, 'error': 'No Instagram session found'}

        try:
            async with async_playwright() as p:
                browser = await p.firefox.launch(headless=False)
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 800},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )

                await context.add_cookies([{
                    'name': 'sessionid',
                    'value': self.sessionid,
                    'domain': '.instagram.com',
                    'path': '/'
                }])

                page = await context.new_page()

                logger.info(f"💔 Unliking post: {post_url}")
                await page.goto(post_url, timeout=30000)
                await asyncio.sleep(3)

                # Find and click unlike button
                unlike_selectors = [
                    'svg[aria-label="Unlike"]',
                    'span:has-text("Unlike")',
                    'article svg[aria-label="Unlike"]'
                ]

                unliked = False
                for selector in unlike_selectors:
                    try:
                        unlike_btn = await page.wait_for_selector(selector, timeout=5000)
                        if unlike_btn and await unlike_btn.is_visible():
                            await unlike_btn.click()
                            logger.info("✅ Post unliked!")
                            unliked = True
                            await asyncio.sleep(2)
                            break
                    except:
                        continue

                await browser.close()

                if unliked:
                    return {'success': True, 'message': 'Post unliked successfully'}
                else:
                    return {'success': False, 'error': 'Could not find unlike button (post may not be liked)'}

        except Exception as e:
            logger.error(f"❌ Error unliking post: {e}")
            return {'success': False, 'error': str(e)}

    async def follow_user(self, username: str) -> dict:
        """Follow an Instagram user"""
        if not self.sessionid:
            return {'success': False, 'error': 'No Instagram session found'}

        try:
            async with async_playwright() as p:
                browser = await p.firefox.launch(headless=False)
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 800},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )

                await context.add_cookies([{
                    'name': 'sessionid',
                    'value': self.sessionid,
                    'domain': '.instagram.com',
                    'path': '/'
                }])

                page = await context.new_page()

                username = username.lstrip('@')
                logger.info(f"👥 Following user: @{username}")
                await page.goto(f'https://www.instagram.com/{username}/', timeout=30000)
                await asyncio.sleep(3)

                # Close popups
                try:
                    close_selectors = ['button[aria-label="Close"]', 'svg[aria-label="Close"]']
                    for selector in close_selectors:
                        close_btn = await page.query_selector(selector)
                        if close_btn and await close_btn.is_visible():
                            await close_btn.click()
                            await asyncio.sleep(1)
                            break
                except:
                    pass

                # Find and click follow button
                follow_selectors = [
                    'button:has-text("Follow")',
                    'div[role="button"]:has-text("Follow")'
                ]

                followed = False
                for selector in follow_selectors:
                    try:
                        follow_btn = await page.wait_for_selector(selector, timeout=5000)
                        if follow_btn and await follow_btn.is_visible():
                            await follow_btn.click()
                            logger.info("✅ User followed!")
                            followed = True
                            await asyncio.sleep(2)
                            break
                    except:
                        continue

                await browser.close()

                if followed:
                    return {'success': True, 'message': f'Followed @{username}'}
                else:
                    return {'success': False, 'error': 'Could not find follow button (may already be following)'}

        except Exception as e:
            logger.error(f"❌ Error following user: {e}")
            return {'success': False, 'error': str(e)}

    async def unfollow_user(self, username: str) -> dict:
        """Unfollow an Instagram user"""
        if not self.sessionid:
            return {'success': False, 'error': 'No Instagram session found'}

        try:
            async with async_playwright() as p:
                browser = await p.firefox.launch(headless=False)
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 800},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )

                await context.add_cookies([{
                    'name': 'sessionid',
                    'value': self.sessionid,
                    'domain': '.instagram.com',
                    'path': '/'
                }])

                page = await context.new_page()

                username = username.lstrip('@')
                logger.info(f"👋 Unfollowing user: @{username}")
                await page.goto(f'https://www.instagram.com/{username}/', timeout=30000)
                await asyncio.sleep(3)

                # Find and click Following button
                following_selectors = [
                    'button:has-text("Following")',
                    'div[role="button"]:has-text("Following")'
                ]

                for selector in following_selectors:
                    try:
                        following_btn = await page.wait_for_selector(selector, timeout=5000)
                        if following_btn and await following_btn.is_visible():
                            await following_btn.click()
                            await asyncio.sleep(1)
                            break
                    except:
                        continue

                # Confirm unfollow
                unfollow_confirm_selectors = [
                    'button:has-text("Unfollow")',
                    'button[class*="primary"]:has-text("Unfollow")'
                ]

                unfollowed = False
                for selector in unfollow_confirm_selectors:
                    try:
                        confirm_btn = await page.wait_for_selector(selector, timeout=5000)
                        if confirm_btn and await confirm_btn.is_visible():
                            await confirm_btn.click()
                            logger.info("✅ User unfollowed!")
                            unfollowed = True
                            await asyncio.sleep(2)
                            break
                    except:
                        continue

                await browser.close()

                if unfollowed:
                    return {'success': True, 'message': f'Unfollowed @{username}'}
                else:
                    return {'success': False, 'error': 'Could not complete unfollow'}

        except Exception as e:
            logger.error(f"❌ Error unfollowing user: {e}")
            return {'success': False, 'error': str(e)}

    async def comment_on_post(self, post_url: str, comment: str) -> dict:
        """Comment on an Instagram post"""
        if not self.sessionid:
            return {'success': False, 'error': 'No Instagram session found'}

        try:
            async with async_playwright() as p:
                browser = await p.firefox.launch(headless=False)
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 800},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )

                await context.add_cookies([{
                    'name': 'sessionid',
                    'value': self.sessionid,
                    'domain': '.instagram.com',
                    'path': '/'
                }])

                page = await context.new_page()

                logger.info(f"💬 Commenting on post: {post_url}")
                await page.goto(post_url, timeout=30000)
                await asyncio.sleep(3)

                # Find comment input
                comment_selectors = [
                    'textarea[placeholder*="Add a comment"]',
                    'textarea[aria-label*="Add a comment"]',
                    'form textarea'
                ]

                comment_input = None
                for selector in comment_selectors:
                    try:
                        comment_input = await page.wait_for_selector(selector, timeout=5000)
                        if comment_input and await comment_input.is_visible():
                            break
                    except:
                        continue

                if not comment_input:
                    await browser.close()
                    return {'success': False, 'error': 'Could not find comment input'}

                # Type comment
                await comment_input.click()
                await asyncio.sleep(0.5)
                await comment_input.fill(comment)
                await asyncio.sleep(1)

                # Post comment
                post_selectors = [
                    'button:has-text("Post")',
                    'div[role="button"]:has-text("Post")'
                ]

                posted = False
                for selector in post_selectors:
                    try:
                        post_btn = await page.query_selector(selector)
                        if post_btn and await post_btn.is_visible():
                            await post_btn.click()
                            logger.info("✅ Comment posted!")
                            posted = True
                            await asyncio.sleep(2)
                            break
                    except:
                        continue

                await browser.close()

                if posted:
                    return {'success': True, 'message': 'Comment posted successfully'}
                else:
                    return {'success': False, 'error': 'Could not post comment'}

        except Exception as e:
            logger.error(f"❌ Error commenting: {e}")
            return {'success': False, 'error': str(e)}

    async def get_post_details(self, post_url: str) -> dict:
        """Get Instagram post details"""
        if not self.sessionid:
            return {'success': False, 'error': 'No Instagram session found'}

        try:
            async with async_playwright() as p:
                browser = await p.firefox.launch(headless=False)
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 800},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )

                await context.add_cookies([{
                    'name': 'sessionid',
                    'value': self.sessionid,
                    'domain': '.instagram.com',
                    'path': '/'
                }])

                page = await context.new_page()

                logger.info(f"📊 Getting post details: {post_url}")
                await page.goto(post_url, timeout=30000)
                await asyncio.sleep(3)

                post_data = {
                    'success': True,
                    'url': post_url,
                    'caption': '',
                    'likes': '0',
                    'comments': '0',
                    'author': '',
                    'timestamp': ''
                }

                # Extract caption
                try:
                    caption_selectors = [
                        'meta[property="og:description"]',
                        'h1'
                    ]
                    for selector in caption_selectors:
                        elem = await page.query_selector(selector)
                        if elem:
                            if selector.startswith('meta'):
                                post_data['caption'] = await elem.get_attribute('content') or ''
                            else:
                                post_data['caption'] = await elem.inner_text() or ''
                            if post_data['caption']:
                                break
                except:
                    pass

                # Extract likes
                try:
                    likes_selectors = [
                        'section a[href*="/liked_by/"]',
                        'button:has-text("like")',
                    ]
                    for selector in likes_selectors:
                        elem = await page.query_selector(selector)
                        if elem:
                            text = await elem.inner_text()
                            if text:
                                post_data['likes'] = text
                                break
                except:
                    pass

                # Extract author
                try:
                    author_selectors = [
                        'meta[property="og:title"]',
                        'a[role="link"]'
                    ]
                    for selector in author_selectors:
                        elem = await page.query_selector(selector)
                        if elem:
                            if selector.startswith('meta'):
                                title = await elem.get_attribute('content') or ''
                                if title:
                                    post_data['author'] = title.split('(')[0].strip()
                                    break
                            else:
                                post_data['author'] = await elem.inner_text() or ''
                                if post_data['author']:
                                    break
                except:
                    pass

                await browser.close()
                return post_data

        except Exception as e:
            logger.error(f"❌ Error getting post details: {e}")
            return {'success': False, 'error': str(e)}

    async def get_user_posts(self, username: str, max_count: int = 20) -> dict:
        """Get user's Instagram posts"""
        if not self.sessionid:
            return {'success': False, 'error': 'No Instagram session found'}

        try:
            async with async_playwright() as p:
                browser = await p.firefox.launch(headless=False)
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 800},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )

                await context.add_cookies([{
                    'name': 'sessionid',
                    'value': self.sessionid,
                    'domain': '.instagram.com',
                    'path': '/'
                }])

                page = await context.new_page()

                username = username.lstrip('@')
                logger.info(f"📸 Getting posts from @{username}")
                await page.goto(f'https://www.instagram.com/{username}/', timeout=30000)
                await asyncio.sleep(3)

                posts = []

                # Find post links
                try:
                    # Scroll to load more posts
                    for _ in range(3):
                        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                        await asyncio.sleep(2)

                    # Extract post URLs
                    post_links = await page.query_selector_all('a[href*="/p/"]')

                    for link in post_links[:max_count]:
                        try:
                            href = await link.get_attribute('href')
                            if href and '/p/' in href:
                                full_url = f'https://www.instagram.com{href}' if not href.startswith('http') else href
                                posts.append({
                                    'url': full_url,
                                    'shortcode': href.split('/p/')[-1].rstrip('/')
                                })
                        except:
                            continue

                except Exception as e:
                    logger.error(f"Error extracting posts: {e}")

                await browser.close()

                return {
                    'success': True,
                    'username': username,
                    'posts': posts,
                    'count': len(posts)
                }

        except Exception as e:
            logger.error(f"❌ Error getting user posts: {e}")
            return {'success': False, 'error': str(e)}

    async def search_by_tag(self, tag: str, max_count: int = 20) -> dict:
        """Search Instagram posts by hashtag"""
        if not self.sessionid:
            return {'success': False, 'error': 'No Instagram session found'}

        try:
            async with async_playwright() as p:
                browser = await p.firefox.launch(headless=False)
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 800},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )

                await context.add_cookies([{
                    'name': 'sessionid',
                    'value': self.sessionid,
                    'domain': '.instagram.com',
                    'path': '/'
                }])

                page = await context.new_page()

                tag = tag.lstrip('#')
                logger.info(f"🔍 Searching tag: #{tag}")
                await page.goto(f'https://www.instagram.com/explore/tags/{tag}/', timeout=30000)
                await asyncio.sleep(3)

                posts = []

                try:
                    # Scroll to load more posts
                    for _ in range(3):
                        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                        await asyncio.sleep(2)

                    # Extract post URLs
                    post_links = await page.query_selector_all('a[href*="/p/"]')

                    for link in post_links[:max_count]:
                        try:
                            href = await link.get_attribute('href')
                            if href and '/p/' in href:
                                full_url = f'https://www.instagram.com{href}' if not href.startswith('http') else href
                                posts.append({
                                    'url': full_url,
                                    'shortcode': href.split('/p/')[-1].rstrip('/')
                                })
                        except:
                            continue

                except Exception as e:
                    logger.error(f"Error extracting posts: {e}")

                await browser.close()

                return {
                    'success': True,
                    'tag': tag,
                    'posts': posts,
                    'count': len(posts)
                }

        except Exception as e:
            logger.error(f"❌ Error searching tag: {e}")
            return {'success': False, 'error': str(e)}


# Initialize Instagram operations
instagram_ops = InstagramOperations()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Instagram Bridge Server is running'
    })


@app.route('/post', methods=['POST'])
def create_post_endpoint():
    """
    Create Instagram post endpoint

    Request body:
    {
        "caption": "Post caption with hashtags",
        "image_path": "/path/to/image.jpg"
    }

    Response:
    {
        "success": true,
        "message": "Post created successfully",
        "url": "https://www.instagram.com/"
    }
    """
    try:
        data = request.get_json()
        caption = data.get('caption', '')
        image_path = data.get('image_path', '')

        if not caption:
            return jsonify({'error': 'Caption required'}), 400

        if not image_path:
            return jsonify({'error': 'Image path required for Instagram post'}), 400

        logger.info(f"📝 Received request to create Instagram post")

        # Run the async operation
        result = asyncio.run(instagram_ops.create_post(caption, image_path))

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"❌ Error in post endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/user/<username>', methods=['GET'])
def get_user_endpoint(username):
    """
    Get Instagram user profile

    Response:
    {
        "success": true,
        "username": "username",
        "profile_url": "https://www.instagram.com/username/",
        "bio": "User bio",
        "followers": "1.2K"
    }
    """
    try:
        logger.info(f"👤 Getting user @{username}")
        result = asyncio.run(instagram_ops.get_user_profile(username))

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"❌ Error getting user: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/dm', methods=['POST'])
def send_dm_endpoint():
    """
    Send Instagram DM

    Request body:
    {
        "username": "target_username",
        "message": "Hello! This is a message."
    }

    Response:
    {
        "success": true,
        "message": "DM sent successfully",
        "username": "target_username"
    }
    """
    try:
        data = request.get_json()
        username = data.get('username', '')
        message = data.get('message', '')

        if not username:
            return jsonify({'error': 'Username required'}), 400

        if not message:
            return jsonify({'error': 'Message required'}), 400

        logger.info(f"💬 Received request to send DM to @{username}")

        # Run the async operation
        result = asyncio.run(instagram_ops.send_dm(username, message))

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"❌ Error in DM endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/like', methods=['POST'])
def like_post_endpoint():
    """Like a post"""
    try:
        data = request.get_json()
        post_url = data.get('post_url', '')

        if not post_url:
            return jsonify({'error': 'Post URL required'}), 400

        result = asyncio.run(instagram_ops.like_post(post_url))

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"❌ Error in like endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/unlike', methods=['POST'])
def unlike_post_endpoint():
    """Unlike a post"""
    try:
        data = request.get_json()
        post_url = data.get('post_url', '')

        if not post_url:
            return jsonify({'error': 'Post URL required'}), 400

        result = asyncio.run(instagram_ops.unlike_post(post_url))

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"❌ Error in unlike endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/follow', methods=['POST'])
def follow_user_endpoint():
    """Follow a user"""
    try:
        data = request.get_json()
        username = data.get('username', '')

        if not username:
            return jsonify({'error': 'Username required'}), 400

        result = asyncio.run(instagram_ops.follow_user(username))

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"❌ Error in follow endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/unfollow', methods=['POST'])
def unfollow_user_endpoint():
    """Unfollow a user"""
    try:
        data = request.get_json()
        username = data.get('username', '')

        if not username:
            return jsonify({'error': 'Username required'}), 400

        result = asyncio.run(instagram_ops.unfollow_user(username))

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"❌ Error in unfollow endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/comment', methods=['POST'])
def comment_endpoint():
    """Comment on a post"""
    try:
        data = request.get_json()
        post_url = data.get('post_url', '')
        comment = data.get('comment', '')

        if not post_url:
            return jsonify({'error': 'Post URL required'}), 400

        if not comment:
            return jsonify({'error': 'Comment text required'}), 400

        result = asyncio.run(instagram_ops.comment_on_post(post_url, comment))

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"❌ Error in comment endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/post/<path:post_id>', methods=['GET'])
def get_post_endpoint(post_id):
    """Get post details"""
    try:
        # Construct full URL if needed
        if not post_id.startswith('http'):
            post_url = f'https://www.instagram.com/p/{post_id}/'
        else:
            post_url = post_id

        result = asyncio.run(instagram_ops.get_post_details(post_url))

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"❌ Error in get post endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/user/<username>/posts', methods=['GET'])
def get_user_posts_endpoint(username):
    """Get user's posts"""
    try:
        max_count = request.args.get('max_count', default=20, type=int)

        result = asyncio.run(instagram_ops.get_user_posts(username, max_count))

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"❌ Error in get user posts endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/search/tag/<tag>', methods=['GET'])
def search_tag_endpoint(tag):
    """Search posts by hashtag"""
    try:
        max_count = request.args.get('max_count', default=20, type=int)

        result = asyncio.run(instagram_ops.search_by_tag(tag, max_count))

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"❌ Error in search tag endpoint: {e}")
        return jsonify({'error': str(e)}), 500


def run_server():
    """Run the Flask server"""
    logger.info("=" * 60)
    logger.info("🚀 Instagram Bridge Server Starting...")
    logger.info("=" * 60)
    logger.info("✅ Server ready on http://localhost:5002")
    logger.info("=" * 60 + "\n")

    app.run(host='0.0.0.0', port=5002, debug=False)


if __name__ == '__main__':
    run_server()
