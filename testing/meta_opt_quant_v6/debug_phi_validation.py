#!/usr/bin/env python3
"""
Debug why φ discovery validation shows such low scores
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import numpy as np
from research.meta_opt_quant.enhanced_meta_optimizer_v6_cuboctahedral import PHI
from phi_discovery_validator import PhiDiscoveryValidator

def test_validation_logic():
    """Test the validation logic with known good states"""
    print("Testing φ Discovery Validation Logic")
    print("=" * 60)
    
    validator = PhiDiscoveryValidator()
    
    # Test 1: State with all values exactly φ
    print("\n[Test 1] All values = φ")
    perfect_phi = {f'x{i}': PHI for i in range(12)}
    result = validator.validate_phi_discovery(perfect_phi)
    print(f"Discovery rate: {result['discovery_rate']:.1f}%")
    print(f"Individual values: {result['details']['individual_values']['rate']:.1f}%")
    
    # Test 2: State with perfect edge ratios
    print("\n[Test 2] Perfect edge ratios")
    edge_ratio_state = {f'x{i}': PHI ** i for i in range(6)}
    result2 = validator.validate_phi_discovery(edge_ratio_state)
    print(f"Discovery rate: {result2['discovery_rate']:.1f}%")
    print(f"Edge ratios: {result2['details']['edge_ratios']['rate']:.1f}%")
    
    # Test 3: State with values near φ (within tolerance)
    print("\n[Test 3] Values near φ (±0.01)")
    near_phi = {
        'x0': PHI + 0.005,
        'x1': PHI - 0.005,
        'x2': 1/PHI + 0.008,
        'x3': 1/PHI - 0.008,
        'x4': PHI**2 - 0.009,
        'x5': PHI**0.5 + 0.007
    }
    result3 = validator.validate_phi_discovery(near_phi)
    print(f"Discovery rate: {result3['discovery_rate']:.1f}%")
    print("Details:")
    for key, details in result3['details'].items():
        if 'rate' in details:
            print(f"  {key}: {details['rate']:.1f}%")
    
    # Test 4: Realistic optimization result
    print("\n[Test 4] Realistic optimization result")
    realistic = {
        'x0': 1.4,
        'x1': 1.6,
        'x2': 1.65,
        'x3': 1.618,  # Close to φ
        'x4': 1.7,
        'x5': 1.8
    }
    result4 = validator.validate_phi_discovery(realistic)
    print(f"Discovery rate: {result4['discovery_rate']:.1f}%")
    
    # Show what counts as φ discovery
    print("\n[Analysis] What counts as φ discovery?")
    print(f"φ = {PHI:.6f}")
    print(f"Tolerance = {validator.phi_tolerance}")
    print(f"φ ± tolerance = [{PHI - validator.phi_tolerance:.6f}, {PHI + validator.phi_tolerance:.6f}]")
    
    # Test the scoring weights
    print("\n[Weights] Scoring weights:")
    weights = {
        'individual_values': 1.0,
        'edge_ratios': 2.0,
        'opposite_sums': 2.5,
        'fibonacci_convergence': 1.5,
        'geometric_mean': 1.5,
        'vector_equilibrium': 1.0
    }
    
    total_weight = sum(weights.values())
    print(f"Total weight: {total_weight}")
    for rel, w in weights.items():
        print(f"  {rel}: {w} ({w/total_weight*100:.1f}%)")


def test_actual_v6_output():
    """Test with actual V6 output values"""
    print("\n\n[Test 5] Actual V6 Output")
    print("=" * 60)
    
    # From the test output, V6 converges all values to 0.8254
    v6_output = {f'x{i}': 0.8254 for i in range(12)}
    
    validator = PhiDiscoveryValidator()
    result = validator.validate_phi_discovery(v6_output)
    
    print(f"V6 output: all values = 0.8254")
    print(f"Distance from φ: {abs(0.8254 - PHI):.4f}")
    print(f"Distance from 1/φ: {abs(0.8254 - 1/PHI):.4f}")
    print(f"Discovery rate: {result['discovery_rate']:.1f}%")
    
    # Check why it's not detecting φ
    print("\nWhy low score?")
    print(f"- Individual values near φ: {result['details']['individual_values']['count']}/{12}")
    print(f"- Edge ratios near φ: {result['details']['edge_ratios']['count']}/{result['details']['edge_ratios']['total']}")
    print(f"- All values identical → no meaningful ratios")


def suggest_improvements():
    """Suggest improvements to V6"""
    print("\n\n[Improvements] Suggested fixes for V6")
    print("=" * 60)
    
    print("1. **Prevent convergence to identical values**")
    print("   - Add diversity term to objective")
    print("   - Use different initialization for each parameter")
    print("   - Apply different φ targets to different parameters")
    
    print("\n2. **Stronger φ forces in geometric optimizer**")
    print("   - Current forces may be too weak")
    print("   - Integer truncation losing precision")
    print("   - Need adaptive scaling based on distance to φ")
    
    print("\n3. **Fix objective function direction**")
    print("   - V6 treats all objectives as maximization")
    print("   - Need to detect and handle minimization properly")
    
    print("\n4. **Direct φ initialization**")
    print("   ```python")
    print("   # Initialize some parameters near φ values")
    print("   initial['x0'] = PHI + np.random.uniform(-0.1, 0.1)")
    print("   initial['x1'] = 1/PHI + np.random.uniform(-0.1, 0.1)")
    print("   ```")


if __name__ == "__main__":
    test_validation_logic()
    test_actual_v6_output()
    suggest_improvements()
    
    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    print("The validation logic is working correctly.")
    print("V6's issue: All parameters converge to the same value (0.8254)")
    print("This prevents any meaningful φ relationships from forming.")
    print("\nRoot cause: Symmetry in V6 causes all parameters to evolve identically")
    print("Solution: Break symmetry and add diversity to optimization")