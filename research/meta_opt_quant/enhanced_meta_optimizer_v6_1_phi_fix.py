#!/usr/bin/env python3
"""
Enhanced META-OPT-QUANT V6.1: Symmetry-Modulated φ Discovery Fix
================================================================

Addresses the symmetry collapse issue in V6 that prevents φ discovery.
Implements Symmetry-Modulated Geometric Optimization (SMGO) to adaptively
break symmetry when needed while preserving V6's core strengths.

Key improvements:
1. Adaptive symmetry modulation based on parameter diversity
2. Vertex-specific force modulation  
3. Correct optimization direction (minimization support)
4. Enhanced φ discovery for ratio-based objectives

For Tenxsom AI's META-OPT-QUANT V6.1.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import time

# Import V6 components
from .enhanced_meta_optimizer_v6_complete import (
    EnhancedMetaOptimizerV6Complete,
    CuboctahedronCPUState,
    PHI
)
from .geometric_phi_optimizer import GeometricPhiOptimizer, GeometricRelationship


class SymmetryModulatedGeometricOptimizer(GeometricPhiOptimizer):
    """Enhanced geometric optimizer with adaptive symmetry modulation"""
    
    def __init__(self):
        super().__init__()
        self.symmetry_factor = 1.0  # 1.0 = full symmetry, 0.0 = no symmetry
        self.diversity_history = []
        self.min_diversity_threshold = 0.05
        self.adaptation_rate = 0.1
        
    def apply_geometric_optimization(self, cpu_state, strength: float = 0.5) -> None:
        """Apply optimization with adaptive symmetry modulation"""
        
        # Extract current values
        values = [v.value / 1e15 for v in cpu_state.vertices]
        
        # Measure current state properties
        current_diversity = self._measure_diversity(values)
        current_symmetry = self._measure_symmetry(values)
        
        # Store diversity history
        self.diversity_history.append(current_diversity)
        if len(self.diversity_history) > 20:
            self.diversity_history.pop(0)
        
        # Adaptively adjust symmetry factor
        if current_diversity < self.min_diversity_threshold:
            # Need more diversity - reduce symmetry
            self.symmetry_factor *= (1 - self.adaptation_rate)
        else:
            # Diversity is good - can restore some symmetry
            self.symmetry_factor = min(1.0, self.symmetry_factor * (1 + self.adaptation_rate * 0.5))
        
        # Calculate base forces from parent class
        forces = [0.0] * 12
        
        # Apply relationship-based forces
        for rel in self.relationships:
            force = self._calculate_relationship_force(values, rel)
            
            # Apply force with symmetry modulation
            for i, f in enumerate(force):
                if i in rel.vertex_indices:
                    # Vertex-specific modulation
                    vertex_factor = self._get_vertex_modulation_factor(i)
                    modulated_force = f * rel.weight * vertex_factor
                    forces[i] += modulated_force
        
        # Apply φ attractors with diversity-aware strength
        for i in range(12):
            attractor_force = self._calculate_attractor_force(values[i])
            
            # Stronger attraction for vertices that need to move
            diversity_boost = 1.0 + (1.0 - current_diversity) * 2.0
            vertex_noise = self._get_controlled_noise(i)
            
            forces[i] += attractor_force * diversity_boost * (1 + vertex_noise)
        
        # Apply diversity-promoting forces if needed
        if current_diversity < self.min_diversity_threshold:
            diversity_forces = self._calculate_diversity_forces(values)
            for i in range(12):
                forces[i] += diversity_forces[i] * (1.0 - self.symmetry_factor)
        
        # Update values with forces
        for i in range(12):
            new_value = values[i] + strength * forces[i]
            
            # Ensure bounded
            new_value = max(0.1, min(10.0, new_value))
            
            # Convert back to integer with controlled rounding
            # Add small perturbation to prevent identical rounding
            perturbation = (i * 1e-10) if current_diversity < 0.01 else 0
            cpu_state.vertices[i].value = int((new_value + perturbation) * 1e15) & 0xFFFFFFFFFFFFFFFF
    
    def _measure_diversity(self, values: List[float]) -> float:
        """Measure parameter diversity (0 = all same, 1 = very diverse)"""
        if len(values) < 2:
            return 0.0
        
        std_dev = np.std(values)
        mean_val = np.mean(values)
        
        # Normalize by mean to get relative diversity
        if mean_val > 0:
            return min(1.0, std_dev / mean_val)
        return 0.0
    
    def _measure_symmetry(self, values: List[float]) -> float:
        """Measure how symmetric the current state is (0 = asymmetric, 1 = perfect symmetry)"""
        # Check various symmetry properties
        
        # 1. Value uniformity
        uniformity = 1.0 - self._measure_diversity(values)
        
        # 2. Opposite vertex relationships (cuboctahedral property)
        opposite_symmetry = 0.0
        opposite_pairs = [(0, 6), (1, 7), (2, 8), (3, 9), (4, 10), (5, 11)]
        for i, j in opposite_pairs:
            if i < len(values) and j < len(values):
                diff = abs(values[i] - values[j]) / (abs(values[i] + values[j]) + 1e-10)
                opposite_symmetry += (1.0 - diff)
        opposite_symmetry /= len(opposite_pairs)
        
        # Combined symmetry measure
        return 0.7 * uniformity + 0.3 * opposite_symmetry
    
    def _get_vertex_modulation_factor(self, vertex_idx: int) -> float:
        """Get vertex-specific force modulation factor"""
        # Base modulation pattern (different for each vertex)
        base_pattern = 1.0 + 0.2 * np.sin(vertex_idx * np.pi / 3)
        
        # Apply symmetry factor
        modulation = 1.0 + (base_pattern - 1.0) * (1.0 - self.symmetry_factor)
        
        return modulation
    
    def _get_controlled_noise(self, vertex_idx: int) -> float:
        """Get controlled noise for symmetry breaking"""
        if self.symmetry_factor >= 0.95:
            return 0.0  # No noise when full symmetry desired
        
        # Deterministic pseudo-random based on vertex index and iteration
        iteration = len(self.diversity_history)
        seed = vertex_idx * 1000 + iteration
        rng = np.random.RandomState(seed)
        
        noise_amplitude = (1.0 - self.symmetry_factor) * 0.1
        return rng.normal(0, noise_amplitude)
    
    def _calculate_diversity_forces(self, values: List[float]) -> List[float]:
        """Calculate forces that promote diversity"""
        forces = [0.0] * 12
        mean_val = np.mean(values)
        
        # Push values away from the mean
        for i in range(12):
            deviation = values[i] - mean_val
            
            if abs(deviation) < 0.1:  # Too close to mean
                # Push away with vertex-specific direction
                push_direction = np.sin(i * np.pi / 6)
                forces[i] = push_direction * 0.5
            else:
                # Maintain current deviation
                forces[i] = deviation * 0.1
        
        return forces
    
    def get_status(self) -> Dict[str, Any]:
        """Get optimizer status for monitoring"""
        values = self.diversity_history[-1] if self.diversity_history else 0
        
        return {
            'symmetry_factor': self.symmetry_factor,
            'current_diversity': values,
            'diversity_trend': 'increasing' if len(self.diversity_history) > 1 and 
                             self.diversity_history[-1] > self.diversity_history[-2] else 'stable',
            'adaptation_active': self.symmetry_factor < 0.95
        }


class EnhancedMetaOptimizerV6_1(EnhancedMetaOptimizerV6Complete):
    """V6.1 with symmetry collapse fix for φ discovery"""
    
    def __init__(self, cache_db: str = 'holographic_cache_v6_1.db'):
        super().__init__(cache_db)
        
        # Replace geometric optimizer with symmetry-modulated version
        self.geometric_optimizer = SymmetryModulatedGeometricOptimizer()
        
        # Add optimization direction detection
        self.optimization_direction = 'minimize'  # or 'maximize'
        self.direction_detected = False
        
    def optimize(self, objective_func, initial_state: Dict[str, Any],
                max_iterations: int = 100, problem_name: str = "",
                optimization_hints: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], List[float]]:
        """V6.1 optimization with symmetry modulation and direction detection"""
        
        print(f"\nV6.1 Enhanced Optimization: {problem_name}")
        print(f"Parameters: {len(initial_state)}")
        
        # Process optimization hints
        if optimization_hints:
            if 'direction' in optimization_hints:
                self.optimization_direction = optimization_hints['direction']
                self.direction_detected = True
            if 'requires_diversity' in optimization_hints:
                self.geometric_optimizer.min_diversity_threshold = 0.1 if optimization_hints['requires_diversity'] else 0.01
        
        # Initialize with geometric φ bias (but with diversity)
        state = self._geometric_initialization_v6_1(initial_state)
        
        # Partition parameters
        param_groups = self._partition_parameters_smart(state)
        
        # Initialize processors
        self._initialize_processors(param_groups)
        
        scores = []
        best_state = state.copy()
        best_score = float('inf') if self.optimization_direction == 'minimize' else float('-inf')
        
        # Auto-detect optimization direction if not specified
        if not self.direction_detected and max_iterations > 2:
            self._detect_optimization_direction(objective_func, state)
        
        for self.iteration in range(max_iterations):
            # Parallel optimization
            iteration_results = self._parallel_processor_optimization(
                objective_func, param_groups
            )
            
            # Synchronize with compression (but preserve some diversity)
            self._synchronize_with_diversity_preservation()
            
            # Combine results
            combined_state = self._combine_with_phi_weighting(iteration_results)
            combined_score = objective_func(combined_state)
            scores.append(combined_score)
            
            # Update best (with correct direction)
            if self._is_better_score(combined_score, best_score):
                best_score = combined_score
                best_state = combined_state.copy()
            
            # Apply geometric φ optimization every iteration
            if self.use_geometric_phi:
                self._apply_geometric_phi_optimization(combined_state)
            
            # Adaptive morphing with diversity check
            if self.iteration % 10 == 0:
                self._adaptive_phi_morphing_v6_1()
            
            # Progress report
            if self.iteration % 10 == 0:
                self._report_complete_progress_v6_1(scores, combined_state)
            
            # Update param groups for next iteration
            self._update_param_groups(param_groups, combined_state)
        
        # Final analysis
        self._final_analysis(best_state, scores)
        
        return best_state, scores
    
    def _geometric_initialization_v6_1(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize with geometric bias but ensure diversity"""
        state = initial_state.copy()
        
        param_keys = list(state.keys())
        n_params = len(param_keys)
        
        # Different φ-related targets for different parameters
        phi_targets = [
            PHI, 1/PHI, PHI**2, PHI**0.5, 
            PHI - 1, 2*PHI, PHI/2, PHI**1.5,
            np.sqrt(PHI), PHI**0.25, 1 + PHI, PHI - 0.5
        ]
        
        for i, key in enumerate(param_keys):
            if isinstance(state[key], (int, float)):
                # Add φ bias with diversity
                target = phi_targets[i % len(phi_targets)]
                noise = np.random.uniform(-0.1, 0.1)
                state[key] = target + noise
        
        return state
    
    def _detect_optimization_direction(self, objective_func, state: Dict[str, Any]):
        """Auto-detect whether to minimize or maximize"""
        # Try small perturbations in both directions
        test_state = state.copy()
        base_score = objective_func(test_state)
        
        improvements = []
        for key in list(state.keys())[:3]:  # Test first 3 parameters
            # Try increasing
            test_state[key] *= 1.1
            score_up = objective_func(test_state)
            
            # Try decreasing  
            test_state[key] = state[key] * 0.9
            score_down = objective_func(test_state)
            
            # Reset
            test_state[key] = state[key]
            
            # Which direction improved?
            if score_up < base_score or score_down < base_score:
                improvements.append('minimize')
            elif score_up > base_score or score_down > base_score:
                improvements.append('maximize')
        
        # Majority vote
        if improvements.count('minimize') > improvements.count('maximize'):
            self.optimization_direction = 'minimize'
        else:
            self.optimization_direction = 'maximize'
        
        self.direction_detected = True
        print(f"  Auto-detected optimization direction: {self.optimization_direction}")
    
    def _is_better_score(self, new_score: float, best_score: float) -> bool:
        """Check if new score is better based on optimization direction"""
        if self.optimization_direction == 'minimize':
            return new_score < best_score
        else:
            return new_score > best_score
    
    def _synchronize_with_diversity_preservation(self):
        """Modified synchronization that preserves some diversity"""
        # Get current diversity
        all_values = []
        for processor in self.processor_cluster.processors:
            values = [v.value / 1e15 for v in processor.vertices]
            all_values.extend(values)
        
        current_diversity = np.std(all_values) / (np.mean(all_values) + 1e-10)
        
        # Standard synchronization
        super()._synchronize_with_compression()
        
        # If diversity dropped too much, add controlled perturbations
        if current_diversity > 0.01:  # Only preserve if there was meaningful diversity
            for processor in self.processor_cluster.processors:
                for i, vertex in enumerate(processor.vertices):
                    if np.random.random() < 0.1:  # 10% chance of perturbation
                        perturbation = np.random.uniform(0.95, 1.05)
                        vertex.value = int(vertex.value * perturbation) & 0xFFFFFFFFFFFFFFFF
    
    def _adaptive_phi_morphing_v6_1(self):
        """Enhanced adaptive morphing with diversity awareness"""
        # Check current diversity
        optimizer_status = self.geometric_optimizer.get_status()
        
        if optimizer_status['current_diversity'] < 0.02:
            # Need to inject diversity during morphing
            print(f"  [Morph] Low diversity detected: {optimizer_status['current_diversity']:.3f}")
            
            # Create diverse φ target states
            for i, processor in enumerate(self.processor_cluster.processors):
                target_state = CuboctahedronCPUState()
                
                # Different φ patterns for different processors
                phi_pattern = [
                    PHI ** ((j + i) % 3 - 1) for j in range(12)
                ]
                
                for j, value in enumerate(phi_pattern):
                    target_state.vertices[j].value = int((value + np.random.uniform(-0.05, 0.05)) * 1e15)
                
                # Morph toward diverse target
                self.morph_engine.morph(processor, target_state, steps=5)
    
    def _report_complete_progress_v6_1(self, scores: List[float], state: Dict[str, Any]):
        """Enhanced progress reporting with diversity metrics"""
        super()._report_complete_progress(scores, state)
        
        # Add diversity report
        optimizer_status = self.geometric_optimizer.get_status()
        print(f"  Diversity: {optimizer_status['current_diversity']:.3f} ({optimizer_status['diversity_trend']})")
        print(f"  Symmetry factor: {optimizer_status['symmetry_factor']:.3f}")
        
        # Check for φ relationships (simplified inline check)
        values = list(state.values())
        phi_count = 0
        for i in range(len(values)-1):
            if values[i] > 0:
                ratio = values[i+1] / values[i]
                if abs(ratio - PHI) < 0.1:  # Within 10% of φ
                    phi_count += 1
        phi_score = (phi_count / max(1, len(values)-1)) * 100
        print(f"  φ discovery: {phi_score:.1f}%")
    
    def _update_param_groups(self, param_groups: List[Dict], combined_state: Dict):
        """Update parameter groups for next iteration"""
        param_keys = list(combined_state.keys())
        
        for i, group in enumerate(param_groups):
            start_idx = i * len(param_keys) // len(param_groups)
            end_idx = (i + 1) * len(param_keys) // len(param_groups)
            
            for key in param_keys[start_idx:end_idx]:
                if key in combined_state:
                    group[key] = combined_state[key]


