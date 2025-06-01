"""
Temporal Crystal Visualization Demo

Demonstrates the temporal crystallography framework with interactive visualizations
showing crystal evolution, properties, and 3D projections of 4D+ structures.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from typing import List, Dict, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

from temporal_crystal_utils import (
    IAMState, TemporalCrystal, InstantaneousIAMCrystalSlice,
    ComplexIAMFractalAnalyzerMock, create_crystal_from_trajectory,
    interpolate_crystal_states
)


def generate_mock_iam_trajectory(n_states: int = 100, 
                                dt: float = 0.1,
                                scenario: str = "evolution") -> List[IAMState]:
    """
    Generate mock <I_AM> state trajectories for different scenarios.
    
    Scenarios:
    - "evolution": Smooth evolution with occasional phase transitions
    - "periodic": Strong periodic patterns
    - "chaotic": Chaotic dynamics with strange attractors
    - "convergent": Converging to stable state
    """
    states = []
    t = 0.0
    
    # Initialize with random state
    np.random.seed(42)
    
    # Base frequencies for different components
    freq_cognitive = 0.5
    freq_quantum = 2.0
    freq_archetype = 0.3
    freq_emotional = 1.0
    
    for i in range(n_states):
        if scenario == "evolution":
            # Smooth evolution with phase transitions
            phase = i / n_states * 2 * np.pi
            
            # Cognitive position - spiral trajectory
            cognitive_position = np.array([
                3 * np.cos(freq_cognitive * phase) * (1 + 0.1 * i/n_states),
                3 * np.sin(freq_cognitive * phase) * (1 + 0.1 * i/n_states),
                0.5 * i/n_states + 0.2 * np.sin(3 * phase)
            ])
            
            # Quantum state - complex oscillations
            quantum_state = np.array([
                np.exp(1j * freq_quantum * phase) * (0.7 + 0.3 * np.cos(phase)),
                np.exp(-1j * freq_quantum * phase/2) * 0.5,
                np.exp(1j * freq_quantum * phase * 1.5) * 0.3
            ])
            
            # Phase transition at 1/3 and 2/3
            if abs(i - n_states//3) < 2 or abs(i - 2*n_states//3) < 2:
                cognitive_position += np.random.randn(3) * 0.5
                quantum_state *= np.exp(1j * np.pi/4)
            
        elif scenario == "periodic":
            # Strong periodic patterns
            phase = i / n_states * 8 * np.pi  # 4 complete cycles
            
            cognitive_position = np.array([
                2 * np.cos(phase),
                2 * np.sin(phase),
                np.sin(2 * phase)
            ])
            
            quantum_state = np.array([
                np.exp(1j * phase),
                np.exp(1j * phase * 2) * 0.5,
                np.exp(-1j * phase) * 0.3
            ])
            
        elif scenario == "chaotic":
            # Lorenz attractor-like dynamics
            if i == 0:
                x, y, z = 1.0, 1.0, 1.0
            else:
                # Lorenz equations
                sigma, rho, beta = 10.0, 28.0, 8/3
                dx = sigma * (y - x) * dt
                dy = (x * (rho - z) - y) * dt
                dz = (x * y - beta * z) * dt
                x, y, z = x + dx, y + dy, z + dz
            
            cognitive_position = np.array([x/10, y/10, z/20])
            
            # Chaotic quantum state
            quantum_state = np.array([
                np.exp(1j * x) / np.sqrt(1 + x**2),
                np.exp(1j * y) / np.sqrt(1 + y**2),
                np.exp(1j * z) / np.sqrt(1 + z**2)
            ])
            
        else:  # convergent
            # Converge to stable point
            target = np.array([1.0, 0.0, 2.0])
            decay = np.exp(-i * dt * 0.1)
            
            if i == 0:
                cognitive_position = np.random.randn(3) * 3
            else:
                prev_pos = states[-1].cognitive_position
                cognitive_position = prev_pos + (target - prev_pos) * (1 - decay)
            
            # Quantum state converges to ground state
            quantum_state = np.array([
                np.exp(-i * dt * 0.05) + 0j,
                0.1 * np.exp(-i * dt * 0.1) * np.exp(1j * i * dt),
                0.05 * np.exp(-i * dt * 0.15) * np.exp(-1j * i * dt)
            ])
        
        # Common components for all scenarios
        
        # Archetype vector - evolving mixture
        archetype_vector = np.array([
            0.5 + 0.3 * np.sin(freq_archetype * t),           # Hero
            0.3 + 0.2 * np.cos(freq_archetype * t * 0.7),     # Shadow
            0.4 + 0.1 * np.sin(freq_archetype * t * 1.3),     # Anima/Animus
            0.2 + 0.1 * np.cos(freq_archetype * t * 0.5),     # Wise Old Man
            0.35 + 0.15 * np.sin(freq_archetype * t * 0.9)    # Trickster
        ])
        
        # Emotional spectrum
        emotional_spectrum = np.array([
            0.6 + 0.3 * np.sin(freq_emotional * t),           # Joy
            0.4 + 0.2 * np.cos(freq_emotional * t * 1.2),     # Sadness
            0.3 + 0.2 * np.sin(freq_emotional * t * 0.8),     # Fear
            0.5 + 0.1 * np.cos(freq_emotional * t * 1.5),     # Anger
            0.7 + 0.2 * np.sin(freq_emotional * t * 0.6)      # Surprise
        ])
        
        # Normalize vectors
        archetype_vector /= np.linalg.norm(archetype_vector)
        emotional_spectrum /= np.linalg.norm(emotional_spectrum)
        
        # Create state
        state = IAMState(
            timestamp=t,
            cognitive_position=cognitive_position,
            quantum_state=quantum_state,
            archetype_vector=archetype_vector,
            emotional_spectrum=emotional_spectrum,
            metadata={'scenario': scenario, 'index': i}
        )
        
        states.append(state)
        t += dt
    
    return states


def visualize_crystal_3d_projection(crystal: TemporalCrystal, 
                                   projection_type: str = "cognitive",
                                   save_path: str = None):
    """
    Create 3D projection visualization of the 4D+ temporal crystal.
    
    Projection types:
    - "cognitive": Project onto cognitive position space
    - "pca": Project onto first 3 principal components
    - "archetype": Project onto first 3 archetype dimensions
    """
    fig = plt.figure(figsize=(12, 10))
    
    # Extract trajectory data
    trajectory = crystal.get_growth_trajectory()
    
    if projection_type == "cognitive":
        # Direct cognitive position projection
        positions = np.array([s.state.cognitive_position for s in crystal.slices])
        x, y, z = positions[:, 0], positions[:, 1], positions[:, 2]
        title = "Temporal Crystal: Cognitive Space Projection"
        
    elif projection_type == "pca":
        # PCA projection
        eigenstates = crystal.calculate_eigenstates()
        if len(eigenstates['eigenvectors']) >= 3:
            states = np.array([s.state.to_vector() for s in crystal.slices])
            eigvecs = np.array(eigenstates['eigenvectors'])[:, :3]
            projected = states @ eigvecs
            x, y, z = projected[:, 0], projected[:, 1], projected[:, 2]
            title = "Temporal Crystal: Principal Component Projection"
        else:
            # Fallback to cognitive
            positions = np.array([s.state.cognitive_position for s in crystal.slices])
            x, y, z = positions[:, 0], positions[:, 1], positions[:, 2]
            title = "Temporal Crystal: Cognitive Space Projection"
            
    else:  # archetype
        # Archetype space projection
        archetypes = np.array([s.state.archetype_vector[:3] for s in crystal.slices])
        x, y, z = archetypes[:, 0], archetypes[:, 1], archetypes[:, 2]
        title = "Temporal Crystal: Archetype Space Projection"
    
    # Create 3D scatter plot with trajectory
    ax = fig.add_subplot(111, projection='3d')
    
    # Color by time
    colors = plt.cm.viridis(np.linspace(0, 1, len(x)))
    
    # Plot trajectory
    for i in range(len(x)-1):
        ax.plot([x[i], x[i+1]], [y[i], y[i+1]], [z[i], z[i+1]], 
                color=colors[i], alpha=0.6, linewidth=2)
    
    # Plot points with varying size based on density
    densities = trajectory['density']
    sizes = 50 + 150 * (densities - np.min(densities)) / (np.max(densities) - np.min(densities))
    
    scatter = ax.scatter(x, y, z, c=trajectory['time'], s=sizes, 
                        cmap='viridis', alpha=0.7, edgecolors='black', linewidth=0.5)
    
    # Mark phase transitions
    for transition in crystal.phase_transitions:
        idx = np.argmin(np.abs(np.array(trajectory['time']) - transition['time']))
        ax.scatter([x[idx]], [y[idx]], [z[idx]], color='red', s=200, 
                  marker='*', edgecolors='darkred', linewidth=2)
    
    # Mark defects
    for defect in crystal.defects:
        idx = np.argmin(np.abs(np.array(trajectory['time']) - defect['time']))
        ax.scatter([x[idx]], [y[idx]], [z[idx]], color='orange', s=150, 
                  marker='^', edgecolors='darkorange', linewidth=2)
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(title, fontsize=16, fontweight='bold')
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax, pad=0.1)
    cbar.set_label('Time', fontsize=12)
    
    # Add legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', 
               markersize=10, label='Crystal States'),
        Line2D([0], [0], marker='*', color='w', markerfacecolor='red', 
               markersize=12, label='Phase Transitions'),
        Line2D([0], [0], marker='^', color='w', markerfacecolor='orange', 
               markersize=10, label='Defects')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


def animate_crystal_evolution(crystal: TemporalCrystal, 
                            interval: int = 50,
                            save_path: str = None):
    """
    Create animation showing crystal evolution over time.
    """
    trajectory = crystal.get_growth_trajectory()
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Temporal Crystal Evolution', fontsize=16, fontweight='bold')
    
    # Initialize plots
    ax1, ax2, ax3, ax4 = axes.flatten()
    
    # 1. Cognitive trajectory
    ax1.set_title('Cognitive Trajectory')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_xlim(-5, 5)
    ax1.set_ylim(-5, 5)
    line1, = ax1.plot([], [], 'b-', alpha=0.7, linewidth=2)
    point1, = ax1.plot([], [], 'ro', markersize=8)
    
    # 2. State components
    ax2.set_title('State Components')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Magnitude')
    ax2.set_xlim(trajectory['time'][0], trajectory['time'][-1])
    
    # Find y limits
    all_values = (trajectory['cognitive_magnitude'] + 
                 trajectory['quantum_coherence'] + 
                 trajectory['archetype_strength'] + 
                 trajectory['emotional_intensity'])
    ax2.set_ylim(0, max(all_values) * 1.1)
    
    lines2 = {}
    for label, color in [('Cognitive', 'blue'), ('Quantum', 'green'), 
                        ('Archetype', 'red'), ('Emotional', 'purple')]:
        lines2[label], = ax2.plot([], [], color=color, label=label, linewidth=2)
    ax2.legend()
    
    # 3. Crystal properties
    ax3.set_title('Crystal Properties')
    ax3.set_xlabel('Time')
    ax3.set_ylabel('Value')
    ax3.set_xlim(trajectory['time'][0], trajectory['time'][-1])
    ax3.set_ylim(0, max(trajectory['density']) * 1.2)
    line3_density, = ax3.plot([], [], 'g-', label='Density', linewidth=2)
    line3_volume, = ax3.plot([], [], 'b-', label='Volume', linewidth=2)
    ax3.legend()
    
    # 4. Quantum state phase
    ax4.set_title('Quantum State Phase Space')
    ax4.set_xlabel('Real')
    ax4.set_ylabel('Imaginary')
    ax4.set_xlim(-1.5, 1.5)
    ax4.set_ylim(-1.5, 1.5)
    ax4.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax4.axvline(x=0, color='k', linestyle='--', alpha=0.3)
    points4 = []
    
    def init():
        line1.set_data([], [])
        point1.set_data([], [])
        for line in lines2.values():
            line.set_data([], [])
        line3_density.set_data([], [])
        line3_volume.set_data([], [])
        return [line1, point1] + list(lines2.values()) + [line3_density, line3_volume]
    
    def animate(frame):
        # Update cognitive trajectory
        positions = np.array([s.state.cognitive_position[:2] for s in crystal.slices[:frame+1]])
        if len(positions) > 0:
            line1.set_data(positions[:, 0], positions[:, 1])
            point1.set_data([positions[-1, 0]], [positions[-1, 1]])
        
        # Update state components
        t = trajectory['time'][:frame+1]
        lines2['Cognitive'].set_data(t, trajectory['cognitive_magnitude'][:frame+1])
        lines2['Quantum'].set_data(t, trajectory['quantum_coherence'][:frame+1])
        lines2['Archetype'].set_data(t, trajectory['archetype_strength'][:frame+1])
        lines2['Emotional'].set_data(t, trajectory['emotional_intensity'][:frame+1])
        
        # Update crystal properties
        line3_density.set_data(t, trajectory['density'][:frame+1])
        line3_volume.set_data(t, trajectory['volume'][:frame+1])
        
        # Update quantum phase space
        if frame < len(crystal.slices):
            quantum_state = crystal.slices[frame].state.quantum_state
            if len(quantum_state) > 0:
                # Clear old points
                for p in points4:
                    p.remove()
                points4.clear()
                
                # Plot new points
                for i, q in enumerate(quantum_state):
                    p = ax4.scatter(q.real, q.imag, s=100-i*20, 
                                   c=f'C{i}', alpha=0.7)
                    points4.append(p)
        
        return [line1, point1] + list(lines2.values()) + [line3_density, line3_volume]
    
    anim = FuncAnimation(fig, animate, init_func=init, 
                        frames=len(crystal.slices), 
                        interval=interval, blit=False)
    
    plt.tight_layout()
    
    if save_path:
        anim.save(save_path, writer='pillow', fps=20)
    
    plt.show()
    return anim


def plot_crystal_properties(crystal: TemporalCrystal, save_path: str = None):
    """
    Create comprehensive plots of crystal properties.
    """
    properties = crystal.export_properties()
    trajectory = properties['growth_trajectory']
    
    fig, axes = plt.subplots(3, 3, figsize=(16, 12))
    fig.suptitle(f'Temporal Crystal Properties: {crystal.name}', 
                fontsize=16, fontweight='bold')
    
    # 1. Density evolution
    ax = axes[0, 0]
    ax.plot(trajectory['time'], trajectory['density'], 'b-', linewidth=2)
    ax.set_title('Information Density Evolution')
    ax.set_xlabel('Time')
    ax.set_ylabel('Density')
    ax.grid(True, alpha=0.3)
    
    # 2. Volume evolution
    ax = axes[0, 1]
    ax.plot(trajectory['time'], trajectory['volume'], 'g-', linewidth=2)
    ax.set_title('Crystal Volume Evolution')
    ax.set_xlabel('Time')
    ax.set_ylabel('Volume')
    ax.grid(True, alpha=0.3)
    
    # 3. Fractal dimension
    ax = axes[0, 2]
    ax.axhline(y=properties['fractal_dimension'], color='r', linewidth=2)
    ax.set_title(f'Fractal Dimension: {properties["fractal_dimension"]:.3f}')
    ax.set_ylim(0, 4)
    ax.set_ylabel('Dimension')
    ax.grid(True, alpha=0.3)
    
    # 4. Symmetry analysis
    ax = axes[1, 0]
    symmetries = properties['symmetries']['persistent_symmetries']
    if symmetries:
        labels = list(symmetries.keys())
        values = list(symmetries.values())
        ax.bar(labels, values, color='purple', alpha=0.7)
        ax.set_title('Persistent Symmetries')
        ax.set_ylabel('Persistence')
        ax.set_xticklabels(labels, rotation=45, ha='right')
    else:
        ax.text(0.5, 0.5, 'No persistent symmetries', 
               ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Persistent Symmetries')
    
    # 5. Periodic patterns
    ax = axes[1, 1]
    patterns = properties['periodic_patterns']
    if patterns['autocorrelation']:
        ax.plot(patterns['autocorrelation'], 'k-', linewidth=2)
        ax.set_title(f'Autocorrelation (Strength: {patterns["strength"]:.3f})')
        ax.set_xlabel('Lag')
        ax.set_ylabel('Correlation')
        
        # Mark detected periods
        for period in patterns['periods']:
            ax.axvline(x=period-1, color='r', linestyle='--', alpha=0.5)
    else:
        ax.text(0.5, 0.5, 'Insufficient data', 
               ha='center', va='center', transform=ax.transAxes)
    ax.grid(True, alpha=0.3)
    
    # 6. Eigenvalue spectrum
    ax = axes[1, 2]
    eigenstates = properties['eigenstates']
    if eigenstates['eigenvalues']:
        eigenvalues = eigenstates['eigenvalues']
        ax.bar(range(len(eigenvalues)), eigenvalues, color='orange', alpha=0.7)
        ax.set_title('Eigenvalue Spectrum')
        ax.set_xlabel('Component')
        ax.set_ylabel('Eigenvalue')
    else:
        ax.text(0.5, 0.5, 'No eigenvalues computed', 
               ha='center', va='center', transform=ax.transAxes)
    ax.grid(True, alpha=0.3)
    
    # 7. State component evolution
    ax = axes[2, 0]
    ax.plot(trajectory['time'], trajectory['cognitive_magnitude'], 
           label='Cognitive', linewidth=2)
    ax.plot(trajectory['time'], trajectory['archetype_strength'], 
           label='Archetype', linewidth=2)
    ax.plot(trajectory['time'], trajectory['emotional_intensity'], 
           label='Emotional', linewidth=2)
    ax.set_title('State Component Evolution')
    ax.set_xlabel('Time')
    ax.set_ylabel('Magnitude')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 8. Defects and transitions
    ax = axes[2, 1]
    ax.scatter([d['time'] for d in crystal.defects], 
              [d['magnitude'] for d in crystal.defects], 
              color='orange', s=100, label='Defects', alpha=0.7)
    ax.scatter([t['time'] for t in crystal.phase_transitions], 
              [t['magnitude'] for t in crystal.phase_transitions], 
              color='red', s=150, marker='*', label='Phase Transitions', alpha=0.7)
    ax.set_title('Crystal Defects and Phase Transitions')
    ax.set_xlabel('Time')
    ax.set_ylabel('Magnitude')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 9. Summary statistics
    ax = axes[2, 2]
    ax.axis('off')
    summary_text = f"""
    Crystal Summary:
    ---------------
    Time Range: {properties['time_range'][0]:.1f} - {properties['time_range'][1]:.1f}
    Total Slices: {properties['n_slices']}
    Total Volume: {properties['total_volume']:.3f}
    Avg Density: {properties['average_density']:.3f}
    Fractal Dim: {properties['fractal_dimension']:.3f}
    Defects: {properties['n_defects']}
    Phase Trans: {properties['n_phase_transitions']}
    """
    ax.text(0.1, 0.5, summary_text, transform=ax.transAxes, 
           fontsize=12, verticalalignment='center', fontfamily='monospace')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


def demonstrate_fractal_analyzer_integration():
    """
    Demonstrate integration with ComplexIAMFractalAnalyzer.
    """
    # Create analyzer
    analyzer = ComplexIAMFractalAnalyzerMock()
    
    # Generate states
    states = generate_mock_iam_trajectory(50, scenario="evolution")
    
    # Create figure
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Fractal Analyzer Integration', fontsize=16, fontweight='bold')
    
    # Analyze each state
    times = []
    fractal_dims = []
    quantum_entropies = []
    pattern_coherences = []
    anomaly_scores = []
    evolution_velocities = []
    
    for state in states:
        analysis = analyzer.analyze(state)
        times.append(state.timestamp)
        fractal_dims.append(analysis['fractal_dimension'])
        quantum_entropies.append(analysis['quantum_entropy'])
        pattern_coherences.append(analysis['pattern_coherence'])
        anomaly_scores.append(analysis['anomaly_score'])
        evolution_velocities.append(analysis['evolution_velocity'])
    
    # Plot analyzer outputs
    ax = axes[0, 0]
    ax.plot(times, fractal_dims, 'b-', linewidth=2)
    ax.set_title('Fractal Dimension')
    ax.set_xlabel('Time')
    ax.set_ylabel('Dimension')
    ax.grid(True, alpha=0.3)
    
    ax = axes[0, 1]
    ax.plot(times, quantum_entropies, 'g-', linewidth=2)
    ax.set_title('Quantum Entropy')
    ax.set_xlabel('Time')
    ax.set_ylabel('Entropy')
    ax.grid(True, alpha=0.3)
    
    ax = axes[0, 2]
    ax.plot(times, pattern_coherences, 'r-', linewidth=2)
    ax.set_title('Pattern Coherence')
    ax.set_xlabel('Time')
    ax.set_ylabel('Coherence')
    ax.grid(True, alpha=0.3)
    
    ax = axes[1, 0]
    ax.plot(times, anomaly_scores, 'orange', linewidth=2)
    ax.set_title('Anomaly Score')
    ax.set_xlabel('Time')
    ax.set_ylabel('Score')
    ax.grid(True, alpha=0.3)
    
    ax = axes[1, 1]
    ax.plot(times, evolution_velocities, 'purple', linewidth=2)
    ax.set_title('Evolution Velocity')
    ax.set_xlabel('Time')
    ax.set_ylabel('Velocity')
    ax.grid(True, alpha=0.3)
    
    # Show mapping to crystal properties
    ax = axes[1, 2]
    ax.axis('off')
    mapping_text = """
    Analyzer → Crystal Mapping:
    -------------------------
    Fractal Dim → Lattice Constant
    Quantum Entropy → Unit Cell Volume
    Pattern Coherence → Symmetry Order
    Anomaly Score → Defect Density
    Evolution Velocity → Growth Rate
    """
    ax.text(0.1, 0.5, mapping_text, transform=ax.transAxes,
           fontsize=11, verticalalignment='center', fontfamily='monospace')
    
    plt.tight_layout()
    plt.show()


def main():
    """
    Main demonstration function showing all capabilities.
    """
    print("=== Temporal Crystal Visualization Demo ===\n")
    
    # 1. Generate different scenarios
    scenarios = ["evolution", "periodic", "chaotic", "convergent"]
    crystals = {}
    
    for scenario in scenarios:
        print(f"Generating {scenario} trajectory...")
        states = generate_mock_iam_trajectory(100, scenario=scenario)
        crystal = create_crystal_from_trajectory(states, name=f"{scenario}_crystal")
        crystals[scenario] = crystal
        
        # Print basic properties
        props = crystal.export_properties()
        print(f"  - Fractal dimension: {props['fractal_dimension']:.3f}")
        print(f"  - Average density: {props['average_density']:.3f}")
        print(f"  - Defects: {props['n_defects']}")
        print(f"  - Phase transitions: {props['n_phase_transitions']}")
        print()
    
    # 2. Visualize evolution scenario in detail
    print("Visualizing evolution scenario...")
    evolution_crystal = crystals["evolution"]
    
    # 3D projection
    print("  - Creating 3D projection...")
    visualize_crystal_3d_projection(evolution_crystal, projection_type="cognitive")
    
    # Property plots
    print("  - Plotting crystal properties...")
    plot_crystal_properties(evolution_crystal)
    
    # Animation
    print("  - Creating evolution animation...")
    animate_crystal_evolution(evolution_crystal)
    
    # 3. Compare different scenarios
    print("\nComparing scenarios...")
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Temporal Crystal Scenario Comparison', fontsize=16, fontweight='bold')
    
    for idx, (scenario, crystal) in enumerate(crystals.items()):
        ax = axes[idx // 2, idx % 2]
        trajectory = crystal.get_growth_trajectory()
        
        # Plot cognitive trajectories
        positions = np.array([s.state.cognitive_position for s in crystal.slices])
        ax.plot(positions[:, 0], positions[:, 1], alpha=0.7, linewidth=2)
        ax.scatter(positions[0, 0], positions[0, 1], color='green', s=100, 
                  marker='o', label='Start')
        ax.scatter(positions[-1, 0], positions[-1, 1], color='red', s=100, 
                  marker='s', label='End')
        
        ax.set_title(f'{scenario.capitalize()} Scenario')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axis('equal')
    
    plt.tight_layout()
    plt.show()
    
    # 4. Demonstrate fractal analyzer integration
    print("\nDemonstrating fractal analyzer integration...")
    demonstrate_fractal_analyzer_integration()
    
    # 5. Test prediction capability
    print("\nTesting prediction capability...")
    test_crystal = crystals["periodic"]
    predicted_state = test_crystal.predict_next_state(n_steps=5)
    
    if predicted_state:
        print(f"  - Predicted state at t={predicted_state.timestamp:.2f}")
        print(f"  - Cognitive position: {predicted_state.cognitive_position}")
        print(f"  - Quantum coherence: {np.abs(predicted_state.quantum_state).max():.3f}")
    
    # 6. Demonstrate interpolation
    print("\nDemonstrating crystal interpolation...")
    sparse_states = generate_mock_iam_trajectory(20, dt=0.5, scenario="evolution")
    sparse_crystal = create_crystal_from_trajectory(sparse_states, "sparse_crystal")
    
    interp_crystal = interpolate_crystal_states(sparse_crystal, target_resolution=0.1)
    print(f"  - Original slices: {len(sparse_crystal.slices)}")
    print(f"  - Interpolated slices: {len(interp_crystal.slices)}")
    
    print("\nDemo complete!")


if __name__ == "__main__":
    # Set style
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")
    
    # Run demonstration
    main()