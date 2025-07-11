#!/usr/bin/env python3

"""
YouTube Analytics Harvester for TenxsomAI
Real-time performance data collection and genome correlation
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class VideoPerformanceData:
    """YouTube video performance metrics"""
    video_id: str
    genome_id: Optional[str]
    upload_date: datetime
    title: str
    description: str
    tags: List[str]
    duration_seconds: int
    # Core metrics
    views: int
    watch_time_minutes: float
    average_view_duration_seconds: float
    average_view_percentage: float
    # Engagement metrics
    likes: int
    dislikes: int
    comments: int
    shares: int
    subscribers_gained: int
    subscribers_lost: int
    # Discovery metrics
    impressions: int
    impressions_click_through_rate: float
    # Audience retention
    retention_graph: List[Dict[str, float]]
    retention_performance: str  # "above_average", "average", "below_average"
    # Revenue metrics
    estimated_revenue: float
    estimated_ad_revenue: float
    estimated_red_partner_revenue: float
    # Derived metrics
    engagement_rate: float
    virality_score: float
    monetization_efficiency: float


@dataclass
class ChannelAnalytics:
    """Channel-level analytics"""
    channel_id: str
    date_range: Tuple[datetime, datetime]
    total_views: int
    total_watch_time_hours: float
    total_subscribers: int
    subscriber_change: int
    total_revenue: float
    top_videos: List[str]
    average_view_duration: float
    channel_ctr: float


class YouTubeAnalyticsHarvester:
    """
    Harvests YouTube Analytics data and correlates with production genomes
    
    Features:
    - Real-time video performance tracking
    - Audience retention analysis
    - Revenue optimization insights
    - Genome correlation for learning
    - Competitive benchmarking
    """
    
    def __init__(self, credentials_path: str, db_connection=None):
        """Initialize YouTube Analytics harvester"""
        self.credentials_path = credentials_path
        self.db_connection = db_connection
        
        # Initialize YouTube APIs
        self.youtube_analytics = None
        self.youtube_data = None
        self._initialize_apis()
        
        # Storage
        self.video_performance_cache = {}
        self.channel_analytics_cache = {}
        
        # Configuration
        self.harvest_config = {
            "min_video_age_hours": 48,  # Wait 48 hours for stable metrics
            "max_video_age_days": 90,   # Analyze videos up to 90 days old
            "batch_size": 50,            # Videos per API batch
            "retention_sample_points": 40, # Points for retention graph
            "update_interval_hours": 6,   # Update frequency
            "viral_threshold_views": 10000,
            "high_performance_percentile": 80
        }
        
        # Performance benchmarks (from channel averages)
        self.performance_benchmarks = {
            "average_view_duration": 60,      # seconds
            "average_ctr": 0.05,              # 5%
            "average_engagement_rate": 0.08,  # 8%
            "average_retention": 0.5          # 50%
        }
        
    def _initialize_apis(self):
        """Initialize YouTube Analytics and Data APIs"""
        try:
            # Load credentials
            creds = Credentials.from_authorized_user_file(self.credentials_path)
            
            # Build API services
            self.youtube_analytics = build('youtubeAnalytics', 'v2', credentials=creds)
            self.youtube_data = build('youtube', 'v3', credentials=creds)
            
            logger.info("✅ YouTube APIs initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize YouTube APIs: {e}")
    
    async def harvest_recent_videos(self, 
                                  channel_id: str,
                                  limit: int = 100) -> List[VideoPerformanceData]:
        """Harvest performance data for recent videos"""
        
        logger.info(f"🎥 Harvesting analytics for channel {channel_id}")
        
        # Get recent video IDs
        video_ids = await self._get_recent_video_ids(channel_id, limit)
        
        if not video_ids:
            logger.warning("No videos found to analyze")
            return []
        
        # Harvest performance data for each video
        performance_data = []
        
        for batch_start in range(0, len(video_ids), self.harvest_config["batch_size"]):
            batch_ids = video_ids[batch_start:batch_start + self.harvest_config["batch_size"]]
            
            # Get video details
            video_details = await self._get_video_details(batch_ids)
            
            # Get analytics for each video
            for video_id, details in video_details.items():
                try:
                    performance = await self._harvest_video_analytics(
                        video_id, details, channel_id
                    )
                    
                    if performance:
                        performance_data.append(performance)
                        self.video_performance_cache[video_id] = performance
                        
                except Exception as e:
                    logger.error(f"Failed to harvest analytics for {video_id}: {e}")
            
            # Rate limiting
            await asyncio.sleep(1)
        
        # Update database
        await self._save_performance_data(performance_data)
        
        logger.info(f"✅ Harvested analytics for {len(performance_data)} videos")
        
        return performance_data
    
    async def _get_recent_video_ids(self, channel_id: str, limit: int) -> List[str]:
        """Get IDs of recent videos from channel"""
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=self.harvest_config["max_video_age_days"])
            
            # Search for channel videos
            request = self.youtube_data.search().list(
                part="id",
                channelId=channel_id,
                type="video",
                order="date",
                publishedAfter=start_date.isoformat() + "Z",
                maxResults=min(limit, 50)  # API limit
            )
            
            video_ids = []
            
            while request and len(video_ids) < limit:
                response = request.execute()
                
                for item in response.get('items', []):
                    video_ids.append(item['id']['videoId'])
                
                # Get next page
                request = self.youtube_data.search().list_next(request, response)
            
            return video_ids[:limit]
            
        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            return []
    
    async def _get_video_details(self, video_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get detailed information for videos"""
        
        try:
            request = self.youtube_data.videos().list(
                part="snippet,contentDetails,statistics",
                id=",".join(video_ids)
            )
            
            response = request.execute()
            
            video_details = {}
            
            for item in response.get('items', []):
                video_id = item['id']
                snippet = item['snippet']
                
                # Parse duration
                duration_str = item['contentDetails']['duration']
                duration_seconds = self._parse_duration(duration_str)
                
                video_details[video_id] = {
                    'title': snippet['title'],
                    'description': snippet['description'],
                    'tags': snippet.get('tags', []),
                    'publishedAt': snippet['publishedAt'],
                    'duration_seconds': duration_seconds,
                    'statistics': item['statistics']
                }
            
            return video_details
            
        except HttpError as e:
            logger.error(f"Failed to get video details: {e}")
            return {}
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse ISO 8601 duration to seconds"""
        import re
        
        pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
        match = pattern.match(duration_str)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    async def _harvest_video_analytics(self,
                                     video_id: str,
                                     details: Dict[str, Any],
                                     channel_id: str) -> Optional[VideoPerformanceData]:
        """Harvest comprehensive analytics for a single video"""
        
        # Check if video is old enough for stable metrics
        upload_date = datetime.fromisoformat(details['publishedAt'].replace('Z', '+00:00'))
        video_age_hours = (datetime.now(upload_date.tzinfo) - upload_date).total_seconds() / 3600
        
        if video_age_hours < self.harvest_config["min_video_age_hours"]:
            logger.info(f"Skipping {video_id} - too recent ({video_age_hours:.1f} hours old)")
            return None
        
        try:
            # Get analytics metrics
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = upload_date.strftime('%Y-%m-%d')
            
            # Video metrics
            metrics_response = self.youtube_analytics.reports().query(
                ids=f'channel=={channel_id}',
                startDate=start_date,
                endDate=end_date,
                metrics='views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,likes,dislikes,comments,shares,subscribersGained,subscribersLost,estimatedRevenue,estimatedAdRevenue,estimatedRedPartnerRevenue,impressions,impressionClickThroughRate',
                dimensions='video',
                filters=f'video=={video_id}'
            ).execute()
            
            # Extract metrics
            if not metrics_response.get('rows'):
                logger.warning(f"No analytics data for {video_id}")
                return None
            
            metrics = metrics_response['rows'][0]
            
            # Get audience retention data
            retention_data = await self._get_audience_retention(video_id)
            
            # Calculate derived metrics
            views = int(metrics[1])
            likes = int(metrics[5])
            comments = int(metrics[7])
            shares = int(metrics[8])
            
            engagement_rate = (likes + comments + shares) / max(views, 1)
            
            # Calculate virality score
            virality_score = self._calculate_virality_score(
                views, engagement_rate, shares, video_age_hours
            )
            
            # Calculate monetization efficiency
            revenue = float(metrics[11]) if metrics[11] else 0.0
            monetization_efficiency = revenue / max(views / 1000, 0.001)  # Revenue per 1k views
            
            # Determine retention performance
            avg_retention = float(metrics[4]) if metrics[4] else 50.0
            retention_performance = self._classify_retention_performance(avg_retention)
            
            # Get genome ID from database
            genome_id = await self._get_genome_id_for_video(video_id)
            
            # Create performance data object
            performance = VideoPerformanceData(
                video_id=video_id,
                genome_id=genome_id,
                upload_date=upload_date,
                title=details['title'],
                description=details['description'],
                tags=details['tags'],
                duration_seconds=details['duration_seconds'],
                views=views,
                watch_time_minutes=float(metrics[2]) if metrics[2] else 0.0,
                average_view_duration_seconds=float(metrics[3]) if metrics[3] else 0.0,
                average_view_percentage=avg_retention,
                likes=likes,
                dislikes=int(metrics[6]) if metrics[6] else 0,
                comments=comments,
                shares=shares,
                subscribers_gained=int(metrics[9]) if metrics[9] else 0,
                subscribers_lost=int(metrics[10]) if metrics[10] else 0,
                impressions=int(metrics[14]) if metrics[14] else 0,
                impressions_click_through_rate=float(metrics[15]) if metrics[15] else 0.0,
                retention_graph=retention_data,
                retention_performance=retention_performance,
                estimated_revenue=revenue,
                estimated_ad_revenue=float(metrics[12]) if metrics[12] else 0.0,
                estimated_red_partner_revenue=float(metrics[13]) if metrics[13] else 0.0,
                engagement_rate=engagement_rate,
                virality_score=virality_score,
                monetization_efficiency=monetization_efficiency
            )
            
            return performance
            
        except HttpError as e:
            logger.error(f"Analytics API error for {video_id}: {e}")
            return None
    
    async def _get_audience_retention(self, video_id: str) -> List[Dict[str, float]]:
        """Get audience retention graph data"""
        
        try:
            # Note: Audience retention requires special API access
            # For now, return simulated data
            # In production, use: youtube_analytics.reports().query() with audienceRetention dimension
            
            retention_points = []
            num_points = self.harvest_config["retention_sample_points"]
            
            # Simulate typical retention curve
            for i in range(num_points):
                time_percent = i / (num_points - 1)
                
                # Typical retention curve (exponential decay with stabilization)
                if time_percent < 0.1:
                    retention = 95 - (time_percent * 200)  # Initial drop
                else:
                    retention = 70 * np.exp(-time_percent * 0.5) + 30  # Exponential decay to 30%
                
                retention_points.append({
                    "elapsedVideoTimeRatio": time_percent,
                    "audienceRetentionPercentage": max(0, min(100, retention))
                })
            
            return retention_points
            
        except Exception as e:
            logger.error(f"Failed to get retention data: {e}")
            return []
    
    def _calculate_virality_score(self,
                                views: int,
                                engagement_rate: float,
                                shares: int,
                                video_age_hours: float) -> float:
        """Calculate virality score (0-100)"""
        
        # Views velocity (views per hour)
        views_per_hour = views / max(video_age_hours, 1)
        
        # Normalize components
        velocity_score = min(views_per_hour / 1000, 1.0) * 40  # Max 40 points
        engagement_score = min(engagement_rate / 0.15, 1.0) * 30  # Max 30 points
        share_score = min(shares / 100, 1.0) * 20  # Max 20 points
        absolute_score = min(views / self.harvest_config["viral_threshold_views"], 1.0) * 10  # Max 10 points
        
        virality_score = velocity_score + engagement_score + share_score + absolute_score
        
        return round(virality_score, 2)
    
    def _classify_retention_performance(self, avg_retention: float) -> str:
        """Classify retention performance relative to benchmarks"""
        
        benchmark = self.performance_benchmarks["average_retention"] * 100
        
        if avg_retention > benchmark * 1.2:
            return "above_average"
        elif avg_retention < benchmark * 0.8:
            return "below_average"
        else:
            return "average"
    
    async def _get_genome_id_for_video(self, video_id: str) -> Optional[str]:
        """Get production genome ID associated with video"""
        
        if not self.db_connection:
            return None
        
        try:
            query = """
            SELECT genome_id FROM production_genomes 
            WHERE video_id = $1
            LIMIT 1
            """
            
            result = await self.db_connection.fetchrow(query, video_id)
            return result['genome_id'] if result else None
            
        except Exception as e:
            logger.error(f"Failed to get genome ID: {e}")
            return None
    
    async def _save_performance_data(self, performance_data: List[VideoPerformanceData]):
        """Save performance data to database"""
        
        if not self.db_connection:
            return
        
        # Create table if not exists
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS video_performance (
            video_id VARCHAR(255) PRIMARY KEY,
            genome_id VARCHAR(255),
            upload_date TIMESTAMP,
            title TEXT,
            description TEXT,
            tags TEXT,
            duration_seconds INTEGER,
            views INTEGER,
            watch_time_minutes FLOAT,
            average_view_duration_seconds FLOAT,
            average_view_percentage FLOAT,
            likes INTEGER,
            dislikes INTEGER,
            comments INTEGER,
            shares INTEGER,
            subscribers_gained INTEGER,
            subscribers_lost INTEGER,
            impressions INTEGER,
            impressions_click_through_rate FLOAT,
            retention_graph TEXT,
            retention_performance VARCHAR(50),
            estimated_revenue FLOAT,
            estimated_ad_revenue FLOAT,
            estimated_red_partner_revenue FLOAT,
            engagement_rate FLOAT,
            virality_score FLOAT,
            monetization_efficiency FLOAT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (genome_id) REFERENCES production_genomes(genome_id)
        );
        """
        
        try:
            await self.db_connection.execute(create_table_sql)
            
            # Insert/update performance data
            for perf in performance_data:
                upsert_sql = """
                INSERT INTO video_performance 
                (video_id, genome_id, upload_date, title, description, tags, duration_seconds,
                 views, watch_time_minutes, average_view_duration_seconds, average_view_percentage,
                 likes, dislikes, comments, shares, subscribers_gained, subscribers_lost,
                 impressions, impressions_click_through_rate, retention_graph, retention_performance,
                 estimated_revenue, estimated_ad_revenue, estimated_red_partner_revenue,
                 engagement_rate, virality_score, monetization_efficiency)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24, $25, $26, $27)
                ON CONFLICT (video_id) DO UPDATE SET
                    views = EXCLUDED.views,
                    watch_time_minutes = EXCLUDED.watch_time_minutes,
                    average_view_duration_seconds = EXCLUDED.average_view_duration_seconds,
                    average_view_percentage = EXCLUDED.average_view_percentage,
                    likes = EXCLUDED.likes,
                    dislikes = EXCLUDED.dislikes,
                    comments = EXCLUDED.comments,
                    shares = EXCLUDED.shares,
                    subscribers_gained = EXCLUDED.subscribers_gained,
                    subscribers_lost = EXCLUDED.subscribers_lost,
                    impressions = EXCLUDED.impressions,
                    impressions_click_through_rate = EXCLUDED.impressions_click_through_rate,
                    retention_graph = EXCLUDED.retention_graph,
                    retention_performance = EXCLUDED.retention_performance,
                    estimated_revenue = EXCLUDED.estimated_revenue,
                    estimated_ad_revenue = EXCLUDED.estimated_ad_revenue,
                    estimated_red_partner_revenue = EXCLUDED.estimated_red_partner_revenue,
                    engagement_rate = EXCLUDED.engagement_rate,
                    virality_score = EXCLUDED.virality_score,
                    monetization_efficiency = EXCLUDED.monetization_efficiency,
                    last_updated = CURRENT_TIMESTAMP
                """
                
                await self.db_connection.execute(
                    upsert_sql,
                    perf.video_id, perf.genome_id, perf.upload_date,
                    perf.title, perf.description, json.dumps(perf.tags),
                    perf.duration_seconds, perf.views, perf.watch_time_minutes,
                    perf.average_view_duration_seconds, perf.average_view_percentage,
                    perf.likes, perf.dislikes, perf.comments, perf.shares,
                    perf.subscribers_gained, perf.subscribers_lost,
                    perf.impressions, perf.impressions_click_through_rate,
                    json.dumps(perf.retention_graph), perf.retention_performance,
                    perf.estimated_revenue, perf.estimated_ad_revenue,
                    perf.estimated_red_partner_revenue, perf.engagement_rate,
                    perf.virality_score, perf.monetization_efficiency
                )
            
            logger.info(f"💾 Saved performance data for {len(performance_data)} videos")
            
        except Exception as e:
            logger.error(f"Failed to save performance data: {e}")
    
    async def correlate_genomes_with_performance(self):
        """Correlate production genomes with video performance"""
        
        if not self.db_connection:
            return
        
        try:
            # Get videos with both genome and performance data
            query = """
            SELECT vp.*, pg.injected_knowledge, pg.executed_steps
            FROM video_performance vp
            JOIN production_genomes pg ON vp.genome_id = pg.genome_id
            WHERE vp.genome_id IS NOT NULL
            AND vp.views > 100  -- Minimum threshold
            ORDER BY vp.upload_date DESC
            LIMIT 1000
            """
            
            results = await self.db_connection.fetch(query)
            
            if not results:
                logger.warning("No videos with genome correlation found")
                return
            
            # Update genomes with performance data
            from mcp_knowledge_integration import MCPKnowledgeIntegration
            knowledge_system = MCPKnowledgeIntegration(self.db_connection)
            
            for row in results:
                youtube_analytics = {
                    "views": row['views'],
                    "avg_view_duration_seconds": row['average_view_duration_seconds'],
                    "ctr": row['impressions_click_through_rate'],
                    "impressions": row['impressions'],
                    "likes": row['likes'],
                    "comments": row['comments'],
                    "shares": row['shares'],
                    "retention_performance": row['retention_performance'],
                    "virality_score": row['virality_score'],
                    "monetization_efficiency": row['monetization_efficiency']
                }
                
                await knowledge_system.update_genome_analytics(
                    row['genome_id'],
                    youtube_analytics
                )
            
            logger.info(f"🔗 Correlated {len(results)} genomes with performance data")
            
        except Exception as e:
            logger.error(f"Failed to correlate genomes: {e}")
    
    async def generate_performance_report(self, 
                                        channel_id: str,
                                        days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        report = {
            "channel_id": channel_id,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary_metrics": {},
            "top_performing_videos": [],
            "viral_videos": [],
            "monetization_analysis": {},
            "genome_performance": {},
            "recommendations": []
        }
        
        # Get recent performance data
        recent_videos = [
            perf for perf in self.video_performance_cache.values()
            if perf.upload_date >= start_date
        ]
        
        if not recent_videos:
            logger.warning("No recent videos to analyze")
            return report
        
        # Calculate summary metrics
        report["summary_metrics"] = {
            "total_videos": len(recent_videos),
            "total_views": sum(v.views for v in recent_videos),
            "average_views": sum(v.views for v in recent_videos) / len(recent_videos),
            "total_watch_time_hours": sum(v.watch_time_minutes for v in recent_videos) / 60,
            "average_view_duration": sum(v.average_view_duration_seconds for v in recent_videos) / len(recent_videos),
            "average_retention": sum(v.average_view_percentage for v in recent_videos) / len(recent_videos),
            "total_revenue": sum(v.estimated_revenue for v in recent_videos),
            "average_ctr": sum(v.impressions_click_through_rate for v in recent_videos) / len(recent_videos),
            "average_engagement_rate": sum(v.engagement_rate for v in recent_videos) / len(recent_videos)
        }
        
        # Top performing videos
        top_videos = sorted(recent_videos, key=lambda x: x.views, reverse=True)[:10]
        report["top_performing_videos"] = [
            {
                "video_id": v.video_id,
                "title": v.title[:50] + "..." if len(v.title) > 50 else v.title,
                "views": v.views,
                "engagement_rate": v.engagement_rate,
                "revenue": v.estimated_revenue
            }
            for v in top_videos
        ]
        
        # Viral videos
        viral_videos = [v for v in recent_videos if v.virality_score > 70]
        report["viral_videos"] = [
            {
                "video_id": v.video_id,
                "title": v.title[:50] + "..." if len(v.title) > 50 else v.title,
                "virality_score": v.virality_score,
                "views": v.views,
                "shares": v.shares
            }
            for v in sorted(viral_videos, key=lambda x: x.virality_score, reverse=True)
        ]
        
        # Monetization analysis
        report["monetization_analysis"] = {
            "total_revenue": report["summary_metrics"]["total_revenue"],
            "revenue_per_1k_views": report["summary_metrics"]["total_revenue"] / (report["summary_metrics"]["total_views"] / 1000) if report["summary_metrics"]["total_views"] > 0 else 0,
            "best_monetized_videos": sorted(
                [{"title": v.title[:30], "efficiency": v.monetization_efficiency} for v in recent_videos],
                key=lambda x: x["efficiency"],
                reverse=True
            )[:5]
        }
        
        # Genome performance analysis
        genome_videos = [v for v in recent_videos if v.genome_id]
        if genome_videos:
            report["genome_performance"] = {
                "videos_with_genomes": len(genome_videos),
                "average_performance_vs_non_genome": {
                    "views": sum(v.views for v in genome_videos) / len(genome_videos) if genome_videos else 0,
                    "engagement": sum(v.engagement_rate for v in genome_videos) / len(genome_videos) if genome_videos else 0
                }
            }
        
        # Generate recommendations
        report["recommendations"] = self._generate_recommendations(recent_videos)
        
        return report
    
    def _generate_recommendations(self, videos: List[VideoPerformanceData]) -> List[str]:
        """Generate actionable recommendations based on performance data"""
        
        recommendations = []
        
        # Analyze patterns
        avg_retention = sum(v.average_view_percentage for v in videos) / len(videos)
        avg_ctr = sum(v.impressions_click_through_rate for v in videos) / len(videos)
        
        # Retention recommendations
        if avg_retention < 40:
            recommendations.append("Focus on improving first 15 seconds - retention is below 40%")
        elif avg_retention > 60:
            recommendations.append("Excellent retention! Consider longer content to maximize watch time")
        
        # CTR recommendations
        if avg_ctr < 0.04:
            recommendations.append("Improve thumbnails and titles - CTR is below 4%")
        elif avg_ctr > 0.08:
            recommendations.append("Great CTR! Test similar thumbnail styles across more videos")
        
        # Viral potential
        viral_count = len([v for v in videos if v.virality_score > 50])
        if viral_count < len(videos) * 0.1:
            recommendations.append("Experiment with trending topics - low viral video ratio")
        
        # Monetization
        avg_monetization = sum(v.monetization_efficiency for v in videos) / len(videos)
        if avg_monetization < 2.0:
            recommendations.append("Target higher CPM niches - monetization below $2 RPM")
        
        return recommendations


async def main():
    """Test YouTube Analytics Harvester"""
    
    # Initialize harvester (requires credentials)
    # harvester = YouTubeAnalyticsHarvester("path/to/credentials.json")
    
    logger.info("📊 YouTube Analytics Harvester Demo")
    
    # Simulate performance data
    sample_performance = VideoPerformanceData(
        video_id="abc123",
        genome_id="genome_20250110_abc123",
        upload_date=datetime.now() - timedelta(days=7),
        title="AI Creates Amazing Video in Seconds",
        description="Watch as our AI system...",
        tags=["ai", "technology", "tutorial"],
        duration_seconds=180,
        views=25000,
        watch_time_minutes=45000,
        average_view_duration_seconds=108,
        average_view_percentage=60.0,
        likes=1200,
        dislikes=50,
        comments=150,
        shares=200,
        subscribers_gained=450,
        subscribers_lost=20,
        impressions=150000,
        impressions_click_through_rate=0.167,
        retention_graph=[],
        retention_performance="above_average",
        estimated_revenue=125.50,
        estimated_ad_revenue=120.00,
        estimated_red_partner_revenue=5.50,
        engagement_rate=0.062,
        virality_score=78.5,
        monetization_efficiency=5.02
    )
    
    print(f"\n📹 Sample Video Performance:")
    print(f"Title: {sample_performance.title}")
    print(f"Views: {sample_performance.views:,}")
    print(f"Engagement Rate: {sample_performance.engagement_rate:.1%}")
    print(f"Virality Score: {sample_performance.virality_score}/100")
    print(f"Revenue: ${sample_performance.estimated_revenue:.2f}")
    print(f"Monetization Efficiency: ${sample_performance.monetization_efficiency:.2f} RPM")
    
    # Generate sample report
    print(f"\n📈 Performance Insights:")
    print(f"• Retention: {sample_performance.retention_performance}")
    print(f"• CTR: {sample_performance.impressions_click_through_rate:.1%}")
    print(f"• Watch Time: {sample_performance.watch_time_minutes:.0f} minutes")
    print(f"• Subscriber Delta: +{sample_performance.subscribers_gained - sample_performance.subscribers_lost}")


if __name__ == "__main__":
    asyncio.run(main())