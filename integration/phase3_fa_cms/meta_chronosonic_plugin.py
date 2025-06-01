#!/usr/bin/env python3
"""
META-CHRONOSONIC Plugin for FA-CMS
==================================

Adapts the META-CHRONOSONIC bridge as a plugin for the FA-CMS framework.
Provides seamless integration of V6.1 optimization and CHRONOSONIC consciousness
dynamics within the fractal algebra system.

Key Features:
- Wraps existing META-CHRONOSONIC bridge
- Translates between bridge and plugin interfaces
- Maintains performance optimizations
- Provides unified state management

For Tenxsom AI's FA-CMS integration.
"""

import numpy as np
from typing import Dict, List, Any, Optional, Callable
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from integration.meta_chronosonic_bridge import (
    MetaChronosonicBridge,
    IntegrationConfig,
    PHI
)

from fa_plugin_interface import (
    FAPlugin,
    PluginConfig,
    UnifiedState,
    ChakraState,
    FAMessage,
    MessageType,
    PluginStatus
)


class MetaChronosonicPlugin(FAPlugin):
    """META-CHRONOSONIC plugin adapter for FA-CMS"""
    
    def __init__(self, config: PluginConfig, bridge_config: Optional[IntegrationConfig] = None):
        super().__init__(config)
        
        # Bridge configuration
        self.bridge_config = bridge_config or IntegrationConfig(
            v6_max_iterations=100,
            cs_use_simplified=False,  # Use full 7-chakra system
            param_mapping_mode="geometric",
            objective_weights={
                'optimization': 0.4,
                'phi_discovery': 0.3,
                'coherence': 0.3
            }
        )
        
        self.bridge = None
        self.optimization_cache = {}
        self.last_optimization_time = 0
        self.optimization_interval = 1.0  # Minimum seconds between optimizations
        
    def initialize(self) -> bool:
        """Initialize META-CHRONOSONIC bridge"""
        try:
            print(f"Initializing META-CHRONOSONIC Plugin...")
            
            # Create bridge instance
            self.bridge = MetaChronosonicBridge(self.bridge_config)
            
            # Warm up the systems
            self._warmup()
            
            print(f"✓ META-CHRONOSONIC Plugin initialized")
            return True
            
        except Exception as e:
            print(f"Failed to initialize META-CHRONOSONIC Plugin: {e}")
            return False
    
    def process(self, state: UnifiedState) -> UnifiedState:
        """Process state through META-CHRONOSONIC optimization"""
        start_time = time.time()
        
        try:
            # Extract optimization parameters
            if not state.optimization_params:
                # No parameters to optimize, just update consciousness state
                self._update_consciousness_state(state)
                self._update_metrics(time.time() - start_time)
                return state
            
            # Check if we should run optimization
            if time.time() - self.last_optimization_time < self.optimization_interval:
                # Too soon, just update consciousness
                self._update_consciousness_state(state)
                self._update_metrics(time.time() - start_time)
                return state
            
            # Create objective function based on state
            objective = self._create_objective_from_state(state)
            
            # Run optimization
            optimized_params, scores = self.bridge.optimize_integrated(
                objective,
                state.optimization_params,
                max_iterations=self.bridge_config.v6_max_iterations
            )
            
            # Update state with optimized parameters
            state.optimization_params = optimized_params
            
            # Extract consciousness metrics
            self._extract_consciousness_metrics(state)
            
            # Update metadata
            state.metadata['meta_chronosonic'] = {
                'optimization_improvement': (scores[0] - scores[-1]) / (scores[0] + 1e-10) * 100,
                'final_score': scores[-1],
                'iterations': len(scores),
                'phi_discovery': self._calculate_phi_discovery(optimized_params),
                'processing_time': time.time() - start_time
            }
            
            self.last_optimization_time = time.time()
            
            # Send update message
            self.send_message(FAMessage(
                source_id=self.id,
                target_id="broadcast",
                message_type=MessageType.EVENT,
                payload={
                    'event': 'optimization_complete',
                    'improvement': state.metadata['meta_chronosonic']['optimization_improvement'],
                    'phi_discovery': state.metadata['meta_chronosonic']['phi_discovery']
                }
            ))
            
        except Exception as e:
            print(f"Error in META-CHRONOSONIC processing: {e}")
            self._update_metrics(time.time() - start_time, error=True)
            
            # Send error message
            self.send_message(FAMessage(
                source_id=self.id,
                target_id="broadcast",
                message_type=MessageType.ERROR,
                payload={'error': str(e)}
            ))
            
            raise
        
        self._update_metrics(time.time() - start_time)
        return state
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get plugin metrics including bridge-specific data"""
        base_metrics = self.metrics.copy()
        
        # Add META-CHRONOSONIC specific metrics
        if self.bridge:
            base_metrics['bridge_metrics'] = {
                'total_optimizations': len(self.optimization_cache),
                'chakra_coherence': self.bridge.chakra_system.get_system_coherence(),
                'iam_coherence': self.bridge.iam_state.get_coherence(),
                'cache_size': len(self.optimization_cache)
            }
            
            # Get recent optimization history
            if self.bridge.metrics_history:
                recent = self.bridge.metrics_history[-10:]  # Last 10
                base_metrics['recent_scores'] = [m.get('total_score', 0) for m in recent]
        
        return base_metrics
    
    def shutdown(self):
        """Clean shutdown of META-CHRONOSONIC systems"""
        print(f"Shutting down META-CHRONOSONIC Plugin...")
        
        # Clear caches
        self.optimization_cache.clear()
        
        # Bridge cleanup (if needed)
        if self.bridge:
            # Save final state if needed
            pass
        
        print(f"✓ META-CHRONOSONIC Plugin shutdown complete")
    
    def _warmup(self):
        """Warm up the optimization and consciousness systems"""
        print("  Warming up systems...")
        
        # Simple test optimization
        def warmup_objective(params):
            return sum(v**2 for v in params.values())
        
        test_params = {'x': 1.0, 'y': 2.0, 'z': 3.0}
        
        try:
            self.bridge.optimize_integrated(
                warmup_objective,
                test_params,
                max_iterations=5
            )
            print("  ✓ Warmup complete")
        except Exception as e:
            print(f"  ⚠️ Warmup warning: {e}")
    
    def _create_objective_from_state(self, state: UnifiedState) -> Callable:
        """Create objective function based on current state"""
        
        # Check if we have fractal dimension target
        target_fractal = state.fractal_dimension
        
        # Check for coherence requirements
        if state.coherence_matrix is not None:
            target_coherence = np.mean(state.coherence_matrix)
        else:
            target_coherence = 0.8
        
        def unified_objective(params: Dict[str, Any]) -> float:
            """Objective that considers multiple state aspects"""
            
            # Base optimization term
            values = np.array(list(params.values()))
            base_score = np.sum(values**2)
            
            # Fractal dimension term
            if len(values) > 1:
                # Simple fractal dimension approximation
                sorted_values = np.sort(values)
                ratios = sorted_values[1:] / (sorted_values[:-1] + 1e-10)
                fractal_score = abs(np.mean(ratios) - target_fractal)
            else:
                fractal_score = 0
            
            # φ discovery term
            phi_score = 0
            for i in range(len(values) - 1):
                if values[i] > 0:
                    ratio = values[i+1] / values[i]
                    phi_score += (ratio - PHI)**2
            
            # Coherence term (penalize high variance)
            coherence_score = np.var(values)
            
            # Combined objective
            return (
                0.3 * base_score +
                0.2 * fractal_score +
                0.3 * phi_score +
                0.2 * coherence_score
            )
        
        return unified_objective
    
    def _update_consciousness_state(self, state: UnifiedState):
        """Update consciousness state without full optimization"""
        if not self.bridge:
            return
        
        # Sync chakra states
        if state.chakra_states:
            for i, chakra_state in enumerate(state.chakra_states):
                chakra_type = list(self.bridge.chakra_system.chakras.keys())[
                    i % len(self.bridge.chakra_system.chakras)
                ]
                
                # Update chakra in bridge
                self.bridge.chakra_system.update_state(
                    chakra_type,
                    frequency=chakra_state.frequency,
                    amplitude=chakra_state.amplitude,
                    phase=chakra_state.phase,
                    coherence=chakra_state.coherence
                )
        
        # Evolve consciousness systems
        for _ in range(10):
            self.bridge.chronosonic.evolve(dt=0.1)
    
    def _extract_consciousness_metrics(self, state: UnifiedState):
        """Extract consciousness metrics from bridge and update state"""
        if not self.bridge:
            return
        
        # Update chakra states
        updated_chakras = []
        for chakra_type, chakra in self.bridge.chakra_system.chakras.items():
            updated_chakras.append(ChakraState(
                type=chakra_type.value,
                frequency=chakra.current_frequency,
                amplitude=chakra.amplitude,
                phase=chakra.phase,
                coherence=chakra.coherence,
                active=chakra.active,
                modulation=(chakra.modulation_depth, chakra.modulation_frequency)
                if chakra.modulation_depth > 0 else None
            ))
        
        state.chakra_states = updated_chakras
        
        # Update coherence matrix
        freq_matrix = self.bridge.chakra_system.get_frequency_matrix()
        state.coherence_matrix = freq_matrix
        
        # Update quantum state from CHRONOSONIC
        if hasattr(self.bridge.chronosonic, 'quantum_state'):
            state.quantum_state = self.bridge.chronosonic.quantum_state.copy()
        
        # Calculate and update fractal dimension
        state.fractal_dimension = self._estimate_fractal_dimension(state.optimization_params)
    
    def _calculate_phi_discovery(self, params: Dict[str, Any]) -> float:
        """Calculate φ discovery percentage"""
        values = list(params.values())
        if len(values) < 2:
            return 0.0
        
        phi_count = 0
        total_pairs = 0
        
        for i in range(len(values) - 1):
            if values[i] > 0:
                ratio = values[i+1] / values[i]
                if abs(ratio - PHI) < 0.1:  # Within 10%
                    phi_count += 1
                total_pairs += 1
        
        return (phi_count / max(1, total_pairs)) * 100
    
    def _estimate_fractal_dimension(self, params: Dict[str, Any]) -> float:
        """Estimate fractal dimension from parameter distribution"""
        values = np.array(list(params.values()))
        
        if len(values) < 2:
            return 1.0
        
        # Box-counting approximation
        sorted_values = np.sort(values)
        
        # Calculate ratios at different scales
        scales = []
        for scale in [0.1, 0.5, 1.0, 2.0]:
            boxes = np.ceil((sorted_values - sorted_values.min()) / scale)
            unique_boxes = len(np.unique(boxes))
            if unique_boxes > 0:
                scales.append((scale, unique_boxes))
        
        if len(scales) >= 2:
            # Linear regression in log-log space
            log_scales = np.log([s[0] for s in scales])
            log_counts = np.log([s[1] for s in scales])
            
            # Simple linear fit
            slope = (log_counts[-1] - log_counts[0]) / (log_scales[-1] - log_scales[0])
            fractal_dim = -slope
            
            # Bound to reasonable range
            return np.clip(fractal_dim, 0.5, 3.0)
        
        return 1.618  # Default to φ


class SevenChakraExtension:
    """Extension module for full 7-chakra support"""
    
    @staticmethod
    def create_full_chakra_states() -> List[ChakraState]:
        """Create initial states for all 7 chakras"""
        chakra_data = [
            ("root", 256.0, "Muladhara"),
            ("sacral", 288.0, "Svadhisthana"),
            ("solar", 320.0, "Manipura"),
            ("heart", 341.3, "Anahata"),
            ("throat", 384.0, "Vishuddha"),
            ("third_eye", 426.7, "Ajna"),
            ("crown", 512.0, "Sahasrara")
        ]
        
        chakra_states = []
        for i, (chakra_type, frequency, sanskrit) in enumerate(chakra_data):
            # Create with harmonic relationships
            amplitude = 0.5 + 0.1 * np.sin(i * np.pi / 7)
            phase = i * np.pi / 7
            coherence = 0.7 + 0.1 * np.cos(i * np.pi / 3.5)
            
            chakra_states.append(ChakraState(
                type=chakra_type,
                frequency=frequency,
                amplitude=amplitude,
                phase=phase,
                coherence=coherence,
                active=True
            ))
        
        return chakra_states
    
    @staticmethod
    def calculate_chakra_hierarchy(chakra_states: List[ChakraState]) -> Dict[str, Any]:
        """Calculate hierarchical relationships between chakras"""
        hierarchy = {
            'levels': {},
            'connections': [],
            'overall_coherence': 0.0
        }
        
        # Group into levels
        levels = {
            'physical': chakra_states[:3],    # Root, Sacral, Solar
            'bridge': chakra_states[3:4],     # Heart
            'spiritual': chakra_states[4:]    # Throat, Third Eye, Crown
        }
        
        # Calculate inter-level coherence
        level_coherences = {}
        for level_name, level_chakras in levels.items():
            coherences = [c.coherence for c in level_chakras]
            level_coherences[level_name] = np.mean(coherences)
        
        hierarchy['levels'] = level_coherences
        
        # Calculate connections strength
        for i in range(len(chakra_states) - 1):
            connection_strength = (
                chakra_states[i].coherence * 
                chakra_states[i+1].coherence * 
                np.cos(chakra_states[i].phase - chakra_states[i+1].phase)
            )
            hierarchy['connections'].append({
                'from': chakra_states[i].type,
                'to': chakra_states[i+1].type,
                'strength': connection_strength
            })
        
        # Overall coherence
        hierarchy['overall_coherence'] = np.mean([c.coherence for c in chakra_states])
        
        return hierarchy


def demo_meta_chronosonic_plugin():
    """Demonstrate META-CHRONOSONIC plugin functionality"""
    print("META-CHRONOSONIC Plugin Demo")
    print("=" * 60)
    
    # Create plugin configuration
    plugin_config = PluginConfig(
        name="META-CHRONOSONIC",
        version="1.0.0",
        priority=8,  # High priority
        custom_params={
            'enable_7_chakra': True
        }
    )
    
    # Create plugin
    plugin = MetaChronosonicPlugin(plugin_config)
    
    # Initialize
    if not plugin.initialize():
        print("Failed to initialize plugin!")
        return
    
    # Create test state with 7 chakras
    test_state = UnifiedState(
        optimization_params={f'x{i}': 1.0 + i*0.5 for i in range(7)},
        chakra_states=SevenChakraExtension.create_full_chakra_states(),
        fractal_dimension=1.618
    )
    
    print("\nInitial state:")
    print(f"  Parameters: {len(test_state.optimization_params)}")
    print(f"  Chakras: {len(test_state.chakra_states)}")
    print(f"  Fractal dimension: {test_state.fractal_dimension}")
    
    # Process through plugin
    print("\nProcessing through META-CHRONOSONIC plugin...")
    processed_state = plugin.process(test_state)
    
    print("\nProcessed state:")
    print(f"  Parameters optimized: ✓")
    
    if 'meta_chronosonic' in processed_state.metadata:
        mc_data = processed_state.metadata['meta_chronosonic']
        print(f"  Optimization improvement: {mc_data['optimization_improvement']:.1f}%")
        print(f"  φ discovery: {mc_data['phi_discovery']:.1f}%")
        print(f"  Processing time: {mc_data['processing_time']:.2f}s")
    
    # Check chakra hierarchy
    hierarchy = SevenChakraExtension.calculate_chakra_hierarchy(processed_state.chakra_states)
    print(f"\nChakra hierarchy:")
    for level, coherence in hierarchy['levels'].items():
        print(f"  {level}: {coherence:.3f}")
    print(f"  Overall coherence: {hierarchy['overall_coherence']:.3f}")
    
    # Get metrics
    metrics = plugin.get_metrics()
    print(f"\nPlugin metrics:")
    print(f"  Processed count: {metrics['processed_count']}")
    print(f"  Error count: {metrics['error_count']}")
    
    if 'bridge_metrics' in metrics:
        bridge = metrics['bridge_metrics']
        print(f"  Chakra coherence: {bridge['chakra_coherence']:.3f}")
        print(f"  I_AM coherence: {bridge['iam_coherence']:.3f}")
    
    # Shutdown
    plugin.shutdown()
    
    print("\n✅ META-CHRONOSONIC plugin demo complete!")


if __name__ == "__main__":
    demo_meta_chronosonic_plugin()