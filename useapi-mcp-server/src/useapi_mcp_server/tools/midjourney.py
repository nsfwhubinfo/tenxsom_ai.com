"""
Midjourney tools for image generation and manipulation
"""

import logging
from typing import Any, Dict

from .base import BaseTool
from ..exceptions import UseAPIValidationError

logger = logging.getLogger(__name__)


class MidjourneyTools(BaseTool):
    """Tools for Midjourney image generation"""
    
    def __init__(self, client):
        super().__init__(client, "midjourney")
    
    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Midjourney tool"""
        try:
            self.validate_arguments(arguments)
            
            if tool_name == "midjourney_imagine":
                return await self.imagine(arguments)
            elif tool_name == "midjourney_upscale":
                return await self.upscale(arguments)
            elif tool_name == "midjourney_variations":
                return await self.variations(arguments)
            elif tool_name == "midjourney_describe":
                return await self.describe(arguments)
            elif tool_name == "midjourney_blend":
                return await self.blend(arguments)
            else:
                raise UseAPIValidationError(f"Unknown Midjourney tool: {tool_name}")
                
        except Exception as e:
            logger.exception(f"Error executing {tool_name}")
            return self.format_error(e, tool_name)
    
    async def imagine(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Generate images using Midjourney imagine"""
        prompt = arguments["prompt"]
        model = arguments.get("model", "v6.1")
        aspect_ratio = arguments.get("aspect_ratio", "1:1")
        quality = arguments.get("quality", "1")
        stylize = arguments.get("stylize", 100)
        
        # Build the full prompt with parameters
        full_prompt = prompt
        
        # Add model parameter
        if model != "v6.1":  # v6.1 is default, don't add
            full_prompt += f" --v {model.replace('v', '').replace('niji', 'niji ')}"
        
        # Add aspect ratio
        if aspect_ratio != "1:1":
            full_prompt += f" --ar {aspect_ratio}"
        
        # Add quality
        if quality != "1":
            full_prompt += f" --q {quality}"
        
        # Add stylize
        if stylize != 100:
            full_prompt += f" --s {stylize}"
        
        data = {
            "prompt": full_prompt,
            "webhook_url": None,  # Could be configured
            "webhook_secret": None,
        }
        
        response = await self.make_request(
            f"{self.get_base_path()}/imagine",
            data,
            "imagine",
            wait_for_completion=True
        )
        
        return self.format_response(response, "imagine")
    
    async def upscale(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Upscale a Midjourney image"""
        image_id = arguments["image_id"]
        upscale_index = arguments["upscale_index"]
        
        if not 1 <= upscale_index <= 4:
            raise UseAPIValidationError(
                "Upscale index must be between 1 and 4",
                field="upscale_index"
            )
        
        data = {
            "message_id": image_id,
            "index": upscale_index,
            "webhook_url": None,
            "webhook_secret": None,
        }
        
        response = await self.make_request(
            f"{self.get_base_path()}/upscale",
            data,
            "upscale",
            wait_for_completion=True
        )
        
        return self.format_response(response, "upscale")
    
    async def variations(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create variations of a Midjourney image"""
        image_id = arguments["image_id"]
        variation_index = arguments["variation_index"]
        
        if not 1 <= variation_index <= 4:
            raise UseAPIValidationError(
                "Variation index must be between 1 and 4",
                field="variation_index"
            )
        
        data = {
            "message_id": image_id,
            "index": variation_index,
            "webhook_url": None,
            "webhook_secret": None,
        }
        
        response = await self.make_request(
            f"{self.get_base_path()}/variation",
            data,
            "variations",
            wait_for_completion=True
        )
        
        return self.format_response(response, "variations")
    
    async def describe(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Describe an image to generate prompts"""
        image_url = arguments["image_url"]
        
        data = {
            "image_url": image_url,
            "webhook_url": None,
            "webhook_secret": None,
        }
        
        response = await self.make_request(
            f"{self.get_base_path()}/describe",
            data,
            "describe",
            wait_for_completion=True
        )
        
        return self.format_response(response, "describe")
    
    async def blend(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Blend multiple images together"""
        image_urls = arguments["image_urls"]
        dimensions = arguments.get("dimensions", "square")
        
        if not isinstance(image_urls, list) or len(image_urls) < 2:
            raise UseAPIValidationError(
                "At least 2 image URLs required for blending",
                field="image_urls"
            )
        
        if len(image_urls) > 5:
            raise UseAPIValidationError(
                "Maximum 5 images can be blended",
                field="image_urls"
            )
        
        data = {
            "image_urls": image_urls,
            "dimensions": dimensions,
            "webhook_url": None,
            "webhook_secret": None,
        }
        
        response = await self.make_request(
            f"{self.get_base_path()}/blend",
            data,
            "blend",
            wait_for_completion=True
        )
        
        return self.format_response(response, "blend")