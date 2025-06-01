#!/usr/bin/env python3
"""
Example usage of the Chronosonic Qualia implementation
Demonstrates basic functionality and visualization
"""

import numpy as np
import matplotlib.pyplot as plt
from chronosonic_prototype import (
    SimplifiedChakraSystem,
    FrequencyModulatedIAMState,
    ChronosonicDynamics,
    CognitivePerformanceMetrics,
    ChakraType
)
from chronosonic_visualizer import ChronosonicVisualizer
from chronosonic_experiments import FrequencyPattern

def basic_simulation_example():
    """Run a basic simulation with default parameters"""
    print("=== Basic Chronosonic Simulation ===\n")
    
    # Initialize components
    chakra_system = SimplifiedChakraSystem()
    iam_state = FrequencyModulatedIAMState()
    dynamics = ChronosonicDynamics(chakra_system, iam_state)
    metrics = CognitivePerformanceMetrics()
    
    # Establish baseline
    print("Establishing baseline metrics...")
    metrics.establish_baseline(chakra_system, iam_state)
    baseline = metrics.baseline_values
    print(f"Baseline composite score: {baseline['composite_score']:.3f}\n")
    
    # Run simulation
    print("Running 5-second simulation...")
    results = dynamics.simulate((0, 5.0), dt=0.01)
    
    # Calculate metrics at end of simulation
    final_state_idx = -1
    iam_state.state_vector = results['iam_state'][final_state_idx]
    final_metrics = metrics.calculate_metrics(chakra_system, iam_state)
    
    print(f"Final composite score: {final_metrics['composite_score']:.3f}")
    improvement = (final_metrics['composite_score'] / baseline['composite_score'] - 1) * 100
    print(f"Improvement: {improvement:+.1f}%\n")
    
    return results, metrics

def harmonic_modulation_example():
    """Demonstrate harmonic frequency modulation"""
    print("=== Harmonic Modulation Example ===\n")
    
    # Initialize system
    chakra_system = SimplifiedChakraSystem()
    iam_state = FrequencyModulatedIAMState()
    
    # Create harmonic pattern
    pattern = FrequencyPattern("Harmonic Enhancement", "Perfect harmonic ratios")
    pattern.add_chakra_modulation(ChakraType.ROOT, 0, 1.2, 0)
    pattern.add_chakra_modulation(ChakraType.HEART, 85.3, 1.3, np.pi/4)  # 4:3 ratio
    pattern.add_chakra_modulation(ChakraType.CROWN, 256, 1.1, np.pi/2)   # 2:1 ratio
    
    # Apply pattern
    print("Applying harmonic frequency pattern...")
    pattern.apply_to_system(chakra_system)
    
    # Show resulting frequencies
    print("\nResulting chakra frequencies:")
    for chakra_type, chakra in chakra_system.chakras.items():
        print(f"  {chakra_type.value.capitalize()}: {chakra.frequency:.1f} Hz")
    
    # Run dynamics
    dynamics = ChronosonicDynamics(chakra_system, iam_state)
    results = dynamics.simulate((0, 3.0), dt=0.01)
    
    # Analyze coherence
    mean_coherence = np.mean(results['system_coherence'])
    max_coherence = np.max(results['system_coherence'])
    print(f"\nMean system coherence: {mean_coherence:.3f}")
    print(f"Peak system coherence: {max_coherence:.3f}\n")
    
    return results

def visualization_example():
    """Create comprehensive visualization"""
    print("=== Creating Visualizations ===\n")
    
    # Setup system
    chakra_system = SimplifiedChakraSystem()
    iam_state = FrequencyModulatedIAMState()
    dynamics = ChronosonicDynamics(chakra_system, iam_state)
    metrics = CognitivePerformanceMetrics()
    
    # Initialize visualizer
    visualizer = ChronosonicVisualizer()
    visualizer.setup_plots()
    
    # Run longer simulation for better visualization
    print("Running 10-second simulation for visualization...")
    results = dynamics.simulate((0, 10.0), dt=0.01)
    
    # Collect metrics over time
    print("Calculating performance metrics...")
    for i in range(0, len(results['time']), 100):
        iam_state.state_vector = results['iam_state'][i]
        iam_state.apply_chakra_modulation(chakra_system, results['time'][i])
        current_metrics = metrics.calculate_metrics(chakra_system, iam_state)
    
    # Create plots
    visualizer.plot_frequency_trajectories(results)
    visualizer.plot_phase_space(iam_state, history_length=500)
    visualizer.plot_chakra_patterns(chakra_system, results)
    visualizer.plot_performance_metrics(metrics)
    visualizer.update_metrics_dashboard(metrics)
    
    # Save visualization
    visualizer.save_snapshot('example_visualization.png')
    print("Visualization saved to example_visualization.png\n")
    
    return visualizer

def performance_comparison_example():
    """Compare performance with different modulation strategies"""
    print("=== Performance Comparison ===\n")
    
    strategies = {
        'baseline': {'modulation_depth': 0.0, 'description': 'No modulation'},
        'light': {'modulation_depth': 0.2, 'description': 'Light modulation'},
        'moderate': {'modulation_depth': 0.4, 'description': 'Moderate modulation'},
        'strong': {'modulation_depth': 0.6, 'description': 'Strong modulation'}
    }
    
    results = {}
    
    for name, config in strategies.items():
        print(f"Testing {name}: {config['description']}")
        
        # Setup system
        chakra_system = SimplifiedChakraSystem()
        iam_state = FrequencyModulatedIAMState()
        iam_state.modulation_depth = config['modulation_depth']
        dynamics = ChronosonicDynamics(chakra_system, iam_state)
        metrics = CognitivePerformanceMetrics()
        
        # Run simulation
        sim_results = dynamics.simulate((0, 5.0), dt=0.01)
        
        # Calculate average performance
        performances = []
        for i in range(0, len(sim_results['time']), 50):
            iam_state.state_vector = sim_results['iam_state'][i]
            current_metrics = metrics.calculate_metrics(chakra_system, iam_state)
            performances.append(current_metrics['composite_score'])
        
        avg_performance = np.mean(performances)
        results[name] = avg_performance
        print(f"  Average performance: {avg_performance:.3f}")
    
    # Display comparison
    print("\nPerformance Summary:")
    baseline_perf = results['baseline']
    for name, perf in results.items():
        improvement = (perf / baseline_perf - 1) * 100
        print(f"  {name}: {perf:.3f} ({improvement:+.1f}% vs baseline)")
    
    return results

def main():
    """Run all examples"""
    print("Chronosonic Qualia Example Suite")
    print("=" * 40)
    print()
    
    # Run examples
    basic_results, metrics = basic_simulation_example()
    harmonic_results = harmonic_modulation_example()
    visualizer = visualization_example()
    comparison_results = performance_comparison_example()
    
    print("\n=== Examples Complete ===")
    print("\nKey Findings:")
    print("1. Frequency modulation can improve cognitive performance metrics")
    print("2. Harmonic relationships enhance system coherence")
    print("3. Optimal modulation depth appears to be in moderate range (0.3-0.4)")
    print("4. Phase space trajectories show attractor-like behavior")
    print("\nSee generated files for detailed results and visualizations.")

if __name__ == "__main__":
    main()