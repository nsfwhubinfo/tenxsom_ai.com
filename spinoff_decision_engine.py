#!/usr/bin/env python3
"""
Spinoff Recommendation Engine for Hub/Spoke Strategy
"""

import asyncio
from typing import Dict, Any, List


class SpinoffRecommendationEngine:
    """AI-powered decision engine for channel spinoffs"""
    
    def __init__(self):
        self.default_thresholds = {
            "min_retention_rate": 65.0,
            "min_subscriber_gain_per_video": 50,
            "min_total_videos": 20,
            "min_avg_views": 10000,
            "min_engagement_rate": 3.5,
            "growth_trend_required": "increasing"
        }
    
    async def analyze_archetype_for_spinoff(self, archetype: str) -> dict:
        """Analyze if archetype is ready for spinoff"""
        
        # Get performance data
        performance_data = await self.get_archetype_performance(archetype)
        
        # Evaluate against criteria
        criteria_evaluation = {}
        spinoff_score = 0
        max_score = len(self.default_thresholds)
        
        for criterion, threshold in self.default_thresholds.items():
            actual_value = performance_data.get(criterion.replace("min_", "").replace("_required", ""))
            
            if criterion == "growth_trend_required":
                meets_criteria = actual_value == threshold
            else:
                meets_criteria = actual_value >= threshold
            
            criteria_evaluation[criterion] = {
                "actual": actual_value,
                "threshold": threshold,
                "meets_criteria": meets_criteria
            }
            
            if meets_criteria:
                spinoff_score += 1
        
        # Calculate confidence
        confidence = spinoff_score / max_score
        
        # Make recommendation
        if confidence >= 0.8:  # 80% of criteria met
            recommendation = "immediate_spinoff"
        elif confidence >= 0.6:  # 60% of criteria met
            recommendation = "monitor_closely"
        else:
            recommendation = "continue_incubation"
        
        return {
            "archetype": archetype,
            "spinoff_score": spinoff_score,
            "max_score": max_score,
            "confidence": confidence,
            "criteria_evaluation": criteria_evaluation,
            "recommendation": recommendation,
            "suggested_actions": self.get_suggested_actions(recommendation, criteria_evaluation)
        }
    
    def get_suggested_actions(self, recommendation: str, criteria: dict) -> list:
        """Get suggested actions based on recommendation"""
        
        if recommendation == "immediate_spinoff":
            return [
                "Create new YouTube channel",
                "Transfer top 10 videos of this archetype",
                "Set up cross-promotion from hub",
                "Begin exclusive content production"
            ]
        elif recommendation == "monitor_closely":
            return [
                "Increase content frequency for this archetype",
                "Focus on retention optimization",
                "A/B test titles and thumbnails",
                "Re-evaluate in 2 weeks"
            ]
        else:
            return [
                "Continue testing on hub channel",
                "Optimize content quality",
                "Experiment with different formats",
                "Build audience before specialization"
            ]
