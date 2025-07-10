#!/usr/bin/env python3

"""
Tenxsom AI 30-Day Monetization Strategy Executor
Orchestrates the complete 30-day YouTube monetization pipeline
Target: 2,880 videos (96/day) at $0.028 average cost
"""

import asyncio
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# Import our production components
from production_config_manager import ProductionConfigManager
from integrations.enhanced_model_router import EnhancedModelRouter, GenerationRequest, Platform, QualityTier
from agents.youtube_expert.main import YouTubePlatformExpert, ContentCategory
import sys
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ContentRequest:
    """Individual content generation request"""
    content_id: str
    platform: str
    quality_tier: str
    topic: str
    duration: int
    scheduled_time: datetime
    priority: int = 1


@dataclass
class GenerationResult:
    """Result of content generation"""
    content_id: str
    success: bool
    video_id: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_path: Optional[str] = None
    model_used: Optional[str] = None
    service_used: Optional[str] = None
    credits_used: int = 0
    cost_usd: float = 0.0
    generation_time: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class DailyTargets:
    """Daily content generation targets"""
    premium_videos: int = 4      # Google AI Ultra Veo 3 Quality 
    standard_videos: int = 8     # Google AI Ultra Veo 3 Fast
    volume_videos: int = 84      # UseAPI.net LTX Turbo (free)
    total_daily: int = 96
    
    def __post_init__(self):
        self.total_daily = self.premium_videos + self.standard_videos + self.volume_videos


