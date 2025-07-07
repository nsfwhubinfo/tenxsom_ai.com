"""
Google AI Ultra API Wrapper
Integrates Veo 3 (Fast/Quality) with Tenxsom AI video generation pipeline
"""

import os
import json
import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

import aiohttp
from aiohttp import ClientSession

logger = logging.getLogger(__name__)


class Veo3Model(Enum):
    """Veo 3 model variants"""
    FAST = "veo3_fast"      # 20 credits
    QUALITY = "veo3_quality"  # 100 credits


class AudioGeneration(Enum):
    """Audio generation options"""
    NONE = "none"
    AMBIENT = "ambient"
    MUSIC = "music"
    NARRATION = "narration"


@dataclass
class VideoRequest:
    """Video generation request"""
    prompt: str
    model: Veo3Model
    duration: int = 5  # seconds
    aspect_ratio: str = "16:9"
    audio: AudioGeneration = AudioGeneration.NONE
    quality_preset: str = "standard"
    

@dataclass
class VideoResponse:
    """Video generation response"""
    video_id: str
    download_url: Optional[str]
    status: str
    credits_used: int
    estimated_cost: float
    metadata: Dict[str, Any]


class GoogleAIUltraWrapper:
    """
    Google AI Ultra API wrapper for Veo 3 video generation
    Provides seamless integration with existing Tenxsom AI pipeline
    """
    
    def __init__(self, credentials_path: str = None):
        """
        Initialize Google AI Ultra wrapper
        
        Args:
            credentials_path: Path to Google AI Ultra credentials file
        """
        self.credentials_path = credentials_path or os.getenv('GOOGLE_AI_ULTRA_CREDENTIALS')
        self.session: Optional[ClientSession] = None
        self.api_key: Optional[str] = None
        self.project_id: Optional[str] = None
        
        # Credit tracking
        self.credits_used_today = 0
        self.credits_limit = 12500  # Monthly limit
        
        # Cost mapping
        self.credit_costs = {
            Veo3Model.FAST: 20,
            Veo3Model.QUALITY: 100
        }
        
    async def initialize(self):
        """Initialize the wrapper with credentials"""
        if not self.credentials_path:
            raise ValueError("Google AI Ultra credentials path not provided")
            
        # Load credentials
        try:
            with open(self.credentials_path, 'r') as f:
                creds = json.load(f)
                self.api_key = creds.get('api_key')
                self.project_id = creds.get('project_id')
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            raise
            
        # Initialize HTTP session
        self.session = aiohttp.ClientSession()
        logger.info("Google AI Ultra wrapper initialized")
        
    async def close(self):
        """Close the wrapper and cleanup resources"""
        if self.session:
            await self.session.close()
            
    async def generate_video(self, request: VideoRequest) -> VideoResponse:
        """
        Generate video using Veo 3
        
        Args:
            request: Video generation request
            
        Returns:
            VideoResponse with generation results
        """
        if not self.session:
            await self.initialize()
            
        # Check credit availability
        credits_needed = self.credit_costs[request.model]
        if self.credits_used_today + credits_needed > self.credits_limit:
            raise Exception(f"Insufficient credits: need {credits_needed}, have {self.credits_limit - self.credits_used_today}")
            
        # Prepare API request
        url = f"https://aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/us-central1/publishers/google/models/{request.model.value}:generateContent"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": request.prompt
                }]
            }],
            "generationConfig": {
                "duration": request.duration,
                "aspectRatio": request.aspect_ratio,
                "audioGeneration": request.audio.value,
                "qualityPreset": request.quality_preset
            }
        }
        
        try:
            async with self.session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract video information
                    video_id = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('videoId')
                    download_url = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('videoUrl')
                    
                    # Update credit usage
                    self.credits_used_today += credits_needed
                    
                    return VideoResponse(
                        video_id=video_id,
                        download_url=download_url,
                        status="completed",
                        credits_used=credits_needed,
                        estimated_cost=0.0,  # Included in plan
                        metadata={
                            "model": request.model.value,
                            "duration": request.duration,
                            "aspect_ratio": request.aspect_ratio,
                            "audio": request.audio.value
                        }
                    )
                else:
                    error_data = await response.text()
                    logger.error(f"Video generation failed: {response.status} - {error_data}")
                    raise Exception(f"API request failed: {response.status}")
                    
        except Exception as e:
            logger.error(f"Video generation error: {e}")
            raise
            
    async def check_credits(self) -> Dict[str, int]:
        """
        Check current credit usage and limits
        
        Returns:
            Credit usage information
        """
        return {
            "credits_used_today": self.credits_used_today,
            "credits_remaining": self.credits_limit - self.credits_used_today,
            "credits_limit": self.credits_limit,
            "fast_videos_remaining": (self.credits_limit - self.credits_used_today) // 20,
            "quality_videos_remaining": (self.credits_limit - self.credits_used_today) // 100
        }
        
    async def get_generation_cost(self, model: Veo3Model, quantity: int = 1) -> Dict[str, Any]:
        """
        Calculate generation cost for given model and quantity
        
        Args:
            model: Veo 3 model variant
            quantity: Number of videos to generate
            
        Returns:
            Cost breakdown
        """
        credits_per_video = self.credit_costs[model]
        total_credits = credits_per_video * quantity
        
        return {
            "model": model.value,
            "quantity": quantity,
            "credits_per_video": credits_per_video,
            "total_credits": total_credits,
            "total_cost_usd": 0.0,  # Included in plan
            "affordable": total_credits <= (self.credits_limit - self.credits_used_today)
        }
        

