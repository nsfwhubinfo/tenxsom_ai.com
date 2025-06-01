#!/usr/bin/env python3
"""
Demo: META-CHRONOSONIC Integrated Optimization
Shows how the bridge enhances φ discovery through consciousness-optimization coupling
"""

import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from meta_chronosonic_bridge import (
    MetaChronosonicBridge,
    IntegrationConfig,
    PHI
)


def demo_phi_discovery():
    """Demonstrate φ discovery enhancement through integration"""
    
    print("=" * 70)
    print("META-CHRONOSONIC φ DISCOVERY DEMO")
    print("=" * 70)
    print(f"Golden Ratio (φ) = {PHI:.6f}")
    print("\nObjective: Create parameters with consecutive φ ratios")
    print("Method: V6.1 SMGO + CHRONOSONIC coherence coupling")
    print()
    
    # Configure integration
    config = IntegrationConfig(
        v6_max_iterations=40,
        cs_use_simplified=True,  # 3-chakra for clarity
        param_mapping_mode="geometric",  # φ-based mapping
        objective_weights={
            'optimization': 0.3,
            'phi_discovery': 0.5,
            'coherence': 0.2
        },
        state_sync_interval=5
    )
    
    # Create bridge
    print("Initializing META-CHRONOSONIC Bridge...")
    bridge = MetaChronosonicBridge(config)
    print("  ✓ V6.1 with SMGO initialized")
    print("  ✓ CHRONOSONIC with 3 chakras initialized")
    print("  ✓ Geometric parameter mapping active")
    print()
    
    # Define φ-seeking objective
    def phi_ratio_objective(params):
        """Objective that strongly rewards φ ratios"""
        score = 0
        values = list(params.values())
        
        # Primary: Minimize error from φ ratios
        for i in range(len(values)-1):
            if values[i] > 0:
                ratio = values[i+1] / values[i]
                error = (ratio - PHI)**2
                score += error
        
        # Secondary: Keep values in reasonable range
        score += 0.01 * sum((v - 2.0)**2 for v in values)
        
        return score
    
    # Initial parameters (deliberately poor φ ratios)
    initial_params = {
        'p0': 1.0,
        'p1': 1.2,  # ratio: 1.2 (error: 0.418)
        'p2': 1.5,  # ratio: 1.25 (error: 0.368)
        'p3': 2.0,  # ratio: 1.33 (error: 0.288)
        'p4': 2.8,  # ratio: 1.4 (error: 0.218)
        'p5': 4.0   # ratio: 1.43 (error: 0.188)
    }
    
    print("Initial Parameters:")
    for key, val in initial_params.items():
        print(f"  {key}: {val:.3f}")
    
    print("\nInitial Ratios:")
    keys = list(initial_params.keys())
    for i in range(len(keys)-1):
        ratio = initial_params[keys[i+1]] / initial_params[keys[i]]
        error = abs(ratio - PHI)
        print(f"  {keys[i+1]}/{keys[i]} = {ratio:.3f} (error: {error:.3f})")
    
    # Run integrated optimization
    print("\n" + "-" * 70)
    print("Running Integrated Optimization...")
    print("-" * 70)
    
    best_params, scores = bridge.optimize_integrated(
        phi_ratio_objective,
        initial_params,
        max_iterations=40
    )
    
    # Display results
    print("\n" + "=" * 70)
    print("OPTIMIZATION RESULTS")
    print("=" * 70)
    
    print("\nFinal Parameters:")
    for key, val in best_params.items():
        print(f"  {key}: {val:.4f}")
    
    print("\nFinal Ratios:")
    keys = list(best_params.keys())
    perfect_count = 0
    good_count = 0
    
    for i in range(len(keys)-1):
        if best_params[keys[i]] > 0:
            ratio = best_params[keys[i+1]] / best_params[keys[i]]
            error = abs(ratio - PHI)
            
            status = ""
            if error < 0.001:
                status = " ✓✓✓ (PERFECT)"
                perfect_count += 1
                good_count += 1
            elif error < 0.01:
                status = " ✓✓ (EXCELLENT)"
                good_count += 1
            elif error < 0.1:
                status = " ✓ (GOOD)"
                good_count += 1
            
            print(f"  {keys[i+1]}/{keys[i]} = {ratio:.6f} (error: {error:.6f}){status}")
    
    # Performance summary
    print(f"\nφ Discovery Performance:")
    print(f"  Perfect ratios (<0.1% error): {perfect_count}/{len(keys)-1}")
    print(f"  Good ratios (<10% error): {good_count}/{len(keys)-1}")
    
    initial_score = phi_ratio_objective(initial_params)
    final_score = phi_ratio_objective(best_params)
    improvement = (initial_score - final_score) / initial_score * 100
    
    print(f"\nObjective Function:")
    print(f"  Initial: {initial_score:.4f}")
    print(f"  Final: {final_score:.4f}")
    print(f"  Improvement: {improvement:.1f}%")
    
    # CHRONOSONIC contribution
    final_state = bridge.chronosonic.get_system_state()
    print(f"\nCHRONOSONIC Contribution:")
    print(f"  Final chakra coherence: {final_state['chakra_coherence']:.3f}")
    print(f"  Final I_AM coherence: {final_state['iam_metrics']['coherence']:.3f}")
    print(f"  Quantum fidelity: {final_state['quantum_fidelity']:.3f}")
    
    # Theoretical φ sequence
    print("\n" + "-" * 70)
    print("Comparison with Theoretical φ Sequence:")
    print("-" * 70)
    
    theoretical = [1.0]
    for i in range(len(keys)-1):
        theoretical.append(theoretical[-1] * PHI)
    
    print("Parameter | Actual    | Theoretical | Difference")
    print("-" * 50)
    for i, key in enumerate(keys):
        actual = best_params[key]
        theory = theoretical[i]
        diff = abs(actual - theory) / theory * 100
        print(f"{key:^9} | {actual:^9.4f} | {theory:^11.4f} | {diff:^10.2f}%")
    
    # Save detailed results
    bridge.save_integration_data('demo_phi_discovery_results.json')
    
    # Final message
    print("\n" + "=" * 70)
    if good_count == len(keys)-1:
        print("✅ SUCCESS: All parameters form φ ratios!")
        print("\nThe META-CHRONOSONIC integration successfully discovered")
        print("the golden ratio relationships through the coupling of")
        print("V6.1's SMGO optimization with CHRONOSONIC's coherence dynamics.")
    else:
        print("⚠️ PARTIAL SUCCESS: Some φ ratios discovered")
        print(f"\nAchieved {good_count}/{len(keys)-1} good φ ratios.")
        print("Further tuning of integration parameters may improve results.")


