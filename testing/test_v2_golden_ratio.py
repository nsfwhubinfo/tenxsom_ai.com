#!/usr/bin/env python3
"""Quick test of V2 golden ratio emergence"""

import sys
sys.path.append('/home/golde/Tenxsom_AI/research/meta_opt_quant')

from enhanced_meta_optimizer_v2 import EnhancedMetaOptimizerV2
import numpy as np

def golden_ratio_test_objective(state):
    """Simple golden ratio objective"""
    phi = 1.618033988749895
    score = 0.0
    
    # F-V-E ratio
    F = abs(state.get('frequency', 1.0))
    V = abs(state.get('vibration', 1.0)) 
    E = abs(state.get('energy', 1.0))
    
    if E > 0:
        ratio = F * V / E
        score += 20 * np.exp(-((ratio - phi)**2 / 0.1))
    
    # Sequential ratios
    x_params = sorted([v for k, v in state.items() if k.startswith('x')])
    for i in range(len(x_params) - 1):
        if x_params[i] > 0:
            ratio = x_params[i+1] / x_params[i]
            score += 10 * np.exp(-((ratio - phi)**2 / 0.1))
    
    return score

# Run 5 trials
print("Testing V2 Golden Ratio Emergence")
print("=" * 50)

successes = 0
best_error = float('inf')

for trial in range(5):
    print(f"\nTrial {trial + 1}:")
    
    # Random initial state near 1
    initial_state = {
        'frequency': np.random.uniform(0.8, 1.2),
        'vibration': np.random.uniform(1.3, 1.7),
        'energy': np.random.uniform(0.9, 1.1),
        'x0': np.random.uniform(0.8, 1.2),
        'x1': np.random.uniform(1.4, 1.8),
        'x2': np.random.uniform(2.2, 2.8)
    }
    
    optimizer = EnhancedMetaOptimizerV2()
    
    result = optimizer.meta_optimize_enhanced(
        initial_state=initial_state,
        objective_function=golden_ratio_test_objective,
        problem_signature={'type': 'golden_seeking', 'dimensions': 6},
        max_iterations=50
    )
    
    print(f"  Final score: {result['final_score']:.2f}")
    print(f"  Iterations: {result['iterations']}")
    print(f"  Best φ error: {result['best_golden_ratio_error']:.6f}")
    print(f"  Golden discoveries: {result['golden_discoveries']}")
    print(f"  F*V/E ratio: {result['symbol']['fve_ratio']:.4f}")
    
    if result['best_golden_ratio_error'] < 0.1:
        successes += 1
        print("  ✓ Golden ratio discovered!")
    
    if result['best_golden_ratio_error'] < best_error:
        best_error = result['best_golden_ratio_error']

print(f"\nSummary:")
print(f"Success rate: {successes}/5 ({successes*20}%)")
print(f"Best φ error: {best_error:.6f}")