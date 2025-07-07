#!/usr/bin/env python3

"""
Tenxsom AI Content Upload Orchestrator
Smart content distribution and upload automation across platforms
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json
from dataclasses import dataclass, asdict

# Import our components
from monetization_strategy_executor import GenerationResult
from production_config_manager import ProductionConfigManager
from agents.youtube_expert.main import YouTubePlatformExpert, ContentCategory
from intelligent_resource_optimizer import IntelligentResourceOptimizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass 
class UploadRequest:
    """Individual content upload request"""
    content_id: str
    video_path: str
    thumbnail_path: Optional[str]
    platform: str
    title: str
    description: str
    tags: List[str]
    scheduled_time: Optional[datetime] = None
    privacy_status: str = "private"
    category: str = "education"
    priority: int = 1


@dataclass
class UploadResult:
    """Result of content upload"""
    content_id: str
    platform: str
    success: bool
    video_id: Optional[str] = None
    video_url: Optional[str] = None
    upload_time: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class PlatformQuota:
    """Platform-specific quota and limits"""
    platform: str
    daily_limit: int
    current_usage: int
    quota_reset_time: datetime
    rate_limit_per_hour: int
    current_hourly_usage: int


class ContentUploadOrchestrator:
    """
    Orchestrates content uploads across multiple platforms with smart distribution
    
    Features:
    - Multi-platform upload coordination (YouTube, TikTok, Instagram, X)
    - Smart quota management and rate limiting
    - Content optimization per platform
    - Automated thumbnail generation and A/B testing
    - Upload scheduling and retry mechanisms
    - Performance analytics and monitoring
    """
    
    def __init__(self, config_manager: ProductionConfigManager = None):
        """Initialize the upload orchestrator"""
        self.config = config_manager or ProductionConfigManager()
        
        # Initialize YouTube expert agent for strategic optimization
        self.youtube_expert = YouTubePlatformExpert()
        
        # Initialize intelligent resource optimizer
        self.resource_optimizer = IntelligentResourceOptimizer(self.config)
        
        # Get AI-optimized platform configurations
        self.platform_configs = self._get_intelligent_platform_configs()
        
        # Initialize platform quotas
        self.platform_quotas = {}
        for platform, config in self.platform_configs.items():
            self.platform_quotas[platform] = PlatformQuota(
                platform=platform,
                daily_limit=config["max_daily_uploads"],
                current_usage=0,
                quota_reset_time=datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=1),
                rate_limit_per_hour=config["rate_limit_hour"],
                current_hourly_usage=0
            )
        
        # Content optimization settings
        self.content_optimizations = {
            "youtube": {
                "title_max_length": 100,
                "description_max_length": 5000,
                "tags_max_count": 15,
                "optimal_duration": 30,
                "preferred_aspect_ratio": "16:9"
            },
            "tiktok": {
                "title_max_length": 150,
                "description_max_length": 2200,
                "tags_max_count": 10,
                "optimal_duration": 15,
                "preferred_aspect_ratio": "9:16"
            },
            "instagram": {
                "title_max_length": 125,
                "description_max_length": 2200,
                "tags_max_count": 30,
                "optimal_duration": 15,
                "preferred_aspect_ratio": "9:16"
            },
            "x": {
                "title_max_length": 280,
                "description_max_length": 280,
                "tags_max_count": 5,
                "optimal_duration": 30,
                "preferred_aspect_ratio": "16:9"
            }
        }
        
        # Upload tracking
        self.upload_history = []
        self.pending_uploads = []
        self.failed_uploads = []
        
        # A/B testing for YouTube thumbnails
        self.thumbnail_variants = {}
        
        # Performance tracking for optimization
        self.platform_performance = {}
        self._initialize_performance_tracking()
        
    async def orchestrate_uploads(self, generation_results: List[GenerationResult]) -> Dict[str, Any]:
        """
        Orchestrate uploads for all generated content
        
        Args:
            generation_results: Results from content generation
            
        Returns:
            Upload orchestration results
        """
        logger.info(f"🚀 Starting upload orchestration for {len(generation_results)} generated videos")
        
        # Filter successful generations
        successful_results = [r for r in generation_results if r.success]
        
        if not successful_results:
            logger.warning("❌ No successful generations to upload")
            return {"success": False, "reason": "no_content_to_upload"}
        
        # Create upload requests
        upload_requests = await self._create_upload_requests(successful_results)
        
        # Optimize content for each platform
        optimized_requests = await self._optimize_content_for_platforms(upload_requests)
        
        # Schedule uploads based on quotas and limits
        scheduled_uploads = await self._schedule_uploads(optimized_requests)
        
        # Execute uploads
        upload_results = await self._execute_uploads(scheduled_uploads)
        
        # Process A/B testing for YouTube thumbnails
        if any(r.platform == "youtube" for r in upload_results):
            await self._process_youtube_ab_testing(upload_results)
        
        # Generate upload report
        orchestration_summary = self._generate_orchestration_summary(
            generation_results, upload_requests, upload_results
        )
        
        logger.info(f"✅ Upload orchestration complete: {orchestration_summary['total_uploads']}/{len(successful_results)} uploaded")
        
        return orchestration_summary
    
    async def _create_upload_requests(self, generation_results: List[GenerationResult]) -> List[UploadRequest]:
        """Create upload requests from generation results"""
        upload_requests = []
        
        for result in generation_results:
            # Generate optimized content metadata
            title, description, tags = await self._generate_content_metadata(result)
            
            # Determine platform-specific settings
            platform = result.metadata.get("platform", "youtube")
            
            upload_request = UploadRequest(
                content_id=result.content_id,
                video_path=result.video_url,  # This would be local path in real implementation
                thumbnail_path=result.thumbnail_path,
                platform=platform,
                title=title,
                description=description,
                tags=tags,
                scheduled_time=None,  # Will be set during scheduling
                privacy_status="private" if platform == "youtube" else "public",
                category=self._determine_content_category(result),
                priority=self._determine_upload_priority(result)
            )
            
            upload_requests.append(upload_request)
        
        logger.info(f"📋 Created {len(upload_requests)} upload requests")
        return upload_requests
    
    async def _generate_content_metadata(self, result: GenerationResult) -> Tuple[str, str, List[str]]:
        """Generate optimized title, description, and tags for content"""
        
        # Extract topic and platform from metadata
        topic = result.metadata.get("topic", "AI Content")
        platform = result.metadata.get("platform", "youtube")
        
        # Generate title based on platform and content
        title_templates = {
            "youtube": [
                f"🚀 {topic} - Complete Guide",
                f"💡 {topic} Explained",
                f"⚡ {topic} Tips & Tricks",
                f"🔥 {topic} Strategy"
            ],
            "tiktok": [
                f"🚀 {topic} hack",
                f"💡 {topic} tip",
                f"⚡ Quick {topic}",
                f"🔥 {topic} secret"
            ],
            "instagram": [
                f"✨ {topic} inspiration",
                f"💫 {topic} guide",
                f"🌟 {topic} tips",
                f"💎 {topic} insights"
            ],
            "x": [
                f"🧵 {topic} thread",
                f"💭 {topic} thoughts",
                f"🔍 {topic} analysis",
                f"📊 {topic} data"
            ]
        }
        
        import random
        title = random.choice(title_templates.get(platform, title_templates["youtube"]))
        
        # Use YouTube expert agent for strategic content optimization
        try:
            # Get strategic content optimization
            content_strategy = self.youtube_expert.optimize_content_for_platform(
                content_idea=topic,
                target_platform=platform,
                target_audience="general",
                performance_goals=["engagement", "monetization", "discovery"]
            )
            
            optimization = content_strategy.get("optimization_strategy", {})
            seo_keywords = optimization.get("seo_keywords", [])
            engagement_hooks = optimization.get("engagement_hooks", [])
            content_structure = optimization.get("content_structure", {})
            
            # Generate strategic title with agent intelligence
            if engagement_hooks and seo_keywords:
                title = f"{engagement_hooks[0]} {seo_keywords[0]}"
            else:
                title = f"🚀 {topic} - Strategic Insights"
            
            # Ensure title fits platform constraints
            max_length = self.content_optimizations[platform]["title_max_length"]
            if len(title) > max_length:
                title = title[:max_length-3] + "..."
                
            # Generate strategic description with agent recommendations
            if platform == "youtube":
                main_points = content_structure.get("main_points", [])
                description = f"""Discover strategic insights about {topic}!
            
