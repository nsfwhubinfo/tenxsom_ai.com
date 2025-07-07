#!/usr/bin/env python3

"""
Tenxsom AI Production Startup and Management Scripts
Easy-to-use startup scripts for launching the complete production system
"""

import os
import sys
import subprocess
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductionStartup:
    """
    Production startup and management system for Tenxsom AI
    
    Features:
    - One-command system startup
    - Environment validation and setup
    - Service health monitoring
    - Graceful shutdown management
    - System status reporting
    - Quick restart capabilities
    """
    
    def __init__(self):
        """Initialize production startup manager"""
        self.project_root = Path(__file__).parent
        self.python_path = sys.executable
        
        # Core system components
        self.core_services = {
            "production_deployment": {
                "script": "production_deployment.py",
                "description": "Main production deployment manager",
                "startup_priority": 1
            },
            "monetization_executor": {
                "script": "monetization_strategy_executor.py", 
                "description": "30-day monetization strategy execution",
                "startup_priority": 2
            },
            "content_scheduler": {
                "script": "daily_content_scheduler.py",
                "description": "Daily content generation scheduler",
                "startup_priority": 3
            },
            "upload_orchestrator": {
                "script": "content_upload_orchestrator.py",
                "description": "Multi-platform upload orchestration",
                "startup_priority": 4
            },
            "analytics_tracker": {
                "script": "analytics_tracker.py",
                "description": "Analytics and monetization tracking",
                "startup_priority": 5
            }
        }
        
        # Optional services
        self.optional_services = {
            "telegram_bot": {
                "script": "chatbot-integration/central-controller.py",
                "description": "Telegram chatbot for mobile control",
                "startup_priority": 6
            },
            "mcp_server": {
                "script": "mcp_fallback.py",
                "description": "MCP fallback server (UseAPI.net integration)",
                "startup_priority": 7
            }
        }
        
        # System requirements
        self.required_env_vars = [
            "USEAPI_BEARER_TOKEN",
            "YOUTUBE_API_KEY", 
            "GOOGLE_APPLICATION_CREDENTIALS",
            "TELEGRAM_BOT_TOKEN"
        ]
        
        # Service tracking
        self.running_processes = {}
        self.startup_log = []
    
    async def start_production_system(self, include_optional: bool = True) -> Dict[str, Any]:
        """Start the complete production system"""
        print("🚀 Starting Tenxsom AI Production System")
        print("=" * 60)
        
        startup_start = datetime.now()
        startup_results = {
            "start_time": startup_start,
            "services_started": [],
            "services_failed": [],
            "environment_status": "unknown",
            "system_ready": False
        }
        
        try:
            # Step 1: Environment validation
            print("\n📋 Step 1: Validating Environment")
            env_status = await self._validate_environment()
            startup_results["environment_status"] = env_status["status"]
            
            if env_status["status"] != "valid":
                print(f"❌ Environment validation failed: {env_status['issues']}")
                return startup_results
            
            print("✅ Environment validation passed")
            
            # Step 2: Start core services
            print("\n🔧 Step 2: Starting Core Services")
            core_results = await self._start_core_services()
            startup_results["services_started"].extend(core_results["started"])
            startup_results["services_failed"].extend(core_results["failed"])
            
            # Step 3: Start optional services
            if include_optional:
                print("\n⚡ Step 3: Starting Optional Services") 
                optional_results = await self._start_optional_services()
                startup_results["services_started"].extend(optional_results["started"])
                startup_results["services_failed"].extend(optional_results["failed"])
            
            # Step 4: System health check
            print("\n📊 Step 4: System Health Check")
            health_status = await self._perform_health_check()
            startup_results["health_status"] = health_status
            
            # Step 5: Final startup report
            startup_duration = (datetime.now() - startup_start).total_seconds()
            startup_results["startup_duration_seconds"] = startup_duration
            startup_results["system_ready"] = len(startup_results["services_failed"]) == 0
            
            await self._generate_startup_report(startup_results)
            
            if startup_results["system_ready"]:
                print(f"\n🎉 PRODUCTION SYSTEM STARTED SUCCESSFULLY!")
                print(f"⏱️ Startup completed in {startup_duration:.1f} seconds")
                print(f"🟢 {len(startup_results['services_started'])} services running")
                
                # Display management commands
                self._show_management_commands()
            else:
                print(f"\n⚠️ PRODUCTION SYSTEM STARTED WITH ISSUES")
                print(f"🟢 {len(startup_results['services_started'])} services started")
                print(f"🔴 {len(startup_results['services_failed'])} services failed")
            
            return startup_results
            
        except Exception as e:
            logger.error(f"❌ Production startup failed: {e}")
            startup_results["startup_error"] = str(e)
            return startup_results
    
    async def _validate_environment(self) -> Dict[str, Any]:
        """Validate production environment"""
        issues = []
        
        # Check Python version
        if sys.version_info < (3, 8):
            issues.append(f"Python 3.8+ required, found {sys.version}")
        
        # Check required environment variables
        missing_vars = []
        for var in self.required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            issues.append(f"Missing environment variables: {missing_vars}")
        
        # Check required files
        required_files = [
            ".env",
            "production_config_manager.py",
            "monetization_strategy_executor.py",
            "daily_content_scheduler.py"
        ]
        
        missing_files = []
        for file_name in required_files:
            if not (self.project_root / file_name).exists():
                missing_files.append(file_name)
        
        if missing_files:
            issues.append(f"Missing required files: {missing_files}")
        
        # Check Google credentials
        google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if google_creds and not Path(google_creds).exists():
            issues.append(f"Google credentials file not found: {google_creds}")
        
        return {
            "status": "valid" if not issues else "invalid",
            "issues": issues,
            "python_version": sys.version,
            "project_root": str(self.project_root)
        }
    
    async def _start_core_services(self) -> Dict[str, List[str]]:
        """Start core system services"""
        started = []
        failed = []
        
        # Sort services by startup priority
        sorted_services = sorted(
            self.core_services.items(),
            key=lambda x: x[1]["startup_priority"]
        )
        
        for service_name, config in sorted_services:
            try:
                success = await self._start_service(service_name, config)
                if success:
                    started.append(service_name)
                    print(f"   ✅ {config['description']}")
                else:
                    failed.append(service_name)
                    print(f"   ❌ {config['description']} - startup failed")
                
                # Brief delay between service starts
                await asyncio.sleep(2)
                
            except Exception as e:
                failed.append(service_name)
                print(f"   ❌ {config['description']} - error: {e}")
        
        return {"started": started, "failed": failed}
    
    async def _start_optional_services(self) -> Dict[str, List[str]]:
        """Start optional system services"""
        started = []
        failed = []
        
        for service_name, config in self.optional_services.items():
            try:
                # Check if service script exists
                script_path = self.project_root / config["script"]
                if not script_path.exists():
                    print(f"   ⚠️ {config['description']} - script not found, skipping")
                    continue
                
                success = await self._start_service(service_name, config)
                if success:
                    started.append(service_name)
                    print(f"   ✅ {config['description']}")
                else:
                    failed.append(service_name)
                    print(f"   ❌ {config['description']} - startup failed")
                
                await asyncio.sleep(1)
                
            except Exception as e:
                failed.append(service_name)
                print(f"   ❌ {config['description']} - error: {e}")
        
        return {"started": started, "failed": failed}
    
    async def _start_service(self, service_name: str, config: Dict[str, Any]) -> bool:
        """Start an individual service"""
        script_path = self.project_root / config["script"]
        
        if not script_path.exists():
            logger.error(f"Service script not found: {script_path}")
            return False
        
        try:
            # Special handling for production deployment (main service)
            if service_name == "production_deployment":
                # Import and run the deployment manager directly
                return await self._start_production_deployment()
            
            # For content scheduler and analytics tracker, use daemon mode
            if service_name in ["content_scheduler", "analytics_tracker"]:
                process = subprocess.Popen(
                    [self.python_path, str(script_path), "--daemon"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(self.project_root)
                )
            # For MCP server, use daemon mode
            elif service_name == "mcp_server":
                process = subprocess.Popen(
                    [self.python_path, str(script_path), "--daemon"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(self.project_root)
                )
            else:
                # For other services, create background processes
                process = subprocess.Popen(
                    [self.python_path, str(script_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(self.project_root)
                )
            
            # Give process time to start
            await asyncio.sleep(2)
            
            # Check if process is still running
            if process.poll() is None:
                self.running_processes[service_name] = {
                    "process": process,
                    "start_time": datetime.now(),
                    "config": config
                }
                return True
            else:
                # Process already terminated
                stdout, stderr = process.communicate()
                logger.error(f"Service {service_name} failed to start: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start service {service_name}: {e}")
            return False
    
    async def _start_production_deployment(self) -> bool:
        """Start the main production deployment manager"""
        try:
            # Import the production deployment manager
            from production_deployment import ProductionDeploymentManager, DeploymentConfig
            
            # Create deployment configuration
            deployment_config = DeploymentConfig(
                environment="production",
                auto_start=True,
                monitoring_enabled=True,
                backup_enabled=True
            )
            
            # Initialize and start deployment manager in background
            deployment_manager = ProductionDeploymentManager(deployment_config)
            
            # Store reference for management
            self.running_processes["production_deployment"] = {
                "manager": deployment_manager,
                "start_time": datetime.now(),
                "config": {"description": "Main production deployment manager"}
            }
            
            # Start deployment asynchronously
            asyncio.create_task(deployment_manager.deploy_production_system())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start production deployment: {e}")
            return False
    
    async def _perform_health_check(self) -> Dict[str, Any]:
        """Perform system health check"""
        health_status = {
            "overall_health": "unknown",
            "services_running": 0,
            "services_total": len(self.running_processes),
            "services_healthy": [],
            "services_unhealthy": [],
            "system_metrics": {}
        }
        
        healthy_count = 0
        
        for service_name, service_info in self.running_processes.items():
            try:
                if "process" in service_info:
                    # Check process-based service
                    process = service_info["process"]
                    if process.poll() is None:
                        health_status["services_healthy"].append(service_name)
                        healthy_count += 1
                    else:
                        health_status["services_unhealthy"].append(service_name)
                
                elif "manager" in service_info:
                    # Check manager-based service
                    health_status["services_healthy"].append(service_name)
                    healthy_count += 1
                
            except Exception as e:
                health_status["services_unhealthy"].append(service_name)
                logger.error(f"Health check failed for {service_name}: {e}")
        
        health_status["services_running"] = healthy_count
        
        # Determine overall health
        if healthy_count == health_status["services_total"]:
            health_status["overall_health"] = "healthy"
        elif healthy_count > 0:
            health_status["overall_health"] = "degraded"
        else:
            health_status["overall_health"] = "critical"
        
        return health_status
    
    async def _generate_startup_report(self, startup_results: Dict[str, Any]):
        """Generate startup report"""
        report_dir = self.project_root / "production" / "startup"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"startup_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(startup_results, f, indent=2, default=str)
        
        print(f"📄 Startup report saved: {report_file}")
    
    def _show_management_commands(self):
        """Show system management commands"""
        print(f"\n🔧 SYSTEM MANAGEMENT COMMANDS")
        print(f"=" * 40)
        print(f"📊 Check Status:    python production_startup.py status")
        print(f"🔄 Restart System:  python production_startup.py restart")
        print(f"🛑 Stop System:     python production_startup.py stop")
        print(f"📈 View Logs:       python production_startup.py logs")
        print(f"🧪 Health Check:    python production_startup.py health")
        print(f"\n💡 Monitor system: tail -f production/logs/*.log")
    
    async def stop_production_system(self) -> Dict[str, Any]:
        """Stop the production system gracefully"""
        print("🛑 Stopping Tenxsom AI Production System")
        print("=" * 50)
        
        stop_results = {
            "stop_time": datetime.now(),
            "services_stopped": [],
            "services_failed": []
        }
        
        # Stop all running processes
        for service_name, service_info in self.running_processes.items():
            try:
                if "process" in service_info:
                    process = service_info["process"]
                    process.terminate()
                    
                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=10)
                        stop_results["services_stopped"].append(service_name)
                        print(f"   ✅ Stopped {service_name}")
                    except subprocess.TimeoutExpired:
                        process.kill()
                        stop_results["services_stopped"].append(service_name)
                        print(f"   ⚡ Force killed {service_name}")
                
                elif "manager" in service_info:
                    manager = service_info["manager"]
                    if hasattr(manager, 'stop_production_system'):
                        await manager.stop_production_system()
                    stop_results["services_stopped"].append(service_name)
                    print(f"   ✅ Stopped {service_name}")
                
            except Exception as e:
                stop_results["services_failed"].append(service_name)
                print(f"   ❌ Failed to stop {service_name}: {e}")
        
        # Clear running processes
        self.running_processes.clear()
        
        print(f"\n✅ System shutdown complete")
        print(f"🛑 {len(stop_results['services_stopped'])} services stopped")
        
        return stop_results
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        health_status = await self._perform_health_check()
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "services_running": len(self.running_processes),
            "system_health": health_status["overall_health"],
            "uptime_info": {},
            "service_details": {}
        }
        
        # Calculate uptime for each service
        for service_name, service_info in self.running_processes.items():
            start_time = service_info.get("start_time")
            if start_time:
                uptime = datetime.now() - start_time
                status["uptime_info"][service_name] = {
                    "uptime_seconds": uptime.total_seconds(),
                    "uptime_human": str(uptime)
                }
            
            status["service_details"][service_name] = {
                "description": service_info["config"]["description"],
                "status": "running" if service_name in health_status["services_healthy"] else "unhealthy"
            }
        
        return status
    
    async def restart_system(self) -> Dict[str, Any]:
        """Restart the production system"""
        print("🔄 Restarting Tenxsom AI Production System")
        print("=" * 50)
        
        # Stop current system
        stop_results = await self.stop_production_system()
        
        # Wait a moment
        await asyncio.sleep(3)
        
        # Start system again
        start_results = await self.start_production_system()
        
        return {
            "restart_time": datetime.now(),
            "stop_results": stop_results,
            "start_results": start_results
        }


async def main():
    """Main entry point for production startup management"""
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Tenxsom AI Production Management")
    parser.add_argument("command", nargs="?", default="start", 
                       choices=["start", "stop", "restart", "status", "health"],
                       help="Management command")
    parser.add_argument("--no-optional", action="store_true",
                       help="Skip optional services during startup")
    
    args = parser.parse_args()
    startup_manager = ProductionStartup()
    
    if args.command == "start":
        result = await startup_manager.start_production_system(
            include_optional=not args.no_optional
        )
        
        if result.get("system_ready"):
            print(f"\n🎯 System ready for 30-day monetization execution!")
        else:
            print(f"\n⚠️ System started with issues - {len(result.get('services_started', []))} services running")
        
        return result
        
    elif args.command == "stop":
        result = await startup_manager.stop_production_system()
        return result
        
    elif args.command == "restart":
        result = await startup_manager.restart_system()
        return result
        
    elif args.command == "status":
        status = await startup_manager.get_system_status()
        print("\n📊 SYSTEM STATUS")
        print("=" * 30)
        print(f"Health: {status['system_health']}")
        print(f"Services: {status['services_running']} running")
        
        if status['service_details']:
            print(f"\n🔧 Service Details:")
            for name, details in status['service_details'].items():
                uptime = status['uptime_info'].get(name, {}).get('uptime_human', 'Unknown')
                print(f"   {details['status']:>8} | {name:20} | {uptime:>15} | {details['description']}")
        
        return status
        
    elif args.command == "health":
        startup_manager.running_processes = {"mock": {"process": None, "start_time": datetime.now(), "config": {"description": "Mock service"}}}
        health = await startup_manager._perform_health_check()
        print(f"\n🏥 HEALTH CHECK")
        print("=" * 25)
        print(f"Overall: {health['overall_health']}")
        print(f"Healthy: {len(health['services_healthy'])}")
        print(f"Unhealthy: {len(health['services_unhealthy'])}")
        return health


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Default: start the system
        asyncio.run(main())
    else:
        # Run with command line arguments
        asyncio.run(main())