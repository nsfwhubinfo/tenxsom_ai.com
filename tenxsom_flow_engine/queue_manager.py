#!/usr/bin/env python3
"""
Queue Manager - Cloud Tasks Production Implementation
Unified interface for Google Cloud Tasks queue system
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class QueueType(Enum):
    """Production queue implementation"""
    CLOUD_TASKS = "cloud_tasks"

class QueueManager:
    """Production queue manager for Google Cloud Tasks"""
    
    def __init__(self, 
                 queue_type: Union[QueueType, str] = QueueType.CLOUD_TASKS,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize queue manager
        
        Args:
            queue_type: Must be cloud_tasks for production
            config: Optional configuration overrides
        """
        if isinstance(queue_type, str):
            if queue_type.lower() not in ["cloud_tasks"]:
                raise ValueError("Production only supports cloud_tasks queue type")
            queue_type = QueueType.CLOUD_TASKS
        
        self.queue_type = QueueType.CLOUD_TASKS
        self.config = config or {}
        self.queue_impl = None
        self.is_initialized = False
        
        # Load configuration
        self._load_config()
        
    def _load_config(self):
        """Load configuration from environment and config files"""
        # Environment variable override (force cloud_tasks)
        env_queue_type = os.getenv("TENXSOM_QUEUE_TYPE", "cloud_tasks").lower()
        if env_queue_type != "cloud_tasks":
            logger.warning(f"Production requires cloud_tasks, ignoring {env_queue_type}")
        
        # Production configuration
        self.default_config = {
            "cloud_tasks": {
                "project_id": None,  # Auto-detect
                "location": "us-central1",
                "queue_name": "tenxsom-video-generation",
                "max_dispatches_per_second": 10,
                "max_concurrent_dispatches": 5
            }
        }
        
        # Merge with provided config
        if "cloud_tasks" in self.config:
            self.default_config["cloud_tasks"].update(self.config["cloud_tasks"])
    
    async def initialize(self) -> bool:
        """Initialize Cloud Tasks queue implementation"""
        if self.is_initialized:
            return True
        
        logger.info("Initializing cloud_tasks queue...")
        
        try:
            await self._initialize_cloud_tasks()
            self.is_initialized = True
            logger.info("✅ cloud_tasks queue initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize cloud_tasks queue: {e}")
            raise RuntimeError(f"Production queue initialization failed: {e}")
    
    async def _initialize_cloud_tasks(self):
        """Initialize Cloud Tasks queue implementation"""
        try:
            from cloud_tasks_queue import CloudTasksQueue
            
            cloud_tasks_config = self.default_config["cloud_tasks"]
            self.queue_impl = CloudTasksQueue(
                project_id=cloud_tasks_config["project_id"],
                location=cloud_tasks_config["location"],
                queue_name=cloud_tasks_config["queue_name"]
            )
            
            # Initialize Cloud Tasks
            success = await self.queue_impl.initialize()
            if not success:
                raise RuntimeError("Cloud Tasks initialization failed")
                
        except ImportError:
            raise RuntimeError("Cloud Tasks dependencies not available - install google-cloud-tasks")
        except Exception as e:
            raise RuntimeError(f"Cloud Tasks initialization failed: {e}")
    
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
            delay_seconds: Delay before processing
            job_id: Optional custom job ID
            
        Returns:
            Task name/ID for tracking
        """
        if not self.is_initialized:
            raise RuntimeError("Queue not initialized")
        
        return await self.queue_impl.enqueue_job(
            flow_name=flow_name,
            params=params,
            job_type=job_type,
            delay_seconds=delay_seconds,
            job_id=job_id
        )
    
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
        if not self.is_initialized:
            raise RuntimeError("Queue not initialized")
        
        return await self.queue_impl.enqueue_batch_jobs(
            jobs=jobs,
            delay_seconds=delay_seconds
        )
    
    async def schedule_daily_production(self, 
                                      daily_topics: List[str],
                                      videos_per_hour: int = 4) -> List[str]:
        """
        Schedule daily video production with optimal timing
        
        Args:
            daily_topics: List of topics for video generation
            videos_per_hour: Rate of video generation
            
        Returns:
            List of scheduled task names/IDs
        """
        if not self.is_initialized:
            raise RuntimeError("Queue not initialized")
        
        return await self.queue_impl.schedule_daily_production(
            daily_topics=daily_topics,
            videos_per_hour=videos_per_hour
        )
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics and status"""
        if not self.is_initialized:
            raise RuntimeError("Queue not initialized")
        
        stats = await self.queue_impl.get_queue_stats()
        stats["queue_manager_type"] = self.queue_type.value
        return stats
    
    async def close(self):
        """Close queue connections"""
        if self.queue_impl:
            await self.queue_impl.close()
            logger.info("cloud_tasks queue closed")

def create_queue_config() -> Dict[str, Dict[str, Any]]:
    """Create queue configuration from environment variables"""
    return {
        "cloud_tasks": {
            "project_id": os.getenv("GOOGLE_CLOUD_PROJECT"),
            "location": os.getenv("CLOUD_TASKS_LOCATION", "us-central1"),
            "queue_name": os.getenv("CLOUD_TASKS_QUEUE", "tenxsom-video-generation"),
            "max_dispatches_per_second": int(os.getenv("CLOUD_TASKS_MAX_DISPATCHES", "10")),
            "max_concurrent_dispatches": int(os.getenv("CLOUD_TASKS_MAX_CONCURRENT", "5"))
        }
    }