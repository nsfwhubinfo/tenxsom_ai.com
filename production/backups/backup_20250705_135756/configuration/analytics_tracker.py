#!/usr/bin/env python3

"""
Tenxsom AI Analytics Tracker
Comprehensive analytics and monetization metrics tracking system
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from dataclasses import dataclass, asdict

# Import our components
from production_config_manager import ProductionConfigManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class VideoMetrics:
    """Individual video performance metrics"""
    video_id: str
    platform: str
    upload_date: datetime
    title: str
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    watch_time_minutes: float = 0.0
    ctr: float = 0.0  # Click-through rate
    avg_view_duration: float = 0.0
    revenue_usd: float = 0.0
    subscriber_gain: int = 0


@dataclass
class MonetizationMetrics:
    """Overall monetization tracking"""
    date: datetime
    total_videos: int
    total_views: int
    total_watch_time_hours: float
    estimated_revenue: float
    subscriber_count: int
    subscriber_growth: int
    monetization_eligible: bool
    youtube_partner_status: str


@dataclass 
class PlatformAnalytics:
    """Platform-specific analytics"""
    platform: str
    videos_uploaded: int
    total_views: int
    avg_views_per_video: float
    total_engagement: int
    engagement_rate: float
    top_performing_video: Optional[str]
    revenue_contribution: float


class AnalyticsTracker:
    """
    Comprehensive analytics tracking for Tenxsom AI monetization strategy
    
    Features:
    - Multi-platform performance tracking
    - YouTube monetization progress monitoring
    - ROI and cost-per-acquisition analysis
    - A/B testing results tracking
    - Automated reporting and alerts
    - Revenue forecasting and optimization
    """
    
    def __init__(self, config_manager: ProductionConfigManager = None):
        """Initialize analytics tracker"""
        self.config = config_manager or ProductionConfigManager()
        
        # Analytics storage
        self.video_metrics: Dict[str, VideoMetrics] = {}
        self.daily_metrics: List[MonetizationMetrics] = []
        self.platform_analytics: Dict[str, PlatformAnalytics] = {}
        
        # Monetization thresholds
        self.monetization_requirements = {
            "youtube": {
                "min_subscribers": 1000,
                "min_watch_hours": 4000,
                "min_videos": 20,
                "community_guidelines": True
            },
            "tiktok": {
                "min_followers": 1000,
                "min_videos": 5,
                "creator_fund_eligible": True
            },
            "instagram": {
                "min_followers": 1000,
                "min_videos": 10,
                "professional_account": True
            }
        }
        
        # Analytics configuration
        self.tracking_config = {
            "data_retention_days": 365,
            "analytics_update_interval": 3600,  # 1 hour
            "report_generation_time": "23:00",
            "alert_thresholds": {
                "low_performance_ctr": 0.02,
                "high_performance_ctr": 0.08,
                "monetization_progress": 0.8
            }
        }
        
        # Initialize platform analytics
        self._initialize_platform_analytics()
        
    def _initialize_platform_analytics(self):
        """Initialize platform analytics tracking"""
        platforms = ["youtube", "tiktok", "instagram", "x"]
        
        for platform in platforms:
            self.platform_analytics[platform] = PlatformAnalytics(
                platform=platform,
                videos_uploaded=0,
                total_views=0,
                avg_views_per_video=0.0,
                total_engagement=0,
                engagement_rate=0.0,
                top_performing_video=None,
                revenue_contribution=0.0
            )
    
    async def track_video_upload(self, video_id: str, platform: str, title: str, metadata: Dict[str, Any] = None):
        """Track a new video upload"""
        logger.info(f"📊 Tracking new upload: {video_id} on {platform}")
        
        video_metrics = VideoMetrics(
            video_id=video_id,
            platform=platform,
            upload_date=datetime.now(),
            title=title
        )
        
        self.video_metrics[video_id] = video_metrics
        
        # Update platform analytics
        platform_analytics = self.platform_analytics[platform]
        platform_analytics.videos_uploaded += 1
        
        # Save tracking data
        await self._save_video_tracking(video_metrics)
        
        logger.info(f"✅ Video tracking initialized for {video_id}")
    
    async def update_video_metrics(self, video_id: str, metrics_data: Dict[str, Any]):
        """Update video performance metrics"""
        if video_id not in self.video_metrics:
            logger.warning(f"⚠️ Video {video_id} not found in tracking")
            return
        
        video = self.video_metrics[video_id]
        
        # Update metrics
        video.views = metrics_data.get("views", video.views)
        video.likes = metrics_data.get("likes", video.likes)
        video.comments = metrics_data.get("comments", video.comments)
        video.shares = metrics_data.get("shares", video.shares)
        video.watch_time_minutes = metrics_data.get("watch_time_minutes", video.watch_time_minutes)
        video.ctr = metrics_data.get("ctr", video.ctr)
        video.avg_view_duration = metrics_data.get("avg_view_duration", video.avg_view_duration)
        video.revenue_usd = metrics_data.get("revenue_usd", video.revenue_usd)
        video.subscriber_gain = metrics_data.get("subscriber_gain", video.subscriber_gain)
        
        # Update platform analytics
        await self._update_platform_analytics(video)
        
        logger.info(f"📈 Updated metrics for {video_id}: {video.views} views, {video.likes} likes")
    
    async def _update_platform_analytics(self, video: VideoMetrics):
        """Update platform-level analytics"""
        platform_analytics = self.platform_analytics[video.platform]
        
        # Recalculate platform totals
        platform_videos = [v for v in self.video_metrics.values() if v.platform == video.platform]
        
        platform_analytics.total_views = sum(v.views for v in platform_videos)
        platform_analytics.total_engagement = sum(v.likes + v.comments + v.shares for v in platform_videos)
        
        if platform_analytics.videos_uploaded > 0:
            platform_analytics.avg_views_per_video = platform_analytics.total_views / platform_analytics.videos_uploaded
            platform_analytics.engagement_rate = platform_analytics.total_engagement / platform_analytics.total_views if platform_analytics.total_views > 0 else 0
        
        # Find top performing video
        if platform_videos:
            top_video = max(platform_videos, key=lambda v: v.views)
            platform_analytics.top_performing_video = top_video.video_id
        
        # Revenue tracking (primarily YouTube)
        if video.platform == "youtube":
            platform_analytics.revenue_contribution = sum(v.revenue_usd for v in platform_videos)
    
    async def calculate_daily_metrics(self, date: datetime = None) -> MonetizationMetrics:
        """Calculate daily monetization metrics"""
        if date is None:
            date = datetime.now()
        
        # Filter videos for the date
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start + timedelta(days=1)
        
        daily_videos = [
            v for v in self.video_metrics.values()
            if date_start <= v.upload_date < date_end
        ]
        
        # Calculate totals
        total_views = sum(v.views for v in self.video_metrics.values())
        total_watch_time_hours = sum(v.watch_time_minutes for v in self.video_metrics.values()) / 60
        estimated_revenue = sum(v.revenue_usd for v in self.video_metrics.values())
        
        # YouTube-specific calculations
        youtube_videos = [v for v in self.video_metrics.values() if v.platform == "youtube"]
        youtube_subscriber_gain = sum(v.subscriber_gain for v in youtube_videos)
        
        # Estimate current subscriber count (would be fetched from API in real implementation)
        current_subscribers = 100 + youtube_subscriber_gain  # Starting baseline + growth
        
        # Check monetization eligibility
        monetization_eligible = await self._check_monetization_eligibility("youtube")
        
        daily_metrics = MonetizationMetrics(
            date=date,
            total_videos=len(daily_videos),
            total_views=total_views,
            total_watch_time_hours=total_watch_time_hours,
            estimated_revenue=estimated_revenue,
            subscriber_count=current_subscribers,
            subscriber_growth=youtube_subscriber_gain,
            monetization_eligible=monetization_eligible,
            youtube_partner_status=self._get_partner_status(current_subscribers, total_watch_time_hours)
        )
        
        self.daily_metrics.append(daily_metrics)
        await self._save_daily_metrics(daily_metrics)
        
        return daily_metrics
    
    async def _check_monetization_eligibility(self, platform: str) -> bool:
        """Check if platform meets monetization requirements"""
        requirements = self.monetization_requirements.get(platform, {})
        
        if platform == "youtube":
            # Get current metrics
            youtube_videos = [v for v in self.video_metrics.values() if v.platform == "youtube"]
            current_subscribers = 100 + sum(v.subscriber_gain for v in youtube_videos)
            total_watch_hours = sum(v.watch_time_minutes for v in youtube_videos) / 60
            
            return (
                current_subscribers >= requirements.get("min_subscribers", 1000) and
                total_watch_hours >= requirements.get("min_watch_hours", 4000) and
                len(youtube_videos) >= requirements.get("min_videos", 20)
            )
        
        return False
    
    def _get_partner_status(self, subscribers: int, watch_hours: float) -> str:
        """Get YouTube Partner Program status"""
        if subscribers >= 1000 and watch_hours >= 4000:
            return "eligible"
        elif subscribers >= 500 or watch_hours >= 2000:
            return "approaching"
        else:
            return "building"
    
    async def generate_analytics_report(self, date: datetime = None) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        if date is None:
            date = datetime.now()
        
        logger.info(f"📊 Generating analytics report for {date.strftime('%Y-%m-%d')}")
        
        # Calculate current metrics
        daily_metrics = await self.calculate_daily_metrics(date)
        
        # Platform breakdown
        platform_breakdown = {}
        for platform, analytics in self.platform_analytics.items():
            platform_breakdown[platform] = asdict(analytics)
        
        # Performance insights
        performance_insights = await self._generate_performance_insights()
        
        # Monetization progress
        monetization_progress = await self._calculate_monetization_progress()
        
        # ROI analysis
        roi_analysis = await self._calculate_roi_analysis()
        
        # Recommendations
        recommendations = await self._generate_recommendations()
        
        report = {
            "report_date": date.isoformat(),
            "generated_at": datetime.now().isoformat(),
            "daily_metrics": asdict(daily_metrics),
            "platform_breakdown": platform_breakdown,
            "performance_insights": performance_insights,
            "monetization_progress": monetization_progress,
            "roi_analysis": roi_analysis,
            "recommendations": recommendations,
            "total_videos_tracked": len(self.video_metrics),
            "tracking_period_days": (datetime.now() - min(v.upload_date for v in self.video_metrics.values() if self.video_metrics)).days if self.video_metrics else 0
        }
        
        # Save report
        await self._save_analytics_report(report, date)
        
        return report
    
    async def _generate_performance_insights(self) -> Dict[str, Any]:
        """Generate performance insights from video data"""
        if not self.video_metrics:
            return {"status": "insufficient_data"}
        
        videos = list(self.video_metrics.values())
        
        # Top performers
        top_viewed = max(videos, key=lambda v: v.views)
        top_engagement = max(videos, key=lambda v: v.likes + v.comments + v.shares)
        
        # Performance averages
        avg_views = sum(v.views for v in videos) / len(videos)
        avg_ctr = sum(v.ctr for v in videos) / len(videos)
        avg_engagement_rate = sum((v.likes + v.comments + v.shares) / max(v.views, 1) for v in videos) / len(videos)
        
        # Growth trends (last 7 days vs previous 7 days)
        recent_videos = [v for v in videos if (datetime.now() - v.upload_date).days <= 7]
        older_videos = [v for v in videos if 7 < (datetime.now() - v.upload_date).days <= 14]
        
        growth_trend = "stable"
        if recent_videos and older_videos:
            recent_avg_views = sum(v.views for v in recent_videos) / len(recent_videos)
            older_avg_views = sum(v.views for v in older_videos) / len(older_videos)
            
            if recent_avg_views > older_avg_views * 1.1:
                growth_trend = "improving"
            elif recent_avg_views < older_avg_views * 0.9:
                growth_trend = "declining"
        
        return {
            "top_performers": {
                "most_viewed": {
                    "video_id": top_viewed.video_id,
                    "title": top_viewed.title,
                    "views": top_viewed.views,
                    "platform": top_viewed.platform
                },
                "most_engaging": {
                    "video_id": top_engagement.video_id,
                    "title": top_engagement.title,
                    "engagement": top_engagement.likes + top_engagement.comments + top_engagement.shares,
                    "platform": top_engagement.platform
                }
            },
            "performance_averages": {
                "avg_views": round(avg_views, 1),
                "avg_ctr": round(avg_ctr * 100, 2),
                "avg_engagement_rate": round(avg_engagement_rate * 100, 2)
            },
            "growth_trend": growth_trend,
            "total_videos": len(videos),
            "platforms_active": len(set(v.platform for v in videos))
        }
    
    async def _calculate_monetization_progress(self) -> Dict[str, Any]:
        """Calculate progress toward monetization goals"""
        youtube_videos = [v for v in self.video_metrics.values() if v.platform == "youtube"]
        
        if not youtube_videos:
            return {"status": "no_youtube_content"}
        
        # Current metrics
        current_subscribers = 100 + sum(v.subscriber_gain for v in youtube_videos)
        total_watch_hours = sum(v.watch_time_minutes for v in youtube_videos) / 60
        video_count = len(youtube_videos)
        
        # Progress percentages
        subscriber_progress = min(current_subscribers / 1000 * 100, 100)
        watch_time_progress = min(total_watch_hours / 4000 * 100, 100)
        video_progress = min(video_count / 20 * 100, 100)
        
        # Overall progress
        overall_progress = (subscriber_progress + watch_time_progress + video_progress) / 3
        
        # Time to monetization estimate
        days_active = (datetime.now() - min(v.upload_date for v in youtube_videos)).days or 1
        current_rate = {
            "subscribers_per_day": sum(v.subscriber_gain for v in youtube_videos) / days_active,
            "watch_hours_per_day": total_watch_hours / days_active,
            "videos_per_day": len(youtube_videos) / days_active
        }
        
        # Calculate days to reach requirements
        days_to_monetization = []
        
        if current_subscribers < 1000 and current_rate["subscribers_per_day"] > 0:
            days_to_monetization.append((1000 - current_subscribers) / current_rate["subscribers_per_day"])
        
        if total_watch_hours < 4000 and current_rate["watch_hours_per_day"] > 0:
            days_to_monetization.append((4000 - total_watch_hours) / current_rate["watch_hours_per_day"])
        
        estimated_days = max(days_to_monetization) if days_to_monetization else 0
        
        return {
            "current_metrics": {
                "subscribers": current_subscribers,
                "watch_hours": round(total_watch_hours, 1),
                "videos": video_count
            },
            "requirements": {
                "subscribers": 1000,
                "watch_hours": 4000,
                "videos": 20
            },
            "progress_percentages": {
                "subscribers": round(subscriber_progress, 1),
                "watch_hours": round(watch_time_progress, 1),
                "videos": round(video_progress, 1),
                "overall": round(overall_progress, 1)
            },
            "estimated_days_to_monetization": round(estimated_days) if estimated_days > 0 else "Already eligible",
            "monthly_projection": {
                "subscribers": round(current_rate["subscribers_per_day"] * 30),
                "watch_hours": round(current_rate["watch_hours_per_day"] * 30, 1),
                "videos": round(current_rate["videos_per_day"] * 30)
            }
        }
    
    async def _calculate_roi_analysis(self) -> Dict[str, Any]:
        """Calculate return on investment analysis"""
        total_revenue = sum(v.revenue_usd for v in self.video_metrics.values())
        
        # Estimated costs (from our monetization strategy)
        estimated_monthly_cost = 80.0  # Google Ultra + UseAPI accounts
        days_active = max((datetime.now() - min(v.upload_date for v in self.video_metrics.values() if self.video_metrics)).days, 1) if self.video_metrics else 1
        estimated_cost = (estimated_monthly_cost / 30) * days_active
        
        # ROI calculation
        roi_percentage = ((total_revenue - estimated_cost) / max(estimated_cost, 0.01)) * 100
        
        # Cost per video
        total_videos = len(self.video_metrics)
        cost_per_video = estimated_cost / max(total_videos, 1)
        
        # Revenue per video
        revenue_per_video = total_revenue / max(total_videos, 1)
        
        return {
            "total_revenue": round(total_revenue, 2),
            "estimated_costs": round(estimated_cost, 2),
            "net_profit": round(total_revenue - estimated_cost, 2),
            "roi_percentage": round(roi_percentage, 1),
            "cost_per_video": round(cost_per_video, 4),
            "revenue_per_video": round(revenue_per_video, 4),
            "break_even_videos": round(estimated_cost / max(revenue_per_video, 0.01)) if revenue_per_video > 0 else "N/A",
            "tracking_period_days": days_active
        }
    
    async def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on analytics"""
        recommendations = []
        
        # Check performance metrics
        if self.video_metrics:
            avg_ctr = sum(v.ctr for v in self.video_metrics.values()) / len(self.video_metrics)
            
            if avg_ctr < self.tracking_config["alert_thresholds"]["low_performance_ctr"]:
                recommendations.append("🎯 Optimize thumbnails and titles to improve click-through rate")
            
            # Check platform distribution
            platform_counts = {}
            for video in self.video_metrics.values():
                platform_counts[video.platform] = platform_counts.get(video.platform, 0) + 1
            
            if platform_counts.get("youtube", 0) < len(self.video_metrics) * 0.7:
                recommendations.append("📺 Increase YouTube content ratio for monetization focus")
            
            # Check upload consistency
            recent_videos = [v for v in self.video_metrics.values() if (datetime.now() - v.upload_date).days <= 7]
            if len(recent_videos) < 10:
                recommendations.append("📅 Maintain consistent daily upload schedule (target: 96 videos/day)")
        
        # Monetization progress recommendations
        monetization_progress = await self._calculate_monetization_progress()
        if monetization_progress.get("progress_percentages", {}).get("overall", 0) < 50:
            recommendations.append("🚀 Focus on subscriber growth and watch time optimization")
        
        return recommendations
    
    async def _save_video_tracking(self, video_metrics: VideoMetrics):
        """Save video tracking data"""
        tracking_dir = Path(__file__).parent / "analytics" / "videos"
        tracking_dir.mkdir(parents=True, exist_ok=True)
        
        video_file = tracking_dir / f"{video_metrics.video_id}.json"
        with open(video_file, 'w') as f:
            json.dump(asdict(video_metrics), f, indent=2, default=str)
    
    async def _save_daily_metrics(self, daily_metrics: MonetizationMetrics):
        """Save daily metrics"""
        metrics_dir = Path(__file__).parent / "analytics" / "daily"
        metrics_dir.mkdir(parents=True, exist_ok=True)
        
        date_str = daily_metrics.date.strftime("%Y-%m-%d")
        metrics_file = metrics_dir / f"daily_metrics_{date_str}.json"
        
        with open(metrics_file, 'w') as f:
            json.dump(asdict(daily_metrics), f, indent=2, default=str)
    
    async def _save_analytics_report(self, report: Dict[str, Any], date: datetime):
        """Save analytics report"""
        reports_dir = Path(__file__).parent / "analytics" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        date_str = date.strftime("%Y-%m-%d")
        report_file = reports_dir / f"analytics_report_{date_str}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📄 Analytics report saved: {report_file}")
    
    def get_tracker_status(self) -> Dict[str, Any]:
        """Get current tracker status"""
        return {
            "videos_tracked": len(self.video_metrics),
            "platforms_active": len(set(v.platform for v in self.video_metrics.values())),
            "daily_metrics_count": len(self.daily_metrics),
            "tracking_start_date": min(v.upload_date for v in self.video_metrics.values() if self.video_metrics).isoformat() if self.video_metrics else None,
            "latest_metrics_date": max(v.upload_date for v in self.video_metrics.values() if self.video_metrics).isoformat() if self.video_metrics else None,
            "monetization_requirements": self.monetization_requirements
        }


