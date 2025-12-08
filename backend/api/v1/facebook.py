"""
Facebook Graph API Compatible Endpoints
Proxies to facebook_bridge_server.py (localhost:5004)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging
import httpx

router = APIRouter()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Facebook bridge server URL
FACEBOOK_BRIDGE_URL = "http://localhost:5004"


# Request/Response Models
class UserProfileResponse(BaseModel):
    success: bool
    username: str
    profile_url: str
    name: Optional[str] = None
    bio: Optional[str] = None


class PostItem(BaseModel):
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    content: Optional[str] = None
    likes: Optional[int] = None
    comments: Optional[int] = None


class UserPostsResponse(BaseModel):
    success: bool
    username: str
    posts: List[PostItem]


class PostLikeRequest(BaseModel):
    post_url: str


class PostCommentRequest(BaseModel):
    post_url: str
    comment: str


class DMRequest(BaseModel):
    username: str
    message: str


class DMResponse(BaseModel):
    success: bool
    message: str
    username: str


# Endpoints
@router.get("/health")
async def health_check():
    """
    Health check endpoint

    Response:
    {
        "status": "ok",
        "message": "Facebook API is running"
    }
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{FACEBOOK_BRIDGE_URL}/health")

            if response.status_code == 200:
                return {
                    "status": "ok",
                    "message": "Facebook API is running",
                    "bridge_status": "connected"
                }
            else:
                return {
                    "status": "degraded",
                    "message": "Facebook API is running but bridge server is unreachable",
                    "bridge_status": "disconnected"
                }

    except Exception as e:
        return {
            "status": "degraded",
            "message": "Facebook API is running but bridge server is unreachable",
            "bridge_status": "disconnected",
            "error": str(e)
        }


@router.get("/users/{username}", response_model=UserProfileResponse)
async def get_user_profile(username: str):
    """
    Get Facebook user profile

    Response:
    {
        "success": true,
        "username": "username",
        "profile_url": "https://www.facebook.com/username",
        "name": "User Name",
        "bio": "User bio"
    }
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{FACEBOOK_BRIDGE_URL}/user/{username}"
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return UserProfileResponse(
                success=result.get("success", False),
                username=result.get("username", username),
                profile_url=result.get("profile_url", ""),
                name=result.get("name"),
                bio=result.get("bio")
            )

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to facebook_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Facebook bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{username}/posts", response_model=UserPostsResponse)
async def get_user_posts(username: str, max_count: int = 10):
    """
    Get Facebook user's posts

    Query params: max_count (default: 10)

    Response:
    {
        "success": true,
        "username": "username",
        "posts": [...]
    }
    """
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(
                f"{FACEBOOK_BRIDGE_URL}/user/{username}/posts?max_count={max_count}"
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            posts = []
            for post in result.get("posts", []):
                posts.append(PostItem(
                    post_id=post.get("post_id"),
                    post_url=post.get("post_url"),
                    content=post.get("content"),
                    likes=post.get("likes"),
                    comments=post.get("comments")
                ))

            return UserPostsResponse(
                success=result.get("success", False),
                username=username,
                posts=posts
            )

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to facebook_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Facebook bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to get user posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/posts/like")
async def like_post(request: PostLikeRequest):
    """
    Like a Facebook post

    Request:
    {
        "post_url": "https://www.facebook.com/..."
    }

    Response:
    {
        "success": true,
        "message": "Post liked successfully"
    }
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{FACEBOOK_BRIDGE_URL}/post/like",
                json={"post_url": request.post_url}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return {
                "success": result.get("success", False),
                "message": result.get("message", "Like completed")
            }

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to facebook_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Facebook bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to like post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/posts/comment")
async def comment_on_post(request: PostCommentRequest):
    """
    Comment on a Facebook post

    Request:
    {
        "post_url": "https://www.facebook.com/...",
        "comment": "Great post!"
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
                f"{FACEBOOK_BRIDGE_URL}/post/comment",
                json={
                    "post_url": request.post_url,
                    "comment": request.comment
                }
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return {
                "success": result.get("success", False),
                "message": result.get("message", "Comment posted")
            }

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to facebook_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Facebook bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to comment on post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/{username}/follow")
async def follow_user(username: str):
    """
    Follow a Facebook user

    Response:
    {
        "success": true,
        "message": "User followed successfully"
    }
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{FACEBOOK_BRIDGE_URL}/user/{username}/follow"
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return {
                "success": result.get("success", False),
                "message": result.get("message", "Follow completed")
            }

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to facebook_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Facebook bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to follow user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dm/send", response_model=DMResponse)
async def send_direct_message(request: DMRequest):
    """
    Send Facebook direct message

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
            response = await client.post(
                f"{FACEBOOK_BRIDGE_URL}/dm/send",
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
                username=result.get("username", request.username)
            )

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to facebook_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="Facebook bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to send DM: {e}")
        raise HTTPException(status_code=500, detail=str(e))
