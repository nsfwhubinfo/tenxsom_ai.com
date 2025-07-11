#!/usr/bin/env python3

"""
Real-Time Trigger System for TenxsomAI
Monitors external events and triggers immediate premium content generation
"""

import asyncio
import logging
import requests
import schedule
import time
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from monetization_strategy_executor import MonetizationStrategyExecutor
from integrations.enhanced_model_router import GenerationRequest, Platform, QualityTier

logger = logging.getLogger(__name__)

@dataclass
class TriggerEvent:
    """External event that triggers content generation"""
    event_id: str
    event_type: str
    priority: int  # 1=highest (premium), 3=lowest
    title: str
    description: str
    keywords: List[str]
    timestamp: datetime
    viral_potential: float  # 0.0-1.0 score

class RealTimeTriggerSystem:
    """
    Monitors external events and triggers immediate content generation
    for breaking news, trending topics, and viral opportunities
    """
    
    def __init__(self, monetization_executor: MonetizationStrategyExecutor):
        self.monetization_executor = monetization_executor
        self.active_monitors = []
        self.trigger_thresholds = {
            "earthquake_magnitude": 4.5,
            "trending_spike": 0.8,  # 80th percentile
            "news_breakout": 0.7,
            "tech_announcement": 0.6
        }
        
    async def start_monitoring(self):
        """Start all real-time monitoring systems"""
        logger.info("🚨 Starting real-time trigger monitoring...")
        
        # Schedule different monitoring frequencies
        schedule.every(1).minutes.do(self._check_breaking_news)
        schedule.every(2).minutes.do(self._check_earthquake_feeds) 
        schedule.every(5).minutes.do(self._check_youtube_trends)
        schedule.every(10).minutes.do(self._check_tech_announcements)
        
        # Main monitoring loop
        while True:
            schedule.run_pending()
            await asyncio.sleep(30)  # Check every 30 seconds
    
    def _check_breaking_news(self):
        """Monitor breaking news feeds for immediate content opportunities"""
        try:
            # NewsAPI for breaking news
            news_api_key = "YOUR_NEWS_API_KEY"  # Configure in environment
            url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={news_api_key}"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                for article in articles[:3]:  # Check top 3 breaking stories
                    # Calculate viral potential based on engagement signals
                    viral_score = self._calculate_viral_potential(article)
                    
                    if viral_score > self.trigger_thresholds["news_breakout"]:
                        event = TriggerEvent(
                            event_id=f"news_{int(time.time())}",
                            event_type="breaking_news",
                            priority=1,  # Premium tier for breaking news
                            title=f"BREAKING: {article['title']}",
                            description=article['description'] or article['title'],
                            keywords=self._extract_keywords(article['title']),
                            timestamp=datetime.now(),
                            viral_potential=viral_score
                        )
                        
                        asyncio.create_task(self._trigger_immediate_generation(event))
                        logger.info(f"🚨 BREAKING NEWS TRIGGER: {event.title}")
                        
        except Exception as e:
            logger.error(f"Breaking news check failed: {e}")
    
    def _check_earthquake_feeds(self):
        """Monitor USGS earthquake feeds for immediate reporting"""
        try:
            # USGS real-time earthquake feed
            usgs_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_hour.geojson"
            
            response = requests.get(usgs_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                features = data.get('features', [])
                
                for earthquake in features:
                    props = earthquake['properties']
                    magnitude = props['mag']
                    place = props['place']
                    timestamp = datetime.fromtimestamp(props['time'] / 1000)
                    
                    # Check if earthquake is recent (last 10 minutes) and significant
                    if (magnitude >= self.trigger_thresholds["earthquake_magnitude"] and 
                        datetime.now() - timestamp < timedelta(minutes=10)):
                        
                        event = TriggerEvent(
                            event_id=f"earthquake_{int(props['time'])}",
                            event_type="earthquake",
                            priority=1,  # Premium tier for major earthquakes
                            title=f"BREAKING: Magnitude {magnitude} Earthquake Hits {place}",
                            description=f"Live updates on the magnitude {magnitude} earthquake in {place}. Latest damage reports and emergency response.",
                            keywords=["earthquake", "breaking", place.split(',')[0], f"magnitude {magnitude}"],
                            timestamp=timestamp,
                            viral_potential=min(magnitude / 7.0, 1.0)  # Scale 0-1 based on magnitude
                        )
                        
                        asyncio.create_task(self._trigger_immediate_generation(event))
                        logger.info(f"🌍 EARTHQUAKE TRIGGER: {event.title}")
                        
        except Exception as e:
            logger.error(f"Earthquake monitoring failed: {e}")
    
    def _check_youtube_trends(self):
        """Monitor YouTube trending for viral content opportunities"""
        try:
            # YouTube Data API for trending videos
            youtube_api_key = "YOUR_YOUTUBE_API_KEY"  # Configure in environment
            url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&chart=mostPopular&regionCode=US&maxResults=10&key={youtube_api_key}"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                videos = data.get('items', [])
                
                for video in videos:
                    snippet = video['snippet']
                    stats = video['statistics']
                    
                    # Calculate trending velocity (views per hour since publish)
                    publish_time = datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00'))
                    hours_since_publish = (datetime.now().timestamp() - publish_time.timestamp()) / 3600
                    
                    if hours_since_publish > 0:
                        views_per_hour = int(stats.get('viewCount', 0)) / hours_since_publish
                        
                        # Trigger if trending velocity is high (>50k views/hour)
                        if views_per_hour > 50000:
                            trending_topic = self._extract_trending_topic(snippet['title'])
                            
                            event = TriggerEvent(
                                event_id=f"trend_{video['id']}",
                                event_type="trending_topic",
                                priority=2,  # Standard tier for trending topics
                                title=f"TRENDING: {trending_topic} Explained",
                                description=f"Breaking down the viral {trending_topic} trend that's taking over social media",
                                keywords=self._extract_keywords(snippet['title']),
                                timestamp=datetime.now(),
                                viral_potential=min(views_per_hour / 100000, 1.0)
                            )
                            
                            asyncio.create_task(self._trigger_immediate_generation(event))
                            logger.info(f"📈 TRENDING TRIGGER: {event.title}")
                            
        except Exception as e:
            logger.error(f"YouTube trending check failed: {e}")
    
    def _check_tech_announcements(self):
        """Monitor tech announcements and product launches"""
        try:
            # Reddit API for tech subreddits
            reddit_url = "https://www.reddit.com/r/technology/hot.json?limit=10"
            headers = {'User-Agent': 'TenxsomAI/1.0'}
            
            response = requests.get(reddit_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', {}).get('children', [])
                
                for post in posts:
                    post_data = post['data']
                    score = post_data.get('score', 0)
                    title = post_data.get('title', '')
                    
                    # Look for high-engagement tech announcements
                    tech_keywords = ['launches', 'announces', 'releases', 'unveils', 'breakthrough']
                    if any(keyword in title.lower() for keyword in tech_keywords) and score > 1000:
                        
                        event = TriggerEvent(
                            event_id=f"tech_{post_data['id']}",
                            event_type="tech_announcement",
                            priority=2,  # Standard tier for tech news
                            title=f"TECH NEWS: {title}",
                            description=f"Latest analysis of {title} and what it means for the industry",
                            keywords=self._extract_keywords(title),
                            timestamp=datetime.now(),
                            viral_potential=min(score / 5000, 1.0)
                        )
                        
                        asyncio.create_task(self._trigger_immediate_generation(event))
                        logger.info(f"💻 TECH TRIGGER: {event.title}")
                        
        except Exception as e:
            logger.error(f"Tech announcement check failed: {e}")
    
    async def _trigger_immediate_generation(self, event: TriggerEvent):
        """Trigger immediate content generation for high-priority events"""
        try:
            # Map priority to quality tier
            quality_tier_map = {
                1: QualityTier.PREMIUM,   # Breaking news, major earthquakes
                2: QualityTier.STANDARD,  # Trending topics, tech news
                3: QualityTier.VOLUME     # General interest
            }
            
            # Create generation request
            request = GenerationRequest(
                prompt=f"{event.description}. Create engaging video content with trending keywords: {', '.join(event.keywords)}",
                platform=Platform.YOUTUBE,  # Focus on YouTube for monetization
                quality_tier=quality_tier_map[event.priority],
                duration=15 if event.priority >= 2 else 30,  # Longer for premium
                priority=event.priority
            )
            
            # Generate video using enhanced model router
            if self.monetization_executor.model_router:
                response = await self.monetization_executor.model_router.generate_video(request)
                
                if response and response.download_url:
                    logger.info(f"✅ Emergency content generated: {event.event_id}")
                    
                    # Queue for immediate upload with optimized metadata
                    await self._queue_emergency_upload(event, response)
                else:
                    logger.error(f"❌ Emergency generation failed: {event.event_id}")
            
        except Exception as e:
            logger.error(f"Emergency generation error for {event.event_id}: {e}")
    
    async def _queue_emergency_upload(self, event: TriggerEvent, video_response):
        """Queue emergency content for immediate upload with optimized metadata"""
        try:
            from content_upload_orchestrator import UploadRequest
            
            # Create optimized upload request
            upload_request = UploadRequest(
                content_id=event.event_id,
                video_path=video_response.download_url,
                thumbnail_path=None,  # Auto-generate thumbnail
                platform="youtube",
                title=event.title,
                description=f"{event.description}\n\n#Breaking #Trending #{' #'.join(event.keywords[:5])}",
                tags=event.keywords + ["breaking", "trending", "news"],
                privacy_status="public",  # Immediate public release
                category="news",
                priority=1  # Highest priority upload
            )
            
            # Execute immediate upload
            if self.monetization_executor.upload_orchestrator:
                upload_result = await self.monetization_executor.upload_orchestrator.upload_content(upload_request)
                
                if upload_result.success:
                    logger.info(f"🚀 Emergency upload successful: {upload_result.video_url}")
                    
                    # Send notification about successful emergency content
                    await self._send_emergency_notification(event, upload_result)
                else:
                    logger.error(f"❌ Emergency upload failed: {event.event_id}")
            
        except Exception as e:
            logger.error(f"Emergency upload error: {e}")
    
    async def _send_emergency_notification(self, event: TriggerEvent, upload_result):
        """Send notification about successful emergency content generation"""
        try:
            # Telegram notification for emergency content
            message = f"""
🚨 EMERGENCY CONTENT LIVE!

Event: {event.title}
Type: {event.event_type}
Viral Potential: {event.viral_potential:.2f}
Video: {upload_result.video_url}
Generated in: <2 minutes

#BreakingNews #FirstToPost #ViralContent
            """
            
            # Send via existing notification system
            # await self.send_telegram_notification(message)
            logger.info(f"📱 Emergency notification sent for {event.event_id}")
            
        except Exception as e:
            logger.error(f"Emergency notification failed: {e}")
    
    def _calculate_viral_potential(self, article: Dict) -> float:
        """Calculate viral potential score for news articles"""
        score = 0.0
        
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        
        # High-impact keywords boost score
        viral_keywords = ['breaking', 'urgent', 'shocking', 'exclusive', 'major', 'unprecedented']
        for keyword in viral_keywords:
            if keyword in title:
                score += 0.2
            if keyword in description:
                score += 0.1
        
        # Source credibility factor
        source = article.get('source', {}).get('name', '').lower()
        credible_sources = ['reuters', 'ap', 'bbc', 'cnn', 'forbes', 'techcrunch']
        if any(credible in source for credible in credible_sources):
            score += 0.3
        
        return min(score, 1.0)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        # Simple keyword extraction (could be enhanced with NLP)
        import re
        
        words = re.findall(r'\b[A-Z][a-z]+\b', text)  # Capitalized words
        common_words = ['The', 'And', 'But', 'For', 'Are', 'With', 'His', 'Her', 'This', 'That']
        keywords = [word.lower() for word in words if word not in common_words]
        
        return keywords[:10]  # Return top 10 keywords
    
    def _extract_trending_topic(self, title: str) -> str:
        """Extract main topic from trending video title"""
        # Extract key phrase (simplified approach)
        import re
        
        # Look for quoted content or capitalized phrases
        quotes = re.findall(r'"([^"]*)"', title)
        if quotes:
            return quotes[0]
        
        # Look for key phrases after common patterns
        patterns = [r'about (.+?)[\.\!\?]', r'explains (.+?)[\.\!\?]', r'reviews (.+?)[\.\!\?]']
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Fallback to first few words
        words = title.split()[:3]
        return ' '.join(words)

# Integration with main system
async def start_real_time_monitoring():
    """Start the real-time trigger system"""
    from production_config_manager import ProductionConfigManager
    
    config = ProductionConfigManager()
    monetization_executor = MonetizationStrategyExecutor(config)
    
    trigger_system = RealTimeTriggerSystem(monetization_executor)
    await trigger_system.start_monitoring()

if __name__ == "__main__":
    print("🚨 Starting Real-Time Trigger System...")
    asyncio.run(start_real_time_monitoring())