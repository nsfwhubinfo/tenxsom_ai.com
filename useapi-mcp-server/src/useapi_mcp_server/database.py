"""
Database schema and operations for MCP templates
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
import asyncpg
import os

logger = logging.getLogger(__name__)


class MCPTemplateDatabase:
    """Database manager for MCP templates"""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize database connection"""
        self.database_url = database_url or os.getenv(
            'DATABASE_URL', 
            'postgresql://localhost:5432/tenxsom_mcp'
        )
        self.pool: Optional[asyncpg.Pool] = None
    
    async def init_pool(self):
        """Initialize connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database connection pool initialized")
            
            # Create tables if they don't exist
            await self.create_tables()
            
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    async def close_pool(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("Database connection pool closed")
    
    async def create_tables(self):
        """Create MCP template tables"""
        create_sql = """
        CREATE TABLE IF NOT EXISTS mcp_templates (
            id SERIAL PRIMARY KEY,
            template_name VARCHAR(255) UNIQUE NOT NULL,
            description TEXT,
            archetype VARCHAR(100) NOT NULL,
            target_platform VARCHAR(50) DEFAULT 'youtube',
            content_tier VARCHAR(20) DEFAULT 'standard',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            template_data JSONB NOT NULL,
            performance_metrics JSONB DEFAULT '{}',
            usage_count INTEGER DEFAULT 0,
            success_rate DECIMAL(5,2) DEFAULT 0.00,
            avg_engagement_score DECIMAL(5,2) DEFAULT 0.00
        );
        
        CREATE INDEX IF NOT EXISTS idx_mcp_templates_archetype ON mcp_templates(archetype);
        CREATE INDEX IF NOT EXISTS idx_mcp_templates_platform ON mcp_templates(target_platform);
        CREATE INDEX IF NOT EXISTS idx_mcp_templates_tier ON mcp_templates(content_tier);
        CREATE INDEX IF NOT EXISTS idx_mcp_templates_performance ON mcp_templates(success_rate DESC, avg_engagement_score DESC);
        
        CREATE TABLE IF NOT EXISTS mcp_template_executions (
            id SERIAL PRIMARY KEY,
            template_id INTEGER REFERENCES mcp_templates(id) ON DELETE CASCADE,
            execution_id VARCHAR(255) UNIQUE NOT NULL,
            context_variables JSONB NOT NULL,
            generated_plan JSONB NOT NULL,
            execution_status VARCHAR(50) DEFAULT 'pending',
            started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP WITH TIME ZONE,
            error_message TEXT,
            performance_data JSONB DEFAULT '{}'
        );
        
        CREATE INDEX IF NOT EXISTS idx_template_executions_template_id ON mcp_template_executions(template_id);
        CREATE INDEX IF NOT EXISTS idx_template_executions_status ON mcp_template_executions(execution_status);
        CREATE INDEX IF NOT EXISTS idx_template_executions_execution_id ON mcp_template_executions(execution_id);
        """
        
        async with self.pool.acquire() as conn:
            await conn.execute(create_sql)
        logger.info("MCP template tables created/verified")
    
    async def store_template(self, template_data: Dict[str, Any]) -> int:
        """Store a new MCP template"""
        insert_sql = """
        INSERT INTO mcp_templates (
            template_name, description, archetype, target_platform, 
            content_tier, template_data
        ) VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (template_name) 
        DO UPDATE SET 
            description = EXCLUDED.description,
            archetype = EXCLUDED.archetype,
            target_platform = EXCLUDED.target_platform,
            content_tier = EXCLUDED.content_tier,
            template_data = EXCLUDED.template_data,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id;
        """
        
        # Extract metadata from template
        template_name = template_data.get('template_name')
        description = template_data.get('description', '')
        archetype = template_data.get('archetype', 'generic')
        target_platform = template_data.get('target_platform', 'youtube')
        content_tier = template_data.get('content_tier', 'standard')
        
        if not template_name:
            raise ValueError("Template must have a template_name field")
        
        async with self.pool.acquire() as conn:
            template_id = await conn.fetchval(
                insert_sql,
                template_name, description, archetype, target_platform,
                content_tier, json.dumps(template_data)
            )
        
        logger.info(f"Stored template '{template_name}' with ID {template_id}")
        return template_id
    
    async def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve a template by name"""
        select_sql = """
        SELECT id, template_name, description, archetype, target_platform,
               content_tier, template_data, created_at, updated_at,
               usage_count, success_rate, avg_engagement_score
        FROM mcp_templates 
        WHERE template_name = $1;
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(select_sql, template_name)
        
        if not row:
            return None
        
        template_data = json.loads(row['template_data'])
        template_data.update({
            'id': row['id'],
            'created_at': row['created_at'].isoformat(),
            'updated_at': row['updated_at'].isoformat(),
            'usage_count': row['usage_count'],
            'success_rate': float(row['success_rate']) if row['success_rate'] else 0.0,
            'avg_engagement_score': float(row['avg_engagement_score']) if row['avg_engagement_score'] else 0.0
        })
        
        return template_data
    
    async def list_templates(
        self, 
        archetype: Optional[str] = None,
        target_platform: Optional[str] = None,
        content_tier: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List templates with optional filtering"""
        where_clauses = []
        params = []
        param_count = 0
        
        if archetype:
            param_count += 1
            where_clauses.append(f"archetype = ${param_count}")
            params.append(archetype)
        
        if target_platform:
            param_count += 1
            where_clauses.append(f"target_platform = ${param_count}")
            params.append(target_platform)
        
        if content_tier:
            param_count += 1
            where_clauses.append(f"content_tier = ${param_count}")
            params.append(content_tier)
        
        where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        param_count += 1
        select_sql = f"""
        SELECT template_name, description, archetype, target_platform,
               content_tier, created_at, usage_count, success_rate, avg_engagement_score
        FROM mcp_templates 
        {where_clause}
        ORDER BY success_rate DESC, avg_engagement_score DESC, usage_count DESC
        LIMIT ${param_count};
        """
        params.append(limit)
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(select_sql, *params)
        
        return [dict(row) for row in rows]
    
    async def increment_usage(self, template_name: str):
        """Increment usage count for a template"""
        update_sql = """
        UPDATE mcp_templates 
        SET usage_count = usage_count + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE template_name = $1;
        """
        
        async with self.pool.acquire() as conn:
            await conn.execute(update_sql, template_name)
    
    async def store_execution(
        self, 
        template_id: int,
        execution_id: str,
        context_variables: Dict[str, Any],
        generated_plan: Dict[str, Any]
    ) -> int:
        """Store template execution record"""
        insert_sql = """
        INSERT INTO mcp_template_executions (
            template_id, execution_id, context_variables, generated_plan
        ) VALUES ($1, $2, $3, $4)
        RETURNING id;
        """
        
        async with self.pool.acquire() as conn:
            exec_id = await conn.fetchval(
                insert_sql,
                template_id, execution_id,
                json.dumps(context_variables),
                json.dumps(generated_plan)
            )
        
        logger.info(f"Stored execution record for template ID {template_id}")
        return exec_id
    
    async def update_execution_status(
        self,
        execution_id: str,
        status: str,
        error_message: Optional[str] = None,
        performance_data: Optional[Dict[str, Any]] = None
    ):
        """Update execution status"""
        update_sql = """
        UPDATE mcp_template_executions 
        SET execution_status = $2,
            completed_at = CASE WHEN $2 IN ('completed', 'failed') THEN CURRENT_TIMESTAMP ELSE completed_at END,
            error_message = $3,
            performance_data = COALESCE($4, performance_data)
        WHERE execution_id = $1;
        """
        
        async with self.pool.acquire() as conn:
            await conn.execute(
                update_sql,
                execution_id, status, error_message,
                json.dumps(performance_data) if performance_data else None
            )
    
    async def get_template_analytics(self, template_name: str) -> Dict[str, Any]:
        """Get analytics for a specific template"""
        analytics_sql = """
        SELECT 
            t.template_name,
            t.usage_count,
            t.success_rate,
            t.avg_engagement_score,
            COUNT(e.id) as total_executions,
            COUNT(CASE WHEN e.execution_status = 'completed' THEN 1 END) as successful_executions,
            COUNT(CASE WHEN e.execution_status = 'failed' THEN 1 END) as failed_executions,
            AVG(EXTRACT(EPOCH FROM (e.completed_at - e.started_at))) as avg_execution_time_seconds
        FROM mcp_templates t
        LEFT JOIN mcp_template_executions e ON t.id = e.template_id
        WHERE t.template_name = $1
        GROUP BY t.id, t.template_name, t.usage_count, t.success_rate, t.avg_engagement_score;
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(analytics_sql, template_name)
        
        if not row:
            return {}
        
        return dict(row)


# Global database instance
db_instance: Optional[MCPTemplateDatabase] = None


async def get_database() -> MCPTemplateDatabase:
    """Get database instance"""
    global db_instance
    if not db_instance:
        db_instance = MCPTemplateDatabase()
        await db_instance.init_pool()
    return db_instance


async def close_database():
    """Close database instance"""
    global db_instance
    if db_instance:
        await db_instance.close_pool()
        db_instance = None