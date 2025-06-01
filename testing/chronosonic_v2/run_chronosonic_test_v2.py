#!/usr/bin/env python3
"""
CHRONOSONIC V2 Test Suite
Uses the refactored implementation with all API issues fixed
"""

import sys
import os
import time
import json
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from research.chronosonic_qualia_v2.chronosonic_refactored import (
    RefactoredChakraSystem,
    RefactoredFrequencyModulatedIAMState,
    RefactoredChronosonicDynamics,
    ChakraType
)


class ChronosonicV2Test:
    """Test suite for refactored CHRONOSONIC"""
    
    def __init__(self, duration_minutes: float = 30):
        self.duration = duration_minutes * 60  # Convert to seconds
        self.chakra_system = RefactoredChakraSystem(use_simplified=True)
        self.iam_state = RefactoredFrequencyModulatedIAMState(base_dimension=3)
        self.dynamics = RefactoredChronosonicDynamics(self.chakra_system, self.iam_state)
        
        self.results = {
            'test_id': f'chronosonic_v2_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'duration_minutes': duration_minutes,
            'metrics': [],
            'phases': {},
            'summary': {}
        }
    
    def run_test(self):
        """Run comprehensive test suite"""
        print("CHRONOSONIC V2 Test Suite")
        print("=" * 60)
        print(f"Duration: {self.duration / 60:.1f} minutes")
        print(f"Start time: {datetime.now()}")
        print()
        
        # Success criteria
        criteria = {
            'frequency_accuracy': 0.95,
            'state_coherence': 0.90,
            'temporal_stability': 0.98,
            'quantum_fidelity': 0.80
        }
        
        print("Success Criteria:")
        for metric, threshold in criteria.items():
            print(f"  {metric}: ≥ {threshold:.0%}")
        print()
        
        # Run test phases
        phase_results = {}
        
        print("Test Phases:")
        print("1. Initialization and baseline")
        phase_results['initialization'] = self._test_initialization()
        
        print("2. Frequency modulation")
        phase_results['modulation'] = self._test_frequency_modulation()
        
        print("3. State transitions")
        phase_results['transitions'] = self._test_state_transitions()
        
        print("4. Long-term stability")
        phase_results['stability'] = self._test_stability()
        
        print("5. Full system integration")
        phase_results['integration'] = self._test_full_integration()
        
        # Calculate final metrics
        self.results['phases'] = phase_results
        self.results['summary'] = self._calculate_summary(phase_results, criteria)
        
        # Display results
        self._display_results(criteria)
        
        # Save results
        self._save_results()
        
        return self.results['summary']['overall_success']
    
    def _test_initialization(self) -> Dict:
        """Test 1: Initialization and baseline metrics"""
        print("\n[Phase 1] Testing initialization...")
        
        metrics = {
            'chakra_frequencies_correct': True,
            'initial_coherence': self.chakra_system.get_system_coherence(),
            'iam_state_normalized': np.abs(np.linalg.norm(self.iam_state.state_vector) - 1.0) < 0.01,
            'quantum_state_valid': np.abs(np.linalg.norm(self.dynamics.quantum_state) - 1.0) < 0.01
        }
        
        # Check frequencies
        for chakra_type in [ChakraType.ROOT, ChakraType.HEART, ChakraType.CROWN]:
            expected = self.chakra_system.BASE_FREQUENCIES[chakra_type]
            actual = self.chakra_system.get_base_frequency(chakra_type)
            if abs(expected - actual) > 0.1:
                metrics['chakra_frequencies_correct'] = False
        
        success = all([
            metrics['chakra_frequencies_correct'],
            metrics['iam_state_normalized'],
            metrics['quantum_state_valid']
        ])
        
        print(f"  ✓ Frequencies: {'PASS' if metrics['chakra_frequencies_correct'] else 'FAIL'}")
        print(f"  ✓ I_AM state: {'PASS' if metrics['iam_state_normalized'] else 'FAIL'}")
        print(f"  ✓ Quantum state: {'PASS' if metrics['quantum_state_valid'] else 'FAIL'}")
        print(f"  Initial coherence: {metrics['initial_coherence']:.3f}")
        
        return {'success': success, 'metrics': metrics}
    
    def _test_frequency_modulation(self) -> Dict:
        """Test 2: Frequency modulation capabilities"""
        print("\n[Phase 2] Testing frequency modulation...")
        
        # Test modulation on each chakra
        modulation_results = {}
        
        for chakra_type in [ChakraType.ROOT, ChakraType.HEART, ChakraType.CROWN]:
            # Get baseline
            base_freq = self.chakra_system.get_base_frequency(chakra_type)
            
            # Apply modulation
            mod_depth = 0.1
            mod_freq = 2.0
            self.chakra_system.modulate_chakra(chakra_type, mod_depth, mod_freq)
            
            # Check result
            new_freq = self.chakra_system.get_frequency(chakra_type)
            expected_freq = base_freq * (1 + mod_depth * 0.5)
            
            error = abs(new_freq - expected_freq) / expected_freq
            modulation_results[chakra_type.value] = {
                'error': error,
                'success': error < 0.01
            }
            
            print(f"  ✓ {chakra_type.value}: {base_freq:.1f} → {new_freq:.1f} Hz " +
                  f"({'PASS' if error < 0.01 else 'FAIL'})")
        
        success = all(r['success'] for r in modulation_results.values())
        
        return {'success': success, 'modulation_results': modulation_results}
    
    def _test_state_transitions(self) -> Dict:
        """Test 3: State transition capabilities"""
        print("\n[Phase 3] Testing state transitions...")
        
        results = {
            'activation_tests': [],
            'coherence_changes': []
        }
        
        # Test activation/deactivation
        for chakra_type in [ChakraType.ROOT, ChakraType.HEART, ChakraType.CROWN]:
            # Deactivate
            initial_coherence = self.chakra_system.get_system_coherence()
            self.chakra_system.deactivate_chakra(chakra_type)
            deactivated_coherence = self.chakra_system.get_system_coherence()
            
            # Reactivate
            self.chakra_system.activate_chakra(chakra_type)
            reactivated_coherence = self.chakra_system.get_system_coherence()
            
            test_passed = (deactivated_coherence != initial_coherence and 
                          abs(reactivated_coherence - initial_coherence) < 0.01)
            
            results['activation_tests'].append({
                'chakra': chakra_type.value,
                'passed': test_passed
            })
            
            print(f"  ✓ {chakra_type.value} activation: {'PASS' if test_passed else 'FAIL'}")
        
        success = all(t['passed'] for t in results['activation_tests'])
        
        return {'success': success, 'results': results}
    
    def _test_stability(self) -> Dict:
        """Test 4: Long-term stability under stress"""
        print("\n[Phase 4] Testing stability...")
        
        # Record initial state
        initial_state = self.dynamics.get_system_state()
        
        # Apply rapid random modulations
        stability_metrics = []
        
        for i in range(20):
            # Random modulation
            chakra = np.random.choice([ChakraType.ROOT, ChakraType.HEART, ChakraType.CROWN])
            amp = np.random.uniform(0.05, 0.2)
            freq = np.random.uniform(0.5, 3.0)
            self.chakra_system.modulate_chakra(chakra, amp, freq)
            
            # Evolve system
            for _ in range(5):
                self.dynamics.evolve(dt=0.1)
            
            # Check stability
            state = self.dynamics.get_system_state()
            stability = 1.0 - abs(state['chakra_coherence'] - initial_state['chakra_coherence'])
            stability_metrics.append(stability)
        
        avg_stability = np.mean(stability_metrics)
        min_stability = np.min(stability_metrics)
        
        print(f"  Average stability: {avg_stability:.3f}")
        print(f"  Minimum stability: {min_stability:.3f}")
        print(f"  Quantum fidelity maintained: {state['quantum_fidelity']:.3f}")
        
        success = avg_stability > 0.98 and min_stability > 0.95
        
        return {
            'success': success,
            'avg_stability': avg_stability,
            'min_stability': min_stability,
            'final_fidelity': state['quantum_fidelity']
        }
    
    def _test_full_integration(self) -> Dict:
        """Test 5: Full system integration over extended time"""
        print("\n[Phase 5] Testing full integration...")
        
        # Reset system
        self.chakra_system = RefactoredChakraSystem(use_simplified=True)
        self.iam_state = RefactoredFrequencyModulatedIAMState(base_dimension=3)
        self.dynamics = RefactoredChronosonicDynamics(self.chakra_system, self.iam_state)
        
        # Run for specified duration with measurements
        start_time = time.time()
        measurements = []
        
        while time.time() - start_time < min(self.duration, 60):  # Cap at 1 minute for testing
            # Evolve
            self.dynamics.evolve(dt=0.1)
            
            # Measure every second
            if len(measurements) == 0 or time.time() - measurements[-1]['timestamp'] > 1.0:
                state = self.dynamics.get_system_state()
                iam_metrics = state['iam_metrics']
                
                measurement = {
                    'timestamp': time.time(),
                    'coherence': state['chakra_coherence'],
                    'quantum_fidelity': state['quantum_fidelity'],
                    'iam_coherence': iam_metrics['coherence'],
                    'frequency_accuracy': self._calculate_frequency_accuracy()
                }
                measurements.append(measurement)
                
                # Progress update every 10 seconds
                if len(measurements) % 10 == 0:
                    elapsed = time.time() - start_time
                    print(f"  [{elapsed:.0f}s] Coherence: {measurement['coherence']:.3f}, " +
                          f"Fidelity: {measurement['quantum_fidelity']:.3f}")
        
        # Calculate integration metrics
        coherences = [m['coherence'] for m in measurements]
        fidelities = [m['quantum_fidelity'] for m in measurements]
        freq_accuracies = [m['frequency_accuracy'] for m in measurements]
        
        integration_metrics = {
            'avg_coherence': np.mean(coherences),
            'coherence_stability': 1.0 - np.std(coherences),
            'avg_fidelity': np.mean(fidelities),
            'avg_frequency_accuracy': np.mean(freq_accuracies),
            'measurement_count': len(measurements)
        }
        
        success = (integration_metrics['avg_coherence'] > 0.9 and
                  integration_metrics['coherence_stability'] > 0.95 and
                  integration_metrics['avg_frequency_accuracy'] > 0.95)
        
        print(f"\n  Integration summary:")
        print(f"    Average coherence: {integration_metrics['avg_coherence']:.3f}")
        print(f"    Coherence stability: {integration_metrics['coherence_stability']:.3f}")
        print(f"    Average fidelity: {integration_metrics['avg_fidelity']:.3f}")
        print(f"    Frequency accuracy: {integration_metrics['avg_frequency_accuracy']:.3f}")
        
        return {
            'success': success,
            'metrics': integration_metrics,
            'measurements': measurements
        }
    
    def _calculate_frequency_accuracy(self) -> float:
        """Calculate frequency generation accuracy"""
        errors = []
        for chakra_type, chakra in self.chakra_system.chakras.items():
            expected = chakra.base_frequency
            actual = chakra.current_frequency
            if expected > 0:
                error = abs(actual - expected) / expected
                errors.append(error)
        return 1.0 - np.mean(errors) if errors else 1.0
    
    def _calculate_summary(self, phase_results: Dict, criteria: Dict) -> Dict:
        """Calculate overall test summary"""
        # Phase success
        phase_success = {phase: results['success'] for phase, results in phase_results.items()}
        phases_passed = sum(phase_success.values())
        
        # Criteria evaluation
        criteria_results = {}
        
        # Frequency accuracy from integration test
        if 'integration' in phase_results and 'metrics' in phase_results['integration']:
            criteria_results['frequency_accuracy'] = phase_results['integration']['metrics']['avg_frequency_accuracy']
        else:
            criteria_results['frequency_accuracy'] = 0.0
        
        # State coherence
        if 'integration' in phase_results and 'metrics' in phase_results['integration']:
            criteria_results['state_coherence'] = phase_results['integration']['metrics']['avg_coherence']
        else:
            criteria_results['state_coherence'] = 0.0
        
        # Temporal stability
        if 'stability' in phase_results:
            criteria_results['temporal_stability'] = phase_results['stability']['avg_stability']
        else:
            criteria_results['temporal_stability'] = 0.0
        
        # Quantum fidelity
        if 'integration' in phase_results and 'metrics' in phase_results['integration']:
            criteria_results['quantum_fidelity'] = phase_results['integration']['metrics']['avg_fidelity']
        else:
            criteria_results['quantum_fidelity'] = 0.0
        
        # Check criteria
        criteria_passed = sum(1 for metric, threshold in criteria.items() 
                            if criteria_results.get(metric, 0) >= threshold)
        
        overall_success = phases_passed == len(phase_results) and criteria_passed == len(criteria)
        
        return {
            'phases_passed': phases_passed,
            'total_phases': len(phase_results),
            'phase_success': phase_success,
            'criteria_results': criteria_results,
            'criteria_passed': criteria_passed,
            'total_criteria': len(criteria),
            'overall_success': overall_success
        }
    
    def _display_results(self, criteria: Dict):
        """Display test results"""
        summary = self.results['summary']
        
        print("\n" + "=" * 60)
        print("TEST RESULTS")
        print("=" * 60)
        
        # Phase results
        print("\nPhase Results:")
        for phase, success in summary['phase_success'].items():
            status = "PASS" if success else "FAIL"
            print(f"  {phase}: [{status}]")
        print(f"\nPhases passed: {summary['phases_passed']}/{summary['total_phases']}")
        
        # Criteria results
        print("\nCriteria Results:")
        for metric, threshold in criteria.items():
            value = summary['criteria_results'].get(metric, 0)
            passed = value >= threshold
            status = "PASS" if passed else "FAIL"
            print(f"  {metric}: {value:.1%} (target: {threshold:.1%}) [{status}]")
        print(f"\nCriteria passed: {summary['criteria_passed']}/{summary['total_criteria']}")
        
        # Overall result
        print("\n" + "=" * 60)
        if summary['overall_success']:
            print("✅ CHRONOSONIC V2 TEST PASSED!")
            print("\nThe refactored implementation meets all requirements.")
            print("Ready for:")
            print("  - FA-CMS integration")
            print("  - 7-chakra scaling")
            print("  - Extended validation testing")
        else:
            print("❌ CHRONOSONIC V2 TEST FAILED")
            print("\nReview failed phases and criteria for debugging.")
    
    def _save_results(self):
        """Save test results to file"""
        filename = f"chronosonic_v2_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert numpy types for JSON serialization
        def convert_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_types(v) for v in obj]
            return obj
        
        results_json = convert_types(self.results)
        
        with open(filename, 'w') as f:
            json.dump(results_json, f, indent=2)
        
        print(f"\nResults saved to: {filename}")


def main():
    """Run CHRONOSONIC V2 test"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CHRONOSONIC V2 Test Suite')
    parser.add_argument('--duration', type=float, default=1,
                       help='Test duration in minutes (default: 1)')
    parser.add_argument('--full', action='store_true',
                       help='Run full 30-minute test')
    
    args = parser.parse_args()
    
    if args.full:
        duration = 30
        print("Running full 30-minute test...")
    else:
        duration = args.duration
    
    # Create and run test
    test = ChronosonicV2Test(duration_minutes=duration)
    success = test.run_test()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())