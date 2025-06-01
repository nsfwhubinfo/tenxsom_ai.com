#!/usr/bin/env python3
"""Analyze V4 results from sample run"""

import re

with open('v4_sample_run.txt', 'rb') as f:
    content = f.read().decode('utf-8', errors='ignore')

# Find all completed tests
completed_pattern = r"Test .* completed: (\d+) iterations, ([-\d.]+)% acceleration, φ-error: ([\d.]+)"
completed_tests = re.findall(completed_pattern, content)

# Count golden discoveries
total_tests = len(completed_tests)
golden_discoveries = sum(1 for _, _, error in completed_tests if float(error) < 0.05)
perfect_discoveries = sum(1 for _, _, error in completed_tests if float(error) < 0.001)

print("=== V4 RESULTS ANALYSIS ===")
print(f"Total tests completed: {total_tests}")
print(f"Golden ratio discoveries (< 0.05): {golden_discoveries}")
print(f"Perfect discoveries (< 0.001): {perfect_discoveries}")
print(f"Discovery rate: {golden_discoveries/total_tests*100:.1f}%")
print(f"Perfect rate: {perfect_discoveries/total_tests*100:.1f}%")

# Analyze by test type
test_results = {}
for match in re.finditer(r"Test (\w+)_\d+_\d+ completed:.*φ-error: ([\d.]+)", content):
    test_type = match.group(1)
    error = float(match.group(2))
    
    if test_type not in test_results:
        test_results[test_type] = {'total': 0, 'golden': 0, 'perfect': 0}
    
    test_results[test_type]['total'] += 1
    if error < 0.05:
        test_results[test_type]['golden'] += 1
    if error < 0.001:
        test_results[test_type]['perfect'] += 1

print("\n=== BY TEST TYPE ===")
for test_type, stats in sorted(test_results.items()):
    if stats['total'] > 0:
        golden_rate = stats['golden'] / stats['total'] * 100
        perfect_rate = stats['perfect'] / stats['total'] * 100
        print(f"{test_type}: {golden_rate:.0f}% golden, {perfect_rate:.0f}% perfect ({stats['total']} tests)")