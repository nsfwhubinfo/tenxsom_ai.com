#!/usr/bin/env python3

"""
Enhanced Viral Opportunity Detection for TenxsomAI
Advanced AI-powered viral content detection with predictive modeling and real-time monitoring
"""

import asyncio
import logging
import json
import requests
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import hashlib
import pickle
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer

# Import existing trigger system
from real_time_trigger_system import RealTimeTriggerSystem, TriggerEvent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ViralCategory(Enum):
    """Categories of viral content"""
    BREAKING_NEWS = "breaking_news"
    TRENDING_TOPIC = "trending_topic"
    VIRAL_CHALLENGE = "viral_challenge"
    CELEBRITY_EVENT = "celebrity_event"
    TECH_ANNOUNCEMENT = "tech_announcement"
    SOCIAL_PHENOMENON = "social_phenomenon"
    MEME_TREND = "meme_trend"
    EDUCATIONAL_VIRAL = "educational_viral"


class ViralStage(Enum):
    """Stages of viral content lifecycle"""
    EMERGING = "emerging"         # Just starting to gain traction
    ACCELERATING = "accelerating" # Rapid growth phase
    PEAK = "peak"                # Maximum viral potential
    DECLINING = "declining"       # Past peak but still relevant
    EXPIRED = "expired"          # No longer viral


@dataclass
class ViralSignal:
    """Individual viral signal detected"""
    signal_id: str
    source: str
    content: str
    category: ViralCategory
    stage: ViralStage
    viral_score: float
    velocity: float  # Rate of growth
    reach_estimate: int
    confidence: float
    detected_at: datetime
    predicted_peak: datetime
    opportunity_window: Tuple[datetime, datetime]
    keywords: List[str]
    sentiment: float
    engagement_metrics: Dict[str, Any]


@dataclass
class ViralOpportunity:
    """Comprehensive viral opportunity with AI predictions"""
    opportunity_id: str
    primary_signal: ViralSignal
    supporting_signals: List[ViralSignal]
    overall_viral_score: float
    urgency_level: int  # 1-10, 10 being most urgent
    content_angle: str
    target_audience: List[str]
    optimal_content_format: str
    predicted_performance: Dict[str, Any]
    competition_analysis: Dict[str, Any]
    action_recommendations: List[str]
    resource_requirements: Dict[str, Any]
    expected_roi: float


