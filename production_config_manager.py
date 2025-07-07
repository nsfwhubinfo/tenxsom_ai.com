#!/usr/bin/env python3

"""
Tenxsom AI Production Configuration Manager
Centralizes configuration management across all system components
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class UseAPIConfig:
    """UseAPI.net service configuration"""
    bearer_token: str
    email: str
    base_url: str = "https://api.useapi.net/v1"
    
    @classmethod
    def from_env(cls) -> 'UseAPIConfig':
        return cls(
            bearer_token=os.getenv('USEAPI_BEARER_TOKEN', ''),
            email=os.getenv('USEAPI_EMAIL', ''),
            base_url=os.getenv('USEAPI_BASE_URL', 'https://api.useapi.net/v1')
        )


@dataclass 
class GoogleCloudConfig:
    """Google Cloud and AI Ultra configuration"""
    credentials_path: str
    project_id: str
    location: str = "us-central1"
    
    @classmethod
    def from_env(cls) -> 'GoogleCloudConfig':
        return cls(
            credentials_path=os.getenv('GOOGLE_APPLICATION_CREDENTIALS', ''),
            project_id=os.getenv('GOOGLE_AI_ULTRA_PROJECT_ID', ''),
            location=os.getenv('GOOGLE_AI_ULTRA_LOCATION', 'us-central1')
        )


@dataclass
class YouTubeConfig:
    """YouTube Data API v3 configuration"""
    api_key: str
    channel_id: str
    channel_url: str
    oauth_client_secrets: str
    default_privacy: str = "private"
    default_category: int = 22
    default_language: str = "en"
    default_tags: List[str] = None
    
    def __post_init__(self):
        if self.default_tags is None:
            self.default_tags = ["TenxsomAI", "automation", "AI"]
    
    @classmethod
    def from_env(cls) -> 'YouTubeConfig':
        tags_str = os.getenv('DEFAULT_TAGS', 'TenxsomAI,automation,AI')
        tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        
        return cls(
            api_key=os.getenv('YOUTUBE_API_KEY', ''),
            channel_id=os.getenv('YOUTUBE_CHANNEL_ID', ''),
            channel_url=os.getenv('YOUTUBE_CHANNEL_URL', ''),
            oauth_client_secrets=os.getenv('YOUTUBE_OAUTH_CLIENT_SECRETS', ''),
            default_privacy=os.getenv('DEFAULT_PRIVACY_STATUS', 'private'),
            default_category=int(os.getenv('DEFAULT_UPLOAD_CATEGORY', '22')),
            default_language=os.getenv('DEFAULT_LANGUAGE', 'en'),
            default_tags=tags
        )


@dataclass
class TelegramConfig:
    """Telegram bot configuration"""
    bot_token: str
    user_id: str
    bot_username: str
    
    @classmethod
    def from_env(cls) -> 'TelegramConfig':
        return cls(
            bot_token=os.getenv('TELEGRAM_BOT_TOKEN', ''),
            user_id=os.getenv('TELEGRAM_USER_ID', ''),
            bot_username=os.getenv('TELEGRAM_BOT_USERNAME', '')
        )


@dataclass
class HeyGenConfig:
    """HeyGen TTS configuration"""
    api_key: str
    base_url: str = "https://api.heygen.com/v1"
    
    @classmethod
    def from_env(cls) -> 'HeyGenConfig':
        return cls(
            api_key=os.getenv('HEYGEN_API_KEY', ''),
            base_url=os.getenv('HEYGEN_BASE_URL', 'https://api.heygen.com/v1')
        )


@dataclass
class MCPConfig:
    """MCP Server configuration"""
    host: str = "localhost"
    port: int = 8000
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> 'MCPConfig':
        return cls(
            host=os.getenv('MCP_SERVER_HOST', 'localhost'),
            port=int(os.getenv('MCP_SERVER_PORT', '8000')),
            log_level=os.getenv('MCP_LOG_LEVEL', 'INFO')
        )


@dataclass
class ThumbnailConfig:
    """Thumbnail generation configuration"""
    width: int = 1280
    height: int = 720
    quality: int = 90
    
    @classmethod
    def from_env(cls) -> 'ThumbnailConfig':
        return cls(
            width=int(os.getenv('THUMBNAIL_WIDTH', '1280')),
            height=int(os.getenv('THUMBNAIL_HEIGHT', '720')),
            quality=int(os.getenv('THUMBNAIL_QUALITY', '90'))
        )


class ProductionConfigManager:
    """
    Centralized configuration manager for all Tenxsom AI components
    """
    
    def __init__(self, env_file: str = None):
        """
        Initialize configuration manager
        
        Args:
            env_file: Path to .env file (defaults to project root)
        """
        self.project_root = Path(__file__).parent
        self.env_file = env_file or self.project_root / ".env"
        
        # Load environment variables
        if self.env_file.exists():
            load_dotenv(self.env_file)
            logger.info(f"Loaded environment from {self.env_file}")
        else:
            logger.warning(f"Environment file not found: {self.env_file}")
        
        # Initialize configurations
        self.useapi = UseAPIConfig.from_env()
        self.google_cloud = GoogleCloudConfig.from_env()
        self.youtube = YouTubeConfig.from_env()
        self.telegram = TelegramConfig.from_env()
        self.heygen = HeyGenConfig.from_env()
        self.mcp = MCPConfig.from_env()
        self.thumbnail = ThumbnailConfig.from_env()
        
        # System settings
        self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.environment = os.getenv('ENVIRONMENT', 'production')
        
    def validate_configuration(self) -> Dict[str, Dict[str, Any]]:
        """
        Validate all configurations and return status report
        
        Returns:
            Validation status for each service
        """
        validation_results = {
            'useapi': self._validate_useapi(),
            'google_cloud': self._validate_google_cloud(),
            'youtube': self._validate_youtube(),
            'telegram': self._validate_telegram(),
            'heygen': self._validate_heygen(),
            'mcp': self._validate_mcp(),
            'thumbnail': self._validate_thumbnail()
        }
        
        return validation_results
    
    def _validate_useapi(self) -> Dict[str, Any]:
        """Validate UseAPI.net configuration"""
        issues = []
        
        if not self.useapi.bearer_token:
            issues.append("Missing USEAPI_BEARER_TOKEN")
        elif not self.useapi.bearer_token.startswith('user:'):
            issues.append("Invalid UseAPI token format (should start with 'user:')")
            
        if not self.useapi.email:
            issues.append("Missing USEAPI_EMAIL")
            
        return {
            'status': 'valid' if not issues else 'invalid',
            'issues': issues,
            'config': asdict(self.useapi) if not issues else None
        }
    
    def _validate_google_cloud(self) -> Dict[str, Any]:
        """Validate Google Cloud configuration"""
        issues = []
        
        if not self.google_cloud.credentials_path:
            issues.append("Missing GOOGLE_APPLICATION_CREDENTIALS")
        elif not Path(self.google_cloud.credentials_path).exists():
            issues.append(f"Credentials file not found: {self.google_cloud.credentials_path}")
            
        if not self.google_cloud.project_id:
            issues.append("Missing GOOGLE_AI_ULTRA_PROJECT_ID")
            
        return {
            'status': 'valid' if not issues else 'invalid',
            'issues': issues,
            'config': asdict(self.google_cloud) if not issues else None
        }
    
    def _validate_youtube(self) -> Dict[str, Any]:
        """Validate YouTube configuration"""
        issues = []
        
        if not self.youtube.api_key:
            issues.append("Missing YOUTUBE_API_KEY")
        elif not self.youtube.api_key.startswith('AIza'):
            issues.append("Invalid YouTube API key format")
            
        if not self.youtube.channel_id:
            issues.append("Missing YOUTUBE_CHANNEL_ID")
            
        if not self.youtube.oauth_client_secrets:
            issues.append("Missing YOUTUBE_OAUTH_CLIENT_SECRETS")
        elif not Path(self.youtube.oauth_client_secrets).exists():
            issues.append(f"OAuth secrets file not found: {self.youtube.oauth_client_secrets}")
            
        return {
            'status': 'valid' if not issues else 'invalid',
            'issues': issues,
            'config': asdict(self.youtube) if not issues else None
        }
    
    def _validate_telegram(self) -> Dict[str, Any]:
        """Validate Telegram configuration"""
        issues = []
        
        if not self.telegram.bot_token:
            issues.append("Missing TELEGRAM_BOT_TOKEN")
        elif ':' not in self.telegram.bot_token:
            issues.append("Invalid Telegram bot token format")
            
        if not self.telegram.user_id:
            issues.append("Missing TELEGRAM_USER_ID")
            
        return {
            'status': 'valid' if not issues else 'invalid', 
            'issues': issues,
            'config': asdict(self.telegram) if not issues else None
        }
    
    def _validate_heygen(self) -> Dict[str, Any]:
        """Validate HeyGen configuration"""
        issues = []
        
        if not self.heygen.api_key:
            issues.append("Missing HEYGEN_API_KEY")
            
        return {
            'status': 'valid' if not issues else 'warning',  # HeyGen is optional
            'issues': issues,
            'config': asdict(self.heygen) if not issues else None
        }
    
    def _validate_mcp(self) -> Dict[str, Any]:
        """Validate MCP server configuration"""
        return {
            'status': 'valid',
            'issues': [],
            'config': asdict(self.mcp)
        }
    
    def _validate_thumbnail(self) -> Dict[str, Any]:
        """Validate thumbnail configuration"""
        return {
            'status': 'valid',
            'issues': [],
            'config': asdict(self.thumbnail)
        }
    
    def get_useapi_accounts_config(self) -> List[Dict[str, Any]]:
        """
        Generate UseAPI.net account configuration for multi-account setup
        
        Returns:
            List of account configurations
        """
        primary_config = {
            "id": "primary",
            "email": self.useapi.email,
            "bearer_token": self.useapi.bearer_token,
            "models": ["pixverse", "ltx-turbo", "flux"],
            "priority": 1,
            "credit_limit": 5000
        }
        
        # TODO: Add secondary accounts when configured
        accounts = [primary_config]
        
        return accounts
    
    def get_enhanced_router_config(self) -> Dict[str, Any]:
        """
        Get configuration for Enhanced Model Router
        
        Returns:
            Router configuration dictionary
        """
        return {
            "google_ultra_credentials": self.google_cloud.credentials_path,
            "useapi_accounts": self.get_useapi_accounts_config(),
            "strategy": "balanced",
            "health_check_interval": 300
        }
    
    def save_validation_report(self, output_path: str = None) -> str:
        """
        Save configuration validation report to file
        
        Args:
            output_path: Where to save the report
            
        Returns:
            Path to saved report
        """
        validation = self.validate_configuration()
        
        if output_path is None:
            timestamp = Path().cwd().name.replace('-', '_')
            output_path = self.project_root / f"config_validation_report_{timestamp}.json"
        
        report = {
            "validation_timestamp": str(Path().stat().st_mtime),
            "environment": self.environment,
            "project_root": str(self.project_root),
            "env_file": str(self.env_file),
            "validation_results": validation,
            "system_status": self._get_system_status(validation)
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Validation report saved to: {output_path}")
        return str(output_path)
    
    def _get_system_status(self, validation: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall system status"""
        valid_services = sum(1 for v in validation.values() if v['status'] == 'valid')
        warning_services = sum(1 for v in validation.values() if v['status'] == 'warning')
        invalid_services = sum(1 for v in validation.values() if v['status'] == 'invalid')
        total_services = len(validation)
        
        if invalid_services == 0:
            overall_status = "ready"
        elif invalid_services <= 2:
            overall_status = "degraded"
        else:
            overall_status = "not_ready"
        
        return {
            "overall_status": overall_status,
            "valid_services": valid_services,
            "warning_services": warning_services,
            "invalid_services": invalid_services,
            "total_services": total_services,
            "readiness_percentage": (valid_services / total_services) * 100,
            "critical_issues": [
                issue for service in validation.values() 
                for issue in service.get('issues', [])
                if service['status'] == 'invalid'
            ]
        }