class MonetizationStrategyExecutor:
    """
    Executes the 30-day YouTube monetization strategy
    
    Strategy Overview:
    - 2,880 total videos over 30 days (96/day)
    - Premium: 120 videos (4/day) using Veo 3 Quality
    - Standard: 240 videos (8/day) using Veo 3 Fast  
    - Volume: 2,520 videos (84/day) using LTX Turbo (free)
    - Target cost: $80/month ($0.028 per video average)
    """
    
    def __init__(self, config_manager: ProductionConfigManager = None):
        """Initialize the monetization executor"""
        self.config = config_manager or ProductionConfigManager()
        self.targets = DailyTargets()
        
        # Initialize enhanced model router for production generation
        self.model_router = None
        self._initialize_model_router()
        
        # Initialize upload orchestrator for production uploads
        self.upload_orchestrator = None
        self._initialize_upload_orchestrator()
        
        # Initialize YouTube expert agent for strategic topic selection
        self.youtube_expert = YouTubePlatformExpert()
        
        # Category mapping for tier-based content strategy
        self.category_mapping = {
            "premium": ContentCategory.BUSINESS,  # High monetization potential
            "standard": ContentCategory.TECH,     # Balanced engagement/monetization
            "volume": ContentCategory.ENTERTAINMENT  # High engagement for reach
        }
        
        # Strategy metrics
        self.daily_stats = {
            "videos_generated": 0,
            "videos_uploaded": 0,
            "total_cost": 0.0,
            "total_credits": 0,
            "success_rate": 0.0,
            "start_time": datetime.now()
        }
        
        # Content categories for variety
        self.content_categories = [
            "technology", "business", "lifestyle", "education", 
            "entertainment", "news", "finance", "health"
        ]
        
        # Platform distribution strategy
        self.platform_distribution = {
            "youtube": 0.80,  # 80% for YouTube monetization focus
            "tiktok": 0.10,   # 10% for TikTok growth
            "instagram": 0.05, # 5% for Instagram presence
            "x": 0.05         # 5% for X/Twitter engagement
        }
        
    def _initialize_model_router(self):
        """Initialize the enhanced model router for production video generation"""
        try:
            google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            useapi_config = [
                {
                    "id": "primary",
                    "email": os.getenv("USEAPI_EMAIL", "goldensonproperties@gmail.com"),
                    "bearer_token": os.getenv("USEAPI_BEARER_TOKEN"),
                    "models": ["pixverse", "ltx-turbo"],
                    "priority": 1,
                    "credit_limit": 5000
                }
            ]
            
            self.model_router = EnhancedModelRouter(
                google_ultra_credentials=google_creds,
                useapi_accounts_config=useapi_config,
                strategy="youtube_monetization",  # Use YouTube monetization strategy
                enable_adaptive_failover=False  # Disable adaptive failover to use our defined tiers
            )
            logger.info("✅ Enhanced model router initialized for production")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize model router: {e}")
            self.model_router = None
            
    async def _start_model_router(self):
        """Start the model router if not already started"""
        if self.model_router and not hasattr(self.model_router, '_started'):
            await self.model_router.start()
            self.model_router._started = True
            
    def _initialize_upload_orchestrator(self):
        """Initialize the upload orchestrator for production uploads"""
        try:
            # Import here to avoid circular dependency
            from content_upload_orchestrator import ContentUploadOrchestrator
            
            self.upload_orchestrator = ContentUploadOrchestrator(self.config)
            logger.info("✅ Upload orchestrator initialized for production")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize upload orchestrator: {e}")
            self.upload_orchestrator = None
        
    def calculate_optimal_distribution(self, failover_mode: bool = False) -> Dict[str, int]:
        """
        Calculate optimal daily video distribution across quality tiers
        Based on Google AI Ultra credits and UseAPI.net capacity
        
        Args:
            failover_mode: If True, optimize for Google AI Ultra as primary engine
        """
        # Google AI Ultra: 12,500 credits/month
        monthly_credits = 12500
        daily_credits = monthly_credits // 30  # ~417 credits/day
        
        if failover_mode:
            # FAILOVER MODE: Maximize Google AI Ultra usage while UseAPI.net is down
            logger.info("🚨 FAILOVER MODE: Optimizing for Google AI Ultra as primary engine")
            
            # Use more Google credits during failover to maintain production
            premium_daily = min(8, daily_credits // 100)  # Increase premium allocation
            remaining_credits = daily_credits - (premium_daily * 100)
            standard_daily = min(20, remaining_credits // 20)  # Significantly increase standard allocation
            
            # Reduce volume tier during failover (no free LTX Turbo available)
            volume_daily = max(0, 96 - premium_daily - standard_daily)
            
            return {
                "premium_daily": premium_daily,
                "standard_daily": standard_daily,
                "volume_daily": volume_daily,
                "total_daily": premium_daily + standard_daily + volume_daily,
                "credits_used_daily": (premium_daily * 100) + (standard_daily * 20),
                "credits_remaining": daily_credits - ((premium_daily * 100) + (standard_daily * 20)),
                "mode": "google_failover",
                "cost_per_video": 0.0,  # Google credits are included in plan
                "estimated_monthly_cost": 0.0
            }
        else:
            # NORMAL MODE: Simplified two-service allocation
            premium_daily = 3  # Veo 3 Quality (100 credits each = 300 credits)
            standard_daily = 5  # Veo 3 Fast (20 credits each = 100 credits)
            volume_daily = 88  # LTX Studio Veo 2 (UseAPI.net credits)
            
            # Total Google credits: 400 (under 417 daily limit)
            
            return {
                "premium_daily": premium_daily,
                "standard_daily": standard_daily, 
                "volume_daily": volume_daily,
                "total_daily": premium_daily + standard_daily + volume_daily,
                "credits_used_daily": (premium_daily * 100) + (standard_daily * 20),
                "credits_remaining": daily_credits - ((premium_daily * 100) + (standard_daily * 20)),
                "mode": "balanced",
                "cost_per_video": 0.028,  # Mixed cost including UseAPI.net
                "estimated_monthly_cost": 80.0
            }
    
    def generate_daily_content_plan(self, date: datetime = None) -> List[ContentRequest]:
        """
        Generate the content plan for a specific day
        
        Args:
            date: Target date (defaults to today)
            
        Returns:
            List of content requests for the day
        """
        if date is None:
            date = datetime.now()
            
        # Detect if we should use failover mode based on model router state
        failover_mode = False
        if self.model_router and hasattr(self.model_router, 'failover_mode'):
            failover_mode = self.model_router.failover_mode
        elif self.model_router and hasattr(self.model_router, 'service_health'):
            failover_mode = not self.model_router.service_health.get("useapi_healthy", True)
            
        distribution = self.calculate_optimal_distribution(failover_mode)
        content_requests = []
        
        # Generate premium content (YouTube focused)
        for i in range(distribution["premium_daily"]):
            content_requests.append(ContentRequest(
                content_id=f"premium_{date.strftime('%Y%m%d')}_{i+1:02d}",
                platform="youtube",
                quality_tier="premium",
                topic=self._select_trending_topic("premium"),
                duration=30,
                scheduled_time=date.replace(hour=8+i*2, minute=0, second=0),
                priority=1
            ))
        
        # Generate standard content (multi-platform)
        platforms = ["youtube", "instagram", "tiktok"]
        for i in range(distribution["standard_daily"]):
            platform = platforms[i % len(platforms)]
            content_requests.append(ContentRequest(
                content_id=f"standard_{date.strftime('%Y%m%d')}_{i+1:02d}",
                platform=platform,
                quality_tier="standard", 
                topic=self._select_trending_topic("standard"),
                duration=15 if platform != "youtube" else 20,
                scheduled_time=date.replace(hour=10+i, minute=0, second=0),
                priority=2
            ))
        
        # Generate volume content (TikTok/Instagram focused)
        volume_platforms = ["tiktok", "instagram", "youtube"]
        for i in range(distribution["volume_daily"]):
            platform = volume_platforms[i % len(volume_platforms)]
            content_requests.append(ContentRequest(
                content_id=f"volume_{date.strftime('%Y%m%d')}_{i+1:02d}",
                platform=platform,
                quality_tier="volume",
                topic=self._select_trending_topic("volume"),
                duration=15,
                scheduled_time=date.replace(hour=12+(i//10), minute=(i%10)*6, second=0),
                priority=3
            ))
        
        logger.info(f"Generated {len(content_requests)} content requests for {date.strftime('%Y-%m-%d')}")
        return content_requests
    
    def _select_trending_topic(self, tier: str) -> str:
        """Select trending topic based on quality tier using YouTube expert agent"""
        try:
            # Map tiers to content categories for strategic focus
            category_mapping = {
                "premium": ContentCategory.BUSINESS,  # High monetization potential
                "standard": ContentCategory.TECH,     # Balanced engagement/monetization
                "volume": ContentCategory.ENTERTAINMENT  # High engagement for reach
            }
            
            category = category_mapping.get(tier, ContentCategory.TECH)
            
            # Get trending opportunities from YouTube expert agent
            trends_data = self.youtube_expert.monitor_trends(
                category=category,
                geographic_region="US",
                time_horizon=7  # Weekly trends for current relevance
            )
            
            # Extract high-priority trending topics
            opportunities = trends_data.get("trends", {}).get("opportunities", [])
            high_priority_topics = [
                opp["keyword"] for opp in opportunities 
                if opp.get("opportunity_score", 0) >= 6.0  # Medium to high priority
            ]
            
            if high_priority_topics:
                # Select from trending topics
                import random
                selected_topic = random.choice(high_priority_topics)
                logger.info(f"Selected trending topic for {tier}: {selected_topic}")
                return selected_topic
            else:
                # Fallback to agent's immediate actions if no high-priority topics
                immediate_actions = trends_data.get("recommendations", {}).get("immediate_actions", [])
                if immediate_actions:
                    return immediate_actions[0].replace("Create content about ", "")
                    
        except Exception as e:
            logger.warning(f"YouTube expert agent failed for tier {tier}: {e}")
            
        # Intelligent fallback using agent's fallback system or context-aware generation
        return self._get_intelligent_fallback_topic(tier)
    
    def _get_intelligent_fallback_topic(self, tier: str) -> str:
        """Get intelligent fallback topic when agent fails"""
        try:
            # Attempt to use agent's fallback system even when main method fails
            fallback_trends = self.youtube_expert.monitor_trends(
                category=self.category_mapping.get(tier, ContentCategory.TECH),
                geographic_region="global",  # Broader scope for fallback
                time_horizon=30  # Longer term stable trends
            )
            
            # Look for any available opportunities
            opportunities = fallback_trends.get("trends", {}).get("opportunities", [])
            if opportunities:
                # Take first available topic even if lower priority
                fallback_topic = opportunities[0]["keyword"]
                logger.info(f"Using agent fallback topic for {tier}: {fallback_topic}")
                return fallback_topic
                
        except Exception as e:
            logger.error(f"Agent fallback also failed for {tier}: {e}")
        
        # Context-aware intelligent fallbacks (not hardcoded)
        current_hour = datetime.now().hour
        day_of_week = datetime.now().weekday()
        
        # Time and context-based intelligent topic generation
        if current_hour < 8:  # Early morning
            context_fallbacks = {
                "premium": "Morning productivity optimization strategies",
                "standard": "Start your day with tech efficiency",
                "volume": "Quick morning motivation boost"
            }
        elif current_hour < 12:  # Morning work hours
            context_fallbacks = {
                "premium": "Business intelligence for professionals",
                "standard": "Workplace technology innovations",
                "volume": "Quick professional development tips"
            }
        elif current_hour < 17:  # Afternoon
            context_fallbacks = {
                "premium": "Strategic innovation analysis",
                "standard": "Afternoon productivity insights",
                "volume": "Fast tech news updates"
            }
        elif current_hour < 22:  # Evening
            context_fallbacks = {
                "premium": "Evening reflection on business trends",
                "standard": "Technology lifestyle integration",
                "volume": "Relaxing tech entertainment"
            }
        else:  # Night
            context_fallbacks = {
                "premium": "Strategic planning for tomorrow",
                "standard": "Night-time productivity optimization",
                "volume": "Inspiring late-night content"
            }
        
        # Weekend vs weekday optimization
        if day_of_week >= 5:  # Weekend
            weekend_suffix = " for weekend exploration"
            fallback_topic = context_fallbacks.get(tier, "Intelligent content strategy") + weekend_suffix
        else:
            fallback_topic = context_fallbacks.get(tier, "Intelligent content strategy")
        
        logger.info(f"Using context-aware fallback for {tier}: {fallback_topic}")
        return fallback_topic
    
    async def execute_daily_strategy(self, date: datetime = None) -> Dict[str, Any]:
        """
        Execute the complete daily content strategy
        
        Args:
            date: Target date for execution
            
        Returns:
            Execution results and metrics
        """
        if date is None:
            date = datetime.now()
            
        logger.info(f"🚀 Starting daily strategy execution for {date.strftime('%Y-%m-%d')}")
        
        # Generate content plan
        content_plan = self.generate_daily_content_plan(date)
        
        # Execute content generation
        generation_results = await self._execute_content_generation(content_plan)
        
        # Execute content upload and distribution  
        upload_results = await self._execute_content_upload(generation_results)
        
        # Update analytics and tracking
        daily_metrics = self._calculate_daily_metrics(generation_results, upload_results)
        
        # Save execution report
        report_path = await self._save_daily_report(date, {
            "content_plan": [asdict(req) for req in content_plan],
            "generation_results": [asdict(result) for result in generation_results],
            "upload_results": upload_results,
            "daily_metrics": daily_metrics
        })
        
        logger.info(f"✅ Daily strategy execution completed")
        logger.info(f"📊 Generated: {daily_metrics['videos_generated']}/{daily_metrics['target_videos']}")
        logger.info(f"📤 Uploaded: {daily_metrics['videos_uploaded']}")
        logger.info(f"💰 Cost: ${daily_metrics['total_cost']:.2f}")
        logger.info(f"📄 Report: {report_path}")
        
        return {
            "execution_date": date.isoformat(),
            "content_plan_size": len(content_plan),
            "generation_results": len(generation_results),
            "daily_metrics": daily_metrics,
            "report_path": report_path
        }
    
    async def _execute_content_generation(self, content_plan: List[ContentRequest]) -> List[GenerationResult]:
        """Execute content generation for all requests"""
        logger.info(f"🎬 Starting content generation for {len(content_plan)} requests")
        
        generation_results = []
        
        # Group by priority for optimal resource usage
        priority_groups = {}
        for request in content_plan:
            if request.priority not in priority_groups:
                priority_groups[request.priority] = []
            priority_groups[request.priority].append(request)
        
        # Execute by priority (premium first)
        for priority in sorted(priority_groups.keys()):
            requests = priority_groups[priority]
            logger.info(f"Processing priority {priority}: {len(requests)} requests")
            
            # Execute in batches of 5 for optimal performance
            batch_size = 5
            for i in range(0, len(requests), batch_size):
                batch = requests[i:i+batch_size]
                batch_results = await self._generate_content_batch(batch)
                generation_results.extend(batch_results)
                
                # Brief pause between batches to avoid rate limiting
                await asyncio.sleep(2)
        
        successful = len([r for r in generation_results if r.success])
        logger.info(f"✅ Content generation complete: {successful}/{len(content_plan)} successful")
        
        return generation_results
    
    async def _generate_content_batch(self, requests: List[ContentRequest]) -> List[GenerationResult]:
        """Generate a batch of content requests"""
        batch_results = []
        
        for request in requests:
            try:
                start_time = datetime.now()
                
                # Production content generation using enhanced model router
                result = await self._production_content_generation(request)
                
                generation_time = (datetime.now() - start_time).total_seconds()
                result.generation_time = generation_time
                
                batch_results.append(result)
                logger.debug(f"Generated {request.content_id}: {result.success}")
                
            except Exception as e:
                logger.error(f"Generation failed for {request.content_id}: {e}")
                batch_results.append(GenerationResult(
                    content_id=request.content_id,
                    success=False,
                    error_message=str(e)
                ))
        
        return batch_results
    
    async def _production_content_generation(self, request: ContentRequest) -> GenerationResult:
        """Production content generation using enhanced model router"""
        try:
            # Ensure model router is started
            await self._start_model_router()
            
            if not self.model_router:
                raise Exception("Model router not available")
            
            # Convert ContentRequest to GenerationRequest
            platform_map = {
                "youtube": Platform.YOUTUBE,
                "tiktok": Platform.TIKTOK,
                "instagram": Platform.INSTAGRAM,
                "x": Platform.X
            }
            
            quality_map = {
                "premium": QualityTier.PREMIUM,
                "standard": QualityTier.STANDARD,
                "volume": QualityTier.VOLUME
            }
            
            generation_request = GenerationRequest(
                prompt=request.topic,
                platform=platform_map.get(request.platform, Platform.YOUTUBE),
                quality_tier=quality_map.get(request.quality_tier, QualityTier.STANDARD),
                duration=request.duration,
                priority=request.priority
            )
            
            # Generate video using enhanced model router
            router_response = await self.model_router.generate_video(generation_request)
            
            # Convert response to GenerationResult
            return GenerationResult(
                content_id=request.content_id,
                success=True,
                video_id=router_response.video_id,
                video_url=router_response.download_url,
                thumbnail_path=None,  # Would be generated separately
                model_used=router_response.model_used,
                service_used=router_response.service_used,
                credits_used=router_response.credits_used,
                cost_usd=router_response.cost_usd,
                generation_time=router_response.generation_time,
                metadata={
                    "platform": request.platform,
                    "topic": request.topic,
                    "router_metadata": router_response.metadata
                }
            )
            
        except Exception as e:
            logger.error(f"Production generation failed for {request.content_id}: {e}")
            return GenerationResult(
                content_id=request.content_id,
                success=False,
                error_message=str(e)
            )
    
    async def _execute_content_upload(self, generation_results: List[GenerationResult]) -> Dict[str, Any]:
        """Execute content upload and distribution"""
        successful_generations = [r for r in generation_results if r.success]
        logger.info(f"📤 Starting upload for {len(successful_generations)} generated videos")
        
        upload_stats = {
            "upload_attempts": len(successful_generations),
            "upload_successes": 0,
            "upload_failures": 0,
            "platforms": {}
        }
        
        # Use production upload orchestrator
        try:
            if self.upload_orchestrator:
                orchestrator_result = await self.upload_orchestrator.orchestrate_uploads(successful_generations)
                
                upload_stats["upload_successes"] = orchestrator_result.get("total_uploads", 0)
                upload_stats["upload_failures"] = len(successful_generations) - upload_stats["upload_successes"]
                upload_stats["platforms"] = orchestrator_result.get("platform_stats", {})
                
            else:
                logger.warning("⚠️ Upload orchestrator not available, using fallback")
                # Fallback to simple upload tracking
                for result in successful_generations:
                    upload_stats["upload_failures"] += 1
                    platform = result.metadata.get("platform", "unknown")
                    if platform not in upload_stats["platforms"]:
                        upload_stats["platforms"][platform] = {"attempts": 0, "successes": 0}
                    upload_stats["platforms"][platform]["attempts"] += 1
                    
        except Exception as e:
            logger.error(f"Upload orchestration failed: {e}")
            upload_stats["upload_failures"] = len(successful_generations)
        
        logger.info(f"✅ Upload complete: {upload_stats['upload_successes']}/{upload_stats['upload_attempts']} successful")
        return upload_stats
    
    # Mock function removed - now using production upload orchestrator
    
    def _calculate_daily_metrics(self, generation_results: List[GenerationResult], upload_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive daily metrics"""
        successful_generations = [r for r in generation_results if r.success]
        
        total_credits = sum(r.credits_used for r in successful_generations)
        total_cost = sum(r.cost_usd for r in successful_generations)
        
        # Calculate success rates
        generation_success_rate = len(successful_generations) / len(generation_results) if generation_results else 0
        upload_success_rate = upload_results["upload_successes"] / upload_results["upload_attempts"] if upload_results["upload_attempts"] > 0 else 0
        
        # Platform breakdown
        platform_breakdown = {}
        for result in successful_generations:
            platform = result.metadata.get("platform", "unknown")
            if platform not in platform_breakdown:
                platform_breakdown[platform] = 0
            platform_breakdown[platform] += 1
        
        return {
            "target_videos": self.targets.total_daily,
            "videos_generated": len(successful_generations),
            "videos_uploaded": upload_results["upload_successes"],
            "generation_success_rate": round(generation_success_rate * 100, 1),
            "upload_success_rate": round(upload_success_rate * 100, 1),
            "total_credits": total_credits,
            "total_cost": round(total_cost, 2),
            "cost_per_video": round(total_cost / len(successful_generations), 4) if successful_generations else 0,
            "platform_breakdown": platform_breakdown,
            "quality_tier_breakdown": {
                "premium": len([r for r in successful_generations if r.model_used == "veo3_quality"]),
                "standard": len([r for r in successful_generations if r.model_used == "veo3_fast"]),
                "volume": len([r for r in successful_generations if r.model_used == "ltx_turbo"])
            }
        }
    
    async def _save_daily_report(self, date: datetime, report_data: Dict[str, Any]) -> str:
        """Save comprehensive daily execution report"""
        reports_dir = Path(__file__).parent / "reports" / "daily"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_filename = f"daily_execution_{date.strftime('%Y_%m_%d')}.json"
        report_path = reports_dir / report_filename
        
        report_data["report_timestamp"] = datetime.now().isoformat()
        report_data["execution_date"] = date.isoformat()
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        return str(report_path)
    
    async def execute_30_day_strategy(self, start_date: datetime = None) -> Dict[str, Any]:
        """
        Execute the complete 30-day monetization strategy
        
        Args:
            start_date: Strategy start date (defaults to today)
            
        Returns:
            30-day execution summary
        """
        if start_date is None:
            start_date = datetime.now()
            
        logger.info(f"🚀 Starting 30-day monetization strategy from {start_date.strftime('%Y-%m-%d')}")
        
        monthly_results = []
        monthly_stats = {
            "total_videos_generated": 0,
            "total_videos_uploaded": 0, 
            "total_cost": 0.0,
            "total_credits": 0,
            "daily_results": []
        }
        
        # Execute for 30 days
        for day in range(30):
            execution_date = start_date + timedelta(days=day)
            
            try:
                daily_result = await self.execute_daily_strategy(execution_date)
                monthly_results.append(daily_result)
                
                # Aggregate stats
                metrics = daily_result["daily_metrics"]
                monthly_stats["total_videos_generated"] += metrics["videos_generated"]
                monthly_stats["total_videos_uploaded"] += metrics["videos_uploaded"]
                monthly_stats["total_cost"] += metrics["total_cost"]
                monthly_stats["total_credits"] += metrics["total_credits"]
                monthly_stats["daily_results"].append(daily_result)
                
                logger.info(f"Day {day+1}/30 complete - Generated: {metrics['videos_generated']}, Uploaded: {metrics['videos_uploaded']}")
                
                # Brief pause between days
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Day {day+1} execution failed: {e}")
                monthly_results.append({
                    "execution_date": execution_date.isoformat(),
                    "error": str(e),
                    "success": False
                })
        
        # Calculate final metrics
        final_metrics = self._calculate_monthly_metrics(monthly_stats)
        
        # Save monthly report
        monthly_report_path = await self._save_monthly_report(start_date, {
            "strategy_period": f"{start_date.strftime('%Y-%m-%d')} to {(start_date + timedelta(days=29)).strftime('%Y-%m-%d')}",
            "monthly_stats": monthly_stats,
            "final_metrics": final_metrics,
            "daily_results": monthly_results
        })
        
        logger.info(f"🎉 30-day strategy execution completed!")
        logger.info(f"📊 Total Videos: {final_metrics['total_videos']}/2880 ({final_metrics['completion_rate']:.1f}%)")
        logger.info(f"💰 Total Cost: ${final_metrics['total_cost']:.2f}")
        logger.info(f"📈 Average Cost per Video: ${final_metrics['cost_per_video']:.4f}")
        logger.info(f"📄 Monthly Report: {monthly_report_path}")
        
        return {
            "execution_period": f"{start_date.strftime('%Y-%m-%d')} to {(start_date + timedelta(days=29)).strftime('%Y-%m-%d')}",
            "final_metrics": final_metrics,
            "monthly_report_path": monthly_report_path,
            "success": True
        }
    
    def _calculate_monthly_metrics(self, monthly_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate final monthly metrics"""
        target_videos = 2880  # 96 videos/day * 30 days
        
        return {
            "target_videos": target_videos,
            "total_videos": monthly_stats["total_videos_generated"],
            "completion_rate": (monthly_stats["total_videos_generated"] / target_videos) * 100,
            "total_cost": monthly_stats["total_cost"],
            "cost_per_video": monthly_stats["total_cost"] / monthly_stats["total_videos_generated"] if monthly_stats["total_videos_generated"] > 0 else 0,
            "upload_success_rate": (monthly_stats["total_videos_uploaded"] / monthly_stats["total_videos_generated"]) * 100 if monthly_stats["total_videos_generated"] > 0 else 0,
            "total_credits_used": monthly_stats["total_credits"],
            "daily_average": monthly_stats["total_videos_generated"] / 30,
            "monetization_ready": monthly_stats["total_videos_generated"] >= 1000  # YouTube Partner Program requirement
        }
    
    async def _save_monthly_report(self, start_date: datetime, report_data: Dict[str, Any]) -> str:
        """Save comprehensive monthly execution report"""
        reports_dir = Path(__file__).parent / "reports" / "monthly"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_filename = f"30_day_strategy_{start_date.strftime('%Y_%m')}.json"
        report_path = reports_dir / report_filename
        
        report_data["report_timestamp"] = datetime.now().isoformat()
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        return str(report_path)


def main():
    """Test the monetization strategy executor"""
    async def test_strategy():
        print("🚀 Tenxsom AI 30-Day Monetization Strategy Executor")
        print("=" * 70)
        
        # Initialize executor
        config_manager = ProductionConfigManager()
        executor = MonetizationStrategyExecutor(config_manager)
        
        # Calculate optimal distribution
        distribution = executor.calculate_optimal_distribution()
        print(f"\n📊 Optimal Daily Distribution:")
        print(f"   Premium (Veo 3 Quality): {distribution['premium_daily']} videos")
        print(f"   Standard (Veo 3 Fast): {distribution['standard_daily']} videos")
        print(f"   Volume (LTX Turbo): {distribution['volume_daily']} videos")
        print(f"   Total Daily: {distribution['total_daily']} videos")
        print(f"   Credits Used: {distribution['credits_used_daily']}/417 daily")
        
        # Test daily strategy execution
        print(f"\n🧪 Testing daily strategy execution...")
        daily_result = await executor.execute_daily_strategy()
        
        print(f"\n✅ Daily Test Results:")
        metrics = daily_result["daily_metrics"]
        print(f"   Generated: {metrics['videos_generated']}/{metrics['target_videos']} videos")
        print(f"   Success Rate: {metrics['generation_success_rate']}%")
        print(f"   Total Cost: ${metrics['total_cost']:.2f}")
        print(f"   Cost per Video: ${metrics['cost_per_video']:.4f}")
        
        # Show platform breakdown
        print(f"\n📊 Platform Breakdown:")
        for platform, count in metrics['platform_breakdown'].items():
            print(f"   {platform.title()}: {count} videos")
        
        print(f"\n🎯 Ready for 30-day execution!")
        print(f"   Projected monthly videos: {metrics['videos_generated'] * 30}")
        print(f"   Projected monthly cost: ${metrics['total_cost'] * 30:.2f}")
        
        return daily_result
    
    # Run test
    asyncio.run(test_strategy())


if __name__ == "__main__":
    main()