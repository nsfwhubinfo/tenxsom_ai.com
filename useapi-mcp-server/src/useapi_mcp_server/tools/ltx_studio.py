"""
LTX Studio tools for video and image generation
"""

import logging
from typing import Any, Dict

from .base import BaseTool
from ..exceptions import UseAPIValidationError

logger = logging.getLogger(__name__)


class LTXStudioTools(BaseTool):
    """Tools for LTX Studio video and image generation"""
    
    def __init__(self, client):
        super().__init__(client, "ltx_studio")
    
    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute LTX Studio tool"""
        try:
            self.validate_arguments(arguments)
            
            if tool_name == "ltx_studio_video_create":
                return await self.create_video(arguments)
            elif tool_name == "ltx_studio_image_create":
                return await self.create_image(arguments)
            elif tool_name == "ltx_studio_image_edit":
                return await self.edit_image(arguments)
            else:
                raise UseAPIValidationError(f"Unknown LTX Studio tool: {tool_name}")
                
        except Exception as e:
            logger.exception(f"Error executing {tool_name}")
            return self.format_error(e, tool_name)
    
    async def create_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Generate videos using LTX Studio models"""
        prompt = arguments["prompt"]
        model = arguments.get("model", "ltx-video")
        duration = arguments.get("duration", 5)
        aspect_ratio = arguments.get("aspect_ratio", "16:9")
        start_image_url = arguments.get("start_image_url")
        
        # Determine the correct endpoint based on model
        if model in ["veo2", "veo3"]:
            endpoint = f"{self.get_base_path()}/videos/veo-create"
        else:
            endpoint = f"{self.get_base_path()}/videos/ltx-create"
        
        data = {
            "prompt": prompt,
            "model": model,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
        }
        
        # Add start image if provided
        if start_image_url:
            # For UseAPI.net, we need to upload the image first and get an asset ID
            # This is a simplified version - in practice, you'd need to handle asset upload
            data["start_asset_id"] = start_image_url
        
        response = await self.make_request(
            endpoint,
            data,
            "create_video",
            wait_for_completion=True
        )
        
        return self.format_response(response, "create_video")
    
    async def create_image(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Generate images using LTX Studio FLUX model"""
        prompt = arguments["prompt"]
        width = arguments.get("width", 1024)
        height = arguments.get("height", 1024)
        guidance_scale = arguments.get("guidance_scale", 7.5)
        
        data = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "guidance_scale": guidance_scale,
            "prompt_optimization": True,
            "safe_mode": True,
        }
        
        response = await self.make_request(
            f"{self.get_base_path()}/images/flux-create",
            data,
            "create_image",
            wait_for_completion=True
        )
        
        return self.format_response(response, "create_image")
    
    async def edit_image(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Edit images using LTX Studio FLUX model"""
        image_url = arguments["image_url"]
        prompt = arguments["prompt"]
        strength = arguments.get("strength", 0.8)
        guidance_scale = arguments.get("guidance_scale", 7.5)
        
        data = {
            "image_url": image_url,
            "prompt": prompt,
            "strength": strength,
            "guidance_scale": guidance_scale,
            "safe_mode": True,
        }
        
        response = await self.make_request(
            f"{self.get_base_path()}/images/flux-edit",
            data,
            "edit_image",
            wait_for_completion=True
        )
        
        return self.format_response(response, "edit_image")
    
    async def upload_asset(self, file_data: bytes, filename: str, asset_type: str = "reference-image") -> str:
        """
        Upload an asset to LTX Studio and return the asset ID
        This is used for image-to-video generation
        """
        response = await self.client.upload_file(
            f"{self.get_base_path()}/assets/?type={asset_type}",
            file_data,
            filename,
            service=self.service_name,
            operation="upload_asset"
        )
        
        # Extract the asset ID from the response
        asset_id = response.get("asset", {}).get("fileId")
        if not asset_id:
            raise UseAPIValidationError("Failed to get asset ID from upload response")
        
        return asset_id