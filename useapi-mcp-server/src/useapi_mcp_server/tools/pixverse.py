"""PixVerse tools for video generation via UseAPI.net"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin

from .base import BaseTool
from ..exceptions import UseAPIError, UseAPITimeoutError

logger = logging.getLogger(__name__)


class PixVerseTools(BaseTool):
    """Production-ready PixVerse video generation tools"""
    
    def __init__(self, client):
        super().__init__(client, "pixverse")
        self.service_name = "pixverse"
        self.base_path = "/v2/pixverse"
        
        # Production configuration (validated against UseAPI.net API)
        self.config = {
            "max_prompt_length": 2000,
            "supported_models": ["v4", "v4.5"],  # Fixed: v4 not v4.0
            "supported_durations": [5, 8],  # Fixed: Only 5s and 8s supported
            "max_video_duration": 8,
            "min_video_duration": 5,
            "supported_aspect_ratios": ["16:9", "9:16", "1:1"],
            "max_concurrent_jobs": 4,
            "polling_interval": 30,  # seconds
            "max_wait_time": 1800,  # 30 minutes
        }
    
    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute PixVerse tool with production error handling"""
        try:
            if tool_name == "create_video":
                return await self._create_video(**arguments)
            elif tool_name == "get_video_status":
                return await self._get_video_status(**arguments)
            elif tool_name == "list_videos":
                return await self._list_videos(**arguments)
            elif tool_name == "wait_for_completion":
                return await self._wait_for_completion(**arguments)
            else:
                raise UseAPIError(f"Unknown PixVerse tool: {tool_name}")
                
        except Exception as e:
            logger.error(f"PixVerse tool '{tool_name}' failed: {e}")
            return {
                "success": False,
                "service": self.service_name,
                "tool": tool_name,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def _create_video(self, prompt: str, model: str = "v4", 
                           aspect_ratio: str = "16:9", duration: int = 5,
                           negative_prompt: Optional[str] = None,
                           start_image: Optional[str] = None,
                           end_image: Optional[str] = None,
                           style: Optional[str] = None,
                           **kwargs) -> Dict[str, Any]:
        """Create video using PixVerse API"""
        
        # Validate inputs
        if len(prompt) > self.config["max_prompt_length"]:
            raise UseAPIError(f"Prompt too long: {len(prompt)} > {self.config['max_prompt_length']}")
        
        if model not in self.config["supported_models"]:
            raise UseAPIError(f"Unsupported model: {model}. Supported: {self.config['supported_models']}")
        
        if aspect_ratio not in self.config["supported_aspect_ratios"]:
            raise UseAPIError(f"Unsupported aspect ratio: {aspect_ratio}. Supported: {self.config['supported_aspect_ratios']}")
        
        if duration not in self.config["supported_durations"]:
            raise UseAPIError(f"Unsupported duration: {duration}. Supported: {self.config['supported_durations']}")
        
        # Build request payload
        payload = {
            "prompt": prompt,
            "model": model,
            "aspect_ratio": aspect_ratio,
            "duration": duration,
        }
        
        # Add optional parameters
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        if start_image:
            payload["start_image"] = start_image
        if end_image:
            payload["end_image"] = end_image
        if style:
            payload["style"] = style
        
        logger.info(f"Creating PixVerse video with model {model}, aspect ratio {aspect_ratio}, duration {duration}s")
        
        # Make API request
        endpoint = f"{self.base_path}/videos/create-v4"
        response = await self.client.post(endpoint, json=payload)
        
        if response.get("success"):
            video_data = response.get("data", {})
            video_id = video_data.get("video_id")
            
            logger.info(f"PixVerse video creation initiated: {video_id}")
            
            return {
                "success": True,
                "service": self.service_name,
                "tool": "create_video",
                "video_id": video_id,
                "status": video_data.get("status", "pending"),
                "model": model,
                "aspect_ratio": aspect_ratio,
                "duration": duration,
                "created_at": video_data.get("created_at"),
                "estimated_completion": video_data.get("estimated_completion"),
                "data": video_data
            }
        else:
            error_msg = response.get("error", "Unknown error")
            raise UseAPIError(f"PixVerse video creation failed: {error_msg}")
    
    async def _get_video_status(self, video_id: str) -> Dict[str, Any]:
        """Get video generation status"""
        if not video_id:
            raise UseAPIError("video_id is required")
        
        logger.info(f"Checking PixVerse video status: {video_id}")
        
        endpoint = f"{self.base_path}/videos/{video_id}"
        response = await self.client.get(endpoint)
        
        if response.get("success"):
            video_data = response.get("data", {})
            status = video_data.get("status")
            
            # Status mapping: 0=pending, 1=processing, 2=completed, 3=failed
            status_map = {
                0: "pending",
                1: "processing", 
                2: "completed",
                3: "failed"
            }
            
            status_text = status_map.get(status, "unknown")
            
            result = {
                "success": True,
                "service": self.service_name,
                "tool": "get_video_status",
                "video_id": video_id,
                "status": status_text,
                "status_code": status,
                "progress": video_data.get("progress", 0),
                "created_at": video_data.get("created_at"),
                "updated_at": video_data.get("updated_at"),
                "data": video_data
            }
            
            # Add video URL if completed
            if status == 2 and video_data.get("video_url"):
                result["video_url"] = video_data["video_url"]
                result["download_url"] = video_data.get("download_url")
            
            # Add error details if failed
            if status == 3:
                result["error"] = video_data.get("error", "Generation failed")
            
            logger.info(f"PixVerse video {video_id} status: {status_text}")
            return result
        else:
            error_msg = response.get("error", "Unknown error")
            raise UseAPIError(f"Failed to get PixVerse video status: {error_msg}")
    
    async def _list_videos(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List recent videos"""
        logger.info(f"Listing PixVerse videos (limit: {limit}, offset: {offset})")
        
        endpoint = f"{self.base_path}/videos"
        params = {"limit": limit, "offset": offset}
        
        response = await self.client.get(endpoint, params=params)
        
        if response.get("success"):
            videos = response.get("data", [])
            
            # Process video data
            processed_videos = []
            for video in videos:
                processed_video = {
                    "video_id": video.get("video_id"),
                    "status": video.get("video_status"),
                    "created_at": video.get("created_at"),
                    "account_id": video.get("account_id"),
                }
                
                # Add video URL if available
                if video.get("video_url"):
                    processed_video["video_url"] = video["video_url"]
                
                processed_videos.append(processed_video)
            
            return {
                "success": True,
                "service": self.service_name,
                "tool": "list_videos",
                "count": len(processed_videos),
                "videos": processed_videos,
                "limit": limit,
                "offset": offset
            }
        else:
            error_msg = response.get("error", "Unknown error")
            raise UseAPIError(f"Failed to list PixVerse videos: {error_msg}")
    
    async def _wait_for_completion(self, video_id: str, timeout: int = 1800) -> Dict[str, Any]:
        """Wait for video generation to complete with polling"""
        if not video_id:
            raise UseAPIError("video_id is required")
        
        logger.info(f"Waiting for PixVerse video completion: {video_id} (timeout: {timeout}s)")
        
        start_time = asyncio.get_event_loop().time()
        polling_interval = self.config["polling_interval"]
        
        while True:
            # Check if timeout exceeded
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                raise UseAPITimeoutError(f"Video generation timeout after {timeout}s")
            
            # Get current status
            status_response = await self._get_video_status(video_id)
            
            if not status_response.get("success"):
                raise UseAPIError(f"Failed to check video status: {status_response.get('error')}")
            
            status = status_response.get("status")
            
            if status == "completed":
                logger.info(f"PixVerse video {video_id} completed successfully")
                return status_response
            elif status == "failed":
                error_msg = status_response.get("error", "Generation failed")
                raise UseAPIError(f"Video generation failed: {error_msg}")
            elif status in ["pending", "processing"]:
                progress = status_response.get("progress", 0)
                logger.info(f"PixVerse video {video_id} {status}: {progress}%")
                
                # Wait before next poll
                await asyncio.sleep(polling_interval)
                continue
            else:
                raise UseAPIError(f"Unknown video status: {status}")
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions for MCP server registration"""
        return [
            {
                "name": "pixverse_create_video",
                "description": "Create video using PixVerse AI with customizable parameters",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Video generation prompt",
                            "maxLength": self.config["max_prompt_length"]
                        },
                        "model": {
                            "type": "string",
                            "description": "PixVerse model version",
                            "enum": self.config["supported_models"],
                            "default": "v4"
                        },
                        "aspect_ratio": {
                            "type": "string",
                            "description": "Video aspect ratio",
                            "enum": self.config["supported_aspect_ratios"],
                            "default": "16:9"
                        },
                        "duration": {
                            "type": "integer",
                            "description": "Video duration in seconds",
                            "enum": self.config["supported_durations"],
                            "default": 5
                        },
                        "negative_prompt": {
                            "type": "string",
                            "description": "Negative prompt to avoid certain elements"
                        },
                        "start_image": {
                            "type": "string",
                            "description": "URL of start image for video"
                        },
                        "end_image": {
                            "type": "string",
                            "description": "URL of end image for video"
                        },
                        "style": {
                            "type": "string",
                            "description": "Video style or theme"
                        }
                    },
                    "required": ["prompt"]
                }
            },
            {
                "name": "pixverse_get_video_status",
                "description": "Get status of PixVerse video generation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "video_id": {
                            "type": "string",
                            "description": "Video ID to check status for"
                        }
                    },
                    "required": ["video_id"]
                }
            },
            {
                "name": "pixverse_list_videos",
                "description": "List recent PixVerse videos",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of videos to return",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 10
                        },
                        "offset": {
                            "type": "integer",
                            "description": "Number of videos to skip",
                            "minimum": 0,
                            "default": 0
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "pixverse_wait_for_completion",
                "description": "Wait for PixVerse video generation to complete",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "video_id": {
                            "type": "string",
                            "description": "Video ID to wait for completion"
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Maximum wait time in seconds",
                            "minimum": 60,
                            "maximum": 3600,
                            "default": 1800
                        }
                    },
                    "required": ["video_id"]
                }
            }
        ]