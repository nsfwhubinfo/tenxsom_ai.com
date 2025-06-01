#!/usr/bin/env python3
"""
Initial test runner for META-OPT-QUANT
Performs a simple validation to ensure all components are working
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from meta_optimizer import MetaOptimizer, example_objective_function

def run_initial_test():
    """Run a simple test to verify META-OPT-QUANT is functional"""
    print("META-OPT-QUANT Initial Test")
    print("=" * 50)
    print("Testing basic functionality...")
    
    try:
        # Create optimizer
        optimizer = MetaOptimizer(cache_dir="./test_cache")
        
        # Simple test state
        test_state = {
            'param_0': 1.0,
            'param_1': 1.2,
            'param_2': 1.5,
            'frequency': 1.0,
            'vibration': 1.618,
            'energy': 1.0
        }
        
        # Run short optimization
        result = optimizer.meta_optimize(
            initial_state=test_state,
            objective_function=example_objective_function,
            max_iterations=10,
            convergence_threshold=0.01
        )
        
        print("\n✓ Test completed successfully!")
        print(f"  Initial score: {example_objective_function(test_state):.4f}")
        print(f"  Final score: {result['final_score']:.4f}")
        print(f"  Improvement: {result['final_score'] - example_objective_function(test_state):.4f}")
        print(f"  Cache patterns stored: {result['cache_stats']['pattern_count']}")
        
        # Test cache retrieval
        print("\n✓ Testing cache functionality...")
        symbol = optimizer.quantizer.quantize(result['optimized_state'])
        cached_pattern = optimizer.cache.retrieve_pattern(symbol.symbol_id)
        
        if cached_pattern:
            print(f"  Successfully retrieved pattern from cache")
            print(f"  Cached F-V-E: ({cached_pattern['F']:.3f}, {cached_pattern['V']:.3f}, {cached_pattern['E']:.3f})")
        
        print("\n✅ All components functional!")
        print("\nReady to run full validation experiments.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_initial_test()
    sys.exit(0 if success else 1)