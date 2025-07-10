"""
Main MCP server implementation for UseAPI.net services
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import urlparse

import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio

from .client import UseAPIClient
from .config import UseAPIConfig, get_service_config, validate_prompt, validate_aspect_ratio, validate_model
from .exceptions import UseAPIError, UseAPIValidationError
from .database import get_database, close_database
from .template_processor import TemplateProcessor
from .tools import (
    MidjourneyTools,
    RunwayTools,
    MiniMaxTools,
    KlingTools,
    LTXStudioTools,
    PixVerseTools,
    PikaTools,
    MurekaTools,
    TemPolorTools,
    InsightFaceSwapTools,
)

logger = logging.getLogger(__name__)


class UseAPIServer:
    """MCP server for UseAPI.net AI services"""
    
    def __init__(self, config: Optional[UseAPIConfig] = None):
        """Initialize the UseAPI MCP server"""
        self.config = config or UseAPIConfig()
        self.server = Server("useapi-mcp-server")
        self.client: Optional[UseAPIClient] = None
        self.template_processor = TemplateProcessor()
        
        # Tool handlers
        self.tools: Dict[str, Any] = {}
        
        # Setup logging
        logging.basicConfig(
            level=self.config.log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # Register handlers
        self._setup_handlers()
        self._register_tools()
        
    def _setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List all available tools"""
            return [
                # Midjourney tools
                types.Tool(
                    name="midjourney_imagine",
                    description="Generate images using Midjourney AI",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Text prompt for image generation",
                                "maxLength": 4000
                            },
                            "model": {
                                "type": "string",
                                "description": "Midjourney model version",
                                "enum": ["v6.1", "v6.0", "v5.2", "niji6", "niji5"],
                                "default": "v6.1"
                            },
                            "aspect_ratio": {
                                "type": "string",
                                "description": "Image aspect ratio",
                                "enum": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
                                "default": "1:1"
                            },
                            "quality": {
                                "type": "string",
                                "description": "Image quality setting",
                                "enum": ["0.25", "0.5", "1", "2"],
                                "default": "1"
                            },
                            "stylize": {
                                "type": "integer",
                                "description": "Stylization strength (0-1000)",
                                "minimum": 0,
                                "maximum": 1000,
                                "default": 100
                            }
                        },
                        "required": ["prompt"]
                    }
                ),
                types.Tool(
                    name="midjourney_upscale",
                    description="Upscale a Midjourney image",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "image_id": {
                                "type": "string",
                                "description": "ID of the image to upscale"
                            },
                            "upscale_index": {
                                "type": "integer",
                                "description": "Index of the image to upscale (1-4)",
                                "minimum": 1,
                                "maximum": 4
                            }
                        },
                        "required": ["image_id", "upscale_index"]
                    }
                ),
                types.Tool(
                    name="midjourney_variations",
                    description="Create variations of a Midjourney image",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "image_id": {
                                "type": "string",
                                "description": "ID of the image to create variations from"
                            },
                            "variation_index": {
                                "type": "integer",
                                "description": "Index of the image for variations (1-4)",
                                "minimum": 1,
                                "maximum": 4
                            }
                        },
                        "required": ["image_id", "variation_index"]
                    }
                ),
                
                # LTX Studio tools
                types.Tool(
                    name="ltx_studio_video_create",
                    description="Generate videos using LTX Studio (LTX-Video, Veo models)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Text prompt for video generation",
                                "maxLength": 3000
                            },
                            "model": {
                                "type": "string",
                                "description": "Video generation model",
                                "enum": ["veo2", "veo3", "ltx-video"],
                                "default": "veo2"
                            },
                            "duration": {
                                "type": "integer",
                                "description": "Video duration in seconds (fixed at 5 for reliability)",
                                "minimum": 5,
                                "maximum": 5,
                                "default": 5
                            },
                            "aspect_ratio": {
                                "type": "string",
                                "description": "Video aspect ratio",
                                "enum": ["16:9", "9:16", "1:1", "4:3", "3:4"],
                                "default": "16:9"
                            },
                            "start_image_url": {
                                "type": "string",
                                "description": "Optional starting image URL",
                                "format": "uri"
                            }
                        },
                        "required": ["prompt"]
                    }
                ),
                types.Tool(
                    name="ltx_studio_image_create",
                    description="Generate images using LTX Studio FLUX model",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Text prompt for image generation",
                                "maxLength": 3000
                            },
                            "width": {
                                "type": "integer",
                                "description": "Image width",
                                "enum": [512, 768, 1024, 1536, 2048],
                                "default": 1024
                            },
                            "height": {
                                "type": "integer",
                                "description": "Image height",
                                "enum": [512, 768, 1024, 1536, 2048],
                                "default": 1024
                            },
                            "guidance_scale": {
                                "type": "number",
                                "description": "How closely to follow the prompt",
                                "minimum": 1.0,
                                "maximum": 20.0,
                                "default": 7.5
                            }
                        },
                        "required": ["prompt"]
                    }
                ),
                
                # Runway tools
                types.Tool(
                    name="runway_image_to_video",
                    description="Convert images to videos using Runway AI",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "image_url": {
                                "type": "string",
                                "description": "URL of the input image",
                                "format": "uri"
                            },
                            "prompt": {
                                "type": "string",
                                "description": "Optional text prompt for video generation",
                                "maxLength": 2000
                            },
                            "model": {
                                "type": "string",
                                "description": "Runway model version",
                                "enum": ["gen4turbo", "gen3alpha", "gen3turbo"],
                                "default": "gen3alpha"
                            },
                            "duration": {
                                "type": "integer",
                                "description": "Video duration in seconds",
                                "minimum": 1,
                                "maximum": 10,
                                "default": 5
                            }
                        },
                        "required": ["image_url"]
                    }
                ),
                
                # MiniMax tools
                types.Tool(
                    name="minimax_video_create",
                    description="Generate videos using MiniMax/Hailuo AI",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Text prompt for video generation",
                                "maxLength": 5000
                            },
                            "model": {
                                "type": "string",
                                "description": "MiniMax model version",
                                "enum": ["video-01"],
                                "default": "video-01"
                            },
                            "duration": {
                                "type": "integer",
                                "description": "Video duration in seconds",
                                "minimum": 1,
                                "maximum": 6,
                                "default": 6
                            }
                        },
                        "required": ["prompt"]
                    }
                ),
                types.Tool(
                    name="minimax_chat",
                    description="Chat with MiniMax LLM models",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Message to send to the AI"
                            },
                            "model": {
                                "type": "string",
                                "description": "MiniMax chat model",
                                "enum": ["text-01", "m1"],
                                "default": "text-01"
                            },
                            "system_prompt": {
                                "type": "string",
                                "description": "Optional system prompt"
                            },
                            "temperature": {
                                "type": "number",
                                "description": "Response creativity (0.0-1.0)",
                                "minimum": 0.0,
                                "maximum": 1.0,
                                "default": 0.7
                            }
                        },
                        "required": ["message"]
                    }
                ),
                
                # Music generation tools
                types.Tool(
                    name="mureka_music_create",
                    description="Generate music using Mureka AI (SkyMusic 2.0)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Text description of the music to generate",
                                "maxLength": 3000
                            },
                            "style": {
                                "type": "string",
                                "description": "Musical style or genre"
                            },
                            "duration": {
                                "type": "integer",
                                "description": "Music duration in seconds",
                                "minimum": 10,
                                "maximum": 180,
                                "default": 30
                            },
                            "instrumental": {
                                "type": "boolean",
                                "description": "Generate instrumental music only",
                                "default": False
                            }
                        },
                        "required": ["prompt"]
                    }
                ),
                
                # MCP Template tools
                types.Tool(
                    name="mcp_template_store",
                    description="Store a new MCP template in the database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "template_data": {
                                "type": "object",
                                "description": "Complete MCP template JSON data",
                                "required": ["template_name", "scenes"]
                            }
                        },
                        "required": ["template_data"]
                    }
                ),
                types.Tool(
                    name="mcp_template_get",
                    description="Retrieve an MCP template by name",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "template_name": {
                                "type": "string",
                                "description": "Name of the template to retrieve"
                            }
                        },
                        "required": ["template_name"]
                    }
                ),
                types.Tool(
                    name="mcp_template_list",
                    description="List available MCP templates with optional filtering",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "archetype": {
                                "type": "string",
                                "description": "Filter by archetype (e.g., 'documentary_mystery', 'viral_shorts')"
                            },
                            "target_platform": {
                                "type": "string",
                                "description": "Filter by target platform (e.g., 'youtube', 'tiktok')"
                            },
                            "content_tier": {
                                "type": "string",
                                "description": "Filter by content tier (premium, standard, volume)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of templates to return",
                                "default": 50,
                                "minimum": 1,
                                "maximum": 100
                            }
                        }
                    }
                ),
                types.Tool(
                    name="mcp_template_process",
                    description="Process an MCP template into an executable production plan",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "template_name": {
                                "type": "string",
                                "description": "Name of the template to process"
                            },
                            "context_variables": {
                                "type": "object",
                                "description": "Variables to substitute in the template (e.g., topic, key_points, etc.)"
                            }
                        },
                        "required": ["template_name", "context_variables"]
                    }
                ),
                types.Tool(
                    name="mcp_template_analytics",
                    description="Get analytics and performance data for a template",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "template_name": {
                                "type": "string",
                                "description": "Name of the template to analyze"
                            }
                        },
                        "required": ["template_name"]
                    }
                ),
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls"""
            try:
                if not self.client:
                    self.client = UseAPIClient(self.config)
                
                # Route to appropriate tool handler
                if name.startswith("mcp_template_"):
                    # Handle MCP template operations
                    result = await self._handle_template_operation(name, arguments)
                elif name.startswith("midjourney_"):
                    handler = MidjourneyTools(self.client)
                    result = await handler.execute(name, arguments)
                elif name.startswith("ltx_studio_"):
                    handler = LTXStudioTools(self.client)
                    result = await handler.execute(name, arguments)
                elif name.startswith("runway_"):
                    handler = RunwayTools(self.client)
                    result = await handler.execute(name, arguments)
                elif name.startswith("minimax_"):
                    handler = MiniMaxTools(self.client)
                    result = await handler.execute(name, arguments)
                elif name.startswith("kling_"):
                    handler = KlingTools(self.client)
                    result = await handler.execute(name, arguments)
                elif name.startswith("pixverse_"):
                    handler = PixVerseTools(self.client)
                    result = await handler.execute(name, arguments)
                elif name.startswith("pika_"):
                    handler = PikaTools(self.client)
                    result = await handler.execute(name, arguments)
                elif name.startswith("mureka_"):
                    handler = MurekaTools(self.client)
                    result = await handler.execute(name, arguments)
                elif name.startswith("tempolor_"):
                    handler = TemPolorTools(self.client)
                    result = await handler.execute(name, arguments)
                elif name.startswith("insight_"):
                    handler = InsightFaceSwapTools(self.client)
                    result = await handler.execute(name, arguments)
                else:
                    raise UseAPIError(f"Unknown tool: {name}")
                
                # Format response
                if isinstance(result, dict):
                    content = json.dumps(result, indent=2)
                else:
                    content = str(result)
                
                return [types.TextContent(type="text", text=content)]
                
            except UseAPIValidationError as e:
                error_msg = f"Validation error: {e.message}"
                if e.field:
                    error_msg += f" (field: {e.field})"
                return [types.TextContent(type="text", text=error_msg)]
            except UseAPIError as e:
                return [types.TextContent(type="text", text=f"API error: {e.message}")]
            except Exception as e:
                logger.exception(f"Unexpected error in tool {name}")
                return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[types.Resource]:
            """List available resources"""
            return [
                types.Resource(
                    uri="useapi://jobs",
                    name="Job Status List",
                    description="List all jobs and their current status",
                    mimeType="application/json"
                ),
                types.Resource(
                    uri="useapi://account",
                    name="Account Information",
                    description="Get account information and credit balance",
                    mimeType="application/json"
                ),
                types.Resource(
                    uri="useapi://models",
                    name="Available Models",
                    description="List all available models for each service",
                    mimeType="application/json"
                ),
                types.Resource(
                    uri="useapi://history",
                    name="Generation History",
                    description="Recent generation history across all services",
                    mimeType="application/json"
                ),
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read resource content"""
            try:
                if not self.client:
                    self.client = UseAPIClient(self.config)
                
                parsed_uri = urlparse(uri)
                path = parsed_uri.path
                
                if path == "/jobs":
                    # List all jobs
                    jobs = await self.client.list_jobs()
                    return json.dumps(jobs, indent=2)
                elif path.startswith("/jobs/"):
                    # Get specific job
                    job_id = path.split("/")[-1]
                    # Extract service from query parameters or job data
                    service = parsed_uri.fragment or "midjourney"  # Default service
                    job_status = await self.client.get_job_status(job_id, service)
                    return json.dumps(job_status, indent=2)
                elif path == "/account":
                    # Get account information
                    account_info = await self.client.get("/account")
                    return json.dumps(account_info, indent=2)
                elif path == "/models":
                    # List available models
                    models = {}
                    for service, config in get_service_config.__globals__['SERVICES_CONFIG'].items():
                        models[service] = config.get("supported_models", [])
                    return json.dumps(models, indent=2)
                elif path == "/history":
                    # Get generation history
                    history = await self.client.list_jobs(limit=50)
                    return json.dumps(history, indent=2)
                else:
                    raise UseAPIError(f"Unknown resource path: {path}")
                    
            except Exception as e:
                logger.exception(f"Error reading resource {uri}")
                return json.dumps({"error": str(e)}, indent=2)
    
    async def _handle_template_operation(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP template operations"""
        db = await get_database()
        
        if name == "mcp_template_store":
            template_data = arguments.get("template_data")
            if not template_data:
                raise UseAPIValidationError("template_data is required", "template_data")
            
            template_id = await db.store_template(template_data)
            return {
                "status": "success",
                "message": f"Template '{template_data.get('template_name')}' stored successfully",
                "template_id": template_id
            }
        
        elif name == "mcp_template_get":
            template_name = arguments.get("template_name")
            if not template_name:
                raise UseAPIValidationError("template_name is required", "template_name")
            
            template = await db.get_template(template_name)
            if not template:
                raise UseAPIError(f"Template '{template_name}' not found")
            
            return template
        
        elif name == "mcp_template_list":
            archetype = arguments.get("archetype")
            target_platform = arguments.get("target_platform")
            content_tier = arguments.get("content_tier")
            limit = arguments.get("limit", 50)
            
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
        
        elif name == "mcp_template_process":
            template_name = arguments.get("template_name")
            context_variables = arguments.get("context_variables", {})
            
            if not template_name:
                raise UseAPIValidationError("template_name is required", "template_name")
            
            # Get template from database
            template_data = await db.get_template(template_name)
            if not template_data:
                raise UseAPIError(f"Template '{template_name}' not found")
            
            # Increment usage count
            await db.increment_usage(template_name)
            
            # Process template into production plan
            production_plan = self.template_processor.process_template(template_data, context_variables)
            
            # Store execution record
            await db.store_execution(
                template_data['id'],
                production_plan.execution_id,
                context_variables,
                self.template_processor.serialize_production_plan(production_plan)
            )
            
            return self.template_processor.serialize_production_plan(production_plan)
        
        elif name == "mcp_template_analytics":
            template_name = arguments.get("template_name")
            if not template_name:
                raise UseAPIValidationError("template_name is required", "template_name")
            
            analytics = await db.get_template_analytics(template_name)
            if not analytics:
                raise UseAPIError(f"Template '{template_name}' not found")
            
            return analytics
        
        else:
            raise UseAPIError(f"Unknown template operation: {name}")
    
    def _register_tools(self):
        """Register all tool handlers"""
        # This would register the actual tool implementation classes
        # For now, they're handled in the call_tool handler
        pass
    
    async def run_stdio(self):
        """Run the server using stdio transport"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="useapi-mcp-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities={}
                    )
                )
            )
    
    async def start(self):
        """Start the MCP server"""
        logger.info("Starting UseAPI MCP Server...")
        try:
            await self.run_stdio()
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.exception("Server error")
            raise
        finally:
            if self.client:
                await self.client.close()
            await close_database()


async def main():
    """Main entry point"""
    config = UseAPIConfig()
    server = UseAPIServer(config)
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())