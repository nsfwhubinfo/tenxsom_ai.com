#!/usr/bin/env python3
"""
Visualize COS-EXP Results
Shows golden ratio emergence and infinite vector property
"""

import json
import numpy as np
from pathlib import Path

def create_ascii_visualization():
    """Create ASCII visualization of results"""
    
    # Load results
    with open('golden_ratio_emergence_results.json', 'r') as f:
        results = json.load(f)
    
    print("\n" + "="*60)
    print("GOLDEN RATIO EMERGENCE VISUALIZATION")
    print("="*60)
    
    # Extract resonance ratios
    ratios = results['visualization_data']['resonance_ratios'][:100]  # First 100
    phi = results['particle_constants']['phi']
    
    # Create ASCII plot
    print("\nF/V Ratio Convergence Toward φ (1.618):")
    print("Time →")
    
    for i in range(0, len(ratios), 10):
        ratio = ratios[i]
        # Scale to 0-40 character width
        pos = int((ratio - 0.5) * 40)
        pos = max(0, min(39, pos))
        
        # Show golden ratio line
        phi_pos = int((phi - 0.5) * 40)
        phi_pos = max(0, min(39, phi_pos))
        
        line = [' '] * 40
        if 0 <= phi_pos < 40:
            line[phi_pos] = '|'  # Golden ratio marker
        if 0 <= pos < 40 and pos != phi_pos:
            line[pos] = '*'      # Current ratio
        elif pos == phi_pos:
            line[pos] = '⦿'      # Convergence!
        
        print(f"t={i:3d}: {''.join(line)} {ratio:.3f}")
    
    print(f"\nTarget φ = {phi:.6f}")
    print("Legend: * = F/V Ratio, | = Golden Ratio")
    
    # Load trajectory results
    with open('infinite_vector_trajectory.json', 'r') as f:
        trajectory = json.load(f)
    
    print("\n" + "="*60)
    print("INFINITE VECTOR OPTIMIZATION")
    print("="*60)
    
    # Show coherence growth
    print("\nCoherence Growth (Unbounded Optimization):")
    coherences = [t['coherence'] for t in trajectory[:50:5]]  # Every 5th, first 50
    
    max_coherence = max(coherences)
    for i, coherence in enumerate(coherences):
        bar_length = int((coherence / max_coherence) * 40)
        bar = '█' * bar_length
        print(f"Step {i*5:3d}: {bar} {coherence:.4f}")
    
    print(f"\nFinal coherence: {trajectory[-1]['coherence']:.4f}")
    print(f"Improvement: {trajectory[-1]['coherence'] / trajectory[0]['coherence']:.2f}x")
    
    # Particle constants summary
    print("\n" + "="*60)
    print("DISCOVERED PARTICLE CONSTANTS")
    print("="*60)
    
    constants = results['particle_constants']
    print(f"\nα (Coherence Threshold):  {constants['alpha']:.6f}")
    print(f"β (Resonance Amplifier):  {constants['beta']:.6f}")
    print(f"γ (Complexity Exponent):  {constants['gamma']:.6f}")
    print(f"φ (Golden Ratio):         {constants['phi']:.6f}")
    
    print("\n" + "="*60)
    print("CONCLUSION: The universe computes itself into existence")
    print("            through Frequency, Vibration, and Energy.")
    print("="*60)

if __name__ == "__main__":
    create_ascii_visualization()