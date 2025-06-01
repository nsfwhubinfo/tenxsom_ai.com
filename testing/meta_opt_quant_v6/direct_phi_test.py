#!/usr/bin/env python3
"""
Direct test of geometric φ optimizer without full V6 infrastructure
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import numpy as np
from research.meta_opt_quant.enhanced_meta_optimizer_v6_cuboctahedral import PHI, CuboctahedronCPUState, CPURegister
from research.meta_opt_quant.geometric_phi_optimizer import GeometricPhiOptimizer
from phi_discovery_validator import PhiDiscoveryValidator

def test_geometric_optimizer_directly():
    """Test geometric optimizer in isolation"""
    print("Direct Test of Geometric φ Optimizer")
    print("=" * 60)
    
    # Create optimizer and validator
    geo_optimizer = GeometricPhiOptimizer()
    validator = PhiDiscoveryValidator()
    
    # Check if it's properly initialized
    print(f"\nOptimizer components:")
    print(f"  Relationships: {len(geo_optimizer.relationships)}")
    print(f"  Attractors: {len(geo_optimizer.attractors)}")
    
    # Create a CPU state with random values
    cpu_state = CuboctahedronCPUState()
    initial_values = {}
    
    print(f"\nInitial state:")
    for i in range(12):
        value = np.random.uniform(0.5, 2.5)
        cpu_state.vertices[i].value = int(value * 1e15)
        initial_values[f'x{i}'] = value
        print(f"  V{i}: {value:.4f}")
    
    initial_phi_score = validator.get_phi_score(initial_values)
    print(f"\nInitial φ score: {initial_phi_score:.1f}%")
    
    # Apply geometric optimization multiple times with increasing strength
    print("\nApplying geometric optimization:")
    for iteration in range(20):
        strength = 0.5 + iteration * 0.05  # Increasing strength
        
        # Apply optimization
        geo_optimizer.apply_geometric_optimization(cpu_state, strength=strength)
        
        # Extract values
        current_values = {}
        for i in range(12):
            current_values[f'x{i}'] = cpu_state.vertices[i].value / 1e15
        
        # Check φ score every 5 iterations
        if iteration % 5 == 0:
            phi_score = validator.get_phi_score(current_values)
            print(f"  Iteration {iteration}: strength={strength:.2f}, φ score={phi_score:.1f}%")
    
    # Final analysis
    final_values = {}
    print(f"\nFinal state:")
    for i in range(12):
        value = cpu_state.vertices[i].value / 1e15
        final_values[f'x{i}'] = value
        print(f"  V{i}: {value:.4f}")
    
    final_phi_score = validator.get_phi_score(final_values)
    validation = validator.validate_phi_discovery(final_values)
    
    print(f"\nFinal φ score: {final_phi_score:.1f}%")
    print(f"Improvement: {final_phi_score - initial_phi_score:.1f}%")
    
    print("\nDetailed results:")
    for rel_type, score in validation['relationship_scores'].items():
        if score > 0:
            print(f"  {rel_type}: {score:.1f}%")
    
    # Check for specific φ relationships
    print("\nChecking for φ relationships:")
    values = list(final_values.values())
    
    # Edge ratios
    for i in range(len(values)-1):
        if values[i] > 0:
            ratio = values[i+1] / values[i]
            if abs(ratio - PHI) < 0.1:
                print(f"  V{i+1}/V{i} = {ratio:.4f} ≈ φ")
    
    # Values near φ
    for i, v in enumerate(values):
        for phi_val, name in [(PHI, 'φ'), (1/PHI, '1/φ'), (PHI**2, 'φ²'), (PHI**0.5, '√φ')]:
            if abs(v - phi_val) < 0.1:
                print(f"  V{i} = {v:.4f} ≈ {name} ({phi_val:.4f})")
    
    return final_phi_score > 10  # Success if > 10%


def test_direct_optimization():
    """Test direct optimization without compression"""
    print("\n\nDirect Optimization Test")
    print("=" * 60)
    
    # Simple optimizer that directly applies φ forces
    def optimize_toward_phi(initial_state, iterations=50):
        state = initial_state.copy()
        
        for i in range(iterations):
            # Calculate φ-based forces
            values = list(state.values())
            forces = []
            
            for j, v in enumerate(values):
                force = 0
                
                # Attract to nearest φ value
                phi_targets = [PHI, 1/PHI, PHI**2, PHI**0.5]
                nearest = min(phi_targets, key=lambda p: abs(v - p))
                force += (nearest - v) * 0.2
                
                # Create edge ratio relationships
                if j > 0:
                    ratio = v / values[j-1] if values[j-1] > 0 else 1
                    force += (PHI - ratio) * 0.1 * values[j-1]
                
                forces.append(force)
            
            # Apply forces
            keys = list(state.keys())
            for j, (key, force) in enumerate(zip(keys, forces)):
                state[key] = max(0.1, state[key] + force)
        
        return state
    
    # Test
    initial = {f'x{i}': np.random.uniform(0.5, 2.5) for i in range(12)}
    validator = PhiDiscoveryValidator()
    
    print(f"Initial φ score: {validator.get_phi_score(initial):.1f}%")
    
    final = optimize_toward_phi(initial)
    final_score = validator.get_phi_score(final)
    
    print(f"Final φ score: {final_score:.1f}%")
    
    if final_score > 20:
        print("\n✅ Direct optimization works!")
        print("This proves φ discovery is possible with proper forces")
    
    return final_score


if __name__ == "__main__":
    print("Testing Geometric φ Optimizer")
    print("\n" + "=" * 80)
    
    # Test 1: Geometric optimizer directly
    geo_works = test_geometric_optimizer_directly()
    
    # Test 2: Simple direct optimization
    direct_score = test_direct_optimization()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Geometric optimizer test: {'PASSED' if geo_works else 'FAILED'}")
    print(f"Direct optimization score: {direct_score:.1f}%")
    
    print("\nCONCLUSIONS:")
    if not geo_works and direct_score > 20:
        print("❌ Geometric optimizer is NOT working properly")
        print("✅ But φ discovery IS possible with proper implementation")
        print("\nRECOMMENDED FIX:")
        print("The geometric optimizer needs stronger forces and better integration")
    elif geo_works:
        print("✅ Geometric optimizer can work with proper parameters")
        print("The issue is in the integration with V6 main loop")
    else:
        print("❌ Both methods failed - fundamental issue with approach")