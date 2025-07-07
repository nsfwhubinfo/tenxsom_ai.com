#!/usr/bin/env python3
"""
Google Cloud Tasks Queue Implementation
Enhanced job queue for video generation with rate limiting and retry logic
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from google.cloud import tasks_v2
from google.auth.exceptions import DefaultCredentialsError
import os

logger = logging.getLogger(__name__)

class CloudTasksQueue:
    """Google Cloud Tasks queue implementation for video generation jobs"""
    
    def __init__(self, 
                 project_id: str = None,
                 location: str = "us-central1",
                 queue_name: str = "tenxsom-video-generation"):
        """
        Initialize Cloud Tasks queue
        
        Args:
            project_id: Google Cloud project ID (auto-detected if None)
            location: Google Cloud location for the queue
            queue_name: Name of the task queue
        """
        self.project_id = project_id or self._get_project_id()
        self.location = location
        self.queue_name = queue_name
        self.client = None
        self.queue_path = None
        
        # Queue configuration
        self.default_config = {
            "max_dispatches_per_second": 10,  # Rate limit for API quotas
            "max_concurrent_dispatches": 5,   # Concurrent video generations
            "max_retry_duration": "300s",     # 5 minutes max retry
            "min_backoff": "10s",             # Initial retry delay
            "max_backoff": "300s"             # Max retry delay
        }
        
    def _get_project_id(self) -> str:
        """Auto-detect Google Cloud project ID"""
        # Try environment variable first
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        if project_id:
            return project_id
            
        # Try from Google AI Ultra config
        try:
            google_creds_path = "/home/golde/.google-ai-ultra-credentials.json"
            if os.path.exists(google_creds_path):
                with open(google_creds_path, 'r') as f:
                    creds_data = json.load(f)
                    return creds_data.get("project_id", "tenxsom-ai-1631088")
        except Exception as e:
            logger.debug(f"Could not read Google credentials: {e}")
            
        # Default fallback
        return "tenxsom-ai-1631088"
    
    async def initialize(self) -> bool:
        """Initialize Cloud Tasks client and ensure queue exists"""
        try:
            # Initialize client
            self.client = tasks_v2.CloudTasksAsyncClient()
            
            # Construct queue path
            parent = f"projects/{self.project_id}/locations/{self.location}"
            self.queue_path = f"{parent}/queues/{self.queue_name}"
            
            # Check if queue exists, create if not
            await self._ensure_queue_exists()
            
            logger.info(f"Cloud Tasks queue initialized: {self.queue_path}")
            return True
            
        except DefaultCredentialsError:
            logger.warning("Google Cloud credentials not found - Cloud Tasks unavailable")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Cloud Tasks: {e}")
            return False
    
    async def _ensure_queue_exists(self):
        """Ensure the task queue exists, create if necessary"""
        try:
            # Try to get the queue
            await self.client.get_queue(name=self.queue_path)
            logger.debug(f"Queue {self.queue_name} already exists")
            
        except Exception as e:
            if "not found" in str(e).lower():
                logger.info(f"Queue {self.queue_name} not found, creating...")
                await self._create_queue()
            else:
                # Queue might exist but we lack permission to check
                logger.warning(f"Could not verify queue existence: {e}")
                logger.info("Assuming queue exists and proceeding...")
    
    async def _create_queue(self):
        """Create a new Cloud Tasks queue with production configuration"""
        try:
            parent = f"projects/{self.project_id}/locations/{self.location}"
            
            queue_config = {
                "name": self.queue_path,
                "rate_limits": {
                    "max_dispatches_per_second": self.default_config["max_dispatches_per_second"],
                    "max_concurrent_dispatches": self.default_config["max_concurrent_dispatches"]
                },
                "retry_config": {
                    "max_retry_duration": self.default_config["max_retry_duration"],
                    "min_backoff": self.default_config["min_backoff"],
                    "max_backoff": self.default_config["max_backoff"],
                    "max_attempts": 5
                }
            }
            
            request = tasks_v2.CreateQueueRequest(
                parent=parent,
                queue=queue_config
            )
            
            queue = await self.client.create_queue(request=request)
            logger.info(f"Created Cloud Tasks queue: {queue.name}")
            
        except Exception as e:
            logger.error(f"Failed to create queue: {e}")
            raise
    
    async def enqueue_job(self, 
                         flow_name: str,
                         params: Dict[str, Any],
                         job_type: str = "single",
                         delay_seconds: int = 0,
                         job_id: Optional[str] = None) -> str:
        """
        Enqueue a video generation job
        
        Args:
            flow_name: Name of the flow to execute
            params: Parameters for the flow
            job_type: Type of job (single, batch)
            delay_seconds: Delay before processing (for scheduling)
            job_id: Optional custom job ID
            
        Returns:
            Task name/ID for tracking
        """
        if not self.client:
            raise RuntimeError("Cloud Tasks not initialized")
        
        # Generate job ID if not provided
        if not job_id:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            job_id = f"video_gen_{timestamp}"
        
        # Create task payload
        task_payload = {
            "job_id": job_id,
            "flow_name": flow_name,
            "job_type": job_type,
            "params": params,
            "queued_at": datetime.now().isoformat(),
            "queue_type": "cloud_tasks"
        }
        
        # Create Cloud Tasks task with HTTP target
        # Use environment variable or default to local worker
        worker_url = os.getenv("CLOUD_TASKS_WORKER_URL", "http://localhost:8080/process_video_job")
        
        task = {
            "name": f"{self.queue_path}/tasks/{job_id}",
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": worker_url,
                "body": json.dumps(task_payload).encode(),
                "headers": {
                    "Content-Type": "application/json"
                }
            }
        }
        
        # Add scheduling if delay specified
        if delay_seconds > 0:
            eta = datetime.now() + timedelta(seconds=delay_seconds)
            task["schedule_time"] = eta
        
        # Create the task
        request = tasks_v2.CreateTaskRequest(
            parent=self.queue_path,
            task=task
        )
        
        try:
            response = await self.client.create_task(request=request)
            logger.info(f"Enqueued Cloud Tasks job: {job_id}")
            return response.name
            
        except Exception as e:
            logger.error(f"Failed to enqueue job {job_id}: {e}")
            raise
    
    async def enqueue_batch_jobs(self, 
                                jobs: List[Dict[str, Any]],
                                delay_seconds: int = 0) -> List[str]:
        """
        Enqueue multiple video generation jobs
        
        Args:
            jobs: List of job specifications
            delay_seconds: Delay before processing
            
        Returns:
            List of task names/IDs
        """
        task_names = []
        
        for i, job in enumerate(jobs):
            # Stagger batch jobs to respect rate limits
            job_delay = delay_seconds + (i * 2)  # 2 second intervals
            
            task_name = await self.enqueue_job(
                flow_name=job.get("flow_name", "youtube_production_flow"),
                params=job.get("params", {}),
                job_type="batch",
                delay_seconds=job_delay,
                job_id=job.get("job_id")
            )
            task_names.append(task_name)
            
        logger.info(f"Enqueued {len(jobs)} batch jobs with staggered delays")
        return task_names
    
    async def schedule_daily_production(self, 
                                      daily_topics: List[str],
                                      videos_per_hour: int = 4) -> List[str]:
        """
        Schedule daily video production with optimal timing
        
        Args:
            daily_topics: List of topics for video generation
            videos_per_hour: Rate of video generation
            
        Returns:
            List of scheduled task names
        """
        scheduled_tasks = []
        interval_seconds = 3600 // videos_per_hour  # Seconds between videos
        
        for i, topic in enumerate(daily_topics):
            delay = i * interval_seconds
            
            job_params = {
                "topic": topic,
                "duration": 5,
                "aspect_ratio": "16:9",
                "quality_tier": "standard"
            }
            
            task_name = await self.enqueue_job(
                flow_name="youtube_production_flow",
                params=job_params,
                delay_seconds=delay,
                job_id=f"daily_video_{i+1:03d}"
            )
            scheduled_tasks.append(task_name)
        
        logger.info(f"Scheduled {len(daily_topics)} videos over {len(daily_topics) // videos_per_hour} hours")
        return scheduled_tasks
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics and health information"""
        if not self.client:
            return {"error": "Cloud Tasks not initialized"}
        
        try:
            queue = await self.client.get_queue(name=self.queue_path)
            
            stats = {
                "queue_name": self.queue_name,
                "state": queue.state.name,
                "rate_limits": {
                    "max_dispatches_per_second": queue.rate_limits.max_dispatches_per_second,
                    "max_concurrent_dispatches": queue.rate_limits.max_concurrent_dispatches
                },
                "retry_config": {
                    "max_attempts": queue.retry_config.max_attempts,
                    "max_retry_duration": str(queue.retry_config.max_retry_duration),
                    "min_backoff": str(queue.retry_config.min_backoff),
                    "max_backoff": str(queue.retry_config.max_backoff)
                }
            }
            
            # Get task counts (requires additional API calls)
            try:
                # List tasks to get counts (limited sample)
                request = tasks_v2.ListTasksRequest(parent=self.queue_path, page_size=100)
                response = await self.client.list_tasks(request=request)
                
                task_count = len(list(response.tasks))
                stats["approximate_task_count"] = task_count
                
            except Exception as e:
                logger.debug(f"Could not get task count: {e}")
                stats["approximate_task_count"] = "unknown"
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get queue stats: {e}")
            return {"error": str(e)}
    
    async def update_queue_config(self, 
                                 max_dispatches_per_second: int = None,
                                 max_concurrent_dispatches: int = None) -> bool:
        """
        Update queue configuration for dynamic rate limiting
        
        Args:
            max_dispatches_per_second: New dispatch rate limit
            max_concurrent_dispatches: New concurrency limit
            
        Returns:
            True if successful
        """
        if not self.client:
            return False
        
        try:
            # Get current queue
            queue = await self.client.get_queue(name=self.queue_path)
            
            # Update rate limits if specified
            if max_dispatches_per_second is not None:
                queue.rate_limits.max_dispatches_per_second = max_dispatches_per_second
            if max_concurrent_dispatches is not None:
                queue.rate_limits.max_concurrent_dispatches = max_concurrent_dispatches
            
            # Update the queue
            update_request = tasks_v2.UpdateQueueRequest(queue=queue)
            await self.client.update_queue(request=update_request)
            
            logger.info(f"Updated queue config - dispatches/sec: {max_dispatches_per_second}, concurrent: {max_concurrent_dispatches}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update queue config: {e}")
            return False
    
    async def close(self):
        """Close the Cloud Tasks client"""
        if self.client:
            await self.client.transport.close()
            logger.debug("Cloud Tasks client closed")

