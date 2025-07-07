"""
Mureka music generation tools
"""

import logging
from typing import Any, Dict

from .base import BaseTool
from ..exceptions import UseAPIValidationError

logger = logging.getLogger(__name__)


class MurekaTools(BaseTool):
    """Tools for Mureka AI music generation"""
    
    def __init__(self, client):
        super().__init__(client, "mureka")
    
    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Mureka tool"""
        try:
            self.validate_arguments(arguments)
            
            if tool_name == "mureka_music_create":
                return await self.create_music(arguments)
            elif tool_name == "mureka_music_extend":
                return await self.extend_music(arguments)
            else:
                raise UseAPIValidationError(f"Unknown Mureka tool: {tool_name}")
                
        except Exception as e:
            logger.exception(f"Error executing {tool_name}")
            return self.format_error(e, tool_name)
    
    async def create_music(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Generate music using Mureka AI"""
        prompt = arguments["prompt"]
        style = arguments.get("style", "")
        duration = arguments.get("duration", 30)
        instrumental = arguments.get("instrumental", False)
        
        data = {
            "prompt": prompt,
            "style": style,
            "duration": duration,
            "instrumental": instrumental,
        }
        
        response = await self.make_request(
            f"{self.get_base_path()}/music/create",
            data,
            "create_music",
            wait_for_completion=True
        )
        
        return self.format_response(response, "create_music")
    
    async def extend_music(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Extend existing music"""
        audio_url = arguments["audio_url"]
        duration = arguments.get("duration", 30)
        
        data = {
            "audio_url": audio_url,
            "duration": duration,
        }
        
        response = await self.make_request(
            f"{self.get_base_path()}/music/extend",
            data,
            "extend_music",
            wait_for_completion=True
        )
        
        return self.format_response(response, "extend_music")