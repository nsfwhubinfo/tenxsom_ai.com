#!/usr/bin/env python3
"""
FastAPI wrapper for the MCP server to enable HTTP API access
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .server import UseAPIServer
from .database import get_database, close_database
from .config import UseAPIConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models for API requests
class TemplateRequest(BaseModel):
    template_data: Dict[str, Any]


class TemplateProcessRequest(BaseModel):
    template_name: str
    context_variables: Dict[str, Any]


class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]


# Global MCP server instance
mcp_server_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    global mcp_server_instance
    
    logger.info("🚀 Starting MCP Server API...")
    
    # Initialize MCP server
    config = UseAPIConfig()
    mcp_server_instance = UseAPIServer(config)
    
    # Initialize database
    try:
        db = await get_database()
        logger.info("✅ Database connection established")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    logger.info("✅ MCP Server API ready")
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down MCP Server API...")
    await close_database()
    logger.info("✅ Shutdown complete")


# Create FastAPI app with lifespan
app = FastAPI(
    title="TenxsomAI MCP Server API",
    description="Model Context Protocol server for template-based content generation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "mcp-server"}


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "TenxsomAI MCP Server",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "templates": "/api/templates",
            "tools": "/api/tools"
        }
    }


# Template Management APIs
@app.post("/api/templates")
async def store_template(request: TemplateRequest):
    """Store a new MCP template"""
    try:
        db = await get_database()
        template_id = await db.store_template(request.template_data)
        
        return {
            "status": "success",
            "message": f"Template '{request.template_data.get('template_name')}' stored successfully",
            "template_id": template_id
        }
    except Exception as e:
        logger.error(f"❌ Template storage failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/templates/{template_name}")
async def get_template(template_name: str):
    """Retrieve a template by name"""
    try:
        db = await get_database()
        template = await db.get_template(template_name)
        
        if not template:
            raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")
        
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Template retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/templates")
async def list_templates(
    archetype: str = None,
    target_platform: str = None,
    content_tier: str = None,
    limit: int = 50
):
    """List templates with optional filtering"""
    try:
        db = await get_database()
        templates = await db.list_templates(
            archetype=archetype,
            target_platform=target_platform,
            content_tier=content_tier,
            limit=limit
        )
        
        return {
            "templates": templates,
            "count": len(templates),
            "filters": {
                "archetype": archetype,
                "target_platform": target_platform,
                "content_tier": content_tier
            }
        }
    except Exception as e:
        logger.error(f"❌ Template listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/templates/process")
async def process_template(request: TemplateProcessRequest):
    """Process a template into an executable production plan"""
    try:
        # Use the MCP server's template operation handler
        result = await mcp_server_instance._handle_template_operation(
            "mcp_template_process",
            {
                "template_name": request.template_name,
                "context_variables": request.context_variables
            }
        )
        
        return result
    except Exception as e:
        logger.error(f"❌ Template processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/templates/{template_name}/analytics")
async def get_template_analytics(template_name: str):
    """Get analytics for a specific template"""
    try:
        result = await mcp_server_instance._handle_template_operation(
            "mcp_template_analytics",
            {"template_name": template_name}
        )
        
        return result
    except Exception as e:
        logger.error(f"❌ Template analytics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Tool APIs (proxy to MCP server)
@app.post("/api/tools/{tool_name}")
async def call_tool(tool_name: str, arguments: Dict[str, Any]):
    """Call a specific MCP tool"""
    try:
        # Use the MCP server's tool call handler
        result = await mcp_server_instance.handle_call_tool(tool_name, arguments)
        
        # Extract text content from MCP response
        if result and len(result) > 0:
            content = result[0].text
            try:
                # Try to parse as JSON
                import json
                return json.loads(content)
            except:
                # Return as text if not JSON
                return {"result": content}
        
        return {"result": "No response from tool"}
        
    except Exception as e:
        logger.error(f"❌ Tool call failed for {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tools")
async def list_tools():
    """List available MCP tools"""
    try:
        # Get tools from MCP server
        tools = await mcp_server_instance.server.list_tools()()
        
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                for tool in tools
            ],
            "count": len(tools)
        }
    except Exception as e:
        logger.error(f"❌ Tool listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Batch operations
@app.post("/api/batch/templates")
async def batch_load_templates(templates: List[Dict[str, Any]]):
    """Batch load multiple templates"""
    try:
        db = await get_database()
        results = []
        
        for template_data in templates:
            try:
                template_id = await db.store_template(template_data)
                results.append({
                    "template_name": template_data.get("template_name"),
                    "status": "success",
                    "template_id": template_id
                })
            except Exception as e:
                results.append({
                    "template_name": template_data.get("template_name", "unknown"),
                    "status": "error",
                    "error": str(e)
                })
        
        success_count = len([r for r in results if r["status"] == "success"])
        
        return {
            "total": len(templates),
            "successful": success_count,
            "failed": len(templates) - success_count,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ Batch template loading failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# System information
@app.get("/api/status")
async def get_system_status():
    """Get system status and metrics"""
    try:
        db = await get_database()
        
        # Get template count
        templates = await db.list_templates(limit=1000)
        template_count = len(templates)
        
        # Get template distribution
        tier_distribution = {}
        archetype_distribution = {}
        
        for template in templates:
            tier = template.get("content_tier", "unknown")
            tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
            
            archetype = template.get("archetype", "unknown")
            archetype_distribution[archetype] = archetype_distribution.get(archetype, 0) + 1
        
        return {
            "status": "operational",
            "database_connected": True,
            "template_count": template_count,
            "tier_distribution": tier_distribution,
            "archetype_distribution": archetype_distribution,
            "environment": {
                "database_url": bool(os.getenv("DATABASE_URL")),
                "useapi_token": bool(os.getenv("USEAPI_BEARER_TOKEN")),
                "google_credentials": bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Status check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "database_connected": False
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)