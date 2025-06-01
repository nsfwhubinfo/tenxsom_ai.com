#!/usr/bin/env python3
"""
Quantized Feedback Processor for Meta-Optimization
==================================================
Implements symbolic abstraction of complex system states
into high-signal "dogfood bits" for accelerated optimization
"""

import numpy as np
from typing import Dict, Tuple, Any, List
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys

# Import COS-EXP components
sys.path.append(str(Path(__file__).parent.parent / "cos_exp"))
from explanatory_function_implementation import ExplanatoryFunction, FVEState

@dataclass
class QuantizedSymbol:
    """Symbolic representation of system state"""
    symbol_id: str
    frequency_band: int  # 0-9 quantized frequency
    vibration_class: str  # 'low', 'medium', 'high', 'resonant'
    energy_level: int     # 0-9 quantized energy
    coherence: float
    particle_alignment: Dict[str, float]  # α, β, γ, φ alignment
    
    def to_string(self) -> str:
        """Convert to compact string representation"""
        return f"Q[F{self.frequency_band}V{self.vibration_class[0].upper()}E{self.energy_level}]"

class QuantizedFeedbackProcessor:
    """Processes complex system feedback into quantized symbols"""
    
    def __init__(self):
        self.explanatory_function = ExplanatoryFunction()
        self.quantization_levels = 10
        self.vibration_classes = {
            'low': (0.0, 0.25),
            'medium': (0.25, 0.75),
            'high': (0.75, 0.95),
            'resonant': (0.95, 1.05)  # Near golden ratio
        }
        self.symbol_cache = {}
        self.particle_constants = {
            'alpha': 0.223,
            'beta': 1.344,
            'gamma': 1.075,
            'phi': 1.618
        }
        
    def extract_frequency(self, complex_state: Dict[str, Any]) -> np.ndarray:
        """Extract frequency signature from complex state"""
        # Analyze state transition rates
        if 'state_transitions' in complex_state:
            transitions = complex_state['state_transitions']
            if isinstance(transitions, list):
                # Calculate transition frequencies
                intervals = np.diff([t['timestamp'] for t in transitions])
                if len(intervals) > 0:
                    frequencies = 1.0 / (intervals + 1e-10)
                    return frequencies[:10]  # Take first 10
                    
        # Default frequency pattern
        return np.random.rand(10) * 2.0
        
    def extract_vibration(self, complex_state: Dict[str, Any]) -> np.ndarray:
        """Extract vibration amplitude patterns"""
        # Analyze amplitude variations
        if 'metrics' in complex_state:
            metrics = complex_state['metrics']
            if isinstance(metrics, dict):
                values = list(metrics.values())
                if values:
                    # Calculate amplitude variations
                    amplitudes = np.array([float(v) for v in values if isinstance(v, (int, float))])
                    if len(amplitudes) > 0:
                        variations = np.abs(np.diff(amplitudes))
                        return np.pad(variations, (0, 10-len(variations)), 'constant')[:10]
                        
        # Default vibration pattern
        return np.random.rand(10)
        
    def extract_energy(self, complex_state: Dict[str, Any]) -> np.ndarray:
        """Extract energy/information density"""
        # Calculate information density
        energy_components = []
        
        # Computational intensity
        if 'cpu_usage' in complex_state:
            energy_components.append(complex_state['cpu_usage'] / 100.0)
            
        # Memory pressure
        if 'memory_usage' in complex_state:
            energy_components.append(complex_state['memory_usage'] / 100.0)
            
        # Information throughput
        if 'throughput' in complex_state:
            energy_components.append(min(complex_state['throughput'] / 1000.0, 1.0))
            
        # Coherence level
        if 'coherence' in complex_state:
            energy_components.append(complex_state['coherence'])
            
        if energy_components:
            base_energy = np.mean(energy_components)
            return np.ones(10) * base_energy + np.random.rand(10) * 0.1
        else:
            return np.random.rand(10) * 0.5 + 0.5
            
    def quantize_to_band(self, value: float, levels: int) -> int:
        """Quantize continuous value to discrete band"""
        return min(int(value * levels), levels - 1)
        
    def classify_vibration(self, vibration_mean: float, frequency_mean: float) -> str:
        """Classify vibration based on resonance with golden ratio"""
        if frequency_mean > 0:
            ratio = vibration_mean / frequency_mean
            proximity_to_phi = abs(ratio - self.particle_constants['phi'])
            
            if proximity_to_phi < 0.05:
                return 'resonant'
            elif vibration_mean > 0.75:
                return 'high'
            elif vibration_mean > 0.25:
                return 'medium'
            else:
                return 'low'
        return 'medium'
        
    def calculate_particle_alignment(self, F: np.ndarray, V: np.ndarray, E: np.ndarray) -> Dict[str, float]:
        """Calculate alignment with discovered particle constants"""
        coherence = np.mean(F) * np.mean(V) * np.mean(E)
        
        # Alpha alignment (coherence threshold)
        alpha_alignment = min(coherence / self.particle_constants['alpha'], 1.0)
        
        # Beta alignment (resonance amplification)
        if np.mean(V) > 0:
            ratio = np.mean(F) / np.mean(V)
            if abs(ratio - self.particle_constants['phi']) < 0.1:
                beta_alignment = self.particle_constants['beta']
            else:
                beta_alignment = 1.0
        else:
            beta_alignment = 0.5
            
        # Gamma alignment (complexity)
        complexity = np.std(F) * np.std(V) * np.std(E)
        gamma_alignment = complexity ** self.particle_constants['gamma']
        
        # Phi alignment (golden ratio)
        phi_alignment = 1.0 - abs(ratio - self.particle_constants['phi']) if np.mean(V) > 0 else 0.0
        
        return {
            'alpha': alpha_alignment,
            'beta': beta_alignment,
            'gamma': gamma_alignment,
            'phi': phi_alignment
        }
        
    def quantize(self, complex_state: Dict[str, Any]) -> QuantizedSymbol:
        """Convert complex state to quantized symbol"""
        # Extract F-V-E signatures
        F = self.extract_frequency(complex_state)
        V = self.extract_vibration(complex_state)
        E = self.extract_energy(complex_state)
        
        # Apply Explanatory Function
        P, T = self.explanatory_function.compute(F, V, E)
        
        # Calculate summary statistics
        f_mean = np.mean(F)
        v_mean = np.mean(V)
        e_mean = np.mean(E)
        
        # Quantize to discrete bands
        frequency_band = self.quantize_to_band(f_mean, self.quantization_levels)
        energy_level = self.quantize_to_band(e_mean, self.quantization_levels)
        vibration_class = self.classify_vibration(v_mean, f_mean)
        
        # Calculate coherence
        coherence = f_mean * v_mean * e_mean
        
        # Calculate particle alignment
        particle_alignment = self.calculate_particle_alignment(F, V, E)
        
        # Generate unique symbol ID
        symbol_str = f"F{frequency_band}V{vibration_class}E{energy_level}C{coherence:.3f}"
        symbol_id = hashlib.sha256(symbol_str.encode()).hexdigest()[:16]
        
        # Create quantized symbol
        symbol = QuantizedSymbol(
            symbol_id=symbol_id,
            frequency_band=frequency_band,
            vibration_class=vibration_class,
            energy_level=energy_level,
            coherence=coherence,
            particle_alignment=particle_alignment
        )
        
        # Cache for fast lookup
        self.symbol_cache[symbol_id] = {
            'symbol': symbol,
            'probability': P.tolist(),
            'trajectory': T.tolist(),
            'timestamp': complex_state.get('timestamp', 0)
        }
        
        return symbol
        
    def symbolic_distance(self, symbol1: QuantizedSymbol, symbol2: QuantizedSymbol) -> float:
        """Calculate distance between two symbols"""
        # Frequency distance
        f_dist = abs(symbol1.frequency_band - symbol2.frequency_band) / self.quantization_levels
        
        # Vibration distance
        v_map = {'low': 0, 'medium': 1, 'high': 2, 'resonant': 3}
        v_dist = abs(v_map[symbol1.vibration_class] - v_map[symbol2.vibration_class]) / 3.0
        
        # Energy distance
        e_dist = abs(symbol1.energy_level - symbol2.energy_level) / self.quantization_levels
        
        # Coherence distance
        c_dist = abs(symbol1.coherence - symbol2.coherence)
        
        # Weighted distance
        return 0.3 * f_dist + 0.3 * v_dist + 0.2 * e_dist + 0.2 * c_dist
        
    def find_similar_symbols(self, target: QuantizedSymbol, threshold: float = 0.2) -> List[QuantizedSymbol]:
        """Find symbols similar to target within threshold"""
        similar = []
        
        for cached in self.symbol_cache.values():
            symbol = cached['symbol']
            if self.symbolic_distance(target, symbol) < threshold:
                similar.append(symbol)
                
        return sorted(similar, key=lambda s: self.symbolic_distance(target, s))
        
    def extract_optimization_pattern(self, symbol_sequence: List[QuantizedSymbol]) -> Dict[str, Any]:
        """Extract optimization pattern from symbol sequence"""
        if not symbol_sequence:
            return {}
            
        # Analyze progression
        coherences = [s.coherence for s in symbol_sequence]
        
        # Check for improvement
        improvement_rate = (coherences[-1] - coherences[0]) / (len(coherences) * coherences[0] + 1e-10)
        
        # Find dominant patterns
        freq_bands = [s.frequency_band for s in symbol_sequence]
        vib_classes = [s.vibration_class for s in symbol_sequence]
        energy_levels = [s.energy_level for s in symbol_sequence]
        
        pattern = {
            'improvement_rate': improvement_rate,
            'coherence_trajectory': coherences,
            'dominant_frequency': max(set(freq_bands), key=freq_bands.count),
            'dominant_vibration': max(set(vib_classes), key=vib_classes.count),
            'average_energy': np.mean(energy_levels),
            'reaches_resonance': 'resonant' in vib_classes,
            'final_coherence': coherences[-1],
            'symbol_sequence': [s.to_string() for s in symbol_sequence]
        }
        
        return pattern


