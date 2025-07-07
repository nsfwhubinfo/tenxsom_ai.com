"""
Veo Tool Functions for Google AI Ultra Subscription
Flow framework tool functions for Veo 3 video generation via AI Ultra subscription
"""

import os
import json
import time
import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional
from google.auth.transport.requests import Request
from google.oauth2 import service_account

# Import our flow framework
import sys
sys.path.append('..')
from flow_framework import func as flow_func

# Configure production logging
logger = logging.getLogger(__name__)

# Configuration - Production Mode Only
GOOGLE_AI_ULTRA_PROJECT_ID = os.getenv("GOOGLE_AI_ULTRA_PROJECT_ID", "gen-lang-client-0874689591")
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "/home/golde/.google-ai-ultra-credentials.json")


class VeoApiClient:
    """Client for Veo 3 API via Google AI Ultra subscription"""
    
    def __init__(self):
        self.credentials = None
        self.access_token = None
        self.project_id = GOOGLE_AI_ULTRA_PROJECT_ID
        
    async def initialize(self):
        """Initialize credentials and authentication"""
        try:
            self.credentials = service_account.Credentials.from_service_account_file(
                CREDENTIALS_PATH,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            
            # Refresh credentials to get access token
            self.credentials.refresh(Request())
            self.access_token = self.credentials.token
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Veo API client: {e}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, method: str, url: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to Veo API"""
        headers = self._get_headers()
        
        async with aiohttp.ClientSession() as session:
            try:
                if method.upper() == "POST":
                    async with session.post(url, headers=headers, json=data, 
                                          timeout=aiohttp.ClientTimeout(total=120)) as response:
                        response_data = await response.json()
                        return {
                            "status": response.status,
                            "data": response_data,
                            "success": response.status in [200, 202]
                        }
                else:
                    async with session.get(url, headers=headers,
                                         timeout=aiohttp.ClientTimeout(total=30)) as response:
                        response_data = await response.json()
                        return {
                            "status": response.status,
                            "data": response_data,
                            "success": response.status == 200
                        }
            except Exception as e:
                return {
                    "status": 500,
                    "data": {"error": str(e)},
                    "success": False
                }


# Global client instance
veo_client = VeoApiClient()


@flow_func
async def initialize_veo_client() -> bool:
    """Initialize the Veo API client with authentication"""
    return await veo_client.initialize()


@flow_func
async def trigger_veo3_generation(prompt: str, duration: int = 5, aspect_ratio: str = "16:9", 
                                 include_audio: bool = True) -> str:
    """
    Trigger Veo 3 video generation via AI Ultra subscription
    
    Args:
        prompt: Text description for video generation
        duration: Video duration in seconds (max 20 for Veo 3)
        aspect_ratio: Video aspect ratio (16:9, 9:16, 1:1)
        include_audio: Whether to include audio generation
    
    Returns:
        Job ID for polling or video URL if completed immediately
    """
    
    # Ensure client is initialized
    if not veo_client.access_token:
        await initialize_veo_client()
    
    # Veo 3 endpoint URL
    url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{veo_client.project_id}/locations/us-central1/publishers/google/models/veo-3.0-generate-preview:predictLongRunning"
    
    # Prepare payload for Veo 3
    payload = {
        "instances": [{
            "prompt": prompt,
            "parameters": {
                "duration": min(duration, 20),  # Veo 3 max duration
                "aspectRatio": aspect_ratio,
                "audioGeneration": "enabled" if include_audio else "disabled",
                "quality": "high",
                "seed": None  # Random seed for variety
            }
        }]
    }
    
    # Make request
    result = await veo_client._make_request("POST", url, payload)
    
    if result["success"]:
        # Extract operation name for polling
        operation_data = result["data"]
        if "name" in operation_data:
            return operation_data["name"]  # This is the job ID for long-running operations
        elif "predictions" in operation_data:
            # Immediate response with video URL
            predictions = operation_data["predictions"]
            if predictions and "videoUrl" in predictions[0]:
                return predictions[0]["videoUrl"]
    
    # Return error information
    error_msg = result["data"].get("error", {}).get("message", "Unknown error")
    raise Exception(f"Veo 3 generation failed: {error_msg}")


@flow_func 
async def poll_veo3_operation(operation_name: str, max_wait_minutes: int = 10) -> str:
    """
    Poll a long-running Veo 3 operation until completion
    
    Args:
        operation_name: The operation name/job ID from trigger_veo3_generation
        max_wait_minutes: Maximum time to wait for completion
    
    Returns:
        Video download URL when ready
    """
    
    # Construct operation polling URL
    url = f"https://us-central1-aiplatform.googleapis.com/v1/{operation_name}"
    
    max_attempts = max_wait_minutes * 6  # Check every 10 seconds
    
    for attempt in range(max_attempts):
        result = await veo_client._make_request("GET", url)
        
        if result["success"]:
            operation = result["data"]
            
            # Check if operation is complete
            if operation.get("done", False):
                # Check for errors
                if "error" in operation:
                    error_msg = operation["error"].get("message", "Unknown error")
                    raise Exception(f"Veo 3 operation failed: {error_msg}")
                
                # Extract video URL from response
                response = operation.get("response", {})
                predictions = response.get("predictions", [])
                
                if predictions and "videoUrl" in predictions[0]:
                    return predictions[0]["videoUrl"]
                elif predictions and "downloadUrl" in predictions[0]:
                    return predictions[0]["downloadUrl"]
                else:
                    raise Exception("No video URL in completed operation")
            
            # Operation still running, wait and retry
            await asyncio.sleep(10)
        else:
            # API error, wait and retry
            await asyncio.sleep(10)
    
    raise Exception(f"Veo 3 operation timed out after {max_wait_minutes} minutes")


@flow_func
async def generate_veo3_video_complete(prompt: str, duration: int = 5, 
                                     aspect_ratio: str = "16:9", 
                                     include_audio: bool = True,
                                     max_wait_minutes: int = 10) -> str:
    """
    Complete Veo 3 video generation workflow - trigger and wait for completion
    
    Args:
        prompt: Text description for video generation
        duration: Video duration in seconds
        aspect_ratio: Video aspect ratio
        include_audio: Whether to include audio generation
        max_wait_minutes: Maximum time to wait for completion
    
    Returns:
        Video download URL
    """
    
    logger.info(f"Starting Veo 3 generation: {prompt[:50]}...")
    
    # Trigger generation
    operation_or_url = await trigger_veo3_generation(
        prompt=prompt,
        duration=duration,
        aspect_ratio=aspect_ratio,
        include_audio=include_audio
    )
    
    # Check if we got immediate URL or need to poll
    if operation_or_url.startswith("http"):
        logger.info("Video generated immediately!")
        return operation_or_url
    else:
        logger.info(f"Polling operation: {operation_or_url[:50]}...")
        video_url = await poll_veo3_operation(operation_or_url, max_wait_minutes)
        logger.info("Video generation completed!")
        return video_url


@flow_func
async def check_veo3_connection() -> Dict[str, Any]:
    """Check connection to Veo 3 API and return service status"""
    
    try:
        # Initialize client
        init_success = await initialize_veo_client()
        if not init_success:
            return {
                "status": "failed",
                "error": "Failed to initialize credentials",
                "veo3_available": False
            }
        
        # Test with a simple request (just check if model is accessible)
        url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{veo_client.project_id}/locations/us-central1/publishers/google/models/veo-3.0-generate-preview"
        
        result = await veo_client._make_request("GET", url)
        
        return {
            "status": "success" if result["success"] else "failed",
            "api_status": result["status"],
            "veo3_available": result["success"],
            "project_id": veo_client.project_id,
            "credentials_valid": bool(veo_client.access_token)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "veo3_available": False
        }


# Backup/Fallback function for Vertex AI standard models
@flow_func
async def fallback_to_imagen(prompt: str) -> str:
    """
    Fallback to Imagen for image generation if Veo 3 is unavailable
    """
    
    url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{veo_client.project_id}/locations/us-central1/publishers/google/models/imagegeneration@002:predict"
    
    payload = {
        "instances": [{
            "prompt": prompt
        }],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "16:9"
        }
    }
    
    result = await veo_client._make_request("POST", url, payload)
    
    if result["success"]:
        predictions = result["data"].get("predictions", [])
        if predictions:
            # Return base64 image data or URL
            return predictions[0].get("bytesBase64Encoded", "")
    
    raise Exception(f"Imagen fallback failed: {result['data']}")


# Export main functions for import
__all__ = [
    'initialize_veo_client',
    'trigger_veo3_generation', 
    'poll_veo3_operation',
    'generate_veo3_video_complete',
    'test_veo3_connection',
    'fallback_to_imagen'
]