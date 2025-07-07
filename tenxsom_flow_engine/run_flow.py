#!/usr/bin/env python3
"""
Tenxsom AI Flow Engine Job Producer
Submits video generation jobs to Google Cloud Tasks for worker processing
"""

import os
import sys
import argparse
import asyncio
import logging
from typing import Dict, Any, List
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

# Global queue manager
queue_manager = None

def create_output_directory():
    """Create output directory for reports"""
    output_dir = Path("flow_reports")
    output_dir.mkdir(exist_ok=True)
    return output_dir

async def submit_job_to_queue(flow_name: str, params: dict, job_type: str = "single"):
    """Submit job to Cloud Tasks queue for worker processing"""
    global queue_manager
    
    if not queue_manager or not queue_manager.is_initialized:
        logger.error("Queue manager not initialized")
        return None

    try:
        job_id = await queue_manager.enqueue_job(
            flow_name=flow_name,
            params=params,
            job_type=job_type
        )
        
        logger.info(f"✅ Job submitted successfully: {job_id}")
        logger.info(f"   Flow: {flow_name}")
        logger.info(f"   Type: {job_type}")
        logger.info(f"   Params: {params}")
        
        return job_id
        
    except Exception as e:
        logger.error(f"❌ Failed to submit job: {e}")
        return None

async def single_video_flow(topic: str, duration: int = 5, aspect_ratio: str = "16:9"):
    """Generate a single video with specified parameters"""
    params = {
        "topic": topic,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"🎬 Starting single video generation")
    logger.info(f"   Topic: {topic}")
    logger.info(f"   Duration: {duration}s")
    logger.info(f"   Aspect Ratio: {aspect_ratio}")
    
    job_id = await submit_job_to_queue("youtube_production_flow", params, "single")
    return job_id

async def batch_video_flow(topics: List[str], duration: int = 5, aspect_ratio: str = "16:9"):
    """Generate multiple videos from a list of topics"""
    logger.info(f"🎬 Starting batch video generation for {len(topics)} topics")
    
    jobs = []
    for i, topic in enumerate(topics):
        params = {
            "topic": topic,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "batch_index": i,
            "batch_total": len(topics),
            "timestamp": datetime.now().isoformat()
        }
        jobs.append({
            "flow_name": "youtube_production_flow",
            "params": params
        })
    
    try:
        job_ids = await queue_manager.enqueue_batch_jobs(jobs)
        logger.info(f"✅ Batch submission successful: {len(job_ids)} jobs queued")
        return job_ids
        
    except Exception as e:
        logger.error(f"❌ Batch submission failed: {e}")
        return []

async def schedule_daily_production(daily_count: int = 96, videos_per_hour: int = 4):
    """Schedule daily video production with optimal timing"""
    # Generate topics for daily production
    topics = [f"AI Innovation Topic {i+1}" for i in range(daily_count)]
    
    logger.info(f"📅 Scheduling daily production")
    logger.info(f"   Videos: {daily_count}/day")
    logger.info(f"   Rate: {videos_per_hour}/hour")
    
    try:
        task_ids = await queue_manager.schedule_daily_production(
            daily_topics=topics,
            videos_per_hour=videos_per_hour
        )
        logger.info(f"✅ Daily production scheduled: {len(task_ids)} videos")
        return task_ids
        
    except Exception as e:
        logger.error(f"❌ Daily scheduling failed: {e}")
        return []

async def get_queue_status():
    """Get current queue status and statistics"""
    global queue_manager
    
    if not queue_manager or not queue_manager.is_initialized:
        logger.error("Queue manager not initialized")
        return None
    
    try:
        stats = await queue_manager.get_queue_stats()
        logger.info("📊 Queue Status:")
        logger.info(f"   Queue Type: {stats.get('queue_manager_type', 'unknown')}")
        logger.info(f"   Queue Name: {stats.get('queue_name', 'unknown')}")
        logger.info(f"   State: {stats.get('state', 'unknown')}")
        logger.info(f"   Tasks: {stats.get('approximate_task_count', 0)}")
        return stats
        
    except Exception as e:
        logger.error(f"❌ Failed to get queue status: {e}")
        return None

async def initialize_job_producer():
    """Initialize the job producer with Cloud Tasks"""
    global queue_manager
    
    try:
        # Create queue configuration
        config = create_queue_config()
        
        # Initialize queue manager (Cloud Tasks only)
        queue_manager = QueueManager(
            queue_type=QueueType.CLOUD_TASKS,
            config=config
        )
        
        # Initialize the queue
        success = await queue_manager.initialize()
        if not success:
            logger.error("❌ Failed to initialize queue")
            return False
        
        logger.info("✅ Job producer initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize job producer: {e}")
        return False

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Tenxsom AI Flow Engine Job Producer")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Single video command
    single_parser = subparsers.add_parser('single', help='Generate single video')
    single_parser.add_argument('--topic', required=True, help='Video topic')
    single_parser.add_argument('--duration', type=int, default=5, help='Video duration in seconds')
    single_parser.add_argument('--aspect-ratio', default='16:9', help='Aspect ratio')
    
    # Batch video command
    batch_parser = subparsers.add_parser('batch', help='Generate batch videos')
    batch_parser.add_argument('--topics', nargs='+', help='List of topics')
    batch_parser.add_argument('--topics-file', help='File containing topics (one per line)')
    batch_parser.add_argument('--duration', type=int, default=5, help='Video duration in seconds')
    batch_parser.add_argument('--aspect-ratio', default='16:9', help='Aspect ratio')
    
    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Schedule daily production')
    schedule_parser.add_argument('--daily-count', type=int, default=96, help='Videos per day')
    schedule_parser.add_argument('--videos-per-hour', type=int, default=4, help='Videos per hour')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check queue status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize job producer
    success = await initialize_job_producer()
    if not success:
        logger.error("Failed to initialize job producer")
        return
    
    try:
        # Execute command
        if args.command == 'single':
            await single_video_flow(
                topic=args.topic,
                duration=args.duration,
                aspect_ratio=args.aspect_ratio
            )
            
        elif args.command == 'batch':
            topics = []
            if args.topics:
                topics = args.topics
            elif args.topics_file:
                with open(args.topics_file, 'r') as f:
                    topics = [line.strip() for line in f if line.strip()]
            else:
                logger.error("Must provide either --topics or --topics-file")
                return
            
            await batch_video_flow(
                topics=topics,
                duration=args.duration,
                aspect_ratio=args.aspect_ratio
            )
            
        elif args.command == 'schedule':
            await schedule_daily_production(
                daily_count=args.daily_count,
                videos_per_hour=args.videos_per_hour
            )
            
        elif args.command == 'status':
            await get_queue_status()
            
    finally:
        # Clean up
        if queue_manager:
            await queue_manager.close()

if __name__ == "__main__":
    asyncio.run(main())