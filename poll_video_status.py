#!/usr/bin/env python3
"""
TenxSOM AI - Asynchronous Video Status Poller
This script checks the status of pending video generation jobs and downloads completed assets.
It is designed to be run periodically (e.g., every 1 minute via cron).
"""
import os
import json
import logging
import requests
from pathlib import Path
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("VideoPoller")

PENDING_JOBS_DIR = Path("pending_video_jobs")
COMPLETED_DIR = Path("generated_content/videos")
API_TOKEN = os.getenv('USEAPI_BEARER_TOKEN')
if not API_TOKEN:
    raise ValueError("HALT: USEAPI_BEARER_TOKEN environment variable not set")

def poll_pending_jobs():
    """Check all pending video jobs and process completed ones"""
    if not PENDING_JOBS_DIR.exists():
        logger.info("No pending jobs directory found. Nothing to poll.")
        return

    pending_files = list(PENDING_JOBS_DIR.glob("*.json"))
    if not pending_files:
        logger.info("No pending video jobs found.")
        return

    logger.info(f"🔍 Found {len(pending_files)} pending job(s). Checking status...")
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    for job_file in pending_files:
        try:
            with open(job_file, 'r') as f:
                job_data = json.load(f)

            logger.info(f"--- Checking job: {job_data['job_id']} for content '{job_data['content_id']}' ---")
            
            # Check job age - warn if job is very old
            submit_time = datetime.fromisoformat(job_data['submit_time'])
            age_minutes = (datetime.now() - submit_time).total_seconds() / 60
            logger.info(f"  📅 Job age: {age_minutes:.1f} minutes")
            
            if age_minutes > 30:  # Warn if job is older than 30 minutes
                logger.warning(f"  ⚠️  Job is quite old ({age_minutes:.1f} minutes). Consider checking manually.")
            
            # Fix endpoint format for LTX Studio - requires email prefix
            if 'ltxstudio' in job_data['status_endpoint']:
                # Extract job ID from endpoint
                job_uuid = job_data['job_id']
                # Reconstruct with correct format
                fixed_endpoint = f"https://api.useapi.net/v1/ltxstudio/assets/email:goldensonproperties@gmail.com-job:{job_uuid}-type:video"
                logger.info(f"  🔧 Fixed endpoint format for LTX Studio")
                response = requests.get(fixed_endpoint, headers=headers, timeout=15)
            else:
                response = requests.get(job_data['status_endpoint'], headers=headers, timeout=15)
            
            if response.status_code == 200:
                status_data = response.json()
                status_obj = status_data.get('status', {})
                job_status = status_obj.get('type', 'unknown')

                logger.info(f"  -> API Status: '{job_status}'")

                if job_status == 'completed':
                    logger.info("  🎉 Job complete! Downloading video asset...")
                    
                    # Extract video URL from artifact structure
                    artifact = status_obj.get('artifact', {})
                    video_url = artifact.get('assetUrl')
                    
                    if video_url:
                        logger.info(f"  📥 Downloading from: {video_url}")
                        video_response = requests.get(video_url, timeout=120)
                        
                        if video_response.status_code == 200:
                            video_path = Path(job_data['expected_file_path'])
                            video_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            with open(video_path, 'wb') as f:
                                f.write(video_response.content)
                            
                            file_size = video_path.stat().st_size
                            logger.info(f"  ✅ Download complete. Video saved to: {video_path} ({file_size:,} bytes)")
                            
                            # Create completion report
                            completion_report = {
                                **job_data,
                                "completion_time": datetime.now().isoformat(),
                                "final_file_path": str(video_path),
                                "file_size_bytes": file_size,
                                "status": "completed_successfully"
                            }
                            
                            report_path = video_path.parent / f"{job_data['content_id']}_completion_report.json"
                            with open(report_path, 'w') as f:
                                json.dump(completion_report, f, indent=2)
                            
                            logger.info(f"  📊 Completion report saved: {report_path}")
                            
                            # Remove from pending queue
                            job_file.unlink()
                            logger.info(f"  🧹 Removed job from pending queue")
                        else:
                            logger.error(f"  ❌ Video download failed with status {video_response.status_code}")
                    else:
                        logger.error("  ❌ Job completed but no assetUrl found in response.")
                        logger.debug(f"  📋 Full response: {json.dumps(status_data, indent=2)}")

                elif job_status == 'failed':
                    error_msg = status_obj.get('error', 'No error details provided')
                    logger.error(f"  ❌ Job failed. Error: {error_msg}")
                    
                    # Create failure report
                    failure_report = {
                        **job_data,
                        "failure_time": datetime.now().isoformat(),
                        "error": error_msg,
                        "status": "failed"
                    }
                    
                    failure_path = COMPLETED_DIR / f"{job_data['content_id']}_failure_report.json"
                    failure_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(failure_path, 'w') as f:
                        json.dump(failure_report, f, indent=2)
                    
                    logger.info(f"  📊 Failure report saved: {failure_path}")
                    
                    # Remove failed job from queue
                    job_file.unlink()
                    logger.info(f"  🧹 Removed failed job from pending queue")
                    
                elif job_status in ['processing', 'queued', 'running']:
                    logger.info(f"  ⏳ Job still {job_status}. Will check again later.")
                    
                else:
                    logger.warning(f"  ❓ Unknown status: '{job_status}'. Keeping in queue for now.")

            elif response.status_code == 404:
                logger.error(f"  ❌ Job not found (404). Removing from queue.")
                job_file.unlink()
                
            elif response.status_code in [522, 503, 504]:
                logger.warning(f"  ⚠️  API temporarily unavailable ({response.status_code}). Will retry later.")
                
            else:
                logger.warning(f"  ⚠️  Received unexpected status code: {response.status_code}")

        except requests.RequestException as e:
            logger.error(f"  ❌ API request failed for job: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"  ❌ Invalid job file format: {job_file}. Error: {e}")
        except Exception as e:
            logger.error(f"  ❌ Unexpected error processing job {job_file}: {e}")
        
        # Stagger requests to avoid rate limiting
        time.sleep(2)

def main():
    """Main polling function with basic error handling"""
    logger.info("🚀 Starting video status polling check...")
    
    try:
        poll_pending_jobs()
        logger.info("✅ Polling check completed successfully")
    except Exception as e:
        logger.error(f"💥 Polling check failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)