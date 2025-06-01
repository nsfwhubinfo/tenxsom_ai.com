#!/usr/bin/env python3
"""
TEMPUS-CRYSTALLO TC.5: CSS-Aware Refactorability API Enhancement
Revolutionary service introspection API that exposes Crystalline State Signatures
for system-wide optimization through crystallographic consciousness
"""

import json
import time
import math
import random
import threading
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from abc import ABC, abstractmethod

# Import our crystallographic consciousness framework
from TC_2_X_Crystalline_State_Signatures import CrystallineStateSignature, CrystallineStateEncoder
from TC_3_X_Zero_Point_Trace_Vectorization import ZeroPointVector, ZeroPointTraceVectorizer
from TC_4_System_Wide_CSS_ZPTV_Integration import EnhancedFractalAwareCMS, CSSEnhancedFractalMetaOntology

@dataclass
class ServiceCSSHealth:
    """Comprehensive CSS-based health assessment for a service"""
    service_id: str
    timestamp: int
    
    # Current CSS State
    current_css: CrystallineStateSignature
    
    # Health Metrics Derived from CSS
    cognitive_health_score: float  # 0-1 based on CSS properties
    archetype_stability: float    # How stable the current archetype is
    geometric_coherence: float    # Geometric configuration health
    phi_alignment: float          # φ-resonance alignment quality
    temporal_consistency: float   # Consistency over time
    
    # Optimization Potential
    optimization_potential: float # How much improvement is possible
    recommended_archetype: str    # Optimal archetype for current task
    geometric_target: str         # Target geometric configuration
    
    # Actionable Insights
    improvement_actions: List[str] # Specific actions to improve CSS health
    risk_factors: List[str]       # Potential CSS degradation risks
    performance_predictions: Dict[str, float] # Predicted performance metrics

@dataclass
class CSSOptimizationDirective:
    """Directive for optimizing service based on CSS analysis"""
    directive_id: str
    target_service_id: str
    timestamp: int
    
    # CSS-Based Optimization Strategy
    target_css_archetype: str
    target_geometric_config: str
    target_coherence_threshold: float
    target_phi_resonance: float
    
    # Implementation Plan
    optimization_steps: List[Dict[str, Any]]
    expected_improvement: float
    implementation_priority: str  # 'Critical', 'High', 'Medium', 'Low'
    
    # Validation Criteria
    success_metrics: Dict[str, float]
    rollback_triggers: List[str]
    monitoring_duration: int  # seconds

