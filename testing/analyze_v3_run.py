#!/usr/bin/env python3
"""Quick analysis of V3 run from the output"""

import re
import sys

def analyze_v3_output(text):
    # Find all golden ratio discoveries
    golden_pattern = r"Golden ratio discovered.*Error: ([\d.]+)"
    perfect_pattern = r"PERFECT golden ratio.*Error: ([\d.]+)"
    completed_pattern = r"Test (\w+) completed: (\d+) iterations, ([-\d.]+)% acceleration, φ-error: ([\d.]+)"
    
    golden_discoveries = re.findall(golden_pattern, text)
    perfect_discoveries = re.findall(perfect_pattern, text)
    completed_tests = re.findall(completed_pattern, text)
    
    print("=== V3 Testing Analysis ===")
    print(f"Total golden ratio discoveries: {len(golden_discoveries)}")
    print(f"Perfect golden ratios (error < 0.001): {len(perfect_discoveries)}")
    
    if golden_discoveries:
        errors = [float(e) for e in golden_discoveries]
        print(f"Best φ error: {min(errors):.6f}")
        print(f"Average φ error: {sum(errors)/len(errors):.6f}")
        
        # Count by error threshold
        excellent = sum(1 for e in errors if e < 0.001)
        good = sum(1 for e in errors if 0.001 <= e < 0.01)
        fair = sum(1 for e in errors if 0.01 <= e < 0.05)
        
        print(f"\nError distribution:")
        print(f"  Excellent (<0.001): {excellent} ({excellent/len(errors)*100:.1f}%)")
        print(f"  Good (0.001-0.01): {good} ({good/len(errors)*100:.1f}%)")
        print(f"  Fair (0.01-0.05): {fair} ({fair/len(errors)*100:.1f}%)")
    
    if completed_tests:
        print(f"\nCompleted tests: {len(completed_tests)}")
        accelerations = [float(a) for _, _, a, _ in completed_tests]
        positive_acc = sum(1 for a in accelerations if a > 0)
        print(f"Positive acceleration rate: {positive_acc/len(accelerations)*100:.1f}%")
        
        # Count golden discoveries in completed tests
        golden_in_completed = sum(1 for _, _, _, e in completed_tests if float(e) < 0.05)
        print(f"Golden ratio discovery rate: {golden_in_completed/len(completed_tests)*100:.1f}%")

if __name__ == "__main__":
    # Read from stdin
    text = sys.stdin.read()
    analyze_v3_output(text)