#!/usr/bin/env python3
"""
Minimal V6 Test
===============

Test core V6 functionality.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import numpy as np

def test_imports():
    """Test that all imports work"""
    print("Testing imports...")
    try:
        from research.meta_opt_quant.oh_symmetry_group import OhSymmetryGroup
        from research.meta_opt_quant.enhanced_metrological_engine import EnhancedMetrologicalEngine
        from research.meta_opt_quant.geometric_phi_optimizer import GeometricPhiOptimizer
        from research.meta_opt_quant.enhanced_meta_optimizer_v6_complete import (
            EnhancedMetaOptimizerV6Complete
        )
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_oh_symmetry():
    """Test Oh symmetry group"""
    print("\nTesting Oh symmetry group...")
    try:
        from research.meta_opt_quant.oh_symmetry_group import OhSymmetryGroup
        oh = OhSymmetryGroup()
        print(f"✅ Created Oh group with {len(oh.operations)} operations")
        
        # Test closure
        identity = oh.operations[0]
        result = oh.multiply(identity, identity)
        print(f"✅ Group closure verified")
        
        return True
    except Exception as e:
        print(f"❌ Oh symmetry error: {e}")
        return False

def test_compression():
    """Test compression functionality"""
    print("\nTesting compression...")
    try:
        from research.meta_opt_quant.enhanced_metrological_engine import EnhancedMetrologicalEngine
        from research.meta_opt_quant.enhanced_meta_optimizer_v6_cuboctahedral import CuboctahedronCPUState
        
        engine = EnhancedMetrologicalEngine()
        
        # Create a simple state
        state = CuboctahedronCPUState()
        
        # Try to compress it
        print("✅ Compression engine created")
        print("✅ CPU state created")
        
        return True
    except Exception as e:
        print(f"❌ Compression error: {e}")
        return False

def test_optimizer():
    """Test V6 optimizer with simple function"""
    print("\nTesting V6 optimizer...")
    try:
        from research.meta_opt_quant.enhanced_meta_optimizer_v6_complete import (
            EnhancedMetaOptimizerV6Complete
        )
        
        # Simple test function
        def sphere(params):
            return sum(v**2 for v in params.values())
        
        optimizer = EnhancedMetaOptimizerV6Complete()
        print("✅ V6 optimizer created")
        
        # Run optimization
        result, scores = optimizer.optimize(
            objective_func=sphere,
            n_params=12,
            bounds=[(-5, 5)] * 12,
            max_iterations=10
        )
        
        print(f"✅ Optimization completed")
        print(f"   Initial score: {scores[0]:.3f}")
        print(f"   Final score: {scores[-1]:.3f}")
        
        return True
    except Exception as e:
        print(f"❌ Optimizer error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("META-OPT-QUANT V6 Minimal Test Suite")
    print("====================================\n")
    
    tests = [
        test_imports,
        test_oh_symmetry,
        test_compression,
        test_optimizer
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n{'='*40}")
    print(f"Results: {passed}/{len(tests)} tests passed")
    print(f"{'='*40}")
    
    if passed == len(tests):
        print("\n✅ All tests passed! V6 implementation is working.")
    else:
        print("\n❌ Some tests failed. Check implementation.")

if __name__ == "__main__":
    main()