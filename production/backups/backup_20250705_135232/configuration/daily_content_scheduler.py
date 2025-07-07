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
    
    def __init__(self, config_manager: ProductionConfigManager = None):
        """Initialize the daily scheduler"""
        self.config = config_manager or ProductionConfigManager()
        self.executor = MonetizationStrategyExecutor(self.config)
        
        # Scheduling configuration
        self.execution_times = [
            "06:00",  # Morning batch - Premium content
            "10:00",  # Midday batch - Standard content  
            "14:00",  # Afternoon batch - Volume content
            "18:00",  # Evening batch - Additional volume
            "22:00"   # Night batch - Volume content
        ]
        
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
                
                # Execute the batch
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
        """Select trending topic based on current trends and tier"""
        import random
        
        # Time-aware topic selection
        current_hour = datetime.now().hour
        day_of_week = datetime.now().weekday()
        
        topics = {
            "premium": {
                "morning": ["AI productivity tools", "Remote work setup", "Business automation"],
                "afternoon": ["Market analysis", "Tech innovations", "Investment strategies"],
                "evening": ["Future of technology", "Industry insights", "Professional development"]
            },
            "standard": {
                "morning": ["Daily tech tips", "Workflow optimization", "Morning routines"],
                "afternoon": ["Social media strategies", "Creative inspiration", "Health breaks"],
                "evening": ["Evening productivity", "Skill development", "Entertainment tech"]
            },
            "volume": {
                "morning": ["Quick motivation", "Daily facts", "News highlights"],
                "afternoon": ["Life hacks", "Quick tips", "Trending topics"],
                "evening": ["Relaxation content", "Fun facts", "Light entertainment"]
            }
        }
        
        time_period = "morning" if current_hour < 12 else "afternoon" if current_hour < 18 else "evening"
        topic_list = topics.get(tier, topics["standard"]).get(time_period, ["General content"])
        
        return random.choice(topic_list)
    
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
        """Send alert notification (placeholder for actual notification system)"""
        logger.error(f"🚨 ALERT: {title} - {message}")
        
        # TODO: Implement actual notification system (email, Telegram, etc.)
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "message": message,
            "severity": "error"
        }
        
        # Save alert to file for now
        alerts_dir = Path(__file__).parent / "logs" / "alerts"
        alerts_dir.mkdir(parents=True, exist_ok=True)
        
        alert_file = alerts_dir / f"alerts_{datetime.now().strftime('%Y_%m_%d')}.jsonl"
        with open(alert_file, 'a') as f:
            f.write(json.dumps(alert_data) + '\n')
    
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


def main():
    """Test the daily content scheduler"""
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
    print(f"   To start: scheduler.start_scheduler()")
    print(f"   To stop: Ctrl+C or scheduler.stop_scheduler()")
    
    # Uncomment to start automated execution
    # scheduler.start_scheduler()


if __name__ == "__main__":
    main()