class EnhancedViralOpportunityDetection:
    """
    Advanced viral opportunity detection system with AI-powered prediction
    
    Features:
    - Multi-source viral signal aggregation
    - AI-powered viral potential prediction
    - Real-time trend velocity calculation
    - Competitive landscape analysis
    - Optimal timing recommendations
    - Content format optimization
    - Audience targeting suggestions
    - ROI prediction and resource allocation
    """
    
    def __init__(self, config_manager=None):
        """Initialize enhanced viral detection system"""
        self.config = config_manager
        
        # Initialize base trigger system
        self.base_trigger_system = RealTimeTriggerSystem(None)
        
        # AI models for viral prediction
        self.ai_models = {
            "viral_classifier": RandomForestClassifier(n_estimators=150, random_state=42),
            "viral_scorer": GradientBoostingRegressor(n_estimators=100, random_state=42),
            "velocity_predictor": RandomForestRegressor(n_estimators=80, random_state=42),
            "peak_predictor": RandomForestRegressor(n_estimators=60, random_state=42)
        }
        
        # Text analysis models
        self.text_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.scalers = {
            model_name: StandardScaler() 
            for model_name in self.ai_models.keys()
        }
        
        # Viral detection configuration
        self.detection_config = {
            "monitoring_sources": {
                "twitter": {"weight": 0.3, "api_limit": 1000},
                "reddit": {"weight": 0.25, "api_limit": 500},
                "youtube": {"weight": 0.2, "api_limit": 100},
                "google_trends": {"weight": 0.15, "api_limit": 200},
                "news_apis": {"weight": 0.1, "api_limit": 300}
            },
            "viral_thresholds": {
                "minimum_viral_score": 0.6,
                "velocity_threshold": 0.8,
                "engagement_threshold": 1000,
                "reach_threshold": 10000,
                "confidence_threshold": 0.7
            },
            "timing_optimization": {
                "max_opportunity_window_hours": 24,
                "urgent_response_minutes": 15,
                "competitive_analysis_depth": 10
            },
            "content_optimization": {
                "format_preferences": {
                    "short_video": 0.4,
                    "long_video": 0.3,
                    "image_post": 0.2,
                    "text_post": 0.1
                },
                "audience_targeting_precision": 0.8
            }
        }
        
        # Data storage
        self.viral_signals = {}
        self.viral_opportunities = {}
        self.detection_history = []
        self.competitive_intelligence = {}
        
        # Real-time monitoring state
        self.monitoring_active = False
        self.last_analysis_time = datetime.now()
        
        # Load existing models and data
        self._load_ai_models()
        self._initialize_monitoring_sources()
        
    def _load_ai_models(self):
        """Load pre-trained AI models for viral detection"""
        
        models_path = Path("viral_detection_models")
        models_path.mkdir(exist_ok=True)
        
        for model_name in self.ai_models.keys():
            model_file = models_path / f"{model_name}.pkl"
            scaler_file = models_path / f"{model_name}_scaler.pkl"
            
            try:
                if model_file.exists() and scaler_file.exists():
                    with open(model_file, 'rb') as f:
                        self.ai_models[model_name] = pickle.load(f)
                    
                    with open(scaler_file, 'rb') as f:
                        self.scalers[model_name] = pickle.load(f)
                    
                    logger.info(f"🧠 Loaded viral detection model: {model_name}")
                    
            except Exception as e:
                logger.warning(f"Failed to load viral model {model_name}: {e}")
        
        # Load text vectorizer
        vectorizer_file = models_path / "text_vectorizer.pkl"
        if vectorizer_file.exists():
            try:
                with open(vectorizer_file, 'rb') as f:
                    self.text_vectorizer = pickle.load(f)
                logger.info("📝 Loaded text vectorizer for viral detection")
            except Exception as e:
                logger.warning(f"Failed to load text vectorizer: {e}")
    
    def _save_ai_models(self):
        """Save trained AI models"""
        
        models_path = Path("viral_detection_models")
        models_path.mkdir(exist_ok=True)
        
        for model_name, model in self.ai_models.items():
            try:
                model_file = models_path / f"{model_name}.pkl"
                scaler_file = models_path / f"{model_name}_scaler.pkl"
                
                with open(model_file, 'wb') as f:
                    pickle.dump(model, f)
                
                with open(scaler_file, 'wb') as f:
                    pickle.dump(self.scalers[model_name], f)
                    
            except Exception as e:
                logger.error(f"Failed to save viral model {model_name}: {e}")
        
        # Save text vectorizer
        try:
            vectorizer_file = models_path / "text_vectorizer.pkl"
            with open(vectorizer_file, 'wb') as f:
                pickle.dump(self.text_vectorizer, f)
        except Exception as e:
            logger.error(f"Failed to save text vectorizer: {e}")
    
    def _initialize_monitoring_sources(self):
        """Initialize monitoring sources with API configurations"""
        
        # API configurations (would be loaded from environment in production)
        self.api_configs = {
            "twitter": {
                "bearer_token": "YOUR_TWITTER_BEARER_TOKEN",
                "rate_limit": 300,  # requests per 15 minutes
                "endpoints": {
                    "trending": "https://api.twitter.com/2/trends/by/woeid/1",
                    "search": "https://api.twitter.com/2/tweets/search/recent"
                }
            },
            "reddit": {
                "client_id": "YOUR_REDDIT_CLIENT_ID",
                "client_secret": "YOUR_REDDIT_CLIENT_SECRET",
                "user_agent": "TenxsomAI_ViralDetector/1.0",
                "endpoints": {
                    "hot": "https://www.reddit.com/r/all/hot.json",
                    "rising": "https://www.reddit.com/r/all/rising.json"
                }
            },
            "youtube": {
                "api_key": "YOUR_YOUTUBE_API_KEY",
                "endpoints": {
                    "trending": "https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&chart=mostPopular"
                }
            },
            "google_trends": {
                "endpoints": {
                    "trending": "https://trends.google.com/trends/api/dailytrends"
                }
            }
        }
    
    async def start_continuous_monitoring(self):
        """Start continuous viral opportunity monitoring"""
        
        if self.monitoring_active:
            logger.warning("Viral monitoring already active")
            return
        
        self.monitoring_active = True
        logger.info("🚨 Starting enhanced viral opportunity monitoring...")
        
        try:
            while self.monitoring_active:
                # Perform comprehensive viral scan
                await self._perform_viral_scan()
                
                # Analyze detected signals
                await self._analyze_viral_signals()
                
                # Generate opportunities
                await self._generate_viral_opportunities()
                
                # Clean up expired signals
                self._cleanup_expired_signals()
                
                # Wait before next scan (adaptive frequency)
                wait_time = self._calculate_adaptive_scan_frequency()
                await asyncio.sleep(wait_time)
                
        except Exception as e:
            logger.error(f"Viral monitoring error: {e}")
        finally:
            self.monitoring_active = False
    
    async def _perform_viral_scan(self):
        """Perform comprehensive viral content scan across all sources"""
        
        scan_start = datetime.now()
        new_signals = []
        
        # Scan each monitoring source
        for source, config in self.detection_config["monitoring_sources"].items():
            try:
                source_signals = await self._scan_source(source, config)
                new_signals.extend(source_signals)
                
            except Exception as e:
                logger.warning(f"Failed to scan {source}: {e}")
        
        # Process new signals with AI
        for signal in new_signals:
            enhanced_signal = await self._enhance_signal_with_ai(signal)
            
            if enhanced_signal.viral_score >= self.detection_config["viral_thresholds"]["minimum_viral_score"]:
                self.viral_signals[enhanced_signal.signal_id] = enhanced_signal
                logger.info(f"🔥 Detected viral signal: {enhanced_signal.content[:50]}... (score: {enhanced_signal.viral_score:.3f})")
        
        scan_duration = (datetime.now() - scan_start).total_seconds()
        logger.info(f"📊 Viral scan completed: {len(new_signals)} signals, {scan_duration:.1f}s")
    
    async def _scan_source(self, source: str, config: Dict[str, Any]) -> List[ViralSignal]:
        """Scan individual source for viral signals"""
        
        signals = []
        
        if source == "twitter":
            signals.extend(await self._scan_twitter())
        elif source == "reddit":
            signals.extend(await self._scan_reddit())
        elif source == "youtube":
            signals.extend(await self._scan_youtube())
        elif source == "google_trends":
            signals.extend(await self._scan_google_trends())
        elif source == "news_apis":
            signals.extend(await self._scan_news_apis())
        
        return signals
    
    async def _scan_twitter(self) -> List[ViralSignal]:
        """Scan Twitter for viral signals"""
        
        signals = []
        
        try:
            # Simulate Twitter API call (replace with actual API integration)
            trending_data = self._simulate_twitter_trending()
            
            for trend in trending_data:
                signal = ViralSignal(
                    signal_id=f"tw_{hashlib.md5(trend['query'].encode()).hexdigest()[:8]}",
                    source="twitter",
                    content=trend["query"],
                    category=self._classify_viral_category(trend["query"]),
                    stage=ViralStage.ACCELERATING,
                    viral_score=trend.get("volume", 1000) / 10000,  # Normalize
                    velocity=trend.get("velocity", 0.5),
                    reach_estimate=trend.get("volume", 1000) * 10,
                    confidence=0.8,
                    detected_at=datetime.now(),
                    predicted_peak=datetime.now() + timedelta(hours=6),
                    opportunity_window=(datetime.now(), datetime.now() + timedelta(hours=12)),
                    keywords=trend["query"].split(),
                    sentiment=trend.get("sentiment", 0.0),
                    engagement_metrics={
                        "tweets_per_hour": trend.get("volume", 1000),
                        "retweet_rate": 0.15,
                        "engagement_rate": 0.08
                    }
                )
                signals.append(signal)
                
        except Exception as e:
            logger.error(f"Twitter scan error: {e}")
        
        return signals
    
    async def _scan_reddit(self) -> List[ViralSignal]:
        """Scan Reddit for viral signals"""
        
        signals = []
        
        try:
            # Use Reddit API to get hot posts
            url = "https://www.reddit.com/r/all/hot.json?limit=25"
            headers = {'User-Agent': 'TenxsomAI_ViralDetector/1.0'}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', {}).get('children', [])
                
                for post in posts:
                    post_data = post['data']
                    
                    # Filter for high-engagement posts
                    score = post_data.get('score', 0)
                    if score > 5000:  # High-engagement threshold
                        
                        signal = ViralSignal(
                            signal_id=f"rd_{post_data['id']}",
                            source="reddit",
                            content=post_data.get('title', ''),
                            category=self._classify_viral_category(post_data.get('title', '')),
                            stage=self._determine_viral_stage(post_data),
                            viral_score=min(score / 20000, 1.0),  # Normalize to 0-1
                            velocity=self._calculate_reddit_velocity(post_data),
                            reach_estimate=score * 50,  # Estimate reach
                            confidence=0.75,
                            detected_at=datetime.now(),
                            predicted_peak=datetime.now() + timedelta(hours=8),
                            opportunity_window=(datetime.now(), datetime.now() + timedelta(hours=16)),
                            keywords=self._extract_keywords(post_data.get('title', '')),
                            sentiment=self._analyze_sentiment(post_data.get('title', '')),
                            engagement_metrics={
                                "score": score,
                                "num_comments": post_data.get('num_comments', 0),
                                "upvote_ratio": post_data.get('upvote_ratio', 0.5),
                                "awards": len(post_data.get('all_awardings', []))
                            }
                        )
                        signals.append(signal)
                        
        except Exception as e:
            logger.error(f"Reddit scan error: {e}")
        
        return signals
    
    async def _scan_youtube(self) -> List[ViralSignal]:
        """Scan YouTube for viral signals"""
        
        signals = []
        
        try:
            # Simulate YouTube trending data (replace with actual API)
            trending_data = self._simulate_youtube_trending()
            
            for video in trending_data:
                signal = ViralSignal(
                    signal_id=f"yt_{video['video_id']}",
                    source="youtube",
                    content=video["title"],
                    category=self._classify_viral_category(video["title"]),
                    stage=ViralStage.PEAK,
                    viral_score=min(video.get("views", 0) / 1000000, 1.0),  # Normalize by 1M views
                    velocity=video.get("views_per_hour", 1000) / 10000,
                    reach_estimate=video.get("views", 0),
                    confidence=0.9,
                    detected_at=datetime.now(),
                    predicted_peak=datetime.now() + timedelta(hours=2),
                    opportunity_window=(datetime.now(), datetime.now() + timedelta(hours=8)),
                    keywords=self._extract_keywords(video["title"]),
                    sentiment=self._analyze_sentiment(video["title"]),
                    engagement_metrics={
                        "views": video.get("views", 0),
                        "likes": video.get("likes", 0),
                        "comments": video.get("comments", 0),
                        "duration": video.get("duration", 0)
                    }
                )
                signals.append(signal)
                
        except Exception as e:
            logger.error(f"YouTube scan error: {e}")
        
        return signals
    
    async def _scan_google_trends(self) -> List[ViralSignal]:
        """Scan Google Trends for viral signals"""
        
        signals = []
        
        try:
            # Simulate Google Trends data
            trends_data = self._simulate_google_trends()
            
            for trend in trends_data:
                signal = ViralSignal(
                    signal_id=f"gt_{hashlib.md5(trend['keyword'].encode()).hexdigest()[:8]}",
                    source="google_trends",
                    content=trend["keyword"],
                    category=self._classify_viral_category(trend["keyword"]),
                    stage=ViralStage.EMERGING,
                    viral_score=trend.get("search_volume", 0) / 100000,  # Normalize
                    velocity=trend.get("growth_rate", 0) / 100,
                    reach_estimate=trend.get("search_volume", 0) * 5,
                    confidence=0.7,
                    detected_at=datetime.now(),
                    predicted_peak=datetime.now() + timedelta(hours=12),
                    opportunity_window=(datetime.now(), datetime.now() + timedelta(hours=24)),
                    keywords=[trend["keyword"]],
                    sentiment=0.0,  # Neutral for search trends
                    engagement_metrics={
                        "search_volume": trend.get("search_volume", 0),
                        "growth_rate": trend.get("growth_rate", 0),
                        "related_queries": trend.get("related_queries", [])
                    }
                )
                signals.append(signal)
                
        except Exception as e:
            logger.error(f"Google Trends scan error: {e}")
        
        return signals
    
    async def _scan_news_apis(self) -> List[ViralSignal]:
        """Scan news APIs for viral signals"""
        
        signals = []
        
        try:
            # Use base trigger system's news monitoring
            # This would integrate with the existing breaking news detection
            signals.extend(await self._get_breaking_news_signals())
            
        except Exception as e:
            logger.error(f"News API scan error: {e}")
        
        return signals
    
    async def _enhance_signal_with_ai(self, signal: ViralSignal) -> ViralSignal:
        """Enhance viral signal with AI predictions"""
        
        try:
            # Extract features for AI analysis
            features = self._extract_signal_features(signal)
            
            # Predict viral score using AI
            if hasattr(self.ai_models["viral_scorer"], 'predict'):
                scaled_features = self.scalers["viral_scorer"].transform([features])
                ai_viral_score = self.ai_models["viral_scorer"].predict(scaled_features)[0]
                
                # Combine with original score
                signal.viral_score = (signal.viral_score * 0.6 + ai_viral_score * 0.4)
            
            # Predict velocity
            if hasattr(self.ai_models["velocity_predictor"], 'predict'):
                scaled_features = self.scalers["velocity_predictor"].transform([features])
                ai_velocity = self.ai_models["velocity_predictor"].predict(scaled_features)[0]
                signal.velocity = max(signal.velocity, ai_velocity)
            
            # Predict peak timing
            peak_hours = self._predict_peak_timing(signal)
            signal.predicted_peak = signal.detected_at + timedelta(hours=peak_hours)
            
            # Update opportunity window
            window_duration = min(24, peak_hours + 6)  # Peak + 6 hours
            signal.opportunity_window = (
                signal.detected_at,
                signal.detected_at + timedelta(hours=window_duration)
            )
            
            # Update confidence based on AI predictions
            signal.confidence = min(signal.confidence * 1.1, 0.95)
            
        except Exception as e:
            logger.warning(f"AI enhancement failed for signal {signal.signal_id}: {e}")
        
        return signal
    
    def _extract_signal_features(self, signal: ViralSignal) -> np.ndarray:
        """Extract features from viral signal for AI analysis"""
        
        features = []
        
        # Basic signal features
        features.extend([
            signal.viral_score,
            signal.velocity,
            signal.reach_estimate / 100000,  # Normalize
            signal.confidence,
            len(signal.keywords),
            signal.sentiment,
        ])
        
        # Source encoding
        sources = ["twitter", "reddit", "youtube", "google_trends", "news_apis"]
        source_features = [1 if signal.source == src else 0 for src in sources]
        features.extend(source_features)
        
        # Category encoding
        category_features = [1 if signal.category == cat else 0 for cat in ViralCategory]
        features.extend(category_features)
        
        # Time-based features
        now = datetime.now()
        features.extend([
            now.hour,
            now.weekday(),
            1 if now.weekday() >= 5 else 0,  # Weekend
            1 if 18 <= now.hour <= 22 else 0,  # Prime time
        ])
        
        # Engagement features
        engagement = signal.engagement_metrics
        features.extend([
            len(engagement),  # Number of engagement metrics
            sum(isinstance(v, (int, float)) and v > 0 for v in engagement.values()),  # Positive metrics count
        ])
        
        # Text analysis features (simplified)
        content_length = len(signal.content)
        word_count = len(signal.content.split())
        exclamation_count = signal.content.count('!')
        question_count = signal.content.count('?')
        
        features.extend([
            content_length / 100,  # Normalize
            word_count,
            exclamation_count,
            question_count
        ])
        
        return np.array(features, dtype=float)
    
    def _predict_peak_timing(self, signal: ViralSignal) -> float:
        """Predict peak timing for viral content"""
        
        # Simple heuristic based on source and category
        base_hours = {
            "twitter": 4,
            "reddit": 8,
            "youtube": 12,
            "google_trends": 24,
            "news_apis": 2
        }
        
        category_modifiers = {
            ViralCategory.BREAKING_NEWS: 0.5,
            ViralCategory.TRENDING_TOPIC: 1.0,
            ViralCategory.VIRAL_CHALLENGE: 1.5,
            ViralCategory.CELEBRITY_EVENT: 0.8,
            ViralCategory.TECH_ANNOUNCEMENT: 1.2,
            ViralCategory.SOCIAL_PHENOMENON: 2.0,
            ViralCategory.MEME_TREND: 1.8,
            ViralCategory.EDUCATIONAL_VIRAL: 2.5
        }
        
        base = base_hours.get(signal.source, 8)
        modifier = category_modifiers.get(signal.category, 1.0)
        velocity_factor = 1.0 + signal.velocity  # Higher velocity = faster peak
        
        peak_hours = (base * modifier) / velocity_factor
        
        return max(1, min(48, peak_hours))  # 1-48 hours range
    
    async def _analyze_viral_signals(self):
        """Analyze viral signals for patterns and correlations"""
        
        if len(self.viral_signals) < 2:
            return
        
        # Group signals by category
        category_groups = {}
        for signal in self.viral_signals.values():
            category = signal.category
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(signal)
        
        # Analyze cross-signal correlations
        correlations = self._find_signal_correlations()
        
        # Update signal stages based on temporal analysis
        await self._update_signal_stages()
        
        logger.info(f"📊 Analyzed {len(self.viral_signals)} viral signals across {len(category_groups)} categories")
    
    def _find_signal_correlations(self) -> Dict[str, List[str]]:
        """Find correlations between viral signals"""
        
        correlations = {}
        
        signals_list = list(self.viral_signals.values())
        
        for i, signal1 in enumerate(signals_list):
            for signal2 in signals_list[i+1:]:
                
                # Check keyword overlap
                keyword_overlap = set(signal1.keywords) & set(signal2.keywords)
                if len(keyword_overlap) >= 2:
                    
                    correlation_id = f"{signal1.signal_id}+{signal2.signal_id}"
                    correlations[correlation_id] = {
                        "signals": [signal1.signal_id, signal2.signal_id],
                        "overlap_keywords": list(keyword_overlap),
                        "correlation_strength": len(keyword_overlap) / max(len(signal1.keywords), len(signal2.keywords))
                    }
        
        return correlations
    
    async def _update_signal_stages(self):
        """Update viral signal stages based on temporal analysis"""
        
        current_time = datetime.now()
        
        for signal in self.viral_signals.values():
            hours_since_detection = (current_time - signal.detected_at).total_seconds() / 3600
            hours_to_predicted_peak = (signal.predicted_peak - current_time).total_seconds() / 3600
            
            # Update stage based on timing
            if hours_to_predicted_peak > 6:
                signal.stage = ViralStage.EMERGING
            elif hours_to_predicted_peak > 0:
                signal.stage = ViralStage.ACCELERATING
            elif hours_to_predicted_peak > -6:
                signal.stage = ViralStage.PEAK
            elif hours_to_predicted_peak > -24:
                signal.stage = ViralStage.DECLINING
            else:
                signal.stage = ViralStage.EXPIRED
    
    async def _generate_viral_opportunities(self):
        """Generate actionable viral opportunities from signals"""
        
        # Clear old opportunities
        self.viral_opportunities = {}
        
        # Group signals for opportunity creation
        high_value_signals = [
            signal for signal in self.viral_signals.values()
            if (signal.viral_score >= 0.7 and 
                signal.stage in [ViralStage.EMERGING, ViralStage.ACCELERATING, ViralStage.PEAK])
        ]
        
        for primary_signal in high_value_signals:
            
            # Find supporting signals
            supporting_signals = self._find_supporting_signals(primary_signal)
            
            # Calculate overall opportunity score
            overall_score = self._calculate_opportunity_score(primary_signal, supporting_signals)
            
            if overall_score >= 0.6:  # Threshold for actionable opportunities
                
                opportunity = await self._create_viral_opportunity(
                    primary_signal, supporting_signals, overall_score
                )
                
                self.viral_opportunities[opportunity.opportunity_id] = opportunity
                
                logger.info(f"🎯 Generated viral opportunity: {opportunity.content_angle} (score: {overall_score:.3f})")
    
    def _find_supporting_signals(self, primary_signal: ViralSignal) -> List[ViralSignal]:
        """Find signals that support the primary viral opportunity"""
        
        supporting = []
        
        for signal in self.viral_signals.values():
            if signal.signal_id == primary_signal.signal_id:
                continue
            
            # Check for keyword overlap
            keyword_overlap = set(primary_signal.keywords) & set(signal.keywords)
            
            # Check for category similarity
            category_similarity = signal.category == primary_signal.category
            
            # Check for temporal proximity
            time_diff = abs((signal.detected_at - primary_signal.detected_at).total_seconds() / 3600)
            temporal_proximity = time_diff <= 6  # Within 6 hours
            
            # Calculate support score
            support_score = (
                len(keyword_overlap) / max(len(primary_signal.keywords), 1) * 0.5 +
                (1 if category_similarity else 0) * 0.3 +
                (1 if temporal_proximity else 0) * 0.2
            )
            
            if support_score >= 0.4:
                supporting.append(signal)
        
        return supporting[:3]  # Limit to top 3 supporting signals
    
    def _calculate_opportunity_score(self, 
                                   primary_signal: ViralSignal,
                                   supporting_signals: List[ViralSignal]) -> float:
        """Calculate overall opportunity score"""
        
        # Primary signal contribution (70%)
        primary_score = (
            primary_signal.viral_score * 0.4 +
            primary_signal.velocity * 0.3 +
            primary_signal.confidence * 0.3
        )
        
        # Supporting signals contribution (20%)
        if supporting_signals:
            support_score = sum(s.viral_score for s in supporting_signals) / len(supporting_signals)
        else:
            support_score = 0
        
        # Timing bonus (10%)
        timing_bonus = 1.0 if primary_signal.stage in [ViralStage.EMERGING, ViralStage.ACCELERATING] else 0.5
        
        overall_score = (
            primary_score * 0.7 +
            support_score * 0.2 +
            timing_bonus * 0.1
        )
        
        return round(overall_score, 3)
    
    async def _create_viral_opportunity(self, 
                                      primary_signal: ViralSignal,
                                      supporting_signals: List[ViralSignal],
                                      overall_score: float) -> ViralOpportunity:
        """Create comprehensive viral opportunity"""
        
        # Generate content angle
        content_angle = self._generate_content_angle(primary_signal, supporting_signals)
        
        # Determine urgency
        urgency_level = self._calculate_urgency_level(primary_signal)
        
        # Predict performance
        predicted_performance = await self._predict_opportunity_performance(primary_signal, overall_score)
        
        # Analyze competition
        competition_analysis = await self._analyze_competition(primary_signal)
        
        # Generate recommendations
        action_recommendations = self._generate_action_recommendations(primary_signal)
        
        # Calculate resource requirements
        resource_requirements = self._calculate_resource_requirements(primary_signal)
        
        # Calculate expected ROI
        expected_roi = self._calculate_expected_roi(predicted_performance, resource_requirements)
        
        # Target audience analysis
        target_audience = self._analyze_target_audience(primary_signal, supporting_signals)
        
        # Optimal content format
        optimal_format = self._determine_optimal_content_format(primary_signal)
        
        opportunity = ViralOpportunity(
            opportunity_id=f"viral_opp_{int(datetime.now().timestamp())}_{primary_signal.signal_id}",
            primary_signal=primary_signal,
            supporting_signals=supporting_signals,
            overall_viral_score=overall_score,
            urgency_level=urgency_level,
            content_angle=content_angle,
            target_audience=target_audience,
            optimal_content_format=optimal_format,
            predicted_performance=predicted_performance,
            competition_analysis=competition_analysis,
            action_recommendations=action_recommendations,
            resource_requirements=resource_requirements,
            expected_roi=expected_roi
        )
        
        return opportunity
    
    def _generate_content_angle(self, 
                              primary_signal: ViralSignal,
                              supporting_signals: List[ViralSignal]) -> str:
        """Generate content angle for viral opportunity"""
        
        # Extract key themes
        all_keywords = primary_signal.keywords[:]
        for signal in supporting_signals:
            all_keywords.extend(signal.keywords)
        
        # Find most common keywords
        keyword_counts = {}
        for keyword in all_keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Generate angle based on category and keywords
        category_angles = {
            ViralCategory.BREAKING_NEWS: f"Breaking: {top_keywords[0][0]} - What You Need to Know",
            ViralCategory.TRENDING_TOPIC: f"Why Everyone's Talking About {top_keywords[0][0]}",
            ViralCategory.VIRAL_CHALLENGE: f"The {top_keywords[0][0]} Challenge Explained",
            ViralCategory.CELEBRITY_EVENT: f"{top_keywords[0][0]} Update: Inside Story",
            ViralCategory.TECH_ANNOUNCEMENT: f"{top_keywords[0][0]}: Game-Changer or Hype?",
            ViralCategory.SOCIAL_PHENOMENON: f"The {top_keywords[0][0]} Phenomenon Taking Over",
            ViralCategory.MEME_TREND: f"Understanding the {top_keywords[0][0]} Meme",
            ViralCategory.EDUCATIONAL_VIRAL: f"Learn About {top_keywords[0][0]} in 60 Seconds"
        }
        
        return category_angles.get(primary_signal.category, f"Deep Dive: {top_keywords[0][0]}")
    
    def _calculate_urgency_level(self, signal: ViralSignal) -> int:
        """Calculate urgency level (1-10) for viral opportunity"""
        
        # Base urgency from viral score and velocity
        base_urgency = (signal.viral_score + signal.velocity) * 5
        
        # Stage modifier
        stage_modifiers = {
            ViralStage.EMERGING: 1.2,
            ViralStage.ACCELERATING: 1.5,
            ViralStage.PEAK: 1.0,
            ViralStage.DECLINING: 0.6,
            ViralStage.EXPIRED: 0.1
        }
        
        # Category modifier
        category_modifiers = {
            ViralCategory.BREAKING_NEWS: 1.8,
            ViralCategory.TRENDING_TOPIC: 1.4,
            ViralCategory.VIRAL_CHALLENGE: 1.2,
            ViralCategory.CELEBRITY_EVENT: 1.3,
            ViralCategory.TECH_ANNOUNCEMENT: 1.1,
            ViralCategory.SOCIAL_PHENOMENON: 1.0,
            ViralCategory.MEME_TREND: 1.1,
            ViralCategory.EDUCATIONAL_VIRAL: 0.8
        }
        
        urgency = (base_urgency * 
                  stage_modifiers.get(signal.stage, 1.0) * 
                  category_modifiers.get(signal.category, 1.0))
        
        return max(1, min(10, int(urgency)))
    
    async def _predict_opportunity_performance(self, 
                                             signal: ViralSignal,
                                             overall_score: float) -> Dict[str, Any]:
        """Predict performance metrics for viral opportunity"""
        
        # Base predictions from signal metrics
        base_views = signal.reach_estimate * 0.1  # 10% reach-to-views conversion
        base_engagement = 0.05  # 5% baseline engagement
        
        # Score multipliers
        score_multiplier = 1 + overall_score
        velocity_multiplier = 1 + signal.velocity
        
        predicted_views = int(base_views * score_multiplier * velocity_multiplier)
        predicted_engagement_rate = min(0.20, base_engagement * score_multiplier)
        
        # Viral probability
        viral_probability = min(0.95, overall_score * signal.velocity * 2)
        
        return {
            "predicted_views": predicted_views,
            "predicted_engagement_rate": round(predicted_engagement_rate, 4),
            "viral_probability": round(viral_probability, 3),
            "estimated_reach": int(predicted_views * 5),  # 5x views for reach
            "peak_performance_window": (signal.predicted_peak - timedelta(hours=2), 
                                      signal.predicted_peak + timedelta(hours=4)),
            "confidence_level": signal.confidence
        }
    
    async def _analyze_competition(self, signal: ViralSignal) -> Dict[str, Any]:
        """Analyze competitive landscape for viral opportunity"""
        
        # Simulate competitive analysis
        competition_level = min(1.0, signal.reach_estimate / 1000000)  # Higher reach = more competition
        
        return {
            "competition_level": round(competition_level, 3),
            "estimated_competitors": int(competition_level * 50),
            "market_saturation": "high" if competition_level > 0.7 else "medium" if competition_level > 0.4 else "low",
            "differentiation_opportunity": 1.0 - competition_level,
            "timing_advantage": 1.0 if signal.stage == ViralStage.EMERGING else 0.5
        }
    
    def _generate_action_recommendations(self, signal: ViralSignal) -> List[str]:
        """Generate specific action recommendations"""
        
        recommendations = []
        
        # Urgency-based recommendations
        if signal.stage == ViralStage.EMERGING:
            recommendations.extend([
                "URGENT: Create content immediately to ride the wave",
                "Monitor trend development closely",
                "Prepare multiple content angles"
            ])
        elif signal.stage == ViralStage.ACCELERATING:
            recommendations.extend([
                "Act quickly - trend is gaining momentum",
                "Focus on unique angle to stand out",
                "Optimize for maximum shareability"
            ])
        elif signal.stage == ViralStage.PEAK:
            recommendations.extend([
                "High competition - focus on unique perspective",
                "Leverage existing trend momentum",
                "Consider follow-up content strategy"
            ])
        
        # Category-specific recommendations
        category_recs = {
            ViralCategory.BREAKING_NEWS: [
                "Verify facts before publishing",
                "Focus on unique analysis or perspective",
                "Prepare for high engagement volume"
            ],
            ViralCategory.TRENDING_TOPIC: [
                "Add personal experience or expertise",
                "Create comprehensive explainer content",
                "Engage with trend community"
            ],
            ViralCategory.VIRAL_CHALLENGE: [
                "Participate authentically",
                "Add educational component",
                "Safety considerations if applicable"
            ]
        }
        
        recommendations.extend(category_recs.get(signal.category, []))
        
        return recommendations[:8]  # Limit to most important
    
    def _calculate_resource_requirements(self, signal: ViralSignal) -> Dict[str, Any]:
        """Calculate resource requirements for opportunity"""
        
        # Base requirements
        base_time_hours = 2
        base_budget = 50.0
        
        # Urgency modifiers
        urgency_multipliers = {
            ViralStage.EMERGING: {"time": 0.8, "budget": 1.2},
            ViralStage.ACCELERATING: {"time": 1.0, "budget": 1.0},
            ViralStage.PEAK: {"time": 1.5, "budget": 0.8},
            ViralStage.DECLINING: {"time": 2.0, "budget": 0.6}
        }
        
        multiplier = urgency_multipliers.get(signal.stage, {"time": 1.0, "budget": 1.0})
        
        # Quality requirements based on viral score
        if signal.viral_score > 0.8:
            quality_multiplier = {"time": 1.5, "budget": 2.0}  # High-quality content needed
        else:
            quality_multiplier = {"time": 1.0, "budget": 1.0}
        
        estimated_time = base_time_hours * multiplier["time"] * quality_multiplier["time"]
        estimated_budget = base_budget * multiplier["budget"] * quality_multiplier["budget"]
        
        return {
            "estimated_time_hours": round(estimated_time, 1),
            "estimated_budget": round(estimated_budget, 2),
            "complexity": "high" if signal.viral_score > 0.8 else "medium",
            "team_size": 1 if estimated_time <= 4 else 2,
            "tools_needed": ["video_editor", "thumbnail_creator", "social_scheduler"],
            "skill_requirements": ["content_creation", "trend_analysis", "rapid_production"]
        }
    
    def _calculate_expected_roi(self, 
                              predicted_performance: Dict[str, Any],
                              resource_requirements: Dict[str, Any]) -> float:
        """Calculate expected ROI for viral opportunity"""
        
        # Revenue calculation
        predicted_views = predicted_performance["predicted_views"]
        viral_probability = predicted_performance["viral_probability"]
        
        # Base revenue per view (varies by platform and monetization)
        revenue_per_view = 0.002  # $0.002 per view baseline
        
        # Viral bonus
        viral_bonus = 1 + viral_probability
        
        expected_revenue = predicted_views * revenue_per_view * viral_bonus
        
        # Cost calculation
        estimated_cost = resource_requirements["estimated_budget"]
        
        # ROI calculation
        roi = (expected_revenue - estimated_cost) / max(estimated_cost, 1.0)
        
        return round(roi, 2)
    
    def _analyze_target_audience(self, 
                               primary_signal: ViralSignal,
                               supporting_signals: List[ViralSignal]) -> List[str]:
        """Analyze target audience for viral opportunity"""
        
        audiences = []
        
        # Category-based audience mapping
        category_audiences = {
            ViralCategory.BREAKING_NEWS: ["news_consumers", "general_public"],
            ViralCategory.TRENDING_TOPIC: ["social_media_users", "trend_followers"],
            ViralCategory.VIRAL_CHALLENGE: ["young_adults", "social_creators"],
            ViralCategory.CELEBRITY_EVENT: ["entertainment_fans", "celebrity_followers"],
            ViralCategory.TECH_ANNOUNCEMENT: ["tech_enthusiasts", "early_adopters"],
            ViralCategory.SOCIAL_PHENOMENON: ["social_observers", "culture_enthusiasts"],
            ViralCategory.MEME_TREND: ["meme_community", "internet_culture"],
            ViralCategory.EDUCATIONAL_VIRAL: ["learners", "knowledge_seekers"]
        }
        
        audiences.extend(category_audiences.get(primary_signal.category, ["general_audience"]))
        
        # Source-based audience refinement
        if primary_signal.source == "reddit":
            audiences.append("reddit_community")
        elif primary_signal.source == "twitter":
            audiences.append("twitter_users")
        elif primary_signal.source == "youtube":
            audiences.append("video_consumers")
        
        return list(set(audiences))  # Remove duplicates
    
    def _determine_optimal_content_format(self, signal: ViralSignal) -> str:
        """Determine optimal content format for viral opportunity"""
        
        # Category-based format preferences
        category_formats = {
            ViralCategory.BREAKING_NEWS: "short_video",
            ViralCategory.TRENDING_TOPIC: "explainer_video",
            ViralCategory.VIRAL_CHALLENGE: "participation_video",
            ViralCategory.CELEBRITY_EVENT: "commentary_video",
            ViralCategory.TECH_ANNOUNCEMENT: "analysis_video",
            ViralCategory.SOCIAL_PHENOMENON: "documentary_style",
            ViralCategory.MEME_TREND: "reaction_video",
            ViralCategory.EDUCATIONAL_VIRAL: "tutorial_video"
        }
        
        base_format = category_formats.get(signal.category, "general_video")
        
        # Adjust based on urgency
        if signal.stage == ViralStage.EMERGING:
            return f"urgent_{base_format}"
        else:
            return base_format
    
    def _calculate_adaptive_scan_frequency(self) -> int:
        """Calculate adaptive scan frequency based on viral activity"""
        
        # Base frequency: 5 minutes
        base_frequency = 300
        
        # Adjust based on current viral activity
        high_activity_signals = len([
            s for s in self.viral_signals.values()
            if s.viral_score > 0.7 and s.stage in [ViralStage.EMERGING, ViralStage.ACCELERATING]
        ])
        
        # More activity = higher frequency
        if high_activity_signals > 5:
            return 180  # 3 minutes
        elif high_activity_signals > 2:
            return 240  # 4 minutes
        else:
            return base_frequency  # 5 minutes
    
    def _cleanup_expired_signals(self):
        """Clean up expired viral signals"""
        
        current_time = datetime.now()
        expired_signals = []
        
        for signal_id, signal in self.viral_signals.items():
            # Remove signals older than 48 hours or marked as expired
            hours_old = (current_time - signal.detected_at).total_seconds() / 3600
            
            if hours_old > 48 or signal.stage == ViralStage.EXPIRED:
                expired_signals.append(signal_id)
        
        for signal_id in expired_signals:
            del self.viral_signals[signal_id]
        
        if expired_signals:
            logger.info(f"🧹 Cleaned up {len(expired_signals)} expired viral signals")
    
    def stop_monitoring(self):
        """Stop viral opportunity monitoring"""
        self.monitoring_active = False
        logger.info("⏹️ Stopped viral opportunity monitoring")
    
    # Simulation methods for development/testing
    def _simulate_twitter_trending(self) -> List[Dict[str, Any]]:
        """Simulate Twitter trending data"""
        return [
            {"query": "AI breakthrough", "volume": 15000, "velocity": 0.8, "sentiment": 0.2},
            {"query": "climate summit", "volume": 8000, "velocity": 0.6, "sentiment": -0.1},
            {"query": "new smartphone", "volume": 12000, "velocity": 0.7, "sentiment": 0.5},
            {"query": "viral dance", "volume": 25000, "velocity": 0.9, "sentiment": 0.8},
            {"query": "space discovery", "volume": 18000, "velocity": 0.75, "sentiment": 0.6}
        ]
    
    def _simulate_youtube_trending(self) -> List[Dict[str, Any]]:
        """Simulate YouTube trending data"""
        return [
            {"video_id": "abc123", "title": "Mind-blowing AI Demo", "views": 500000, "likes": 25000, "comments": 3000, "duration": 180, "views_per_hour": 15000},
            {"video_id": "def456", "title": "Viral Challenge Gone Wrong", "views": 800000, "likes": 40000, "comments": 8000, "duration": 120, "views_per_hour": 25000},
            {"video_id": "ghi789", "title": "Breaking Tech News", "views": 300000, "likes": 15000, "comments": 2000, "duration": 300, "views_per_hour": 8000}
        ]
    
    def _simulate_google_trends(self) -> List[Dict[str, Any]]:
        """Simulate Google Trends data"""
        return [
            {"keyword": "quantum computing", "search_volume": 50000, "growth_rate": 150, "related_queries": ["quantum AI", "quantum breakthrough"]},
            {"keyword": "sustainable energy", "search_volume": 80000, "growth_rate": 80, "related_queries": ["solar power", "green technology"]},
            {"keyword": "virtual reality", "search_volume": 60000, "growth_rate": 120, "related_queries": ["VR headset", "metaverse"]}
        ]
    
    async def _get_breaking_news_signals(self) -> List[ViralSignal]:
        """Get breaking news signals from base trigger system"""
        # This would integrate with the existing breaking news detection
        return []
    
    def _classify_viral_category(self, content: str) -> ViralCategory:
        """Classify content into viral category"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["breaking", "urgent", "alert"]):
            return ViralCategory.BREAKING_NEWS
        elif any(word in content_lower for word in ["challenge", "viral", "trend"]):
            return ViralCategory.VIRAL_CHALLENGE
        elif any(word in content_lower for word in ["celebrity", "star", "famous"]):
            return ViralCategory.CELEBRITY_EVENT
        elif any(word in content_lower for word in ["tech", "technology", "ai", "innovation"]):
            return ViralCategory.TECH_ANNOUNCEMENT
        elif any(word in content_lower for word in ["meme", "funny", "humor"]):
            return ViralCategory.MEME_TREND
        elif any(word in content_lower for word in ["learn", "education", "tutorial"]):
            return ViralCategory.EDUCATIONAL_VIRAL
        elif any(word in content_lower for word in ["phenomenon", "culture", "society"]):
            return ViralCategory.SOCIAL_PHENOMENON
        else:
            return ViralCategory.TRENDING_TOPIC
    
    def _determine_viral_stage(self, post_data: Dict[str, Any]) -> ViralStage:
        """Determine viral stage from post data"""
        score = post_data.get('score', 0)
        created_utc = post_data.get('created_utc', 0)
        
        # Simple heuristic based on score and age
        hours_old = (datetime.now().timestamp() - created_utc) / 3600
        
        if hours_old < 2 and score > 10000:
            return ViralStage.ACCELERATING
        elif hours_old < 6 and score > 5000:
            return ViralStage.PEAK
        elif hours_old < 24:
            return ViralStage.DECLINING
        else:
            return ViralStage.EXPIRED
    
    def _calculate_reddit_velocity(self, post_data: Dict[str, Any]) -> float:
        """Calculate Reddit post velocity"""
        score = post_data.get('score', 0)
        created_utc = post_data.get('created_utc', 0)
        
        hours_old = max(1, (datetime.now().timestamp() - created_utc) / 3600)
        velocity = score / hours_old / 1000  # Normalize
        
        return min(1.0, velocity)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        import re
        
        # Simple keyword extraction
        words = re.findall(r'\b[A-Za-z]{3,}\b', text.lower())
        
        # Filter common words
        stop_words = {'the', 'and', 'but', 'for', 'are', 'with', 'his', 'her', 'this', 'that', 'you', 'your', 'can', 'how', 'what', 'when', 'why', 'where'}
        keywords = [word for word in words if word not in stop_words]
        
        return keywords[:10]  # Top 10 keywords
    
    def _analyze_sentiment(self, text: str) -> float:
        """Simple sentiment analysis"""
        positive_words = ['good', 'great', 'amazing', 'awesome', 'love', 'best', 'excellent', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disaster', 'fail']
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count + negative_count == 0:
            return 0.0
        
        sentiment = (positive_count - negative_count) / (positive_count + negative_count)
        return round(sentiment, 3)


async def main():
    """Main entry point for enhanced viral opportunity detection"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Viral Opportunity Detection")
    parser.add_argument("--monitor", action="store_true", help="Start continuous monitoring")
    parser.add_argument("--scan", action="store_true", help="Perform single viral scan")
    parser.add_argument("--opportunities", action="store_true", help="Show current opportunities")
    parser.add_argument("--signals", action="store_true", help="Show detected signals")
    parser.add_argument("--duration", type=int, default=300, help="Monitoring duration in seconds")
    
    args = parser.parse_args()
    
    # Initialize viral detection system
    detector = EnhancedViralOpportunityDetection()
    
    if args.scan:
        # Perform single scan
        print("🔍 Performing viral opportunity scan...")
        
        await detector._perform_viral_scan()
        await detector._analyze_viral_signals()
        await detector._generate_viral_opportunities()
        
        print(f"📊 Scan Results:")
        print(f"Signals detected: {len(detector.viral_signals)}")
        print(f"Opportunities generated: {len(detector.viral_opportunities)}")
    
    if args.signals:
        # Show detected signals
        print(f"🔥 Viral Signals ({len(detector.viral_signals)}):")
        
        for signal in sorted(detector.viral_signals.values(), key=lambda x: x.viral_score, reverse=True)[:10]:
            print(f"  {signal.content[:60]}...")
            print(f"    Score: {signal.viral_score:.3f}, Velocity: {signal.velocity:.3f}")
            print(f"    Source: {signal.source}, Stage: {signal.stage.value}")
            print(f"    Reach: {signal.reach_estimate:,}")
    
    if args.opportunities:
        # Show viral opportunities
        print(f"🎯 Viral Opportunities ({len(detector.viral_opportunities)}):")
        
        for opp in sorted(detector.viral_opportunities.values(), key=lambda x: x.overall_viral_score, reverse=True):
            print(f"\n  {opp.content_angle}")
            print(f"    Score: {opp.overall_viral_score:.3f}, Urgency: {opp.urgency_level}/10")
            print(f"    Format: {opp.optimal_content_format}")
            print(f"    Audience: {', '.join(opp.target_audience)}")
            print(f"    Expected ROI: {opp.expected_roi:.1f}x")
            print(f"    Resources: {opp.resource_requirements['estimated_time_hours']}h, ${opp.resource_requirements['estimated_budget']}")
            
            if opp.action_recommendations:
                print(f"    Actions:")
                for rec in opp.action_recommendations[:3]:
                    print(f"      • {rec}")
    
    if args.monitor:
        # Start continuous monitoring
        print(f"🚨 Starting continuous viral monitoring for {args.duration} seconds...")
        
        # Run monitoring for specified duration
        monitoring_task = asyncio.create_task(detector.start_continuous_monitoring())
        
        try:
            await asyncio.sleep(args.duration)
            detector.stop_monitoring()
            await monitoring_task
            
        except KeyboardInterrupt:
            detector.stop_monitoring()
            print("\n⏹️ Monitoring stopped by user")
        
        print(f"\n📈 Monitoring Summary:")
        print(f"Total signals detected: {len(detector.viral_signals)}")
        print(f"Active opportunities: {len(detector.viral_opportunities)}")


if __name__ == "__main__":
    asyncio.run(main())