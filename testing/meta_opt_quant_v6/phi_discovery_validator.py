#!/usr/bin/env python3
"""
Proper φ Discovery Validator for META-OPT-QUANT V6
Validates geometric φ relationships, not just individual values
"""

import numpy as np
from typing import Dict, List, Tuple
from research.meta_opt_quant.enhanced_meta_optimizer_v6_cuboctahedral import PHI

class PhiDiscoveryValidator:
    """Validates φ discovery through geometric relationships"""
    
    def __init__(self):
        self.phi_tolerance = 0.01
        self.relationship_types = [
            'individual_values',
            'edge_ratios', 
            'face_diagonals',
            'vertex_distances',
            'opposite_sums',
            'fibonacci_convergence',
            'geometric_mean'
        ]
    
    def validate_phi_discovery(self, state: Dict[str, float]) -> Dict[str, any]:
        """Comprehensive φ discovery validation"""
        values = list(state.values())
        n = len(values)
        
        results = {
            'total_phi_discoveries': 0,
            'discovery_rate': 0.0,
            'relationship_scores': {},
            'details': {}
        }
        
        # 1. Individual values (V4-style check)
        individual_phi = 0
        for v in values:
            if abs(v - PHI) < self.phi_tolerance or abs(v - 1/PHI) < self.phi_tolerance:
                individual_phi += 1
        results['details']['individual_values'] = {
            'count': individual_phi,
            'rate': individual_phi / n * 100
        }
        
        # 2. Edge ratios (V6 geometric relationships)
        edge_ratios = []
        if n >= 12:  # Cuboctahedral structure
            # Check specific edge relationships
            for i in range(0, n-3, 4):
                if i+3 < n:
                    ratio = (values[i] + values[i+1]) / (values[i+2] + values[i+3] + 1e-10)
                    edge_ratios.append(ratio)
        
        edge_phi_count = sum(1 for r in edge_ratios 
                           if abs(r - PHI) < self.phi_tolerance or 
                              abs(r - 1/PHI) < self.phi_tolerance)
        results['details']['edge_ratios'] = {
            'count': edge_phi_count,
            'total': len(edge_ratios),
            'rate': edge_phi_count / len(edge_ratios) * 100 if edge_ratios else 0
        }
        
        # 3. Opposite vertex sums (Cuboctahedral property)
        opposite_phi = 0
        if n == 12:  # Exact cuboctahedral structure
            phi_squared = PHI ** 2
            opposite_pairs = [(0, 6), (1, 7), (2, 8), (3, 9), (4, 10), (5, 11)]
            for i, j in opposite_pairs:
                sum_val = values[i] + values[j]
                if abs(sum_val - phi_squared) < self.phi_tolerance * 2:
                    opposite_phi += 1
        
        results['details']['opposite_sums'] = {
            'count': opposite_phi,
            'total': 6 if n == 12 else 0,
            'rate': opposite_phi / 6 * 100 if n == 12 else 0
        }
        
        # 4. Fibonacci convergence check
        fib_ratios = []
        sorted_vals = sorted(values)
        for i in range(len(sorted_vals) - 1):
            if sorted_vals[i] > 0:
                ratio = sorted_vals[i+1] / sorted_vals[i]
                fib_ratios.append(ratio)
        
        fib_phi_count = sum(1 for r in fib_ratios 
                          if abs(r - PHI) < self.phi_tolerance * 2)
        results['details']['fibonacci_convergence'] = {
            'count': fib_phi_count,
            'total': len(fib_ratios),
            'rate': fib_phi_count / len(fib_ratios) * 100 if fib_ratios else 0
        }
        
        # 5. Geometric mean relationships
        geo_phi = 0
        for i in range(n-2):
            # Check if geometric mean of three consecutive values approaches φ
            geo_mean = np.cbrt(abs(values[i] * values[i+1] * values[i+2]))
            if abs(geo_mean - PHI) < self.phi_tolerance:
                geo_phi += 1
        
        results['details']['geometric_mean'] = {
            'count': geo_phi,
            'total': n-2 if n > 2 else 0,
            'rate': geo_phi / (n-2) * 100 if n > 2 else 0
        }
        
        # 6. Vector equilibrium (distance from center)
        if n >= 12:
            center = np.mean(values)
            distances = [abs(v - center) for v in values]
            vec_phi = sum(1 for d in distances if abs(d - PHI) < self.phi_tolerance)
            results['details']['vector_equilibrium'] = {
                'count': vec_phi,
                'total': n,
                'rate': vec_phi / n * 100
            }
        
        # Calculate total discoveries (weighted by importance)
        weights = {
            'individual_values': 1.0,
            'edge_ratios': 2.0,  # More important for V6
            'opposite_sums': 2.5,  # Critical cuboctahedral property
            'fibonacci_convergence': 1.5,
            'geometric_mean': 1.5,
            'vector_equilibrium': 1.0
        }
        
        total_weighted_discoveries = 0
        total_weight = 0
        
        for rel_type, details in results['details'].items():
            if 'count' in details:
                weight = weights.get(rel_type, 1.0)
                total_weighted_discoveries += details['count'] * weight
                total_weight += details.get('total', details['count']) * weight
        
        # Overall discovery rate (weighted)
        results['total_phi_discoveries'] = total_weighted_discoveries
        results['discovery_rate'] = (total_weighted_discoveries / total_weight * 100) if total_weight > 0 else 0
        
        # Relationship scores
        for rel_type, details in results['details'].items():
            if 'rate' in details:
                results['relationship_scores'][rel_type] = details['rate']
        
        # Determine if V6 geometric optimization is working
        results['geometric_optimization_active'] = (
            results['details']['edge_ratios']['rate'] > 20 or
            results['details']['opposite_sums']['rate'] > 30 or
            results['details'].get('vector_equilibrium', {}).get('rate', 0) > 15
        )
        
        return results
    
    def get_phi_score(self, state: Dict[str, float]) -> float:
        """Get a single φ discovery score (0-100)"""
        validation = self.validate_phi_discovery(state)
        return validation['discovery_rate']
    
    def is_phi_discovered(self, state: Dict[str, float], threshold: float = 50.0) -> bool:
        """Check if φ discovery exceeds threshold"""
        return self.get_phi_score(state) >= threshold


