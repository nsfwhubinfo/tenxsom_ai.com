#!/usr/bin/env python3
"""
Phase 2: 4-Hour Extended Validation Test
========================================

This test validates the META-CHRONOSONIC integration over an extended period,
measuring stability, performance, and optimization quality.

Test Objectives:
1. Verify system stability over 4 hours
2. Measure performance metrics and degradation
3. Test φ discovery consistency
4. Monitor memory usage and resource consumption
5. Validate coherence maintenance

For Tenxsom AI integration validation.
"""

import numpy as np
import time
import psutil
import json
import os
import sys
from datetime import datetime, timedelta
import traceback
from typing import Dict, List, Tuple, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from integration.meta_chronosonic_bridge import (
    MetaChronosonicBridge,
    IntegrationConfig,
    PHI
)


class ExtendedValidationTest:
    """4-hour extended validation test suite"""
    
    def __init__(self, duration_hours: float = 4.0):
        self.duration = duration_hours * 3600  # Convert to seconds
        self.start_time = None
        self.process = psutil.Process()
        
        # Test configurations
        self.test_configs = [
            {
                'name': 'balanced',
                'config': IntegrationConfig(
                    v6_max_iterations=100,
                    cs_use_simplified=False,  # Full 7-chakra
                    param_mapping_mode="geometric",
                    objective_weights={
                        'optimization': 0.4,
                        'phi_discovery': 0.3,
                        'coherence': 0.3
                    }
                ),
                'duration_minutes': 60
            },
            {
                'name': 'phi_focused',
                'config': IntegrationConfig(
                    v6_max_iterations=150,
                    cs_use_simplified=True,  # 3-chakra for speed
                    param_mapping_mode="geometric",
                    objective_weights={
                        'optimization': 0.2,
                        'phi_discovery': 0.6,
                        'coherence': 0.2
                    }
                ),
                'duration_minutes': 60
            },
            {
                'name': 'coherence_focused',
                'config': IntegrationConfig(
                    v6_max_iterations=120,
                    cs_use_simplified=False,
                    param_mapping_mode="harmonic",
                    objective_weights={
                        'optimization': 0.2,
                        'phi_discovery': 0.1,
                        'coherence': 0.7
                    }
                ),
                'duration_minutes': 60
            },
            {
                'name': 'performance_stress',
                'config': IntegrationConfig(
                    v6_max_iterations=200,
                    cs_use_simplified=False,
                    param_mapping_mode="direct",
                    objective_weights={
                        'optimization': 0.8,
                        'phi_discovery': 0.1,
                        'coherence': 0.1
                    },
                    state_sync_interval=2  # Frequent syncs
                ),
                'duration_minutes': 60
            }
        ]
        
        # Results storage
        self.results = {
            'test_id': f'extended_4h_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'duration_hours': duration_hours,
            'start_time': None,
            'end_time': None,
            'test_results': {},
            'performance_metrics': [],
            'stability_events': [],
            'summary': {}
        }
    
    def run_validation(self):
        """Run the complete 4-hour validation test"""
        self.start_time = time.time()
        self.results['start_time'] = datetime.now().isoformat()
        
        print("=" * 80)
        print("META-CHRONOSONIC 4-HOUR EXTENDED VALIDATION TEST")
        print("=" * 80)
        print(f"Start time: {datetime.now()}")
        print(f"Planned duration: {self.duration / 3600:.1f} hours")
        print(f"Test configurations: {len(self.test_configs)}")
        print()
        
        # Run each test configuration
        for i, test_config in enumerate(self.test_configs):
            if time.time() - self.start_time > self.duration:
                print("\nTime limit reached, ending tests.")
                break
            
            print(f"\n{'='*60}")
            print(f"Test {i+1}/{len(self.test_configs)}: {test_config['name']}")
            print(f"{'='*60}")
            
            try:
                self._run_single_test(test_config)
            except Exception as e:
                print(f"\n❌ Test failed: {e}")
                self.results['stability_events'].append({
                    'time': time.time() - self.start_time,
                    'event': 'test_failure',
                    'test': test_config['name'],
                    'error': str(e),
                    'traceback': traceback.format_exc()
                })
        
        # Final analysis
        self._final_analysis()
        
        # Save results
        self._save_results()
    
    def _run_single_test(self, test_config: Dict):
        """Run a single test configuration"""
        config_name = test_config['name']
        config = test_config['config']
        duration = test_config['duration_minutes'] * 60
        
        print(f"\nConfiguration:")
        print(f"  Mapping mode: {config.param_mapping_mode}")
        print(f"  Weights: {config.objective_weights}")
        print(f"  Chakras: {'3 (simplified)' if config.cs_use_simplified else '7 (full)'}")
        print(f"  Duration: {test_config['duration_minutes']} minutes")
        
        # Create bridge
        bridge = MetaChronosonicBridge(config)
        
        # Define test objectives
        objectives = {
            'rosenbrock_phi': self._create_rosenbrock_phi_objective(),
            'multi_modal': self._create_multi_modal_objective(),
            'coherence_driven': self._create_coherence_driven_objective()
        }
        
        test_results = {
            'config': config_name,
            'runs': [],
            'performance': [],
            'memory': []
        }
        
        test_start = time.time()
        run_count = 0
        
        # Run multiple optimization cycles
        while time.time() - test_start < duration:
            run_count += 1
            print(f"\n  Run {run_count}:")
            
            # Rotate through objectives
            obj_name = list(objectives.keys())[(run_count - 1) % len(objectives)]
            objective = objectives[obj_name]
            
            # Random initial parameters
            n_params = 12 if not config.cs_use_simplified else 6
            initial = {f'x{i}': np.random.uniform(0.5, 2.5) for i in range(n_params)}
            
            # Record pre-run metrics
            pre_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            pre_cpu = self.process.cpu_percent(interval=0.1)
            
            run_start = time.time()
            
            try:
                # Run optimization
                best_params, scores = bridge.optimize_integrated(
                    objective,
                    initial,
                    max_iterations=config.v6_max_iterations
                )
                
                run_time = time.time() - run_start
                
                # Record post-run metrics
                post_memory = self.process.memory_info().rss / 1024 / 1024
                post_cpu = self.process.cpu_percent(interval=0.1)
                
                # Analyze results
                phi_score = self._analyze_phi_discovery(best_params)
                final_coherence = bridge.chronosonic.get_system_state()['chakra_coherence']
                improvement = (scores[0] - scores[-1]) / (scores[0] + 1e-10) * 100
                
                run_result = {
                    'run': run_count,
                    'objective': obj_name,
                    'runtime': run_time,
                    'iterations': len(scores),
                    'improvement': improvement,
                    'phi_score': phi_score,
                    'final_coherence': final_coherence,
                    'memory_delta': post_memory - pre_memory,
                    'cpu_usage': (pre_cpu + post_cpu) / 2
                }
                
                test_results['runs'].append(run_result)
                
                print(f"    Objective: {obj_name}")
                print(f"    Runtime: {run_time:.1f}s")
                print(f"    Improvement: {improvement:.1f}%")
                print(f"    φ score: {phi_score:.1f}%")
                print(f"    Coherence: {final_coherence:.3f}")
                
                # Performance tracking
                if run_count % 5 == 0:
                    perf_metrics = {
                        'elapsed_time': time.time() - self.start_time,
                        'test': config_name,
                        'run': run_count,
                        'avg_runtime': np.mean([r['runtime'] for r in test_results['runs']]),
                        'memory_usage': post_memory,
                        'cpu_usage': post_cpu
                    }
                    self.results['performance_metrics'].append(perf_metrics)
                    test_results['performance'].append(perf_metrics)
                
            except Exception as e:
                print(f"    ❌ Run failed: {e}")
                self.results['stability_events'].append({
                    'time': time.time() - self.start_time,
                    'event': 'run_failure',
                    'test': config_name,
                    'run': run_count,
                    'error': str(e)
                })
            
            # Brief pause between runs
            time.sleep(1)
        
        # Test summary
        self._summarize_test(config_name, test_results)
        self.results['test_results'][config_name] = test_results
    
    def _create_rosenbrock_phi_objective(self):
        """Create Rosenbrock function with φ bias"""
        def objective(params):
            values = np.array(list(params.values()))
            
            # Rosenbrock component
            rosenbrock = 0
            for i in range(len(values) - 1):
                rosenbrock += 100 * (values[i+1] - values[i]**2)**2 + (1 - values[i])**2
            
            # φ ratio bonus
            phi_bonus = 0
            for i in range(len(values) - 1):
                if values[i] > 0:
                    ratio = values[i+1] / values[i]
                    phi_bonus -= 5 * np.exp(-abs(ratio - PHI))
            
            return rosenbrock + phi_bonus
        
        return objective
    
    def _create_multi_modal_objective(self):
        """Create multi-modal test function"""
        def objective(params):
            values = np.array(list(params.values()))
            
            # Multiple local minima
            score = 0
            for i, v in enumerate(values):
                score += v**2 * (1 + 0.1 * np.sin(5 * np.pi * v))
            
            # Global structure
            score += 0.1 * np.sum(values)**2
            
            return score
        
        return objective
    
    def _create_coherence_driven_objective(self):
        """Create objective that benefits from high coherence"""
        def objective(params):
            values = np.array(list(params.values()))
            
            # Encourage parameter synchronization
            mean_val = np.mean(values)
            coherence_term = np.sum((values - mean_val)**2)
            
            # Distance from target
            target = PHI
            distance_term = np.sum((values - target)**2)
            
            return 0.3 * coherence_term + 0.7 * distance_term
        
        return objective
    
    def _analyze_phi_discovery(self, params: Dict) -> float:
        """Analyze φ discovery in parameters"""
        values = list(params.values())
        if len(values) < 2:
            return 0.0
        
        phi_count = 0
        total_pairs = 0
        
        # Check all ratios
        for i in range(len(values) - 1):
            if values[i] > 0:
                ratio = values[i+1] / values[i]
                if abs(ratio - PHI) < 0.1:  # Within 10%
                    phi_count += 1
                total_pairs += 1
        
        # Check reverse ratios
        for i in range(len(values) - 1):
            if values[i+1] > 0:
                ratio = values[i] / values[i+1]
                if abs(ratio - 1/PHI) < 0.1:  # Within 10%
                    phi_count += 1
                total_pairs += 1
        
        return (phi_count / max(1, total_pairs)) * 100
    
    def _summarize_test(self, test_name: str, results: Dict):
        """Summarize individual test results"""
        print(f"\n  Test Summary - {test_name}:")
        print("  " + "-" * 40)
        
        runs = results['runs']
        if not runs:
            print("  No successful runs")
            return
        
        # Calculate statistics
        avg_runtime = np.mean([r['runtime'] for r in runs])
        avg_improvement = np.mean([r['improvement'] for r in runs])
        avg_phi_score = np.mean([r['phi_score'] for r in runs])
        avg_coherence = np.mean([r['final_coherence'] for r in runs])
        max_memory = max([r.get('memory_delta', 0) for r in runs])
        
        print(f"  Runs completed: {len(runs)}")
        print(f"  Avg runtime: {avg_runtime:.1f}s")
        print(f"  Avg improvement: {avg_improvement:.1f}%")
        print(f"  Avg φ score: {avg_phi_score:.1f}%")
        print(f"  Avg coherence: {avg_coherence:.3f}")
        print(f"  Max memory delta: {max_memory:.1f} MB")
    
    def _final_analysis(self):
        """Perform final analysis of all tests"""
        print("\n" + "=" * 80)
        print("FINAL ANALYSIS")
        print("=" * 80)
        
        total_time = time.time() - self.start_time
        self.results['end_time'] = datetime.now().isoformat()
        
        print(f"\nTest Duration: {total_time / 3600:.2f} hours")
        print(f"Stability Events: {len(self.results['stability_events'])}")
        
        # Aggregate metrics
        all_runs = []
        for test_name, test_results in self.results['test_results'].items():
            all_runs.extend(test_results['runs'])
        
        if all_runs:
            # Overall performance
            avg_improvement = np.mean([r['improvement'] for r in all_runs])
            avg_phi_score = np.mean([r['phi_score'] for r in all_runs])
            avg_coherence = np.mean([r['final_coherence'] for r in all_runs])
            
            print(f"\nOverall Performance:")
            print(f"  Total runs: {len(all_runs)}")
            print(f"  Avg improvement: {avg_improvement:.1f}%")
            print(f"  Avg φ discovery: {avg_phi_score:.1f}%")
            print(f"  Avg coherence: {avg_coherence:.3f}")
            
            # Performance degradation analysis
            if self.results['performance_metrics']:
                perf_metrics = self.results['performance_metrics']
                early_runtime = np.mean([p['avg_runtime'] for p in perf_metrics[:3]])
                late_runtime = np.mean([p['avg_runtime'] for p in perf_metrics[-3:]])
                degradation = (late_runtime - early_runtime) / early_runtime * 100
                
                print(f"\nPerformance Stability:")
                print(f"  Early avg runtime: {early_runtime:.1f}s")
                print(f"  Late avg runtime: {late_runtime:.1f}s")
                print(f"  Degradation: {degradation:+.1f}%")
            
            # Memory analysis
            if self.results['performance_metrics']:
                memory_usage = [p['memory_usage'] for p in perf_metrics]
                print(f"\nMemory Usage:")
                print(f"  Initial: {memory_usage[0]:.1f} MB")
                print(f"  Final: {memory_usage[-1]:.1f} MB")
                print(f"  Growth: {memory_usage[-1] - memory_usage[0]:.1f} MB")
            
            # Best configuration
            config_scores = {}
            for test_name, test_results in self.results['test_results'].items():
                runs = test_results['runs']
                if runs:
                    config_scores[test_name] = {
                        'improvement': np.mean([r['improvement'] for r in runs]),
                        'phi_score': np.mean([r['phi_score'] for r in runs]),
                        'coherence': np.mean([r['final_coherence'] for r in runs])
                    }
            
            if config_scores:
                print(f"\nConfiguration Rankings:")
                
                # By improvement
                by_improvement = sorted(config_scores.items(), 
                                      key=lambda x: x[1]['improvement'], 
                                      reverse=True)
                print(f"  Best improvement: {by_improvement[0][0]} ({by_improvement[0][1]['improvement']:.1f}%)")
                
                # By φ discovery
                by_phi = sorted(config_scores.items(), 
                               key=lambda x: x[1]['phi_score'], 
                               reverse=True)
                print(f"  Best φ discovery: {by_phi[0][0]} ({by_phi[0][1]['phi_score']:.1f}%)")
                
                # By coherence
                by_coherence = sorted(config_scores.items(), 
                                    key=lambda x: x[1]['coherence'], 
                                    reverse=True)
                print(f"  Best coherence: {by_coherence[0][0]} ({by_coherence[0][1]['coherence']:.3f})")
        
        # Success criteria evaluation
        print("\n" + "-" * 60)
        print("Success Criteria Evaluation:")
        print("-" * 60)
        
        criteria = {
            'Stability (< 5 failures)': len(self.results['stability_events']) < 5,
            'Performance (< 20% degradation)': abs(degradation) < 20 if 'degradation' in locals() else False,
            'φ Discovery (> 30% avg)': avg_phi_score > 30 if 'avg_phi_score' in locals() else False,
            'Coherence (> 0.6 avg)': avg_coherence > 0.6 if 'avg_coherence' in locals() else False,
            'Memory (< 500MB growth)': (memory_usage[-1] - memory_usage[0]) < 500 if 'memory_usage' in locals() else False
        }
        
        passed = 0
        for criterion, result in criteria.items():
            status = "PASS" if result else "FAIL"
            print(f"  {criterion}: {status}")
            if result:
                passed += 1
        
        success_rate = passed / len(criteria) * 100
        print(f"\nSuccess Rate: {passed}/{len(criteria)} ({success_rate:.0f}%)")
        
        self.results['summary'] = {
            'total_runtime_hours': total_time / 3600,
            'total_runs': len(all_runs),
            'stability_events': len(self.results['stability_events']),
            'avg_improvement': avg_improvement if 'avg_improvement' in locals() else 0,
            'avg_phi_score': avg_phi_score if 'avg_phi_score' in locals() else 0,
            'avg_coherence': avg_coherence if 'avg_coherence' in locals() else 0,
            'performance_degradation': degradation if 'degradation' in locals() else 0,
            'memory_growth_mb': memory_usage[-1] - memory_usage[0] if 'memory_usage' in locals() else 0,
            'criteria_passed': passed,
            'success_rate': success_rate
        }
        
        if success_rate >= 80:
            print("\n✅ 4-HOUR VALIDATION PASSED!")
            print("The META-CHRONOSONIC integration is stable and performant.")
            print("Ready for 8-hour extended testing.")
        else:
            print("\n⚠️ 4-HOUR VALIDATION NEEDS ATTENTION")
            print("Review failed criteria and stability events.")
    
    def _save_results(self):
        """Save detailed results to file"""
        filename = f"validation_4h_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert numpy types for JSON
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
        
        print(f"\nDetailed results saved to: {filename}")


def main():
    """Run the 4-hour validation test"""
    import argparse
    
    parser = argparse.ArgumentParser(description='4-Hour Extended Validation Test')
    parser.add_argument('--duration', type=float, default=4.0,
                       help='Test duration in hours (default: 4.0)')
    parser.add_argument('--quick', action='store_true',
                       help='Run quick 20-minute test instead')
    
    args = parser.parse_args()
    
    if args.quick:
        duration = 0.33  # 20 minutes
        print("Running quick 20-minute validation test...")
    else:
        duration = args.duration
    
    # Create and run test
    validator = ExtendedValidationTest(duration_hours=duration)
    
    try:
        validator.run_validation()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        validator._final_analysis()
        validator._save_results()
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        traceback.print_exc()
        validator._save_results()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())