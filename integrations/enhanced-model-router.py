"""
Enhanced Model Router for Tenxsom AI
Intelligently routes video generation requests across three tiers:
1. Google AI Ultra (Veo 3 Quality/Fast)
2. UseAPI.net Premium (Veo2)
3. UseAPI.net Volume (LTX Turbo)
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

from google_ai_ultra_wrapper import GoogleAIUltraWrapper, TenxsomGoogleUltraIntegration, Veo3Model
from load_balancer.account_pool_manager import AccountPoolManager, ModelType

logger = logging.getLogger(__name__)


class QualityTier(Enum):
    """Content quality tiers"""
    PREMIUM = "premium"      # Veo 3 Quality (100 credits)
    STANDARD = "standard"    # Veo 3 Fast (20 credits) or Veo2 (700 credits)
    VOLUME = "volume"        # LTX Turbo (0 credits)


class Platform(Enum):
    """Target platforms"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    X = "x"
    GENERAL = "general"


@dataclass
class GenerationRequest:
    """Video generation request"""
    prompt: str
    platform: Platform
    quality_tier: QualityTier
    duration: int = 15
    aspect_ratio: str = "16:9"
    priority: int = 1  # 1=highest, 5=lowest
    

@dataclass
class GenerationResponse:
    """Video generation response"""
    video_id: str
    download_url: Optional[str]
    model_used: str
    service_used: str  # google_ultra, useapi_premium, useapi_volume
    credits_used: int
    cost_usd: float
    generation_time: float
    metadata: Dict[str, Any]


class ModelSelectionStrategy:
    """Strategy for selecting the best model for a request"""
    
    @staticmethod
    def select_for_youtube_monetization(request: GenerationRequest) -> tuple[str, str]:
        """Select model optimized for YouTube monetization"""
        if request.quality_tier == QualityTier.PREMIUM:
            return "google_ultra", "veo3_quality"
        elif request.quality_tier == QualityTier.STANDARD:
            return "google_ultra", "veo3_fast"
        else:
            return "useapi_volume", "ltx_turbo"
    
    @staticmethod
    def select_cost_optimized(request: GenerationRequest) -> tuple[str, str]:
        """Select model optimized for cost"""
        if request.quality_tier == QualityTier.VOLUME:
            return "useapi_volume", "ltx_turbo"
        elif request.quality_tier == QualityTier.STANDARD:
            return "google_ultra", "veo3_fast"
        else:
            return "google_ultra", "veo3_quality"
    
    @staticmethod
    def select_balanced(request: GenerationRequest) -> tuple[str, str]:
        """Select model with balanced quality/cost"""
        if request.platform == Platform.YOUTUBE and request.quality_tier == QualityTier.PREMIUM:
            return "google_ultra", "veo3_quality"
        elif request.quality_tier == QualityTier.VOLUME:
            return "useapi_volume", "ltx_turbo"
        else:
            return "google_ultra", "veo3_fast"


