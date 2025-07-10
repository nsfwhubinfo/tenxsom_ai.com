#!/usr/bin/env python3
"""
Content Pipeline Server - Cloud-ready FastAPI application
Orchestrates the 96 videos/day content generation pipeline
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
import logging
import os
import json
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Import our components
from monetization_strategy_executor import MonetizationStrategyExecutor
from analytics_tracker import AnalyticsTracker
from content_upload_orchestrator import ContentUploadOrchestrator
from production_config_manager import ProductionConfigManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="TenxsomAI Content Pipeline",
    description="Cloud-native content generation orchestrator",
    version="1.0.0"
)

# Initialize components
config_manager = ProductionConfigManager()
analytics_tracker = AnalyticsTracker()
monetization_executor = None  # Initialize on startup
upload_orchestrator = None

class ContentRequest(BaseModel):
    """Content generation request model"""
    topic: Optional[str] = None
    platform: str = "youtube"
    quality_tier: str = "standard"
    duration: int = 60
    scheduled_time: Optional[datetime] = None
    priority: int = 1

class BatchContentRequest(BaseModel):
    """Batch content generation request"""
    count: int = 96
    platforms: List[str] = ["youtube"]
    date: Optional[str] = None

class SystemStatus(BaseModel):
    """System status response"""
    healthy: bool
    services: Dict[str, Any]
    metrics: Dict[str, Any]
    timestamp: datetime

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global monetization_executor, upload_orchestrator
    
    logger.info("🚀 Starting TenxsomAI Content Pipeline Server")
    
    # Initialize monetization executor
    try:
        monetization_executor = MonetizationStrategyExecutor()
        logger.info("✅ Monetization executor initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize monetization executor: {e}")
    
    # Initialize upload orchestrator
    try:
        upload_orchestrator = ContentUploadOrchestrator()
        logger.info("✅ Upload orchestrator initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize upload orchestrator: {e}")
    
    logger.info("✅ Content Pipeline Server ready")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "TenxsomAI Content Pipeline",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "generate": "/api/generate",
            "batch": "/api/batch",
            "analytics": "/api/analytics"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    try:
        # Check component health
        checks = {
            "config_manager": config_manager is not None,
            "analytics_tracker": analytics_tracker is not None,
            "monetization_executor": monetization_executor is not None,
            "upload_orchestrator": upload_orchestrator is not None
        }
        
        all_healthy = all(checks.values())
        
        return {
            "healthy": all_healthy,
            "components": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/status")
async def get_status():
    """Get detailed system status"""
    try:
        # Get analytics metrics
        metrics = await analytics_tracker.get_current_metrics()
        
        # Get service status
        services = {
            "mcp_server": await check_mcp_server_status(),
            "video_worker": await check_video_worker_status(),
            "youtube_api": await check_youtube_status()
        }
        
        return SystemStatus(
            healthy=all(s.get("healthy", False) for s in services.values()),
            services=services,
            metrics=metrics,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate")
async def generate_content(
    request: ContentRequest,
    background_tasks: BackgroundTasks
):
    """Generate a single piece of content"""
    try:
        logger.info(f"📹 Content generation request: {request.dict()}")
        
        # Generate content ID
        content_id = f"content_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Add to background tasks
        background_tasks.add_task(
            process_content_generation,
            content_id,
            request
        )
        
        return {
            "status": "accepted",
            "content_id": content_id,
            "message": "Content generation started",
            "estimated_completion": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Generation request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/batch")
async def generate_batch(
    request: BatchContentRequest,
    background_tasks: BackgroundTasks
):
    """Generate batch content (daily 96 videos)"""
    try:
        logger.info(f"📦 Batch generation request: {request.dict()}")
        
        # Create batch ID
        batch_id = f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Start batch processing
        background_tasks.add_task(
            process_batch_generation,
            batch_id,
            request
        )
        
        return {
            "status": "accepted",
            "batch_id": batch_id,
            "count": request.count,
            "message": f"Batch generation for {request.count} videos started",
            "estimated_completion": (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Batch request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics")
async def get_analytics(days: int = 7):
    """Get analytics for the specified period"""
    try:
        analytics = await analytics_tracker.get_analytics_summary(days)
        
        return {
            "period_days": days,
            "analytics": analytics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Analytics request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/monetization/status")
async def get_monetization_status():
    """Get current monetization status"""
    try:
        if not monetization_executor:
            raise HTTPException(status_code=503, detail="Monetization executor not initialized")
        
        status = await monetization_executor.get_monetization_status()
        
        return {
            "status": status,
            "daily_target": 96,
            "monthly_cost_target": 48,
            "revenue_projections": {
                "low": 576,
                "high": 17280
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Monetization status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task processors
async def process_content_generation(content_id: str, request: ContentRequest):
    """Process content generation in background"""
    try:
        logger.info(f"🎬 Processing content generation: {content_id}")
        
        # Execute monetization strategy
        if monetization_executor:
            result = await monetization_executor.generate_content(
                content_id=content_id,
                platform=request.platform,
                quality_tier=request.quality_tier,
                topic=request.topic,
                duration=request.duration
            )
            
            # Track analytics
            await analytics_tracker.track_generation(content_id, result)
            
            # Upload if successful
            if result.get("success") and upload_orchestrator:
                await upload_orchestrator.upload_content(content_id, result)
        
        logger.info(f"✅ Content generation completed: {content_id}")
        
    except Exception as e:
        logger.error(f"❌ Content generation failed: {content_id} - {e}")

async def process_batch_generation(batch_id: str, request: BatchContentRequest):
    """Process batch content generation"""
    try:
        logger.info(f"🎬 Processing batch generation: {batch_id}")
        
        if monetization_executor:
            # Execute daily production
            results = await monetization_executor.execute_daily_production(
                target_count=request.count,
                platforms=request.platforms
            )
            
            # Track batch analytics
            await analytics_tracker.track_batch(batch_id, results)
        
        logger.info(f"✅ Batch generation completed: {batch_id}")
        
    except Exception as e:
        logger.error(f"❌ Batch generation failed: {batch_id} - {e}")

# Utility functions
async def check_mcp_server_status():
    """Check MCP server status"""
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://tenxsom-mcp-server-540103863590.us-central1.run.app/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                return {
                    "healthy": response.status == 200,
                    "status_code": response.status
                }
    except:
        return {"healthy": False, "error": "Connection failed"}

async def check_video_worker_status():
    """Check video worker status"""
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://tenxsom-video-worker-hpkm6siuqq-uc.a.run.app/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                return {
                    "healthy": response.status == 200,
                    "status_code": response.status
                }
    except:
        return {"healthy": False, "error": "Connection failed"}

async def check_youtube_status():
    """Check YouTube API status"""
    try:
        # Check if YouTube credentials are available
        youtube_token_exists = os.path.exists(
            "youtube-upload-pipeline/auth/channel_tokens/token_hub.json"
        )
        return {
            "healthy": youtube_token_exists,
            "authenticated": youtube_token_exists
        }
    except:
        return {"healthy": False, "error": "YouTube check failed"}

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)