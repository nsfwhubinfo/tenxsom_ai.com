#!/usr/bin/env python3
"""
Tenxsom AI Production System Launch
Deploy the complete video generation and YouTube monetization pipeline
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from pathlib import Path
import sys
import os

# Add project paths
sys.path.append('/home/golde/tenxsom-ai-vertex')
sys.path.append('/home/golde/tenxsom-ai-vertex/integrations')
sys.path.append('/home/golde/tenxsom-ai-vertex/heygen-integration')

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TenxsomProductionLauncher:
    """Launch and manage the production video generation system"""
    
    def __init__(self):
        self.launch_time = datetime.now()
        self.generation_count = 0
        self.total_cost = 0.0
        self.success_rate = 0.0
        
        # Production configuration
        self.config = {
            "google_credentials": "/home/golde/.google-ai-ultra-credentials.json",
            "useapi_accounts": [
                {
                    "id": "primary",
                    "email": "goldensonproperties@gmail.com", 
                    "bearer_token": "user:1831-r8vA1WGayarXKuYwpT1PW",
                    "models": ["pixverse", "ltx-turbo"],
                    "priority": 1,
                    "credit_limit": 5000
                }
            ],
            "strategy": "youtube_monetization",
            "target_daily_videos": 96,
            "cost_target": 0.016  # $0.016 per video average
        }
        
    async def launch_system(self):
        """Launch the complete production system"""
        logger.info("🚀 LAUNCHING TENXSOM AI PRODUCTION SYSTEM")
        logger.info("="*60)
        
        # Initialize components
        logger.info("📡 Initializing system components...")
        
        try:
            # Initialize Enhanced Model Router
            from enhanced_model_router import EnhancedModelRouter, GenerationRequest, Platform, QualityTier
            
            self.router = EnhancedModelRouter(
                google_ultra_credentials=self.config["google_credentials"],
                useapi_accounts_config=self.config["useapi_accounts"],
                strategy=self.config["strategy"],
                enable_adaptive_failover=True
            )
            
            logger.info("✅ Enhanced Model Router initialized")
            
            # Initialize YouTube Narration Workflow
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "youtube_narration_workflow", 
                "/home/golde/tenxsom-ai-vertex/heygen-integration/youtube-narration-workflow.py"
            )
            youtube_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(youtube_module)
            
            self.narration = youtube_module.YouTubeNarrationWorkflow("user:1831-r8vA1WGayarXKuYwpT1PW")
            
            logger.info("✅ YouTube Narration Workflow initialized")
            
            # Start router
            await self.router.start()
            logger.info("✅ Model router started with adaptive failover")
            
            # Run initial system health check
            await self._system_health_check()
            
            # Start production pipeline
            await self._start_production_pipeline()
            
        except Exception as e:
            logger.error(f"❌ System launch failed: {e}")
            raise
    
    async def _system_health_check(self):
        """Perform comprehensive system health check"""
        logger.info("🏥 Performing system health check...")
        
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "google_ai_ultra": "unknown",
            "useapi_pixverse": "unknown", 
            "useapi_ltx_studio": "unknown",
            "heygen_tts": "unknown",
            "overall_health": "unknown"
        }
        
        # Check capacity
        try:
            capacity = await self.router.get_capacity_report()
            logger.info(f"📊 Daily Capacity: {capacity['total_daily_capacity']}")
            health_report["capacity"] = capacity["total_daily_capacity"]
        except Exception as e:
            logger.warning(f"⚠️ Capacity check failed: {e}")
        
        # Check 30-day strategy
        try:
            strategy = await self.router.optimize_for_30_day_strategy()
            logger.info(f"💰 30-day optimization: {strategy['cost_breakdown']['cost_per_video']:.4f} per video")
            health_report["strategy"] = strategy
        except Exception as e:
            logger.warning(f"⚠️ Strategy optimization failed: {e}")
        
        # Test endpoints (quick check)
        health_checks = {
            "pixverse": await self._test_pixverse_endpoint(),
            "ltx_studio": await self._test_ltx_studio_endpoint(),  
            "heygen_tts": await self._test_heygen_endpoint()
        }
        
        working_services = sum(1 for status in health_checks.values() if status)
        health_report["service_health"] = health_checks
        health_report["overall_health"] = "healthy" if working_services >= 2 else "degraded"
        
        logger.info(f"🎯 System Health: {health_report['overall_health'].upper()}")
        logger.info(f"📈 Working Services: {working_services}/3")
        
        return health_report
    
    async def _test_pixverse_endpoint(self) -> bool:
        """Quick test of Pixverse endpoint"""
        try:
            # Import here to avoid circular imports
            import aiohttp
            
            url = "https://api.useapi.net/v2/pixverse/videos/create-v4"
            headers = {"Authorization": f"Bearer {self.config['useapi_accounts'][0]['bearer_token']}"}
            
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=headers, json={"prompt": "test"}) as response:
                    # 400 is expected (bad request), 522 would be connection timeout
                    return response.status != 522
        except:
            return False
    
    async def _test_ltx_studio_endpoint(self) -> bool:
        """Quick test of LTX Studio endpoint"""
        try:
            import aiohttp
            
            url = "https://api.useapi.net/v1/ltxstudio/videos/ltx-create"
            headers = {"Authorization": f"Bearer {self.config['useapi_accounts'][0]['bearer_token']}"}
            
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=headers, json={"prompt": "test"}) as response:
                    return response.status != 522
        except:
            return False
    
    async def _test_heygen_endpoint(self) -> bool:
        """Quick test of HeyGen TTS endpoint"""
        try:
            import aiohttp
            
            url = "https://api.useapi.net/v1/heygen/tts/create"
            headers = {"Authorization": f"Bearer {self.config['useapi_accounts'][0]['bearer_token']}"}
            
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=headers, json={"text": "test"}) as response:
                    return response.status != 522
        except:
            return False
    
    async def _start_production_pipeline(self):
        """Start the production video generation pipeline"""
        logger.info("🎬 Starting production video generation pipeline...")
        
        # Sample content topics for initial generation
        test_topics = [
            {
                "topic": "AI Technology Trends 2025",
                "content_type": "educational",
                "platform": "youtube",
                "quality": "premium"
            },
            {
                "topic": "Quick Tech Tips for Productivity", 
                "content_type": "educational",
                "platform": "youtube",
                "quality": "standard"
            },
            {
                "topic": "Latest Gadget Reviews",
                "content_type": "commercial", 
                "platform": "youtube",
                "quality": "volume"
            }
        ]
        
        successful_generations = 0
        total_attempts = len(test_topics)
        
        for i, topic in enumerate(test_topics):
            logger.info(f"🎯 Generating video {i+1}/{total_attempts}: {topic['topic']}")
            
            try:
                # Generate video
                success = await self._generate_single_video(topic)
                if success:
                    successful_generations += 1
                    logger.info(f"✅ Video {i+1} generated successfully")
                else:
                    logger.warning(f"⚠️ Video {i+1} generation failed")
                
                # Small delay between generations
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Video {i+1} generation error: {e}")
        
        # Calculate success rate
        self.success_rate = (successful_generations / total_attempts) * 100
        
        logger.info("="*60)
        logger.info("🎉 PRODUCTION PIPELINE LAUNCH COMPLETE")
        logger.info(f"📊 Success Rate: {self.success_rate:.1f}% ({successful_generations}/{total_attempts})")
        logger.info(f"💰 Total Cost: ${self.total_cost:.4f}")
        logger.info(f"⏱️ Launch Duration: {(datetime.now() - self.launch_time).total_seconds():.1f}s")
        
        if self.success_rate >= 66:
            logger.info("🚀 SYSTEM READY FOR PRODUCTION SCALING!")
        else:
            logger.warning("⚠️ System needs optimization before full scaling")
    
    async def _generate_single_video(self, topic: dict) -> bool:
        """Generate a single video and narration"""
        try:
            # Import request classes
            from enhanced_model_router import GenerationRequest, Platform, QualityTier
            
            # Map quality to tier
            quality_map = {
                "premium": QualityTier.PREMIUM,
                "standard": QualityTier.STANDARD, 
                "volume": QualityTier.VOLUME
            }
            
            # Create generation request
            request = GenerationRequest(
                prompt=f"Professional video about {topic['topic']} with engaging visuals",
                platform=Platform.YOUTUBE,
                quality_tier=quality_map.get(topic['quality'], QualityTier.STANDARD),
                duration=5,
                aspect_ratio="16:9"
            )
            
            # Generate video
            start_time = time.time()
            response = await self.router.generate_video(request)
            generation_time = time.time() - start_time
            
            # Track costs
            self.total_cost += response.cost_usd
            self.generation_count += 1
            
            logger.info(f"   🎬 Video: {response.service_used}:{response.model_used} ({generation_time:.1f}s)")
            logger.info(f"   💰 Cost: ${response.cost_usd:.4f}")
            
            # Generate narration
            try:
                script = f"Welcome to our video about {topic['topic']}. This comprehensive guide will help you understand the key concepts and practical applications."
                
                narration_job = await self.narration.generate_narration(
                    script=script,
                    content_type=topic['content_type']
                )
                
                if narration_job.status == "completed":
                    logger.info(f"   🎤 Narration: {narration_job.voice_name} ({narration_job.duration}s)")
                else:
                    logger.warning(f"   ⚠️ Narration failed: {narration_job.status}")
            
            except Exception as e:
                logger.warning(f"   ⚠️ Narration error: {e}")
            
            return response.video_id is not None
            
        except Exception as e:
            logger.error(f"   ❌ Generation failed: {e}")
            return False
    
    async def shutdown(self):
        """Gracefully shutdown the system"""
        logger.info("🔄 Shutting down production system...")
        
        if hasattr(self, 'router'):
            await self.router.stop()
        
        logger.info("✅ System shutdown complete")

async def main():
    """Main launcher"""
    launcher = TenxsomProductionLauncher()
    
    try:
        await launcher.launch_system()
        
        # Keep system running for monitoring
        logger.info("🔄 System running... Press Ctrl+C to stop")
        
        # Run for 30 seconds to demonstrate operation
        await asyncio.sleep(30)
        
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown requested by user")
    except Exception as e:
        logger.error(f"💥 Critical system error: {e}")
    finally:
        await launcher.shutdown()

if __name__ == "__main__":
    asyncio.run(main())