def main():
    """Test configuration manager"""
    print("🔧 Tenxsom AI Production Configuration Manager")
    print("=" * 60)
    
    # Initialize manager
    config_manager = ProductionConfigManager()
    
    # Validate configuration
    print("\n🔍 Validating system configuration...")
    validation = config_manager.validate_configuration()
    
    # Display results
    for service, result in validation.items():
        status_icon = {
            'valid': '✅',
            'warning': '⚠️', 
            'invalid': '❌'
        }.get(result['status'], '❓')
        
        print(f"{status_icon} {service.upper()}: {result['status']}")
        
        if result['issues']:
            for issue in result['issues']:
                print(f"   • {issue}")
    
    # System status
    system_status = config_manager._get_system_status(validation)
    print(f"\n📊 System Status: {system_status['overall_status'].upper()}")
    print(f"📈 Readiness: {system_status['readiness_percentage']:.1f}%")
    print(f"✅ Valid Services: {system_status['valid_services']}/{system_status['total_services']}")
    
    if system_status['critical_issues']:
        print(f"\n🚨 Critical Issues:")
        for issue in system_status['critical_issues']:
            print(f"   • {issue}")
    
    # Save report
    report_path = config_manager.save_validation_report()
    print(f"\n📄 Full report saved to: {report_path}")
    
    # Show next steps
    if system_status['overall_status'] == 'ready':
        print(f"\n🎉 System is ready for production!")
        print(f"   • Start MCP server: python useapi-mcp-server/src/useapi_mcp_server/server.py")
        print(f"   • Start chatbot: python chatbot-integration/central-controller.py")
        print(f"   • Test YouTube upload: python youtube-upload-pipeline/tests/test_upload.py")
    else:
        print(f"\n⚠️ System requires additional configuration before production use.")


if __name__ == "__main__":
    main()