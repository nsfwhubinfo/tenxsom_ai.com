#!/usr/bin/env python3
"""Test imports and basic functionality"""

import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "research" / "meta_opt_quant"))

print("Testing imports...")

try:
    from enhanced_meta_optimizer import EnhancedMetaOptimizer
    print("✓ EnhancedMetaOptimizer imported")
except Exception as e:
    print(f"✗ Failed to import EnhancedMetaOptimizer: {e}")
    sys.exit(1)

try:
    from global_cache_manager import get_global_cache
    print("✓ GlobalCacheManager imported")
except Exception as e:
    print(f"✗ Failed to import GlobalCacheManager: {e}")
    sys.exit(1)

try:
    # Test basic functionality
    optimizer = EnhancedMetaOptimizer()
    print("✓ Created EnhancedMetaOptimizer instance")
    
    # Simple test
    def test_objective(state):
        return -sum(state[k]**2 for k in state if isinstance(state[k], (int, float)))
    
    initial_state = {'x0': 1.0, 'x1': 1.0}
    problem_signature = {'type': 'test', 'dimensions': 2}
    
    print("Running quick optimization test...")
    result = optimizer.meta_optimize_enhanced(
        initial_state=initial_state,
        objective_function=test_objective,
        problem_signature=problem_signature,
        max_iterations=5
    )
    
    print(f"✓ Optimization completed: {result['iterations']} iterations")
    print(f"✓ Final score: {result['final_score']:.4f}")
    
except Exception as e:
    print(f"✗ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nAll tests passed! The system is ready for continuous testing.")
print("\nTo run continuous testing:")
print("  python3 continuous_meta_opt_testing.py")