#!/usr/bin/env python3

"""
Content Lifecycle Manager for TenxsomAI
Automated content repurposing, cross-platform adaptation, and lifecycle optimization
"""

import asyncio
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentStage(Enum):
    """Content lifecycle stages"""
    CREATED = "created"
    PUBLISHED = "published"
    PERFORMING = "performing"
    DECLINING = "declining"
    ARCHIVED = "archived"
    REPURPOSED = "repurposed"


class RepurposeType(Enum):
    """Types of content repurposing"""
    FORMAT_ADAPTATION = "format_adaptation"      # Long-form to short-form
    PLATFORM_OPTIMIZATION = "platform_optimization"  # Platform-specific edits
    CONTENT_SEGMENTATION = "content_segmentation"     # Break into parts
    TREND_REFRESH = "trend_refresh"              # Update with current trends
    AUDIENCE_TARGETING = "audience_targeting"    # Different audience focus
    LANGUAGE_LOCALIZATION = "language_localization"   # Different languages
    SEASONAL_REFRESH = "seasonal_refresh"        # Seasonal relevance


@dataclass
class ContentAsset:
    """Individual content asset in the lifecycle"""
    asset_id: str
    title: str
    description: str
    content_type: str  # video, image, audio, text
    platform: str
    duration: Optional[int]
    file_path: Optional[str]
    created_at: datetime
    published_at: Optional[datetime]
    stage: ContentStage
    performance_metrics: Dict[str, Any]
    repurpose_history: List[str]
    tags: List[str]
    category: str


@dataclass
class RepurposeOpportunity:
    """Identified repurposing opportunity"""
    source_asset_id: str
    target_platforms: List[str]
    repurpose_type: RepurposeType
    adaptation_requirements: Dict[str, Any]
    estimated_performance: Dict[str, float]
    priority_score: float
    automation_feasibility: float
    resource_requirements: Dict[str, Any]
    expected_roi: float


@dataclass
class LifecycleAnalytics:
    """Content lifecycle analytics"""
    total_assets: int
    assets_by_stage: Dict[str, int]
    repurpose_success_rate: float
    avg_asset_lifespan_days: float
    top_performing_categories: List[str]
    optimization_opportunities: List[str]
    cross_platform_performance: Dict[str, Dict[str, float]]


