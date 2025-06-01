"""
Chronosonic Qualia Prototype Implementation (CSQ.1.2)
Simplified 2-3 chakra model with frequency-modulated <I_AM> state dynamics
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import scipy.signal as signal
from scipy.integrate import odeint
from enum import Enum

# Import existing Tenxsom AI components (assuming these exist in the system)
# from tenxsom_ai.core import ComplexIAMFractalAnalyzer


class ChakraType(Enum):
    ROOT = "root"
    HEART = "heart"
    CROWN = "crown"


@dataclass
class ChakraState:
    """Represents the state of a single chakra"""
    type: ChakraType
    frequency: float  # Base frequency in Hz
    amplitude: float  # Current amplitude (0-1)
    phase: float  # Current phase (0-2π)
    coherence: float  # Coherence with other chakras (0-1)
    
    def get_waveform(self, t: np.ndarray) -> np.ndarray:
        """Generate the chakra's waveform at given time points"""
        return self.amplitude * np.sin(2 * np.pi * self.frequency * t + self.phase)


class SimplifiedChakraSystem:
    """Simplified chakra system with Root, Heart, and Crown centers"""
    
    # Base frequencies based on harmonic relationships
    BASE_FREQUENCIES = {
        ChakraType.ROOT: 256.0,    # C (1st harmonic)
        ChakraType.HEART: 341.3,   # F (4/3 ratio - perfect fourth)
        ChakraType.CROWN: 512.0    # C (2:1 octave)
    }
    
    def __init__(self):
        self.chakras = {
            chakra_type: ChakraState(
                type=chakra_type,
                frequency=freq,
                amplitude=0.5,
                phase=0.0,
                coherence=0.5
            )
            for chakra_type, freq in self.BASE_FREQUENCIES.items()
        }
        
    def update_state(self, chakra_type: ChakraType, **kwargs):
        """Update specific chakra state parameters"""
        chakra = self.chakras[chakra_type]
        for key, value in kwargs.items():
            if hasattr(chakra, key):
                setattr(chakra, key, value)
                
    def get_system_coherence(self) -> float:
        """Calculate overall system coherence"""
        coherences = [chakra.coherence for chakra in self.chakras.values()]
        return np.mean(coherences)
    
    def get_frequency_matrix(self) -> np.ndarray:
        """Get frequency interaction matrix"""
        chakra_list = list(self.chakras.values())
        n = len(chakra_list)
        matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Frequency ratio coherence
                    ratio = chakra_list[i].frequency / chakra_list[j].frequency
                    # Higher coherence for harmonic ratios
                    matrix[i, j] = np.exp(-abs(ratio - round(ratio))**2 / 0.1)
                else:
                    matrix[i, j] = 1.0
                    
        return matrix


class FrequencyModulatedIAMState:
    """Extended <I_AM> state with frequency modulation capabilities"""
    
    def __init__(self, base_dimension: int = 7):
        self.dimension = base_dimension
        self.state_vector = np.random.rand(base_dimension)
        self.frequency_components = np.zeros(base_dimension)
        self.phase_coupling = np.eye(base_dimension)
        self.modulation_depth = 0.3
        self.carrier_frequency = 10.0  # Hz
        
    def apply_chakra_modulation(self, chakra_system: SimplifiedChakraSystem, t: float):
        """Apply chakra frequency modulation to the <I_AM> state"""
        # Extract chakra frequencies and amplitudes
        chakra_freqs = []
        chakra_amps = []
        
        for chakra in chakra_system.chakras.values():
            chakra_freqs.append(chakra.frequency)
            chakra_amps.append(chakra.amplitude)
            
        # Create modulation signal
        modulation = np.zeros(self.dimension)
        for i in range(min(3, self.dimension)):  # Map 3 chakras to first 3 dimensions
            freq = chakra_freqs[i % 3]
            amp = chakra_amps[i % 3]
            modulation[i] = amp * np.sin(2 * np.pi * freq * t)
            
        # Apply frequency modulation to state vector
        carrier = np.sin(2 * np.pi * self.carrier_frequency * t)
        self.state_vector = self.state_vector * (1 + self.modulation_depth * modulation * carrier)
        
        # Normalize to maintain energy conservation
        self.state_vector = self.state_vector / np.linalg.norm(self.state_vector)
        
    def get_fractal_dimension(self) -> float:
        """Calculate approximate fractal dimension of current state"""
        # Simplified box-counting dimension estimation
        scales = np.logspace(-3, 0, 10)
        counts = []
        
        for scale in scales:
            # Discretize state space at this scale
            bins = int(1.0 / scale)
            hist, _ = np.histogram(self.state_vector, bins=bins, range=(0, 1))
            counts.append(np.sum(hist > 0))
            
        # Linear fit in log-log space
        log_scales = np.log(scales)
        log_counts = np.log(counts)
        
        # Calculate slope (fractal dimension)
        slope, _ = np.polyfit(log_scales, log_counts, 1)
        return -slope