class TenxsomGoogleUltraIntegration:
    """
    Integration layer between Google AI Ultra and Tenxsom AI content pipeline
    """
    
    def __init__(self, google_wrapper: GoogleAIUltraWrapper):
        self.google_wrapper = google_wrapper
        
    async def generate_premium_content(self, 
                                     prompt: str,
                                     platform: str = "youtube",
                                     quality_tier: str = "premium") -> VideoResponse:
        """
        Generate premium content using appropriate Veo 3 model
        
        Args:
            prompt: Video generation prompt
            platform: Target platform (youtube, instagram, etc.)
            quality_tier: Quality level (premium, standard)
            
        Returns:
            Generated video response
        """
        # Select model based on quality tier
        if quality_tier == "premium":
            model = Veo3Model.QUALITY
        else:
            model = Veo3Model.FAST
            
        # Platform-specific configurations
        if platform == "youtube":
            aspect_ratio = "16:9"
            duration = 30
            audio = AudioGeneration.AMBIENT
        elif platform == "instagram":
            aspect_ratio = "9:16"
            duration = 15
            audio = AudioGeneration.MUSIC
        elif platform == "tiktok":
            aspect_ratio = "9:16"
            duration = 15
            audio = AudioGeneration.MUSIC
        else:
            aspect_ratio = "16:9"
            duration = 15
            audio = AudioGeneration.NONE
            
        request = VideoRequest(
            prompt=prompt,
            model=model,
            duration=duration,
            aspect_ratio=aspect_ratio,
            audio=audio,
            quality_preset="high" if quality_tier == "premium" else "standard"
        )
        
        return await self.google_wrapper.generate_video(request)
        
    async def get_daily_capacity(self) -> Dict[str, int]:
        """
        Calculate remaining daily capacity for each model
        
        Returns:
            Capacity information
        """
        credits = await self.google_wrapper.check_credits()
        remaining = credits["credits_remaining"]
        
        return {
            "veo3_quality_capacity": remaining // 100,
            "veo3_fast_capacity": remaining // 20,
            "total_credits_remaining": remaining
        }


# Example usage
if __name__ == "__main__":
    async def test_google_ultra():
        wrapper = GoogleAIUltraWrapper("/home/golde/.google-ai-ultra-credentials.json")
        integration = TenxsomGoogleUltraIntegration(wrapper)
        
        # Generate premium YouTube content
        response = await integration.generate_premium_content(
            prompt="A stunning sunrise over mountains with golden light",
            platform="youtube",
            quality_tier="premium"
        )
        
        print(f"Generated video: {response.video_id}")
        print(f"Credits used: {response.credits_used}")
        
        # Check capacity
        capacity = await integration.get_daily_capacity()
        print(f"Remaining capacity: {capacity}")
        
        await wrapper.close()
        
    asyncio.run(test_google_ultra())