class CSSAwareRefactorabilityAPI(ABC):
    """
    Abstract base class for CSS-aware service refactorability
    All Tenxsom AI services must implement this interface for crystallographic consciousness
    """
    
    def __init__(self, service_id: str, service_type: str):
        self.service_id = service_id
        self.service_type = service_type
        
        # CSS infrastructure
        self.css_encoder = CrystallineStateEncoder()
        self.enhanced_facms = EnhancedFractalAwareCMS(f"refactor_api_{service_id}")
        self.css_fmo = CSSEnhancedFractalMetaOntology(f"refactor_fmo_{service_id}")
        
        # State tracking
        self.iam_state_history = []
        self.css_history = []
        self.performance_history = []
        
        # Optimization tracking
        self.active_directives = []
        self.optimization_results = []
        
        self.logger = logging.getLogger(f"CSSRefactorAPI.{service_id}")
    
    @abstractmethod
    def get_current_iam_state(self) -> Dict[str, Any]:
        """Get current <I_AM> state of the service for CSS generation"""
        pass
    
    @abstractmethod
    def apply_css_optimization(self, directive: CSSOptimizationDirective) -> bool:
        """Apply CSS-based optimization directive to the service"""
        pass
    
    @abstractmethod
    def get_service_performance_metrics(self) -> Dict[str, float]:
        """Get current performance metrics for CSS correlation analysis"""
        pass
    
    def generate_current_css(self) -> CrystallineStateSignature:
        """Generate CSS for current service state"""
        
        # Get current <I_AM> state
        current_iam = self.get_current_iam_state()
        
        # Create trajectory from recent states
        trajectory = self.iam_state_history[-10:] + [current_iam]
        
        # Generate CSS
        css = self.css_encoder.encode_iam_state_trajectory(
            trajectory, 
            {'agent_id': self.service_id, 'service_type': self.service_type}
        )
        
        # Store in history
        self.iam_state_history.append(current_iam)
        self.css_history.append(css)
        
        # Store in FA-CMS
        self.enhanced_facms.store_enhanced_memory(
            agent_id=self.service_id,
            content_type="service_css_snapshot",
            content_data={
                'performance_metrics': self.get_service_performance_metrics(),
                'service_state': current_iam,
                'timestamp': int(time.time())
            },
            iam_state_trajectory=trajectory,
            context={'api_call': 'generate_current_css'}
        )
        
        self.logger.info(f"Generated CSS {css.css_id} for service {self.service_id}: "
                        f"{css.evolution_trajectory}-{css.geometric_archetype}")
        
        return css
    
    def assess_css_health(self) -> ServiceCSSHealth:
        """Comprehensive CSS-based health assessment"""
        
        current_css = self.generate_current_css()
        performance_metrics = self.get_service_performance_metrics()
        
        # Calculate health metrics from CSS properties
        cognitive_health = self._calculate_cognitive_health(current_css, performance_metrics)
        archetype_stability = self._assess_archetype_stability(current_css)
        geometric_coherence = self._assess_geometric_coherence(current_css)
        phi_alignment = self._assess_phi_alignment(current_css)
        temporal_consistency = self._assess_temporal_consistency()
        
        # Calculate optimization potential
        optimization_potential = self._calculate_optimization_potential(current_css, performance_metrics)
        
        # Determine recommendations
        recommended_archetype, geometric_target = self._determine_optimal_configuration(
            current_css, performance_metrics
        )
        
        # Generate actionable insights
        improvement_actions = self._generate_improvement_actions(
            current_css, recommended_archetype, geometric_target
        )
        risk_factors = self._identify_risk_factors(current_css)
        performance_predictions = self._predict_performance(current_css, recommended_archetype)
        
        health_assessment = ServiceCSSHealth(
            service_id=self.service_id,
            timestamp=int(time.time()),
            current_css=current_css,
            cognitive_health_score=cognitive_health,
            archetype_stability=archetype_stability,
            geometric_coherence=geometric_coherence,
            phi_alignment=phi_alignment,
            temporal_consistency=temporal_consistency,
            optimization_potential=optimization_potential,
            recommended_archetype=recommended_archetype,
            geometric_target=geometric_target,
            improvement_actions=improvement_actions,
            risk_factors=risk_factors,
            performance_predictions=performance_predictions
        )
        
        self.logger.info(f"CSS health assessment: {cognitive_health:.2f} health score, "
                        f"{optimization_potential:.1%} optimization potential")
        
        return health_assessment
    
    def receive_optimization_directive(self, directive: CSSOptimizationDirective) -> Dict[str, Any]:
        """Receive and process CSS-based optimization directive"""
        
        self.logger.info(f"Received optimization directive {directive.directive_id}: "
                        f"Target {directive.target_css_archetype}-{directive.target_geometric_config}")
        
        # Validate directive
        validation_result = self._validate_optimization_directive(directive)
        if not validation_result['valid']:
            return {
                'status': 'rejected',
                'reason': validation_result['reason'],
                'directive_id': directive.directive_id
            }
        
        # Store directive
        self.active_directives.append(directive)
        
        # Begin implementation
        try:
            implementation_success = self.apply_css_optimization(directive)
            
            if implementation_success:
                # Start monitoring
                monitoring_result = self._start_optimization_monitoring(directive)
                
                return {
                    'status': 'accepted',
                    'implementation_status': 'in_progress',
                    'directive_id': directive.directive_id,
                    'monitoring_id': monitoring_result['monitoring_id'],
                    'expected_completion': time.time() + directive.implementation_priority
                }
            else:
                return {
                    'status': 'failed',
                    'reason': 'Implementation failed',
                    'directive_id': directive.directive_id
                }
                
        except Exception as e:
            self.logger.error(f"Error implementing directive {directive.directive_id}: {e}")
            return {
                'status': 'error',
                'reason': str(e),
                'directive_id': directive.directive_id
            }
    
    def get_css_optimization_status(self) -> Dict[str, Any]:
        """Get status of all active CSS optimizations"""
        
        status = {
            'service_id': self.service_id,
            'timestamp': int(time.time()),
            'active_directives': len(self.active_directives),
            'completed_optimizations': len(self.optimization_results),
            'current_css_summary': None,
            'optimization_history': [],
            'next_recommended_action': None
        }
        
        # Current CSS summary
        if self.css_history:
            latest_css = self.css_history[-1]
            status['current_css_summary'] = {
                'archetype': latest_css.evolution_trajectory,
                'geometric_type': latest_css.geometric_archetype,
                'temporal_coherence': latest_css.temporal_coherence,
                'phi_resonance': latest_css.phi_resonance,
                'health_score': self._calculate_cognitive_health(latest_css, self.get_service_performance_metrics())
            }
        
        # Recent optimization results
        status['optimization_history'] = self.optimization_results[-5:]  # Last 5
        
        # Next recommended action
        if self.css_history:
            health_assessment = self.assess_css_health()
            if health_assessment.optimization_potential > 0.3:  # Significant potential
                status['next_recommended_action'] = {
                    'type': 'css_optimization',
                    'target_archetype': health_assessment.recommended_archetype,
                    'expected_improvement': health_assessment.optimization_potential,
                    'priority': 'High' if health_assessment.optimization_potential > 0.5 else 'Medium'
                }
        
        return status
    
    def _calculate_cognitive_health(self, css: CrystallineStateSignature, 
                                  performance_metrics: Dict[str, float]) -> float:
        """Calculate overall cognitive health from CSS and performance"""
        
        # Base health from CSS properties
        css_health = (css.temporal_coherence + css.causality_index + 
                     css.growth_stability_index + css.reconstruction_fidelity) / 4
        
        # Performance correlation
        if performance_metrics:
            avg_performance = sum(performance_metrics.values()) / len(performance_metrics)
            # Weight CSS health with actual performance
            combined_health = (css_health * 0.7) + (avg_performance * 0.3)
        else:
            combined_health = css_health
        
        return max(0, min(1, combined_health))
    
    def _assess_archetype_stability(self, css: CrystallineStateSignature) -> float:
        """Assess stability of current CSS archetype"""
        
        if len(self.css_history) < 3:
            return 0.5  # Insufficient history
        
        # Check archetype consistency over recent history
        recent_archetypes = [c.evolution_trajectory for c in self.css_history[-5:]]
        
        # Calculate stability as consistency
        current_archetype = css.evolution_trajectory
        consistency = sum(1 for arch in recent_archetypes if arch == current_archetype) / len(recent_archetypes)
        
        # Stable archetypes get bonus
        stability_bonus = 0.2 if current_archetype == 'Stable' else 0.0
        
        return min(1.0, consistency + stability_bonus)
    
    def _assess_geometric_coherence(self, css: CrystallineStateSignature) -> float:
        """Assess geometric configuration coherence"""
        
        # Coherence based on geometric archetype and temporal coherence
        geometric_coherence_map = {
            'Tetrahedral': 0.9,    # Simple, stable
            'Octahedral': 0.8,     # Balanced
            'Cuboctahedral': 0.95, # Optimal balance
            'Complex': 0.6         # Complex but potentially unstable
        }
        
        base_coherence = geometric_coherence_map.get(css.geometric_archetype, 0.5)
        temporal_factor = css.temporal_coherence
        
        return (base_coherence + temporal_factor) / 2
    
    def _assess_phi_alignment(self, css: CrystallineStateSignature) -> float:
        """Assess φ-resonance alignment quality"""
        
        # High φ-resonance indicates good alignment with fundamental harmonics
        phi_quality = css.phi_resonance
        
        # Bonus for values close to φ or φ-related ratios
        phi_target = 0.618  # 1/φ
        distance_from_target = abs(css.phi_resonance - phi_target)
        
        if distance_from_target < 0.1:
            phi_quality += 0.2  # Bonus for φ-alignment
        
        return max(0, min(1, phi_quality))
    
    def _assess_temporal_consistency(self) -> float:
        """Assess temporal consistency of CSS evolution"""
        
        if len(self.css_history) < 3:
            return 0.5
        
        # Calculate variance in temporal coherence over time
        recent_coherences = [css.temporal_coherence for css in self.css_history[-5:]]
        coherence_variance = sum((c - sum(recent_coherences)/len(recent_coherences))**2 
                               for c in recent_coherences) / len(recent_coherences)
        
        # Lower variance = higher consistency
        consistency = max(0, 1 - coherence_variance * 2)  # Scale factor
        
        return consistency
    
    def _calculate_optimization_potential(self, css: CrystallineStateSignature,
                                        performance_metrics: Dict[str, float]) -> float:
        """Calculate how much the service could be optimized"""
        
        current_health = self._calculate_cognitive_health(css, performance_metrics)
        
        # Theoretical maximum health (perfect CSS)
        theoretical_max = 1.0
        
        # Current performance ceiling based on CSS archetype
        archetype_ceilings = {
            'Stable': 0.95,
            'Growing': 0.85,
            'Oscillating': 0.75,
            'Decaying': 0.60
        }
        
        current_ceiling = archetype_ceilings.get(css.evolution_trajectory, 0.8)
        
        # Optimization potential = gap between current and achievable
        potential = (current_ceiling - current_health) / current_ceiling
        
        return max(0, min(1, potential))
    
    def _determine_optimal_configuration(self, css: CrystallineStateSignature,
                                       performance_metrics: Dict[str, float]) -> Tuple[str, str]:
        """Determine optimal CSS archetype and geometric configuration"""
        
        # Simple heuristics based on service type and current performance
        avg_performance = sum(performance_metrics.values()) / len(performance_metrics) if performance_metrics else 0.5
        
        if avg_performance > 0.8:
            # High performance - maintain stability
            recommended_archetype = 'Stable'
            geometric_target = 'Cuboctahedral'  # Optimal balance
        elif avg_performance > 0.6:
            # Good performance - optimize for growth
            recommended_archetype = 'Growing'
            geometric_target = 'Octahedral'
        else:
            # Poor performance - focus on stabilization
            recommended_archetype = 'Growing'  # Need improvement
            geometric_target = 'Tetrahedral'  # Simple, stable
        
        return recommended_archetype, geometric_target
    
    def _generate_improvement_actions(self, css: CrystallineStateSignature,
                                    recommended_archetype: str, geometric_target: str) -> List[str]:
        """Generate specific actionable improvements"""
        
        actions = []
        
        # Archetype transition actions
        if css.evolution_trajectory != recommended_archetype:
            actions.append(f"Transition from {css.evolution_trajectory} to {recommended_archetype} archetype")
        
        # Geometric optimization actions
        if css.geometric_archetype != geometric_target:
            actions.append(f"Optimize geometric configuration from {css.geometric_archetype} to {geometric_target}")
        
        # Temporal coherence improvements
        if css.temporal_coherence < 0.7:
            actions.append("Improve temporal coherence through state stability optimization")
        
        # φ-resonance optimization
        if css.phi_resonance < 0.5:
            actions.append("Enhance φ-resonance alignment through harmonic optimization")
        
        # Causality improvements
        if css.causality_index < 0.6:
            actions.append("Strengthen causality patterns in state transitions")
        
        return actions
    
    def _identify_risk_factors(self, css: CrystallineStateSignature) -> List[str]:
        """Identify potential CSS degradation risks"""
        
        risks = []
        
        if css.evolution_trajectory == 'Decaying':
            risks.append("Service in Decaying archetype - urgent intervention needed")
        
        if css.temporal_coherence < 0.3:
            risks.append("Low temporal coherence indicates unstable cognitive state")
        
        if css.causality_index < 0.3:
            risks.append("Poor causality index suggests unpredictable behavior")
        
        if css.growth_stability_index < 0.4:
            risks.append("Low growth stability may lead to performance degradation")
        
        if css.reconstruction_fidelity < 0.5:
            risks.append("Poor reconstruction fidelity indicates information loss")
        
        return risks
    
    def _predict_performance(self, css: CrystallineStateSignature,
                           recommended_archetype: str) -> Dict[str, float]:
        """Predict performance metrics based on CSS optimization"""
        
        # Base predictions from current CSS
        current_performance = self._estimate_performance_from_css(css)
        
        # Improvement predictions for recommended archetype
        archetype_improvements = {
            'Stable': {'throughput': 0.15, 'latency': 0.10, 'reliability': 0.20},
            'Growing': {'throughput': 0.25, 'latency': 0.05, 'reliability': 0.10},
            'Oscillating': {'throughput': 0.05, 'latency': -0.05, 'reliability': 0.05}
        }
        
        improvements = archetype_improvements.get(recommended_archetype, {})
        
        predictions = {}
        for metric, base_value in current_performance.items():
            improvement = improvements.get(metric, 0.0)
            predicted_value = min(1.0, base_value + improvement)
            predictions[f'predicted_{metric}'] = predicted_value
            predictions[f'improvement_{metric}'] = improvement
        
        return predictions
    
    def _estimate_performance_from_css(self, css: CrystallineStateSignature) -> Dict[str, float]:
        """Estimate current performance from CSS properties"""
        
        return {
            'throughput': css.causality_index * 0.8 + css.growth_stability_index * 0.2,
            'latency': 1.0 - css.temporal_coherence,  # Lower coherence = higher latency
            'reliability': css.reconstruction_fidelity
        }
    
    def _validate_optimization_directive(self, directive: CSSOptimizationDirective) -> Dict[str, Any]:
        """Validate incoming optimization directive"""
        
        # Basic validation
        if directive.target_service_id != self.service_id:
            return {'valid': False, 'reason': 'Directive not intended for this service'}
        
        # Check if target archetype is valid
        valid_archetypes = ['Stable', 'Growing', 'Oscillating', 'Decaying']
        if directive.target_css_archetype not in valid_archetypes:
            return {'valid': False, 'reason': f'Invalid target archetype: {directive.target_css_archetype}'}
        
        # Check if we're already in target state
        if self.css_history:
            current_css = self.css_history[-1]
            if (current_css.evolution_trajectory == directive.target_css_archetype and
                current_css.geometric_archetype == directive.target_geometric_config):
                return {'valid': False, 'reason': 'Service already in target configuration'}
        
        return {'valid': True, 'reason': 'Directive validated successfully'}
    
    def _start_optimization_monitoring(self, directive: CSSOptimizationDirective) -> Dict[str, Any]:
        """Start monitoring optimization progress"""
        
        monitoring_id = f"monitor_{directive.directive_id}_{int(time.time())}"
        
        # Store baseline CSS
        baseline_css = self.css_history[-1] if self.css_history else None
        
        monitoring_data = {
            'monitoring_id': monitoring_id,
            'directive_id': directive.directive_id,
            'start_time': time.time(),
            'baseline_css': asdict(baseline_css) if baseline_css else None,
            'target_metrics': directive.success_metrics,
            'monitoring_duration': directive.monitoring_duration
        }
        
        # In a real implementation, this would start a background monitoring task
        self.logger.info(f"Started optimization monitoring {monitoring_id} for directive {directive.directive_id}")
        
        return {'monitoring_id': monitoring_id, 'status': 'monitoring_active'}