def test_quantization():
    """Test quantized feedback processing"""
    processor = QuantizedFeedbackProcessor()
    
    # Test state 1: Low performance
    state1 = {
        'timestamp': 1000,
        'state_transitions': [
            {'timestamp': 0}, {'timestamp': 100}, {'timestamp': 300}
        ],
        'metrics': {
            'latency': 50,
            'throughput': 100,
            'errors': 5
        },
        'cpu_usage': 30,
        'memory_usage': 40,
        'coherence': 0.3
    }
    
    # Test state 2: High performance
    state2 = {
        'timestamp': 2000,
        'state_transitions': [
            {'timestamp': 0}, {'timestamp': 10}, {'timestamp': 20}, 
            {'timestamp': 30}, {'timestamp': 40}
        ],
        'metrics': {
            'latency': 5,
            'throughput': 1000,
            'errors': 0
        },
        'cpu_usage': 80,
        'memory_usage': 70,
        'coherence': 0.9
    }
    
    # Process states
    symbol1 = processor.quantize(state1)
    symbol2 = processor.quantize(state2)
    
    print("Quantization Test Results")
    print("=" * 50)
    print(f"State 1 → {symbol1.to_string()}")
    print(f"  Coherence: {symbol1.coherence:.4f}")
    print(f"  Particle Alignment: {symbol1.particle_alignment}")
    print()
    print(f"State 2 → {symbol2.to_string()}")
    print(f"  Coherence: {symbol2.coherence:.4f}")
    print(f"  Particle Alignment: {symbol2.particle_alignment}")
    print()
    print(f"Symbol Distance: {processor.symbolic_distance(symbol1, symbol2):.4f}")
    
    # Extract pattern
    pattern = processor.extract_optimization_pattern([symbol1, symbol2])
    print(f"\nOptimization Pattern:")
    print(f"  Improvement Rate: {pattern['improvement_rate']:.2%}")
    print(f"  Reaches Resonance: {pattern['reaches_resonance']}")


if __name__ == "__main__":
    test_quantization()