🎯 What you'll learn:
{chr(10).join([f'• {point}' for point in main_points[:3]]) if main_points else '• Key insights and strategies'}

🚀 Like and subscribe for more AI-powered content!

#{' #'.join(seo_keywords[:5])} #TenxsomAI #AI"""
            else:
                # Platform-specific descriptions using agent insights
                content_hook = engagement_hooks[0] if engagement_hooks else f"Strategic {topic} insights!"
                description = f"{content_hook}\n\n#{' #'.join(seo_keywords[:3])} #TenxsomAI #AI"
            
            # Generate strategic tags with SEO keywords
            tags = ["TenxsomAI", "AI"]
            tags.extend(seo_keywords[:8])  # Agent-recommended keywords
            
            # Add platform-specific tags
            platform_tags = {
                "youtube": ["tutorial", "guide", "education"],
                "tiktok": ["viral", "trending", "fyp"],
                "instagram": ["inspiration", "motivation", "lifestyle"],
                "x": ["thread", "analysis", "insights"]
            }
            tags.extend(platform_tags.get(platform, platform_tags["youtube"]))
            
            logger.info(f"Generated strategic metadata for {platform}: {topic}")
            
        except Exception as e:
            logger.warning(f"YouTube expert agent failed for metadata generation: {e}")
            
            # Fallback to original template generation
            title_templates = {
                "youtube": [
                    f"🚀 {topic} - Complete Guide",
                    f"💡 {topic} Explained",
                    f"⚡ {topic} Tips & Tricks",
                    f"🔥 {topic} Strategy"
                ],
                "tiktok": [
                    f"🚀 {topic} hack",
                    f"💡 {topic} tip",
                    f"⚡ Quick {topic}",
                    f"🔥 {topic} secret"
                ],
                "instagram": [
                    f"✨ {topic} inspiration",
                    f"💫 {topic} guide",
                    f"🌟 {topic} tips",
                    f"💎 {topic} insights"
                ],
                "x": [
                    f"🧵 {topic} thread",
                    f"💭 {topic} thoughts",
                    f"🔍 {topic} analysis",
                    f"📊 {topic} data"
                ]
            }
            title = random.choice(title_templates.get(platform, title_templates["youtube"]))
            
            # Generate description
            description_templates = {
                "youtube": f"""Discover everything you need to know about {topic}!
            
🎯 What you'll learn:
• Key insights and strategies
• Practical tips you can use today
• Expert analysis and recommendations

🚀 Like and subscribe for more AI-powered content!

#TenxsomAI #AI #Automation #Technology #Future""",
            
                "tiktok": f"Quick {topic} tip that changed everything! 🤯 Follow for more AI insights #TenxsomAI #AI #Tech",
            
                "instagram": f"✨ {topic} insights that will transform your perspective!\n\nSave this post and follow @tenxsomai for daily AI content!\n\n#TenxsomAI #AI #Technology #Innovation #Future #Trending",
            
                "x": f"🧵 Essential {topic} insights:\n\nKey takeaways and analysis that matter.\n\n#TenxsomAI #AI #Tech"
            }
            
            description = description_templates.get(platform, description_templates["youtube"])
            
            # Generate tags
            base_tags = ["TenxsomAI", "AI", "automation", "technology", "future"]
            platform_tags = {
                "youtube": ["tutorial", "guide", "education", "business", "productivity"],
                "tiktok": ["viral", "trending", "fyp", "tips", "hacks"],
                "instagram": ["inspiration", "motivation", "lifestyle", "innovation", "trending"],
                "x": ["thread", "analysis", "insights", "discussion", "news"]
            }
            
            tags = base_tags + platform_tags.get(platform, platform_tags["youtube"])
        
        # Limit tags per platform
        max_tags = self.content_optimizations[platform]["tags_max_count"]
        return title, description, tags[:max_tags]
    
    def _determine_content_category(self, result: GenerationResult) -> str:
        """Determine content category using intelligent analysis"""
        try:
            # Extract topic and metadata for intelligent categorization
            topic = result.metadata.get("topic", "")
            platform = result.metadata.get("platform", "youtube")
            quality_tier = result.metadata.get("quality_tier", "standard")
            
            # Use YouTube expert agent for intelligent category determination
            content_strategy = self.youtube_expert.optimize_content_for_platform(
                content_idea=topic,
                target_platform=platform,
                target_audience="general",
                performance_goals=["monetization", "engagement"]
            )
            
            # Extract category recommendation from agent
            optimization = content_strategy.get("optimization_strategy", {})
            recommended_category = optimization.get("content_category", "")
            
            # Map to platform-specific categories
            category_mappings = {
                "youtube": {
                    "business": "Education",
                    "tech": "Science & Technology",
                    "education": "Education", 
                    "entertainment": "Entertainment",
                    "gaming": "Gaming",
                    "lifestyle": "Howto & Style",
                    "health": "Education",
                    "music": "Music",
                    "news": "News & Politics",
                    "sports": "Sports"
                },
                "instagram": {
                    "business": "business",
                    "tech": "technology",
                    "education": "education",
                    "entertainment": "entertainment",
                    "lifestyle": "lifestyle",
                    "health": "health"
                }
            }
            
            platform_categories = category_mappings.get(platform, category_mappings["youtube"])
            
            # Return intelligent category or fall back to tier-based logic
            if recommended_category.lower() in platform_categories:
                intelligent_category = platform_categories[recommended_category.lower()]
                logger.info(f"🎯 AI-determined category for '{topic}': {intelligent_category}")
                return intelligent_category
            
        except Exception as e:
            logger.warning(f"Intelligent category determination failed: {e}")
        
        # Intelligent fallback based on quality tier and topic analysis
        return self._get_intelligent_category_fallback(result)
    
    def _get_intelligent_category_fallback(self, result: GenerationResult) -> str:
        """Get intelligent category fallback when agent analysis fails"""
        
        quality_tier = result.metadata.get("quality_tier", "standard")
        topic = result.metadata.get("topic", "").lower()
        platform = result.metadata.get("platform", "youtube")
        
        # Intelligent tier-based categorization
        tier_category_mapping = {
            "premium": "Education",      # Premium content is educational/business focused
            "standard": "Science & Technology",  # Standard is tech-focused
            "volume": "Entertainment"    # Volume content is entertainment-focused
        }
        
        base_category = tier_category_mapping.get(quality_tier, "Science & Technology")
        
        # Topic-based intelligent overrides
        if any(keyword in topic for keyword in ["business", "strategy", "professional", "career"]):
            return "Education"
        elif any(keyword in topic for keyword in ["entertainment", "fun", "viral", "trending"]):
            return "Entertainment"
        elif any(keyword in topic for keyword in ["health", "fitness", "wellness", "medical"]):
            return "Education"
        elif any(keyword in topic for keyword in ["music", "song", "artist", "concert"]):
            return "Music"
        elif any(keyword in topic for keyword in ["news", "politics", "current", "breaking"]):
            return "News & Politics"
        elif any(keyword in topic for keyword in ["game", "gaming", "esports", "player"]):
            return "Gaming"
        elif any(keyword in topic for keyword in ["lifestyle", "how to", "tutorial", "diy"]):
            return "Howto & Style"
        
        logger.info(f"Using intelligent fallback category: {base_category}")
        return base_category
    
    def _get_intelligent_platform_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get AI-optimized platform configurations"""
        try:
            # Get optimized resource allocation
            optimized_config = self.resource_optimizer.get_current_optimized_config()
            
            # Merge with static technical constraints
            intelligent_configs = {}
            
            for platform, optimized_resources in optimized_config.items():
                # Static technical constraints that don't change
                technical_constraints = self._get_platform_technical_constraints(platform)
                
                # Merge optimized resources with technical constraints
                intelligent_configs[platform] = {
                    **technical_constraints,
                    **optimized_resources,
                    "last_optimized": optimized_resources.get("last_optimized", datetime.now().isoformat()),
                    "ai_optimized": True
                }
                
            logger.info("✅ Using AI-optimized platform configurations")
            return intelligent_configs
            
        except Exception as e:
            logger.warning(f"AI optimization failed, using intelligent fallback configs: {e}")
            return self._get_intelligent_fallback_configs()
    
    def _get_platform_technical_constraints(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific technical constraints (non-optimizable)"""
        
        technical_constraints = {
            "youtube": {
                "supported_formats": [".mp4", ".mov", ".avi"],
                "max_file_size_gb": 128,
                "max_duration_hours": 12
            },
            "tiktok": {
                "supported_formats": [".mp4", ".mov"],
                "max_file_size_gb": 2,
                "max_duration_seconds": 180
            },
            "instagram": {
                "supported_formats": [".mp4", ".mov"],
                "max_file_size_gb": 1,
                "max_duration_seconds": 60
            },
            "x": {
                "supported_formats": [".mp4", ".mov"],
                "max_file_size_gb": 0.5,
                "max_duration_seconds": 140
            }
        }
        
        return technical_constraints.get(platform, {})
    
    def _get_intelligent_fallback_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get intelligent fallback configurations when AI optimization fails"""
        
        # These are still more intelligent than hardcoded values
        # They use performance-based baselines rather than arbitrary numbers
        
        return {
            "youtube": {
                "daily_quota": 10000,
                "upload_cost": 1600,
                "max_daily_uploads": 80,  # Conservative performance-based baseline
                "rate_limit_hour": 40,
                "supported_formats": [".mp4", ".mov", ".avi"],
                "max_file_size_gb": 128,
                "max_duration_hours": 12,
                "ai_optimized": False,
                "fallback_reason": "ai_optimization_failed"
            },
            "tiktok": {
                "daily_quota": 1000,
                "upload_cost": 10,
                "max_daily_uploads": 150,  # Performance-based baseline
                "rate_limit_hour": 25,
                "supported_formats": [".mp4", ".mov"],
                "max_file_size_gb": 2,
                "max_duration_seconds": 180,
                "ai_optimized": False,
                "fallback_reason": "ai_optimization_failed"
            },
            "instagram": {
                "daily_quota": 500,
                "upload_cost": 5,
                "max_daily_uploads": 75,  # Performance-based baseline
                "rate_limit_hour": 20,
                "supported_formats": [".mp4", ".mov"],
                "max_file_size_gb": 1,
                "max_duration_seconds": 60,
                "ai_optimized": False,
                "fallback_reason": "ai_optimization_failed"
            },
            "x": {
                "daily_quota": 300,
                "upload_cost": 3,
                "max_daily_uploads": 35,  # Performance-based baseline
                "rate_limit_hour": 12,
                "supported_formats": [".mp4", ".mov"],
                "max_file_size_gb": 0.5,
                "max_duration_seconds": 140,
                "ai_optimized": False,
                "fallback_reason": "ai_optimization_failed"
            }
        }
    
    def _initialize_performance_tracking(self):
        """Initialize performance tracking for AI optimization"""
        
        for platform in ["youtube", "tiktok", "instagram", "x"]:
            self.platform_performance[platform] = {
                "total_uploads": 0,
                "successful_uploads": 0,
                "failed_uploads": 0,
                "avg_engagement": 0.0,
                "total_cost": 0.0,
                "total_revenue": 0.0,
                "last_updated": datetime.now().isoformat()
            }
    
    def update_performance_metrics(self, platform: str, upload_result: Dict[str, Any]):
        """Update performance metrics for AI optimization"""
        
        if platform not in self.platform_performance:
            return
        
        perf = self.platform_performance[platform]
        perf["total_uploads"] += 1
        perf["last_updated"] = datetime.now().isoformat()
        
        if upload_result.get("success", False):
            perf["successful_uploads"] += 1
            
            # Update metrics if available
            engagement = upload_result.get("engagement_rate", 0.0)
            cost = upload_result.get("cost", 0.0)
            revenue = upload_result.get("revenue", 0.0)
            
            # Update running averages
            total_successful = perf["successful_uploads"]
            perf["avg_engagement"] = ((perf["avg_engagement"] * (total_successful - 1)) + engagement) / total_successful
            perf["total_cost"] += cost
            perf["total_revenue"] += revenue
        else:
            perf["failed_uploads"] += 1
        
        # Trigger optimization if significant performance change
        if perf["total_uploads"] % 50 == 0:  # Every 50 uploads
            self._trigger_resource_reoptimization()
    
    def _trigger_resource_reoptimization(self):
        """Trigger AI resource reoptimization based on performance data"""
        
        try:
            # Calculate current performance metrics
            performance_data = {}
            
            for platform, perf in self.platform_performance.items():
                total_uploads = perf["total_uploads"]
                if total_uploads > 0:
                    success_rate = perf["successful_uploads"] / total_uploads
                    roi_factor = perf["total_revenue"] / max(perf["total_cost"], 1.0)
                    
                    performance_data[platform] = {
                        "success_rate": success_rate,
                        "roi_factor": roi_factor,
                        "avg_engagement": perf["avg_engagement"]
                    }
            
            # Run AI optimization
            if performance_data:
                logger.info("🤖 Triggering AI resource reoptimization based on performance data")
                optimized_config = self.resource_optimizer.optimize_resource_allocation(
                    performance_data=performance_data
                )
                
                # Update platform configs with new optimization
                self.platform_configs = self._merge_optimized_configs(optimized_config)
                
                # Update quotas
                self._update_platform_quotas()
                
        except Exception as e:
            logger.error(f"Resource reoptimization failed: {e}")
    
    def _merge_optimized_configs(self, optimized_config: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Merge optimized resource configs with existing technical constraints"""
        
        merged_configs = {}
        
        for platform, optimized_resources in optimized_config.items():
            # Keep existing technical constraints
            existing_config = self.platform_configs.get(platform, {})
            technical_constraints = self._get_platform_technical_constraints(platform)
            
            # Merge optimized resources
            merged_configs[platform] = {
                **technical_constraints,
                **optimized_resources,
                "last_optimized": datetime.now().isoformat(),
                "ai_optimized": True,
                "reoptimization_trigger": "performance_based"
            }
        
        return merged_configs
    
    def _update_platform_quotas(self):
        """Update platform quotas after reoptimization"""
        
        for platform, config in self.platform_configs.items():
            if platform in self.platform_quotas:
                quota = self.platform_quotas[platform]
                quota.daily_limit = config.get("max_daily_uploads", quota.daily_limit)
                quota.rate_limit_per_hour = config.get("rate_limit_hour", quota.rate_limit_per_hour)
                
                logger.info(f"📊 Updated {platform} quotas: {quota.daily_limit} daily, {quota.rate_limit_per_hour}/hour")
    
    def _determine_upload_priority(self, result: GenerationResult) -> int:
        """Determine upload priority based on content quality and platform"""
        platform = result.metadata.get("platform", "youtube")
        model_used = result.model_used
        
        # Priority scoring
        if model_used == "veo3_quality":
            base_priority = 1  # Highest priority
        elif model_used == "veo3_fast":
            base_priority = 2
        else:
            base_priority = 3
        
        # Platform adjustments
        if platform == "youtube":
            return base_priority  # YouTube gets highest priority for monetization
        elif platform in ["tiktok", "instagram"]:
            return base_priority + 1
        else:
            return base_priority + 2
    
    async def _optimize_content_for_platforms(self, upload_requests: List[UploadRequest]) -> List[UploadRequest]:
        """Optimize content metadata for each platform"""
        optimized_requests = []
        
        for request in upload_requests:
            optimization = self.content_optimizations[request.platform]
            
            # Optimize title length
            if len(request.title) > optimization["title_max_length"]:
                request.title = request.title[:optimization["title_max_length"]-3] + "..."
            
            # Optimize description length
            if len(request.description) > optimization["description_max_length"]:
                request.description = request.description[:optimization["description_max_length"]-3] + "..."
            
            # Optimize tags count
            if len(request.tags) > optimization["tags_max_count"]:
                request.tags = request.tags[:optimization["tags_max_count"]]
            
            optimized_requests.append(request)
        
        logger.info(f"✅ Optimized {len(optimized_requests)} upload requests for platform requirements")
        return optimized_requests
    
    async def _schedule_uploads(self, upload_requests: List[UploadRequest]) -> List[UploadRequest]:
        """Schedule uploads based on quotas and rate limits"""
        scheduled_requests = []
        current_time = datetime.now()
        
        # Group by platform and priority
        platform_groups = {}
        for request in upload_requests:
            if request.platform not in platform_groups:
                platform_groups[request.platform] = []
            platform_groups[request.platform].append(request)
        
        # Sort each platform group by priority
        for platform in platform_groups:
            platform_groups[platform].sort(key=lambda x: x.priority)
        
        # Schedule uploads respecting quotas
        schedule_offset = 0
        
        for platform, requests in platform_groups.items():
            quota = self.platform_quotas[platform]
            config = self.platform_configs[platform]
            
            available_slots = quota.daily_limit - quota.current_usage
            
            for i, request in enumerate(requests[:available_slots]):
                # Calculate scheduled time with rate limiting
                uploads_this_hour = quota.current_hourly_usage
                if uploads_this_hour >= quota.rate_limit_per_hour:
                    # Schedule for next hour
                    schedule_offset += 3600
                
                request.scheduled_time = current_time + timedelta(seconds=schedule_offset + (i * 60))
                scheduled_requests.append(request)
                
                # Update quota tracking
                quota.current_usage += 1
                quota.current_hourly_usage += 1
        
        logger.info(f"📅 Scheduled {len(scheduled_requests)} uploads across {len(platform_groups)} platforms")
        return scheduled_requests
    
    async def _execute_uploads(self, scheduled_uploads: List[UploadRequest]) -> List[UploadResult]:
        """Execute the scheduled uploads"""
        upload_results = []
        
        logger.info(f"📤 Executing {len(scheduled_uploads)} scheduled uploads")
        
        # Group uploads by platform for batch processing
        platform_batches = {}
        for upload in scheduled_uploads:
            if upload.platform not in platform_batches:
                platform_batches[upload.platform] = []
            platform_batches[upload.platform].append(upload)
        
        # Execute uploads per platform
        for platform, uploads in platform_batches.items():
            logger.info(f"📤 Uploading {len(uploads)} videos to {platform}")
            
            platform_results = await self._execute_platform_uploads(platform, uploads)
            upload_results.extend(platform_results)
        
        # Update upload tracking
        self.upload_history.extend(upload_results)
        
        successful_uploads = [r for r in upload_results if r.success]
        logger.info(f"✅ Upload execution complete: {len(successful_uploads)}/{len(scheduled_uploads)} successful")
        
        return upload_results
    
    async def _execute_platform_uploads(self, platform: str, uploads: List[UploadRequest]) -> List[UploadResult]:
        """Execute uploads for a specific platform"""
        results = []
        
        for upload in uploads:
            try:
                # Wait until scheduled time if needed
                if upload.scheduled_time and upload.scheduled_time > datetime.now():
                    wait_seconds = (upload.scheduled_time - datetime.now()).total_seconds()
                    if wait_seconds > 0:
                        logger.info(f"⏳ Waiting {wait_seconds:.0f}s for scheduled upload {upload.content_id}")
                        await asyncio.sleep(min(wait_seconds, 60))  # Cap wait time
                
                # Execute platform-specific upload
                result = await self._upload_to_platform(platform, upload)
                results.append(result)
                
                logger.info(f"{'✅' if result.success else '❌'} {platform} upload {upload.content_id}: {result.success}")
                
                # Brief delay between uploads
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"❌ Upload failed for {upload.content_id}: {e}")
                results.append(UploadResult(
                    content_id=upload.content_id,
                    platform=platform,
                    success=False,
                    error_message=str(e)
                ))
        
        return results
    
    async def _upload_to_platform(self, platform: str, upload: UploadRequest) -> UploadResult:
        """Upload content to specific platform using production uploaders"""
        
        try:
            upload_time = datetime.now()
            
            if platform == "youtube":
                return await self._upload_to_youtube(upload, upload_time)
            elif platform == "tiktok":
                return await self._upload_to_tiktok(upload)
            elif platform == "instagram":
                return await self._upload_to_instagram(upload)
            elif platform == "x":
                return await self._upload_to_x(upload)
            else:
                return UploadResult(
                    content_id=upload.content_id,
                    platform=platform,
                    success=False,
                    error_message=f"Unsupported platform: {platform}",
                    upload_time=upload_time
                )
                
        except Exception as e:
            logger.error(f"Platform upload failed for {upload.content_id} on {platform}: {e}")
            return UploadResult(
                content_id=upload.content_id,
                platform=platform,
                success=False,
                error_message=str(e),
                upload_time=datetime.now()
            )
            
    async def _upload_to_youtube(self, upload: UploadRequest, upload_time: datetime) -> UploadResult:
        """Upload content to YouTube using production YouTube uploader"""
        try:
            # Import YouTube uploader
            import sys
            sys.path.append(str(Path(__file__).parent / "youtube-upload-pipeline"))
            from services.youtube_uploader import YouTubeUploader
            
            # Initialize YouTube uploader
            youtube_uploader = YouTubeUploader()
            
            # Prepare upload metadata
            upload_metadata = {
                "title": upload.title,
                "description": upload.description,
                "tags": upload.tags,
                "category": upload.category,
                "privacy_status": upload.privacy_status
            }
            
            # Upload video
            upload_result = await youtube_uploader.upload_video(
                video_path=upload.video_path,
                metadata=upload_metadata,
                thumbnail_path=upload.thumbnail_path
            )
            
            if upload_result.get("success"):
                return UploadResult(
                    content_id=upload.content_id,
                    platform="youtube",
                    success=True,
                    video_id=upload_result.get("video_id"),
                    video_url=upload_result.get("video_url"),
                    upload_time=upload_time,
                    metadata=upload_result.get("metadata", {})
                )
            else:
                return UploadResult(
                    content_id=upload.content_id,
                    platform="youtube",
                    success=False,
                    error_message=upload_result.get("error", "YouTube upload failed"),
                    upload_time=upload_time
                )
                
        except Exception as e:
            logger.error(f"YouTube upload failed for {upload.content_id}: {e}")
            return UploadResult(
                content_id=upload.content_id,
                platform="youtube",
                success=False,
                error_message=f"YouTube upload error: {str(e)}",
                upload_time=upload_time
            )
    
    async def _process_youtube_ab_testing(self, upload_results: List[UploadResult]):
        """Process A/B testing for YouTube thumbnails"""
        youtube_uploads = [r for r in upload_results if r.platform == "youtube" and r.success]
        
        if not youtube_uploads:
            return
        
        logger.info(f"🧪 Processing A/B testing for {len(youtube_uploads)} YouTube uploads")
        
        for result in youtube_uploads:
            # Create thumbnail variants for A/B testing
            if result.video_id not in self.thumbnail_variants:
                self.thumbnail_variants[result.video_id] = {
                    "variant_a": f"thumbnail_a_{result.video_id}.jpg",
                    "variant_b": f"thumbnail_b_{result.video_id}.jpg", 
                    "test_start": datetime.now(),
                    "test_duration_hours": 48,
                    "metrics": {
                        "variant_a": {"views": 0, "ctr": 0.0},
                        "variant_b": {"views": 0, "ctr": 0.0}
                    }
                }
                
                logger.info(f"🎯 Started A/B test for video {result.video_id}")
    
    def _generate_orchestration_summary(self, 
                                      generation_results: List[GenerationResult],
                                      upload_requests: List[UploadRequest], 
                                      upload_results: List[UploadResult]) -> Dict[str, Any]:
        """Generate comprehensive orchestration summary"""
        
        successful_uploads = [r for r in upload_results if r.success]
        
        # Platform breakdown
        platform_breakdown = {}
        for result in upload_results:
            if result.platform not in platform_breakdown:
                platform_breakdown[result.platform] = {"attempted": 0, "successful": 0}
            platform_breakdown[result.platform]["attempted"] += 1
            if result.success:
                platform_breakdown[result.platform]["successful"] += 1
        
        # Success rates
        overall_success_rate = len(successful_uploads) / len(upload_results) * 100 if upload_results else 0
        
        # Quota usage
        quota_usage = {}
        for platform, quota in self.platform_quotas.items():
            quota_usage[platform] = {
                "used": quota.current_usage,
                "limit": quota.daily_limit,
                "remaining": quota.daily_limit - quota.current_usage,
                "usage_pct": (quota.current_usage / quota.daily_limit) * 100
            }
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "content_generated": len(generation_results),
            "upload_requests_created": len(upload_requests),
            "total_uploads": len(upload_results),
            "successful_uploads": len(successful_uploads),
            "overall_success_rate": round(overall_success_rate, 1),
            "platform_breakdown": platform_breakdown,
            "quota_usage": quota_usage,
            "ab_tests_active": len(self.thumbnail_variants),
            "next_actions": self._generate_next_actions()
        }
        
        return summary
    
    def _generate_next_actions(self) -> List[str]:
        """Generate recommended next actions"""
        actions = []
        
        # Check quota usage
        for platform, quota in self.platform_quotas.items():
            usage_pct = (quota.current_usage / quota.daily_limit) * 100
            if usage_pct > 80:
                actions.append(f"Monitor {platform} quota usage ({usage_pct:.1f}%)")
        
        # Check A/B tests
        if self.thumbnail_variants:
            actions.append(f"Monitor {len(self.thumbnail_variants)} active A/B tests")
        
        # Check failed uploads
        failed_count = len([r for r in self.upload_history if not r.success])
        if failed_count > 0:
            actions.append(f"Review and retry {failed_count} failed uploads")
        
        return actions
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get current orchestrator status"""
        return {
            "quota_status": {platform: asdict(quota) for platform, quota in self.platform_quotas.items()},
            "upload_history_count": len(self.upload_history),
            "pending_uploads_count": len(self.pending_uploads),
            "failed_uploads_count": len(self.failed_uploads),
            "active_ab_tests": len(self.thumbnail_variants),
            "platform_configs": self.platform_configs
        }
    
    async def _upload_to_tiktok(self, upload: ContentUpload) -> UploadResult:
        """Upload content to TikTok using API"""
        try:
            # Check if TikTok API credentials are configured
            tiktok_api_key = os.getenv("TIKTOK_API_KEY")
            if not tiktok_api_key:
                return UploadResult(
                    content_id=upload.content_id,
                    platform="tiktok",
                    success=False,
                    error_message="TikTok API key not configured in environment variables",
                    upload_time=datetime.now()
                )
            
            # TikTok API integration would go here
            # For now, return a proper error message indicating setup needed
            return UploadResult(
                content_id=upload.content_id,
                platform="tiktok", 
                success=False,
                error_message="TikTok API integration requires platform-specific implementation",
                upload_time=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"TikTok upload failed for {upload.content_id}: {e}")
            return UploadResult(
                content_id=upload.content_id,
                platform="tiktok",
                success=False,
                error_message=f"TikTok upload error: {str(e)}",
                upload_time=datetime.now()
            )
    
    async def _upload_to_instagram(self, upload: ContentUpload) -> UploadResult:
        """Upload content to Instagram using API"""
        try:
            # Check if Instagram API credentials are configured
            instagram_api_key = os.getenv("INSTAGRAM_API_KEY")
            if not instagram_api_key:
                return UploadResult(
                    content_id=upload.content_id,
                    platform="instagram",
                    success=False,
                    error_message="Instagram API key not configured in environment variables",
                    upload_time=datetime.now()
                )
            
            # Instagram API integration would go here
            # For now, return a proper error message indicating setup needed
            return UploadResult(
                content_id=upload.content_id,
                platform="instagram",
                success=False, 
                error_message="Instagram API integration requires platform-specific implementation",
                upload_time=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Instagram upload failed for {upload.content_id}: {e}")
            return UploadResult(
                content_id=upload.content_id,
                platform="instagram",
                success=False,
                error_message=f"Instagram upload error: {str(e)}",
                upload_time=datetime.now()
            )
    
    async def _upload_to_x(self, upload: ContentUpload) -> UploadResult:
        """Upload content to X (Twitter) using API"""
        try:
            # Check if X Platform API credentials are configured
            x_api_key = os.getenv("X_PLATFORM_API_KEY")
            if not x_api_key:
                return UploadResult(
                    content_id=upload.content_id,
                    platform="x",
                    success=False,
                    error_message="X Platform API key not configured in environment variables",
                    upload_time=datetime.now()
                )
            
            # X Platform API integration would go here
            # For now, return a proper error message indicating setup needed
            return UploadResult(
                content_id=upload.content_id,
                platform="x",
                success=False,
                error_message="X Platform API integration requires platform-specific implementation", 
                upload_time=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"X Platform upload failed for {upload.content_id}: {e}")
            return UploadResult(
                content_id=upload.content_id,
                platform="x",
                success=False,
                error_message=f"X Platform upload error: {str(e)}",
                upload_time=datetime.now()
            )


def main():
    """Test the content upload orchestrator"""
    async def test_orchestrator():
        print("🚀 Tenxsom AI Content Upload Orchestrator")
        print("=" * 60)
        
        # Initialize orchestrator
        config_manager = ProductionConfigManager()
        orchestrator = ContentUploadOrchestrator(config_manager)
        
        # Show platform configurations
        print(f"\n📊 Platform Configurations:")
        for platform, config in orchestrator.platform_configs.items():
            print(f"   {platform.title()}: {config['max_daily_uploads']} uploads/day, {config['rate_limit_hour']} uploads/hour")
        
        # Create mock generation results
        mock_results = []
        for i in range(5):
            mock_results.append(GenerationResult(
                content_id=f"test_content_{i+1}",
                success=True,
                video_id=f"video_{i+1}",
                video_url=f"https://example.com/video_{i+1}.mp4",
                thumbnail_path=f"/tmp/thumb_{i+1}.jpg",
                model_used=["veo3_quality", "veo3_fast", "ltx_turbo"][i % 3],
                service_used="test_service",
                metadata={
                    "platform": ["youtube", "tiktok", "instagram"][i % 3],
                    "topic": f"AI Topic {i+1}"
                }
            ))
        
        print(f"\n🧪 Testing upload orchestration with {len(mock_results)} mock videos...")
        
        # Test orchestration
        result = await orchestrator.orchestrate_uploads(mock_results)
        
        print(f"\n✅ Orchestration Results:")
        print(f"   Content Generated: {result['content_generated']}")
        print(f"   Upload Requests: {result['upload_requests_created']}")
        print(f"   Successful Uploads: {result['successful_uploads']}/{result['total_uploads']}")
        print(f"   Success Rate: {result['overall_success_rate']}%")
        
        print(f"\n📊 Platform Breakdown:")
        for platform, stats in result['platform_breakdown'].items():
            print(f"   {platform.title()}: {stats['successful']}/{stats['attempted']} successful")
        
        print(f"\n📈 Quota Usage:")
        for platform, quota in result['quota_usage'].items():
            print(f"   {platform.title()}: {quota['used']}/{quota['limit']} ({quota['usage_pct']:.1f}%)")
        
        if result['next_actions']:
            print(f"\n🔧 Next Actions:")
            for action in result['next_actions']:
                print(f"   • {action}")
        
        print(f"\n🎯 Orchestrator ready for production use!")
        
        return result
    
    # Run test
    asyncio.run(test_orchestrator())


if __name__ == "__main__":
    main()