# Test the validator
if __name__ == "__main__":
    validator = PhiDiscoveryValidator()
    
    # Test case 1: No φ discovery
    test_state_1 = {f'x{i}': np.random.uniform(0, 5) for i in range(12)}
    result_1 = validator.validate_phi_discovery(test_state_1)
    print("Random state:")
    print(f"  Discovery rate: {result_1['discovery_rate']:.1f}%")
    print(f"  Geometric optimization: {result_1['geometric_optimization_active']}")
    
    # Test case 2: Individual φ values (V4-style)
    test_state_2 = {f'x{i}': PHI if i < 6 else 1.0 for i in range(12)}
    result_2 = validator.validate_phi_discovery(test_state_2)
    print("\nIndividual φ values:")
    print(f"  Discovery rate: {result_2['discovery_rate']:.1f}%")
    print(f"  Individual values: {result_2['details']['individual_values']['rate']:.1f}%")
    
    # Test case 3: Geometric relationships (V6-style)
    test_state_3 = {}
    for i in range(12):
        if i < 6:
            test_state_3[f'x{i}'] = PHI ** (i/6)
        else:
            # Opposite vertices sum to φ²
            test_state_3[f'x{i}'] = PHI**2 - test_state_3[f'x{i-6}']
    
    result_3 = validator.validate_phi_discovery(test_state_3)
    print("\nGeometric φ relationships:")
    print(f"  Discovery rate: {result_3['discovery_rate']:.1f}%")
    print(f"  Opposite sums: {result_3['details']['opposite_sums']['rate']:.1f}%")
    print(f"  Geometric optimization: {result_3['geometric_optimization_active']}")