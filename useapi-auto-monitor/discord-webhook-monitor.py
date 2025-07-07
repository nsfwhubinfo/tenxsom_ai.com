"""
Discord Webhook Monitor for UseAPI.net Updates
Automatically detects new service announcements and triggers integration updates
"""

import asyncio
import json
import logging
import re
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

import httpx
from asyncio_throttle import Throttler

logger = logging.getLogger(__name__)


@dataclass
class ServiceUpdate:
    """Represents a new service update from UseAPI.net"""
    service_name: str
    api_version: str
    description: str
    is_free: bool
    features: List[str]
    documentation_url: str
    blog_url: Optional[str]
    detected_at: datetime
    discord_message_id: str
    

class UseAPIDiscordMonitor:
    """
    Monitors UseAPI.net Discord announcements and automatically integrates new services
    """
    
    def __init__(self, 
                 discord_bot_token: str,
                 discord_channel_id: str,
                 webhook_url: str,
                 mcp_server_path: str):
        """
        Initialize Discord monitor
        
        Args:
            discord_bot_token: Discord bot token for API access
            discord_channel_id: UseAPI.net announcements channel ID
            webhook_url: Webhook URL for triggering integrations
            mcp_server_path: Path to MCP server for updates
        """
        self.bot_token = discord_bot_token
        self.channel_id = discord_channel_id
        self.webhook_url = webhook_url
        self.mcp_server_path = mcp_server_path
        
        # Rate limiting for Discord API
        self.throttler = Throttler(rate_limit=50, period=60)  # 50 requests per minute
        
        # Track processed messages
        self.processed_messages = set()
        self.last_check_time = datetime.now(timezone.utc)
        
        # Service detection patterns
        self.service_patterns = {
            'new_api': re.compile(r'announce.*release.*\[([^\]]+) API v([^\]]+)\]', re.IGNORECASE),
            'service_name': re.compile(r'\[([^\]]+)\]\(https://useapi\.net/docs/api-([^/]+)/\)'),
            'free_indicator': re.compile(r'\*\*free\*\*|unlimited.*free', re.IGNORECASE),
            'features': re.compile(r'- (.+?)(?=\n|$)', re.MULTILINE),
            'docs_url': re.compile(r'\[([^\]]+)\]\((https://useapi\.net/docs/[^)]+)\)'),
            'blog_url': re.compile(r'\[Example\]\((https://useapi\.net/blog/[^)]+)\)'),
        }
        
    async def start_monitoring(self):
        """Start the Discord monitoring loop"""
        logger.info("Starting UseAPI.net Discord monitor...")
        
        while True:
            try:
                await self.check_for_updates()
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def check_for_updates(self):
        """Check Discord channel for new service announcements"""
        async with self.throttler:
            try:
                messages = await self.fetch_recent_messages()
                
                for message in messages:
                    if message['id'] not in self.processed_messages:
                        update = await self.parse_service_update(message)
                        if update:
                            await self.process_service_update(update)
                            self.processed_messages.add(message['id'])
                
                self.last_check_time = datetime.now(timezone.utc)
                
            except Exception as e:
                logger.error(f"Error checking for updates: {e}")
    
    async def fetch_recent_messages(self) -> List[Dict[str, Any]]:
        """Fetch recent messages from Discord channel"""
        url = f"https://discord.com/api/v10/channels/{self.channel_id}/messages"
        headers = {
            "Authorization": f"Bot {self.bot_token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "limit": 50,
            "after": int(self.last_check_time.timestamp() * 1000) << 22  # Convert to snowflake
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
    
    async def parse_service_update(self, message: Dict[str, Any]) -> Optional[ServiceUpdate]:
        """Parse Discord message to extract service update information"""
        content = message.get('content', '')
        
        # Check if this is a service announcement
        api_match = self.service_patterns['new_api'].search(content)
        if not api_match:
            return None
        
        service_name = api_match.group(1)
        api_version = api_match.group(2)
        
        # Extract documentation URL
        docs_match = self.service_patterns['docs_url'].search(content)
        docs_url = docs_match.group(2) if docs_match else ""
        
        # Extract blog URL
        blog_match = self.service_patterns['blog_url'].search(content)
        blog_url = blog_match.group(1) if blog_match else None
        
        # Check if free
        is_free = bool(self.service_patterns['free_indicator'].search(content))
        
        # Extract features
        features = self.service_patterns['features'].findall(content)
        
        # Create service update
        update = ServiceUpdate(
            service_name=service_name,
            api_version=api_version,
            description=content[:500],  # First 500 chars
            is_free=is_free,
            features=features,
            documentation_url=docs_url,
            blog_url=blog_url,
            detected_at=datetime.now(timezone.utc),
            discord_message_id=message['id']
        )
        
        return update
    
    async def process_service_update(self, update: ServiceUpdate):
        """Process a detected service update"""
        logger.info(f"🚨 New service detected: {update.service_name} v{update.api_version}")
        
        # Send notification
        await self.send_notification(update)
        
        # Auto-generate MCP integration
        await self.auto_generate_integration(update)
        
        # Trigger webhook for external processing
        await self.trigger_webhook(update)
    
    async def send_notification(self, update: ServiceUpdate):
        """Send notification about new service"""
        notification = {
            "type": "new_useapi_service",
            "service": update.service_name,
            "version": update.api_version,
            "is_free": update.is_free,
            "features_count": len(update.features),
            "docs_url": update.documentation_url,
            "detected_at": update.detected_at.isoformat(),
            "urgent": update.is_free and "unlimited" in update.description.lower()
        }
        
        logger.info(f"📢 Notification: {json.dumps(notification, indent=2)}")
        
        # Here you could integrate with your notification system
        # (Slack, email, SMS, etc.)
    
    async def auto_generate_integration(self, update: ServiceUpdate):
        """Auto-generate MCP server integration for new service"""
        logger.info(f"🔧 Auto-generating integration for {update.service_name}...")
        
        # Generate tool template
        tool_code = self.generate_mcp_tool_template(update)
        
        # Save to MCP server
        tool_file_path = f"{self.mcp_server_path}/src/useapi_mcp_server/tools/{update.service_name.lower().replace(' ', '_')}.py"
        
        try:
            with open(tool_file_path, 'w') as f:
                f.write(tool_code)
            
            logger.info(f"✅ Generated MCP tool: {tool_file_path}")
            
            # Update server registration
            await self.update_server_registration(update)
            
        except Exception as e:
            logger.error(f"❌ Failed to generate tool: {e}")
    
    def generate_mcp_tool_template(self, update: ServiceUpdate) -> str:
        """Generate MCP tool template for new service"""
        service_class_name = update.service_name.replace(' ', '').replace('-', '') + 'Tools'
        service_identifier = update.service_name.lower().replace(' ', '_').replace('-', '_')
        
        template = f'''"""
{update.service_name} tools for UseAPI.net MCP Server
Auto-generated on {update.detected_at.isoformat()}

Service: {update.service_name} v{update.api_version}
Documentation: {update.documentation_url}
Features: {', '.join(update.features[:3])}...
"""

import logging
from typing import Any, Dict

from .base import BaseTool
from ..exceptions import UseAPIValidationError

logger = logging.getLogger(__name__)


class {service_class_name}(BaseTool):
    """Tools for {update.service_name}"""
    
    def __init__(self, client):
        super().__init__(client, "{service_identifier}")
    
    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute {update.service_name} tool"""
        try:
            self.validate_arguments(arguments)
            
            if tool_name == "{service_identifier}_generate":
                return await self.generate(arguments)
            else:
                raise UseAPIValidationError(f"Unknown {update.service_name} tool: {{tool_name}}")
                
        except Exception as e:
            logger.exception(f"Error executing {{tool_name}}")
            return self.format_error(e, tool_name)
    
    async def generate(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content using {update.service_name}"""
        # Extract common parameters
        prompt = arguments.get("prompt", "")
        model = arguments.get("model", "default")
        
        data = {{
            "prompt": prompt,
            "model": model,
        }}
        
        # Add service-specific parameters based on detected features
'''
        
        # Add feature-specific parameters
        if any("voice" in feature.lower() for feature in update.features):
            template += '''        if "voice" in arguments:
            data["voice"] = arguments["voice"]
        '''
        
        if any("tts" in feature.lower() or "speech" in feature.lower() for feature in update.features):
            template += '''        if "text" in arguments:
            data["text"] = arguments["text"]
        '''
        
        template += f'''
        response = await self.make_request(
            f"{{self.get_base_path()}}/generate",
            data,
            "generate",
            wait_for_completion=True
        )
        
        return self.format_response(response, "generate")
'''
        
        return template
    
    async def update_server_registration(self, update: ServiceUpdate):
        """Update MCP server to register new tool"""
        # This would modify the server.py file to include the new tool
        # For now, just log the needed registration
        
        service_name = update.service_name.lower().replace(' ', '_').replace('-', '_')
        tool_name = f"{service_name}_generate"
        
        registration_code = f'''
        types.Tool(
            name="{tool_name}",
            description="Generate content using {update.service_name}",
            inputSchema={{
                "type": "object",
                "properties": {{
                    "prompt": {{
                        "type": "string",
                        "description": "Text prompt for generation"
                    }},
                    "model": {{
                        "type": "string", 
                        "description": "{update.service_name} model to use",
                        "default": "default"
                    }}
                }},
                "required": ["prompt"]
            }}
        ),'''
        
        logger.info(f"📝 Tool registration needed:\n{registration_code}")
    
    async def trigger_webhook(self, update: ServiceUpdate):
        """Trigger webhook for external processing"""
        webhook_data = {
            "event": "new_useapi_service",
            "service": asdict(update),
            "action_required": {
                "create_account": True,
                "update_mcp_server": True,
                "test_integration": True
            },
            "priority": "high" if update.is_free else "medium"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=webhook_data,
                    timeout=30
                )
                response.raise_for_status()
                logger.info(f"✅ Webhook triggered successfully")
                
        except Exception as e:
            logger.error(f"❌ Webhook failed: {e}")


class UseAPIAutoUpdater:
    """
    Handles automatic updates to the MCP server when new services are detected
    """
    
    def __init__(self, mcp_server_path: str, config_path: str):
        self.mcp_server_path = mcp_server_path
        self.config_path = config_path
        
    async def process_webhook(self, webhook_data: Dict[str, Any]):
        """Process incoming webhook for service updates"""
        if webhook_data.get("event") != "new_useapi_service":
            return
        
        service_data = webhook_data["service"]
        service_name = service_data["service_name"]
        
        logger.info(f"🔄 Processing auto-update for {service_name}")
        
        # Update service configuration
        await self.update_service_config(service_data)
        
        # Add to MCP tool registry
        await self.register_mcp_tool(service_data)
        
        # Create integration tests
        await self.create_integration_tests(service_data)
        
        logger.info(f"✅ Auto-update complete for {service_name}")
    
    async def update_service_config(self, service_data: Dict[str, Any]):
        """Update service configuration with new service"""
        config_file = f"{self.config_path}/services_config.json"
        
        try:
            # Load existing config
            with open(config_file, 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            config = {"services": {}}
        
        # Add new service
        service_name = service_data["service_name"].lower().replace(' ', '_')
        config["services"][service_name] = {
            "name": service_data["service_name"],
            "version": service_data["api_version"],
            "base_path": f"/api-{service_name.replace('_', '-')}-{service_data['api_version']}",
            "is_free": service_data["is_free"],
            "features": service_data["features"],
            "docs_url": service_data["documentation_url"],
            "added_date": service_data["detected_at"],
            "auto_generated": True
        }
        
        # Save updated config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"📝 Updated service config: {service_name}")
    
    async def register_mcp_tool(self, service_data: Dict[str, Any]):
        """Register new tool in MCP server"""
        # This would modify the server.py imports and tool registration
        # For production, you'd implement actual file modification
        logger.info(f"🔧 MCP tool registration: {service_data['service_name']}")
    
    async def create_integration_tests(self, service_data: Dict[str, Any]):
        """Create integration tests for new service"""
        service_name = service_data["service_name"].lower().replace(' ', '_')
        test_file = f"{self.mcp_server_path}/tests/test_{service_name}.py"
        
        test_code = f'''"""
Auto-generated tests for {service_data["service_name"]}
Generated on {service_data["detected_at"]}
"""

import pytest
from useapi_mcp_server.tools.{service_name} import {service_data["service_name"].replace(' ', '')}Tools

class Test{service_data["service_name"].replace(' ', '')}:
    """Test {service_data["service_name"]} integration"""
    
    @pytest.mark.asyncio
    async def test_{service_name}_generate(self):
        """Test basic generation"""
        # Auto-generated test - customize as needed
        pass
'''
        
        try:
            with open(test_file, 'w') as f:
                f.write(test_code)
            logger.info(f"📝 Created test file: {test_file}")
        except Exception as e:
            logger.error(f"❌ Failed to create tests: {e}")


# Example configuration
async def main():
    """Example usage"""
    
    # Configuration
    discord_token = "YOUR_DISCORD_BOT_TOKEN"
    channel_id = "USEAPI_ANNOUNCEMENTS_CHANNEL_ID"
    webhook_url = "https://your-webhook-endpoint.com/useapi-updates"
    mcp_server_path = "/home/golde/tenxsom-ai-vertex/useapi-mcp-server"
    
    # Initialize monitor
    monitor = UseAPIDiscordMonitor(
        discord_bot_token=discord_token,
        discord_channel_id=channel_id,
        webhook_url=webhook_url,
        mcp_server_path=mcp_server_path
    )
    
    # Start monitoring
    await monitor.start_monitoring()


if __name__ == "__main__":
    asyncio.run(main())