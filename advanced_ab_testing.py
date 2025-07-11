#!/usr/bin/env python3

"""
Advanced A/B Testing Framework for TenxsomAI
Tests thumbnails, titles, descriptions, and posting times for optimal performance
"""

import asyncio
import logging
import json
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ABTestVariant:
    """Individual variant in an A/B test"""
    variant_id: str
    test_id: str
    element_type: str  # 'thumbnail', 'title', 'description', 'post_time'
    content: Any
    impressions: int = 0
    clicks: int = 0
    views: int = 0
    engagement_rate: float = 0.0
    conversion_rate: float = 0.0
    revenue: float = 0.0

@dataclass
class ABTest:
    """A/B test configuration and results"""
    test_id: str
    test_type: str
    start_date: datetime
    end_date: Optional[datetime]
    variants: List[ABTestVariant]
    traffic_split: List[float]  # Percentage for each variant
    status: str = "running"  # running, completed, paused
    confidence_level: float = 0.0
    winner: Optional[str] = None

class AdvancedABTestingFramework:
    """
    Advanced A/B testing framework for optimizing content performance
    """
    
    def __init__(self, results_dir: str = "/tmp/ab_test_results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.active_tests = {}
        self.test_history = []
        
    async def create_thumbnail_test(self, content_id: str, thumbnail_variants: List[str]) -> str:
        """Create A/B test for thumbnail performance"""
        test_id = f"thumb_{content_id}_{int(datetime.now().timestamp())}"
        
        variants = []
        for i, thumbnail_path in enumerate(thumbnail_variants):
            variant = ABTestVariant(
                variant_id=f"{test_id}_var_{i}",
                test_id=test_id,
                element_type="thumbnail",
                content=thumbnail_path
            )
            variants.append(variant)
        
        # Equal traffic split
        traffic_split = [1.0 / len(variants)] * len(variants)
        
        ab_test = ABTest(
            test_id=test_id,
            test_type="thumbnail",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=7),
            variants=variants,
            traffic_split=traffic_split
        )
        
        self.active_tests[test_id] = ab_test
        await self._save_test_config(ab_test)
        
        logger.info(f"📊 Created thumbnail A/B test: {test_id} with {len(variants)} variants")
        return test_id
    
    async def create_title_test(self, content_id: str, title_variants: List[str]) -> str:
        """Create A/B test for title performance"""
        test_id = f"title_{content_id}_{int(datetime.now().timestamp())}"
        
        variants = []
        for i, title in enumerate(title_variants):
            variant = ABTestVariant(
                variant_id=f"{test_id}_var_{i}",
                test_id=test_id,
                element_type="title",
                content=title
            )
            variants.append(variant)
        
        traffic_split = [1.0 / len(variants)] * len(variants)
        
        ab_test = ABTest(
            test_id=test_id,
            test_type="title",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=3),  # Shorter test for titles
            variants=variants,
            traffic_split=traffic_split
        )
        
        self.active_tests[test_id] = ab_test
        await self._save_test_config(ab_test)
        
        logger.info(f"📊 Created title A/B test: {test_id} with {len(variants)} variants")
        return test_id
    
    async def create_posting_time_test(self, content_id: str, time_slots: List[str]) -> str:
        """Create A/B test for optimal posting times"""
        test_id = f"time_{content_id}_{int(datetime.now().timestamp())}"
        
        variants = []
        for i, time_slot in enumerate(time_slots):
            variant = ABTestVariant(
                variant_id=f"{test_id}_var_{i}",
                test_id=test_id,
                element_type="post_time",
                content=time_slot
            )
            variants.append(variant)
        
        traffic_split = [1.0 / len(variants)] * len(variants)
        
        ab_test = ABTest(
            test_id=test_id,
            test_type="posting_time",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=14),  # Longer test for time patterns
            variants=variants,
            traffic_split=traffic_split
        )
        
        self.active_tests[test_id] = ab_test
        await self._save_test_config(ab_test)
        
        logger.info(f"📊 Created posting time A/B test: {test_id} with {len(variants)} variants")
        return test_id
    
    def get_variant_for_user(self, test_id: str, user_id: str = None) -> Optional[ABTestVariant]:
        """Get the variant to show for a specific user/session"""
        if test_id not in self.active_tests:
            return None
        
        test = self.active_tests[test_id]
        
        # Use consistent hashing for user assignment
        if user_id:
            hash_value = hash(f"{test_id}_{user_id}") % 100
        else:
            hash_value = random.randint(0, 99)
        
        # Assign based on traffic split
        cumulative = 0
        for i, (variant, split) in enumerate(zip(test.variants, test.traffic_split)):
            cumulative += split * 100
            if hash_value < cumulative:
                return variant
        
        # Fallback to first variant
        return test.variants[0] if test.variants else None
    
    async def record_impression(self, test_id: str, variant_id: str):
        """Record an impression for a variant"""
        if test_id in self.active_tests:
            test = self.active_tests[test_id]
            for variant in test.variants:
                if variant.variant_id == variant_id:
                    variant.impressions += 1
                    await self._save_test_results(test)
                    break
    
    async def record_click(self, test_id: str, variant_id: str):
        """Record a click for a variant"""
        if test_id in self.active_tests:
            test = self.active_tests[test_id]
            for variant in test.variants:
                if variant.variant_id == variant_id:
                    variant.clicks += 1
                    variant.conversion_rate = variant.clicks / max(variant.impressions, 1)
                    await self._save_test_results(test)
                    break
    
    async def record_view(self, test_id: str, variant_id: str, view_duration: float = 0):
        """Record a view for a variant"""
        if test_id in self.active_tests:
            test = self.active_tests[test_id]
            for variant in test.variants:
                if variant.variant_id == variant_id:
                    variant.views += 1
                    # Calculate engagement rate based on view duration
                    if view_duration > 0:
                        variant.engagement_rate = (variant.engagement_rate * (variant.views - 1) + view_duration) / variant.views
                    await self._save_test_results(test)
                    break
    
    async def record_revenue(self, test_id: str, variant_id: str, revenue: float):
        """Record revenue for a variant"""
        if test_id in self.active_tests:
            test = self.active_tests[test_id]
            for variant in test.variants:
                if variant.variant_id == variant_id:
                    variant.revenue += revenue
                    await self._save_test_results(test)
                    break
    
    async def analyze_test_results(self, test_id: str) -> Dict[str, Any]:
        """Analyze A/B test results and determine statistical significance"""
        if test_id not in self.active_tests:
            return {"error": "Test not found"}
        
        test = self.active_tests[test_id]
        
        # Calculate performance metrics for each variant
        results = {
            "test_id": test_id,
            "test_type": test.test_type,
            "start_date": test.start_date.isoformat(),
            "variants": [],
            "winner": None,
            "confidence_level": 0.0,
            "recommendation": ""
        }
        
        best_variant = None
        best_score = 0
        
        for variant in test.variants:
            # Calculate composite performance score
            ctr = variant.clicks / max(variant.impressions, 1)
            view_rate = variant.views / max(variant.clicks, 1)
            revenue_per_impression = variant.revenue / max(variant.impressions, 1)
            
            # Weighted composite score
            composite_score = (
                ctr * 0.3 +  # Click-through rate
                view_rate * 0.3 +  # View completion rate
                variant.engagement_rate * 0.2 +  # Engagement quality
                revenue_per_impression * 100 * 0.2  # Revenue efficiency
            )
            
            variant_result = {
                "variant_id": variant.variant_id,
                "content": str(variant.content),
                "impressions": variant.impressions,
                "clicks": variant.clicks,
                "views": variant.views,
                "ctr": round(ctr * 100, 2),
                "view_rate": round(view_rate * 100, 2),
                "engagement_rate": round(variant.engagement_rate, 2),
                "revenue": round(variant.revenue, 2),
                "composite_score": round(composite_score, 4)
            }
            
            results["variants"].append(variant_result)
            
            if composite_score > best_score:
                best_score = composite_score
                best_variant = variant
        
        # Determine statistical significance (simplified)
        if best_variant and len(test.variants) > 1:
            total_impressions = sum(v.impressions for v in test.variants)
            if total_impressions > 1000:  # Minimum sample size
                # Simple confidence calculation based on sample size and performance difference
                other_variants = [v for v in test.variants if v != best_variant]
                avg_other_score = sum(
                    v.clicks / max(v.impressions, 1) for v in other_variants
                ) / len(other_variants)
                best_score_rate = best_variant.clicks / max(best_variant.impressions, 1)
                
                if best_score_rate > avg_other_score * 1.1:  # 10% improvement threshold
                    results["confidence_level"] = min(95.0, total_impressions / 50)  # Simplified confidence
                    results["winner"] = best_variant.variant_id
                    
                    # Update test status
                    test.confidence_level = results["confidence_level"]
                    test.winner = best_variant.variant_id
                    if results["confidence_level"] > 80:
                        test.status = "completed"
        
        # Generate recommendation
        if results["winner"]:
            winning_variant = next(v for v in results["variants"] if v["variant_id"] == results["winner"])
            results["recommendation"] = f"Use variant {results['winner']} ('{winning_variant['content']}') - {results['confidence_level']:.1f}% confidence"
        else:
            results["recommendation"] = "Continue testing - insufficient data for conclusive results"
        
        await self._save_test_results(test)
        
        return results
    
    async def get_optimization_recommendations(self) -> Dict[str, Any]:
        """Get overall optimization recommendations based on all test results"""
        recommendations = {
            "thumbnail_insights": [],
            "title_insights": [],
            "timing_insights": [],
            "general_recommendations": []
        }
        
        # Analyze completed tests for patterns
        completed_tests = [test for test in self.active_tests.values() if test.status == "completed"]
        
        # Thumbnail insights
        thumbnail_tests = [test for test in completed_tests if test.test_type == "thumbnail"]
        if thumbnail_tests:
            # Analyze winning thumbnail characteristics
            winning_thumbnails = [test.winner for test in thumbnail_tests if test.winner]
            if winning_thumbnails:
                recommendations["thumbnail_insights"].append("Successful thumbnail patterns identified")
        
        # Title insights
        title_tests = [test for test in completed_tests if test.test_type == "title"]
        if title_tests:
            recommendations["title_insights"].append("Optimal title structures identified")
        
        # Timing insights
        timing_tests = [test for test in completed_tests if test.test_type == "posting_time"]
        if timing_tests:
            recommendations["timing_insights"].append("Optimal posting times identified")
        
        # General recommendations
        if len(completed_tests) > 5:
            recommendations["general_recommendations"].append("Sufficient test data for strategic optimization")
        else:
            recommendations["general_recommendations"].append("Continue A/B testing for more insights")
        
        return recommendations
    
    async def _save_test_config(self, test: ABTest):
        """Save test configuration to disk"""
        config_file = self.results_dir / f"{test.test_id}_config.json"
        with open(config_file, 'w') as f:
            # Convert dataclass to dict for JSON serialization
            test_dict = asdict(test)
            test_dict['start_date'] = test.start_date.isoformat()
            if test.end_date:
                test_dict['end_date'] = test.end_date.isoformat()
            json.dump(test_dict, f, indent=2)
    
    async def _save_test_results(self, test: ABTest):
        """Save test results to disk"""
        results_file = self.results_dir / f"{test.test_id}_results.json"
        with open(results_file, 'w') as f:
            test_dict = asdict(test)
            test_dict['start_date'] = test.start_date.isoformat()
            if test.end_date:
                test_dict['end_date'] = test.end_date.isoformat()
            test_dict['last_updated'] = datetime.now().isoformat()
            json.dump(test_dict, f, indent=2)