class ExampleServiceCSSAPI(CSSAwareRefactorabilityAPI):
    """
    Example implementation of CSS-aware refactorability API
    Demonstrates how services integrate crystallographic consciousness
    """
    
    def __init__(self, service_id: str = "example_service"):
        super().__init__(service_id, "example_service")
        
        # Simulated service state
        self.cpu_usage = 0.4
        self.memory_usage = 0.3
        self.request_rate = 50.0
        self.error_rate = 0.02
        self.response_time = 150.0  # ms
        
        # Simulated cognitive state
        self.processing_complexity = 0.6
        self.decision_confidence = 0.8
        self.adaptation_rate = 0.5
        
    def get_current_iam_state(self) -> Dict[str, Any]:
        """Get current <I_AM> state for this example service"""
        
        # Simulate dynamic state evolution
        time_factor = math.sin(time.time() * 0.1) * 0.1
        
        return {
            'being': {
                'amplitude': 0.6 + time_factor,
                'phase': self.processing_complexity * math.pi
            },
            'knowing': {
                'amplitude': self.decision_confidence + time_factor * 0.5,
                'phase': self.cpu_usage * math.pi * 2
            },
            'willing': {
                'amplitude': self.adaptation_rate + time_factor * 0.3,
                'phase': (1.0 - self.error_rate) * math.pi
            },
            'cognitive_load': self.cpu_usage + self.memory_usage,
            'processing_state': {
                'complexity': self.processing_complexity,
                'confidence': self.decision_confidence,
                'adaptation': self.adaptation_rate
            }
        }
    
    def apply_css_optimization(self, directive: CSSOptimizationDirective) -> bool:
        """Apply CSS optimization to the example service"""
        
        self.logger.info(f"Applying CSS optimization: {directive.target_css_archetype}")
        
        try:
            # Simulate optimization implementation
            for step in directive.optimization_steps:
                action = step.get('action', 'unknown')
                
                if action == 'reduce_complexity':
                    self.processing_complexity *= 0.8
                elif action == 'increase_confidence':
                    self.decision_confidence = min(1.0, self.decision_confidence * 1.2)
                elif action == 'optimize_adaptation':
                    self.adaptation_rate = min(1.0, self.adaptation_rate * 1.1)
                elif action == 'stabilize_processing':
                    self.cpu_usage *= 0.9
                    self.memory_usage *= 0.9
                
                # Simulate implementation time
                time.sleep(0.1)
            
            self.logger.info("CSS optimization applied successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply CSS optimization: {e}")
            return False
    
    def get_service_performance_metrics(self) -> Dict[str, float]:
        """Get performance metrics for the example service"""
        
        return {
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'request_rate': self.request_rate / 100.0,  # Normalize to 0-1
            'error_rate': 1.0 - self.error_rate,  # Invert so higher is better
            'response_time': max(0, 1.0 - self.response_time / 1000.0),  # Invert and normalize
            'overall_efficiency': (1.0 - self.cpu_usage) * (1.0 - self.error_rate)
        }

