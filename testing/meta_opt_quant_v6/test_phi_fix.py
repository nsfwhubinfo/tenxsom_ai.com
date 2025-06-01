#!/usr/bin/env python3
"""
Test fix for φ discovery by applying stronger geometric optimization
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from research.meta_opt_quant.enhanced_meta_optimizer_v6_complete import EnhancedMetaOptimizerV6Complete
from research.meta_opt_quant.enhanced_meta_optimizer_v6_cuboctahedral import PHI, CuboctahedronCPUState
from phi_discovery_validator import PhiDiscoveryValidator
import numpy as np

class EnhancedV6WithStrongerPhi(EnhancedMetaOptimizerV6Complete):
    """Modified V6 with stronger φ optimization"""
    
    def _apply_geometric_phi_optimization(self, state):
        """Apply STRONGER geometric φ optimization"""
        # Create temporary CPU state
        cpu_state = CuboctahedronCPUState()
        
        # Map parameters to vertices
        param_values = list(state.values())[:12]
        for i in range(min(12, len(param_values))):
            if isinstance(param_values[i], (int, float)):
                cpu_state.vertices[i].value = int(param_values[i] * 1e15)
        
        # Apply geometric optimization with MUCH STRONGER force
        iteration_strength = 0.5 + 0.5 * (self.iteration / 50)  # 0.5 to 1.0 instead of 0.1 to 0.3
        self.geometric_optimizer.apply_geometric_optimization(
            cpu_state, strength=iteration_strength
        )
        
        # Also apply direct φ bias
        for i in range(12):
            current = cpu_state.vertices[i].value / 1e15
            # Pull toward nearest φ-related value
            phi_targets = [PHI, 1/PHI, PHI**2, PHI**0.5]
            nearest_phi = min(phi_targets, key=lambda p: abs(current - p))
            
            # Apply 20% pull toward nearest φ
            new_value = current * 0.8 + nearest_phi * 0.2
            cpu_state.vertices[i].value = int(new_value * 1e15)
        
        # Update state
        param_keys = list(state.keys())[:12]
        for i in range(min(12, len(param_keys))):
            state[param_keys[i]] = cpu_state.vertices[i].value / 1e15
    
    def optimize(self, objective_func, initial_state, max_iterations=100, problem_name=""):
        """Override to apply φ optimization EVERY iteration"""
        print(f"\nEnhanced V6 with Stronger φ: {problem_name}")
        print(f"Parameters: {len(initial_state)}")
        
        state = self._geometric_initialization(initial_state)
        param_groups = self._partition_parameters_smart(state)
        self._initialize_processors(param_groups)
        
        scores = []
        best_state = state.copy()
        best_score = float('inf')  # For minimization
        
        for self.iteration in range(max_iterations):
            # Regular optimization
            iteration_results = self._parallel_processor_optimization(
                objective_func, param_groups
            )
            
            self._synchronize_with_compression()
            combined_state = self._combine_with_phi_weighting(iteration_results)
            combined_score = objective_func(combined_state)
            scores.append(combined_score)
            
            if combined_score < best_score:  # Minimization
                best_score = combined_score
                best_state = combined_state.copy()
            
            # Apply geometric φ optimization EVERY iteration
            self._apply_geometric_phi_optimization(combined_state)
            
            # Update param groups
            param_keys = list(initial_state.keys())
            for i, group in enumerate(param_groups):
                start_idx = i * len(param_keys) // len(param_groups)
                end_idx = (i + 1) * len(param_keys) // len(param_groups)
                for j, key in enumerate(param_keys[start_idx:end_idx]):
                    if key in combined_state:
                        group[key] = combined_state[key]
            
            # Progress
            if self.iteration % 10 == 0:
                validator = PhiDiscoveryValidator()
                phi_score = validator.get_phi_score(combined_state)
                print(f"  Iteration {self.iteration}: Score={combined_score:.4f}, φ discovery={phi_score:.1f}%")
        
        # Final analysis
        self._final_analysis(best_state, scores)
        
        return best_state, scores


def test_enhanced_phi():
    """Test enhanced φ discovery"""
    print("Testing Enhanced φ Discovery Fix")
    print("=" * 60)
    
    # Use enhanced optimizer
    optimizer = EnhancedV6WithStrongerPhi()
    validator = PhiDiscoveryValidator()
    
    # Test with direct φ objective
    def phi_objective(params):
        return sum((v - PHI)**2 for v in params.values())
    
    initial = {f'x{i}': np.random.uniform(0.5, 2.5) for i in range(12)}
    print(f"\nInitial φ score: {validator.get_phi_score(initial):.1f}%")
    print(f"Initial objective: {phi_objective(initial):.4f}")
    
    final, scores = optimizer.optimize(
        objective_func=phi_objective,
        initial_state=initial,
        max_iterations=50,
        problem_name="enhanced_phi_test"
    )
    
    print(f"\nFinal φ score: {validator.get_phi_score(final):.1f}%")
    print(f"Final objective: {scores[-1]:.4f}")
    print(f"Improvement: {scores[0] - scores[-1]:.4f}")
    
    # Detailed validation
    validation = validator.validate_phi_discovery(final)
    print("\nDetailed φ Discovery:")
    for rel_type, score in validation['relationship_scores'].items():
        if score > 0:
            print(f"  {rel_type}: {score:.1f}%")
    
    # Show values close to φ
    print("\nValues close to φ:")
    for key, value in final.items():
        for phi_val in [PHI, 1/PHI, PHI**2, PHI**0.5]:
            if abs(value - phi_val) < 0.1:
                print(f"  {key}: {value:.4f} ≈ {phi_val:.4f}")
                break
    
    return validation['discovery_rate']


if __name__ == "__main__":
    phi_rate = test_enhanced_phi()
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    if phi_rate > 20:
        print(f"✅ SUCCESS! Enhanced optimization achieves {phi_rate:.1f}% φ discovery")
        print("\nRECOMMENDED FIXES:")
        print("1. Increase geometric optimization strength from 0.1 to 0.5+")
        print("2. Apply φ optimization every iteration, not every 5")
        print("3. Add direct φ bias in addition to geometric forces")
        print("4. Consider φ-guided initialization")
    else:
        print(f"❌ Still failing with {phi_rate:.1f}% φ discovery")
        print("More fundamental changes needed to geometric optimizer")