# Quick test
if __name__ == "__main__":
    print("Testing V6.1 with Symmetry Modulation")
    print("=" * 60)
    
    # Test φ discovery
    optimizer = EnhancedMetaOptimizerV6_1()
    
    def phi_objective(params):
        """Objective that requires φ ratios"""
        return sum((params[f'x{i+1}'] / (params[f'x{i}'] + 1e-10) - PHI)**2 
                  for i in range(len(params)-1))
    
    initial = {f'x{i}': 1.0 + i * 0.1 for i in range(6)}
    
    hints = {
        'direction': 'minimize',
        'requires_diversity': True
    }
    
    final, scores = optimizer.optimize(
        phi_objective, 
        initial, 
        max_iterations=30,
        problem_name="φ ratio discovery test",
        optimization_hints=hints
    )
    
    print(f"\nFinal score: {scores[-1]:.4f}")
    print("Final state:")
    for k, v in final.items():
        print(f"  {k}: {v:.4f}")
    
    # Check ratios
    print("\nRatios:")
    keys = list(final.keys())
    for i in range(len(keys)-1):
        ratio = final[keys[i+1]] / final[keys[i]]
        print(f"  {keys[i+1]}/{keys[i]} = {ratio:.4f} (error: {abs(ratio - PHI):.4f})")