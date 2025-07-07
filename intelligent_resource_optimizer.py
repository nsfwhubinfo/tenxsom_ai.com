#!/usr/bin/env python3

"""
Intelligent Resource Optimizer
Replaces static quota configurations with AI-powered resource optimization
Uses performance data and trend analysis for dynamic resource allocation
"""

import sys
import logging
import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# Add paths for imports
sys.path.append(str(Path(__file__).parent))

from agents.youtube_expert.main import YouTubePlatformExpert, ContentCategory
from production_config_manager import ProductionConfigManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ResourceMetrics:
    """Resource usage and performance metrics"""
    platform: str
    current_usage: int
    daily_limit: int
    hourly_usage: int
    hourly_limit: int
    success_rate: float
    avg_performance_score: float
    cost_per_success: float
    roi_factor: float
    trend_momentum: float


@dataclass
class OptimizationRecommendation:
    """AI-powered optimization recommendation"""
    platform: str
    action: str  # increase, decrease, maintain, redistribute
    current_allocation: int
    recommended_allocation: int
    confidence_score: float
    reasoning: str
    expected_improvement: float
    risk_assessment: str


class IntelligentResourceOptimizer:
    """
    AI-powered resource optimization system
    
    Features:
    - Dynamic quota allocation based on performance
    - Real-time resource redistribution
    - Performance-based priority adjustment
    - Cost optimization with ROI analysis
    - Predictive resource planning
    - Multi-platform load balancing
    """
    
    def __init__(self, config_manager: ProductionConfigManager = None):
        """Initialize intelligent resource optimizer"""
        self.config = config_manager or ProductionConfigManager()
        self.youtube_expert = YouTubePlatformExpert()
        
        # AI optimization parameters
        self.optimization_config = {
            "learning_rate": 0.1,
            "performance_weight": 0.4,
            "cost_weight": 0.3,
            "trend_weight": 0.2,
            "risk_tolerance": 0.7,
            "min_allocation_threshold": 0.1,
            "max_allocation_threshold": 0.8,
            "rebalance_frequency": 3600,  # 1 hour
            "performance_history_days": 7
        }
        
        # Base platform configurations (starting points for optimization)
        self.base_platform_configs = {
            "youtube": {
                "base_quota": 10000,
                "base_upload_cost": 1600,
                "base_daily_uploads": 100,
                "base_hourly_limit": 50,
                "monetization_priority": 1.0,
                "performance_target": 0.8
            },
            "tiktok": {
                "base_quota": 1000,
                "base_upload_cost": 10,
                "base_daily_uploads": 200,
                "base_hourly_limit": 30,
                "monetization_priority": 0.6,
                "performance_target": 0.7
            },
            "instagram": {
                "base_quota": 500,
                "base_upload_cost": 5,
                "base_daily_uploads": 100,
                "base_hourly_limit": 25,
                "monetization_priority": 0.5,
                "performance_target": 0.6
            },
            "x": {
                "base_quota": 300,
                "base_upload_cost": 3,
                "base_daily_uploads": 50,
                "base_hourly_limit": 15,
                "monetization_priority": 0.4,
                "performance_target": 0.5
            }
        }
        
        # Performance tracking
        self.performance_history = {}
        self.resource_metrics = {}
        self.optimization_history = []
        
        # Initialize resource tracking
        self._initialize_resource_tracking()
        
    def _initialize_resource_tracking(self):
        """Initialize resource tracking for all platforms"""
        for platform, config in self.base_platform_configs.items():
            self.resource_metrics[platform] = ResourceMetrics(
                platform=platform,
                current_usage=0,
                daily_limit=config["base_daily_uploads"],
                hourly_usage=0,
                hourly_limit=config["base_hourly_limit"],
                success_rate=0.8,  # Initial baseline
                avg_performance_score=0.6,  # Initial baseline
                cost_per_success=config["base_upload_cost"],
                roi_factor=1.0,  # Initial baseline
                trend_momentum=0.0  # Neutral starting point
            )
    
    def optimize_resource_allocation(self, 
                                   total_available_quota: int = 10000,
                                   performance_data: Dict[str, Any] = None) -> Dict[str, Dict[str, Any]]:
        """
        Main AI-powered resource optimization method
        
        Args:
            total_available_quota: Total quota available for allocation
            performance_data: Recent performance metrics
            
        Returns:
            Optimized resource allocation for all platforms
        """
        logger.info("🤖 Starting AI-powered resource optimization")
        
        # Update performance metrics
        if performance_data:
            self._update_performance_metrics(performance_data)
        
        # Get trend-based insights
        trend_insights = self._analyze_platform_trends()
        
        # Calculate optimization recommendations
        recommendations = self._generate_optimization_recommendations(total_available_quota, trend_insights)
        
        # Apply AI-optimized allocations
        optimized_config = self._apply_optimization_recommendations(recommendations)
        
        # Log optimization results
        self._log_optimization_results(recommendations, optimized_config)
        
        # Save optimization history
        self._save_optimization_history(recommendations, optimized_config)
        
        logger.info("✅ AI resource optimization completed")
        return optimized_config
    
    def _update_performance_metrics(self, performance_data: Dict[str, Any]):
        """Update performance metrics from recent data"""
        
        for platform, data in performance_data.items():
            if platform in self.resource_metrics:
                metrics = self.resource_metrics[platform]
                
                # Update metrics with new data
                metrics.current_usage = data.get("current_usage", metrics.current_usage)
                metrics.hourly_usage = data.get("hourly_usage", metrics.hourly_usage)
                metrics.success_rate = data.get("success_rate", metrics.success_rate)
                metrics.avg_performance_score = data.get("avg_performance_score", metrics.avg_performance_score)
                metrics.cost_per_success = data.get("cost_per_success", metrics.cost_per_success)
                metrics.roi_factor = data.get("roi_factor", metrics.roi_factor)
                
                logger.info(f"📊 Updated metrics for {platform}: Success rate {metrics.success_rate:.2f}, ROI {metrics.roi_factor:.2f}")
    
    def _analyze_platform_trends(self) -> Dict[str, Dict[str, Any]]:
        """Analyze platform trends using YouTube expert agent"""
        
        trend_insights = {}
        
        for platform in self.base_platform_configs.keys():
            try:
                if platform == "youtube":
                    # Use YouTube expert agent for detailed trend analysis
                    trends_data = self.youtube_expert.monitor_trends(
                        category=ContentCategory.TECH,
                        geographic_region="US",
                        time_horizon=7
                    )
                    
                    opportunities = trends_data.get("trends", {}).get("opportunities", [])
                    high_priority_count = len([opp for opp in opportunities if opp.get("opportunity_score", 0) >= 8.0])
                    avg_growth_rate = sum(opp.get("growth_rate", 0) for opp in opportunities) / max(len(opportunities), 1)
                    
                    trend_insights[platform] = {
                        "trend_strength": min(avg_growth_rate / 100, 1.0),
                        "opportunity_density": min(high_priority_count / 10, 1.0),
                        "market_momentum": self._calculate_market_momentum(trends_data),
                        "monetization_potential": self._calculate_monetization_potential(opportunities)
                    }
                else:
                    # Estimate trends for other platforms based on general tech trends
                    # This would be enhanced with platform-specific expert agents
                    trend_insights[platform] = {
                        "trend_strength": 0.6,  # Moderate baseline
                        "opportunity_density": 0.5,
                        "market_momentum": 0.0,
                        "monetization_potential": 0.4
                    }
                    
            except Exception as e:
                logger.warning(f"Trend analysis failed for {platform}: {e}")
                trend_insights[platform] = {
                    "trend_strength": 0.5,
                    "opportunity_density": 0.5,
                    "market_momentum": 0.0,
                    "monetization_potential": 0.5
                }
        
        return trend_insights
    
    def _calculate_market_momentum(self, trends_data: Dict[str, Any]) -> float:
        """Calculate market momentum from trend data"""
        
        immediate_actions = trends_data.get("recommendations", {}).get("immediate_actions", [])
        market_insights = trends_data.get("market_insights", {})
        
        # Calculate momentum based on immediate opportunities and market conditions
        momentum_score = len(immediate_actions) / 10.0  # Normalize to 0-1
        
        # Adjust based on market insights
        if "dominant_categories" in market_insights:
            momentum_score *= 1.2  # Strong market signals
        
        return min(momentum_score, 1.0)
    
    def _calculate_monetization_potential(self, opportunities: List[Dict[str, Any]]) -> float:
        """Calculate monetization potential from opportunities"""
        
        if not opportunities:
            return 0.5
        
        # Average monetization potential weighted by opportunity score
        total_weighted_potential = 0
        total_weight = 0
        
        for opp in opportunities:
            opp_score = opp.get("opportunity_score", 5.0)
            monetization = opp.get("monetization_potential", 0.5)
            
            weight = opp_score / 10.0
            total_weighted_potential += monetization * weight
            total_weight += weight
        
        return total_weighted_potential / max(total_weight, 0.1)
    
    def _generate_optimization_recommendations(self, 
                                             total_quota: int, 
                                             trend_insights: Dict[str, Dict[str, Any]]) -> List[OptimizationRecommendation]:
        """Generate AI-powered optimization recommendations"""
        
        recommendations = []
        
        for platform, metrics in self.resource_metrics.items():
            base_config = self.base_platform_configs[platform]
            trends = trend_insights.get(platform, {})
            
            # Calculate optimization score
            optimization_score = self._calculate_optimization_score(metrics, trends, base_config)
            
            # Determine recommended allocation
            current_allocation = metrics.daily_limit
            base_allocation = base_config["base_daily_uploads"]
            
            # AI-powered allocation adjustment
            performance_factor = metrics.success_rate * metrics.roi_factor
            trend_factor = trends.get("trend_strength", 0.5) * trends.get("monetization_potential", 0.5)
            momentum_factor = 1.0 + trends.get("market_momentum", 0.0)
            
            # Calculate recommended adjustment
            adjustment_factor = (
                performance_factor * self.optimization_config["performance_weight"] +
                trend_factor * self.optimization_config["trend_weight"] +
                (metrics.cost_per_success / base_config["base_upload_cost"]) * self.optimization_config["cost_weight"]
            ) * momentum_factor
            
            recommended_allocation = int(base_allocation * adjustment_factor)
            
            # Apply constraints
            min_allocation = int(base_allocation * self.optimization_config["min_allocation_threshold"])
            max_allocation = int(base_allocation * (1 + self.optimization_config["max_allocation_threshold"]))
            recommended_allocation = max(min_allocation, min(max_allocation, recommended_allocation))
            
            # Determine action
            if recommended_allocation > current_allocation * 1.1:
                action = "increase"
            elif recommended_allocation < current_allocation * 0.9:
                action = "decrease"
            else:
                action = "maintain"
            
            # Calculate confidence and expected improvement
            confidence_score = min(optimization_score, 0.95)
            expected_improvement = abs(recommended_allocation - current_allocation) / current_allocation
            
            # Risk assessment
            if expected_improvement > 0.3:
                risk_assessment = "high"
            elif expected_improvement > 0.1:
                risk_assessment = "medium"
            else:
                risk_assessment = "low"
            
            # Create recommendation
            recommendation = OptimizationRecommendation(
                platform=platform,
                action=action,
                current_allocation=current_allocation,
                recommended_allocation=recommended_allocation,
                confidence_score=confidence_score,
                reasoning=self._generate_reasoning(platform, action, performance_factor, trend_factor),
                expected_improvement=expected_improvement,
                risk_assessment=risk_assessment
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _calculate_optimization_score(self, 
                                    metrics: ResourceMetrics, 
                                    trends: Dict[str, Any], 
                                    base_config: Dict[str, Any]) -> float:
        """Calculate optimization score for a platform"""
        
        # Performance component
        performance_score = (metrics.success_rate * 0.4 + 
                           metrics.avg_performance_score * 0.3 + 
                           metrics.roi_factor * 0.3)
        
        # Trend component
        trend_score = (trends.get("trend_strength", 0.5) * 0.4 +
                      trends.get("opportunity_density", 0.5) * 0.3 +
                      trends.get("monetization_potential", 0.5) * 0.3)
        
        # Cost efficiency component
        cost_efficiency = min(base_config["base_upload_cost"] / max(metrics.cost_per_success, 0.1), 2.0) / 2.0
        
        # Combine components
        optimization_score = (
            performance_score * 0.5 +
            trend_score * 0.3 +
            cost_efficiency * 0.2
        )
        
        return min(optimization_score, 1.0)
    
    def _generate_reasoning(self, platform: str, action: str, performance_factor: float, trend_factor: float) -> str:
        """Generate human-readable reasoning for the recommendation"""
        
        reasoning_templates = {
            "increase": f"Performance factor ({performance_factor:.2f}) and trend analysis ({trend_factor:.2f}) indicate strong opportunity for {platform}. Recommend increasing allocation for maximum ROI.",
            "decrease": f"Performance factor ({performance_factor:.2f}) or trend analysis ({trend_factor:.2f}) suggest reallocating resources from {platform} to higher-performing platforms.",
            "maintain": f"Current {platform} allocation is optimal based on performance factor ({performance_factor:.2f}) and trend analysis ({trend_factor:.2f}). Maintain existing resource levels."
        }
        
        return reasoning_templates.get(action, f"Optimization analysis for {platform} suggests {action} action.")
    
    def _apply_optimization_recommendations(self, recommendations: List[OptimizationRecommendation]) -> Dict[str, Dict[str, Any]]:
        """Apply optimization recommendations and generate new configuration"""
        
        optimized_config = {}
        
        for rec in recommendations:
            platform = rec.platform
            base_config = self.base_platform_configs[platform]
            
            # Apply recommendation if confidence is high enough
            if rec.confidence_score >= self.optimization_config["risk_tolerance"]:
                new_allocation = rec.recommended_allocation
                logger.info(f"🎯 Applying optimization for {platform}: {rec.current_allocation} → {new_allocation}")
            else:
                new_allocation = rec.current_allocation
                logger.info(f"⚠️ Low confidence for {platform}, maintaining current allocation")
            
            # Calculate derived quotas
            hourly_limit = max(1, new_allocation // 24)
            quota_multiplier = new_allocation / base_config["base_daily_uploads"]
            
            optimized_config[platform] = {
                "daily_quota": int(base_config["base_quota"] * quota_multiplier),
                "upload_cost": base_config["base_upload_cost"],
                "max_daily_uploads": new_allocation,
                "rate_limit_hour": hourly_limit,
                "optimization_applied": True,
                "confidence_score": rec.confidence_score,
                "expected_improvement": rec.expected_improvement,
                "optimization_reasoning": rec.reasoning
            }
            
            # Update resource metrics
            self.resource_metrics[platform].daily_limit = new_allocation
            self.resource_metrics[platform].hourly_limit = hourly_limit
        
        return optimized_config
    
    def _log_optimization_results(self, 
                                recommendations: List[OptimizationRecommendation], 
                                optimized_config: Dict[str, Dict[str, Any]]):
        """Log optimization results"""
        
        logger.info("🤖 AI Resource Optimization Results:")
        
        for rec in recommendations:
            platform = rec.platform
            config = optimized_config[platform]
            
            logger.info(f"  {platform.upper()}:")
            logger.info(f"    Action: {rec.action}")
            logger.info(f"    Allocation: {rec.current_allocation} → {rec.recommended_allocation}")
            logger.info(f"    Confidence: {rec.confidence_score:.3f}")
            logger.info(f"    Expected improvement: {rec.expected_improvement:.2%}")
            logger.info(f"    Risk: {rec.risk_assessment}")
    
    def _save_optimization_history(self, 
                                 recommendations: List[OptimizationRecommendation], 
                                 optimized_config: Dict[str, Dict[str, Any]]):
        """Save optimization history for learning"""
        
        optimization_record = {
            "timestamp": datetime.now().isoformat(),
            "recommendations": [asdict(rec) for rec in recommendations],
            "optimized_config": optimized_config,
            "optimization_params": self.optimization_config
        }
        
        self.optimization_history.append(optimization_record)
        
        # Save to file for persistence
        history_file = Path("optimization_history.json")
        try:
            if history_file.exists():
                with open(history_file, 'r') as f:
                    existing_history = json.load(f)
            else:
                existing_history = []
            
            existing_history.append(optimization_record)
            
            # Keep only last 100 optimization records
            if len(existing_history) > 100:
                existing_history = existing_history[-100:]
            
            with open(history_file, 'w') as f:
                json.dump(existing_history, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Failed to save optimization history: {e}")
    
    def get_current_optimized_config(self) -> Dict[str, Dict[str, Any]]:
        """Get current optimized configuration"""
        
        current_config = {}
        
        for platform, metrics in self.resource_metrics.items():
            base_config = self.base_platform_configs[platform]
            
            current_config[platform] = {
                "daily_quota": int(base_config["base_quota"] * (metrics.daily_limit / base_config["base_daily_uploads"])),
                "upload_cost": base_config["base_upload_cost"],
                "max_daily_uploads": metrics.daily_limit,
                "rate_limit_hour": metrics.hourly_limit,
                "current_usage": metrics.current_usage,
                "success_rate": metrics.success_rate,
                "roi_factor": metrics.roi_factor,
                "last_optimized": datetime.now().isoformat()
            }
        
        return current_config
    
    def predict_resource_needs(self, days_ahead: int = 7) -> Dict[str, Dict[str, Any]]:
        """Predict future resource needs using AI analysis"""
        
        predictions = {}
        
        for platform in self.base_platform_configs.keys():
            try:
                # Get trend predictions
                if platform == "youtube":
                    trends_data = self.youtube_expert.monitor_trends(
                        category=ContentCategory.TECH,
                        geographic_region="US",
                        time_horizon=days_ahead
                    )
                    
                    # Extract prediction factors
                    opportunities = trends_data.get("trends", {}).get("opportunities", [])
                    avg_growth = sum(opp.get("growth_rate", 0) for opp in opportunities) / max(len(opportunities), 1)
                else:
                    avg_growth = 10.0  # Default growth assumption
                
                current_metrics = self.resource_metrics[platform]
                
                # Predict resource needs
                growth_factor = 1.0 + (avg_growth / 100.0)
                predicted_daily_uploads = int(current_metrics.daily_limit * growth_factor)
                predicted_quota_needed = int(self.base_platform_configs[platform]["base_quota"] * growth_factor)
                
                predictions[platform] = {
                    "predicted_daily_uploads": predicted_daily_uploads,
                    "predicted_quota_needed": predicted_quota_needed,
                    "growth_factor": growth_factor,
                    "confidence": 0.7,  # AI confidence in prediction
                    "recommendation": "scale_up" if growth_factor > 1.1 else "maintain" if growth_factor > 0.9 else "scale_down"
                }
                
            except Exception as e:
                logger.warning(f"Prediction failed for {platform}: {e}")
                predictions[platform] = {
                    "predicted_daily_uploads": current_metrics.daily_limit,
                    "predicted_quota_needed": self.base_platform_configs[platform]["base_quota"],
                    "growth_factor": 1.0,
                    "confidence": 0.5,
                    "recommendation": "maintain"
                }
        
        return predictions


def main():
    """Main entry point for intelligent resource optimization"""
    import argparse
    
    parser = argparse.ArgumentParser(description="TenxsomAI Intelligent Resource Optimizer")
    parser.add_argument("--optimize", action="store_true", help="Run optimization")
    parser.add_argument("--predict", type=int, default=7, help="Predict resource needs N days ahead")
    parser.add_argument("--quota", type=int, default=10000, help="Total available quota")
    parser.add_argument("--output", type=str, help="Output configuration file")
    
    args = parser.parse_args()
    
    # Initialize optimizer
    optimizer = IntelligentResourceOptimizer()
    
    if args.optimize:
        # Run optimization
        print("🤖 Running AI-powered resource optimization...")
        
        # Sample performance data (would come from actual monitoring)
        sample_performance = {
            "youtube": {"success_rate": 0.85, "roi_factor": 1.2},
            "tiktok": {"success_rate": 0.75, "roi_factor": 0.8},
            "instagram": {"success_rate": 0.70, "roi_factor": 0.6},
            "x": {"success_rate": 0.65, "roi_factor": 0.5}
        }
        
        optimized_config = optimizer.optimize_resource_allocation(
            total_available_quota=args.quota,
            performance_data=sample_performance
        )
        
        print(f"\n✅ Optimization complete!")
        for platform, config in optimized_config.items():
            print(f"  {platform}: {config['max_daily_uploads']} uploads/day (confidence: {config['confidence_score']:.3f})")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(optimized_config, f, indent=2)
            print(f"💾 Configuration saved to {args.output}")
    
    if args.predict:
        # Run prediction
        print(f"🔮 Predicting resource needs for next {args.predict} days...")
        
        predictions = optimizer.predict_resource_needs(args.predict)
        
        print(f"\n📈 Predictions:")
        for platform, prediction in predictions.items():
            print(f"  {platform}: {prediction['predicted_daily_uploads']} uploads/day")
            print(f"    Growth factor: {prediction['growth_factor']:.2f}")
            print(f"    Recommendation: {prediction['recommendation']}")


if __name__ == "__main__":
    main()