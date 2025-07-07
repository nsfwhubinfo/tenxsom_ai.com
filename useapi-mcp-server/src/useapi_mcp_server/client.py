"""
HTTP client for UseAPI.net API
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, Union, AsyncGenerator
from urllib.parse import urljoin
import time

import httpx
from asyncio_throttle import Throttler

from .config import UseAPIConfig
from .exceptions import (
    UseAPIError,
    UseAPITimeoutError,
    UseAPIRateLimitError,
    handle_api_error,
)

logger = logging.getLogger(__name__)


class UseAPIClient:
    """HTTP client for UseAPI.net API with rate limiting and error handling"""
    
    def __init__(self, config: UseAPIConfig):
        self.config = config
        self.base_url = config.base_url
        self.api_key = config.api_key
        
        # Rate limiting
        self.throttler = Throttler(rate_limit=config.rate_limit, period=60)
        
        # HTTP client with timeout
        timeout = httpx.Timeout(
            timeout=config.timeout,
            connect=30.0,
            read=config.timeout,
            write=30.0
        )
        
        self.client = httpx.AsyncClient(
            timeout=timeout,
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "UseAPI-MCP-Server/1.0.0",
            },
        )
        
        # Job tracking
        self.active_jobs: Dict[str, Dict[str, Any]] = {}
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
        
    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        service: Optional[str] = None,
        operation: Optional[str] = None,
        retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to UseAPI.net with rate limiting and retries
        """
        if retries is None:
            retries = self.config.max_retries
            
        url = urljoin(self.base_url, endpoint.lstrip("/"))
        
        for attempt in range(retries + 1):
            try:
                # Rate limiting
                async with self.throttler:
                    if files:
                        # File upload request
                        response = await self.client.request(
                            method,
                            url,
                            data=data,
                            files=files,
                        )
                    else:
                        # JSON request
                        response = await self.client.request(
                            method,
                            url,
                            json=data,
                        )
                    
                    # Log request for debugging
                    if self.config.enable_debug:
                        logger.debug(
                            f"{method} {url} -> {response.status_code} "
                            f"({len(response.content)} bytes)"
                        )
                    
                    # Handle successful responses
                    if response.status_code < 400:
                        try:
                            return response.json()
                        except json.JSONDecodeError:
                            return {"data": response.content, "content_type": response.headers.get("content-type")}
                    
                    # Handle error responses
                    try:
                        error_data = response.json()
                    except json.JSONDecodeError:
                        error_data = {"error": {"message": response.text}}
                    
                    # Check if we should retry
                    if response.status_code in (429, 503) and attempt < retries:
                        # Rate limit or service unavailable - wait and retry
                        retry_after = int(response.headers.get("retry-after", 5))
                        logger.warning(
                            f"Rate limited or service unavailable, retrying after {retry_after}s "
                            f"(attempt {attempt + 1}/{retries + 1})"
                        )
                        await asyncio.sleep(retry_after)
                        continue
                    
                    # Raise appropriate exception
                    raise handle_api_error(
                        response.status_code,
                        error_data,
                        service=service,
                        operation=operation,
                    )
                    
            except httpx.TimeoutException:
                if attempt < retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(
                        f"Request timeout, retrying in {wait_time}s "
                        f"(attempt {attempt + 1}/{retries + 1})"
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise UseAPITimeoutError(
                        f"Request timed out after {retries + 1} attempts",
                        service=service,
                        operation=operation,
                    )
            except httpx.HTTPError as e:
                if attempt < retries:
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"HTTP error: {e}, retrying in {wait_time}s "
                        f"(attempt {attempt + 1}/{retries + 1})"
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise UseAPIError(
                        f"HTTP error: {e}",
                        service=service,
                        operation=operation,
                    )
                    
        # Should not reach here
        raise UseAPIError(
            f"Failed after {retries + 1} attempts",
            service=service,
            operation=operation,
        )
    
    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a GET request"""
        return await self.request("GET", endpoint, **kwargs)
    
    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make a POST request"""
        return await self.request("POST", endpoint, data=data, **kwargs)
    
    async def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make a PUT request"""
        return await self.request("PUT", endpoint, data=data, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a DELETE request"""
        return await self.request("DELETE", endpoint, **kwargs)
    
    async def upload_file(
        self,
        endpoint: str,
        file_data: bytes,
        filename: str,
        mime_type: str = "image/jpeg",
        additional_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Upload a file to the API"""
        files = {
            "file": (filename, file_data, mime_type)
        }
        
        return await self.request(
            "POST",
            endpoint,
            data=additional_data,
            files=files,
            **kwargs
        )
    
    async def wait_for_job(
        self,
        job_id: str,
        service: str,
        poll_interval: Optional[int] = None,
        max_wait_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Wait for a job to complete by polling its status
        """
        if poll_interval is None:
            poll_interval = self.config.poll_interval
        if max_wait_time is None:
            max_wait_time = self.config.max_poll_time
            
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                # Get job status
                status_response = await self.get(
                    f"/{service}/jobs/{job_id}",
                    service=service,
                    operation="get_job_status",
                )
                
                status = status_response.get("status", "unknown")
                
                # Track job
                self.active_jobs[job_id] = {
                    "service": service,
                    "status": status,
                    "last_update": time.time(),
                    "response": status_response,
                }
                
                if status in ("completed", "success"):
                    logger.info(f"Job {job_id} completed successfully")
                    return status_response
                elif status in ("failed", "error", "cancelled"):
                    error_message = status_response.get("error", {}).get("message", "Job failed")
                    raise UseAPIError(
                        f"Job {job_id} failed: {error_message}",
                        service=service,
                        operation="job_execution",
                    )
                elif status in ("processing", "queued", "pending"):
                    # Still processing, continue polling
                    await asyncio.sleep(poll_interval)
                    continue
                else:
                    # Unknown status, continue polling
                    logger.warning(f"Unknown job status for {job_id}: {status}")
                    await asyncio.sleep(poll_interval)
                    continue
                    
            except UseAPINotFoundError:
                # Job not found - might be completed and cleaned up
                logger.warning(f"Job {job_id} not found, may have been completed")
                break
            except Exception as e:
                logger.error(f"Error polling job {job_id}: {e}")
                await asyncio.sleep(poll_interval)
                continue
        
        # Timeout
        raise UseAPITimeoutError(
            f"Job {job_id} did not complete within {max_wait_time} seconds",
            service=service,
            operation="job_execution",
        )
    
    async def get_job_status(self, job_id: str, service: str) -> Dict[str, Any]:
        """Get the current status of a job"""
        return await self.get(
            f"/{service}/jobs/{job_id}",
            service=service,
            operation="get_job_status",
        )
    
    async def list_jobs(
        self,
        service: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """List jobs with optional filtering"""
        params = {"limit": limit}
        if status:
            params["status"] = status
            
        endpoint = f"/{service}/jobs" if service else "/jobs"
        return await self.get(endpoint, data=params)
    
    async def cancel_job(self, job_id: str, service: str) -> Dict[str, Any]:
        """Cancel a running job"""
        return await self.delete(
            f"/{service}/jobs/{job_id}",
            service=service,
            operation="cancel_job",
        )
    
    def get_active_jobs(self) -> Dict[str, Dict[str, Any]]:
        """Get all currently tracked jobs"""
        return self.active_jobs.copy()
    
    async def stream_job_updates(
        self,
        job_id: str,
        service: str,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream job status updates until completion
        """
        start_time = time.time()
        
        while time.time() - start_time < self.config.max_poll_time:
            try:
                status_response = await self.get_job_status(job_id, service)
                status = status_response.get("status", "unknown")
                
                yield status_response
                
                if status in ("completed", "success", "failed", "error", "cancelled"):
                    break
                    
                await asyncio.sleep(self.config.poll_interval)
                
            except Exception as e:
                logger.error(f"Error streaming job {job_id}: {e}")
                break