"""
UniAPI - Universal Social Media API Platform
FastAPI Backend Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from api.v1 import twitter, instagram, tiktok, facebook, linkedin
from core.config import settings

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO")

app = FastAPI(
    title="UniAPI",
    description="Universal Social Media API Platform - Scraper-based API for all platforms",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(twitter.router, prefix="/api/v1/twitter", tags=["Twitter"])
app.include_router(instagram.router, prefix="/api/v1/instagram", tags=["Instagram"])
app.include_router(tiktok.router, prefix="/api/v1/tiktok", tags=["TikTok"])
app.include_router(facebook.router, prefix="/api/v1/facebook", tags=["Facebook"])
app.include_router(linkedin.router, prefix="/api/v1/linkedin", tags=["LinkedIn"])

@app.get("/")
async def root():
    return {
        "message": "UniAPI - Universal Social Media API Platform",
        "version": "1.0.0",
        "docs": "/api/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
