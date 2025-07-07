#!/usr/bin/env python3
"""
Google Cloud Tasks Worker
Flask application to process video generation jobs from Cloud Tasks
Compatible interface with existing Redis worker
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from flow_framework import run as flow_run
from flows.youtube_production_flow import main_youtube_production_flow, batch_production_flow
from utils.history_processor import log_flow_history_as_json

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cloud_tasks_worker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create Flask app for Cloud Tasks webhook
app = Flask(__name__)

# Statistics tracking
worker_stats = {
    "jobs_processed": 0,
    "jobs_successful": 0,
    "jobs_failed": 0,
    "start_time": datetime.now().isoformat(),
    "last_job_time": None
}

async def process_video_job(job_payload: dict) -> dict:
    """
    Process a single video generation job (same logic as Redis worker)
    
    Args:
        job_payload: Job data from Cloud Tasks
        
    Returns:
        Processing result dictionary
    """
    job_id = job_payload.get("job_id", "unknown")
    flow_name = job_payload.get("flow_name")
    job_type = job_payload.get("job_type")
    params = job_payload.get("params", {})
    
    logger.info(f"Processing Cloud Tasks job {job_id}: {flow_name} ({job_type})")
    
    result = {
        "job_id": job_id,
        "status": "unknown",
        "processed_at": datetime.now().isoformat(),
        "execution_time": 0,
        "error": None
    }
    
    start_time = datetime.now()
    
    try:
        if flow_name == 'youtube_production_flow':
            # Single video production
            history = await flow_run(
                main_youtube_production_flow,
                topic=params.get("topic"),
                duration=params.get("duration", 5),
                aspect_ratio=params.get("aspect_ratio", "16:9")
            )
            
        elif flow_name == 'batch_production_flow':
            # Batch video production
            history = await flow_run(
                batch_production_flow,
                topics=params.get("topics", []),
                duration=params.get("duration", 5)
            )
            
        else:
            raise ValueError(f"Unknown flow name: {flow_name}")
        
        # Log structured results
        log_flow_history_as_json(history)
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        
        result.update({
            "status": "completed",
            "execution_time": execution_time,
            "flow_history_length": len(history) if history else 0
        })
        
        # Update stats
        worker_stats["jobs_successful"] += 1
        worker_stats["last_job_time"] = result["processed_at"]
        
        logger.info(f"Job {job_id} completed successfully in {execution_time:.2f}s")
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        error_msg = str(e)
        
        result.update({
            "status": "failed",
            "execution_time": execution_time,
            "error": error_msg
        })
        
        # Update stats
        worker_stats["jobs_failed"] += 1
        worker_stats["last_job_time"] = result["processed_at"]
        
        logger.error(f"Job {job_id} failed after {execution_time:.2f}s: {error_msg}")
    
    finally:
        worker_stats["jobs_processed"] += 1
    
    return result

@app.route('/process_video_job', methods=['POST'])
def handle_cloud_tasks_job():
    """
    Handle incoming Cloud Tasks webhook for video generation
    This is the endpoint that Cloud Tasks will call
    """
    try:
        # Get job payload from Cloud Tasks
        job_payload = request.get_json()
        
        if not job_payload:
            logger.error("No JSON payload received")
            return jsonify({"error": "No JSON payload"}), 400
        
        logger.info(f"Received Cloud Tasks job: {job_payload.get('job_id', 'unknown')}")
        
        # Process the job asynchronously
        result = asyncio.run(process_video_job(job_payload))
        
        # Return appropriate HTTP status
        if result["status"] == "completed":
            return jsonify(result), 200
        else:
            # Return 500 to trigger Cloud Tasks retry
            return jsonify(result), 500
            
    except BadRequest:
        logger.error("Invalid request format")
        return jsonify({"error": "Invalid request format"}), 400
    except Exception as e:
        logger.error(f"Unexpected error processing job: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Cloud Tasks worker"""
    return jsonify({
        "status": "healthy",
        "worker_type": "cloud_tasks",
        "stats": worker_stats,
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/stats', methods=['GET'])
def get_worker_stats():
    """Get worker statistics"""
    uptime_seconds = (datetime.now() - datetime.fromisoformat(worker_stats["start_time"])).total_seconds()
    
    enhanced_stats = worker_stats.copy()
    enhanced_stats.update({
        "uptime_seconds": uptime_seconds,
        "uptime_hours": uptime_seconds / 3600,
        "success_rate": (worker_stats["jobs_successful"] / max(1, worker_stats["jobs_processed"])) * 100,
        "failure_rate": (worker_stats["jobs_failed"] / max(1, worker_stats["jobs_processed"])) * 100
    })
    
    return jsonify(enhanced_stats), 200

@app.route('/shutdown', methods=['POST'])
def shutdown_worker():
    """Graceful shutdown endpoint"""
    logger.info("Shutdown requested via API")
    
    # In production, you'd want authentication for this endpoint
    shutdown_stats = worker_stats.copy()
    shutdown_stats["shutdown_time"] = datetime.now().isoformat()
    
    # Graceful shutdown
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        return jsonify({"error": "Not running with the Werkzeug Server"}), 500
    
    func()
    return jsonify({
        "message": "Cloud Tasks worker shutting down",
        "final_stats": shutdown_stats
    }), 200

class CloudTasksWorkerManager:
    """Manager class for Cloud Tasks worker - compatible with Redis worker interface"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.app = app
        
    def start(self):
        """Start the Cloud Tasks worker server"""
        logger.info("🚀 Starting Cloud Tasks Worker")
        logger.info(f"   Listening on {self.host}:{self.port}")
        logger.info(f"   Endpoint: /process_video_job")
        logger.info(f"   Health: /health")
        logger.info(f"   Stats: /stats")
        
        try:
            # Run Flask app
            self.app.run(
                host=self.host,
                port=self.port,
                debug=False,  # Production mode
                threaded=True  # Handle multiple requests
            )
        except KeyboardInterrupt:
            logger.info("Worker shutdown requested")
        except Exception as e:
            logger.error(f"Worker error: {e}")
            raise
    
    def stop(self):
        """Stop the worker (handled by Flask shutdown)"""
        logger.info("Cloud Tasks worker stopped")

def main():
    """Main entry point - compatible with Redis worker.py"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cloud Tasks Worker for Video Generation')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--log-level', default='INFO', help='Logging level')
    
    args = parser.parse_args()
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))
    
    # Create and start worker
    worker = CloudTasksWorkerManager(host=args.host, port=args.port)
    worker.start()

if __name__ == "__main__":
    main()