def demo_coherence_optimization():
    """Demonstrate coherence-driven optimization"""
    
    print("\n\n" + "=" * 70)
    print("COHERENCE-DRIVEN OPTIMIZATION DEMO")
    print("=" * 70)
    print("\nObjective: Maximize system coherence while optimizing")
    print("Method: Heavy weighting on CHRONOSONIC coherence metrics")
    print()
    
    # Configure for coherence focus
    config = IntegrationConfig(
        v6_max_iterations=30,
        cs_use_simplified=False,  # Full 7-chakra system
        param_mapping_mode="harmonic",
        objective_weights={
            'optimization': 0.2,
            'phi_discovery': 0.1,
            'coherence': 0.7  # Heavy coherence focus
        }
    )
    
    bridge = MetaChronosonicBridge(config)
    
    # Simple optimization objective
    def coherence_objective(params):
        """Simple objective to test coherence influence"""
        # Just minimize distance from center
        center = 1.5
        return sum((v - center)**2 for v in params.values())
    
    # Random initial state
    initial = {f'x{i}': np.random.uniform(0.5, 2.5) for i in range(7)}
    
    print("Running coherence-focused optimization...")
    
    best, scores = bridge.optimize_integrated(
        coherence_objective,
        initial,
        max_iterations=30
    )
    
    # Results
    final_state = bridge.chronosonic.get_system_state()
    
    print(f"\nFinal System State:")
    print(f"  Chakra coherence: {final_state['chakra_coherence']:.3f}")
    print(f"  I_AM coherence: {final_state['iam_metrics']['coherence']:.3f}")
    print(f"  Active chakras: {final_state['active_chakras']}/7")
    print(f"  Frequency matrix determinant: {final_state['frequency_matrix_determinant']:.3f}")
    
    print("\nThis demonstrates how CHRONOSONIC coherence metrics can")
    print("guide the optimization process toward states of higher")
    print("system-wide harmony and synchronization.")


if __name__ == "__main__":
    # Run φ discovery demo
    demo_phi_discovery()
    
    # Run coherence optimization demo
    demo_coherence_optimization()
    
    print("\n✅ Demos complete! Check the JSON files for detailed results.")