#!/usr/bin/env python3
"""
TenxSOM AI - Complete System Launch
Launches the full production system including video generation, monitoring, and Telegram bot
"""

import os
import sys
import time
import subprocess
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
)
logger = logging.getLogger("SystemLauncher")

class TenxSOMSystemLauncher:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.processes = {}
        self.required_env_vars = [
            'USEAPI_BEARER_TOKEN',
            'TELEGRAM_BOT_TOKEN', 
            'AUTHORIZED_USER_ID'
        ]
        
    def check_environment(self):
        """Verify all required environment variables are set"""
        logger.info("🔍 Checking environment configuration...")
        
        missing_vars = []
        for var in self.required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            logger.info("💡 Set these environment variables before launching:")
            for var in missing_vars:
                logger.info(f"   export {var}=your_value_here")
            return False
        
        logger.info("✅ Environment configuration verified")
        return True
    
    def start_video_poller(self):
        """Start the asynchronous video status poller"""
        logger.info("🎬 Starting video status poller...")
        
        try:
            process = subprocess.Popen([
                sys.executable, 
                str(self.base_dir / "poll_video_status.py")
            ], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            env=os.environ.copy()
            )
            
            self.processes['video_poller'] = process
            logger.info(f"✅ Video poller started (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start video poller: {e}")
            return False
    
    def start_system_monitor(self):
        """Start the real-time system monitor"""
        logger.info("📊 Starting system monitor...")
        
        try:
            process = subprocess.Popen([
                sys.executable,
                str(self.base_dir / "realtime_system_monitor.py")
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy()
            )
            
            self.processes['system_monitor'] = process
            logger.info(f"✅ System monitor started (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start system monitor: {e}")
            return False
    
    def start_telegram_bot(self):
        """Start the Telegram bot controller"""
        logger.info("🤖 Starting Telegram bot...")
        
        try:
            process = subprocess.Popen([
                sys.executable,
                str(self.base_dir / "chatbot-integration" / "central-controller.py")
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(self.base_dir / "chatbot-integration"),
            env=os.environ.copy()
            )
            
            self.processes['telegram_bot'] = process
            logger.info(f"✅ Telegram bot started (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start Telegram bot: {e}")
            return False
    
    def check_process_health(self, process_name, process):
        """Check if a process is still running"""
        if process.poll() is None:
            return True
        else:
            stdout, stderr = process.communicate()
            logger.error(f"❌ {process_name} process died")
            if stderr:
                logger.error(f"   Error: {stderr.decode()}")
            return False
    
    def generate_test_video(self):
        """Generate a test video to verify the pipeline works"""
        logger.info("🎬 Generating test video to verify pipeline...")
        
        try:
            result = subprocess.run([
                sys.executable,
                str(self.base_dir / "master_orchestrator_v3.py"),
                str(self.base_dir / "final_launch_job.json")
            ], 
            capture_output=True, 
            text=True,
            env=os.environ.copy()
            )
            
            if result.returncode == 0:
                logger.info("✅ Test video generation initiated successfully")
                logger.info("📋 Check pending_video_jobs/ directory for job status")
                return True
            else:
                logger.error(f"❌ Test video generation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to generate test video: {e}")
            return False
    
    def display_system_status(self):
        """Display current system status"""
        logger.info("\n" + "="*60)
        logger.info("🚀 TENXSOM AI SYSTEM STATUS")
        logger.info("="*60)
        
        for name, process in self.processes.items():
            status = "🟢 RUNNING" if process.poll() is None else "🔴 STOPPED"
            pid = process.pid if process.poll() is None else "N/A"
            logger.info(f"   {name:<20}: {status} (PID: {pid})")
        
        # Display pending video jobs
        pending_jobs_dir = self.base_dir / "pending_video_jobs"
        if pending_jobs_dir.exists():
            pending_count = len(list(pending_jobs_dir.glob("*.json")))
            logger.info(f"   {'pending_videos':<20}: {pending_count} jobs in queue")
        
        logger.info("\n🔗 System URLs:")
        logger.info("   📊 Monitor Dashboard: Run 'python3 realtime_system_monitor.py'")
        logger.info("   🤖 Telegram Bot: Check your Telegram for @TenxsomAI_bot")
        logger.info("   🎬 Video Generation: Use 'python3 master_orchestrator_v3.py job.json'")
        
        logger.info("\n📋 Management Commands:")
        logger.info("   Check video status: python3 poll_video_status.py")
        logger.info("   Generate video: python3 master_orchestrator_v3.py final_launch_job.json")
        logger.info("   Stop system: pkill -f 'tenxsom|poll_video|realtime_system'")
        
    def launch_system(self):
        """Launch the complete TenxSOM AI system"""
        logger.info("🚀 LAUNCHING TENXSOM AI PRODUCTION SYSTEM")
        logger.info("="*60)
        
        # Check environment
        if not self.check_environment():
            return False
        
        # Launch core components
        components = [
            ("Video Poller", self.start_video_poller),
            ("System Monitor", self.start_system_monitor), 
            ("Telegram Bot", self.start_telegram_bot)
        ]
        
        failed_components = []
        for name, start_func in components:
            if not start_func():
                failed_components.append(name)
        
        if failed_components:
            logger.error(f"❌ Failed to start components: {failed_components}")
            return False
        
        # Wait for components to stabilize
        logger.info("⏳ Waiting for components to stabilize...")
        time.sleep(5)
        
        # Verify components are running
        all_healthy = True
        for name, process in self.processes.items():
            if not self.check_process_health(name, process):
                all_healthy = False
        
        if not all_healthy:
            logger.error("❌ Some components failed to start properly")
            return False
        
        # Generate test video
        if not self.generate_test_video():
            logger.warning("⚠️ Test video generation failed, but system is running")
        
        # Display status
        self.display_system_status()
        
        logger.info("\n🎉 TENXSOM AI SYSTEM LAUNCHED SUCCESSFULLY!")
        logger.info("💡 System is now running in background processes")
        logger.info("📊 Use 'python3 realtime_system_monitor.py' for live monitoring")
        
        return True
    
    def monitor_system(self, duration_minutes=60):
        """Monitor system health for specified duration"""
        logger.info(f"🔍 Monitoring system health for {duration_minutes} minutes...")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        try:
            while time.time() < end_time:
                all_healthy = True
                
                for name, process in self.processes.items():
                    if not self.check_process_health(name, process):
                        logger.warning(f"⚠️ Component {name} needs restart")
                        all_healthy = False
                
                if all_healthy:
                    logger.info("✅ All components healthy")
                
                time.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")
        
        logger.info("📊 Monitoring session completed")

def main():
    """Main launcher function"""
    launcher = TenxSOMSystemLauncher()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        # Monitor existing system
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        launcher.monitor_system(duration)
    else:
        # Launch new system
        success = launcher.launch_system()
        
        if not success:
            logger.error("💥 System launch failed")
            sys.exit(1)
        
        # Monitor for 10 minutes by default
        launcher.monitor_system(10)

if __name__ == "__main__":
    main()