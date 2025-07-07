"""
Health Check Module for Tenxsom AI Agents
Provides a standardized health endpoint for monitoring
"""

import asyncio
import json
import logging
import os
import psutil
import time
from datetime import datetime
from threading import Thread
from typing import Dict, Any, Callable, Optional

try:
    from aiohttp import web
except ImportError:
    # Fallback to Flask if aiohttp not available
    from flask import Flask, jsonify
    web = None

logger = logging.getLogger(__name__)


class HealthCheckServer:
    """Unified health check server for Tenxsom AI agents"""
    
    def __init__(self, 
                 agent_name: str,
                 port: int,
                 custom_checks: Optional[Dict[str, Callable]] = None):
        """
        Initialize health check server
        
        Args:
            agent_name: Name of the agent
            port: Port to run health server on
            custom_checks: Dict of custom health check functions
        """
        self.agent_name = agent_name
        self.port = port
        self.custom_checks = custom_checks or {}
        self.start_time = time.time()
        self.request_count = 0
        self.last_error = None
        self.is_healthy = True
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system resource metrics"""
        process = psutil.Process(os.getpid())
        
        return {
            "cpu_percent": process.cpu_percent(interval=0.1),
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "memory_percent": process.memory_percent(),
            "num_threads": process.num_threads(),
            "open_files": len(process.open_files()),
        }
        
    def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status"""
        uptime = time.time() - self.start_time
        
        status = {
            "status": "ok" if self.is_healthy else "degraded",
            "agent": self.agent_name,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": int(uptime),
            "uptime_human": self._format_uptime(uptime),
            "metrics": {
                "requests_served": self.request_count,
                "system": self.get_system_metrics(),
            }
        }
        
        # Run custom health checks
        if self.custom_checks:
            custom_results = {}
            for check_name, check_func in self.custom_checks.items():
                try:
                    result = check_func()
                    custom_results[check_name] = {
                        "status": "ok" if result else "failed",
                        "result": result
                    }
                except Exception as e:
                    custom_results[check_name] = {
                        "status": "error",
                        "error": str(e)
                    }
                    self.is_healthy = False
            status["custom_checks"] = custom_results
            
        # Add last error if any
        if self.last_error:
            status["last_error"] = self.last_error
            
        return status
        
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        
        parts = []
        if days: parts.append(f"{days}d")
        if hours: parts.append(f"{hours}h")
        if minutes: parts.append(f"{minutes}m")
        
        return " ".join(parts) or "< 1m"
        
    def run_aiohttp_server(self):
        """Run health server using aiohttp (async)"""
        app = web.Application()
        
        async def health_handler(request):
            self.request_count += 1
            status = self.get_agent_status()
            return web.json_response(status, status=200 if self.is_healthy else 503)
            
        async def ready_handler(request):
            # Simple readiness probe
            return web.json_response({"ready": True})
            
        app.router.add_get('/health', health_handler)
        app.router.add_get('/ready', ready_handler)
        
        runner = web.AppRunner(app)
        asyncio.run(self._start_aiohttp(runner))
        
    async def _start_aiohttp(self, runner):
        """Start aiohttp server"""
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        logger.info(f"Health check server running on http://0.0.0.0:{self.port}")
        
        # Keep server running
        while True:
            await asyncio.sleep(3600)
            
    def run_flask_server(self):
        """Run health server using Flask (fallback)"""
        app = Flask(__name__)
        
        @app.route('/health')
        def health():
            self.request_count += 1
            status = self.get_agent_status()
            return jsonify(status), 200 if self.is_healthy else 503
            
        @app.route('/ready')
        def ready():
            return jsonify({"ready": True})
            
        # Use production server if available
        try:
            from waitress import serve
            logger.info(f"Health check server (waitress) running on http://0.0.0.0:{self.port}")
            serve(app, host='0.0.0.0', port=self.port, threads=2)
        except ImportError:
            logger.warning("Waitress not available, using Flask development server")
            app.run(host='0.0.0.0', port=self.port, debug=False)
            
    def start(self):
        """Start health check server in background thread"""
        def run_server():
            try:
                if web:
                    self.run_aiohttp_server()
                else:
                    self.run_flask_server()
            except Exception as e:
                logger.error(f"Health check server failed: {e}")
                self.last_error = str(e)
                self.is_healthy = False
                
        thread = Thread(target=run_server, daemon=True)
        thread.start()
        logger.info(f"Started health check server for {self.agent_name} on port {self.port}")
        
    def set_healthy(self, is_healthy: bool, error: Optional[str] = None):
        """Update health status"""
        self.is_healthy = is_healthy
        if error:
            self.last_error = error
            

# Convenience function for agents
def start_health_server(agent_name: str, 
                       port: Optional[int] = None,
                       custom_checks: Optional[Dict[str, Callable]] = None) -> HealthCheckServer:
    """
    Start a health check server for an agent
    
    Args:
        agent_name: Name of the agent
        port: Port to run on (defaults from env)
        custom_checks: Custom health check functions
        
    Returns:
        HealthCheckServer instance
    """
    if port is None:
        # Get port from environment based on agent name
        env_key = f"{agent_name.upper().replace(' ', '_')}_HEALTH_PORT"
        port = int(os.getenv(env_key, 8090))
        
    server = HealthCheckServer(agent_name, port, custom_checks)
    server.start()
    return server


# Example usage in an agent:
if __name__ == "__main__":
    # Example custom health checks
    def check_database():
        # Simulate database check
        return True
        
    def check_api_connection():
        # Simulate API check
        return {"connected": True, "latency_ms": 45}
        
    # Start health server
    health_server = start_health_server(
        "ExampleAgent",
        port=8090,
        custom_checks={
            "database": check_database,
            "api": check_api_connection
        }
    )
    
    # Simulate agent work
    import time
    while True:
        time.sleep(10)
        print("Agent working...")