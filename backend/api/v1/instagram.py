"""
Instagram Graph API Compatible Endpoints
Proxies to instagram_bridge_server.py (localhost:5002)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import httpx

router = APIRouter()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instagram bridge server URL
INSTAGRAM_BRIDGE_URL = "http://localhost:5002"


# Request/Response Models (matching Instagram Graph API schema)
class MediaCreateRequest(BaseModel):
    caption: str
    image_path: str


class MediaCreateResponse(BaseModel):
    success: bool
    message: str
    url: Optional[str] = None


class UserProfileResponse(BaseModel):
    success: bool
    username: str
    profile_url: str
    bio: Optional[str] = None
    followers: Optional[str] = None


class DMRequest(BaseModel):
    username: str
    message: str


class DMResponse(BaseModel):
    success: bool
    message: str
    username: str


# Endpoints
@router.post("/media", response_model=MediaCreateResponse)
async def create_media(request: MediaCreateRequest):
    """
    Create Instagram post (POST /media equivalent)

    Proxies to instagram_bridge_server.py which uses Playwright implementation

    Request:
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
        async with httpx.AsyncClient(timeout=180.0) as client:
            # Forward to instagram_bridge_server
            response = await client.post(
                f"{INSTAGRAM_BRIDGE_URL}/post",
                json={
                    "caption": request.caption,
                    "image_path": request.image_path
                }
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return MediaCreateResponse(
                success=result.get("success", False),
                message=result.get("message", ""),
                url=result.get("url")
            )

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to instagram_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Instagram bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to create post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{username}", response_model=UserProfileResponse)
async def get_user_profile(username: str):
    """
    Get Instagram user profile (GET /users/{username} equivalent)

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
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{INSTAGRAM_BRIDGE_URL}/user/{username}"
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return UserProfileResponse(
                success=result.get("success", False),
                username=result.get("username", username),
                profile_url=result.get("profile_url", ""),
                bio=result.get("bio"),
                followers=result.get("followers")
            )

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to instagram_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Instagram bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/{username}/dm", response_model=DMResponse)
async def send_direct_message(username: str, request: DMRequest):
    """
    Send Instagram direct message (POST /users/{username}/dm equivalent)

    Request:
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
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Forward to instagram_bridge_server
            response = await client.post(
                f"{INSTAGRAM_BRIDGE_URL}/dm",
                json={
                    "username": request.username,
                    "message": request.message
                }
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return DMResponse(
                success=result.get("success", False),
                message=result.get("message", ""),
                username=result.get("username", username)
            )

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to instagram_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Instagram bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to send DM: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Post Interactions
@router.post("/media/{media_id}/like")
async def like_post(media_id: str):
    """
    Like an Instagram post (POST /media/{media_id}/like)

    Response:
    {
        "success": true,
        "message": "Post liked successfully"
    }
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{INSTAGRAM_BRIDGE_URL}/like",
                json={"post_url": media_id}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return {"success": result.get("success", False), "message": result.get("message", "Like completed")}

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to instagram_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Instagram bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to like post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/media/{media_id}/like")
async def unlike_post(media_id: str):
    """
    Unlike an Instagram post (DELETE /media/{media_id}/like)

    Response:
    {
        "success": true,
        "message": "Post unliked successfully"
    }
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{INSTAGRAM_BRIDGE_URL}/unlike",
                json={"post_url": media_id}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return {"success": result.get("success", False), "message": result.get("message", "Unlike completed")}

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to instagram_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Instagram bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to unlike post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# User Operations
@router.post("/users/{username}/follow")
async def follow_user(username: str):
    """
    Follow an Instagram user (POST /users/{username}/follow)

    Response:
    {
        "success": true,
        "message": "User followed successfully"
    }
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{INSTAGRAM_BRIDGE_URL}/follow",
                json={"username": username}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return {"success": result.get("success", False), "message": result.get("message", "Follow completed")}

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to instagram_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Instagram bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to follow user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{username}/follow")
async def unfollow_user(username: str):
    """
    Unfollow an Instagram user (DELETE /users/{username}/follow)

    Response:
    {
        "success": true,
        "message": "User unfollowed successfully"
    }
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{INSTAGRAM_BRIDGE_URL}/unfollow",
                json={"username": username}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return {"success": result.get("success", False), "message": result.get("message", "Unfollow completed")}

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to instagram_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Instagram bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to unfollow user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class CommentRequest(BaseModel):
    text: str


@router.post("/media/{media_id}/comments")
async def comment_on_post(media_id: str, request: CommentRequest):
    """
    Comment on an Instagram post (POST /media/{media_id}/comments)

    Request:
    {
        "text": "Great post!"
    }

    Response:
    {
        "success": true,
        "message": "Comment posted successfully"
    }
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{INSTAGRAM_BRIDGE_URL}/comment",
                json={"post_url": media_id, "comment": request.text}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return {"success": result.get("success", False), "message": result.get("message", "Comment posted")}

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to instagram_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Instagram bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to comment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/media/{media_id}")
async def get_post(media_id: str):
    """
    Get Instagram post details (GET /media/{media_id})

    Response:
    {
        "success": true,
        "media_id": "...",
        "caption": "...",
        "likes": 123,
        "comments": 45
    }
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{INSTAGRAM_BRIDGE_URL}/post/{media_id}"
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return result

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to instagram_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Instagram bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to get post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{username}/media")
async def get_user_posts(username: str, max_results: int = 20):
    """
    Get user's Instagram posts (GET /users/{username}/media)

    Query params: max_results (default: 20)

    Response:
    {
        "success": true,
        "posts": [...]
    }
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{INSTAGRAM_BRIDGE_URL}/user/{username}/posts?max_count={max_results}"
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return result

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to instagram_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Instagram bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to get user posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tags/{tag}/media/recent")
async def search_by_tag(tag: str, max_results: int = 20):
    """
    Search Instagram posts by hashtag (GET /tags/{tag}/media/recent)

    Query params: max_results (default: 20)

    Response:
    {
        "success": true,
        "posts": [...]
    }
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{INSTAGRAM_BRIDGE_URL}/search/tag/{tag}?max_count={max_results}"
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return result

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to instagram_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Instagram bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check endpoint

    Response:
    {
        "status": "ok",
        "message": "Instagram API is running"
    }
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{INSTAGRAM_BRIDGE_URL}/health")

            if response.status_code == 200:
                return {
                    "status": "ok",
                    "message": "Instagram API is running",
                    "bridge_status": "connected"
                }
            else:
                return {
                    "status": "degraded",
                    "message": "Instagram API is running but bridge server is unreachable",
                    "bridge_status": "disconnected"
                }

    except Exception as e:
        return {
            "status": "degraded",
            "message": "Instagram API is running but bridge server is unreachable",
            "bridge_status": "disconnected",
            "error": str(e)
        }
