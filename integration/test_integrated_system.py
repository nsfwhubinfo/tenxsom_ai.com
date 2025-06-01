#!/usr/bin/env python3
"""
Test script for META-CHRONOSONIC integrated system
Validates the bridge functionality and measures performance
"""

import sys
import os
import numpy as np
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from meta_chronosonic_bridge import (
    MetaChronosonicBridge,
    IntegrationConfig,
    PHI
)


class IntegratedSystemTest:
    """Comprehensive test suite for integrated system"""
    
    def __init__(self):
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'summary': {}
        }
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("META-CHRONOSONIC INTEGRATED SYSTEM TEST")
        print("=" * 70)
        print(f"Start time: {datetime.now()}")
        print()
        
        # Test 1: Basic Integration
        print("Test 1: Basic Integration")
        print("-" * 40)
        self.test_basic_integration()
        
        # Test 2: Parameter Mapping Modes
        print("\nTest 2: Parameter Mapping Modes")
        print("-" * 40)
        self.test_parameter_mappings()
        
        # Test 3: Objective Weighting
        print("\nTest 3: Objective Weighting")
        print("-" * 40)
        self.test_objective_weights()
        
        # Test 4: Performance Benchmark
        print("\nTest 4: Performance Benchmark")
        print("-" * 40)
        self.test_performance()
        
        # Test 5: φ Discovery Enhancement
        print("\nTest 5: φ Discovery Enhancement")
        print("-" * 40)
        self.test_phi_discovery()
        
        # Summary
        self.generate_summary()
        
    def test_basic_integration(self):
        """Test basic integration functionality"""
        config = IntegrationConfig(
            v6_max_iterations=10,
            cs_use_simplified=True,
            param_mapping_mode="direct"
        )
        
        bridge = MetaChronosonicBridge(config)
        
        # Simple objective
        def simple_objective(params):
            return sum(v**2 for v in params.values())
        
        initial = {'x0': 1.0, 'x1': 2.0, 'x2': 3.0}
        
        try:
            best, scores = bridge.optimize_integrated(
                simple_objective,
                initial,
                max_iterations=10
            )
            
            success = len(scores) == 10 and all(isinstance(s, (int, float)) for s in scores)
            improvement = (scores[0] - scores[-1]) / scores[0] * 100
            
            self.test_results['tests']['basic_integration'] = {
                'success': success,
                'improvement': improvement,
                'final_score': scores[-1]
            }
            
            print(f"  Status: {'PASS' if success else 'FAIL'}")
            print(f"  Improvement: {improvement:.1f}%")
            
        except Exception as e:
            self.test_results['tests']['basic_integration'] = {
                'success': False,
                'error': str(e)
            }
            print(f"  Status: FAIL - {e}")
    
    def test_parameter_mappings(self):
        """Test different parameter mapping modes"""
        modes = ['direct', 'harmonic', 'geometric']
        results = {}
        
        for mode in modes:
            print(f"\n  Testing {mode} mapping:")
            
            config = IntegrationConfig(
                v6_max_iterations=20,
                param_mapping_mode=mode
            )
            
            bridge = MetaChronosonicBridge(config)
            
            # φ-friendly objective
            def phi_objective(params):
                score = 0
                values = list(params.values())
                for i in range(len(values)-1):
                    ratio = values[i+1] / (values[i] + 1e-10)
                    score += (ratio - PHI)**2
                return score
            
            initial = {f'x{i}': 1.0 + i*0.5 for i in range(4)}
            
            try:
                best, scores = bridge.optimize_integrated(
                    phi_objective,
                    initial,
                    max_iterations=20
                )
                
                # Check φ discovery
                values = list(best.values())
                phi_errors = []
                for i in range(len(values)-1):
                    ratio = values[i+1] / (values[i] + 1e-10)
                    phi_errors.append(abs(ratio - PHI))
                
                avg_error = np.mean(phi_errors)
                phi_count = sum(1 for e in phi_errors if e < 0.1)
                
                results[mode] = {
                    'avg_phi_error': avg_error,
                    'phi_ratios_found': phi_count,
                    'final_score': scores[-1]
                }
                
                print(f"    Average φ error: {avg_error:.4f}")
                print(f"    φ ratios found: {phi_count}/{len(phi_errors)}")
                
            except Exception as e:
                results[mode] = {'error': str(e)}
                print(f"    Error: {e}")
        
        self.test_results['tests']['parameter_mappings'] = results
    
    def test_objective_weights(self):
        """Test different objective weight configurations"""
        weight_configs = [
            {'optimization': 0.8, 'phi_discovery': 0.1, 'coherence': 0.1},
            {'optimization': 0.4, 'phi_discovery': 0.4, 'coherence': 0.2},
            {'optimization': 0.2, 'phi_discovery': 0.2, 'coherence': 0.6}
        ]
        
        results = []
        
        for i, weights in enumerate(weight_configs):
            print(f"\n  Config {i+1}: {weights}")
            
            config = IntegrationConfig(
                v6_max_iterations=15,
                objective_weights=weights
            )
            
            bridge = MetaChronosonicBridge(config)
            
            # Multi-objective function
            def multi_objective(params):
                # Base optimization
                base = sum((v - 1.5)**2 for v in params.values())
                # φ component
                values = list(params.values())
                phi_error = 0
                for j in range(len(values)-1):
                    if values[j] > 0:
                        ratio = values[j+1] / values[j]
                        phi_error += abs(ratio - PHI)
                return base + phi_error
            
            initial = {f'x{i}': np.random.uniform(0.5, 2.5) for i in range(5)}
            
            try:
                best, scores = bridge.optimize_integrated(
                    multi_objective,
                    initial,
                    max_iterations=15
                )
                
                # Get final metrics
                final_metrics = bridge.metrics_history[-1] if bridge.metrics_history else {}
                
                result = {
                    'weights': weights,
                    'final_base': final_metrics.get('base_score', 0),
                    'final_phi': final_metrics.get('phi_score', 0),
                    'final_coherence': final_metrics.get('coherence_score', 0),
                    'improvement': (scores[0] - scores[-1]) / scores[0] * 100
                }
                
                results.append(result)
                
                print(f"    Improvement: {result['improvement']:.1f}%")
                print(f"    Final coherence: {result['final_coherence']:.3f}")
                
            except Exception as e:
                results.append({'error': str(e)})
                print(f"    Error: {e}")
        
        self.test_results['tests']['objective_weights'] = results
    
    def test_performance(self):
        """Benchmark integrated system performance"""
        print("\n  Running performance benchmark...")
        
        config = IntegrationConfig(
            v6_max_iterations=50,
            cs_use_simplified=False,  # Full 7-chakra system
            param_mapping_mode="geometric"
        )
        
        bridge = MetaChronosonicBridge(config)
        
        # Complex objective
        def complex_objective(params):
            values = np.array(list(params.values()))
            # Rosenbrock-like with φ bias
            score = 0
            for i in range(len(values)-1):
                score += 100 * (values[i+1] - values[i]**2)**2 + (1 - values[i])**2
                # φ bonus
                if values[i] > 0:
                    ratio = values[i+1] / values[i]
                    score -= 10 * np.exp(-abs(ratio - PHI))
            return score
        
        initial = {f'x{i}': np.random.uniform(0.5, 1.5) for i in range(12)}
        
        start_time = time.time()
        
        try:
            best, scores = bridge.optimize_integrated(
                complex_objective,
                initial,
                max_iterations=50
            )
            
            elapsed = time.time() - start_time
            
            # Performance metrics
            iterations_per_second = 50 / elapsed
            final_coherence = bridge.chronosonic.get_system_state()['chakra_coherence']
            
            # φ discovery
            values = list(best.values())
            phi_count = 0
            for i in range(len(values)-1):
                if values[i] > 0:
                    ratio = values[i+1] / values[i]
                    if abs(ratio - PHI) < 0.1:
                        phi_count += 1
            
            self.test_results['tests']['performance'] = {
                'elapsed_time': elapsed,
                'iterations_per_second': iterations_per_second,
                'final_coherence': final_coherence,
                'phi_ratios_found': phi_count,
                'improvement': (scores[0] - scores[-1]) / scores[0] * 100
            }
            
            print(f"    Time: {elapsed:.2f}s ({iterations_per_second:.1f} iter/s)")
            print(f"    Final coherence: {final_coherence:.3f}")
            print(f"    φ ratios: {phi_count}/{len(values)-1}")
            
        except Exception as e:
            self.test_results['tests']['performance'] = {'error': str(e)}
            print(f"    Error: {e}")
    
    def test_phi_discovery(self):
        """Test φ discovery enhancement through integration"""
        print("\n  Testing φ discovery enhancement...")
        
        # Compare with and without CHRONOSONIC
        results = {}
        
        # Without CHRONOSONIC (weights set to minimize influence)
        config_without = IntegrationConfig(
            v6_max_iterations=30,
            objective_weights={
                'optimization': 0.9,
                'phi_discovery': 0.1,
                'coherence': 0.0
            }
        )
        
        # With CHRONOSONIC (balanced weights)
        config_with = IntegrationConfig(
            v6_max_iterations=30,
            objective_weights={
                'optimization': 0.4,
                'phi_discovery': 0.3,
                'coherence': 0.3
            },
            param_mapping_mode="geometric"
        )
        
        # φ-specific objective
        def phi_discovery_objective(params):
            score = 0
            values = list(params.values())
            # Reward consecutive φ ratios
            for i in range(len(values)-1):
                if values[i] > 0:
                    ratio = values[i+1] / values[i]
                    score += (ratio - PHI)**2
            # Penalty for extreme values
            score += 0.1 * sum((v - PHI)**2 for v in values)
            return score
        
        initial = {f'x{i}': 1.0 + i*0.3 for i in range(6)}
        
        for name, config in [("Without CHRONOSONIC", config_without), 
                            ("With CHRONOSONIC", config_with)]:
            print(f"\n    {name}:")
            
            bridge = MetaChronosonicBridge(config)
            
            try:
                best, scores = bridge.optimize_integrated(
                    phi_discovery_objective,
                    initial.copy(),
                    max_iterations=30
                )
                
                # Analyze φ discovery
                values = list(best.values())
                phi_errors = []
                for i in range(len(values)-1):
                    if values[i] > 0:
                        ratio = values[i+1] / values[i]
                        error = abs(ratio - PHI)
                        phi_errors.append(error)
                
                avg_error = np.mean(phi_errors)
                perfect_ratios = sum(1 for e in phi_errors if e < 0.01)
                good_ratios = sum(1 for e in phi_errors if e < 0.1)
                
                results[name] = {
                    'avg_error': avg_error,
                    'perfect_ratios': perfect_ratios,
                    'good_ratios': good_ratios,
                    'final_score': scores[-1],
                    'improvement': (scores[0] - scores[-1]) / scores[0] * 100
                }
                
                print(f"      Average error: {avg_error:.4f}")
                print(f"      Perfect ratios (<1%): {perfect_ratios}/{len(phi_errors)}")
                print(f"      Good ratios (<10%): {good_ratios}/{len(phi_errors)}")
                
            except Exception as e:
                results[name] = {'error': str(e)}
                print(f"      Error: {e}")
        
        self.test_results['tests']['phi_discovery'] = results
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        
        total_tests = 0
        passed_tests = 0
        
        # Basic integration
        if 'basic_integration' in self.test_results['tests']:
            total_tests += 1
            if self.test_results['tests']['basic_integration'].get('success', False):
                passed_tests += 1
                print("✅ Basic Integration: PASS")
            else:
                print("❌ Basic Integration: FAIL")
        
        # Parameter mappings
        if 'parameter_mappings' in self.test_results['tests']:
            mappings = self.test_results['tests']['parameter_mappings']
            total_tests += len(mappings)
            for mode, result in mappings.items():
                if 'error' not in result:
                    passed_tests += 1
                    print(f"✅ Parameter Mapping ({mode}): PASS")
                else:
                    print(f"❌ Parameter Mapping ({mode}): FAIL")
        
        # Performance
        if 'performance' in self.test_results['tests']:
            total_tests += 1
            perf = self.test_results['tests']['performance']
            if 'error' not in perf and perf.get('iterations_per_second', 0) > 1:
                passed_tests += 1
                print("✅ Performance Benchmark: PASS")
            else:
                print("❌ Performance Benchmark: FAIL")
        
        # φ Discovery
        if 'phi_discovery' in self.test_results['tests']:
            total_tests += 1
            phi_test = self.test_results['tests']['phi_discovery']
            with_cs = phi_test.get('With CHRONOSONIC', {})
            without_cs = phi_test.get('Without CHRONOSONIC', {})
            
            if (with_cs.get('avg_error', 1) < without_cs.get('avg_error', 1) or
                with_cs.get('good_ratios', 0) > without_cs.get('good_ratios', 0)):
                passed_tests += 1
                print("✅ φ Discovery Enhancement: PASS (CHRONOSONIC improves φ discovery)")
            else:
                print("❌ φ Discovery Enhancement: FAIL")
        
        # Overall summary
        success_rate = passed_tests / total_tests * 100 if total_tests > 0 else 0
        
        print(f"\nTests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        self.test_results['summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': success_rate
        }
        
        if success_rate >= 80:
            print("\n✅ INTEGRATION VALIDATED")
            print("The META-CHRONOSONIC bridge is working correctly!")
        else:
            print("\n⚠️ INTEGRATION NEEDS WORK")
            print("Review failed tests for debugging.")
        
        # Save results
        import json
        filename = f"integration_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        print(f"\nDetailed results saved to: {filename}")


if __name__ == "__main__":
    tester = IntegratedSystemTest()
    tester.run_all_tests()