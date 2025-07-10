-- Hub and Spoke Network Database Schema Updates
-- Generated: 2025-07-08T19:12:48.453179

-- Channels Table
CREATE TABLE IF NOT EXISTS channels (
                    id SERIAL PRIMARY KEY,
                    channel_name VARCHAR(255) NOT NULL,
                    youtube_channel_id VARCHAR(255) UNIQUE,
                    youtube_handle VARCHAR(255),
                    primary_archetype VARCHAR(100),
                    channel_role VARCHAR(50) DEFAULT 'spoke',
                    description TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT true,
                    performance_threshold JSONB DEFAULT '{}',
                    branding_config JSONB DEFAULT '{}'
                );

-- Archetype Performance Table
CREATE TABLE IF NOT EXISTS archetype_performance (
                    id SERIAL PRIMARY KEY,
                    archetype VARCHAR(100) NOT NULL,
                    channel_id INTEGER REFERENCES channels(id),
                    measurement_date DATE DEFAULT CURRENT_DATE,
                    retention_rate DECIMAL(5,2),
                    ctr_shorts_feed DECIMAL(5,2),
                    subscriber_gain INTEGER DEFAULT 0,
                    shares_per_1000_views DECIMAL(8,2),
                    total_videos INTEGER DEFAULT 0,
                    avg_view_duration_seconds INTEGER DEFAULT 0,
                    total_views BIGINT DEFAULT 0,
                    engagement_rate DECIMAL(5,2),
                    growth_trend VARCHAR(50) DEFAULT 'stable'
                );

-- Template Enhancements
ALTER TABLE mcp_templates 
                ADD COLUMN IF NOT EXISTS target_channel_id INTEGER REFERENCES channels(id),
                ADD COLUMN IF NOT EXISTS archetype_category VARCHAR(100),
                ADD COLUMN IF NOT EXISTS branding_package JSONB DEFAULT '{}',
                ADD COLUMN IF NOT EXISTS cross_promotion_config JSONB DEFAULT '{}';

-- Channel Analytics View
CREATE OR REPLACE VIEW channel_performance_summary AS
                SELECT 
                    c.id as channel_id,
                    c.channel_name,
                    c.primary_archetype,
                    c.channel_role,
                    COUNT(t.id) as total_templates,
                    AVG(ap.retention_rate) as avg_retention_rate,
                    AVG(ap.subscriber_gain) as avg_subscriber_gain,
                    SUM(ap.total_views) as total_network_views
                FROM channels c
                LEFT JOIN mcp_templates t ON c.id = t.target_channel_id
                LEFT JOIN archetype_performance ap ON c.primary_archetype = ap.archetype
                WHERE c.is_active = true
                GROUP BY c.id, c.channel_name, c.primary_archetype, c.channel_role;

