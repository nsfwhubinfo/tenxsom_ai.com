#!/usr/bin/env python3
"""
Simple FastAPI wrapper for quick deployment testing
"""

import asyncio
import logging
import os
from typing import Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TenxsomAI MCP Server API",
    description="Model Context Protocol server for template-based content generation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "mcp-server", "mode": "simple"}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "TenxsomAI MCP Server",
        "version": "1.0.0",
        "status": "running",
        "mode": "simple",
        "endpoints": {
            "health": "/health",
            "status": "/api/status"
        }
    }

@app.get("/api/status")
async def get_system_status():
    """Get system status"""
    return {
        "status": "operational",
        "mode": "simple",
        "environment": {
            "database_url": bool(os.getenv("DATABASE_URL")),
            "useapi_token": bool(os.getenv("USEAPI_BEARER_TOKEN")),
            "port": os.getenv("PORT", "8000")
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)