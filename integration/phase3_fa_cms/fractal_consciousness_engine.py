#!/usr/bin/env python3
"""
Fractal Consciousness Engine for FA-CMS
=======================================

Implements fractal algebra-based consciousness modeling, providing:
- Fractal dimension analysis of consciousness states
- Self-similarity detection across scales
- Recursive pattern recognition
- Multi-scale coherence measurement

Based on the principle that consciousness exhibits fractal properties
across different scales of organization.

For Tenxsom AI's FA-CMS framework.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import time
from scipy import signal
from scipy.spatial.distance import pdist, squareform
import itertools

from fa_plugin_interface import (
    FAPlugin,
    PluginConfig,
    UnifiedState,
    ChakraState,
    FAMessage,
    MessageType
)


@dataclass
class FractalMetrics:
    """Metrics for fractal analysis"""
    dimension: float
    lacunarity: float  # Measure of gaps/heterogeneity
    self_similarity: float  # 0-1 scale
    scaling_exponent: float
    multifractal_spectrum: Optional[np.ndarray] = None


class FractalAnalyzer:
    """Analyzes fractal properties of data"""
    
    @staticmethod
    def calculate_box_dimension(data: np.ndarray, scales: Optional[List[float]] = None) -> float:
        """Calculate box-counting fractal dimension"""
        if scales is None:
            scales = np.logspace(-2, 0, 10)  # 0.01 to 1.0
        
        if len(data.shape) == 1:
            # 1D data - convert to 2D trajectory
            data = np.column_stack([np.arange(len(data)), data])
        
        counts = []
        
        for scale in scales:
            # Create boxes
            boxes = set()
            for point in data:
                box = tuple(np.floor(point / scale).astype(int))
                boxes.add(box)
            counts.append(len(boxes))
        
        # Log-log regression
        log_scales = np.log(scales)
        log_counts = np.log(counts)
        
        # Linear fit
        coeffs = np.polyfit(log_scales, log_counts, 1)
        dimension = -coeffs[0]
        
        return np.clip(dimension, 0, 3)
    
    @staticmethod
    def calculate_correlation_dimension(data: np.ndarray, 
                                      embedding_dim: int = 3,
                                      tau: int = 1) -> float:
        """Calculate correlation dimension using Grassberger-Procaccia algorithm"""
        if len(data) < embedding_dim * tau:
            return 1.0
        
        # Embed the data
        embedded = FractalAnalyzer._embed_time_series(data, embedding_dim, tau)
        
        # Calculate pairwise distances
        distances = pdist(embedded)
        distances = distances[distances > 0]  # Remove zeros
        
        if len(distances) == 0:
            return 1.0
        
        # Calculate correlation sum for different radii
        radii = np.logspace(np.log10(distances.min()), np.log10(distances.max()), 20)
        correlation_sums = []
        
        for r in radii:
            c_r = np.sum(distances < r) / len(distances)
            if c_r > 0:
                correlation_sums.append(c_r)
            else:
                correlation_sums.append(1e-10)
        
        # Fit in log-log space
        log_r = np.log(radii)
        log_c = np.log(correlation_sums)
        
        # Find linear region
        coeffs = np.polyfit(log_r[5:15], log_c[5:15], 1)  # Middle region
        
        return np.clip(coeffs[0], 0, embedding_dim)
    
    @staticmethod
    def calculate_lacunarity(data: np.ndarray, box_sizes: Optional[List[int]] = None) -> float:
        """Calculate lacunarity - measure of gaps/texture in fractal"""
        if box_sizes is None:
            box_sizes = [2, 4, 8, 16, 32]
        
        lacunarities = []
        
        for box_size in box_sizes:
            if box_size > len(data):
                continue
            
            # Sliding box algorithm
            box_masses = []
            for i in range(0, len(data) - box_size + 1, box_size // 2):
                box_data = data[i:i+box_size]
                mass = np.sum(box_data > np.mean(data))  # Count above mean
                box_masses.append(mass)
            
            if len(box_masses) > 1:
                mean_mass = np.mean(box_masses)
                var_mass = np.var(box_masses)
                if mean_mass > 0:
                    lac = 1 + var_mass / (mean_mass ** 2)
                    lacunarities.append(lac)
        
        return np.mean(lacunarities) if lacunarities else 1.0
    
    @staticmethod
    def calculate_self_similarity(data: np.ndarray, scales: List[int] = [2, 4, 8]) -> float:
        """Calculate self-similarity across scales"""
        similarities = []
        
        for scale in scales:
            if scale >= len(data):
                continue
            
            # Downsample data
            downsampled = signal.resample(data, len(data) // scale)
            
            # Compare statistical properties
            orig_mean = np.mean(data)
            orig_std = np.std(data)
            down_mean = np.mean(downsampled)
            down_std = np.std(downsampled)
            
            # Normalized difference
            mean_sim = 1 - abs(orig_mean - down_mean) / (abs(orig_mean) + 1e-10)
            std_sim = 1 - abs(orig_std - down_std) / (abs(orig_std) + 1e-10)
            
            # Spectral similarity
            orig_fft = np.abs(np.fft.fft(data))[:len(data)//2]
            down_fft = np.abs(np.fft.fft(downsampled))[:len(downsampled)//2]
            
            # Resample to same length for comparison
            down_fft_resampled = signal.resample(down_fft, len(orig_fft))
            
            # Correlation coefficient
            spectral_sim = np.corrcoef(orig_fft, down_fft_resampled)[0, 1]
            
            similarity = (mean_sim + std_sim + spectral_sim) / 3
            similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0.0
    
    @staticmethod
    def _embed_time_series(data: np.ndarray, dim: int, tau: int) -> np.ndarray:
        """Embed time series in higher dimension"""
        n = len(data)
        embedded = np.zeros((n - (dim-1)*tau, dim))
        
        for i in range(dim):
            embedded[:, i] = data[i*tau:n-(dim-1-i)*tau]
        
        return embedded


class ConsciousnessFieldGenerator:
    """Generates consciousness fields with fractal properties"""
    
    @staticmethod
    def generate_fractal_field(size: int, 
                              fractal_dim: float = 1.5,
                              octaves: int = 6) -> np.ndarray:
        """Generate 1D fractal field using spectral synthesis"""
        # Frequency components
        freqs = np.fft.fftfreq(size)[1:size//2]
        
        # Power spectrum with fractal scaling
        beta = 2 * fractal_dim - 1
        power = freqs ** (-beta/2)
        
        # Random phases
        phases = np.random.uniform(0, 2*np.pi, len(power))
        
        # Construct Fourier coefficients
        coeffs = np.zeros(size, dtype=complex)
        coeffs[1:size//2] = power * np.exp(1j * phases)
        coeffs[size//2+1:] = np.conj(coeffs[1:size//2][::-1])
        
        # Inverse FFT
        field = np.real(np.fft.ifft(coeffs))
        
        # Normalize
        field = (field - field.min()) / (field.max() - field.min() + 1e-10)
        
        return field
    
    @staticmethod
    def generate_multifractal_field(size: int,
                                   h_min: float = 0.1,
                                   h_max: float = 0.9,
                                   intermittency: float = 0.5) -> np.ndarray:
        """Generate multifractal field with varying local regularity"""
        # Base fractal
        base = ConsciousnessFieldGenerator.generate_fractal_field(size, 1.5)
        
        # Modulation for multifractal behavior
        modulation = ConsciousnessFieldGenerator.generate_fractal_field(size, 1.8)
        
        # Local Hölder exponents
        h_local = h_min + (h_max - h_min) * modulation
        
        # Apply varying regularity
        result = np.zeros(size)
        for i in range(size):
            # Local perturbation based on Hölder exponent
            perturbation = np.random.normal(0, h_local[i] * intermittency)
            result[i] = base[i] + perturbation
        
        return result


class FractalConsciousnessPlugin(FAPlugin):
    """Fractal consciousness analysis and enhancement plugin"""
    
    def __init__(self, config: PluginConfig):
        super().__init__(config)
        self.analyzer = FractalAnalyzer()
        self.generator = ConsciousnessFieldGenerator()
        
        # Configuration
        self.target_dimension = config.custom_params.get('target_dimension', 1.618)  # φ
        self.enhance_fractality = config.custom_params.get('enhance_fractality', True)
        self.multiscale_analysis = config.custom_params.get('multiscale_analysis', True)
        
        # Cache for analysis results
        self.analysis_cache = {}
        
    def initialize(self) -> bool:
        """Initialize fractal consciousness engine"""
        try:
            print(f"Initializing Fractal Consciousness Engine...")
            
            # Test fractal analysis
            test_data = np.random.randn(100)
            dim = self.analyzer.calculate_box_dimension(test_data)
            
            print(f"  ✓ Fractal analyzer ready (test dimension: {dim:.3f})")
            print(f"  ✓ Target dimension: {self.target_dimension}")
            
            return True
            
        except Exception as e:
            print(f"Failed to initialize Fractal Consciousness Engine: {e}")
            return False
    
    def process(self, state: UnifiedState) -> UnifiedState:
        """Process state through fractal analysis and enhancement"""
        start_time = time.time()
        
        try:
            # Extract consciousness field from state
            consciousness_field = self._extract_consciousness_field(state)
            
            # Analyze fractal properties
            metrics = self._analyze_fractal_properties(consciousness_field)
            
            # Store metrics in state
            state.metadata['fractal_metrics'] = {
                'dimension': metrics.dimension,
                'lacunarity': metrics.lacunarity,
                'self_similarity': metrics.self_similarity,
                'scaling_exponent': metrics.scaling_exponent
            }
            
            # Update state fractal dimension
            state.fractal_dimension = metrics.dimension
            
            # Enhance fractality if enabled
            if self.enhance_fractality:
                enhanced_field = self._enhance_fractality(
                    consciousness_field,
                    metrics,
                    self.target_dimension
                )
                
                # Apply enhancement to state
                self._apply_enhanced_field(state, enhanced_field)
            
            # Multi-scale coherence analysis
            if self.multiscale_analysis:
                coherence_profile = self._multiscale_coherence_analysis(state)
                state.metadata['multiscale_coherence'] = coherence_profile
            
            # Send analysis event
            self.send_message(FAMessage(
                source_id=self.id,
                target_id="broadcast",
                message_type=MessageType.EVENT,
                payload={
                    'event': 'fractal_analysis_complete',
                    'dimension': metrics.dimension,
                    'self_similarity': metrics.self_similarity,
                    'coherence_scales': len(coherence_profile) if self.multiscale_analysis else 0
                }
            ))
            
        except Exception as e:
            print(f"Error in fractal consciousness processing: {e}")
            self._update_metrics(time.time() - start_time, error=True)
            raise
        
        self._update_metrics(time.time() - start_time)
        return state
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get fractal engine metrics"""
        base_metrics = self.metrics.copy()
        
        # Add fractal-specific metrics
        if self.analysis_cache:
            recent_dimensions = [m.dimension for m in self.analysis_cache.values()][-10:]
            base_metrics['fractal_metrics'] = {
                'avg_dimension': np.mean(recent_dimensions) if recent_dimensions else 0,
                'dimension_stability': 1 - np.std(recent_dimensions) if len(recent_dimensions) > 1 else 1,
                'cache_size': len(self.analysis_cache)
            }
        
        return base_metrics
    
    def shutdown(self):
        """Shutdown fractal engine"""
        print(f"Shutting down Fractal Consciousness Engine...")
        self.analysis_cache.clear()
        print(f"  ✓ Fractal engine shutdown complete")
    
    def _extract_consciousness_field(self, state: UnifiedState) -> np.ndarray:
        """Extract 1D consciousness field from state"""
        fields = []
        
        # From optimization parameters
        if state.optimization_params:
            fields.append(np.array(list(state.optimization_params.values())))
        
        # From chakra states
        if state.chakra_states:
            # Amplitude field
            amp_field = np.array([c.amplitude for c in state.chakra_states])
            fields.append(amp_field)
            
            # Coherence field
            coh_field = np.array([c.coherence for c in state.chakra_states])
            fields.append(coh_field)
            
            # Frequency field (normalized)
            freq_field = np.array([c.frequency for c in state.chakra_states])
            freq_field = (freq_field - freq_field.min()) / (freq_field.max() - freq_field.min() + 1e-10)
            fields.append(freq_field)
        
        # From quantum state
        if state.quantum_state is not None:
            # Use magnitude of complex amplitudes
            quantum_field = np.abs(state.quantum_state)
            fields.append(quantum_field)
        
        # Concatenate all fields
        if fields:
            consciousness_field = np.concatenate(fields)
        else:
            # Generate random field if no data
            consciousness_field = np.random.randn(50)
        
        return consciousness_field
    
    def _analyze_fractal_properties(self, field: np.ndarray) -> FractalMetrics:
        """Comprehensive fractal analysis"""
        # Box dimension
        box_dim = self.analyzer.calculate_box_dimension(field)
        
        # Correlation dimension
        corr_dim = self.analyzer.calculate_correlation_dimension(field)
        
        # Average dimensions
        dimension = (box_dim + corr_dim) / 2
        
        # Lacunarity
        lacunarity = self.analyzer.calculate_lacunarity(field)
        
        # Self-similarity
        self_similarity = self.analyzer.calculate_self_similarity(field)
        
        # Scaling exponent (Hurst)
        scaling_exponent = self._calculate_hurst_exponent(field)
        
        metrics = FractalMetrics(
            dimension=dimension,
            lacunarity=lacunarity,
            self_similarity=self_similarity,
            scaling_exponent=scaling_exponent
        )
        
        # Cache results
        cache_key = hash(field.tobytes())
        self.analysis_cache[cache_key] = metrics
        
        # Limit cache size
        if len(self.analysis_cache) > 100:
            oldest_key = list(self.analysis_cache.keys())[0]
            del self.analysis_cache[oldest_key]
        
        return metrics
    
    def _calculate_hurst_exponent(self, data: np.ndarray) -> float:
        """Calculate Hurst exponent using R/S analysis"""
        n = len(data)
        if n < 20:
            return 0.5
        
        # Calculate for different lags
        lags = range(2, min(n//2, 20))
        rs_values = []
        
        for lag in lags:
            # Divide into chunks
            chunks = [data[i:i+lag] for i in range(0, n-lag+1, lag)]
            
            rs_chunk = []
            for chunk in chunks:
                if len(chunk) < 2:
                    continue
                
                # Mean and cumulative deviation
                mean_chunk = np.mean(chunk)
                y = np.cumsum(chunk - mean_chunk)
                
                # Range and standard deviation
                R = np.max(y) - np.min(y)
                S = np.std(chunk)
                
                if S > 0:
                    rs_chunk.append(R / S)
            
            if rs_chunk:
                rs_values.append((lag, np.mean(rs_chunk)))
        
        if len(rs_values) < 2:
            return 0.5
        
        # Log-log regression
        log_lags = np.log([r[0] for r in rs_values])
        log_rs = np.log([r[1] for r in rs_values])
        
        hurst = np.polyfit(log_lags, log_rs, 1)[0]
        
        return np.clip(hurst, 0, 1)
    
    def _enhance_fractality(self, field: np.ndarray, 
                           current_metrics: FractalMetrics,
                           target_dimension: float) -> np.ndarray:
        """Enhance field to approach target fractal dimension"""
        current_dim = current_metrics.dimension
        
        if abs(current_dim - target_dimension) < 0.1:
            # Already close to target
            return field
        
        # Generate adjustment field
        adjustment_dim = 2 * target_dimension - current_dim
        adjustment_field = self.generator.generate_fractal_field(
            len(field),
            fractal_dim=np.clip(adjustment_dim, 0.5, 2.5)
        )
        
        # Blend fields
        blend_factor = min(0.5, abs(current_dim - target_dimension))
        enhanced = (1 - blend_factor) * field + blend_factor * adjustment_field
        
        # Preserve original scale
        enhanced = enhanced * (field.std() / enhanced.std())
        enhanced = enhanced + (field.mean() - enhanced.mean())
        
        return enhanced
    
    def _apply_enhanced_field(self, state: UnifiedState, enhanced_field: np.ndarray):
        """Apply enhanced consciousness field back to state"""
        idx = 0
        
        # Update optimization parameters
        if state.optimization_params:
            n_params = len(state.optimization_params)
            param_values = enhanced_field[idx:idx+n_params]
            
            for i, key in enumerate(state.optimization_params.keys()):
                if i < len(param_values):
                    state.optimization_params[key] = float(param_values[i])
            
            idx += n_params
        
        # Update chakra amplitudes
        if state.chakra_states and idx < len(enhanced_field):
            n_chakras = len(state.chakra_states)
            amp_values = enhanced_field[idx:idx+n_chakras]
            
            for i, chakra in enumerate(state.chakra_states):
                if i < len(amp_values):
                    # Normalize to [0, 1]
                    chakra.amplitude = np.clip(amp_values[i], 0, 1)
    
    def _multiscale_coherence_analysis(self, state: UnifiedState) -> Dict[str, float]:
        """Analyze coherence across multiple scales"""
        coherence_profile = {}
        
        if not state.chakra_states:
            return coherence_profile
        
        # Get chakra frequencies
        frequencies = np.array([c.frequency for c in state.chakra_states])
        
        # Analyze at different scales
        scales = ['micro', 'meso', 'macro']
        scale_ranges = [(0, 300), (300, 400), (400, 600)]  # Hz ranges
        
        for scale, (f_min, f_max) in zip(scales, scale_ranges):
            # Get chakras in this frequency range
            scale_chakras = [
                c for c in state.chakra_states 
                if f_min <= c.frequency <= f_max
            ]
            
            if len(scale_chakras) >= 2:
                # Calculate pairwise coherence
                coherences = []
                for c1, c2 in itertools.combinations(scale_chakras, 2):
                    # Phase coherence
                    phase_diff = abs(c1.phase - c2.phase)
                    phase_coherence = np.cos(phase_diff)
                    
                    # Amplitude coherence
                    amp_coherence = 1 - abs(c1.amplitude - c2.amplitude)
                    
                    # Combined coherence
                    coherence = (phase_coherence + amp_coherence) / 2
                    coherences.append(coherence)
                
                coherence_profile[scale] = np.mean(coherences)
            else:
                coherence_profile[scale] = 0.0
        
        # Cross-scale coherence
        if len(scales) >= 2:
            cross_coherences = []
            for s1, s2 in itertools.combinations(coherence_profile.values(), 2):
                cross_coherences.append(abs(s1 - s2))
            
            coherence_profile['cross_scale'] = 1 - np.mean(cross_coherences)
        
        return coherence_profile


def demo_fractal_consciousness():
    """Demonstrate fractal consciousness analysis"""
    print("Fractal Consciousness Engine Demo")
    print("=" * 60)
    
    # Create plugin
    config = PluginConfig(
        name="FractalConsciousness",
        version="1.0.0",
        priority=7,
        custom_params={
            'target_dimension': 1.618,  # φ
            'enhance_fractality': True,
            'multiscale_analysis': True
        }
    )
    
    plugin = FractalConsciousnessPlugin(config)
    
    # Initialize
    if not plugin.initialize():
        print("Failed to initialize!")
        return
    
    # Create test state
    test_state = UnifiedState(
        optimization_params={f'x{i}': np.sin(i * 0.5) + 1 for i in range(10)},
        chakra_states=[
            ChakraState(
                type=f"chakra_{i}",
                frequency=256 * (1.2 ** i),
                amplitude=0.5 + 0.3 * np.sin(i),
                phase=i * np.pi / 4,
                coherence=0.7 + 0.2 * np.cos(i)
            )
            for i in range(7)
        ]
    )
    
    print("\nAnalyzing consciousness field...")
    
    # Process
    processed = plugin.process(test_state)
    
    # Display results
    if 'fractal_metrics' in processed.metadata:
        metrics = processed.metadata['fractal_metrics']
        print(f"\nFractal Analysis Results:")
        print(f"  Dimension: {metrics['dimension']:.3f}")
        print(f"  Target dimension: {plugin.target_dimension:.3f}")
        print(f"  Lacunarity: {metrics['lacunarity']:.3f}")
        print(f"  Self-similarity: {metrics['self_similarity']:.3f}")
        print(f"  Scaling exponent: {metrics['scaling_exponent']:.3f}")
    
    if 'multiscale_coherence' in processed.metadata:
        coherence = processed.metadata['multiscale_coherence']
        print(f"\nMulti-scale Coherence:")
        for scale, value in coherence.items():
            print(f"  {scale}: {value:.3f}")
    
    # Check enhancement
    print(f"\nFractality Enhancement:")
    print(f"  Original dimension: {test_state.fractal_dimension:.3f}")
    print(f"  Enhanced dimension: {processed.fractal_dimension:.3f}")
    print(f"  Improvement: {abs(processed.fractal_dimension - plugin.target_dimension):.3f}")
    
    # Shutdown
    plugin.shutdown()
    
    print("\n✅ Fractal consciousness demo complete!")


if __name__ == "__main__":
    demo_fractal_consciousness()