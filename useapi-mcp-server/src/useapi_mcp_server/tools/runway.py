"""
Runway tools for video generation and manipulation
"""

import logging
from typing import Any, Dict

from .base import BaseTool
from ..exceptions import UseAPIValidationError

logger = logging.getLogger(__name__)


class RunwayTools(BaseTool):
    """Tools for Runway AI video generation"""
    
    def __init__(self, client):
        super().__init__(client, "runway")
    
    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Runway tool"""
        try:
            self.validate_arguments(arguments)
            
            if tool_name == "runway_image_to_video":
                return await self.image_to_video(arguments)
            elif tool_name == "runway_video_to_video":
                return await self.video_to_video(arguments)
            elif tool_name == "runway_lipsync":
                return await self.lipsync(arguments)
            elif tool_name == "runway_extend_video":
                return await self.extend_video(arguments)
            else:
                raise UseAPIValidationError(f"Unknown Runway tool: {tool_name}")
                
        except Exception as e:
            logger.exception(f"Error executing {tool_name}")
            return self.format_error(e, tool_name)
    
    async def image_to_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Convert image to video using Runway"""
        image_url = arguments["image_url"]
        prompt = arguments.get("prompt", "")
        model = arguments.get("model", "gen3alpha")
        duration = arguments.get("duration", 5)
        
        data = {
            "image_url": image_url,
            "prompt": prompt,
            "model": model,
            "duration": duration,
        }
        
        response = await self.make_request(
            f"{self.get_base_path()}/image-to-video",
            data,
            "image_to_video",
            wait_for_completion=True
        )
        
        return self.format_response(response, "image_to_video")
    
    async def video_to_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Transform video using Runway"""
        video_url = arguments["video_url"]
        prompt = arguments["prompt"]
        model = arguments.get("model", "gen3alpha")
        
        data = {
            "video_url": video_url,
            "prompt": prompt,
            "model": model,
        }
        
        response = await self.make_request(
            f"{self.get_base_path()}/video-to-video",
            data,
            "video_to_video",
            wait_for_completion=True
        )
        
        return self.format_response(response, "video_to_video")
    
    async def lipsync(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Add lip sync to video using Runway"""
        video_url = arguments["video_url"]
        audio_url = arguments["audio_url"]
        
        data = {
            "video_url": video_url,
            "audio_url": audio_url,
        }
        
        response = await self.make_request(
            f"{self.get_base_path()}/lipsync/create",
            data,
            "lipsync",
            wait_for_completion=True
        )
        
        return self.format_response(response, "lipsync")
    
    async def extend_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Extend video duration using Runway"""
        video_url = arguments["video_url"]
        prompt = arguments.get("prompt", "")
        model = arguments.get("model", "gen3alpha")
        
        data = {
            "video_url": video_url,
            "prompt": prompt,
            "model": model,
        }
        
        response = await self.make_request(
            f"{self.get_base_path()}/extend",
            data,
            "extend_video",
            wait_for_completion=True
        )
        
        return self.format_response(response, "extend_video")