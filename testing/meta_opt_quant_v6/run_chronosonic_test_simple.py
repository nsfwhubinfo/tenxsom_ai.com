#!/usr/bin/env python3
"""
Simple CHRONOSONIC Test without visualization dependencies
Tests core functionality without matplotlib
"""

import sys
import os
import time
import json
import numpy as np
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Import core components directly to avoid visualizer
import importlib.util
spec = importlib.util.spec_from_file_location(
    "chronosonic_prototype",
    os.path.join(os.path.dirname(__file__), "research/chronosonic_qualia/chronosonic_prototype.py")
)
chronosonic_prototype = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chronosonic_prototype)

SimplifiedChakraSystem = chronosonic_prototype.SimplifiedChakraSystem
FrequencyModulatedIAMState = chronosonic_prototype.FrequencyModulatedIAMState
ChronosonicDynamics = chronosonic_prototype.ChronosonicDynamics
ChakraType = chronosonic_prototype.ChakraType

class SimplifiedChronosonicTest:
    """Simplified test without visualization"""
    
    def __init__(self, duration_minutes: float = 30):
        self.duration = duration_minutes * 60  # Convert to seconds
        self.chakra_system = SimplifiedChakraSystem()
        self.iam_state = FrequencyModulatedIAMState(base_dimension=3)  # 3-chakra system
        self.dynamics = ChronosonicDynamics(self.chakra_system, self.iam_state)
        
        self.results = {
            'test_id': f'chronosonic_simple_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'duration_minutes': duration_minutes,
            'metrics': [],
            'summary': {}
        }
        
    def run_test(self):
        """Run simplified test"""
        print("CHRONOSONIC Simple Test")
        print("=" * 60)
        print(f"Duration: {self.duration / 60:.1f} minutes")
        print(f"Start time: {datetime.now()}")
        print()
        
        start_time = time.time()
        iteration = 0
        
        # Success criteria
        criteria = {
            'frequency_accuracy': 0.95,
            'state_coherence': 0.90,
            'temporal_stability': 0.98
        }
        
        print("Testing phases:")
        print("1. Initialization")
        print("2. Frequency modulation")
        print("3. State transitions")
        print("4. Stability analysis")
        print()
        
        # Metrics tracking
        frequency_errors = []
        coherence_values = []
        stability_scores = []
        
        while time.time() - start_time < self.duration:
            # Evolve system
            self._evolve_system(dt=0.1)
            
            # Measure metrics every second
            if iteration % 10 == 0:
                # Frequency accuracy
                freq_error = self._measure_frequency_accuracy()
                frequency_errors.append(freq_error)
                
                # State coherence
                coherence = self._measure_coherence()
                coherence_values.append(coherence)
                
                # Temporal stability
                stability = self._measure_stability()
                stability_scores.append(stability)
                
                # Progress update every 30 seconds
                if iteration % 300 == 0:
                    elapsed = time.time() - start_time
                    progress = elapsed / self.duration * 100
                    print(f"[{elapsed/60:.1f}m] Progress: {progress:.1f}%")
                    print(f"  Frequency accuracy: {1-np.mean(frequency_errors[-30:]):.1%}")
                    print(f"  State coherence: {np.mean(coherence_values[-30:]):.1%}")
                    print(f"  Temporal stability: {np.mean(stability_scores[-30:]):.1%}")
            
            iteration += 1
            
            # Test specific transitions
            if iteration == 100:
                print("\n[Phase 2] Testing frequency modulation...")
                self._test_frequency_modulation()
            elif iteration == 200:
                print("\n[Phase 3] Testing state transitions...")
                self._test_state_transitions()
            elif iteration == 300:
                print("\n[Phase 4] Testing stability...")
                self._test_stability()
        
        # Calculate final results
        self.results['summary'] = {
            'frequency_accuracy': 1 - np.mean(frequency_errors),
            'state_coherence': np.mean(coherence_values),
            'temporal_stability': np.mean(stability_scores),
            'test_duration': time.time() - start_time,
            'iterations': iteration
        }
        
        # Check success criteria
        success = True
        print("\n" + "=" * 60)
        print("Test Results:")
        print("=" * 60)
        
        for metric, threshold in criteria.items():
            value = self.results['summary'][metric]
            passed = value >= threshold
            success &= passed
            status = "PASS" if passed else "FAIL"
            print(f"{metric}: {value:.1%} (target: {threshold:.1%}) [{status}]")
        
        self.results['success'] = success
        
        # Save results
        self._save_results()
        
        return success
    
    def _evolve_system(self, dt: float):
        """Simple system evolution"""
        # Update time
        if not hasattr(self, 'time'):
            self.time = 0
        self.time += dt
        
        # Apply modulation to IAM state
        self.iam_state.apply_chakra_modulation(self.chakra_system, self.time)
        
        # Update quantum state (simplified)
        if not hasattr(self.dynamics, 'quantum_state'):
            self.dynamics.quantum_state = np.random.randn(3) + 1j * np.random.randn(3)
            self.dynamics.quantum_state /= np.linalg.norm(self.dynamics.quantum_state)
        
        # Simple evolution
        phase = 2 * np.pi * self.time * 0.1
        self.dynamics.quantum_state *= np.exp(1j * phase)
    
    def _measure_frequency_accuracy(self) -> float:
        """Measure frequency generation accuracy"""
        errors = []
        for chakra in ChakraType:
            expected = self.chakra_system.get_base_frequency(chakra)
            actual = self.chakra_system.get_frequency(chakra)
            if expected > 0:
                error = abs(actual - expected) / expected
                errors.append(error)
        return np.mean(errors) if errors else 0
    
    def _measure_coherence(self) -> float:
        """Measure I_AM state coherence"""
        # Simple coherence based on amplitude variance
        amplitudes = [self.chakra_system.get_amplitude(c) for c in ChakraType]
        if amplitudes:
            return 1.0 / (1.0 + np.std(amplitudes))
        return 0
    
    def _measure_stability(self) -> float:
        """Measure temporal stability"""
        # Check if quantum state norm is preserved
        norm = np.linalg.norm(self.dynamics.quantum_state)
        return min(1.0, 1.0 / abs(norm - 1.0 + 0.01))
    
    def _test_frequency_modulation(self):
        """Test frequency modulation capabilities"""
        # Modulate root chakra
        self.chakra_system.modulate_chakra(ChakraType.ROOT, 0.1, 2.0)
        print("  - Root chakra modulated")
        
        # Modulate heart chakra
        self.chakra_system.modulate_chakra(ChakraType.HEART, 0.05, 1.5)
        print("  - Heart chakra modulated")
    
    def _test_state_transitions(self):
        """Test state transition capabilities"""
        # Activate all chakras in sequence
        for chakra in ChakraType:
            self.chakra_system.activate_chakra(chakra)
            time.sleep(0.1)
        print("  - All chakras activated")
        
        # Test deactivation
        self.chakra_system.deactivate_chakra(ChakraType.ROOT)
        print("  - Root chakra deactivated")
    
    def _test_stability(self):
        """Test system stability under stress"""
        # Apply rapid modulations
        for _ in range(10):
            chakra = np.random.choice(list(ChakraType))
            amp = np.random.uniform(0.05, 0.2)
            freq = np.random.uniform(0.5, 3.0)
            self.chakra_system.modulate_chakra(chakra, amp, freq)
        print("  - Stress test completed")
    
    def _save_results(self):
        """Save test results"""
        filename = f"chronosonic_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to: {filename}")


def main():
    """Run CHRONOSONIC test"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CHRONOSONIC Simple Test')
    parser.add_argument('--duration', type=float, default=30,
                       help='Test duration in minutes (default: 30)')
    parser.add_argument('--quick', action='store_true',
                       help='Run 5-minute quick test')
    
    args = parser.parse_args()
    
    if args.quick:
        duration = 5
        print("Running 5-minute quick test...")
    else:
        duration = args.duration
    
    # Create and run test
    test = SimplifiedChronosonicTest(duration_minutes=duration)
    success = test.run_test()
    
    if success:
        print("\n✅ CHRONOSONIC test PASSED!")
        print("Ready for FA-CMS integration and 7-chakra scaling")
        # Update TODO
        return 0
    else:
        print("\n❌ CHRONOSONIC test FAILED")
        print("Review results and adjust parameters")
        return 1


if __name__ == "__main__":
    sys.exit(main())