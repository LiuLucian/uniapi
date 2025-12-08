"""
Twitter API Implementation using Playwright
Directly copied from working twitter_bridge_server.py
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from typing import Optional
from loguru import logger

from .auth import TwitterAuth


class TwitterAPI:
    """
    Twitter API implementation using Playwright scraping
    Compatible with Twitter API v2 response format
    """

    def __init__(self, auth: TwitterAuth):
        self.auth = auth

    async def _post_single_tweet(self, page, text):
        """Post a single tweet - copied from twitter_bridge_server.py"""
        try:
            # New tweet
            logger.info("Opening Twitter home...")
            await page.goto('https://twitter.com/home', wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(3)

            # Find compose box
            logger.info("Finding compose box...")
            compose_box = await page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=10000)

            # Type tweet
            logger.info(f"Typing tweet ({len(text)} chars)...")
            await compose_box.click()
            await asyncio.sleep(0.5)
            await compose_box.fill(text)
            await asyncio.sleep(1)

            # Click post button
            logger.info("Posting...")
            post_button = await page.query_selector('[data-testid="tweetButtonInline"]')

            if not post_button:
                post_button = await page.query_selector('button:has-text("Post"), button:has-text("Reply"), button:has-text("Tweet")')

            if post_button:
                await post_button.click()
            else:
                logger.error("Could not find post button!")
                return None

            # Wait for post to complete
            await asyncio.sleep(5)

            # Try to get tweet ID from URL first
            current_url = page.url
            if '/status/' in current_url:
                tweet_id = current_url.split('/status/')[-1].split('?')[0]
                logger.info(f"Posted! Tweet ID: {tweet_id}")
                return tweet_id

            # If URL didn't change, try to find tweet in timeline
            logger.info("Trying to find posted tweet in timeline...")
            await asyncio.sleep(3)

            try:
                # Wait for at least one tweet to appear (with timeout)
                await page.wait_for_selector('article[data-testid="tweet"]', timeout=10000)
                tweets = await page.query_selector_all('article[data-testid="tweet"]')
                if tweets and len(tweets) > 0:
                    first_tweet = tweets[0]
                    time_link = await first_tweet.query_selector('time')
                    if time_link:
                        parent_link = await time_link.evaluate_handle('el => el.closest("a")')
                        href = await parent_link.get_attribute('href')
                        if href and '/status/' in href:
                            tweet_id = href.split('/status/')[-1].split('?')[0]
                            logger.info(f"Posted! Tweet ID: {tweet_id}")
                            return tweet_id
            except Exception as e:
                logger.warning(f"Couldn't extract tweet ID: {e}")

            # Tweet was posted but couldn't get ID - that's OK!
            logger.info("Tweet posted successfully (ID extraction skipped)")
            return "posted"

        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            return None

    async def _create_tweet_task(self, text: str) -> dict:
        """Complete tweet posting task - uses Firefox + cookies"""
        # Check if auth file exists
        auth_file = Path.home() / '.distroflow' / 'twitter_auth.json'

        if not auth_file.exists():
            logger.error("No saved authentication found!")
            raise Exception("No saved authentication found at ~/.distroflow/twitter_auth.json")

        logger.info("Launching browser...")

        async with async_playwright() as p:
            # Use Firefox instead of Chromium (Chromium crashes with SEGV_ACCERR on this system)
            # Note: twitter_bridge_server.py uses Chromium and works, but might be different env
            browser = await p.firefox.launch(
                headless=False
            )

            context = await browser.new_context(
                viewport={'width': 1400, 'height': 900},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            # Load cookies from saved persistent context
            import json
            auth_file = Path.home() / '.distroflow' / 'twitter_auth.json'
            with open(auth_file) as f:
                auth_data = json.load(f)

            await context.add_cookies(auth_data['cookies'])

            page = await context.new_page()

            # Verify login
            try:
                await page.goto('https://twitter.com/home', wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(2)
                await page.wait_for_selector('[data-testid="SideNav_AccountSwitcher_Button"]', timeout=10000)
                logger.info("Logged in successfully!")
            except Exception as e:
                logger.error(f"Failed to verify login: {e}")
                await context.close()
                raise

            # Post tweet
            tweet_id = await self._post_single_tweet(page, text)

            # Close browser
            await context.close()
            await browser.close()
            logger.info("Browser closed")

            if not tweet_id:
                raise Exception("Failed to post tweet")

            return {
                "id": tweet_id,
                "text": text
            }

    async def create_tweet(self, text: str) -> dict:
        """
        Post a tweet

        Returns Twitter API v2 compatible response:
        {
            "id": "1234567890",
            "text": "Hello World"
        }
        """
        # Call async task directly (FastAPI already runs in event loop)
        return await self._create_tweet_task(text)

    async def get_current_user(self) -> dict:
        """Get current user information"""
        # TODO: Implement using persistent context like create_tweet
        raise NotImplementedError("Get current user not yet implemented")

    async def delete_tweet(self, tweet_id: str):
        """Delete a tweet by ID"""
        raise NotImplementedError("Delete tweet not yet implemented")

    async def retweet(self, tweet_id: str) -> dict:
        """Retweet a tweet"""
        raise NotImplementedError("Retweet not yet implemented")

    async def like_tweet(self, tweet_id: str) -> dict:
        """Like a tweet"""
        raise NotImplementedError("Like tweet not yet implemented")
