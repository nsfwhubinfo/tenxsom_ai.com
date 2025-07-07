"""
Base tool class for UseAPI.net service tools
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ..client import UseAPIClient
from ..config import get_service_config, validate_prompt, validate_aspect_ratio, validate_model
from ..exceptions import UseAPIValidationError

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """Base class for UseAPI.net service tools"""
    
    def __init__(self, client: UseAPIClient, service_name: str):
        self.client = client
        self.service_name = service_name
        self.config = get_service_config(service_name)
        
    def validate_arguments(self, arguments: Dict[str, Any]) -> None:
        """Validate tool arguments against service configuration"""
        
        # Validate prompt if present
        if "prompt" in arguments:
            prompt = arguments["prompt"]
            if not validate_prompt(self.service_name, prompt):
                max_length = self.config.get("max_prompt_length", 2000)
                raise UseAPIValidationError(
                    f"Prompt too long. Maximum length: {max_length}",
                    field="prompt",
                    service=self.service_name
                )
        
        # Validate aspect ratio if present
        if "aspect_ratio" in arguments:
            aspect_ratio = arguments["aspect_ratio"]
            if not validate_aspect_ratio(self.service_name, aspect_ratio):
                supported = self.config.get("supported_aspect_ratios", [])
                raise UseAPIValidationError(
                    f"Unsupported aspect ratio. Supported: {supported}",
                    field="aspect_ratio",
                    service=self.service_name
                )
        
        # Validate model if present
        if "model" in arguments:
            model = arguments["model"]
            if not validate_model(self.service_name, model):
                supported = self.config.get("supported_models", [])
                raise UseAPIValidationError(
                    f"Unsupported model. Supported: {supported}",
                    field="model",
                    service=self.service_name
                )
        
        # Validate duration if present
        if "duration" in arguments:
            duration = arguments["duration"]
            max_duration = self.config.get("max_video_duration") or self.config.get("max_duration", 300)
            if duration > max_duration:
                raise UseAPIValidationError(
                    f"Duration too long. Maximum: {max_duration} seconds",
                    field="duration",
                    service=self.service_name
                )
    
    async def make_request(
        self,
        endpoint: str,
        data: Dict[str, Any],
        operation: str,
        wait_for_completion: bool = True,
    ) -> Dict[str, Any]:
        """
        Make a request to the API and optionally wait for completion
        """
        # Make the initial request
        response = await self.client.post(
            endpoint,
            data=data,
            service=self.service_name,
            operation=operation,
        )
        
        # Check if this is an async job
        job_id = response.get("job_id") or response.get("id")
        
        if job_id and wait_for_completion:
            # Wait for job completion
            logger.info(f"Waiting for job {job_id} to complete...")
            final_response = await self.client.wait_for_job(
                job_id, 
                self.service_name
            )
            return final_response
        
        return response
    
    @abstractmethod
    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with given arguments"""
        pass
    
    def get_base_path(self) -> str:
        """Get the base API path for this service"""
        return self.config.get("base_path", f"/{self.service_name}")
    
    def format_response(self, response: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Format the API response for consistent output"""
        formatted = {
            "success": True,
            "service": self.service_name,
            "operation": operation,
            "data": response
        }
        
        # Extract common fields
        if "job_id" in response or "id" in response:
            formatted["job_id"] = response.get("job_id") or response.get("id")
        
        if "status" in response:
            formatted["status"] = response["status"]
        
        if "url" in response or "image_url" in response or "video_url" in response:
            formatted["media_url"] = (
                response.get("url") or 
                response.get("image_url") or 
                response.get("video_url")
            )
        
        if "urls" in response:
            formatted["media_urls"] = response["urls"]
        
        # Include metadata
        if "metadata" in response:
            formatted["metadata"] = response["metadata"]
        
        return formatted
    
    def format_error(self, error: Exception, operation: str) -> Dict[str, Any]:
        """Format an error response"""
        return {
            "success": False,
            "service": self.service_name,
            "operation": operation,
            "error": {
                "type": type(error).__name__,
                "message": str(error)
            }
        }