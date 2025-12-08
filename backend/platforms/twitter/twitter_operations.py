#!/usr/bin/env python3
"""
Twitter Operations Module
Playwright-based Twitter API implementation
All operations use browser automation (no official API needed)
"""
import asyncio
import logging
from pathlib import Path
from playwright.async_api import async_playwright, Page

logger = logging.getLogger(__name__)


class TwitterOperations:
    """Twitter operations using Playwright automation"""

    def __init__(self):
        self.user_data_dir = Path.home() / '.distroflow/twitter_browser'

    async def _get_browser_context(self):
        """Launch browser with saved session"""
        if not self.user_data_dir.exists():
            raise Exception("No saved login session found at ~/.distroflow/twitter_browser")

        playwright = await async_playwright().start()

        context = await playwright.chromium.launch_persistent_context(
            str(self.user_data_dir),
            headless=False,
            viewport={'width': 1400, 'height': 900},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            args=[
                '--disable-blink-features=AutomationControlled',
                '--start-maximized',
                '--no-sandbox'
            ]
        )

        page = context.pages[0] if context.pages else await context.new_page()

        return playwright, context, page

    async def like_tweet(self, tweet_id: str) -> dict:
        """Like a tweet"""
        logger.info(f"Liking tweet {tweet_id}")

        playwright, context, page = await self._get_browser_context()

        try:
            # Navigate to tweet
            tweet_url = f"https://twitter.com/i/status/{tweet_id}"
            await page.goto(tweet_url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(3)

            # Find and click like button
            like_button = await page.query_selector('[data-testid="like"]')

            if not like_button:
                raise Exception("Like button not found")

            await like_button.click()
            await asyncio.sleep(2)

            logger.info(f"Successfully liked tweet {tweet_id}")

            await context.close()
            await playwright.stop()

            return {"success": True, "tweet_id": tweet_id, "action": "liked"}

        except Exception as e:
            await context.close()
            await playwright.stop()
            raise e

    async def unlike_tweet(self, tweet_id: str) -> dict:
        """Unlike a tweet"""
        logger.info(f"Unliking tweet {tweet_id}")

        playwright, context, page = await self._get_browser_context()

        try:
            tweet_url = f"https://twitter.com/i/status/{tweet_id}"
            await page.goto(tweet_url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(3)

            # Find and click unlike button
            unlike_button = await page.query_selector('[data-testid="unlike"]')

            if not unlike_button:
                raise Exception("Unlike button not found (tweet may not be liked)")

            await unlike_button.click()
            await asyncio.sleep(2)

            logger.info(f"Successfully unliked tweet {tweet_id}")

            await context.close()
            await playwright.stop()

            return {"success": True, "tweet_id": tweet_id, "action": "unliked"}

        except Exception as e:
            await context.close()
            await playwright.stop()
            raise e

    async def retweet(self, tweet_id: str) -> dict:
        """Retweet a tweet"""
        logger.info(f"Retweeting tweet {tweet_id}")

        playwright, context, page = await self._get_browser_context()

        try:
            tweet_url = f"https://twitter.com/i/status/{tweet_id}"
            await page.goto(tweet_url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(3)

            # Click retweet button
            retweet_button = await page.query_selector('[data-testid="retweet"]')

            if not retweet_button:
                raise Exception("Retweet button not found")

            await retweet_button.click()
            await asyncio.sleep(1)

            # Click "Retweet" in the menu (not "Quote")
            retweet_confirm = await page.query_selector('[data-testid="retweetConfirm"]')

            if retweet_confirm:
                await retweet_confirm.click()
                await asyncio.sleep(2)

            logger.info(f"Successfully retweeted tweet {tweet_id}")

            await context.close()
            await playwright.stop()

            return {"success": True, "tweet_id": tweet_id, "action": "retweeted"}

        except Exception as e:
            await context.close()
            await playwright.stop()
            raise e

    async def unretweet(self, tweet_id: str) -> dict:
        """Undo retweet"""
        logger.info(f"Unretweeting tweet {tweet_id}")

        playwright, context, page = await self._get_browser_context()

        try:
            tweet_url = f"https://twitter.com/i/status/{tweet_id}"
            await page.goto(tweet_url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(3)

            # Click unretweet button
            unretweet_button = await page.query_selector('[data-testid="unretweet"]')

            if not unretweet_button:
                raise Exception("Unretweet button not found (tweet may not be retweeted)")

            await unretweet_button.click()
            await asyncio.sleep(1)

            # Confirm unretweet
            unretweet_confirm = await page.query_selector('[data-testid="unretweetConfirm"]')

            if unretweet_confirm:
                await unretweet_confirm.click()
                await asyncio.sleep(2)

            logger.info(f"Successfully unretweeted tweet {tweet_id}")

            await context.close()
            await playwright.stop()

            return {"success": True, "tweet_id": tweet_id, "action": "unretweeted"}

        except Exception as e:
            await context.close()
            await playwright.stop()
            raise e

    async def delete_tweet(self, tweet_id: str) -> dict:
        """Delete a tweet"""
        logger.info(f"Deleting tweet {tweet_id}")

        playwright, context, page = await self._get_browser_context()

        try:
            tweet_url = f"https://twitter.com/i/status/{tweet_id}"
            await page.goto(tweet_url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(3)

            # Click the "More" menu button
            more_button = await page.query_selector('[data-testid="caret"]')

            if not more_button:
                raise Exception("More menu button not found")

            await more_button.click()
            await asyncio.sleep(1)

            # Click "Delete" option
            delete_button = await page.query_selector('[data-testid="Dropdown"] [role="menuitem"]:has-text("Delete")')

            if not delete_button:
                raise Exception("Delete button not found (you may not own this tweet)")

            await delete_button.click()
            await asyncio.sleep(1)

            # Confirm deletion
            confirm_delete = await page.query_selector('[data-testid="confirmationSheetConfirm"]')

            if confirm_delete:
                await confirm_delete.click()
                await asyncio.sleep(2)

            logger.info(f"Successfully deleted tweet {tweet_id}")

            await context.close()
            await playwright.stop()

            return {"success": True, "tweet_id": tweet_id, "action": "deleted"}

        except Exception as e:
            await context.close()
            await playwright.stop()
            raise e

    async def get_tweet(self, tweet_id: str) -> dict:
        """Get tweet details"""
        logger.info(f"Getting tweet {tweet_id}")

        playwright, context, page = await self._get_browser_context()

        try:
            tweet_url = f"https://twitter.com/i/status/{tweet_id}"
            await page.goto(tweet_url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(3)

            # Extract tweet data
            tweet_article = await page.query_selector('article[data-testid="tweet"]')

            if not tweet_article:
                raise Exception("Tweet not found")

            # Get tweet text
            text_elem = await tweet_article.query_selector('[data-testid="tweetText"]')
            text = await text_elem.inner_text() if text_elem else ""

            # Get author
            author_elem = await tweet_article.query_selector('[data-testid="User-Name"] a[role="link"]')
            author_username = ""
            if author_elem:
                href = await author_elem.get_attribute('href')
                author_username = href.strip('/') if href else ""

            # Get stats
            reply_count = "0"
            retweet_count = "0"
            like_count = "0"

            reply_elem = await tweet_article.query_selector('[data-testid="reply"]')
            if reply_elem:
                reply_text = await reply_elem.inner_text()
                reply_count = reply_text if reply_text.isdigit() else "0"

            retweet_elem = await tweet_article.query_selector('[data-testid="retweet"]')
            if retweet_elem:
                retweet_text = await retweet_elem.inner_text()
                retweet_count = retweet_text if retweet_text.isdigit() else "0"

            like_elem = await tweet_article.query_selector('[data-testid="like"]')
            if like_elem:
                like_text = await like_elem.inner_text()
                like_count = like_text if like_text.isdigit() else "0"

            await context.close()
            await playwright.stop()

            return {
                "id": tweet_id,
                "text": text,
                "author_username": author_username,
                "reply_count": reply_count,
                "retweet_count": retweet_count,
                "like_count": like_count
            }

        except Exception as e:
            await context.close()
            await playwright.stop()
            raise e

    async def get_user_by_username(self, username: str) -> dict:
        """Get user profile by username"""
        logger.info(f"Getting user profile: @{username}")

        playwright, context, page = await self._get_browser_context()

        try:
            user_url = f"https://twitter.com/{username}"
            await page.goto(user_url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(3)

            # Extract user data
            name_elem = await page.query_selector('[data-testid="UserName"] span')
            name = await name_elem.inner_text() if name_elem else username

            bio_elem = await page.query_selector('[data-testid="UserDescription"]')
            bio = await bio_elem.inner_text() if bio_elem else ""

            # Get follower/following counts
            followers_elem = await page.query_selector('a[href$="/verified_followers"] span')
            followers_count = "0"
            if followers_elem:
                followers_text = await followers_elem.inner_text()
                followers_count = followers_text.replace(',', '')

            following_elem = await page.query_selector('a[href$="/following"] span')
            following_count = "0"
            if following_elem:
                following_text = await following_elem.inner_text()
                following_count = following_text.replace(',', '')

            await context.close()
            await playwright.stop()

            return {
                "id": username,
                "username": username,
                "name": name,
                "description": bio,
                "public_metrics": {
                    "followers_count": followers_count,
                    "following_count": following_count
                }
            }

        except Exception as e:
            await context.close()
            await playwright.stop()
            raise e

    async def follow_user(self, username: str) -> dict:
        """Follow a user"""
        logger.info(f"Following user @{username}")

        playwright, context, page = await self._get_browser_context()

        try:
            user_url = f"https://twitter.com/{username}"
            await page.goto(user_url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(3)

            follow_button = await page.query_selector('[data-testid*="follow"]')
            if not follow_button:
                raise Exception("Follow button not found (may already be following)")

            await follow_button.click()
            await asyncio.sleep(2)

            logger.info(f"Successfully followed @{username}")

            await context.close()
            await playwright.stop()

            return {"success": True, "username": username, "action": "followed"}

        except Exception as e:
            await context.close()
            await playwright.stop()
            raise e

    async def unfollow_user(self, username: str) -> dict:
        """Unfollow a user"""
        logger.info(f"Unfollowing user @{username}")

        playwright, context, page = await self._get_browser_context()

        try:
            user_url = f"https://twitter.com/{username}"
            await page.goto(user_url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(3)

            following_button = await page.query_selector('[data-testid*="unfollow"]')
            if not following_button:
                raise Exception("Unfollow button not found (may not be following)")

            await following_button.click()
            await asyncio.sleep(1)

            confirm_button = await page.query_selector('[data-testid="confirmationSheetConfirm"]')
            if confirm_button:
                await confirm_button.click()
                await asyncio.sleep(2)

            logger.info(f"Successfully unfollowed @{username}")

            await context.close()
            await playwright.stop()

            return {"success": True, "username": username, "action": "unfollowed"}

        except Exception as e:
            await context.close()
            await playwright.stop()
            raise e

    async def get_user_tweets(self, username: str, max_count: int = 20) -> list:
        """Get user's recent tweets"""
        logger.info(f"Getting tweets from @{username}")

        playwright, context, page = await self._get_browser_context()

        try:
            user_url = f"https://twitter.com/{username}"
            await page.goto(user_url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(3)

            tweets = []
            tweet_articles = await page.query_selector_all('article[data-testid="tweet"]')

            for article in tweet_articles[:max_count]:
                try:
                    text_elem = await article.query_selector('[data-testid="tweetText"]')
                    text = await text_elem.inner_text() if text_elem else ""

                    time_elem = await article.query_selector('time')
                    tweet_id = "unknown"
                    if time_elem:
                        parent_link = await time_elem.evaluate_handle('el => el.closest("a")')
                        href = await parent_link.get_attribute('href')
                        if href and '/status/' in href:
                            tweet_id = href.split('/status/')[-1].split('?')[0]

                    tweets.append({
                        "id": tweet_id,
                        "text": text,
                        "author_username": username
                    })

                except Exception as e:
                    logger.warning(f"Failed to parse tweet: {e}")
                    continue

            await context.close()
            await playwright.stop()

            return tweets

        except Exception as e:
            await context.close()
            await playwright.stop()
            raise e

    async def search_tweets(self, query: str, max_count: int = 20) -> list:
        """Search recent tweets"""
        logger.info(f"Searching tweets: {query}")

        playwright, context, page = await self._get_browser_context()

        try:
            search_url = f"https://twitter.com/search?q={query.replace(' ', '%20')}&src=typed_query&f=live"
            await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(3)

            tweets = []
            tweet_articles = await page.query_selector_all('article[data-testid="tweet"]')

            for article in tweet_articles[:max_count]:
                try:
                    text_elem = await article.query_selector('[data-testid="tweetText"]')
                    text = await text_elem.inner_text() if text_elem else ""

                    author_elem = await article.query_selector('[data-testid="User-Name"] a[role="link"]')
                    author_username = ""
                    if author_elem:
                        href = await author_elem.get_attribute('href')
                        author_username = href.strip('/') if href else ""

                    time_elem = await article.query_selector('time')
                    tweet_id = "unknown"
                    if time_elem:
                        parent_link = await time_elem.evaluate_handle('el => el.closest("a")')
                        href = await parent_link.get_attribute('href')
                        if href and '/status/' in href:
                            tweet_id = href.split('/status/')[-1].split('?')[0]

                    tweets.append({
                        "id": tweet_id,
                        "text": text,
                        "author_username": author_username
                    })

                except Exception as e:
                    logger.warning(f"Failed to parse tweet: {e}")
                    continue

            await context.close()
            await playwright.stop()

            return tweets

        except Exception as e:
            await context.close()
            await playwright.stop()
            raise e
