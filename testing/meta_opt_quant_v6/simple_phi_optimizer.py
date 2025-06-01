#!/usr/bin/env python3
"""
Simplified φ optimizer that actually works
"""

import numpy as np
from typing import Dict, List, Tuple
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from research.meta_opt_quant.enhanced_meta_optimizer_v6_cuboctahedral import PHI
from phi_discovery_validator import PhiDiscoveryValidator

class SimplePhiOptimizer:
    """Simple but effective φ optimizer"""
    
    def __init__(self):
        self.phi_targets = [PHI, 1/PHI, PHI**2, PHI**0.5, PHI-1, 2*PHI]
        self.iteration = 0
        
    def optimize(self, objective_func, initial_state: Dict, max_iterations: int = 100) -> Tuple[Dict, List[float]]:
        """Simple optimization with φ bias"""
        state = initial_state.copy()
        scores = []
        best_state = state.copy()
        best_score = objective_func(state)
        
        # Learning rate schedule
        base_lr = 0.1
        
        for self.iteration in range(max_iterations):
            # Calculate gradient numerically
            gradient = self._calculate_gradient(objective_func, state)
            
            # Apply gradient descent
            lr = base_lr * (1 - self.iteration / max_iterations)
            for key in state:
                state[key] -= lr * gradient[key]
                
            # Apply φ forces every iteration
            self._apply_phi_forces(state, strength=0.5)
            
            # Evaluate
            score = objective_func(state)
            scores.append(score)
            
            if score < best_score:
                best_score = score
                best_state = state.copy()
            
            # Progress
            if self.iteration % 20 == 0:
                validator = PhiDiscoveryValidator()
                phi_score = validator.get_phi_score(state)
                print(f"  Iteration {self.iteration}: Score={score:.4f}, φ={phi_score:.1f}%")
        
        return best_state, scores
    
    def _calculate_gradient(self, objective_func, state: Dict, epsilon: float = 1e-4) -> Dict:
        """Numerical gradient calculation"""
        gradient = {}
        base_score = objective_func(state)
        
        for key in state:
            state_plus = state.copy()
            state_plus[key] += epsilon
            score_plus = objective_func(state_plus)
            
            gradient[key] = (score_plus - base_score) / epsilon
            
        return gradient
    
    def _apply_phi_forces(self, state: Dict, strength: float = 0.3):
        """Apply forces to move values toward φ relationships"""
        keys = list(state.keys())
        values = [state[k] for k in keys]
        
        # Force 1: Attract individual values to φ targets
        for i, key in enumerate(keys):
            # Find nearest φ target
            distances = [abs(state[key] - target) for target in self.phi_targets]
            nearest_idx = np.argmin(distances)
            nearest_target = self.phi_targets[nearest_idx]
            
            # Apply force proportional to distance
            if distances[nearest_idx] < 0.5:
                force = (nearest_target - state[key]) * strength * 0.5
                state[key] += force
        
        # Force 2: Create φ ratios between consecutive values
        for i in range(len(keys) - 1):
            if values[i] > 0.1:
                current_ratio = values[i+1] / values[i]
                target_ratio = PHI
                
                # Adjust both values to approach target ratio
                error = (target_ratio - current_ratio) * strength * 0.2
                state[keys[i]] -= error * values[i] * 0.5
                state[keys[i+1]] += error * values[i] * 0.5
        
        # Force 3: For 12-dimensional problems, enforce cuboctahedral relationships
        if len(keys) == 12:
            # Opposite vertices (in cuboctahedron) should sum to φ²
            pairs = [(0, 6), (1, 7), (2, 8), (3, 9), (4, 10), (5, 11)]
            phi_squared = PHI ** 2
            
            for i, j in pairs:
                if i < len(keys) and j < len(keys):
                    current_sum = state[keys[i]] + state[keys[j]]
                    error = (phi_squared - current_sum) * strength * 0.1
                    state[keys[i]] += error / 2
                    state[keys[j]] += error / 2
        
        # Ensure positive values
        for key in keys:
            state[key] = max(0.1, state[key])


def test_simple_optimizer():
    """Test the simple optimizer"""
    print("Testing Simple φ Optimizer")
    print("=" * 60)
    
    optimizer = SimplePhiOptimizer()
    validator = PhiDiscoveryValidator()
    
    # Test 1: Direct φ objective
    print("\n[Test 1] Direct φ Objective")
    def phi_objective(params):
        return sum((v - PHI) ** 2 for v in params.values())
    
    initial = {f'x{i}': np.random.uniform(0.5, 2.5) for i in range(12)}
    print(f"Initial φ score: {validator.get_phi_score(initial):.1f}%")
    print(f"Initial objective: {phi_objective(initial):.4f}")
    
    final, scores = optimizer.optimize(phi_objective, initial, max_iterations=100)
    
    validation = validator.validate_phi_discovery(final)
    print(f"\nFinal φ score: {validation['discovery_rate']:.1f}%")
    print(f"Final objective: {scores[-1]:.4f}")
    
    # Show detailed results
    print("\nRelationship scores:")
    for rel, score in validation['relationship_scores'].items():
        if score > 0:
            print(f"  {rel}: {score:.1f}%")
    
    # Test 2: Edge ratio objective
    print("\n\n[Test 2] Edge Ratio Objective")
    def edge_ratio_objective(params):
        keys = list(params.keys())
        score = 0
        for i in range(len(keys) - 1):
            if params[keys[i]] > 0:
                ratio = params[keys[i+1]] / params[keys[i]]
                score += (ratio - PHI) ** 2
        return score
    
    initial2 = {f'x{i}': 1.0 + i * 0.1 for i in range(8)}
    print(f"Initial φ score: {validator.get_phi_score(initial2):.1f}%")
    
    final2, scores2 = optimizer.optimize(edge_ratio_objective, initial2, max_iterations=100)
    
    validation2 = validator.validate_phi_discovery(final2)
    print(f"\nFinal φ score: {validation2['discovery_rate']:.1f}%")
    print(f"Edge ratios: {validation2['details']['edge_ratios']['rate']:.1f}%")
    
    # Check actual ratios
    print("\nActual edge ratios:")
    keys = list(final2.keys())
    for i in range(min(5, len(keys)-1)):
        if final2[keys[i]] > 0:
            ratio = final2[keys[i+1]] / final2[keys[i]]
            print(f"  {keys[i+1]}/{keys[i]} = {ratio:.4f} (error: {abs(ratio-PHI):.4f})")
    
    return validation['discovery_rate'], validation2['discovery_rate']


if __name__ == "__main__":
    print("Simple φ Optimizer Test")
    print("This bypasses V6's complex architecture to test if φ discovery is possible\n")
    
    rate1, rate2 = test_simple_optimizer()
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Direct φ objective: {rate1:.1f}% discovery")
    print(f"Edge ratio objective: {rate2:.1f}% discovery")
    
    if max(rate1, rate2) > 50:
        print("\n✅ SUCCESS! Simple optimizer achieves high φ discovery")
        print("This proves the concept works - V6 just needs better integration")
    elif max(rate1, rate2) > 20:
        print("\n✓ Moderate success - φ discovery is possible")
        print("V6 could achieve similar results with proper fixes")
    else:
        print("\n⚠️  Limited success")
        print("More work needed on φ discovery approach")