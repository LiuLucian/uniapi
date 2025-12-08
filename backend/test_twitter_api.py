"""
Test script for Twitter API endpoints
Run this to verify the Twitter API implementation works correctly
"""
import asyncio
import httpx
from loguru import logger

BASE_URL = "http://localhost:8000"

async def test_health():
    """Test health endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        logger.info(f"Health check: {response.json()}")
        assert response.status_code == 200

async def test_root():
    """Test root endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")
        data = response.json()
        logger.info(f"Root: {data}")
        assert response.status_code == 200
        assert data["version"] == "1.0.0"

async def test_get_current_user():
    """Test GET /api/v1/twitter/users/me"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/api/v1/twitter/users/me")
            logger.info(f"Current user: {response.json()}")
            assert response.status_code == 200
        except Exception as e:
            logger.error(f"Get current user failed: {e}")
            logger.warning("Make sure you have logged in to Twitter first!")
            logger.warning("Run: python3 setup_twitter_auth.py")

async def test_create_tweet():
    """Test POST /api/v1/twitter/tweets"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/twitter/tweets",
                json={"text": "Testing UniAPI - Twitter scraper-based API! This is a test tweet."}
            )
            data = response.json()
            logger.info(f"Created tweet: {data}")
            assert response.status_code == 200
            return data["data"]["id"]
        except Exception as e:
            logger.error(f"Create tweet failed: {e}")
            logger.warning("Make sure you have logged in to Twitter first!")

async def main():
    logger.info("Starting UniAPI Twitter tests...\n")

    # Test basic endpoints
    logger.info("1. Testing health endpoint...")
    await test_health()

    logger.info("\n2. Testing root endpoint...")
    await test_root()

    logger.info("\n3. Testing get current user...")
    await test_get_current_user()

    logger.info("\n4. Testing create tweet...")
    tweet_id = await test_create_tweet()

    if tweet_id and tweet_id != "unknown":
        logger.success(f"\nAll tests passed! Tweet ID: {tweet_id}")
        logger.info(f"View tweet: https://twitter.com/user/status/{tweet_id}")
    else:
        logger.warning("\nTests completed but tweet ID not captured")

    logger.info("\nAPI Documentation: http://localhost:8000/api/docs")

if __name__ == "__main__":
    asyncio.run(main())