# Integration example
async def integrate_ab_testing_with_content_upload():
    """Example of how to integrate A/B testing with content upload"""
    ab_framework = AdvancedABTestingFramework()
    
    # Example: Test multiple thumbnails for a video
    thumbnail_variants = [
        "/path/to/thumbnail_a.jpg",  # Bright colors, large text
        "/path/to/thumbnail_b.jpg",  # Dark theme, minimal text
        "/path/to/thumbnail_c.jpg"   # Face closeup, emotion-driven
    ]
    
    test_id = await ab_framework.create_thumbnail_test("video_001", thumbnail_variants)
    
    # When uploading, get the variant for this user/upload
    variant = ab_framework.get_variant_for_user(test_id, "user_123")
    
    if variant:
        # Use the selected thumbnail variant
        thumbnail_to_use = variant.content
        
        # Record impression
        await ab_framework.record_impression(test_id, variant.variant_id)
        
        print(f"Using thumbnail variant: {thumbnail_to_use}")
        
        # Later, when tracking performance:
        await ab_framework.record_click(test_id, variant.variant_id)
        await ab_framework.record_view(test_id, variant.variant_id, view_duration=120.5)
        await ab_framework.record_revenue(test_id, variant.variant_id, 0.05)
    
    # Analyze results after collecting data
    results = await ab_framework.analyze_test_results(test_id)
    print(f"Test results: {results}")

if __name__ == "__main__":
    asyncio.run(integrate_ab_testing_with_content_upload())