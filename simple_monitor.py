#!/usr/bin/env python3
"""
TenxSOM AI - Simple System Monitor
Lightweight monitoring without complex dependencies
"""

import time
import os
import subprocess
import json
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
)
logger = logging.getLogger("SimpleMonitor")

class SimpleSystemMonitor:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.pending_jobs_dir = self.base_dir / "pending_video_jobs"
        
    def check_pending_jobs(self):
        """Check status of pending video jobs"""
        if not self.pending_jobs_dir.exists():
            return {"count": 0, "jobs": []}
        
        job_files = list(self.pending_jobs_dir.glob("*.json"))
        jobs = []
        
        for job_file in job_files:
            try:
                with open(job_file, 'r') as f:
                    job_data = json.load(f)
                
                submit_time = datetime.fromisoformat(job_data['submit_time'])
                age_minutes = (datetime.now() - submit_time).total_seconds() / 60
                
                jobs.append({
                    "job_id": job_data['job_id'],
                    "content_id": job_data['content_id'],
                    "age_minutes": round(age_minutes, 1),
                    "title": job_data['title']
                })
            except Exception as e:
                logger.warning(f"Error reading job file {job_file}: {e}")
        
        return {"count": len(jobs), "jobs": jobs}
    
    def check_processes(self):
        """Check if TenxSOM processes are running"""
        processes = {}
        
        try:
            # Check for our processes
            result = subprocess.run(['pgrep', '-f', 'poll_video_status'], 
                                  capture_output=True, text=True)
            processes['video_poller'] = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            
            result = subprocess.run(['pgrep', '-f', 'central-controller'], 
                                  capture_output=True, text=True)
            processes['telegram_bot'] = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            
        except Exception as e:
            logger.warning(f"Error checking processes: {e}")
            
        return processes
    
    def check_api_health(self):
        """Check UseAPI.net connectivity"""
        try:
            import requests
            response = requests.get("https://api.useapi.net/health", timeout=10)
            return {"status": "healthy" if response.status_code == 200 else "unhealthy", 
                   "response_code": response.status_code}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def display_status(self):
        """Display current system status"""
        print("\n" + "="*60)
        print(f"🚀 TENXSOM AI SYSTEM STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # Check processes
        processes = self.check_processes()
        print("\n📊 RUNNING PROCESSES:")
        for name, count in processes.items():
            status = "🟢 RUNNING" if count > 0 else "🔴 STOPPED"
            print(f"   {name:<20}: {status} ({count} instances)")
        
        # Check pending jobs
        jobs_status = self.check_pending_jobs()
        print(f"\n🎬 VIDEO GENERATION QUEUE:")
        print(f"   Pending jobs: {jobs_status['count']}")
        
        if jobs_status['jobs']:
            print("   Recent jobs:")
            for job in jobs_status['jobs'][:5]:  # Show latest 5
                print(f"     • {job['content_id']} ({job['age_minutes']} min ago)")
        
        # Check API health
        api_health = self.check_api_health()
        print(f"\n🌐 API CONNECTIVITY:")
        print(f"   UseAPI.net: {api_health['status']}")
        
        print("\n🔗 MANAGEMENT COMMANDS:")
        print("   Generate video: python3 master_orchestrator_v3.py final_launch_job.json")
        print("   Check videos: python3 poll_video_status.py")
        print("   System status: python3 simple_monitor.py")
        
        print("\n💡 SYSTEM INFORMATION:")
        print(f"   Working directory: {self.base_dir}")
        print(f"   Environment: {'USEAPI_BEARER_TOKEN' in os.environ}")
        
    def monitor_loop(self, interval_seconds=30):
        """Run monitoring loop"""
        logger.info(f"🔍 Starting monitoring loop (interval: {interval_seconds}s)")
        
        try:
            while True:
                self.display_status()
                print(f"\n⏰ Next update in {interval_seconds} seconds... (Ctrl+C to stop)")
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            logger.info("Monitoring session ended")

def main():
    """Main function"""
    import sys
    
    monitor = SimpleSystemMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--loop":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        monitor.monitor_loop(interval)
    else:
        monitor.display_status()

if __name__ == "__main__":
    main()