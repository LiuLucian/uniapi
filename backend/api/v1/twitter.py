"""
Twitter API v2 Compatible Endpoints
Proxies to twitter_bridge_server.py (localhost:5001)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from loguru import logger
import httpx

router = APIRouter()

# Twitter bridge server URL
TWITTER_BRIDGE_URL = "http://localhost:5001"


# Request/Response Models (matching Twitter API v2 schema)
class TweetCreateRequest(BaseModel):
    text: str
    reply_settings: Optional[str] = "everyone"


class TweetCreateResponse(BaseModel):
    data: dict


class UserMeResponse(BaseModel):
    data: dict


# Endpoints
@router.post("/tweets", response_model=TweetCreateResponse)
async def create_tweet(request: TweetCreateRequest):
    """
    Create a tweet (POST /2/tweets equivalent)

    Proxies to twitter_bridge_server.py which uses working Playwright implementation
    """
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Forward to twitter_bridge_server
            response = await client.post(
                f"{TWITTER_BRIDGE_URL}/post",
                json={"tweets": [{"text": request.text}]}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            # Convert bridge response to Twitter API v2 format
            tweet_id = result.get("tweet_ids", ["unknown"])[0] if result.get("tweet_ids") else "unknown"

            return TweetCreateResponse(data={
                "id": tweet_id,
                "text": request.text
            })

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to twitter_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Twitter bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to create tweet: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/me", response_model=UserMeResponse)
async def get_current_user():
    """
    Get current authenticated user info (GET /2/users/me equivalent)

    TODO: Implement proxy to twitter_bridge_server or extract from auth
    """
    # For now return mock data
    return UserMeResponse(data={
        "id": "1234567890",
        "name": "Lucian Liu",
        "username": "LucianLiu861650"
    })


# Tweet interactions
@router.post("/users/{user_id}/likes")
async def like_tweet(user_id: str, tweet_id: str):
    """
    Like a tweet (POST /2/users/:id/likes)

    Twitter API v2 format: POST /2/users/:id/likes
    Body: {"tweet_id": "1234567890"}
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{TWITTER_BRIDGE_URL}/like",
                json={"tweet_id": tweet_id}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return {"data": {"liked": result.get("success", False)}}

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to twitter_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Twitter bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to like tweet: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{user_id}/likes/{tweet_id}")
async def unlike_tweet(user_id: str, tweet_id: str):
    """
    Unlike a tweet (DELETE /2/users/:id/likes/:tweet_id)
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{TWITTER_BRIDGE_URL}/unlike",
                json={"tweet_id": tweet_id}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return {"data": {"liked": False}}

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to twitter_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Twitter bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to unlike tweet: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/{user_id}/retweets")
async def retweet(user_id: str, tweet_id: str):
    """
    Retweet a tweet (POST /2/users/:id/retweets)

    Body: {"tweet_id": "1234567890"}
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{TWITTER_BRIDGE_URL}/retweet",
                json={"tweet_id": tweet_id}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return {"data": {"retweeted": result.get("success", False)}}

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to twitter_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Twitter bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to retweet: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{source_user_id}/retweets/{tweet_id}")
async def unretweet(source_user_id: str, tweet_id: str):
    """
    Undo retweet (DELETE /2/users/:source_user_id/retweets/:tweet_id)
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{TWITTER_BRIDGE_URL}/unretweet",
                json={"tweet_id": tweet_id}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return {"data": {"retweeted": False}}

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to twitter_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Twitter bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to unretweet: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/tweets/{tweet_id}")
async def delete_tweet(tweet_id: str):
    """
    Delete a tweet (DELETE /2/tweets/:id)
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.delete(
                f"{TWITTER_BRIDGE_URL}/tweet/{tweet_id}"
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return {"data": {"deleted": result.get("success", False)}}

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to twitter_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Twitter bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to delete tweet: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tweets/{tweet_id}")
async def get_tweet(tweet_id: str):
    """
    Get tweet details (GET /2/tweets/:id)

    Returns tweet text, author, and engagement metrics
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{TWITTER_BRIDGE_URL}/tweet/{tweet_id}"
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            # Convert to Twitter API v2 format
            return {
                "data": {
                    "id": result.get("id"),
                    "text": result.get("text"),
                    "author_id": result.get("author_username"),
                    "public_metrics": {
                        "reply_count": int(result.get("reply_count", 0)),
                        "retweet_count": int(result.get("retweet_count", 0)),
                        "like_count": int(result.get("like_count", 0))
                    }
                }
            }

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to twitter_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Twitter bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to get tweet: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Phase 2: User Operations
@router.get("/users/by/username/{username}")
async def get_user_by_username(username: str):
    """
    Get user by username (GET /2/users/by/username/:username)
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{TWITTER_BRIDGE_URL}/user/{username}"
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return {"data": result}

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to twitter_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Twitter bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to get user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/{user_id}/following")
async def follow_user(user_id: str, target_username: str):
    """
    Follow a user (POST /2/users/:id/following)
    Body: {"target_user_id": "username"}
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{TWITTER_BRIDGE_URL}/follow",
                json={"username": target_username}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return {"data": {"following": result.get("success", False)}}

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to twitter_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Twitter bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to follow user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{source_user_id}/following/{target_username}")
async def unfollow_user(source_user_id: str, target_username: str):
    """
    Unfollow a user (DELETE /2/users/:source_user_id/following/:target_user_id)
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{TWITTER_BRIDGE_URL}/unfollow",
                json={"username": target_username}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return {"data": {"following": False}}

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to twitter_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Twitter bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to unfollow user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/tweets")
async def get_user_tweets(user_id: str, max_results: int = 20):
    """
    Get user's tweets (GET /2/users/:id/tweets)
    Query params: max_results (default: 20)
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{TWITTER_BRIDGE_URL}/user/{user_id}/tweets?max_count={max_results}"
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return {
                "data": result.get("tweets", []),
                "meta": {"result_count": result.get("count", 0)}
            }

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to twitter_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Twitter bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to get user tweets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Phase 3: Search & Discovery
@router.get("/tweets/search/recent")
async def search_tweets(query: str, max_results: int = 20):
    """
    Search recent tweets (GET /2/tweets/search/recent)
    Query params: query (required), max_results (default: 20)
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{TWITTER_BRIDGE_URL}/search/tweets",
                params={"query": query, "max_count": max_results}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return {
                "data": result.get("tweets", []),
                "meta": {"result_count": result.get("count", 0)}
            }

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to twitter_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Twitter bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to search tweets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

