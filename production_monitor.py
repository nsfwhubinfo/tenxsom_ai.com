#!/usr/bin/env python3

"""
TenxsomAI Production Monitor
Real-time monitoring dashboard for live production system
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import sys
import os

# Add project root to path
sys.path.append('/home/golde/tenxsom-ai-vertex')

class ProductionMonitor:
    """Real-time production monitoring system"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.health_endpoints = {
            "Platform Agents": "http://localhost:8080/health",
            "MCP Server": "https://tenxsom-mcp-server-540103863590.us-central1.run.app/health",
            "Cloud Worker": "https://tenxsom-video-worker-hpkm6siuqq-uc.a.run.app/health"
        }
        
    async def check_service_health(self, name: str, url: str) -> Dict[str, Any]:
        """Check health of individual service"""
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                start_time = time.time()
                async with session.get(url) as response:
                    response_time = (time.time() - start_time) * 1000  # ms
                    
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "healthy",
                            "response_time_ms": round(response_time, 2),
                            "details": data
                        }
                    else:
                        return {
                            "status": "unhealthy",
                            "response_time_ms": round(response_time, 2),
                            "error": f"HTTP {response.status}"
                        }
        except Exception as e:
            return {
                "status": "error",
                "response_time_ms": None,
                "error": str(e)
            }
    
    async def check_component_imports(self) -> Dict[str, bool]:
        """Check if all critical components can be imported"""
        components = {
            "ProductionConfigManager": "production_config_manager",
            "ContentUploadOrchestrator": "content_upload_orchestrator", 
            "DailyContentScheduler": "daily_content_scheduler",
            "AgentSwarmOrchestrator": "agent_swarm_orchestrator",
            "PredictiveAnalyticsEngine": "predictive_analytics_engine",
            "ContentLifecycleManager": "content_lifecycle_manager",
            "EnhancedRevenueOptimizationAI": "enhanced_revenue_optimization_ai"
        }
        
        results = {}
        for name, module in components.items():
            try:
                __import__(module)
                results[name] = True
            except Exception:
                results[name] = False
        
        return results
    
    def check_process_status(self) -> Dict[str, Any]:
        """Check running processes"""
        import subprocess
        
        processes = {}
        
        # Check for platform agents
        try:
            result = subprocess.run(['pgrep', '-f', 'platform_agents_server'], 
                                  capture_output=True, text=True)
            processes["Platform Agents Server"] = len(result.stdout.strip().split('\n')) > 0 if result.stdout.strip() else False
        except:
            processes["Platform Agents Server"] = False
            
        # Check for scheduler
        try:
            result = subprocess.run(['pgrep', '-f', 'daily_content_scheduler'], 
                                  capture_output=True, text=True)
            processes["Daily Content Scheduler"] = len(result.stdout.strip().split('\n')) > 0 if result.stdout.strip() else False
        except:
            processes["Daily Content Scheduler"] = False
            
        return processes
    
    def check_file_system(self) -> Dict[str, Any]:
        """Check critical files and directories"""
        critical_paths = {
            "Production Config": "/home/golde/tenxsom-ai-vertex/production-config.env",
            "Logs Directory": "/home/golde/tenxsom-ai-vertex/logs",
            "Virtual Environment": "/home/golde/tenxsom-ai-vertex/venv",
            "MCP Templates": "/home/golde/tenxsom-ai-vertex/mcp-templates",
            "SystemD Service": "/home/golde/tenxsom-ai-vertex/systemd/tenxsom-scheduler.service"
        }
        
        results = {}
        for name, path in critical_paths.items():
            results[name] = os.path.exists(path)
            
        return results
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        
        # Get all health checks
        service_health = {}
        for name, url in self.health_endpoints.items():
            service_health[name] = await self.check_service_health(name, url)
        
        component_status = await self.check_component_imports()
        process_status = self.check_process_status()
        filesystem_status = self.check_file_system()
        
        # Calculate overall health
        healthy_services = sum(1 for h in service_health.values() if h["status"] == "healthy")
        healthy_components = sum(1 for status in component_status.values() if status)
        healthy_processes = sum(1 for status in process_status.values() if status)
        healthy_filesystem = sum(1 for status in filesystem_status.values() if status)
        
        total_checks = len(service_health) + len(component_status) + len(process_status) + len(filesystem_status)
        total_healthy = healthy_services + healthy_components + healthy_processes + healthy_filesystem
        
        overall_health = (total_healthy / total_checks) * 100
        
        uptime = datetime.now() - self.start_time
        
        return {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": int(uptime.total_seconds()),
            "overall_health_percent": round(overall_health, 1),
            "service_health": service_health,
            "component_status": component_status,
            "process_status": process_status,
            "filesystem_status": filesystem_status,
            "summary": {
                "services": f"{healthy_services}/{len(service_health)}",
                "components": f"{healthy_components}/{len(component_status)}",
                "processes": f"{healthy_processes}/{len(process_status)}",
                "filesystem": f"{healthy_filesystem}/{len(filesystem_status)}"
            }
        }
    
    def print_dashboard(self, metrics: Dict[str, Any]):
        """Print beautiful monitoring dashboard"""
        
        # Clear screen and print header
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("=" * 80)
        print("🎯 TENXSOMAI PRODUCTION MONITORING DASHBOARD")
        print("=" * 80)
        print(f"⏰ {metrics['timestamp']}")
        print(f"🔄 Uptime: {metrics['uptime_seconds'] // 3600}h {(metrics['uptime_seconds'] % 3600) // 60}m")
        print(f"💚 Overall Health: {metrics['overall_health_percent']}%")
        print()
        
        # Service Health
        print("🌐 SERVICE HEALTH")
        print("-" * 40)
        for name, health in metrics['service_health'].items():
            status_icon = "✅" if health['status'] == "healthy" else "❌"
            response_time = f" ({health['response_time_ms']}ms)" if health['response_time_ms'] else ""
            print(f"{status_icon} {name}: {health['status']}{response_time}")
        print()
        
        # Component Status
        print("🔧 COMPONENT STATUS")
        print("-" * 40)
        for name, status in metrics['component_status'].items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {name}: {'operational' if status else 'failed'}")
        print()
        
        # Process Status
        print("⚙️ PROCESS STATUS")
        print("-" * 40)
        for name, status in metrics['process_status'].items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {name}: {'running' if status else 'stopped'}")
        print()
        
        # Filesystem Status
        print("📁 FILESYSTEM STATUS")
        print("-" * 40)
        for name, status in metrics['filesystem_status'].items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {name}: {'exists' if status else 'missing'}")
        print()
        
        # Summary
        print("📊 SUMMARY")
        print("-" * 40)
        for category, count in metrics['summary'].items():
            print(f"   {category.title()}: {count}")
        print()
        
        # Production readiness assessment
        health_percent = metrics['overall_health_percent']
        if health_percent >= 90:
            print("🚀 STATUS: PRODUCTION READY - ALL SYSTEMS OPERATIONAL")
        elif health_percent >= 80:
            print("⚠️ STATUS: MOSTLY OPERATIONAL - MINOR ISSUES DETECTED")  
        elif health_percent >= 70:
            print("🔧 STATUS: DEGRADED PERFORMANCE - ATTENTION REQUIRED")
        else:
            print("🚨 STATUS: CRITICAL ISSUES - IMMEDIATE ACTION NEEDED")
        
        print("=" * 80)
        print("Press Ctrl+C to exit monitoring")
    
    async def run_monitoring_loop(self, interval: int = 30):
        """Run continuous monitoring loop"""
        print("🚀 Starting TenxsomAI Production Monitor...")
        print(f"📊 Refreshing every {interval} seconds")
        print()
        
        try:
            while True:
                metrics = await self.get_system_metrics()
                self.print_dashboard(metrics)
                
                # Save metrics to file
                log_file = f"/home/golde/tenxsom-ai-vertex/logs/production_metrics_{datetime.now().strftime('%Y_%m_%d')}.jsonl"
                with open(log_file, 'a') as f:
                    f.write(json.dumps(metrics) + '\n')
                
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
        except Exception as e:
            print(f"\n\n❌ Monitoring error: {e}")


async def main():
    """Main monitoring function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="TenxsomAI Production Monitor")
    parser.add_argument("--interval", type=int, default=30, help="Refresh interval in seconds")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    
    args = parser.parse_args()
    
    monitor = ProductionMonitor()
    
    if args.once:
        # Single check mode
        metrics = await monitor.get_system_metrics()
        monitor.print_dashboard(metrics)
        
        # Return appropriate exit code
        health_percent = metrics['overall_health_percent']
        sys.exit(0 if health_percent >= 80 else 1)
    else:
        # Continuous monitoring mode
        await monitor.run_monitoring_loop(args.interval)


if __name__ == "__main__":
    asyncio.run(main())