#!/usr/bin/env python3
"""Analyze continuous testing results"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def analyze_results(results_file):
    """Analyze test results"""
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Group by dataset
    by_dataset = defaultdict(list)
    for result in results:
        if result['success']:
            by_dataset[result['dataset']].append(result)
    
    print(f"Total tests: {len(results)}")
    print(f"Successful: {sum(1 for r in results if r['success'])}")
    print(f"Failed: {sum(1 for r in results if not r['success'])}\n")
    
    # Analyze by dataset
    for dataset, tests in by_dataset.items():
        print(f"\n{dataset.upper()} ({len(tests)} tests):")
        
        # Filter out overflow results
        valid_tests = [t for t in tests if abs(t['final_score']) < 1e10]
        
        if valid_tests:
            iterations = [t['iterations'] for t in valid_tests]
            improvements = [t['improvement'] for t in valid_tests]
            golden_errors = [t['golden_ratio_error'] for t in valid_tests]
            accelerations = [t['acceleration_percentage'] for t in valid_tests]
            
            print(f"  Avg iterations: {np.mean(iterations):.1f}")
            print(f"  Avg improvement: {np.mean(improvements):.2f}")
            print(f"  Avg acceleration: {np.mean(accelerations):.1f}%")
            print(f"  Best golden ratio error: {min(golden_errors):.4f}")
            
            # Count golden discoveries
            golden_found = sum(1 for e in golden_errors if e < 0.1)
            print(f"  Golden ratios found: {golden_found}/{len(valid_tests)} ({golden_found/len(valid_tests)*100:.1f}%)")
        else:
            print("  All tests had numerical overflow")

# Run analysis
if __name__ == "__main__":
    results_dir = Path("continuous_test_results")
    latest_results = sorted(results_dir.glob("results_*.json"))[-1]
    print(f"Analyzing {latest_results}")
    analyze_results(latest_results)