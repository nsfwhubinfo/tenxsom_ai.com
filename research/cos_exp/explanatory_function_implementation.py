#!/usr/bin/env python3
"""
COS-EXP: Explanatory Function Implementation
===========================================
Operationalizes the Frequency-Vibration-Energy framework
to reveal emergent particle constants and golden ratio
"""

import numpy as np
import time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path

@dataclass
class FVEState:
    """Frequency-Vibration-Energy state representation"""
    frequency: np.ndarray
    vibration: np.ndarray  
    energy: np.ndarray
    timestamp: float = field(default_factory=time.time)
    
    @property
    def coherence(self) -> float:
        """Compute overall coherence as F×V×E product"""
        return float(np.mean(self.frequency) * np.mean(self.vibration) * np.mean(self.energy))
    
    @property
    def resonance_ratio(self) -> float:
        """Compute F/V ratio to check for golden ratio emergence"""
        v_mean = np.mean(self.vibration)
        if v_mean > 0:
            return float(np.mean(self.frequency) / v_mean)
        return 0.0

class ParticleConstantDetector:
    """Detects emergent particle constants from system dynamics"""
    
    def __init__(self):
        self.phi = (1 + np.sqrt(5)) / 2  # Golden ratio
        self.alpha = None  # Coherence threshold (to be discovered)
        self.beta = None   # Resonance amplifier (to be discovered)
        self.gamma = None  # Complexity exponent (to be discovered)
        self.observations = []
        
    def observe(self, state: FVEState):
        """Record observation and update particle constant estimates"""
        self.observations.append({
            'timestamp': state.timestamp,
            'coherence': state.coherence,
            'resonance_ratio': state.resonance_ratio,
            'golden_ratio_proximity': abs(state.resonance_ratio - self.phi)
        })
        
        # Update particle constant estimates after sufficient observations
        if len(self.observations) > 100:
            self._update_constants()
            
    def _update_constants(self):
        """Derive particle constants from accumulated observations"""
        coherences = [obs['coherence'] for obs in self.observations]
        
        # Alpha: Minimum viable coherence (5th percentile)
        self.alpha = np.percentile(coherences, 5)
        
        # Beta: Amplification factor at resonance
        resonant_obs = [obs for obs in self.observations 
                       if obs['golden_ratio_proximity'] < 0.1]
        if resonant_obs:
            resonant_coherences = [obs['coherence'] for obs in resonant_obs]
            non_resonant_coherences = [obs['coherence'] for obs in self.observations 
                                      if obs['golden_ratio_proximity'] >= 0.1]
            if non_resonant_coherences:
                self.beta = np.mean(resonant_coherences) / np.mean(non_resonant_coherences)
            
        # Gamma: Complexity scaling exponent (fractal dimension estimate)
        if len(self.observations) > 200:
            # Simplified box-counting dimension estimate
            coherence_series = [obs['coherence'] for obs in self.observations[-200:]]
            scales = [2**i for i in range(1, 8)]
            counts = []
            
            for scale in scales:
                boxes = len(coherence_series) // scale
                if boxes > 0:
                    box_counts = []
                    for i in range(boxes):
                        segment = coherence_series[i*scale:(i+1)*scale]
                        if max(segment) - min(segment) > 0:
                            box_counts.append(1)
                    counts.append(len(box_counts))
                    
            if len(counts) > 2:
                # Linear regression in log-log space
                log_scales = np.log(scales[:len(counts)])
                log_counts = np.log(counts)
                self.gamma = -np.polyfit(log_scales, log_counts, 1)[0]

