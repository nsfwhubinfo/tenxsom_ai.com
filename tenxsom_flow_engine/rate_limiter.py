#!/usr/bin/env python3
"""
Rate Limiter for UseAPI.net Quota Management
Implements intelligent rate limiting for video generation based on API quotas
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class RateLimitType(Enum):
    """Types of rate limiting"""
    PER_SECOND = "per_second"
    PER_MINUTE = "per_minute"
    PER_HOUR = "per_hour"
    PER_DAY = "per_day"

@dataclass
class RateLimit:
    """Rate limit configuration"""
    limit: int
    period_seconds: int
    current_count: int = 0
    period_start: Optional[datetime] = None
    
    def reset_if_needed(self):
        """Reset counter if period has elapsed"""
        now = datetime.now()
        if not self.period_start:
            self.period_start = now
            return
        
        if (now - self.period_start).total_seconds() >= self.period_seconds:
            self.current_count = 0
            self.period_start = now

class UseAPIRateLimiter:
    """
    Rate limiter specifically designed for UseAPI.net quota management
    Handles different API endpoints with their specific limits
    """
    
    def __init__(self):
        """Initialize rate limiter with UseAPI.net-specific limits"""
        # UseAPI.net observed limits and best practices
        self.rate_limits = {
            "pixverse": {
                RateLimitType.PER_SECOND: RateLimit(limit=1, period_seconds=1),
                RateLimitType.PER_MINUTE: RateLimit(limit=10, period_seconds=60),
                RateLimitType.PER_HOUR: RateLimit(limit=100, period_seconds=3600)
            },
            "ltx_studio": {
                RateLimitType.PER_SECOND: RateLimit(limit=2, period_seconds=1),
                RateLimitType.PER_MINUTE: RateLimit(limit=20, period_seconds=60),
                RateLimitType.PER_HOUR: RateLimit(limit=200, period_seconds=3600)
            },
            "heygen_tts": {
                RateLimitType.PER_SECOND: RateLimit(limit=3, period_seconds=1),
                RateLimitType.PER_MINUTE: RateLimit(limit=30, period_seconds=60),
                RateLimitType.PER_HOUR: RateLimit(limit=300, period_seconds=3600)
            },
            "global": {
                RateLimitType.PER_SECOND: RateLimit(limit=5, period_seconds=1),
                RateLimitType.PER_MINUTE: RateLimit(limit=50, period_seconds=60),
                RateLimitType.PER_HOUR: RateLimit(limit=500, period_seconds=3600),
                RateLimitType.PER_DAY: RateLimit(limit=2000, period_seconds=86400)
            }
        }
        
        # Track API usage
        self.usage_stats = {
            "total_requests": 0,
            "rate_limited_requests": 0,
            "average_wait_time": 0.0,
            "start_time": datetime.now()
        }
        
        # Adaptive limits based on observed response times
        self.adaptive_limits = {
            "pixverse": {"base_delay": 1.0, "backoff_factor": 1.5},
            "ltx_studio": {"base_delay": 0.5, "backoff_factor": 1.2},
            "heygen_tts": {"base_delay": 0.3, "backoff_factor": 1.1}
        }
    
    async def check_rate_limit(self, service: str, endpoint: str = None) -> Dict[str, Any]:
        """
        Check if request can proceed without hitting rate limits
        
        Args:
            service: Service name (pixverse, ltx_studio, heygen_tts)
            endpoint: Optional specific endpoint
            
        Returns:
            Dictionary with rate limit status and wait time
        """
        service_limits = self.rate_limits.get(service, self.rate_limits["global"])
        global_limits = self.rate_limits["global"]
        
        # Check all rate limit periods for the service
        max_wait_time = 0
        limiting_type = None
        
        for limit_type, rate_limit in service_limits.items():
            rate_limit.reset_if_needed()
            
            if rate_limit.current_count >= rate_limit.limit:
                # Calculate wait time for this limit
                elapsed = (datetime.now() - rate_limit.period_start).total_seconds()
                wait_time = rate_limit.period_seconds - elapsed
                
                if wait_time > max_wait_time:
                    max_wait_time = wait_time
                    limiting_type = limit_type
        
        # Also check global limits
        for limit_type, rate_limit in global_limits.items():
            rate_limit.reset_if_needed()
            
            if rate_limit.current_count >= rate_limit.limit:
                elapsed = (datetime.now() - rate_limit.period_start).total_seconds()
                wait_time = rate_limit.period_seconds - elapsed
                
                if wait_time > max_wait_time:
                    max_wait_time = wait_time
                    limiting_type = f"global_{limit_type.value}"
        
        return {
            "can_proceed": max_wait_time <= 0,
            "wait_time": max(0, max_wait_time),
            "limiting_type": limiting_type,
            "service": service
        }
    
    async def wait_for_rate_limit(self, service: str, endpoint: str = None) -> float:
        """
        Wait for rate limits and return actual wait time
        
        Args:
            service: Service name
            endpoint: Optional specific endpoint
            
        Returns:
            Actual wait time in seconds
        """
        start_time = time.time()
        
        rate_check = await self.check_rate_limit(service, endpoint)
        
        if not rate_check["can_proceed"]:
            wait_time = rate_check["wait_time"]
            limiting_type = rate_check["limiting_type"]
            
            logger.info(f"Rate limit hit for {service} ({limiting_type}) - waiting {wait_time:.2f}s")
            
            # Track rate limiting
            self.usage_stats["rate_limited_requests"] += 1
            
            # Wait with adaptive backoff
            adaptive_delay = self._calculate_adaptive_delay(service, wait_time)
            await asyncio.sleep(adaptive_delay)
            
            actual_wait = time.time() - start_time
            self._update_wait_time_stats(actual_wait)
            
            return actual_wait
        
        return 0.0
    
    def _calculate_adaptive_delay(self, service: str, base_wait_time: float) -> float:
        """Calculate adaptive delay based on service performance"""
        adaptive_config = self.adaptive_limits.get(service, {"base_delay": 1.0, "backoff_factor": 1.2})
        
        # Add base delay to prevent hammering
        base_delay = adaptive_config["base_delay"]
        
        # Apply backoff factor if we're hitting limits frequently
        backoff_factor = adaptive_config["backoff_factor"]
        
        # Calculate recent rate limit frequency
        recent_rate_limited = self.usage_stats["rate_limited_requests"]
        total_requests = max(1, self.usage_stats["total_requests"])
        rate_limit_percentage = recent_rate_limited / total_requests
        
        if rate_limit_percentage > 0.1:  # More than 10% rate limited
            backoff_multiplier = 1 + (rate_limit_percentage * backoff_factor)
        else:
            backoff_multiplier = 1.0
        
        return max(base_wait_time, base_delay * backoff_multiplier)
    
    def _update_wait_time_stats(self, wait_time: float):
        """Update average wait time statistics"""
        current_avg = self.usage_stats["average_wait_time"]
        total_waits = self.usage_stats["rate_limited_requests"]
        
        # Calculate rolling average
        self.usage_stats["average_wait_time"] = (
            (current_avg * (total_waits - 1) + wait_time) / total_waits
        )
    
    async def record_request(self, service: str, endpoint: str = None, 
                           success: bool = True, response_time: float = None):
        """
        Record an API request for rate limiting calculations
        
        Args:
            service: Service name
            endpoint: Optional specific endpoint
            success: Whether the request was successful
            response_time: Response time in seconds
        """
        # Update counters
        service_limits = self.rate_limits.get(service, self.rate_limits["global"])
        global_limits = self.rate_limits["global"]
        
        for rate_limit in service_limits.values():
            rate_limit.current_count += 1
        
        for rate_limit in global_limits.values():
            rate_limit.current_count += 1
        
        # Update usage stats
        self.usage_stats["total_requests"] += 1
        
        # Log high response times as potential rate limiting indicators
        if response_time and response_time > 10.0:
            logger.warning(f"Slow response from {service}: {response_time:.2f}s")
    
    def get_rate_limit_stats(self) -> Dict[str, Any]:
        """Get comprehensive rate limiting statistics"""
        uptime = (datetime.now() - self.usage_stats["start_time"]).total_seconds()
        
        stats = {
            "uptime_seconds": uptime,
            "usage_stats": self.usage_stats.copy(),
            "current_limits": {},
            "efficiency_metrics": {}
        }
        
        # Current rate limit status
        for service, limits in self.rate_limits.items():
            stats["current_limits"][service] = {}
            for limit_type, rate_limit in limits.items():
                rate_limit.reset_if_needed()
                stats["current_limits"][service][limit_type.value] = {
                    "limit": rate_limit.limit,
                    "current_count": rate_limit.current_count,
                    "remaining": rate_limit.limit - rate_limit.current_count,
                    "period_seconds": rate_limit.period_seconds
                }
        
        # Efficiency metrics
        total_requests = max(1, self.usage_stats["total_requests"])
        rate_limited_percentage = (self.usage_stats["rate_limited_requests"] / total_requests) * 100
        
        stats["efficiency_metrics"] = {
            "rate_limited_percentage": rate_limited_percentage,
            "average_wait_time": self.usage_stats["average_wait_time"],
            "requests_per_hour": (total_requests / max(1, uptime)) * 3600,
            "efficiency_score": max(0, 100 - rate_limited_percentage)
        }
        
        return stats
    
    def update_limits_from_response(self, service: str, response_headers: Dict[str, str]):
        """
        Update rate limits based on API response headers
        Many APIs return rate limit information in headers
        """
        # Common rate limit headers
        limit_headers = {
            "x-ratelimit-limit": "limit",
            "x-ratelimit-remaining": "remaining",
            "x-ratelimit-reset": "reset",
            "retry-after": "retry_after"
        }
        
        for header, field in limit_headers.items():
            if header in response_headers:
                value = response_headers[header]
                logger.debug(f"Rate limit header {header}: {value} for {service}")
                
                # Update adaptive limits based on actual API responses
                if field == "retry_after":
                    try:
                        retry_seconds = float(value)
                        if service in self.adaptive_limits:
                            self.adaptive_limits[service]["base_delay"] = max(
                                self.adaptive_limits[service]["base_delay"],
                                retry_seconds
                            )
                    except ValueError:
                        pass

class RateLimitedAPIClient:
    """
    API client wrapper that automatically handles rate limiting
    """
    
    def __init__(self, rate_limiter: UseAPIRateLimiter):
        self.rate_limiter = rate_limiter
    
    async def make_request(self, service: str, request_func, *args, **kwargs):
        """
        Make rate-limited API request
        
        Args:
            service: Service name for rate limiting
            request_func: Async function that makes the actual request
            *args, **kwargs: Arguments for the request function
            
        Returns:
            Response from the request function
        """
        # Wait for rate limits
        wait_time = await self.rate_limiter.wait_for_rate_limit(service)
        
        # Make the request
        start_time = time.time()
        try:
            response = await request_func(*args, **kwargs)
            response_time = time.time() - start_time
            
            # Record successful request
            await self.rate_limiter.record_request(
                service=service,
                success=True,
                response_time=response_time
            )
            
            return response
            
        except Exception as e:
            response_time = time.time() - start_time
            
            # Record failed request
            await self.rate_limiter.record_request(
                service=service,
                success=False,
                response_time=response_time
            )
            
            # Check if it's a rate limit error
            if "rate limit" in str(e).lower() or "429" in str(e):
                logger.warning(f"Rate limit error detected for {service}: {e}")
                # Increase adaptive delay
                if service in self.rate_limiter.adaptive_limits:
                    current_delay = self.rate_limiter.adaptive_limits[service]["base_delay"]
                    self.rate_limiter.adaptive_limits[service]["base_delay"] = min(
                        current_delay * 1.5, 10.0  # Cap at 10 seconds
                    )
            
            raise