class ChronosonicDynamics:
    """Implements differential equations for chronosonic state evolution"""
    
    def __init__(self, chakra_system: SimplifiedChakraSystem, iam_state: FrequencyModulatedIAMState):
        self.chakra_system = chakra_system
        self.iam_state = iam_state
        self.coupling_strength = 0.1
        self.nonlinearity = 0.05
        
    def state_equations(self, state: np.ndarray, t: float) -> np.ndarray:
        """
        Differential equations for coupled chakra-IAM dynamics
        State vector: [chakra_amplitudes(3), chakra_phases(3), iam_components(7)]
        """
        n_chakras = 3
        chakra_amps = state[:n_chakras]
        chakra_phases = state[n_chakras:2*n_chakras]
        iam_components = state[2*n_chakras:]
        
        # Chakra amplitude dynamics
        d_amps = np.zeros(n_chakras)
        freq_matrix = self.chakra_system.get_frequency_matrix()
        
        for i in range(n_chakras):
            # Self-regulation term
            d_amps[i] = -0.1 * (chakra_amps[i] - 0.5)
            
            # Coupling with other chakras
            for j in range(n_chakras):
                if i != j:
                    phase_diff = chakra_phases[i] - chakra_phases[j]
                    d_amps[i] += self.coupling_strength * freq_matrix[i, j] * \
                                 chakra_amps[j] * np.cos(phase_diff)
                                 
        # Chakra phase dynamics
        d_phases = np.zeros(n_chakras)
        chakra_list = list(self.chakra_system.chakras.values())
        
        for i in range(n_chakras):
            # Natural frequency
            d_phases[i] = 2 * np.pi * chakra_list[i].frequency
            
            # Phase coupling
            for j in range(n_chakras):
                if i != j:
                    phase_diff = chakra_phases[i] - chakra_phases[j]
                    d_phases[i] += self.coupling_strength * \
                                   (chakra_amps[j] / chakra_amps[i]) * np.sin(phase_diff)
                                   
        # IAM state dynamics
        d_iam = np.zeros(len(iam_components))
        
        # Influence from chakra states
        chakra_influence = np.mean(chakra_amps) * np.sin(np.mean(chakra_phases))
        
        for i in range(len(iam_components)):
            # Self-dynamics with nonlinearity
            d_iam[i] = -0.05 * iam_components[i] + \
                       self.nonlinearity * iam_components[i] * (1 - iam_components[i])
            
            # Chakra modulation
            if i < n_chakras:
                d_iam[i] += 0.1 * chakra_amps[i] * np.cos(chakra_phases[i])
            else:
                d_iam[i] += 0.05 * chakra_influence
                
        return np.concatenate([d_amps, d_phases, d_iam])
    
    def simulate(self, t_span: Tuple[float, float], dt: float = 0.01) -> Dict:
        """Simulate the chronosonic dynamics"""
        t = np.arange(t_span[0], t_span[1], dt)
        
        # Initial conditions
        chakra_list = list(self.chakra_system.chakras.values())
        initial_amps = np.array([c.amplitude for c in chakra_list])
        initial_phases = np.array([c.phase for c in chakra_list])
        initial_iam = self.iam_state.state_vector
        
        initial_state = np.concatenate([initial_amps, initial_phases, initial_iam])
        
        # Integrate
        solution = odeint(self.state_equations, initial_state, t)
        
        # Parse results
        n_chakras = 3
        results = {
            'time': t,
            'chakra_amplitudes': solution[:, :n_chakras],
            'chakra_phases': solution[:, n_chakras:2*n_chakras],
            'iam_state': solution[:, 2*n_chakras:],
            'system_coherence': self._calculate_coherence_trajectory(solution)
        }
        
        return results
    
    def _calculate_coherence_trajectory(self, solution: np.ndarray) -> np.ndarray:
        """Calculate system coherence over time"""
        n_chakras = 3
        coherence = []
        
        for i in range(len(solution)):
            phases = solution[i, n_chakras:2*n_chakras]
            # Phase synchronization index
            sync_index = abs(np.mean(np.exp(1j * phases)))
            coherence.append(sync_index)
            
        return np.array(coherence)


