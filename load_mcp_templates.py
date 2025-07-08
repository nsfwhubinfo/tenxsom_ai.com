#!/usr/bin/env python3
"""
Load foundational MCP templates into the database
"""

import asyncio
import json
import os
import logging
from pathlib import Path

# Add the MCP server source to the path
import sys
sys.path.append('/home/golde/tenxsom-ai-vertex/useapi-mcp-server/src')

from useapi_mcp_server.database import get_database, close_database

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def load_template_from_file(file_path: Path, db):
    """Load a single template from a JSON file"""
    try:
        with open(file_path, 'r') as f:
            template_data = json.load(f)
        
        template_id = await db.store_template(template_data)
        logger.info(f"Loaded template '{template_data.get('template_name')}' from {file_path.name} (ID: {template_id})")
        return template_id
    
    except Exception as e:
        logger.error(f"Failed to load template from {file_path}: {e}")
        return None


async def load_all_templates():
    """Load all MCP templates from the templates directory"""
    templates_dir = Path('/home/golde/tenxsom-ai-vertex/mcp-templates')
    
    if not templates_dir.exists():
        logger.error(f"Templates directory not found: {templates_dir}")
        return
    
    # Get database connection
    db = await get_database()
    
    # Find all JSON template files
    template_files = list(templates_dir.glob('*.json'))
    
    if not template_files:
        logger.warning(f"No template files found in {templates_dir}")
        return
    
    logger.info(f"Found {len(template_files)} template files to load")
    
    # Load each template
    loaded_count = 0
    for template_file in template_files:
        template_id = await load_template_from_file(template_file, db)
        if template_id:
            loaded_count += 1
    
    logger.info(f"Successfully loaded {loaded_count} out of {len(template_files)} templates")
    
    # List all templates in database
    templates = await db.list_templates(limit=100)
    logger.info(f"Database now contains {len(templates)} templates:")
    
    for template in templates:
        logger.info(f"  - {template['template_name']} ({template['archetype']}, {template['content_tier']})")
    
    await close_database()


async def main():
    """Main entry point"""
    logger.info("Starting MCP template loading process...")
    try:
        await load_all_templates()
        logger.info("Template loading completed successfully!")
    except Exception as e:
        logger.error(f"Template loading failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())