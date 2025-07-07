#!/usr/bin/env python3
"""
Enhanced Tenxsom AI Flow Engine Job Producer
Production implementation using Google Cloud Tasks only
"""

import os
import sys
import asyncio
import argparse
import json
import logging
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from queue_manager import QueueManager, QueueType, create_queue_config

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FlowJobProducer:
    """Enhanced job producer for video generation workflows"""
    
    def __init__(self, queue_type: str = "cloud_tasks"):
        """
        Initialize job producer
        
        Args:
            queue_type: Must be cloud_tasks for production
        """
        self.queue_manager = None
        if queue_type.lower() not in ["cloud_tasks"]:
            logger.warning("Production only supports cloud_tasks queue type")
            queue_type = "cloud_tasks"
        self.queue_type = queue_type
        self.config = create_queue_config()
        
    async def initialize(self) -> bool:
        """Initialize the queue manager"""
        try:
            self.queue_manager = QueueManager(
                queue_type=self.queue_type,
                config=self.config
            )
            
            success = await self.queue_manager.initialize()
            if success:
                logger.info(f"✅ Queue initialized: {self.queue_manager.queue_type.value}")
                return True
            else:
                logger.error("❌ Failed to initialize queue")
                return False
                
        except Exception as e:
            logger.error(f"❌ Queue initialization error: {e}")
            return False
    
    async def submit_single_video_job(self, topic: str, duration: int = 5, 
                                    aspect_ratio: str = "16:9", 
                                    delay_seconds: int = 0) -> bool:
        """Submit single video generation job"""
        if not self.queue_manager or not self.queue_manager.is_initialized:
            logger.error("Queue not initialized")
            return False
        
        params = {
            "topic": topic,
            "duration": duration,
            "aspect_ratio": aspect_ratio
        }
        
        try:
            job_id = await self.queue_manager.enqueue_job(
                flow_name="youtube_production_flow",
                params=params,
                job_type="single",
                delay_seconds=delay_seconds
            )
            
            logger.info(f"✅ Single video job submitted: {job_id}")
            logger.info(f"   Topic: {topic}")
            logger.info(f"   Duration: {duration}s")
            logger.info(f"   Aspect Ratio: {aspect_ratio}")
            if delay_seconds > 0:
                logger.info(f"   Scheduled delay: {delay_seconds}s")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to submit single video job: {e}")
            return False
    
    async def submit_batch_video_jobs(self, topics: list, duration: int = 5,
                                    stagger_delay: int = 60) -> bool:
        """Submit batch video generation jobs"""
        if not self.queue_manager or not self.queue_manager.is_initialized:
            logger.error("Queue not initialized")
            return False
        
        jobs = []
        for i, topic in enumerate(topics):
            job = {
                "flow_name": "youtube_production_flow",
                "params": {
                    "topic": topic,
                    "duration": duration,
                    "aspect_ratio": "16:9"
                },
                "job_id": f"batch_video_{i+1:03d}"
            }
            jobs.append(job)
        
        try:
            task_ids = await self.queue_manager.enqueue_batch_jobs(
                jobs=jobs,
                delay_seconds=0  # Individual staggering handled by queue manager
            )
            
            logger.info(f"✅ Batch video jobs submitted: {len(task_ids)} jobs")
            logger.info(f"   Topics: {len(topics)} videos")
            logger.info(f"   Duration: {duration}s each")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to submit batch video jobs: {e}")
            return False
    
    async def schedule_daily_production(self, daily_topics: list, 
                                      videos_per_hour: int = 4) -> bool:
        """Schedule daily video production"""
        if not self.queue_manager or not self.queue_manager.is_initialized:
            logger.error("Queue not initialized")
            return False
        
        try:
            task_ids = await self.queue_manager.schedule_daily_production(
                daily_topics=daily_topics,
                videos_per_hour=videos_per_hour
            )
            
            hours_needed = len(daily_topics) / videos_per_hour
            
            logger.info(f"✅ Daily production scheduled: {len(task_ids)} videos")
            logger.info(f"   Rate: {videos_per_hour} videos/hour")
            logger.info(f"   Duration: {hours_needed:.1f} hours")
            logger.info(f"   Queue: {self.queue_manager.queue_type.value}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to schedule daily production: {e}")
            return False
    
    async def get_queue_status(self) -> dict:
        """Get current queue status and statistics"""
        if not self.queue_manager or not self.queue_manager.is_initialized:
            return {"error": "Queue not initialized"}
        
        return await self.queue_manager.get_queue_stats()
    
    async def update_rate_limits(self, max_per_second: int = None, 
                               max_concurrent: int = None) -> bool:
        """Update queue rate limits (Cloud Tasks only)"""
        if not self.queue_manager or not self.queue_manager.is_initialized:
            return False
        
        return await self.queue_manager.update_rate_limits(
            max_dispatches_per_second=max_per_second,
            max_concurrent_dispatches=max_concurrent
        )
    
    async def close(self):
        """Close queue connections"""
        if self.queue_manager:
            await self.queue_manager.close()

def create_output_directory():
    """Create output directory for reports"""
    output_dir = Path("flow_reports")
    output_dir.mkdir(exist_ok=True)
    return output_dir

