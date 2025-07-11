#!/usr/bin/env python3

"""
Tenxsom AI Daily Content Generation Scheduler
Automated daily content generation with smart scheduling and resource optimization
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

# Import our components
from monetization_strategy_executor import MonetizationStrategyExecutor, ContentRequest
from production_config_manager import ProductionConfigManager
from intelligent_topic_generator import IntelligentTopicGenerator
from content_upload_orchestrator import ContentUploadOrchestrator
from agents.youtube_expert.main import YouTubePlatformExpert

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DailyContentScheduler:
    """
    Automated daily content generation scheduler with smart resource management
    
    Features:
    - Automated daily execution at optimal times
    - Resource optimization based on API limits
    - Failure recovery and retry mechanisms
    - Real-time monitoring and alerts
    - Performance analytics and reporting
    """
    
    def __init__(self, config_manager: ProductionConfigManager = None, mcp_enabled: bool = True):
        """Initialize the daily scheduler"""
        self.config = config_manager or ProductionConfigManager()
        self.executor = MonetizationStrategyExecutor(self.config)
        
        # Initialize intelligent topic generator
        self.topic_generator = IntelligentTopicGenerator(self.config)
        
        # Initialize MCP-enabled content orchestrator
        self.mcp_enabled = mcp_enabled
        if self.mcp_enabled:
            self.content_orchestrator = ContentUploadOrchestrator(
                config_manager=self.config,
                mcp_server_url="https://tenxsom-mcp-server-540103863590.us-central1.run.app"
            )
            self.youtube_expert = YouTubePlatformExpert()
            logger.info("✅ MCP integration enabled for template-based content generation")
        else:
            self.content_orchestrator = None
            self.youtube_expert = None
            logger.info("ℹ️ MCP integration disabled, using traditional generation methods")
        
        # Scheduling configuration with MCP template strategy
        self.execution_times = [
            "06:00",  # Morning batch - Premium content (Documentary, Cinematic)
            "10:00",  # Midday batch - Standard content (Explainer, Tech News)
            "14:00",  # Afternoon batch - Volume content (Shorts, ASMR)
            "18:00",  # Evening batch - Additional volume (Gaming, Viral)
            "22:00"   # Night batch - Volume content (Productivity, LoFi)
        ]
        
        # MCP Template tier distribution by time
        self.tier_distribution = {
            "06:00": {"premium": 0.6, "standard": 0.4, "volume": 0.0},
            "10:00": {"premium": 0.2, "standard": 0.6, "volume": 0.2},
            "14:00": {"premium": 0.1, "standard": 0.2, "volume": 0.7},
            "18:00": {"premium": 0.1, "standard": 0.2, "volume": 0.7},
            "22:00": {"premium": 0.0, "standard": 0.2, "volume": 0.8}
        }
        
        # Platform distribution strategy
        self.platform_distribution = {
            "06:00": {"youtube": 0.8, "youtube_shorts": 0.2},
            "10:00": {"youtube": 0.7, "youtube_shorts": 0.3},
            "14:00": {"youtube": 0.3, "youtube_shorts": 0.5, "tiktok": 0.2},
            "18:00": {"youtube": 0.2, "youtube_shorts": 0.5, "tiktok": 0.2, "instagram": 0.1},
            "22:00": {"youtube": 0.5, "youtube_shorts": 0.3, "instagram": 0.2}
        }
        
        # Resource management
        self.daily_limits = {
            "google_ultra_credits": 417,  # Daily allocation from 12,500 monthly
            "useapi_requests": 1000,      # Conservative daily limit
            "youtube_uploads": 100        # YouTube quota management
        }
        
        # Tracking
        self.daily_usage = {
            "google_ultra_credits": 0,
            "useapi_requests": 0,
            "youtube_uploads": 0,
            "videos_generated": 0,
            "videos_uploaded": 0
        }
        
        # State management
        self.scheduler_active = False
        self.current_execution = None
        self.execution_history = []
        
        # Error handling
        self.max_retries = 3
        self.retry_delays = [300, 900, 1800]  # 5min, 15min, 30min
        
    def start_scheduler(self):
        """Start the automated daily scheduler"""
        logger.info("🚀 Starting Tenxsom AI Daily Content Scheduler")
        
        self.scheduler_active = True
        logger.info(f"✅ Scheduler active with {len(self.execution_times)} daily execution times")
        
        # Start the scheduler loop
        self._run_scheduler()
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        logger.info("🔄 Scheduler loop started")
        
        try:
            while self.scheduler_active:
                current_time = datetime.now()
                current_time_str = current_time.strftime("%H:%M")
                
                # Check if current time matches any execution time
                if current_time_str in self.execution_times:
                    self._execute_scheduled_batch()
                
                # Check for midnight reset
                if current_time_str == "00:01":
                    self._reset_daily_usage()
                
                # Check for daily report
                if current_time_str == "23:45":
                    self._generate_daily_report()
                
                # Hourly health check
                if current_time.minute == 0:
                    self._health_check()
                
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("⚠️ Scheduler interrupted by user")
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")
        finally:
            self.stop_scheduler()
    
    def stop_scheduler(self):
        """Stop the scheduler gracefully"""
        logger.info("🛑 Stopping scheduler...")
        self.scheduler_active = False
        logger.info("✅ Scheduler stopped")
    
    def _execute_scheduled_batch(self):
        """Execute a scheduled content generation batch"""
        execution_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"🚀 Starting scheduled batch execution: {execution_id}")
        
        try:
            # Run async execution in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self._execute_batch_with_retry(execution_id)
            )
            
            loop.close()
            
            # Track execution
            self.execution_history.append({
                "execution_id": execution_id,
                "timestamp": datetime.now().isoformat(),
                "result": result,
                "success": result.get("success", False)
            })
            
            logger.info(f"✅ Batch execution completed: {execution_id}")
            
        except Exception as e:
            logger.error(f"❌ Batch execution failed: {execution_id} - {e}")
            self._send_alert(f"Batch execution failed: {execution_id}", str(e))
    
    async def _execute_batch_with_retry(self, execution_id: str) -> Dict[str, Any]:
        """Execute batch with retry mechanism"""
        
        for attempt in range(self.max_retries + 1):
            try:
                # Check resource availability
                if not self._check_resource_availability():
                    logger.warning(f"⚠️ Resource limits reached, skipping batch {execution_id}")
                    return {"success": False, "reason": "resource_limits_reached"}
                
                # Determine batch size based on time and resources
                batch_size = self._calculate_optimal_batch_size()
                
                # Generate batch content requests
                content_requests = self._generate_batch_requests(batch_size)
                
                # Execute the batch (MCP-enabled or traditional)
                if self.mcp_enabled:
                    result = await self._execute_mcp_content_batch(execution_id, batch_size)
                else:
                    result = await self._execute_content_batch(content_requests)
                
                # Update usage tracking
                self._update_usage_tracking(result)
                
                return {
                    "success": True,
                    "execution_id": execution_id,
                    "batch_size": batch_size,
                    "result": result,
                    "attempt": attempt + 1
                }
                
            except Exception as e:
                logger.error(f"❌ Batch execution attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries:
                    delay = self.retry_delays[attempt]
                    logger.info(f"⏳ Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"❌ All retry attempts exhausted for {execution_id}")
                    self._send_alert(f"Batch execution failed after {self.max_retries} retries", str(e))
                    
                    return {
                        "success": False,
                        "execution_id": execution_id,
                        "error": str(e),
                        "attempts": attempt + 1
                    }
    
    def _check_resource_availability(self) -> bool:
        """Check if resources are available for execution"""
        
        # Check Google Ultra credits
        if self.daily_usage["google_ultra_credits"] >= self.daily_limits["google_ultra_credits"]:
            logger.warning("⚠️ Google Ultra daily credit limit reached")
            return False
        
        # Check UseAPI requests
        if self.daily_usage["useapi_requests"] >= self.daily_limits["useapi_requests"]:
            logger.warning("⚠️ UseAPI daily request limit reached")
            return False
        
        # Check YouTube uploads
        if self.daily_usage["youtube_uploads"] >= self.daily_limits["youtube_uploads"]:
            logger.warning("⚠️ YouTube daily upload limit reached")
            return False
        
        return True
    
    def _calculate_optimal_batch_size(self) -> int:
        """Calculate optimal batch size based on current time and resources"""
        current_hour = datetime.now().hour
        
        # Resource-based batch sizing
        remaining_credits = self.daily_limits["google_ultra_credits"] - self.daily_usage["google_ultra_credits"]
        remaining_requests = self.daily_limits["useapi_requests"] - self.daily_usage["useapi_requests"]
        
        # Time-based batch sizing
        if 6 <= current_hour < 10:
            # Morning: Premium content focus
            base_size = min(8, remaining_credits // 100)  # Premium videos use 100 credits
        elif 10 <= current_hour < 14:
            # Midday: Standard content focus
            base_size = min(12, remaining_credits // 20)  # Standard videos use 20 credits
        elif 14 <= current_hour < 22:
            # Afternoon/Evening: Volume content focus
            base_size = min(20, remaining_requests // 5)  # Volume videos use minimal requests
        else:
            # Night: Light volume content
            base_size = min(10, remaining_requests // 3)
        
        return max(1, base_size)  # Ensure at least 1 video per batch
    
    def _generate_batch_requests(self, batch_size: int) -> List[ContentRequest]:
        """Generate content requests for the current batch"""
        current_time = datetime.now()
        
        # Determine content distribution based on time of day
        if 6 <= current_time.hour < 10:
            # Morning: 60% premium, 40% standard
            premium_count = int(batch_size * 0.6)
            standard_count = batch_size - premium_count
            volume_count = 0
        elif 10 <= current_time.hour < 14:
            # Midday: 20% premium, 60% standard, 20% volume
            premium_count = int(batch_size * 0.2)
            standard_count = int(batch_size * 0.6)
            volume_count = batch_size - premium_count - standard_count
        else:
            # Afternoon/Evening/Night: 10% premium, 20% standard, 70% volume
            premium_count = int(batch_size * 0.1)
            standard_count = int(batch_size * 0.2)
            volume_count = batch_size - premium_count - standard_count
        
        requests = []
        request_counter = 0
        
        # Generate premium requests
        for i in range(premium_count):
            requests.append(ContentRequest(
                content_id=f"premium_{current_time.strftime('%Y%m%d_%H%M')}_{i+1:02d}",
                platform="youtube",
                quality_tier="premium",
                topic=self._select_trending_topic("premium"),
                duration=30,
                scheduled_time=current_time + timedelta(minutes=i*5),
                priority=1
            ))
            request_counter += 1
        
        # Generate standard requests
        for i in range(standard_count):
            platform = ["youtube", "instagram", "tiktok"][i % 3]
            requests.append(ContentRequest(
                content_id=f"standard_{current_time.strftime('%Y%m%d_%H%M')}_{i+1:02d}",
                platform=platform,
                quality_tier="standard",
                topic=self._select_trending_topic("standard"),
                duration=20 if platform == "youtube" else 15,
                scheduled_time=current_time + timedelta(minutes=request_counter*3),
                priority=2
            ))
            request_counter += 1
        
        # Generate volume requests
        for i in range(volume_count):
            platform = ["tiktok", "instagram", "youtube"][i % 3]
            requests.append(ContentRequest(
                content_id=f"volume_{current_time.strftime('%Y%m%d_%H%M')}_{i+1:02d}",
                platform=platform,
                quality_tier="volume",
                topic=self._select_trending_topic("volume"),
                duration=15,
                scheduled_time=current_time + timedelta(minutes=request_counter*2),
                priority=3
            ))
            request_counter += 1
        
        logger.info(f"📋 Generated {len(requests)} content requests (P:{premium_count}, S:{standard_count}, V:{volume_count})")
        return requests
    
    def _select_trending_topic(self, tier: str) -> str:
        """Select AI-powered trending topic based on current trends, time context, and tier optimization"""
        current_hour = datetime.now().hour
        
        try:
            # Determine time-based content optimization
            time_context = self._get_time_context(current_hour)
            
            # Use intelligent topic generator for AI-powered selection
            topic_data = self.topic_generator.generate_trending_topics(
                count=1,
                quality_distribution={tier: 1},
                time_horizon=time_context["trend_horizon"]
            )
            
            if topic_data and len(topic_data) > 0:
                selected_topic = topic_data[0]["topic"]
                
                # Add time-based context optimization
                optimized_topic = self._optimize_topic_for_time(selected_topic, time_context, tier)
                
                logger.info(f"🎯 AI-generated topic for {tier} at {current_hour}:00 - {optimized_topic}")
                return optimized_topic
            else:
                logger.warning("No AI topics generated, using intelligent fallback")
                
        except Exception as e:
            logger.error(f"AI topic generation failed: {e}")
        
        # Intelligent fallback (not hardcoded templates)
        return self._get_intelligent_fallback_topic(tier, current_hour)
    
    def _get_time_context(self, hour: int) -> Dict[str, Any]:
        """Get intelligent time-based context for content optimization"""
        
        time_contexts = {
            "early_morning": {  # 5-8 AM
                "audience_state": "commuting_preparing",
                "content_focus": "productivity_motivation",
                "trend_horizon": "immediate",
                "engagement_type": "quick_consumption",
                "optimal_duration": "2-5_minutes"
            },
            "morning": {  # 8-12 PM
                "audience_state": "work_focused",
                "content_focus": "professional_development",
                "trend_horizon": "short_term",
                "engagement_type": "educational",
                "optimal_duration": "5-10_minutes"
            },
            "afternoon": {  # 12-17 PM
                "audience_state": "break_seeking",
                "content_focus": "entertainment_information",
                "trend_horizon": "short_term",
                "engagement_type": "engaging_informative",
                "optimal_duration": "3-8_minutes"
            },
            "evening": {  # 17-22 PM
                "audience_state": "relaxation_mode",
                "content_focus": "lifestyle_entertainment",
                "trend_horizon": "medium_term",
                "engagement_type": "entertaining",
                "optimal_duration": "5-15_minutes"
            },
            "night": {  # 22+ PM
                "audience_state": "wind_down",
                "content_focus": "light_entertainment",
                "trend_horizon": "long_term",
                "engagement_type": "relaxing",
                "optimal_duration": "2-10_minutes"
            }
        }
        
        if 5 <= hour < 8:
            return time_contexts["early_morning"]
        elif 8 <= hour < 12:
            return time_contexts["morning"]
        elif 12 <= hour < 17:
            return time_contexts["afternoon"]
        elif 17 <= hour < 22:
            return time_contexts["evening"]
        else:
            return time_contexts["night"]
    
    def _optimize_topic_for_time(self, topic: str, time_context: Dict[str, Any], tier: str) -> str:
        """Optimize topic based on time context and audience state"""
        
        content_focus = time_context["content_focus"]
        
        # Time-based topic optimization patterns
        optimization_patterns = {
            "productivity_motivation": {
                "premium": f"Morning Strategy: {topic}",
                "standard": f"Start Your Day: {topic}",
                "volume": f"Quick Morning: {topic}"
            },
            "professional_development": {
                "premium": f"Business Insight: {topic}",
                "standard": f"Professional Growth: {topic}",
                "volume": f"Career Tip: {topic}"
            },
            "entertainment_information": {
                "premium": f"Deep Dive: {topic}",
                "standard": f"Explore: {topic}",
                "volume": f"Quick Facts: {topic}"
            },
            "lifestyle_entertainment": {
                "premium": f"Lifestyle Analysis: {topic}",
                "standard": f"Life Enhancement: {topic}",
                "volume": f"Fun with: {topic}"
            },
            "light_entertainment": {
                "premium": f"Evening Insights: {topic}",
                "standard": f"Relax with: {topic}",
                "volume": f"Tonight's: {topic}"
            }
        }
        
        # Apply time-based optimization
        pattern = optimization_patterns.get(content_focus, {})
        optimized = pattern.get(tier, topic)
        
        return optimized
    
    def _get_intelligent_fallback_topic(self, tier: str, hour: int) -> str:
        """Get intelligent fallback topic when AI generation fails"""
        
        # Even fallbacks are context-aware and intelligent
        time_context = self._get_time_context(hour)
        content_focus = time_context["content_focus"]
        
        intelligent_fallbacks = {
            "productivity_motivation": {
                "premium": "Strategic morning productivity optimization",
                "standard": "Effective daily workflow enhancement",
                "volume": "Quick morning motivation boost"
            },
            "professional_development": {
                "premium": "Advanced business intelligence strategies",
                "standard": "Essential professional skill development",
                "volume": "Career advancement quick tips"
            },
            "entertainment_information": {
                "premium": "In-depth technology trend analysis",
                "standard": "Fascinating innovation discoveries",
                "volume": "Cool tech facts and insights"
            },
            "lifestyle_entertainment": {
                "premium": "Lifestyle optimization methodologies",
                "standard": "Life enhancement strategies",
                "volume": "Fun lifestyle improvements"
            },
            "light_entertainment": {
                "premium": "Evening reflection on innovation",
                "standard": "Relaxing technology insights",
                "volume": "Fun tech discoveries"
            }
        }
        
        fallback_topic = intelligent_fallbacks.get(content_focus, {}).get(
            tier, "Intelligent content optimization strategies"
        )
        
        logger.info(f"Using intelligent fallback topic: {fallback_topic}")
        return fallback_topic
    
    async def _execute_content_batch(self, content_requests: List[ContentRequest]) -> Dict[str, Any]:
        """Execute a batch of content generation requests"""
        logger.info(f"🎬 Executing batch of {len(content_requests)} content requests")
        
        # Use the monetization executor for actual generation
        generation_results = await self.executor._execute_content_generation(content_requests)
        upload_results = await self.executor._execute_content_upload(generation_results)
        
        # Calculate batch metrics
        successful_generations = [r for r in generation_results if r.success]
        
        batch_metrics = {
            "requests": len(content_requests),
            "generated": len(successful_generations),
            "uploaded": upload_results["upload_successes"],
            "generation_success_rate": len(successful_generations) / len(content_requests) * 100,
            "upload_success_rate": upload_results["upload_successes"] / len(successful_generations) * 100 if successful_generations else 0,
            "total_credits": sum(r.credits_used for r in successful_generations),
            "total_cost": sum(r.cost_usd for r in successful_generations),
            "execution_time": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Batch complete: {batch_metrics['generated']}/{batch_metrics['requests']} generated, {batch_metrics['uploaded']} uploaded")
        
        return {
            "metrics": batch_metrics,
            "generation_results": generation_results,
            "upload_results": upload_results
        }
    
    async def _execute_mcp_content_batch(self, execution_id: str, batch_size: int) -> Dict[str, Any]:
        """Execute MCP template-based content generation batch"""
        logger.info(f"🎬 Executing MCP-enabled batch {execution_id} with {batch_size} videos")
        
        # Get current time for tier/platform distribution
        current_time = datetime.now().strftime("%H:%M")
        
        # Generate topics using intelligent topic generator
        topics = await self._generate_strategic_topics(batch_size, current_time)
        
        # Determine content tiers based on time distribution
        content_tiers = self._distribute_content_tiers(batch_size, current_time)
        
        # Determine target platforms based on time distribution
        target_platforms = self._distribute_target_platforms(batch_size, current_time)
        
        logger.info(f"📋 Generated batch plan:")
        logger.info(f"   Topics: {len(topics)}")
        logger.info(f"   Tier distribution: {dict(zip(set(content_tiers), [content_tiers.count(t) for t in set(content_tiers)]))}")
        logger.info(f"   Platform distribution: {dict(zip(set(target_platforms), [target_platforms.count(p) for p in set(target_platforms)]))}")
        
        # Execute MCP content generation and upload orchestration
        try:
            mcp_result = await self.content_orchestrator.orchestrate_mcp_content_generation(
                topics=topics,
                content_tiers=content_tiers,
                target_platforms=target_platforms,
                batch_size=5  # Process in smaller concurrent batches
            )
            
            # Extract metrics from MCP result
            batch_metrics = {
                "requests": batch_size,
                "generated": mcp_result.get("successful_generations", 0),
                "uploaded": mcp_result.get("upload_orchestration", {}).get("successful_uploads", 0),
                "production_plans_generated": mcp_result.get("production_plans_generated", 0),
                "generation_success_rate": (mcp_result.get("successful_generations", 0) / batch_size) * 100,
                "upload_success_rate": self._calculate_upload_success_rate(mcp_result),
                "total_estimated_cost": mcp_result.get("estimated_total_cost", 0),
                "template_usage": mcp_result.get("template_usage", {}),
                "execution_time": datetime.now().isoformat(),
                "mcp_enabled": True
            }
            
            logger.info(f"✅ MCP Batch complete:")
            logger.info(f"   Production plans: {batch_metrics['production_plans_generated']}")
            logger.info(f"   Generated: {batch_metrics['generated']}/{batch_metrics['requests']}")
            logger.info(f"   Uploaded: {batch_metrics['uploaded']}")
            logger.info(f"   Estimated cost: ${batch_metrics['total_estimated_cost']:.2f}")
            
            return {
                "metrics": batch_metrics,
                "mcp_result": mcp_result,
                "topics_used": topics,
                "tiers_used": content_tiers,
                "platforms_used": target_platforms
            }
            
        except Exception as e:
            logger.error(f"❌ MCP batch execution failed: {e}")
            
            # Fallback to traditional generation if MCP fails
            logger.info("🔄 Falling back to traditional content generation")
            
            # Generate traditional content requests
            content_requests = self._generate_batch_requests(batch_size)
            traditional_result = await self._execute_content_batch(content_requests)
            
            # Mark as fallback
            traditional_result["metrics"]["mcp_fallback"] = True
            traditional_result["mcp_error"] = str(e)
            
            return traditional_result
    
    def _update_usage_tracking(self, batch_result: Dict[str, Any]):
        """Update daily usage tracking"""
        metrics = batch_result["metrics"]
        
        self.daily_usage["google_ultra_credits"] += metrics["total_credits"]
        self.daily_usage["useapi_requests"] += metrics["requests"]
        self.daily_usage["youtube_uploads"] += metrics["uploaded"]
        self.daily_usage["videos_generated"] += metrics["generated"]
        self.daily_usage["videos_uploaded"] += metrics["uploaded"]
        
        # Log usage status
        credits_pct = (self.daily_usage["google_ultra_credits"] / self.daily_limits["google_ultra_credits"]) * 100
        requests_pct = (self.daily_usage["useapi_requests"] / self.daily_limits["useapi_requests"]) * 100
        
        logger.info(f"📊 Daily usage: {self.daily_usage['videos_generated']} videos, {credits_pct:.1f}% credits, {requests_pct:.1f}% requests")
    
    def _reset_daily_usage(self):
        """Reset daily usage counters at midnight"""
        logger.info("🔄 Resetting daily usage counters")
        
        # Save yesterday's final stats
        yesterday_stats = {
            "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "final_usage": self.daily_usage.copy(),
            "execution_count": len(self.execution_history),
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to file
        stats_dir = Path(__file__).parent / "reports" / "daily_stats"
        stats_dir.mkdir(parents=True, exist_ok=True)
        
        stats_file = stats_dir / f"daily_stats_{yesterday_stats['date']}.json"
        with open(stats_file, 'w') as f:
            json.dump(yesterday_stats, f, indent=2)
        
        # Reset counters
        for key in self.daily_usage:
            self.daily_usage[key] = 0
        
        # Clear execution history
        self.execution_history = []
        
        logger.info(f"✅ Daily counters reset, yesterday's stats saved to {stats_file}")
    
    def _health_check(self):
        """Perform hourly health check"""
        current_time = datetime.now()
        
        # Check system health
        health_status = {
            "timestamp": current_time.isoformat(),
            "scheduler_active": self.scheduler_active,
            "daily_usage": self.daily_usage.copy(),
            "executions_today": len(self.execution_history),
            "last_execution": self.execution_history[-1] if self.execution_history else None,
            "resource_usage": {
                "credits_pct": (self.daily_usage["google_ultra_credits"] / self.daily_limits["google_ultra_credits"]) * 100,
                "requests_pct": (self.daily_usage["useapi_requests"] / self.daily_limits["useapi_requests"]) * 100,
                "uploads_pct": (self.daily_usage["youtube_uploads"] / self.daily_limits["youtube_uploads"]) * 100
            }
        }
        
        # Log health status
        logger.info(f"💊 Health check: {health_status['executions_today']} executions, {health_status['daily_usage']['videos_generated']} videos generated")
        
        # Check for issues
        if health_status["resource_usage"]["credits_pct"] > 90:
            logger.warning("⚠️ Google Ultra credits approaching daily limit")
        
        if health_status["resource_usage"]["requests_pct"] > 90:
            logger.warning("⚠️ UseAPI requests approaching daily limit")
        
        # Save health log
        health_dir = Path(__file__).parent / "logs" / "health"
        health_dir.mkdir(parents=True, exist_ok=True)
        
        health_file = health_dir / f"health_{current_time.strftime('%Y_%m_%d')}.jsonl"
        with open(health_file, 'a') as f:
            f.write(json.dumps(health_status) + '\n')
    
    def _generate_daily_report(self):
        """Generate comprehensive daily report"""
        logger.info("📊 Generating daily report...")
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Calculate daily performance
        successful_executions = [e for e in self.execution_history if e.get("success", False)]
        
        daily_report = {
            "date": current_date,
            "summary": {
                "total_executions": len(self.execution_history),
                "successful_executions": len(successful_executions),
                "videos_generated": self.daily_usage["videos_generated"],
                "videos_uploaded": self.daily_usage["videos_uploaded"],
                "success_rate": len(successful_executions) / len(self.execution_history) * 100 if self.execution_history else 0
            },
            "resource_usage": {
                "google_ultra_credits": self.daily_usage["google_ultra_credits"],
                "useapi_requests": self.daily_usage["useapi_requests"],
                "youtube_uploads": self.daily_usage["youtube_uploads"]
            },
            "target_progress": {
                "daily_target": 96,
                "achieved": self.daily_usage["videos_generated"],
                "percentage": (self.daily_usage["videos_generated"] / 96) * 100
            },
            "execution_history": self.execution_history,
            "report_timestamp": datetime.now().isoformat()
        }
        
        # Save daily report
        reports_dir = Path(__file__).parent / "reports" / "daily_scheduler"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = reports_dir / f"daily_report_{current_date}.json"
        with open(report_file, 'w') as f:
            json.dump(daily_report, f, indent=2)
        
        logger.info(f"📄 Daily report saved: {report_file}")
        logger.info(f"📈 Daily performance: {daily_report['summary']['videos_generated']}/96 videos ({daily_report['target_progress']['percentage']:.1f}%)")
    
    def _send_alert(self, title: str, message: str):
        """Send alert notification via multiple channels"""
        logger.error(f"🚨 ALERT: {title} - {message}")
        
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "message": message,
            "severity": "error"
        }
        
        # Save alert to file for audit trail
        alerts_dir = Path(__file__).parent / "logs" / "alerts"
        alerts_dir.mkdir(parents=True, exist_ok=True)
        
        alert_file = alerts_dir / f"alerts_{datetime.now().strftime('%Y_%m_%d')}.jsonl"
        with open(alert_file, 'a') as f:
            f.write(json.dumps(alert_data) + '\n')
        
        # Send Telegram notification if configured
        self._send_telegram_alert(title, message)
    
    def _send_telegram_alert(self, title: str, message: str):
        """Send alert via Telegram bot"""
        try:
            import requests
            
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            authorized_user_id = os.getenv('AUTHORIZED_USER_ID')
            
            if not bot_token or not authorized_user_id:
                logger.debug("Telegram credentials not configured, skipping notification")
                return
            
            alert_message = f"🚨 *TenxsomAI Alert*\n\n*{title}*\n\n{message}\n\n_Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
            
            telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": authorized_user_id,
                "text": alert_message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(telegram_url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Alert sent via Telegram")
            else:
                logger.warning(f"⚠️ Telegram alert failed: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to send Telegram alert: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        # Calculate next execution time
        current_time = datetime.now()
        next_execution = None
        
        for exec_time in self.execution_times:
            exec_datetime = datetime.strptime(exec_time, "%H:%M").replace(
                year=current_time.year, 
                month=current_time.month, 
                day=current_time.day
            )
            if exec_datetime > current_time:
                next_execution = exec_datetime
                break
        
        if not next_execution:
            # Next execution is tomorrow's first time
            tomorrow = current_time + timedelta(days=1)
            next_execution = datetime.strptime(self.execution_times[0], "%H:%M").replace(
                year=tomorrow.year,
                month=tomorrow.month, 
                day=tomorrow.day
            )
        
        return {
            "scheduler_active": self.scheduler_active,
            "daily_usage": self.daily_usage.copy(),
            "daily_limits": self.daily_limits.copy(),
            "execution_times": self.execution_times,
            "executions_today": len(self.execution_history),
            "last_execution": self.execution_history[-1] if self.execution_history else None,
            "next_scheduled": next_execution.isoformat() if next_execution else None
        }


    async def _generate_strategic_topics(self, batch_size: int, current_time: str) -> List[str]:
        """Generate strategic topics using intelligent topic generator and YouTube expert"""
        try:
            # Get time-based context
            time_context = self._get_time_context_string(current_time)
            
            # Generate base topics
            base_topics = await self.topic_generator.generate_topics(
                count=batch_size,
                time_context=time_context
            )
            
            # Enhance topics with YouTube expert insights if available
            if self.youtube_expert:
                enhanced_topics = []
                for topic in base_topics:
                    try:
                        # Get trending analysis for topic
                        trending_analysis = self.youtube_expert.monitor_trends()
                        opportunities = trending_analysis.get("opportunities", [])
                        
                        # Enhance topic based on trending opportunities
                        if opportunities:
                            top_opportunity = opportunities[0]
                            enhanced_topic = f"{topic} - {top_opportunity.get('keyword', topic)}"
                            enhanced_topics.append(enhanced_topic)
                        else:
                            enhanced_topics.append(topic)
                            
                    except Exception as e:
                        logger.warning(f"⚠️ YouTube expert enhancement failed for '{topic}': {e}")
                        enhanced_topics.append(topic)
                
                return enhanced_topics[:batch_size]
            
            return base_topics[:batch_size]
            
        except Exception as e:
            logger.error(f"❌ Strategic topic generation failed: {e}")
            # Fallback to simple topics
            return [f"AI Innovation Topic {i+1}" for i in range(batch_size)]
    
    def _distribute_content_tiers(self, batch_size: int, current_time: str) -> List[str]:
        """Distribute content across tiers based on time-based strategy"""
        distribution = self.tier_distribution.get(current_time, self.tier_distribution["14:00"])
        
        tiers = []
        premium_count = int(batch_size * distribution["premium"])
        standard_count = int(batch_size * distribution["standard"])
        volume_count = batch_size - premium_count - standard_count
        
        tiers.extend(["premium"] * premium_count)
        tiers.extend(["standard"] * standard_count)
        tiers.extend(["volume"] * volume_count)
        
        # Shuffle to avoid predictable patterns
        import random
        random.shuffle(tiers)
        
        return tiers
    
    def _distribute_target_platforms(self, batch_size: int, current_time: str) -> List[str]:
        """Distribute content across platforms based on time-based strategy"""
        distribution = self.platform_distribution.get(current_time, self.platform_distribution["14:00"])
        
        platforms = []
        for platform, ratio in distribution.items():
            count = int(batch_size * ratio)
            platforms.extend([platform] * count)
        
        # Fill any remaining slots with YouTube (default)
        while len(platforms) < batch_size:
            platforms.append("youtube")
        
        # Shuffle to avoid predictable patterns
        import random
        random.shuffle(platforms)
        
        return platforms[:batch_size]
    
    def _get_time_context_string(self, current_time: str) -> str:
        """Get contextual information based on current time string"""
        time_contexts = {
            "06:00": "morning_professional_content",
            "10:00": "midday_educational_content", 
            "14:00": "afternoon_entertainment_content",
            "18:00": "evening_viral_content",
            "22:00": "night_productivity_content"
        }
        
        return time_contexts.get(current_time, "general_content")
    
    def _calculate_upload_success_rate(self, mcp_result: Dict[str, Any]) -> float:
        """Calculate upload success rate from MCP result"""
        upload_orchestration = mcp_result.get("upload_orchestration", {})
        
        successful_uploads = upload_orchestration.get("successful_uploads", 0)
        total_uploads = upload_orchestration.get("total_uploads", 0)
        
        if total_uploads == 0:
            return 0.0
        
        return (successful_uploads / total_uploads) * 100
    
    async def get_mcp_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive MCP performance summary"""
        if not self.mcp_enabled or not self.content_orchestrator:
            return {"mcp_enabled": False, "error": "MCP integration not available"}
        
        try:
            # Get template performance analytics
            template_analytics = await self.content_orchestrator.get_mcp_template_performance_analytics()
            
            # Combine with execution history
            mcp_executions = [
                exec_hist for exec_hist in self.execution_history 
                if exec_hist.get("result", {}).get("metrics", {}).get("mcp_enabled")
            ]
            
            performance_summary = {
                "mcp_enabled": True,
                "template_analytics": template_analytics,
                "execution_count": len(mcp_executions),
                "total_videos_generated": sum(
                    exec_hist.get("result", {}).get("metrics", {}).get("generated", 0)
                    for exec_hist in mcp_executions
                ),
                "total_estimated_cost": sum(
                    exec_hist.get("result", {}).get("metrics", {}).get("total_estimated_cost", 0)
                    for exec_hist in mcp_executions
                ),
                "average_success_rate": sum(
                    exec_hist.get("result", {}).get("metrics", {}).get("generation_success_rate", 0)
                    for exec_hist in mcp_executions
                ) / len(mcp_executions) if mcp_executions else 0,
                "fallback_count": len([
                    exec_hist for exec_hist in mcp_executions
                    if exec_hist.get("result", {}).get("metrics", {}).get("mcp_fallback")
                ])
            }
            
            return performance_summary
            
        except Exception as e:
            logger.error(f"❌ Failed to get MCP performance summary: {e}")
            return {"mcp_enabled": True, "error": str(e)}


