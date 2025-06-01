#!/usr/bin/env python3
"""Analyze V2 continuous testing results"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict

def analyze_v2_results():
    """Analyze V2 test results"""
    results_file = Path("continuous_test_results_v2/results_20250530.json")
    
    if not results_file.exists():
        print("No results file found")
        return
    
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Group by dataset
    by_dataset = defaultdict(list)
    golden_discoveries_by_dataset = defaultdict(int)
    
    for result in results:
        if result['success']:
            dataset = result['dataset']
            by_dataset[dataset].append(result)
            
            # Count golden discoveries
            if result['golden_ratio_error'] < 0.1:
                golden_discoveries_by_dataset[dataset] += 1
    
    print(f"META-OPT-QUANT V2 Results Analysis")
    print(f"=" * 50)
    print(f"Total tests: {len(results)}")
    print(f"Successful: {sum(1 for r in results if r['success'])}")
    
    # Overall golden ratio stats
    all_golden_errors = [r['golden_ratio_error'] for r in results 
                        if r['success'] and r['golden_ratio_error'] != float('inf')]
    golden_discoveries = sum(1 for r in results 
                           if r['success'] and r['golden_ratio_error'] < 0.1)
    
    print(f"\nGolden Ratio Statistics:")
    print(f"  Total discoveries: {golden_discoveries}")
    print(f"  Discovery rate: {golden_discoveries/len(results)*100:.1f}%")
    if all_golden_errors:
        print(f"  Best φ error: {min(all_golden_errors):.6f}")
        print(f"  Average φ error: {np.mean(all_golden_errors):.6f}")
    
    # Positive acceleration stats
    positive_accel = sum(1 for r in results 
                        if r['success'] and r['acceleration_percentage'] > 0)
    print(f"\nAcceleration Statistics:")
    print(f"  Positive accelerations: {positive_accel}/{len(results)} ({positive_accel/len(results)*100:.1f}%)")
    
    # By dataset analysis
    print(f"\nResults by Dataset:")
    print(f"-" * 50)
    
    for dataset, tests in sorted(by_dataset.items()):
        print(f"\n{dataset.upper()} ({len(tests)} tests):")
        
        iterations = [t['iterations'] for t in tests]
        accelerations = [t['acceleration_percentage'] for t in tests]
        golden_errors = [t['golden_ratio_error'] for t in tests 
                        if t['golden_ratio_error'] != float('inf')]
        
        print(f"  Avg iterations: {np.mean(iterations):.1f}")
        print(f"  Avg acceleration: {np.mean(accelerations):.1f}%")
        print(f"  Positive accelerations: {sum(1 for a in accelerations if a > 0)}")
        
        if golden_errors:
            print(f"  Best φ error: {min(golden_errors):.6f}")
            print(f"  Golden discoveries: {golden_discoveries_by_dataset[dataset]}")
            print(f"  Discovery rate: {golden_discoveries_by_dataset[dataset]/len(tests)*100:.1f}%")
        else:
            print(f"  No golden ratio attempts")
    
    # Best performers
    print(f"\nTop 5 Golden Ratio Discoveries:")
    print(f"-" * 50)
    
    golden_results = sorted([r for r in results if r['success'] and r['golden_ratio_error'] < 1], 
                          key=lambda x: x['golden_ratio_error'])[:5]
    
    for i, r in enumerate(golden_results):
        print(f"{i+1}. {r['dataset']}: φ error = {r['golden_ratio_error']:.6f}, "
              f"iterations = {r['iterations']}, acceleration = {r['acceleration_percentage']:.1f}%")

if __name__ == "__main__":
    analyze_v2_results()