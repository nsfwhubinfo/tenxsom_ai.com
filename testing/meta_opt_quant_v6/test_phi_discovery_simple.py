#!/usr/bin/env python3
"""
Simple test to verify φ discovery issue in V6
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from research.meta_opt_quant.enhanced_meta_optimizer_v6_complete import EnhancedMetaOptimizerV6Complete
from research.meta_opt_quant.enhanced_meta_optimizer_v6_cuboctahedral import PHI
from phi_discovery_validator import PhiDiscoveryValidator
import numpy as np

def test_phi_discovery():
    """Test if V6 can discover φ with a simple objective"""
    print("Testing V6 φ Discovery")
    print("=" * 60)
    
    optimizer = EnhancedMetaOptimizerV6Complete()
    validator = PhiDiscoveryValidator()
    
    # Test 1: Direct φ objective (should be easy)
    print("\n[Test 1] Direct φ Objective")
    def direct_phi_objective(params):
        return sum((v - PHI)**2 for v in params.values())
    
    initial = {f'x{i}': np.random.uniform(0, 3) for i in range(12)}
    print(f"Initial objective value: {direct_phi_objective(initial):.4f}")
    
    final, scores = optimizer.optimize(
        objective_func=direct_phi_objective,
        initial_state=initial,
        max_iterations=100,
        problem_name="direct_phi_test"
    )
    
    print(f"Final objective value: {scores[-1]:.4f}")
    print(f"Improvement: {scores[0] - scores[-1]:.4f}")
    
    # Validate
    validation = validator.validate_phi_discovery(final)
    print(f"\nφ Discovery Results:")
    print(f"  Overall rate: {validation['discovery_rate']:.1f}%")
    print(f"  Individual φ values: {validation['details']['individual_values']['rate']:.1f}%")
    
    # Show actual values
    print(f"\nFinal values:")
    for i, (k, v) in enumerate(final.items()):
        distance_to_phi = abs(v - PHI)
        print(f"  {k}: {v:.4f} (distance to φ: {distance_to_phi:.4f})")
    
    # Test 2: Check if geometric optimizer is working
    print("\n" + "=" * 60)
    print("[Test 2] Checking Geometric Optimizer")
    
    # Check if geometric optimizer exists
    if hasattr(optimizer, 'geometric_processor'):
        print("✓ Geometric processor exists")
        
        if hasattr(optimizer.geometric_processor, 'phi_optimizer'):
            print("✓ Phi optimizer exists")
            geo_opt = optimizer.geometric_processor.phi_optimizer
            
            # Check components
            print(f"  - Relationships defined: {len(geo_opt.relationships)}")
            print(f"  - Attractors defined: {len(geo_opt.attractors)}")
        else:
            print("✗ Phi optimizer missing!")
    else:
        print("✗ Geometric processor missing!")
    
    # Test 3: Manual geometric optimization
    print("\n[Test 3] Testing Manual Geometric Optimization")
    
    # Create a state with values far from φ
    test_state = {f'x{i}': 1.0 for i in range(12)}
    print(f"Initial uniform state: all values = 1.0")
    
    # Try to apply geometric forces manually
    if hasattr(optimizer.geometric_processor, 'apply_phi_optimization'):
        # This would need the actual method
        print("Attempting to apply geometric optimization...")
    else:
        print("No direct geometric optimization method available")
    
    # Conclusion
    print("\n" + "=" * 60)
    print("DIAGNOSIS")
    print("=" * 60)
    
    if validation['discovery_rate'] < 10:
        print("❌ V6 is NOT discovering φ effectively")
        print("\nPossible reasons:")
        print("1. Geometric optimizer not integrated into main loop")
        print("2. Forces too weak or incorrectly applied")
        print("3. Optimization getting stuck in local minima")
        print("4. Integer truncation losing precision")
    else:
        print("✅ V6 is discovering φ (unexpected given previous results)")
    
    return validation['discovery_rate']


def test_simple_convergence():
    """Test if V6 can even minimize a simple quadratic"""
    print("\n\n[Sanity Check] Simple Quadratic Minimization")
    print("=" * 60)
    
    optimizer = EnhancedMetaOptimizerV6Complete()
    
    def simple_quadratic(params):
        return sum(v**2 for v in params.values())
    
    initial = {f'x{i}': np.random.uniform(-5, 5) for i in range(6)}
    initial_value = simple_quadratic(initial)
    print(f"Initial value: {initial_value:.4f}")
    
    final, scores = optimizer.optimize(
        objective_func=simple_quadratic,
        initial_state=initial,
        max_iterations=50,
        problem_name="simple_quadratic"
    )
    
    final_value = simple_quadratic(final)
    print(f"Final value: {final_value:.4f}")
    print(f"Improvement: {initial_value - final_value:.4f}")
    
    if final_value < 0.1:
        print("✅ Basic optimization working")
    else:
        print("❌ Even basic optimization failing!")
    
    return final_value < 0.1


if __name__ == "__main__":
    # Run tests
    phi_rate = test_phi_discovery()
    basic_works = test_simple_convergence()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"φ Discovery Rate: {phi_rate:.1f}%")
    print(f"Basic Optimization: {'Working' if basic_works else 'Failed'}")
    
    if phi_rate < 10:
        print("\nRECOMMENDATION: Debug and fix geometric φ optimizer")
        print("See geometric_phi_optimizer.py and enhance integration")
    
    # Save results for pipeline
    import json
    results = {
        'phi_discovery_rate': phi_rate,
        'basic_optimization_works': basic_works,
        'timestamp': str(np.datetime64('now'))
    }
    
    with open('phi_discovery_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to phi_discovery_test_results.json")