def main():
    """Test the analytics tracker"""
    async def test_analytics():
        print("📊 Tenxsom AI Analytics Tracker")
        print("=" * 50)
        
        # Initialize tracker
        config_manager = ProductionConfigManager()
        tracker = AnalyticsTracker(config_manager)
        
        # Show tracker status
        status = tracker.get_tracker_status()
        print(f"\n📋 Tracker Status:")
        print(f"   Videos tracked: {status['videos_tracked']}")
        print(f"   Platforms active: {status['platforms_active']}")
        print(f"   Monetization requirements: YouTube (1K subs, 4K watch hours)")
        
        # Simulate video tracking
        print(f"\n🧪 Testing video tracking...")
        
        # Add sample videos
        sample_videos = [
            {"video_id": "yt_video_1", "platform": "youtube", "title": "AI Productivity Tips"},
            {"video_id": "tt_video_1", "platform": "tiktok", "title": "Quick AI Hack"},
            {"video_id": "ig_video_1", "platform": "instagram", "title": "AI Innovation"},
        ]
        
        for video in sample_videos:
            await tracker.track_video_upload(
                video_id=video["video_id"],
                platform=video["platform"],
                title=video["title"]
            )
        
        # Simulate performance updates
        print(f"\n📈 Simulating performance updates...")
        
        import random
        for video in sample_videos:
            await tracker.update_video_metrics(video["video_id"], {
                "views": random.randint(100, 5000),
                "likes": random.randint(10, 200),
                "comments": random.randint(5, 50),
                "watch_time_minutes": random.uniform(50, 300),
                "ctr": random.uniform(0.02, 0.08),
                "subscriber_gain": random.randint(1, 10) if video["platform"] == "youtube" else 0
            })
        
        # Generate analytics report
        print(f"\n📊 Generating analytics report...")
        report = await tracker.generate_analytics_report()
        
        print(f"\n✅ Analytics Report Generated:")
        print(f"   Total videos: {report['total_videos_tracked']}")
        print(f"   Daily views: {report['daily_metrics']['total_views']}")
        print(f"   Subscriber growth: {report['daily_metrics']['subscriber_growth']}")
        print(f"   Monetization eligible: {report['daily_metrics']['monetization_eligible']}")
        
        # Show monetization progress
        if 'monetization_progress' in report:
            progress = report['monetization_progress']
            print(f"\n🎯 Monetization Progress:")
            print(f"   Overall: {progress['progress_percentages']['overall']}%")
            print(f"   Subscribers: {progress['current_metrics']['subscribers']}/1000")
            print(f"   Watch hours: {progress['current_metrics']['watch_hours']}/4000")
        
        # Show recommendations
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   • {rec}")
        
        print(f"\n🎯 Analytics tracker ready for production monitoring!")
        
        return report
    
    # Run test
    asyncio.run(test_analytics())


if __name__ == "__main__":
    main()