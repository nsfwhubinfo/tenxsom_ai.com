"""
Enhanced Model Router for Tenxsom AI
Intelligently routes video generation requests across three tiers:
1. Google AI Ultra (Veo 3 Quality/Fast)
2. UseAPI.net Premium (Veo2)
3. UseAPI.net Volume (LTX Turbo)
"""

import asyncio
import logging
import time
import aiohttp
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

from integrations.google_ultra.google_ai_ultra_wrapper import GoogleAIUltraWrapper, TenxsomGoogleUltraIntegration, Veo3Model
from integrations.useapi.account_pool_manager import AccountPoolManager, ModelType

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
        # Simplified two-service architecture
        if request.quality_tier == QualityTier.PREMIUM:
            return "google_ultra", "veo3_quality"
        elif request.quality_tier == QualityTier.STANDARD:
            return "google_ultra", "veo3_fast"
        else:  # VOLUME
            return "useapi_volume", "ltx_studio"
    
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
    
    @staticmethod
    def select_google_failover(request: GenerationRequest) -> tuple[str, str]:
        """Select Google AI Ultra as primary during UseAPI.net issues"""
        # Prioritize Google AI Ultra for all tiers during failover
        if request.quality_tier == QualityTier.PREMIUM:
            return "google_ultra", "veo3_quality"
        elif request.quality_tier == QualityTier.STANDARD:
            return "google_ultra", "veo3_fast"
        else:
            # Even volume tier uses Google Fast during failover
            return "google_ultra", "veo3_fast"
    
    @staticmethod
    def select_adaptive_failover(request: GenerationRequest, service_health: dict) -> tuple[str, str]:
        """Adaptive selection based on real-time service health"""
        useapi_healthy = service_health.get("useapi_healthy", False)
        google_healthy = service_health.get("google_healthy", True)
        
        # If UseAPI.net is healthy, use normal balanced strategy
        if useapi_healthy:
            return ModelSelectionStrategy.select_balanced(request)
        
        # If UseAPI.net is down but Google is healthy, use Google failover
        elif google_healthy:
            return ModelSelectionStrategy.select_google_failover(request)
        
        # Emergency: both services have issues, prioritize any working service
        else:
            logger.warning("🚨 Both services degraded, using emergency fallback")
            return "google_ultra", "veo3_fast"  # Most reliable fallback


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
                 strategy: str = "balanced",
                 enable_adaptive_failover: bool = True):
        """
        Initialize the enhanced model router
        
        Args:
            google_ultra_credentials: Path to Google AI Ultra credentials
            useapi_accounts_config: UseAPI.net account configurations
            strategy: Selection strategy (youtube_monetization, cost_optimized, balanced, google_failover, adaptive_failover)
            enable_adaptive_failover: Enable automatic failover based on service health
        """
        self.strategy = strategy
        self.enable_adaptive_failover = enable_adaptive_failover
        self.failover_mode = False  # Track if we're in failover mode
        
        # Initialize Google AI Ultra
        self.google_wrapper = GoogleAIUltraWrapper(google_ultra_credentials)
        self.google_integration = TenxsomGoogleUltraIntegration(self.google_wrapper)
        
        # Initialize UseAPI.net account pool
        self.useapi_pool = AccountPoolManager(useapi_accounts_config)
        
        # Strategy selector
        self.strategy_map = {
            "youtube_monetization": ModelSelectionStrategy.select_for_youtube_monetization,
            "cost_optimized": ModelSelectionStrategy.select_cost_optimized,
            "balanced": ModelSelectionStrategy.select_balanced,
            "google_failover": ModelSelectionStrategy.select_google_failover,
            "adaptive_failover": ModelSelectionStrategy.select_adaptive_failover
        }
        
        # Service health tracking
        self.service_health = {
            "useapi_healthy": False,
            "google_healthy": True,
            "last_health_check": None,
            "consecutive_useapi_failures": 0,
            "consecutive_google_failures": 0
        }
        
        # Usage tracking
        self.generation_stats = {
            "google_ultra_quality": 0,
            "google_ultra_fast": 0,
            "useapi_veo2": 0,
            "useapi_ltx_turbo": 0,
            "total_cost": 0.0,
            "total_credits": 0,
            "failover_activations": 0,
            "service_restorations": 0
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
        Generate video using the optimal model with adaptive failover
        
        Args:
            request: Video generation request
            
        Returns:
            Generation response with video details
        """
        start_time = time.time()
        
        # Update service health before selection
        await self._update_service_health()
        
        # Select service and model based on strategy and health
        if self.enable_adaptive_failover and self.strategy == "adaptive_failover":
            service, model = ModelSelectionStrategy.select_adaptive_failover(request, self.service_health)
        else:
            strategy_func = self.strategy_map[self.strategy]
            service, model = strategy_func(request)
            
        # Override with failover if UseAPI.net is unhealthy and we're not already using Google
        if (self.enable_adaptive_failover and 
            not self.service_health["useapi_healthy"] and 
            service.startswith("useapi")):
            logger.warning(f"🔄 UseAPI.net unhealthy, switching to Google AI Ultra failover")
            service, model = ModelSelectionStrategy.select_google_failover(request)
            if not self.failover_mode:
                self.failover_mode = True
                self.generation_stats["failover_activations"] += 1
                logger.info("🚨 FAILOVER MODE ACTIVATED: Using Google AI Ultra as primary engine")
        
        try:
            if service == "google_ultra":
                response = await self._generate_with_google_ultra(request, model)
                # Mark Google as healthy on success
                self.service_health["google_healthy"] = True
                self.service_health["consecutive_google_failures"] = 0
            elif service == "useapi_premium":
                response = await self._generate_with_useapi_premium(request)
                # Mark UseAPI as healthy on success
                self.service_health["useapi_healthy"] = True
                self.service_health["consecutive_useapi_failures"] = 0
                if self.failover_mode:
                    self.failover_mode = False
                    self.generation_stats["service_restorations"] += 1
                    logger.info("✅ SERVICE RESTORED: UseAPI.net back online, exiting failover mode")
            elif service == "useapi_volume":
                response = await self._generate_with_useapi_volume(request)
                # Mark UseAPI as healthy on success
                self.service_health["useapi_healthy"] = True
                self.service_health["consecutive_useapi_failures"] = 0
                if self.failover_mode:
                    self.failover_mode = False
                    self.generation_stats["service_restorations"] += 1
                    logger.info("✅ SERVICE RESTORED: UseAPI.net back online, exiting failover mode")
            else:
                raise ValueError(f"Unknown service: {service}")
                
            # Update stats
            generation_time = time.time() - start_time
            response.generation_time = generation_time
            
            self._update_stats(service, model, response.credits_used, response.cost_usd)
            
            mode_indicator = " [FAILOVER]" if self.failover_mode else ""
            logger.info(f"Generated video using {service}:{model} in {generation_time:.2f}s{mode_indicator}")
            return response
            
        except Exception as e:
            # Update failure counters
            if service == "google_ultra":
                self.service_health["consecutive_google_failures"] += 1
                if self.service_health["consecutive_google_failures"] >= 3:
                    self.service_health["google_healthy"] = False
            elif service.startswith("useapi"):
                self.service_health["consecutive_useapi_failures"] += 1
                if self.service_health["consecutive_useapi_failures"] >= 3:
                    self.service_health["useapi_healthy"] = False
            
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
        """Generate video using UseAPI.net premium account (Pixverse) with retry logic"""
        account = await self.useapi_pool.get_account_for_model(ModelType.PIXVERSE, prefer_free=False)
        if not account:
            raise Exception("No premium accounts available")
            
        # PRODUCTION: Actual UseAPI.net Pixverse API call with retry logic
        import aiohttp
        
        url = "https://api.useapi.net/v2/pixverse/videos/create-v4"  # Updated to current Pixverse API
        headers = {
            "Authorization": f"Bearer {account.bearer_token}",
            "Content-Type": "application/json"
        }
        
        # Get a reference image from assets if needed
        start_asset_id = None
        if hasattr(request, 'image_path') and request.image_path:
            try:
                start_asset_id = await self._upload_reference_image(request.image_path, account.bearer_token)
            except Exception as e:
                logger.warning(f"Reference image upload failed, generating without image: {e}")
        
        # Use correct Pixverse API parameters
        payload = {
            "prompt": request.prompt,
            "duration": 5 if request.duration <= 5 else 8,  # Pixverse valid durations: 5 or 8 seconds
            "aspect_ratio": request.aspect_ratio,  # Use standard format "16:9"
            "seed": None  # Optional
        }
        
        # Add image reference if available
        if start_asset_id:
            payload["image_id"] = start_asset_id
        
        # Retry logic for server issues
        max_retries = 3
        retry_delays = [5, 15, 30]  # Progressive backoff
        
        for attempt in range(max_retries):
            try:
                timeout = aiohttp.ClientTimeout(total=60, connect=15)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(url, headers=headers, json=payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            video_id = data.get("video_id")
                            
                            # Poll for completion
                            download_url = await self._poll_pixverse_status(session, video_id, headers)
                            
                            return GenerationResponse(
                                video_id=video_id,
                                download_url=download_url,
                                model_used="pixverse-v4",
                                service_used="useapi_premium",
                                credits_used=100,  # Updated Pixverse pricing
                                cost_usd=0.12,     # Updated Pixverse cost
                                generation_time=0.0,
                                metadata={"account": account.email, "platform": request.platform.value}
                            )
                        elif response.status in [522, 523, 502, 503, 504]:
                            # Server-side errors - retry with backoff
                            if attempt < max_retries - 1:
                                delay = retry_delays[attempt]
                                logger.warning(f"Pixverse server error {response.status}, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                                await asyncio.sleep(delay)
                                continue
                            else:
                                error_data = await response.text()
                                raise Exception(f"Pixverse generation failed after {max_retries} attempts: {response.status}")
                        else:
                            error_data = await response.text()
                            raise Exception(f"Pixverse generation failed: {response.status} - {error_data}")
                            
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt < max_retries - 1:
                    delay = retry_delays[attempt]
                    logger.warning(f"Pixverse connection error, retrying in {delay}s (attempt {attempt + 1}/{max_retries}): {e}")
                    await asyncio.sleep(delay)
                    continue
                else:
                    logger.error(f"Pixverse generation failed after {max_retries} attempts: {e}")
                    raise
                    
            except Exception as e:
                logger.error(f"Pixverse generation error: {e}")
                raise
        
    async def _generate_with_useapi_volume(self, request: GenerationRequest) -> GenerationResponse:
        """Generate video using UseAPI.net volume account (LTX Turbo) with retry logic"""
        account = await self.useapi_pool.get_account_for_model(ModelType.LTX_TURBO, prefer_free=True)
        if not account:
            raise Exception("No volume accounts available")
            
        # PRODUCTION: Actual UseAPI.net LTX Turbo API call with retry logic
        import aiohttp
        
        # First, upload reference image if needed
        image_url = None
        if hasattr(request, 'image_path') and request.image_path:
            try:
                image_url = await self._upload_reference_image(request.image_path, account.bearer_token)
            except Exception as e:
                logger.warning(f"Image upload failed, proceeding without reference image: {e}")
        
        url = "https://api.useapi.net/v1/ltxstudio/videos/veo-create"  # LTX Studio Veo endpoint
        headers = {
            "Authorization": f"Bearer {account.bearer_token}",
            "Content-Type": "application/json"
        }
        
        # Use LTX Studio API parameters - go back to veo2 with proper asset handling
        model_name = "veo2"  # Use veo2 model which has proven working examples
        valid_durations = [5]  # Use only duration 5 which was confirmed working
        ltx_duration = 5  # Fixed duration for consistency
        
        payload = {
            "prompt": request.prompt,
            "model": model_name,
            "duration": str(ltx_duration),  # Convert to string as per working examples
            "aspectRatio": request.aspect_ratio,  # LTX uses standard format: "16:9"
        }
        
        # veo2 requires startAssetId - create a minimal placeholder image if needed
        if image_url:
            payload["startAssetId"] = image_url
            logger.info(f"Using provided image URL: {image_url[:50]}...")
        else:
            # Use the exact format from working examples
            # This was the proven working format from video-generation-success.md
            asset_id = "asset:708f0544-8a77-4325-a455-08bdf3d2501a-type:image/jpeg"
            payload["startAssetId"] = asset_id
            logger.info(f"Using working production asset ID: {asset_id}")
        
        # Retry logic for server issues
        max_retries = 3
        retry_delays = [5, 15, 30]  # Progressive backoff
        
        for attempt in range(max_retries):
            try:
                timeout = aiohttp.ClientTimeout(total=60, connect=15)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(url, headers=headers, json=payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            job_id = data.get("job")
                            
                            # Poll for completion
                            download_url = await self._poll_ltx_status(session, job_id, headers)
                            
                            return GenerationResponse(
                                video_id=job_id,
                                download_url=download_url,
                                model_used="ltxv",
                                service_used="useapi_volume",
                                credits_used=1,  # LTX Studio Veo 2 uses credits from subscription
                                cost_usd=0.01,  # Approximate cost per video from $336/year plan
                                generation_time=0.0,
                                metadata={"account": account.email, "platform": request.platform.value}
                            )
                        elif response.status in [522, 523, 502, 503, 504]:
                            # Server-side errors - retry with backoff
                            if attempt < max_retries - 1:
                                delay = retry_delays[attempt]
                                logger.warning(f"LTX Turbo server error {response.status}, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                                await asyncio.sleep(delay)
                                continue
                            else:
                                error_data = await response.text()
                                raise Exception(f"LTX Turbo generation failed after {max_retries} attempts: {response.status}")
                        else:
                            error_data = await response.text()
                            raise Exception(f"LTX Turbo generation failed: {response.status} - {error_data}")
                            
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt < max_retries - 1:
                    delay = retry_delays[attempt]
                    logger.warning(f"LTX Turbo connection error, retrying in {delay}s (attempt {attempt + 1}/{max_retries}): {e}")
                    await asyncio.sleep(delay)
                    continue
                else:
                    logger.error(f"LTX Turbo generation failed after {max_retries} attempts: {e}")
                    raise
                    
            except Exception as e:
                logger.error(f"LTX Turbo generation error: {e}")
                raise
    
    async def _poll_pixverse_status(self, session: aiohttp.ClientSession, video_id: str, headers: dict) -> str:
        """Poll Pixverse generation status until completion"""
        status_url = f"https://api.useapi.net/v2/pixverse/videos/{video_id}"
        
        for attempt in range(30):  # Max 30 attempts (5 minutes)
            try:
                async with session.get(status_url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        status = data.get("status")
                        
                        if status == "completed":
                            return data.get("download_url")
                        elif status == "failed":
                            raise Exception(f"Pixverse generation failed: {data.get('error', 'Unknown error')}")
                        
                        # Still processing, wait 10 seconds
                        await asyncio.sleep(10)
                    else:
                        logger.warning(f"Status check failed: {response.status}")
                        await asyncio.sleep(10)
                        
            except Exception as e:
                logger.warning(f"Status polling error: {e}")
                await asyncio.sleep(10)
        
        raise Exception("Pixverse generation timed out after 5 minutes")
    
    async def _poll_ltx_status(self, session: aiohttp.ClientSession, job_id: str, headers: dict) -> str:
        """Poll LTX Studio generation status until completion"""
        status_url = f"https://api.useapi.net/v1/ltxstudio/videos/{job_id}"  # LTX Studio status endpoint
        
        for attempt in range(20):  # Max 20 attempts (2 minutes)
            try:
                async with session.get(status_url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        status = data.get("status")
                        
                        if status == "completed":
                            return data.get("download_url")
                        elif status == "failed":
                            raise Exception(f"LTX Turbo generation failed: {data.get('error', 'Unknown error')}")
                        
                        # Still processing, wait 6 seconds
                        await asyncio.sleep(6)
                    else:
                        logger.warning(f"Status check failed: {response.status}")
                        await asyncio.sleep(6)
                        
            except Exception as e:
                logger.warning(f"Status polling error: {e}")
                await asyncio.sleep(6)
        
        raise Exception("LTX Turbo generation timed out after 2 minutes")
    
    async def _upload_reference_image(self, image_path: str, bearer_token: str) -> str:
        """Upload reference image to UseAPI.net"""
        url = "https://api.useapi.net/v1/ltxstudio/assets/"  # Keep trailing slash - this endpoint works!
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "image/jpeg"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                    
                async with session.post(url, headers=headers, data=image_data, params={"type": "reference-image"}) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("url")
                    else:
                        error_data = await response.text()
                        raise Exception(f"Image upload failed: {response.status} - {error_data}")
                        
        except Exception as e:
            logger.error(f"Image upload error: {e}")
            raise
    
    async def _create_minimal_placeholder_asset(self, bearer_token: str) -> str:
        """Create a minimal 1x1 pixel placeholder image asset"""
        try:
            # Create a minimal 1x1 pixel JPEG image in memory
            import io
            from PIL import Image
            
            # Create a tiny 16x16 neutral gray image
            img = Image.new('RGB', (16, 16), color=(128, 128, 128))
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG', quality=85)
            img_data = img_buffer.getvalue()
            
            # Upload the placeholder image
            url = "https://api.useapi.net/v1/ltxstudio/assets/"
            headers = {
                "Authorization": f"Bearer {bearer_token}",
                "Content-Type": "image/jpeg"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=img_data, params={"type": "reference-image"}) as response:
                    if response.status == 200:
                        data = await response.json()
                        asset_id = data.get("asset", {}).get("fileId")
                        if asset_id:
                            logger.info(f"Created minimal placeholder asset: {asset_id}")
                            return asset_id
                    
                    logger.warning(f"Placeholder asset creation failed: {response.status}")
                    return None
                    
        except ImportError:
            logger.warning("PIL not available for image creation")
            return None
        except Exception as e:
            logger.warning(f"Placeholder asset creation error: {e}")
            return None
    
    async def _get_or_create_default_asset(self, bearer_token: str) -> str:
        """Get or create a default background asset for LTX Studio"""
        # Check if we have a cached default asset ID
        if hasattr(self, '_default_asset_cache'):
            return self._default_asset_cache
        
        # Create a simple gradient background using the assets endpoint
        url = "https://api.useapi.net/v1/ltxstudio/assets/"  # Confirmed working endpoint
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }
        
        # Use a simpler approach - create a minimal image asset
        # Instead of generating, just create a placeholder asset record
        default_payload = {
            "type": "reference-image",
            "description": "Default placeholder asset for video generation",
            "width": 1920,
            "height": 1080
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=default_payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        asset_id = data.get("asset_id") or data.get("url")
                        
                        # Cache the asset ID for reuse
                        self._default_asset_cache = asset_id
                        logger.info("Created and cached default LTX Studio asset")
                        return asset_id
                    else:
                        # Fallback: use a known working asset URL if available
                        logger.warning(f"Default asset creation failed: {response.status}")
                        
                        # Use a minimal fallback - empty string may work for some LTX models
                        return None
                        
        except Exception as e:
            logger.error(f"Default asset creation error: {e}")
            return None
        
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
    
    async def _update_service_health(self):
        """Update service health status"""
        from datetime import datetime, timedelta
        
        # Only check health every 30 seconds to avoid overhead
        if (self.service_health["last_health_check"] and 
            datetime.now() - self.service_health["last_health_check"] < timedelta(seconds=30)):
            return
            
        try:
            # Quick health check using account pool
            if self.useapi_pool and hasattr(self.useapi_pool, 'test_service_health'):
                health_result = await self.useapi_pool.test_service_health()
                self.service_health["useapi_healthy"] = health_result.get("overall_health") == "healthy"
            
            # Google health check (assume healthy unless we've had recent failures)
            if self.service_health["consecutive_google_failures"] < 3:
                self.service_health["google_healthy"] = True
                
            self.service_health["last_health_check"] = datetime.now()
            
        except Exception as e:
            logger.debug(f"Health check error: {e}")
            
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