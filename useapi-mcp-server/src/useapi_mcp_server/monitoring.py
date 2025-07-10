#!/usr/bin/env python3
"""
Performance monitoring and logging for MCP server
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
import os
from dataclasses import dataclass, asdict
from functools import wraps

import httpx
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    timestamp: str
    endpoint: str
    method: str
    duration_ms: float
    status_code: int
    template_name: Optional[str] = None
    template_processing_ms: Optional[float] = None
    database_query_ms: Optional[float] = None
    useapi_request_ms: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    error_message: Optional[str] = None


@dataclass
class SystemMetrics:
    """System-level metrics"""
    timestamp: str
    active_connections: int
    database_pool_size: int
    template_count: int
    requests_per_minute: float
    average_response_time: float
    error_rate: float
    uptime_seconds: float


class StructuredLogger:
    """Structured logging for MCP server"""
    
    def __init__(self, service_name: str = "tenxsom-mcp-server"):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        
        # Configure structured logging
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_request(self, request: Request, response: Response, duration_ms: float, extra_data: Dict[str, Any] = None):
        """Log HTTP request with structured data"""
        log_data = {
            "event": "http_request",
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "user_agent": request.headers.get("user-agent"),
            "remote_addr": request.client.host if request.client else None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": self.service_name
        }
        
        if extra_data:
            log_data.update(extra_data)
        
        level = logging.ERROR if response.status_code >= 400 else logging.INFO
        self.logger.log(level, json.dumps(log_data))
    
    def log_template_processing(self, template_name: str, duration_ms: float, success: bool, extra_data: Dict[str, Any] = None):
        """Log template processing events"""
        log_data = {
            "event": "template_processing",
            "template_name": template_name,
            "duration_ms": duration_ms,
            "success": success,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": self.service_name
        }
        
        if extra_data:
            log_data.update(extra_data)
        
        level = logging.INFO if success else logging.ERROR
        self.logger.log(level, json.dumps(log_data))
    
    def log_database_operation(self, operation: str, duration_ms: float, success: bool, extra_data: Dict[str, Any] = None):
        """Log database operations"""
        log_data = {
            "event": "database_operation",
            "operation": operation,
            "duration_ms": duration_ms,
            "success": success,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": self.service_name
        }
        
        if extra_data:
            log_data.update(extra_data)
        
        level = logging.INFO if success else logging.ERROR
        self.logger.log(level, json.dumps(log_data))
    
    def log_error(self, error: Exception, context: str = None, extra_data: Dict[str, Any] = None):
        """Log errors with context"""
        log_data = {
            "event": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": self.service_name
        }
        
        if extra_data:
            log_data.update(extra_data)
        
        self.logger.error(json.dumps(log_data))


class PerformanceMonitor:
    """Performance monitoring and metrics collection"""
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics: List[PerformanceMetric] = []
        self.request_count = 0
        self.error_count = 0
        self.total_duration = 0.0
        self.logger = StructuredLogger()
    
    def record_metric(self, metric: PerformanceMetric):
        """Record a performance metric"""
        self.metrics.append(metric)
        self.request_count += 1
        self.total_duration += metric.duration_ms
        
        if metric.status_code >= 400:
            self.error_count += 1
        
        # Keep only last 1000 metrics in memory
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-1000:]
    
    def get_system_metrics(self, template_count: int = 0, active_connections: int = 0, db_pool_size: int = 0) -> SystemMetrics:
        """Get current system metrics"""
        now = datetime.now(timezone.utc).isoformat()
        uptime = time.time() - self.start_time
        
        # Calculate rates
        requests_per_minute = (self.request_count / uptime) * 60 if uptime > 0 else 0
        average_response_time = self.total_duration / self.request_count if self.request_count > 0 else 0
        error_rate = (self.error_count / self.request_count) * 100 if self.request_count > 0 else 0
        
        return SystemMetrics(
            timestamp=now,
            active_connections=active_connections,
            database_pool_size=db_pool_size,
            template_count=template_count,
            requests_per_minute=requests_per_minute,
            average_response_time=average_response_time,
            error_rate=error_rate,
            uptime_seconds=uptime
        )
    
    def get_recent_metrics(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent performance metrics"""
        recent = self.metrics[-limit:] if limit else self.metrics
        return [asdict(metric) for metric in recent]
    
    async def export_metrics_to_cloud_logging(self):
        """Export metrics to Google Cloud Logging"""
        try:
            # This would integrate with Google Cloud Logging API
            # For now, we'll just log the metrics
            system_metrics = self.get_system_metrics()
            self.logger.logger.info(f"System metrics: {json.dumps(asdict(system_metrics))}")
        except Exception as e:
            self.logger.log_error(e, "metrics_export")


class PerformanceMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for performance monitoring"""
    
    def __init__(self, app, monitor: PerformanceMonitor):
        super().__init__(app)
        self.monitor = monitor
        self.logger = StructuredLogger()
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Extract template name from request if available
        template_name = None
        if request.method == "POST" and "/templates/" in request.url.path:
            try:
                # Try to extract template name from URL or body
                path_parts = request.url.path.split("/")
                if "process" in path_parts:
                    # This is a template processing request
                    body = await request.body()
                    if body:
                        try:
                            data = json.loads(body.decode())
                            template_name = data.get("template_name")
                        except:
                            pass
            except:
                pass
        
        # Process request
        try:
            response = await call_next(request)
            error_message = None
        except Exception as e:
            response = Response(status_code=500, content="Internal Server Error")
            error_message = str(e)
            self.logger.log_error(e, "request_processing")
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Create performance metric
        metric = PerformanceMetric(
            timestamp=datetime.now(timezone.utc).isoformat(),
            endpoint=request.url.path,
            method=request.method,
            duration_ms=duration_ms,
            status_code=response.status_code,
            template_name=template_name,
            error_message=error_message
        )
        
        # Record metric
        self.monitor.record_metric(metric)
        
        # Log request
        extra_data = {}
        if template_name:
            extra_data["template_name"] = template_name
        if error_message:
            extra_data["error_message"] = error_message
        
        self.logger.log_request(request, response, duration_ms, extra_data)
        
        return response


def performance_timer(operation_name: str):
    """Decorator to time function execution"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            logger = StructuredLogger()
            
            try:
                result = await func(*args, **kwargs)
                success = True
                error_msg = None
            except Exception as e:
                result = None
                success = False
                error_msg = str(e)
                logger.log_error(e, operation_name)
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                logger.log_database_operation(operation_name, duration_ms, success, 
                                            {"error": error_msg} if error_msg else None)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            logger = StructuredLogger()
            
            try:
                result = func(*args, **kwargs)
                success = True
                error_msg = None
            except Exception as e:
                result = None
                success = False
                error_msg = str(e)
                logger.log_error(e, operation_name)
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                logger.log_database_operation(operation_name, duration_ms, success,
                                            {"error": error_msg} if error_msg else None)
            
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    return performance_monitor