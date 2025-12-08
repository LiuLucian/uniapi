"""
LinkedIn API Compatible Endpoints
Proxies to linkedin_bridge_server.py (localhost:5005)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging
import httpx

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LINKEDIN_BRIDGE_URL = "http://localhost:5005"


class UserProfileResponse(BaseModel):
    success: bool
    username: str
    profile_url: str
    name: Optional[str] = None
    headline: Optional[str] = None


class PostItem(BaseModel):
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    content: Optional[str] = None


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


@router.get("/health")
async def health_check():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{LINKEDIN_BRIDGE_URL}/health")
            if response.status_code == 200:
                return {"status": "ok", "message": "LinkedIn API is running", "bridge_status": "connected"}
            else:
                return {"status": "degraded", "message": "LinkedIn API is running but bridge server is unreachable", "bridge_status": "disconnected"}
    except Exception as e:
        return {"status": "degraded", "message": "LinkedIn API is running but bridge server is unreachable", "bridge_status": "disconnected", "error": str(e)}


@router.get("/users/{username}", response_model=UserProfileResponse)
async def get_user_profile(username: str):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(f"{LINKEDIN_BRIDGE_URL}/user/{username}")
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            result = response.json()
            return UserProfileResponse(success=result.get("success", False), username=result.get("username", username), profile_url=result.get("profile_url", ""), name=result.get("name"), headline=result.get("headline"))
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to linkedin_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="LinkedIn bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{username}/posts", response_model=UserPostsResponse)
async def get_user_posts(username: str, max_count: int = 10):
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(f"{LINKEDIN_BRIDGE_URL}/user/{username}/posts?max_count={max_count}")
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            result = response.json()
            posts = [PostItem(post_id=p.get("post_id"), post_url=p.get("post_url"), content=p.get("content")) for p in result.get("posts", [])]
            return UserPostsResponse(success=result.get("success", False), username=username, posts=posts)
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to linkedin_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="LinkedIn bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to get user posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/posts/like")
async def like_post(request: PostLikeRequest):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{LINKEDIN_BRIDGE_URL}/post/like", json={"post_url": request.post_url})
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            result = response.json()
            return {"success": result.get("success", False), "message": result.get("message", "Like completed")}
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to linkedin_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="LinkedIn bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to like post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/posts/comment")
async def comment_on_post(request: PostCommentRequest):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{LINKEDIN_BRIDGE_URL}/post/comment", json={"post_url": request.post_url, "comment": request.comment})
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            result = response.json()
            return {"success": result.get("success", False), "message": result.get("message", "Comment posted")}
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to linkedin_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="LinkedIn bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to comment on post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/{username}/connect")
async def connect_with_user(username: str):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{LINKEDIN_BRIDGE_URL}/user/{username}/connect")
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            result = response.json()
            return {"success": result.get("success", False), "message": result.get("message", "Connect completed")}
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to linkedin_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="LinkedIn bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to connect with user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dm/send", response_model=DMResponse)
async def send_direct_message(request: DMRequest):
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(f"{LINKEDIN_BRIDGE_URL}/dm/send", json={"username": request.username, "message": request.message})
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            result = response.json()
            return DMResponse(success=result.get("success", False), message=result.get("message", ""), username=result.get("username", request.username))
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to linkedin_bridge_server: {e}")
        raise HTTPException(status_code=503, detail="LinkedIn bridge server unavailable")
    except Exception as e:
        logger.error(f"Failed to send DM: {e}")
        raise HTTPException(status_code=500, detail=str(e))