def main():
    """Main entry point for content scheduler"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Tenxsom AI Daily Content Scheduler")
    parser.add_argument("--daemon", action="store_true", help="Run in daemon mode")
    parser.add_argument("--production", action="store_true", help="Run in production mode with full logging")
    parser.add_argument("--test", action="store_true", help="Run test mode")
    parser.add_argument("--execute-batch", action="store_true", help="Execute single batch now")
    
    args = parser.parse_args()
    
    if args.daemon:
        # Daemon mode - run continuous scheduler
        if args.production:
            print("🚀 Starting Tenxsom AI Content Scheduler in PRODUCTION daemon mode")
            # Configure production logging
            import logging
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.StreamHandler(),
                    logging.FileHandler('/home/golde/tenxsom-ai-vertex/logs/scheduler_production.log')
                ]
            )
        else:
            print("🚀 Starting Tenxsom AI Content Scheduler in daemon mode")
            
        config_manager = ProductionConfigManager()
        scheduler = DailyContentScheduler(config_manager)
        
        try:
            scheduler.start_scheduler()
        except KeyboardInterrupt:
            print("\n⚠️ Scheduler stopped by user")
            scheduler.stop_scheduler()
        except Exception as e:
            print(f"\n❌ Scheduler error: {e}")
            scheduler.stop_scheduler()
            
    elif args.test:
        # Test mode - run diagnostics
        print("🚀 Tenxsom AI Daily Content Scheduler")
        print("=" * 60)
        
        # Initialize scheduler
        config_manager = ProductionConfigManager()
        scheduler = DailyContentScheduler(config_manager)
        
        # Show current status
        status = scheduler.get_status()
        print(f"\n📊 Scheduler Status:")
        print(f"   Daily target: 96 videos")
        print(f"   Execution times: {', '.join(status['execution_times'])}")
        print(f"   Resource limits: {status['daily_limits']}")
        
        # Test batch execution
        print(f"\n🧪 Testing single batch execution...")
        
        # Simulate batch execution
        batch_size = scheduler._calculate_optimal_batch_size()
        content_requests = scheduler._generate_batch_requests(batch_size)
        
        print(f"   Optimal batch size: {batch_size}")
        print(f"   Generated requests: {len(content_requests)}")
        
        # Show request breakdown
        premium_count = len([r for r in content_requests if r.quality_tier == "premium"])
        standard_count = len([r for r in content_requests if r.quality_tier == "standard"])
        volume_count = len([r for r in content_requests if r.quality_tier == "volume"])
        
        print(f"   Request breakdown: {premium_count} premium, {standard_count} standard, {volume_count} volume")
        
        print(f"\n✅ Scheduler ready for automated execution!")
        print(f"   To start daemon: python daily_content_scheduler.py --daemon")
        
    elif args.execute_batch:
        # Execute batch mode - run single batch now
        print("🚀 Executing Single Batch - Live Production Test")
        print("=" * 60)
        
        # Initialize scheduler
        config_manager = ProductionConfigManager()
        scheduler = DailyContentScheduler(config_manager)
        
        print(f"\n📊 Starting single batch execution...")
        print(f"   Target: YouTube videos for 30-day monetization plan")
        print(f"   Quality tiers: Premium/Standard/Volume mix")
        
        try:
            # Generate batch requests
            batch_size = scheduler._calculate_optimal_batch_size()
            content_requests = scheduler._generate_batch_requests(batch_size)
            
            print(f"\n📋 Generated {len(content_requests)} content requests")
            
            # Execute immediate batch
            import asyncio
            result = asyncio.run(scheduler._execute_content_batch(content_requests))
            
            print(f"\n✅ Batch execution completed!")
            print(f"   Results: {result}")
            
        except Exception as e:
            print(f"\n❌ Batch execution failed: {e}")
            import traceback
            traceback.print_exc()
        
    else:
        # Default: show help
        parser.print_help()


if __name__ == "__main__":
    main()