async def handle_single_command(args):
    """Handle single video generation command"""
    producer = FlowJobProducer(queue_type=args.queue_type)
    
    if not await producer.initialize():
        logger.error("Failed to initialize job producer")
        return False
    
    try:
        success = await producer.submit_single_video_job(
            topic=args.topic,
            duration=args.duration,
            aspect_ratio=args.aspect_ratio,
            delay_seconds=getattr(args, 'delay', 0)
        )
        
        if success:
            # Show queue status
            stats = await producer.get_queue_status()
            logger.info(f"📊 Queue status: {json.dumps(stats, indent=2)}")
        
        return success
        
    finally:
        await producer.close()

async def handle_batch_command(args):
    """Handle batch video generation command"""
    producer = FlowJobProducer(queue_type=args.queue_type)
    
    if not await producer.initialize():
        logger.error("Failed to initialize job producer")
        return False
    
    try:
        # Read topics from file or use provided list
        if hasattr(args, 'topics_file') and args.topics_file:
            with open(args.topics_file, 'r') as f:
                topics = [line.strip() for line in f if line.strip()]
        else:
            topics = args.topics or ["Default AI Topic", "Tech Innovation Update"]
        
        success = await producer.submit_batch_video_jobs(
            topics=topics,
            duration=args.duration
        )
        
        if success:
            stats = await producer.get_queue_status()
            logger.info(f"📊 Queue status: {json.dumps(stats, indent=2)}")
        
        return success
        
    finally:
        await producer.close()

async def handle_schedule_command(args):
    """Handle scheduled production command"""
    producer = FlowJobProducer(queue_type=args.queue_type)
    
    if not await producer.initialize():
        logger.error("Failed to initialize job producer")
        return False
    
    try:
        # Generate daily topics or use provided list
        if hasattr(args, 'daily_topics') and args.daily_topics:
            topics = args.daily_topics
        else:
            # Generate default daily topics
            topics = [
                f"AI Technology Update {i+1}" for i in range(args.daily_count or 24)
            ]
        
        success = await producer.schedule_daily_production(
            daily_topics=topics,
            videos_per_hour=args.videos_per_hour or 4
        )
        
        if success:
            stats = await producer.get_queue_status()
            logger.info(f"📊 Queue status: {json.dumps(stats, indent=2)}")
        
        return success
        
    finally:
        await producer.close()

async def handle_status_command(args):
    """Handle queue status command"""
    producer = FlowJobProducer(queue_type=args.queue_type)
    
    if not await producer.initialize():
        logger.error("Failed to initialize job producer")
        return False
    
    try:
        stats = await producer.get_queue_status()
        
        print("\n" + "="*60)
        print("📊 QUEUE STATUS REPORT")
        print("="*60)
        print(json.dumps(stats, indent=2))
        print("="*60)
        
        return True
        
    finally:
        await producer.close()

def main():
    """Main entry point with enhanced command line interface"""
    parser = argparse.ArgumentParser(
        description='Enhanced Tenxsom AI Flow Engine Job Producer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single video production
  python run_flow_enhanced.py single --topic "AI Innovation 2025"
  
  # Batch videos from topics file
  python run_flow_enhanced.py batch --topics-file topics.txt
  
  # Schedule daily production
  python run_flow_enhanced.py schedule --daily-count 96 --videos-per-hour 4
  
  # Check queue status
  python run_flow_enhanced.py status
        """
    )
    
    # Global options
    parser.add_argument('--queue-type', 
                       choices=['cloud_tasks'],
                       default='cloud_tasks',
                       help='Queue type to use (production: cloud_tasks only)')
    parser.add_argument('--log-level',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO',
                       help='Logging level')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Single video command
    single_parser = subparsers.add_parser('single', help='Generate single video')
    single_parser.add_argument('--topic', required=True, help='Video topic')
    single_parser.add_argument('--duration', type=int, default=5, help='Video duration in seconds')
    single_parser.add_argument('--aspect-ratio', default='16:9', help='Video aspect ratio')
    single_parser.add_argument('--delay', type=int, default=0, help='Delay before processing (seconds)')
    
    # Batch video command
    batch_parser = subparsers.add_parser('batch', help='Generate batch videos')
    batch_parser.add_argument('--topics', nargs='+', help='List of video topics')
    batch_parser.add_argument('--topics-file', help='File containing topics (one per line)')
    batch_parser.add_argument('--duration', type=int, default=5, help='Video duration in seconds')
    
    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Schedule daily production')
    schedule_parser.add_argument('--daily-count', type=int, default=24, help='Number of videos per day')
    schedule_parser.add_argument('--videos-per-hour', type=int, default=4, help='Videos per hour rate')
    schedule_parser.add_argument('--daily-topics', nargs='+', help='Custom daily topics')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check queue status')
    
    args = parser.parse_args()
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    if not args.command:
        parser.print_help()
        return
    
    # Handle commands
    try:
        if args.command == 'single':
            success = asyncio.run(handle_single_command(args))
        elif args.command == 'batch':
            success = asyncio.run(handle_batch_command(args))
        elif args.command == 'schedule':
            success = asyncio.run(handle_schedule_command(args))
        elif args.command == 'status':
            success = asyncio.run(handle_status_command(args))
        else:
            logger.error(f"Unknown command: {args.command}")
            success = False
        
        if success:
            logger.info("✅ Command completed successfully")
        else:
            logger.error("❌ Command failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Operation cancelled by user")
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()