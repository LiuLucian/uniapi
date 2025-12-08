"""
TikTok API Compatible Endpoints
Proxies to tiktok_bridge_server.py (localhost:5003)
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

# TikTok bridge server URL
TIKTOK_BRIDGE_URL = "http://localhost:5003"


# Request/Response Models (matching TikTok API schema)
class UserProfileResponse(BaseModel):
    success: bool
    username: str
    profile_url: str
    bio: Optional[str] = None
    followers: Optional[str] = None
    likes: Optional[str] = None


class VideoItem(BaseModel):
    video_id: str
    video_url: str
    description: Optional[str] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    views: Optional[int] = None


class UserVideosResponse(BaseModel):
    success: bool
    username: str
    videos: List[VideoItem]


class VideoLikeRequest(BaseModel):
    video_url: str


class VideoCommentRequest(BaseModel):
    video_url: str
    comment_text: str


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
        "message": "TikTok API is running"
    }
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{TIKTOK_BRIDGE_URL}/health")

            if response.status_code == 200:
                return {
                    "status": "ok",
                    "message": "TikTok API is running",
                    "bridge_status": "connected"
                }
            else:
                return {
                    "status": "degraded",
                    "message": "TikTok API is running but bridge server is unreachable",
                    "bridge_status": "disconnected"
                }

    except Exception as e:
        return {
            "status": "degraded",
            "message": "TikTok API is running but bridge server is unreachable",
            "bridge_status": "disconnected",
            "error": str(e)
        }


@router.get("/users/{username}", response_model=UserProfileResponse)
async def get_user_profile(username: str):
    """
    Get TikTok user profile (GET /users/{username} equivalent)

    Response:
    {
        "success": true,
        "username": "username",
        "profile_url": "https://www.tiktok.com/@username",
        "bio": "User bio",
        "followers": "1.2M",
        "likes": "10.5M"
    }
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{TIKTOK_BRIDGE_URL}/user/{username}"
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return UserProfileResponse(
                success=result.get("success", False),
                username=result.get("username", username),
                profile_url=result.get("profile_url", ""),
                bio=result.get("bio"),
                followers=result.get("followers"),
                likes=result.get("likes")
            )

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to tiktok_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="TikTok bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{username}/videos", response_model=UserVideosResponse)
async def get_user_videos(username: str, max_count: int = 10):
    """
    Get TikTok user's videos (GET /users/{username}/videos)

    Query params: max_count (default: 10)

    Response:
    {
        "success": true,
        "username": "username",
        "videos": [
            {
                "video_id": "...",
                "video_url": "...",
                "description": "...",
                "likes": 1234,
                "comments": 56,
                "shares": 78,
                "views": 9012
            }
        ]
    }
    """
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(
                f"{TIKTOK_BRIDGE_URL}/user/{username}/videos?max_count={max_count}"
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            # Transform response to match model
            videos = []
            for video in result.get("videos", []):
                videos.append(VideoItem(
                    video_id=video.get("video_id", ""),
                    video_url=video.get("video_url", ""),
                    description=video.get("description"),
                    likes=video.get("likes"),
                    comments=video.get("comments"),
                    shares=video.get("shares"),
                    views=video.get("views")
                ))

            return UserVideosResponse(
                success=result.get("success", False),
                username=username,
                videos=videos
            )

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to tiktok_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="TikTok bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to get user videos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/videos/like")
async def like_video(request: VideoLikeRequest):
    """
    Like a TikTok video (POST /videos/like)

    Request:
    {
        "video_url": "https://www.tiktok.com/@user/video/123456"
    }

    Response:
    {
        "success": true,
        "message": "Video liked successfully"
    }
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{TIKTOK_BRIDGE_URL}/video/like",
                json={"video_url": request.video_url}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return {
                "success": result.get("success", False),
                "message": result.get("message", "Like completed")
            }

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to tiktok_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="TikTok bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to like video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/videos/comment")
async def comment_on_video(request: VideoCommentRequest):
    """
    Comment on a TikTok video (POST /videos/comment)

    Request:
    {
        "video_url": "https://www.tiktok.com/@user/video/123456",
        "comment_text": "Great video!"
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
                f"{TIKTOK_BRIDGE_URL}/video/comment",
                json={
                    "video_url": request.video_url,
                    "comment_text": request.comment_text
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
        logger.error(f"Failed to connect to tiktok_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="TikTok bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to comment on video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/{username}/follow")
async def follow_user(username: str):
    """
    Follow a TikTok user (POST /users/{username}/follow)

    Response:
    {
        "success": true,
        "message": "User followed successfully"
    }
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{TIKTOK_BRIDGE_URL}/user/{username}/follow"
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()

            return {
                "success": result.get("success", False),
                "message": result.get("message", "Follow completed")
            }

    except httpx.RequestError as e:
        logger.error(f"Failed to connect to tiktok_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="TikTok bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to follow user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dm/send", response_model=DMResponse)
async def send_direct_message(request: DMRequest):
    """
    Send TikTok direct message (POST /dm/send)

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
                f"{TIKTOK_BRIDGE_URL}/dm/send",
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
        logger.error(f"Failed to connect to tiktok_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="TikTok bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to send DM: {e}")
        raise HTTPException(status_code=500, detail=str(e))
