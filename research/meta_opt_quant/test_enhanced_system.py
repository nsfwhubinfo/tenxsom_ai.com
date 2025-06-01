#!/usr/bin/env python3
"""
Quick test of enhanced META-OPT-QUANT system
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from enhanced_meta_optimizer import EnhancedMetaOptimizer
from meta_optimizer import example_objective_function

def test_enhanced_system():
    """Quick test to verify enhanced system works"""
    print("Testing Enhanced META-OPT-QUANT System")
    print("=" * 50)
    
    try:
        # Create optimizer
        optimizer = EnhancedMetaOptimizer()
        
        # Simple test state
        test_state = {
            'param_0': 1.0,
            'param_1': 1.2, 
            'param_2': 1.5,
            'frequency': 1.0,
            'vibration': 1.618,
            'energy': 1.0
        }
        
        problem_signature = {
            'type': 'test_problem',
            'dimensions': 6,
            'objective_type': 'golden_ratio_seeking'
        }
        
        # Run short optimization
        result = optimizer.meta_optimize_enhanced(
            initial_state=test_state,
            objective_function=example_objective_function,
            problem_signature=problem_signature,
            max_iterations=10
        )
        
        print("\n✓ Enhanced system test completed!")
        print(f"  Final score: {result['final_score']:.4f}")
        print(f"  Iterations: {result['iterations']}")
        print(f"  Acceleration: {result['acceleration_percentage']:.1f}%")
        print(f"  Patterns used: {result['patterns_used']}")
        print(f"  F*V/E ratio: {result['symbol']['fve_ratio']:.4f}")
        
        print("\n✅ Enhanced system functional!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_system()
    sys.exit(0 if success else 1)