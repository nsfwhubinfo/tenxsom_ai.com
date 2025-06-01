#!/usr/bin/env python3
"""
Extended Test Suite for CHRONOSONIC Qualia Prototype
Comprehensive testing of frequency modulation, chakra dynamics, and cognitive performance
"""

import unittest
import numpy as np
import sys
import os
from pathlib import Path
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import tempfile
import warnings

# Add research directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "research" / "chronosonic_qualia"))

from chronosonic_prototype import (
    ChakraType, ChakraState, SimplifiedChakraSystem,
    FrequencyModulatedIAMState, ChronosonicDynamics,
    ComplexIAMFractalAnalyzer, CognitivePerformanceMetrics
)
from chronosonic_experiments import (
    FrequencyPattern, ChronosonicExperiment,
    FrequencyPatternExperiment, CognitivePerformanceComparison,
    FractalSignatureAnalysis, EmpiricalValidationProtocol
)


class TestChakraSystem(unittest.TestCase):
    """Test the chakra system components"""
    
    def setUp(self):
        """Initialize test components"""
        self.chakra_system = SimplifiedChakraSystem()
        
    def test_chakra_initialization(self):
        """Test proper chakra initialization"""
        # Check all chakras are created
        self.assertEqual(len(self.chakra_system.chakras), 3)
        
        # Check chakra types
        expected_types = {ChakraType.ROOT, ChakraType.HEART, ChakraType.CROWN}
        actual_types = set(self.chakra_system.chakras.keys())
        self.assertEqual(expected_types, actual_types)
        
        # Check base frequencies
        self.assertEqual(self.chakra_system.chakras[ChakraType.ROOT].frequency, 256.0)
        self.assertEqual(self.chakra_system.chakras[ChakraType.HEART].frequency, 341.3)
        self.assertEqual(self.chakra_system.chakras[ChakraType.CROWN].frequency, 512.0)
        
    def test_chakra_waveform_generation(self):
        """Test chakra waveform generation"""
        t = np.linspace(0, 1, 1000)
        root_chakra = self.chakra_system.chakras[ChakraType.ROOT]
        waveform = root_chakra.get_waveform(t)
        
        # Check waveform properties
        self.assertEqual(len(waveform), len(t))
        self.assertTrue(np.all(np.abs(waveform) <= root_chakra.amplitude))
        
        # Check frequency content using FFT
        fft = np.fft.fft(waveform)
        freqs = np.fft.fftfreq(len(t), t[1] - t[0])
        peak_freq_idx = np.argmax(np.abs(fft[:len(fft)//2]))
        peak_freq = np.abs(freqs[peak_freq_idx])
        
        # Allow 1% tolerance for frequency accuracy
        self.assertAlmostEqual(peak_freq, root_chakra.frequency, delta=root_chakra.frequency * 0.01)
        
    def test_chakra_state_update(self):
        """Test chakra state updates"""
        original_freq = self.chakra_system.chakras[ChakraType.HEART].frequency
        original_amp = self.chakra_system.chakras[ChakraType.HEART].amplitude
        
        # Update state
        self.chakra_system.update_state(
            ChakraType.HEART,
            frequency=400.0,
            amplitude=0.8,
            phase=np.pi/4
        )
        
        # Verify updates
        heart_chakra = self.chakra_system.chakras[ChakraType.HEART]
        self.assertEqual(heart_chakra.frequency, 400.0)
        self.assertEqual(heart_chakra.amplitude, 0.8)
        self.assertEqual(heart_chakra.phase, np.pi/4)
        
    def test_system_coherence(self):
        """Test system coherence calculation"""
        # Set all chakras to same coherence
        for chakra_type in self.chakra_system.chakras:
            self.chakra_system.update_state(chakra_type, coherence=0.7)
            
        coherence = self.chakra_system.get_system_coherence()
        self.assertAlmostEqual(coherence, 0.7)
        
        # Test with different coherences
        self.chakra_system.update_state(ChakraType.ROOT, coherence=0.5)
        self.chakra_system.update_state(ChakraType.HEART, coherence=0.8)
        self.chakra_system.update_state(ChakraType.CROWN, coherence=0.9)
        
        expected_coherence = (0.5 + 0.8 + 0.9) / 3
        actual_coherence = self.chakra_system.get_system_coherence()
        self.assertAlmostEqual(actual_coherence, expected_coherence)
        
    def test_frequency_matrix(self):
        """Test frequency interaction matrix"""
        matrix = self.chakra_system.get_frequency_matrix()
        
        # Check matrix properties
        self.assertEqual(matrix.shape, (3, 3))
        self.assertTrue(np.all(matrix >= 0))
        self.assertTrue(np.all(matrix <= 1))
        
        # Check diagonal is 1
        np.testing.assert_array_equal(np.diag(matrix), [1.0, 1.0, 1.0])
        
        # Check symmetry
        self.assertTrue(np.allclose(matrix, matrix.T))
        
        # Check harmonic relationships
        # Root to Crown should have high coherence (2:1 octave)
        root_idx = list(self.chakra_system.chakras.keys()).index(ChakraType.ROOT)
        crown_idx = list(self.chakra_system.chakras.keys()).index(ChakraType.CROWN)
        self.assertGreater(matrix[root_idx, crown_idx], 0.8)


class TestFrequencyModulatedIAMState(unittest.TestCase):
    """Test the frequency-modulated <I_AM> state"""
    
    def setUp(self):
        """Initialize test components"""
        self.iam_state = FrequencyModulatedIAMState()
        self.chakra_system = SimplifiedChakraSystem()
        
    def test_iam_initialization(self):
        """Test IAM state initialization"""
        self.assertEqual(self.iam_state.dimension, 7)
        self.assertEqual(len(self.iam_state.state_vector), 7)
        self.assertEqual(len(self.iam_state.frequency_components), 7)
        self.assertEqual(self.iam_state.phase_coupling.shape, (7, 7))
        
        # Check default parameters
        self.assertEqual(self.iam_state.modulation_depth, 0.3)
        self.assertEqual(self.iam_state.carrier_frequency, 10.0)
        
    def test_chakra_modulation(self):
        """Test chakra frequency modulation on IAM state"""
        initial_state = self.iam_state.state_vector.copy()
        
        # Apply modulation at different time points
        for t in np.linspace(0, 1, 10):
            self.iam_state.apply_chakra_modulation(self.chakra_system, t)
            
        # State should have changed
        self.assertFalse(np.array_equal(initial_state, self.iam_state.state_vector))
        
        # State should remain normalized
        norm = np.linalg.norm(self.iam_state.state_vector)
        self.assertAlmostEqual(norm, 1.0, places=6)
        
    def test_fractal_dimension_calculation(self):
        """Test fractal dimension calculation"""
        # Test with known patterns
        # Uniform distribution should have higher dimension
        self.iam_state.state_vector = np.ones(7) / np.sqrt(7)
        dim_uniform = self.iam_state.get_fractal_dimension()
        
        # Sparse distribution should have lower dimension
        self.iam_state.state_vector = np.zeros(7)
        self.iam_state.state_vector[0] = 1.0
        dim_sparse = self.iam_state.get_fractal_dimension()
        
        # Uniform should have higher fractal dimension
        self.assertGreater(dim_uniform, dim_sparse)
        
        # Dimensions should be positive
        self.assertGreater(dim_uniform, 0)
        self.assertGreater(dim_sparse, 0)
        
    def test_modulation_depth_effect(self):
        """Test effect of modulation depth"""
        # Test with no modulation
        self.iam_state.modulation_depth = 0.0
        initial_state = self.iam_state.state_vector.copy()
        self.iam_state.apply_chakra_modulation(self.chakra_system, 0.5)
        
        # With zero depth, modulation should have minimal effect
        # (only normalization might cause small differences)
        self.assertTrue(np.allclose(initial_state, self.iam_state.state_vector, atol=1e-10))
        
        # Test with high modulation
        self.iam_state.modulation_depth = 0.9
        self.iam_state.apply_chakra_modulation(self.chakra_system, 0.5)
        
        # Should have significant change
        self.assertFalse(np.allclose(initial_state, self.iam_state.state_vector, atol=0.1))


class TestChronosonicDynamics(unittest.TestCase):
    """Test the chronosonic dynamics system"""
    
    def setUp(self):
        """Initialize test components"""
        self.chakra_system = SimplifiedChakraSystem()
        self.iam_state = FrequencyModulatedIAMState()
        self.dynamics = ChronosonicDynamics(self.chakra_system, self.iam_state)
        
    def test_dynamics_initialization(self):
        """Test dynamics system initialization"""
        self.assertEqual(self.dynamics.coupling_strength, 0.1)
        self.assertEqual(self.dynamics.nonlinearity, 0.05)
        self.assertIs(self.dynamics.chakra_system, self.chakra_system)
        self.assertIs(self.dynamics.iam_state, self.iam_state)
        
    def test_state_equations(self):
        """Test differential equations"""
        # Create initial state vector
        n_chakras = 3
        chakra_amps = np.array([0.5, 0.5, 0.5])
        chakra_phases = np.array([0, np.pi/4, np.pi/2])
        iam_components = self.iam_state.state_vector
        
        initial_state = np.concatenate([chakra_amps, chakra_phases, iam_components])
        
        # Calculate derivatives
        derivatives = self.dynamics.state_equations(initial_state, 0.0)
        
        # Check output shape
        self.assertEqual(len(derivatives), len(initial_state))
        
        # Check that derivatives are finite
        self.assertTrue(np.all(np.isfinite(derivatives)))
        
    def test_simulation(self):
        """Test simulation execution"""
        # Run short simulation
        results = self.dynamics.simulate((0, 1.0), dt=0.01)
        
        # Check results structure
        self.assertIn('time', results)
        self.assertIn('chakra_amplitudes', results)
        self.assertIn('chakra_phases', results)
        self.assertIn('iam_state', results)
        self.assertIn('system_coherence', results)
        
        # Check dimensions
        n_steps = len(results['time'])
        self.assertEqual(results['chakra_amplitudes'].shape, (n_steps, 3))
        self.assertEqual(results['chakra_phases'].shape, (n_steps, 3))
        self.assertEqual(results['iam_state'].shape, (n_steps, 7))
        self.assertEqual(len(results['system_coherence']), n_steps)
        
        # Check time array
        self.assertAlmostEqual(results['time'][0], 0.0)
        self.assertAlmostEqual(results['time'][-1], 1.0, places=2)
        
    def test_phase_synchronization(self):
        """Test phase synchronization dynamics"""
        # Set strong coupling
        self.dynamics.coupling_strength = 0.5
        
        # Initialize with random phases
        for chakra_type in self.chakra_system.chakras:
            self.chakra_system.update_state(
                chakra_type,
                phase=np.random.uniform(0, 2*np.pi)
            )
            
        # Run simulation
        results = self.dynamics.simulate((0, 5.0), dt=0.01)
        
        # Check if phases tend to synchronize
        initial_coherence = results['system_coherence'][0]
        final_coherence = results['system_coherence'][-1]
        
        # With strong coupling, coherence should increase
        self.assertGreater(final_coherence, initial_coherence)
        
    def test_energy_conservation(self):
        """Test approximate energy conservation"""
        results = self.dynamics.simulate((0, 2.0), dt=0.01)
        
        # Calculate total "energy" at each step
        energies = []
        for i in range(len(results['time'])):
            # Amplitude energy
            amp_energy = np.sum(results['chakra_amplitudes'][i]**2)
            # IAM state energy
            iam_energy = np.sum(results['iam_state'][i]**2)
            total_energy = amp_energy + iam_energy
            energies.append(total_energy)
            
        # Energy should be approximately conserved
        energy_variation = (np.max(energies) - np.min(energies)) / np.mean(energies)
        self.assertLess(energy_variation, 0.2)  # Less than 20% variation


class TestCognitivePerformanceMetrics(unittest.TestCase):
    """Test cognitive performance measurement"""
    
    def setUp(self):
        """Initialize test components"""
        self.metrics = CognitivePerformanceMetrics()
        self.chakra_system = SimplifiedChakraSystem()
        self.iam_state = FrequencyModulatedIAMState()
        
    def test_metrics_calculation(self):
        """Test performance metrics calculation"""
        metrics = self.metrics.calculate_metrics(self.chakra_system, self.iam_state)
        
        # Check all required metrics are present
        required_metrics = [
            'coherence_index', 'fractal_complexity', 'state_stability',
            'frequency_alignment', 'information_flow', 'composite_score'
        ]
        for metric in required_metrics:
            self.assertIn(metric, metrics)
            
        # Check metric ranges
        for key, value in metrics.items():
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)
            
    def test_baseline_establishment(self):
        """Test baseline metrics establishment"""
        self.assertFalse(self.metrics.baseline_established)
        
        self.metrics.establish_baseline(self.chakra_system, self.iam_state)
        
        self.assertTrue(self.metrics.baseline_established)
        self.assertIsNotNone(self.metrics.baseline_values)
        self.assertGreater(len(self.metrics.baseline_values), 0)
        
    def test_improvement_ratio(self):
        """Test improvement ratio calculation"""
        # Establish baseline
        self.metrics.establish_baseline(self.chakra_system, self.iam_state)
        
        # Calculate current metrics
        self.metrics.calculate_metrics(self.chakra_system, self.iam_state)
        
        # Get improvement ratios
        ratios = self.metrics.get_improvement_ratio()
        
        # All ratios should be positive
        for ratio in ratios.values():
            self.assertGreater(ratio, 0)
            
    def test_frequency_alignment_calculation(self):
        """Test frequency alignment metric"""
        # Set perfect harmonic ratios
        self.chakra_system.update_state(ChakraType.ROOT, frequency=200.0)
        self.chakra_system.update_state(ChakraType.HEART, frequency=300.0)  # 3:2
        self.chakra_system.update_state(ChakraType.CROWN, frequency=400.0)  # 2:1
        
        metrics = self.metrics.calculate_metrics(self.chakra_system, self.iam_state)
        
        # Should have high frequency alignment
        self.assertGreater(metrics['frequency_alignment'], 0.8)
        
        # Set dissonant frequencies
        self.chakra_system.update_state(ChakraType.ROOT, frequency=200.0)
        self.chakra_system.update_state(ChakraType.HEART, frequency=277.3)  # Non-harmonic
        self.chakra_system.update_state(ChakraType.CROWN, frequency=431.7)  # Non-harmonic
        
        metrics_dissonant = self.metrics.calculate_metrics(self.chakra_system, self.iam_state)
        
        # Should have lower frequency alignment
        self.assertLess(metrics_dissonant['frequency_alignment'], 
                       metrics['frequency_alignment'])


class TestFrequencyPatterns(unittest.TestCase):
    """Test frequency pattern experiments"""
    
    def setUp(self):
        """Initialize test components"""
        self.patterns = self._create_test_patterns()
        
    def _create_test_patterns(self) -> List[FrequencyPattern]:
        """Create test frequency patterns"""
        patterns = []
        
        # Baseline pattern (no modulation)
        baseline = FrequencyPattern("Baseline", "No frequency modulation")
        patterns.append(baseline)
        
        # Harmonic pattern
        harmonic = FrequencyPattern("Harmonic", "Simple harmonic ratios")
        harmonic.add_chakra_modulation(ChakraType.ROOT, 0, 1.0)
        harmonic.add_chakra_modulation(ChakraType.HEART, 128, 1.2)  # 3:2 ratio
        harmonic.add_chakra_modulation(ChakraType.CROWN, 256, 1.0)  # 2:1 octave
        patterns.append(harmonic)
        
        # Golden ratio pattern
        golden = FrequencyPattern("Golden", "Golden ratio relationships")
        phi = 1.618033988749
        golden.add_chakra_modulation(ChakraType.ROOT, 0, 1.0)
        golden.add_chakra_modulation(ChakraType.HEART, 256 * (phi - 1), 1.1)
        golden.add_chakra_modulation(ChakraType.CROWN, 256 * (phi - 1), 0.9)
        patterns.append(golden)
        
        return patterns
        
    def test_pattern_application(self):
        """Test applying patterns to chakra system"""
        chakra_system = SimplifiedChakraSystem()
        
        for pattern in self.patterns:
            # Store original frequencies
            original_freqs = {
                chakra_type: chakra.frequency 
                for chakra_type, chakra in chakra_system.chakras.items()
            }
            
            # Apply pattern
            pattern.apply_to_system(chakra_system)
            
            # Check if pattern was applied
            if pattern.modulations:
                # At least one frequency should have changed
                new_freqs = {
                    chakra_type: chakra.frequency 
                    for chakra_type, chakra in chakra_system.chakras.items()
                }
                self.assertNotEqual(original_freqs, new_freqs)
                
    def test_pattern_experiment(self):
        """Test frequency pattern experiment execution"""
        experiment = FrequencyPatternExperiment(self.patterns[:2], duration=1.0)
        
        # Run experiment
        results = experiment.run()
        
        # Check results structure
        self.assertEqual(len(results), 2)  # Two patterns tested
        
        for pattern_name, pattern_results in results.items():
            self.assertIn('dynamics', pattern_results)
            self.assertIn('metrics', pattern_results)
            self.assertIn('fractal_analysis', pattern_results)
            self.assertIn('final_improvement', pattern_results)
            
    def test_fractal_analysis(self):
        """Test fractal signature analysis"""
        freq_ranges = [(100, 300), (200, 600)]
        experiment = FractalSignatureAnalysis(freq_ranges, duration=1.0)
        
        results = experiment.run()
        
        # Check results for each frequency range
        self.assertEqual(len(results), 2)
        
        for range_name, analysis in results.items():
            self.assertIn('multifractal_spectrum', analysis)
            self.assertIn('dfa_results', analysis)
            self.assertIn('recurrence_metrics', analysis)
            self.assertIn('lyapunov_estimate', analysis)


class TestEmpiricalValidation(unittest.TestCase):
    """Test empirical validation protocols"""
    
    def setUp(self):
        """Initialize validation protocol"""
        self.validator = EmpiricalValidationProtocol()
        
    def test_validation_conditions(self):
        """Test validation test conditions"""
        conditions = self.validator.test_conditions
        
        # Should have multiple test conditions
        self.assertGreater(len(conditions), 0)
        
        # Each condition should have required fields
        for condition in conditions:
            self.assertIn('name', condition)
            self.assertIn('description', condition)
            self.assertIn('modulation_depth', condition)
            self.assertIn('frequency_pattern', condition)
            
    def test_reproducibility_testing(self):
        """Test reproducibility validation"""
        # Run with fewer iterations for testing
        results = self.validator._test_reproducibility(n_runs=3)
        
        # Check results structure
        self.assertIsInstance(results, dict)
        
        for condition_name, condition_results in results.items():
            self.assertIn('runs', condition_results)
            self.assertIn('mean', condition_results)
            self.assertIn('std', condition_results)
            self.assertIn('cv', condition_results)
            
            # CV should be reasonable (not too high)
            self.assertLess(condition_results['cv'], 0.5)
            
    def test_sensitivity_analysis(self):
        """Test parameter sensitivity analysis"""
        results = self.validator._sensitivity_analysis()
        
        # Check results for each parameter
        expected_params = ['modulation_depth', 'coupling_strength', 'carrier_frequency']
        
        for param in expected_params:
            self.assertIn(param, results)
            param_results = results[param]
            
            self.assertIn('values', param_results)
            self.assertIn('responses', param_results)
            self.assertIn('sensitivity', param_results)
            
            # Sensitivity should be non-negative
            self.assertGreaterEqual(param_results['sensitivity'], 0)
            
    def test_cross_validation(self):
        """Test cross-validation protocol"""
        results = self.validator._cross_validation(n_folds=3)
        
        # Check results structure
        self.assertIn('fold_results', results)
        self.assertIn('mean_test_improvement', results)
        self.assertIn('cv_score', results)
        
        # Check fold results
        self.assertEqual(len(results['fold_results']), 3)
        
        for fold_result in results['fold_results']:
            self.assertIn('fold', fold_result)
            self.assertIn('train_mean_improvement', fold_result)
            self.assertIn('test_mean_improvement', fold_result)
            
    def test_validation_report_generation(self):
        """Test validation report generation"""
        # Run minimal validation
        self.validator._test_reproducibility(n_runs=2)
        self.validator._sensitivity_analysis()
        self.validator._cross_validation(n_folds=2)
        
        # Generate report
        report = self.validator._generate_validation_report()
        
        # Check report structure
        self.assertIn('summary', report)
        self.assertIn('reproducibility_summary', report)
        self.assertIn('sensitivity_summary', report)
        self.assertIn('cross_validation_summary', report)
        self.assertIn('recommendations', report)
        
        # Check summary fields
        self.assertIn('overall_validity', report['summary'])
        self.assertGreaterEqual(report['summary']['overall_validity'], 0)
        self.assertLessEqual(report['summary']['overall_validity'], 1)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for complete scenarios"""
    
    def test_complete_simulation_workflow(self):
        """Test complete simulation workflow"""
        # Initialize system
        chakra_system = SimplifiedChakraSystem()
        iam_state = FrequencyModulatedIAMState()
        dynamics = ChronosonicDynamics(chakra_system, iam_state)
        metrics = CognitivePerformanceMetrics()
        
        # Establish baseline
        metrics.establish_baseline(chakra_system, iam_state)
        
        # Apply frequency modulation
        chakra_system.update_state(ChakraType.HEART, frequency=400.0, amplitude=0.8)
        
        # Run simulation
        results = dynamics.simulate((0, 2.0), dt=0.01)
        
        # Calculate performance throughout
        performance_trajectory = []
        for i in range(0, len(results['time']), 50):
            iam_state.state_vector = results['iam_state'][i]
            current_metrics = metrics.calculate_metrics(chakra_system, iam_state)
            performance_trajectory.append(current_metrics['composite_score'])
            
        # Performance should vary over time
        self.assertGreater(np.std(performance_trajectory), 0)
        
        # Get final improvement
        final_improvement = metrics.get_improvement_ratio()
        self.assertIsInstance(final_improvement, dict)
        
    def test_frequency_pattern_comparison(self):
        """Test comparing multiple frequency patterns"""
        # Create patterns
        patterns = [
            FrequencyPattern("Control", "No modulation"),
            FrequencyPattern("Harmonic", "Harmonic ratios"),
            FrequencyPattern("Dissonant", "Dissonant frequencies")
        ]
        
        # Configure harmonic pattern
        patterns[1].add_chakra_modulation(ChakraType.ROOT, 0, 1.0)
        patterns[1].add_chakra_modulation(ChakraType.HEART, 85.3, 1.0)  # 4:3
        patterns[1].add_chakra_modulation(ChakraType.CROWN, 256, 1.0)  # 2:1
        
        # Configure dissonant pattern
        patterns[2].add_chakra_modulation(ChakraType.ROOT, 17.3, 0.8)
        patterns[2].add_chakra_modulation(ChakraType.HEART, -23.7, 1.2)
        patterns[2].add_chakra_modulation(ChakraType.CROWN, 41.1, 0.9)
        
        # Run experiment
        experiment = FrequencyPatternExperiment(patterns, duration=1.0)
        results = experiment.run()
        
        # Harmonic pattern should perform better than dissonant
        harmonic_score = results['Harmonic']['metrics'][-1]['composite_score']
        dissonant_score = results['Dissonant']['metrics'][-1]['composite_score']
        
        self.assertGreater(harmonic_score, dissonant_score)
        
    def test_long_duration_stability(self):
        """Test system stability over longer durations"""
        chakra_system = SimplifiedChakraSystem()
        iam_state = FrequencyModulatedIAMState()
        dynamics = ChronosonicDynamics(chakra_system, iam_state)
        
        # Run longer simulation
        results = dynamics.simulate((0, 10.0), dt=0.1)
        
        # Check for numerical stability
        self.assertTrue(np.all(np.isfinite(results['chakra_amplitudes'])))
        self.assertTrue(np.all(np.isfinite(results['chakra_phases'])))
        self.assertTrue(np.all(np.isfinite(results['iam_state'])))
        
        # Amplitudes should remain bounded
        self.assertTrue(np.all(results['chakra_amplitudes'] >= 0))
        self.assertTrue(np.all(results['chakra_amplitudes'] <= 2))
        
        # Phases should remain in reasonable range (allowing for multiple rotations)
        self.assertTrue(np.all(np.abs(results['chakra_phases']) < 100 * 2 * np.pi))


class TestPerformanceOptimization(unittest.TestCase):
    """Test performance and optimization aspects"""
    
    def test_simulation_performance(self):
        """Test simulation execution time"""
        chakra_system = SimplifiedChakraSystem()
        iam_state = FrequencyModulatedIAMState()
        dynamics = ChronosonicDynamics(chakra_system, iam_state)
        
        # Time a moderate simulation
        start_time = time.time()
        results = dynamics.simulate((0, 5.0), dt=0.01)
        elapsed_time = time.time() - start_time
        
        # Should complete in reasonable time (less than 5 seconds)
        self.assertLess(elapsed_time, 5.0)
        
        # Calculate simulation speed
        sim_steps = len(results['time'])
        steps_per_second = sim_steps / elapsed_time
        
        # Should achieve reasonable performance
        self.assertGreater(steps_per_second, 100)  # At least 100 steps/second
        
    def test_memory_efficiency(self):
        """Test memory usage efficiency"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create multiple systems
        systems = []
        for _ in range(10):
            chakra_system = SimplifiedChakraSystem()
            iam_state = FrequencyModulatedIAMState()
            dynamics = ChronosonicDynamics(chakra_system, iam_state)
            systems.append((chakra_system, iam_state, dynamics))
            
        # Run simulations
        for chakra_system, iam_state, dynamics in systems:
            results = dynamics.simulate((0, 1.0), dt=0.01)
            
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100 MB)
        self.assertLess(memory_increase, 100)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def test_invalid_chakra_updates(self):
        """Test handling of invalid chakra updates"""
        chakra_system = SimplifiedChakraSystem()
        
        # Should handle negative frequency gracefully
        chakra_system.update_state(ChakraType.ROOT, frequency=-100)
        # System should still function
        coherence = chakra_system.get_system_coherence()
        self.assertIsInstance(coherence, float)
        
    def test_extreme_parameters(self):
        """Test system behavior with extreme parameters"""
        chakra_system = SimplifiedChakraSystem()
        iam_state = FrequencyModulatedIAMState()
        
        # Test with very high modulation depth
        iam_state.modulation_depth = 0.99
        dynamics = ChronosonicDynamics(chakra_system, iam_state)
        
        # Should still run without errors
        results = dynamics.simulate((0, 0.5), dt=0.01)
        self.assertIsNotNone(results)
        
        # Test with very high coupling
        dynamics.coupling_strength = 0.99
        results = dynamics.simulate((0, 0.5), dt=0.01)
        self.assertIsNotNone(results)
        
    def test_zero_amplitude_handling(self):
        """Test handling of zero amplitudes"""
        chakra_system = SimplifiedChakraSystem()
        
        # Set all amplitudes to zero
        for chakra_type in chakra_system.chakras:
            chakra_system.update_state(chakra_type, amplitude=0.0)
            
        iam_state = FrequencyModulatedIAMState()
        dynamics = ChronosonicDynamics(chakra_system, iam_state)
        
        # Should handle gracefully
        results = dynamics.simulate((0, 1.0), dt=0.01)
        self.assertTrue(np.all(np.isfinite(results['iam_state'])))


class TestDataPersistence(unittest.TestCase):
    """Test data saving and loading"""
    
    def test_experiment_results_saving(self):
        """Test saving experiment results"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create simple experiment
            patterns = [FrequencyPattern("Test", "Test pattern")]
            experiment = FrequencyPatternExperiment(patterns, duration=0.5)
            results = experiment.run()
            
            # Save results
            filename = os.path.join(temp_dir, "test_results.json")
            experiment.save_results(filename)
            
            # Check file exists
            self.assertTrue(os.path.exists(filename))
            
            # Load and verify
            with open(filename, 'r') as f:
                loaded_data = json.load(f)
                
            self.assertEqual(loaded_data['experiment_name'], "Frequency Pattern Comparison")
            self.assertIn('results', loaded_data)
            self.assertIn('timestamp', loaded_data)
            
    def test_validation_report_saving(self):
        """Test validation report persistence"""
        validator = EmpiricalValidationProtocol()
        
        # Run minimal validation
        validator._test_reproducibility(n_runs=2)
        
        report = validator._generate_validation_report()
        
        # Should be JSON serializable
        json_str = json.dumps(report, default=str)
        self.assertIsInstance(json_str, str)
        
        # Should be able to reload
        reloaded = json.loads(json_str)
        self.assertEqual(reloaded['summary']['protocol_version'], 
                        report['summary']['protocol_version'])


# Performance benchmark suite
class ChronosonicBenchmarkSuite:
    """Benchmark suite for performance testing"""
    
    @staticmethod
    def run_benchmarks():
        """Run performance benchmarks"""
        results = {}
        
        # Benchmark 1: Simulation speed
        print("Running simulation speed benchmark...")
        chakra_system = SimplifiedChakraSystem()
        iam_state = FrequencyModulatedIAMState()
        dynamics = ChronosonicDynamics(chakra_system, iam_state)
        
        durations = [1.0, 5.0, 10.0]
        for duration in durations:
            start = time.time()
            results_sim = dynamics.simulate((0, duration), dt=0.01)
            elapsed = time.time() - start
            
            steps = len(results_sim['time'])
            results[f'sim_{duration}s'] = {
                'duration': duration,
                'steps': steps,
                'time': elapsed,
                'steps_per_second': steps / elapsed
            }
            
        # Benchmark 2: Pattern comparison
        print("Running pattern comparison benchmark...")
        patterns = []
        for i in range(5):
            p = FrequencyPattern(f"Pattern_{i}", f"Test pattern {i}")
            p.add_chakra_modulation(ChakraType.ROOT, i * 10, 1.0)
            patterns.append(p)
            
        start = time.time()
        experiment = FrequencyPatternExperiment(patterns, duration=2.0)
        exp_results = experiment.run()
        elapsed = time.time() - start
        
        results['pattern_comparison'] = {
            'n_patterns': len(patterns),
            'time': elapsed,
            'patterns_per_second': len(patterns) / elapsed
        }
        
        # Benchmark 3: Validation suite
        print("Running validation benchmark...")
        validator = EmpiricalValidationProtocol()
        
        start = time.time()
        validator._test_reproducibility(n_runs=3)
        validator._sensitivity_analysis()
        validator._cross_validation(n_folds=3)
        elapsed = time.time() - start
        
        results['validation_suite'] = {
            'time': elapsed,
            'tests_completed': 3
        }
        
        return results


def run_extended_test_suite():
    """Run the complete extended test suite"""
    print("=" * 80)
    print("CHRONOSONIC Extended Test Suite")
    print("=" * 80)
    print(f"Started at: {datetime.now()}")
    print()
    
    # Configure test runner
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestChakraSystem,
        TestFrequencyModulatedIAMState,
        TestChronosonicDynamics,
        TestCognitivePerformanceMetrics,
        TestFrequencyPatterns,
        TestEmpiricalValidation,
        TestIntegrationScenarios,
        TestPerformanceOptimization,
        TestErrorHandling,
        TestDataPersistence
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
        
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    
    # Run benchmarks if all tests pass
    if result.wasSuccessful():
        print("\n" + "=" * 80)
        print("Running Performance Benchmarks")
        print("=" * 80)
        
        benchmark_results = ChronosonicBenchmarkSuite.run_benchmarks()
        
        print("\nBenchmark Results:")
        for name, data in benchmark_results.items():
            print(f"\n{name}:")
            for key, value in data.items():
                print(f"  {key}: {value}")
                
    print(f"\nCompleted at: {datetime.now()}")
    
    return result


if __name__ == "__main__":
    # Run extended test suite
    result = run_extended_test_suite()
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)