class EnhancedModelRouter:
    """
    Enhanced model router that intelligently selects between:
    - Google AI Ultra (Veo 3 Quality/Fast)
    - UseAPI.net Premium accounts (Veo2)
    - UseAPI.net Volume accounts (LTX Turbo)
    """
    
    def __init__(self, 
                 google_ultra_credentials: str,
                 useapi_accounts_config: List[Dict],
                 strategy: str = "balanced"):
        """
        Initialize the enhanced model router
        
        Args:
            google_ultra_credentials: Path to Google AI Ultra credentials
            useapi_accounts_config: UseAPI.net account configurations
            strategy: Selection strategy (youtube_monetization, cost_optimized, balanced)
        """
        self.strategy = strategy
        
        # Initialize Google AI Ultra
        self.google_wrapper = GoogleAIUltraWrapper(google_ultra_credentials)
        self.google_integration = TenxsomGoogleUltraIntegration(self.google_wrapper)
        
        # Initialize UseAPI.net account pool
        self.useapi_pool = AccountPoolManager(useapi_accounts_config)
        
        # Strategy selector
        self.strategy_map = {
            "youtube_monetization": ModelSelectionStrategy.select_for_youtube_monetization,
            "cost_optimized": ModelSelectionStrategy.select_cost_optimized,
            "balanced": ModelSelectionStrategy.select_balanced
        }
        
        # Usage tracking
        self.generation_stats = {
            "google_ultra_quality": 0,
            "google_ultra_fast": 0,
            "useapi_pixverse": 0,
            "useapi_ltx_turbo": 0,
            "total_cost": 0.0,
            "total_credits": 0
        }
        
    async def start(self):
        """Start the model router"""
        await self.google_wrapper.initialize()
        await self.useapi_pool.start()
        logger.info("Enhanced Model Router started")
        
    async def stop(self):
        """Stop the model router"""
        await self.google_wrapper.close()
        await self.useapi_pool.stop()
        
    async def generate_video(self, request: GenerationRequest) -> GenerationResponse:
        """
        Generate video using the optimal model
        
        Args:
            request: Video generation request
            
        Returns:
            Generation response with video details
        """
        import time
        start_time = time.time()
        
        # Select service and model
        strategy_func = self.strategy_map[self.strategy]
        service, model = strategy_func(request)
        
        try:
            if service == "google_ultra":
                response = await self._generate_with_google_ultra(request, model)
            elif service == "useapi_premium":
                response = await self._generate_with_useapi_premium(request)
            elif service == "useapi_volume":
                response = await self._generate_with_useapi_volume(request)
            else:
                raise ValueError(f"Unknown service: {service}")
                
            # Update stats
            generation_time = time.time() - start_time
            response.generation_time = generation_time
            
            self._update_stats(service, model, response.credits_used, response.cost_usd)
            
            logger.info(f"Generated video using {service}:{model} in {generation_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Generation failed with {service}:{model} - {e}")
            # Attempt fallback
            return await self._fallback_generation(request, start_time)
            
    async def _generate_with_google_ultra(self, request: GenerationRequest, model: str) -> GenerationResponse:
        """Generate video using Google AI Ultra"""
        quality_tier = "premium" if model == "veo3_quality" else "standard"
        
        ultra_response = await self.google_integration.generate_premium_content(
            prompt=request.prompt,
            platform=request.platform.value,
            quality_tier=quality_tier
        )
        
        return GenerationResponse(
            video_id=ultra_response.video_id,
            download_url=ultra_response.download_url,
            model_used=model,
            service_used="google_ultra",
            credits_used=ultra_response.credits_used,
            cost_usd=0.0,  # Included in plan
            generation_time=0.0,  # Set by caller
            metadata=ultra_response.metadata
        )
        
    async def _generate_with_useapi_premium(self, request: GenerationRequest) -> GenerationResponse:
        """Generate video using UseAPI.net premium account (Veo2)"""
        account = await self.useapi_pool.get_account_for_model(ModelType.VEO2, prefer_free=False)
        if not account:
            raise Exception("No premium accounts available")
            
        # Here you would implement the actual UseAPI.net Veo2 call
        # For now, returning a mock response
        return GenerationResponse(
            video_id=f"pixverse_{account.id}_{int(time.time())}",
            download_url="https://example.com/video.mp4",
            model_used="pixverse-v4",
            service_used="useapi_premium",
            credits_used=700,
            cost_usd=0.85,
            generation_time=0.0,
            metadata={"account": account.email, "platform": request.platform.value}
        )
        
    async def _generate_with_useapi_volume(self, request: GenerationRequest) -> GenerationResponse:
        """Generate video using UseAPI.net volume account (LTX Turbo)"""
        account = await self.useapi_pool.get_account_for_model(ModelType.LTX_TURBO, prefer_free=True)
        if not account:
            raise Exception("No volume accounts available")
            
        # Here you would implement the actual UseAPI.net LTX Turbo call
        # For now, returning a mock response
        return GenerationResponse(
            video_id=f"ltx_{account.id}_{int(time.time())}",
            download_url="https://example.com/video.mp4",
            model_used="ltx_turbo",
            service_used="useapi_volume",
            credits_used=0,
            cost_usd=0.0,
            generation_time=0.0,
            metadata={"account": account.email, "platform": request.platform.value}
        )
        
    async def _fallback_generation(self, request: GenerationRequest, start_time: float) -> GenerationResponse:
        """Attempt fallback generation if primary method fails"""
        # Try LTX Turbo as fallback (always available)
        try:
            response = await self._generate_with_useapi_volume(request)
            response.generation_time = time.time() - start_time
            response.metadata["fallback"] = True
            logger.warning("Used fallback generation with LTX Turbo")
            return response
        except Exception as e:
            logger.error(f"Fallback generation also failed: {e}")
            raise
            
    def _update_stats(self, service: str, model: str, credits: int, cost: float):
        """Update generation statistics"""
        stat_key = f"{service}_{model}".replace("google_ultra_veo3_", "google_ultra_")
        if stat_key in self.generation_stats:
            self.generation_stats[stat_key] += 1
        self.generation_stats["total_credits"] += credits
        self.generation_stats["total_cost"] += cost
        
    async def get_capacity_report(self) -> Dict[str, Any]:
        """Get current capacity across all services"""
        google_capacity = await self.google_integration.get_daily_capacity()
        useapi_stats = self.useapi_pool.get_stats()
        
        return {
            "google_ultra": google_capacity,
            "useapi_pool": useapi_stats,
            "generation_stats": self.generation_stats,
            "total_daily_capacity": {
                "premium_videos": google_capacity["veo3_quality_capacity"],
                "standard_videos": google_capacity["veo3_fast_capacity"] + useapi_stats["healthy_accounts"],
                "volume_videos": 999999  # Unlimited with LTX Turbo
            }
        }
        
    async def optimize_for_30_day_strategy(self) -> Dict[str, int]:
        """
        Calculate optimal distribution for 30-day monetization strategy
        Target: 2,880 videos (96/day) at $0.016 average cost
        """
        google_credits = await self.google_wrapper.check_credits()
        monthly_credits = google_credits["credits_limit"]
        
        # Optimal distribution for 30 days
        premium_daily = min(4, monthly_credits // (30 * 100))  # Veo 3 Quality
        standard_daily = min(8, (monthly_credits - premium_daily * 30 * 100) // (30 * 20))  # Veo 3 Fast
        volume_daily = 96 - premium_daily - standard_daily  # LTX Turbo
        
        return {
            "daily_distribution": {
                "premium_videos": premium_daily,
                "standard_videos": standard_daily,
                "volume_videos": volume_daily,
                "total_daily": premium_daily + standard_daily + volume_daily
            },
            "monthly_totals": {
                "premium_videos": premium_daily * 30,
                "standard_videos": standard_daily * 30,
                "volume_videos": volume_daily * 30,
                "total_monthly": (premium_daily + standard_daily + volume_daily) * 30
            },
            "cost_breakdown": {
                "google_ultra_cost": 0.0,  # Included in plan
                "useapi_cost": 45.0,  # 3 accounts at $15 each
                "ltx_studio_cost": 35.0,
                "total_monthly": 80.0,
                "cost_per_video": 80.0 / ((premium_daily + standard_daily + volume_daily) * 30)
            }
        }


# Example usage
if __name__ == "__main__":
    async def test_enhanced_router():
        # Configuration
        google_creds = "/home/golde/.google-ai-ultra-credentials.json"
        useapi_accounts = [
            {
                "id": "primary",
                "email": "goldensonproperties@gmail.com",
                "bearer_token": "user:1831-r8vA1WGayarXKuYwpT1PW",
                "models": ["pixverse", "ltx-turbo"],
                "priority": 1,
                "credit_limit": 5000
            }
        ]
        
        router = EnhancedModelRouter(google_creds, useapi_accounts, "balanced")
        await router.start()
        
        # Test generation
        request = GenerationRequest(
            prompt="A beautiful sunset over a calm lake",
            platform=Platform.YOUTUBE,
            quality_tier=QualityTier.PREMIUM
        )
        
        response = await router.generate_video(request)
        print(f"Generated: {response.video_id} using {response.service_used}:{response.model_used}")
        
        # Get capacity report
        capacity = await router.get_capacity_report()
        print(f"Capacity: {capacity}")
        
        # Get 30-day strategy
        strategy = await router.optimize_for_30_day_strategy()
        print(f"30-day strategy: {strategy}")
        
        await router.stop()
        
    asyncio.run(test_enhanced_router())