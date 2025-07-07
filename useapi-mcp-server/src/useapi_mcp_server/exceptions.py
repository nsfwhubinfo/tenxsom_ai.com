"""
Custom exceptions for UseAPI.net MCP Server
"""

from typing import Optional, Dict, Any


class UseAPIError(Exception):
    """Base exception for UseAPI.net operations"""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        service: Optional[str] = None,
        operation: Optional[str] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        self.service = service
        self.operation = operation
        super().__init__(message)
    
    def __str__(self) -> str:
        parts = [self.message]
        if self.service:
            parts.append(f"Service: {self.service}")
        if self.operation:
            parts.append(f"Operation: {self.operation}")
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        return " | ".join(parts)


class UseAPIAuthenticationError(UseAPIError):
    """Authentication failed with UseAPI.net"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, status_code=401, **kwargs)


class UseAPIRateLimitError(UseAPIError):
    """Rate limit exceeded for UseAPI.net"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs
    ):
        self.retry_after = retry_after
        super().__init__(message, status_code=429, **kwargs)


class UseAPITimeoutError(UseAPIError):
    """Request timed out"""
    
    def __init__(self, message: str = "Request timed out", **kwargs):
        super().__init__(message, **kwargs)


class UseAPINotFoundError(UseAPIError):
    """Resource not found"""
    
    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, status_code=404, **kwargs)


class UseAPIValidationError(UseAPIError):
    """Input validation failed"""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        self.field = field
        super().__init__(message, status_code=400, **kwargs)


class UseAPIServiceUnavailableError(UseAPIError):
    """Service is temporarily unavailable"""
    
    def __init__(self, message: str = "Service temporarily unavailable", **kwargs):
        super().__init__(message, status_code=503, **kwargs)


class UseAPIJobError(UseAPIError):
    """Job execution failed"""
    
    def __init__(
        self,
        message: str,
        job_id: Optional[str] = None,
        job_status: Optional[str] = None,
        **kwargs
    ):
        self.job_id = job_id
        self.job_status = job_status
        super().__init__(message, **kwargs)


class UseAPIQuotaExceededError(UseAPIError):
    """API quota exceeded"""
    
    def __init__(
        self,
        message: str = "API quota exceeded",
        quota_type: Optional[str] = None,
        reset_time: Optional[int] = None,
        **kwargs
    ):
        self.quota_type = quota_type
        self.reset_time = reset_time
        super().__init__(message, status_code=429, **kwargs)


def handle_api_error(
    response_status: int,
    response_data: Dict[str, Any],
    service: Optional[str] = None,
    operation: Optional[str] = None,
) -> UseAPIError:
    """
    Convert API response to appropriate exception
    """
    error_message = response_data.get("error", {}).get("message", "Unknown error")
    error_code = response_data.get("error", {}).get("code", "unknown")
    
    # Common error mappings
    if response_status == 401:
        return UseAPIAuthenticationError(
            message=error_message,
            response_data=response_data,
            service=service,
            operation=operation,
        )
    elif response_status == 403:
        if "quota" in error_message.lower() or "limit" in error_message.lower():
            return UseAPIQuotaExceededError(
                message=error_message,
                response_data=response_data,
                service=service,
                operation=operation,
            )
        return UseAPIError(
            message=error_message,
            status_code=response_status,
            response_data=response_data,
            service=service,
            operation=operation,
        )
    elif response_status == 404:
        return UseAPINotFoundError(
            message=error_message,
            response_data=response_data,
            service=service,
            operation=operation,
        )
    elif response_status == 429:
        retry_after = response_data.get("retry_after")
        return UseAPIRateLimitError(
            message=error_message,
            retry_after=retry_after,
            response_data=response_data,
            service=service,
            operation=operation,
        )
    elif response_status == 503:
        return UseAPIServiceUnavailableError(
            message=error_message,
            response_data=response_data,
            service=service,
            operation=operation,
        )
    elif 400 <= response_status < 500:
        return UseAPIValidationError(
            message=error_message,
            response_data=response_data,
            service=service,
            operation=operation,
        )
    else:
        return UseAPIError(
            message=error_message,
            status_code=response_status,
            response_data=response_data,
            service=service,
            operation=operation,
        )