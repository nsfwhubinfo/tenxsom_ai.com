"""
Configuration for UseAPI.net MCP Server
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class UseAPIConfig:
    """Configuration for UseAPI.net MCP Server"""
    
    # Authentication
    api_key: Optional[str] = None
    
    # API Settings
    base_url: str = "https://api.useapi.net/v1"
    timeout: int = 300  # 5 minutes
    max_retries: int = 3
    rate_limit: int = 60  # requests per minute
    
    # Webhook Settings
    enable_webhooks: bool = False
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    
    # Polling Settings
    poll_interval: int = 5  # seconds
    max_poll_time: int = 1800  # 30 minutes
    
    # Cache Settings
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hour
    
    # Logging
    log_level: str = "INFO"
    enable_debug: bool = False
    
    def __post_init__(self):
        """Load configuration from environment variables if not provided"""
        if self.api_key is None:
            # Support both environment variable names
            self.api_key = os.getenv("USEAPI_BEARER_TOKEN") or os.getenv("USEAPI_API_KEY")
            
        if not self.api_key:
            raise ValueError("USEAPI_BEARER_TOKEN or USEAPI_API_KEY environment variable is required")
            
        # Override with environment variables if present
        self.base_url = os.getenv("USEAPI_BASE_URL", self.base_url)
        self.timeout = int(os.getenv("USEAPI_TIMEOUT", str(self.timeout)))
        self.max_retries = int(os.getenv("USEAPI_MAX_RETRIES", str(self.max_retries)))
        self.rate_limit = int(os.getenv("USEAPI_RATE_LIMIT", str(self.rate_limit)))
        
        # Webhook settings
        self.webhook_url = os.getenv("USEAPI_WEBHOOK_URL", self.webhook_url)
        self.webhook_secret = os.getenv("USEAPI_WEBHOOK_SECRET", self.webhook_secret)
        if self.webhook_url:
            self.enable_webhooks = True
            
        # Debug settings
        if os.getenv("USEAPI_DEBUG", "").lower() in ("true", "1", "yes"):
            self.enable_debug = True
            self.log_level = "DEBUG"


# Service-specific configurations
SERVICES_CONFIG = {
    "midjourney": {
        "base_path": "/midjourney",
        "max_prompt_length": 4000,
        "supported_models": ["v6.1", "v6.0", "v5.2", "niji6", "niji5"],
        "supported_aspect_ratios": ["1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2"],
        "max_images_blend": 5,
    },
    "runway": {
        "base_path": "/runway",
        "max_prompt_length": 2000,
        "supported_models": ["gen4turbo", "gen3alpha", "gen3turbo"],
        "max_video_duration": 10,
        "supported_aspect_ratios": ["16:9", "9:16", "1:1"],
    },
    "minimax": {
        "base_path": "/minimax",
        "max_prompt_length": 5000,
        "supported_models": ["video-01", "text-01", "m1"],
        "max_video_duration": 6,
        "supported_aspect_ratios": ["16:9", "9:16", "1:1"],
    },
    "kling": {
        "base_path": "/kling",
        "max_prompt_length": 2500,
        "supported_models": ["v1.6", "v1.5"],
        "max_video_duration": 10,
        "supported_aspect_ratios": ["16:9", "9:16", "1:1"],
    },
    "ltx_studio": {
        "base_path": "/ltxstudio",
        "max_prompt_length": 3000,
        "supported_models": ["ltx-video", "veo2", "veo3", "flux"],
        "max_video_duration": 45,
        "supported_aspect_ratios": ["16:9", "9:16", "1:1", "4:3", "3:4"],
    },
    # "pixverse": {
    #     "base_path": "/pixverse",
    #     "max_prompt_length": 2000,
    #     "supported_models": ["v4.5", "v4.0"],
    #     "max_video_duration": 8,
    #     "supported_aspect_ratios": ["16:9", "9:16", "1:1"],
    # },
    "pika": {
        "base_path": "/pika",
        "max_prompt_length": 1500,
        "supported_models": ["v1.0"],
        "max_video_duration": 4,
        "supported_aspect_ratios": ["16:9", "9:16", "1:1"],
    },
    "mureka": {
        "base_path": "/mureka",
        "max_prompt_length": 3000,
        "supported_models": ["skymusic-2.0"],
        "max_duration": 180,  # 3 minutes
    },
    "tempolor": {
        "base_path": "/tempolor",
        "max_prompt_length": 2000,
        "supported_models": ["v1.0"],
        "max_duration": 300,  # 5 minutes
    },
    "insight_face_swap": {
        "base_path": "/faceswap",
        "supported_formats": ["jpg", "jpeg", "png", "webp"],
        "max_file_size": 10 * 1024 * 1024,  # 10MB
    },
}


def get_service_config(service_name: str) -> dict:
    """Get configuration for a specific service"""
    if service_name not in SERVICES_CONFIG:
        raise ValueError(f"Unknown service: {service_name}")
    return SERVICES_CONFIG[service_name]


def validate_prompt(service_name: str, prompt: str) -> bool:
    """Validate prompt length for a service"""
    config = get_service_config(service_name)
    max_length = config.get("max_prompt_length", 2000)
    return len(prompt) <= max_length


def validate_aspect_ratio(service_name: str, aspect_ratio: str) -> bool:
    """Validate aspect ratio for a service"""
    config = get_service_config(service_name)
    supported_ratios = config.get("supported_aspect_ratios", [])
    return aspect_ratio in supported_ratios


def validate_model(service_name: str, model: str) -> bool:
    """Validate model for a service"""
    config = get_service_config(service_name)
    supported_models = config.get("supported_models", [])
    return model in supported_models