class ContentLifecycleManager:
    """
    Comprehensive content lifecycle management system
    
    Features:
    - Automated content tracking across all platforms
    - Performance-based lifecycle stage management
    - Intelligent repurposing opportunity identification
    - Cross-platform content adaptation
    - Automated content archival and retrieval
    - Performance-driven content refresh
    - Multi-format content generation
    """
    
    def __init__(self, config_manager=None):
        """Initialize content lifecycle manager"""
        self.config = config_manager
        
        # Content storage
        self.content_database = {}
        self.repurpose_opportunities = []
        self.lifecycle_analytics = LifecycleAnalytics(
            total_assets=0, assets_by_stage={}, repurpose_success_rate=0.0,
            avg_asset_lifespan_days=0.0, top_performing_categories=[],
            optimization_opportunities=[], cross_platform_performance={}
        )
        
        # Lifecycle configuration
        self.lifecycle_config = {
            "performance_thresholds": {
                "high_performance": 0.15,     # Top 15% engagement
                "low_performance": 0.05,      # Bottom 5% engagement
                "declining_threshold": 0.3,   # 30% drop from peak
                "archive_threshold": 90       # Days without engagement
            },
            "repurpose_scoring": {
                "performance_weight": 0.4,
                "trend_alignment_weight": 0.3,
                "platform_fit_weight": 0.2,
                "resource_efficiency_weight": 0.1
            },
            "automation_thresholds": {
                "high_automation": 0.8,      # Fully automated
                "medium_automation": 0.6,    # Semi-automated
                "manual_required": 0.4       # Manual intervention needed
            },
            "cross_platform_mappings": {
                "youtube": {"tiktok": 0.7, "instagram": 0.8, "x": 0.6},
                "tiktok": {"youtube": 0.5, "instagram": 0.9, "x": 0.7},
                "instagram": {"youtube": 0.6, "tiktok": 0.8, "x": 0.7},
                "x": {"youtube": 0.4, "tiktok": 0.6, "instagram": 0.5}
            }
        }
        
        # Platform-specific adaptation rules
        self.platform_adaptations = {
            "youtube": {
                "optimal_duration": (180, 600),    # 3-10 minutes
                "aspect_ratio": "16:9",
                "title_length": (30, 60),
                "description_length": (100, 500),
                "call_to_action": "Subscribe and hit the bell!"
            },
            "tiktok": {
                "optimal_duration": (15, 60),      # 15-60 seconds
                "aspect_ratio": "9:16",
                "title_length": (10, 30),
                "description_length": (20, 100),
                "call_to_action": "Follow for more!"
            },
            "instagram": {
                "optimal_duration": (15, 90),      # 15-90 seconds
                "aspect_ratio": "1:1",
                "title_length": (10, 40),
                "description_length": (50, 200),
                "call_to_action": "Follow and share!"
            },
            "x": {
                "optimal_duration": (10, 30),      # 10-30 seconds
                "aspect_ratio": "16:9",
                "title_length": (10, 30),
                "description_length": (20, 80),
                "call_to_action": "Retweet if you agree!"
            }
        }
        
        # Load existing content database
        self._load_content_database()
        
    def _load_content_database(self):
        """Load existing content database from storage"""
        
        db_file = Path("content_lifecycle_database.json")
        if db_file.exists():
            try:
                with open(db_file, 'r') as f:
                    data = json.load(f)
                
                # Convert back to ContentAsset objects
                for asset_id, asset_data in data.get("assets", {}).items():
                    asset_data["created_at"] = datetime.fromisoformat(asset_data["created_at"])
                    if asset_data["published_at"]:
                        asset_data["published_at"] = datetime.fromisoformat(asset_data["published_at"])
                    asset_data["stage"] = ContentStage(asset_data["stage"])
                    
                    self.content_database[asset_id] = ContentAsset(**asset_data)
                
                logger.info(f"📚 Loaded {len(self.content_database)} assets from content database")
                
            except Exception as e:
                logger.error(f"Failed to load content database: {e}")
                
    def _save_content_database(self):
        """Save content database to storage"""
        
        db_file = Path("content_lifecycle_database.json")
        
        try:
            # Convert ContentAsset objects to serializable format
            serializable_data = {}
            for asset_id, asset in self.content_database.items():
                asset_dict = asdict(asset)
                asset_dict["created_at"] = asset.created_at.isoformat()
                asset_dict["published_at"] = asset.published_at.isoformat() if asset.published_at else None
                asset_dict["stage"] = asset.stage.value
                serializable_data[asset_id] = asset_dict
            
            data = {
                "assets": serializable_data,
                "last_updated": datetime.now().isoformat(),
                "total_assets": len(self.content_database)
            }
            
            with open(db_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save content database: {e}")
    
    async def track_content_asset(self, 
                                content_metadata: Dict[str, Any],
                                performance_data: Dict[str, Any] = None) -> str:
        """
        Track a new content asset in the lifecycle system
        
        Args:
            content_metadata: Content metadata (title, description, platform, etc.)
            performance_data: Initial performance data
            
        Returns:
            Asset ID for tracking
        """
        
        # Generate unique asset ID
        content_hash = hashlib.md5(
            f"{content_metadata.get('title', '')}{content_metadata.get('platform', '')}{datetime.now()}".encode()
        ).hexdigest()[:12]
        asset_id = f"asset_{content_hash}"
        
        # Create content asset
        asset = ContentAsset(
            asset_id=asset_id,
            title=content_metadata.get("title", ""),
            description=content_metadata.get("description", ""),
            content_type=content_metadata.get("content_type", "video"),
            platform=content_metadata.get("platform", "youtube"),
            duration=content_metadata.get("duration"),
            file_path=content_metadata.get("file_path"),
            created_at=datetime.now(),
            published_at=content_metadata.get("published_at"),
            stage=ContentStage.CREATED,
            performance_metrics=performance_data or {},
            repurpose_history=[],
            tags=content_metadata.get("tags", []),
            category=content_metadata.get("category", "general")
        )
        
        # Add to database
        self.content_database[asset_id] = asset
        
        # Update stage if already published
        if asset.published_at:
            asset.stage = ContentStage.PUBLISHED
        
        # Save database
        self._save_content_database()
        
        logger.info(f"📝 Tracked new content asset: {asset_id} ({asset.title[:50]}...)")
        
        return asset_id
    
    async def update_performance_metrics(self, 
                                       asset_id: str,
                                       performance_data: Dict[str, Any]):
        """Update performance metrics for a content asset"""
        
        if asset_id not in self.content_database:
            logger.warning(f"Asset {asset_id} not found in database")
            return
        
        asset = self.content_database[asset_id]
        
        # Update metrics
        asset.performance_metrics.update(performance_data)
        
        # Update lifecycle stage based on performance
        await self._update_lifecycle_stage(asset)
        
        # Save changes
        self._save_content_database()
        
        logger.info(f"📊 Updated performance metrics for {asset_id}")
    
    async def _update_lifecycle_stage(self, asset: ContentAsset):
        """Update content lifecycle stage based on performance"""
        
        current_stage = asset.stage
        performance = asset.performance_metrics
        
        views = performance.get("views", 0)
        engagement_rate = performance.get("engagement_rate", 0.0)
        days_since_published = (datetime.now() - (asset.published_at or asset.created_at)).days
        
        # Stage transition logic
        if current_stage == ContentStage.CREATED and asset.published_at:
            asset.stage = ContentStage.PUBLISHED
            
        elif current_stage == ContentStage.PUBLISHED:
            if engagement_rate >= self.lifecycle_config["performance_thresholds"]["high_performance"]:
                asset.stage = ContentStage.PERFORMING
            elif days_since_published >= 7:  # Give it a week
                asset.stage = ContentStage.DECLINING
                
        elif current_stage == ContentStage.PERFORMING:
            # Check for declining performance
            recent_engagement = performance.get("recent_engagement_rate", engagement_rate)
            if recent_engagement < engagement_rate * (1 - self.lifecycle_config["performance_thresholds"]["declining_threshold"]):
                asset.stage = ContentStage.DECLINING
                
        elif current_stage == ContentStage.DECLINING:
            if days_since_published >= self.lifecycle_config["performance_thresholds"]["archive_threshold"]:
                asset.stage = ContentStage.ARCHIVED
        
        if asset.stage != current_stage:
            logger.info(f"🔄 Asset {asset.asset_id} stage changed: {current_stage.value} → {asset.stage.value}")
    
    async def identify_repurpose_opportunities(self, 
                                             min_priority_score: float = 0.6) -> List[RepurposeOpportunity]:
        """
        Identify content repurposing opportunities
        
        Args:
            min_priority_score: Minimum priority score for opportunities
            
        Returns:
            List of repurposing opportunities
        """
        
        opportunities = []
        
        # Analyze each asset for repurposing potential
        for asset_id, asset in self.content_database.items():
            
            # Skip recently repurposed content
            if asset.stage == ContentStage.REPURPOSED:
                continue
            
            # Focus on performing or declining content
            if asset.stage in [ContentStage.PERFORMING, ContentStage.DECLINING]:
                
                # Identify repurposing opportunities
                asset_opportunities = await self._analyze_asset_repurpose_potential(asset)
                opportunities.extend(asset_opportunities)
        
        # Filter by priority score
        high_priority_opportunities = [
            opp for opp in opportunities 
            if opp.priority_score >= min_priority_score
        ]
        
        # Sort by priority score
        high_priority_opportunities.sort(key=lambda x: x.priority_score, reverse=True)
        
        # Update internal list
        self.repurpose_opportunities = high_priority_opportunities
        
        logger.info(f"🔍 Identified {len(high_priority_opportunities)} high-priority repurpose opportunities")
        
        return high_priority_opportunities
    
    async def _analyze_asset_repurpose_potential(self, asset: ContentAsset) -> List[RepurposeOpportunity]:
        """Analyze repurposing potential for a single asset"""
        
        opportunities = []
        
        # Current platform performance
        current_performance = asset.performance_metrics.get("engagement_rate", 0.05)
        
        # Analyze each target platform
        for target_platform in ["youtube", "tiktok", "instagram", "x"]:
            
            if target_platform == asset.platform:
                continue  # Skip same platform
            
            # Calculate cross-platform compatibility
            compatibility = self.lifecycle_config["cross_platform_mappings"].get(
                asset.platform, {}
            ).get(target_platform, 0.5)
            
            # Different repurpose types
            repurpose_types = [
                RepurposeType.FORMAT_ADAPTATION,
                RepurposeType.PLATFORM_OPTIMIZATION,
                RepurposeType.TREND_REFRESH
            ]
            
            for repurpose_type in repurpose_types:
                
                # Calculate opportunity metrics
                priority_score = await self._calculate_repurpose_priority(
                    asset, target_platform, repurpose_type, compatibility, current_performance
                )
                
                if priority_score >= 0.4:  # Minimum threshold
                    
                    # Generate opportunity
                    opportunity = RepurposeOpportunity(
                        source_asset_id=asset.asset_id,
                        target_platforms=[target_platform],
                        repurpose_type=repurpose_type,
                        adaptation_requirements=self._get_adaptation_requirements(
                            asset, target_platform, repurpose_type
                        ),
                        estimated_performance=self._estimate_repurpose_performance(
                            asset, target_platform, compatibility
                        ),
                        priority_score=priority_score,
                        automation_feasibility=self._calculate_automation_feasibility(repurpose_type),
                        resource_requirements=self._calculate_resource_requirements(
                            asset, target_platform, repurpose_type
                        ),
                        expected_roi=self._calculate_expected_roi(
                            asset, target_platform, priority_score
                        )
                    )
                    
                    opportunities.append(opportunity)
        
        return opportunities
    
    async def _calculate_repurpose_priority(self, 
                                          asset: ContentAsset,
                                          target_platform: str,
                                          repurpose_type: RepurposeType,
                                          compatibility: float,
                                          current_performance: float) -> float:
        """Calculate priority score for repurposing opportunity"""
        
        scoring = self.lifecycle_config["repurpose_scoring"]
        
        # Performance factor (better performing content = higher priority)
        performance_factor = min(current_performance / 0.10, 1.0)  # Normalize to 10% engagement
        
        # Trend alignment factor (simulated - would integrate with trend analysis)
        trend_factor = 0.7  # Default trend alignment
        
        # Platform fit factor
        platform_adaptations = self.platform_adaptations.get(target_platform, {})
        duration_fit = 1.0
        if asset.duration:
            optimal_range = platform_adaptations.get("optimal_duration", (30, 300))
            if optimal_range[0] <= asset.duration <= optimal_range[1]:
                duration_fit = 1.0
            else:
                duration_fit = 0.6
        
        platform_fit = compatibility * duration_fit
        
        # Resource efficiency factor
        efficiency_map = {
            RepurposeType.FORMAT_ADAPTATION: 0.7,
            RepurposeType.PLATFORM_OPTIMIZATION: 0.8,
            RepurposeType.CONTENT_SEGMENTATION: 0.6,
            RepurposeType.TREND_REFRESH: 0.5,
            RepurposeType.AUDIENCE_TARGETING: 0.7,
            RepurposeType.LANGUAGE_LOCALIZATION: 0.4,
            RepurposeType.SEASONAL_REFRESH: 0.6
        }
        resource_efficiency = efficiency_map.get(repurpose_type, 0.6)
        
        # Calculate weighted score
        priority_score = (
            performance_factor * scoring["performance_weight"] +
            trend_factor * scoring["trend_alignment_weight"] +
            platform_fit * scoring["platform_fit_weight"] +
            resource_efficiency * scoring["resource_efficiency_weight"]
        )
        
        return round(priority_score, 3)
    
    def _get_adaptation_requirements(self, 
                                   asset: ContentAsset,
                                   target_platform: str,
                                   repurpose_type: RepurposeType) -> Dict[str, Any]:
        """Get adaptation requirements for repurposing"""
        
        target_specs = self.platform_adaptations.get(target_platform, {})
        
        requirements = {
            "duration_adjustment": None,
            "aspect_ratio_change": target_specs.get("aspect_ratio"),
            "title_adaptation": True,
            "description_adaptation": True,
            "content_editing": False,
            "thumbnail_creation": True
        }
        
        # Duration adjustment
        if asset.duration:
            optimal_duration = target_specs.get("optimal_duration", (30, 300))
            if asset.duration > optimal_duration[1]:
                requirements["duration_adjustment"] = "shorten"
                requirements["content_editing"] = True
            elif asset.duration < optimal_duration[0]:
                requirements["duration_adjustment"] = "extend"
        
        # Repurpose type specific requirements
        if repurpose_type == RepurposeType.FORMAT_ADAPTATION:
            requirements["content_editing"] = True
            requirements["format_conversion"] = True
        elif repurpose_type == RepurposeType.TREND_REFRESH:
            requirements["trend_integration"] = True
            requirements["metadata_refresh"] = True
        elif repurpose_type == RepurposeType.CONTENT_SEGMENTATION:
            requirements["content_segmentation"] = True
            requirements["multiple_outputs"] = True
        
        return requirements
    
    def _estimate_repurpose_performance(self, 
                                      asset: ContentAsset,
                                      target_platform: str,
                                      compatibility: float) -> Dict[str, float]:
        """Estimate performance for repurposed content"""
        
        current_performance = asset.performance_metrics
        current_views = current_performance.get("views", 1000)
        current_engagement = current_performance.get("engagement_rate", 0.05)
        
        # Platform performance multipliers (based on typical cross-platform performance)
        platform_multipliers = {
            "youtube": {"views": 0.8, "engagement": 0.9},
            "tiktok": {"views": 1.5, "engagement": 1.2},
            "instagram": {"views": 1.0, "engagement": 1.1},
            "x": {"views": 0.6, "engagement": 0.8}
        }
        
        multiplier = platform_multipliers.get(target_platform, {"views": 0.8, "engagement": 0.9})
        
        # Apply compatibility and platform factors
        estimated_views = int(current_views * multiplier["views"] * compatibility)
        estimated_engagement = current_engagement * multiplier["engagement"] * compatibility
        
        return {
            "estimated_views": estimated_views,
            "estimated_engagement_rate": round(estimated_engagement, 4),
            "confidence": round(compatibility, 3)
        }
    
    def _calculate_automation_feasibility(self, repurpose_type: RepurposeType) -> float:
        """Calculate how easily this repurposing can be automated"""
        
        automation_scores = {
            RepurposeType.FORMAT_ADAPTATION: 0.8,      # High automation
            RepurposeType.PLATFORM_OPTIMIZATION: 0.9,  # Very high automation
            RepurposeType.CONTENT_SEGMENTATION: 0.6,   # Medium automation
            RepurposeType.TREND_REFRESH: 0.4,          # Low automation (needs trend research)
            RepurposeType.AUDIENCE_TARGETING: 0.7,     # Medium-high automation
            RepurposeType.LANGUAGE_LOCALIZATION: 0.3,  # Low automation (translation needed)
            RepurposeType.SEASONAL_REFRESH: 0.5        # Medium automation
        }
        
        return automation_scores.get(repurpose_type, 0.6)
    
    def _calculate_resource_requirements(self, 
                                       asset: ContentAsset,
                                       target_platform: str,
                                       repurpose_type: RepurposeType) -> Dict[str, Any]:
        """Calculate resource requirements for repurposing"""
        
        base_time_minutes = 15  # Base processing time
        
        # Time multipliers by repurpose type
        time_multipliers = {
            RepurposeType.FORMAT_ADAPTATION: 2.0,
            RepurposeType.PLATFORM_OPTIMIZATION: 1.2,
            RepurposeType.CONTENT_SEGMENTATION: 2.5,
            RepurposeType.TREND_REFRESH: 1.8,
            RepurposeType.AUDIENCE_TARGETING: 1.5,
            RepurposeType.LANGUAGE_LOCALIZATION: 3.0,
            RepurposeType.SEASONAL_REFRESH: 1.6
        }
        
        estimated_time = base_time_minutes * time_multipliers.get(repurpose_type, 1.5)
        
        return {
            "estimated_time_minutes": int(estimated_time),
            "human_review_required": repurpose_type in [
                RepurposeType.TREND_REFRESH, 
                RepurposeType.LANGUAGE_LOCALIZATION
            ],
            "technical_complexity": "medium" if estimated_time > 30 else "low",
            "automation_level": self._calculate_automation_feasibility(repurpose_type)
        }
    
    def _calculate_expected_roi(self, 
                              asset: ContentAsset,
                              target_platform: str,
                              priority_score: float) -> float:
        """Calculate expected ROI for repurposing"""
        
        # Base ROI calculation
        current_revenue = asset.performance_metrics.get("revenue", 2.50)  # Default $2.50
        
        # Platform revenue multipliers
        revenue_multipliers = {
            "youtube": 1.0,
            "tiktok": 0.6,     # Lower monetization
            "instagram": 0.8,
            "x": 0.4          # Lowest monetization
        }
        
        # Expected revenue from repurposed content
        expected_revenue = current_revenue * revenue_multipliers.get(target_platform, 0.7) * priority_score
        
        # Estimated cost (time * hourly rate)
        estimated_cost = 0.5  # $0.50 base automation cost
        
        # ROI calculation
        roi = (expected_revenue - estimated_cost) / estimated_cost if estimated_cost > 0 else 0
        
        return round(roi, 2)
    
    async def execute_repurpose_opportunity(self, opportunity: RepurposeOpportunity) -> Dict[str, Any]:
        """
        Execute a repurposing opportunity
        
        Args:
            opportunity: Repurposing opportunity to execute
            
        Returns:
            Execution results
        """
        
        source_asset = self.content_database.get(opportunity.source_asset_id)
        if not source_asset:
            return {"status": "error", "message": "Source asset not found"}
        
        logger.info(f"🔄 Executing repurpose opportunity: {source_asset.title} → {opportunity.target_platforms}")
        
        execution_results = {
            "status": "success",
            "source_asset_id": opportunity.source_asset_id,
            "repurpose_type": opportunity.repurpose_type.value,
            "target_platforms": opportunity.target_platforms,
            "new_assets": [],
            "execution_time_minutes": 0,
            "automation_level": opportunity.automation_feasibility
        }
        
        start_time = datetime.now()
        
        # Execute repurposing for each target platform
        for target_platform in opportunity.target_platforms:
            
            try:
                # Generate adapted content
                adapted_content = await self._adapt_content_for_platform(
                    source_asset, target_platform, opportunity
                )
                
                # Create new asset
                new_asset_id = await self.track_content_asset(adapted_content)
                execution_results["new_assets"].append(new_asset_id)
                
                # Mark source asset as repurposed
                if source_asset.stage != ContentStage.REPURPOSED:
                    source_asset.stage = ContentStage.REPURPOSED
                    source_asset.repurpose_history.append(new_asset_id)
                
                logger.info(f"✅ Created repurposed asset: {new_asset_id} for {target_platform}")
                
            except Exception as e:
                logger.error(f"❌ Failed to repurpose for {target_platform}: {e}")
                execution_results["status"] = "partial_success"
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds() / 60
        execution_results["execution_time_minutes"] = round(execution_time, 1)
        
        # Save changes
        self._save_content_database()
        
        return execution_results
    
    async def _adapt_content_for_platform(self, 
                                         source_asset: ContentAsset,
                                         target_platform: str,
                                         opportunity: RepurposeOpportunity) -> Dict[str, Any]:
        """Adapt content for target platform"""
        
        target_specs = self.platform_adaptations.get(target_platform, {})
        adaptations = opportunity.adaptation_requirements
        
        # Adapt title
        adapted_title = self._adapt_title(source_asset.title, target_specs)
        
        # Adapt description
        adapted_description = self._adapt_description(source_asset.description, target_specs)
        
        # Calculate adapted duration
        adapted_duration = self._adapt_duration(source_asset.duration, target_specs, adaptations)
        
        # Generate new metadata
        adapted_content = {
            "title": adapted_title,
            "description": adapted_description,
            "content_type": source_asset.content_type,
            "platform": target_platform,
            "duration": adapted_duration,
            "category": source_asset.category,
            "tags": self._adapt_tags(source_asset.tags, target_platform),
            "source_asset_id": source_asset.asset_id,
            "repurpose_type": opportunity.repurpose_type.value,
            "adaptation_metadata": {
                "aspect_ratio": target_specs.get("aspect_ratio"),
                "call_to_action": target_specs.get("call_to_action"),
                "platform_optimization": True
            }
        }
        
        return adapted_content
    
    def _adapt_title(self, original_title: str, target_specs: Dict[str, Any]) -> str:
        """Adapt title for target platform"""
        
        title_range = target_specs.get("title_length", (10, 60))
        max_length = title_range[1]
        
        # Truncate if too long
        if len(original_title) > max_length:
            # Try to truncate at word boundary
            words = original_title.split()
            adapted_title = ""
            
            for word in words:
                if len(adapted_title + " " + word) <= max_length - 3:
                    adapted_title += (" " if adapted_title else "") + word
                else:
                    break
            
            adapted_title += "..."
        else:
            adapted_title = original_title
        
        return adapted_title
    
    def _adapt_description(self, original_description: str, target_specs: Dict[str, Any]) -> str:
        """Adapt description for target platform"""
        
        desc_range = target_specs.get("description_length", (50, 500))
        max_length = desc_range[1]
        
        # Add platform-specific call-to-action
        cta = target_specs.get("call_to_action", "")
        
        # Truncate description if needed
        available_length = max_length - len(cta) - 10  # Buffer for formatting
        
        if len(original_description) > available_length:
            adapted_description = original_description[:available_length-3] + "..."
        else:
            adapted_description = original_description
        
        # Add call-to-action
        if cta:
            adapted_description += f"\n\n{cta}"
        
        return adapted_description
    
    def _adapt_duration(self, 
                       original_duration: Optional[int],
                       target_specs: Dict[str, Any],
                       adaptations: Dict[str, Any]) -> Optional[int]:
        """Adapt duration for target platform"""
        
        if not original_duration:
            return None
        
        optimal_range = target_specs.get("optimal_duration", (30, 300))
        
        # Check if adaptation is needed
        duration_adjustment = adaptations.get("duration_adjustment")
        
        if duration_adjustment == "shorten":
            # Shorten to fit platform
            return min(original_duration, optimal_range[1])
        elif duration_adjustment == "extend":
            # Extend to minimum (would need content extension)
            return optimal_range[0]
        else:
            # No adjustment needed
            return original_duration
    
    def _adapt_tags(self, original_tags: List[str], target_platform: str) -> List[str]:
        """Adapt tags for target platform"""
        
        # Platform-specific tag adaptations
        platform_tag_styles = {
            "youtube": lambda tags: tags,  # Keep original
            "tiktok": lambda tags: [f"#{tag.lower().replace(' ', '')}" for tag in tags],
            "instagram": lambda tags: [f"#{tag.lower().replace(' ', '')}" for tag in tags[:10]],
            "x": lambda tags: [f"#{tag.lower().replace(' ', '')}" for tag in tags[:5]]
        }
        
        adapter = platform_tag_styles.get(target_platform, lambda tags: tags)
        return adapter(original_tags)
    
    async def generate_lifecycle_analytics(self) -> LifecycleAnalytics:
        """Generate comprehensive lifecycle analytics"""
        
        total_assets = len(self.content_database)
        
        # Assets by stage
        assets_by_stage = {}
        for stage in ContentStage:
            count = len([a for a in self.content_database.values() if a.stage == stage])
            assets_by_stage[stage.value] = count
        
        # Calculate repurpose success rate
        repurposed_assets = [a for a in self.content_database.values() if a.repurpose_history]
        repurpose_success_rate = len(repurposed_assets) / max(total_assets, 1)
        
        # Average asset lifespan
        published_assets = [a for a in self.content_database.values() if a.published_at]
        if published_assets:
            lifespans = [
                (datetime.now() - a.published_at).days 
                for a in published_assets
            ]
            avg_lifespan = sum(lifespans) / len(lifespans)
        else:
            avg_lifespan = 0.0
        
        # Top performing categories
        category_performance = {}
        for asset in self.content_database.values():
            if asset.category not in category_performance:
                category_performance[asset.category] = []
            
            engagement = asset.performance_metrics.get("engagement_rate", 0.0)
            category_performance[asset.category].append(engagement)
        
        # Calculate average performance by category
        category_averages = {
            cat: sum(performances) / len(performances)
            for cat, performances in category_performance.items()
            if performances
        }
        
        top_categories = sorted(
            category_averages.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Cross-platform performance analysis
        cross_platform_performance = {}
        for platform in ["youtube", "tiktok", "instagram", "x"]:
            platform_assets = [a for a in self.content_database.values() if a.platform == platform]
            
            if platform_assets:
                avg_views = sum(a.performance_metrics.get("views", 0) for a in platform_assets) / len(platform_assets)
                avg_engagement = sum(a.performance_metrics.get("engagement_rate", 0) for a in platform_assets) / len(platform_assets)
                
                cross_platform_performance[platform] = {
                    "avg_views": int(avg_views),
                    "avg_engagement_rate": round(avg_engagement, 4),
                    "total_assets": len(platform_assets)
                }
        
        # Optimization opportunities
        optimization_opportunities = self._identify_optimization_opportunities()
        
        # Update analytics
        self.lifecycle_analytics = LifecycleAnalytics(
            total_assets=total_assets,
            assets_by_stage=assets_by_stage,
            repurpose_success_rate=round(repurpose_success_rate, 3),
            avg_asset_lifespan_days=round(avg_lifespan, 1),
            top_performing_categories=[cat for cat, _ in top_categories],
            optimization_opportunities=optimization_opportunities,
            cross_platform_performance=cross_platform_performance
        )
        
        logger.info(f"📈 Generated lifecycle analytics: {total_assets} assets, {repurpose_success_rate:.1%} repurpose rate")
        
        return self.lifecycle_analytics
    
    def _identify_optimization_opportunities(self) -> List[str]:
        """Identify content lifecycle optimization opportunities"""
        
        opportunities = []
        
        # Analyze assets by stage
        stage_counts = {}
        for asset in self.content_database.values():
            stage_counts[asset.stage] = stage_counts.get(asset.stage, 0) + 1
        
        total_assets = len(self.content_database)
        
        # High archive rate
        archived_count = stage_counts.get(ContentStage.ARCHIVED, 0)
        if archived_count / max(total_assets, 1) > 0.3:
            opportunities.append("High archive rate - consider more aggressive repurposing")
        
        # Low repurpose rate
        repurposed_count = len([a for a in self.content_database.values() if a.repurpose_history])
        if repurposed_count / max(total_assets, 1) < 0.2:
            opportunities.append("Low repurpose rate - automate content adaptation")
        
        # Platform imbalance
        platform_counts = {}
        for asset in self.content_database.values():
            platform_counts[asset.platform] = platform_counts.get(asset.platform, 0) + 1
        
        if platform_counts:
            max_platform_count = max(platform_counts.values())
            min_platform_count = min(platform_counts.values())
            
            if max_platform_count / max(min_platform_count, 1) > 3:
                opportunities.append("Platform imbalance - increase cross-platform distribution")
        
        # Low performing content
        low_performing = [
            a for a in self.content_database.values()
            if a.performance_metrics.get("engagement_rate", 0) < 0.02
        ]
        
        if len(low_performing) / max(total_assets, 1) > 0.4:
            opportunities.append("High low-performing content rate - improve content strategy")
        
        # Add default opportunities if none found
        if not opportunities:
            opportunities = [
                "Implement automated content refresh cycles",
                "Expand cross-platform content distribution",
                "Develop trend-based content optimization"
            ]
        
        return opportunities
    
    async def batch_repurpose_execution(self, 
                                      max_opportunities: int = 10,
                                      min_priority: float = 0.7) -> Dict[str, Any]:
        """
        Execute multiple repurposing opportunities in batch
        
        Args:
            max_opportunities: Maximum opportunities to execute
            min_priority: Minimum priority score for execution
            
        Returns:
            Batch execution results
        """
        
        # Get high-priority opportunities
        opportunities = await self.identify_repurpose_opportunities(min_priority)
        
        # Limit to max opportunities
        opportunities_to_execute = opportunities[:max_opportunities]
        
        logger.info(f"🚀 Executing batch repurpose: {len(opportunities_to_execute)} opportunities")
        
        batch_results = {
            "total_opportunities": len(opportunities_to_execute),
            "successful_executions": 0,
            "failed_executions": 0,
            "new_assets_created": 0,
            "total_execution_time": 0.0,
            "execution_details": []
        }
        
        start_time = datetime.now()
        
        # Execute each opportunity
        for i, opportunity in enumerate(opportunities_to_execute):
            logger.info(f"📝 Executing opportunity {i+1}/{len(opportunities_to_execute)}")
            
            try:
                result = await self.execute_repurpose_opportunity(opportunity)
                
                if result["status"] in ["success", "partial_success"]:
                    batch_results["successful_executions"] += 1
                    batch_results["new_assets_created"] += len(result["new_assets"])
                else:
                    batch_results["failed_executions"] += 1
                
                batch_results["execution_details"].append(result)
                
            except Exception as e:
                logger.error(f"❌ Batch execution failed for opportunity {i+1}: {e}")
                batch_results["failed_executions"] += 1
        
        # Calculate total time
        total_time = (datetime.now() - start_time).total_seconds() / 60
        batch_results["total_execution_time"] = round(total_time, 1)
        
        # Calculate success rate
        batch_results["success_rate"] = (
            batch_results["successful_executions"] / 
            max(len(opportunities_to_execute), 1)
        )
        
        logger.info(f"✅ Batch repurpose completed: {batch_results['successful_executions']}/{len(opportunities_to_execute)} successful")
        
        return batch_results


async def main():
    """Main entry point for content lifecycle management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="TenxsomAI Content Lifecycle Manager")
    parser.add_argument("--analyze", action="store_true", help="Analyze lifecycle metrics")
    parser.add_argument("--opportunities", action="store_true", help="Identify repurpose opportunities")
    parser.add_argument("--execute", type=int, default=0, help="Execute N repurpose opportunities")
    parser.add_argument("--track", type=str, help="Track new content asset (JSON file)")
    parser.add_argument("--batch", action="store_true", help="Execute batch repurposing")
    
    args = parser.parse_args()
    
    # Initialize lifecycle manager
    lifecycle_manager = ContentLifecycleManager()
    
    if args.analyze:
        # Generate analytics
        analytics = await lifecycle_manager.generate_lifecycle_analytics()
        
        print(f"📊 Content Lifecycle Analytics:")
        print(f"Total Assets: {analytics.total_assets}")
        print(f"Repurpose Success Rate: {analytics.repurpose_success_rate:.1%}")
        print(f"Average Lifespan: {analytics.avg_asset_lifespan_days:.1f} days")
        
        print(f"\n📈 Assets by Stage:")
        for stage, count in analytics.assets_by_stage.items():
            print(f"  {stage}: {count}")
        
        print(f"\n🏆 Top Categories:")
        for category in analytics.top_performing_categories[:3]:
            print(f"  • {category}")
        
        if analytics.optimization_opportunities:
            print(f"\n💡 Optimization Opportunities:")
            for opp in analytics.optimization_opportunities:
                print(f"  • {opp}")
    
    if args.opportunities:
        # Identify opportunities
        opportunities = await lifecycle_manager.identify_repurpose_opportunities()
        
        print(f"🔍 Repurpose Opportunities ({len(opportunities)}):")
        for i, opp in enumerate(opportunities[:10], 1):
            source_asset = lifecycle_manager.content_database.get(opp.source_asset_id)
            source_title = source_asset.title[:40] + "..." if source_asset else "Unknown"
            
            print(f"  {i}. {source_title}")
            print(f"     → {', '.join(opp.target_platforms)} ({opp.repurpose_type.value})")
            print(f"     Priority: {opp.priority_score:.3f}, ROI: {opp.expected_roi:.1f}x")
    
    if args.execute > 0:
        # Execute specific number of opportunities
        opportunities = await lifecycle_manager.identify_repurpose_opportunities()
        
        if opportunities:
            print(f"🚀 Executing top {args.execute} repurpose opportunities...")
            
            for i in range(min(args.execute, len(opportunities))):
                opportunity = opportunities[i]
                result = await lifecycle_manager.execute_repurpose_opportunity(opportunity)
                
                print(f"  {i+1}. {result['status']}: {len(result.get('new_assets', []))} new assets")
        else:
            print("No repurpose opportunities found")
    
    if args.batch:
        # Execute batch repurposing
        print("🚀 Executing batch repurposing...")
        
        batch_result = await lifecycle_manager.batch_repurpose_execution()
        
        print(f"✅ Batch Results:")
        print(f"Successful: {batch_result['successful_executions']}")
        print(f"Failed: {batch_result['failed_executions']}")
        print(f"New Assets: {batch_result['new_assets_created']}")
        print(f"Success Rate: {batch_result['success_rate']:.1%}")
        print(f"Execution Time: {batch_result['total_execution_time']:.1f} minutes")
    
    if args.track:
        # Track new content
        with open(args.track, 'r') as f:
            content_data = json.load(f)
        
        asset_id = await lifecycle_manager.track_content_asset(content_data)
        print(f"📝 Tracked new asset: {asset_id}")


if __name__ == "__main__":
    asyncio.run(main())