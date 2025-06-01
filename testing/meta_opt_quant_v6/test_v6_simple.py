#!/usr/bin/env python3
"""
Simple Test for V6 Implementation
=================================

Basic test to verify V6 components work correctly.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import numpy as np
from research.meta_opt_quant.enhanced_meta_optimizer_v6_complete import (
    EnhancedMetaOptimizerV6Complete
)
from research.meta_opt_quant.oh_symmetry_group import OhSymmetryGroup
from research.meta_opt_quant.enhanced_metrological_engine import EnhancedMetrologicalEngine
from research.meta_opt_quant.geometric_phi_optimizer import GeometricPhiOptimizer
from research.meta_opt_quant.enhanced_meta_optimizer_v6_cuboctahedral import (
    CuboctahedronCPUState, PHI
)

def simple_sphere(params):
    """Simple sphere function for testing"""
    return sum(v**2 for v in params.values())

def rosenbrock(params):
    """Rosenbrock function"""
    values = list(params.values())
    total = 0.0
    for i in range(len(values) - 1):
        total += 100 * (values[i+1] - values[i]**2)**2 + (1 - values[i])**2
    return total

def main():
    print("V6 Simple Test Suite")
    print("===================\n")
    
    # Test 1: Oh Symmetry Group
    print("Test 1: Oh Symmetry Group")
    oh_group = OhSymmetryGroup()
    print(f"Number of operations: {len(oh_group.operations)}")
    print(f"Identity check: {np.allclose(oh_group.operations[0].matrix, np.eye(3))}")
    
    # Test 2: Compression
    print("\nTest 2: Metrological Engine")
    engine = EnhancedMetrologicalEngine()
    
    # Create a symmetric state
    state = CuboctahedronCPUState()
    # Set values for some vertices
    state.set_register('RAX', int(PHI * 1000))
    state.set_register('RBX', int(PHI * 1000))
    
    compressed = engine.compress_state(state)
    decompressed = engine.decompress_state(compressed)
    
    print(f"Original size: {len(state.to_bytes())} bytes")
    print(f"Compressed size: {len(compressed)} bytes")
    print(f"Compression ratio: {len(state.to_bytes()) / len(compressed):.1f}x")
    
    # Test 3: Geometric Optimizer
    print("\nTest 3: Geometric Phi Optimizer")
    optimizer = GeometricPhiOptimizer()
    
    initial_state = CuboctahedronCPUState()
    # Initialize with random values
    import random
    for reg in ['RAX', 'RBX', 'RCX', 'RDX']:
        initial_state.set_register(reg, random.randint(0, 10000))
    
    initial_score = optimizer._compute_phi_score(initial_state)
    
    optimized_state = initial_state.copy()
    optimizer.apply_geometric_optimization(optimized_state, strength=0.1)
    
    final_score = optimizer._compute_phi_score(optimized_state)
    
    print(f"Initial φ score: {initial_score:.3f}")
    print(f"Final φ score: {final_score:.3f}")
    print(f"Improvement: {final_score - initial_score:.3f}")
    
    # Test 4: Complete Optimizer with simple function
    print("\nTest 4: Complete V6 Optimizer")
    v6_optimizer = EnhancedMetaOptimizerV6Complete()
    
    # Test with sphere function
    print("\nOptimizing sphere function (12 parameters):")
    final_state, scores = v6_optimizer.optimize(
        objective_func=simple_sphere,
        n_params=12,
        bounds=[(-5, 5)] * 12,
        max_iterations=50
    )
    
    print(f"Final score: {scores[-1]:.6f}")
    print(f"Score improvement: {scores[0] - scores[-1]:.6f}")
    
    # Count φ discoveries
    phi_count = 0
    # Check the actual parameter values returned
    for key, value in v6_optimizer.best_params.items():
        if abs(value - PHI) < 0.01 or abs(value - 1/PHI) < 0.01:
            phi_count += 1
    
    print(f"φ discoveries: {phi_count}/12")
    
    # Test with Rosenbrock
    print("\nOptimizing Rosenbrock function (12 parameters):")
    final_state2, scores2 = v6_optimizer.optimize(
        objective_func=rosenbrock,
        n_params=12,
        bounds=[(-2, 2)] * 12,
        max_iterations=100
    )
    
    print(f"Final score: {scores2[-1]:.6f}")
    print(f"Score improvement: {scores2[0] - scores2[-1]:.6f}")
    
    # Check compression statistics
    print("\nCompression Statistics:")
    comp_stats = v6_optimizer.compression_stats
    print(f"Average compression: {comp_stats['average']:.1f}x")
    print(f"Maximum compression: {comp_stats['max']:.1f}x")
    
    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    main()