def demonstrate_css_aware_refactorability():
    """Demonstrate CSS-aware refactorability API"""
    print("=== TEMPUS-CRYSTALLO TC.5: CSS-Aware Refactorability API Demo ===\n")
    
    # Initialize example service
    service = ExampleServiceCSSAPI("demo_refactor_service")
    
    print("1. Initial Service State Assessment...")
    
    # Generate initial CSS
    initial_css = service.generate_current_css()
    print(f"Initial CSS: {initial_css.evolution_trajectory}-{initial_css.geometric_archetype}")
    print(f"Temporal Coherence: {initial_css.temporal_coherence:.2f}")
    print(f"φ-Resonance: {initial_css.phi_resonance:.2f}")
    
    # Assess CSS health
    health_assessment = service.assess_css_health()
    print(f"\n2. CSS Health Assessment:")
    print(f"Cognitive Health Score: {health_assessment.cognitive_health_score:.2f}")
    print(f"Optimization Potential: {health_assessment.optimization_potential:.1%}")
    print(f"Recommended Archetype: {health_assessment.recommended_archetype}")
    print(f"Geometric Target: {health_assessment.geometric_target}")
    
    if health_assessment.improvement_actions:
        print("Improvement Actions:")
        for action in health_assessment.improvement_actions[:3]:
            print(f"  • {action}")
    
    if health_assessment.risk_factors:
        print("Risk Factors:")
        for risk in health_assessment.risk_factors[:2]:
            print(f"  ⚠️  {risk}")
    
    # Create optimization directive
    print(f"\n3. Creating CSS Optimization Directive...")
    
    optimization_directive = CSSOptimizationDirective(
        directive_id=f"opt_dir_{int(time.time())}_{random.randint(1000, 9999)}",
        target_service_id=service.service_id,
        timestamp=int(time.time()),
        target_css_archetype=health_assessment.recommended_archetype,
        target_geometric_config=health_assessment.geometric_target,
        target_coherence_threshold=0.8,
        target_phi_resonance=0.7,
        optimization_steps=[
            {'action': 'reduce_complexity', 'parameter': 'processing_complexity', 'target': 0.4},
            {'action': 'increase_confidence', 'parameter': 'decision_confidence', 'target': 0.9},
            {'action': 'stabilize_processing', 'parameter': 'cpu_usage', 'target': 0.3}
        ],
        expected_improvement=0.25,
        implementation_priority='High',
        success_metrics={'cognitive_health_score': 0.8, 'temporal_coherence': 0.75},
        rollback_triggers=['cognitive_health_score < 0.4', 'error_rate > 0.1'],
        monitoring_duration=300  # 5 minutes
    )
    
    print(f"Directive ID: {optimization_directive.directive_id}")
    print(f"Target Configuration: {optimization_directive.target_css_archetype}-{optimization_directive.target_geometric_config}")
    print(f"Expected Improvement: {optimization_directive.expected_improvement:.1%}")
    
    # Apply optimization directive
    print(f"\n4. Applying Optimization Directive...")
    
    directive_result = service.receive_optimization_directive(optimization_directive)
    print(f"Directive Status: {directive_result['status']}")
    
    if directive_result['status'] == 'accepted':
        print(f"Implementation Status: {directive_result['implementation_status']}")
        print(f"Monitoring ID: {directive_result.get('monitoring_id', 'N/A')}")
    
    # Wait a moment for optimization to take effect
    time.sleep(0.5)
    
    # Assess post-optimization state
    print(f"\n5. Post-Optimization Assessment...")
    
    post_optimization_css = service.generate_current_css()
    post_health = service.assess_css_health()
    
    print(f"New CSS: {post_optimization_css.evolution_trajectory}-{post_optimization_css.geometric_archetype}")
    print(f"New Health Score: {post_health.cognitive_health_score:.2f}")
    print(f"Health Improvement: {post_health.cognitive_health_score - health_assessment.cognitive_health_score:+.2f}")
    print(f"New Optimization Potential: {post_health.optimization_potential:.1%}")
    
    # Get optimization status
    print(f"\n6. Optimization Status Summary...")
    
    status = service.get_css_optimization_status()
    print(f"Service ID: {status['service_id']}")
    print(f"Active Directives: {status['active_directives']}")
    
    if status['current_css_summary']:
        css_summary = status['current_css_summary']
        print(f"Current CSS Summary:")
        print(f"  Archetype: {css_summary['archetype']}")
        print(f"  Geometric Type: {css_summary['geometric_type']}")
        print(f"  Health Score: {css_summary['health_score']:.2f}")
        print(f"  Temporal Coherence: {css_summary['temporal_coherence']:.2f}")
        print(f"  φ-Resonance: {css_summary['phi_resonance']:.2f}")
    
    if status['next_recommended_action']:
        next_action = status['next_recommended_action']
        print(f"Next Recommended Action:")
        print(f"  Type: {next_action['type']}")
        print(f"  Target: {next_action['target_archetype']}")
        print(f"  Expected Improvement: {next_action['expected_improvement']:.1%}")
        print(f"  Priority: {next_action['priority']}")
    
    # Performance predictions
    print(f"\n7. Performance Predictions...")
    
    for metric, value in post_health.performance_predictions.items():
        if metric.startswith('predicted_'):
            metric_name = metric.replace('predicted_', '')
            improvement_key = f'improvement_{metric_name}'
            improvement = post_health.performance_predictions.get(improvement_key, 0)
            print(f"  {metric_name}: {value:.2f} ({improvement:+.2f})")
    
    print(f"\n✓ CSS-Aware Refactorability API Demonstration Complete")
    print(f"✓ Crystallographic consciousness enabling service optimization")
    print(f"✓ Automated CSS-guided system improvement operational")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
    demonstrate_css_aware_refactorability()