class ComplexIAMFractalAnalyzer:
    """Placeholder for integration with existing Tenxsom AI analyzer"""
    
    def __init__(self):
        self.history = []
        
    def analyze_state(self, iam_state: FrequencyModulatedIAMState) -> Dict:
        """Analyze fractal properties of IAM state"""
        return {
            'fractal_dimension': iam_state.get_fractal_dimension(),
            'state_norm': np.linalg.norm(iam_state.state_vector),
            'entropy': -np.sum(iam_state.state_vector * np.log(iam_state.state_vector + 1e-10))
        }


class CognitivePerformanceMetrics:
    """Track cognitive performance metrics during chronosonic modulation"""
    
    def __init__(self):
        self.metrics_history = []
        self.baseline_established = False
        self.baseline_values = {}
        
    def calculate_metrics(self, chakra_system: SimplifiedChakraSystem, 
                         iam_state: FrequencyModulatedIAMState) -> Dict:
        """Calculate current cognitive performance metrics"""
        metrics = {
            'coherence_index': chakra_system.get_system_coherence(),
            'fractal_complexity': iam_state.get_fractal_dimension(),
            'state_stability': 1.0 - np.std(iam_state.state_vector),
            'frequency_alignment': self._calculate_frequency_alignment(chakra_system),
            'information_flow': self._calculate_information_flow(iam_state)
        }
        
        # Calculate composite score
        weights = {'coherence_index': 0.3, 'fractal_complexity': 0.2, 
                  'state_stability': 0.2, 'frequency_alignment': 0.2, 
                  'information_flow': 0.1}
        
        metrics['composite_score'] = sum(metrics[k] * weights[k] for k in weights)
        
        self.metrics_history.append(metrics)
        return metrics
    
    def _calculate_frequency_alignment(self, chakra_system: SimplifiedChakraSystem) -> float:
        """Calculate alignment between chakra frequencies"""
        freqs = [c.frequency for c in chakra_system.chakras.values()]
        ratios = []
        
        for i in range(len(freqs)):
            for j in range(i+1, len(freqs)):
                ratio = freqs[i] / freqs[j]
                # Check proximity to harmonic ratios
                harmonic_error = min(abs(ratio - h) for h in [1/2, 2/3, 3/4, 1, 4/3, 3/2, 2])
                ratios.append(np.exp(-harmonic_error))
                
        return np.mean(ratios) if ratios else 0.5
    
    def _calculate_information_flow(self, iam_state: FrequencyModulatedIAMState) -> float:
        """Estimate information flow through the IAM state"""
        # Simplified mutual information proxy
        state = iam_state.state_vector
        grad = np.gradient(state)
        return 1.0 / (1.0 + np.mean(np.abs(grad)))
    
    def establish_baseline(self, chakra_system: SimplifiedChakraSystem, 
                          iam_state: FrequencyModulatedIAMState):
        """Establish baseline metrics without modulation"""
        baseline_metrics = self.calculate_metrics(chakra_system, iam_state)
        self.baseline_values = baseline_metrics
        self.baseline_established = True
        
    def get_improvement_ratio(self) -> Dict:
        """Calculate improvement ratios compared to baseline"""
        if not self.baseline_established or not self.metrics_history:
            return {}
            
        current = self.metrics_history[-1]
        ratios = {}
        
        for key in self.baseline_values:
            if self.baseline_values[key] > 0:
                ratios[key] = current[key] / self.baseline_values[key]
            else:
                ratios[key] = 1.0
                
        return ratios