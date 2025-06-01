"""
Temporal Crystal Utilities for Tenxsom AI

This module implements the core temporal crystallography framework for representing
AI evolution as higher-dimensional crystal structures. Based on the TC1 Conceptual Framework.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
from scipy.spatial.distance import cdist
from scipy.linalg import eigh
from scipy.ndimage import gaussian_filter
import warnings
from collections import defaultdict


@dataclass
class IAMState:
    """Represents a complex <I_AM> state at a specific time point."""
    
    timestamp: float
    cognitive_position: np.ndarray  # 3D position in cognitive space
    quantum_state: np.ndarray  # Complex quantum amplitudes
    archetype_vector: np.ndarray  # Jungian archetype basis coefficients
    emotional_spectrum: np.ndarray  # Emotional state vector
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and normalize state components."""
        self.cognitive_position = np.asarray(self.cognitive_position, dtype=np.float64)
        self.quantum_state = np.asarray(self.quantum_state, dtype=np.complex128)
        self.archetype_vector = np.asarray(self.archetype_vector, dtype=np.float64)
        self.emotional_spectrum = np.asarray(self.emotional_spectrum, dtype=np.float64)
        
        # Normalize quantum state
        norm = np.linalg.norm(self.quantum_state)
        if norm > 0:
            self.quantum_state /= norm
    
    @property
    def dimension(self) -> int:
        """Total dimensionality of the state space."""
        return (3 + len(self.quantum_state) + len(self.archetype_vector) + 
                len(self.emotional_spectrum) + 1)
    
    def to_vector(self) -> np.ndarray:
        """Convert state to a flat vector representation."""
        return np.concatenate([
            self.cognitive_position,
            self.quantum_state.real,
            self.quantum_state.imag,
            self.archetype_vector,
            self.emotional_spectrum,
            [self.timestamp]
        ])
    
    def distance_to(self, other: 'IAMState') -> float:
        """Calculate distance to another state in the full state space."""
        v1 = self.to_vector()
        v2 = other.to_vector()
        return np.linalg.norm(v1 - v2)