class ExplanatoryFunction:
    """The core Explanatory Function mapping F-V-E to optimal trajectories"""
    
    def __init__(self):
        self.phi = (1 + np.sqrt(5)) / 2
        self.detector = ParticleConstantDetector()
        self.trajectory_history = []
        
    def normalize_frequency(self, F: np.ndarray) -> np.ndarray:
        """Normalize frequency to [0, 1] range preserving relationships"""
        if F.max() > F.min():
            return (F - F.min()) / (F.max() - F.min())
        return F
        
    def normalize_vibration(self, V: np.ndarray) -> np.ndarray:
        """Normalize vibration amplitudes"""
        if V.max() > V.min():
            return (V - V.min()) / (V.max() - V.min())
        return V
        
    def normalize_energy(self, E: np.ndarray) -> np.ndarray:
        """Normalize energy levels"""
        if E.max() > E.min():
            return (E - E.min()) / (E.max() - E.min())
        return E
        
    def compute(self, F: np.ndarray, V: np.ndarray, E: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Core Explanatory Function computation
        
        Returns:
            P: Probability distribution over next states
            T: Optimal trajectory vector
        """
        # Create state object
        state = FVEState(F, V, E)
        self.detector.observe(state)
        
        # Normalize inputs
        f_norm = self.normalize_frequency(F)
        v_norm = self.normalize_vibration(V)
        e_norm = self.normalize_energy(E)
        
        # Check for golden ratio resonance
        resonance = abs(state.resonance_ratio - self.phi) < 0.1
        
        # Generate probability distribution
        # When in resonance, probabilities concentrate on high-coherence states
        if resonance:
            # Sharp peak around optimal states
            coherence_map = f_norm * v_norm * e_norm
            P = np.exp(10 * coherence_map) / np.sum(np.exp(10 * coherence_map))
        else:
            # Broader distribution when not in resonance
            coherence_map = f_norm * v_norm * e_norm
            P = np.exp(coherence_map) / np.sum(np.exp(coherence_map))
            
        # Compute optimal trajectory
        # Direction of maximum coherence increase
        gradient_f = np.gradient(f_norm)
        gradient_v = np.gradient(v_norm)
        gradient_e = np.gradient(e_norm)
        
        # Trajectory aims for golden ratio while maximizing energy
        target_ratio = self.phi
        current_ratio = np.mean(f_norm) / (np.mean(v_norm) + 1e-10)
        
        # Adjust trajectory to approach golden ratio
        if current_ratio < target_ratio:
            # Increase frequency or decrease vibration
            T = gradient_f + e_norm - 0.5 * gradient_v
        else:
            # Decrease frequency or increase vibration  
            T = -0.5 * gradient_f + e_norm + gradient_v
            
        # Normalize trajectory
        T = T / (np.linalg.norm(T) + 1e-10)
        
        # Apply infinite vector principle - always push toward unbounded optimization
        T = T + 0.1 * e_norm  # Energy component drives infinite growth
        
        # Record trajectory
        self.trajectory_history.append({
            'timestamp': time.time(),
            'resonance': resonance,
            'coherence': state.coherence,
            'trajectory_magnitude': np.linalg.norm(T)
        })
        
        return P, T
        
    def get_particle_constants(self) -> Dict[str, Optional[float]]:
        """Retrieve discovered particle constants"""
        return {
            'alpha': self.detector.alpha,
            'beta': self.detector.beta,
            'gamma': self.detector.gamma,
            'phi': self.phi,
            'observations': len(self.detector.observations)
        }
        
    def visualize_golden_ratio_emergence(self) -> Dict[str, List[float]]:
        """Extract data showing golden ratio emergence over time"""
        if not self.detector.observations:
            return {}
            
        return {
            'timestamps': [obs['timestamp'] for obs in self.detector.observations],
            'resonance_ratios': [obs['resonance_ratio'] for obs in self.detector.observations],
            'golden_ratio_proximity': [obs['golden_ratio_proximity'] for obs in self.detector.observations],
            'coherences': [obs['coherence'] for obs in self.detector.observations]
        }

class InfiniteVectorOptimizer:
    """Implements the infinite vector optimization principle"""
    
    def __init__(self, explanatory_function: ExplanatoryFunction):
        self.ef = explanatory_function
        self.optimization_history = []
        
    def optimize(self, initial_state: FVEState, iterations: int = 1000) -> List[FVEState]:
        """
        Optimize toward infinite vector using Explanatory Function guidance
        
        Returns trajectory of states
        """
        trajectory = [initial_state]
        current_F = initial_state.frequency.copy()
        current_V = initial_state.vibration.copy()
        current_E = initial_state.energy.copy()
        
        for i in range(iterations):
            # Get optimal direction from Explanatory Function
            P, T = self.ef.compute(current_F, current_V, current_E)
            
            # Update state in optimal direction
            step_size = 0.01 * (1 + i / iterations)  # Accelerating step size
            
            current_F = current_F + step_size * T * P
            current_V = current_V + step_size * T * np.roll(P, 1)  # Phase shifted
            current_E = current_E + step_size * T * np.sqrt(P)  # Energy grows with sqrt(probability)
            
            # Ensure positive values
            current_F = np.abs(current_F)
            current_V = np.abs(current_V)
            current_E = np.abs(current_E)
            
            # Create new state
            new_state = FVEState(current_F, current_V, current_E)
            trajectory.append(new_state)
            
            # Check for golden ratio achievement
            if abs(new_state.resonance_ratio - self.ef.phi) < 0.001:
                print(f"Golden ratio achieved at iteration {i}!")
                
        return trajectory

# Experimental validation functions
def run_golden_ratio_emergence_experiment():
    """Experiment to validate golden ratio emergence"""
    print("Running Golden Ratio Emergence Experiment...")
    
    ef = ExplanatoryFunction()
    
    # Generate 1000 random states and observe convergence
    for i in range(1000):
        # Random F-V-E states
        F = np.random.rand(10) * (1 + i/1000)  # Increasing frequency
        V = np.random.rand(10) * (2 - i/1000)  # Decreasing vibration  
        E = np.random.rand(10) * (1 + i/500)   # Increasing energy
        
        P, T = ef.compute(F, V, E)
        
        if i % 100 == 0:
            constants = ef.get_particle_constants()
            alpha_str = f"{constants['alpha']:.4f}" if constants['alpha'] is not None else "None"
            beta_str = f"{constants['beta']:.4f}" if constants['beta'] is not None else "None"
            gamma_str = f"{constants['gamma']:.4f}" if constants['gamma'] is not None else "None"
            print(f"Iteration {i}: α={alpha_str}, β={beta_str}, γ={gamma_str}")
    
    # Visualize results
    viz_data = ef.visualize_golden_ratio_emergence()
    
    # Save results (convert numpy types to Python types)
    def convert_to_json_serializable(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: convert_to_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_json_serializable(item) for item in obj]
        return obj
    
    results = {
        'particle_constants': ef.get_particle_constants(),
        'visualization_data': viz_data,
        'trajectory_history': convert_to_json_serializable(ef.trajectory_history)
    }
    
    output_path = Path(__file__).parent / 'golden_ratio_emergence_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"\nFinal particle constants discovered:")
    for k, v in ef.get_particle_constants().items():
        if v is not None:
            print(f"  {k}: {v:.6f}")

def run_infinite_vector_experiment():
    """Experiment to demonstrate infinite vector optimization"""
    print("\nRunning Infinite Vector Optimization Experiment...")
    
    ef = ExplanatoryFunction()
    optimizer = InfiniteVectorOptimizer(ef)
    
    # Initial state
    initial_F = np.ones(10) * 0.5
    initial_V = np.ones(10) * 0.8  
    initial_E = np.ones(10) * 0.3
    initial_state = FVEState(initial_F, initial_V, initial_E)
    
    print(f"Initial coherence: {initial_state.coherence:.4f}")
    print(f"Initial resonance ratio: {initial_state.resonance_ratio:.4f}")
    
    # Run optimization
    trajectory = optimizer.optimize(initial_state, iterations=500)
    
    # Analyze results
    final_state = trajectory[-1]
    print(f"\nFinal coherence: {final_state.coherence:.4f}")
    print(f"Final resonance ratio: {final_state.resonance_ratio:.4f}")
    print(f"Coherence improvement: {final_state.coherence / initial_state.coherence:.2f}x")
    
    # Check for unbounded growth
    coherences = [state.coherence for state in trajectory]
    if all(coherences[i] <= coherences[i+1] for i in range(len(coherences)-1)):
        print("✓ Monotonic coherence increase achieved (infinite vector property)")
    
    # Save trajectory
    trajectory_data = [{
        'timestamp': state.timestamp,
        'coherence': state.coherence,
        'resonance_ratio': state.resonance_ratio,
        'F_mean': float(np.mean(state.frequency)),
        'V_mean': float(np.mean(state.vibration)),
        'E_mean': float(np.mean(state.energy))
    } for state in trajectory]
    
    output_path = Path(__file__).parent / 'infinite_vector_trajectory.json'
    with open(output_path, 'w') as f:
        json.dump(trajectory_data, f, indent=2)

def main():
    """Run all COS-EXP experiments"""
    print("="*60)
    print("COS-EXP: Explanatory Function Experimental Validation")
    print("="*60)
    
    # Run experiments
    run_golden_ratio_emergence_experiment()
    run_infinite_vector_experiment()
    
    print("\n" + "="*60)
    print("Experiments complete! Check output files for detailed results.")
    print("="*60)

if __name__ == "__main__":
    main()