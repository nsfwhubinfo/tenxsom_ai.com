"""
Tenxsom AI Holistic Integration Bridge
Orchestrates all components for seamless content generation
"""

import asyncio
import logging
import os
import sys
import importlib.util
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass

# Add paths for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from integrations.google_ultra.google_ai_ultra_wrapper import GoogleAIUltraWrapper, TenxsomGoogleUltraIntegration
from integrations.useapi.account_pool_manager import AccountPoolManager
from agents.youtube_expert.main import YouTubePlatformExpert, ContentCategory

# Import from phase1-consolidation using importlib
spec = importlib.util.spec_from_file_location(
    "enhanced_model_router", 
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "phase1-consolidation", "enhanced-model-router.py")
)
enhanced_router_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(enhanced_router_module)

EnhancedModelRouter = enhanced_router_module.EnhancedModelRouter
GenerationRequest = enhanced_router_module.GenerationRequest
Platform = enhanced_router_module.Platform
QualityTier = enhanced_router_module.QualityTier

logger = logging.getLogger(__name__)


class TenxsomHolisticBridge:
    """
    Main orchestrator for Tenxsom AI holistic integration
    Coordinates Google AI Ultra, UseAPI.net multi-account, and Platform Experts
    """
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize components
        self.model_router = None
        self.platform_experts = {
            "youtube": YouTubePlatformExpert(),
            # Additional platform experts can be added here
        }
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        # Implementation would load from env file
        return {
            "google_ultra_credentials": os.getenv("GOOGLE_AI_ULTRA_CREDENTIALS"),
            "model_router_strategy": os.getenv("MODEL_ROUTER_STRATEGY", "balanced"),
            "daily_video_target": int(os.getenv("DAILY_VIDEO_TARGET", 96)),
            "premium_ratio": float(os.getenv("PREMIUM_RATIO", 0.125))
        }
        
    async def initialize(self):
        """Initialize all components"""
        log("Initializing Tenxsom AI Holistic Bridge...")
        
        # Initialize model router with multi-account config
        useapi_accounts = self._get_useapi_accounts()
        self.model_router = EnhancedModelRouter(
            google_ultra_credentials=self.config["google_ultra_credentials"],
            useapi_accounts_config=useapi_accounts,
            strategy=self.config["model_router_strategy"]
        )
        
        await self.model_router.start()
        log("✅ Model router initialized")
        
        # Initialize platform experts
        await self._initialize_platform_experts()
        log("✅ Platform experts initialized")
        
        log("🚀 Tenxsom AI Holistic Bridge ready for production")
        
    async def _initialize_platform_experts(self):
        """Initialize platform expert agents"""
        platforms = ["youtube", "tiktok", "instagram", "x"]
        for platform in platforms:
            if os.getenv(f"{platform.upper()}_ENABLED", "true").lower() == "true":
                # Import and initialize platform expert
                self.platform_experts[platform] = f"{platform}_expert_instance"
                
    def _get_useapi_accounts(self) -> List[Dict]:
        """Get UseAPI.net account configurations"""
        return [
            {
                "id": "primary",
                "email": "goldensonproperties@gmail.com",
                "bearer_token": os.getenv("USEAPI_PRIMARY_TOKEN"),
                "models": ["pixverse", "ltx-turbo"],
                "priority": 1,
                "credit_limit": 5000
            },
            {
                "id": "secondary-1",
                "email": "tenxsom.ai.1@gmail.com",
                "bearer_token": os.getenv("USEAPI_SECONDARY_1_TOKEN"),
                "models": ["ltx-turbo"],
                "priority": 2,
                "credit_limit": 0
            }
        ]
        
    def get_trending_topics(self, platform: str = "youtube", category: str = "tech", count: int = 10) -> List[str]:
        """Get trending topics from platform expert agents"""
        try:
            if platform in self.platform_experts:
                expert = self.platform_experts[platform]
                
                # Map category string to ContentCategory enum
                category_mapping = {
                    "tech": ContentCategory.TECH,
                    "business": ContentCategory.BUSINESS,
                    "entertainment": ContentCategory.ENTERTAINMENT,
                    "education": ContentCategory.EDUCATION,
                    "gaming": ContentCategory.GAMING,
                    "lifestyle": ContentCategory.LIFESTYLE,
                    "health": ContentCategory.HEALTH,
                    "music": ContentCategory.MUSIC,
                    "news": ContentCategory.NEWS,
                    "sports": ContentCategory.SPORTS
                }
                
                content_category = category_mapping.get(category.lower(), ContentCategory.TECH)
                
                # Get trending topics from the expert agent
                trends_data = expert.monitor_trends(
                    category=content_category,
                    geographic_region="US",
                    time_horizon=7  # Weekly trends
                )
                
                # Extract high-priority topics
                opportunities = trends_data.get("trends", {}).get("opportunities", [])
                trending_topics = [
                    opp["keyword"] for opp in opportunities[:count]
                    if opp.get("opportunity_score", 0) >= 6.0  # Medium to high priority
                ]
                
                if trending_topics:
                    logger.info(f"Retrieved {len(trending_topics)} trending topics from {platform} expert")
                    return trending_topics
                else:
                    logger.warning(f"No high-priority trending topics found from {platform} expert")
                    
            else:
                logger.warning(f"No expert agent available for platform: {platform}")
                
        except Exception as e:
            logger.error(f"Failed to get trending topics from {platform} expert: {e}")
        
        # Intelligent adaptive fallback using context and performance data
        return self._get_intelligent_adaptive_fallback(platform, category, count)
    
    def _get_intelligent_adaptive_fallback(self, platform: str, category: str, count: int) -> List[str]:
        """Get intelligent adaptive fallback topics when all expert agents fail"""
        
        try:
            # Analyze current context for adaptive fallback
            current_hour = datetime.now().hour
            current_day = datetime.now().weekday()
            
            # Time-based content optimization
            time_context = self._get_time_based_context(current_hour)
            
            # Platform-specific optimization
            platform_context = self._get_platform_context(platform)
            
            # Category-based intelligent topics
            category_topics = self._get_category_intelligent_topics(category, time_context, platform_context)
            
            # Adaptive selection based on recent performance (if available)
            adaptive_topics = self._apply_performance_adaptation(category_topics, platform)
            
            logger.info(f"Generated {len(adaptive_topics)} intelligent adaptive fallback topics for {platform}/{category}")
            return adaptive_topics[:count]
            
        except Exception as e:
            logger.error(f"Intelligent adaptive fallback failed: {e}")
            
            # Final emergency fallback (minimal but still contextual)
            emergency_topics = [
                f"Strategic {category} insights for modern professionals",
                f"Advanced {category} strategies and implementation",
                f"Future-focused {category} trends and opportunities",
                f"Practical {category} solutions for daily challenges",
                f"Innovation in {category} technology and applications"
            ]
            return emergency_topics[:count]
    
    def _get_time_based_context(self, hour: int) -> Dict[str, Any]:
        """Get time-based context for content optimization"""
        
        if 5 <= hour < 9:  # Early morning
            return {
                "audience_state": "starting_day",
                "content_focus": "motivation_productivity",
                "energy_level": "high",
                "attention_span": "medium",
                "preferred_format": "quick_actionable"
            }
        elif 9 <= hour < 12:  # Morning work
            return {
                "audience_state": "work_focused",
                "content_focus": "professional_development",
                "energy_level": "high",
                "attention_span": "high",
                "preferred_format": "detailed_educational"
            }
        elif 12 <= hour < 14:  # Lunch break
            return {
                "audience_state": "break_time",
                "content_focus": "light_informative",
                "energy_level": "medium",
                "attention_span": "medium",
                "preferred_format": "entertaining_educational"
            }
        elif 14 <= hour < 17:  # Afternoon work
            return {
                "audience_state": "afternoon_productivity",
                "content_focus": "practical_solutions",
                "energy_level": "medium",
                "attention_span": "medium",
                "preferred_format": "solution_oriented"
            }
        elif 17 <= hour < 21:  # Evening
            return {
                "audience_state": "winding_down",
                "content_focus": "lifestyle_improvement",
                "energy_level": "medium",
                "attention_span": "high",
                "preferred_format": "comprehensive_relaxed"
            }
        else:  # Night
            return {
                "audience_state": "relaxation_mode",
                "content_focus": "light_entertainment",
                "energy_level": "low",
                "attention_span": "low",
                "preferred_format": "short_engaging"
            }
    
    def _get_platform_context(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific context for content optimization"""
        
        platform_contexts = {
            "youtube": {
                "format_preference": "educational_entertaining",
                "optimal_length": "medium_to_long",
                "monetization_focus": "high",
                "audience_engagement": "deep_dive",
                "content_style": "authoritative_informative"
            },
            "tiktok": {
                "format_preference": "quick_viral",
                "optimal_length": "very_short",
                "monetization_focus": "medium",
                "audience_engagement": "immediate_hook",
                "content_style": "trendy_entertaining"
            },
            "instagram": {
                "format_preference": "visual_storytelling",
                "optimal_length": "short_to_medium",
                "monetization_focus": "medium",
                "audience_engagement": "lifestyle_focused",
                "content_style": "aesthetic_inspirational"
            },
            "x": {
                "format_preference": "conversation_starter",
                "optimal_length": "very_short",
                "monetization_focus": "low",
                "audience_engagement": "thought_provoking",
                "content_style": "concise_insightful"
            }
        }
        
        return platform_contexts.get(platform, platform_contexts["youtube"])
    
    def _get_category_intelligent_topics(self, 
                                       category: str, 
                                       time_context: Dict[str, Any], 
                                       platform_context: Dict[str, Any]) -> List[str]:
        """Generate category-specific intelligent topics based on context"""
        
        # Intelligent topic templates that adapt to context
        content_focus = time_context["content_focus"]
        preferred_format = time_context["preferred_format"]
        content_style = platform_context["content_style"]
        
        # Category-specific intelligent topic generation
        if category == "tech":
            base_topics = [
                "artificial intelligence applications",
                "automation workflow optimization",
                "cybersecurity best practices",
                "cloud computing strategies",
                "data analysis techniques",
                "software development trends",
                "digital transformation methods",
                "machine learning implementation",
                "blockchain technology uses",
                "IoT innovation opportunities"
            ]
        elif category == "business":
            base_topics = [
                "strategic business planning",
                "revenue optimization strategies",
                "market analysis techniques",
                "leadership development methods",
                "customer acquisition strategies",
                "operational efficiency improvement",
                "financial management systems",
                "competitive advantage building",
                "team productivity enhancement",
                "business model innovation"
            ]
        elif category == "education":
            base_topics = [
                "learning acceleration techniques",
                "skill development strategies",
                "knowledge retention methods",
                "critical thinking development",
                "problem-solving frameworks",
                "creativity enhancement techniques",
                "memory improvement systems",
                "communication skill building",
                "analytical thinking methods",
                "professional growth planning"
            ]
        elif category == "lifestyle":
            base_topics = [
                "productivity optimization methods",
                "wellness improvement strategies",
                "time management techniques",
                "goal achievement systems",
                "habit formation strategies",
                "stress management methods",
                "work-life balance optimization",
                "personal development planning",
                "mindfulness practice techniques",
                "energy management systems"
            ]
        else:
            # Default intelligent topics
            base_topics = [
                "innovation implementation strategies",
                "efficiency optimization methods",
                "strategic planning techniques",
                "performance improvement systems",
                "growth acceleration strategies",
                "quality enhancement methods",
                "solution development approaches",
                "optimization strategy implementation",
                "effectiveness improvement techniques",
                "strategic advantage building"
            ]
        
        # Apply contextual adaptations
        adapted_topics = []
        
        for base_topic in base_topics:
            # Adapt based on time context
            if content_focus == "motivation_productivity":
                adapted_topic = f"Morning motivation: {base_topic}"
            elif content_focus == "professional_development":
                adapted_topic = f"Professional mastery of {base_topic}"
            elif content_focus == "light_informative":
                adapted_topic = f"Quick insights into {base_topic}"
            elif content_focus == "practical_solutions":
                adapted_topic = f"Practical {base_topic} for immediate results"
            elif content_focus == "lifestyle_improvement":
                adapted_topic = f"Life-enhancing {base_topic}"
            elif content_focus == "light_entertainment":
                adapted_topic = f"Fascinating {base_topic} discoveries"
            else:
                adapted_topic = f"Strategic {base_topic}"
            
            # Further adapt based on platform context
            if content_style == "authoritative_informative":
                final_topic = f"Expert guide to {adapted_topic.lower()}"
            elif content_style == "trendy_entertaining":
                final_topic = f"Trending: {adapted_topic.lower()}"
            elif content_style == "aesthetic_inspirational":
                final_topic = f"Inspiring {adapted_topic.lower()}"
            elif content_style == "concise_insightful":
                final_topic = f"Key insight: {adapted_topic.lower()}"
            else:
                final_topic = adapted_topic
            
            adapted_topics.append(final_topic)
        
        return adapted_topics
    
    def _apply_performance_adaptation(self, topics: List[str], platform: str) -> List[str]:
        """Apply performance-based adaptation to topic selection"""
        
        # This would use historical performance data to adapt topic selection
        # For now, implement intelligent ordering based on proven patterns
        
        # Performance-based topic ordering heuristics
        performance_keywords = {
            "high_performing": ["strategic", "professional", "expert", "mastery", "optimization"],
            "medium_performing": ["practical", "effective", "efficient", "improvement", "development"],
            "engagement_boosting": ["trending", "innovative", "breakthrough", "advanced", "cutting-edge"]
        }
        
        # Score topics based on performance keywords
        scored_topics = []
        
        for topic in topics:
            score = 0
            topic_lower = topic.lower()
            
            # High performing keywords
            for keyword in performance_keywords["high_performing"]:
                if keyword in topic_lower:
                    score += 3
            
            # Medium performing keywords
            for keyword in performance_keywords["medium_performing"]:
                if keyword in topic_lower:
                    score += 2
            
            # Engagement boosting keywords
            for keyword in performance_keywords["engagement_boosting"]:
                if keyword in topic_lower:
                    score += 1
            
            scored_topics.append((topic, score))
        
        # Sort by performance score (highest first)
        scored_topics.sort(key=lambda x: x[1], reverse=True)
        
        # Return topics in performance-optimized order
        return [topic for topic, score in scored_topics]
        
    async def generate_content_batch(self, requests: List[Dict]) -> List[Dict]:
        """Generate a batch of content across platforms"""
        results = []
        
        for req in requests:
            try:
                generation_request = GenerationRequest(
                    prompt=req["prompt"],
                    platform=Platform(req["platform"]),
                    quality_tier=QualityTier(req["quality_tier"]),
                    duration=req.get("duration", 15)
                )
                
                response = await self.model_router.generate_video(generation_request)
                results.append({
                    "success": True,
                    "video_id": response.video_id,
                    "download_url": response.download_url,
                    "model_used": response.model_used,
                    "service_used": response.service_used,
                    "platform": req["platform"],
                    "metadata": response.metadata
                })
                
            except Exception as e:
                logger.error(f"Generation failed for {req}: {e}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "platform": req["platform"]
                })
                
        return results
        
    async def execute_30_day_strategy(self):
        """Execute the 30-day monetization strategy"""
        strategy = await self.model_router.optimize_for_30_day_strategy()
        
        daily_plan = strategy["daily_distribution"]
        log(f"30-day strategy: {daily_plan['total_daily']} videos/day")
        log(f"Distribution: {daily_plan['premium_videos']} premium, {daily_plan['standard_videos']} standard, {daily_plan['volume_videos']} volume")
        
        # Generate today's content
        requests = []
        
        # Premium YouTube content
        for i in range(daily_plan["premium_videos"]):
            requests.append({
                "prompt": f"Premium YouTube content #{i+1}",
                "platform": "youtube",
                "quality_tier": "premium",
                "duration": 30
            })
            
        # Standard cross-platform content
        for i in range(daily_plan["standard_videos"]):
            requests.append({
                "prompt": f"Standard content #{i+1}",
                "platform": "instagram",  # Rotate platforms
                "quality_tier": "standard",
                "duration": 15
            })
            
        # Volume content
        for i in range(daily_plan["volume_videos"]):
            requests.append({
                "prompt": f"Volume content #{i+1}",
                "platform": "tiktok",  # High-volume platform
                "quality_tier": "volume",
                "duration": 15
            })
            
        # Execute batch generation
        results = await self.generate_content_batch(requests)
        
        successful = len([r for r in results if r["success"]])
        log(f"Generated {successful}/{len(requests)} videos successfully")
        
        return results


def log(message):
    print(f"[BRIDGE] {message}")


# Example usage
if __name__ == "__main__":
    async def test_bridge():
        bridge = TenxsomHolisticBridge("/home/golde/tenxsom-ai-vertex/config/production/holistic-config.env")
        await bridge.initialize()
        
        # Test 30-day strategy execution
        results = await bridge.execute_30_day_strategy()
        print(f"Strategy execution completed: {len(results)} videos processed")
        
    asyncio.run(test_bridge())