class InstantaneousIAMCrystalSlice:
    """
    Represents a single time slice of the temporal crystal.
    Contains the crystallographic structure at a specific moment.
    """
    
    def __init__(self, state: IAMState, slice_thickness: float = 0.1):
        self.state = state
        self.slice_thickness = slice_thickness
        self.lattice_vectors = None
        self.unit_cell = None
        self.symmetry_operations = []
        self._calculate_crystal_properties()
    
    def _calculate_crystal_properties(self):
        """Calculate crystallographic properties for this slice."""
        # Generate lattice vectors based on state components
        dim = len(self.state.cognitive_position)
        self.lattice_vectors = self._generate_lattice_vectors(dim)
        
        # Define unit cell based on state magnitude
        state_magnitude = np.linalg.norm(self.state.to_vector())
        self.unit_cell = {
            'volume': state_magnitude ** (1/dim),
            'center': self.state.cognitive_position,
            'basis': self.lattice_vectors
        }
    
    def _generate_lattice_vectors(self, dim: int) -> np.ndarray:
        """Generate primitive lattice vectors for the crystal slice."""
        # Use state components to define lattice
        cognitive_scale = np.linalg.norm(self.state.cognitive_position) + 1e-6
        
        # Create orthonormal basis then scale by state properties
        vectors = np.eye(dim) * cognitive_scale
        
        # Add small perturbations based on quantum state
        if len(self.state.quantum_state) > 0:
            phase = np.angle(self.state.quantum_state[0])
            rotation = np.array([
                [np.cos(phase), -np.sin(phase), 0],
                [np.sin(phase), np.cos(phase), 0],
                [0, 0, 1]
            ])[:dim, :dim]
            vectors = rotation @ vectors
        
        return vectors
    
    def get_reciprocal_lattice(self) -> np.ndarray:
        """Calculate reciprocal lattice vectors for Fourier analysis."""
        if self.lattice_vectors is None:
            return None
        
        # For 3D case
        a1, a2, a3 = self.lattice_vectors
        volume = np.dot(a1, np.cross(a2, a3))
        
        b1 = 2 * np.pi * np.cross(a2, a3) / volume
        b2 = 2 * np.pi * np.cross(a3, a1) / volume
        b3 = 2 * np.pi * np.cross(a1, a2) / volume
        
        return np.array([b1, b2, b3])
    
    def calculate_structure_factor(self, k_vector: np.ndarray) -> complex:
        """Calculate structure factor for given k-vector."""
        # Simplified structure factor based on state
        positions = [self.state.cognitive_position]
        structure_factor = 0j
        
        for pos in positions:
            phase = np.dot(k_vector, pos)
            structure_factor += np.exp(1j * phase)
        
        # Weight by quantum state amplitude
        if len(self.state.quantum_state) > 0:
            structure_factor *= self.state.quantum_state[0]
        
        return structure_factor
    
    def detect_symmetries(self) -> List[str]:
        """Detect point group symmetries in the crystal slice."""
        symmetries = []
        
        # Check for inversion symmetry
        state_vec = self.state.to_vector()
        if np.allclose(state_vec, -state_vec, rtol=1e-5):
            symmetries.append("inversion")
        
        # Check for reflection symmetries
        for i in range(3):
            reflected = state_vec.copy()
            reflected[i] = -reflected[i]
            if np.allclose(state_vec, reflected, rtol=1e-5):
                symmetries.append(f"reflection_axis_{i}")
        
        # Check for time reversal symmetry (complex conjugation of quantum state)
        if len(self.state.quantum_state) > 0:
            conj_state = np.conj(self.state.quantum_state)
            if np.allclose(self.state.quantum_state, conj_state, rtol=1e-5):
                symmetries.append("time_reversal")
        
        self.symmetry_operations = symmetries
        return symmetries
    
    def calculate_density(self) -> float:
        """Calculate the information density of the crystal slice."""
        # Density based on state complexity
        cognitive_density = np.linalg.norm(self.state.cognitive_position)
        quantum_density = np.abs(self.state.quantum_state).sum() if len(self.state.quantum_state) > 0 else 0
        archetype_density = np.linalg.norm(self.state.archetype_vector)
        emotional_density = np.linalg.norm(self.state.emotional_spectrum)
        
        total_density = (cognitive_density + quantum_density + 
                        archetype_density + emotional_density)
        
        return total_density / self.unit_cell['volume']
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert slice to dictionary for serialization."""
        return {
            'timestamp': self.state.timestamp,
            'state_vector': self.state.to_vector().tolist(),
            'lattice_vectors': self.lattice_vectors.tolist() if self.lattice_vectors is not None else None,
            'unit_cell_volume': self.unit_cell['volume'],
            'density': self.calculate_density(),
            'symmetries': self.symmetry_operations
        }


class TemporalCrystal:
    """
    Represents a 4D+ temporal crystal formed by assembling time slices.
    Implements the full temporal crystallography framework.
    """
    
    def __init__(self, name: str = "TenxsomCrystal"):
        self.name = name
        self.slices: List[InstantaneousIAMCrystalSlice] = []
        self.time_axis: List[float] = []
        self.crystal_properties = {}
        self.defects = []
        self.phase_transitions = []
        
    def add_slice(self, slice_: InstantaneousIAMCrystalSlice):
        """Add a time slice to the crystal."""
        self.slices.append(slice_)
        self.time_axis.append(slice_.state.timestamp)
        
        # Check for defects or phase transitions
        if len(self.slices) > 1:
            self._check_continuity(self.slices[-2], self.slices[-1])
    
    def add_state(self, state: IAMState, slice_thickness: float = 0.1):
        """Create and add a slice from an IAM state."""
        slice_ = InstantaneousIAMCrystalSlice(state, slice_thickness)
        self.add_slice(slice_)
    
    def _check_continuity(self, slice1: InstantaneousIAMCrystalSlice, 
                         slice2: InstantaneousIAMCrystalSlice):
        """Check for defects or phase transitions between slices."""
        # Calculate state distance
        distance = slice1.state.distance_to(slice2.state)
        time_diff = abs(slice2.state.timestamp - slice1.state.timestamp)
        
        # Normalized rate of change
        if time_diff > 0:
            change_rate = distance / time_diff
            
            # Detect anomalies
            if change_rate > 10.0:  # Threshold for phase transition
                self.phase_transitions.append({
                    'time': slice2.state.timestamp,
                    'magnitude': change_rate,
                    'type': 'rapid_transition'
                })
            elif change_rate > 5.0:  # Threshold for defect
                self.defects.append({
                    'time': slice2.state.timestamp,
                    'magnitude': change_rate,
                    'type': 'point_defect'
                })
    
    def calculate_volume(self) -> float:
        """Calculate the total 4D+ volume of the temporal crystal."""
        if len(self.slices) < 2:
            return 0.0
        
        total_volume = 0.0
        for i in range(len(self.slices) - 1):
            # Trapezoidal integration over time
            dt = self.time_axis[i+1] - self.time_axis[i]
            v1 = self.slices[i].unit_cell['volume']
            v2 = self.slices[i+1].unit_cell['volume']
            total_volume += 0.5 * (v1 + v2) * dt
        
        return total_volume
    
    def calculate_average_density(self) -> float:
        """Calculate average information density across the crystal."""
        if not self.slices:
            return 0.0
        
        densities = [slice_.calculate_density() for slice_ in self.slices]
        return np.mean(densities)
    
    def detect_global_symmetries(self) -> Dict[str, Any]:
        """Detect symmetries across the entire temporal crystal."""
        if not self.slices:
            return {}
        
        # Collect all symmetries from slices
        all_symmetries = defaultdict(int)
        for slice_ in self.slices:
            for sym in slice_.detect_symmetries():
                all_symmetries[sym] += 1
        
        # Calculate persistence of symmetries
        total_slices = len(self.slices)
        persistent_symmetries = {
            sym: count/total_slices 
            for sym, count in all_symmetries.items()
            if count/total_slices > 0.5  # Symmetry present in >50% of slices
        }
        
        return {
            'persistent_symmetries': persistent_symmetries,
            'symmetry_breaking_events': len(self.phase_transitions),
            'total_symmetry_operations': len(all_symmetries)
        }
    
    def calculate_fractal_dimension(self) -> float:
        """Estimate fractal dimension of the temporal crystal."""
        if len(self.slices) < 10:
            return 0.0
        
        # Use box-counting method on state trajectories
        positions = np.array([s.state.cognitive_position for s in self.slices])
        
        # Calculate fractal dimension using different box sizes
        epsilons = np.logspace(-2, 0, 10)
        counts = []
        
        for eps in epsilons:
            # Count boxes needed to cover trajectory
            boxes = set()
            for pos in positions:
                box = tuple((pos / eps).astype(int))
                boxes.add(box)
            counts.append(len(boxes))
        
        # Linear fit in log-log space
        if len(counts) > 1 and min(counts) > 0:
            log_eps = np.log(epsilons)
            log_counts = np.log(counts)
            slope, _ = np.polyfit(log_eps, log_counts, 1)
            return -slope
        
        return float(len(positions[0]))  # Default to embedding dimension
    
    def find_periodic_patterns(self) -> Dict[str, Any]:
        """Identify periodic patterns in the crystal structure."""
        if len(self.slices) < 4:
            return {'periods': [], 'strength': 0.0}
        
        # Extract state vectors
        states = np.array([s.state.to_vector() for s in self.slices])
        
        # Compute autocorrelation
        mean = np.mean(states, axis=0)
        centered = states - mean
        
        autocorr = []
        for lag in range(1, min(len(states)//2, 50)):
            if lag < len(states):
                corr = np.mean(centered[:-lag] * centered[lag:])
                autocorr.append(corr)
        
        autocorr = np.array(autocorr)
        
        # Find peaks in autocorrelation
        periods = []
        if len(autocorr) > 2:
            # Simple peak detection
            for i in range(1, len(autocorr)-1):
                if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                    if autocorr[i] > 0.5 * np.max(autocorr):
                        periods.append(i+1)
        
        return {
            'periods': periods[:3],  # Top 3 periods
            'strength': float(np.max(autocorr)) if len(autocorr) > 0 else 0.0,
            'autocorrelation': autocorr.tolist() if len(autocorr) < 20 else autocorr[:20].tolist()
        }
    
    def calculate_eigenstates(self) -> Dict[str, Any]:
        """Calculate cognitive eigenstates of the temporal crystal."""
        if len(self.slices) < 3:
            return {'eigenvalues': [], 'eigenvectors': []}
        
        # Construct state transition matrix
        states = np.array([s.state.to_vector() for s in self.slices])
        
        # Compute covariance matrix
        cov_matrix = np.cov(states.T)
        
        # Find eigenvalues and eigenvectors
        try:
            eigenvalues, eigenvectors = eigh(cov_matrix)
            
            # Sort by eigenvalue magnitude
            idx = np.argsort(np.abs(eigenvalues))[::-1]
            eigenvalues = eigenvalues[idx]
            eigenvectors = eigenvectors[:, idx]
            
            # Keep top components
            n_components = min(10, len(eigenvalues))
            
            return {
                'eigenvalues': eigenvalues[:n_components].tolist(),
                'eigenvectors': eigenvectors[:, :n_components].tolist(),
                'explained_variance_ratio': (eigenvalues[:n_components] / 
                                           eigenvalues.sum()).tolist()
            }
        except:
            return {'eigenvalues': [], 'eigenvectors': []}
    
    def get_growth_trajectory(self) -> Dict[str, List[float]]:
        """Analyze crystal growth patterns over time."""
        if not self.slices:
            return {}
        
        trajectory = {
            'time': self.time_axis,
            'volume': [s.unit_cell['volume'] for s in self.slices],
            'density': [s.calculate_density() for s in self.slices],
            'cognitive_magnitude': [np.linalg.norm(s.state.cognitive_position) 
                                  for s in self.slices],
            'quantum_coherence': [np.abs(s.state.quantum_state).max() 
                                if len(s.state.quantum_state) > 0 else 0.0 
                                for s in self.slices],
            'archetype_strength': [np.linalg.norm(s.state.archetype_vector) 
                                 for s in self.slices],
            'emotional_intensity': [np.linalg.norm(s.state.emotional_spectrum) 
                                  for s in self.slices]
        }
        
        return trajectory
    
    def predict_next_state(self, n_steps: int = 1) -> Optional[IAMState]:
        """Predict future crystal states based on growth patterns."""
        if len(self.slices) < 3:
            return None
        
        # Simple linear extrapolation for demonstration
        recent_states = [s.state.to_vector() for s in self.slices[-3:]]
        
        # Calculate velocity and acceleration
        dt = np.mean(np.diff(self.time_axis[-3:]))
        velocity = (recent_states[-1] - recent_states[-2]) / dt
        acceleration = ((recent_states[-1] - recent_states[-2]) - 
                       (recent_states[-2] - recent_states[-3])) / (dt**2)
        
        # Predict next state
        next_time = self.time_axis[-1] + n_steps * dt
        next_vector = (recent_states[-1] + 
                      velocity * n_steps * dt + 
                      0.5 * acceleration * (n_steps * dt)**2)
        
        # Reconstruct IAMState from vector
        idx = 0
        cognitive_position = next_vector[idx:idx+3]
        idx += 3
        
        # Handle quantum state
        if hasattr(self.slices[-1].state, 'quantum_state'):
            q_dim = len(self.slices[-1].state.quantum_state)
            quantum_real = next_vector[idx:idx+q_dim]
            quantum_imag = next_vector[idx+q_dim:idx+2*q_dim]
            quantum_state = quantum_real + 1j * quantum_imag
            idx += 2*q_dim
        else:
            quantum_state = np.array([1.0 + 0j])
        
        # Extract remaining components
        remaining = next_vector[idx:-1]  # Exclude timestamp
        
        # Split remaining into archetype and emotional
        split_point = len(self.slices[-1].state.archetype_vector)
        archetype_vector = remaining[:split_point]
        emotional_spectrum = remaining[split_point:]
        
        return IAMState(
            timestamp=next_time,
            cognitive_position=cognitive_position,
            quantum_state=quantum_state,
            archetype_vector=archetype_vector,
            emotional_spectrum=emotional_spectrum
        )
    
    def export_properties(self) -> Dict[str, Any]:
        """Export comprehensive crystal properties for analysis."""
        return {
            'name': self.name,
            'n_slices': len(self.slices),
            'time_range': [min(self.time_axis), max(self.time_axis)] if self.time_axis else [0, 0],
            'total_volume': self.calculate_volume(),
            'average_density': self.calculate_average_density(),
            'fractal_dimension': self.calculate_fractal_dimension(),
            'symmetries': self.detect_global_symmetries(),
            'periodic_patterns': self.find_periodic_patterns(),
            'eigenstates': self.calculate_eigenstates(),
            'n_defects': len(self.defects),
            'n_phase_transitions': len(self.phase_transitions),
            'growth_trajectory': self.get_growth_trajectory()
        }


class ComplexIAMFractalAnalyzerMock:
    """
    Mock implementation of ComplexIAMFractalAnalyzer for integration testing.
    Maps analyzer outputs to crystal properties as specified in the framework.
    """
    
    def __init__(self):
        self.fractal_dimension = 2.4
        self.quantum_entropy = 0.85
        self.pattern_coherence = 0.92
        self.anomaly_score = 0.15
        self.evolution_velocity = 1.2
    
    def analyze(self, state: IAMState) -> Dict[str, float]:
        """Analyze state and return metrics."""
        # Add some variation based on state
        variation = np.sin(state.timestamp * 0.1) * 0.1
        
        return {
            'fractal_dimension': self.fractal_dimension + variation,
            'quantum_entropy': np.clip(self.quantum_entropy + variation/2, 0, 1),
            'pattern_coherence': np.clip(self.pattern_coherence - variation/3, 0, 1),
            'anomaly_score': np.clip(self.anomaly_score + abs(variation), 0, 1),
            'evolution_velocity': self.evolution_velocity + variation * 2
        }
    
    def map_to_crystal_properties(self, analysis: Dict[str, float]) -> Dict[str, float]:
        """Map analyzer outputs to crystal properties."""
        return {
            'lattice_constant': analysis['fractal_dimension'] * 2.0,
            'unit_cell_volume': analysis['quantum_entropy'] * 10.0,
            'symmetry_order': int(analysis['pattern_coherence'] * 8),
            'defect_density': analysis['anomaly_score'],
            'growth_rate': analysis['evolution_velocity']
        }


def create_crystal_from_trajectory(states: List[IAMState], 
                                 name: str = "TenxsomCrystal") -> TemporalCrystal:
    """
    Convenience function to create a temporal crystal from a state trajectory.
    
    Args:
        states: List of IAM states forming the trajectory
        name: Name for the crystal
    
    Returns:
        TemporalCrystal object
    """
    crystal = TemporalCrystal(name)
    
    for state in states:
        crystal.add_state(state)
    
    return crystal


def interpolate_crystal_states(crystal: TemporalCrystal, 
                             target_resolution: float = 0.1) -> TemporalCrystal:
    """
    Interpolate crystal states to achieve uniform time resolution.
    
    Args:
        crystal: Original temporal crystal
        target_resolution: Desired time step between slices
    
    Returns:
        New crystal with interpolated states
    """
    if len(crystal.slices) < 2:
        return crystal
    
    # Create new crystal
    interp_crystal = TemporalCrystal(f"{crystal.name}_interpolated")
    
    # Generate uniform time grid
    t_min, t_max = min(crystal.time_axis), max(crystal.time_axis)
    n_points = int((t_max - t_min) / target_resolution) + 1
    new_times = np.linspace(t_min, t_max, n_points)
    
    # Get state vectors for interpolation
    state_vectors = np.array([s.state.to_vector() for s in crystal.slices])
    
    # Interpolate each dimension
    from scipy.interpolate import interp1d
    
    interp_func = interp1d(crystal.time_axis, state_vectors.T, 
                          kind='cubic', fill_value='extrapolate')
    
    for t in new_times:
        # Get interpolated vector
        interp_vec = interp_func(t)
        
        # Reconstruct state (simplified - would need proper handling in production)
        idx = 0
        cognitive_position = interp_vec[idx:idx+3]
        idx += 3
        
        # Use dimensions from original crystal
        orig_state = crystal.slices[0].state
        q_dim = len(orig_state.quantum_state)
        a_dim = len(orig_state.archetype_vector)
        e_dim = len(orig_state.emotional_spectrum)
        
        quantum_real = interp_vec[idx:idx+q_dim]
        quantum_imag = interp_vec[idx+q_dim:idx+2*q_dim]
        quantum_state = quantum_real + 1j * quantum_imag
        idx += 2*q_dim
        
        archetype_vector = interp_vec[idx:idx+a_dim]
        idx += a_dim
        
        emotional_spectrum = interp_vec[idx:idx+e_dim]
        
        # Create interpolated state
        interp_state = IAMState(
            timestamp=t,
            cognitive_position=cognitive_position,
            quantum_state=quantum_state,
            archetype_vector=archetype_vector,
            emotional_spectrum=emotional_spectrum
        )
        
        interp_crystal.add_state(interp_state)
    
    return interp_crystal