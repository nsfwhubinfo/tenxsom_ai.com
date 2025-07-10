#!/usr/bin/env python3
"""
Cloud Failover Manager for TenxsomAI
Monitors cloud services and automatically starts local instances if they fail
"""
import os
import sys
import time
import json
import subprocess
import logging
import requests
from datetime import datetime
from threading import Thread
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('failover_manager.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Service configurations
SERVICES = {
    'mcp_server': {
        'cloud_url': 'https://tenxsom-mcp-server-540103863590.us-central1.run.app/health',
        'local_port': 8080,
        'local_start_cmd': 'cd mcp_server && python3 -m uvicorn main:app --host 0.0.0.0 --port 8080',
        'health_endpoint': '/health',
        'max_retries': 3,
        'retry_delay': 30
    },
    'video_worker': {
        'cloud_url': 'https://tenxsom-video-worker-hpkm6siuqq-uc.a.run.app/health',
        'local_port': 8081,
        'local_start_cmd': 'cd video_worker && python3 worker.py',
        'health_endpoint': '/health',
        'max_retries': 3,
        'retry_delay': 30
    }
}

# Monitoring configuration
CHECK_INTERVAL = 60  # Check every 60 seconds
FAILURE_THRESHOLD = 3  # Number of consecutive failures before failover
RECOVERY_THRESHOLD = 5  # Number of consecutive successes before switching back

class ServiceMonitor:
    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config
        self.is_cloud_healthy = True
        self.is_local_running = False
        self.failure_count = 0
        self.success_count = 0
        self.local_process = None
        
    def check_health(self, url: str, timeout: int = 5) -> bool:
        """Check if a service is healthy"""
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Health check failed for {url}: {e}")
            return False
    
    def start_local_service(self) -> bool:
        """Start the local service"""
        if self.is_local_running:
            logger.info(f"{self.name}: Local service already running")
            return True
            
        try:
            logger.info(f"{self.name}: Starting local service on port {self.config['local_port']}")
            
            # Set up environment variables
            env = os.environ.copy()
            env['PORT'] = str(self.config['local_port'])
            
            # Start the service
            self.local_process = subprocess.Popen(
                self.config['local_start_cmd'],
                shell=True,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for service to start
            time.sleep(5)
            
            # Check if service started successfully
            local_url = f"http://localhost:{self.config['local_port']}{self.config['health_endpoint']}"
            for i in range(10):
                if self.check_health(local_url):
                    self.is_local_running = True
                    logger.info(f"{self.name}: Local service started successfully")
                    return True
                time.sleep(2)
                
            logger.error(f"{self.name}: Failed to start local service")
            return False
            
        except Exception as e:
            logger.error(f"{self.name}: Error starting local service: {e}")
            return False
    
    def stop_local_service(self):
        """Stop the local service"""
        if self.local_process:
            logger.info(f"{self.name}: Stopping local service")
            self.local_process.terminate()
            self.local_process.wait(timeout=10)
            self.is_local_running = False
            self.local_process = None
    
    def monitor(self):
        """Monitor service health and manage failover"""
        cloud_healthy = self.check_health(self.config['cloud_url'])
        
        if cloud_healthy:
            self.failure_count = 0
            self.success_count += 1
            
            # If cloud is recovered and local is running, consider switching back
            if self.is_local_running and self.success_count >= RECOVERY_THRESHOLD:
                logger.info(f"{self.name}: Cloud service recovered, stopping local instance")
                self.stop_local_service()
                self.is_cloud_healthy = True
                
        else:
            self.success_count = 0
            self.failure_count += 1
            
            # If cloud has failed enough times, start local service
            if self.failure_count >= FAILURE_THRESHOLD and not self.is_local_running:
                logger.warning(f"{self.name}: Cloud service failed {self.failure_count} times, starting failover")
                if self.start_local_service():
                    self.is_cloud_healthy = False
                    self.send_alert(f"{self.name} failed over to local instance")
                else:
                    self.send_alert(f"{self.name} failover failed - service is DOWN")
    
    def send_alert(self, message: str):
        """Send alert via Telegram"""
        try:
            bot_token = "8165715351:AAGx8GbvklCMy0o7B2Kuo6wz8_aKcvBcMO8"
            chat_id = "8088003389"
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            data = {
                "chat_id": chat_id,
                "text": f"🚨 FAILOVER ALERT: {message}\nTime: {datetime.now().isoformat()}"
            }
            
            requests.post(url, json=data, timeout=5)
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")

class FailoverManager:
    def __init__(self):
        self.monitors = {}
        self.running = False
        
    def initialize(self):
        """Initialize service monitors"""
        for name, config in SERVICES.items():
            self.monitors[name] = ServiceMonitor(name, config)
            logger.info(f"Initialized monitor for {name}")
    
    def start(self):
        """Start the failover manager"""
        self.running = True
        logger.info("Starting Failover Manager")
        
        while self.running:
            for monitor in self.monitors.values():
                monitor.monitor()
            
            time.sleep(CHECK_INTERVAL)
    
    def stop(self):
        """Stop the failover manager"""
        logger.info("Stopping Failover Manager")
        self.running = False
        
        # Stop all local services
        for monitor in self.monitors.values():
            if monitor.is_local_running:
                monitor.stop_local_service()

def setup_environment():
    """Set up required environment variables for local services"""
    env_file = ".env.failover"
    
    if not os.path.exists(env_file):
        logger.info("Creating failover environment file")
        with open(env_file, 'w') as f:
            f.write("""# Failover Environment Variables
USEAPI_BEARER_TOKEN=user:1831-r8vA1WGayarXKuYwpT1PW
TELEGRAM_BOT_TOKEN=8165715351:AAGx8GbvklCMy0o7B2Kuo6wz8_aKcvBcMO8
AUTHORIZED_USER_ID=8088003389
DATABASE_URL=postgresql://user:password@localhost/tenxsom_local
CLOUD_TASKS_WORKER_URL=http://localhost:8081/process_video_job
""")
    
    # Load environment variables
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

def main():
    """Main entry point"""
    setup_environment()
    
    manager = FailoverManager()
    manager.initialize()
    
    try:
        manager.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        manager.stop()

if __name__ == "__main__":
    main()