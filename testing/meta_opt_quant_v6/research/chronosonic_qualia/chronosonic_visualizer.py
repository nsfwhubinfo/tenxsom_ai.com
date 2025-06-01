"""
Chronosonic Qualia Visualizer
Real-time visualization of frequency-driven state trajectories and performance metrics
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.gridspec import GridSpec
import seaborn as sns
from typing import Dict, List, Optional, Tuple
from collections import deque

from chronosonic_prototype import (
    SimplifiedChakraSystem, FrequencyModulatedIAMState, 
    ChronosonicDynamics, CognitivePerformanceMetrics,
    ChakraType
)


class ChronosonicVisualizer:
    """Main visualization class for chronosonic dynamics"""
    
    def __init__(self, figure_size: Tuple[int, int] = (16, 10)):
        self.fig = plt.figure(figsize=figure_size)
        self.gs = GridSpec(3, 3, figure=self.fig, hspace=0.3, wspace=0.3)
        
        # Create subplots
        self.ax_trajectory = self.fig.add_subplot(self.gs[0:2, 0])
        self.ax_phase_space = self.fig.add_subplot(self.gs[0:2, 1])
        self.ax_chakra_pattern = self.fig.add_subplot(self.gs[0:2, 2])
        self.ax_performance = self.fig.add_subplot(self.gs[2, :2])
        self.ax_metrics = self.fig.add_subplot(self.gs[2, 2])
        
        # Data buffers
        self.buffer_size = 1000
        self.time_buffer = deque(maxlen=self.buffer_size)
        self.state_buffer = deque(maxlen=self.buffer_size)
        self.chakra_buffer = deque(maxlen=self.buffer_size)
        self.performance_buffer = deque(maxlen=self.buffer_size)
        
        # Style settings
        plt.style.use('dark_background')
        self.colormap = plt.cm.viridis
        
    def setup_plots(self):
        """Initialize plot layouts and labels"""
        # Frequency trajectory plot
        self.ax_trajectory.set_title('Frequency-Driven State Trajectories', fontsize=14)
        self.ax_trajectory.set_xlabel('Time (s)')
        self.ax_trajectory.set_ylabel('State Amplitude')
        self.ax_trajectory.grid(True, alpha=0.3)
        
        # Phase space plot
        self.ax_phase_space.set_title('<I_AM> State Phase Space', fontsize=14)
        self.ax_phase_space.set_xlabel('Dimension 1')
        self.ax_phase_space.set_ylabel('Dimension 2')
        self.ax_phase_space.grid(True, alpha=0.3)
        
        # Chakra activation pattern
        self.ax_chakra_pattern.set_title('Chakra Activation Patterns', fontsize=14)
        self.ax_chakra_pattern.set_xlabel('Time (s)')
        self.ax_chakra_pattern.set_ylabel('Chakra')
        
        # Performance metrics
        self.ax_performance.set_title('Cognitive Performance Over Time', fontsize=14)
        self.ax_performance.set_xlabel('Time (s)')
        self.ax_performance.set_ylabel('Performance Score')
        self.ax_performance.grid(True, alpha=0.3)
        
        # Metrics dashboard
        self.ax_metrics.set_title('Current Metrics', fontsize=14)
        self.ax_metrics.axis('off')
        
    def plot_frequency_trajectories(self, dynamics_results: Dict):
        """Plot frequency-driven state trajectories"""
        self.ax_trajectory.clear()
        
        time = dynamics_results['time']
        iam_state = dynamics_results['iam_state']
        
        # Plot first 3 dimensions of IAM state
        for i in range(min(3, iam_state.shape[1])):
            self.ax_trajectory.plot(time, iam_state[:, i], 
                                  label=f'IAM Dim {i+1}', 
                                  alpha=0.8, linewidth=2)
        
        # Plot system coherence
        self.ax_trajectory.plot(time, dynamics_results['system_coherence'], 
                               'w--', label='System Coherence', 
                               alpha=0.6, linewidth=2)
        
        self.ax_trajectory.set_xlabel('Time (s)')
        self.ax_trajectory.set_ylabel('Amplitude')
        self.ax_trajectory.set_title('Frequency-Driven State Trajectories')
        self.ax_trajectory.legend(loc='upper right', fontsize=10)
        self.ax_trajectory.grid(True, alpha=0.3)
        
    def plot_phase_space(self, iam_state: FrequencyModulatedIAMState, 
                        history_length: int = 500):
        """Plot IAM state evolution in phase space"""
        if len(self.state_buffer) < 2:
            return
            
        # Extract recent history
        states = np.array(list(self.state_buffer))[-history_length:]
        
        # Plot 2D projection
        self.ax_phase_space.clear()
        
        # Create color gradient for time
        colors = self.colormap(np.linspace(0, 1, len(states)))
        
        # Plot trajectory
        for i in range(1, len(states)):
            self.ax_phase_space.plot(states[i-1:i+1, 0], states[i-1:i+1, 1],
                                   color=colors[i], alpha=0.8, linewidth=2)
        
        # Mark current position
        if len(states) > 0:
            self.ax_phase_space.scatter(states[-1, 0], states[-1, 1], 
                                      color='red', s=100, marker='o',
                                      edgecolor='white', linewidth=2)
        
        # Add attractor regions
        self._draw_attractor_regions()
        
        self.ax_phase_space.set_xlabel('IAM Dimension 1')
        self.ax_phase_space.set_ylabel('IAM Dimension 2')
        self.ax_phase_space.set_title('<I_AM> State Phase Space Evolution')
        self.ax_phase_space.grid(True, alpha=0.3)
        
    def _draw_attractor_regions(self):
        """Draw theoretical attractor regions in phase space"""
        # Define attractor centers based on harmonic relationships
        attractors = [
            (0.5, 0.5),   # Balanced state
            (0.2, 0.8),   # Root-dominant
            (0.8, 0.2),   # Crown-dominant
        ]
        
        for center in attractors:
            circle = plt.Circle(center, 0.15, fill=False, 
                              edgecolor='cyan', alpha=0.3, 
                              linestyle='--', linewidth=1)
            self.ax_phase_space.add_patch(circle)
    
    def plot_chakra_patterns(self, chakra_system: SimplifiedChakraSystem, 
                           dynamics_results: Dict):
        """Visualize chakra activation patterns over time"""
        self.ax_chakra_pattern.clear()
        
        time = dynamics_results['time']
        chakra_amps = dynamics_results['chakra_amplitudes']
        
        # Create heatmap data
        chakra_names = ['Root', 'Heart', 'Crown']
        
        # Normalize amplitudes for visualization
        heatmap_data = chakra_amps.T
        
        # Plot heatmap
        im = self.ax_chakra_pattern.imshow(heatmap_data, aspect='auto',
                                         cmap='plasma', origin='lower',
                                         extent=[time[0], time[-1], 0, 3])
        
        # Add chakra labels
        self.ax_chakra_pattern.set_yticks([0.5, 1.5, 2.5])
        self.ax_chakra_pattern.set_yticklabels(chakra_names)
        
        # Add phase synchronization overlay
        phases = dynamics_results['chakra_phases']
        sync_indices = []
        
        for i in range(len(time)):
            phase_vec = phases[i]
            sync_index = abs(np.mean(np.exp(1j * phase_vec)))
            sync_indices.append(sync_index)
        
        # Overlay synchronization as contour
        ax2 = self.ax_chakra_pattern.twinx()
        ax2.plot(time, sync_indices, 'w-', alpha=0.6, linewidth=2)
        ax2.set_ylabel('Phase Sync', color='white')
        ax2.set_ylim([0, 1])
        
        self.ax_chakra_pattern.set_xlabel('Time (s)')
        self.ax_chakra_pattern.set_title('Chakra Activation Patterns')
        
        # Add colorbar
        plt.colorbar(im, ax=self.ax_chakra_pattern, 
                    label='Activation Level', pad=0.1)
    
    def plot_performance_metrics(self, metrics: CognitivePerformanceMetrics):
        """Plot cognitive performance metrics dashboard"""
        if not metrics.metrics_history:
            return
            
        self.ax_performance.clear()
        
        # Extract metric history
        history = metrics.metrics_history
        n_points = len(history)
        time_points = np.arange(n_points) * 0.1  # Assuming 0.1s sampling
        
        # Plot individual metrics
        metric_names = ['coherence_index', 'fractal_complexity', 
                       'state_stability', 'frequency_alignment']
        
        for metric_name in metric_names:
            values = [h[metric_name] for h in history]
            self.ax_performance.plot(time_points, values, 
                                   label=metric_name.replace('_', ' ').title(),
                                   alpha=0.8, linewidth=2)
        
        # Plot composite score
        composite = [h['composite_score'] for h in history]
        self.ax_performance.plot(time_points, composite, 'w-', 
                               label='Composite Score', 
                               linewidth=3, alpha=0.9)
        
        # Add baseline reference if available
        if metrics.baseline_established:
            baseline_composite = metrics.baseline_values['composite_score']
            self.ax_performance.axhline(y=baseline_composite, 
                                      color='red', linestyle='--',
                                      alpha=0.5, label='Baseline')
        
        self.ax_performance.set_xlabel('Time (s)')
        self.ax_performance.set_ylabel('Performance Score')
        self.ax_performance.set_title('Cognitive Performance Metrics')
        self.ax_performance.legend(loc='upper left', fontsize=9)
        self.ax_performance.grid(True, alpha=0.3)
        self.ax_performance.set_ylim([0, 1.2])
    
    def update_metrics_dashboard(self, metrics: CognitivePerformanceMetrics):
        """Update the current metrics dashboard"""
        self.ax_metrics.clear()
        self.ax_metrics.axis('off')
        
        if not metrics.metrics_history:
            return
        
        current = metrics.metrics_history[-1]
        
        # Create text display
        y_pos = 0.9
        
        self.ax_metrics.text(0.1, y_pos, 'Current Metrics:', 
                           fontsize=12, weight='bold')
        y_pos -= 0.15
        
        # Display each metric
        for key, value in current.items():
            if key != 'composite_score':
                label = key.replace('_', ' ').title()
                self.ax_metrics.text(0.1, y_pos, f'{label}:', fontsize=10)
                self.ax_metrics.text(0.7, y_pos, f'{value:.3f}', fontsize=10)
                y_pos -= 0.12
        
        # Highlight composite score
        y_pos -= 0.05
        self.ax_metrics.text(0.1, y_pos, 'Composite Score:', 
                           fontsize=11, weight='bold', color='cyan')
        self.ax_metrics.text(0.7, y_pos, f'{current["composite_score"]:.3f}', 
                           fontsize=11, weight='bold', color='cyan')
        
        # Show improvement if baseline exists
        if metrics.baseline_established:
            improvements = metrics.get_improvement_ratio()
            y_pos -= 0.15
            self.ax_metrics.text(0.1, y_pos, 'vs Baseline:', 
                               fontsize=10, style='italic')
            composite_improvement = improvements.get('composite_score', 1.0)
            color = 'green' if composite_improvement > 1.0 else 'red'
            sign = '+' if composite_improvement > 1.0 else ''
            self.ax_metrics.text(0.7, y_pos, 
                               f'{sign}{(composite_improvement-1)*100:.1f}%',
                               fontsize=10, color=color)
    
    def create_animation(self, chakra_system: SimplifiedChakraSystem,
                        iam_state: FrequencyModulatedIAMState,
                        dynamics: ChronosonicDynamics,
                        metrics: CognitivePerformanceMetrics,
                        interval: int = 100):
        """Create real-time animation of the system"""
        
        def update(frame):
            # Simulate one step
            t_current = frame * 0.1
            t_span = (t_current, t_current + 0.1)
            
            # Run dynamics
            results = dynamics.simulate(t_span, dt=0.01)
            
            # Update states
            self.state_buffer.append(iam_state.state_vector.copy())
            self.time_buffer.append(t_current)
            
            # Calculate metrics
            current_metrics = metrics.calculate_metrics(chakra_system, iam_state)
            
            # Update plots
            if len(self.time_buffer) > 10:
                self.plot_frequency_trajectories(results)
                self.plot_phase_space(iam_state)
                self.plot_chakra_patterns(chakra_system, results)
                self.plot_performance_metrics(metrics)
                self.update_metrics_dashboard(metrics)
            
            return self.fig.axes
        
        self.setup_plots()
        anim = FuncAnimation(self.fig, update, interval=interval, blit=False)
        return anim
    
    def save_snapshot(self, filename: str):
        """Save current visualization state"""
        self.fig.savefig(filename, dpi=300, bbox_inches='tight', 
                        facecolor='black', edgecolor='none')


class SpectrumAnalyzer:
    """Analyze frequency spectrum of chronosonic states"""
    
    def __init__(self):
        self.fig, (self.ax_spectrum, self.ax_spectrogram) = plt.subplots(2, 1, 
                                                                         figsize=(10, 8))
        plt.style.use('dark_background')
        
    def analyze_spectrum(self, signal: np.ndarray, sampling_rate: float = 1000.0):
        """Perform frequency spectrum analysis"""
        # Compute FFT
        fft = np.fft.fft(signal)
        freqs = np.fft.fftfreq(len(signal), 1/sampling_rate)
        
        # Only positive frequencies
        pos_mask = freqs > 0
        freqs = freqs[pos_mask]
        magnitude = np.abs(fft[pos_mask])
        
        # Plot spectrum
        self.ax_spectrum.clear()
        self.ax_spectrum.semilogy(freqs, magnitude)
        self.ax_spectrum.set_xlabel('Frequency (Hz)')
        self.ax_spectrum.set_ylabel('Magnitude')
        self.ax_spectrum.set_title('Frequency Spectrum')
        self.ax_spectrum.grid(True, alpha=0.3)
        
        # Mark chakra frequencies
        chakra_freqs = [256.0, 341.3, 512.0]
        for freq in chakra_freqs:
            self.ax_spectrum.axvline(x=freq, color='red', 
                                   linestyle='--', alpha=0.5)
        
        return freqs, magnitude
    
    def plot_spectrogram(self, signal: np.ndarray, sampling_rate: float = 1000.0):
        """Create spectrogram visualization"""
        from scipy import signal as scipy_signal
        
        # Compute spectrogram
        f, t, Sxx = scipy_signal.spectrogram(signal, sampling_rate, 
                                            nperseg=256, noverlap=128)
        
        # Plot
        self.ax_spectrogram.clear()
        self.ax_spectrogram.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10),
                                      shading='gouraud', cmap='plasma')
        self.ax_spectrogram.set_ylabel('Frequency (Hz)')
        self.ax_spectrogram.set_xlabel('Time (s)')
        self.ax_spectrogram.set_title('Spectrogram')
        self.ax_spectrogram.set_ylim([0, 600])
        
        return f, t, Sxx