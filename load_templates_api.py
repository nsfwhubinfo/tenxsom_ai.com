#!/usr/bin/env python3
"""
Load MCP templates into the MCP server via API
"""

import asyncio
import json
import logging
import os
import httpx
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def load_templates_via_api():
    """Load all templates through the MCP server API"""
    # Get MCP server URL from environment or use default
    mcp_server_url = os.getenv('MCP_SERVER_URL', 'https://tenxsom-mcp-server-hpkm6siuqq-uc.a.run.app')
    
    template_dir = Path("mcp-templates")
    if not template_dir.exists():
        logger.error(f"Template directory not found: {template_dir}")
        return
    
    # Collect all templates
    templates = []
    for template_file in template_dir.glob("*.json"):
        try:
            with open(template_file, 'r') as f:
                template_data = json.load(f)
            templates.append(template_data)
            logger.info(f"📖 Read template: {template_data.get('template_name', template_file.name)}")
        except Exception as e:
            logger.error(f"❌ Failed to read {template_file.name}: {e}")
    
    if not templates:
        logger.warning("No templates found to load")
        return
    
    # Send batch request to API
    async with httpx.AsyncClient() as client:
        logger.info(f"📤 Sending {len(templates)} templates to {mcp_server_url}")
        try:
            response = await client.post(
                f"{mcp_server_url}/api/batch/templates",
                json=templates,
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"\n✅ Batch upload complete!")
                logger.info(f"📊 Summary: {result['successful']} loaded, {result['failed']} errors")
                
                # Show details if there were errors
                if result['failed'] > 0:
                    for item in result['results']:
                        if item['status'] == 'error':
                            logger.error(f"  ❌ {item['template_name']}: {item['error']}")
            else:
                logger.error(f"❌ API request failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Request failed: {e}")


async def verify_templates():
    """Verify templates were loaded correctly"""
    mcp_server_url = os.getenv('MCP_SERVER_URL', 'https://tenxsom-mcp-server-hpkm6siuqq-uc.a.run.app')
    
    async with httpx.AsyncClient() as client:
        try:
            # Check status
            response = await client.get(f"{mcp_server_url}/api/status")
            if response.status_code == 200:
                status = response.json()
                logger.info(f"\n📊 Server Status:")
                logger.info(f"  - Template count: {status['template_count']}")
                logger.info(f"  - Tier distribution: {status['tier_distribution']}")
                logger.info(f"  - Archetype distribution: {status['archetype_distribution']}")
            
            # List templates
            response = await client.get(f"{mcp_server_url}/api/templates")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"\n📋 Templates loaded ({data['count']} total):")
                for template in data['templates'][:5]:  # Show first 5
                    logger.info(f"  - {template['template_name']} ({template['archetype']}, {template['content_tier']})")
                if data['count'] > 5:
                    logger.info(f"  ... and {data['count'] - 5} more")
                    
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")


async def main():
    """Main function"""
    logger.info("🚀 Starting MCP template loader...")
    
    # Load templates
    await load_templates_via_api()
    
    # Verify they were loaded
    await verify_templates()
    
    logger.info("\n✅ Template loading complete!")


if __name__ == "__main__":
    asyncio.run(main())