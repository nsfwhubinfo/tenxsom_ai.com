#!/usr/bin/env python3
"""
Health monitoring script for MCP server
Can be run as a cron job or monitoring system integration
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Dict, Any, Optional

import httpx


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPHealthMonitor:
    """Health monitoring for MCP server"""
    
    def __init__(self, server_url: str, alert_webhook: Optional[str] = None):
        self.server_url = server_url.rstrip('/')
        self.alert_webhook = alert_webhook
        self.thresholds = {
            'max_response_time_ms': 5000,
            'max_error_rate_percent': 5.0,
            'min_uptime_seconds': 60,
            'max_database_latency_ms': 2000
        }
    
    async def check_health(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "server_url": self.server_url,
            "status": "healthy",
            "checks": {},
            "alerts": []
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Basic health check
            try:
                response = await client.get(f"{self.server_url}/health")
                health_report["checks"]["basic_health"] = {
                    "status": "pass" if response.status_code == 200 else "fail",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "status_code": response.status_code
                }
                
                if response.status_code != 200:
                    health_report["status"] = "unhealthy"
                    health_report["alerts"].append("Basic health check failed")
                    
            except Exception as e:
                health_report["checks"]["basic_health"] = {
                    "status": "fail",
                    "error": str(e)
                }
                health_report["status"] = "unhealthy"
                health_report["alerts"].append(f"Health endpoint unreachable: {e}")
            
            # Detailed health check
            try:
                response = await client.get(f"{self.server_url}/health/detailed")
                if response.status_code == 200:
                    detailed_health = response.json()
                    health_report["checks"]["detailed_health"] = detailed_health
                    
                    # Check component health
                    for component, status in detailed_health.get("components", {}).items():
                        if status.get("status") != "healthy":
                            health_report["status"] = "degraded"
                            health_report["alerts"].append(f"Component {component} is {status.get('status')}")
                else:
                    health_report["alerts"].append("Detailed health check failed")
                    
            except Exception as e:
                health_report["checks"]["detailed_health"] = {
                    "status": "fail",
                    "error": str(e)
                }
                health_report["alerts"].append(f"Detailed health check failed: {e}")
            
            # Performance metrics check
            try:
                response = await client.get(f"{self.server_url}/metrics")
                if response.status_code == 200:
                    metrics = response.json()
                    health_report["checks"]["metrics"] = metrics
                    
                    # Check performance thresholds
                    system_metrics = metrics.get("system_metrics", {})
                    
                    # Response time check
                    avg_response_time = system_metrics.get("average_response_time_ms", 0)
                    if avg_response_time > self.thresholds["max_response_time_ms"]:
                        health_report["status"] = "degraded"
                        health_report["alerts"].append(
                            f"High average response time: {avg_response_time:.1f}ms"
                        )
                    
                    # Error rate check
                    error_rate = system_metrics.get("error_rate_percent", 0)
                    if error_rate > self.thresholds["max_error_rate_percent"]:
                        health_report["status"] = "degraded"
                        health_report["alerts"].append(
                            f"High error rate: {error_rate:.1f}%"
                        )
                    
                    # Uptime check
                    uptime = system_metrics.get("uptime_seconds", 0)
                    if uptime < self.thresholds["min_uptime_seconds"]:
                        health_report["alerts"].append(
                            f"Recent restart detected: uptime {uptime:.0f}s"
                        )
                        
                else:
                    health_report["alerts"].append("Metrics endpoint failed")
                    
            except Exception as e:
                health_report["checks"]["metrics"] = {
                    "status": "fail",
                    "error": str(e)
                }
                health_report["alerts"].append(f"Metrics check failed: {e}")
            
            # Template functionality check
            try:
                response = await client.get(f"{self.server_url}/api/templates?limit=1")
                if response.status_code == 200:
                    templates_data = response.json()
                    template_count = templates_data.get("count", 0)
                    health_report["checks"]["templates"] = {
                        "status": "pass",
                        "template_count": template_count
                    }
                    
                    if template_count == 0:
                        health_report["status"] = "degraded"
                        health_report["alerts"].append("No templates loaded")
                else:
                    health_report["alerts"].append("Template API failed")
                    
            except Exception as e:
                health_report["checks"]["templates"] = {
                    "status": "fail",
                    "error": str(e)
                }
                health_report["alerts"].append(f"Template check failed: {e}")
        
        return health_report
    
    async def send_alert(self, health_report: Dict[str, Any]):
        """Send alert if configured"""
        if not self.alert_webhook or not health_report["alerts"]:
            return
        
        alert_payload = {
            "timestamp": health_report["timestamp"],
            "service": "tenxsom-mcp-server",
            "status": health_report["status"],
            "alerts": health_report["alerts"],
            "server_url": self.server_url
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.alert_webhook,
                    json=alert_payload,
                    timeout=10.0
                )
                if response.status_code == 200:
                    logger.info("Alert sent successfully")
                else:
                    logger.error(f"Failed to send alert: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
    
    async def run_check(self) -> int:
        """Run health check and return exit code"""
        try:
            health_report = await self.check_health()
            
            # Print report
            print(json.dumps(health_report, indent=2))
            
            # Send alert if there are issues
            if health_report["alerts"]:
                await self.send_alert(health_report)
            
            # Return appropriate exit code
            if health_report["status"] == "healthy":
                return 0
            elif health_report["status"] == "degraded":
                return 1
            else:
                return 2
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return 3


async def main():
    """Main function"""
    # Get configuration from environment
    server_url = os.getenv('MCP_SERVER_URL', 'https://tenxsom-mcp-server-hpkm6siuqq-uc.a.run.app')
    alert_webhook = os.getenv('ALERT_WEBHOOK_URL')
    
    # Create monitor
    monitor = MCPHealthMonitor(server_url, alert_webhook)
    
    # Run health check
    exit_code = await monitor.run_check()
    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())