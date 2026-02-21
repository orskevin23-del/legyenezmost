from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from datetime import datetime, timezone

# Import routes
from routes import auth, scripts, hooks, metrics, videos, analytics, notion_analytics, saved_voices, voice_preferences
from utils.database import init_database
from database import db

# Create FastAPI app
app = FastAPI(
    title="LEGYENEZ - Short Video Factory API",
    version="1.0.0",
    description="AI-powered German Faith-niche YouTube Shorts generation system"
)

# API Router
api_router = APIRouter(prefix="/api")

# Health check
@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(scripts.router, prefix="/scripts", tags=["Scripts"])
api_router.include_router(hooks.router, prefix="/hooks", tags=["Hooks"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
api_router.include_router(videos.router, prefix="/videos", tags=["Videos"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(notion_analytics.router, prefix="/notion-analytics", tags=["Notion Analytics"])
api_router.include_router(saved_voices.router, prefix="/saved-voices", tags=["Saved Voices"])
api_router.include_router(voice_preferences.router, prefix="/voice-preferences", tags=["Voice Preferences"])

# Include router in app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize database indexes on startup"""
    logger.info("Starting LEGYENEZ API Server...")
    await init_database(db)
    logger.info("Database initialized with indexes")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    logger.info("Shutting down LEGYENEZ API Server...")
    from database import client
    client.close()

@app.get("/")
async def root():
    return {
        "message": "LEGYENEZ - Short Video Factory API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }